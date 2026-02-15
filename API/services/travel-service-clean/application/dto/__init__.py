"""
Data Transfer Objects (DTOs).

These are used to transfer data between layers.
They are different from domain entities - DTOs are for
serialization/API responses, entities are for business logic.
"""

from .pnr_dto import PNRResponse, PassengerDTO
from .train_dto import TrainDTO, TrainScheduleResponse, TrainSearchResponse, StopDTO, StationDTO, LiveStatusDTO

__all__ = [
    "PNRResponse",
    "PassengerDTO",
    "TrainDTO",
    "TrainScheduleResponse",
    "TrainSearchResponse",
    "StopDTO",
    "StationDTO",
    "LiveStatusDTO",
]
