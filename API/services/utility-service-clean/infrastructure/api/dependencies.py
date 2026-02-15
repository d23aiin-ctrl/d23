"""Dependency Injection for Utility Service API."""
from infrastructure.repositories import (
    MockWeatherRepository,
    MockGoldRepository,
    MockFuelRepository,
    MockCurrencyRepository,
    MockPincodeRepository,
    MockIFSCRepository,
    MockHolidayRepository
)
from application.use_cases import (
    GetWeatherUseCase,
    GetGoldPriceUseCase,
    GetFuelPriceUseCase,
    GetCurrencyRateUseCase,
    GetPincodeInfoUseCase,
    GetIFSCInfoUseCase,
    GetHolidaysUseCase
)


# Repository instances
_weather_repository = MockWeatherRepository()
_gold_repository = MockGoldRepository()
_fuel_repository = MockFuelRepository()
_currency_repository = MockCurrencyRepository()
_pincode_repository = MockPincodeRepository()
_ifsc_repository = MockIFSCRepository()
_holiday_repository = MockHolidayRepository()


def get_weather_use_case() -> GetWeatherUseCase:
    return GetWeatherUseCase(weather_repository=_weather_repository)


def get_gold_price_use_case() -> GetGoldPriceUseCase:
    return GetGoldPriceUseCase(gold_repository=_gold_repository)


def get_fuel_price_use_case() -> GetFuelPriceUseCase:
    return GetFuelPriceUseCase(fuel_repository=_fuel_repository)


def get_currency_rate_use_case() -> GetCurrencyRateUseCase:
    return GetCurrencyRateUseCase(currency_repository=_currency_repository)


def get_pincode_info_use_case() -> GetPincodeInfoUseCase:
    return GetPincodeInfoUseCase(pincode_repository=_pincode_repository)


def get_ifsc_info_use_case() -> GetIFSCInfoUseCase:
    return GetIFSCInfoUseCase(ifsc_repository=_ifsc_repository)


def get_holidays_use_case() -> GetHolidaysUseCase:
    return GetHolidaysUseCase(holiday_repository=_holiday_repository)
