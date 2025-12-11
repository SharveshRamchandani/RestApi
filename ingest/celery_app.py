import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

app = Celery("n8n_ingest", broker=REDIS_URL, backend=REDIS_URL)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover tasks in the ingest.tasks module
app.autodiscover_tasks(["ingest.tasks"])

from celery.signals import worker_ready
from prometheus_client import start_http_server

@worker_ready.connect
def start_prometheus_server(sender, **kwargs):
    # Start on port 9090 inside the worker container
    try:
        start_http_server(9090)
        print("Prometheus metrics server started on port 9090")
    except Exception as e:
        print(f"Failed to start Prometheus server: {e}")

# Celery Beat Schedule
from celery.schedules import crontab

app.conf.beat_schedule = {
    'fetch-youtube-daily': {
        'task': 'ingest.fetch_youtube',
        'schedule': crontab(hour=0, minute=0), # Daily at midnight
        'args': ('US',),
    },
    'fetch-forum-daily': {
        'task': 'ingest.fetch_forum',
        'schedule': crontab(hour=0, minute=30), # Daily at 00:30
        'args': (3,),
    },
    'fetch-trends-weekly': {
        'task': 'ingest.fetch_trends',
        'schedule': crontab(day_of_week='mon', hour=1, minute=0), # Mondays
    },
}
