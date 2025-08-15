"""
Rating and review models
"""

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer,
    Enum as SQLEnum, ForeignKey, Text, Numeric, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional, Dict, Any

from .base import BaseModel


class RatingType(str, enum.Enum):
    """Rating type enumeration"""
    CONSULTANT = "consultant"   # امتیاز به مشاور
    SESSION = "session"         # امتیاز به جلسه
    PLATFORM = "platform"       # امتیاز به پلتفرم


class ReviewStatus(str, enum.Enum):
    """Review status enumeration"""
    PENDING = "pending"         # در انتظار بررسی
    APPROVED = "approved"       # تایید شده
    REJECTED = "rejected"       # رد شده
    HIDDEN = "hidden"           # مخفی شده


class Rating(BaseModel):
    """
    Rating system for consultants and sessions
    """

    __tablename__ = "ratings"

    # Rater (who gives the rating)
    rater_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Target (what/who is being rated)
    rating_type = Column(SQLEnum(RatingType), nullable=False, index=True)

    # Target references
    consultant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultants.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultation_sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Rating details
    overall_rating = Column(Integer, nullable=False)  # 1-5 stars

    # Detailed ratings
    communication_rating = Column(Integer, nullable=True)  # 1-5
    expertise_rating = Column(Integer, nullable=True)      # 1-5
    punctuality_rating = Column(Integer, nullable=True)    # 1-5
    helpfulness_rating = Column(Integer, nullable=True)    # 1-5

    # Additional feedback
    positive_aspects = Column(JSON, nullable=True)         # List of positive aspects
    improvement_areas = Column(JSON, nullable=True)        # Areas for improvement

    # Metadata
    is_anonymous = Column(Boolean, default=False, nullable=False)

    def is_valid_rating(self, rating: int) -> bool:
        """Validate rating value"""
        return 1 <= rating <= 5

    def __repr__(self):
        return f"<Rating(id={self.id}, overall={self.overall_rating}, type={self.rating_type})>"


class Review(BaseModel):
    """
    Text reviews and comments
    """

    __tablename__ = "reviews"

    # Link to rating
    rating_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ratings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Reviewer
    reviewer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Review content
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)

    # Status and moderation
    status = Column(
        SQLEnum(ReviewStatus),
        default=ReviewStatus.PENDING,
        nullable=False,
        index=True
    )
    moderation_notes = Column(Text, nullable=True)
    moderated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    moderated_at = Column(DateTime(timezone=True), nullable=True)

    # Interaction
    helpful_count = Column(Integer, default=0, nullable=False)
    reported_count = Column(Integer, default=0, nullable=False)

    # Response from consultant
    consultant_response = Column(Text, nullable=True)
    response_date = Column(DateTime(timezone=True), nullable=True)

    # Language and content analysis
    language = Column(String(10), default="fa", nullable=False)
    sentiment_score = Column(Numeric(3, 2), nullable=True)  # -1 to 1

    def is_approved(self) -> bool:
        """Check if review is approved"""
        return self.status == ReviewStatus.APPROVED

    def can_be_displayed(self) -> bool:
        """Check if review can be displayed publicly"""
        return self.status == ReviewStatus.APPROVED

    def __repr__(self):
        return f"<Review(id={self.id}, status={self.status})>"


class ReviewHelpful(BaseModel):
    """
    Track which users found reviews helpful
    """

    __tablename__ = "review_helpful"

    # User who marked as helpful
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Review that was marked
    review_id = Column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Whether it was helpful or not
    is_helpful = Column(Boolean, nullable=False)

    def __repr__(self):
        return (
            f"<ReviewHelpful(user_id={self.user_id}, "
            f"review_id={self.review_id}, "
            f"helpful={self.is_helpful})>"
        )