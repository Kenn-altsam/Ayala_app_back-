"""
OpenAI service for AI conversation functionality

Handles communication with OpenAI API for charity sponsorship matching.
"""

import asyncio
from typing import Optional

import openai
from fastapi import HTTPException

from ..core.config import get_settings


class OpenAIService:
    """Service for handling OpenAI API interactions"""
    
    def __init__(self):
        self.settings = get_settings()
        openai.api_key = self.settings.openai_api_key
        self.client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
        
    async def generate_response(self, user_input: str) -> str:
        """
        Generate AI response for charity sponsorship matching
        
        Args:
            user_input: User's message/query
            
        Returns:
            AI-generated response
            
        Raises:
            HTTPException: If OpenAI API call fails
        """
        try:
            # System prompt for charity sponsorship context
            system_prompt = """
            You are an AI assistant helping charity foundations find potential corporate sponsors. 
            Your role is to:
            1. Understand the charity's mission, focus areas, and sponsorship needs
            2. Ask clarifying questions to better understand their requirements
            3. Provide helpful guidance on approaching potential sponsors
            4. Be encouraging and professional in your responses
            
            Keep responses conversational, helpful, and focused on sponsorship matching.
            If the user asks about something unrelated to charity work or sponsorship, 
            politely redirect them back to sponsorship topics.
            """
            
            # Make API call to OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            # Extract the response
            ai_message = response.choices[0].message.content
            
            if not ai_message:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate AI response"
                )
                
            return ai_message.strip()
            
        except openai.APIError as e:
            raise HTTPException(
                status_code=503,
                detail=f"OpenAI API error: {str(e)}"
            )
        except openai.RateLimitError as e:
            raise HTTPException(
                status_code=429,
                detail="OpenAI API rate limit exceeded. Please try again later."
            )
        except openai.AuthenticationError as e:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API authentication failed. Please check configuration."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error in AI service: {str(e)}"
            )


# Global service instance
ai_service = OpenAIService() 