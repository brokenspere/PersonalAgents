import os
from celery import Celery

# Use Redis as the broker and backend
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "agent_platform",
    broker=redis_url,
    backend=redis_url,
    include=["scheduler.tasks", "workers.scraper.tasks", "workers.notification.tasks"]
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
