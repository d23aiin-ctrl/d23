"""
Astrology Node for WhatsApp Bot

Uses the new web-based horoscope handler with real-time data and beautiful Hindi formatting.
Handles horoscope and astrology queries with multilingual support (11+ Indian languages).
"""

import logging
from typing import Dict

from whatsapp_bot.state import BotState

# Import the new web-based horoscope handler
from common.graph.nodes.horoscope_node import handle_horoscope

logger = logging.getLogger(__name__)

INTENT = "get_horoscope"

# Export the handle_horoscope function directly from horoscope_node
# This function now:
# 1. Fetches real-time data from the web (Aaj Tak, Navbharat Times, etc.)
# 2. Shows ALL horoscopes when no sign is specified
# 3. Shows detailed horoscope for a specific sign
# 4. Formats in beautiful Hindi narrative style
# 5. Supports all 11 Indian languages
# 6. Includes professional life, love life, lucky details, sources

__all__ = ['handle_horoscope', 'INTENT']
