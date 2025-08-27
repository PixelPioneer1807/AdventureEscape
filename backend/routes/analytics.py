from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from db.database import get_db
from models.analytics_event import AnalyticsEvent
from core.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/event")
def log_event(event: Dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Accepts { story_id, event_type, payload } and logs to analytics_events.
    """
    ev = AnalyticsEvent(
        user_id=current_user.id,
        story_id=event.get("story_id"),
        event_type=event["event_type"],
        payload=event.get("payload", {})
    )
    db.add(ev)
    db.commit()
    return {"message": "Event logged"}

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """
    Returns aggregated metrics:
      - total_starts
      - total_choices
      - total_endings
      - total_wins
      - completion_rate
      - winning_rate
    """
    total_starts = db.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == "start").count()
    total_choices = db.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == "choice").count()
    total_endings = db.query(AnalyticsEvent).filter(AnalyticsEvent.event_type == "ending").count()
    total_wins = db.query(AnalyticsEvent).filter(
        AnalyticsEvent.event_type == "ending",
        AnalyticsEvent.payload["is_winning_ending"].as_boolean() == True
    ).count()
    completion_rate = (total_endings / total_starts * 100) if total_starts else 0
    winning_rate = (total_wins / total_endings * 100) if total_endings else 0
    return {
        "total_starts": total_starts,
        "total_choices": total_choices,
        "total_endings": total_endings,
        "total_wins": total_wins,
        "completion_rate": round(completion_rate, 1),
        "winning_rate": round(winning_rate, 1)
    }
