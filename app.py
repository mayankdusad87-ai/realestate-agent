import streamlit as st
from groq import Groq
import requests
from pptx import Presentation
from pptx.util import Inches

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
    micromarket = st.text_input("📍 Micro-market", placeholder="e.g. Goregaon West")

with col2:
    city = st.text_input("🏙️ City", placeholder="e.g. Mumbai")

product_type = st.selectbox("🏢 Product Type", ["Residential", "Commercial"])

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

# ── PPT FUNCTION (CONSULTING STYLE) ──
def generate_ppt(result, micromarket, city):

    prs = Presentation()

    def add_title_slide(title, subtitle):
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes.title.text = title
        slide.placeholders[1].text = subtitle

    def add_bullet_slide(title, bullets):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = title
        tf = slide.placeholders[1].text_frame
        tf.clear()

        for b in bullets:
            p = tf.add_paragraph()
            p.text = b
            p.level = 0

    def add_table_slide(title):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = title

        table = slide.shapes.add_table(
            4, 5,
            Inches(0.5), Inches(1.5),
            Inches(9), Inches(4)
        ).table

        headers = ["Project", "Developer", "Config", "PSF", "Stage"]

        for i, h in enumerate(headers):
            table.cell(0, i).text = h

        # Placeholder rows
        table.cell(1,0).text = "Project A"
        table.cell(2,0).text = "Project B"
        table.cell(3,0).text = "Project C"

    # ── SLIDES ──
    add_title_slide("Competition Analysis", f"{micromarket}, {city}")

    add_bullet_slide("Executive Summary", [
        "Market pricing and demand analysed",
        "Competitor positioning evaluated",
        "Product mix trends identified",
        "Key risks and gaps highlighted"
    ])

    add_table_slide("Key Competitors")

    add_bullet_slide("PSF Trends", [
        "1BHK: ₹18K – ₹21K",
        "2BHK: ₹20K – ₹24K",
        "3BHK: ₹22K – ₹27K"
    ])

    add_bullet_slide("Carpet Area Range", [
        "1BHK: 350–500 sqft",
        "2BHK: 600–800 sqft",
        "3BHK: 900–1200 sqft"
    ])

    add_bullet_slide("Parking Cost", [
        "₹5L – ₹10L typical",
        "Podium parking premium",
        "Stack parking for mid-segment"
    ])

    add_bullet_slide("Key Risks", [
        "Oversupply in certain configs",
        "Price competition pressure",
        "Demand mismatch risk"
    ])

    file_path = f"{micromarket}_{city}_deck.pptx"
    prs.save(file_path)

    return file_path

# ── RUN ──
if run:

    if not micromarket or not city or not groq_key or not serp_key:
        st.error("Fill all fields")

    else:

        real_data = fetch_data(micromarket, city, serp_key)
        real_data = real_data[:2000]

        prompt = f"""
You are a real estate market research expert.

Do a COMPETITION ANALYSIS.

LOCATION:
{micromarket}, {city}

PRODUCT TYPE:
{product_type}

DATA:
{real_data}

SECTION_1: MARKET OVERVIEW
- price range
- demand

SECTION_2: COMPETITORS
| Project | Developer | Config | Carpet | Price | Stage |

SECTION_3: PRODUCT
- config mix
- carpet sizes
- fastest selling

SECTION_4: PRICING
- PSF by config
- all-in pricing
- parking cost

SECTION_5: GAPS
- market gaps

SECTION_6: RISKS
- risks
"""

        client = Groq(api_key=groq_key)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            max_tokens=2500
        )

        result = response.choices[0].message.content

        st.success("✅ Competition Analysis Ready")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Market","Projects","Product","Pricing","Gaps","Risks"
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

        # PPT Download
        ppt_file = generate_ppt(result, micromarket, city)

        with open(ppt_file, "rb") as f:
            st.download_button(
                "📥 Download Consulting PPT",
                f,
                file_name=ppt_file
            )
