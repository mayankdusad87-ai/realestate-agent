"""
Configuration constants for the Real Estate Competition Analysis Engine.
"""

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS = 4000
GROQ_MAX_RETRIES = 2
GROQ_RETRY_DELAY_SECONDS = 3

SERPAPI_URL = "https://serpapi.com/search"
SERPAPI_NUM_RESULTS = 5
SERPAPI_COUNTRY = "in"
SERPAPI_LANGUAGE = "en"
SERPAPI_TIMEOUT = 12

LIVE_DATA_SNIPPET_LIMIT = 3500
LIVE_DATA_DISPLAY_LIMIT = 2500
MAX_COMPETITORS = 5

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

# ─────────────────────────────────────────────────────────────────────────────
# AGENT REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
AGENT_NAMES = {
    1: "Daily Command Brief",
    2: "Collections Chase Agent",
    3: "RERA Compliance Agent",
    4: "Broker Performance Agent",
    5: "Construction Progress Summariser",
    6: "Buyer Experience Agent",
    7: "Competitive Intelligence Agent",
    8: "Cash Flow Risk Agent",
    9: "Sales Team Performance Agent",
    10: "Channel Partner Performance Agent",
}

# ─────────────────────────────────────────────────────────────────────────────
# WHATSAPP BUSINESS API (Meta Cloud API)
# ─────────────────────────────────────────────────────────────────────────────
WHATSAPP_API_URL = "https://graph.facebook.com/v21.0"
WHATSAPP_API_TIMEOUT = 15

# ─────────────────────────────────────────────────────────────────────────────
# EMAIL (SMTP)
# ─────────────────────────────────────────────────────────────────────────────
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USE_TLS = True

# ─────────────────────────────────────────────────────────────────────────────
# GOOGLE SHEETS
# ─────────────────────────────────────────────────────────────────────────────
GOOGLE_CREDENTIALS_PATH = ""  # Path to service-account JSON; set via secrets
