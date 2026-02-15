"""
Train Domain Entities.

Represents trains, stations, and schedules.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import time, timedelta
from enum import Enum


class TrainType(Enum):
    """Train type classification."""
    RAJDHANI = "Rajdhani"
    SHATABDI = "Shatabdi"
    DURONTO = "Duronto"
    SUPERFAST = "Superfast"
    EXPRESS = "Express"
    PASSENGER = "Passenger"
    LOCAL = "Local"


@dataclass(frozen=True)
class Station:
    """
    Railway station value object.

    Immutable - stations don't change.
    """
    code: str
    name: str
    zone: Optional[str] = None
    state: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


@dataclass
class StationStop:
    """A station stop in a train schedule."""
    station: Station
    arrival: Optional[time]
    departure: Optional[time]
    day: int  # Day of journey (1, 2, 3...)
    distance_km: int
    halt_minutes: Optional[int] = None
    platform: Optional[str] = None

    @property
    def is_source(self) -> bool:
        """Check if this is the source station."""
        return self.arrival is None

    @property
    def is_destination(self) -> bool:
        """Check if this is the destination station."""
        return self.departure is None


@dataclass
class TrainSchedule:
    """Complete train schedule with all stops."""
    train: "Train"
    stops: List[StationStop] = field(default_factory=list)

    @property
    def source(self) -> Optional[StationStop]:
        """Get source station stop."""
        return self.stops[0] if self.stops else None

    @property
    def destination(self) -> Optional[StationStop]:
        """Get destination station stop."""
        return self.stops[-1] if self.stops else None

    @property
    def total_stops(self) -> int:
        """Total number of stops including source and destination."""
        return len(self.stops)

    @property
    def intermediate_stops(self) -> int:
        """Number of intermediate stops."""
        return max(0, len(self.stops) - 2)

    def get_stop(self, station_code: str) -> Optional[StationStop]:
        """Get stop by station code."""
        for stop in self.stops:
            if stop.station.code == station_code:
                return stop
        return None

    def stops_between(self, from_code: str, to_code: str) -> List[StationStop]:
        """Get stops between two stations."""
        from_idx = None
        to_idx = None

        for i, stop in enumerate(self.stops):
            if stop.station.code == from_code:
                from_idx = i
            if stop.station.code == to_code:
                to_idx = i

        if from_idx is not None and to_idx is not None:
            return self.stops[from_idx:to_idx + 1]
        return []


@dataclass
class Train:
    """
    Train domain entity.

    Represents a train with its properties and running days.
    """
    number: str
    name: str
    train_type: TrainType
    source: Station
    destination: Station
    departure_time: time
    arrival_time: time
    duration: timedelta
    distance_km: int
    runs_on: List[str] = field(default_factory=list)  # ["Mon", "Tue", ...]
    classes: List[str] = field(default_factory=list)  # ["1A", "2A", "3A", "SL"]
    has_pantry: bool = False

    @property
    def is_daily(self) -> bool:
        """Check if train runs daily."""
        return len(self.runs_on) == 7

    @property
    def average_speed_kmph(self) -> float:
        """Calculate average speed."""
        hours = self.duration.total_seconds() / 3600
        return self.distance_km / hours if hours > 0 else 0

    def runs_on_day(self, day: str) -> bool:
        """Check if train runs on a specific day."""
        return day in self.runs_on

    def has_class(self, travel_class: str) -> bool:
        """Check if train has a specific class."""
        return travel_class in self.classes

    def validate(self) -> List[str]:
        """Validate train data."""
        errors = []
        if len(self.number) != 5:
            errors.append("Train number must be 5 digits")
        if not self.number.isdigit():
            errors.append("Train number must contain only digits")
        if not self.runs_on:
            errors.append("Train must run on at least one day")
        return errors
