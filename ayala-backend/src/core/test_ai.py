import asyncio
import logging
from src.core.ai import get_ai_response, analyze_user_input, analyze_company_match, suggest_approach_strategy

# Set logging to DEBUG level to see all logs
logging.basicConfig(level=logging.DEBUG)

async def test_get_ai_response():
    print("\n=== Testing get_ai_response ===")
    try:
        response = await get_ai_response("Tell me about the Ayala Foundation")
        print(f"Response received: {response[:200]}...")  # Show first 200 chars
    except Exception as e:
        print(f"Error in get_ai_response: {e}")

async def test_analyze_user_input():
    print("\n=== Testing analyze_user_input ===")
    test_input = """
    We're planning a project called 'Green Future' in Almaty region. 
    It's an environmental education program targeting schools.
    We need about 5 million tenge for implementation.
    """
    try:
        result = await analyze_user_input(test_input)
        print("Extracted information:")
        print(f"Project name: {result.get('project_name')}")
        print(f"Description: {result.get('project_description')}")
        print(f"Region: {result.get('target_region')}")
        print(f"Investment: {result.get('investment_amount')}")
    except Exception as e:
        print(f"Error in analyze_user_input: {e}")

async def test_analyze_company_match():
    print("\n=== Testing analyze_company_match ===")
    test_company = {
        "name": "Test Company",
        "industry": "Technology",
        "annual_tax_paid": 1000000,
        "past_donations": "Previous donations to educational projects",
        "region": "Almaty"
    }
    try:
        result = await analyze_company_match(
            test_company,
            "Environmental education program in schools",
            5000000
        )
        print("Match analysis:")
        print(f"Match score: {result.get('match_score')}")
        print(f"Reasoning: {result.get('reasoning')}")
        print(f"Strategy: {result.get('approach_strategy')}")
    except Exception as e:
        print(f"Error in analyze_company_match: {e}")

async def test_suggest_approach_strategy():
    print("\n=== Testing suggest_approach_strategy ===")
    test_company = {
        "name": "Tech Solutions Ltd",
        "industry": "Technology",
        "past_donations": "Educational initiatives",
        "region": "Almaty"
    }
    test_project = {
        "name": "Digital Literacy",
        "description": "Teaching programming to high school students",
        "target_region": "Almaty",
        "investment_amount": 3000000
    }
    try:
        strategy = await suggest_approach_strategy(test_company, test_project)
        print(f"Generated strategy: {strategy[:200]}...")  # Show first 200 chars
    except Exception as e:
        print(f"Error in suggest_approach_strategy: {e}")

async def run_all_tests():
    """Run all test functions"""
    print("Starting AI response tests...")
    
    await test_get_ai_response()
    await test_analyze_user_input()
    await test_analyze_company_match()
    await test_suggest_approach_strategy()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_all_tests()) 