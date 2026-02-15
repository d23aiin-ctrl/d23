"""Get Stock Price Use Case."""
from domain.entities import Exchange
from domain.repositories import StockRepository
from application.dto import StockPriceRequest, StockPriceResponse
from application.dto.stock_dto import StockPriceDTO, ExchangeDTO


class StockNotFoundError(Exception):
    """Raised when stock is not found."""
    pass


class GetStockPriceUseCase:
    """Use case for getting stock price."""

    def __init__(self, stock_repository: StockRepository):
        self.stock_repository = stock_repository

    def _map_exchange(self, exchange_dto: ExchangeDTO) -> Exchange:
        mapping = {
            ExchangeDTO.NSE: Exchange.NSE,
            ExchangeDTO.BSE: Exchange.BSE,
        }
        return mapping[exchange_dto]

    async def execute(self, request: StockPriceRequest) -> StockPriceResponse:
        """Get stock price for given symbol and exchange."""
        exchange = self._map_exchange(request.exchange)
        stock_price = await self.stock_repository.get_stock_price(
            symbol=request.symbol.upper(),
            exchange=exchange
        )

        if not stock_price:
            raise StockNotFoundError(f"Stock {request.symbol} not found on {request.exchange.value}")

        return StockPriceResponse(
            success=True,
            data=StockPriceDTO(
                symbol=stock_price.symbol,
                name=stock_price.name,
                exchange=stock_price.exchange.value,
                price=stock_price.price,
                change=stock_price.change,
                change_percent=stock_price.change_percent,
                open=stock_price.open,
                high=stock_price.high,
                low=stock_price.low,
                close=stock_price.close,
                volume=stock_price.volume,
                market_cap=stock_price.market_cap,
                pe_ratio=stock_price.pe_ratio,
                week_52_high=stock_price.week_52_high,
                week_52_low=stock_price.week_52_low,
                timestamp=stock_price.timestamp
            )
        )
