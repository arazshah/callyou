"""
User management service
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from uuid import UUID
import logging

from app.models.user import User, UserProfile, ActivityLog, UserType, UserStatus
from app.schemas.user import (
    UserUpdate, UserProfileCreate, UserProfileUpdate,
    UserWithProfile, UserResponse, UserProfileResponse
)
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.core.security import validate_phone_number, validate_email_address

logger = logging.getLogger(__name__)


class UserService:
    """User management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_with_profile(self, user_id: UUID) -> Optional[UserWithProfile]:
        """Get user with profile by ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Load profile if not already loaded
        if not user.profile:
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            user.profile = profile
        
        return UserWithProfile.from_orm(user)
    
    def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate,
        current_user: User
    ) -> UserResponse:
        """Update user information"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("کاربر یافت نشد")
        
        # Check permissions (users can only update themselves, admins can update anyone)
        if current_user.id != user_id and not current_user.is_admin():
            raise ValidationError("شما مجاز به ویرایش این کاربر نیستید")
        
        try:
            # Update email if provided
            if user_data.email and user_data.email != user.email:
                # Check if email already exists
                existing = self.db.query(User).filter(
                    and_(User.email == user_data.email, User.id != user_id)
                ).first()
                if existing:
                    raise ConflictError("کاربری با این ایمیل قبلاً وجود دارد")
                
                # Validate email
                is_valid, result = validate_email_address(user_data.email)
                if not is_valid:
                    raise ValidationError(f"ایمیل نامعتبر: {result}")
                
                user.email = result
                user.is_email_verified = False  # Need to verify new email
            
            # Update phone if provided
            if user_data.phone and user_data.phone != user.phone:
                # Check if phone already exists
                existing = self.db.query(User).filter(
                    and_(User.phone == user_data.phone, User.id != user_id)
                ).first()
                if existing:
                    raise ConflictError("کاربری با این شماره تلفن قبلاً وجود دارد")
                
                user.phone = user_data.phone
                user.is_phone_verified = False  # Need to verify new phone
            
            # Update other fields (admin only)
            if current_user.is_admin():
                if user_data.is_active is not None:
                    user.is_active = user_data.is_active
            
            # Log activity
            self._log_activity(
                user=current_user,
                action="user_updated",
                resource_type="user",
                resource_id=user.id,
                details=f"Updated user: {user.email}"
            )
            
            self.db.commit()
            
            logger.info(f"User updated: {user.email}")
            return UserResponse.from_orm(user)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"User update failed: {e}")
            raise
    
    def create_or_update_profile(
        self,
        user_id: UUID,
        profile_data: UserProfileUpdate,
        current_user: User
    ) -> UserProfileResponse:
        """Create or update user profile"""
        # Check permissions
        if current_user.id != user_id and not current_user.is_admin():
            raise ValidationError("شما مجاز به ویرایش این پروفایل نیستید")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("کاربر یافت نشد")
        
        try:
            # Get or create profile
            profile = self.db.query(UserProfile).filter(
                UserProfile.user_id == user_id
            ).first()
            
            if not profile:
                # Create new profile
                profile = UserProfile(user_id=user_id)
                self.db.add(profile)
            
            # Update profile fields
            update_data = profile_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            
            # Log activity
            self._log_activity(
                user=current_user,
                action="profile_updated",
                resource_type="user_profile",
                resource_id=profile.id if hasattr(profile, 'id') else None,
                details=f"Updated profile for user: {user.email}"
            )
            
            self.db.commit()
            
            logger.info(f"Profile updated for user: {user.email}")
            return UserProfileResponse.from_orm(profile)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Profile update failed: {e}")
            raise
    
    def get_user_activity_logs(
        self,
        user_id: UUID,
        current_user: User,
        limit: int = 50,
        offset: int = 0
    ) -> List[ActivityLog]:
        """Get user activity logs"""
        # Check permissions
        if current_user.id != user_id and not current_user.is_admin():
            raise ValidationError("شما مجاز به مشاهده این اطلاعات نیستید")
        
        logs = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).order_by(
            ActivityLog.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return logs
    
    def deactivate_user(
        self,
        user_id: UUID,
        current_user: User,
        reason: Optional[str] = None
    ) -> bool:
        """Deactivate user account"""
        # Check permissions (users can deactivate themselves, admins can deactivate anyone)
        if current_user.id != user_id and not current_user.is_admin():
            raise ValidationError("شما مجاز به غیرفعال کردن این کاربر نیستید")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("کاربر یافت نشد")
        
        try:
            user.is_active = False
            user.status = UserStatus.INACTIVE
            
            # Log activity
            self._log_activity(
                user=current_user,
                action="user_deactivated",
                resource_type="user",
                resource_id=user.id,
                details=f"Deactivated user: {user.email}. Reason: {reason or 'Not specified'}"
            )
            
            self.db.commit()
            
            logger.info(f"User deactivated: {user.email}")
            return True
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"User deactivation failed: {e}")
            raise
    
    def search_users(
        self,
        query: str,
        user_type: Optional[UserType] = None,
        is_active: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[UserWithProfile]:
        """Search users"""
        db_query = self.db.query(User)
        
        # Apply filters
        if query:
            db_query = db_query.filter(
                or_(
                    User.email.ilike(f"%{query}%"),
                    UserProfile.first_name.ilike(f"%{query}%"),
                    UserProfile.last_name.ilike(f"%{query}%"),
                    UserProfile.display_name.ilike(f"%{query}%")
                )
            ).join(UserProfile, User.id == UserProfile.user_id, isouter=True)
        
        if user_type:
            db_query = db_query.filter(User.user_type == user_type)
        
        if is_active is not None:
            db_query = db_query.filter(User.is_active == is_active)
        
        users = db_query.offset(offset).limit(limit).all()
        
        # Convert to UserWithProfile
        result = []
        for user in users:
            user_data = UserWithProfile.from_orm(user)
            result.append(user_data)
        
        return result
    
    def get_user_stats(self, user_id: UUID) -> dict:
        """Get user statistics"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("کاربر یافت نشد")
        
        # Get activity count
        activity_count = self.db.query(ActivityLog).filter(
            ActivityLog.user_id == user_id
        ).count()
        
        # Get failed login count
        failed_logins = self.db.query(ActivityLog).filter(
            and_(
                ActivityLog.user_id == user_id,
                ActivityLog.action == "failed_login"
            )
        ).count()
        
        return {
            "user_id": user_id,
            "login_count": user.login_count,
            "failed_login_attempts": user.failed_login_attempts,
            "total_failed_logins": failed_logins,
            "activity_count": activity_count,
            "last_login": user.last_login,
            "account_age_days": (user.created_at - user.created_at).days if user.created_at else 0,
            "is_verified": user.is_verified,
            "is_email_verified": user.is_email_verified,
            "is_phone_verified": user.is_phone_verified
        }
    
    def _log_activity(
        self,
        user: User,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        details: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log user activity"""
        activity = ActivityLog(
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            success=success,
            error_message=error_message
        )
        self.db.add(activity)