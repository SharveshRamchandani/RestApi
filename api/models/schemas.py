from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime

class WorkflowBase(BaseModel):
    platform: str
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    workflow: str
    normalized_title: Optional[str] = None
    country: Optional[str] = None
    popularity_metrics: Dict[str, Any]
    collected_at: Optional[datetime] = None

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowRead(WorkflowBase):
    id: int
    score: Optional[float]
    first_seen: Optional[datetime]
    last_seen: Optional[datetime]
    inserted_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True # Pydantic v1
        from_attributes = True # Pydantic v2 support
