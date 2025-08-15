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
    CONSULTANT = "consultant"
    SESSION = "session"
    PLATFORM = "platform"


class ReviewStatus(str, enum.Enum):
    """Review status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    HIDDEN = "hidden"


class Rating(BaseModel):
    """Rating system for consultants and sessions"""
    
    __tablename__ = "ratings"
    
    rater_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    rating_type = Column(SQLEnum(RatingType), nullable=False, index=True)
    
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
    
    overall_rating = Column(Integer, nullable=False)
    
    communication_rating = Column(Integer, nullable=True)
    expertise_rating = Column(Integer, nullable=True)
    punctuality_rating = Column(Integer, nullable=True)
    helpfulness_rating = Column(Integer, nullable=True)
    
    positive_aspects = Column(JSON, nullable=True)
    improvement_areas = Column(JSON, nullable=True)
    
    is_anonymous = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<Rating(id={self.id}, overall={self.overall_rating}, type={self.rating_type})>"


class Review(BaseModel):
    """Text reviews and comments"""
    
    __tablename__ = "reviews"
    
    rating_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("ratings.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    reviewer_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False, index=True)
    moderation_notes = Column(Text, nullable=True)
    moderated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    moderated_at = Column(DateTime(timezone=True), nullable=True)
    
    helpful_count = Column(Integer, default=0, nullable=False)
    reported_count = Column(Integer, default=0, nullable=False)
    
    consultant_response = Column(Text, nullable=True)
    response_date = Column(DateTime(timezone=True), nullable=True)
    
    language = Column(String(10), default="fa", nullable=False)
    sentiment_score = Column(Numeric(3, 2), nullable=True)
    
    def __repr__(self):
        return f"<Review(id={self.id}, status={self.status})>"


class ReviewHelpful(BaseModel):
    """Track which users found reviews helpful"""
    
    __tablename__ = "review_helpful"
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    review_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("reviews.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    is_helpful = Column(Boolean, nullable=False)
    
    def __repr__(self):
        return f"<ReviewHelpful(user_id={self.user_id}, review_id={self.review_id})>"