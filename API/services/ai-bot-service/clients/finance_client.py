"""Client for Finance Service (port 8007)."""

from clients.base_client import BaseServiceClient


class FinanceClient(BaseServiceClient):
    """Async client for the Finance microservice."""

    def __init__(self, base_url: str = "http://localhost:8007", **kwargs):
        super().__init__(base_url, service_name="Finance Service", **kwargs)

    async def calculate_emi(
        self,
        principal: float,
        annual_rate: float,
        tenure_months: int,
        loan_type: str = "personal",
    ) -> dict:
        return await self.post("/emi/calculate", json={
            "principal": principal,
            "annual_rate": annual_rate,
            "tenure_months": tenure_months,
            "loan_type": loan_type,
        })

    async def calculate_sip(
        self,
        monthly_investment: float,
        duration_years: int,
        expected_return_rate: float,
    ) -> dict:
        return await self.post("/sip/calculate", json={
            "monthly_investment": monthly_investment,
            "duration_years": duration_years,
            "expected_return_rate": expected_return_rate,
        })

    async def get_stock_price(self, symbol: str, exchange: str = "NSE") -> dict:
        return await self.get(f"/stocks/{symbol}", params={"exchange": exchange})
