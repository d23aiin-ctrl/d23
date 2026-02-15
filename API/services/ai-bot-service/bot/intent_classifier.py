"""Intent classification using LLM (OpenAI) with rule-based fallback."""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from bot.entity_extractor import (
    CURRENCY_MAP,
    STOCK_SYMBOLS,
    ZODIAC_MAP,
    extract_entities,
)
from bot.prompts import INTENT_CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    intent: str
    confidence: float
    entities: dict[str, Any] = field(default_factory=dict)


class IntentClassifier:
    """Classifies user messages into intents using LLM or rule-based fallback."""

    def __init__(self, openai_client=None, model: str = "gpt-4o-mini"):
        self._openai = openai_client
        self._model = model

    @property
    def llm_available(self) -> bool:
        return self._openai is not None

    async def classify(self, message: str) -> ClassificationResult:
        """Classify a user message into an intent with extracted entities."""
        if self.llm_available:
            try:
                return await self._classify_llm(message)
            except Exception as e:
                logger.warning("LLM classification failed, falling back to rules: %s", e)

        return self._classify_rules(message)

    async def _classify_llm(self, message: str) -> ClassificationResult:
        """Use OpenAI to classify intent and extract entities."""
        response = await self._openai.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": INTENT_CLASSIFICATION_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.1,
            max_tokens=300,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        return ClassificationResult(
            intent=data.get("intent", "unknown"),
            confidence=data.get("confidence", 0.8),
            entities=data.get("entities", {}),
        )

    def _classify_rules(self, message: str) -> ClassificationResult:
        """Rule-based intent classification using keywords and regex."""
        msg = message.strip()
        msg_lower = msg.lower()

        # Check greeting first
        if self._is_greeting(msg_lower):
            return ClassificationResult(intent="greeting", confidence=0.9, entities={})

        # Try each intent rule
        for intent, checker in self._rules():
            result = checker(msg, msg_lower)
            if result is not None:
                entities = extract_entities(msg, intent)
                return ClassificationResult(
                    intent=intent,
                    confidence=result,
                    entities=entities,
                )

        return ClassificationResult(intent="unknown", confidence=0.3, entities={})

    def _is_greeting(self, msg_lower: str) -> bool:
        greetings = {
            "hi", "hello", "hey", "help", "namaste", "namaskar", "नमस्ते",
            "नमस्कार", "hola", "good morning", "good evening", "good afternoon",
            "howdy", "start", "menu",
        }
        return msg_lower.strip().rstrip("!.") in greetings or msg_lower.startswith(("hi ", "hello ", "hey "))

    def _rules(self):
        """Return intent rules as (intent_name, checker_function) pairs."""
        # Order matters: keyword-specific intents before generic pattern-based ones
        return [
            ("pmkisan", self._check_pmkisan),
            ("ifsc", self._check_ifsc),
            ("pincode", self._check_pincode),
            ("driving_license", self._check_dl),
            ("echallan", self._check_echallan),
            ("vehicle_info", self._check_vehicle),
            ("pnr_status", self._check_pnr),
            ("train_search", self._check_train_search),
            ("train_schedule", self._check_train_schedule),
            ("train_status", self._check_train_status),
            ("horoscope", self._check_horoscope),
            ("kundli_match", self._check_kundli_match),
            ("kundli", self._check_kundli),
            ("panchang", self._check_panchang),
            ("emi_calculate", self._check_emi),
            ("sip_calculate", self._check_sip),
            ("stock_price", self._check_stock),
            ("weather", self._check_weather),
            ("gold_price", self._check_gold),
            ("fuel_price", self._check_fuel),
            ("currency", self._check_currency),
            ("holidays", self._check_holidays),
        ]

    def _check_pnr(self, msg: str, msg_lower: str) -> float | None:
        # Avoid matching 10-digit numbers that belong to other intents
        skip_keywords = {"pm kisan", "pmkisan", "pm-kisan", "kisan", "challan", "echallan"}
        if any(k in msg_lower for k in skip_keywords):
            return None
        if re.search(r"\bpnr\b", msg_lower) or re.search(r"\b\d{10}\b", msg):
            if "pnr" in msg_lower:
                return 0.95
            return 0.7
        return None

    def _check_train_search(self, msg: str, msg_lower: str) -> float | None:
        patterns = ["trains from", "train from", "trains between", "to train"]
        if any(p in msg_lower for p in patterns):
            return 0.9
        if re.search(r"\b\w+\s+to\s+\w+\s+train", msg_lower):
            return 0.85
        return None

    def _check_train_schedule(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["schedule", "timetable", "time table", "samay sarini"]
        if any(k in msg_lower for k in keywords):
            return 0.9
        if re.search(r"train\s+\d{4,5}", msg_lower) and "schedule" in msg_lower:
            return 0.95
        return None

    def _check_train_status(self, msg: str, msg_lower: str) -> float | None:
        keywords = [
            "running status", "train status", "where is train", "live status",
            "train location", "kahan hai",
        ]
        if any(k in msg_lower for k in keywords):
            return 0.9
        return None

    def _check_horoscope(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["horoscope", "rashifal", "राशिफल", "rashi", "zodiac", "राशि"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        for sign in ZODIAC_MAP:
            if sign in msg_lower or sign in msg:
                if any(w in msg_lower for w in ["horoscope", "rashifal", "today", "आज", "daily", "weekly"]):
                    return 0.85
                return 0.6
        return None

    def _check_kundli_match(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["kundli match", "kundali match", "match kundli", "kundli milan", "कुंडली मिलान", "gun milan"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.95
        return None

    def _check_kundli(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["kundli", "kundali", "birth chart", "janam kundli", "कुंडली", "जन्म कुंडली"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        return None

    def _check_panchang(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["panchang", "panchangam", "पंचांग", "tithi", "तिथि", "muhurat", "मुहूर्त", "shubh muhurat"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        return None

    def _check_emi(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["emi", "loan emi", "home loan", "car loan", "loan calculator"]
        if any(k in msg_lower for k in keywords):
            return 0.9
        if "loan" in msg_lower and ("%" in msg or "rate" in msg_lower):
            return 0.85
        return None

    def _check_sip(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["sip", "mutual fund", "sip calculator", "sip returns", "monthly investment"]
        if any(k in msg_lower for k in keywords):
            return 0.9
        return None

    def _check_stock(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["stock", "share", "share price", "stock price", "शेयर"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        for key in STOCK_SYMBOLS:
            if key in msg_lower:
                if any(w in msg_lower for w in ["price", "rate", "stock", "share", "value"]):
                    return 0.85
                return 0.6
        return None

    def _check_pmkisan(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["pm kisan", "pmkisan", "pm-kisan", "पीएम किसान", "kisan samman"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.95
        return None

    def _check_dl(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["driving license", "driving licence", "dl status", "dl number"]
        if any(k in msg_lower for k in keywords):
            return 0.9
        if re.search(r"\b[A-Z]{2}\d{13}\b", msg):
            return 0.85
        return None

    def _check_vehicle(self, msg: str, msg_lower: str) -> float | None:
        keywords = [
            "vehicle info", "vehicle number", "rc details", "registration",
            "car number", "gaadi number", "गाड़ी",
        ]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        if re.search(r"\b[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}\b", msg.upper()):
            if "challan" not in msg_lower:
                return 0.75
        return None

    def _check_echallan(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["challan", "e-challan", "echallan", "traffic fine", "चालान"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        return None

    def _check_weather(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["weather", "mausam", "मौसम", "temperature", "तापमान"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.95
        return None

    def _check_gold(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["gold", "sona", "सोना", "सोने का भाव", "gold rate", "gold price", "silver", "chandi", "चांदी"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        return None

    def _check_fuel(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["petrol", "diesel", "fuel", "पेट्रोल", "डीज़ल", "fuel price"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        return None

    def _check_currency(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["convert", "exchange rate", "currency", "dollar", "usd to inr", "forex"]
        if any(k in msg_lower for k in keywords):
            return 0.9
        # Check if two currency names appear
        found = sum(1 for key in CURRENCY_MAP if key in msg_lower)
        if found >= 2:
            return 0.85
        return None

    def _check_pincode(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["pincode", "pin code", "postal code", "पिनकोड"]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        if re.search(r"\b\d{6}\b", msg) and ("pin" in msg_lower or "area" in msg_lower):
            return 0.8
        return None

    def _check_ifsc(self, msg: str, msg_lower: str) -> float | None:
        keywords = ["ifsc", "bank branch"]
        if any(k in msg_lower for k in keywords):
            return 0.9
        if re.search(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", msg.upper()):
            return 0.85
        return None

    def _check_holidays(self, msg: str, msg_lower: str) -> float | None:
        keywords = [
            "holiday", "holidays", "public holiday", "छुट्टी", "छुट्टियां",
            "bank holiday", "gazetted holiday",
        ]
        if any(k in msg_lower or k in msg for k in keywords):
            return 0.9
        return None
