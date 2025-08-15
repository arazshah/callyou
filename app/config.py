import os
from typing import Optional, List, Union
from pydantic_settings import BaseSettings
from pydantic import validator, Field


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Consultation Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-secret-key-in-production"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://consultation_user:consultation_password@localhost:5432/consultation_platform"
    DATABASE_TEST_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://:redis_password@localhost:6379/0"
    
    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8080"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # SMS
    SMS_PROVIDER: str = "kavenegar"
    SMS_API_KEY: Optional[str] = None
    SMS_SENDER: Optional[str] = None
    
    # File Upload
    UPLOAD_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: Union[str, List[str]] = "jpg,jpeg,png,gif,pdf,doc,docx,txt,mp4,mp3"
    
    @validator("ALLOWED_FILE_TYPES", pre=True)
    def assemble_file_types(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    # Payment
    ZARINPAL_MERCHANT_ID: Optional[str] = None
    ZARINPAL_SANDBOX: bool = True
    
    # WebRTC
    TURN_SERVER_URL: Optional[str] = None
    TURN_USERNAME: Optional[str] = None
    TURN_PASSWORD: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 8001
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Backup
    BACKUP_PATH: str = "./backups"
    BACKUP_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields for flexibility
        extra = "ignore"


# Create settings instance with error handling
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Error loading settings: {e}")
    print("📝 Using default settings...")
    settings = Settings(
        SECRET_KEY="development-secret-key-change-in-production",
        DATABASE_URL="postgresql://consultation_user:consultation_password@localhost:5432/consultation_platform"
    )