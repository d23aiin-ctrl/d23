"""Route classified intents to the appropriate service client method."""

import logging
from typing import Any

from bot.intent_classifier import ClassificationResult
from clients.astrology_client import AstrologyClient
from clients.base_client import ServiceUnavailableError
from clients.finance_client import FinanceClient
from clients.government_client import GovernmentClient
from clients.travel_client import TravelClient
from clients.utility_client import UtilityClient

logger = logging.getLogger(__name__)

# Greeting and help messages
GREETING_RESPONSE = {
    "message": (
        "Hello! I'm your AI assistant. I can help you with:\n\n"
        "🚂 **Travel** - PNR status, train schedules, search trains\n"
        "🔮 **Astrology** - Horoscope, Kundli, Panchang\n"
        "💰 **Finance** - EMI calculator, SIP returns, stock prices\n"
        "🏛 **Government** - PM Kisan, driving license, vehicle info, e-challan\n"
        "🌤 **Utility** - Weather, gold/fuel prices, currency, pincode, IFSC, holidays\n\n"
        "Just type your question in English or Hindi!"
    )
}

UNKNOWN_RESPONSE = {
    "message": (
        "I'm not sure what you're looking for. Here are some things I can help with:\n\n"
        "- \"Check PNR 4521678903\"\n"
        "- \"Weather in Mumbai\"\n"
        "- \"Aries horoscope\"\n"
        "- \"TCS stock price\"\n"
        "- \"EMI for 50 lakh at 8.5% for 20 years\"\n"
        "- \"Gold rate today\"\n"
        "- \"Petrol price in Delhi\"\n"
        "- \"PM Kisan status 9876543210\"\n"
        "- \"Convert 100 USD to INR\"\n"
        "- \"Pincode 400001\"\n"
    )
}

MISSING_ENTITY_MESSAGES = {
    "pnr_status": "Please provide a 10-digit PNR number. Example: \"Check PNR 4521678903\"",
    "train_schedule": "Please provide a train number. Example: \"Schedule of train 12301\"",
    "train_status": "Please provide a train number. Example: \"Running status of 12301\"",
    "train_search": "Please provide source and destination. Example: \"Trains from Delhi to Mumbai\"",
    "horoscope": "Please provide your zodiac sign. Example: \"Aries horoscope\" or \"मेष राशिफल\"",
    "kundli": "To generate a kundli, I need: name, birth date (YYYY-MM-DD), time (HH:MM), and place. Example: \"Kundli for Ravi, 1990-05-15, 10:30, Delhi\"",
    "stock_price": "Please provide a stock/company name. Example: \"TCS stock price\" or \"Reliance share price\"",
    "pmkisan": "Please provide a 10-digit mobile number or 12-digit Aadhaar. Example: \"PM Kisan status 9876543210\"",
    "driving_license": "Please provide your DL number. Example: \"Check DL DL0120160001234\"",
    "vehicle_info": "Please provide a vehicle registration number. Example: \"Vehicle info DL01AB1234\"",
    "echallan": "Please provide a vehicle number. Example: \"E-challan check DL01AB1234\"",
    "weather": "Which city? Example: \"Weather in Mumbai\"",
    "gold_price": "Which city? Example: \"Gold rate in Delhi\" (default: Delhi)",
    "fuel_price": "Which city? Example: \"Petrol price in Mumbai\"",
    "pincode": "Please provide a 6-digit pincode. Example: \"Pincode 400001\"",
    "ifsc": "Please provide an IFSC code. Example: \"IFSC SBIN0001234\"",
}


