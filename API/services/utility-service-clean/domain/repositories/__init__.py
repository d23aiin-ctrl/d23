"""Domain Repository Interfaces for Utility Service."""
from .weather_repository import WeatherRepository
from .gold_repository import GoldRepository
from .fuel_repository import FuelRepository
from .currency_repository import CurrencyRepository
from .pincode_repository import PincodeRepository
from .ifsc_repository import IFSCRepository
from .holiday_repository import HolidayRepository

__all__ = [
    "WeatherRepository",
    "GoldRepository",
    "FuelRepository",
    "CurrencyRepository",
    "PincodeRepository",
    "IFSCRepository",
    "HolidayRepository"
]
