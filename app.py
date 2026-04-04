import streamlit as st
from groq import Groq
import requests

st.set_page_config(
    page_title="RE Strategy Agent",
    page_icon="🏗️",
    layout="wide"
)

st.title("🏗️ Real Estate Strategy Agent")
st.caption("AI-powered pricing decision engine for developers")

# ── INPUTS ──
col1, col2 = st.columns(2)

with col1:
    micromarket = st.text_input("📍 Micro-market",placeholder="e.g. Goregaon West"))
    budget = st.text_input("💰 Budget Range")
    configurations = st.text_input("🏠 Configurations")

with col2:
    city = st.text_input("🏙️ City")
    product_type = st.selectbox("🏢 Product Type",
                                ["Residential", "Commercial",
                                 "Mixed-use", "Plotted"])
    timeline = st.selectbox("📅 Timeline",
                            ["0-3 months", "3-6 months",
                             "6-12 months"])

st.divider()

groq_key = st.text_input("🔑 Groq API Key", type="password")
serp_key = st.text_input("🔎 SerpAPI Key", type="password")

run = st.button("🚀 Run Analysis")

# ── FETCH DATA ──
def fetch_data(micromarket, city, serp_key):
    query = f"property price {micromarket} {city}"
    try:
        res = requests.get(
            "https://serpapi.com/search",
            params={"q": query, "api_key": serp_key},
            timeout=10
        )
        data = res.json()

        snippets = []
        for item in data.get("organic_results", [])[:5]:
            if item.get("snippet"):
                snippets.append(item["snippet"])

        return "\n".join(snippets)

    except:
        return "No data found"


# ── RUN ──
if run:
    if not micromarket or not city or not groq_key or not serp_key:
        st.error("Fill all required fields")
    else:
        with st.spinner("Fetching market data..."):
            real_data = fetch_data(micromarket, city, serp_key)

        # 🔴 CRITICAL: Trim data
        real_data = real_data[:2000]

        prompt = f"""
You are a Head of Pricing Strategy with 20+ years experience at Lodha & Rustomjee.

Think like a developer.

PROJECT:
- {micromarket}, {city}
- Budget: {budget}
- Config: {configurations}

DATA:
{real_data}

OUTPUT FORMAT:

SECTION_1: MARKET REALITY
- True price
- Price band
- Buyer type

SECTION_2: COMPETITOR POSITIONING
Explain market gap + table

SECTION_3: PRICING STRATEGY
Give:
- Aggressive price + absorption
- Balanced price + absorption
- Premium price + absorption

SECTION_4: LAUNCH PLAN
- Phase pricing
- Floor rise

SECTION_5: CONFIGURATION
- Sizes
- Ticket size

SECTION_6: RISKS
- Key risks

IMPORTANT:
- Complete ALL sections
- Give numbers
"""

        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000
        )

        result = response.choices[0].message.content

        st.success("Analysis Complete")

        # 🔥 FIXED PARSING
        sections = result.split("SECTION_")

        def get_section(i):
            try:
                return sections[i]
            except:
                return "⚠️ Missing section"

        # ── TABS ──
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Market",
            "Competitors",
            "Pricing",
            "Launch",
            "Config",
            "Risks"
        ])

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
