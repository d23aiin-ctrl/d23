"""Mock Stock Repository Implementation."""
from typing import List, Optional
from datetime import datetime
from domain.entities import Stock, StockPrice, Exchange
from domain.repositories import StockRepository


class MockStockRepository(StockRepository):
    """Mock implementation of stock repository for testing."""

    def __init__(self):
        self._stocks = {
            ("RELIANCE", Exchange.NSE): StockPrice(
                symbol="RELIANCE",
                name="Reliance Industries Ltd",
                exchange=Exchange.NSE,
                price=2450.75,
                change=25.50,
                change_percent=1.05,
                open=2420.00,
                high=2465.00,
                low=2415.00,
                close=2425.25,
                volume=5234567,
                market_cap=16500000000000,
                pe_ratio=28.5,
                week_52_high=2750.00,
                week_52_low=2100.00,
                timestamp=datetime.now()
            ),
            ("TCS", Exchange.NSE): StockPrice(
                symbol="TCS",
                name="Tata Consultancy Services Ltd",
                exchange=Exchange.NSE,
                price=3650.00,
                change=-15.25,
                change_percent=-0.42,
                open=3670.00,
                high=3680.00,
                low=3640.00,
                close=3665.25,
                volume=1234567,
                market_cap=13500000000000,
                pe_ratio=32.1,
                week_52_high=3900.00,
                week_52_low=3200.00,
                timestamp=datetime.now()
            ),
            ("INFY", Exchange.NSE): StockPrice(
                symbol="INFY",
                name="Infosys Ltd",
                exchange=Exchange.NSE,
                price=1520.50,
                change=12.75,
                change_percent=0.85,
                open=1505.00,
                high=1530.00,
                low=1500.00,
                close=1507.75,
                volume=3456789,
                market_cap=6300000000000,
                pe_ratio=25.8,
                week_52_high=1700.00,
                week_52_low=1350.00,
                timestamp=datetime.now()
            ),
        }

        self._stock_list = [
            Stock(symbol="RELIANCE", name="Reliance Industries Ltd", sector="Energy", exchange=Exchange.NSE),
            Stock(symbol="TCS", name="Tata Consultancy Services Ltd", sector="IT", exchange=Exchange.NSE),
            Stock(symbol="INFY", name="Infosys Ltd", sector="IT", exchange=Exchange.NSE),
            Stock(symbol="HDFCBANK", name="HDFC Bank Ltd", sector="Banking", exchange=Exchange.NSE),
            Stock(symbol="ICICIBANK", name="ICICI Bank Ltd", sector="Banking", exchange=Exchange.NSE),
        ]

    async def get_stock_price(self, symbol: str, exchange: Exchange) -> Optional[StockPrice]:
        return self._stocks.get((symbol, exchange))

    async def search_stocks(self, query: str) -> List[Stock]:
        query_lower = query.lower()
        return [
            stock for stock in self._stock_list
            if query_lower in stock.symbol.lower() or query_lower in stock.name.lower()
        ]

    async def get_top_gainers(self, exchange: Exchange, limit: int = 10) -> List[StockPrice]:
        stocks = [s for s in self._stocks.values() if s.exchange == exchange and s.change_percent > 0]
        return sorted(stocks, key=lambda x: x.change_percent, reverse=True)[:limit]

    async def get_top_losers(self, exchange: Exchange, limit: int = 10) -> List[StockPrice]:
        stocks = [s for s in self._stocks.values() if s.exchange == exchange and s.change_percent < 0]
        return sorted(stocks, key=lambda x: x.change_percent)[:limit]
