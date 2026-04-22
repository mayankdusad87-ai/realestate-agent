"""
LLM prompt construction and response parsing.
"""
from config import LIVE_DATA_SNIPPET_LIMIT


def build_prompt(
    micromarket: str,
    city: str,
    product_type: str,
    our_project_name: str,
    our_land_area: str,
    our_target_segment: str,
    our_configs: str,
    our_launch_timeline: str,
    our_strengths: str,
    all_competitors: list[str],
    live_data: str,
) -> str:
    comp_list = (
        ", ".join(all_competitors)
        if all_competitors
        else "Not specified - discover top 5 projects"
    )
    cfg_parts = (
        [c.strip() for c in our_configs.split(",") if c.strip()]
        if our_configs
        else ["2BHK", "3BHK"]
    )
    cfg1 = cfg_parts[0] if len(cfg_parts) > 0 else "2BHK"
    cfg2 = cfg_parts[1] if len(cfg_parts) > 1 else "3BHK"
    proj = (our_project_name or "YOUR PROJECT").upper()

    return f"""
You are a senior real estate strategy analyst with deep expertise in Indian real estate markets.
Your client is a REAL ESTATE DEVELOPER who needs a hard-hitting, specific competitor intelligence report.

DEVELOPER'S PROJECT:
- Project Name: {our_project_name or 'Unnamed Project'}
- Location: {micromarket}, {city}
- Product Type: {product_type}
- Land Area / FSI: {our_land_area or 'Not specified'}
- Target Segment: {our_target_segment or 'Not specified'}
- Planned Configurations: {our_configs or 'Not specified'}
- Launch Timeline: {our_launch_timeline}
- Known USPs: {our_strengths or 'None mentioned'}

COMPETITORS IDENTIFIED BY TEAM:
{comp_list}

LIVE MARKET DATA (fetched today from Google + RERA portals):
{live_data[:LIVE_DATA_SNIPPET_LIMIT]}

IMPORTANT: The live data above includes RERA portal information where available.
When you find RERA registration numbers, carpet areas, possession dates, or
registration status - treat these as VERIFIED FACTS and highlight them clearly
in your analysis. RERA data is more reliable than portal listings.

RULES:
- Use live data as PRIMARY source; fill gaps with your knowledge of Indian RE markets.
- Every number must be specific. ₹ figures must have carpet sqft context.
- Think like the developer's strategy team: where can they price, differentiate, and win?
- If named competitor has insufficient data, use your training knowledge of that project.

OUTPUT FORMAT - use EXACTLY these markers (no skipping, no renaming):

SECTION_1: MARKET SNAPSHOT
• Avg ₹/sqft range: ₹X,XXX - ₹X,XXX (carpet, {micromarket})
• Total active inventory: ~X projects / ~X,XXX units in pipeline
• Market temperature: [Hot 🔥 / Stable 📊 / Cooling ❄️] - reason in one line
• Primary buyer: [profile, income bracket, end-use vs investment %]
• YoY price appreciation: X% (source or estimate)

SECTION_2: COMPETITOR DEEP-DIVE
For EACH project (named + 2-3 discovered), write:

**[Project Name] - [Developer]**
- Configurations: X BHK (XXX-XXX sqft carpet)
- Pricing: ₹X,XXX - ₹X,XXX/sqft | All-in: ₹X.X Cr - ₹X.X Cr
- Stage: [Under Construction / Ready / New Launch]
- RERA: [Registered / Not registered / Unknown]
- Key USP: [one line]
- Weakness / Gap: [one line - where they are vulnerable]

After all projects:
**Market Pricing Band:** ₹X,XXX - ₹X,XXX/sqft (budget) | ₹X,XXX - ₹X,XXX/sqft (mid) | ₹X,XXX+/sqft (premium)
**Dominant payment scheme:** [CLP / Subvention / Flexi - typical structure]

SECTION_3: COMPETITOR COMPARISON TABLE
| Project | Developer | Config | Carpet (sqft) | ₹/sqft | All-in Price | Stage | Key USP |
|---|---|---|---|---|---|---|---|
[fill 5-7 rows with real data]

SECTION_4: PRICING STRATEGY FOR {proj}
• Recommended launch ₹/sqft: ₹XX,XXX - justify vs 3 nearest competitors
• {cfg1}: XXX sqft carpet → ₹X.XX Cr all-in
• {cfg2}: XXX sqft carpet → ₹X.XX Cr all-in
• Floor rise: ₹XX/sqft per floor (low-rise) | ₹XX/sqft per floor (high-rise)
• PLC premiums: preferred-facing +X% | corner +X%
• Parking: ₹X.X L per covered slot
• Recommended payment scheme: [name + structure e.g. 10:80:10 CLP]
• Absorption forecast: X units/month at recommended pricing

SECTION_5: MARKET GAPS & DIFFERENTIATION OPPORTUNITIES
GAP 1: [underserved segment / config / price point + why + demand size]
GAP 2: [underserved segment / config / price point + why + demand size]
GAP 3: [location, amenity, or product format gap + why + demand size]
HOW {proj} CAN WIN:
• [specific differentiation play 1]
• [specific differentiation play 2]
• [specific differentiation play 3]

SECTION_6: RISK FLAGS
• Risk 1 [HIGH/MED/LOW]: [description] → Mitigation: [one line]
• Risk 2 [HIGH/MED/LOW]: [description] → Mitigation: [one line]
• Risk 3 [HIGH/MED/LOW]: [description] → Mitigation: [one line]
• Risk 4 [HIGH/MED/LOW]: [description] → Mitigation: [one line]
• VERDICT: [GO ✅ / CAUTION ⚠️ / HOLD 🛑] - [one sentence strategic rationale]
"""


def parse_sections(raw_result: str) -> dict[str, str]:
    sections = {}
    for sec in raw_result.split("SECTION_")[1:]:
        if ":" in sec:
            num = sec.split(":")[0].strip()
            sections[num] = ":".join(sec.split(":")[1:]).strip()
    return sections
