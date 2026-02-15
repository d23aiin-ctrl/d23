"""
API Routers.

HTTP endpoints organized by feature.
"""

from .horoscope_router import router as horoscope_router
from .kundli_router import router as kundli_router
from .panchang_router import router as panchang_router

__all__ = [
    "horoscope_router",
    "kundli_router",
    "panchang_router",
]
