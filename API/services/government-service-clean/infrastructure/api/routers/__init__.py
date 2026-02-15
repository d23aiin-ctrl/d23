"""API Routers."""
from .pmkisan_router import router as pmkisan_router
from .dl_router import router as dl_router
from .vehicle_router import router as vehicle_router
from .echallan_router import router as echallan_router

__all__ = ["pmkisan_router", "dl_router", "vehicle_router", "echallan_router"]
