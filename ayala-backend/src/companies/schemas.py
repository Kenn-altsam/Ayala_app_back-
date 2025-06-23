from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, UUID4, EmailStr, HttpUrl, constr, Field, field_validator, model_validator
from annotated_types import MinLen, MaxLen
from typing_extensions import Annotated


class LocationBase(BaseModel):
    region: str
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    coordinates: Optional[str] = None  # WKT format: 'POINT(longitude latitude)'
    is_primary: bool = False


class LocationCreate(LocationBase):
    pass


class LocationUpdate(LocationBase):
    region: Optional[str] = None


class Location(LocationBase):
    id: UUID
    company_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyBase(BaseModel):
    name: str
    bin: Optional[Annotated[str, MinLen(12), MaxLen(12)]] = None
    registration_date: Optional[date] = None
    status: Optional[str] = None
    company_type: Optional[str] = None
    employee_count: Optional[int] = None
    revenue_range: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[HttpUrl] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    social_media: dict = Field(default_factory=dict)
    annual_tax_paid: Optional[float] = None
    tax_reporting_year: Optional[int] = None
    tax_compliance_score: Optional[float] = None
    last_tax_update: Optional[date] = None
    past_donations: Optional[str] = None
    sponsorship_interests: Optional[str] = None

    @field_validator('bin')
    @classmethod
    def validate_bin(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.isdigit():
            raise ValueError('BIN must contain only digits')
        return v


class CompanyCreate(CompanyBase):
    locations: Optional[List[LocationCreate]] = None


class CompanyUpdate(CompanyBase):
    name: Optional[str] = None
    locations: Optional[List[LocationCreate]] = None


class Company(CompanyBase):
    id: UUID
    has_social_media: bool
    has_website: bool
    has_contact_info: bool
    created_at: datetime
    updated_at: datetime
    locations: List[Location] = []

    class Config:
        from_attributes = True


class CompanyResponse(BaseModel):
    status: str = "success"
    data: Company
    message: str = "Company retrieved successfully"


class CompanyListResponse(BaseModel):
    status: str = "success"
    data: List[Company]
    message: str = "Companies retrieved successfully"
    metadata: dict = Field(default_factory=dict)


class CompanyDetailResponse(CompanyResponse):
    past_donations: Optional[str] = None


class CompanySuggestion(BaseModel):
    company: CompanyResponse
    match_score: float
    match_reason: str
    potential_sponsorship_areas: List[str]

    class Config:
        from_attributes = True


class CompanySearchFilters(BaseModel):
    query: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = None
    industry: Optional[str] = None
    min_employees: Optional[int] = None
    max_employees: Optional[int] = None 