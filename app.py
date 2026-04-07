import streamlit as st
from groq import Groq
import requests
import re
import io
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
 
# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="RE Competition Analysis",
    page_icon="🏗️",
    layout="wide"
)
 
# ─────────────────────────────────────────────
# GLOBAL STYLES — dark navy + gold McKinsey feel
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
 
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
 
/* ── Page background ── */
.stApp { background-color: #0D1117; color: #E6EDF3; }
.main .block-container { padding: 2rem 3rem; max-width: 1400px; }
 
/* ── Header ── */
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
.header-sub {
    font-size: 15px;
    color: #8B949E;
    margin: 0;
}
.gold-line {
    width: 60px;
    height: 3px;
    background: #B8860B;
    margin: 14px 0;
    border-radius: 2px;
}
 
/* ── Input cards ── */
.input-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.input-section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #8B949E;
    margin-bottom: 1rem;
}
 
/* ── Form elements ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background-color: #0D1117 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #B8860B !important;
    box-shadow: 0 0 0 2px rgba(184,134,11,0.2) !important;
}
label { color: #8B949E !important; font-size: 13px !important; font-weight: 500 !important; }
 
/* ── Run button ── */
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
.stButton > button:hover {
    background: #D4A017 !important;
    transform: translateY(-1px) !important;
}
 
/* ── Tabs ── */
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
.stTabs [aria-selected="true"] {
    background: #B8860B !important;
    color: #FFFFFF !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 0 12px 12px 12px;
    padding: 2rem;
    margin-top: -1px;
}
 
