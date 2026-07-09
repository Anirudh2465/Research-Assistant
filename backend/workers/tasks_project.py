from celery import chord
from backend.workers.celery_app import celery_app
from backend.core.logging import logger
from backend.services.vector_service import vector_service
from backend.services.graph_service import graph_service
from backend.services.llm_extraction import llm_extractor
from backend.db.sqlite import SessionLocal
from backend.db.models import CeleryJob, Project, Task
from backend.db.neo4j import neo4j_client
from backend.db.graph_schema import Label, Relation
import json

@celery_app.task(name="project.initialize_kg")
def initialize_project_kg_task(project_id: int):
    # 1. Fetch Project Details
    session = SessionLocal()
    project = session.query(Project).filter(Project.id == project_id).first()
    if not project:
         session.close()
         return "Project not found"
    
    ps = project.problem_statement
    session.close()

    # 2. Parse PS via LLM (Fix #10: actually use the returned keywords)
    keywords = extract_keywords(ps)
    
    # 3. Retrieve Global Concepts
    all_concepts = graph_service.get_all_concepts()  # List of dicts
    
    # 4. Rank Concepts
    candidates = []
    if all_concepts:
        # Build temp index
        index, concept_list = vector_service.create_batch_index(all_concepts)
        # Use keywords joined + full PS as query for semantic match
        query = f"{' '.join(keywords)} {ps}" if keywords else ps
        results = vector_service.search_local_index(query, index, concept_list, k=20)
        
        candidates = [r["concept"] for r in results]

    # 5. Store Candidates for Review
    return {"candidates": candidates, "project_id": project_id}

@celery_app.task(name="project.import_concepts")
def import_concepts_task(project_id: int, concept_names: list):
    driver = neo4j_client.driver
    if not driver:
        neo4j_client.connect()
        driver = neo4j_client.driver

    with driver.session() as session:
        query = f"""
        MATCH (c:{Label.Concept})
        WHERE c.name IN $names
        MATCH (p:{Label.Project} {{project_id: $pid}})
        MERGE (c)-[:{Relation.BELONGS_TO_PROJECT} {{source: "global_import"}}]->(p)
        """
        session.run(query, names=concept_names, pid=project_id)
        
    return f"Imported {len(concept_names)} concepts to Project {project_id}"

@celery_app.task(name="project.calculate_progress")
def calculate_progress_task(project_id: int):
    """
    Fix #11: Calculate progress from actual data instead of hardcoded values.
    Dimensions:
      - literature : fraction of concept nodes linked (goal=20)
      - method     : fraction of Method nodes linked (goal=5)
      - evaluation : fraction of tasks marked done (goal based on total tasks)
      - novelty    : fraction of Idea nodes with novelty >= 0.7 (goal=2)
    """
    subgraph = graph_service.get_project_subgraph(project_id)
    nodes = subgraph.get("nodes", [])

    # Count node types
    concept_count = sum(1 for n in nodes if "Concept" in n.get("labels", []))
    method_count  = sum(1 for n in nodes if "Method" in n.get("labels", []))
    idea_count    = sum(1 for n in nodes if "Idea"   in n.get("labels", []))
    novel_ideas   = sum(
        1 for n in nodes
        if "Idea" in n.get("labels", []) and n.get("properties", {}).get("novelty", 0) >= 0.7
    )

    # Task completion from SQLite
    db = SessionLocal()
    try:
        total_tasks = db.query(Task).filter(Task.linked_project_id == project_id).count()
        done_tasks  = db.query(Task).filter(
            Task.linked_project_id == project_id,
            Task.status == "done"
        ).count()
    finally:
        db.close()

    progress = {
        "literature": min(concept_count / 20.0, 1.0),
        "method":     min(method_count / 5.0, 1.0),
        "evaluation": (done_tasks / total_tasks) if total_tasks > 0 else 0.0,
        "novelty":    min(novel_ideas / 2.0, 1.0),
    }

    return progress

def extract_keywords(text: str) -> list:
    """
    Fix #10: Actually parse the LLM JSON response instead of returning hardcoded mock.
    """
    prompt = (
        f"Extract the core research keywords from the following problem statement. "
        f"Return a JSON array of strings only, no other text.\n\nProblem: {text}"
    )
    messages = [{"role": "user", "content": prompt}]
    try:
        res = llm_extractor._call_llm(messages)
        # Find JSON array in response
        start = res.find("[")
        end   = res.rfind("]") + 1
        if start != -1 and end != 0:
            keywords = json.loads(res[start:end])
            if isinstance(keywords, list):
                return [str(k) for k in keywords]
        return []
    except Exception as e:
        logger.warning(f"extract_keywords failed: {e}")
        return []
