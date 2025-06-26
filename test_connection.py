#!/usr/bin/env python3
"""Simple database connection test for Ayala Foundation Backend"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    print("🔍 Testing Database Connection...")
    
    try:
        from core.init_db import test_connection, init_database
        
        if test_connection():
            print("✅ Database connection successful!")
            
            response = input("Create tables? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                init_database()
                print("✅ Tables created!")
        else:
            print("❌ Connection failed!")
            
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 