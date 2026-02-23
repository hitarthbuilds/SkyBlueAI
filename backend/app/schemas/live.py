from typing import Any
from pydantic import BaseModel


class LiveSnapshotOut(BaseModel):
    match_id: str
    payload: Any
