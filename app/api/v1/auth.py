"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserLogin,
    Token,
    UserWithProfile,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    EmailVerification,
)
from app.services.auth import AuthService
from app.dependencies import (
    get_current_user,
    get_current_active_user,
    get_client_ip,
    get_user_agent,
    auth_rate_limiter,
)
from app.models.user import User
from app.core.exceptions import ValidationError, AuthenticationError
from app.services.user import UserService  # Moved up to avoid late import

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Dict[str, Any])
async def register(
    user_data: UserCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: None = Depends(auth_rate_limiter),
):
    """
    Register a new user
    """
    try:
        auth_service = AuthService(db)

        # Get client info
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        # Register user
        user, verification_token = auth_service.register_user(
            user_data=user_data,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # TODO: Send verification email in background
        # background_tasks.add_task(send_verification_email, user.email, verification_token)

        logger.info(f"User registered successfully: {user.email}")

        return {
            "success": True,
            "message": "ثبت‌نام با موفقیت انجام شد",
            "data": {
                "user_id": str(user.id),
                "email": user.email,
                "verification_required": True,
                "message": "لینک تأیید به ایمیل شما ارسال شد",
            },
        }

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise


@router.post("/login", response_model=Dict[str, Any])
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(auth_rate_limiter),
):
    """
    User login
    """
    try:
        auth_service = AuthService(db)

        # Get client info
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        # Authenticate user
        user = auth_service.authenticate_user(
            credentials=credentials,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Create tokens
        tokens = auth_service.create_tokens(user)

        # Get user with profile
        user_service = UserService(db)
        user_with_profile = user_service.get_user_with_profile(user.id)

        logger.info(f"User logged in successfully: {user.email}")

        return {
            "success": True,
            "message": "ورود با موفقیت انجام شد",
            "data": {
                "user": user_with_profile,
                "tokens": tokens,
            },
        }

    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise


@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    """
    Refresh access token
    """
    try:
        auth_service = AuthService(db)
        tokens = auth_service.refresh_access_token(refresh_token)

        return {
            "success": True,
            "message": "توکن با موفقیت تجدید شد",
            "data": tokens,
        }

    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise


@router.post("/logout", response_model=Dict[str, Any])
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    User logout
    """
    try:
        auth_service = AuthService(db)

        # Log activity
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        auth_service._log_activity(
            user=current_user,
            action="user_logout",
            ip_address=ip_address,
            user_agent=user_agent,
            details="User logged out",
        )

        db.commit()

        logger.info(f"User logged out: {current_user.email}")

        return {
            "success": True,
            "message": "خروج با موفقیت انجام شد",
        }

    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise


@router.post("/verify-email", response_model=Dict[str, Any])
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db),
):
    """
    Verify user email
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.verify_email(verification_data.token)

        if success:
            return {
                "success": True,
                "message": "ایمیل با موفقیت تأیید شد",
            }
        else:
            raise ValidationError("تأیید ایمیل ناموفق بود")

    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        raise


@router.post("/resend-verification", response_model=Dict[str, Any])
async def resend_verification(
    email_data: PasswordReset,  # Reuse schema for email
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: None = Depends(auth_rate_limiter),
):
    """
    Resend verification email
    """
    try:
        auth_service = AuthService(db)
        verification_token = auth_service.resend_verification_email(email_data.email)

        # TODO: Send verification email in background
        # background_tasks.add_task(send_verification_email, email_data.email, verification_token)

        return {
            "success": True,
            "message": "ایمیل تأیید مجدداً ارسال شد",
        }

    except Exception as e:
        logger.error(f"Resend verification failed: {e}")
        raise


@router.post("/forgot-password", response_model=Dict[str, Any])
async def forgot_password(
    email_data: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: None = Depends(auth_rate_limiter),
):
    """
    Request password reset
    """
    try:
        auth_service = AuthService(db)
        reset_token = auth_service.request_password_reset(email_data.email)

        # TODO: Send password reset email in background
        # background_tasks.add_task(send_password_reset_email, email_data.email, reset_token)

        return {
            "success": True,
            "message": "در صورت وجود حساب کاربری، لینک بازیابی رمز عبور ارسال شد",
        }

    except Exception as e:
        logger.error(f"Password reset request failed: {e}")
        raise


@router.post("/reset-password", response_model=Dict[str, Any])
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """
    Reset password with token
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.reset_password(
            token=reset_data.token,
            new_password=reset_data.new_password,
        )

        if success:
            return {
                "success": True,
                "message": "رمز عبور با موفقیت تغییر یافت",
            }
        else:
            raise ValidationError("بازیابی رمز عبور ناموفق بود")

    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise


@router.post("/change-password", response_model=Dict[str, Any])
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Change user password
    """
    try:
        auth_service = AuthService(db)
        success = auth_service.change_password(
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )

        if success:
            return {
                "success": True,
                "message": "رمز عبور با موفقیت تغییر یافت",
            }
        else:
            raise ValidationError("تغییر رمز عبور ناموفق بود")

    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user information
    """
    try:
        user_service = UserService(db)
        user_with_profile = user_service.get_user_with_profile(current_user.id)

        return {
            "success": True,
            "data": user_with_profile,
        }

    except Exception as e:
        logger.error(f"Get current user failed: {e}")
        raise


@router.get("/profile", response_model=Dict[str, Any])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user profile
    """
    try:
        user_service = UserService(db)
        user_with_profile = user_service.get_user_with_profile(current_user.id)
        stats = user_service.get_user_stats(current_user.id)

        return {
            "success": True,
            "data": {
                "user": user_with_profile,
                "stats": stats,
            },
        }

    except Exception as e:
        logger.error(f"Get user profile failed: {e}")
        raise