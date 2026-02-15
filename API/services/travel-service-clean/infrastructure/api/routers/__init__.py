"""
FastAPI Routers.

HTTP layer - handles requests/responses.
Routers are thin - they just call use cases.
"""

from .pnr_router import router as pnr_router
from .train_router import router as train_router

__all__ = ["pnr_router", "train_router"]
