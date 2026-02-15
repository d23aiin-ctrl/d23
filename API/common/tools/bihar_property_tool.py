"""
Bihar Property Registration Tool

Provides information about property registration, stamp duty, and related charges in Bihar.
Data source: enibandhan.bihar.gov.in and official government notifications.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from common.config.settings import settings
from common.graph.state import ToolResult

logger = logging.getLogger(__name__)


class BiharPropertyInfo:
    """Bihar property registration information and rates."""

    # Stamp Duty Rates (as % of property value)
    STAMP_DUTY_MALE = 6.3  # Male buyers
    STAMP_DUTY_FEMALE = 5.7  # Female buyers

    # Registration Charges
    REGISTRATION_FEE = 2.0  # 2% of property market value (all buyers)

    # Gender-specific adjustments
    MALE_TO_FEMALE_REBATE = 0.4  # Woman buying from man gets 0.4% rebate
    FEMALE_TO_MALE_SURCHARGE = 0.4  # Man buying from woman pays 0.4% extra

    # Mukhyamantri Bas Sthal Kray Yojana
    SCHEME_MAX_VALUE = 60000  # Properties up to Rs. 60,000 are exempt

    # Important information
    REGISTRATION_DEADLINE_MONTHS = 4  # Must register within 4 months
    MAX_PENALTY_MULTIPLIER = 10  # Up to 10x registration charges as penalty

    # Tax benefits
    INCOME_TAX_DEDUCTION_80C = 150000  # Rs. 1.5 lakh deduction available

    OFFICIAL_PORTALS = {
        "e-Nibandhan": "https://enibandhan.bihar.gov.in",
        "Bhumijankari": "https://bhumijankari.bihar.gov.in",
        "OGRAS Payment": "https://ogras.bihar.gov.in"
    }

    SERVICES_AVAILABLE = [
        "Document Registration",
        "Certified Copy",
        "Encumbrance Certificate",
        "Marriage Registration",
        "Online Payment",
        "Society Registration",
        "Firm Registration",
        "Application/Challan Status",
        "Grievance Management"
    ]

    EXEMPTIONS = [
        "Industrial properties (100% exemption)",
        "Lands for industrial purposes within/outside industrial zones",
        "Properties under Mukhyamantri Bas Sthal Kray Yojana (up to Rs. 60,000)"
    ]


def calculate_charges(
    property_value: float,
    buyer_gender: str = "male",
    seller_gender: Optional[str] = None,
    is_industrial: bool = False
) -> Dict[str, Any]:
    """
    Calculate stamp duty and registration charges.

    Args:
        property_value: Market value of property in Rupees
        buyer_gender: "male" or "female"
        seller_gender: Optional seller gender for cross-gender adjustments
        is_industrial: Whether property is for industrial use

    Returns:
        Dictionary with breakdown of all charges
    """
    buyer_gender = buyer_gender.lower()

    # Industrial properties are exempt
    if is_industrial:
        return {
            "property_value": property_value,
            "stamp_duty": 0,
            "registration_fee": 0,
            "total_charges": 0,
            "exemption": "Industrial property - 100% exempt",
            "breakdown": "Industrial properties are fully exempt from stamp duty and registration charges in Bihar."
        }

    # Mukhyamantri Bas Sthal Kray Yojana exemption
    if property_value <= BiharPropertyInfo.SCHEME_MAX_VALUE:
        return {
            "property_value": property_value,
            "stamp_duty": 0,
            "registration_fee": 0,
            "total_charges": 0,
            "exemption": "Mukhyamantri Bas Sthal Kray Yojana",
            "breakdown": f"Properties up to Rs. {BiharPropertyInfo.SCHEME_MAX_VALUE:,.0f} are exempt under the scheme."
        }

    # Base stamp duty based on buyer gender
    if buyer_gender == "female":
        stamp_duty_rate = BiharPropertyInfo.STAMP_DUTY_FEMALE
    else:
        stamp_duty_rate = BiharPropertyInfo.STAMP_DUTY_MALE

    # Cross-gender adjustments
    adjustment_rate = 0
    adjustment_note = ""

    if seller_gender:
        seller_gender = seller_gender.lower()
        if buyer_gender == "male" and seller_gender == "female":
            adjustment_rate = BiharPropertyInfo.FEMALE_TO_MALE_SURCHARGE
            adjustment_note = "Additional 0.4% surcharge (man buying from woman)"
        elif buyer_gender == "female" and seller_gender == "male":
            adjustment_rate = -BiharPropertyInfo.MALE_TO_FEMALE_REBATE
            adjustment_note = "0.4% rebate (woman buying from man)"

    # Calculate charges
    final_stamp_duty_rate = stamp_duty_rate + adjustment_rate
    stamp_duty = (final_stamp_duty_rate / 100) * property_value
    registration_fee = (BiharPropertyInfo.REGISTRATION_FEE / 100) * property_value
    total_charges = stamp_duty + registration_fee

    breakdown = f"""**Calculation Breakdown:**

**Property Value:** ₹{property_value:,.2f}

**Stamp Duty:**
- Base rate ({buyer_gender.title()}): {stamp_duty_rate}%
{f"- {adjustment_note}" if adjustment_note else ""}
- Effective rate: {final_stamp_duty_rate}%
- **Stamp Duty Amount:** ₹{stamp_duty:,.2f}

