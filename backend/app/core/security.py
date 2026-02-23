from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import get_settings

settings = get_settings()


def _get_keys() -> list[str]:
    return [k.strip() for k in settings.api_keys.split(",") if k.strip()]


def is_api_key_valid(key: Optional[str]) -> bool:
    keys = _get_keys()
    if not keys:
        return True
    return key in keys


def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if is_api_key_valid(x_api_key):
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
