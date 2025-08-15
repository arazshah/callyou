"""
API v1 package
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(
    auth_router, 
    prefix="/auth", 
    tags=["Authentication"]
)

api_router.include_router(
    users_router, 
    prefix="/users", 
    tags=["Users"]
)

# Export api_router
__all__ = ["api_router"]