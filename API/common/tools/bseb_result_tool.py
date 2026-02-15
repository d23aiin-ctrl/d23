"""
BSEB Result Information Tool

Provides information about checking Bihar School Examination Board (BSEB) matric results.
"""

import logging
import re
from typing import Optional, Dict, Any
import httpx
from bs4 import BeautifulSoup
from common.graph.state import ToolResult

logger = logging.getLogger(__name__)


class BSEBResultInfo:
    """Information about BSEB result checking process."""

    # Official websites
    OFFICIAL_WEBSITES = {
        "Primary": "https://results.biharboardonline.com/",
        "Alternative 1": "https://matricbiharboard.com/",
        "Alternative 2": "https://matricresult2025.com/",
        "Alternative 3": "https://www.results.shiksha/bihar/matric.htm",
    }

    # SMS service details
    SMS_FORMAT = "BIHAR10 <Roll Number>"
    SMS_NUMBER = "56263"
    SMS_EXAMPLE = "BIHAR10 123456"

    # Result announcement details
    RESULT_ANNOUNCEMENT_DATE = "29th March 2025"
    RESULT_ANNOUNCEMENT_TIME = "12:00 PM"

    # Exam details
    EXAM_START_DATE = "17th February 2025"
    EXAM_END_DATE = "25th February 2025"
    TOTAL_STUDENTS = "15,85,868"

    # Result checking endpoints
    RESULT_ENDPOINTS = [
        "https://results.biharboardonline.com/",
        "https://www.results.shiksha/bihar/matric.htm",
    ]


def extract_roll_code_and_number(text: str) -> Dict[str, Optional[str]]:
    """
    Extract roll code and roll number from user message.
    Supports both English and Hindi text.

    Args:
        text: User message

    Returns:
        Dict with 'roll_code' and 'roll_number' keys
    """
    result = {"roll_code": None, "roll_number": None}

    # Pattern 1: English and Hindi patterns for "roll code" and "roll number"
    roll_code_patterns = [
        r'(?:roll\s*code|code)\s*[:\-]?\s*(\d{3,6})',  # English
        r'(?:रोल\s*कोड|कोड)\s*[:\-]?\s*(\d{3,6})',  # Hindi
    ]
    roll_number_patterns = [
        r'(?:roll\s*(?:number|no)|number)\s*[:\-]?\s*(\d{4,10})',  # English
        r'(?:रोल\s*(?:नंबर|नम्बर)|नंबर|नम्बर)\s*[:\-]?\s*(\d{4,10})',  # Hindi
    ]

    # Try English patterns on lowercased text
    text_lower = text.lower()
    for pattern in roll_code_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if not match:
            match = re.search(pattern, text)  # Try original text for Hindi
        if match:
            result["roll_code"] = match.group(1)
            break

    for pattern in roll_number_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if not match:
            match = re.search(pattern, text)  # Try original text for Hindi
        if match:
            result["roll_number"] = match.group(1)
            break

    # Pattern 2: Two numbers separated by space/comma (first is code, second is number)
    if not result["roll_code"] or not result["roll_number"]:
        two_numbers = re.findall(r'\b(\d{3,6})\s*[,\s]\s*(\d{4,10})\b', text)
        if two_numbers:
            result["roll_code"] = two_numbers[0][0]
            result["roll_number"] = two_numbers[0][1]

    return result


async def fetch_bseb_result(roll_code: str, roll_number: str) -> Dict[str, Any]:
    """
    Fetch BSEB result from the official website.

    Args:
        roll_code: Student's roll code
        roll_number: Student's roll number

    Returns:
        Dictionary containing result data or error information
    """
    try:
        # Try multiple endpoints
        for endpoint in BSEBResultInfo.RESULT_ENDPOINTS:
            try:
                async with httpx.AsyncClient(verify=False, timeout=15.0) as client:
                    # First, get the form page to understand structure
                    response = await client.get(endpoint)

                    if response.status_code != 200:
                        continue

                    # Parse the form to find the submission endpoint
                    soup = BeautifulSoup(response.text, 'html.parser')
                    form = soup.find('form')

                    if not form:
                        continue

                    # Get form action URL
                    action = form.get('action', '')
                    if not action.startswith('http'):
                        action = endpoint.rstrip('/') + '/' + action.lstrip('/')

                    # Prepare form data
                    form_data = {
                        'rollCode': roll_code,
                        'rollNumber': roll_number,
                        'regdNo': roll_number,  # Some forms use this
                    }

                    # Find all input fields in the form and add them
                    for input_field in form.find_all('input'):
                        name = input_field.get('name')
                        value = input_field.get('value', '')
                        if name and name not in form_data:
                            form_data[name] = value

                    # Submit the form
                    result_response = await client.post(action, data=form_data, follow_redirects=True)

                    if result_response.status_code != 200:
                        continue

                    # Parse result page
                    result_soup = BeautifulSoup(result_response.text, 'html.parser')

                    # Check for error messages
                    error_indicators = ['not found', 'invalid', 'incorrect', 'error', 'नहीं मिला']
                    page_text = result_soup.get_text().lower()

                    if any(indicator in page_text for indicator in error_indicators):
                        continue

                    # Extract result data
                    result_data = extract_result_from_html(result_soup)

                    if result_data:
                        return {
                            "success": True,
                            "data": result_data,
                            "source": endpoint
                        }

            except Exception as e:
                logger.warning(f"Failed to fetch from {endpoint}: {e}")
                continue

        # If all endpoints failed
        return {
            "success": False,
            "error": "Could not fetch result from BSEB website. Please try again later or check directly on the official website.",
            "roll_code": roll_code,
            "roll_number": roll_number
        }

    except Exception as e:
        logger.error(f"Error fetching BSEB result: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to fetch result: {str(e)}",
            "roll_code": roll_code,
            "roll_number": roll_number
        }


