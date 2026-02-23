import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON, Float, Index
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    match_date = Column(String, nullable=True)
    event_data_path = Column(String, nullable=True)
    video_path = Column(String, nullable=True)
    status = Column(String, default="ingested")
    created_at = Column(DateTime, default=datetime.utcnow)

    insights = relationship("Insight", back_populates="match")
    players = relationship("Player", back_populates="match")


class Player(Base):
    __tablename__ = "players"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    team = Column(String, nullable=True)
    position = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True)
    match_id = Column(String, ForeignKey("matches.id"))

    match = relationship("Match", back_populates="players")


class Insight(Base):
    __tablename__ = "insights"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String, ForeignKey("matches.id"))
    type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, default="medium")
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="insights")


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String, ForeignKey("matches.id"), index=True, nullable=False)
    timestamp = Column(Float, nullable=True)
    type = Column(String, nullable=False)
    team = Column(String, nullable=True)
    player_id = Column(String, nullable=True)
    x = Column(Float, nullable=True)
    y = Column(Float, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class LiveSnapshot(Base):
    __tablename__ = "live_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    match_id = Column(String, ForeignKey("matches.id"), unique=True, nullable=False)
    payload = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, index=True)


Index("ix_events_match_created", Event.match_id, Event.created_at)
