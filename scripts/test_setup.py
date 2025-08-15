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
    print("🧪 Testing configuration...")
    try:
        from app.config import settings
        print("✅ Config loaded successfully")
        print(f"   📱 App Name: {settings.APP_NAME}")
        print(f"   🌍 Environment: {settings.ENVIRONMENT}")
        print(f"   🔧 Debug: {settings.DEBUG}")
        print(f"   🔑 Secret Key: {'*' * 10}...")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_database():
    """Test database connection"""
    print("🧪 Testing database connection...")
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


def test_api_endpoints():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    
    endpoints = [
        ("Root", "http://localhost:8000/"),
        ("Health", "http://localhost:8000/health"),
        ("Test", "http://localhost:8000/api/v1/test"),
    ]
    
    results = []
    
    for name, url in endpoints:
        try:
            print(f"   🔍 Testing {name} endpoint...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK ({response.status_code})")
                results.append(True)
            else:
                print(f"   ❌ {name}: Failed ({response.status_code})")
                results.append(False)
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ {name}: Connection refused (server not running?)")
            results.append(False)
        except Exception as e:
            print(f"   ❌ {name}: {e}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"✅ All API endpoints working ({success_count}/{total_count})")
        return True
    else:
        print(f"❌ Some API endpoints failed ({success_count}/{total_count})")
        return False


def test_docker_services():
    """Test Docker services"""
    print("🧪 Testing Docker services...")
    
    try:
        import subprocess
        
        # Check if containers are running
        result = subprocess.run(
            ["docker-compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            running_services = result.stdout.strip().split('\n')
            running_services = [s for s in running_services if s]  # Remove empty strings
            
            expected_services = ['postgres', 'app']
            
            print(f"   🔍 Running services: {running_services}")
            
            if all(service in running_services for service in expected_services):
                print("✅ All required Docker services are running")
                return True
            else:
                missing = [s for s in expected_services if s not in running_services]
                print(f"❌ Missing services: {missing}")
                return False
        else:
            print(f"❌ Docker command failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Docker or docker-compose not found")
        return False
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 Development Setup Test Suite")
    print("=" * 50)
    print()
    
    tests = [
        ("Configuration Loading", test_config),
        ("Docker Services", test_docker_services),
        ("Database Connection", test_database),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"📋 {name}")
        print("-" * 30)
        result = test_func()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary")
    print("=" * 30)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {passed}/{total} ({(passed/total*100):.1f}%)")
    print()
    
    if passed == total:
        print("🎉 All tests passed! Setup is working correctly.")
        print("🚀 Ready to proceed with development!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the setup.")
        print("💡 Make sure Docker services are running: docker-compose up -d")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)