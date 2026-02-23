from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class PlayerMetricsOut(BaseModel):
    id: str
    external_id: Optional[str] = None
    name: str
    team: Optional[str] = None
    position: Optional[str] = None
    metrics: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)
