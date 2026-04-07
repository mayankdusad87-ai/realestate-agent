import streamlit as st
from groq import Groq
import requests
import re
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RE Competition Analysis",
    page_icon="🏗️",
    layout="wide"
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background-color: #0D1117; color: #E6EDF3; }
.main .block-container { padding: 2rem 3rem; max-width: 1400px; }

.header-wrap {
    background: linear-gradient(135deg, #161B22 0%, #1C2333 100%);
    border: 1px solid #30363D;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
}
.header-badge {
    display: inline-block;
    background: rgba(184,134,11,0.15);
    border: 1px solid rgba(184,134,11,0.4);
    color: #D4A017;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 12px;
}
.header-title {
    font-size: 36px;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
.header-sub { font-size: 15px; color: #8B949E; margin: 8px 0 0 0; }

.section-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #D4A017;
    margin-bottom: 0.6rem;
    margin-top: 1.5rem;
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background-color: #0D1117 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
    font-family: 'Inter', sans-serif !important;
}
label { color: #8B949E !important; font-size: 13px !important; font-weight: 500 !important; }

.stButton > button {
    background: #B8860B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 36px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { background: #D4A017 !important; transform: translateY(-1px) !important; }

.stTabs [data-baseweb="tab-list"] {
    background: #161B22;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #30363D;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #8B949E;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] { background: #B8860B !important; color: #FFFFFF !important; }
.stTabs [data-baseweb="tab-panel"] {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 0 12px 12px 12px;
    padding: 2rem;
    margin-top: -1px;
}

.stAlert { border-radius: 10px !important; border: none !important; }
hr { border-color: #21262D !important; }

.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #B8860B !important;
    color: #D4A017 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    width: 100% !important;
}
.stDownloadButton > button:hover { background: rgba(184,134,11,0.1) !important; }

table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #1C2333; color: #D4A017; font-weight: 600; padding: 10px 14px; text-align: left; border-bottom: 2px solid #B8860B; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
td { padding: 10px 14px; border-bottom: 1px solid #21262D; color: #E6EDF3; vertical-align: top; }
tr:hover td { background: rgba(184,134,11,0.05); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-wrap">
    <div class="header-badge">Real Estate Developer Intelligence</div>
    <div class="header-title">🏗️ Competition Analysis Engine</div>
    <div class="header-sub">
        Your team inputs the market — AI delivers a developer-grade competitor intelligence report &amp; PPT
    </div>
</div>
""", unsafe_allow_html=True)

st.info("📡 Fetches live Google data + AI analysis. Verify all figures before board presentations.")

# ─────────────────────────────────────────────
# INPUT FORM — SECTION 1: LOCATION & MARKET
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">📍 Market Context</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    micromarket = st.text_input("Micro-market", placeholder="e.g. Goregaon West")
with col2:
    city = st.text_input("City", placeholder="e.g. Mumbai")
with col3:
    product_type = st.selectbox("Product Type", ["Residential", "Commercial", "Mixed-use", "Plots", "Warehousing"])

# ─────────────────────────────────────────────
# SECTION 2: YOUR PROJECT DETAILS
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">🏢 Your Project Details</div>', unsafe_allow_html=True)
col4, col5, col6 = st.columns(3)
with col4:
    our_project_name = st.text_input("Your Project Name", placeholder="e.g. Skyline Residences")
with col5:
    our_land_area = st.text_input("Land Area / FSI", placeholder="e.g. 2 acres, FSI 3.0")
with col6:
    our_target_segment = st.text_input("Target Segment", placeholder="e.g. Premium mid-segment, ₹1.5–3 Cr")

col7, col8 = st.columns(2)
with col7:
    our_configs = st.text_input("Planned Configurations", placeholder="e.g. 2BHK & 3BHK, 700–1200 sqft carpet")
with col8:
    our_launch_timeline = st.selectbox("Your Launch Timeline", [
        "Immediate (0–3 months)", "Short-term (3–6 months)",
        "Mid-term (6–12 months)", "Long-term (1–2 years)"
    ])

our_strengths = st.text_area(
    "Project USPs / Strengths (optional)",
    placeholder="e.g. Metro connectivity 500m, branded developer, rooftop amenities, RERA registered",
    height=70
)

# ─────────────────────────────────────────────
# SECTION 3: KNOWN COMPETITORS
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">🎯 Known Competitors to Benchmark</div>', unsafe_allow_html=True)
st.caption("List projects your team has already identified. AI will analyse these + discover additional ones.")

comp_cols = st.columns(3)
competitors = []
for i, col in enumerate(comp_cols):
    with col:
        name = st.text_input(f"Competitor {i+1} — Project Name", placeholder=f"e.g. {'Lodha Palava' if i==0 else 'Godrej Reserve' if i==1 else 'Raymond Realty'}", key=f"comp_{i}")
        competitors.append(name.strip())

# 2 more competitors in a second row
comp_cols2 = st.columns(3)
extra_comps = []
for i, col in enumerate(comp_cols2[:2]):
    with col:
        name = st.text_input(f"Competitor {i+4} — Project Name", placeholder="Optional", key=f"comp_extra_{i}")
        extra_comps.append(name.strip())

all_competitors = [c for c in competitors + extra_comps if c]

# ─────────────────────────────────────────────
# SECTION 4: API KEYS
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">🔑 API Configuration</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
with col_b:
    serp_key = st.text_input("SerpAPI Key", type="password", placeholder="Your SerpAPI key")

st.divider()
run = st.button("🚀 Run Competition Analysis")


# ─────────────────────────────────────────────
# DATA FETCHER
# ─────────────────────────────────────────────
def fetch_live_data(micromarket, city, product_type, all_competitors, serp_key):
    """Fetch live SERP data for market + each named competitor."""
    snippets = []

    # Core market queries
    queries = [
        f"property price per sqft {micromarket} {city} 2024 2025 {product_type.lower()}",
        f"new residential projects launch {micromarket} {city} 2025",
        f"real estate market trend {micromarket} {city} latest",
    ]

    # Competitor-specific queries
    for comp in all_competitors[:5]:
        queries.append(f"{comp} {city} price per sqft carpet area configurations launch")

    for q in queries:
        try:
            res = requests.get(
                "https://serpapi.com/search",
                params={"q": q, "api_key": serp_key, "num": 5, "gl": "in", "hl": "en"},
                timeout=12
            )
            data = res.json()
            for item in data.get("organic_results", [])[:4]:
                snippet = item.get("snippet", "")
                source = item.get("source", "")
                title = item.get("title", "")
                if snippet:
                    snippets.append(f"[{source}] {title}: {snippet}")
        except Exception:
            continue

    return "\n\n".join(snippets) if snippets else "Live data unavailable — use knowledge base."


# ─────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────
def build_prompt(micromarket, city, product_type, our_project_name, our_land_area,
                 our_target_segment, our_configs, our_launch_timeline, our_strengths,
                 all_competitors, live_data):

    comp_list = ", ".join(all_competitors) if all_competitors else "Not specified — discover top projects"

    return f"""
You are a senior real estate strategy analyst with deep expertise in Indian property markets.
Your client is a DEVELOPER who wants a hard-hitting competitor intelligence report.

DEVELOPER'S PROJECT:
- Project Name: {our_project_name or 'Unnamed Project'}
- Location: {micromarket}, {city}
- Product Type: {product_type}
- Land Area / FSI: {our_land_area or 'Not specified'}
- Target Segment: {our_target_segment or 'Not specified'}
- Planned Configurations: {our_configs or 'Not specified'}
- Launch Timeline: {our_launch_timeline}
- Known USPs / Strengths: {our_strengths or 'None mentioned'}

COMPETITORS IDENTIFIED BY TEAM:
{comp_list}

LIVE MARKET DATA (fetched today from Google):
{live_data[:3500]}

INSTRUCTIONS:
- Use live data as PRIMARY source; fill gaps with your training knowledge of Indian RE markets.
- Every number must be specific. ₹ figures must have carpet sqft context.
- Think like the developer's strategy team: where can they price, differentiate, and win?
- If a named competitor has insufficient data, use your knowledge of that project.
- Do NOT include budget range as an input — infer it from market data.

OUTPUT FORMAT — use EXACTLY these section markers (do not skip or rename any):

SECTION_1: MARKET SNAPSHOT
Write 5 sharp bullet points:
• Avg ₹/sqft range: ₹X,XXX – ₹X,XXX (carpet, {micromarket})
• Total active inventory: ~X projects / ~X,XXX units in pipeline
• Market temperature: [Hot 🔥 / Stable 📊 / Cooling ❄️] — reason in one line
• Primary buyer: [profile, income bracket, end-use vs investment %]
• YoY price appreciation: X% (source or estimate)

SECTION_2: COMPETITOR DEEP-DIVE
Analyse each named competitor (plus 2–3 discovered projects). For EACH project write:

**[Project Name] — [Developer]**
- Configurations: X BHK (XXX–XXX sqft carpet)
- Pricing: ₹X,XXX – ₹X,XXX/sqft | All-in: ₹X.X Cr – ₹X.X Cr
- Stage: [Under Construction / Ready / New Launch]
- RERA: [Registered / Not registered / Unknown]
- Key USP: [one line]
- Weakness / Gap: [one line — where they are vulnerable]

After all projects add:
**Market Pricing Band:** ₹X,XXX – ₹X,XXX/sqft (budget) | ₹X,XXX – ₹X,XXX/sqft (mid) | ₹X,XXX+/sqft (premium)
**Dominant payment scheme in market:** [CLP / Subvention / Flexi — typical structure]

SECTION_3: COMPETITOR COMPARISON TABLE
Produce a markdown table with all benchmarked projects:

| Project | Developer | Config | Carpet (sqft) | ₹/sqft | All-in Price | Stage | Key USP |
|---|---|---|---|---|---|---|---|
| Name | Developer | 2/3 BHK | 700–900 | ₹XX,XXX | ₹X.X Cr | UC/Ready | USP |

SECTION_4: PRICING STRATEGY FOR {our_project_name or 'YOUR PROJECT'}
Based on the competitive landscape, recommend:
• Recommended launch ₹/sqft: ₹XX,XXX — justify vs 3 nearest competitors
• Config-wise pricing:
  - {our_configs.split(',')[0].strip() if our_configs else '2BHK'}: XXX sqft carpet → ₹X.XX Cr
  - {our_configs.split(',')[1].strip() if our_configs and ',' in our_configs else '3BHK'}: XXX sqft carpet → ₹X.XX Cr
• Floor rise: ₹XX/sqft per floor
• PLC premiums: preferred-facing +X% | corner +X%
• Parking: ₹X.X L per slot
• Recommended payment scheme: [name + structure e.g. 10:80:10 CLP with subvention option]
• Absorption forecast: X units/month at recommended pricing

SECTION_5: MARKET GAPS & DIFFERENTIATION OPPORTUNITIES
3 specific gaps your project can exploit:
• GAP 1: [underserved segment / configuration / price point + why + demand size]
• GAP 2: [underserved segment / configuration / price point + why + demand size]
• GAP 3: [location, amenity, or product format gap + why + demand size]
• HOW {our_project_name or 'YOUR PROJECT'} CAN WIN: [3 sharp differentiation plays]

SECTION_6: RISK FLAGS
Rate each risk [HIGH / MED / LOW]:
• Risk 1 [LEVEL]: [description] → Mitigation: [one line]
• Risk 2 [LEVEL]: [description] → Mitigation: [one line]
• Risk 3 [LEVEL]: [description] → Mitigation: [one line]
• Risk 4 [LEVEL]: [description] → Mitigation: [one line]
• VERDICT: [GO ✅ / CAUTION ⚠️ / HOLD 🛑] — [one sentence strategic rationale]
"""


# ─────────────────────────────────────────────
# PPT COLOUR PALETTE
# ─────────────────────────────────────────────
NAVY       = RGBColor(0x1E, 0x27, 0x61)
GOLD       = RGBColor(0xB8, 0x86, 0x0B)
GOLD_LIGHT = RGBColor(0xD4, 0xA0, 0x17)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE  = RGBColor(0xF4, 0xF4, 0xF8)
LIGHT_GRAY = RGBColor(0xCA, 0xDC, 0xFC)
DARK_GRAY  = RGBColor(0x3A, 0x3A, 0x5C)
MID_GRAY   = RGBColor(0x8B, 0x8B, 0xA8)
CREAM      = RGBColor(0xF2, 0xF2, 0xF5)
RED_FLAG   = RGBColor(0xC0, 0x39, 0x2B)
AMBER_FLAG = RGBColor(0xD3, 0x7A, 0x00)
GREEN_FLAG = RGBColor(0x1E, 0x88, 0x55)


# ─────────────────────────────────────────────
# PPT HELPERS
# ─────────────────────────────────────────────
def set_slide_bg(slide, r, g, b):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(r, g, b)


def add_rect(slide, left, top, width, height, fill_rgb, line_rgb=None, line_pt=0):
    from pptx.util import Inches
    shape = slide.shapes.add_shape(
        1, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_pt)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, text, left, top, width, height,
             size=12, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, italic=False, font="Calibri"):
    from pptx.util import Inches
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font
    return txBox


def add_footer(slide, label, page_num):
    add_rect(slide, 0, 7.28, 10, 0.22, NAVY)
    add_text(slide, label, 0.25, 7.3, 8.5, 0.2,
             size=8, color=LIGHT_GRAY, align=PP_ALIGN.LEFT)
    add_text(slide, str(page_num), 9.5, 7.3, 0.4, 0.2,
             size=8, color=GOLD, align=PP_ALIGN.RIGHT)


def set_cell_bg(cell, rgb_tuple):
    from pptx.oxml.ns import qn
    from lxml import etree
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    solidFill = etree.SubElement(tcPr, qn('a:solidFill'))
    srgbClr = etree.SubElement(solidFill, qn('a:srgbClr'))
    r, g, b = rgb_tuple
    srgbClr.set('val', f'{r:02X}{g:02X}{b:02X}')


# ─────────────────────────────────────────────
# SLIDE BUILDERS
# ─────────────────────────────────────────────
def slide_cover(prs, micromarket, city, product_type, our_project_name, our_launch_timeline):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0x1E, 0x27, 0x61)

    # Left gold accent bar
    add_rect(slide, 0, 0, 0.1, 7.5, GOLD)
    # Top right gold corner
    add_rect(slide, 9.1, 0, 0.9, 0.12, GOLD)

    add_text(slide, "REAL ESTATE DEVELOPER INTELLIGENCE", 0.4, 0.3, 9, 0.4,
             size=9, bold=True, color=GOLD, font="Calibri")

    add_text(slide, "Competition Analysis", 0.4, 1.1, 9.2, 1.1,
             size=46, bold=True, color=WHITE, font="Calibri")

    add_text(slide, f"{our_project_name or 'Developer Project'}  ·  {micromarket}, {city}",
             0.4, 2.4, 9.2, 0.6,
             size=22, bold=False, color=GOLD_LIGHT, font="Calibri")

    add_rect(slide, 0.4, 3.2, 3.5, 0.05, GOLD)

    details = f"Product: {product_type}    ·    Launch: {our_launch_timeline}"
    add_text(slide, details, 0.4, 3.4, 9, 0.4,
             size=12, color=LIGHT_GRAY, font="Calibri")

    add_text(slide, "STRICTLY CONFIDENTIAL — FOR INTERNAL STRATEGY USE ONLY",
             0.4, 6.9, 9.2, 0.3,
             size=8, color=MID_GRAY, italic=True, font="Calibri")


def slide_exec_summary(prs, micromarket, city, bullets, our_project_name, page):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)

    add_rect(slide, 0, 0, 10, 0.85, NAVY)
    add_text(slide, "EXECUTIVE SUMMARY", 0.4, 0.2, 7, 0.5,
             size=18, bold=True, color=WHITE, font="Calibri")
    add_text(slide, f"{micromarket}, {city}", 7.5, 0.23, 2.3, 0.4,
             size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font="Calibri")

    icons = ["01", "02", "03", "04"]
    labels = ["Market Snapshot", "Competitive Landscape", "Your Pricing Position", "Strategic Verdict"]
    positions = [(0.25, 1.0), (5.15, 1.0), (0.25, 3.7), (5.15, 3.7)]

    for i, (lx, ly) in enumerate(positions):
        # Card
        add_rect(slide, lx, ly, 4.6, 2.45, WHITE, line_rgb=RGBColor(0xE0, 0xE0, 0xE8), line_pt=0.5)
        # Gold top bar
        add_rect(slide, lx, ly, 4.6, 0.08, GOLD)
        # Number
        add_text(slide, icons[i], lx + 0.15, ly + 0.12, 0.6, 0.38,
                 size=22, bold=True, color=GOLD, font="Calibri")
        # Label
        add_text(slide, labels[i], lx + 0.7, ly + 0.16, 3.7, 0.32,
                 size=10, bold=True, color=NAVY, font="Calibri")
        # Content
        content = bullets[i] if i < len(bullets) else "See full analysis"
        add_text(slide, content[:180], lx + 0.15, ly + 0.6, 4.2, 1.75,
                 size=10, color=DARK_GRAY, font="Calibri")

    add_footer(slide, f"{our_project_name or 'Project'}  ·  {micromarket}, {city}  ·  Confidential", page)


def slide_market_snapshot(prs, micromarket, city, content, our_project_name, page):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)

    add_rect(slide, 0, 0, 10, 0.85, NAVY)
    add_text(slide, "MARKET SNAPSHOT", 0.4, 0.2, 7, 0.5,
             size=18, bold=True, color=WHITE, font="Calibri")
    add_text(slide, f"{micromarket}, {city}", 7.5, 0.23, 2.3, 0.4,
             size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font="Calibri")

    # Left stat panel
    add_rect(slide, 0.25, 1.0, 2.9, 6.1, NAVY)

    stat_labels = ["Avg ₹/sqft", "Market Temp", "YoY Growth", "Inventory"]
    stat_values = ["₹18K–24K", "STABLE →", "+8–12%", "Active"]

    price_matches = re.findall(r'₹[\d,]+(?:\s*–\s*₹[\d,]+)?', content)
    if price_matches:
        stat_values[0] = price_matches[0][:18]

    for i, (lbl, val) in enumerate(zip(stat_labels, stat_values)):
        y = 1.3 + i * 1.35
        add_text(slide, lbl, 0.35, y, 2.6, 0.3, size=8, bold=True, color=GOLD, font="Calibri")
        add_text(slide, val, 0.35, y + 0.3, 2.6, 0.65, size=15, bold=True, color=WHITE, font="Calibri")
        if i < 3:
            add_rect(slide, 0.4, y + 1.0, 2.4, 0.02, DARK_GRAY)

    # Right panel — content
    add_text(slide, "Market Intelligence", 3.45, 1.05, 6.3, 0.42,
             size=13, bold=True, color=NAVY, font="Calibri")

    lines = [l.strip().lstrip("•·-* ") for l in content.split('\n') if l.strip() and len(l.strip()) > 12][:8]
    y_pos = 1.6
    for line in lines:
        add_rect(slide, 3.45, y_pos + 0.1, 0.07, 0.07, GOLD)
        add_text(slide, line, 3.65, y_pos, 6.0, 0.52, size=11, color=DARK_GRAY, font="Calibri")
        y_pos += 0.58
        if y_pos > 6.8:
            break

    add_footer(slide, f"{our_project_name or 'Project'}  ·  {micromarket}, {city}  ·  Confidential", page)


def slide_competitor_deepdive(prs, micromarket, city, content, our_project_name, page):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)

    add_rect(slide, 0, 0, 10, 0.85, NAVY)
    add_text(slide, "COMPETITOR DEEP-DIVE", 0.4, 0.2, 7, 0.5,
             size=18, bold=True, color=WHITE, font="Calibri")
    add_text(slide, f"{micromarket}, {city}", 7.5, 0.23, 2.3, 0.4,
             size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font="Calibri")

    # Parse individual competitor blocks
    blocks = re.split(r'\*\*(.+?—.+?)\*\*', content)
    competitors_parsed = []
    i = 1
    while i < len(blocks) - 1:
        header = blocks[i].strip()
        body = blocks[i + 1].strip() if i + 1 < len(blocks) else ""
        competitors_parsed.append((header, body))
        i += 2

    if not competitors_parsed:
        # fallback: just show content
        lines = [l.strip().lstrip("•·-* ") for l in content.split('\n') if l.strip() and len(l.strip()) > 8][:14]
        y_pos = 1.0
        for line in lines:
            add_rect(slide, 0.35, y_pos + 0.1, 0.07, 0.07, GOLD)
            add_text(slide, line, 0.55, y_pos, 9.1, 0.46, size=11, color=DARK_GRAY, font="Calibri")
            y_pos += 0.5
    else:
        card_positions = [(0.25, 1.0), (5.15, 1.0), (0.25, 3.85), (5.15, 3.85)]
        for idx, (header, body) in enumerate(competitors_parsed[:4]):
            lx, ly = card_positions[idx]
            add_rect(slide, lx, ly, 4.6, 2.55, WHITE, line_rgb=RGBColor(0xE0, 0xE0, 0xE8), line_pt=0.5)
            add_rect(slide, lx, ly, 0.08, 2.55, GOLD)
            add_text(slide, header[:50], lx + 0.18, ly + 0.1, 4.2, 0.35,
                     size=10, bold=True, color=NAVY, font="Calibri")
            lines = [l.strip().lstrip("•·- ") for l in body.split('\n') if l.strip() and len(l.strip()) > 5][:5]
            y = ly + 0.52
            for line in lines:
                add_text(slide, f"· {line}", lx + 0.18, y, 4.25, 0.38, size=9, color=DARK_GRAY, font="Calibri")
                y += 0.38

    add_footer(slide, f"{our_project_name or 'Project'}  ·  {micromarket}, {city}  ·  Confidential", page)


def slide_comparison_table(prs, micromarket, city, content, our_project_name, page):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)

    add_rect(slide, 0, 0, 10, 0.85, NAVY)
    add_text(slide, "COMPETITOR COMPARISON TABLE", 0.4, 0.2, 7, 0.5,
             size=18, bold=True, color=WHITE, font="Calibri")
    add_text(slide, f"{micromarket}, {city}", 7.5, 0.23, 2.3, 0.4,
             size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font="Calibri")

    # Parse markdown table
    rows = []
    for line in content.split('\n'):
        if '|' in line and '---' not in line:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                rows.append(cells)

    if len(rows) >= 2:
        headers = rows[0]
        data_rows = rows[1:8]
        n_cols = min(len(headers), 8)
        n_rows = len(data_rows) + 1

        col_widths_raw = [1.6, 1.3, 0.9, 1.0, 0.9, 1.1, 0.9, 1.8][:n_cols]
        total = sum(col_widths_raw)
        scale = 9.3 / total
        col_widths = [w * scale for w in col_widths_raw]

        row_h = min(0.5, 5.2 / n_rows)
        tbl = slide.shapes.add_table(
            n_rows, n_cols,
            Inches(0.35), Inches(1.1),
            Inches(9.3), Inches(row_h * n_rows + 0.1)
        ).table

        for ci, h in enumerate(headers[:n_cols]):
            cell = tbl.cell(0, ci)
            cell.text = h.upper()
            set_cell_bg(cell, (0x1E, 0x27, 0x61))
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.runs[0] if p.runs else p.add_run()
            run.font.bold = True
            run.font.size = Pt(8)
            run.font.color.rgb = GOLD
            run.font.name = "Calibri"

        for ri, row_data in enumerate(data_rows):
            bg = (0xFF, 0xFF, 0xFF) if ri % 2 == 0 else (0xF4, 0xF4, 0xF8)
            for ci in range(n_cols):
                cell = tbl.cell(ri + 1, ci)
                val = row_data[ci] if ci < len(row_data) else ""
                cell.text = val
                set_cell_bg(cell, bg)
                p = cell.text_frame.paragraphs[0]
                run = p.runs[0] if p.runs else p.add_run()
                run.font.size = Pt(9)
                run.font.color.rgb = NAVY if ci == 0 else DARK_GRAY
                run.font.bold = ci == 0
                run.font.name = "Calibri"
    else:
        add_text(slide, content[:900], 0.35, 1.1, 9.3, 6.0,
                 size=11, color=DARK_GRAY, font="Calibri")

    add_footer(slide, f"{our_project_name or 'Project'}  ·  {micromarket}, {city}  ·  Confidential", page)


def slide_pricing_strategy(prs, micromarket, city, content, our_project_name, our_configs, page):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)

    add_rect(slide, 0, 0, 10, 0.85, NAVY)
    add_text(slide, f"PRICING STRATEGY — {(our_project_name or 'YOUR PROJECT').upper()}", 0.4, 0.2, 8.5, 0.5,
             size=17, bold=True, color=WHITE, font="Calibri")
    add_text(slide, f"{micromarket}, {city}", 7.5, 0.23, 2.3, 0.4,
             size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font="Calibri")

    # Config price cards
    configs_raw = [c.strip() for c in our_configs.split(',') if c.strip()] if our_configs else ["2BHK", "3BHK"]
    configs = configs_raw[:3]
    if len(configs) < 3:
        configs.append("Jodi/Special")

    card_fills = [NAVY, RGBColor(0xB8, 0x86, 0x0B), NAVY]
    prices = re.findall(r'₹[\d.,\s]+(?:Cr|L|K)?', content)

    for i, (cfg, fill) in enumerate(zip(configs[:3], card_fills)):
        lx = 0.25 + i * 3.25
        add_rect(slide, lx, 1.05, 3.05, 1.9, fill)
        add_text(slide, cfg, lx + 0.18, 1.15, 2.7, 0.45,
                 size=20, bold=True, color=WHITE, font="Calibri")
        price_hint = prices[i] if i < len(prices) else "See report"
        add_text(slide, price_hint, lx + 0.18, 1.65, 2.7, 0.45,
                 size=16, bold=True,
                 color=GOLD if fill == NAVY else WHITE, font="Calibri")
        add_text(slide, "All-in price", lx + 0.18, 2.15, 2.7, 0.3,
                 size=9, color=LIGHT_GRAY if fill == NAVY else RGBColor(0x1E, 0x27, 0x61), font="Calibri")

    # Details below
    add_text(slide, "Pricing Intelligence", 0.25, 3.15, 9.5, 0.38,
             size=12, bold=True, color=NAVY, font="Calibri")
    add_rect(slide, 0.25, 3.55, 1.5, 0.04, GOLD)

    lines = [l.strip().lstrip("•·-* ") for l in content.split('\n') if l.strip() and len(l.strip()) > 8][:10]
    y = 3.72
    for line in lines:
        add_rect(slide, 0.25, y + 0.1, 0.07, 0.07, GOLD)
        add_text(slide, line, 0.45, y, 9.2, 0.44, size=11, color=DARK_GRAY, font="Calibri")
        y += 0.48
        if y > 7.0:
            break

    add_footer(slide, f"{our_project_name or 'Project'}  ·  {micromarket}, {city}  ·  Confidential", page)


def slide_gaps(prs, micromarket, city, content, our_project_name, page):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)

    add_rect(slide, 0, 0, 10, 0.85, NAVY)
    add_text(slide, "MARKET GAPS & DIFFERENTIATION OPPORTUNITIES", 0.4, 0.2, 9, 0.5,
             size=17, bold=True, color=WHITE, font="Calibri")

    lines = [l.strip().lstrip("•·-* ") for l in content.split('\n') if l.strip() and len(l.strip()) > 10]

    # Gap cards on left
    gap_lines = [l for l in lines if l.upper().startswith("GAP")][:3]
    if not gap_lines:
        gap_lines = lines[:3]

    add_text(slide, "IDENTIFIED GAPS", 0.25, 1.0, 4.5, 0.35,
             size=9, bold=True, color=NAVY, font="Calibri")
    for i, gap in enumerate(gap_lines):
        clean = gap.replace(f"GAP {i+1}:", "").replace(f"GAP{i+1}:", "").strip()
        ly = 1.45 + i * 1.7
        add_rect(slide, 0.25, ly, 4.5, 1.5, WHITE, line_rgb=RGBColor(0xE0, 0xE0, 0xE8), line_pt=0.5)
        add_rect(slide, 0.25, ly, 0.08, 1.5, GOLD)
        add_text(slide, f"GAP {i+1:02d}", 0.42, ly + 0.1, 4.0, 0.28,
                 size=9, bold=True, color=GOLD, font="Calibri")
        add_text(slide, clean[:200], 0.42, ly + 0.42, 3.95, 0.98,
                 size=10, color=DARK_GRAY, font="Calibri")

    # Win plays on right — navy panel
    add_rect(slide, 5.0, 1.0, 4.75, 6.1, NAVY)
    add_text(slide, "HOW TO WIN", 5.2, 1.15, 4.2, 0.35,
             size=9, bold=True, color=GOLD, font="Calibri")

    win_lines = [l for l in lines if "WIN" in l.upper() or "PLAY" in l.upper() or "DIFFERENTI" in l.upper()]
    if not win_lines:
        win_lines = lines[3:]

    y = 1.65
    for line in win_lines[:8]:
        clean = line.replace("HOW YOUR PROJECT CAN WIN:", "").replace("HOW TO WIN:", "").strip()
        if not clean:
            continue
        add_rect(slide, 5.2, y + 0.1, 0.07, 0.07, GOLD)
        add_text(slide, clean[:160], 5.42, y, 4.15, 0.58,
                 size=10, color=LIGHT_GRAY, font="Calibri")
        y += 0.65
        if y > 6.7:
            break

    add_footer(slide, f"{our_project_name or 'Project'}  ·  {micromarket}, {city}  ·  Confidential", page)


def slide_risks(prs, micromarket, city, content, our_project_name, page):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)

    add_rect(slide, 0, 0, 10, 0.85, NAVY)
    add_text(slide, "RISK FLAGS", 0.4, 0.2, 7, 0.5,
             size=18, bold=True, color=WHITE, font="Calibri")
    add_text(slide, f"{micromarket}, {city}", 7.5, 0.23, 2.3, 0.4,
             size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font="Calibri")

    lines = [l.strip().lstrip("•·-* ") for l in content.split('\n') if l.strip() and len(l.strip()) > 8]

    color_map = {
        "HIGH": (RED_FLAG, "HIGH"),
        "MED": (AMBER_FLAG, "MED"),
        "LOW": (GREEN_FLAG, "LOW"),
    }

    y = 1.05
    risk_count = 0
    verdict_line = ""

    for line in lines:
        if "VERDICT" in line.upper():
            verdict_line = line
            continue

        level = "MED"
        for lvl in ["HIGH", "MED", "LOW"]:
            if f"[{lvl}]" in line.upper() or f" {lvl}" in line.upper():
                level = lvl
                break

        fill_color, label = color_map.get(level, color_map["MED"])
        add_rect(slide, 0.25, y, 1.1, 0.72, fill_color)
        add_text(slide, label, 0.25, y + 0.17, 1.1, 0.38,
                 size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")

        add_rect(slide, 1.5, y, 8.15, 0.72, WHITE, line_rgb=RGBColor(0xE0, 0xE0, 0xE8), line_pt=0.5)
        clean = re.sub(r'\[?(HIGH|MED|LOW)\]?', '', line, flags=re.IGNORECASE).strip().lstrip(':- ')
        add_text(slide, clean[:200], 1.65, y + 0.08, 7.8, 0.58, size=10, color=DARK_GRAY, font="Calibri")

        y += 0.88
        risk_count += 1
        if risk_count >= 5:
            break

    # Verdict box
    if verdict_line:
        add_rect(slide, 0.25, y + 0.15, 9.5, 0.85, NAVY)
        clean_verdict = verdict_line.replace("VERDICT:", "").strip()
        add_text(slide, f"VERDICT  ·  {clean_verdict}", 0.45, y + 0.27, 9.1, 0.62,
                 size=12, bold=True, color=GOLD_LIGHT, font="Calibri")

    add_footer(slide, f"{our_project_name or 'Project'}  ·  {micromarket}, {city}  ·  Confidential", page)


def slide_closing(prs, micromarket, city, our_project_name):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0x1E, 0x27, 0x61)

    add_rect(slide, 0, 0, 0.1, 7.5, GOLD)
    add_rect(slide, 9.1, 7.3, 0.9, 0.2, GOLD)

    add_text(slide, "REAL ESTATE DEVELOPER INTELLIGENCE", 0.4, 2.0, 9.2, 0.45,
             size=10, bold=True, color=GOLD, align=PP_ALIGN.CENTER, font="Calibri")
    add_text(slide, "Thank You", 0.4, 2.7, 9.2, 1.0,
             size=48, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font="Calibri")
    add_rect(slide, 3.2, 3.95, 3.6, 0.06, GOLD)
    add_text(slide, f"{our_project_name or 'Developer Project'}  ·  {micromarket}, {city}",
             0.4, 4.2, 9.2, 0.45,
             size=14, color=LIGHT_GRAY, align=PP_ALIGN.CENTER, font="Calibri")
    add_text(slide, "This document is confidential and intended solely for internal strategy use.",
             0.4, 6.7, 9.2, 0.35, size=9, color=MID_GRAY, italic=True,
             align=PP_ALIGN.CENTER, font="Calibri")


# ─────────────────────────────────────────────
# MASTER PPT GENERATOR
# ─────────────────────────────────────────────
def generate_ppt(sections, micromarket, city, product_type,
                 our_project_name, our_configs, our_launch_timeline):
    prs = Presentation()
    prs.slide_width  = Inches(10)
    prs.slide_height = Inches(7.5)

    exec_bullets = [
        sections.get("1", "")[:180],
        sections.get("2", "")[:180],
        sections.get("4", "")[:180],
        sections.get("6", "")[:180],
    ]

    footer_label = f"{our_project_name or 'Project'}  ·  {micromarket}, {city}  ·  Confidential"

    slide_cover(prs, micromarket, city, product_type, our_project_name, our_launch_timeline)
    slide_exec_summary(prs, micromarket, city, exec_bullets, our_project_name, 2)
    slide_market_snapshot(prs, micromarket, city, sections.get("1", ""), our_project_name, 3)
    slide_competitor_deepdive(prs, micromarket, city, sections.get("2", ""), our_project_name, 4)
    slide_comparison_table(prs, micromarket, city, sections.get("3", ""), our_project_name, 5)
    slide_pricing_strategy(prs, micromarket, city, sections.get("4", ""), our_project_name, our_configs, 6)
    slide_gaps(prs, micromarket, city, sections.get("5", ""), our_project_name, 7)
    slide_risks(prs, micromarket, city, sections.get("6", ""), our_project_name, 8)
    slide_closing(prs, micromarket, city, our_project_name)

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────
# MAIN RUN LOGIC
# ─────────────────────────────────────────────
if run:
    if not micromarket or not city or not groq_key or not serp_key:
        st.error("⚠️ Please fill in Micro-market, City, and both API keys before running.")
    else:
        # Stage 1 — Fetch live data
        with st.status("🔍 Fetching live market & competitor data...", expanded=True) as status:
            st.write(f"Searching market prices in {micromarket}, {city}...")
            if all_competitors:
                st.write(f"Searching named competitors: {', '.join(all_competitors)}...")
            st.write("Searching active project launches and market trends...")
            live_data = fetch_live_data(micromarket, city, product_type, all_competitors, serp_key)
            status.update(label="✅ Live data fetched!", state="complete")

        with st.expander("📄 View raw data fetched from web"):
            st.text(live_data[:2500])

        # Stage 2 — AI Analysis
        with st.status("🤖 AI generating competition analysis...", expanded=True) as status:
            st.write("Running competitor intelligence analysis...")
            st.write("Building pricing strategy and gap analysis...")
            prompt = build_prompt(
                micromarket, city, product_type,
                our_project_name, our_land_area, our_target_segment,
                our_configs, our_launch_timeline, our_strengths,
                all_competitors, live_data
            )
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            result = response.choices[0].message.content
            status.update(label="✅ Analysis complete!", state="complete")

        # Parse sections
        raw_sections = result.split("SECTION_")
        sections_dict = {}
        for sec in raw_sections[1:]:
            if ':' in sec:
                num = sec.split(':')[0].strip()
                content_body = ':'.join(sec.split(':')[1:]).strip()
                sections_dict[num] = content_body

        st.success(f"🎉 Competition Analysis for **{our_project_name or micromarket}** is ready!")
        st.divider()

        # ── Display Tabs ──
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Market Snapshot",
            "🏢 Competitor Deep-Dive",
            "📋 Comparison Table",
            "💰 Pricing Strategy",
            "🎯 Gaps & Opportunities",
            "⚠️ Risk Flags"
        ])

        def show(key):
            return sections_dict.get(key, "_Section not generated — try re-running the analysis._")

        with tab1: st.markdown(show("1"))
        with tab2: st.markdown(show("2"))
        with tab3: st.markdown(show("3"))
        with tab4: st.markdown(show("4"))
        with tab5: st.markdown(show("5"))
        with tab6: st.markdown(show("6"))

        st.divider()

        # ── Downloads ──
        st.markdown('<div class="section-label">⬇️ Download Reports</div>', unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            ppt_buf = generate_ppt(
                sections_dict, micromarket, city, product_type,
                our_project_name, our_configs, our_launch_timeline
            )
            fname = f"{(our_project_name or micromarket).replace(' ', '_')}_Competition_Analysis.pptx"
            st.download_button(
                label="📥 Download PPT Deck (McKinsey-style)",
                data=ppt_buf,
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

        with col_dl2:
            txt_fname = f"{(our_project_name or micromarket).replace(' ', '_')}_Competition_Analysis.txt"
            st.download_button(
                label="📄 Download Full Report (TXT)",
                data=result,
                file_name=txt_fname,
                mime="text/plain"
            )
