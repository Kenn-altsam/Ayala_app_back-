#!/usr/bin/env python3

import os
import sys
sys.path.append('.')

from src.core.config import settings

print("=== Configuration Test ===")
print(f"Project Name: {settings.PROJECT_NAME}")
print(f"Version: {settings.VERSION}")
print(f"API V1 String: {settings.API_V1_STR}")

print("\n=== Database Configuration ===")
print(f"Database URL: {settings.get_database_url()}")

print("\n=== Redis Configuration ===")
print(f"Redis URL: {settings.REDIS_URL}")

print("\n=== OpenAI Configuration ===")
print(f"OpenAI API Key: {'Set' if settings.OPENAI_API_KEY else 'Not Set'}")
print(f"OpenAI Model: {settings.OPENAI_MODEL}")

print("\n=== JWT Configuration ===")
print(f"JWT Secret Key: {'Set' if settings.JWT_SECRET_KEY else 'Not Set'}")

print("\n=== Google OAuth Configuration ===")
print(f"Google Client ID: {'Set' if settings.GOOGLE_CLIENT_ID else 'Not Set'}")

print("\n=== CORS Configuration ===")
print(f"Allowed Origins: {settings.ALLOWED_ORIGINS}")

print("\n=== Environment Variables ===")
env_vars = [
    'POSTGRES_PASSWORD', 
    'OPENAI_API_KEY', 
    'GOOGLE_CLIENT_ID', 
    'JWT_SECRET_KEY'
]

for var in env_vars:
    value = os.getenv(var)
    print(f"{var}: {'Set' if value else 'Not Set'}") 