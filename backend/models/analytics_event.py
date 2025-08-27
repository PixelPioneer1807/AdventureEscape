from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=True)
    event_type = Column(String, index=True)  # "start", "choice", "ending"
    payload = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
