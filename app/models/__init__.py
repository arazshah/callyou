"""
Database models for the consultation platform
"""

# Import base classes first
from .base import BaseModel, TimestampMixin

# Import user models first (they are referenced by others)
from .user import User, UserProfile, ActivityLog, UserType, Gender, UserStatus

# Import consultant models
from .consultant import Consultant, ConsultationCategory, ConsultantStatus, AvailabilityStatus, WorkingMode

# Import consultation models
from .consultation import (
 ConsultationRequest, ConsultationSession, 
 ConsultationStatus, ConsultationType, ConsultationMethod, PaymentStatus
)

# Import wallet models
from .wallet import (
 Wallet, Transaction, PaymentMethod,
 TransactionType, TransactionStatus, PaymentMethodType
)

# Import rating models
from .rating import Rating, Review, ReviewHelpful, RatingType, ReviewStatus

# Now define cross-model relationships
def setup_relationships():
 """Setup relationships between models"""
 
 # User relationships
 User.consultant = relationship(
 "Consultant", 
 back_populates="user", 
 uselist=False, 
 cascade="all, delete-orphan"
 )
 
 User.wallet = relationship(
 "Wallet", 
 back_populates="user", 
 uselist=False, 
 cascade="all, delete-orphan"
 )
 
 User.client_requests = relationship(
 "ConsultationRequest",
 foreign_keys="ConsultationRequest.client_id",
 back_populates="client",
 cascade="all, delete-orphan"
 )
 
 User.client_sessions = relationship(
 "ConsultationSession",
 foreign_keys="ConsultationSession.client_id", 
 back_populates="client",
 cascade="all, delete-orphan"
 )
 
 User.ratings_given = relationship(
 "Rating",
 foreign_keys="Rating.rater_id",
 back_populates="rater",
 cascade="all, delete-orphan"
 )
 
 User.reviews_written = relationship(
 "Review",
 foreign_keys="Review.reviewer_id",
 back_populates="reviewer", 
 cascade="all, delete-orphan"
 )
 
 User.payment_methods = relationship(
 "PaymentMethod",
 back_populates="user",
 cascade="all, delete-orphan"
 )
 
 # Consultant relationships
 Consultant.user = relationship("User", back_populates="consultant")
 
 Consultant.requests = relationship(
 "ConsultationRequest",
 back_populates="consultant",
 cascade="all, delete-orphan"
 )
 
 Consultant.sessions = relationship(
 "ConsultationSession",
 back_populates="consultant",
 cascade="all, delete-orphan"
 )
 
 Consultant.ratings = relationship(
 "Rating",
 back_populates="consultant",
 cascade="all, delete-orphan"
 )
 
 # Wallet relationships
 Wallet.user = relationship("User", back_populates="wallet")
 Wallet.transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")
 
 # Transaction relationships
 Transaction.wallet = relationship("Wallet", back_populates="transactions")
 Transaction.related_user = relationship("User", foreign_keys="Transaction.related_user_id")
 Transaction.related_session = relationship("ConsultationSession", foreign_keys="Transaction.related_session_id")
 Transaction.payment_method = relationship("PaymentMethod")
 
 # PaymentMethod relationships
 PaymentMethod.user = relationship("User", back_populates="payment_methods")
 PaymentMethod.transactions = relationship("Transaction", back_populates="payment_method")
 
 # ConsultationRequest relationships
 ConsultationRequest.client = relationship("User", foreign_keys="ConsultationRequest.client_id", back_populates="client_requests")
 ConsultationRequest.consultant = relationship("Consultant", back_populates="requests")
 ConsultationRequest.category = relationship("ConsultationCategory")
 ConsultationRequest.session = relationship("ConsultationSession", back_populates="request", uselist=False)
 
 # ConsultationSession relationships
 ConsultationSession.request = relationship("ConsultationRequest", back_populates="session")
 ConsultationSession.client = relationship("User", foreign_keys="ConsultationSession.client_id", back_populates="client_sessions")
 ConsultationSession.consultant = relationship("Consultant", back_populates="sessions")
 ConsultationSession.transactions = relationship("Transaction", foreign_keys="Transaction.related_session_id")
 ConsultationSession.ratings = relationship("Rating", back_populates="session")
 
 # Rating relationships
 Rating.rater = relationship("User", foreign_keys="Rating.rater_id", back_populates="ratings_given")
 Rating.consultant = relationship("Consultant", back_populates="ratings")
 Rating.session = relationship("ConsultationSession", back_populates="ratings")
 Rating.review = relationship("Review", back_populates="rating", uselist=False)
 
 # Review relationships
 Review.rating = relationship("Rating", back_populates="review")
 Review.reviewer = relationship("User", foreign_keys="Review.reviewer_id", back_populates="reviews_written")
 Review.moderator = relationship("User", foreign_keys="Review.moderated_by")
 Review.helpful_votes = relationship("ReviewHelpful", back_populates="review", cascade="all, delete-orphan")
 
 # ReviewHelpful relationships
 ReviewHelpful.user = relationship("User")
 ReviewHelpful.review = relationship("Review", back_populates="helpful_votes")

# Setup relationships
setup_relationships()

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