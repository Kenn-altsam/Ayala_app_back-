"""
SQLAlchemy models for companies and locations

Defines the database schema for company and location data.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, Date, DateTime, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


class Company(Base):
    """Company model for storing company information"""
    
    __tablename__ = "companies"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic company information
    name = Column(String(255), nullable=False, index=True)
    bin = Column(String(12), unique=True, index=True)  # Business Identification Number
    registration_date = Column(Date)
    status = Column(String(50), default="active")
    company_type = Column(String(50))
    
    # Business details
    employee_count = Column(Integer, index=True)
    revenue_range = Column(String(50))
    industry = Column(String(100), index=True)
    
    # Contact information
    website = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    description = Column(Text)
    
    # Social media and digital presence
    social_media = Column(JSON, default=dict)
    has_social_media = Column(Boolean, default=False, index=True)
    has_website = Column(Boolean, default=False, index=True)
    has_contact_info = Column(Boolean, default=False, index=True)
    
    # Tax and financial information
    annual_tax_paid = Column(Float, index=True)
    tax_reporting_year = Column(Integer, index=True)
    tax_compliance_score = Column(Float)
    last_tax_update = Column(Date)
    
    # Sponsorship information
    past_donations = Column(Text)
    sponsorship_interests = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    locations = relationship("Location", back_populates="company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', bin='{self.bin}')>"


class Location(Base):
    """Location model for storing company addresses and geographic data"""
    
    __tablename__ = "locations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to company
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Location information
    region = Column(String(100), nullable=False, index=True)
    city = Column(String(100), index=True)
    address = Column(Text)
    postal_code = Column(String(10))
    
    # Geographic coordinates (latitude, longitude as separate columns)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Location metadata
    is_primary = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="locations")
    
    def __repr__(self):
        return f"<Location(id={self.id}, region='{self.region}', city='{self.city}')>" 