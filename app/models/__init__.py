"""
Database models for the consultation platform
"""

# Import base classes first
from .base import BaseModel, TimestampMixin

# Import user models first
from .user import User, UserProfile, ActivityLog, UserType, Gender, UserStatus

# Import other models
from .consultant import Consultant, ConsultationCategory, ConsultantStatus, AvailabilityStatus, WorkingMode
from .consultation import (
 ConsultationRequest, ConsultationSession, 
 ConsultationStatus, ConsultationType, ConsultationMethod, PaymentStatus
)
from .wallet import (
 Wallet, Transaction, PaymentMethod,
 TransactionType, TransactionStatus, PaymentMethodType
)
from .rating import Rating, Review, ReviewHelpful, RatingType, ReviewStatus

# Export all models
__all__ = [
 # Base classes
 "BaseModel", 
 "TimestampMixin",
 
 # User models
 "User", 
 "UserProfile", 
 "ActivityLog",
 
 # Consultant models
 "Consultant",
 "ConsultationCategory",
 
 # Consultation models
 "ConsultationRequest",
 "ConsultationSession",
 
 # Wallet models
 "Wallet",
 "Transaction", 
 "PaymentMethod",
 
 # Rating models
 "Rating",
 "Review",
 "ReviewHelpful",
 
 # Enums
 "UserType", "Gender", "UserStatus",
 "ConsultantStatus", "AvailabilityStatus", "WorkingMode",
 "ConsultationStatus", "ConsultationType", "ConsultationMethod", "PaymentStatus",
 "TransactionType", "TransactionStatus", "PaymentMethodType",
 "RatingType", "ReviewStatus",
]