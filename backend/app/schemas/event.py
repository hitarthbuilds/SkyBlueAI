from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class LiveEventIn(BaseModel):
    match_id: str
    timestamp: Optional[float] = None
    type: str
    team: Optional[str] = None
    player_id: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    payload: Optional[Any] = None


class LiveEventOut(BaseModel):
    id: str
    match_id: str
    timestamp: Optional[float] = None
    type: str
    team: Optional[str] = None
    player_id: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    payload: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)
