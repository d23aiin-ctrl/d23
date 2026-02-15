"""
Get Train Schedule Use Case.

Single responsibility: Get the schedule of a train.
"""

from typing import Optional
from dataclasses import dataclass

from application.dto import TrainScheduleResponse, TrainDTO, StopDTO
from domain.repositories import TrainRepository
from domain.entities import TrainSchedule


class TrainValidationError(Exception):
    """Raised when train number validation fails."""
    pass


class TrainNotFoundError(Exception):
    """Raised when train is not found."""
    pass


@dataclass
class GetTrainScheduleUseCase:
    """
    Use case for getting train schedule.
    """

    train_repository: TrainRepository

    async def execute(self, train_number: str) -> TrainScheduleResponse:
        """
        Execute the use case.

        Args:
            train_number: 5-digit train number

        Returns:
            TrainScheduleResponse DTO

        Raises:
            TrainValidationError: If train number format is invalid
            TrainNotFoundError: If train is not found
        """
        # 1. Validate input
        self._validate_train_number(train_number)

        # 2. Get from repository
        schedule = await self.train_repository.get_schedule(train_number)

        if schedule is None:
            raise TrainNotFoundError(f"Train {train_number} not found")

        # 3. Transform to DTO
        return self._to_response(schedule)

    def _validate_train_number(self, train_number: str) -> None:
        """Validate train number format."""
        if not train_number:
            raise TrainValidationError("Train number is required")

        if len(train_number) != 5:
            raise TrainValidationError("Train number must be 5 digits")

        if not train_number.isdigit():
            raise TrainValidationError("Train number must contain only digits")

    def _to_response(self, schedule: TrainSchedule) -> TrainScheduleResponse:
        """Transform domain entity to response DTO."""
        train = schedule.train

        train_dto = TrainDTO(
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

        stops = [
            StopDTO(
                station_code=stop.station.code,
                station_name=stop.station.name,
                arrival=stop.arrival.strftime("%H:%M") if stop.arrival else None,
                departure=stop.departure.strftime("%H:%M") if stop.departure else None,
                day=stop.day,
                distance_km=stop.distance_km,
                halt_minutes=stop.halt_minutes,
                platform=stop.platform,
            )
            for stop in schedule.stops
        ]

        return TrainScheduleResponse(
            success=True,
            train=train_dto,
            total_stops=schedule.total_stops,
            stops=stops,
        )

    def _format_duration(self, duration) -> str:
        """Format timedelta to string like '17h 30m'."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes:02d}m"
