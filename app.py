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
You are a senior real estate strategy analyst specialising in Indian
residential markets with 15 years of experience.

A developer is planning to launch a project:
- Micro-market: {micromarket}, {city}
- Budget range: {budget}
- Product type: {product_type}
- Target configurations: {configurations}
- Launch timeline: {timeline}

IMPORTANT: I have fetched the following REAL-TIME data from Google
search results today. Use this as your PRIMARY data source.
Analyse it carefully and extract pricing, project names, and
market signals from it:

=== REAL-TIME MARKET DATA ===
{real_data}
=== END OF REAL-TIME DATA ===

Based on the above real data AND your own market knowledge,
provide a report with EXACTLY these 4 sections:

## 1. MARKET OVERVIEW
- What the real-time data tells us about current prices
- Price range seen in the data (minimum to maximum)
- Current market temperature based on the news found
- Buyer profile for this micro-market

## 2. COMPETITOR BENCHMARK
Extract real projects mentioned in the data above.
Fill gaps with your knowledge if needed.
| Project Name | Developer | Config | Price/sqft | All-in Price | Stage |

## 3. PRICING RECOMMENDATION
Based on the real data found:
- Recommended launch price per sqft with justification
- Price for each configuration (carpet area + all-in price)
- One payment scheme to offer buyers

## 4. TOP 3 RISKS
Based on the market signals in the real data:
List 3 risks with severity (High / Medium / Low) for each.

Always cite when using real-time data vs your own knowledge.
Be specific with rupee figures.
"""
            # Uses groq_key variable from the input box — never hardcoded
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content
            status.update(label="✅ Analysis complete!", state="complete")

        st.success("🎉 Real-time analysis complete!")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Market Overview",
            "🏢 Competitors",
            "💰 Pricing",
            "⚠️ Risks"
        ])

        sections = result.split("##")

        with tab1:
            st.markdown(sections[1] if len(sections) > 1 else result)
        with tab2:
            st.markdown(sections[2] if len(sections) > 2 else result)
        with tab3:
            st.markdown(sections[3] if len(sections) > 3 else result)
        with tab4:
            st.markdown(sections[4] if len(sections) > 4 else result)

        st.divider()
        st.download_button(
            label="📥 Download Full Report",
            data=result,
            file_name=f"{micromarket}_{city}_analysis.txt",
            mime="text/plain"
        )
