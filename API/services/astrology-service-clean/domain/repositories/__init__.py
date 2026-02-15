"""
Domain Repository Interfaces.

Abstract interfaces that define data access contracts.
Infrastructure layer provides implementations.
"""

from .horoscope_repository import HoroscopeRepository
from .kundli_repository import KundliRepository
from .panchang_repository import PanchangRepository

__all__ = [
    "HoroscopeRepository",
    "KundliRepository",
    "PanchangRepository",
]
