from celery import Celery
from backend.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.CELERY_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Fix #13: All task modules must be listed so Celery workers auto-discover tasks.
    # Previously only health_tasks was included, so ingestion/graph/reasoning/project
    # tasks were never registered on the workers.
    imports=[
        "backend.workers.health_tasks",
        "backend.workers.tasks_ingestion",
        "backend.workers.tasks_graph",
        "backend.workers.tasks_reasoning",
        "backend.workers.tasks_project",
    ]
)
