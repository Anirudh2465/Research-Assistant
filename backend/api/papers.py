from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4
import shutil
import json

from backend.db.sqlite import get_db
from backend.db.models import CeleryJob, Paper
from backend.core.paths import PDF_DIR
from backend.workers.tasks_ingestion import parse_pdf_task, extract_text_task, extract_concepts_task, abstract_concepts_task
from celery import chain

router = APIRouter(prefix="/api/papers", tags=["papers"])

@router.post("/upload")
async def upload_paper(
    file: UploadFile = File(...),
    scope: str = Form("global"), # global or project
    project_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Save File
    file_id = str(uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = PDF_DIR / filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # 2. Create Paper Record (Operational)
    new_paper = Paper(
        title=file.filename, # extraction will update this
        pdf_path=str(file_path),
        ingestion_status="processing"
    )
    db.add(new_paper)
    db.commit()
    db.refresh(new_paper)

    # 3. Create Celery Job
    new_job = CeleryJob(
        job_type="ingestion",
        status="queued",
        payload=json.dumps({"paper_id": new_paper.id, "scope": scope, "project_id": project_id})
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # 4. Monitor: Trigger Celery Pipeline
    # Using chain to enforce order
    workflow = chain(
        parse_pdf_task.s(str(file_path), new_job.id),
        extract_text_task.s(),
        extract_concepts_task.s(),
        abstract_concepts_task.s()
    )
    workflow.apply_async()

    return {"job_id": new_job.id, "paper_id": new_paper.id, "status": "queued"}

@router.get("/jobs/{job_id}")
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = db.query(CeleryJob).filter(CeleryJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # If waiting for review, unpack concepts
    payload = None
    if job.payload:
        try:
             payload = json.loads(job.payload)
        except:
             payload = job.payload

    return {
        "job_id": job.id,
        "status": job.status,
        "payload": payload,  # Contains high_level_concepts if waiting_for_review
        "started_at": job.started_at,
        "finished_at": job.finished_at
    }

@router.post("/jobs/{job_id}/approve")
def approve_job(job_id: int, approved_data: dict, db: Session = Depends(get_db)):
    job = db.query(CeleryJob).filter(CeleryJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "waiting_for_review":
        raise HTTPException(status_code=400, detail="Job is not waiting for review")

    # Update Job with Approved Data
    job.status = "approved"
    job.payload = json.dumps(approved_data) # Store the approved concepts
    db.commit()

    # Trigger Phase 2 (Graph Write)
    from backend.workers.tasks_graph import write_concepts_task
    
    # Extract approved concepts from payload - assuming payload is dict with "approved_concepts"
    # or just the list itself depending on UI. Schema in backend/schemas/ingestion.py says ApprovalRequest has "approved_concepts"
    # For now assume approved_data IS the ApprovalRequest dict
    
    concepts = approved_data.get("approved_concepts", [])
    if not concepts:
         # Fallback if raw list passed
         if isinstance(approved_data, list):
             concepts = approved_data
         elif "high_level_concepts" in approved_data:
             concepts = approved_data["high_level_concepts"]

    # Retrieve paper_id from original job payload
    paper_id = 0
    try:
        orig_payload = json.loads(job.payload)
        paper_id = orig_payload.get("paper_id", 0)
    except:
        pass

    write_concepts_task.delay(job_id, concepts, paper_id)

    return {"status": "approved", "message": "Graph write triggered"}
