"""Format raw API responses into conversational chat messages."""

import json
import logging
from typing import Any

from bot.prompts import RESPONSE_FORMAT_PROMPT

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formats API responses using LLM or template-based fallback."""

    def __init__(self, openai_client=None, model: str = "gpt-4o-mini"):
        self._openai = openai_client
        self._model = model

    @property
    def llm_available(self) -> bool:
        return self._openai is not None

    async def format(self, intent: str, data: dict[str, Any], user_message: str = "") -> str:
        """Format a service response into a user-friendly message."""
        # If the response already has a pre-formatted message, return it
        if "message" in data and isinstance(data["message"], str):
            return data["message"]

        # Unwrap service envelope
        data = self._unwrap_data(data)

        # Check for error responses
        if data.get("error"):
            detail = data.get("detail", "Something went wrong")
            if isinstance(detail, dict):
                detail = detail.get("detail", detail.get("message", str(detail)))
            return f"Sorry, there was an issue: {detail}"

        if self.llm_available:
            try:
                return await self._format_llm(intent, data, user_message)
            except Exception as e:
                logger.warning("LLM formatting failed, using template: %s", e)

        return self._format_template(intent, data)

    async def _format_llm(self, intent: str, data: dict, user_message: str) -> str:
        """Use LLM to format the response conversationally."""
        prompt = (
            f"User asked: \"{user_message}\"\n"
            f"Intent: {intent}\n"
            f"API Response:\n```json\n{json.dumps(data, indent=2, default=str)}\n```\n\n"
            "Format this into a friendly, concise chat response. Use emoji where appropriate. "
            "Format numbers with Indian numbering (lakhs/crores). Keep it short."
        )

        response = await self._openai.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": RESPONSE_FORMAT_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=500,
        )

        return response.choices[0].message.content

    @staticmethod
    def _unwrap_data(data: dict) -> dict:
        """Unwrap common service response envelope like {"success": ..., "data": {...}}."""
        if "data" in data and isinstance(data["data"], dict):
            return data["data"]
        return data

    def _format_template(self, intent: str, data: dict) -> str:
        """Template-based response formatting."""
        data = self._unwrap_data(data)
        formatters = {
            "pnr_status": self._fmt_pnr,
            "train_schedule": self._fmt_train_schedule,
            "train_status": self._fmt_train_status,
            "train_search": self._fmt_train_search,
            "horoscope": self._fmt_horoscope,
            "kundli": self._fmt_generic,
            "panchang": self._fmt_panchang,
            "emi_calculate": self._fmt_emi,
            "sip_calculate": self._fmt_sip,
            "stock_price": self._fmt_stock,
            "pmkisan": self._fmt_pmkisan,
            "driving_license": self._fmt_dl,
            "vehicle_info": self._fmt_vehicle,
            "echallan": self._fmt_echallan,
            "weather": self._fmt_weather,
            "gold_price": self._fmt_gold,
            "fuel_price": self._fmt_fuel,
            "currency": self._fmt_currency,
            "pincode": self._fmt_pincode,
            "ifsc": self._fmt_ifsc,
            "holidays": self._fmt_holidays,
        }

        formatter = formatters.get(intent, self._fmt_generic)
        try:
            return formatter(data)
        except Exception as e:
            logger.warning("Template formatting error for %s: %s", intent, e)
            return self._fmt_generic(data)

    # --- Template formatters ---

    def _fmt_pnr(self, d: dict) -> str:
        pnr = d.get("pnr_number", d.get("pnr", "N/A"))
        train = d.get("train_name", d.get("train", ""))
        train_no = d.get("train_number", "")
        status = d.get("status", d.get("booking_status", ""))
        doj = d.get("date_of_journey", d.get("journey_date", ""))

        lines = [f"🚂 **PNR Status: {pnr}**"]
        if train:
            lines.append(f"Train: {train_no} - {train}" if train_no else f"Train: {train}")
        if doj:
            lines.append(f"Journey Date: {doj}")
        if status:
            lines.append(f"Status: **{status}**")

        passengers = d.get("passengers", [])
        if passengers:
            lines.append("\n**Passengers:**")
            for i, p in enumerate(passengers, 1):
                name = p.get("name", f"Passenger {i}")
                bk = p.get("booking_status", p.get("status", "N/A"))
                cur = p.get("current_status", bk)
                lines.append(f"  {i}. {name} - Booking: {bk} | Current: {cur}")

        return "\n".join(lines)

    def _fmt_train_schedule(self, d: dict) -> str:
        name = d.get("train_name", "Train")
        number = d.get("train_number", "")
        lines = [f"🚂 **{number} - {name} Schedule**"]

        stations = d.get("stations", d.get("schedule", []))
        if stations:
            for s in stations[:15]:  # Limit to 15 stations
                stn = s.get("station_name", s.get("station", ""))
                code = s.get("station_code", s.get("code", ""))
                arr = s.get("arrival", s.get("arrives", "--"))
                dep = s.get("departure", s.get("departs", "--"))
                lines.append(f"  {code} ({stn}) - Arr: {arr} | Dep: {dep}")
        else:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_train_status(self, d: dict) -> str:
        name = d.get("train_name", "Train")
        number = d.get("train_number", "")
        status = d.get("status", d.get("running_status", ""))
        delay = d.get("delay", d.get("delay_minutes", ""))

        lines = [f"🚂 **{number} - {name} Running Status**"]
        if status:
            lines.append(f"Status: **{status}**")
        if delay:
            lines.append(f"Delay: {delay} minutes")

        last_station = d.get("last_station", d.get("current_station", ""))
        if last_station:
            lines.append(f"Last/Current Station: {last_station}")

        return "\n".join(lines)

    def _fmt_train_search(self, d: dict) -> str:
        trains = d.get("trains", d.get("results", []))
        if not trains:
            return "No trains found for this route. Please check station codes."

        lines = ["🚂 **Trains Found:**\n"]
        for t in trains[:10]:
            name = t.get("train_name", t.get("name", ""))
            number = t.get("train_number", t.get("number", ""))
            dep = t.get("departure", t.get("departs", ""))
            arr = t.get("arrival", t.get("arrives", ""))
            lines.append(f"  **{number}** - {name}")
            if dep or arr:
                lines.append(f"    Dep: {dep} → Arr: {arr}")

        return "\n".join(lines)

    def _fmt_horoscope(self, d: dict) -> str:
        sign = d.get("sign", d.get("zodiac", ""))
        prediction = d.get("prediction", d.get("horoscope", d.get("message", "")))
        lucky_number = d.get("lucky_number", "")
        lucky_color = d.get("lucky_color", "")

        lines = [f"🔮 **{sign.title()} Horoscope**"]
        if prediction:
            lines.append(f"\n{prediction}")
        if lucky_number:
            lines.append(f"\nLucky Number: {lucky_number}")
        if lucky_color:
            lines.append(f"Lucky Color: {lucky_color}")

        return "\n".join(lines)

    def _fmt_panchang(self, d: dict) -> str:
        date = d.get("date", "Today")
        tithi = d.get("tithi", "")
        nakshatra = d.get("nakshatra", "")
        yoga = d.get("yoga", "")
        karana = d.get("karana", "")

        lines = [f"🙏 **Panchang for {date}**"]
        if tithi:
            lines.append(f"Tithi: {tithi}")
        if nakshatra:
            lines.append(f"Nakshatra: {nakshatra}")
        if yoga:
            lines.append(f"Yoga: {yoga}")
        if karana:
            lines.append(f"Karana: {karana}")

        sunrise = d.get("sunrise", "")
        sunset = d.get("sunset", "")
        if sunrise:
            lines.append(f"Sunrise: {sunrise}")
        if sunset:
            lines.append(f"Sunset: {sunset}")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_emi(self, d: dict) -> str:
        emi = d.get("emi", d.get("monthly_emi", 0))
        principal = d.get("principal", d.get("loan_amount", 0))
        total_interest = d.get("total_interest", 0)
        total_payment = d.get("total_payment", d.get("total_amount", 0))

        lines = ["💰 **EMI Calculation**"]
        if principal:
            lines.append(f"Loan Amount: {self._fmt_inr(principal)}")
        lines.append(f"**Monthly EMI: {self._fmt_inr(emi)}**")
        if total_interest:
            lines.append(f"Total Interest: {self._fmt_inr(total_interest)}")
        if total_payment:
            lines.append(f"Total Payment: {self._fmt_inr(total_payment)}")

        rate = d.get("annual_rate", d.get("interest_rate", ""))
        tenure = d.get("tenure_months", d.get("tenure", ""))
        if rate:
            lines.append(f"Interest Rate: {rate}%")
        if tenure:
            years = int(tenure) // 12
            months = int(tenure) % 12
            t_str = f"{years} years" if years else ""
            if months:
                t_str += f" {months} months"
            lines.append(f"Tenure: {t_str.strip()}")

        return "\n".join(lines)

    def _fmt_sip(self, d: dict) -> str:
        invested = d.get("total_invested", d.get("invested_amount", 0))
        returns = d.get("estimated_returns", d.get("wealth_gained", 0))
        total = d.get("total_value", d.get("maturity_amount", 0))

        lines = ["📈 **SIP Calculator**"]
        if invested:
            lines.append(f"Total Invested: {self._fmt_inr(invested)}")
        if returns:
            lines.append(f"Estimated Returns: {self._fmt_inr(returns)}")
        if total:
            lines.append(f"**Total Value: {self._fmt_inr(total)}**")

        monthly = d.get("monthly_investment", "")
        duration = d.get("duration_years", "")
        rate = d.get("expected_return_rate", d.get("return_rate", ""))
        if monthly:
            lines.append(f"Monthly SIP: {self._fmt_inr(monthly)}")
        if duration:
            lines.append(f"Duration: {duration} years")
        if rate:
            lines.append(f"Expected Return: {rate}%")

        return "\n".join(lines)

    def _fmt_stock(self, d: dict) -> str:
        symbol = d.get("symbol", d.get("ticker", ""))
        name = d.get("name", d.get("company_name", symbol))
        price = d.get("price", d.get("current_price", d.get("ltp", "")))
        change = d.get("change", d.get("price_change", ""))
        change_pct = d.get("change_percent", d.get("percent_change", ""))
        exchange = d.get("exchange", "NSE")

        lines = [f"📊 **{symbol} ({name})** - {exchange}"]
        if price:
            lines.append(f"Current Price: **₹{price}**")
        if change is not None and change != "":
            arrow = "🟢" if float(str(change).replace(",", "")) >= 0 else "🔴"
            lines.append(f"{arrow} Change: ₹{change} ({change_pct}%)" if change_pct else f"{arrow} Change: ₹{change}")

        high = d.get("high", d.get("day_high", ""))
        low = d.get("low", d.get("day_low", ""))
        if high and low:
            lines.append(f"Day Range: ₹{low} - ₹{high}")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_pmkisan(self, d: dict) -> str:
        status = d.get("status", d.get("beneficiary_status", ""))
        name = d.get("name", d.get("farmer_name", ""))
        lines = ["🌾 **PM Kisan Status**"]
        if name:
            lines.append(f"Name: {name}")
        if status:
            lines.append(f"Status: **{status}**")

        installments = d.get("installments", d.get("payments", []))
        if installments:
            lines.append("\n**Recent Installments:**")
            for inst in installments[:5]:
                amt = inst.get("amount", "")
                date = inst.get("date", inst.get("paid_on", ""))
                lines.append(f"  - ₹{amt} on {date}")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_dl(self, d: dict) -> str:
        dl = d.get("dl_number", d.get("license_number", ""))
        name = d.get("name", d.get("holder_name", ""))
        status = d.get("status", "")
        validity = d.get("validity", d.get("valid_till", ""))

        lines = ["🪪 **Driving License Status**"]
        if dl:
            lines.append(f"DL Number: {dl}")
        if name:
            lines.append(f"Name: {name}")
        if status:
            lines.append(f"Status: **{status}**")
        if validity:
            lines.append(f"Valid Till: {validity}")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_vehicle(self, d: dict) -> str:
        reg = d.get("registration_number", d.get("vehicle_number", ""))
        owner = d.get("owner_name", d.get("owner", ""))
        make = d.get("make", d.get("manufacturer", ""))
        model = d.get("model", "")
        fuel = d.get("fuel_type", "")
        status = d.get("status", d.get("registration_status", ""))

        lines = [f"🚗 **Vehicle Info: {reg}**"]
        if owner:
            lines.append(f"Owner: {owner}")
        if make or model:
            lines.append(f"Vehicle: {make} {model}".strip())
        if fuel:
            lines.append(f"Fuel: {fuel}")
        if status:
            lines.append(f"Status: **{status}**")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_echallan(self, d: dict) -> str:
        challans = d.get("challans", d.get("results", []))
        if isinstance(d, list):
            challans = d

        if not challans:
            pending = d.get("pending_amount", "")
            if pending:
                return f"🚨 **E-Challan Status**\nPending Amount: ₹{pending}"
            return "🚨 **E-Challan Status**\n" + self._fmt_key_value(d)

        lines = ["🚨 **E-Challan Results:**"]
        total = 0
        for c in challans[:5]:
            amt = c.get("amount", c.get("fine", 0))
            date = c.get("date", c.get("violation_date", ""))
            violation = c.get("violation", c.get("offense", ""))
            lines.append(f"  - {violation} | ₹{amt} | {date}")
            total += float(str(amt).replace(",", "") or 0)

        if total:
            lines.append(f"\n**Total Pending: ₹{total:,.0f}**")

        return "\n".join(lines)

    def _fmt_weather(self, d: dict) -> str:
        city = d.get("city", d.get("location", d.get("name", "")))
        temp = d.get("temperature", d.get("temp", ""))
        feels_like = d.get("feels_like", "")
        desc = d.get("description", d.get("condition", d.get("weather", "")))
        humidity = d.get("humidity", "")
        wind = d.get("wind_speed", d.get("wind", ""))

        lines = [f"🌤 **Weather in {city}**"]
        if temp:
            t_str = f"Temperature: {temp}°C"
            if feels_like:
                t_str += f" (Feels like {feels_like}°C)"
            lines.append(t_str)
        if desc:
            lines.append(f"Condition: {desc}")
        if humidity:
            lines.append(f"Humidity: {humidity}%")
        if wind:
            lines.append(f"Wind: {wind} km/h")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_gold(self, d: dict) -> str:
        city = d.get("city", "India")
        gold_24k = d.get("gold_24k", d.get("gold_price", d.get("gold", "")))
        gold_22k = d.get("gold_22k", "")
        silver = d.get("silver", d.get("silver_price", ""))

        lines = [f"🥇 **Gold & Silver Prices ({city})**"]
        if gold_24k:
            lines.append(f"Gold (24K): ₹{gold_24k}/10g")
        if gold_22k:
            lines.append(f"Gold (22K): ₹{gold_22k}/10g")
        if silver:
            lines.append(f"Silver: ₹{silver}/kg")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_fuel(self, d: dict) -> str:
        city = d.get("city", "")
        petrol = d.get("petrol", d.get("petrol_price", ""))
        diesel = d.get("diesel", d.get("diesel_price", ""))

        lines = [f"⛽ **Fuel Prices in {city}**"]
        if petrol:
            lines.append(f"Petrol: ₹{petrol}/litre")
        if diesel:
            lines.append(f"Diesel: ₹{diesel}/litre")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_currency(self, d: dict) -> str:
        base = d.get("base", d.get("from", "USD"))
        quote = d.get("quote", d.get("to", "INR"))
        rate = d.get("rate", d.get("exchange_rate", ""))
        converted = d.get("converted_amount", d.get("result", ""))
        amount = d.get("amount", "")

        lines = [f"💱 **Currency Exchange**"]
        if amount and converted:
            lines.append(f"{amount} {base} = **{converted} {quote}**")
        elif rate:
            lines.append(f"1 {base} = **{rate} {quote}**")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_pincode(self, d: dict) -> str:
        pincode = d.get("pincode", d.get("pin", ""))
        area = d.get("area", d.get("office_name", d.get("post_office", "")))
        district = d.get("district", "")
        state = d.get("state", "")

        lines = [f"📍 **Pincode: {pincode}**"]
        if area:
            lines.append(f"Area: {area}")
        if district:
            lines.append(f"District: {district}")
        if state:
            lines.append(f"State: {state}")

        offices = d.get("post_offices", [])
        if offices:
            lines.append("\n**Post Offices:**")
            for o in offices[:5]:
                name = o.get("name", o.get("office_name", ""))
                lines.append(f"  - {name}")

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_ifsc(self, d: dict) -> str:
        ifsc = d.get("ifsc", d.get("code", ""))
        bank = d.get("bank", d.get("bank_name", ""))
        branch = d.get("branch", d.get("branch_name", ""))
        address = d.get("address", "")
        city = d.get("city", "")
        state = d.get("state", "")

        lines = [f"🏦 **IFSC: {ifsc}**"]
        if bank:
            lines.append(f"Bank: {bank}")
        if branch:
            lines.append(f"Branch: {branch}")
        if address:
            lines.append(f"Address: {address}")
        elif city or state:
            lines.append(f"Location: {city}, {state}".strip(", "))

        if len(lines) == 1:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_holidays(self, d: dict) -> str:
        year = d.get("year", "")
        holidays = d.get("holidays", d.get("results", []))

        lines = [f"📅 **Public Holidays {year}**"]
        if holidays:
            for h in holidays[:15]:
                name = h.get("name", h.get("holiday", ""))
                date = h.get("date", "")
                htype = h.get("type", "")
                lines.append(f"  - {date}: **{name}**" + (f" ({htype})" if htype else ""))
        else:
            lines.append(self._fmt_key_value(d))

        return "\n".join(lines)

    def _fmt_generic(self, d: dict) -> str:
        """Generic key-value formatter as last resort."""
        return self._fmt_key_value(d)

    def _fmt_key_value(self, d: dict) -> str:
        """Format a dict as key-value pairs."""
        lines = []
        for k, v in d.items():
            if k.startswith("_") or v is None:
                continue
            key_display = k.replace("_", " ").title()
            if isinstance(v, dict):
                lines.append(f"**{key_display}:**")
                for sk, sv in v.items():
                    lines.append(f"  {sk.replace('_', ' ').title()}: {sv}")
            elif isinstance(v, list):
                if v and isinstance(v[0], dict):
                    lines.append(f"**{key_display}:** {len(v)} items")
                else:
                    lines.append(f"{key_display}: {', '.join(str(x) for x in v)}")
            else:
                lines.append(f"{key_display}: {v}")
        return "\n".join(lines) if lines else "No data available."

    @staticmethod
    def _fmt_inr(amount) -> str:
        """Format a number in Indian currency style."""
        try:
            amt = float(str(amount).replace(",", ""))
        except (ValueError, TypeError):
            return str(amount)

        if amt >= 10000000:
            return f"₹{amt / 10000000:.2f} Cr"
        elif amt >= 100000:
            return f"₹{amt / 100000:.2f} L"
        else:
            return f"₹{amt:,.0f}"
