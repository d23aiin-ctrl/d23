"""
Match Kundli Use Case.

Single responsibility: Match two kundlis for marriage compatibility.
"""

from dataclasses import dataclass

from domain.repositories import KundliRepository
from application.dto import MatchingRequest, MatchingResponse, GunaMatchDTO
from .generate_kundli import GenerateKundliUseCase, KundliValidationError


class MatchingError(Exception):
    """Raised when kundli matching fails."""
    pass


@dataclass
class MatchKundliUseCase:
    """
    Use case for kundli matching (Guna Milan).

    Generates both kundlis and performs compatibility matching.
    """
    kundli_repository: KundliRepository

    async def execute(self, request: MatchingRequest) -> MatchingResponse:
        """
        Execute the use case.

        Args:
            request: MatchingRequest with both persons' details

        Returns:
            MatchingResponse DTO

        Raises:
            KundliValidationError: If input is invalid
            MatchingError: If matching fails
        """
        # 1. Generate both kundlis
        generate_use_case = GenerateKundliUseCase(
            kundli_repository=self.kundli_repository
        )

        kundli1_response = await generate_use_case.execute(request.person1)
        kundli2_response = await generate_use_case.execute(request.person2)

        # 2. For matching, we need the domain entities
        # Re-create them from birth details
        from domain.entities import BirthDetails
        from datetime import datetime

        birth1 = BirthDetails(
            name=request.person1.name,
            date_time=datetime.strptime(
                f"{request.person1.date} {request.person1.time}",
                "%Y-%m-%d %H:%M"
            ),
            place=request.person1.place,
            latitude=request.person1.latitude,
            longitude=request.person1.longitude
        )
        birth2 = BirthDetails(
            name=request.person2.name,
            date_time=datetime.strptime(
                f"{request.person2.date} {request.person2.time}",
                "%Y-%m-%d %H:%M"
            ),
            place=request.person2.place,
            latitude=request.person2.latitude,
            longitude=request.person2.longitude
        )

        kundli1 = await self.kundli_repository.generate_kundli(birth1)
        kundli2 = await self.kundli_repository.generate_kundli(birth2)

        if not kundli1 or not kundli2:
            raise MatchingError("Failed to generate one or both kundlis")

        # 3. Perform matching
        match_result = await self.kundli_repository.match_kundlis(
            kundli1, kundli2
        )

        # 4. Transform to response
        return self._to_response(match_result, kundli1, kundli2)

    def _to_response(
        self,
        match_result: dict,
        kundli1,
        kundli2
    ) -> MatchingResponse:
        """Transform match result to DTO."""
        total_points = match_result.get("total_points", 0)
        max_points = 36

        # Determine verdict
        percentage = (total_points / max_points) * 100
        if percentage >= 75:
            verdict = "Excellent"
            is_recommended = True
        elif percentage >= 60:
            verdict = "Good"
            is_recommended = True
        elif percentage >= 45:
            verdict = "Average"
            is_recommended = True
        else:
            verdict = "Below Average"
            is_recommended = False

        # Guna details
        guna_details = [
            GunaMatchDTO(
                name=g["name"],
                name_hindi=g["name_hindi"],
                max_points=g["max_points"],
                obtained_points=g["obtained_points"],
                description=g["description"]
            )
            for g in match_result.get("guna_details", [])
        ]

        # Manglik status
        both_manglik = kundli1.has_manglik_dosha and kundli2.has_manglik_dosha
        neither_manglik = not kundli1.has_manglik_dosha and not kundli2.has_manglik_dosha

        if both_manglik:
            manglik_status = "Both are Manglik - Compatible"
        elif neither_manglik:
            manglik_status = "Neither is Manglik - Compatible"
        else:
            manglik_status = "One is Manglik - Needs remedies"

        return MatchingResponse(
            success=True,
            total_points=total_points,
            max_points=max_points,
            match_percentage=round(percentage, 1),
            verdict=verdict,
            is_recommended=is_recommended,
            guna_details=guna_details,
            manglik_status=manglik_status,
            nadi_dosha=match_result.get("nadi_dosha", False),
            recommendations=match_result.get("recommendations", [])
        )
