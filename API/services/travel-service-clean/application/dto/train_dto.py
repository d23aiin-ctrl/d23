"""
Train Data Transfer Objects.

Pydantic models for train-related API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class StationDTO(BaseModel):
    """Station data for API response."""
    code: str
    name: str


class StopDTO(BaseModel):
    """Station stop in schedule."""
    station_code: str
    station_name: str
    arrival: Optional[str]
    departure: Optional[str]
    day: int
    distance_km: int
    halt_minutes: Optional[int]
    platform: Optional[str]


class TrainDTO(BaseModel):
    """Train data for API response."""
    train_number: str
    train_name: str
    train_type: str
    source: str
    source_name: str
    destination: str
    destination_name: str
    departure: str
    arrival: str
    duration: str
    distance_km: int
    runs_on: List[str]
    classes: List[str]
    is_daily: bool


class TrainScheduleResponse(BaseModel):
    """Train schedule API response."""
    success: bool = True
    train: TrainDTO
    total_stops: int
    stops: List[StopDTO]


class TrainSearchResponse(BaseModel):
    """Train search API response."""
    success: bool = True
    from_station: str
    from_station_name: str
    to_station: str
    to_station_name: str
    date: Optional[str]
    trains_found: int
    trains: List[TrainDTO]


class LiveStatusDTO(BaseModel):
    """Live train status response."""
    success: bool = True
    train_number: str
    train_name: str
    current_station: str
    current_station_name: str
    delay_minutes: int
    last_updated: str
    stations: List[dict]
