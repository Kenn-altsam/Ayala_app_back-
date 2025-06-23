#!/usr/bin/env python3
"""
Simple backend runner for Ayala App
This script runs the FastAPI backend server for development
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def get_local_ip():
    """Get the local IP address for network connections"""
    try:
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if 'en0:' in line or 'en1:' in line:  # WiFi or Ethernet
                    for j in range(i+1, min(i+10, len(lines))):
                        if 'inet ' in lines[j] and '127.0.0.1' not in lines[j]:
                            ip = lines[j].split('inet ')[1].split(' ')[0]
                            return ip
    except:
        pass
    return "192.168.1.84"  # fallback IP

def install_dependencies():
    """Install Python dependencies with compatibility fixes"""
    print("📦 Installing dependencies...")
    
    # Try installing with no binary for problematic packages
    packages = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "pydantic>=2.0.0,<3.0.0",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "email-validator",
        "python-dotenv",
        "alembic"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {package}: {e}")
            
    print("✅ Dependencies installation complete!")

def create_env_file():
    """Create .env file with default values"""
    env_content = """# Database Configuration
DATABASE_URL=sqlite:///./ayala_app.db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# App Configuration
APP_NAME=Ayala Foundation API
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=["*"]

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with default configuration")

def run_server():
    """Run the FastAPI server"""
    local_ip = get_local_ip()
    print(f"\n🚀 Starting Ayala Foundation Backend Server...")
    print(f"📱 iOS Device URL: http://{local_ip}:8000")
    print(f"🖥️  Simulator URL: http://127.0.0.1:8000")
    print(f"📖 API Docs: http://127.0.0.1:8000/docs")
    print(f"🔄 Server will reload on code changes")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    # Update the iOS API configuration file
    print(f"💡 Update your iOS APIConfiguration.swift device IP to: {local_ip}")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except FileNotFoundError:
        print("❌ Error: uvicorn not found. Installing dependencies first...")
        install_dependencies()
        run_server()
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running: pip install -r requirements.txt")

def main():
    """Main function"""
    print("🏗️  Ayala Foundation Backend Setup")
    print("=" * 40)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Create .env file if needed
    create_env_file()
    
    # Check if we need to install dependencies
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("📦 Installing missing dependencies...")
        install_dependencies()
    
    # Run the server
    run_server()

if __name__ == "__main__":
    main() 