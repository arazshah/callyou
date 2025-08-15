#!/usr/bin/env python3
"""
Final test for all models
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_imports():
    """Test importing all models"""
    print("🧪 Testing model imports...")
    
    try:
        from app.models import (
            User, UserProfile, ActivityLog,
            Consultant, ConsultationCategory,
            ConsultationRequest, ConsultationSession,
            Wallet, Transaction, PaymentMethod,
            Rating, Review, ReviewHelpful
        )
        print("✅ All models imported successfully")
        
        # Test enums
        from app.models import (
            UserType, ConsultantStatus, ConsultationStatus,
            TransactionType, RatingType
        )
        print("✅ All enums imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Test database creation"""
    print("\n🧪 Testing database creation...")
    
    try:
        from app.database import test_connection, create_tables
        
        if not test_connection():
            print("❌ Database connection failed")
            return False
        
        create_tables()
        print("✅ Tables created successfully")
        
        # Verify tables
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
        
        if missing_tables:
            print(f"⚠️ Missing tables: {missing_tables}")
        else:
            print("✅ All expected tables found")
        
        print(f"📊 Total tables: {len(tables)}")
        return len(missing_tables) == 0
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_operations():
    """Test basic model operations"""
    print("\n🧪 Testing basic model operations...")
    
    try:
        from app.database import SessionLocal
        from app.models import User, UserType, Wallet
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        
        try:
            # Create test user
            test_user = User(
                email="test@example.com",
                password_hash=get_password_hash("testpass"),
                user_type=UserType.CLIENT
            )
            
            db.add(test_user)
            db.flush()
            
            # Create wallet
            test_wallet = Wallet(user_id=test_user.id)
            db.add(test_wallet)
            db.flush()
            
            print("✅ Basic operations successful")
            
            db.rollback() # Don't save test data
            return True
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ Basic operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🧪 Final Model Test Suite")
    print("=" * 50)
    
    tests = [
        ("Model Imports", test_imports),
        ("Database Creation", test_database),
        ("Basic Operations", test_basic_operations),
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
        print("\n🎉 All tests passed! Task 4 completed successfully!")
        return True
    else:
        print("\n⚠️ Some tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)