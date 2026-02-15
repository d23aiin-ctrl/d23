"""
Get PNR Status Use Case.

Single responsibility: Get the status of a PNR.
"""

from typing import Optional
from dataclasses import dataclass

from application.dto import PNRResponse, PassengerDTO
from domain.repositories import PNRRepository
from domain.entities import PNR


class PNRValidationError(Exception):
    """Raised when PNR validation fails."""
    pass


class PNRNotFoundError(Exception):
    """Raised when PNR is not found."""
    pass


@dataclass
class GetPNRStatusUseCase:
    """
    Use case for getting PNR status.

    This class:
    - Validates input
    - Calls repository to get data
    - Transforms domain entity to DTO
    - Handles errors

    It does NOT:
    - Know about HTTP/FastAPI
    - Know about databases
    - Handle caching (that's repository's job)
    """

    pnr_repository: PNRRepository

    async def execute(self, pnr_number: str) -> PNRResponse:
        """
        Execute the use case.

        Args:
            pnr_number: 10-digit PNR number

        Returns:
            PNRResponse DTO

        Raises:
            PNRValidationError: If PNR format is invalid
            PNRNotFoundError: If PNR is not found
        """
        # 1. Validate input
        self._validate_pnr(pnr_number)

        # 2. Get from repository
        pnr = await self.pnr_repository.get_by_pnr(pnr_number)

        if pnr is None:
            raise PNRNotFoundError(f"PNR {pnr_number} not found")

        # 3. Transform to DTO
        return self._to_response(pnr)

    def _validate_pnr(self, pnr_number: str) -> None:
        """Validate PNR format."""
        if not pnr_number:
            raise PNRValidationError("PNR number is required")

        if len(pnr_number) != 10:
            raise PNRValidationError("PNR must be 10 digits")

        if not pnr_number.isdigit():
            raise PNRValidationError("PNR must contain only digits")

    def _to_response(self, pnr: PNR) -> PNRResponse:
        """Transform domain entity to response DTO."""
        passengers = [
            PassengerDTO(
                number=p.number,
                booking_status=p.booking_status.value,
                current_status=p.current_status.value,
                coach=p.coach,
                berth=p.berth,
                berth_type=p.berth_type,
                is_confirmed=p.is_confirmed,
            )
            for p in pnr.passengers
        ]

        return PNRResponse(
            success=True,
            pnr=pnr.pnr_number,
            train_number=pnr.train_number,
            train_name=pnr.train_name,
            journey_date=pnr.journey_date.strftime("%d-%m-%Y"),
            from_station=pnr.from_station_code,
            from_station_name=pnr.from_station_name,
            to_station=pnr.to_station_code,
            to_station_name=pnr.to_station_name,
            travel_class=pnr.travel_class,
            chart_prepared=pnr.chart_prepared,
            passengers=passengers,
            total_passengers=pnr.total_passengers,
            confirmed_passengers=pnr.confirmed_passengers,
            all_confirmed=pnr.all_confirmed,
            status_summary=pnr.booking_status_summary,
            message="Chart not prepared yet" if not pnr.chart_prepared else None,
        )
