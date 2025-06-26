"""
SQLAlchemy models for user authentication

Defines the database schema for user accounts and authentication.
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base


class User(Base):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User profile
    full_name = Column(String(255), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    fund_profile = relationship("FundProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', full_name='{self.full_name}')>" 