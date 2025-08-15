"""
Database models for the consultation platform

This module imports and exposes all SQLAlchemy models and enums
to allow centralized access throughout the application.
"""

# Import base classes first
from .base import BaseModel, TimestampMixin

# Import models
from .user import (
    User,
    UserProfile,
    ActivityLog,
    UserType,
    Gender,
    UserStatus,
)

from .consultant import (
    Consultant,
    ConsultationCategory,
    ConsultantStatus,
    AvailabilityStatus,
    WorkingMode,
)

from .consultation import (
    ConsultationRequest,
    ConsultationSession,
    ConsultationStatus,
    ConsultationType,
    ConsultationMethod,
    PaymentStatus,
)

from .wallet import (
    Wallet,
    Transaction,
    PaymentMethod,
    TransactionType,
    TransactionStatus,
    PaymentMethodType,
)

from .rating import (
    Rating,
    Review,
    ReviewHelpful,
    RatingType,
    ReviewStatus,
)

# Export all public symbols
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

    # Enums - User
    "UserType",
    "Gender",
    "UserStatus",

    # Enums - Consultant
    "ConsultantStatus",
    "AvailabilityStatus",
    "WorkingMode",

    # Enums - Consultation
    "ConsultationStatus",
    "ConsultationType",
    "ConsultationMethod",
    "PaymentStatus",

    # Enums - Wallet
    "TransactionType",
    "TransactionStatus",
    "PaymentMethodType",

    # Enums - Rating
    "RatingType",
    "ReviewStatus",
]