class BotRouter:
    """Routes intents to the appropriate service client and executes the call."""

    def __init__(
        self,
        travel: TravelClient,
        astrology: AstrologyClient,
        finance: FinanceClient,
        government: GovernmentClient,
        utility: UtilityClient,
    ):
        self.travel = travel
        self.astrology = astrology
        self.finance = finance
        self.government = government
        self.utility = utility

    async def route(self, classification: ClassificationResult) -> dict[str, Any]:
        """Route a classification result to the correct service and return response data."""
        intent = classification.intent
        entities = classification.entities

        if intent == "greeting":
            return {"intent": intent, "response": GREETING_RESPONSE}

        if intent == "unknown":
            return {"intent": intent, "response": UNKNOWN_RESPONSE}

        handler = self._get_handler(intent)
        if handler is None:
            return {"intent": intent, "response": UNKNOWN_RESPONSE}

        # Check for required entities
        missing = self._check_required_entities(intent, entities)
        if missing:
            return {
                "intent": intent,
                "response": {"message": missing},
                "needs_input": True,
            }

        try:
            data = await handler(entities)
            return {"intent": intent, "response": data, "success": True}
        except ServiceUnavailableError as e:
            return {
                "intent": intent,
                "response": {"message": f"Sorry, the {e.service_name} is currently unavailable. Please try again later."},
                "error": True,
            }
        except Exception as e:
            logger.exception("Error routing intent %s", intent)
            return {
                "intent": intent,
                "response": {"message": f"Something went wrong while processing your request. Please try again."},
                "error": True,
            }

    def _get_handler(self, intent: str):
        """Map intent to handler function."""
        handlers = {
            "pnr_status": self._handle_pnr,
            "train_schedule": self._handle_train_schedule,
            "train_status": self._handle_train_status,
            "train_search": self._handle_train_search,
            "horoscope": self._handle_horoscope,
            "kundli": self._handle_kundli,
            "kundli_match": self._handle_kundli_match,
            "panchang": self._handle_panchang,
            "emi_calculate": self._handle_emi,
            "sip_calculate": self._handle_sip,
            "stock_price": self._handle_stock,
            "pmkisan": self._handle_pmkisan,
            "driving_license": self._handle_dl,
            "vehicle_info": self._handle_vehicle,
            "echallan": self._handle_echallan,
            "weather": self._handle_weather,
            "gold_price": self._handle_gold,
            "fuel_price": self._handle_fuel,
            "currency": self._handle_currency,
            "pincode": self._handle_pincode,
            "ifsc": self._handle_ifsc,
            "holidays": self._handle_holidays,
        }
        return handlers.get(intent)

    def _check_required_entities(self, intent: str, entities: dict) -> str | None:
        """Check if required entities are present, return message if missing."""
        required = {
            "pnr_status": ["pnr_number"],
            "train_schedule": ["train_number"],
            "train_status": ["train_number"],
            "train_search": ["from_station", "to_station"],
            "horoscope": ["sign"],
            "stock_price": ["symbol"],
            "driving_license": ["dl_number"],
            "vehicle_info": ["vehicle_number"],
            "pincode": ["pincode"],
            "ifsc": ["ifsc"],
        }

        required_fields = required.get(intent, [])
        for field in required_fields:
            if field not in entities or not entities[field]:
                return MISSING_ENTITY_MESSAGES.get(intent, "Please provide more details.")
        return None

    # --- Travel handlers ---

    async def _handle_pnr(self, entities: dict) -> dict:
        return await self.travel.get_pnr_status(entities["pnr_number"])

    async def _handle_train_schedule(self, entities: dict) -> dict:
        return await self.travel.get_train_schedule(entities["train_number"])

    async def _handle_train_status(self, entities: dict) -> dict:
        return await self.travel.get_train_status(
            entities["train_number"], entities.get("date"),
        )

    async def _handle_train_search(self, entities: dict) -> dict:
        return await self.travel.search_trains(
            entities["from_station"], entities["to_station"], entities.get("date"),
        )

    # --- Astrology handlers ---

    async def _handle_horoscope(self, entities: dict) -> dict:
        return await self.astrology.get_horoscope(
            entities["sign"], entities.get("period", "daily"),
        )

    async def _handle_kundli(self, entities: dict) -> dict:
        if not entities.get("name") or not entities.get("date"):
            return {"message": MISSING_ENTITY_MESSAGES["kundli"]}
        return await self.astrology.generate_kundli(
            name=entities["name"],
            date=entities["date"],
            time=entities.get("time", "12:00"),
            place=entities.get("place", "Delhi"),
            latitude=entities.get("latitude", 28.6139),
            longitude=entities.get("longitude", 77.2090),
        )

    async def _handle_kundli_match(self, entities: dict) -> dict:
        return {"message": MISSING_ENTITY_MESSAGES.get("kundli", "Please provide birth details for both persons.")}

    async def _handle_panchang(self, entities: dict) -> dict:
        return await self.astrology.get_panchang(
            date=entities.get("date"),
            city=entities.get("city", "Delhi"),
        )

    # --- Finance handlers ---

    async def _handle_emi(self, entities: dict) -> dict:
        principal = entities.get("principal", 0)
        rate = entities.get("annual_rate", 0)
        tenure = entities.get("tenure_months", 0)

        if not principal or not rate or not tenure:
            return {"message": "Please provide loan amount, interest rate, and tenure. Example: \"EMI for 50 lakh at 8.5% for 20 years\""}

        return await self.finance.calculate_emi(
            principal=principal,
            annual_rate=rate,
            tenure_months=tenure,
            loan_type=entities.get("loan_type", "personal"),
        )

    async def _handle_sip(self, entities: dict) -> dict:
        monthly = entities.get("monthly_investment", 0)
        duration = entities.get("duration_years", 0)

        if not monthly or not duration:
            return {"message": "Please provide monthly amount and duration. Example: \"SIP 10000/month for 10 years at 12%\""}

        return await self.finance.calculate_sip(
            monthly_investment=monthly,
            duration_years=duration,
            expected_return_rate=entities.get("expected_return_rate", 12.0),
        )

    async def _handle_stock(self, entities: dict) -> dict:
        return await self.finance.get_stock_price(
            entities["symbol"], entities.get("exchange", "NSE"),
        )

    # --- Government handlers ---

    async def _handle_pmkisan(self, entities: dict) -> dict:
        return await self.government.check_pmkisan(
            mobile=entities.get("mobile"),
            aadhaar=entities.get("aadhaar"),
            registration_number=entities.get("registration_number"),
        )

    async def _handle_dl(self, entities: dict) -> dict:
        return await self.government.check_driving_license(
            entities["dl_number"], entities.get("dob"),
        )

    async def _handle_vehicle(self, entities: dict) -> dict:
        return await self.government.get_vehicle_info(entities["vehicle_number"])

    async def _handle_echallan(self, entities: dict) -> dict:
        return await self.government.check_echallan(
            vehicle_number=entities.get("vehicle_number"),
            challan_number=entities.get("challan_number"),
        )

    # --- Utility handlers ---

    async def _handle_weather(self, entities: dict) -> dict:
        city = entities.get("city", "Delhi")
        return await self.utility.get_weather(city)

    async def _handle_gold(self, entities: dict) -> dict:
        city = entities.get("city", "Delhi")
        return await self.utility.get_gold_price(city)

    async def _handle_fuel(self, entities: dict) -> dict:
        city = entities.get("city", "Delhi")
        return await self.utility.get_fuel_price(city)

    async def _handle_currency(self, entities: dict) -> dict:
        amount = entities.get("amount")
        base = entities.get("base", "USD")
        quote = entities.get("quote", "INR")

        if amount:
            return await self.utility.convert_currency(amount, base, quote)
        return await self.utility.get_currency_rate(base, quote)

    async def _handle_pincode(self, entities: dict) -> dict:
        return await self.utility.get_pincode_info(entities["pincode"])

    async def _handle_ifsc(self, entities: dict) -> dict:
        return await self.utility.get_ifsc_info(entities["ifsc"])

    async def _handle_holidays(self, entities: dict) -> dict:
        return await self.utility.get_holidays(
            year=entities.get("year", 2024),
            state=entities.get("state"),
        )

    async def close(self):
        """Close all service client connections."""
        for client in [self.travel, self.astrology, self.finance, self.government, self.utility]:
            await client.close()