def extract_result_from_html(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """
    Extract result data from HTML page.

    Args:
        soup: BeautifulSoup object of result page

    Returns:
        Dictionary with extracted result data or None
    """
    try:
        result = {}

        # Look for common result table patterns
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)

                    # Map common field names
                    if 'name' in key and 'student' in key.lower():
                        result['student_name'] = value
                    elif 'roll' in key and 'number' in key:
                        result['roll_number'] = value
                    elif 'roll' in key and 'code' in key:
                        result['roll_code'] = value
                    elif 'status' in key or 'result' in key:
                        result['status'] = value
                    elif 'percentage' in key or '%' in key:
                        result['percentage'] = value
                    elif 'total' in key and 'marks' in key:
                        result['total_marks'] = value
                    elif 'obtained' in key or 'scored' in key:
                        result['obtained_marks'] = value
                    elif 'division' in key or 'grade' in key:
                        result['division'] = value

        # Look for subject-wise marks
        subjects = []
        for row in soup.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                # Check if this looks like a subject row
                first_cell = cells[0].get_text(strip=True)
                if any(subj in first_cell.lower() for subj in ['science', 'math', 'english', 'hindi', 'social']):
                    subject_data = {
                        'subject': first_cell,
                        'marks': cells[1].get_text(strip=True) if len(cells) > 1 else ''
                    }
                    subjects.append(subject_data)

        if subjects:
            result['subjects'] = subjects

        # Return result only if we found meaningful data
        if len(result) > 0:
            return result

        return None

    except Exception as e:
        logger.error(f"Error extracting result from HTML: {e}")
        return None


def format_result_output(result_data: Dict[str, Any]) -> str:
    """
    Format result data into human-readable text.

    Args:
        result_data: Dictionary containing result information

    Returns:
        Formatted result string
    """
    output = "**🎓 BSEB Matric Result 2025**\n\n"

    # Student details
    if 'student_name' in result_data:
        output += f"**Student Name:** {result_data['student_name']}\n"
    if 'roll_code' in result_data:
        output += f"**Roll Code:** {result_data['roll_code']}\n"
    if 'roll_number' in result_data:
        output += f"**Roll Number:** {result_data['roll_number']}\n"

    output += "\n"

    # Result status
    if 'status' in result_data:
        status_emoji = "✅" if "pass" in result_data['status'].lower() else "❌"
        output += f"**Result:** {status_emoji} {result_data['status']}\n"

    # Marks
    if 'obtained_marks' in result_data:
        output += f"**Obtained Marks:** {result_data['obtained_marks']}"
        if 'total_marks' in result_data:
            output += f" / {result_data['total_marks']}"
        output += "\n"

    if 'percentage' in result_data:
        output += f"**Percentage:** {result_data['percentage']}\n"

    if 'division' in result_data:
        output += f"**Division/Grade:** {result_data['division']}\n"

    # Subject-wise marks
    if 'subjects' in result_data and result_data['subjects']:
        output += "\n**📚 Subject-wise Marks:**\n"
        for subject in result_data['subjects']:
            output += f"- {subject['subject']}: {subject['marks']}\n"

    output += "\n✅ **Result fetched successfully from BSEB official website**"

    return output


def get_result_check_info() -> str:
    """
    Get comprehensive information about checking BSEB matric results.

    Returns:
        Formatted information string
    """
    info = f"""**Bihar Board (BSEB) Matric Result 2025 Information**

📅 **Result Announcement:**
- Date: {BSEBResultInfo.RESULT_ANNOUNCEMENT_DATE}
- Time: {BSEBResultInfo.RESULT_ANNOUNCEMENT_TIME}

📝 **How to Check Your Result Online:**

**Step 1:** Visit any official website:
{chr(10).join(f"- {name}: {url}" for name, url in BSEBResultInfo.OFFICIAL_WEBSITES.items())}

**Step 2:** Enter Your Details:
- Roll Code (from your admit card)
- Roll Number (from your admit card)

**Step 3:** Click "Submit" to view your result

📱 **Check via SMS:**
- Format: {BSEBResultInfo.SMS_FORMAT}
- Send to: {BSEBResultInfo.SMS_NUMBER}
- Example: {BSEBResultInfo.SMS_EXAMPLE}
- You'll receive your result on the same mobile number

📋 **Important Information:**
- Both Roll Code AND Roll Number are required
- These are printed on your BSEB 10th Admit Card
- Total students appeared: {BSEBResultInfo.TOTAL_STUDENTS}

🔍 **What You'll Get:**
- Overall marks and percentage
- Subject-wise marks
- Pass/Fail status
- Division/Grade
- Downloadable marksheet

⚠️ **Important Notes:**
- Keep your admit card handy before checking
- Results are available 24/7 once declared
- Take a screenshot or download your marksheet
- For discrepancies, contact BSEB Patna

📞 **Contact BSEB:**
- Official Website: http://biharboardonline.bihar.gov.in/
- For queries about results, visit the official portal

💡 **Tip:** If websites are slow due to heavy traffic, try:
1. Checking during off-peak hours (late night/early morning)
2. Using alternative official websites
3. Using the SMS method
"""
    return info


