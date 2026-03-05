from pydantic import BaseModel
from typing import Optional


class Employer(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    license_type: Optional[str] = None
    industry: Optional[str] = None
    active: bool = True


class TransitRoute(BaseModel):
    id: int
    route_number: int
    route_name: str
    weekday_start: Optional[str] = None  # "05:00"
    weekday_end: Optional[str] = None    # "21:00"
    saturday: bool = True
    sunday: bool = False  # CRITICAL: M Transit has NO Sunday service


class TransitStop(BaseModel):
    id: int
    route_id: int
    stop_name: str
    lat: float
    lng: float
    sequence: Optional[int] = None


class WorkforceResource(BaseModel):
    id: int
    name: str
    category: str  # career_center, training, childcare, social_service, government
    subcategory: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    phone: Optional[str] = None
    url: Optional[str] = None
    eligibility: Optional[str] = None
    services: Optional[list[str]] = None
    hours: Optional[str] = None
    notes: Optional[str] = None
