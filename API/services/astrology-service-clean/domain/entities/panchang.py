"""
Panchang (Hindu Calendar) Domain Entity.

Represents daily Hindu calendar with Tithi, Nakshatra, Yoga, Karana.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date, time
from enum import Enum


class TithiPaksha(Enum):
    """Fortnight phase."""
    SHUKLA = "Shukla"  # Bright/Waxing
    KRISHNA = "Krishna"  # Dark/Waning


@dataclass(frozen=True)
class Tithi:
    """
    Lunar day (Tithi).

    15 tithis in each paksha (fortnight).
    """
    number: int  # 1-15 (or 30 for Amavasya/Purnima)
    name: str
    hindi_name: str
    paksha: TithiPaksha
    end_time: time
    is_auspicious: bool = True

    def validate(self) -> List[str]:
        errors = []
        if not 1 <= self.number <= 15:
            errors.append("Tithi number must be 1-15")
        return errors


@dataclass(frozen=True)
class Yoga:
    """
    Yoga - combination of Sun and Moon longitude.

    27 yogas, each has specific characteristics.
    """
    number: int  # 1-27
    name: str
    hindi_name: str
    end_time: time
    is_auspicious: bool = True

    def validate(self) -> List[str]:
        errors = []
        if not 1 <= self.number <= 27:
            errors.append("Yoga number must be 1-27")
        return errors


@dataclass(frozen=True)
class Karana:
    """
    Karana - half of a tithi.

    11 karanas, 7 recurring + 4 fixed.
    """
    number: int  # 1-11
    name: str
    hindi_name: str
    end_time: time
    is_auspicious: bool = True


@dataclass
class Muhurta:
    """Auspicious time period."""
    name: str
    start_time: time
    end_time: time
    is_auspicious: bool
    suitable_for: List[str] = field(default_factory=list)


@dataclass
class Panchang:
    """
    Complete Panchang (Hindu Calendar) for a day.

    Contains all five limbs:
    - Tithi (lunar day)
    - Nakshatra (lunar mansion)
    - Yoga (sun-moon combination)
    - Karana (half-tithi)
    - Vara (weekday)
    """
    date: date

    # Location
    city: str
    latitude: float
    longitude: float

    # Five limbs (Panch-Ang)
    tithi: Tithi
    nakshatra_name: str
    nakshatra_hindi: str
    nakshatra_end_time: time
    yoga: Yoga
    karana: Karana
    vara: str  # Weekday
    vara_hindi: str

    # Sun/Moon times
    sunrise: time
    sunset: time

    # Hindu month
    hindu_month: str
    hindu_month_hindi: str
    hindu_year: int  # Vikram Samvat

    # Optional times
    moonrise: Optional[time] = None
    moonset: Optional[time] = None

    # Auspicious periods
    abhijit_muhurta: Optional[Muhurta] = None
    rahukaal: Optional[Muhurta] = None  # Inauspicious
    yamaganda: Optional[Muhurta] = None  # Inauspicious
    gulika: Optional[Muhurta] = None  # Inauspicious

    # Special days
    is_ekadashi: bool = False
    is_pradosh: bool = False
    is_amavasya: bool = False
    is_purnima: bool = False
    festivals: List[str] = field(default_factory=list)

    @property
    def is_auspicious_day(self) -> bool:
        """Check if overall day is auspicious."""
        return (self.tithi.is_auspicious and
                self.yoga.is_auspicious and
                self.karana.is_auspicious)

    @property
    def day_length_hours(self) -> float:
        """Calculate day length in hours."""
        sunrise_mins = self.sunrise.hour * 60 + self.sunrise.minute
        sunset_mins = self.sunset.hour * 60 + self.sunset.minute
        return (sunset_mins - sunrise_mins) / 60

    def validate(self) -> List[str]:
        """Validate panchang data."""
        errors = []
        errors.extend(self.tithi.validate())
        errors.extend(self.yoga.validate())
        return errors
