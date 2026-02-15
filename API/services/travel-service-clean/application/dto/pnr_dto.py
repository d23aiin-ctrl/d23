"""
PNR Data Transfer Objects.

Pydantic models for API request/response serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class PassengerDTO(BaseModel):
    """Passenger data for API response."""
    number: int
    booking_status: str
    current_status: str
    coach: Optional[str] = None
    berth: Optional[int] = None
    berth_type: Optional[str] = None
    is_confirmed: bool

    class Config:
        from_attributes = True


class PNRResponse(BaseModel):
    """PNR status API response."""
    success: bool = True
    pnr: str = Field(..., description="10-digit PNR number")
    train_number: str
    train_name: str
    journey_date: str
    from_station: str
    from_station_name: str
    to_station: str
    to_station_name: str
    travel_class: str
    chart_prepared: bool
    passengers: List[PassengerDTO]
    total_passengers: int
    confirmed_passengers: int
    all_confirmed: bool
    status_summary: str
    message: Optional[str] = None

    class Config:
        from_attributes = True


class PNRNotFoundResponse(BaseModel):
    """Response when PNR is not found."""
    success: bool = False
    pnr: str
    error: str = "PNR not found"
    message: str = "Please check the PNR number and try again"
