"""
Real Estate Competition Analysis Engine
Streamlit UI layer — all business logic lives in dedicated modules.
"""
import logging
import time
from pathlib import Path

import streamlit as st
from groq import Groq

logger = logging.getLogger(__name__)

from config import (
    GROQ_MAX_RETRIES,
    GROQ_MAX_TOKENS,
    GROQ_MODEL,
    GROQ_RETRY_DELAY_SECONDS,
    GROQ_TEMPERATURE,
    LAUNCH_TIMELINES,
    LIVE_DATA_DISPLAY_LIMIT,
    PRODUCT_TYPES,
)
import memory_store
from data_fetcher import fetch_live_data
from ppt.generator import generate_ppt
from prompt_builder import (
    build_prompt,
    extract_table_rows,
    parse_response,
    sections_to_text,
    verified_rows,
)

memory_store.init_db()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RE Competition Analysis",
    page_icon="\U0001f3d7\ufe0f",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "style.css"
st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-wrap">
    <div class="header-badge">Real Estate Developer Intelligence</div>
    <div class="header-title">\U0001f3d7\ufe0f Competition Analysis Engine</div>
    <div class="header-sub">
        Your team inputs the market — AI delivers a developer-grade
        competitor intelligence report
    </div>
</div>
""", unsafe_allow_html=True)

st.info("\U0001f4e1 Fetches live Google data + AI analysis. Verify all figures before board presentations.")

# ─────────────────────────────────────────────────────────────────────────────
# INPUT FORM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">\U0001f4cd Market Context</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    micromarket = st.text_input("Micro-market", placeholder="e.g. Goregaon West")
with col2:
    city = st.text_input("City", placeholder="e.g. Mumbai")
with col3:
    product_type = st.selectbox("Product Type", PRODUCT_TYPES)

st.markdown('<div class="section-label">\U0001f3e2 Your Project Details</div>', unsafe_allow_html=True)
col4, col5, col6 = st.columns(3)
with col4:
    our_project_name = st.text_input("Your Project Name", placeholder="e.g. Skyline Residences")
with col5:
    our_land_area = st.text_input("Land Area / FSI", placeholder="e.g. 2 acres, FSI 3.0")
with col6:
    our_target_segment = st.text_input(
        "Target Segment", placeholder="e.g. Premium mid-segment, \u20b91.5\u20133 Cr"
    )

col7, col8 = st.columns(2)
with col7:
    our_configs = st.text_input(
        "Planned Configurations", placeholder="e.g. 2BHK, 3BHK (700\u20131200 sqft carpet)"
    )
with col8:
    our_launch_timeline = st.selectbox("Your Launch Timeline", LAUNCH_TIMELINES)

our_strengths = st.text_area(
    "Project USPs / Strengths (optional)",
    placeholder="e.g. Metro connectivity 500m, branded developer, rooftop amenities, RERA registered",
    height=68,
)

st.markdown('<div class="section-label">\U0001f3af Known Competitors to Benchmark</div>', unsafe_allow_html=True)
st.caption("List projects your team has already identified. AI will analyse these + discover additional ones.")

comp_row1 = st.columns(3)
competitors = []
for i, col in enumerate(comp_row1):
    with col:
        nm = st.text_input(
            f"Competitor {i + 1}",
            placeholder=["Lodha Palava", "Godrej Reserve", "Raymond Realty"][i],
            key=f"comp_{i}",
        )
        competitors.append(nm.strip())

comp_row2 = st.columns(3)
for i, col in enumerate(comp_row2[:2]):
    with col:
        nm = st.text_input(f"Competitor {i + 4}", placeholder="Optional", key=f"comp_ex_{i}")
        competitors.append(nm.strip())

all_competitors = [c for c in competitors if c]

try:
    groq_key = st.secrets["GROQ_API_KEY"]
    serp_key = st.secrets["SERP_API_KEY"]
except Exception:
    st.error("\u26a0\ufe0f API keys not configured. Please contact the administrator.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — FACT MEMORY (Phase 1)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### \U0001f9e0 Fact Memory")
    if city:
        remembered = memory_store.recall_projects(city)
        st.caption(f"{len(remembered)} remembered project(s) for **{city.title()}**")
        for p in remembered[:15]:
            price = p["price_sqft"] or "?"
            stage = p["stage"] or "?"
            st.markdown(f"- **{p['project']}** — {price} · {stage}")

        active = memory_store.recall_corrections(city)
        if active:
            st.markdown("**Active corrections (authoritative):**")
            for c in active:
                cols = st.columns([5, 1])
                cols[0].markdown(f"- {c['subject']} / {c['field']} → **{c['value']}**")
                if cols[1].button("✕", key=f"del_corr_{c['id']}", help="Remove"):
                    memory_store.delete_correction(c["id"])
                    st.rerun()

        with st.form("add_correction", clear_on_submit=True):
            st.markdown("**Add a correction**")
            c_subject = st.text_input("Subject (project or 'market')")
            c_field = st.text_input("Field (e.g. ₹/sqft, carpet, RERA)")
            c_value = st.text_input("Correct value")
            c_note = st.text_input("Note (optional)")
            if st.form_submit_button("Save correction"):
                if c_subject and c_field and c_value:
                    memory_store.add_correction(city, c_subject, c_field, c_value, c_note)
                    st.success("Saved — it will override future reports for this city.")
                else:
                    st.warning("Subject, field and value are all required.")
    else:
        st.caption("Enter a City above to see and edit its memory.")

st.divider()
run = st.button("\U0001f680 Run Full Competition Analysis")

# ─────────────────────────────────────────────────────────────────────────────
# MAIN RUN LOGIC
# ─────────────────────────────────────────────────────────────────────────────
if run:
    if not micromarket or not city:
        st.error("\u26a0\ufe0f Please fill in Micro-market and City before running.")
    else:
        with st.status("\U0001f50d Fetching live market & competitor data...", expanded=True) as status:
            st.write(f"Searching market prices in {micromarket}, {city}...")
            if all_competitors:
                st.write(f"Searching named competitors: {', '.join(all_competitors)}...")
            st.write("Searching active project launches and market trends...")
            live = fetch_live_data(micromarket, city, product_type, tuple(all_competitors), serp_key)
            stats = live["stats"]
            st.write(
                f"Queries run: {stats['queries']} \u00b7 sources found: {stats['sources']} "
                f"\u00b7 pages read: {stats['pages_fetched']}"
            )
            if live["live_ok"]:
                status.update(label="\u2705 Live data fetched!", state="complete")
            else:
                status.update(label="\u26a0\ufe0f No live data retrieved", state="error")

        live_data = live["text"]

        if live["errors"]:
            st.error(
                "\u26a0\ufe0f The web search reported problems, so results may be incomplete: "
                + "; ".join(live["errors"])
            )
        if not live["live_ok"]:
            st.warning(
                "\u26a0\ufe0f No live sources were retrieved (check the SerpAPI key/quota). "
                "The report below is **not grounded in live data** \u2014 the AI will mark "
                "data-dependent figures as unknown. Treat everything as unverified."
            )

        with st.expander("\U0001f4c4 View raw data fetched from web"):
            st.text(live_data[:LIVE_DATA_DISPLAY_LIMIT] if live_data else "No live data.")

        memory_data, corrections_data = memory_store.format_memory_block(city)
        if memory_data:
            n_mem = len(memory_data.strip().splitlines())
            st.caption(f"\U0001f9e0 Grounding in {n_mem} remembered fact(s) from prior runs in {city}.")
        if corrections_data:
            st.caption("\U0001f4cc Applying your saved team corrections (authoritative).")

        with st.status("\U0001f916 AI generating competition analysis...", expanded=True) as status:
            st.write("Running competitor intelligence analysis...")
            st.write("Building pricing strategy and gap analysis...")
            prompt = build_prompt(
                micromarket, city, product_type,
                our_project_name, our_land_area, our_target_segment,
                our_configs, our_launch_timeline, our_strengths,
                all_competitors, live_data,
                memory_data=memory_data,
                corrections_data=corrections_data,
            )
            client = Groq(api_key=groq_key)
            result = None
            for attempt in range(1, GROQ_MAX_RETRIES + 1):
                try:
                    response = client.chat.completions.create(
                        model=GROQ_MODEL,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=GROQ_MAX_TOKENS,
                        temperature=GROQ_TEMPERATURE,
                        response_format={"type": "json_object"},
                    )
                    result = response.choices[0].message.content
                    break
                except Exception as e:
                    logger.warning("Groq API attempt %d failed: %s", attempt, e)
                    if attempt < GROQ_MAX_RETRIES:
                        st.write(f"API call failed, retrying ({attempt}/{GROQ_MAX_RETRIES})...")
                        time.sleep(GROQ_RETRY_DELAY_SECONDS)
                    else:
                        st.error(f"\u26a0\ufe0f AI analysis failed after {GROQ_MAX_RETRIES} attempts: {e}")
                        st.stop()
            status.update(label="\u2705 Analysis complete!", state="complete")

        sections_dict = parse_response(result)
        if not sections_dict:
            st.warning("\u26a0\ufe0f AI returned an unexpected format. Some sections may be missing. Try re-running.")
        elif len(sections_dict) < 6:
            missing = [n for n in ("1", "2", "3", "4", "5", "6") if n not in sections_dict]
            st.warning(f"\u26a0\ufe0f Sections {', '.join(missing)} were not generated. Try re-running.")

        report_text = sections_to_text(sections_dict) or (result or "")

        # Phase 1: remember the verified competitor rows so future runs build on them.
        try:
            table_rows = extract_table_rows(sections_dict.get("3", ""))
            to_store = verified_rows(table_rows)
            if to_store:
                stored = memory_store.remember_projects(city, to_store)
                if stored:
                    st.caption(
                        f"\U0001f9e0 Saved {stored} verified project(s) to memory for {city} — "
                        "future runs will build on these."
                    )
        except Exception as e:  # memory must never break the report
            logger.warning("Memory write failed: %s", e)

        proj_label = our_project_name or micromarket
        st.success(f"\U0001f389 Competition Analysis for **{proj_label}** is ready!")
        st.divider()

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "\U0001f4ca Market Snapshot", "\U0001f3e2 Competitor Deep-Dive", "\U0001f4cb Comparison Table",
            "\U0001f4b0 Pricing Strategy", "\U0001f3af Gaps & Opportunities", "\u26a0\ufe0f Risk Flags",
        ])

        def _show(k):
            return sections_dict.get(k, "_Section not generated \u2014 please re-run._")

        with tab1:
            st.markdown(_show("1"))
        with tab2:
            st.markdown(_show("2"))
        with tab3:
            st.markdown(_show("3"))
        with tab4:
            st.markdown(_show("4"))
        with tab5:
            st.markdown(_show("5"))
        with tab6:
            st.markdown(_show("6"))

        st.divider()
        st.markdown('<div class="section-label">\u2b07\ufe0f Download Reports</div>', unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns(2)
        safe = (our_project_name or micromarket).replace(" ", "_")

        with col_dl1:
            ppt_buf = generate_ppt(
                sections_dict, micromarket, city, product_type,
                our_project_name, our_configs, our_launch_timeline,
            )
            st.download_button(
                label="\U0001f4e5 Download PPT Deck",
                data=ppt_buf,
                file_name=f"{safe}_Competition_Analysis.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            )
        with col_dl2:
            st.download_button(
                label="\U0001f4c4 Download Full Report (TXT)",
                data=report_text,
                file_name=f"{safe}_Competition_Analysis.txt",
                mime="text/plain",
            )
