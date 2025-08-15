"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException

from app.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength
    Returns: (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 8:
        errors.append("رمز عبور باید حداقل 8 کاراکتر باشد")

    if len(password) > 128:
        errors.append("رمز عبور نباید بیش از 128 کاراکتر باشد")

    if not any(c.islower() for c in password):
        errors.append("رمز عبور باید شامل حداقل یک حرف کوچک باشد")

    if not any(c.isupper() for c in password):
        errors.append("رمز عبور باید شامل حداقل یک حرف بزرگ باشد")

    if not any(c.isdigit() for c in password):
        errors.append("رمز عبور باید شامل حداقل یک عدد باشد")

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("رمز عبور باید شامل حداقل یک کاراکتر خاص باشد")

    return len(errors) == 0, errors


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_verification_token() -> str:
    """Generate secure verification token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def validate_email_address(email: str) -> tuple[bool, str]:
    """
    Validate email address
    Returns: (is_valid, normalized_email_or_error)
    """
    try:
        valid = validate_email(email)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)


def validate_phone_number(phone: str, country_code: str = "IR") -> tuple[bool, str]:
    """
    Validate phone number
    Returns: (is_valid, formatted_phone_or_error)
    """
    try:
        parsed = phonenumbers.parse(phone, country_code)
        if phonenumbers.is_valid_number(parsed):
            formatted = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
            return True, formatted
        else:
            return False, "شماره تلفن نامعتبر است"
    except NumberParseException as e:
        return False, f"خطا در تجزیه شماره تلفن: {e}"


def generate_secure_filename(original_filename: str) -> str:
    """Generate secure filename"""
    import os
    from uuid import uuid4

    # Get file extension
    _, ext = os.path.splitext(original_filename)

    # Generate secure filename
    secure_name = str(uuid4())

    return f"{secure_name}{ext}"


def is_safe_url(url: str) -> bool:
    """Check if URL is safe for redirects"""
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False