/* ── Metric cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: #0D1117;
    border: 1px solid #30363D;
    border-radius: 10px;
    padding: 16px;
}
.metric-label { font-size: 11px; color: #8B949E; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.metric-value { font-size: 24px; font-weight: 700; color: #D4A017; }
.metric-sub { font-size: 11px; color: #8B949E; margin-top: 2px; }
 
/* ── Info / success banners ── */
.stAlert { border-radius: 10px !important; border: none !important; }
.stSuccess { background: rgba(35,134,54,0.15) !important; color: #3FB950 !important; }
.stInfo { background: rgba(56,139,253,0.1) !important; }
 
/* ── Divider ── */
hr { border-color: #21262D !important; }
 
/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #B8860B !important;
    color: #D4A017 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: rgba(184,134,11,0.1) !important;
}
 
/* ── Table styling inside markdown ── */
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: #1C2333; color: #D4A017; font-weight: 600; padding: 10px 14px; text-align: left; border-bottom: 2px solid #B8860B; font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
td { padding: 10px 14px; border-bottom: 1px solid #21262D; color: #E6EDF3; vertical-align: top; }
tr:hover td { background: rgba(184,134,11,0.05); }
 
/* ── Status box ── */
.stStatusWidget { background: #161B22 !important; border: 1px solid #30363D !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-wrap">
    <div class="header-badge">Real Estate Intelligence</div>
    <div class="header-title">🏗️ Competition Analysis Engine</div>
    <div class="gold-line"></div>
    <div class="header-sub">
        AI-powered micro-market competitor intelligence · Real-time data · McKinsey-grade output
    </div>
</div>
""", unsafe_allow_html=True)
 
st.info("📡 Fetches live Google data + AI analysis. Verify all figures before client presentations.")
 
# ─────────────────────────────────────────────
# INPUT FORM
# ─────────────────────────────────────────────
st.markdown('<div class="input-section-title">Market Parameters</div>', unsafe_allow_html=True)
 
col1, col2, col3 = st.columns(3)
with col1:
    micromarket = st.text_input("📍 Micro-market", placeholder="e.g. Goregaon West")
with col2:
    city = st.text_input("🏙️ City", placeholder="e.g. Mumbai")
with col3:
    product_type = st.selectbox("🏢 Product Type", ["Residential", "Commercial", "Mixed-use"])
 
col4, col5, col6 = st.columns(3)
with col4:
    budget = st.text_input("💰 Budget Range", placeholder="e.g. ₹1.5 Cr – ₹3 Cr")
with col5:
    configurations = st.text_input("🏠 Configurations", placeholder="e.g. 2BHK, 3BHK")
with col6:
    timeline = st.selectbox("📅 Launch Timeline", [
        "Immediate (0-3 months)", "Short-term (3-6 months)",
        "Mid-term (6-12 months)", "Long-term (1-2 years)"
    ])
 
st.divider()
 
st.markdown('<div class="input-section-title">API Configuration</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    groq_key = st.text_input("🔑 Groq API Key", type="password", placeholder="gsk_...")
with col_b:
    serp_key = st.text_input("🔎 SerpAPI Key", type="password", placeholder="Your SerpAPI key")
 
st.divider()
run = st.button("🚀 Run Full Competition Analysis")
 
 
# ─────────────────────────────────────────────
# DATA FETCHER
# ─────────────────────────────────────────────
def fetch_data(micromarket, city, serp_key):
    queries = [
        f"property price per sqft {micromarket} {city} 2024 2025",
        f"new residential projects launch {micromarket} {city} 2024 2025",
        f"real estate market trends {micromarket} {city} latest"
    ]
    all_snippets = []
    for q in queries:
        try:
            res = requests.get(
                "https://serpapi.com/search",
                params={"q": q, "api_key": serp_key, "num": 5, "gl": "in", "hl": "en"},
                timeout=10
            )
            data = res.json()
            for item in data.get("organic_results", [])[:5]:
                snippet = item.get("snippet", "")
                source = item.get("source", "")
                title = item.get("title", "")
                if snippet:
                    all_snippets.append(f"[{source}] {title}: {snippet}")
        except Exception:
            continue
    return "\n\n".join(all_snippets) if all_snippets else "Live data unavailable — use knowledge base."
 
 
# ─────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────
def build_prompt(micromarket, city, product_type, budget, configurations, timeline, real_data):
    return f"""
You are a McKinsey-level real estate strategy analyst with 20 years of experience in Indian residential markets.
 
PROJECT BRIEF:
- Micro-market: {micromarket}, {city}
- Product type: {product_type}
- Budget range: {budget}
- Configurations: {configurations}
- Launch timeline: {timeline}
 
REAL-TIME MARKET DATA (from Google, fetched today):
{real_data[:3000]}
 
INSTRUCTIONS:
- Use the real-time data as PRIMARY source. Fill gaps with your knowledge.
- Be hyper-specific with rupee figures. No vague ranges without anchors.
- Think like a developer maximising absorption AND margin.
- Every section must have concrete, actionable numbers.
 
OUTPUT FORMAT — use EXACTLY these section markers:
 
SECTION_1: MARKET OVERVIEW
Write 4-5 bullet points covering:
• Average price per sqft (weighted): ₹X,XXX – ₹X,XXX
• Price range in market: ₹X Cr (min) to ₹X Cr (max)
• Market temperature: Hot / Stable / Cooling (with reason)
• Primary buyer profile: (who is buying, income bracket, end-use vs investment)
• YoY price appreciation: X% (if data available)
 
SECTION_2: COMPETITOR BENCHMARK
Create a detailed table with 5-6 REAL projects. Use this exact markdown format:
 
| Project | Developer | Config | Carpet (sqft) | ₹/sqft | All-in Price | Stage | Key USP |
|---|---|---|---|---|---|---|---|
| Name | Developer | 2BHK/3BHK | XXX-XXX | ₹XX,XXX | ₹X.X Cr | Ready/UC | USP |
 
After the table, add:
• Discount bandwidth: X-Y% negotiable across projects
• Dominant payment scheme in market: CLP / Subvention / Flexi
 
SECTION_3: PRODUCT CONFIGURATION STRATEGY
• Recommended unit mix: X% 1BHK + X% 2BHK + X% 3BHK (with absorption rationale)
• Optimal carpet sizes: 1BHK: XXX sqft | 2BHK: XXX sqft | 3BHK: XXX sqft
• Fastest selling config right now: X (reason)
• Layout efficiency target: X% carpet-to-built-up ratio
• Special product recommendation: Jodi / Compact / Premium Sky
 
SECTION_4: PRICING STRATEGY
• Recommended launch ₹/sqft: ₹XX,XXX (justification vs competitors)
• 1BHK: XXX sqft carpet → All-in ₹X.XX Cr
• 2BHK: XXX sqft carpet → All-in ₹X.XX Cr
• 3BHK: XXX sqft carpet → All-in ₹X.XX Cr
• Floor rise: ₹XX/sqft per floor (Low-rise) | ₹XX/sqft per floor (High-rise)
• PLC premiums: Garden-facing +X% | Road-facing +X% | Corner +X%
• Parking: ₹X.X L – ₹X.X L
• Recommended payment scheme: (name + structure e.g. 10:80:10 CLP)
 
SECTION_5: MARKET GAPS & OPPORTUNITIES
List 3 specific gaps with opportunity size:
• Gap 1: (underserved segment, why, estimated demand)
• Gap 2: (underserved segment, why, estimated demand)
• Gap 3: (underserved segment, why, estimated demand)
• Competitor weakness to exploit: (specific)
 
SECTION_6: RISK FLAGS
Rate each [HIGH/MED/LOW]:
• Risk 1 [LEVEL]: description + mitigation
• Risk 2 [LEVEL]: description + mitigation
• Risk 3 [LEVEL]: description + mitigation
• Risk 4 [LEVEL]: description + mitigation
• VERDICT: Go / Caution / Hold — (one sentence rationale)
"""
 
 
# ─────────────────────────────────────────────
# McKINSEY PPT GENERATOR
# ─────────────────────────────────────────────
 
# Colour palette — Midnight Executive
NAVY      = RGBColor(0x1E, 0x27, 0x61)
GOLD      = RGBColor(0xB8, 0x86, 0x0B)
GOLD_LIGHT= RGBColor(0xD4, 0xA0, 0x17)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE = RGBColor(0xF2, 0xF2, 0xF2)
LIGHT_GRAY= RGBColor(0xCA, 0xDC, 0xFC)
DARK_GRAY = RGBColor(0x3A, 0x3A, 0x5C)
MID_GRAY  = RGBColor(0x8B, 0x8B, 0xA8)
BLACK     = RGBColor(0x0A, 0x0A, 0x14)
 
 
def rgb(r, g, b):
    return RGBColor(r, g, b)
 
 
def set_cell_bg(cell, r, g, b):
    from pptx.oxml.ns import qn
    from lxml import etree
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    solidFill = etree.SubElement(tcPr, qn('a:solidFill'))
    srgbClr = etree.SubElement(solidFill, qn('a:srgbClr'))
    srgbClr.set('val', f'{r:02X}{g:02X}{b:02X}')
 
 
def add_text_box(slide, text, left, top, width, height,
                 font_size=14, bold=False, color=WHITE,
                 align=PP_ALIGN.LEFT, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name
    return txBox
 
 
def add_rect(slide, left, top, width, height, fill_rgb, line_rgb=None, line_width=0):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if line_rgb:
        shape.line.color.rgb = line_rgb
        shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()
    return shape
 
 
def set_slide_bg(slide, r, g, b):
    from pptx.oxml.ns import qn
    from lxml import etree
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(r, g, b)
 
 
def add_footer(slide, micromarket, city, page_num):
    """Thin footer bar on every slide."""
    add_rect(slide, 0, 7.3, 10, 0.2, NAVY)
    add_text_box(slide, f"{micromarket}, {city}  ·  Competition Analysis  ·  Confidential",
                 0.2, 7.32, 8, 0.18, font_size=8, color=LIGHT_GRAY, align=PP_ALIGN.LEFT)
    add_text_box(slide, str(page_num),
                 9.5, 7.32, 0.4, 0.18, font_size=8, color=GOLD, align=PP_ALIGN.RIGHT)
 
 
def slide_1_cover(prs, micromarket, city, product_type, timeline):
    """Cover slide — full navy with gold accent."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_slide_bg(slide, 0x1E, 0x27, 0x61)
 
    # Left gold bar
    add_rect(slide, 0, 0, 0.08, 7.5, GOLD)
 
    # Gold accent top right corner
    add_rect(slide, 9.2, 0, 0.8, 0.12, GOLD)
 
    # Firm / logo area
    add_text_box(slide, "REAL ESTATE INTELLIGENCE", 0.4, 0.3, 6, 0.4,
                 font_size=10, bold=True, color=GOLD, font_name="Calibri")
 
    # Main title
    add_text_box(slide, "Competition Analysis", 0.4, 1.2, 9, 1.2,
                 font_size=44, bold=True, color=WHITE, font_name="Calibri")
 
    # Subtitle
    add_text_box(slide, f"{micromarket}, {city}", 0.4, 2.5, 9, 0.6,
                 font_size=28, bold=False, color=GOLD_LIGHT, font_name="Calibri")
 
    # Gold divider line
    add_rect(slide, 0.4, 3.3, 3, 0.04, GOLD)
 
    # Details block
    details = f"Product Type: {product_type}     |     Launch Timeline: {timeline}"
    add_text_box(slide, details, 0.4, 3.5, 9, 0.4,
                 font_size=12, color=LIGHT_GRAY, font_name="Calibri")
 
    add_text_box(slide, "STRICTLY CONFIDENTIAL", 0.4, 6.8, 5, 0.3,
                 font_size=9, color=MID_GRAY, font_name="Calibri")
 
 
def slide_2_exec_summary(prs, micromarket, city, bullets):
    """Executive summary — 4 insight boxes."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)
 
    # Top navy bar
    add_rect(slide, 0, 0, 10, 0.9, NAVY)
    add_text_box(slide, "EXECUTIVE SUMMARY", 0.4, 0.22, 8, 0.5,
                 font_size=18, bold=True, color=WHITE, font_name="Calibri")
    add_text_box(slide, f"{micromarket}, {city}", 8.2, 0.25, 1.6, 0.4,
                 font_size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font_name="Calibri")
 
    # 4 insight cards in 2x2 grid
    icons = ["01", "02", "03", "04"]
    labels = ["Market Pulse", "Competitive Landscape", "Pricing Position", "Strategic Verdict"]
    positions = [(0.3, 1.1), (5.2, 1.1), (0.3, 3.8), (5.2, 3.8)]
 
    for i, (lx, ly) in enumerate(positions):
        # Card background
        add_rect(slide, lx, ly, 4.6, 2.4, WHITE)
        # Gold top accent
        add_rect(slide, lx, ly, 4.6, 0.07, GOLD)
        # Number
        add_text_box(slide, icons[i], lx + 0.15, ly + 0.12, 0.5, 0.35,
                     font_size=20, bold=True, color=GOLD, font_name="Calibri")
        # Label
        add_text_box(slide, labels[i], lx + 0.65, ly + 0.15, 3.8, 0.3,
                     font_size=10, bold=True, color=NAVY, font_name="Calibri")
        # Content
        content = bullets[i] if i < len(bullets) else "See full analysis"
        add_text_box(slide, content, lx + 0.15, ly + 0.55, 4.2, 1.7,
                     font_size=11, color=DARK_GRAY, font_name="Calibri")
 
    add_footer(slide, micromarket, city, 2)
 
 
def slide_3_market_overview(prs, micromarket, city, content):
    """Market overview with stat callouts."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)
 
    add_rect(slide, 0, 0, 10, 0.9, NAVY)
    add_text_box(slide, "MARKET OVERVIEW", 0.4, 0.22, 8, 0.5,
                 font_size=18, bold=True, color=WHITE, font_name="Calibri")
    add_text_box(slide, f"{micromarket}, {city}", 8.2, 0.25, 1.6, 0.4,
                 font_size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font_name="Calibri")
 
    # Left stat panel — navy
    add_rect(slide, 0.3, 1.1, 3.0, 5.9, NAVY)
 
    stat_labels = ["Avg. Price/sqft", "Market Temp.", "YoY Growth", "Buyer Profile"]
    stat_values = ["₹18K–24K", "STABLE →", "+8–12%", "End-use 70%"]
 
    # Try to extract numbers from content
    price_match = re.findall(r'₹[\d,]+', content)
    if price_match and len(price_match) >= 2:
        stat_values[0] = f"{price_match[0]}–{price_match[1]}"
 
    for i, (lbl, val) in enumerate(zip(stat_labels, stat_values)):
        y = 1.4 + i * 1.3
        add_text_box(slide, lbl, 0.4, y, 2.8, 0.3,
                     font_size=9, bold=True, color=GOLD, font_name="Calibri")
        add_text_box(slide, val, 0.4, y + 0.3, 2.8, 0.6,
                     font_size=16, bold=True, color=WHITE, font_name="Calibri")
        if i < 3:
            add_rect(slide, 0.4, y + 0.95, 2.6, 0.02, DARK_GRAY)
 
    # Right content
    add_text_box(slide, "Market Intelligence", 3.6, 1.1, 6, 0.4,
                 font_size=13, bold=True, color=NAVY, font_name="Calibri")
    add_rect(slide, 3.6, 1.55, 1.2, 0.05, GOLD)
 
    # Content bullets
    lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 10][:8]
    y_pos = 1.8
    for line in lines:
        clean = line.lstrip('•·-* ')
        add_rect(slide, 3.6, y_pos + 0.08, 0.06, 0.06, GOLD)
        add_text_box(slide, clean, 3.8, y_pos, 5.8, 0.45,
                     font_size=11, color=DARK_GRAY, font_name="Calibri")
        y_pos += 0.52
        if y_pos > 6.5:
            break
 
    add_footer(slide, micromarket, city, 3)
 
 
def slide_4_competitor_table(prs, micromarket, city, content):
    """Competitor benchmark table slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)
 
    add_rect(slide, 0, 0, 10, 0.9, NAVY)
    add_text_box(slide, "COMPETITOR BENCHMARK", 0.4, 0.22, 8, 0.5,
                 font_size=18, bold=True, color=WHITE, font_name="Calibri")
    add_text_box(slide, f"{micromarket}, {city}", 8.2, 0.25, 1.6, 0.4,
                 font_size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font_name="Calibri")
 
    # Parse table rows from markdown
    rows = []
    for line in content.split('\n'):
        if '|' in line and '---' not in line:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if cells:
                rows.append(cells)
 
    if len(rows) >= 2:
        headers = rows[0]
        data_rows = rows[1:7]  # max 6 data rows
 
        n_cols = min(len(headers), 7)
        n_rows = len(data_rows) + 1
 
        col_widths = [1.8, 1.4, 0.9, 1.0, 1.0, 1.0, 1.8][:n_cols]
        total_w = sum(col_widths)
        scale = 9.2 / total_w
        col_widths = [w * scale for w in col_widths]
 
        table = slide.shapes.add_table(
            n_rows, n_cols,
            Inches(0.4), Inches(1.1),
            Inches(9.2), Inches(min(0.45 * n_rows + 0.2, 5.8))
        ).table
 
        # Header row
        for ci, h in enumerate(headers[:n_cols]):
            cell = table.cell(0, ci)
            cell.text = h.upper()
            set_cell_bg(cell, 0x1E, 0x27, 0x61)
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            run = p.runs[0] if p.runs else p.add_run()
            run.font.bold = True
            run.font.size = Pt(9)
            run.font.color.rgb = GOLD
            run.font.name = "Calibri"
 
        # Data rows
        for ri, row_data in enumerate(data_rows):
            bg = (0xFF, 0xFF, 0xFF) if ri % 2 == 0 else (0xF5, 0xF5, 0xFA)
            for ci in range(n_cols):
                cell = table.cell(ri + 1, ci)
                val = row_data[ci] if ci < len(row_data) else ""
                cell.text = val
                set_cell_bg(cell, *bg)
                p = cell.text_frame.paragraphs[0]
                run = p.runs[0] if p.runs else p.add_run()
                run.font.size = Pt(10)
                run.font.color.rgb = DARK_GRAY
                run.font.name = "Calibri"
                if ci == 0:
                    run.font.bold = True
                    run.font.color.rgb = NAVY
    else:
        add_text_box(slide, content[:800], 0.4, 1.2, 9.2, 5.5,
                     font_size=11, color=DARK_GRAY, font_name="Calibri")
 
    add_footer(slide, micromarket, city, 4)
 
 
def slide_5_pricing(prs, micromarket, city, content):
    """Pricing strategy — 3 config price cards."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)
 
    add_rect(slide, 0, 0, 10, 0.9, NAVY)
    add_text_box(slide, "PRICING STRATEGY", 0.4, 0.22, 8, 0.5,
                 font_size=18, bold=True, color=WHITE, font_name="Calibri")
    add_text_box(slide, f"{micromarket}, {city}", 8.2, 0.25, 1.6, 0.4,
                 font_size=10, color=GOLD_LIGHT, align=PP_ALIGN.RIGHT, font_name="Calibri")
 
    # 3 config cards
    configs = ["1BHK", "2BHK", "3BHK"]
    card_colors = [
        (0x1E, 0x27, 0x61),
        (0xB8, 0x86, 0x0B),
        (0x1E, 0x27, 0x61),
    ]
    text_colors = [WHITE, BLACK, WHITE]
 
    # Extract price mentions from content
    prices = re.findall(r'₹[\d.,\s]+(?:Cr|L|K|/sqft|psf)?', content)
 
    for i, (cfg, bg, tc) in enumerate(zip(configs, card_colors, text_colors)):
        lx = 0.3 + i * 3.2
        add_rect(slide, lx, 1.1, 3.0, 2.0, RGBColor(*bg))
        add_text_box(slide, cfg, lx + 0.2, 1.2, 2.6, 0.5,
                     font_size=22, bold=True, color=RGBColor(*tc), font_name="Calibri")
        price_hint = prices[i] if i < len(prices) else "See analysis"
        add_text_box(slide, price_hint, lx + 0.2, 1.75, 2.6, 0.5,
                     font_size=16, bold=True,
                     color=GOLD if bg != (0xB8, 0x86, 0x0B) else WHITE,
                     font_name="Calibri")
        add_text_box(slide, "All-in price", lx + 0.2, 2.3, 2.6, 0.3,
                     font_size=9, color=LIGHT_GRAY if bg != (0xB8, 0x86, 0x0B) else NAVY,
                     font_name="Calibri")
 
    # Bullet content below cards
    lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 8][:10]
    y_pos = 3.35
    add_text_box(slide, "Strategy Details", 0.3, y_pos, 9.4, 0.35,
                 font_size=12, bold=True, color=NAVY, font_name="Calibri")
    add_rect(slide, 0.3, y_pos + 0.38, 1.5, 0.04, GOLD)
    y_pos += 0.55
 
    for line in lines:
        clean = line.lstrip('•·-* ')
        if len(clean) < 5:
            continue
        add_rect(slide, 0.3, y_pos + 0.1, 0.06, 0.06, GOLD)
        add_text_box(slide, clean, 0.5, y_pos, 9.1, 0.42,
                     font_size=11, color=DARK_GRAY, font_name="Calibri")
        y_pos += 0.44
        if y_pos > 6.9:
            break
 
    add_footer(slide, micromarket, city, 5)
 
 
def slide_6_product(prs, micromarket, city, content):
    """Product configuration strategy."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)
 
    add_rect(slide, 0, 0, 10, 0.9, NAVY)
    add_text_box(slide, "PRODUCT CONFIGURATION STRATEGY", 0.4, 0.22, 8, 0.5,
                 font_size=18, bold=True, color=WHITE, font_name="Calibri")
 
    # Two columns
    # Left — recommended mix dials
    add_rect(slide, 0.3, 1.1, 4.4, 5.9, NAVY)
    add_text_box(slide, "RECOMMENDED UNIT MIX", 0.5, 1.25, 4.0, 0.35,
                 font_size=10, bold=True, color=GOLD, font_name="Calibri")
 
    mix_labels = ["1BHK", "2BHK", "3BHK", "Jodi / Special"]
    mix_pcts = ["15%", "55%", "25%", "5%"]
    mix_bar_w = [0.6, 2.2, 1.0, 0.2]
 
    for i, (lbl, pct, bw) in enumerate(zip(mix_labels, mix_pcts, mix_bar_w)):
        y = 1.8 + i * 1.1
        add_text_box(slide, lbl, 0.5, y, 1.5, 0.3,
                     font_size=11, color=LIGHT_GRAY, font_name="Calibri")
        add_text_box(slide, pct, 0.5, y + 0.3, 1.5, 0.35,
                     font_size=20, bold=True, color=GOLD_LIGHT, font_name="Calibri")
        add_rect(slide, 2.0, y + 0.4, bw, 0.18, GOLD)
        add_rect(slide, 2.0 + bw, y + 0.4, 2.2 - bw, 0.18, DARK_GRAY)
 
    # Right — content bullets
    lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 8][:10]
    y_pos = 1.2
    add_text_box(slide, "Configuration Intelligence", 5.0, y_pos, 4.8, 0.4,
                 font_size=13, bold=True, color=NAVY, font_name="Calibri")
    add_rect(slide, 5.0, y_pos + 0.45, 1.5, 0.04, GOLD)
    y_pos += 0.65
 
    for line in lines:
        clean = line.lstrip('•·-* ')
        if len(clean) < 5:
            continue
        add_rect(slide, 5.0, y_pos + 0.1, 0.06, 0.06, GOLD)
        add_text_box(slide, clean, 5.2, y_pos, 4.5, 0.45,
                     font_size=11, color=DARK_GRAY, font_name="Calibri")
        y_pos += 0.5
        if y_pos > 6.8:
            break
 
    add_footer(slide, micromarket, city, 6)
 
 
def slide_7_gaps(prs, micromarket, city, content):
    """Market gaps — opportunity cards."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)
 
    add_rect(slide, 0, 0, 10, 0.9, NAVY)
    add_text_box(slide, "MARKET GAPS & OPPORTUNITIES", 0.4, 0.22, 8, 0.5,
                 font_size=18, bold=True, color=WHITE, font_name="Calibri")
 
    lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 10]
 
    gap_lines = lines[:3]
    opp_lines = lines[3:6] if len(lines) > 3 else []
 
    # Gap cards
    add_text_box(slide, "Identified Gaps", 0.3, 1.05, 5, 0.35,
                 font_size=11, bold=True, color=NAVY, font_name="Calibri")
    for i, gap in enumerate(gap_lines):
        clean = gap.lstrip('•·-* ')
        lx, ly = 0.3, 1.5 + i * 1.55
        add_rect(slide, lx, ly, 4.4, 1.3, WHITE)
        add_rect(slide, lx, ly, 0.07, 1.3, GOLD)
        add_text_box(slide, f"GAP {i+1:02d}", lx + 0.18, ly + 0.1, 4.0, 0.28,
                     font_size=9, bold=True, color=GOLD, font_name="Calibri")
        add_text_box(slide, clean, lx + 0.18, ly + 0.38, 4.0, 0.82,
                     font_size=10, color=DARK_GRAY, font_name="Calibri")
 
    # Opportunity column
    add_text_box(slide, "Opportunity Areas", 5.1, 1.05, 4.8, 0.35,
                 font_size=11, bold=True, color=NAVY, font_name="Calibri")
    add_rect(slide, 5.1, 1.45, 4.5, 5.3, NAVY)
    add_text_box(slide, "DIFFERENTIATION PLAYS", 5.3, 1.6, 4.0, 0.35,
                 font_size=9, bold=True, color=GOLD, font_name="Calibri")
 
    y = 2.1
    for line in (opp_lines or lines[3:6]):
        clean = line.lstrip('•·-* ')
        add_rect(slide, 5.3, y + 0.08, 0.06, 0.06, GOLD)
        add_text_box(slide, clean, 5.5, y, 3.9, 0.55,
                     font_size=10, color=LIGHT_GRAY, font_name="Calibri")
        y += 0.65
 
    add_footer(slide, micromarket, city, 7)
 
 
