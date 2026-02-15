"""
Horoscope Domain Entity.

Represents daily/weekly/monthly predictions.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
from enum import Enum

from .zodiac import ZodiacSign


class HoroscopePeriod(Enum):
    """Period for horoscope prediction."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass(frozen=True)
class LuckyElements:
    """Lucky elements for a zodiac sign."""
    numbers: List[int]
    colors: List[str]
    time: str  # e.g., "2:00 PM - 4:00 PM"
    day: str  # e.g., "Tuesday"

    def validate(self) -> List[str]:
        errors = []
        if not self.numbers:
            errors.append("Lucky numbers required")
        if not self.colors:
            errors.append("Lucky colors required")
        return errors


@dataclass
class Horoscope:
    """
    Horoscope prediction entity.

    Contains prediction text and various aspects of life.
    """
    sign: ZodiacSign
    period: HoroscopePeriod
    date: date

    # Core prediction
    prediction: str

    # Life aspects (0-100 scale)
    love_score: int
    career_score: int
    health_score: int
    finance_score: int

    # Detailed predictions
    love_prediction: Optional[str] = None
    career_prediction: Optional[str] = None
    health_prediction: Optional[str] = None
    finance_prediction: Optional[str] = None

    # Mood and tips
    mood: Optional[str] = None
    health_tip: Optional[str] = None

    # Lucky elements
    lucky: Optional[LuckyElements] = None

    # Compatibility
    compatible_signs: List[ZodiacSign] = field(default_factory=list)

    @property
    def overall_score(self) -> int:
        """Calculate overall score from all aspects."""
        return (self.love_score + self.career_score +
                self.health_score + self.finance_score) // 4

    @property
    def is_favorable(self) -> bool:
        """Check if overall prediction is favorable."""
        return self.overall_score >= 60

    @property
    def strongest_aspect(self) -> str:
        """Get the strongest life aspect."""
        aspects = {
            "love": self.love_score,
            "career": self.career_score,
            "health": self.health_score,
            "finance": self.finance_score
        }
        return max(aspects, key=aspects.get)

    @property
    def weakest_aspect(self) -> str:
        """Get the weakest life aspect."""
        aspects = {
            "love": self.love_score,
            "career": self.career_score,
            "health": self.health_score,
            "finance": self.finance_score
        }
        return min(aspects, key=aspects.get)

    def validate(self) -> List[str]:
        """Validate horoscope data."""
        errors = []

        if not self.prediction:
            errors.append("Prediction text is required")

        for score_name, score in [
            ("love", self.love_score),
            ("career", self.career_score),
            ("health", self.health_score),
            ("finance", self.finance_score)
        ]:
            if not 0 <= score <= 100:
                errors.append(f"{score_name}_score must be 0-100")

        return errors
