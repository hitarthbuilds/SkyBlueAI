from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import Match
from app.services.analysis import store_match_analysis
from app.services.celery_app import celery_app


@celery_app.task(name="skyblueai.process_match")
def process_match(match_id: str) -> str:
    db: Session = SessionLocal()
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return "match_not_found"
        store_match_analysis(db, match)
        return "processed"
    finally:
        db.close()
