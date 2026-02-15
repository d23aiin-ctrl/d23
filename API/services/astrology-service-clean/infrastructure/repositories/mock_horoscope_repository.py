"""
Mock Horoscope Repository.

Returns sample horoscope data for testing and development.
"""

import random
from typing import Optional
from datetime import date

from domain.repositories import HoroscopeRepository
from domain.entities import (
    Horoscope, ZodiacSign, HoroscopePeriod, LuckyElements
)


class MockHoroscopeRepository(HoroscopeRepository):
    """Mock repository for testing."""

    PREDICTIONS = {
        "daily": [
            "Today brings positive energy and new opportunities. Stay focused on your goals.",
            "A day of reflection and inner growth. Take time for yourself.",
            "Communication is key today. Express your thoughts clearly.",
            "Financial matters need attention. Make wise decisions.",
            "Love and relationships take center stage. Open your heart.",
        ],
        "weekly": [
            "This week promises growth in career and personal life.",
            "Focus on health and wellness throughout the week.",
            "New connections will bring exciting opportunities.",
        ],
        "monthly": [
            "This month is ideal for new beginnings and fresh starts.",
            "Career advancement is on the horizon. Work hard.",
            "Financial stability improves through careful planning.",
        ]
    }

    MOODS = ["Optimistic", "Contemplative", "Energetic", "Romantic", "Ambitious"]

    HEALTH_TIPS = [
        "Stay hydrated and get adequate rest",
        "Morning exercise will boost your energy",
        "Include more greens in your diet",
        "Practice meditation for mental clarity",
    ]

    async def get_horoscope(
        self,
        sign: ZodiacSign,
        period: HoroscopePeriod,
        target_date: Optional[date] = None
    ) -> Optional[Horoscope]:
        """Get mock horoscope."""
        target_date = target_date or date.today()

        # Generate deterministic but varied scores based on sign and date
        seed = hash((sign.number, target_date.toordinal(), period.value))
        random.seed(seed)

        predictions = self.PREDICTIONS.get(period.value, self.PREDICTIONS["daily"])
        prediction = random.choice(predictions)

        love_score = random.randint(50, 95)
        career_score = random.randint(50, 95)
        health_score = random.randint(50, 95)
        finance_score = random.randint(50, 95)

        lucky = LuckyElements(
            numbers=[random.randint(1, 9) for _ in range(3)],
            colors=[random.choice(["Red", "Blue", "Green", "Yellow", "Orange", "Purple"])
                    for _ in range(2)],
            time=f"{random.randint(1, 12)}:00 PM - {random.randint(1, 12) + 2}:00 PM",
            day=random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        )

        # Compatible signs (same element + 1)
        compatible = []
        for s in ZodiacSign:
            if s.element == sign.element and s != sign:
                compatible.append(s)
        compatible = compatible[:3]

        return Horoscope(
            sign=sign,
            period=period,
            date=target_date,
            prediction=prediction,
            love_score=love_score,
            career_score=career_score,
            health_score=health_score,
            finance_score=finance_score,
            love_prediction=f"Love looks favorable with a score of {love_score}%",
            career_prediction=f"Career prospects are strong at {career_score}%",
            health_prediction=f"Health remains stable at {health_score}%",
            finance_prediction=f"Financial outlook is at {finance_score}%",
            mood=random.choice(self.MOODS),
            health_tip=random.choice(self.HEALTH_TIPS),
            lucky=lucky,
            compatible_signs=compatible
        )

    async def get_compatibility(
        self,
        sign1: ZodiacSign,
        sign2: ZodiacSign
    ) -> dict:
        """Get mock compatibility."""
        # Same element = high compatibility
        if sign1.element == sign2.element:
            score = random.randint(75, 95)
        else:
            score = random.randint(45, 75)

        return {
            "sign1": sign1.english,
            "sign2": sign2.english,
            "score": score,
            "description": f"Compatibility between {sign1.english} and {sign2.english}"
        }
