"""
Application Use Cases.

Each use case represents a single business operation.
They orchestrate domain entities and repositories.

Use cases are:
- Single responsibility (one operation)
- Independent of frameworks
- Testable in isolation
"""

from .get_pnr_status import GetPNRStatusUseCase
from .get_train_schedule import GetTrainScheduleUseCase
from .search_trains import SearchTrainsUseCase
from .get_live_status import GetLiveStatusUseCase

__all__ = [
    "GetPNRStatusUseCase",
    "GetTrainScheduleUseCase",
    "SearchTrainsUseCase",
    "GetLiveStatusUseCase",
]
