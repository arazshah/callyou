"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.models.user import User, UserType

logger = logging.getLogger(__name__)
router = APIRouter()


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent string"""
    return request.headers.get("User-Agent", "unknown")


@router.post("/register", response_model=Dict[str, Any])
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    try:
        from app.services.auth import AuthService
        
        auth_service = AuthService(db)
        
        # Get client info
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Register user
        user, verification_token = auth_service.register_user(
            user_data=user_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"User registered successfully: {user.email}")
        
        return {
            "success": True,
            "message": "ثبت‌نام با موفقیت انجام شد",
            "data": {
                "user_id": str(user.id),
                "email": user.email,
                "verification_required": True,
                "message": "لینک تأیید به ایمیل شما ارسال شد"
            }
        }
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Dict[str, Any])
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    User login
    """
    try:
        from app.services.auth import AuthService
        
        auth_service = AuthService(db)
        
        # Get client info
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Authenticate user
        user = auth_service.authenticate_user(
            credentials=credentials,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Create tokens
        tokens = auth_service.create_tokens(user)
        
        # Get user with profile
        user_with_profile = auth_service.get_user_with_profile(user.id)
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return {
            "success": True,
            "message": "ورود با موفقیت انجام شد",
            "data": {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "user_type": user.user_type.value,
                    "is_verified": user.is_verified
                },
                "tokens": tokens
            }
        }
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/test", response_model=Dict[str, Any])
async def test_auth():
    """
    Test authentication endpoint
    """
    return {
        "success": True,
        "message": "Authentication API is working!",
        "endpoints": [
            "POST /auth/register - Register new user",
            "POST /auth/login - User login",
            "GET /auth/test - Test endpoint"
        ]
    }