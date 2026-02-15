"""
Get Live Status Use Case.

Single responsibility: Get live running status of a train.
"""

from typing import Optional
from dataclasses import dataclass
from datetime import date, datetime

from application.dto import LiveStatusDTO
from domain.repositories import TrainRepository


class LiveStatusError(Exception):
    """Raised when live status cannot be retrieved."""
    pass


@dataclass
class GetLiveStatusUseCase:
    """
    Use case for getting live train running status.
    """

    train_repository: TrainRepository

    async def execute(
        self,
        train_number: str,
        journey_date: Optional[str] = None
    ) -> LiveStatusDTO:
        """
        Execute the use case.

        Args:
            train_number: 5-digit train number
            journey_date: Optional date in DD-MM-YYYY format

        Returns:
            LiveStatusDTO

        Raises:
            LiveStatusError: If status cannot be retrieved
        """
        # 1. Validate train number
        if not train_number or len(train_number) != 5:
            raise LiveStatusError("Invalid train number")

        # 2. Parse date (default to today)
        if journey_date:
            try:
                parsed_date = datetime.strptime(journey_date, "%d-%m-%Y").date()
            except ValueError:
                raise LiveStatusError("Invalid date format. Use DD-MM-YYYY")
        else:
            parsed_date = date.today()

        # 3. Get live status
        status = await self.train_repository.get_live_status(
            train_number, parsed_date
        )

        if status is None:
            raise LiveStatusError(
                f"Live status not available for train {train_number}"
            )

        # 4. Return DTO
        return LiveStatusDTO(
            success=True,
            train_number=status.get("train_number", train_number),
            train_name=status.get("train_name", ""),
            current_station=status.get("current_station", ""),
            current_station_name=status.get("current_station_name", ""),
            delay_minutes=status.get("delay_minutes", 0),
            last_updated=status.get("last_updated", ""),
            stations=status.get("stations", []),
        )
