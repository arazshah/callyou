#!/usr/bin/env python3
"""
Test new models - Simple version
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_imports():
    """Test importing models"""
    print("🧪 Testing model imports...")
    
    try:
        from app.models import (
            User, UserProfile, Consultant, Wallet, 
            ConsultationRequest, Rating
        )
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database():
    """Test database creation"""
    print("\n🧪 Testing database...")
    
    try:
        from app.database import test_connection, create_tables
        
        if not test_connection():
            print("❌ Database connection failed")
            return False
        
        create_tables()
        print("✅ Tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run tests"""
    print("🧪 Simple Model Test")
    print("=" * 30)
    
    tests = [
        test_imports,
        test_database
    ]
    
    results = [test() for test in tests]
    passed = sum(results)
    
    print(f"\n📊 Results: {passed}/{len(results)} passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)