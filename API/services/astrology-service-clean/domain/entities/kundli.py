"""
Kundli (Birth Chart) Domain Entity.

Represents a person's astrological birth chart.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

from .zodiac import ZodiacSign, Planet, Nakshatra


@dataclass(frozen=True)
class BirthDetails:
    """Birth details for kundli calculation."""
    name: str
    date_time: datetime
    place: str
    latitude: float
    longitude: float
    timezone: str = "Asia/Kolkata"

    def validate(self) -> List[str]:
        errors = []
        if not self.name:
            errors.append("Name is required")
        if not -90 <= self.latitude <= 90:
            errors.append("Invalid latitude")
        if not -180 <= self.longitude <= 180:
            errors.append("Invalid longitude")
        return errors


@dataclass
class PlanetPosition:
    """Position of a planet in the chart."""
    planet: Planet
    sign: ZodiacSign
    house: int  # 1-12
    degree: float  # 0-30 within sign
    nakshatra: str
    nakshatra_pada: int  # 1-4
    is_retrograde: bool = False
    is_combust: bool = False  # Too close to Sun
    is_exalted: bool = False
    is_debilitated: bool = False

    @property
    def absolute_degree(self) -> float:
        """Get absolute degree (0-360)."""
        return ((self.sign.number - 1) * 30) + self.degree

    @property
    def strength(self) -> str:
        """Get planet strength."""
        if self.is_exalted:
            return "Exalted"
        elif self.is_debilitated:
            return "Debilitated"
        elif self.is_combust:
            return "Combust"
        elif self.is_retrograde:
            return "Retrograde"
        return "Normal"


@dataclass
class House:
    """A house in the birth chart."""
    number: int  # 1-12
    sign: ZodiacSign
    degree: float  # Starting degree
    planets: List[Planet] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Check if house has no planets."""
        return len(self.planets) == 0

    @property
    def significance(self) -> str:
        """Get house significance."""
        significances = {
            1: "Self, Personality",
            2: "Wealth, Family",
            3: "Siblings, Courage",
            4: "Mother, Home",
            5: "Children, Education",
            6: "Enemies, Health",
            7: "Marriage, Partnership",
            8: "Longevity, Secrets",
            9: "Fortune, Father",
            10: "Career, Status",
            11: "Gains, Friends",
            12: "Losses, Spirituality"
        }
        return significances.get(self.number, "")


class DoshaType(Enum):
    """Types of doshas (afflictions)."""
    MANGLIK = "Manglik Dosha"
    KAAL_SARP = "Kaal Sarp Dosha"
    SADE_SATI = "Sade Sati"
    PITRA = "Pitra Dosha"
    NADI = "Nadi Dosha"


@dataclass
class Dosha:
    """A dosha (affliction) in the chart."""
    dosha_type: DoshaType
    is_present: bool
    severity: str  # "None", "Mild", "Moderate", "Severe"
    description: str
    remedies: List[str] = field(default_factory=list)


@dataclass
class Kundli:
    """
    Complete birth chart (Kundli/Janam Patri).

    Contains all astrological information for a person.
    """
    birth_details: BirthDetails

    # Ascendant (Lagna)
    lagna: ZodiacSign
    lagna_degree: float
    lagna_nakshatra: str

    # Moon sign (Rashi)
    moon_sign: ZodiacSign
    moon_nakshatra: str
    moon_nakshatra_pada: int

    # Sun sign
    sun_sign: ZodiacSign

    # Planet positions
    planets: List[PlanetPosition] = field(default_factory=list)

    # Houses
    houses: List[House] = field(default_factory=list)

    # Doshas
    doshas: List[Dosha] = field(default_factory=list)

    # Dasha (planetary period)
    current_mahadasha: Optional[str] = None
    current_antardasha: Optional[str] = None
    mahadasha_end_date: Optional[datetime] = None

    @property
    def has_manglik_dosha(self) -> bool:
        """Check if Manglik dosha is present."""
        return any(d.dosha_type == DoshaType.MANGLIK and d.is_present
                   for d in self.doshas)

    @property
    def has_kaal_sarp_dosha(self) -> bool:
        """Check if Kaal Sarp dosha is present."""
        return any(d.dosha_type == DoshaType.KAAL_SARP and d.is_present
                   for d in self.doshas)

    def get_planet_position(self, planet: Planet) -> Optional[PlanetPosition]:
        """Get position of a specific planet."""
        for pos in self.planets:
            if pos.planet == planet:
                return pos
        return None

    def get_house(self, number: int) -> Optional[House]:
        """Get a specific house."""
        for house in self.houses:
            if house.number == number:
                return house
        return None

    def validate(self) -> List[str]:
        """Validate kundli data."""
        errors = []
        errors.extend(self.birth_details.validate())

        if not self.planets:
            errors.append("Planet positions required")

        if len(self.houses) != 12:
            errors.append("Must have exactly 12 houses")

        return errors
