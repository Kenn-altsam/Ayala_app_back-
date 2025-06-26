#!/usr/bin/env python3
"""
Add sample company data to the Ayala Foundation database

This script adds a sample company record to test the database setup.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.database import SessionLocal
from src.companies.models import Company, Location
from datetime import datetime, date
import uuid

def add_sample_company():
    """Add a sample company record to the database"""
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Sample company data based on your CSV files
        sample_company = Company(
            id=uuid.uuid4(),
            name='АО "КАЗПОЧТА"',
            bin="000140002217",
            registration_date=date(2015, 1, 1),
            status="active",
            company_type="Акционерное общество",
            employee_count=1500,
            revenue_range="Large (>1000 employees)",
            industry="Почтовые услуги",
            website="https://kazpost.kz",
            phone="+7 (717) 2-123-456",
            email="info@kazpost.kz",
            description="Почтовые услуги в соответствии с обязательствами по предоставлению услуг в зоне всеобщего охвата",
            social_media={"website": "https://kazpost.kz"},
            has_social_media=False,
            has_website=True,
            has_contact_info=True,
            annual_tax_paid=50000000.0,  # 50 million tenge
            tax_reporting_year=2023,
            tax_compliance_score=95.5,
            last_tax_update=date(2024, 1, 15),
            past_donations="Educational initiatives, community development projects",
            sponsorship_interests="Education, community development, technology initiatives"
        )
        
        # Add company to session
        db.add(sample_company)
        db.flush()  # Get the company ID
        
        # Sample location data
        sample_location = Location(
            id=uuid.uuid4(),
            company_id=sample_company.id,
            region="Астана",
            city="Астана",
            address='район "САРЫАРКА"',
            postal_code="010000",
            latitude=51.1694,  # Nur-Sultan coordinates
            longitude=71.4491,
            is_primary=True
        )
        
        # Add location to session
        db.add(sample_location)
        
        # Commit the transaction
        db.commit()
        
        print("✅ Sample company added successfully!")
        print(f"   Company: {sample_company.name}")
        print(f"   BIN: {sample_company.bin}")
        print(f"   Industry: {sample_company.industry}")
        print(f"   Location: {sample_location.city}, {sample_location.region}")
        print(f"   Company ID: {sample_company.id}")
        
        return sample_company.id
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding sample company: {e}")
        raise
        
    finally:
        db.close()

def verify_data():
    """Verify the sample data was inserted correctly"""
    db = SessionLocal()
    
    try:
        # Query the company
        company = db.query(Company).filter(Company.bin == "000140002217").first()
        
        if company:
            print(f"\n🔍 Verification successful!")
            print(f"   Found company: {company.name}")
            print(f"   Locations: {len(company.locations)}")
            
            for location in company.locations:
                print(f"   - {location.city}, {location.region} ({location.latitude}, {location.longitude})")
        else:
            print("❌ Company not found in database")
            
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🏢 Adding sample company data...")
    add_sample_company()
    verify_data()
    print("🎉 Sample data insertion completed!") 