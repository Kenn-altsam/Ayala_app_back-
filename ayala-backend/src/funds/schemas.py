from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class FundProfileCreate(BaseModel):
    fund_name: str = Field(..., min_length=1, max_length=255)
    fund_description: str = Field(..., min_length=10)
    fund_email: EmailStr


class FundProfileResponse(FundProfileCreate):
    id: UUID
    user_id: UUID
    conversation_state: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    target_region: str = Field(..., min_length=1, max_length=100)
    investment_amount: float = Field(..., gt=0)


class ProjectResponse(ProjectCreate):
    id: UUID
    fund_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationInput(BaseModel):
    user_input: str = Field(..., min_length=1)


class ConversationResponse(BaseModel):
    message: str
    required_fields: Dict[str, Optional[str]]
    is_complete: bool
    
    model_config = ConfigDict(from_attributes=True) 