"""
User related models
"""

from sqlalchemy import (
    Column, String, Boolean, Date, DateTime,
    Enum as SQLEnum, ForeignKey, Text, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional

from .base import BaseModel


class UserType(str, enum.Enum):
    """User type enumeration"""
    CLIENT = "client"
    CONSULTANT = "consultant"
    ADMIN = "admin"


class Gender(str, enum.Enum):
    """Gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class UserStatus(str, enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"


class User(BaseModel):
    """User model for authentication and basic info"""

    __tablename__ = "users"

    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # User classification
    user_type = Column(SQLEnum(UserType), nullable=False, index=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    # Verification and security
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)

    # Two-factor authentication
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(255), nullable=True)

    # Login tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_failed_login = Column(DateTime(timezone=True), nullable=True)

    # Account management
    email_verification_token = Column(String(255), nullable=True)
    email_verification_sent_at = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_sent_at = Column(DateTime(timezone=True), nullable=True)

    def is_consultant(self) -> bool:
        """Check if user is a consultant"""
        return self.user_type == UserType.CONSULTANT

    def is_client(self) -> bool:
        """Check if user is a client"""
        return self.user_type == UserType.CLIENT

    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.user_type == UserType.ADMIN

    def can_login(self) -> bool:
        """Check if user can login"""
        return (
            self.is_active
            and self.status == UserStatus.ACTIVE
            and self.failed_login_attempts < 5
        )

    def record_login(self) -> None:
        """Record successful login"""
        self.last_login = func.now()
        self.login_count += 1
        self.failed_login_attempts = 0
        self.last_failed_login = None

    def record_failed_login(self) -> None:
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        self.last_failed_login = func.now()

    def __repr__(self):
        return f"<User(email={self.email}, type={self.user_type}, status={self.status})>"


class UserProfile(BaseModel):
    """Extended user profile information"""

    __tablename__ = "user_profiles"

    # Foreign key
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Personal information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    display_name = Column(String(150), nullable=True)
    bio = Column(Text, nullable=True)

    # Demographics
    birth_date = Column(Date, nullable=True)
    gender = Column(SQLEnum(Gender), nullable=True)

    # Location
    country = Column(String(100), default="Iran", nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    postal_code = Column(String(20), nullable=True)

    # Contact preferences
    timezone = Column(String(50), default="Asia/Tehran", nullable=True)
    language = Column(String(10), default="fa", nullable=True)

    # Media
    avatar_url = Column(String(500), nullable=True)
    cover_image_url = Column(String(500), nullable=True)

    # Social links
    website_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    telegram_username = Column(String(100), nullable=True)
    instagram_username = Column(String(100), nullable=True)

    # Privacy settings
    is_profile_public = Column(Boolean, default=True, nullable=False)
    show_email = Column(Boolean, default=False, nullable=False)
    show_phone = Column(Boolean, default=False, nullable=False)

    # Notification preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)

    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        elif self.display_name:
            return self.display_name
        else:
            return "کاربر ناشناس"

    @property
    def age(self) -> Optional[int]:
        """Calculate age from birth date"""
        if self.birth_date:
            from datetime import date
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    def get_display_name(self) -> str:
        """Get display name for UI"""
        return self.display_name or self.full_name

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, name={self.full_name})>"


class ActivityLog(BaseModel):
    """User activity logging for security and analytics"""

    __tablename__ = "activity_logs"

    # Foreign key
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Activity details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # Request details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    request_path = Column(String(255), nullable=True)
    request_method = Column(String(10), nullable=True)

    # Additional data
    details = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ActivityLog(user_id={self.user_id}, action={self.action})>"


# Define relationships
User.profile = relationship(
    "UserProfile",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan"
)

User.activity_logs = relationship(
    "ActivityLog",
    back_populates="user",
    cascade="all, delete-orphan"
)

UserProfile.user = relationship("User", back_populates="profile")
ActivityLog.user = relationship("User", back_populates="activity_logs")