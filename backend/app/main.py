from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.limiter import limiter
from app.core.logging import setup_logging, RequestContextMiddleware, SecurityHeadersMiddleware
from app.db.session import engine
from app.db.models import Base
from app.api.router import api_router

settings = get_settings()
setup_logging(settings.log_level)

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    if settings.auto_create_db:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(api_router)
