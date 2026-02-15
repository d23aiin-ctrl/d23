"""Finance Service - Clean Architecture Implementation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from infrastructure.api.routers import emi_router, stock_router, sip_router

app = FastAPI(
    title="Finance Service",
    description="Financial calculators and stock market data with Clean Architecture",
    version="1.0.0"
)

app.include_router(emi_router)
app.include_router(stock_router)
app.include_router(sip_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "finance-service"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
