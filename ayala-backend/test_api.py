#!/usr/bin/env python3
"""
Test script for Ayala Backend API
Tests authentication, AI conversation, and other endpoints
"""

import asyncio
import aiohttp
import json
import sys

BASE_URL = "http://127.0.0.1:8001/api/v1"

async def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Health check passed: {data}")
                    return True
                else:
                    print(f"❌ Health check failed: {resp.status}")
                    return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

async def test_register_and_login():
    """Test user registration and login"""
    print("\n👤 Testing user registration and login...")
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    async with aiohttp.ClientSession() as session:
        # Register user
        try:
            async with session.post(f"{BASE_URL}/auth/register", json=test_user) as resp:
                if resp.status == 200:
                    print("✅ User registration successful")
                elif resp.status == 400:
                    print("⚠️  User already exists (this is ok for testing)")
                else:
                    print(f"❌ Registration failed: {resp.status}")
                    text = await resp.text()
                    print(f"   Response: {text}")
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return None

        # Login user
        try:
            login_data = {
                "username": test_user["email"],
                "password": test_user["password"]
            }
            
            async with session.post(
                f"{BASE_URL}/auth/token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token = data.get("access_token")
                    print(f"✅ Login successful, token: {token[:20]}...")
                    return token
                else:
                    print(f"❌ Login failed: {resp.status}")
                    text = await resp.text()
                    print(f"   Response: {text}")
                    return None
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None

async def test_fund_profile(token):
    """Test fund profile creation"""
    print("\n🏛️ Testing fund profile...")
    
    profile_data = {
        "fund_name": "Test Foundation",
        "fund_description": "A test foundation for educational purposes and community development",
        "fund_email": "test@testfoundation.org"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with aiohttp.ClientSession() as session:
        # Create fund profile
        try:
            async with session.post(f"{BASE_URL}/funds/profile", json=profile_data, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Fund profile created successfully")
                    return True
                elif resp.status == 400:
                    print("⚠️  Fund profile already exists (this is ok for testing)")
                    return True
                else:
                    print(f"❌ Fund profile creation failed: {resp.status}")
                    text = await resp.text()
                    print(f"   Response: {text}")
                    return False
        except Exception as e:
            print(f"❌ Fund profile error: {e}")
            return False

async def test_ai_conversation(token):
    """Test AI conversation endpoint"""
    print("\n🤖 Testing AI conversation...")
    
    conversation_data = {
        "user_input": "Hi, I'm looking for sponsors for my education project in Almaty. We need about $5000 to help underprivileged children."
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BASE_URL}/funds/conversation", 
                json=conversation_data, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ AI conversation test successful!")
                    print(f"   AI Response: {data.get('message', 'No message')}")
                    print(f"   Required Fields: {data.get('required_fields', {})}")
                    print(f"   Is Complete: {data.get('is_complete', False)}")
                    return True
                else:
                    print(f"❌ AI conversation failed: {resp.status}")
                    text = await resp.text()
                    print(f"   Response: {text}")
                    return False
        except asyncio.TimeoutError:
            print("❌ AI conversation timed out (OpenAI API might be slow)")
            return False
        except Exception as e:
            print(f"❌ AI conversation error: {e}")
            return False

async def main():
    """Main test function"""
    print("🧪 Starting Ayala Backend API Tests")
    print("=" * 50)
    
    # Test health
    health_ok = await test_health()
    if not health_ok:
        print("❌ Health check failed, stopping tests")
        return
    
    # Test authentication
    token = await test_register_and_login()
    if not token:
        print("❌ Authentication failed, stopping tests")
        return
    
    # Test fund profile
    profile_ok = await test_fund_profile(token)
    if not profile_ok:
        print("❌ Fund profile test failed, but continuing...")
    
    # Test AI conversation (this is the main test for your use case)
    conversation_ok = await test_ai_conversation(token)
    
    print("\n" + "=" * 50)
    if health_ok and token and conversation_ok:
        print("🎉 All tests passed! Backend is ready for iOS testing.")
        print(f"📱 Your iOS app should connect to: {BASE_URL}")
        print("🔑 Make sure to use the registration and login flow in your iOS app.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main()) 