from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os
import secrets

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    # DB
    DATABASE_URL: Optional[str] = None

    # CORS
    ALLOWED_ORIGINS: str = ""

    # Euriai (optional, can stay unset in .env for now)
    EURI_API_KEY: Optional[str] = None
    EURI_BASE_URL: Optional[str] = None
    EURI_MODEL: str = "euriai-chat-mini"
    
    # --- IMAGE GENERATION MODEL (Updated) ---
    EURI_IMAGE_MODEL: str = "black-forest-labs/FLUX.1-schnell"
    # ----------------------------------------
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Back-compat envs already used in your project (optional)
    CHOREO_OPENAI_CONNECTION_OPENAI_API_KEY: Optional[str] = None
    CHOREO_OPENAI_CONNECTION_SERVICEURL: Optional[str] = None

    def __init__(self, **values):
        super().__init__(**values)
        # If DATABASE_URL not set and not DEBUG, try building Postgres URL from parts.
        # With your current .env (SQLite + DEBUG=True), nothing changes.
        if not self.DATABASE_URL and not self.DEBUG:
            db_user = os.getenv("DB_USER")
            db_password = os.getenv("DB_PASSWORD")
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT")
            db_name = os.getenv("DB_NAME")
            if all([db_user, db_password, db_host, db_port, db_name]):
                self.DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(",") if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()