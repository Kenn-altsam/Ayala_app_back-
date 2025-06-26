#!/usr/bin/env python3
"""
Database Connection Test Script for Ayala Foundation Backend

Simple script to test the PostgreSQL database connection with the provided credentials.
Run this script to verify that your database connection is working properly.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    print("🔍 Ayala Foundation Backend - Database Connection Test")
    print("=" * 60)
    
    try:
        from core.init_db import test_connection, init_database
        
        # Test database connection
        if test_connection():
            print("\n✅ Database connection test PASSED!")
            
            # Ask user if they want to initialize tables
            response = input("\n❓ Would you like to create database tables? (y/N): ").strip().lower()
            
            if response in ['y', 'yes']:
                print("\n🚀 Initializing database tables...")
                try:
                    init_database()
                    print("✅ Database initialization completed!")
                except Exception as e:
                    print(f"❌ Database initialization failed: {e}")
                    sys.exit(1)
            else:
                print("⏭️  Skipping table creation.")
        else:
            print("\n❌ Database connection test FAILED!")
            print("\n🔧 Please check:")
            print("   1. PostgreSQL server is running")
            print("   2. Database 'nFac_server' exists")
            print("   3. User 'postgres' has access to the database")
            print("   4. Password is correct: JT0v3/9TR0c4")
            print("   5. Server is accessible at localhost:5432")
            sys.exit(1)
            
        print("\n🎉 All tests completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed the required dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 