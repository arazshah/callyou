"""
Consultant related models
"""

from sqlalchemy import Column, String, Boolean, Integer, ARRAY, Text, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class Consultant(BaseModel):
    """Consultant model"""
    
    __tablename__ = "consultants"
    
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    specialization = Column(ARRAY(String), nullable=True)
    experience_years = Column(Integer, nullable=True)
    rating = Column(DECIMAL(3, 2), default=0.00)
    total_consultations = Column(Integer, default=0)
    is_online = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    status = Column(String(20), default="pending")
    
    # Relationships
    user = relationship("User", back_populates="consultant")
    
    def __repr__(self):
        return f"<Consultant(user_id={self.user_id}, title={self.title})>"