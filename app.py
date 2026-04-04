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
    micromarket = st.text_input(
        "📍 Micro-market",
        placeholder="e.g. Goregaon West / Wakad / Whitefield"
    )

    budget = st.text_input(
        "💰 Budget Range",
        placeholder="e.g. ₹1.5 Cr – ₹2.5 Cr (target ticket size)"
    )

    configurations = st.text_input(
        "🏠 Configurations",
        placeholder="e.g. 2BHK (650 sqft), 3BHK (900 sqft)"
    )

with col2:
    city = st.text_input(
        "🏙️ City",
        placeholder="e.g. Mumbai / Pune / Bangalore"
    )

    product_type = st.selectbox(
        "🏢 Product Type",
        ["Residential", "Commercial", "Mixed-use", "Plotted Development"]
    )

    timeline = st.selectbox(
        "📅 Launch Timeline",
        ["Immediate (0-3 months)", "3-6 months", "6-12 months", "1+ year"]
    )

st.divider()

groq_key = st.text_input("🔑 Groq API Key", type="password")
serp_key = st.text_input("🔎 SerpAPI Key", type="password")

run = st.button("🚀 Run Market Analysis")

# ── FETCH DATA ──
def fetch_real_time_data(micromarket, city, serp_key):
    try:
        res = requests.get(
            "https://serpapi.com/search",
            params={"q": f"{micromarket} {city} property price", "api_key": serp_key},
            timeout=10
        )
        data = res.json()
        return " ".join([i.get("snippet", "") for i in data.get("organic_results", [])[:5]])
    except:
        return "No data found"

# ── RUN LOGIC ──
if run:

    if not micromarket or not city or not budget:
        st.error("Please fill required fields")

    elif not groq_key or not serp_key:
        st.error("Please add API keys")

    else:

        real_data = fetch_real_time_data(micromarket, city, serp_key)
        real_data = real_data[:2000]

        prompt = f"""
You are a Head of Pricing Strategy with 20+ years experience at top Indian developers like Lodha and Rustomjee.

PROJECT DETAILS:
- Micro-market: {micromarket}, {city}
- Budget range: {budget}
- Product type: {product_type}
- Configurations: {configurations}
- Launch timeline: {timeline}

REAL MARKET DATA:
{real_data}

----------------------------------------

## 1. MARKET REALITY
- True trading price
- Price band
- Buyer type

## 2. COMPETITOR POSITIONING
- Market leaders
- Undercutters
- Price gap
| Project | Developer | Price/sqft | Positioning |

## 3. PRICING STRATEGY

- Market median price

### Aggressive
- Launch Price: ₹X /sqft (PSF)
- All-in Price: ₹X Cr
- Absorption: X units/month

### Balanced
- Launch Price: ₹X /sqft (PSF)
- All-in Price: ₹X Cr
- Absorption: X units/month

### Premium
- Launch Price: ₹X /sqft (PSF)
- All-in Price: ₹X Cr
- Absorption: X units/month

IMPORTANT:
- Clearly show PSF and All-in separately

## 4. LAUNCH PLAN
- Phase pricing
- Floor rise

## 5. CONFIGURATION
- Sizes
- Ticket sizes

## 6. RISKS
- Pricing risk
- Inventory risk
- Demand risk

IMPORTANT:
- Complete all sections fully
"""

        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000
        )

        result = response.choices[0].message.content

        st.success("✅ Analysis Complete")

        # ── TABS ──
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Market",
            "🏢 Competitors",
            "💰 Pricing (PSF + All-in)",
            "🚀 Launch Plan",
            "🏠 Config",
            "⚠️ Risks"
        ])

        sections = result.split("##")

        def get_section(i):
            try:
                return sections[i]
            except:
                return "⚠️ Section missing"

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
