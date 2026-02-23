from typing import Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    match_id: str
    path: str
    status: str
    message: Optional[str] = None
