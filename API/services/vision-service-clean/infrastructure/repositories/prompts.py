"""Prompts for different vision analysis tasks."""

DESCRIBE_PROMPT = """Describe this image in detail. Include:
- Main subjects and their appearance
- Setting and background
- Colors and composition
- Any text visible
- Overall mood or context

{language_instruction}"""

EXTRACT_TEXT_PROMPT = """Extract ALL text visible in this image.
- Include text from signs, labels, documents, screens, etc.
- Preserve the original formatting and structure as much as possible
- If text is in regional scripts (Hindi, Kannada, Tamil, Telugu, etc.), include it as-is
- If no text is found, respond with "No text found"

{language_instruction}"""

DETECT_OBJECTS_PROMPT = """List all objects visible in this image.
Format each object on a new line as: "object_name"
Be comprehensive and include:
- Main subjects
- Background objects
- Small items
- Text/signs if visible

Only list object names, nothing else."""

ANALYZE_DOCUMENT_PROMPT = """Analyze this document image and extract:
1. Document type (ID card, form, certificate, letter, receipt, etc.)
2. Title or heading if visible
3. Key fields and their values (names, dates, numbers, etc.)
4. Any important text content

Format as:
DOCUMENT_TYPE: [type]
TITLE: [title if any]
FIELDS:
- [field_name]: [value]
- [field_name]: [value]
RAW_TEXT: [all visible text]

{language_instruction}"""

ANALYZE_RECEIPT_PROMPT = """Analyze this receipt/bill image and extract:
1. Merchant/Store name
2. Date of transaction
3. List of items with quantities and prices
4. Subtotal, tax, and total amount
5. Payment method if visible

Format as:
MERCHANT: [name]
DATE: [date]
ITEMS:
- [item name] x[qty] @ [price]
- [item name] x[qty] @ [price]
TAX: [amount]
TOTAL: [amount]
PAYMENT: [method]"""

IDENTIFY_FOOD_PROMPT = """Identify the food items in this image:
1. List each food item/dish visible
2. Identify the cuisine type (Indian, Chinese, Italian, etc.)
3. Is it vegetarian or non-vegetarian?
4. Estimate calories if possible
5. Brief description of the dish

Format as:
ITEMS: [item1], [item2], [item3]
CUISINE: [cuisine type]
VEGETARIAN: [yes/no/unknown]
CALORIES: [estimated range or unknown]
DESCRIPTION: [brief description]

{language_instruction}"""

CUSTOM_QUERY_PROMPT = """{query}

{language_instruction}"""


def get_language_instruction(language: str) -> str:
    """Get instruction for response language."""
    lang_map = {
        "en": "Respond in English.",
        "hi": "Respond in Hindi (Devanagari script).",
        "kn": "Respond in Kannada.",
        "ta": "Respond in Tamil.",
        "te": "Respond in Telugu.",
        "mr": "Respond in Marathi.",
        "gu": "Respond in Gujarati.",
        "bn": "Respond in Bengali.",
        "ml": "Respond in Malayalam.",
        "pa": "Respond in Punjabi.",
        "or": "Respond in Odia.",
    }
    return lang_map.get(language, "Respond in English.")


def get_prompt(task: str, language: str = "en", query: str = "") -> str:
    """Get the appropriate prompt for a task."""
    lang_instruction = get_language_instruction(language)

    prompts = {
        "describe": DESCRIBE_PROMPT,
        "extract_text": EXTRACT_TEXT_PROMPT,
        "detect_objects": DETECT_OBJECTS_PROMPT,
        "analyze_document": ANALYZE_DOCUMENT_PROMPT,
        "analyze_receipt": ANALYZE_RECEIPT_PROMPT,
        "identify_food": IDENTIFY_FOOD_PROMPT,
        "custom_query": CUSTOM_QUERY_PROMPT,
    }

    prompt_template = prompts.get(task, DESCRIBE_PROMPT)

    return prompt_template.format(
        language_instruction=lang_instruction,
        query=query,
    ).strip()
