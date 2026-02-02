from backend.workers.celery_app import celery_app
from backend.core.logging import logger
from backend.db.neo4j import neo4j_client
from backend.db.graph_schema import Label, Relation
from backend.db.sqlite import SessionLocal
from backend.db.models import CeleryJob
from datetime import datetime

@celery_app.task(name="graph.write_concepts")
def write_concepts_task(job_id: int, approved_concepts: list, paper_id: int):
    # This task is triggered after human approval
    logger.info(f"Writing {len(approved_concepts)} concepts to Graph for Job {job_id}")
    
    driver = neo4j_client.driver
    if not driver:
         neo4j_client.connect()
         driver = neo4j_client.driver

    with driver.session() as session:
        for concept in approved_concepts:
            # 1. Merge Concept
            query = f"""
            MERGE (c:{Label.Concept} {{name: $name}})
            ON CREATE SET c.description = $desc, c.confidence = $conf
            ON MATCH SET c.description = $desc, c.confidence = $conf
            RETURN c
            """
            session.run(query, name=concept["name"], desc=concept["description"], conf=concept["confidence"])
            
            # 2. Link to Paper (Simplified for demo)
            # In real system, we'd lookup specific paper node
            # query_link = f"""
            # MATCH (c:{Label.Concept} {{name: $name}})
            # MERGE (p:{Label.Paper} {{id: $paper_id}})
            # MERGE (c)-[:MENTIONED_IN]->(p)
            # """
            # session.run(query_link, name=concept["name"], paper_id=paper_id)

    # Mark Job Complete
    finalize_job(job_id)
    return "graph_write_complete"

def finalize_job(job_id):
    session = SessionLocal()
    try:
        job = session.query(CeleryJob).filter(CeleryJob.id == job_id).first()
        if job:
            job.status = "completed"
            job.finished_at = datetime.utcnow()
            session.commit()
    except Exception as e:
        logger.error(f"Failed to finalize job {job_id}: {e}")
    finally:
        session.close()