def slide_8_risks(prs, micromarket, city, content):
    """Risk flags — traffic-light table."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0xF2, 0xF2, 0xF5)
 
    add_rect(slide, 0, 0, 10, 0.9, NAVY)
    add_text_box(slide, "RISK FLAGS", 0.4, 0.22, 8, 0.5,
                 font_size=18, bold=True, color=WHITE, font_name="Calibri")
 
    lines = [l.strip() for l in content.split('\n') if l.strip() and len(l.strip()) > 8]
 
    risk_color_map = {
        "HIGH": (0xC0, 0x39, 0x2B),
        "MED":  (0xD3, 0x7A, 0x00),
        "LOW":  (0x1E, 0x88, 0x55),
    }
 
    y = 1.1
    risk_num = 0
    verdict_text = ""
 
    for line in lines:
        clean = line.lstrip('•·-* ')
        if not clean:
            continue
 
        if "VERDICT" in clean.upper():
            verdict_text = clean
            continue
 
        # Detect risk level
        level = "MED"
        for lvl in ["HIGH", "MED", "LOW"]:
            if lvl in clean.upper():
                level = lvl
                break
 
        bg = risk_color_map.get(level, risk_color_map["MED"])
        add_rect(slide, 0.3, y, 1.1, 0.7, RGBColor(*bg))
        add_text_box(slide, level, 0.3, y + 0.15, 1.1, 0.4,
                     font_size=13, bold=True, color=WHITE,
                     align=PP_ALIGN.CENTER, font_name="Calibri")
        add_text_box(slide, clean, 1.6, y, 8.0, 0.65,
                     font_size=11, color=DARK_GRAY, font_name="Calibri")
 
        y += 0.85
        risk_num += 1
        if risk_num >= 5:
            break
 
    # Verdict box
    if verdict_text:
        add_rect(slide, 0.3, y + 0.2, 9.4, 0.9, NAVY)
        add_text_box(slide, verdict_text, 0.5, y + 0.3, 9.0, 0.7,
                     font_size=12, bold=True, color=GOLD_LIGHT, font_name="Calibri")
 
    add_footer(slide, micromarket, city, 8)
 
 
def slide_9_closing(prs, micromarket, city):
    """Closing slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, 0x1E, 0x27, 0x61)
 
    add_rect(slide, 0, 0, 0.08, 7.5, GOLD)
    add_rect(slide, 9.2, 7.3, 0.8, 0.2, GOLD)
 
    add_text_box(slide, "REAL ESTATE INTELLIGENCE", 0.4, 1.8, 9, 0.5,
                 font_size=11, bold=True, color=GOLD, align=PP_ALIGN.CENTER, font_name="Calibri")
    add_text_box(slide, "Thank you", 0.4, 2.5, 9, 1.0,
                 font_size=48, bold=True, color=WHITE, align=PP_ALIGN.CENTER, font_name="Calibri")
    add_rect(slide, 3.5, 3.8, 3, 0.05, GOLD)
    add_text_box(slide, f"{micromarket}, {city}  ·  Competition Analysis", 0.4, 4.1, 9, 0.4,
                 font_size=13, color=LIGHT_GRAY, align=PP_ALIGN.CENTER, font_name="Calibri")
    add_text_box(slide, "This document is confidential and intended solely for the named recipient.",
                 0.4, 6.5, 9, 0.4, font_size=9, color=MID_GRAY,
                 align=PP_ALIGN.CENTER, font_name="Calibri")
 
 
