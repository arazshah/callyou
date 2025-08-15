"""
Application settings using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import field_validator
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Consultation Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-secret-key-in-production-minimum-32-characters"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://consultation_user:[REDACTED]@localhost:5432/consultation_platform"

    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Validate and parse CORS origins.
        Accepts a JSON list or comma-separated string.
        """
        if isinstance(v, str):
            # Strip brackets if it's a raw string like "[...]"
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed]
                except json.JSONDecodeError:
                    pass
            # Otherwise treat as comma-separated
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return [str(origin).strip() for origin in v]
        raise ValueError("Invalid CORS origins format. Must be a list or comma-separated string.")

    # File Upload
    UPLOAD_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance with error handling
try:
    settings = Settings()
    print("✅ Settings loaded successfully")
except Exception as e:
    print(f"❌ Error loading settings: {e}")
    print("📝 Falling back to default settings...")
    settings = Settings(
        SECRET_KEY="fallback-secret-key-change-in-production-32-chars",
        DATABASE_URL="postgresql://consultation_user:consultation_password@localhost:5432/consultation_platform"
    )