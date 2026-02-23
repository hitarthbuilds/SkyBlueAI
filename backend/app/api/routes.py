from typing import Optional

import json
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.limiter import limiter
from app.db.deps import get_db
from app.db.session import SessionLocal
from app.db.models import Match, Player, Event, LiveSnapshot
from app.schemas.event import LiveEventIn, LiveEventOut
from app.schemas.live import LiveSnapshotOut
from app.schemas.match import MatchOut
from app.schemas.player import PlayerMetricsOut
from app.schemas.setpiece import SetPieceRequest, SetPieceResponse
from app.schemas.upload import UploadResponse
from app.services.ingestion import attach_event_data, attach_video, get_or_create_match, save_upload
from app.services.analysis import store_match_analysis
from app.services.setpiece import generate_set_piece
from app.services.injury import compute_injury_risk
from app.services.tactical import simulate_tactical_adjustments
from app.services.live import update_live_snapshot
from app.services.realtime_bus import publish, subscribe

settings = get_settings()

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@router.get("/ready")
def readiness(db: Session = Depends(get_db)) -> dict:
    db_status = "ok"
    redis_status = "unknown"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    if settings.redis_url:
        try:
            from redis import Redis

            Redis.from_url(settings.redis_url).ping()
            redis_status = "ok"
        except Exception:
            redis_status = "error"
    else:
        redis_status = "disabled"

    overall = "ok" if db_status == "ok" and redis_status in ("ok", "disabled") else "degraded"
    return {"status": overall, "db": db_status, "redis": redis_status}


@router.post("/upload/video", response_model=UploadResponse)
@limiter.limit(get_settings().rate_limit_upload)
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    match_id: Optional[str] = Form(None),
    home_team: Optional[str] = Form(None),
    away_team: Optional[str] = Form(None),
    match_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> UploadResponse:
    path = await save_upload(file, "videos")
    match = get_or_create_match(db, match_id, home_team, away_team, match_date)
    attach_video(db, match, path)

    return UploadResponse(match_id=match.id, path=path, status="uploaded")