def get_result_format_info() -> str:
    """
    Get information about roll number format and requirements.

    Returns:
        Formatted information string
    """
    info = """**BSEB Roll Number Format Information**

📌 **What You Need:**
1. **Roll Code**: A unique code for your examination center
2. **Roll Number**: Your individual registration number

📍 **Where to Find:**
- Both are printed on your BSEB Class 10 Admit Card
- Usually in format: Roll Code is separate from Roll Number
- Example Roll Number: 123456 (6 digits typically)

✅ **Before Checking Results:**
- Keep your admit card ready
- Check the spelling of your name on admit card
- Note down both Roll Code and Roll Number correctly

❌ **Common Mistakes to Avoid:**
- Entering only roll number without roll code
- Swapping roll code and roll number
- Using last year's credentials
- Missing leading zeros in roll number

📞 **If You Lost Your Admit Card:**
- Contact your school principal
- Visit the examination center
- Call BSEB helpline for assistance
"""
    return info


async def handle_bseb_result_query(
    query: str,
    roll_number: Optional[str] = None,
    roll_code: Optional[str] = None,
    language: str = "en"
) -> ToolResult:
    """
    Handle BSEB result related queries.

    Args:
        query: User's question about BSEB results
        roll_number: Optional roll number if mentioned
        roll_code: Optional roll code if mentioned
        language: Language code (en/hi)

    Returns:
        ToolResult with result information
    """
    try:
        query_lower = query.lower()

        # Extract roll code and number if not provided
        if not roll_code or not roll_number:
            extracted = extract_roll_code_and_number(query)
            roll_code = roll_code or extracted.get("roll_code")
            roll_number = roll_number or extracted.get("roll_number")

        # If both roll code and number are available, fetch actual result
        if roll_code and roll_number:
            logger.info(f"Fetching BSEB result for roll code: {roll_code}, roll number: {roll_number}")

            result_data = await fetch_bseb_result(roll_code, roll_number)

            if result_data.get("success"):
                # Format and return the actual result
                response = format_result_output(result_data["data"])

                return ToolResult(
                    success=True,
                    data={
                        "output": response,
                        "result_data": result_data["data"],
                        "source": result_data.get("source", "BSEB Official Website"),
                        "language": language
                    },
                    error=None,
                    tool_name="bseb_result"
                )
            else:
                # Failed to fetch result, provide instructions
                error_msg = result_data.get("error", "Could not fetch result")
                response = f"""❌ **Unable to fetch result automatically**

{error_msg}

**Your Details:**
- Roll Code: {roll_code}
- Roll Number: {roll_number}

{get_result_check_info()}
"""
                return ToolResult(
                    success=True,
                    data={
                        "output": response,
                        "source": "Bihar School Examination Board (BSEB)",
                        "language": language
                    },
                    error=None,
                    tool_name="bseb_result"
                )

        # Determine what information to provide
        if any(word in query_lower for word in ["format", "roll number", "roll code", "admit card"]):
            response = get_result_format_info()
        elif roll_number or roll_code:
            # User provided partial information
            response = f"""**⚠️ Incomplete Information**

To check your BSEB result, I need both:
1. **Roll Code** (from your admit card)
2. **Roll Number** (from your admit card)

"""
            if roll_code:
                response += f"✅ Roll Code provided: {roll_code}\n"
            else:
                response += "❌ Roll Code missing\n"

            if roll_number:
                response += f"✅ Roll Number provided: {roll_number}\n"
            else:
                response += "❌ Roll Number missing\n"

            response += f"\n{get_result_check_info()}"
        else:
            # General result information
            response = get_result_check_info()

        return ToolResult(
            success=True,
            data={
                "output": response,
                "source": "Bihar School Examination Board (BSEB)",
                "language": language
            },
            error=None,
            tool_name="bseb_result"
        )

    except Exception as e:
        logger.error(f"Error in BSEB result query handler: {e}", exc_info=True)
        return ToolResult(
            success=False,
            data={"output": get_result_check_info()},
            error=f"Failed to process query: {str(e)}",
            tool_name="bseb_result"
        )
