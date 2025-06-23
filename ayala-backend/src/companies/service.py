from typing import List, Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_GeomFromText
from openai import AsyncOpenAI
from uuid import UUID
from sqlalchemy.orm import selectinload

from src.companies.models import Company, Location
from src.companies.schemas import CompanySearchFilters, CompanySuggestion, CompanyCreate, CompanyUpdate, LocationCreate
from src.core.config import settings
from src.core.ai import generate_smart_company_query, analyze_company_match

# Initialize OpenAI client only if API key is available
client = None
if settings.OPENAI_API_KEY:
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        print(f"Warning: Failed to initialize OpenAI client in companies service: {e}")
        client = None

async def search_companies(
    db: AsyncSession,
    query: Optional[str] = None,
    region: Optional[str] = None,
    city: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius: Optional[float] = None,
    industry: Optional[str] = None,
    min_employees: Optional[int] = None,
    max_employees: Optional[int] = None,
) -> List[Company]:
    """
    Search for companies using various filters including location and natural language query.
    """
    # Base query
    query_obj = select(Company).join(Location)
    
    # Apply filters
    filters = []
    
    if region:
        filters.append(Location.region.ilike(f"%{region}%"))
    
    if city:
        filters.append(Location.city.ilike(f"%{city}%"))
    
    if latitude and longitude and radius:
        # Convert radius from km to meters
        radius_meters = radius * 1000
        point = ST_MakePoint(longitude, latitude)
        filters.append(
            ST_DWithin(
                Location.coordinates,
                point,
                radius_meters
            )
        )
    
    if industry:
        filters.append(Company.industry.ilike(f"%{industry}%"))
    
    if min_employees:
        filters.append(Company.employee_count >= min_employees)
    
    if max_employees:
        filters.append(Company.employee_count <= max_employees)
    
    if query:
        # Natural language search using company attributes
        filters.append(
            or_(
                Company.name.ilike(f"%{query}%"),
                Company.description.ilike(f"%{query}%"),
                Company.sponsorship_interests.ilike(f"%{query}%")
            )
        )
    
    if filters:
        query_obj = query_obj.where(and_(*filters))
    
    # Execute query
    result = await db.execute(query_obj)
    return result.scalars().unique().all()

async def get_company(db: AsyncSession, company_id: str) -> Optional[Company]:
    """
    Get a specific company by ID.
    """
    query = select(Company).where(Company.id == company_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_companies_by_region(
    db: AsyncSession,
    region: str,
    city: Optional[str] = None
) -> List[Company]:
    """
    Get companies in a specific region or city.
    """
    query = select(Company).join(Location)
    
    filters = [Location.region.ilike(f"%{region}%")]
    if city:
        filters.append(Location.city.ilike(f"%{city}%"))
    
    query = query.where(and_(*filters))
    result = await db.execute(query)
    return result.scalars().unique().all()

async def suggest_companies(
    db: AsyncSession,
    charity_description: str,
    region: Optional[str] = None
) -> List[CompanySuggestion]:
    """
    Use AI to suggest potential sponsor companies based on charity description.
    """
    # Get companies (with region filter if specified)
    query = select(Company).join(Location)
    if region:
        query = query.where(Location.region.ilike(f"%{region}%"))
    
    result = await db.execute(query)
    companies = result.scalars().unique().all()
    
    # Use OpenAI to analyze and match companies
    suggestions = []
    for company in companies:
        company_info = {
            "name": company.name,
            "industry": company.industry,
            "description": company.description,
            "sponsorship_interests": company.sponsorship_interests,
            "past_donations": company.past_donations
        }
        
        if client:
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """
                    You are an AI assistant helping match charities with potential corporate sponsors.
                    Analyze the charity's needs and the company's profile to determine compatibility.
                    Provide a match score (0-1), reason for the match, and potential sponsorship areas.
                    """},
                    {"role": "user", "content": f"""
                    Charity Description: {charity_description}
                    
                    Company Information:
                    {company_info}
                    
                    Analyze the compatibility and provide:
                    1. Match score (0-1)
                    2. Reason for match
                    3. Potential sponsorship areas
                    """}
                ]
            )
            # Parse AI response and create suggestion
            analysis = response.choices[0].message.content
        else:
            analysis = "AI analysis not available - OpenAI client not configured"
        # Simple parsing logic - in production, use more robust parsing
        match_score = 0.7  # Example score
        match_reason = "Strong alignment in values and interests"  # Example reason
        potential_areas = ["Education", "Healthcare"]  # Example areas
        
        suggestions.append(
            CompanySuggestion(
                company=company,
                match_score=match_score,
                match_reason=match_reason,
                potential_sponsorship_areas=potential_areas
            )
        )
    
    # Sort suggestions by match score
    suggestions.sort(key=lambda x: x.match_score, reverse=True)
    return suggestions

class CompanyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_company(self, company_data: CompanyCreate) -> Company:
        # Create company instance
        company = Company(
            name=company_data.name,
            bin=company_data.bin,
            registration_date=company_data.registration_date,
            status=company_data.status,
            company_type=company_data.company_type,
            employee_count=company_data.employee_count,
            revenue_range=company_data.revenue_range,
            industry=company_data.industry,
            website=company_data.website,
            phone=company_data.phone,
            email=company_data.email,
            description=company_data.description,
            social_media=company_data.social_media,
            annual_tax_paid=company_data.annual_tax_paid,
            tax_reporting_year=company_data.tax_reporting_year,
            tax_compliance_score=company_data.tax_compliance_score,
            last_tax_update=company_data.last_tax_update,
            past_donations=company_data.past_donations,
            sponsorship_interests=company_data.sponsorship_interests,
        )

        # Set verification flags
        company.has_website = bool(company_data.website)
        company.has_social_media = bool(company_data.social_media)
        company.has_contact_info = bool(company_data.email or company_data.phone)

        # Add locations if provided
        if company_data.locations:
            for loc_data in company_data.locations:
                location = Location(
                    region=loc_data.region,
                    city=loc_data.city,
                    address=loc_data.address,
                    postal_code=loc_data.postal_code,
                    is_primary=loc_data.is_primary,
                )
                if loc_data.coordinates:
                    location.coordinates = ST_GeomFromText(loc_data.coordinates, 4326)
                company.locations.append(location)

        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def get_company(self, company_id: UUID) -> Optional[Company]:
        query = select(Company).options(selectinload(Company.locations)).where(Company.id == company_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_companies(
        self,
        skip: int = 0,
        limit: int = 10,
        industry: Optional[str] = None,
        has_website: Optional[bool] = None,
        has_social_media: Optional[bool] = None,
        has_contact_info: Optional[bool] = None,
        min_tax_paid: Optional[float] = None,
    ) -> List[Company]:
        query = select(Company).options(selectinload(Company.locations))

        # Apply filters
        if industry:
            query = query.where(Company.industry == industry)
        if has_website is not None:
            query = query.where(Company.has_website == has_website)
        if has_social_media is not None:
            query = query.where(Company.has_social_media == has_social_media)
        if has_contact_info is not None:
            query = query.where(Company.has_contact_info == has_contact_info)
        if min_tax_paid is not None:
            query = query.where(Company.annual_tax_paid >= min_tax_paid)

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_company(self, company_id: UUID, company_data: CompanyUpdate) -> Optional[Company]:
        # Get existing company
        company = await self.get_company(company_id)
        if not company:
            return None

        # Update company fields
        for field, value in company_data.dict(exclude_unset=True).items():
            if field == "locations":
                continue
            setattr(company, field, value)

        # Update verification flags
        if company_data.website is not None:
            company.has_website = bool(company_data.website)
        if company_data.social_media is not None:
            company.has_social_media = bool(company_data.social_media)
        if company_data.email is not None or company_data.phone is not None:
            company.has_contact_info = bool(company.email or company.phone)

        # Handle location updates if provided
        if company_data.locations:
            # Remove existing locations
            company.locations = []
            # Add new locations
            for loc_data in company_data.locations:
                location = Location(
                    region=loc_data.region,
                    city=loc_data.city,
                    address=loc_data.address,
                    postal_code=loc_data.postal_code,
                    is_primary=loc_data.is_primary,
                )
                if loc_data.coordinates:
                    location.coordinates = ST_GeomFromText(loc_data.coordinates, 4326)
                company.locations.append(location)

        await self.session.commit()
        await self.session.refresh(company)
        return company

    async def delete_company(self, company_id: UUID) -> bool:
        # Get existing company
        company = await self.get_company(company_id)
        if not company:
            return False
            
        # Delete the company
        await self.session.delete(company)
        await self.session.commit()
        return True

    async def smart_search_companies(self, natural_language_query: str) -> List[Company]:
        """
        Use AI to interpret natural language query and search companies.
        
        Example queries:
        - "Find tech companies in Almaty with websites"
        - "Large manufacturing companies that pay high taxes"
        - "Companies in Astana with social media presence"
        """
        # Use AI to generate search parameters
        ai_params = await generate_smart_company_query(natural_language_query)
        
        # Build database query based on AI interpretation
        query_obj = select(Company).join(Location)
        filters = []
        
        # Apply AI-generated filters
        if "region" in ai_params:
            filters.append(Location.region.ilike(f"%{ai_params['region']}%"))
        
        if "city" in ai_params:
            filters.append(Location.city.ilike(f"%{ai_params['city']}%"))
        
        if "industry" in ai_params:
            filters.append(Company.industry.ilike(f"%{ai_params['industry']}%"))
        
        if "min_employees" in ai_params:
            filters.append(Company.employee_count >= ai_params["min_employees"])
        
        if "max_employees" in ai_params:
            filters.append(Company.employee_count <= ai_params["max_employees"])
        
        if "has_website" in ai_params:
            filters.append(Company.has_website == ai_params["has_website"])
        
        if "has_social_media" in ai_params:
            filters.append(Company.has_social_media == ai_params["has_social_media"])
        
        if "has_contact_info" in ai_params:
            filters.append(Company.has_contact_info == ai_params["has_contact_info"])
        
        if "min_tax_paid" in ai_params:
            filters.append(Company.annual_tax_paid >= ai_params["min_tax_paid"])
        
        if "max_tax_paid" in ai_params:
            filters.append(Company.annual_tax_paid <= ai_params["max_tax_paid"])
        
        # Apply fallback text search if no specific filters found
        if not filters:
            filters.append(
                or_(
                    Company.name.ilike(f"%{natural_language_query}%"),
                    Company.description.ilike(f"%{natural_language_query}%"),
                    Company.sponsorship_interests.ilike(f"%{natural_language_query}%")
                )
            )
        
        # Execute query
        if filters:
            query_obj = query_obj.where(and_(*filters))
        
        result = await self.session.execute(query_obj)
        return result.scalars().unique().all()

    async def get_ai_company_suggestions(
        self, 
        project_description: str, 
        investment_amount: float,
        region: Optional[str] = None
    ) -> List[dict]:
        """
        Get AI-powered company suggestions based on project description and investment needs.
        """
        # Get companies (filter by region if provided)
        query_obj = select(Company).join(Location).options(selectinload(Company.locations))
        
        if region:
            query_obj = query_obj.where(Location.region.ilike(f"%{region}%"))
        
        # Limit to top companies by tax paid (indicates financial capacity)
        query_obj = query_obj.order_by(Company.annual_tax_paid.desc()).limit(50)
        
        result = await self.session.execute(query_obj)
        companies = result.scalars().unique().all()
        
        suggestions = []
        for company in companies:
            # Prepare company data for AI analysis
            company_data = {
                "id": str(company.id),
                "name": company.name,
                "industry": company.industry,
                "employee_count": company.employee_count,
                "annual_tax_paid": company.annual_tax_paid,
                "has_website": company.has_website,
                "has_social_media": company.has_social_media,
                "has_contact_info": company.has_contact_info,
                "description": company.description,
                "region": company.locations[0].region if company.locations else None,
                "city": company.locations[0].city if company.locations else None
            }
            
            # Get AI analysis for this company
            try:
                ai_analysis = await analyze_company_match(
                    company_data, 
                    project_description, 
                    investment_amount
                )
                
                suggestions.append({
                    "company": {
                        "id": company_data["id"],
                        "name": company_data["name"],
                        "industry": company_data["industry"],
                        "region": company_data["region"]
                    },
                    "match_score": ai_analysis.get("match_score", 0),
                    "reasoning": ai_analysis.get("reasoning", ""),
                    "approach_strategy": ai_analysis.get("approach_strategy", "")
                })
            except Exception as e:
                # If AI analysis fails, skip this company
                continue
        
        # Sort by match score and return top 10
        suggestions.sort(key=lambda x: x["match_score"], reverse=True)
        return suggestions[:10]

    async def search_companies_by_location(
        self,
        longitude: float,
        latitude: float,
        radius_km: float,
        limit: int = 10
    ) -> List[Company]:
        """Search companies within a radius of a point."""
        # Create the point in WKT format
        point = f'POINT({longitude} {latitude})'
        
        # Build query using PostGIS functions
        query = select(Company).join(Location).where(
            # ST_DWithin uses meters, so multiply km by 1000
            ST_GeomFromText(point, 4326).ST_DWithin(Location.coordinates, radius_km * 1000)
        ).options(selectinload(Company.locations)).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all() 