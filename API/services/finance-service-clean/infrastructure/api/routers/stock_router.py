"""Stock API Router."""
from fastapi import APIRouter, Depends, HTTPException
from application.dto import StockPriceRequest, StockPriceResponse
from application.dto.stock_dto import ExchangeDTO
from application.use_cases import GetStockPriceUseCase
from application.use_cases.get_stock_price import StockNotFoundError
from infrastructure.api.dependencies import get_stock_price_use_case

router = APIRouter(prefix="/stocks", tags=["Stock Market"])


@router.get("/{symbol}", response_model=StockPriceResponse)
async def get_stock_price(
    symbol: str,
    exchange: ExchangeDTO = ExchangeDTO.NSE,
    use_case: GetStockPriceUseCase = Depends(get_stock_price_use_case)
) -> StockPriceResponse:
    """Get current stock price."""
    try:
        request = StockPriceRequest(symbol=symbol, exchange=exchange)
        return await use_case.execute(request)
    except StockNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
