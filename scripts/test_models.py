#!/usr/bin/env python3
"""
Test new models
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_model_imports():
    """Test importing all models"""
    print("🧪 Testing model imports...")
    
    try:
        # Import models one by one to identify issues
        from app.models.base import BaseModel, TimestampMixin
        print("✅ Base models imported")
        
        from app.models.user import User, UserProfile, ActivityLog
        print("✅ User models imported")
        
        from app.models.consultant import Consultant, ConsultationCategory
        print("✅ Consultant models imported")
        
        from app.models.consultation import ConsultationRequest, ConsultationSession
        print("✅ Consultation models imported")
        
        from app.models.wallet import Wallet, Transaction, PaymentMethod
        print("✅ Wallet models imported")
        
        from app.models.rating import Rating, Review, ReviewHelpful
        print("✅ Rating models imported")
        
        # Now import all together
        from app.models import (
            User, UserProfile, ActivityLog,
            Consultant, ConsultationCategory,
            ConsultationRequest, ConsultationSession,
            Wallet, Transaction, PaymentMethod,
            Rating, Review, ReviewHelpful
        )
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_creation():
    """Test creating tables"""
    print("\n🧪 Testing database table creation...")
    
    try:
        from app.database import create_tables, test_connection
        
        if not test_connection():
            print("❌ Database connection failed")
            return False
        
        create_tables()
        print("✅ All tables created successfully")
        
        # Verify tables exist
        from sqlalchemy import inspect
        from app.database import engine
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'users', 'user_profiles', 'activity_logs',
            'consultants', 'consultation_categories', 'consultant_categories',
            'consultation_requests', 'consultation_sessions',
            'wallets', 'transactions', 'payment_methods',
            'ratings', 'reviews', 'review_helpful'
        ]
        
        missing_tables = [table for table in expected_tables if table not in tables]
        extra_tables = [table for table in tables if table not in expected_tables]
        
        if missing_tables:
            print(f"⚠️ Missing tables: {missing_tables}")
        
        if extra_tables:
            print(f"ℹ️ Extra tables: {extra_tables}")
        
        print(f"📊 Total tables created: {len(tables)}")
        print(f"📋 Tables: {sorted(tables)}")
        
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_model_creation():
    """Test creating basic model instances"""
    print("\n🧪 Testing basic model creation...")
    
    try:
        from app.database import SessionLocal
        from app.models import User, UserType, UserProfile
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        
        try:
            # Create a test user
            test_user = User(
                email="test@example.com",
                password_hash=get_password_hash("testpassword"),
                user_type=UserType.CLIENT
            )
            
            db.add(test_user)
            db.flush()  # Get ID without committing
            
            # Create profile
            test_profile = UserProfile(
                user_id=test_user.id,
                first_name="Test",
                last_name="User"
            )
            
            db.add(test_profile)
            db.flush()
            
            print("✅ Basic model instances created successfully")
            
            # Test relationships
            if test_user.profile:
                print("✅ User-Profile relationship working")
            else:
                print("⚠️ User-Profile relationship not working")
            
            db.rollback()  # Don't save test data
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Model creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all model tests"""
    print("🧪 Model Test Suite")
    print("=" * 50)
    
    tests = [
        ("Model Imports", test_model_imports),
        ("Database Creation", test_database_creation),
        ("Basic Model Creation", test_basic_model_creation),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n📋 {name}")
        print("-" * 30)
        result = test_func()
        results.append(result)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary")
    print("=" * 30)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {passed}/{total} ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("\n🎉 All model tests passed!")
        return True
    else:
        print("\n⚠️ Some model tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)