"""Government Service - Main Entry Point."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.api.config import get_settings
from infrastructure.api.routers import pmkisan_router, dl_router, vehicle_router, echallan_router

settings = get_settings()

app = FastAPI(
    title="Government Service",
    description="Government services API: PM-KISAN, DL, Vehicle RC, E-Challan",
    version=settings.SERVICE_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pmkisan_router)
app.include_router(dl_router)
app.include_router(vehicle_router)
app.include_router(echallan_router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.SERVICE_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
