"""
Pydantic models for AI conversation functionality

Data models for AI conversation requests and responses.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from pydantic import validator


class ConversationInput(BaseModel):
    """Legacy conversation input model for backwards compatibility"""
    
    user_input: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="User's message or query"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "Can you help me find tech companies?"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat conversation with history"""
    
    user_input: str = Field(
        ..., 
        min_length=1, 
        max_length=1000,
        description="User's message or query"
    )
    history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Conversation history with role and content"
    )
    assistant_id: Optional[str] = Field(
        None,
        description="Optional OpenAI Assistant ID for persistent conversations"
    )
    thread_id: Optional[str] = Field(
        None,
        description="Optional OpenAI Thread ID for persistent conversations"
    )
    
    @validator('history', pre=True, always=True)
    def validate_request_history(cls, v):
        """Validate and clean incoming history"""
        if not v:
            return []
        
        if not isinstance(v, list):
            print(f"⚠️ [MODELS] Request history is not a list: {type(v)}, converting to empty list")
            return []
        
        validated_history = []
        for i, item in enumerate(v):
            if isinstance(item, dict):
                # Be more flexible with the validation - just require some content
                role = item.get('role', '').strip()
                content = item.get('content', '').strip()
                
                if role and content:
                    validated_history.append({
                        'role': role,
                        'content': content
                    })
                else:
                    print(f"⚠️ [MODELS] Skipping history item {i} with missing role/content: {item}")
            else:
                print(f"⚠️ [MODELS] Skipping non-dict history item {i}: {type(item)}")
        
        print(f"✅ [MODELS] Request history validated: {len(v)} -> {len(validated_history)} items")
        return validated_history
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "Can you help me find tech companies?",
                "history": [
                    {"role": "user", "content": "Hi there!"},
                    {"role": "assistant", "content": "Hello! I'm here to help you find potential corporate sponsors in Kazakhstan. How can I assist you today?"}
                ]
            }
        }


