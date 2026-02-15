"""API Routers for Utility Service."""
from .weather_router import router as weather_router
from .gold_router import router as gold_router
from .fuel_router import router as fuel_router
from .currency_router import router as currency_router
from .pincode_router import router as pincode_router
from .ifsc_router import router as ifsc_router
from .holiday_router import router as holiday_router

__all__ = [
    "weather_router",
    "gold_router",
    "fuel_router",
    "currency_router",
    "pincode_router",
    "ifsc_router",
    "holiday_router"
]
