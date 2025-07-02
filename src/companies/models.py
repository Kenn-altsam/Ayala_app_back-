"""
SQLAlchemy models for companies

Defines the database schema for company data.
"""

from sqlalchemy import Column, String, Integer, Float, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


class Company(Base):
    """Company model for storing company information"""
    
    __tablename__ = "companies"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Company information based on provided columns
    BIN = Column(String(12), index=True)  # Business Identification Number
    Company = Column(String(255), nullable=False, index=True)  # Company name
    OKED = Column(String(50), index=True)  # OKED classification code
    Activity = Column(String(255), index=True)  # Activity description
    KATO = Column(String(50), index=True)  # KATO territorial code
    Locality = Column(String(100), index=True)  # Locality/Region
    KRP = Column(String(50))  # KRP code
    Size = Column(String(50), index=True)  # Company size
    
    # --- Tax information columns (added) ---
    # Annual tax paid (most recent year)
    annual_tax_paid = Column(Float, nullable=True, index=True)

    # Historical tax data by year
    tax_2020 = Column(Float, nullable=True)
    tax_2021 = Column(Float, nullable=True)
    tax_2022 = Column(Float, nullable=True)
    tax_2023 = Column(Float, nullable=True)
    tax_2024 = Column(Float, nullable=True)
    tax_2025 = Column(Float, nullable=True)

    # Date when tax info was last updated
    last_tax_update = Column(Date, nullable=True)
    
    def __repr__(self):
        return f"<Company(id={self.id}, Company='{self.Company}', BIN='{self.BIN}')>" 