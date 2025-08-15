from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
import logging

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import config
try:
    from app.config import settings
    logger.info("✅ Config loaded successfully")
except Exception as e:
    logger.error(f"❌ Config loading failed: {e}")
    # Use default settings
    class DefaultSettings:
        APP_NAME = "Consultation Platform"
        ENVIRONMENT = "development"
        DEBUG = True
        API_V1_STR = "/api/v1"
        BACKEND_CORS_ORIGINS = ["*"]
        UPLOAD_PATH = "./uploads"
    
    settings = DefaultSettings()

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
    allow_origins=settings.BACKEND_CORS_ORIGINS if hasattr(settings, 'BACKEND_CORS_ORIGINS') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "message": "داده‌های ارسالی نامعتبر است",
                "details": exc.errors(),
                "path": str(request.url)
            }
        }
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": {
                "message": "منبع مورد نظر یافت نشد",
                "path": str(request.url)
            }
        }
    )


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info(f"🚀 Starting {settings.APP_NAME}...")
    logger.info(f"📝 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")
    
    # Create directories
    try:
        os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
        os.makedirs("./logs", exist_ok=True)
        logger.info("📁 Directories created successfully")
    except Exception as e:
        logger.warning(f"⚠️ Could not create directories: {e}")
    
    # Test database connection
    try:
        from app.database import test_connection, create_tables
        
        logger.info("🔍 Testing database connection...")
        if test_connection():
            logger.info("✅ Database connection successful")
            
            # Try to create tables
            try:
                create_tables()
                logger.info("✅ Database tables ready")
            except Exception as e:
                logger.warning(f"⚠️ Could not create tables: {e}")
        else:
            logger.error("❌ Database connection failed")
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
    
    logger.info(f"🎉 {settings.APP_NAME} started successfully!")
    if settings.DEBUG:
        logger.info(f"📚 API Docs: http://localhost:8000{settings.API_V1_STR}/docs")
        logger.info(f"🏥 Health Check: http://localhost:8000/health")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "success": True,
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "features": [
            "User Authentication",
            "User Management", 
            "Consultation System",
            "Wallet Management",
            "Rating System"
        ],
        "docs_url": f"{settings.API_V1_STR}/docs" if settings.DEBUG else None
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        from app.database import test_connection
        db_status = test_connection()
        
        return {
            "success": True,
            "status": "healthy" if db_status else "degraded",
            "checks": {
                "database": "connected" if db_status else "disconnected",
                "app": "running"
            },
            "app_name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
            "debug": settings.DEBUG
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "app_name": settings.APP_NAME
            }
        )


# Try to include API router
try:
    from app.api.v1 import api_router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    logger.info("✅ API routes loaded successfully")
except Exception as e:
    logger.error(f"❌ Failed to load API routes: {e}")
    
    # Add fallback routes
    @app.get(f"{settings.API_V1_STR}/test")
    async def api_test():
        return {
            "success": True,
            "message": "API is working but some routes failed to load",
            "error": str(e)
        }
    
    @app.get(f"{settings.API_V1_STR}/status")
    async def api_status():
        return {
            "success": False,
            "message": "API routes not fully loaded",
            "error": str(e),
            "available_endpoints": [
                f"GET {settings.API_V1_STR}/test",
                f"GET {settings.API_V1_STR}/status",
                "GET /health",
                "GET /"
            ]
        }