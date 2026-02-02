from celery import chord, chain
from backend.workers.celery_app import celery_app
from backend.core.logging import logger
from backend.services.pdf_processing import extract_text_blocks
from backend.services.llm_extraction import llm_extractor
from backend.db.sqlite import SessionLocal
from backend.db.models import CeleryJob
import json

@celery_app.task(name="ingestion.parse_pdf", bind=True)
def parse_pdf_task(self, pdf_path: str, job_id: int):
    # Update Job Status
    update_job_status(job_id, "parsing_structure")
    # For now, just return path, eventually call GROBID here
    return {"pdf_path": pdf_path, "job_id": job_id}

@celery_app.task(name="ingestion.extract_text")
def extract_text_task(data):
    pdf_path = data["pdf_path"]
    job_id = data["job_id"]
    update_job_status(job_id, "extracting_text")
    
    blocks = extract_text_blocks(pdf_path)
    # Return limited blocks for demo to avoid massive payload
    # In prod, store blocks in DB or file, pass reference
    return {"blocks": blocks[:5], "job_id": job_id} # Demo: first 5 blocks

@celery_app.task(name="ingestion.extract_concepts")
def extract_concepts_task(data):
    blocks = data["blocks"]
    job_id = data["job_id"]
    update_job_status(job_id, "extracting_concepts")
    
    all_raw_concepts = []
    # Simple loop for now (could be parallel map)
    for block in blocks:
        text = block["text"]
        result = llm_extractor.extract_raw_concepts(text)
        all_raw_concepts.extend(result.get("concepts", []))
    
    return {"raw_concepts": list(set(all_raw_concepts)), "job_id": job_id}

@celery_app.task(name="ingestion.abstract_concepts")
def abstract_concepts_task(data):
    raw_concepts = data["raw_concepts"]
    job_id = data["job_id"]
    update_job_status(job_id, "abstracting_concepts")
    
    high_level = llm_extractor.abstract_concepts(raw_concepts)
    
    # SAVE FOR HUMAN REVIEW
    update_job_review_payload(job_id, high_level)
    update_job_status(job_id, "waiting_for_review")
    
    return "paused_for_review"

def update_job_status(job_id, status):
    session = SessionLocal()
    try:
        job = session.query(CeleryJob).filter(CeleryJob.id == job_id).first()
        if job:
            job.status = status
            session.commit()
    except Exception as e:
        logger.error(f"Failed to update job {job_id}: {e}")
    finally:
        session.close()

def update_job_review_payload(job_id, payload):
    session = SessionLocal()
    try:
        job = session.query(CeleryJob).filter(CeleryJob.id == job_id).first()
        if job:
            job.payload = json.dumps(payload)
            session.commit()
    except Exception as e:
        logger.error(f"Failed to update job {job_id} payload: {e}")
    finally:
        session.close()
