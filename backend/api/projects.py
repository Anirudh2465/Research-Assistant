from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.db.sqlite import get_db
from backend.db.models import Project, CeleryJob
from backend.workers.tasks_project import initialize_project_kg_task, import_concepts_task, calculate_progress_task
from backend.db.neo4j import neo4j_client
from backend.db.graph_schema import Label
import json

router = APIRouter(prefix="/api/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    domain: str
    problem_statement: str
    constraints: str

@router.post("/create")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # 1. SQLite Insert
    new_proj = Project(
        name=project.name,
        domain=project.domain,
        problem_statement=project.problem_statement,
        # constraints not in model yet, ignoring or adding to PS
    )
    db.add(new_proj)
    db.commit()
    db.refresh(new_proj)

    # 2. Neo4j Node Create
    driver = neo4j_client.driver
    if not driver: neo4j_client.connect()
    with driver.session() as session:
        session.run(f"MERGE (p:{Label.Project} {{project_id: $pid, name: $name}})", 
                    pid=new_proj.id, name=new_proj.name)

    # 3. Trigger Init Job
    # We wrap this in a CeleryJob for tracking candidates
    job = CeleryJob(job_type="project_init", status="queued", payload=json.dumps({"project_id": new_proj.id}))
    db.add(job)
    db.commit()
    db.refresh(job)

    # Trigger Task
    # For demo, we just fire and forget, but ideally we link job_id
    initialize_project_kg_task.delay(new_proj.id)

    return {"project_id": new_proj.id, "init_job_id": job.id}

@router.get("/")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    # In real app, we might join with Tasks/Ideas for counts, 
    # but for now basic list is enough for UI card
    return projects

@router.get("/{id}")
def get_project(id: int, db: Session = Depends(get_db)):
    proj = db.query(Project).filter(Project.id == id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.post("/{id}/import")
def import_concepts(id: int, concept_names: list):
    # Validates relevance gate
    task = import_concepts_task.delay(id, concept_names)
    return {"status": "importing", "task_id": task.id}

@router.get("/{id}/progress")
def get_progress(id: int):
    # In real world, we might cache this. For now, trigger sync or return last calc.
    # We'll trigger sync for demo
    task = calculate_progress_task.delay(id)
    # Return placeholder or wait
    return {"status": "calculating", "task_id": task.id}
