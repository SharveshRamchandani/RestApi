from fastapi import FastAPI, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from api.db.base import get_db, engine, Base
from api.db.models import Workflow
from api.models.schemas import WorkflowCreate, WorkflowRead
from ingest.tasks import upsert_workflows
from prometheus_client import make_asgi_app

app = FastAPI(title="n8n Workflow Popularity API")

# Expose Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup():
    # In production, use Alembic. For quick MVP dev, we can create tables.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/workflows/import")
async def import_workflows(
    items: List[WorkflowCreate], 
    db: AsyncSession = Depends(get_db),
    # token: str = Depends(...) # Auth placeholder
):
    # Convert Pydantic models to dicts for the upsert logic
    data = [item.dict() for item in items]
    await upsert_workflows(data)
    return {"inserted": len(items), "status": "processed"}

@app.get("/workflows", response_model=List[WorkflowRead])
async def get_workflows(
    platform: Optional[str] = None,
    country: Optional[str] = None,
    sort: str = "score",
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Workflow)
    
    if platform:
        stmt = stmt.where(Workflow.platform == platform)
    if country:
        stmt = stmt.where(Workflow.country == country)
        
    if sort == "last_seen":
        stmt = stmt.order_by(desc(Workflow.last_seen))
    else:
        stmt = stmt.order_by(desc(Workflow.score))
        
    stmt = stmt.limit(limit).offset(offset)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@app.get("/workflows/{id}", response_model=WorkflowRead)
async def get_workflow(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow).where(Workflow.id == id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return item
