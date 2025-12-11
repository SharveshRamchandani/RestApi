import asyncio
import logging
from ingest.celery_app import app
from ingest.fetchers.youtube import YouTubeFetcher
from ingest.fetchers.discourse import DiscourseFetcher
from ingest.fetchers.trends import TrendsFetcher
from api.db.base import AsyncSessionLocal
from api.db.models import Workflow
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func
from sqlalchemy import text
from ingest.metrics import FETCH_COUNT_TOTAL, FETCH_FAILURES_TOTAL, TASK_DURATION_SECONDS
from ingest.search import index_item
import os

USE_OPENSEARCH = os.getenv("USE_OPENSEARCH", "false").lower() == "true"

logger = logging.getLogger(__name__)

async def upsert_workflows(items):
    if not items:
        return
    
    async with AsyncSessionLocal() as session:
        for item in items:
            # Side effect: Index to Search (synchronous call, preferably move to async task)
            if USE_OPENSEARCH:
                try:
                    index_item(item)
                except Exception as e:
                    logger.error(f"Failed to index item: {e}")

            stmt = insert(Workflow).values(
                platform=item["platform"],
                source_id=item["source_id"],
                source_url=item["source_url"],
                workflow=item["workflow"],
                normalized_title=item["normalized_title"],
                country=item["country"],
                popularity_metrics=item["popularity_metrics"],
                latest_metrics=item["popularity_metrics"], 
                # raw_snapshots is distinct, initially we can just store the list of 1
                raw_snapshots=[item["popularity_metrics"]] 
            )
            
            # Upsert logic
            update_dict = {
                "latest_metrics": stmt.excluded.latest_metrics,
                "popularity_metrics": stmt.excluded.popularity_metrics,
                "last_seen": func.now(),
                "updated_at": func.now()
            }
            
            on_conflict_stmt = stmt.on_conflict_do_update(
                index_elements=['platform', 'source_id'],
                set_=update_dict
            )
            
            await session.execute(on_conflict_stmt)
            
        await session.commit()

def run_async(coro):
    return asyncio.run(coro)

@app.task(bind=True, name="ingest.fetch_youtube")
def task_fetch_youtube(self, region="US"):
    logger.info(f"Starting YouTube fetch for {region}")
    try:
        with TASK_DURATION_SECONDS.labels(task_name="fetch_youtube").time():
            fetcher = YouTubeFetcher()
            items = fetcher.search_videos(region=region)
            logger.info(f"Fetched {len(items)} items from YouTube")
            
            run_async(upsert_workflows(items))
            FETCH_COUNT_TOTAL.labels(platform="YouTube").inc(len(items))
            
            return {"status": "ok", "count": len(items)}
    except Exception as e:
        FETCH_FAILURES_TOTAL.labels(platform="YouTube").inc()
        raise e

@app.task(bind=True, name="ingest.fetch_forum")
def task_fetch_forum(self, pages=3):
    logger.info(f"Starting Discourse fetch for {pages} pages")
    try:
        with TASK_DURATION_SECONDS.labels(task_name="fetch_forum").time():
            fetcher = DiscourseFetcher()
            items = fetcher.fetch_latest_topics(pages=pages)
            logger.info(f"Fetched {len(items)} items from Discourse")
            
            run_async(upsert_workflows(items))
            FETCH_COUNT_TOTAL.labels(platform="Discourse").inc(len(items))
            return {"status": "ok", "count": len(items)}
    except Exception as e:
        FETCH_FAILURES_TOTAL.labels(platform="Discourse").inc()
        raise e

@app.task(bind=True, name="ingest.fetch_trends")
def task_fetch_trends(self):
    logger.info("Starting Google Trends fetch")
    try:
        with TASK_DURATION_SECONDS.labels(task_name="fetch_trends").time():
            fetcher = TrendsFetcher()
            items = fetcher.fetch_trends()
            logger.info(f"Fetched {len(items)} items from Trends")
            
            run_async(upsert_workflows(items))
            FETCH_COUNT_TOTAL.labels(platform="GoogleTrends").inc(len(items))
            return {"status": "ok", "count": len(items)}
    except Exception as e:
        FETCH_FAILURES_TOTAL.labels(platform="GoogleTrends").inc()
        raise e

@app.task(name="ingest.process_pending")
def task_process_pending():
    pass
