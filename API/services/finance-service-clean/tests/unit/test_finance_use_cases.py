"""Unit tests for Finance Service use cases."""
import pytest
from application.use_cases import CalculateEMIUseCase, GetStockPriceUseCase, CalculateSIPUseCase
from application.use_cases.calculate_emi import EMIValidationError
from application.use_cases.get_stock_price import StockNotFoundError
from application.use_cases.calculate_sip import SIPValidationError
from application.dto import EMIRequest, StockPriceRequest, SIPRequest
from application.dto.emi_dto import LoanTypeDTO
from application.dto.stock_dto import ExchangeDTO
from infrastructure.repositories import MockEMIRepository, MockStockRepository, MockSIPRepository


class TestEMIUseCase:
    @pytest.fixture
    def use_case(self):
        return CalculateEMIUseCase(emi_repository=MockEMIRepository())

    @pytest.mark.asyncio
    async def test_calculate_home_loan_emi(self, use_case):
        request = EMIRequest(
            principal=5000000,
            annual_rate=8.5,
            tenure_months=240,
            loan_type=LoanTypeDTO.HOME
        )
        result = await use_case.execute(request)
        assert result.success
        assert result.monthly_emi > 0
        assert result.total_interest > 0
        assert result.total_amount > result.principal

    @pytest.mark.asyncio
    async def test_calculate_personal_loan_emi(self, use_case):
        request = EMIRequest(
            principal=100000,
            annual_rate=12.0,
            tenure_months=24,
            loan_type=LoanTypeDTO.PERSONAL
        )
        result = await use_case.execute(request)
        assert result.success
        assert result.loan_type == "Personal Loan"
        assert result.monthly_emi > 4000  # Roughly ₹4,700

    @pytest.mark.asyncio
    async def test_zero_interest_loan(self, use_case):
        request = EMIRequest(
            principal=120000,
            annual_rate=0,
            tenure_months=12,
            loan_type=LoanTypeDTO.PERSONAL
        )
        result = await use_case.execute(request)
        assert result.success
        assert result.monthly_emi == 10000.0  # Simple division


class TestStockUseCase:
    @pytest.fixture
    def use_case(self):
        return GetStockPriceUseCase(stock_repository=MockStockRepository())

    @pytest.mark.asyncio
    async def test_get_reliance_price(self, use_case):
        request = StockPriceRequest(symbol="RELIANCE", exchange=ExchangeDTO.NSE)
        result = await use_case.execute(request)
        assert result.success
        assert result.data.symbol == "RELIANCE"
        assert result.data.price > 0

    @pytest.mark.asyncio
    async def test_get_tcs_price(self, use_case):
        request = StockPriceRequest(symbol="TCS", exchange=ExchangeDTO.NSE)
        result = await use_case.execute(request)
        assert result.success
        assert result.data.name == "Tata Consultancy Services Ltd"

    @pytest.mark.asyncio
    async def test_stock_not_found(self, use_case):
        request = StockPriceRequest(symbol="INVALID", exchange=ExchangeDTO.NSE)
        with pytest.raises(StockNotFoundError):
            await use_case.execute(request)


class TestSIPUseCase:
    @pytest.fixture
    def use_case(self):
        return CalculateSIPUseCase(sip_repository=MockSIPRepository())

    @pytest.mark.asyncio
    async def test_calculate_sip_returns(self, use_case):
        request = SIPRequest(
            monthly_investment=10000,
            duration_years=10,
            expected_return_rate=12
        )
        result = await use_case.execute(request)
        assert result.success
        assert result.total_invested == 1200000  # 10000 * 12 * 10
        assert result.maturity_value > result.total_invested
        assert result.estimated_returns > 0

    @pytest.mark.asyncio
    async def test_sip_with_zero_return(self, use_case):
        request = SIPRequest(
            monthly_investment=5000,
            duration_years=5,
            expected_return_rate=0
        )
        result = await use_case.execute(request)
        assert result.success
        assert result.maturity_value == result.total_invested  # No returns

    @pytest.mark.asyncio
    async def test_sip_short_term(self, use_case):
        request = SIPRequest(
            monthly_investment=25000,
            duration_years=1,
            expected_return_rate=15
        )
        result = await use_case.execute(request)
        assert result.success
        assert result.total_invested == 300000  # 25000 * 12
