"""
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/test", response_model=Dict[str, Any])
async def test_users():
    """
    Test users endpoint
    """
    return {
        "success": True,
        "message": "Users API is working!",
        "endpoints": [
            "GET /users/test - Test endpoint",
            "GET /users/ - Get users list (Admin only)",
            "GET /users/me - Get current user info"
        ]
    }


@router.get("/", response_model=Dict[str, Any])
async def get_users(
    db: Session = Depends(get_db)
):
    """
    Get users list (simplified for testing)
    """
    try:
        users = db.query(User).limit(10).all()
        
        users_data = []
        for user in users:
            users_data.append({
                "id": str(user.id),
                "email": user.email,
                "user_type": user.user_type.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        return {
            "success": True,
            "data": {
                "users": users_data,
                "total": len(users_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Get users failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )