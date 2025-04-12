"""
Celery application for background tasks.
"""
from celery import Celery
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Celery configuration
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery(
    "cyberforge",
    broker=redis_url,
    backend=redis_url,
    include=["src.tasks"]
)

# Configure Celery
app.conf.update(
    result_expires=3600,  # Results expire after 1 hour
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=4,
)

# Configure periodic tasks
app.conf.beat_schedule = {
    "scheduled-darkweb-scan": {
        "task": "src.tasks.scan_darkweb_sources",
        "schedule": 3600.0,  # Run every hour
        "args": (),
    },
    "update-threat-intelligence": {
        "task": "src.tasks.update_threat_intelligence",
        "schedule": 86400.0,  # Run daily
        "args": (),
    },
    "cleanup-old-data": {
        "task": "src.tasks.cleanup_old_data",
        "schedule": 604800.0,  # Run weekly
        "args": (30,),  # Keep data for 30 days
    },
}

if __name__ == "__main__":
    app.start()