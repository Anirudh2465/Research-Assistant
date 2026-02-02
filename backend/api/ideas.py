from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.db.sqlite import get_db
from backend.db.models import Idea, CeleryJob, Project
from backend.workers.tasks_project import initialize_project_kg_task
from backend.workers.tasks_reasoning import synthesize_ideas_task
from backend.db.neo4j import neo4j_client
from backend.db.graph_schema import Label, Relation
import json

router = APIRouter(prefix="/api/ideas", tags=["ideas"])

@router.get("/")
def list_ideas(db: Session = Depends(get_db)):
    ideas = db.query(Idea).all()
    return ideas

@router.post("/generate")
def generate_idea(
    concept_names: List[str],
    mode: str = "Cross-Domain Transfer",
    project_id: Optional[int] = None
):
    # Trigger Synthesis Task
    task = synthesize_ideas_task.delay(concept_names, mode, project_id)
    return {"status": "generating", "task_id": task.id}

@router.get("/{id}")
def get_idea(id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea

@router.patch("/{id}/status")
def update_status(id: int, status: str = Body(..., embed=True), db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    if status not in ["draft", "mature", "rejected", "promoted"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    idea.status = status
    db.commit()
    return idea

@router.post("/{id}/promote")
def promote_idea(id: int, db: Session = Depends(get_db)):
    # 1. Fetch Idea
    idea = db.query(Idea).filter(Idea.id == id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
        
    if idea.status != "mature":
        raise HTTPException(status_code=400, detail="Idea must be 'mature' to promote")

    # 2. Check Promotion Rules (e.g., checks executed here or manually overridden)
    # For now, we assume manual trigger = approval

    # 3. Create Project
    new_proj = Project(
        name=idea.title,
        domain="Promoted Idea", 
        problem_statement=idea.summary,
        status="active"
    )
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)
    
    # 4. Link Idea -> Project (BELONGS_TO_PROJECT) - already handled if created in project context, 
    # but this is promotion to NEW project.
    
    driver = neo4j_client.driver
    if not driver: neo4j_client.connect()
    with driver.session() as session:
        # Create Project Node
        session.run(f"MERGE (p:{Label.Project} {{project_id: $pid, name: $name}})", 
                    pid=new_proj.id, name=new_proj.name)
        
        # Link Idea (which lives in Neo4j) to this new Project
        # We need to find the Neo4j node for this SQL Idea. Ideally we stored elementId in SQL or 
        # use title matching (risky). Phase 5 spec says "No duplication", so we link.
        # We'll match by title for this demo (since we didn't store Neo4j ID in SQLite Idea table yet)
        
        q_link = f"""
        MATCH (i:{Label.Idea} {{title: $title}})
        MATCH (p:{Label.Project} {{project_id: $pid}})
        MERGE (i)-[:{Relation.BELONGS_TO_PROJECT} {{source: "promotion"}}]->(p)
        """
        session.run(q_link, title=idea.title, pid=new_proj.id)

        # 5. Initialize Project KG based on lineage?
        # Typically we want to import the SOURCE concepts of the idea into the project too.
        # "Initialize project KG using idea lineage"
        q_import_lineage = f"""
        MATCH (i:{Label.Idea} {{title: $title}})-[:{Relation.DERIVED_FROM}]->(c:{Label.Concept})
        MATCH (p:{Label.Project} {{project_id: $pid}})
        MERGE (c)-[:{Relation.BELONGS_TO_PROJECT} {{source: "idea_lineage"}}]->(p)
        """
        session.run(q_import_lineage, title=idea.title, pid=new_proj.id)

    # 6. Update Idea Status
    idea.status = "promoted"
    db.commit()

    return {"status": "promoted", "new_project_id": new_proj.id}
