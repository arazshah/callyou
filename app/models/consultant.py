"""
Consultant related models
"""

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer,
    Enum as SQLEnum, ForeignKey, Text, Numeric, JSON, Table
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime, time
from typing import Optional, List, Dict, Any
from decimal import Decimal

from .base import BaseModel


class ConsultantStatus(str, enum.Enum):
    """Consultant status enumeration"""
    PENDING = "pending"      # در انتظار تایید
    APPROVED = "approved"    # تایید شده
    REJECTED = "rejected"    # رد شده
    SUSPENDED = "suspended"  # تعلیق شده
    INACTIVE = "inactive"    # غیرفعال


class AvailabilityStatus(str, enum.Enum):
    """Availability status enumeration"""
    AVAILABLE = "available"     # در دسترس
    BUSY = "busy"               # مشغول
    OFFLINE = "offline"         # آفلاین
    IN_SESSION = "in_session"   # در جلسه


class WorkingMode(str, enum.Enum):
    """Working mode enumeration"""
    INDIVIDUAL = "individual"   # فردی
    GROUP = "group"             # گروهی
    COMPANY = "company"         # شرکتی


class Consultant(BaseModel):
    """
    Consultant profile and information
    """

    __tablename__ = "consultants"

    # Foreign key to user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Professional information
    license_number = Column(String(100), unique=True, nullable=True)
    specialization = Column(String(200), nullable=False)
    experience_years = Column(Integer, default=0, nullable=False)
    education = Column(Text, nullable=True)
    certifications = Column(JSON, nullable=True)  # List of certifications

    # Status and verification
    status = Column(SQLEnum(ConsultantStatus), default=ConsultantStatus.PENDING, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_date = Column(DateTime(timezone=True), nullable=True)

    # Availability
    availability_status = Column(SQLEnum(AvailabilityStatus), default=AvailabilityStatus.OFFLINE, nullable=False)
    is_accepting_requests = Column(Boolean, default=True, nullable=False)

    # Working preferences
    working_mode = Column(SQLEnum(WorkingMode), default=WorkingMode.INDIVIDUAL, nullable=False)
    max_concurrent_sessions = Column(Integer, default=1, nullable=False)

    # Pricing
    hourly_rate = Column(Numeric(10, 2), default=0, nullable=False)
    session_rate = Column(Numeric(10, 2), default=0, nullable=False)  # Per session
    emergency_rate = Column(Numeric(10, 2), default=0, nullable=True)  # Emergency consultation

    # Working hours (JSON format)
    working_hours = Column(JSON, nullable=True)  # {"monday": {"start": "09:00", "end": "17:00"}, ...}
    timezone = Column(String(50), default="Asia/Tehran", nullable=False)

    # Statistics
    total_sessions = Column(Integer, default=0, nullable=False)
    completed_sessions = Column(Integer, default=0, nullable=False)
    cancelled_sessions = Column(Integer, default=0, nullable=False)
    average_rating = Column(Numeric(3, 2), default=0, nullable=False)
    total_ratings = Column(Integer, default=0, nullable=False)

    # Financial
    total_earnings = Column(Numeric(12, 2), default=0, nullable=False)
    pending_earnings = Column(Numeric(12, 2), default=0, nullable=False)

    # Additional info
    languages = Column(JSON, nullable=True)  # ["fa", "en", ...]
    consultation_methods = Column(JSON, nullable=True)  # ["video", "audio", "chat"]
    bio = Column(Text, nullable=True)

    # Metadata
    last_activity = Column(DateTime(timezone=True), nullable=True)

    def update_rating(self, new_rating: float) -> None:
        """Update average rating"""
        total_score = self.average_rating * self.total_ratings + new_rating
        self.total_ratings += 1
        self.average_rating = Decimal(total_score) / self.total_ratings

    def is_available(self) -> bool:
        """Check if consultant is available for new sessions"""
        return (
            self.status == ConsultantStatus.APPROVED
            and self.is_accepting_requests
            and self.availability_status in [AvailabilityStatus.AVAILABLE, AvailabilityStatus.OFFLINE]
        )

    def can_take_session(self) -> bool:
        """Check if consultant can take a new session"""
        # This would check current active sessions vs max_concurrent_sessions
        return self.is_available()

    def __repr__(self):
        return f"<Consultant(user_id={self.user_id}, specialization={self.specialization})>"


class ConsultationCategory(BaseModel):
    """
    Consultation categories and subcategories
    """

    __tablename__ = "consultation_categories"

    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # Hierarchy
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultation_categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Display and ordering
    icon = Column(String(100), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color
    sort_order = Column(Integer, default=0, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    parent = relationship("ConsultationCategory", remote_side="ConsultationCategory.id", back_populates="children")
    children = relationship("ConsultationCategory", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ConsultationCategory(name={self.name})>"


# Many-to-many relationship between consultants and categories
consultant_categories = Table(
    "consultant_categories",
    BaseModel.metadata,
    Column("consultant_id", UUID(as_uuid=True), ForeignKey("consultants.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("consultation_categories.id", ondelete="CASCADE"), primary_key=True)
)