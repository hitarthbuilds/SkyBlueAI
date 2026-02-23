from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict


class MatchCreate(BaseModel):
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    match_date: Optional[str] = None


class InsightOut(BaseModel):
    id: str
    type: str
    description: str
    severity: str
    data: Optional[Any] = None


class MatchOut(BaseModel):
    id: str
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    match_date: Optional[str] = None
    status: str
    insights: List[InsightOut] = []

    model_config = ConfigDict(from_attributes=True)
