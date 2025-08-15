from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import settings
from app.database import test_connection

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A secure online consultation platform",
    version="1.0.0",
    docs_url=f"{settings.API_V1_STR}/docs" if settings.DEBUG else None,
    redoc_url=f"{settings.API_V1_STR}/redoc" if settings.DEBUG else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    # Create directories
    os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    
    # Test database connection
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    print(f"🚀 {settings.APP_NAME} started!")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    if settings.DEBUG:
        print(f"📚 Docs: http://localhost:8000{settings.API_V1_STR}/docs")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }


# Include API routes (will be added later)
# app.include_router(api_router, prefix=settings.API_V1_STR)