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
    DEPOSIT = "deposit"            # واریز
    WITHDRAWAL = "withdrawal"      # برداشت
    PAYMENT = "payment"            # پرداخت
    REFUND = "refund"              # بازگشت
    COMMISSION = "commission"      # کمیسیون
    BONUS = "bonus"                # جایزه
    PENALTY = "penalty"            # جریمه


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration"""
    PENDING = "pending"            # در انتظار
    PROCESSING = "processing"      # در حال پردازش
    COMPLETED = "completed"        # تکمیل شده
    FAILED = "failed"              # ناموفق
    CANCELLED = "cancelled"        # لغو شده
    DISPUTED = "disputed"          # اختلاف


class PaymentMethodType(str, enum.Enum):
    """Payment method type enumeration"""
    BANK_CARD = "bank_card"              # کارت بانکی
    BANK_TRANSFER = "bank_transfer"      # انتقال بانکی
    DIGITAL_WALLET = "digital_wallet"    # کیف پول دیجیتال
    CRYPTOCURRENCY = "cryptocurrency"    # ارز دیجیتال
    CREDIT = "credit"                    # اعتبار


class Wallet(BaseModel):
    """
    User digital wallet
    """

    __tablename__ = "wallets"

    # Owner
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Balance
    balance = Column(Numeric(12, 2), default=0, nullable=False)
    pending_balance = Column(Numeric(12, 2), default=0, nullable=False)  # Pending transactions
    frozen_balance = Column(Numeric(12, 2), default=0, nullable=False)  # Frozen for disputes

    # Limits
    daily_limit = Column(Numeric(10, 2), default=1000000, nullable=False)   # Daily transaction limit
    monthly_limit = Column(Numeric(12, 2), default=10000000, nullable=False)  # Monthly limit

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Statistics
    total_deposits = Column(Numeric(12, 2), default=0, nullable=False)
    total_withdrawals = Column(Numeric(12, 2), default=0, nullable=False)
    total_transactions = Column(Integer, default=0, nullable=False)

    # Security
    pin_hash = Column(String(255), nullable=True)  # Wallet PIN
    two_factor_enabled = Column(Boolean, default=False, nullable=False)

    # Metadata
    last_transaction_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def available_balance(self) -> Decimal:
        """Get available balance (total - pending - frozen)"""
        return self.balance - self.pending_balance - self.frozen_balance

    def can_withdraw(self, amount: Decimal) -> bool:
        """Check if user can withdraw specified amount"""
        return (
            self.is_active
            and self.available_balance >= amount
            and amount > 0
        )

    def can_pay(self, amount: Decimal) -> bool:
        """Check if user can make payment"""
        return self.can_withdraw(amount)

    def __repr__(self):
        return f"<Wallet(user_id={self.user_id}, balance={self.balance})>"


class Transaction(BaseModel):
    """
    Financial transactions
    """

    __tablename__ = "transactions"

    # Wallet reference
    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Transaction details
    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    fee = Column(Numeric(10, 2), default=0, nullable=False)
    net_amount = Column(Numeric(12, 2), nullable=False)  # Amount after fee

    # Status
    status = Column(
        SQLEnum(TransactionStatus),
        default=TransactionStatus.PENDING,
        nullable=False,
        index=True
    )

    # Description and reference
    description = Column(String(500), nullable=False)
    reference_id = Column(String(100), nullable=True, index=True)  # External reference
    internal_reference = Column(String(100), nullable=True, index=True)  # Internal reference

    # Related entities
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

    # Payment method
    payment_method_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True
    )

    # Balance tracking
    balance_before = Column(Numeric(12, 2), nullable=False)
    balance_after = Column(Numeric(12, 2), nullable=False)

    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional transaction data
    processed_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(String(500), nullable=True)

    # Gateway information
    gateway_transaction_id = Column(String(200), nullable=True)
    gateway_response = Column(JSON, nullable=True)

    def is_successful(self) -> bool:
        """Check if transaction is successful"""
        return self.status == TransactionStatus.COMPLETED

    def is_pending(self) -> bool:
        """Check if transaction is pending"""
        return self.status in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]

    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"


class PaymentMethod(BaseModel):
    """
    User payment methods
    """

    __tablename__ = "payment_methods"

    # Owner
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Method details
    method_type = Column(SQLEnum(PaymentMethodType), nullable=False)
    name = Column(String(100), nullable=False)  # User-defined name

    # Card/Account information (encrypted)
    card_number_masked = Column(String(20), nullable=True)  # Last 4 digits
    account_number_masked = Column(String(20), nullable=True)
    bank_name = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    # Verification
    verification_code = Column(String(10), nullable=True)
    verification_attempts = Column(Integer, default=0, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Usage statistics
    total_transactions = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Security
    encrypted_data = Column(Text, nullable=True)  # Encrypted sensitive data

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, type={self.method_type}, name={self.name})>"