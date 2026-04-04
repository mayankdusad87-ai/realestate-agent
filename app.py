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
    .title-text {
        font-size: 32px;
        font-weight: 700;
        color: #B8860B;
    }
    .sub-text {
        font-size: 14px;
        color: #888888;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">🏗️ Real Estate Strategy Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">AI-powered competitive intelligence with real-time market data</div>', unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    micromarket = st.text_input("📍 Micro-market")
    budget = st.text_input("💰 Budget Range")
    configurations = st.text_input("🏠 Configurations")

with col2:
    city = st.text_input("🏙️ City")
    product_type = st.selectbox("🏢 Product Type", ["Residential","Commercial","Mixed-use","Plotted Development"])
    timeline = st.selectbox("📅 Launch Timeline", ["0-3","3-6","6-12","12+"])

st.divider()

groq_key = st.text_input("🔑 Groq API Key", type="password")
serp_key = st.text_input("🔎 SerpAPI Key", type="password")

run = st.button("🚀 Run Analysis")


def fetch_real_time_data(micromarket, city, serp_key):
    try:
        res = requests.get(
            "https://serpapi.com/search",
            params={"q": f"{micromarket} {city} property price", "api_key": serp_key}
        )
        data = res.json()
        return " ".join([i.get("snippet","") for i in data.get("organic_results",[])[:5]])
    except:
        return "No data found"


if run:

    if not micromarket or not city or not budget:
        st.error("Please fill required fields")

    elif not groq_key or not serp_key:
        st.error("Add API keys")

    else:

        real_data = fetch_real_time_data(micromarket, city, serp_key)
        real_data = real_data[:2000]

        prompt = f"""
You are a Head of Pricing Strategy with 20+ years experience at top
Indian developers like Lodha and Rustomjee.

You do NOT give generic reports. You give sharp, decision-oriented
pricing strategies focused on absorption, cash flow and margin.

PROJECT DETAILS:
- Micro-market: {micromarket}, {city}
- Budget range: {budget}
- Product type: {product_type}
- Configurations: {configurations}
- Launch timeline: {timeline}

You are also given REAL-TIME MARKET DATA below. This is your base input.

=== REAL MARKET DATA ===
{real_data}
=== END ===

Your job is to think like a developer launching inventory and answer:
👉 What price should I launch at?
👉 How will sales move at different prices?
👉 How should I phase pricing?

----------------------------------------

## 1. MARKET REALITY (NO FLUFF)
- True market trading price (not advertised)
- Realistic price band (min–max)
- Inventory pressure (high / moderate / low)
- Who is actually buying (end-user / investor)

----------------------------------------

## 2. COMPETITOR POSITIONING
Do NOT just list projects.

Explain:
- Who is premium leader
- Who is undercutting
- Where is price gap in market

Then give table:
| Project | Developer | Price/sqft | Positioning |

----------------------------------------

## 3. PRICING STRATEGY (CORE SECTION)

FIRST:
- Market median price

THEN give 3 clear strategies:

### Aggressive (Velocity Play)
- Launch Price: ₹X
- Expected Absorption: X units/month

### Balanced (Optimal Strategy)
- Launch Price: ₹X
- Expected Absorption: X units/month

### Premium (Margin Play)
- Launch Price: ₹X
- Expected Absorption: X units/month

----------------------------------------

## 4. LAUNCH EXECUTION PLAN

- Phase 1 price
- Phase 2 price
- Phase 3 price

----------------------------------------

## 5. CONFIGURATION PRICING

- Sizes
- Ticket size

----------------------------------------

## 6. KEY RISKS

- Pricing risk
- Inventory risk
- Demand risk

IMPORTANT:
- Complete ALL sections
"""

        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000
        )

        result = response.choices[0].message.content

        st.success("Analysis Complete")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Market Reality",
            "🏢 Competitors",
            "💰 Pricing",
            "🚀 Launch",
            "🏠 Config",
            "⚠️ Risks"
        ])

        sections = result.split("##")

        def get_section(i):
            try:
                return sections[i]
            except:
                return "Section missing"

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
