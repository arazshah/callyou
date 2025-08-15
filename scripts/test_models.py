#!/usr/bin/env python3
"""
Test new models – Validate model imports, table creation, and relationships
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
        from app.models import (
            User,
            UserProfile,
            ActivityLog,
            Consultant,
            ConsultationCategory,
            ConsultationRequest,
            ConsultationSession,
            Wallet,
            Transaction,
            PaymentMethod,
            Rating,
            Review,
            ReviewHelpful,
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

        # Create tables
        create_tables()
        print("✅ Tables creation attempted")

        # Verify tables exist
        from sqlalchemy import inspect
        from app.database import engine

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = {
            'users',
            'user_profiles',
            'activity_logs',
            'consultants',
            'consultation_categories',
            'consultation_requests',
            'consultation_sessions',
            'wallets',
            'transactions',
            'payment_methods',
            'ratings',
            'reviews',
            'review_helpful'
        }

        missing_tables = expected_tables - set(tables)

        if missing_tables:
            print(f"❌ Missing tables: {sorted(missing_tables)}")
        else:
            print("✅ All expected tables found in database")

        print(f"📊 Total tables in database: {len(tables)}")
        print(f"📋 Tables: {sorted(tables)}")

        return len(missing_tables) == 0

    except Exception as e:
        print(f"❌ Database creation or inspection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_relationships():
    """Test model relationships"""
    print("\n🧪 Testing model relationships...")

    try:
        from app.models import User, Consultant, Wallet, ConsultationRequest, Rating, Review

        # Define expected relationships
        test_cases = [
            # User relationships
            (User, 'profile', "User.profile"),
            (User, 'consultant', "User.consultant"),
            (User, 'wallet', "User.wallet"),
            (User, 'activity_logs', "User.activity_logs"),
            (User, 'client_requests', "User.client_requests"),
            (User, 'client_sessions', "User.client_sessions"),
            (User, 'ratings_given', "User.ratings_given"),
            (User, 'reviews_written', "User.reviews_written"),
            (User, 'payment_methods', "User.payment_methods"),

            # Consultant relationships (example)
            (Consultant, 'user', "Consultant.user"),
            (Consultant, 'categories', "Consultant.categories"),

            # Wallet
            (Wallet, 'user', "Wallet.user"),
            (Wallet, 'transactions', "Wallet.transactions"),

            # ConsultationRequest
            (ConsultationRequest, 'client', "ConsultationRequest.client"),
            (ConsultationRequest, 'consultant', "ConsultationRequest.consultant"),

            # Rating
            (Rating, 'rater', "Rating.rater"),
            (Rating, 'consultant', "Rating.consultant"),
            (Rating, 'session', "Rating.session"),

            # Review
            (Review, 'rating', "Review.rating"),
            (Review, 'reviewer', "Review.reviewer"),
            (Review, 'consultant_response', "Review.consultant_response"),
        ]

        passed = 0
        for model, attr, name in test_cases:
            if hasattr(model, attr):
                print(f"✅ {name} relationship exists")
                passed += 1
            else:
                print(f"❌ {name} relationship missing")

        if passed == len(test_cases):
            print("✅ All expected relationships found")
        else:
            print(f"⚠️ Missing {len(test_cases) - passed} relationships")

        return passed == len(test_cases)

    except Exception as e:
        print(f"❌ Relationship test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all model tests"""
    print("🧪 Model Test Suite")
    print("=" * 60)

    tests = [
        ("Model Imports", test_model_imports),
        ("Database Creation", test_database_creation),
        ("Model Relationships", test_model_relationships),
    ]

    results = []

    for name, test_func in tests:
        print(f"\n📋 {name}")
        print("-" * 40)
        result = test_func()
        results.append(result)

    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100

    print(f"\n📊 Test Summary")
    print("=" * 40)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {passed}/{total} ({success_rate:.1f}%)")

    if passed == total:
        print("\n🎉 All model tests passed!")
        return True
    else:
        print("\n⚠️ Some model tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)