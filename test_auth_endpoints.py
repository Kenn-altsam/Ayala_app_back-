#!/usr/bin/env python3
"""
Test authentication endpoints to identify validation issues
"""
import json
import requests
import sys

def test_auth_endpoints():
    """Test registration and login endpoints"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Authentication Endpoints...")
    print(f"📍 Base URL: {base_url}")
    
    # Test 1: Health check
    print("\n1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("💡 Make sure the backend is running with: cd Ayala_app_back/back && python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    # Test 2: Registration with various payloads
    print("\n2️⃣ Testing registration endpoint...")
    
    # Test with missing fields (should show validation error)
    test_cases = [
        {
            "name": "Empty payload",
            "data": {}
        },
        {
            "name": "Missing password",
            "data": {
                "email": "test@example.com",
                "full_name": "Test User"
            }
        },
        {
            "name": "Short password", 
            "data": {
                "email": "test@example.com",
                "password": "123",
                "full_name": "Test User"
            }
        },
        {
            "name": "Valid registration",
            "data": {
                "email": "testuser@ayala.foundation",
                "password": "securepassword123",
                "full_name": "Test User"
            }
        },
        {
            "name": "iOS app format",
            "data": {
                "email": "testuser2@ayala.foundation", 
                "password": "securepassword123",
                "fullName": "Test User 2"  # Note: camelCase instead of snake_case
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n   Testing: {test_case['name']}")
        try:
            response = requests.post(
                f"{base_url}/auth/register",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 422:
                # Validation error - this is what we're looking for
                error_details = response.json()
                print(f"   ❌ Validation Error: {json.dumps(error_details, indent=2)}")
            elif response.status_code == 201:
                print(f"   ✅ Success: {response.json()}")
            elif response.status_code == 400:
                print(f"   ⚠️  Bad Request: {response.json()}")
            else:
                print(f"   ❓ Unexpected response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
    
    # Test 3: Login endpoint
    print("\n3️⃣ Testing login endpoint...")
    login_data = {
        "email": "testuser@ayala.foundation",
        "password": "securepassword123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Login successful: {response.json()}")
        else:
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Login request failed: {e}")
    
    print("\n🔍 Analysis:")
    print("If you see validation errors above, they show exactly what the backend expects.")
    print("The iOS app should match these field names and validation rules.")
    
    return True

if __name__ == "__main__":
    success = test_auth_endpoints()
    exit(0 if success else 1) 