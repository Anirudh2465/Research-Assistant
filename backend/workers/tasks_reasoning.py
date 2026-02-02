from backend.workers.celery_app import celery_app
from backend.services.graph_service import graph_service
from backend.services.llm_reasoning import llm_reasoning
from backend.db.neo4j import neo4j_client
from backend.db.graph_schema import Label, Relation
import json

@celery_app.task(name="reasoning.detect_contradictions")
def detect_contradictions_task():
    # Naive implementation: Compare all concept pairs (O(N^2) - Warning!)
    # Phase 3 spec says "newly added" + existing. 
    # For MVP, we'll limit to a small random subset or just recent ones.
    
    # Fetch all concepts (Limit to 50 for demo safety)
    driver = neo4j_client.driver
    query = f"MATCH (c:{Label.Concept}) RETURN c LIMIT 50"
    
    concepts = []
    with driver.session() as session:
        result = session.run(query)
        concepts = [graph_service._serialize_node(r["c"]) for r in result]

    # Compare pairs
    conflicts = 0
    for i in range(len(concepts)):
        for j in range(i+1, len(concepts)):
            c1 = concepts[i]
            c2 = concepts[j]
            
            # Skip if already related
            # (In real impl, check graph first)
            
            check = llm_reasoning.check_contradiction(c1["properties"], c2["properties"])
            if check:
                try:
                    res_json = json.loads(check) if isinstance(check, str) else check
                    if res_json.get("contradiction"):
                        # Create CONFLICTS_WITH edge
                        with driver.session() as session:
                            q_conflict = f"""
                            MATCH (a:{Label.Concept}), (b:{Label.Concept})
                            WHERE elementId(a) = $id1 AND elementId(b) = $id2
                            MERGE (a)-[r:{Relation.CONFLICTS_WITH}]->(b)
                            SET r.explanation = $expl, r.confidence = 0.9
                            """
                            session.run(q_conflict, id1=c1["id"], id2=c2["id"], expl=res_json.get("explanation", "Detected by LLM"))
                        conflicts += 1
                except:
                    pass
    
    return f"Contradiction scan complete. Found {conflicts} conflicts."

@celery_app.task(name="reasoning.synthesize_ideas")
def synthesize_ideas_task(concept_names: list, mode: str, project_id: int = None):
    # Fetch concept details
    concepts = [graph_service.get_concept_details(name) for name in concept_names]
    concepts = [c for c in concepts if c] 
    
    # Call Advanced LLM
    result = llm_reasoning.synthesize_idea_advanced(concepts, mode)
    
    if result:
        res_json = json.loads(result) if isinstance(result, str) else result
        
        title = res_json.get("title", "Untitled Idea")
        summary = res_json.get("summary", "")
        novelty = res_json.get("novelty_score", 0.5)
        feasibility = res_json.get("feasibility_score", 0.5)
        
        driver = neo4j_client.driver
        if not driver: neo4j_client.connect()
        
        with driver.session() as session:
            # 1. Create Idea Node
            q_idea = f"""
            CREATE (i:{Label.Idea} {{
                title: $title, 
                summary: $summary, 
                novelty: $novelty, 
                feasibility: $feasibility,
                mode: $mode,
                created_at: distinct(date())
            }})
            RETURN elementId(i) as id
            """
            idea_res = session.run(q_idea, title=title, summary=summary, 
                                   novelty=novelty, feasibility=feasibility, mode=mode).single()
            idea_id = idea_res["id"]

            # 2. Create Lineage (DERIVED_FROM)
            q_lineage = f"""
            MATCH (i:{Label.Idea}), (c:{Label.Concept})
            WHERE elementId(i) = $iid AND c.name IN $sources
            MERGE (i)-[:{Relation.DERIVED_FROM}]->(c)
            """
            session.run(q_lineage, iid=idea_id, sources=concept_names)
            
            # 3. Project Context (if applicable)
            if project_id:
                # Link Idea to Project
                q_proj = f"""
                MATCH (i:{Label.Idea}), (p:{Label.Project} {{project_id: $pid}})
                WHERE elementId(i) = $iid
                MERGE (i)-[:{Relation.BELONGS_TO_PROJECT}]->(p)
                """
                session.run(q_proj, iid=idea_id, pid=project_id)
            
            # 4. Store in SQLite (Operational View)
            # Create Idea in SQL
            sql_session = SessionLocal()
            from backend.db.models import Idea
            new_idea = Idea(
                title=title,
                summary=summary,
                status="draft",
                origin="project" if project_id else "research"
            )
            sql_session.add(new_idea)
            sql_session.commit()
            sql_session.close()

    return result
