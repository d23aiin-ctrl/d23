"""Gold Price API Router."""
from fastapi import APIRouter, Depends
from application.dto import GoldPriceRequest, GoldPriceResponse
from application.use_cases import GetGoldPriceUseCase
from infrastructure.api.dependencies import get_gold_price_use_case

router = APIRouter(prefix="/gold", tags=["Gold & Silver"])


@router.get("/", response_model=GoldPriceResponse)
async def get_gold_prices(
    city: str = "Delhi",
    use_case: GetGoldPriceUseCase = Depends(get_gold_price_use_case)
) -> GoldPriceResponse:
    """Get gold and silver prices."""
    request = GoldPriceRequest(city=city)
    return await use_case.execute(request)
