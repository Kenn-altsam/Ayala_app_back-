"""
SQLAlchemy models for fund profiles and conversation state

Defines the database schema for charity fund profiles and AI conversation state.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..core.database import Base


class FundProfile(Base):
    """Fund profile model for charity foundation information"""
    
    __tablename__ = "fund_profiles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Fund information
    fund_name = Column(String(255), nullable=False)
    fund_description = Column(Text)
    fund_email = Column(String(255))
    
    # AI conversation state
    conversation_state = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="fund_profile")
    
    def __repr__(self):
        return f"<FundProfile(id={self.id}, fund_name='{self.fund_name}', user_id={self.user_id})>" 