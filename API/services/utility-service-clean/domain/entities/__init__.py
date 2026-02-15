"""Domain Entities for Utility Service."""
from .weather import Weather, WeatherForecast
from .gold import GoldPrice, MetalType
from .fuel import FuelPrice, FuelType
from .currency import CurrencyRate, CurrencyPair
from .pincode import PincodeInfo
from .ifsc import IFSCInfo
from .holiday import Holiday, HolidayType

__all__ = [
    "Weather", "WeatherForecast",
    "GoldPrice", "MetalType",
    "FuelPrice", "FuelType",
    "CurrencyRate", "CurrencyPair",
    "PincodeInfo",
    "IFSCInfo",
    "Holiday", "HolidayType"
]
