"""API Routers for Finance Service."""
from .emi_router import router as emi_router
from .stock_router import router as stock_router
from .sip_router import router as sip_router

__all__ = ["emi_router", "stock_router", "sip_router"]
