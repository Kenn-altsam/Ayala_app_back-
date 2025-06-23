from datetime import datetime
import uuid
from sqlalchemy import String, Text, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from src.core.database import Base


class FundProfile(Base):
    __tablename__ = "fund_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    fund_name: Mapped[str] = mapped_column(String(255), nullable=False)
    fund_description: Mapped[str] = mapped_column(Text, nullable=False)
    fund_email: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Conversation state tracking
    conversation_state: Mapped[dict] = mapped_column(
        JSON, 
        default={
            "project_name": None,
            "project_description": None,
            "target_region": None,
            "investment_amount": None,
            "last_question": None
        }
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fund_id: Mapped[str] = mapped_column(String(36), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_region: Mapped[str] = mapped_column(String(100), nullable=False)
    investment_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    ) 