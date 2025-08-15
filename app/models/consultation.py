"""
Consultation session models
"""

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer,
    Enum as SQLEnum, ForeignKey, Text, Numeric, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from decimal import Decimal

from .base import BaseModel


class ConsultationStatus(str, enum.Enum):
    """Consultation status enumeration"""
    REQUESTED = "requested"      # درخواست شده
    ACCEPTED = "accepted"        # پذیرفته شده
    CONFIRMED = "confirmed"      # تایید شده
    IN_PROGRESS = "in_progress"  # در حال انجام
    COMPLETED = "completed"      # تکمیل شده
    CANCELLED = "cancelled"      # لغو شده
    NO_SHOW = "no_show"          # عدم حضور
    DISPUTED = "disputed"        # اختلاف


class ConsultationType(str, enum.Enum):
    """Consultation type enumeration"""
    SCHEDULED = "scheduled"      # برنامه‌ریزی شده
    IMMEDIATE = "immediate"      # فوری
    EMERGENCY = "emergency"      # اضطراری


class ConsultationMethod(str, enum.Enum):
    """Consultation method enumeration"""
    VIDEO = "video"              # ویدیو کال
    AUDIO = "audio"              # تماس صوتی
    CHAT = "chat"                # چت متنی
    IN_PERSON = "in_person"      # حضوری


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"          # در انتظار پرداخت
    PARTIAL = "partial"          # پرداخت جزئی
    PAID = "paid"                # پرداخت شده
    REFUNDED = "refunded"        # بازگشت داده شده
    DISPUTED = "disputed"        # اختلاف


class ConsultationRequest(BaseModel):
    """
    Consultation request from client to consultant
    """

    __tablename__ = "consultation_requests"

    # Participants
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    consultant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultation_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Request details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    consultation_type = Column(SQLEnum(ConsultationType), nullable=False)
    consultation_method = Column(SQLEnum(ConsultationMethod), nullable=False)

    # Scheduling
    requested_datetime = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=60, nullable=False)

    # Status
    status = Column(SQLEnum(ConsultationStatus), default=ConsultationStatus.REQUESTED, nullable=False)

    # Pricing
    quoted_price = Column(Numeric(10, 2), nullable=False)
    final_price = Column(Numeric(10, 2), nullable=True)

    # Response from consultant
    consultant_response = Column(Text, nullable=True)
    response_datetime = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    priority = Column(Integer, default=0, nullable=False)  # Higher number = higher priority
    attachments = Column(JSON, nullable=True)  # File attachments

    # Expiry
    expires_at = Column(DateTime(timezone=True), nullable=True)

    def is_expired(self) -> bool:
        """Check if request has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def can_be_accepted(self) -> bool:
        """Check if request can be accepted"""
        return (
            self.status == ConsultationStatus.REQUESTED
            and not self.is_expired()
        )

    def __repr__(self):
        return f"<ConsultationRequest(id={self.id}, status={self.status})>"


class ConsultationSession(BaseModel):
    """
    Actual consultation session
    """

    __tablename__ = "consultation_sessions"

    # Link to request
    request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultation_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Participants (denormalized for performance)
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    consultant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Session details
    title = Column(String(200), nullable=False)
    consultation_method = Column(SQLEnum(ConsultationMethod), nullable=False)

    # Scheduling
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(SQLEnum(ConsultationStatus), default=ConsultationStatus.CONFIRMED, nullable=False)

    # Technical details
    session_url = Column(String(500), nullable=True)  # Video call URL
    session_id = Column(String(100), nullable=True)  # External session ID
    recording_url = Column(String(500), nullable=True)

    # Pricing and payment
    agreed_price = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    # Session notes and summary
    consultant_notes = Column(Text, nullable=True)
    session_summary = Column(Text, nullable=True)
    client_feedback = Column(Text, nullable=True)

    # Attachments and files shared during session
    shared_files = Column(JSON, nullable=True)

    # Reminders sent
    reminder_sent = Column(Boolean, default=False, nullable=False)
    reminder_sent_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate actual session duration"""
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        return None

    @property
    def scheduled_duration_minutes(self) -> int:
        """Calculate scheduled session duration"""
        delta = self.scheduled_end - self.scheduled_start
        return int(delta.total_seconds() / 60)

    def is_upcoming(self) -> bool:
        """Check if session is upcoming"""
        return (
            self.status in [ConsultationStatus.CONFIRMED, ConsultationStatus.ACCEPTED]
            and self.scheduled_start > datetime.utcnow()
        )

    def is_ongoing(self) -> bool:
        """Check if session is currently ongoing"""
        return (
            self.status == ConsultationStatus.IN_PROGRESS
            and self.actual_start is not None
            and self.actual_end is None
        )

    def can_start(self) -> bool:
        """Check if session can be started"""
        now = datetime.utcnow()
        # Allow starting 10 minutes before scheduled time
        return (
            self.status == ConsultationStatus.CONFIRMED
            and self.scheduled_start - timedelta(minutes=10) <= now <= self.scheduled_end
        )

    def __repr__(self):
        return f"<ConsultationSession(id={self.id}, status={self.status})>"