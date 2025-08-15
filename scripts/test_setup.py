#!/usr/bin/env python3
"""
Test the development setup
"""
import sys
import os
import requests
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_config():
    """Test configuration loading"""
    try:
        from app.config import settings
        print("✅ Config loaded successfully")
        print(f"   - App Name: {settings.APP_NAME}")
        print(f"   - Environment: {settings.ENVIRONMENT}")
        print(f"   - Debug: {settings.DEBUG}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_database():
    """Test database connection"""
    try:
        from app.database import test_connection
        if test_connection():
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_api():
    """Test API endpoints"""
    try:
        # Wait for server to start
        time.sleep(2)
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API health check successful")
            print(f"   - Status: {response.json().get('status')}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing development setup...\n")
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database),
        ("API", test_api),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing {name}...")
        result = test_func()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the setup.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)