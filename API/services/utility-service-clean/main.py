"""Utility Service - Clean Architecture Implementation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from infrastructure.api.routers import (
    weather_router,
    gold_router,
    fuel_router,
    currency_router,
    pincode_router,
    ifsc_router,
    holiday_router
)

app = FastAPI(
    title="Utility Service",
    description="Utility services for weather, news, prices, and lookups with Clean Architecture",
    version="1.0.0"
)

app.include_router(weather_router)
app.include_router(gold_router)
app.include_router(fuel_router)
app.include_router(currency_router)
app.include_router(pincode_router)
app.include_router(ifsc_router)
app.include_router(holiday_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "utility-service"}


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "utility-service",
        "version": "1.0.0",
        "endpoints": {
            "weather": "GET /weather/{city}",
            "gold_price": "GET /gold",
            "fuel_price": "GET /fuel/{city}",
            "currency": "GET /currency/rate",
            "pincode": "GET /pincode/{pincode}",
            "ifsc": "GET /ifsc/{code}",
            "holidays": "GET /holidays",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
