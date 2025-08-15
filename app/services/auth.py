"""
Authentication service
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
import logging

from app.models.user import User, UserProfile, ActivityLog, UserType, UserStatus
from app.schemas.user import UserCreate, UserLogin, UserWithProfile
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    generate_verification_token,
    verify_token,
)
from app.core.exceptions import (
    AuthenticationError,
    ValidationError,
    ConflictError,
    NotFoundError,
)
from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service class"""

    def __init__(self, db: Session):
        self.db = db

    def register_user(
        self,
        user_data: UserCreate,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Tuple[User, str]:
        """
        Register a new user
        Returns: (user, verification_token)
        """
        try:
            # Check if user already exists
            query = self.db.query(User).filter(
                or_(
                    User.email == user_data.email,
                    User.phone == user_data.phone if user_data.phone else False,
                )
            )
            existing_user = query.first()

            if existing_user:
                if existing_user.email == user_data.email:
                    raise ConflictError("کاربری با این ایمیل قبلاً ثبت‌نام کرده است")
                else:
                    raise ConflictError("کاربری با این شماره تلفن قبلاً ثبت‌نام کرده است")

            # Create new user
            user = User(
                email=user_data.email,
                phone=user_data.phone,
                password_hash=get_password_hash(user_data.password),
                user_type=user_data.user_type,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_verified=False,
                is_email_verified=False,
                is_phone_verified=False,
                email_verification_token=generate_verification_token(),
                email_verification_sent_at=datetime.utcnow(),
            )

            self.db.add(user)
            self.db.flush()  # To get the user ID

            # Create user profile
            profile = UserProfile(
                user_id=user.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
            )
            self.db.add(profile)

            # Log activity
            self._log_activity(
                user=user,
                action="user_registered",
                ip_address=ip_address,
                user_agent=user_agent,
                details=f"User registered with email: {user.email}",
            )

            self.db.commit()

            logger.info(f"New user registered: {user.email}")
            return user, user.email_verification_token

        except Exception as e:
            self.db.rollback()
            logger.error(f"User registration failed: {e}")
            raise

    def authenticate_user(
        self,
        credentials: UserLogin,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[User]:
        """
        Authenticate user with email and password
        """
        try:
            # Find user by email
            user = self.db.query(User).filter(User.email == credentials.email).first()

            if not user:
                self._log_failed_login(
                    email=credentials.email,
                    reason="user_not_found",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
                raise AuthenticationError("ایمیل یا رمز عبور اشتباه است")

            # Check if user can login
            if not user.can_login():
                reason = "account_locked" if user.failed_login_attempts >= 5 else "account_inactive"
                self._log_failed_login(
                    email=credentials.email,
                    reason=reason,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    user_id=user.id,
                )

                if user.failed_login_attempts >= 5:
                    raise AuthenticationError("حساب کاربری به دلیل تلاش‌های ناموفق زیاد قفل شده است")
                else:
                    raise AuthenticationError("حساب کاربری غیرفعال است")

            # Verify password
            if not verify_password(credentials.password, user.password_hash):
                user.record_failed_login()
                self.db.commit()

                self._log_failed_login(
                    email=credentials.email,
                    reason="wrong_password",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    user_id=user.id,
                )
                raise AuthenticationError("ایمیل یا رمز عبور اشتباه است")

            # Successful login
            user.record_login()
            self._log_activity(
                user=user,
                action="user_login",
                ip_address=ip_address,
                user_agent=user_agent,
                details="Successful login",
            )

            self.db.commit()
            logger.info(f"User authenticated: {user.email}")
            return user

        except Exception as e:
            self.db.rollback()
            logger.error(f"Authentication failed: {e}")
            raise

    def create_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user"""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "user_type": user.user_type.value,
            "is_verified": user.is_verified,
        }

        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Create new access token from refresh token"""
        payload = verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise AuthenticationError("توکن نامعتبر است")

        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("توکن نامعتبر است")

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.can_login():
            raise AuthenticationError("کاربر نامعتبر یا غیرفعال است")

        return self.create_tokens(user)

    def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        user = self.db.query(User).filter(
            User.email_verification_token == token
        ).first()

        if not user:
            raise NotFoundError("توکن تأیید نامعتبر است")

        # Check if token is expired (24 hours)
        if user.email_verification_sent_at:
            if datetime.utcnow() - user.email_verification_sent_at > timedelta(hours=24):
                raise ValidationError("توکن تأیید منقضی شده است")

        # Verify email
        user.is_email_verified = True
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_sent_at = None

        self._log_activity(
            user=user,
            action="email_verified",
            details="Email verification successful",
        )

        self.db.commit()
        logger.info(f"Email verified for user: {user.email}")
        return True

    def resend_verification_email(self, email: str) -> str:
        """Resend verification email"""
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            raise NotFoundError("کاربری با این ایمیل یافت نشد")

        if user.is_email_verified:
            raise ValidationError("ایمیل قبلاً تأیید شده است")

        # Generate new token
        user.email_verification_token = generate_verification_token()
        user.email_verification_sent_at = datetime.utcnow()

        self._log_activity(
            user=user,
            action="verification_email_resent",
            details="Verification email resent",
        )

        self.db.commit()
        return user.email_verification_token

    def request_password_reset(self, email: str) -> str:
        """Request password reset"""
        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            # Don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return "dummy_token"  # Return dummy token for security

        # Generate reset token
        user.password_reset_token = generate_verification_token()
        user.password_reset_sent_at = datetime.utcnow()

        self._log_activity(
            user=user,
            action="password_reset_requested",
            details="Password reset requested",
        )

        self.db.commit()
        return user.password_reset_token

    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token"""
        user = self.db.query(User).filter(
            User.password_reset_token == token
        ).first()

        if not user:
            raise NotFoundError("توکن بازیابی نامعتبر است")

        # Check if token is expired (1 hour)
        if user.password_reset_sent_at:
            if datetime.utcnow() - user.password_reset_sent_at > timedelta(hours=1):
                raise ValidationError("توکن بازیابی منقضی شده است")

        # Reset password
        user.password_hash = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_sent_at = None
        user.failed_login_attempts = 0  # Reset failed attempts

        self._log_activity(
            user=user,
            action="password_reset",
            details="Password reset successful",
        )

        self.db.commit()
        logger.info(f"Password reset for user: {user.email}")
        return True

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> bool:
        """Change user password"""
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise AuthenticationError("رمز عبور فعلی اشتباه است")

        # Update password
        user.password_hash = get_password_hash(new_password)

        self._log_activity(
            user=user,
            action="password_changed",
            details="Password changed successfully",
        )

        self.db.commit()
        logger.info(f"Password changed for user: {user.email}")
        return True

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def _log_activity(
        self,
        user: User,
        action: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ):
        """Log user activity"""
        activity = ActivityLog(
            user_id=user.id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            success=success,
            error_message=error_message,
        )
        self.db.add(activity)

    def _log_failed_login(
        self,
        email: str,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ):
        """Log failed login attempt"""
        activity = ActivityLog(
            user_id=user_id,
            action="failed_login",
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"Failed login for {email}. Reason: {reason}",
            success=False,
            error_message=reason,
        )
        self.db.add(activity)