"""
Kundli Node for WhatsApp Bot

Uses the enhanced kundli handler with:
- Swiss Ephemeris calculations for accuracy
- Beautiful Hindi formatting with emojis
- Web-enhanced astrological insights
- Multi-language support (11+ Indian languages)
"""

import logging
from whatsapp_bot.state import BotState

# Import the enhanced kundli handler from common
from common.graph.nodes.kundli_node import handle_birth_chart

logger = logging.getLogger(__name__)

INTENT = "birth_chart"

# Export the handle_birth_chart function directly from kundli_node
# This function now:
# 1. Uses Swiss Ephemeris for accurate planetary calculations
# 2. Formats in beautiful Hindi/English narrative style
# 3. Web-enhanced astrological interpretations
# 4. Provides detailed life predictions
# 5. Supports all 11 Indian languages
# 6. Includes personality, career, relationships analysis

__all__ = ['handle_birth_chart', 'INTENT']
