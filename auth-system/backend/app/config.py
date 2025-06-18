from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr # Added for email validation
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auth System Backend"
    API_V1_STR: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:3001" # Default for Vite typical dev port

    # JWT Settings
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_env_file_for_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 # Changed from 30 to 15 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Account Security Settings
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 30

    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "devuser"
    POSTGRES_PASSWORD: str = "devpassword"
    POSTGRES_DB: str = "auth_dev_db"
    DATABASE_URL: Optional[str] = None

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None

    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = "smtp.example.com" # Placeholder
    SMTP_USER: Optional[str] = "user@example.com"   # Placeholder
    SMTP_PASSWORD: Optional[str] = "supersecretpassword" # Placeholder
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "noreply@example.com"
    EMAILS_FROM_NAME: Optional[str] = "Auth System"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 1
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48
    EMAILS_ENABLED: bool = False # Default to False for dev/test
    EMAIL_TEMPLATES_DIR: Optional[str] = "app/email-templates" # Optional, if using file templates

    # First superuser (optional)
    # FIRST_SUPERUSER_EMAIL: EmailStr = "admin@example.com"
    # FIRST_SUPERUSER_PASSWORD: str = "adminpassword"

    LOGGING_LEVEL: str = "INFO"
    DEBUG: bool = False # General debug mode
    DB_ECHO_LOG: bool = False # Set to True to see SQLAlchemy logs

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    def __init__(self, **values):
        super().__init__(**values)
        if self.DATABASE_URL is None:
            pg_port = 5432 # Default postgres port
            self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{pg_port}/{self.POSTGRES_DB}"
        if self.REDIS_URL is None:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings: Settings = get_settings()
