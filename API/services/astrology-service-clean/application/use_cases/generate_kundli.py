"""
Generate Kundli Use Case.

Single responsibility: Generate birth chart from birth details.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.entities import BirthDetails, Kundli
from domain.repositories import KundliRepository
from application.dto import (
    KundliRequest, KundliResponse,
    PlanetPositionDTO, HouseDTO, DoshaDTO
)


class KundliValidationError(Exception):
    """Raised when kundli request validation fails."""
    pass


class KundliGenerationError(Exception):
    """Raised when kundli generation fails."""
    pass


@dataclass
class GenerateKundliUseCase:
    """
    Use case for generating birth chart.

    Validates input, generates kundli, transforms to DTO.
    """
    kundli_repository: KundliRepository

    async def execute(self, request: KundliRequest) -> KundliResponse:
        """
        Execute the use case.

        Args:
            request: KundliRequest with birth details

        Returns:
            KundliResponse DTO

        Raises:
            KundliValidationError: If input is invalid
            KundliGenerationError: If generation fails
        """
        # 1. Validate and create birth details
        birth_details = self._create_birth_details(request)

        # 2. Generate kundli
        kundli = await self.kundli_repository.generate_kundli(birth_details)

        if kundli is None:
            raise KundliGenerationError(
                f"Failed to generate kundli for {request.name}"
            )

        # 3. Get doshas
        doshas = await self.kundli_repository.get_doshas(kundli)
        kundli.doshas = doshas

        # 4. Transform to DTO
        return self._to_response(kundli)

    def _create_birth_details(self, request: KundliRequest) -> BirthDetails:
        """Create and validate birth details."""
        if not request.name.strip():
            raise KundliValidationError("Name is required")

        try:
            birth_datetime = datetime.strptime(
                f"{request.date} {request.time}",
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            raise KundliValidationError(
                "Invalid date/time format. Use YYYY-MM-DD and HH:MM"
            )

        if not -90 <= request.latitude <= 90:
            raise KundliValidationError("Invalid latitude")

        if not -180 <= request.longitude <= 180:
            raise KundliValidationError("Invalid longitude")

        return BirthDetails(
            name=request.name.strip(),
            date_time=birth_datetime,
            place=request.place,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )

    def _to_response(self, kundli: Kundli) -> KundliResponse:
        """Transform domain entity to DTO."""
        planets = [
            PlanetPositionDTO(
                planet=p.planet.english,
                planet_hindi=p.planet.hindi,
                sign=p.sign.english,
                sign_hindi=p.sign.hindi,
                house=p.house,
                degree=p.degree,
                nakshatra=p.nakshatra,
                nakshatra_pada=p.nakshatra_pada,
                is_retrograde=p.is_retrograde,
                strength=p.strength
            )
            for p in kundli.planets
        ]

        houses = [
            HouseDTO(
                number=h.number,
                sign=h.sign.english,
                sign_hindi=h.sign.hindi,
                planets=[p.english for p in h.planets],
                significance=h.significance
            )
            for h in kundli.houses
        ]

        doshas = [
            DoshaDTO(
                name=d.dosha_type.value,
                is_present=d.is_present,
                severity=d.severity,
                description=d.description,
                remedies=d.remedies
            )
            for d in kundli.doshas
        ]

        return KundliResponse(
            success=True,
            name=kundli.birth_details.name,
            birth_date=kundli.birth_details.date_time.strftime("%Y-%m-%d"),
            birth_time=kundli.birth_details.date_time.strftime("%H:%M"),
            birth_place=kundli.birth_details.place,
            lagna=kundli.lagna.english,
            lagna_hindi=kundli.lagna.hindi,
            moon_sign=kundli.moon_sign.english,
            moon_sign_hindi=kundli.moon_sign.hindi,
            sun_sign=kundli.sun_sign.english,
            nakshatra=kundli.moon_nakshatra,
            nakshatra_pada=kundli.moon_nakshatra_pada,
            planets=planets,
            houses=houses,
            doshas=doshas,
            has_manglik=kundli.has_manglik_dosha,
            has_kaal_sarp=kundli.has_kaal_sarp_dosha,
            current_mahadasha=kundli.current_mahadasha,
            current_antardasha=kundli.current_antardasha,
            mahadasha_end_date=(
                kundli.mahadasha_end_date.strftime("%Y-%m-%d")
                if kundli.mahadasha_end_date else None
            )
        )
