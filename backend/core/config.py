from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database - Use relative path that stays constant
    DATABASE_URL: str = "sqlite+aiosqlite:///./risk.db"
    
    # ML Model
    MODEL_PATH: str = "backend/models/model.pkl"
    MODEL_VERSION: str = "1.0"
    
    # API Settings
    API_TITLE: str = "Early Risk Signals API"
    API_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
