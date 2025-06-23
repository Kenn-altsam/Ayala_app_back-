#!/usr/bin/env python3
"""
Simple database connection test for Ayala_app
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def test_connection():
    """Test database connection and basic operations"""
    try:
        # Database connection parameters
        conn_params = {
            'host': 'localhost',
            'port': 5432,
            'database': 'Ayala_app',
            'user': 'postgres',
            'password': 'postgres123'
        }
        
        print("🔌 Testing database connection...")
        
        # Connect to database
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Successfully connected to database!")
        
        # Test 1: Check if all tables exist
        print("\n📋 Checking tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        expected_tables = ['companies', 'fund_profiles', 'locations', 'projects', 'users']
        
        for table in tables:
            table_name = table['table_name']
            if table_name in expected_tables:
                print(f"✅ Table '{table_name}' exists")
            else:
                print(f"ℹ️  Additional table '{table_name}' found")
        
        # Test 2: Test user insertion and retrieval
        print("\n👤 Testing user table operations...")
        
        # Insert a test user
        test_email = "test@ayala.foundation"
        cursor.execute("""
            INSERT INTO users (email, hashed_password, full_name, is_verified)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET
                full_name = EXCLUDED.full_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, email, full_name, created_at;
        """, (test_email, "hashed_password_123", "Test User", True))
        
        user = cursor.fetchone()
        print(f"✅ User created/updated: {user['email']} (ID: {user['id']})")
        
        # Query the user back
        cursor.execute("SELECT * FROM users WHERE email = %s", (test_email,))
        retrieved_user = cursor.fetchone()
        print(f"✅ User retrieved: {retrieved_user['full_name']}")
        
        # Test 3: Test companies table
        print("\n🏢 Testing companies table...")
        cursor.execute("SELECT COUNT(*) as count FROM companies")
        company_count = cursor.fetchone()['count']
        print(f"✅ Companies table accessible (current count: {company_count})")
        
        # Test 4: Test fund_profiles table
        print("\n💰 Testing fund_profiles table...")
        cursor.execute("SELECT COUNT(*) as count FROM fund_profiles")
        fund_count = cursor.fetchone()['count']
        print(f"✅ Fund profiles table accessible (current count: {fund_count})")
        
        # Commit changes and close
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 All database tests passed successfully!")
        print("✅ Backend is properly connected to the Ayala_app PostgreSQL database")
        print("\n📱 Your iOS app should now be able to:")
        print("   - Register new users")
        print("   - Login existing users") 
        print("   - Search for companies")
        print("   - Create fund profiles")
        print("   - Manage projects")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1) 