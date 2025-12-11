from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Numeric, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from .base import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(32), nullable=False)
    source_id = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    workflow = Column(Text, nullable=False)
    normalized_title = Column(Text, nullable=True)
    country = Column(String(32), nullable=True)
    popularity_metrics = Column(JSONB, nullable=False)
    latest_metrics = Column(JSONB, nullable=True)
    score = Column(Numeric, default=0)
    
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    inserted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    raw_snapshots = Column(ARRAY(JSONB), nullable=True)

    __table_args__ = (
        UniqueConstraint('platform', 'source_id', name='uq_platform_source_id'),
        Index('idx_platform_country', 'platform', 'country'),
        Index('idx_score', score.desc()),
        # Note: GIN index for text search usually requires raw SQL DDL or specific dialect usage.
        # We will add it via migration or raw SQL if needed, but for now we stick to standard core.
        # Index('idx_normalized_title_gin', 'normalized_title', postgresql_using='gin') 
    )
