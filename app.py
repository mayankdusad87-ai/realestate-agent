import streamlit as st
from groq import Groq
import requests

st.set_page_config(
    page_title="RE Competition Analysis",
    page_icon="🏗️",
    layout="wide"
)

st.markdown("""
<style>
.title-text {font-size:32px;font-weight:700;color:#B8860B;}
.sub-text {font-size:14px;color:#888;margin-bottom:24px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">🏗️ Real Estate Competition Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">AI-powered micro-market competitor intelligence</div>', unsafe_allow_html=True)

st.divider()

# ── INPUTS ──
col1, col2 = st.columns(2)

with col1:
    micromarket = st.text_input(
        "📍 Micro-market",
        placeholder="e.g. Goregaon West"
    )

with col2:
    city = st.text_input(
        "🏙️ City",
        placeholder="e.g. Mumbai"
    )

product_type = st.selectbox(
    "🏢 Product Type",
    ["Residential", "Commercial"]
)

st.divider()

groq_key = st.text_input("Groq Key", type="password")
serp_key = st.text_input("Serp Key", type="password")

run = st.button("Run Competition Analysis")

# ── FETCH DATA ──
def fetch_data(micromarket, city, serp_key):
    try:
        res = requests.get(
            "https://serpapi.com/search",
            params={"q": f"{micromarket} {city} real estate projects pricing", "api_key": serp_key}
        )
        data = res.json()
        return " ".join([i.get("snippet","") for i in data.get("organic_results",[])[:5]])
    except:
        return "No data"

# ── RUN ──
if run:

    if not micromarket or not city or not groq_key or not serp_key:
        st.error("Fill all fields")

    else:

        real_data = fetch_data(micromarket, city, serp_key)
        real_data = real_data[:2000]

        prompt = f"""
You are a real estate market research expert.

Your task is to do a COMPETITION ANALYSIS for the given micro-market.

LOCATION:
{micromarket}, {city}

PRODUCT TYPE:
{product_type}

REAL MARKET DATA:
{real_data}

----------------------------------------

SECTION_1: MARKET OVERVIEW
- Current price range (₹/sqft)
- Market trend (rising / stable / slow)
- Buyer profile

SECTION_2: COMPETITOR PROJECTS
Provide 4–6 key projects:
| Project | Developer | Config | Carpet Size | Price/sqft | Stage |

SECTION_3: PRODUCT ANALYSIS
- What configurations are being offered (2BHK/3BHK mix)
- Typical carpet sizes
- What is selling fastest
- What is slow-moving

SECTION_4: PRICING ANALYSIS
- PSF range in market
- All-in price range
- Premium vs budget positioning

SECTION_5: MARKET GAPS
- What is missing in the market
- Opportunities for new developer

SECTION_6: RISKS
- Oversupply risk
- Pricing pressure
- Demand mismatch

IMPORTANT:
- Be specific with numbers
- Focus on competition, not suggestions
"""

        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            max_tokens=2500
        )

        result = response.choices[0].message.content

        st.success("✅ Competition Analysis Ready")

        # ── TABS ──
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Market",
            "🏢 Projects",
            "🏠 Product",
            "💰 Pricing",
            "📈 Gaps",
            "⚠️ Risks"
        ])

        sections = result.split("SECTION_")

        def get_section(i):
            return sections[i] if i < len(sections) else "Missing"

        with tab1:
            st.markdown(get_section(1))

        with tab2:
            st.markdown(get_section(2))

        with tab3:
            st.markdown(get_section(3))

        with tab4:
            st.markdown(get_section(4))

        with tab5:
            st.markdown(get_section(5))

        with tab6:
            st.markdown(get_section(6))

        st.download_button("📥 Download Report", result)
