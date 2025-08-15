"""
API v1 router
"""

from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router

api_router = APIRouter()

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])