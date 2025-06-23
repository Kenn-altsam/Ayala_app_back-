from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name (required)")
    fullName: Optional[str] = Field(None, description="User's full name (iOS camelCase)", exclude=True)
    google_id: Optional[str] = Field(None, description="Google user ID (for Google OAuth users)")
    
    @model_validator(mode='before')
    @classmethod
    def validate_name_fields(cls, data):
        if isinstance(data, dict):
            # If fullName is provided but full_name is not, use fullName
            if 'fullName' in data and data['fullName'] and not data.get('full_name'):
                data['full_name'] = data['fullName']
            
            # Validate that we have a non-empty full_name
            if not data.get('full_name') or not data.get('full_name').strip():
                raise ValueError("Full name is required and cannot be empty")
                
        return data


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    email: str = Field(..., description="Email address for password reset")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100) 