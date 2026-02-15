"""Mock Holiday Repository Implementation."""
from typing import List, Optional
from datetime import date, datetime, timedelta
from domain.entities import Holiday, HolidayType
from domain.repositories import HolidayRepository


class MockHolidayRepository(HolidayRepository):
    """Mock implementation of holiday repository for testing."""

    def __init__(self):
        self._holidays = [
            Holiday(name="Republic Day", date=date(2024, 1, 26), holiday_type=HolidayType.NATIONAL, day="Friday", description="Celebrates Constitution adoption"),
            Holiday(name="Holi", date=date(2024, 3, 25), holiday_type=HolidayType.NATIONAL, day="Monday", description="Festival of Colors"),
            Holiday(name="Good Friday", date=date(2024, 3, 29), holiday_type=HolidayType.BANK, day="Friday", description="Christian Holiday"),
            Holiday(name="Independence Day", date=date(2024, 8, 15), holiday_type=HolidayType.NATIONAL, day="Thursday", description="Independence from British rule"),
            Holiday(name="Gandhi Jayanti", date=date(2024, 10, 2), holiday_type=HolidayType.NATIONAL, day="Wednesday", description="Mahatma Gandhi's Birthday"),
            Holiday(name="Diwali", date=date(2024, 11, 1), holiday_type=HolidayType.NATIONAL, day="Friday", description="Festival of Lights"),
            Holiday(name="Guru Nanak Jayanti", date=date(2024, 11, 15), holiday_type=HolidayType.OPTIONAL, day="Friday", description="Guru Nanak's Birthday"),
            Holiday(name="Christmas", date=date(2024, 12, 25), holiday_type=HolidayType.NATIONAL, day="Wednesday", description="Christmas Day"),
            Holiday(name="Pongal", date=date(2024, 1, 15), holiday_type=HolidayType.REGIONAL, day="Monday", description="Tamil Harvest Festival", state="Tamil Nadu"),
            Holiday(name="Onam", date=date(2024, 9, 15), holiday_type=HolidayType.REGIONAL, day="Sunday", description="Kerala Harvest Festival", state="Kerala"),
        ]

    async def get_holidays(
        self,
        year: int,
        state: Optional[str] = None,
        holiday_type: Optional[HolidayType] = None
    ) -> List[Holiday]:
        holidays = [h for h in self._holidays if h.date.year == year]

        if state:
            holidays = [h for h in holidays if h.state is None or h.state.lower() == state.lower()]

        if holiday_type:
            holidays = [h for h in holidays if h.holiday_type == holiday_type]

        return sorted(holidays, key=lambda h: h.date)

    async def get_upcoming_holidays(self, days: int = 30) -> List[Holiday]:
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        return [h for h in self._holidays if today <= h.date <= end_date]