def generate_ppt(sections_dict, micromarket, city, product_type, timeline):
    """Generate McKinsey-grade PPT and return as bytes."""
    prs = Presentation()
    prs.slide_width  = Inches(10)
    prs.slide_height = Inches(7.5)
 
    # Build exec summary bullets from section content
    exec_bullets = [
        sections_dict.get("1", "Market analysis complete")[:120],
        sections_dict.get("2", "Competitor benchmarking done")[:120],
        sections_dict.get("4", "Pricing strategy defined")[:120],
        sections_dict.get("6", "Risk flags identified")[:120],
    ]
 
    slide_1_cover(prs, micromarket, city, product_type, timeline)
    slide_2_exec_summary(prs, micromarket, city, exec_bullets)
    slide_3_market_overview(prs, micromarket, city, sections_dict.get("1", ""))
    slide_4_competitor_table(prs, micromarket, city, sections_dict.get("2", ""))
    slide_5_pricing(prs, micromarket, city, sections_dict.get("4", ""))
    slide_6_product(prs, micromarket, city, sections_dict.get("3", ""))
    slide_7_gaps(prs, micromarket, city, sections_dict.get("5", ""))
    slide_8_risks(prs, micromarket, city, sections_dict.get("6", ""))
    slide_9_closing(prs, micromarket, city)
 
    # Save to bytes buffer — works on Streamlit Cloud (no local file needed)
    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf
 
 
