from openai import AsyncOpenAI
from .config import settings
from typing import Dict, Any, List, Optional
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create async OpenAI client only if API key is available
ai_client = None
if settings.OPENAI_API_KEY:
    try:
        ai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI client: {str(e)}")
        ai_client = None
else:
    logger.warning("OpenAI API key not found. AI features will be disabled.")


async def validate_openai_response(response: Any, context: str) -> bool:
    """
    Validate OpenAI API response.
    
    Args:
        response: The response from OpenAI API
        context: Context of the API call for logging
        
    Returns:
        bool: True if response is valid, False otherwise
    """
    try:
        if not response or not response.choices:
            logger.error(f"Invalid OpenAI response in {context}: No choices found")
            return False
            
        if not response.choices[0].message:
            logger.error(f"Invalid OpenAI response in {context}: No message in first choice")
            return False
            
        if not response.choices[0].message.content:
            logger.error(f"Invalid OpenAI response in {context}: Empty content in message")
            return False
            
        # Log successful response
        logger.info(f"Valid OpenAI response received for {context}")
        logger.debug(f"Response content: {response.choices[0].message.content[:100]}...")  # Log first 100 chars
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating OpenAI response in {context}: {str(e)}")
        return False


async def get_ai_response(prompt: str) -> str:
    """
    Get a response from OpenAI API.
    
    Args:
        prompt: The input text to send to OpenAI
        
    Returns:
        The AI-generated response text
    """
    if not ai_client:
        raise ValueError("OpenAI client is not available. Please configure OPENAI_API_KEY.")
    
    try:
        logger.info("Sending request to OpenAI API")
        logger.debug(f"Prompt: {prompt[:100]}...")  # Log first 100 chars of prompt
        
        response = await ai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for the Ayala Foundation, helping to match companies with charity funds."},
                {"role": "user", "content": prompt}
            ],
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS
        )
        
        if await validate_openai_response(response, "get_ai_response"):
            return response.choices[0].message.content
        else:
            raise ValueError("Invalid response from OpenAI API")
            
    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        raise


async def analyze_user_input(user_input: str) -> Dict[str, Any]:
    """
    Analyze user input to extract project information.
    Returns a dictionary with extracted fields.
    """
    if not ai_client:
        logger.warning("OpenAI client not available, returning empty analysis")
        return {
            "project_name": None,
            "project_description": None,
            "target_region": None,
            "investment_amount": None
        }
    
    try:
        logger.info("Analyzing user input")
        logger.debug(f"User input: {user_input[:100]}...")  # Log first 100 chars
        
        system_prompt = """
        You are an AI assistant helping to extract project information from user input.
        The goal is to identify the following fields if present:
        - project_name: The name of the project
        - project_description: Description and goals of the project
        - target_region: The region where they're seeking sponsors
        - investment_amount: The amount of investment needed (convert text to number)
        
        Only extract information that is explicitly mentioned. Do not make assumptions.
        Return NULL for fields that are not clearly stated.
        Format the response as a valid JSON object.
        """
        
        user_message = f"Please analyze this text and extract project information: {user_input}"
        
        response = await ai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,  # Low temperature for more focused extraction
            max_tokens=500
        )
        
        if not await validate_openai_response(response, "analyze_user_input"):
            raise ValueError("Invalid response from OpenAI API")
        
        # Parse the response to extract the fields
        content = response.choices[0].message.content
        logger.debug(f"Raw AI response: {content}")
        
        # Attempt to parse JSON response
        try:
            extracted = json.loads(content)
            logger.info("Successfully parsed JSON response")
            logger.debug(f"Extracted data: {extracted}")
            return extracted
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {str(e)}")
            logger.debug(f"Problematic content: {content}")
            raise
            
    except Exception as e:
        logger.error(f"Error in analyze_user_input: {str(e)}")
        return {
            "project_name": None,
            "project_description": None,
            "target_region": None,
            "investment_amount": None
        }


async def analyze_company_match(
    company_data: Dict[str, Any],
    project_description: str,
    investment_amount: float
) -> Dict[str, Any]:
    """
    Analyze how well a company matches with a project's needs.
    Returns a match score and reasoning.
    """
    if not ai_client:
        logger.warning("OpenAI client not available, returning default match score")
        return {
            "match_score": 50,
            "reasoning": "AI analysis not available - manual review required",
            "approach_strategy": "Contact company directly to discuss partnership opportunities"
        }
    
    try:
        logger.info("Analyzing company match")
        
        system_prompt = """
        You are an AI assistant helping to match companies with charity projects.
        Analyze the company data and project requirements to:
        1. Calculate a match score (0-100)
        2. Provide reasoning for the score
        3. Suggest an approach strategy
        
        Consider:
        - Company's industry alignment with project
        - Company's financial capacity vs. investment needed
        - Past donation history
        - Geographic proximity
        - Social responsibility indicators
        
        Format the response as a valid JSON object with fields:
        - match_score: number (0-100)
        - reasoning: string
        - approach_strategy: string
        """
        
        user_message = f"""
        Project Description: {project_description}
        Investment Amount Needed: {investment_amount}
        
        Company Information:
        {json.dumps(company_data, indent=2)}
        """
        
        response = await ai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        if not await validate_openai_response(response, "analyze_company_match"):
            raise ValueError("Invalid response from OpenAI API")
        
        content = response.choices[0].message.content
        logger.debug(f"Raw AI response: {content}")
        
        try:
            result = json.loads(content)
            logger.info("Successfully parsed company match analysis")
            logger.debug(f"Analysis result: {result}")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from company match analysis: {str(e)}")
            logger.debug(f"Problematic content: {content}")
            raise
            
    except Exception as e:
        logger.error(f"Error in analyze_company_match: {str(e)}")
        return {
            "match_score": 0,
            "reasoning": f"Error analyzing match: {str(e)}",
            "approach_strategy": "Unable to generate strategy"
        }


