import time
from .celery_app import celery_app

@celery_app.task(name="check_health")
def check_health():
    """Simple task to verify Celery execution."""
    time.sleep(2)
    return "ok"
