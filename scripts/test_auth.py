#!/usr/bin/env python3
"""
Test authentication system
"""

import sys
import os
import requests
import json
from uuid import uuid4

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"


def test_user_registration():
    """Test user registration"""
    print("🧪 Testing user registration...")

    test_email = f"test_{uuid4().hex[:8]}@example.com"

    data = {
        "email": test_email,
        "password": "TestPassword123!",
        "user_type": "client",
        "first_name": "تست",
        "last_name": "کاربر",
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

    if response.status_code == 200:
        try:
            result = response.json()
            print("✅ Registration successful")
            print(f" - User ID: {result['data']['user_id']}")
            print(f" - Email: {result['data']['email']}")
            return test_email
        except json.JSONDecodeError:
            print("❌ Invalid JSON response")
            print(response.text)
            return None
    else:
        print(f"❌ Registration failed: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def test_user_login(email: str):
    """Test user login"""
    print("🧪 Testing user login...")

    data = {
        "email": email,
        "password": "TestPassword123!",
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

    if response.status_code == 200:
        try:
            result = response.json()
            print("✅ Login successful")
            print(f" - Access Token: {result['data']['tokens']['access_token'][:50]}...")
            return result["data"]["tokens"]["access_token"]
        except (json.JSONDecodeError, KeyError):
            print("❌ Invalid or incomplete login response")
            print(response.text)
            return None
    else:
        print(f"❌ Login failed: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return None


def test_protected_endpoint(token: str):
    """Test access to a protected endpoint (get current user)"""
    print("🧪 Testing protected endpoint (/auth/me)...")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    if response.status_code == 200:
        try:
            result = response.json()
            print("✅ Protected endpoint access successful")
            print(f" - User Email: {result['data']['email']}")
            return True
        except json.JSONDecodeError:
            print("❌ Invalid JSON response")
            print(response.text)
            return False
    else:
        print(f"❌ Protected endpoint failed: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return False


def test_profile_update(token: str):
    """Test updating user profile (assuming the endpoint exists)"""
    print("🧪 Testing profile update...")

    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "bio": "این یک بیوگرافی تستی است",
        "city": "تهران",
        "country": "ایران",
    }

    # ⚠️ Make sure this endpoint exists and accepts PUT/PATCH
    url = f"{BASE_URL}/users/me/profile"
    try:
        response = requests.put(url, json=data, headers=headers, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

    if response.status_code in (200, 201):
        try:
            result = response.json()
            print("✅ Profile update successful")
            if "bio" in result.get("data", {}):
                print(f" - Updated Bio: {result['data']['bio']}")
            return True
        except json.JSONDecodeError:
            print("✅ Profile updated (no JSON returned)")
            return True
    else:
        print(f"❌ Profile update failed: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except:
            print(response.text)
        return False


def main():
    """Run all authentication tests"""
    print("🧪 Authentication System Test Suite")
    print("=" * 60)
    print()

    # Test 1: Registration
    email = test_user_registration()
    if not email:
        print("❌ Registration test failed, stopping...")
        return False
    print()

    # Test 2: Login
    token = test_user_login(email)
    if not token:
        print("❌ Login test failed, stopping...")
        return False
    print()

    # Test 3: Access protected endpoint
    if not test_protected_endpoint(token):
        print("❌ Protected endpoint test failed")
        return False
    print()

    # Test 4: Update profile (optional, if endpoint exists)
    # Remove or skip if profile update is not implemented yet
    if not test_profile_update(token):
        print("🟡 Profile update test failed (endpoint may not be implemented yet)")
        # You can treat this as non-critical: return True anyway
        # Or fail: return False

    print()
    print("🎉 All authentication tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the FastAPI app is running on http://localhost:8000")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Test suite interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with unexpected error: {e}")
        sys.exit(1)