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
    .stButton > button {
        background-color: #B8860B;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        font-size: 15px;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #D4A017;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-text">🏗️ Real Estate Strategy Agent</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-text">AI-powered competitive intelligence '
            'with real-time market data</div>',
            unsafe_allow_html=True)

st.info(
    "📡 This tool fetches real-time data from Google search results "
    "and analyses it using AI. Always verify figures before client presentations."
)
st.divider()

# ── Input form ──
col1, col2 = st.columns(2)

with col1:
    micromarket = st.text_input("📍 Micro-market",
                                placeholder="e.g. Goregaon West")
    budget = st.text_input("💰 Budget Range",
                           placeholder="e.g. ₹1.5 Cr – ₹3 Cr")
    configurations = st.text_input("🏠 Configurations",
                                   placeholder="e.g. 2BHK and 3BHK")

with col2:
    city = st.text_input("🏙️ City",
                         placeholder="e.g. Mumbai, Pune, Bengaluru")
    product_type = st.selectbox("🏢 Product Type",
                                ["Residential", "Commercial",
                                 "Mixed-use", "Plotted Development"])
    timeline = st.selectbox("📅 Launch Timeline",
                            ["Immediate (0-3 months)",
                             "Short-term (3-6 months)",
                             "Mid-term (6-12 months)",
                             "Long-term (1-2 years)"])

st.divider()

# ── API Keys — entered by user in the app, never stored in code ──
col_a, col_b = st.columns(2)
with col_a:
    groq_key = st.text_input("🔑 Groq API Key",
                             type="password",
                             placeholder="Paste your new gsk_ key")
with col_b:
    serp_key = st.text_input("🔎 SerpAPI Key",
                             type="password",
                             placeholder="Paste your new SerpAPI key")

run = st.button("🚀 Run Real-Time Market Analysis")


def fetch_real_time_data(micromarket, city, serp_key):
    searches = [
        f"property price per sqft {micromarket} {city} 2024 2025",
        f"new residential projects launch {micromarket} {city} 2024 2025",
        f"real estate market {micromarket} {city} latest news"
    ]

    all_results = []

    for query in searches:
        try:
            response = requests.get(
                "https://serpapi.com/search",
                params={
                    "q": query,
                    "api_key": serp_key,
                    "num": 5,
                    "hl": "en",
                    "gl": "in"
                },
                timeout=10
            )
            data = response.json()

            if "organic_results" in data:
                for item in data["organic_results"][:5]:
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    source = item.get("source", "")
                    if snippet:
                        all_results.append(
                            f"Source: {source}\n"
                            f"Title: {title}\n"
                            f"Info: {snippet}"
                        )
        except Exception:
            all_results.append(f"Search unavailable for: {query}")
            continue

    return "\n\n---\n\n".join(all_results)


if run:
    if not micromarket or not city or not budget:
        st.error("Please fill in micro-market, city, and budget.")
    elif not groq_key:
        st.error("Please add your Groq API key.")
    elif not serp_key:
        st.error("Please add your SerpAPI key.")
    else:
        with st.status("🔍 Fetching real-time market data from Google...",
                       expanded=True) as status:
            st.write("Searching current property prices...")
            st.write("Searching active project launches...")
            st.write("Searching latest market news...")
            real_data = fetch_real_time_data(micromarket, city, serp_key)
            st.write("✅ Real-time data collected!")
            status.update(label="✅ Market data fetched!", state="complete")

        with st.expander("📄 View raw data fetched from Google"):
            st.text(real_data)

        with st.status("🤖 AI is analysing the real data...",
                       expanded=True) as status:
            st.write("Building strategic report...")

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
- When to use: (cash flow pressure / high inventory)

### Balanced (Optimal Strategy)
- Launch Price: ₹X
- Expected Absorption: X units/month
- Sweet spot between margin & speed

### Premium (Margin Play)
- Launch Price: ₹X
- Expected Absorption: X units/month
- Risk: slower movement

----------------------------------------

## 4. LAUNCH EXECUTION PLAN (VERY IMPORTANT)

Give:
- Phase 1 (first 20–25 units): ₹X
- Phase 2: ₹X
- Phase 3: ₹X

Also include:
- Floor rise logic (₹/floor)
- View premium (garden/road)

----------------------------------------

## 5. CONFIGURATION PRICING

Give:
- Carpet size assumptions
- Ticket size for each config
- Which config will sell fastest

----------------------------------------

## 6. KEY RISKS (REAL DEVELOPER RISKS)

- Pricing too high → absorption impact
- Inventory overhang
- Market sentiment

----------------------------------------

RULES:
- Be sharp, not generic
- Give numbers like a real pricing meeting
- Prioritise decision-making, not description
IMPORTANT:
- Complete ALL sections fully
- Do NOT stop mid-way
- Ensure Pricing Strategy section includes ALL 3 strategies in full detail
- Output must be complete and structured properly


Always cite when using real-time data vs your own knowledge.
Be specific with rupee figures.
"""
            # Uses groq_key variable from the input box — never hardcoded
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000
            )
            result = response.choices[0].message.content
            status.update(label="✅ Analysis complete!", state="complete")

        st.success("🎉 Real-time analysis complete!")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Market Reality",
    "🏢 Competitors",
    "💰 Pricing Strategy",
    "🚀 Launch Plan",
    "🏠 Configuration",
    "⚠️ Risks"
])
sections = result.split("##")
def get_section(index):
    try:
        return sections[index]
    except:
        return "⚠️ Section incomplete. Please re-run."
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
    
st.divider()
st.download_button(
            label="📥 Download Full Report",
            data=result,
            file_name=f"{micromarket}_{city}_analysis.txt",
            mime="text/plain"
        )
