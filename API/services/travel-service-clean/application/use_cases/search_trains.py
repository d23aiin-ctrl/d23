"""
Search Trains Use Case.

Single responsibility: Search trains between stations.
"""

from typing import Optional, List
from dataclasses import dataclass
from datetime import date, datetime

from application.dto import TrainSearchResponse, TrainDTO
from domain.repositories import TrainRepository
from domain.entities import Train


class StationValidationError(Exception):
    """Raised when station validation fails."""
    pass


@dataclass
class SearchTrainsUseCase:
    """
    Use case for searching trains between stations.
    """

    train_repository: TrainRepository

    async def execute(
        self,
        from_station: str,
        to_station: str,
        journey_date: Optional[str] = None
    ) -> TrainSearchResponse:
        """
        Execute the use case.

        Args:
            from_station: Source station code
            to_station: Destination station code
            journey_date: Optional date in DD-MM-YYYY format

        Returns:
            TrainSearchResponse DTO

        Raises:
            StationValidationError: If station codes are invalid
        """
        # 1. Validate input
        from_station = from_station.upper()
        to_station = to_station.upper()
        self._validate_stations(from_station, to_station)

        # 2. Parse date if provided
        parsed_date = None
        if journey_date:
            parsed_date = self._parse_date(journey_date)

        # 3. Search trains
        trains = await self.train_repository.search(
            from_station, to_station, parsed_date
        )

        # 4. Transform to DTO
        return self._to_response(
            trains, from_station, to_station, journey_date
        )

    def _validate_stations(self, from_station: str, to_station: str) -> None:
        """Validate station codes."""
        if not from_station:
            raise StationValidationError("Source station is required")

        if not to_station:
            raise StationValidationError("Destination station is required")

        if len(from_station) < 2 or len(from_station) > 5:
            raise StationValidationError("Invalid source station code")

        if len(to_station) < 2 or len(to_station) > 5:
            raise StationValidationError("Invalid destination station code")

        if from_station == to_station:
            raise StationValidationError("Source and destination cannot be same")

    def _parse_date(self, date_str: str) -> date:
        """Parse date from DD-MM-YYYY format."""
        try:
            return datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            raise StationValidationError("Invalid date format. Use DD-MM-YYYY")

    def _to_response(
        self,
        trains: List[Train],
        from_station: str,
        to_station: str,
        journey_date: Optional[str]
    ) -> TrainSearchResponse:
        """Transform domain entities to response DTO."""
        # Note: In real implementation, we'd get station names from a lookup
        train_dtos = [
            TrainDTO(
                train_number=train.number,
                train_name=train.name,
                train_type=train.train_type.value,
                source=train.source.code,
                source_name=train.source.name,
                destination=train.destination.code,
                destination_name=train.destination.name,
                departure=train.departure_time.strftime("%H:%M"),
                arrival=train.arrival_time.strftime("%H:%M"),
                duration=self._format_duration(train.duration),
                distance_km=train.distance_km,
                runs_on=train.runs_on,
                classes=train.classes,
                is_daily=train.is_daily,
            )
            for train in trains
        ]

        return TrainSearchResponse(
            success=True,
            from_station=from_station,
            from_station_name=from_station,  # Would be looked up
            to_station=to_station,
            to_station_name=to_station,  # Would be looked up
            date=journey_date,
            trains_found=len(train_dtos),
            trains=train_dtos,
        )

    def _format_duration(self, duration) -> str:
        """Format timedelta to string."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes:02d}m"
