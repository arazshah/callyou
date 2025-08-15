from pydantic_settings import BaseSettings
from typing import List, Union
from pydantic import validator
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Consultation Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-secret-key-in-production"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://consultation_user:consultation_password@localhost:5432/consultation_platform"
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # File Upload
    UPLOAD_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()