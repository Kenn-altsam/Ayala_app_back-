from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.auth.models import User
from .service import FundService
from .schemas import (
    FundProfileCreate,
    FundProfileResponse,
    ProjectCreate,
    ProjectResponse,
    ConversationInput,
    ConversationResponse
)

router = APIRouter(prefix="/funds", tags=["funds"])


@router.post("/profile", response_model=FundProfileResponse)
async def create_fund_profile(
    profile_data: FundProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new fund profile for the current user."""
    fund_service = FundService(db)
    
    # Check if profile already exists
    existing_profile = await fund_service.get_fund_profile(current_user.id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fund profile already exists"
        )
    
    fund = await fund_service.create_fund_profile(
        user_id=current_user.id,
        fund_name=profile_data.fund_name,
        fund_description=profile_data.fund_description,
        fund_email=profile_data.fund_email
    )
    return fund


@router.get("/profile", response_model=FundProfileResponse)
async def get_fund_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current user's fund profile."""
    fund_service = FundService(db)
    fund = await fund_service.get_fund_profile(current_user.id)
    
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fund profile not found"
        )
    
    return fund


@router.post("/conversation", response_model=ConversationResponse)
async def process_conversation(
    input_data: ConversationInput,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process conversation input and get AI response.
    The AI will ask questions to gather project information.
    """
    fund_service = FundService(db)
    fund = await fund_service.get_fund_profile(current_user.id)
    
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fund profile not found. Please create a profile first."
        )
    
    # Process the conversation
    message, required_fields, is_complete = await fund_service.process_conversation(
        fund=fund,
        user_input=input_data.user_input
    )
    
    # If conversation is complete, create a project
    if is_complete:
        state = fund.conversation_state
        await fund_service.create_project(
            fund_id=fund.id,
            name=state["project_name"],
            description=state["project_description"],
            target_region=state["target_region"],
            investment_amount=float(state["investment_amount"])
        )
        # Reset conversation state for next project
        await fund_service.reset_conversation(fund.id)
    
    return ConversationResponse(
        message=message,
        required_fields=required_fields,
        is_complete=is_complete
    )


@router.post("/conversation/reset")
async def reset_conversation(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reset the conversation state to start over."""
    fund_service = FundService(db)
    fund = await fund_service.get_fund_profile(current_user.id)
    
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fund profile not found"
        )
    
    await fund_service.reset_conversation(fund.id)
    return {"message": "Conversation reset successfully"} 