class ConversationResponse(BaseModel):
    """Legacy conversation response model for backwards compatibility"""
    
    message: str = Field(
        ..., 
        description="AI-generated response message"
    )
    required_fields: Optional[Dict[str, Optional[str]]] = Field(
        None,
        description="Required fields for completing the request"
    )
    is_complete: Optional[bool] = Field(
        None,
        description="Whether the conversation request is complete"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I'd be happy to help you find tech companies! Could you tell me which region you're interested in?",
                "required_fields": {"region": None},
                "is_complete": False
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat conversation with history"""
    
    message: str = Field(
        ..., 
        description="AI-generated response message"
    )
    companies_data: List['CompanyData'] = Field(
        default_factory=list,
        description="List of company data found"
    )
    updated_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Updated conversation history"
    )
    intent: Optional[str] = Field(
        None,
        description="Detected user intent"
    )
    location_detected: Optional[str] = Field(
        None,
        description="Location extracted from user input"
    )
    activity_keywords: Optional[List[str]] = Field(
        None,
        description="Activity keywords extracted from user input"
    )
    quantity_requested: Optional[int] = Field(
        None,
        description="Number of companies requested by user"
    )
    companies_found: int = Field(
        0,
        description="Number of companies found"
    )
    has_more_companies: bool = Field(
        False,
        description="Whether there are more companies available"
    )
    reasoning: Optional[str] = Field(
        None,
        description="AI reasoning for debugging"
    )
    assistant_id: Optional[str] = Field(
        None,
        description="OpenAI Assistant ID used for this response"
    )
    thread_id: Optional[str] = Field(
        None,
        description="OpenAI Thread ID used for this response"
    )
    
    @validator('updated_history', pre=True, always=True)
    def validate_history(cls, v):
        """
        Validate and clean updated_history with improved error handling.
        CRITICAL: This validator must preserve conversation history at all costs.
        """
        print(f"🔍 [MODELS] Validating updated_history: type={type(v)}, length={len(v) if isinstance(v, list) else 'N/A'}")
        
        if v is None:
            print("⚠️ [MODELS] Warning: updated_history was None, setting to empty list")
            return []
        
        if not isinstance(v, list):
            print(f"⚠️ [MODELS] Warning: updated_history was not a list: {type(v)}, converting to empty list")
            return []
        
        # More flexible validation - preserve as much history as possible
        validated_history = []
        for i, item in enumerate(v):
            try:
                if isinstance(item, dict):
                    # Extract role and content with better error handling
                    role = str(item.get('role', '')).strip()
                    content = str(item.get('content', '')).strip()
                    
                    # Accept any non-empty role and content
                    if role and content:
                        # Normalize role names
                        if role.lower() in ['user', 'human', 'participant']:
                            role = 'user'
                        elif role.lower() in ['assistant', 'ai', 'bot', 'system']:
                            role = 'assistant'
                        
                        validated_history.append({
                            'role': role,
                            'content': content
                        })
                    else:
                        print(f"⚠️ [MODELS] History item {i} missing role/content: role='{role}', content='{content[:50]}...'")
                else:
                    print(f"⚠️ [MODELS] History item {i} is not a dict: {type(item)} - {str(item)[:100]}...")
                    
            except Exception as e:
                print(f"❌ [MODELS] Error processing history item {i}: {e}")
                continue
        
        original_count = len(v)
        validated_count = len(validated_history)
        
        if validated_count != original_count:
            print(f"⚠️ [MODELS] History items changed: {original_count} -> {validated_count}")
        else:
            print(f"✅ [MODELS] All {validated_count} history items validated successfully")
        
        return validated_history
    
    @validator('message', pre=True, always=True)
    def validate_message(cls, v):
        """Ensure message is always a non-empty string"""
        if not v or not isinstance(v, str):
            print("⚠️ [MODELS] Invalid message, using fallback")
            return "Произошла ошибка при обработке запроса."
        return v.strip()
    
    @validator('companies_data', pre=True, always=True)
    def validate_companies_data(cls, v):
        """Ensure companies_data is always a list"""
        if not isinstance(v, list):
            print(f"⚠️ [MODELS] companies_data is not a list: {type(v)}, converting to empty list")
            return []
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Great! I found 5 companies in Almaty that might be interested in tech sponsorship...",
                "companies_data": [
                    {
                        "id": "123",
                        "name": "Tech Company LLP",
                        "activity": "Software development",
                        "locality": "Almaty",
                        "size": "Medium"
                    }
                ],
                "updated_history": [
                    {"role": "user", "content": "Hi there!"},
                    {"role": "assistant", "content": "Hello! How can I help?"},
                    {"role": "user", "content": "Can you help me find tech companies?"},
                    {"role": "assistant", "content": "Great! I found 5 companies..."}
                ],
                "intent": "find_companies",
                "location_detected": "Almaty",
                "activity_keywords": ["tech", "software"],
                "quantity_requested": 10,
                "companies_found": 5,
                "has_more_companies": False,
                "reasoning": "User asked for tech companies in Almaty"
            }
        }


class CompanyData(BaseModel):
    """
    Company data model for API responses, updated for consistency.
    FIX: This model now uses standard snake_case field names without aliases,
    ensuring it correctly consumes the data from the service layer.
    """
    
    id: str = Field(..., description="Company UUID")
    
    bin: Optional[str] = Field(None, description="Business Identification Number")
    name: str = Field(..., description="Company name")
    oked: Optional[str] = Field(None, description="OKED classification code")
    activity: Optional[str] = Field(None, description="Business activity description")
    kato: Optional[str] = Field(None, description="KATO territorial code")
    locality: Optional[str] = Field(None, description="Company location")
    krp: Optional[str] = Field(None, description="KRP classification code")
    size: Optional[str] = Field(None, description="Company size category")
    
    class Config:
        # populate_by_name is no longer needed as we've standardized the field names
        json_schema_extra = {
            "example": {
                "id": "b4262001-044d-4d62-bf90-49d1f6ae8dc0",
                "bin": "080241016588",
                "name": "Sample Company LLP",
                "oked": "50200",
                "activity": "Maritime and coastal freight transport",
                "kato": "471010000",
                "locality": "Mangistau region, Aktau",
                "krp": "310",
                "size": "Large enterprises (501 - 1000 people)"
            }
        }


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    
    status: str = Field(
        ..., 
        description="Response status (success/error)"
    )
    data: Union[
        ChatResponse,
        List[CompanyData], 
        List[Dict[str, Any]], 
        Dict[str, Any]
    ] = Field(
        ..., 
        description="Response data"
    )
    message: str = Field(
        ..., 
        description="Response message"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "message": "I found some great companies for you!",
                    "companies_data": [],
                    "updated_history": [],
                    "companies_found": 0
                },
                "message": "Request processed successfully"
            }
        } 