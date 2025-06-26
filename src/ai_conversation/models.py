"""
Pydantic models for AI conversation functionality

Defines request/response models for AI chat interactions.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ConversationInput(BaseModel):
    """Input model for AI conversation requests"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_input": "I'm looking for tech companies in Almaty that might be interested in sponsoring education initiatives"
            }
        }
    )
    
    user_input: str = Field(..., description="User's message/query to the AI")


class ConversationResponse(BaseModel):
    """Response model for AI conversation"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "I'd be happy to help you find tech companies in Almaty interested in education sponsorship. Could you tell me more about your educational initiative and what type of sponsorship you're looking for?"
            }
        }
    )
    
    message: str = Field(..., description="AI's response message")


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": {
                    "message": "AI response here"
                },
                "message": "Conversation message processed successfully"
            }
        }
    )
    
    status: str = Field(..., description="Response status: success or error")
    data: Optional[Any] = Field(None, description="Response data payload")
    message: str = Field(..., description="Human-readable response message") 