"""Dependency Injection for Finance Service API."""
from infrastructure.repositories import MockEMIRepository, MockStockRepository, MockSIPRepository
from application.use_cases import CalculateEMIUseCase, GetStockPriceUseCase, CalculateSIPUseCase


# Repository instances
_emi_repository = MockEMIRepository()
_stock_repository = MockStockRepository()
_sip_repository = MockSIPRepository()


def get_calculate_emi_use_case() -> CalculateEMIUseCase:
    """Get EMI calculation use case instance."""
    return CalculateEMIUseCase(emi_repository=_emi_repository)


def get_stock_price_use_case() -> GetStockPriceUseCase:
    """Get stock price use case instance."""
    return GetStockPriceUseCase(stock_repository=_stock_repository)


def get_calculate_sip_use_case() -> CalculateSIPUseCase:
    """Get SIP calculation use case instance."""
    return CalculateSIPUseCase(sip_repository=_sip_repository)
