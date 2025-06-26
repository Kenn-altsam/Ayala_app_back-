"""
API Router for AI conversation endpoints

Provides endpoints for charity sponsorship AI conversations.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from .models import ConversationInput, ConversationResponse, APIResponse
from .service import ai_service

# Create router
router = APIRouter(
    prefix="/funds",
    tags=["AI Conversation"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/conversation",
    response_model=APIResponse,
    summary="AI Conversation",
    description="Send a message to the AI assistant for charity sponsorship guidance"
)
async def ai_conversation(conversation_input: ConversationInput):
    """
    AI Conversation endpoint for charity sponsorship matching
    
    This endpoint allows charity foundations to interact with an AI assistant
    that helps them find potential sponsors and provides guidance on 
    sponsorship strategies.
    
    Args:
        conversation_input: User's input message
        
    Returns:
        AI-generated response with sponsorship guidance
        
    Raises:
        HTTPException: If AI service fails or input is invalid
    """
    try:
        # Validate input
        if not conversation_input.user_input.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User input cannot be empty"
            )
        
        # Generate AI response
        ai_response = await ai_service.generate_response(conversation_input.user_input)
        
        # Return structured response
        return APIResponse(
            status="success",
            data=ConversationResponse(message=ai_response),
            message="Conversation message processed successfully"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (from AI service)
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process conversation: {str(e)}"
        )


@router.get(
    "/conversation/health",
    summary="AI Service Health Check",
    description="Check if the AI conversation service is available"
)
async def ai_health_check():
    """
    Health check for AI conversation service
    
    Returns:
        Service status and availability
    """
    try:
        # Simple test to ensure AI service is configured
        if ai_service.settings.openai_api_key:
            return APIResponse(
                status="success",
                data={"service": "ai-conversation", "available": True},
                message="AI conversation service is available"
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=APIResponse(
                    status="error",
                    data={"service": "ai-conversation", "available": False},
                    message="AI service configuration missing"
                ).dict()
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=APIResponse(
                status="error",
                data={"service": "ai-conversation", "available": False},
                message=f"AI service health check failed: {str(e)}"
            ).dict()
        ) 