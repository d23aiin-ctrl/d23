"""Unit tests for Utility Service use cases."""
import pytest
from application.use_cases import (
    GetWeatherUseCase,
    GetGoldPriceUseCase,
    GetFuelPriceUseCase,
    GetCurrencyRateUseCase,
    GetPincodeInfoUseCase,
    GetIFSCInfoUseCase,
    GetHolidaysUseCase
)
from application.use_cases.get_weather import WeatherNotFoundError
from application.use_cases.get_fuel_price import FuelPriceNotFoundError
from application.use_cases.get_currency_rate import CurrencyNotFoundError
from application.use_cases.get_pincode_info import PincodeNotFoundError
from application.use_cases.get_ifsc_info import IFSCNotFoundError
from application.dto import (
    WeatherRequest,
    GoldPriceRequest,
    FuelPriceRequest,
    CurrencyRequest,
    PincodeRequest,
    IFSCRequest,
    HolidayRequest
)
from application.dto.currency_dto import ConversionRequest
from infrastructure.repositories import (
    MockWeatherRepository,
    MockGoldRepository,
    MockFuelRepository,
    MockCurrencyRepository,
    MockPincodeRepository,
    MockIFSCRepository,
    MockHolidayRepository
)


class TestWeatherUseCase:
    @pytest.fixture
    def use_case(self):
        return GetWeatherUseCase(weather_repository=MockWeatherRepository())

    @pytest.mark.asyncio
    async def test_get_delhi_weather(self, use_case):
        request = WeatherRequest(city="Delhi")
        result = await use_case.execute(request)
        assert result.success
        assert result.data.city == "Delhi"
        assert result.data.temperature > 0

    @pytest.mark.asyncio
    async def test_weather_not_found(self, use_case):
        request = WeatherRequest(city="UnknownCity")
        with pytest.raises(WeatherNotFoundError):
            await use_case.execute(request)


class TestGoldPriceUseCase:
    @pytest.fixture
    def use_case(self):
        return GetGoldPriceUseCase(gold_repository=MockGoldRepository())

    @pytest.mark.asyncio
    async def test_get_gold_prices(self, use_case):
        request = GoldPriceRequest(city="Delhi")
        result = await use_case.execute(request)
        assert result.success
        assert len(result.data) >= 2  # At least gold and silver
        assert any(p.metal_type == "gold_24k" for p in result.data)


class TestFuelPriceUseCase:
    @pytest.fixture
    def use_case(self):
        return GetFuelPriceUseCase(fuel_repository=MockFuelRepository())

    @pytest.mark.asyncio
    async def test_get_delhi_fuel_prices(self, use_case):
        request = FuelPriceRequest(city="Delhi")
        result = await use_case.execute(request)
        assert result.success
        assert len(result.data) == 3  # Petrol, Diesel, CNG
        petrol = next(p for p in result.data if p.fuel_type == "petrol")
        assert petrol.price > 0

    @pytest.mark.asyncio
    async def test_fuel_price_not_found(self, use_case):
        request = FuelPriceRequest(city="UnknownCity")
        with pytest.raises(FuelPriceNotFoundError):
            await use_case.execute(request)


class TestCurrencyRateUseCase:
    @pytest.fixture
    def use_case(self):
        return GetCurrencyRateUseCase(currency_repository=MockCurrencyRepository())

    @pytest.mark.asyncio
    async def test_get_usd_to_inr(self, use_case):
        request = CurrencyRequest(base="USD", quote="INR")
        result = await use_case.execute(request)
        assert result.success
        assert result.data.rate > 80  # USD to INR is typically > 80

    @pytest.mark.asyncio
    async def test_convert_currency(self, use_case):
        request = ConversionRequest(amount=100, from_currency="USD", to_currency="INR")
        result = await use_case.convert(request)
        assert result.success
        assert result.converted_amount > 8000  # 100 USD > 8000 INR

    @pytest.mark.asyncio
    async def test_currency_not_found(self, use_case):
        request = CurrencyRequest(base="ABC", quote="XYZ")
        with pytest.raises(CurrencyNotFoundError):
            await use_case.execute(request)


class TestPincodeInfoUseCase:
    @pytest.fixture
    def use_case(self):
        return GetPincodeInfoUseCase(pincode_repository=MockPincodeRepository())

    @pytest.mark.asyncio
    async def test_get_delhi_pincode(self, use_case):
        request = PincodeRequest(pincode="110001")
        result = await use_case.execute(request)
        assert result.success
        assert len(result.data) >= 1
        assert result.data[0].state == "Delhi"

    @pytest.mark.asyncio
    async def test_pincode_not_found(self, use_case):
        request = PincodeRequest(pincode="999999")
        with pytest.raises(PincodeNotFoundError):
            await use_case.execute(request)


class TestIFSCInfoUseCase:
    @pytest.fixture
    def use_case(self):
        return GetIFSCInfoUseCase(ifsc_repository=MockIFSCRepository())

    @pytest.mark.asyncio
    async def test_get_sbi_ifsc(self, use_case):
        request = IFSCRequest(ifsc="SBIN0001234")
        result = await use_case.execute(request)
        assert result.success
        assert result.data.bank_name == "State Bank of India"
        assert result.data.neft
        assert result.data.upi

    @pytest.mark.asyncio
    async def test_ifsc_not_found(self, use_case):
        request = IFSCRequest(ifsc="XXXX0000000")
        with pytest.raises(IFSCNotFoundError):
            await use_case.execute(request)


class TestHolidaysUseCase:
    @pytest.fixture
    def use_case(self):
        return GetHolidaysUseCase(holiday_repository=MockHolidayRepository())

    @pytest.mark.asyncio
    async def test_get_national_holidays(self, use_case):
        from application.dto.holiday_dto import HolidayTypeDTO
        request = HolidayRequest(year=2024, holiday_type=HolidayTypeDTO.NATIONAL)
        result = await use_case.execute(request)
        assert result.success
        assert len(result.data) >= 3  # At least Republic Day, Independence Day, Gandhi Jayanti

    @pytest.mark.asyncio
    async def test_get_all_holidays_2024(self, use_case):
        request = HolidayRequest(year=2024)
        result = await use_case.execute(request)
        assert result.success
        assert len(result.data) >= 5  # Multiple holidays