**Registration Fee:**
- Rate: {BiharPropertyInfo.REGISTRATION_FEE}% (applicable to all)
- **Registration Amount:** ₹{registration_fee:,.2f}

**Total Charges:** ₹{total_charges:,.2f}

**Important Notes:**
- Registration must be completed within 4 months
- Late registration may attract penalty up to 10x the charges
- Tax deduction up to ₹1.5 lakh available under Section 80C
"""

    return {
        "property_value": property_value,
        "stamp_duty_rate": final_stamp_duty_rate,
        "stamp_duty": stamp_duty,
        "registration_fee": registration_fee,
        "total_charges": total_charges,
        "breakdown": breakdown
    }


def get_general_info(query_type: str = "general") -> str:
    """
    Get general information about Bihar property registration.

    Args:
        query_type: Type of information requested

    Returns:
        Formatted information string
    """
    info = f"""**Bihar Property Registration Information**

**Stamp Duty Rates:**
- Male buyers: {BiharPropertyInfo.STAMP_DUTY_MALE}% of property value
- Female buyers: {BiharPropertyInfo.STAMP_DUTY_FEMALE}% of property value
- Cross-gender adjustments: ±0.4%

**Registration Charges:**
- {BiharPropertyInfo.REGISTRATION_FEE}% of property market value (all buyers)

**Important Deadlines:**
- Registration must be completed within {BiharPropertyInfo.REGISTRATION_DEADLINE_MONTHS} months of transaction
- Late registration penalty: Up to {BiharPropertyInfo.MAX_PENALTY_MULTIPLIER}x the registration charges

**Exemptions:**
{chr(10).join(f"- {exemption}" for exemption in BiharPropertyInfo.EXEMPTIONS)}

**Tax Benefits:**
- Income tax deduction up to ₹{BiharPropertyInfo.INCOME_TAX_DEDUCTION_80C:,} under Section 80C

**Online Services Available:**
{chr(10).join(f"- {service}" for service in BiharPropertyInfo.SERVICES_AVAILABLE[:5])}

**Official Portals:**
{chr(10).join(f"- {name}: {url}" for name, url in BiharPropertyInfo.OFFICIAL_PORTALS.items())}

**How to Register:**
1. Visit https://enibandhan.bihar.gov.in
2. Select "Document Registration"
3. Pay stamp duty & registration fee online
4. Submit required documents
5. Get registration certificate

**Contact:**
- 137 registry offices across Bihar
- Online grievance management available
"""
    return info


async def handle_property_query(
    query: str,
    property_value: Optional[float] = None,
    buyer_gender: Optional[str] = None,
    seller_gender: Optional[str] = None,
    language: str = "en"
) -> ToolResult:
    """
    Handle property registration queries using AI.

    Args:
        query: User's question about property registration
        property_value: Optional property value for calculations
        buyer_gender: Optional buyer gender
        seller_gender: Optional seller gender
        language: Response language

    Returns:
        ToolResult with property registration information
    """
    try:
        # If property value is provided, calculate charges
        calculation_info = ""
        if property_value:
            calc_result = calculate_charges(
                property_value=property_value,
                buyer_gender=buyer_gender or "male",
                seller_gender=seller_gender
            )
            calculation_info = calc_result.get("breakdown", "")

        # Get general information
        general_info = get_general_info()

        # Combine information
        context = f"{general_info}\n\n{calculation_info}"

        # Use LLM to provide contextual answer
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Bihar property registration expert assistant.

Use the following information to answer the user's question about property registration in Bihar:

{context}

Provide accurate, helpful information. If calculations were done, include them in your response.
Be concise but complete. Always include relevant official portal links.
"""),
            ("user", "{query}")
        ])

        chain = prompt | llm
        response = await chain.ainvoke({
            "context": context,
            "query": query
        })

        answer = response.content

        # Add official sources
        answer += f"\n\n**Official Resources:**\n"
        for name, url in BiharPropertyInfo.OFFICIAL_PORTALS.items():
            answer += f"- {name}: {url}\n"

        return ToolResult(
            success=True,
            output=answer,
            metadata={
                "source": "Bihar e-Nibandhan Portal",
                "calculation_done": property_value is not None,
                "language": language
            }
        )

    except Exception as e:
        logger.error(f"Error in property query handler: {e}")
        return ToolResult(
            success=False,
            error=f"Failed to fetch property information: {str(e)}",
            output=get_general_info()
        )


def handle_property_query_sync(
    query: str,
    property_value: Optional[float] = None,
    buyer_gender: Optional[str] = None,
    seller_gender: Optional[str] = None,
    language: str = "en"
) -> ToolResult:
    """Synchronous version of handle_property_query."""
    try:
        # If property value is provided, calculate charges
        if property_value:
            calc_result = calculate_charges(
                property_value=property_value,
                buyer_gender=buyer_gender or "male",
                seller_gender=seller_gender
            )
            response = calc_result.get("breakdown", "")
            response += f"\n\n{get_general_info()}"
        else:
            response = get_general_info()

        return ToolResult(
            success=True,
            data={
                "output": response,
                "source": "Bihar e-Nibandhan Portal",
                "calculation_done": property_value is not None,
                "language": language
            },
            error=None,
            tool_name="bihar_property"
        )

    except Exception as e:
        logger.error(f"Error in property query handler: {e}")
        return ToolResult(
            success=False,
            data={"output": get_general_info()},
            error=f"Failed to fetch property information: {str(e)}",
            tool_name="bihar_property"
        )
