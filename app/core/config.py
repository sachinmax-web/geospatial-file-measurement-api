import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    PROJECT_NAME: str = "Geospatial File Measurement API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = "sqlite:///./geospatial.db"
    
    # Storage & Security
    MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB limit
    UPLOAD_DIRECTORY: str = "./uploads"
    ALLOWED_EXTENSIONS: List[str] = [".kml", ".zip"]
    
    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
