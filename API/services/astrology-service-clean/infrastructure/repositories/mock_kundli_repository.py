"""
Mock Kundli Repository.

Returns sample birth chart data for testing and development.
"""

import random
from typing import Optional, List
from datetime import datetime

from domain.repositories import KundliRepository
from domain.entities import (
    Kundli, BirthDetails, PlanetPosition, House,
    ZodiacSign, Planet, Dosha, DoshaType
)


class MockKundliRepository(KundliRepository):
    """Mock repository for testing."""

    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
        "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
        "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
        "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    async def generate_kundli(
        self,
        birth_details: BirthDetails
    ) -> Optional[Kundli]:
        """Generate mock kundli."""
        # Use birth time to seed random for consistent results
        seed = hash((birth_details.name, birth_details.date_time.timestamp()))
        random.seed(seed)

        signs = list(ZodiacSign)
        planets = list(Planet)

        # Generate lagna (ascendant)
        lagna = random.choice(signs)
        lagna_nakshatra = random.choice(self.NAKSHATRAS)

        # Generate planet positions
        planet_positions = []
        for i, planet in enumerate(planets):
            sign = signs[(lagna.number - 1 + i * 2) % 12]
            house = ((sign.number - lagna.number) % 12) + 1

            planet_positions.append(PlanetPosition(
                planet=planet,
                sign=sign,
                house=house,
                degree=random.uniform(0, 30),
                nakshatra=random.choice(self.NAKSHATRAS),
                nakshatra_pada=random.randint(1, 4),
                is_retrograde=random.random() < 0.2,
                is_exalted=random.random() < 0.1,
                is_debilitated=random.random() < 0.1
            ))

        # Generate houses
        houses = []
        for i in range(1, 13):
            sign = signs[(lagna.number - 1 + i - 1) % 12]
            house_planets = [p.planet for p in planet_positions if p.house == i]
            houses.append(House(
                number=i,
                sign=sign,
                degree=0.0,
                planets=house_planets
            ))

        # Moon sign and nakshatra
        moon_pos = next((p for p in planet_positions if p.planet == Planet.MOON), None)
        moon_sign = moon_pos.sign if moon_pos else random.choice(signs)
        moon_nakshatra = moon_pos.nakshatra if moon_pos else random.choice(self.NAKSHATRAS)

        # Sun sign
        sun_pos = next((p for p in planet_positions if p.planet == Planet.SUN), None)
        sun_sign = sun_pos.sign if sun_pos else random.choice(signs)

        # Current dasha
        dasha_planets = ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"]
        current_mahadasha = random.choice(dasha_planets)
        current_antardasha = random.choice(dasha_planets)

        return Kundli(
            birth_details=birth_details,
            lagna=lagna,
            lagna_degree=random.uniform(0, 30),
            lagna_nakshatra=lagna_nakshatra,
            moon_sign=moon_sign,
            moon_nakshatra=moon_nakshatra,
            moon_nakshatra_pada=random.randint(1, 4),
            sun_sign=sun_sign,
            planets=planet_positions,
            houses=houses,
            current_mahadasha=current_mahadasha,
            current_antardasha=current_antardasha,
            mahadasha_end_date=datetime(2030, 1, 1)
        )

    async def get_doshas(
        self,
        kundli: Kundli
    ) -> List[Dosha]:
        """Analyze mock doshas."""
        doshas = []

        # Check Manglik dosha (Mars in 1, 4, 7, 8, 12)
        mars_pos = next((p for p in kundli.planets if p.planet == Planet.MARS), None)
        manglik_houses = [1, 4, 7, 8, 12]
        is_manglik = mars_pos and mars_pos.house in manglik_houses

        doshas.append(Dosha(
            dosha_type=DoshaType.MANGLIK,
            is_present=is_manglik,
            severity="Moderate" if is_manglik else "None",
            description="Mars in angular house" if is_manglik else "No Manglik dosha",
            remedies=["Kumbh Vivah", "Hanuman Chalisa recitation"] if is_manglik else []
        ))

        # Kaal Sarp dosha (all planets between Rahu-Ketu)
        rahu_pos = next((p for p in kundli.planets if p.planet == Planet.RAHU), None)
        ketu_pos = next((p for p in kundli.planets if p.planet == Planet.KETU), None)
        is_kaal_sarp = random.random() < 0.15  # 15% chance

        doshas.append(Dosha(
            dosha_type=DoshaType.KAAL_SARP,
            is_present=is_kaal_sarp,
            severity="Severe" if is_kaal_sarp else "None",
            description="All planets between Rahu-Ketu" if is_kaal_sarp else "No Kaal Sarp dosha",
            remedies=["Rahu-Ketu shanti puja", "Visit Trimbakeshwar"] if is_kaal_sarp else []
        ))

        # Sade Sati (Saturn transit over Moon)
        is_sade_sati = random.random() < 0.22  # ~7.5 years out of 30

        doshas.append(Dosha(
            dosha_type=DoshaType.SADE_SATI,
            is_present=is_sade_sati,
            severity="Mild" if is_sade_sati else "None",
            description="Saturn transiting Moon sign" if is_sade_sati else "Not in Sade Sati period",
            remedies=["Shani puja on Saturdays", "Donate black items"] if is_sade_sati else []
        ))

        return doshas

    async def match_kundlis(
        self,
        kundli1: Kundli,
        kundli2: Kundli
    ) -> dict:
        """Mock kundli matching."""
        # Ashtakoot guna milan (8 aspects, 36 points max)
        gunas = [
            {"name": "Varna", "name_hindi": "वर्ण", "max_points": 1},
            {"name": "Vashya", "name_hindi": "वश्य", "max_points": 2},
            {"name": "Tara", "name_hindi": "तारा", "max_points": 3},
            {"name": "Yoni", "name_hindi": "योनि", "max_points": 4},
            {"name": "Graha Maitri", "name_hindi": "ग्रह मैत्री", "max_points": 5},
            {"name": "Gana", "name_hindi": "गण", "max_points": 6},
            {"name": "Bhakoot", "name_hindi": "भकूट", "max_points": 7},
            {"name": "Nadi", "name_hindi": "नाड़ी", "max_points": 8},
        ]

        guna_details = []
        total = 0

        for guna in gunas:
            # Random but deterministic score
            seed = hash((kundli1.birth_details.name, kundli2.birth_details.name, guna["name"]))
            random.seed(seed)
            obtained = random.uniform(0, guna["max_points"])
            obtained = round(obtained, 1)
            total += obtained

            guna_details.append({
                "name": guna["name"],
                "name_hindi": guna["name_hindi"],
                "max_points": guna["max_points"],
                "obtained_points": obtained,
                "description": f"{guna['name']} compatibility score"
            })

        # Nadi dosha check (same nadi = dosha)
        nadi_dosha = random.random() < 0.33  # 1/3 chance

        recommendations = []
        if total < 18:
            recommendations.append("Match score is below recommended threshold")
            recommendations.append("Consult with a pandit for remedies")
        elif nadi_dosha:
            recommendations.append("Nadi dosha present - remedies recommended")
            recommendations.append("Nadi shanti puja advised")
        else:
            recommendations.append("Match is favorable")
            recommendations.append("Proceed with confidence")

        return {
            "total_points": round(total, 1),
            "guna_details": guna_details,
            "nadi_dosha": nadi_dosha,
            "recommendations": recommendations
        }