async def suggest_approach_strategy(
    company_data: Dict[str, Any],
    project_data: Dict[str, Any]
) -> str:
    """
    Generate a personalized approach strategy for contacting the company.
    """
    try:
        logger.info("Generating approach strategy")
        
        system_prompt = """
        You are an AI assistant helping charities approach potential corporate sponsors.
        Create a personalized strategy considering:
        1. Company's past donation history
        2. Industry alignment
        3. Company's social responsibility focus
        4. Recent company news or developments
        5. Potential mutual benefits
        
        Provide specific, actionable advice for making the approach.
        """
        
        user_message = f"""
        Project Information:
        {json.dumps(project_data, indent=2)}
        
        Company Information:
        {json.dumps(company_data, indent=2)}
        """
        
        response = await ai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        if not await validate_openai_response(response, "suggest_approach_strategy"):
            raise ValueError("Invalid response from OpenAI API")
            
        strategy = response.choices[0].message.content
        logger.info("Successfully generated approach strategy")
        logger.debug(f"Strategy preview: {strategy[:100]}...")  # Log first 100 chars
        
        return strategy
        
    except Exception as e:
        logger.error(f"Error in suggest_approach_strategy: {str(e)}")
        return f"Error generating approach strategy: {str(e)}"


async def generate_smart_company_query(user_input: str) -> Dict[str, Any]:
    """
    Use OpenAI to interpret natural language and generate database query parameters.
    This helps users find companies using conversational queries.
    
    Example:
    "Find tech companies in Almaty with good websites" 
    -> {region: "Almaty", industry: "technology", has_website: true}
    """
    try:
        logger.info("Generating smart company query from user input")
        logger.debug(f"User input: {user_input}")
        
        system_prompt = """
        You are an AI assistant that converts natural language queries into structured database search parameters.
        
        Available search parameters:
        - region: string (Kazakhstan regions like "Almaty", "Astana", "Atyrau", etc.)
        - city: string 
        - industry: string (technology, finance, manufacturing, retail, etc.)
        - min_employees: integer
        - max_employees: integer
        - has_website: boolean
        - has_social_media: boolean
        - has_contact_info: boolean
        - min_tax_paid: float (annual tax paid)
        - max_tax_paid: float
        
        Parse the user's natural language query and extract relevant search parameters.
        Return a JSON object with only the parameters that can be inferred from the query.
        If a parameter cannot be determined, omit it from the response.
        
        Examples:
        "Find tech companies in Almaty" -> {"region": "Almaty", "industry": "technology"}
        "Large companies with websites" -> {"min_employees": 100, "has_website": true}
        "Manufacturing companies in Astana with good online presence" -> {"region": "Astana", "industry": "manufacturing", "has_website": true, "has_social_media": true}
        """
        
        response = await ai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Convert this query to search parameters: {user_input}"}
            ],
            temperature=0.1,  # Low temperature for consistent parsing
            max_tokens=300
        )
        
        if not await validate_openai_response(response, "generate_smart_company_query"):
            raise ValueError("Invalid response from OpenAI API")
        
        content = response.choices[0].message.content
        logger.debug(f"AI generated query parameters: {content}")
        
        try:
            query_params = json.loads(content)
            logger.info("Successfully generated smart query parameters")
            return query_params
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse query parameters: {str(e)}")
            return {}
            
    except Exception as e:
        logger.error(f"Error generating smart company query: {str(e)}")
        return {}


async def generate_fund_profile_questions(current_state: Dict[str, Any]) -> str:
    """
    Generate intelligent follow-up questions to complete fund profile information.
    """
    try:
        logger.info("Generating fund profile questions")
        
        system_prompt = """
        You are an AI assistant helping charity funds complete their profile information.
        Based on what information is already provided, ask relevant follow-up questions to gather missing details.
        
        Be conversational and helpful. Focus on:
        - Project goals and objectives
        - Target regions for sponsorship
        - Investment amounts needed
        - Industry preferences
        - Timeline and urgency
        
        Keep questions natural and engaging, like a friendly consultant would ask.
        """
        
        current_info = json.dumps(current_state, indent=2)
        user_message = f"Based on this current fund information, what should I ask next to complete their profile?\n\nCurrent Info:\n{current_info}"
        
        response = await ai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,  # Higher temperature for more conversational responses
            max_tokens=400
        )
        
        if not await validate_openai_response(response, "generate_fund_profile_questions"):
            return "Tell me more about your project and what kind of companies you're looking to partner with."
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating fund profile questions: {str(e)}")
        return "Could you tell me more about your project goals and target regions?" 