from prometheus_client import start_http_server, Counter, Summary
import time

# Define metrics
FETCH_COUNT_TOTAL = Counter('ingest_fetch_count_total', 'Total number of items fetched', ['platform'])
FETCH_FAILURES_TOTAL = Counter('ingest_fetch_failures_total', 'Total number of fetch failures', ['platform'])
TASK_DURATION_SECONDS = Summary('celery_task_duration_seconds', 'Time spent processing celery tasks', ['task_name'])
