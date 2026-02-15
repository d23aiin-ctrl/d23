"""Application DTOs for Utility Service."""
from .weather_dto import WeatherRequest, WeatherResponse
from .gold_dto import GoldPriceRequest, GoldPriceResponse
from .fuel_dto import FuelPriceRequest, FuelPriceResponse
from .currency_dto import CurrencyRequest, CurrencyResponse, ConversionRequest
from .pincode_dto import PincodeRequest, PincodeResponse
from .ifsc_dto import IFSCRequest, IFSCResponse
from .holiday_dto import HolidayRequest, HolidayResponse

__all__ = [
    "WeatherRequest", "WeatherResponse",
    "GoldPriceRequest", "GoldPriceResponse",
    "FuelPriceRequest", "FuelPriceResponse",
    "CurrencyRequest", "CurrencyResponse", "ConversionRequest",
    "PincodeRequest", "PincodeResponse",
    "IFSCRequest", "IFSCResponse",
    "HolidayRequest", "HolidayResponse"
]
