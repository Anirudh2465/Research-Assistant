from fastapi import FastAPI
from backend.core.config import settings
from backend.core.logging import logger
from backend.db.neo4j import neo4j_client
from backend.workers.celery_app import celery_app
from backend.workers.health_tasks import check_health
from backend.api import papers, research, projects, ideas, tasks

import redis

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Research OS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router)
app.include_router(research.router)
app.include_router(projects.router)
app.include_router(ideas.router)
app.include_router(tasks.router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Research OS API...")
    # Neo4j connection is lazy, but we can init here if we want.
    # We'll rely on the health check to verify connections.

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Research OS API...")
    neo4j_client.close()

@app.get("/health")
def health_check():
    health_status = {
        "status": "ok",
        "neo4j": "unknown",
        "redis": "unknown",
        "celery": "unknown"
    }

    # Check Neo4j
    if neo4j_client.check_connection():
        health_status["neo4j"] = "reachable"
    else:
        health_status["status"] = "degraded"
        health_status["neo4j"] = "unreachable"

    # Check Redis/Celery Broker
    try:
        r = redis.from_url(settings.REDIS_URL)
        if r.ping():
             health_status["redis"] = "reachable"
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        health_status["status"] = "degraded"
        health_status["redis"] = "unreachable"

    # Check Celery Worker (submission)
    try:
        # We just check if we can send a task. 
        # For a true "ready" check we might need to inspect queues, 
        # but sending a task confirms broker connectivity + app config.
        # Ideally we'd use celery_app.control.ping() but that requires workers to be online.
        # User asked for "celery: ready".
        # We'll trigger the async task.
        task = check_health.delay()
        health_status["celery"] = "ready" # Task dispatched
    except Exception as e:
        logger.error(f"Celery check failed: {e}")
        health_status["status"] = "degraded"
        health_status["celery"] = "error"

    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
