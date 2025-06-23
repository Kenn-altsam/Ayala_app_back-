from typing import Optional, Dict, Any, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from .models import FundProfile, Project
from src.core.ai import analyze_user_input


class FundService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_fund_profile(
        self, 
        user_id: UUID,
        fund_name: str,
        fund_description: str,
        fund_email: str
    ) -> FundProfile:
        fund = FundProfile(
            user_id=user_id,
            fund_name=fund_name,
            fund_description=fund_description,
            fund_email=fund_email
        )
        self.session.add(fund)
        await self.session.commit()
        await self.session.refresh(fund)
        return fund

    async def get_fund_profile(self, user_id: UUID) -> Optional[FundProfile]:
        result = await self.session.execute(
            select(FundProfile).where(FundProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_project(
        self,
        fund_id: UUID,
        name: str,
        description: str,
        target_region: str,
        investment_amount: float
    ) -> Project:
        project = Project(
            fund_id=fund_id,
            name=name,
            description=description,
            target_region=target_region,
            investment_amount=investment_amount
        )
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def process_conversation(
        self,
        fund: FundProfile,
        user_input: str
    ) -> Tuple[str, Dict[str, Optional[str]], bool]:
        """
        Process user input and update conversation state.
        Returns (AI response, updated required fields, conversation complete flag)
        """
        # Analyze user input using AI
        analysis = await analyze_user_input(user_input)
        
        # Update conversation state based on AI analysis
        state = fund.conversation_state
        
        # Extract information from user input
        if not state["project_name"] and analysis.get("project_name"):
            state["project_name"] = analysis["project_name"]
        
        if not state["project_description"] and analysis.get("project_description"):
            state["project_description"] = analysis["project_description"]
            
        if not state["target_region"] and analysis.get("target_region"):
            state["target_region"] = analysis["target_region"]
            
        if not state["investment_amount"] and analysis.get("investment_amount"):
            state["investment_amount"] = analysis["investment_amount"]
        
        # Determine what information is still needed
        missing_fields = {
            "project_name": state["project_name"],
            "project_description": state["project_description"],
            "target_region": state["target_region"],
            "investment_amount": state["investment_amount"]
        }
        
        # Generate appropriate response based on missing information
        if not state["project_name"]:
            response = "What is the name of your project?"
            state["last_question"] = "project_name"
        elif not state["project_description"]:
            response = "Please describe your project and its goals."
            state["last_question"] = "project_description"
        elif not state["target_region"]:
            response = "In which region are you looking for sponsors?"
            state["last_question"] = "target_region"
        elif not state["investment_amount"]:
            response = "What is the approximate investment amount you're seeking?"
            state["last_question"] = "investment_amount"
        else:
            response = (
                "Great! I have all the information I need. "
                "I'll now search for potential sponsors that match your criteria."
            )
            state["last_question"] = None
        
        # Update fund profile with new state
        fund.conversation_state = state
        await self.session.commit()
        
        is_complete = all(value is not None for value in missing_fields.values())
        
        return response, missing_fields, is_complete

    async def get_conversation_state(self, fund_id: UUID) -> Dict[str, Any]:
        """Get the current conversation state for a fund."""
        result = await self.session.execute(
            select(FundProfile).where(FundProfile.id == fund_id)
        )
        fund = result.scalar_one_or_none()
        return fund.conversation_state if fund else None

    async def reset_conversation(self, fund_id: UUID) -> None:
        """Reset the conversation state for a fund."""
        result = await self.session.execute(
            select(FundProfile).where(FundProfile.id == fund_id)
        )
        fund = result.scalar_one_or_none()
        if fund:
            fund.conversation_state = {
                "project_name": None,
                "project_description": None,
                "target_region": None,
                "investment_amount": None,
                "last_question": None
            }
            await self.session.commit() 