"""
User schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

from app.models.user import UserType, Gender, UserStatus


# Base schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    user_type: UserType


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        from app.core.security import validate_password_strength
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"رمز عبور نامعتبر: {', '.join(errors)}")
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            from app.core.security import validate_phone_number
            is_valid, result = validate_phone_number(v)
            if not is_valid:
                raise ValueError(result)
            return result
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for user updates"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            from app.core.security import validate_phone_number
            is_valid, result = validate_phone_number(v)
            if not is_valid:
                raise ValueError(result)
            return result
        return v


class UserResponse(BaseModel):
    """Schema for user response"""
    id: UUID
    email: str
    phone: Optional[str]
    user_type: UserType
    status: UserStatus
    is_active: bool
    is_verified: bool
    is_email_verified: bool
    is_phone_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Updated for Pydantic v2 compatibility


# Profile schemas
class UserProfileBase(BaseModel):
    """Base profile schema"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=150)
    bio: Optional[str] = Field(None, max_length=1000)


class UserProfileCreate(UserProfileBase):
    """Schema for profile creation"""
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class UserProfileUpdate(UserProfileBase):
    """Schema for profile updates"""
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    postal_code: Optional[str] = Field(None, max_length=20)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    website_url: Optional[str] = Field(None, max_length=255)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    telegram_username: Optional[str] = Field(None, max_length=100)
    instagram_username: Optional[str] = Field(None, max_length=100)
    is_profile_public: Optional[bool] = None
    show_email: Optional[bool] = None
    show_phone: Optional[bool] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None


class UserProfileResponse(BaseModel):
    """Schema for profile response"""
    id: UUID
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    bio: Optional[str]
    birth_date: Optional[date]
    gender: Optional[Gender]
    country: Optional[str]
    state: Optional[str]
    city: Optional[str]
    address: Optional[str]
    postal_code: Optional[str]
    timezone: str
    language: str
    avatar_url: Optional[str]
    cover_image_url: Optional[str]
    website_url: Optional[str]
    linkedin_url: Optional[str]
    telegram_username: Optional[str]
    instagram_username: Optional[str]
    is_profile_public: bool
    show_email: bool
    show_phone: bool
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    created_at: datetime
    updated_at: datetime

    # Computed fields
    full_name: str
    age: Optional[int]

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode


# Authentication schemas
class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[UUID] = None
    email: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @validator('new_password')
    def validate_new_password(cls, v):
        from app.core.security import validate_password_strength
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"رمز عبور جدید نامعتبر: {', '.join(errors)}")
        return v


class PasswordReset(BaseModel):
    """Password reset schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @validator('new_password')
    def validate_new_password(cls, v):
        from app.core.security import validate_password_strength
        is_valid, errors = validate_password_strength(v)
        if not is_valid:
            raise ValueError(f"رمز عبور جدید نامعتبر: {', '.join(errors)}")
        return v


class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str


# Combined user with profile
class UserWithProfile(UserResponse):
    """User with profile schema"""
    profile: Optional[UserProfileResponse] = None

    class Config:
        from_attributes = True


# Activity log schema
class ActivityLogResponse(BaseModel):
    """Activity log response schema"""
    id: UUID
    action: str
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_path: Optional[str]
    request_method: Optional[str]
    success: bool
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True