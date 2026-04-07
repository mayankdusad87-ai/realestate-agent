import streamlit as st
from groq import Groq
import requests

st.set_page_config(
    page_title="RE Strategy Agent",
    page_icon="🏗️",
    layout="wide"
)

st.markdown("""
<style>
.title-text {font-size:32px;font-weight:700;color:#B8860B;}
.sub-text {font-size:14px;color:#888;margin-bottom:24px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">🏗️ Real Estate Strategy Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">AI-powered pricing decision engine</div>', unsafe_allow_html=True)

st.divider()

# ── INPUTS ──
col1, col2 = st.columns(2)

with col1:
    micromarket = st.text_input("📍 Micro-market", placeholder="e.g. Goregaon West")
    budget = st.text_input("💰 Budget", placeholder="₹1.5–2.5 Cr")
    configurations = st.text_input("🏠 Config", placeholder="2BHK (650), 3BHK (900)")

with col2:
    city = st.text_input("🏙️ City", placeholder="Mumbai")
    product_type = st.selectbox("🏢 Type", ["Residential","Commercial"])
    timeline = st.selectbox("📅 Timeline", ["0-3","3-6","6-12"])

st.divider()

groq_key = st.text_input("Groq Key", type="password")
serp_key = st.text_input("Serp Key", type="password")

run = st.button("Run Analysis")

# ── FETCH DATA ──
def fetch_data(micromarket, city, serp_key):
    try:
        res = requests.get(
            "https://serpapi.com/search",
            params={"q": f"{micromarket} {city} property price", "api_key": serp_key}
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
You are a Head of Pricing Strategy.

PROJECT:
{micromarket}, {city}
Budget: {budget}
Config: {configurations}

DATA:
{real_data}

SECTION_1: MARKET
- price
- demand

SECTION_2: COMPETITORS
- key players

SECTION_3: PRICING
Aggressive:
₹X/sqft
All-in ₹X Cr

Balanced:
₹X/sqft
All-in ₹X Cr

Premium:
₹X/sqft
All-in ₹X Cr

SECTION_4: LAUNCH
- phase pricing

SECTION_5: CONFIG
- sizes

SECTION_6: RISKS
- key risks

IMPORTANT:
use all sections properly
"""

        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            max_tokens=2000
        )

        result = response.choices[0].message.content

        st.success("Done")

        # ── TABS ──
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Market","Competitors","Pricing (PSF + All-in)","Launch","Config","Risks"
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

        st.download_button("Download Report", result)
