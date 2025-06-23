from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import String, Boolean, Float, Integer, Date, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from src.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    # Basic Information
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bin: Mapped[Optional[str]] = mapped_column(String(12), unique=True)
    registration_date: Mapped[Optional[datetime]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    company_type: Mapped[Optional[str]] = mapped_column(String(50))
    employee_count: Mapped[Optional[int]] = mapped_column(Integer)
    revenue_range: Mapped[Optional[str]] = mapped_column(String(50))
    industry: Mapped[Optional[str]] = mapped_column(String(100))

    # Contact Information
    website: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000))

    # Social Media and Contact Verification
    social_media: Mapped[dict] = mapped_column(JSONB, server_default='{}')
    has_social_media: Mapped[bool] = mapped_column(Boolean, server_default='false')
    has_website: Mapped[bool] = mapped_column(Boolean, server_default='false')
    has_contact_info: Mapped[bool] = mapped_column(Boolean, server_default='false')

    # Tax Information
    annual_tax_paid: Mapped[Optional[float]] = mapped_column(Float)
    tax_reporting_year: Mapped[Optional[int]] = mapped_column(Integer)
    tax_compliance_score: Mapped[Optional[float]] = mapped_column(Float)
    last_tax_update: Mapped[Optional[datetime]] = mapped_column(Date)

    # Sponsorship Information
    past_donations: Mapped[Optional[str]] = mapped_column(Text)
    sponsorship_interests: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default='CURRENT_TIMESTAMP'
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default='CURRENT_TIMESTAMP', 
        onupdate=datetime.utcnow
    )

    # Relationships
    locations: Mapped[list["Location"]] = relationship(
        "Location", 
        back_populates="company", 
        cascade="all, delete-orphan"
    )


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("companies.id", ondelete="CASCADE"), 
        nullable=False
    )
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(String(500))
    postal_code: Mapped[Optional[str]] = mapped_column(String(10))
    coordinates = mapped_column(Geography(geometry_type='POINT', srid=4326))
    is_primary: Mapped[bool] = mapped_column(Boolean, server_default='false')
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default='CURRENT_TIMESTAMP'
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="locations") 