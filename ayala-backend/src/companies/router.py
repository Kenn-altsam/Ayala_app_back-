from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.companies import service, schemas
from src.companies.service import CompanyService
from src.auth.dependencies import get_current_user
from uuid import UUID
from src.core.ai import analyze_company_match, suggest_approach_strategy

router = APIRouter(prefix="/companies")

@router.get("/search", response_model=List[schemas.CompanyResponse])
async def search_companies(
    query: str = Query(None, description="Natural language search query"),
    region: str = Query(None, description="Region to search in"),
    city: str = Query(None, description="City to search in"),
    latitude: float = Query(None, description="Latitude for location-based search"),
    longitude: float = Query(None, description="Longitude for location-based search"),
    radius: float = Query(None, description="Search radius in kilometers"),
    industry: str = Query(None, description="Industry filter"),
    min_employees: int = Query(None, description="Minimum number of employees"),
    max_employees: int = Query(None, description="Maximum number of employees"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Search for companies using various filters including location and natural language query.
    Uses AI to interpret natural language queries and match with relevant companies.
    """
    companies = await service.search_companies(
        db=db,
        query=query,
        region=region,
        city=city,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        industry=industry,
        min_employees=min_employees,
        max_employees=max_employees
    )
    return companies

@router.get("/ai-search", response_model=List[schemas.CompanyResponse])
async def ai_search_companies(
    query: str = Query(..., description="Natural language query like 'Find tech companies in Almaty with websites'"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    AI-powered company search using natural language.
    
    Examples:
    - "Find tech companies in Almaty with websites"
    - "Large manufacturing companies that pay high taxes"
    - "Companies in Astana with social media presence"
    """
    company_service = CompanyService(db)
    companies = await company_service.smart_search_companies(query)
    return companies

@router.get("/ai-suggestions")
async def get_ai_company_suggestions(
    project_description: str = Query(..., description="Description of your charity project"),
    investment_amount: float = Query(..., description="Investment amount needed"),
    region: Optional[str] = Query(None, description="Target region"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get AI-powered company suggestions based on project description and investment needs.
    
    Returns companies ranked by AI-calculated match scores with reasoning and approach strategies.
    """
    company_service = CompanyService(db)
    suggestions = await company_service.get_ai_company_suggestions(
        project_description, 
        investment_amount, 
        region
    )
    return {
        "status": "success",
        "data": suggestions,
        "message": f"Found {len(suggestions)} potential sponsors"
    }

@router.get("/{company_id}", response_model=schemas.CompanyDetailResponse)
async def get_company(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get detailed information about a specific company.
    """
    company = await service.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.get("/region/{region}", response_model=List[schemas.CompanyResponse])
async def get_companies_by_region(
    region: str,
    city: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get companies in a specific region or city.
    """
    companies = await service.get_companies_by_region(db, region, city)
    return companies

@router.get("/suggest", response_model=List[schemas.CompanySuggestion])
async def suggest_companies(
    charity_description: str = Query(..., description="Description of charity's needs and interests"),
    region: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get AI-powered suggestions for potential sponsor companies based on charity description.
    """
    suggestions = await service.suggest_companies(db, charity_description, region)
    return suggestions 