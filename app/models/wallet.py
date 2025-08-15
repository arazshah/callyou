"""
Wallet and transaction models
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
from decimal import Decimal

from .base import BaseModel


class TransactionType(str, enum.Enum):
    """Transaction type enumeration"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    COMMISSION = "commission"
    BONUS = "bonus"
    PENALTY = "penalty"


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class PaymentMethodType(str, enum.Enum):
    """Payment method type enumeration"""
    BANK_CARD = "bank_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"
    CREDIT = "credit"


class Wallet(BaseModel):
    """User digital wallet"""

    __tablename__ = "wallets"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    balance = Column(Numeric(12, 2), default=0, nullable=False)
    pending_balance = Column(Numeric(12, 2), default=0, nullable=False)
    frozen_balance = Column(Numeric(12, 2), default=0, nullable=False)

    daily_limit = Column(Numeric(10, 2), default=1000000, nullable=False)
    monthly_limit = Column(Numeric(12, 2), default=10000000, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    total_deposits = Column(Numeric(12, 2), default=0, nullable=False)
    total_withdrawals = Column(Numeric(12, 2), default=0, nullable=False)
    total_transactions = Column(Integer, default=0, nullable=False)

    pin_hash = Column(String(255), nullable=True)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)

    last_transaction_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def available_balance(self) -> Decimal:
        """Get available balance"""
        return self.balance - self.pending_balance - self.frozen_balance

    def can_withdraw(self, amount: Decimal) -> bool:
        """Check if user can withdraw specified amount"""
        return (
            self.is_active
            and self.available_balance >= amount
            and amount > 0
        )

    def __repr__(self):
        return f"<Wallet(user_id={self.user_id}, balance={self.balance})>"


class Transaction(BaseModel):
    """Financial transactions"""

    __tablename__ = "transactions"

    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    fee = Column(Numeric(10, 2), default=0, nullable=False)
    net_amount = Column(Numeric(12, 2), nullable=False)

    status = Column(
        SQLEnum(TransactionStatus),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True
    )

    description = Column(String(500), nullable=False)
    reference_id = Column(String(100), nullable=True, index=True)
    internal_reference = Column(String(100), nullable=True, index=True)

    related_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    related_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("consultation_sessions.id", ondelete="SET NULL"),
        nullable=True
    )

    payment_method_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True
    )

    balance_before = Column(Numeric(12, 2), nullable=False)
    balance_after = Column(Numeric(12, 2), nullable=False)

    # Changed from 'metadata' to 'transaction_data' to avoid reserved word
    transaction_data = Column(JSON, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(String(500), nullable=True)

    gateway_transaction_id = Column(String(200), nullable=True)
    gateway_response = Column(JSON, nullable=True)

    def is_successful(self) -> bool:
        """Check if transaction is successful"""
        return self.status == TransactionStatus.COMPLETED

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"


class PaymentMethod(BaseModel):
    """User payment methods"""

    __tablename__ = "payment_methods"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    method_type = Column(SQLEnum(PaymentMethodType), nullable=False)
    name = Column(String(100), nullable=False)

    card_number_masked = Column(String(20), nullable=True)
    account_number_masked = Column(String(20), nullable=True)
    bank_name = Column(String(100), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    verification_code = Column(String(10), nullable=True)
    verification_attempts = Column(Integer, default=0, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    total_transactions = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    encrypted_data = Column(Text, nullable=True)

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, type={self.method_type}, name={self.name})>"


# Define relationships
Wallet.user = relationship("User", backref="wallet")
Wallet.transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")

Transaction.wallet = relationship("Wallet", back_populates="transactions")
Transaction.related_user = relationship("User", foreign_keys=[Transaction.related_user_id])
Transaction.related_session = relationship("ConsultationSession", foreign_keys=[Transaction.related_session_id])
Transaction.payment_method = relationship("PaymentMethod")

PaymentMethod.user = relationship("User", backref="payment_methods")
PaymentMethod.transactions = relationship("Transaction", back_populates="payment_method")