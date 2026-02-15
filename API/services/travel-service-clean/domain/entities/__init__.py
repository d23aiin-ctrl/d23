"""
Domain Entities.

Pure business objects with no external dependencies.
These represent the core business concepts.
"""

from .pnr import PNR, Passenger, BookingStatus
from .train import Train, Station, TrainSchedule, StationStop, TrainType

__all__ = [
    "PNR",
    "Passenger",
    "BookingStatus",
    "Train",
    "Station",
    "TrainSchedule",
    "StationStop",
    "TrainType",
]