@router.post("/upload/events", response_model=UploadResponse)
@limiter.limit(get_settings().rate_limit_upload)
async def upload_events(
    request: Request,
    file: UploadFile = File(...),
    match_id: Optional[str] = Form(None),
    home_team: Optional[str] = Form(None),
    away_team: Optional[str] = Form(None),
    match_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> UploadResponse:
    path = await save_upload(file, "events")
    match = get_or_create_match(db, match_id, home_team, away_team, match_date)
    attach_event_data(db, match, path)

    # Inline analysis for MVP
    store_match_analysis(db, match)

    return UploadResponse(match_id=match.id, path=path, status="processed")


@router.get("/match/{match_id}/analysis", response_model=MatchOut)
def get_match_analysis(match_id: str, db: Session = Depends(get_db)) -> MatchOut:
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status != "processed" and match.event_data_path:
        store_match_analysis(db, match)
        db.refresh(match)

    return MatchOut(
        id=match.id,
        home_team=match.home_team,
        away_team=match.away_team,
        match_date=match.match_date,
        status=match.status,
        insights=[
            {
                "id": insight.id,
                "type": insight.type,
                "description": insight.description,
                "severity": insight.severity,
                "data": insight.data,
            }
            for insight in match.insights
        ],
    )


@router.get("/player/{player_id}/metrics", response_model=PlayerMetricsOut)
def get_player_metrics(player_id: str, db: Session = Depends(get_db)) -> PlayerMetricsOut:
    player = (
        db.query(Player)
        .filter((Player.id == player_id) | (Player.external_id == player_id))
        .first()
    )
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.post("/simulate/setpiece", response_model=SetPieceResponse)
def simulate_setpiece(request: SetPieceRequest) -> SetPieceResponse:
    routine = generate_set_piece(request.opponent_profile)
    return SetPieceResponse(**routine)


@router.post("/injury/risk")
def injury_risk(payload: dict) -> dict:
    return compute_injury_risk(payload)


@router.post("/tactical/simulate")
def tactical_simulation(payload: dict) -> dict:
    return simulate_tactical_adjustments(payload)


@router.post("/ingest/event", response_model=LiveEventOut)
@limiter.limit(get_settings().rate_limit_ingest)
def ingest_event(payload: LiveEventIn, request: Request, db: Session = Depends(get_db)) -> LiveEventOut:
    match = db.query(Match).filter(Match.id == payload.match_id).first()
    if not match:
        match = Match(id=payload.match_id, status="live")
        db.add(match)
        db.commit()
        db.refresh(match)

    event = Event(
        match_id=payload.match_id,
        timestamp=payload.timestamp,
        type=payload.type,
        team=payload.team,
        player_id=payload.player_id,
        x=payload.x,
        y=payload.y,
        payload=payload.payload,
    )
    db.add(event)
    match.status = "live"
    db.add(match)
    db.commit()
    db.refresh(event)

    snapshot = update_live_snapshot(db, payload.match_id)
    publish_payload = {
        "event": {
            "id": event.id,
            "match_id": event.match_id,
            "timestamp": event.timestamp,
            "type": event.type,
            "team": event.team,
            "player_id": event.player_id,
            "x": event.x,
            "y": event.y,
            "payload": event.payload,
        },
        "snapshot": snapshot.payload,
    }

    channel = f"match:{payload.match_id}"
    import anyio

    anyio.from_thread.run(publish, channel, publish_payload)

    return event


@router.post("/ingest/events", response_model=List[LiveEventOut])
@limiter.limit(get_settings().rate_limit_ingest)
def ingest_events(payload: List[LiveEventIn], request: Request, db: Session = Depends(get_db)) -> List[LiveEventOut]:
    events: List[LiveEventOut] = []
    if not payload:
        return events

    match = db.query(Match).filter(Match.id == payload[0].match_id).first()
    if not match:
        match = Match(id=payload[0].match_id, status="live")
        db.add(match)
        db.commit()
        db.refresh(match)

    for item in payload:
        event = Event(
            match_id=item.match_id,
            timestamp=item.timestamp,
            type=item.type,
            team=item.team,
            player_id=item.player_id,
            x=item.x,
            y=item.y,
            payload=item.payload,
        )
        db.add(event)
        events.append(event)

    match.status = "live"
    db.add(match)
    db.commit()

    snapshot = update_live_snapshot(db, payload[0].match_id)
    channel = f"match:{payload[0].match_id}"
    publish_payload = {
        "batch": True,
        "snapshot": snapshot.payload,
        "count": len(events),
    }
    import anyio

    anyio.from_thread.run(publish, channel, publish_payload)

    return events


@router.get("/match/{match_id}/live", response_model=LiveSnapshotOut)
def get_live_snapshot(match_id: str, db: Session = Depends(get_db)) -> LiveSnapshotOut:
    snapshot = db.query(LiveSnapshot).filter(LiveSnapshot.match_id == match_id).first()
    if snapshot is None:
        snapshot = update_live_snapshot(db, match_id)
    return LiveSnapshotOut(match_id=match_id, payload=snapshot.payload)


@router.get("/match/{match_id}/events", response_model=List[LiveEventOut])
def get_live_events(match_id: str, limit: int = 50, db: Session = Depends(get_db)) -> List[LiveEventOut]:
    events = (
        db.query(Event)
        .filter(Event.match_id == match_id)
        .order_by(Event.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(events))


@router.websocket("/ws/match/{match_id}")
async def match_ws(websocket: WebSocket, match_id: str) -> None:
    await websocket.accept()
    channel = f"match:{match_id}"

    db = SessionLocal()
    try:
        snapshot = db.query(LiveSnapshot).filter(LiveSnapshot.match_id == match_id).first()
        if snapshot:
            await websocket.send_text(json.dumps({"snapshot": snapshot.payload}))
    finally:
        db.close()

    try:
        async for payload in subscribe(channel):
            await websocket.send_text(payload)
    except WebSocketDisconnect:
        return
