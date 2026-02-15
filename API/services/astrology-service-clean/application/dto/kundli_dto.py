"""
Kundli DTOs.

API request/response models for birth chart endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class KundliRequest(BaseModel):
    """Kundli generation request."""
    name: str = Field(..., min_length=1, description="Person's name")
    date: str = Field(..., description="Birth date (YYYY-MM-DD)")
    time: str = Field(..., description="Birth time (HH:MM)")
    place: str = Field(..., description="Birth place")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = Field(default="Asia/Kolkata")


class PlanetPositionDTO(BaseModel):
    """Planet position in chart."""
    planet: str
    planet_hindi: str
    sign: str
    sign_hindi: str
    house: int
    degree: float
    nakshatra: str
    nakshatra_pada: int
    is_retrograde: bool = False
    strength: str = "Normal"


class HouseDTO(BaseModel):
    """House in birth chart."""
    number: int
    sign: str
    sign_hindi: str
    planets: List[str] = []
    significance: str


class DoshaDTO(BaseModel):
    """Dosha analysis."""
    name: str
    is_present: bool
    severity: str  # None, Mild, Moderate, Severe
    description: str
    remedies: List[str] = []


class KundliResponse(BaseModel):
    """Kundli generation response."""
    success: bool = True

    # Birth details
    name: str
    birth_date: str
    birth_time: str
    birth_place: str

    # Main signs
    lagna: str
    lagna_hindi: str
    moon_sign: str
    moon_sign_hindi: str
    sun_sign: str
    nakshatra: str
    nakshatra_pada: int

    # Chart data
    planets: List[PlanetPositionDTO] = []
    houses: List[HouseDTO] = []

    # Doshas
    doshas: List[DoshaDTO] = []
    has_manglik: bool = False
    has_kaal_sarp: bool = False

    # Current dasha
    current_mahadasha: Optional[str] = None
    current_antardasha: Optional[str] = None
    mahadasha_end_date: Optional[str] = None


class MatchingRequest(BaseModel):
    """Kundli matching request."""
    person1: KundliRequest
    person2: KundliRequest


class GunaMatchDTO(BaseModel):
    """Individual guna match."""
    name: str
    name_hindi: str
    max_points: float
    obtained_points: float
    description: str


class MatchingResponse(BaseModel):
    """Kundli matching response."""
    success: bool = True

    # Scores
    total_points: float
    max_points: float = 36
    match_percentage: float

    # Verdict
    verdict: str  # Excellent, Good, Average, Below Average
    is_recommended: bool

    # Detailed matching (Ashtakoot)
    guna_details: List[GunaMatchDTO] = []

    # Dosha comparison
    manglik_status: str
    nadi_dosha: bool = False

    # Recommendations
    recommendations: List[str] = []
