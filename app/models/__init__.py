"""
Database models for the consultation platform
"""

# Import all models to register them with SQLAlchemy
from .base import BaseModel, TimestampMixin
from .user import User, UserProfile, ActivityLog, UserType, Gender, UserStatus

# Export all models
__all__ = [
 # Base classes
 "BaseModel", 
 "TimestampMixin",
 
 # User models
 "User", 
 "UserProfile", 
 "ActivityLog",
 
 # Enums
 "UserType", 
 "Gender", 
 "UserStatus",
]