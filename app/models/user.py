from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class UserType(str, enum.Enum):
    CLIENT = "client"
    CONSULTANT = "consultant"
    ADMIN = "admin"


class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<User(email={self.email})>"