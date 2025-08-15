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
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    DISPUTED = "disputed"


class ConsultationType(str, enum.Enum):
    """Consultation type enumeration"""
    SCHEDULED = "scheduled"
    IMMEDIATE = "immediate"
    EMERGENCY = "emergency"


class ConsultationMethod(str, enum.Enum):
    """Consultation method enumeration"""
    VIDEO = "video"
    AUDIO = "audio"
    CHAT = "chat"
    IN_PERSON = "in_person"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"
    DISPUTED = "disputed"


class ConsultationRequest(BaseModel):
    """Consultation request from client to consultant"""

    __tablename__ = "consultation_requests"

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

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    consultation_type = Column(SQLEnum(ConsultationType), nullable=False)
    consultation_method = Column(SQLEnum(ConsultationMethod), nullable=False)

    requested_datetime = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=60, nullable=False)

    status = Column(SQLEnum(ConsultationStatus), default=ConsultationStatus.REQUESTED, nullable=False)

    quoted_price = Column(Numeric(10, 2), nullable=False)
    final_price = Column(Numeric(10, 2), nullable=True)

    consultant_response = Column(Text, nullable=True)
    response_datetime = Column(DateTime(timezone=True), nullable=True)

    priority = Column(Integer, default=0, nullable=False)
    attachments = Column(JSON, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    def is_expired(self) -> bool:
        """Check if request has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def __repr__(self):
        return f"<ConsultationRequest(id={self.id}, status={self.status})>"


class ConsultationSession(BaseModel):
    """Actual consultation session"""

    __tablename__ = "consultation_sessions"

    request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultation_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

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

    title = Column(String(200), nullable=False)
    consultation_method = Column(SQLEnum(ConsultationMethod), nullable=False)

    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)

    status = Column(SQLEnum(ConsultationStatus), default=ConsultationStatus.CONFIRMED, nullable=False)

    session_url = Column(String(500), nullable=True)
    session_id = Column(String(100), nullable=True)
    recording_url = Column(String(500), nullable=True)

    agreed_price = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    consultant_notes = Column(Text, nullable=True)
    session_summary = Column(Text, nullable=True)
    client_feedback = Column(Text, nullable=True)

    shared_files = Column(JSON, nullable=True)

    reminder_sent = Column(Boolean, default=False, nullable=False)
    reminder_sent_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate actual session duration"""
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        return None

    def __repr__(self):
        return f"<ConsultationSession(id={self.id}, status={self.status})>"