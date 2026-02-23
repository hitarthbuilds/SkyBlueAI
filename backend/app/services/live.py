from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.db.models import Event, LiveSnapshot, Match
from app.services.analysis import compute_heatmap, compute_xthreat, compute_pressing_intensity


def compute_live_snapshot_payload(events: List[Event]) -> Dict[str, Any]:
    event_dicts = [
        {
            "type": e.type,
            "x": e.x,
            "y": e.y,
            "team": e.team,
            "player_id": e.player_id,
            "timestamp": e.timestamp,
        }
        for e in events
    ]

    heatmap = compute_heatmap(event_dicts)
    xthreat = compute_xthreat(heatmap)
    pressing_index = compute_pressing_intensity(event_dicts)

    shots = sum(1 for e in event_dicts if e["type"] == "shot")
    passes = sum(1 for e in event_dicts if e["type"] == "pass")
    transitions = sum(1 for e in event_dicts if e["type"] == "transition")

    last_event = event_dicts[-1] if event_dicts else None

    return {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "counts": {
            "shots": shots,
            "passes": passes,
            "transitions": transitions,
        },
        "pressing_index": pressing_index,
        "heatmap": heatmap,
        "xthreat": xthreat,
        "last_event": last_event,
    }


def update_live_snapshot(db: Session, match_id: str, window: int = 80) -> LiveSnapshot:
    events = (
        db.query(Event)
        .filter(Event.match_id == match_id)
        .order_by(Event.created_at.desc())
        .limit(window)
        .all()
    )
    events = list(reversed(events))

    payload = compute_live_snapshot_payload(events)

    snapshot = db.query(LiveSnapshot).filter(LiveSnapshot.match_id == match_id).first()
    if snapshot is None:
        snapshot = LiveSnapshot(match_id=match_id, payload=payload)
        db.add(snapshot)
    else:
        snapshot.payload = payload
        snapshot.updated_at = datetime.utcnow()
        db.add(snapshot)

    db.commit()
    db.refresh(snapshot)
    return snapshot