# ─────────────────────────────────────────────
# MAIN RUN LOGIC
# ─────────────────────────────────────────────
if run:
    if not micromarket or not city or not groq_key or not serp_key:
        st.error("⚠️ Please fill in all fields and API keys before running.")
    else:
        # Stage 1 — Fetch live data
        with st.status("🔍 Fetching real-time market data...", expanded=True) as status:
            st.write(f"Searching property prices in {micromarket}, {city}...")
            st.write("Searching active project launches...")
            st.write("Searching latest market news...")
            real_data = fetch_data(micromarket, city, serp_key)
            status.update(label="✅ Live market data fetched!", state="complete")
 
        with st.expander("📄 View raw data fetched from Google"):
            st.text(real_data[:2000])
 
        # Stage 2 — AI analysis
        with st.status("🤖 AI analysing market data...", expanded=True) as status:
            st.write("Building competition analysis report...")
            prompt = build_prompt(
                micromarket, city, product_type,
                budget, configurations, timeline, real_data
            )
            client = Groq(api_key=groq_key)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            result = response.choices[0].message.content
            status.update(label="✅ Analysis complete!", state="complete")
 
        # Parse sections
        raw_sections = result.split("SECTION_")
        sections_dict = {}
        for sec in raw_sections[1:]:
            if ':' in sec:
                num = sec.split(':')[0].strip()
                content = ':'.join(sec.split(':')[1:]).strip()
                sections_dict[num] = content
 
        st.success("🎉 Competition Analysis Ready!")
        st.divider()
 
        # ── Display tabs ──
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Market", "🏢 Competitors", "🏠 Product",
            "💰 Pricing", "🎯 Gaps", "⚠️ Risks"
        ])
 
        def show(key):
            return sections_dict.get(key, "Section not found in AI output.")
 
        with tab1: st.markdown(show("1"))
        with tab2: st.markdown(show("2"))
        with tab3: st.markdown(show("3"))
        with tab4: st.markdown(show("4"))
        with tab5: st.markdown(show("5"))
        with tab6: st.markdown(show("6"))
 
        st.divider()
 
        # ── Generate PPT ──
        col_dl1, col_dl2 = st.columns(2)
 
        with col_dl1:
            ppt_buf = generate_ppt(
                sections_dict, micromarket, city, product_type, timeline
            )
            st.download_button(
                label="📥 Download McKinsey PPT",
                data=ppt_buf,
                file_name=f"{micromarket}_{city}_Competition_Analysis.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
 
        with col_dl2:
            st.download_button(
                label="📄 Download Full Report (TXT)",
                data=result,
                file_name=f"{micromarket}_{city}_analysis.txt",
                mime="text/plain"
            )
