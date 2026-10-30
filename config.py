"""
Configuration constants for the Real Estate Competition Analysis Engine.
"""
from pathlib import Path

# Phase 1 fact memory (SQLite). Local file next to the app; override the env-style
# constant to point at durable storage on an ephemeral host (see memory_store.py).
MEMORY_DB_PATH = str(Path(__file__).parent / "re_memory.db")

GROQ_MODEL = "openai/gpt-oss-120b"
# Groq's free tier allows ~8,000 tokens/minute, and max_tokens is RESERVED against
# that limit (input + max_tokens must fit). We size the output budget DYNAMICALLY
# at call time (GROQ_TPM_BUDGET - estimated input), capped by GROQ_MAX_TOKENS, so we
# use all the room left for the report without ever exceeding the per-minute limit.
GROQ_TPM_BUDGET = 8000          # per-minute token limit of the tier (raise on paid)
GROQ_MAX_TOKENS = 5000          # ceiling on output tokens (used when input is small)
GROQ_MIN_OUTPUT_TOKENS = 1500   # floor; below this the report can't complete
GROQ_TPM_SAFETY_MARGIN = 500    # keep clear of the hard limit
GROQ_TEMPERATURE = 0            # deterministic: we want grounded extraction, not creative prose
GROQ_MAX_RETRIES = 2
GROQ_RETRY_DELAY_SECONDS = 3

SERPAPI_URL = "https://serpapi.com/search"
SERPAPI_NUM_RESULTS = 5
SERPAPI_COUNTRY = "in"
SERPAPI_LANGUAGE = "en"
SERPAPI_TIMEOUT = 20

# Fetching the actual pages behind the top results (not just Google snippets).
PAGE_FETCH_ENABLED = True
MAX_PAGES_TO_FETCH = 6          # unique URLs fetched across all queries (bounds runtime)
PAGE_FETCH_TIMEOUT = 8          # seconds per page
PAGE_TEXT_CHAR_LIMIT = 1200     # chars of extracted text kept per page
PAGE_FETCH_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# Char budget for the sources block in the prompt. Kept small so the input leaves
# enough of the TPM budget for the output; raise it on a paid Groq tier.
LIVE_DATA_SNIPPET_LIMIT = 4500
LIVE_DATA_DISPLAY_LIMIT = 6000   # char budget for the "raw data" expander in the UI
MAX_COMPETITORS = 5
MAX_MEMORY_FACTS = 20            # cap remembered facts injected into the prompt (bounds tokens)

PRODUCT_TYPES = ["Residential", "Commercial", "Mixed-use", "Plots", "Warehousing"]

LAUNCH_TIMELINES = [
    "Immediate (0-3 months)",
    "Short-term (3-6 months)",
    "Mid-term (6-12 months)",
    "Long-term (1-2 years)",
]

CITY_TO_STATE = {
    "mumbai": "maharashtra",
    "pune": "maharashtra",
    "thane": "maharashtra",
    "nagpur": "maharashtra",
    "nashik": "maharashtra",
    "bengaluru": "karnataka",
    "bangalore": "karnataka",
    "mysuru": "karnataka",
    "hyderabad": "telangana",
    "warangal": "telangana",
    "delhi": "delhi",
    "noida": "uttar pradesh",
    "gurgaon": "haryana",
    "gurugram": "haryana",
    "faridabad": "haryana",
    "ahmedabad": "gujarat",
    "surat": "gujarat",
    "vadodara": "gujarat",
    "jaipur": "rajasthan",
    "jodhpur": "rajasthan",
    "chennai": "tamil nadu",
    "coimbatore": "tamil nadu",
    "kolkata": "west bengal",
    "bhubaneswar": "odisha",
    "lucknow": "uttar pradesh",
    "kanpur": "uttar pradesh",
    "chandigarh": "punjab",
    "ludhiana": "punjab",
    "bhopal": "madhya pradesh",
    "indore": "madhya pradesh",
}

RERA_PORTALS = {
    "maharashtra": "maharera.mahaonline.gov.in",
    "karnataka": "rera.karnataka.gov.in",
    "telangana": "rera.telangana.gov.in",
    "delhi": "rera.delhi.gov.in",
    "uttar pradesh": "up-rera.in",
    "haryana": "haryanarera.gov.in",
    "gujarat": "gujrera.gujarat.gov.in",
    "rajasthan": "rera.rajasthan.gov.in",
    "tamil nadu": "tnrera.in",
    "west bengal": "hira.wb.gov.in",
    "punjab": "rera.punjab.gov.in",
    "madhya pradesh": "rera.mp.gov.in",
}
