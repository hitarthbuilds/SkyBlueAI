from typing import Optional, Any
from pydantic import BaseModel


class SetPieceRequest(BaseModel):
    match_id: Optional[str] = None
    opponent_profile: Optional[Any] = None


class SetPieceResponse(BaseModel):
    routine_id: str
    description: str
    animation: Any
