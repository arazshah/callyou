"""
FastAPI dependencies
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging
import time

from app.database import get_db
from app.models.user import User, UserType
from app.services.auth import AuthService
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user
    """
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        if not payload:
            raise AuthenticationError("توکن نامعتبر است")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("توکن نامعتبر است")

        # Get user from database
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(UUID(user_id))

        if not user:
            raise AuthenticationError("کاربر یافت نشد")

        if not user.can_login():
            raise AuthenticationError("حساب کاربری غیرفعال است")

        return user

    except ValueError:
        raise AuthenticationError("توکن نامعتبر است")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise AuthenticationError("خطا در احراز هویت")


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise AuthenticationError("حساب کاربری غیرفعال است")
    return current_user


def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current verified user
    """
    if not current_user.is_verified:
        raise AuthenticationError("حساب کاربری تأیید نشده است")
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current admin user
    """
    if not current_user.is_admin():
        raise AuthorizationError("دسترسی مدیریتی مورد نیاز است")
    return current_user


def get_current_consultant_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """
    Get current consultant user
    """
    if not current_user.is_consultant():
        raise AuthorizationError("دسترسی مشاور مورد نیاز است")
    return current_user


def get_current_client_user(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """
    Get current client user
    """
    if not current_user.is_client():
        raise AuthorizationError("دسترسی مشتری مورد نیاز است")
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None
    """
    if not credentials:
        return None

    try:
        return get_current_user(credentials, db)
    except Exception:
        return None


def get_client_ip(request: Request) -> str:
    """
    Get client IP address
    """
    # Check for forwarded IP first (for reverse proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection IP
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """
    Get user agent string
    """
    return request.headers.get("User-Agent", "unknown")


# Rate limiting dependency (basic in-memory implementation)
class RateLimiter:
    """
    Simple rate limiter (in-memory, not for production without Redis)
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def __call__(self, request: Request):
        client_ip = get_client_ip(request)
        current_time = time.time()

        # Clean old entries outside the time window
        cutoff_time = current_time - self.window_seconds
        self.requests = {
            ip: [t for t in timestamps if t > cutoff_time]
            for ip, timestamps in self.requests.items()
        }

        # Initialize request list for this IP
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="تعداد درخواست‌ها بیش از حد مجاز است",
            )

        # Log this request
        self.requests[client_ip].append(current_time)


# Create rate limiter instances
auth_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)  # 10/min for auth
api_rate_limiter = RateLimiter(max_requests=100, window_seconds=60)  # 100/min for API