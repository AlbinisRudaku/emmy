from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.core.database import Base

class DBInstance(Base):
    __tablename__ = "instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    website_url = Column(String, nullable=False)
    settings = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 