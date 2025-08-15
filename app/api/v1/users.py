"""
User management endpoints
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging

from app.database import get_db
from app.schemas.user import (
    UserUpdate, UserProfileUpdate, UserResponse,
    UserProfileResponse, UserWithProfile, ActivityLogResponse
)
from app.services.user import UserService
from app.dependencies import (
    get_current_user, get_current_active_user,
    get_current_admin_user, api_rate_limiter
)
from app.models.user import User, UserType

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_users(
    query: Optional[str] = Query(None, description="جستجو در نام، ایمیل یا نام نمایشی"),
    user_type: Optional[UserType] = Query(None, description="نوع کاربر"),
    is_active: Optional[bool] = Query(None, description="وضعیت فعال بودن"),
    limit: int = Query(20, ge=1, le=100, description="تعداد نتایج"),
    offset: int = Query(0, ge=0, description="شروع از"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    _: None = Depends(api_rate_limiter)
):
    """
    Get users list (Admin only)
    """
    try:
        user_service = UserService(db)
        users = user_service.search_users(
            query=query,
            user_type=user_type,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": {
                "users": users,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(users)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Get users failed: {e}")
        raise


@router.get("/{user_id}", response_model=Dict[str, Any])
async def get_user(
    user_id: UUID = Path(..., description="شناسه کاربر"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    """
    try:
        user_service = UserService(db)
        
        # Check permissions (users can view themselves, admins can view anyone)
        if current_user.id != user_id and not current_user.is_admin():
            from app.core.exceptions import AuthorizationError
            raise AuthorizationError("شما مجاز به مشاهده این کاربر نیستید")
        
        user_with_profile = user_service.get_user_with_profile(user_id)
        
        if not user_with_profile:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("کاربر یافت نشد")
        
        return {
            "success": True,
            "data": user_with_profile
        }
        
    except Exception as e:
        logger.error(f"Get user failed: {e}")
        raise


@router.put("/{user_id}", response_model=Dict[str, Any])
async def update_user(
    user_id: UUID = Path(..., description="شناسه کاربر"),
    user_data: UserUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user information
    """
    try:
        user_service = UserService(db)
        updated_user = user_service.update_user(
            user_id=user_id,
            user_data=user_data,
            current_user=current_user
        )
        
        return {
            "success": True,
            "message": "اطلاعات کاربر با موفقیت به‌روزرسانی شد",
            "data": updated_user
        }
        
    except Exception as e:
        logger.error(f"Update user failed: {e}")
        raise


@router.get("/{user_id}/profile", response_model=Dict[str, Any])
async def get_user_profile(
    user_id: UUID = Path(..., description="شناسه کاربر"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user profile
    """
    try:
        user_service = UserService(db)
        
        # Check permissions
        if current_user.id != user_id and not current_user.is_admin():
            from app.core.exceptions import AuthorizationError
            raise AuthorizationError("شما مجاز به مشاهده این پروفایل نیستید")
        
        user_with_profile = user_service.get_user_with_profile(user_id)
        
        if not user_with_profile:
            from app.core.exceptions import NotFoundError
            raise NotFoundError("کاربر یافت نشد")
        
        return {
            "success": True,
            "data": user_with_profile.profile if user_with_profile.profile else None
        }
        
    except Exception as e:
        logger.error(f"Get user profile failed: {e}")
        raise


@router.put("/{user_id}/profile", response_model=Dict[str, Any])
async def update_user_profile(
    user_id: UUID = Path(..., description="شناسه کاربر"),
    profile_data: UserProfileUpdate = ...,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    """
    try:
        user_service = UserService(db)
        updated_profile = user_service.create_or_update_profile(
            user_id=user_id,
            profile_data=profile_data,
            current_user=current_user
        )
        
        return {
            "success": True,
            "message": "پروفایل با موفقیت به‌روزرسانی شد",
            "data": updated_profile
        }
        
    except Exception as e:
        logger.error(f"Update user profile failed: {e}")
        raise


@router.get("/{user_id}/activity", response_model=Dict[str, Any])
async def get_user_activity(
    user_id: UUID = Path(..., description="شناسه کاربر"),
    limit: int = Query(50, ge=1, le=100, description="تعداد نتایج"),
    offset: int = Query(0, ge=0, description="شروع از"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user activity logs
    """
    try:
        user_service = UserService(db)
        activity_logs = user_service.get_user_activity_logs(
            user_id=user_id,
            current_user=current_user,
            limit=limit,
            offset=offset
        )
        
        # Convert to response schema
        logs_response = [ActivityLogResponse.from_orm(log) for log in activity_logs]
        
        return {
            "success": True,
            "data": {
                "activity_logs": logs_response,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": len(logs_response)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Get user activity failed: {e}")
        raise


@router.get("/{user_id}/stats", response_model=Dict[str, Any])
async def get_user_stats(
    user_id: UUID = Path(..., description="شناسه کاربر"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user statistics
    """
    try:
        user_service = UserService(db)
        
        # Check permissions
        if current_user.id != user_id and not current_user.is_admin():
            from app.core.exceptions import AuthorizationError
            raise AuthorizationError("شما مجاز به مشاهده این آمار نیستید")
        
        stats = user_service.get_user_stats(user_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Get user stats failed: {e}")
        raise


@router.post("/{user_id}/deactivate", response_model=Dict[str, Any])
async def deactivate_user(
    user_id: UUID = Path(..., description="شناسه کاربر"),
    reason: Optional[str] = Query(None, description="دلیل غیرفعال‌سازی"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate user account
    """
    try:
        user_service = UserService(db)
        success = user_service.deactivate_user(
            user_id=user_id,
            current_user=current_user,
            reason=reason
        )
        
        if success:
            return {
                "success": True,
                "message": "حساب کاربری با موفقیت غیرفعال شد"
            }
        else:
            from app.core.exceptions import ValidationError
            raise ValidationError("غیرفعال‌سازی حساب کاربری ناموفق بود")
        
    except Exception as e:
        logger.error(f"Deactivate user failed: {e}")
        raise


# Shortcut endpoints for current user
@router.get("/me/profile", response_model=Dict[str, Any])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    """
    return await get_user_profile(current_user.id, current_user, db)


@router.put("/me/profile", response_model=Dict[str, Any])
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    return await update_user_profile(current_user.id, profile_data, current_user, db)


@router.get("/me/activity", response_model=Dict[str, Any])
async def get_my_activity(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user activity logs
    """
    return await get_user_activity(current_user.id, limit, offset, current_user, db)


@router.get("/me/stats", response_model=Dict[str, Any])
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user statistics
    """
    return await get_user_stats(current_user.id, current_user, db)


@router.post("/me/deactivate", response_model=Dict[str, Any])
async def deactivate_my_account(
    reason: Optional[str] = Query(None, description="دلیل غیرفعال‌سازی"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate current user account
    """
    return await deactivate_user(current_user.id, reason, current_user, db)