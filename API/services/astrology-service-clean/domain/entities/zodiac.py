"""
Zodiac Domain Entities.

Core astrological value objects and entities.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ZodiacSign(Enum):
    """12 Zodiac signs (Rashi)."""
    ARIES = ("Aries", "मेष", "Mesh", 1)
    TAURUS = ("Taurus", "वृषभ", "Vrishabh", 2)
    GEMINI = ("Gemini", "मिथुन", "Mithun", 3)
    CANCER = ("Cancer", "कर्क", "Kark", 4)
    LEO = ("Leo", "सिंह", "Simha", 5)
    VIRGO = ("Virgo", "कन्या", "Kanya", 6)
    LIBRA = ("Libra", "तुला", "Tula", 7)
    SCORPIO = ("Scorpio", "वृश्चिक", "Vrishchik", 8)
    SAGITTARIUS = ("Sagittarius", "धनु", "Dhanu", 9)
    CAPRICORN = ("Capricorn", "मकर", "Makar", 10)
    AQUARIUS = ("Aquarius", "कुम्भ", "Kumbh", 11)
    PISCES = ("Pisces", "मीन", "Meen", 12)

    def __init__(self, english: str, hindi: str, transliterated: str, number: int):
        self.english = english
        self.hindi = hindi
        self.transliterated = transliterated
        self.number = number

    @classmethod
    def from_string(cls, value: str) -> "ZodiacSign":
        """Get sign from string (English, Hindi, or transliterated)."""
        value_lower = value.lower().strip()
        for sign in cls:
            if (value_lower == sign.english.lower() or
                value == sign.hindi or
                value_lower == sign.transliterated.lower()):
                return sign
        raise ValueError(f"Unknown zodiac sign: {value}")

    @property
    def element(self) -> str:
        """Get element (Fire, Earth, Air, Water)."""
        elements = {
            1: "Fire", 2: "Earth", 3: "Air", 4: "Water",
            5: "Fire", 6: "Earth", 7: "Air", 8: "Water",
            9: "Fire", 10: "Earth", 11: "Air", 12: "Water"
        }
        return elements[self.number]

    @property
    def ruling_planet(self) -> str:
        """Get ruling planet."""
        rulers = {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
            5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
            9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
        }
        return rulers[self.number]


class Planet(Enum):
    """Nine planets (Navagraha)."""
    SUN = ("Sun", "सूर्य", "Surya")
    MOON = ("Moon", "चंद्र", "Chandra")
    MARS = ("Mars", "मंगल", "Mangal")
    MERCURY = ("Mercury", "बुध", "Budh")
    JUPITER = ("Jupiter", "बृहस्पति", "Brihaspati")
    VENUS = ("Venus", "शुक्र", "Shukra")
    SATURN = ("Saturn", "शनि", "Shani")
    RAHU = ("Rahu", "राहु", "Rahu")
    KETU = ("Ketu", "केतु", "Ketu")

    def __init__(self, english: str, hindi: str, transliterated: str):
        self.english = english
        self.hindi = hindi
        self.transliterated = transliterated


@dataclass(frozen=True)
class Nakshatra:
    """
    Lunar mansion (Nakshatra).

    27 Nakshatras, each divided into 4 padas (quarters).
    """
    number: int  # 1-27
    name: str
    hindi_name: str
    pada: int  # 1-4
    ruling_planet: Planet

    @property
    def degree_start(self) -> float:
        """Starting degree of this nakshatra."""
        return (self.number - 1) * 13.333333

    @property
    def degree_end(self) -> float:
        """Ending degree of this nakshatra."""
        return self.number * 13.333333

    def validate(self) -> list:
        """Validate nakshatra data."""
        errors = []
        if not 1 <= self.number <= 27:
            errors.append("Nakshatra number must be 1-27")
        if not 1 <= self.pada <= 4:
            errors.append("Pada must be 1-4")
        return errors


# Nakshatra data
NAKSHATRAS = [
    ("Ashwini", "अश्विनी", Planet.KETU),
    ("Bharani", "भरणी", Planet.VENUS),
    ("Krittika", "कृत्तिका", Planet.SUN),
    ("Rohini", "रोहिणी", Planet.MOON),
    ("Mrigashira", "मृगशिरा", Planet.MARS),
    ("Ardra", "आर्द्रा", Planet.RAHU),
    ("Punarvasu", "पुनर्वसु", Planet.JUPITER),
    ("Pushya", "पुष्य", Planet.SATURN),
    ("Ashlesha", "आश्लेषा", Planet.MERCURY),
    ("Magha", "मघा", Planet.KETU),
    ("Purva Phalguni", "पूर्व फाल्गुनी", Planet.VENUS),
    ("Uttara Phalguni", "उत्तर फाल्गुनी", Planet.SUN),
    ("Hasta", "हस्त", Planet.MOON),
    ("Chitra", "चित्रा", Planet.MARS),
    ("Swati", "स्वाति", Planet.RAHU),
    ("Vishakha", "विशाखा", Planet.JUPITER),
    ("Anuradha", "अनुराधा", Planet.SATURN),
    ("Jyeshtha", "ज्येष्ठा", Planet.MERCURY),
    ("Mula", "मूल", Planet.KETU),
    ("Purva Ashadha", "पूर्व आषाढ़ा", Planet.VENUS),
    ("Uttara Ashadha", "उत्तर आषाढ़ा", Planet.SUN),
    ("Shravana", "श्रवण", Planet.MOON),
    ("Dhanishta", "धनिष्ठा", Planet.MARS),
    ("Shatabhisha", "शतभिषा", Planet.RAHU),
    ("Purva Bhadrapada", "पूर्व भाद्रपद", Planet.JUPITER),
    ("Uttara Bhadrapada", "उत्तर भाद्रपद", Planet.SATURN),
    ("Revati", "रेवती", Planet.MERCURY),
]
