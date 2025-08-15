from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

from app.config import settings
from app.database import test_connection, create_tables

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
    print(f"🚀 Starting {settings.APP_NAME}...")
    print(f"📝 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug mode: {settings.DEBUG}")
    
    # Create directories
    try:
        os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
        print("📁 Directories created successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not create directories: {e}")
    
    # Test database connection
    print("🔍 Testing database connection...")
    if test_connection():
        print("✅ Database connection successful")
        
        # Try to create tables
        try:
            create_tables()
            print("✅ Database tables ready")
        except Exception as e:
            print(f"⚠️ Warning: Could not create tables: {e}")
    else:
        print("❌ Database connection failed")
        print("⚠️ Application will start but database features may not work")
    
    print(f"🎉 {settings.APP_NAME} started successfully!")
    if settings.DEBUG:
        print(f"📚 API Docs: http://localhost:8000{settings.API_V1_STR}/docs")
        print(f"🏥 Health Check: http://localhost:8000/health")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "docs_url": f"{settings.API_V1_STR}/docs" if settings.DEBUG else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_status = test_connection()
        
        return {
            "status": "healthy" if db_status else "degraded",
            "database": "connected" if db_status else "disconnected",
            "app_name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "debug": settings.DEBUG
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "app_name": settings.APP_NAME
            }
        )


# Simple test endpoint
@app.get(f"{settings.API_V1_STR}/test")
async def test_endpoint():
    """Test endpoint"""
    return {
        "message": "API is working!",
        "timestamp": "2024-01-01T00:00:00Z",
        "database_status": test_connection()
    }


# Include API routes (will be added later)
# app.include_router(api_router, prefix=settings.API_V1_STR)