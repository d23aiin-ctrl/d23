"""
Mock Panchang Repository.

Returns sample Hindu calendar data for testing and development.
"""

from typing import Optional, List
from datetime import date, time

from domain.repositories import PanchangRepository
from domain.entities import (
    Panchang, Tithi, TithiPaksha, Yoga, Karana, Muhurta
)


class MockPanchangRepository(PanchangRepository):
    """Mock repository for testing."""

    TITHIS = [
        ("Pratipada", "प्रतिपदा"),
        ("Dwitiya", "द्वितीया"),
        ("Tritiya", "तृतीया"),
        ("Chaturthi", "चतुर्थी"),
        ("Panchami", "पंचमी"),
        ("Shashthi", "षष्ठी"),
        ("Saptami", "सप्तमी"),
        ("Ashtami", "अष्टमी"),
        ("Navami", "नवमी"),
        ("Dashami", "दशमी"),
        ("Ekadashi", "एकादशी"),
        ("Dwadashi", "द्वादशी"),
        ("Trayodashi", "त्रयोदशी"),
        ("Chaturdashi", "चतुर्दशी"),
        ("Purnima/Amavasya", "पूर्णिमा/अमावस्या"),
    ]

    YOGAS = [
        ("Vishkumbha", "विष्कुम्भ"),
        ("Priti", "प्रीति"),
        ("Ayushman", "आयुष्मान"),
        ("Saubhagya", "सौभाग्य"),
        ("Shobhana", "शोभन"),
    ]

    KARANAS = [
        ("Bava", "बव"),
        ("Balava", "बालव"),
        ("Kaulava", "कौलव"),
        ("Taitila", "तैतिल"),
        ("Garaja", "गरज"),
    ]

    NAKSHATRAS = [
        ("Ashwini", "अश्विनी"),
        ("Bharani", "भरणी"),
        ("Krittika", "कृत्तिका"),
        ("Rohini", "रोहिणी"),
        ("Mrigashira", "मृगशिरा"),
    ]

    DAYS = [
        ("Monday", "सोमवार"),
        ("Tuesday", "मंगलवार"),
        ("Wednesday", "बुधवार"),
        ("Thursday", "गुरुवार"),
        ("Friday", "शुक्रवार"),
        ("Saturday", "शनिवार"),
        ("Sunday", "रविवार"),
    ]

    MONTHS = [
        ("Chaitra", "चैत्र"),
        ("Vaishakha", "वैशाख"),
        ("Jyeshtha", "ज्येष्ठ"),
        ("Ashadha", "आषाढ़"),
        ("Shravana", "श्रावण"),
        ("Bhadrapada", "भाद्रपद"),
        ("Ashwina", "आश्विन"),
        ("Kartika", "कार्तिक"),
        ("Margashirsha", "मार्गशीर्ष"),
        ("Pausha", "पौष"),
        ("Magha", "माघ"),
        ("Phalguna", "फाल्गुन"),
    ]

    async def get_panchang(
        self,
        target_date: date,
        city: str,
        latitude: float,
        longitude: float
    ) -> Optional[Panchang]:
        """Get mock panchang."""
        # Calculate indices based on date
        day_of_year = target_date.timetuple().tm_yday

        tithi_num = (day_of_year % 15) + 1
        is_shukla = (day_of_year // 15) % 2 == 0
        tithi_data = self.TITHIS[(tithi_num - 1) % 15]

        tithi = Tithi(
            number=tithi_num,
            name=tithi_data[0],
            hindi_name=tithi_data[1],
            paksha=TithiPaksha.SHUKLA if is_shukla else TithiPaksha.KRISHNA,
            end_time=time(18, 45),
            is_auspicious=tithi_num not in [4, 8, 14]  # Chaturthi, Ashtami, Chaturdashi
        )

        yoga_data = self.YOGAS[day_of_year % 5]
        yoga = Yoga(
            number=(day_of_year % 27) + 1,
            name=yoga_data[0],
            hindi_name=yoga_data[1],
            end_time=time(14, 30),
            is_auspicious=True
        )

        karana_data = self.KARANAS[day_of_year % 5]
        karana = Karana(
            number=(day_of_year % 11) + 1,
            name=karana_data[0],
            hindi_name=karana_data[1],
            end_time=time(9, 15),
            is_auspicious=True
        )

        nakshatra_data = self.NAKSHATRAS[day_of_year % 5]
        day_data = self.DAYS[target_date.weekday()]
        month_data = self.MONTHS[target_date.month - 1]

        # Muhurtas
        abhijit = Muhurta(
            name="Abhijit",
            start_time=time(11, 45),
            end_time=time(12, 33),
            is_auspicious=True,
            suitable_for=["Travel", "New ventures", "Important decisions"]
        )

        rahukaal = Muhurta(
            name="Rahu Kaal",
            start_time=time(13, 30),
            end_time=time(15, 0),
            is_auspicious=False,
            suitable_for=[]
        )

        yamaganda = Muhurta(
            name="Yamaganda",
            start_time=time(9, 0),
            end_time=time(10, 30),
            is_auspicious=False,
            suitable_for=[]
        )

        # Special days
        is_ekadashi = tithi_num == 11
        is_purnima = tithi_num == 15 and is_shukla
        is_amavasya = tithi_num == 15 and not is_shukla

        festivals = []
        if is_ekadashi:
            festivals.append("Ekadashi Vrat")
        if is_purnima:
            festivals.append("Purnima")
        if is_amavasya:
            festivals.append("Amavasya")

        return Panchang(
            date=target_date,
            city=city,
            latitude=latitude,
            longitude=longitude,
            tithi=tithi,
            nakshatra_name=nakshatra_data[0],
            nakshatra_hindi=nakshatra_data[1],
            nakshatra_end_time=time(22, 15),
            yoga=yoga,
            karana=karana,
            vara=day_data[0],
            vara_hindi=day_data[1],
            sunrise=time(6, 58),
            sunset=time(18, 5),
            moonrise=time(19, 30),
            moonset=time(7, 15),
            hindu_month=month_data[0],
            hindu_month_hindi=month_data[1],
            hindu_year=2082,  # Vikram Samvat
            abhijit_muhurta=abhijit,
            rahukaal=rahukaal,
            yamaganda=yamaganda,
            is_ekadashi=is_ekadashi,
            is_pradosh=tithi_num == 13,
            is_amavasya=is_amavasya,
            is_purnima=is_purnima,
            festivals=festivals
        )

    async def get_festivals(
        self,
        month: int,
        year: int
    ) -> List[dict]:
        """Get mock festivals."""
        return [
            {"date": f"{year}-{month:02d}-01", "name": "New Month Begins"},
            {"date": f"{year}-{month:02d}-15", "name": "Full Moon Day"},
        ]

    async def get_auspicious_dates(
        self,
        purpose: str,
        start_date: date,
        end_date: date
    ) -> List[date]:
        """Get mock auspicious dates."""
        dates = []
        current = start_date
        while current <= end_date:
            # Every 3rd and 7th day is auspicious
            if current.day % 3 == 0 or current.day % 7 == 0:
                dates.append(current)
            from datetime import timedelta
            current += timedelta(days=1)
        return dates[:10]  # Limit to 10 dates
