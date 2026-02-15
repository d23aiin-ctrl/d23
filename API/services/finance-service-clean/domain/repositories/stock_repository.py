"""Stock Repository Interface."""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import Stock, StockPrice, Exchange


class StockRepository(ABC):
    """Abstract repository for stock data."""

    @abstractmethod
    async def get_stock_price(self, symbol: str, exchange: Exchange) -> Optional[StockPrice]:
        """Get current stock price."""
        pass

    @abstractmethod
    async def search_stocks(self, query: str) -> List[Stock]:
        """Search stocks by name or symbol."""
        pass

    @abstractmethod
    async def get_top_gainers(self, exchange: Exchange, limit: int = 10) -> List[StockPrice]:
        """Get top gaining stocks."""
        pass

    @abstractmethod
    async def get_top_losers(self, exchange: Exchange, limit: int = 10) -> List[StockPrice]:
        """Get top losing stocks."""
        pass
