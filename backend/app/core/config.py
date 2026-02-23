from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SkyBlueAI"
    env: str = "dev"
    database_url: str = "sqlite:///./skyblueai.db"
    redis_url: str = "redis://localhost:6379/0"
    storage_root: str = "/Users/hitarthdesai/Downloads/man city/storage"
    jwt_secret: str = "change-me"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "skyblue"
    minio_secret_key: str = "skyblue123"
    minio_bucket: str = "skyblueai"
    cors_origins: str = "*"
    log_level: str = "INFO"
    auto_create_db: bool = True
    rate_limit_ingest: str = "120/second"
    rate_limit_upload: str = "30/minute"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
