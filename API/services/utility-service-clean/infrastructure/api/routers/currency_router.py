"""Currency API Router."""
from fastapi import APIRouter, Depends, HTTPException
from application.dto import CurrencyRequest, CurrencyResponse
from application.dto.currency_dto import ConversionRequest, ConversionResponse
from application.use_cases import GetCurrencyRateUseCase
from application.use_cases.get_currency_rate import CurrencyNotFoundError
from infrastructure.api.dependencies import get_currency_rate_use_case

router = APIRouter(prefix="/currency", tags=["Currency"])


@router.get("/rate", response_model=CurrencyResponse)
async def get_currency_rate(
    base: str = "USD",
    quote: str = "INR",
    use_case: GetCurrencyRateUseCase = Depends(get_currency_rate_use_case)
) -> CurrencyResponse:
    """Get currency exchange rate."""
    try:
        request = CurrencyRequest(base=base, quote=quote)
        return await use_case.execute(request)
    except CurrencyNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/convert", response_model=ConversionResponse)
async def convert_currency(
    request: ConversionRequest,
    use_case: GetCurrencyRateUseCase = Depends(get_currency_rate_use_case)
) -> ConversionResponse:
    """Convert currency amount."""
    try:
        return await use_case.convert(request)
    except CurrencyNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
