#!/usr/bin/env python3
"""
Test models - Ultra simple version
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def main():
    """Run simple test"""
    print("🧪 Ultra Simple Model Test")
    print("=" * 30)
    
    # Test 1: Basic imports
    print("1. Testing basic imports...")
    try:
        from app.models.base import BaseModel
        print(" ✅ BaseModel imported")
        
        from app.models.user import User, UserProfile
        print(" ✅ User models imported")
        
        from app.models.consultant import Consultant
        print(" ✅ Consultant imported")
        
        from app.models.wallet import Wallet
        print(" ✅ Wallet imported")
        
        print("✅ All basic imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Database connection
    print("\n2. Testing database connection...")
    try:
        from app.database import test_connection
        if test_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    # Test 3: Table creation
    print("\n3. Testing table creation...")
    try:
        from app.database import create_tables
        create_tables()
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False
    
    print("\n🎉 All tests passed!")
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Models are working correctly!")
    else:
        print("❌ Some tests failed")
    sys.exit(1)