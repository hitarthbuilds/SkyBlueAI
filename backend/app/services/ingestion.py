import json
import os
from typing import Optional, Tuple

import aiofiles
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Match

settings = get_settings()


def ensure_storage() -> None:
    os.makedirs(settings.storage_root, exist_ok=True)
    os.makedirs(os.path.join(settings.storage_root, "videos"), exist_ok=True)
    os.makedirs(os.path.join(settings.storage_root, "events"), exist_ok=True)


async def save_upload(file, subdir: str) -> str:
    ensure_storage()
    filename = file.filename or "upload.bin"
    safe_name = filename.replace("/", "_")
    dest = os.path.join(settings.storage_root, subdir, safe_name)
    async with aiofiles.open(dest, "wb") as out:
        content = await file.read()
        await out.write(content)
    return dest


def load_event_data(path: str) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_or_create_match(
    db: Session,
    match_id: Optional[str],
    home_team: Optional[str],
    away_team: Optional[str],
    match_date: Optional[str],
) -> Match:
    if match_id:
        match = db.query(Match).filter(Match.id == match_id).first()
        if match:
            return match
    match = Match(
        home_team=home_team,
        away_team=away_team,
        match_date=match_date,
        status="ingested",
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def attach_event_data(db: Session, match: Match, path: str) -> Match:
    match.event_data_path = path
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def attach_video(db: Session, match: Match, path: str) -> Match:
    match.video_path = path
    db.add(match)
    db.commit()
    db.refresh(match)
    return match
