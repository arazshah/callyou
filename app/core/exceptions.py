"""
Custom exceptions for the application
"""

from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class CustomException(HTTPException):
    """Base custom exception"""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


class AuthenticationError(CustomException):
    """Authentication related errors"""
    
    def __init__(self, message: str = "احراز هویت ناموفق"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            details={"error_type": "authentication_error"}
        )


class AuthorizationError(CustomException):
    """Authorization related errors"""
    
    def __init__(self, message: str = "دسترسی غیرمجاز"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            details={"error_type": "authorization_error"}
        )


class ValidationError(CustomException):
    """Validation related errors"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"error_type": "validation_error"}
        if field:
            details["field"] = field
        
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            details=details
        )


class NotFoundError(CustomException):
    """Resource not found errors"""
    
    def __init__(self, message: str = "منبع مورد نظر یافت نشد"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            details={"error_type": "not_found_error"}
        )


class ConflictError(CustomException):
    """Resource conflict errors"""
    
    def __init__(self, message: str = "تداخل در منابع"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            details={"error_type": "conflict_error"}
        )


class RateLimitError(CustomException):
    """Rate limiting errors"""
    
    def __init__(self, message: str = "تعداد درخواست‌ها بیش از حد مجاز"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            details={"error_type": "rate_limit_error"}
        )


class ServiceUnavailableError(CustomException):
    """Service unavailable errors"""
    
    def __init__(self, message: str = "سرویس در حال حاضر در دسترس نیست"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            message=message,
            details={"error_type": "service_unavailable_error"}
        )