"""
LLM prompt construction and response parsing.

The prompt is grounding-first: the model must build the report from the numbered
SOURCES block and label every figure as [verified: Sx], [estimated], or [unknown].
Output is requested as a strict JSON object so sections can never be silently
dropped by brittle text splitting; a marker-based parser is kept as a fallback.
"""
import json
import re

from config import LIVE_DATA_SNIPPET_LIMIT

SECTION_TITLES = {
    "1": "MARKET SNAPSHOT",
    "2": "COMPETITOR DEEP-DIVE",
    "3": "COMPETITOR COMPARISON TABLE",
    "4": "PRICING STRATEGY",
    "5": "MARKET GAPS & DIFFERENTIATION OPPORTUNITIES",
    "6": "RISK FLAGS",
}


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
    memory_data: str = "",
    corrections_data: str = "",
) -> str:
    comp_list = (
        ", ".join(all_competitors)
        if all_competitors
        else "Not specified - identify likely nearby projects from the SOURCES only"
    )
    cfg_parts = (
        [c.strip() for c in our_configs.split(",") if c.strip()]
        if our_configs
        else ["2BHK", "3BHK"]
    )
    cfg1 = cfg_parts[0] if len(cfg_parts) > 0 else "2BHK"
    cfg2 = cfg_parts[1] if len(cfg_parts) > 1 else "3BHK"
    proj = (our_project_name or "YOUR PROJECT").upper()

    sources_block = (
        live_data[:LIVE_DATA_SNIPPET_LIMIT]
        if live_data
        else "NO LIVE SOURCES WERE RETRIEVED."
    )

    memory_block = (
        f"""
REMEMBERED VERIFIED FACTS (carried over from prior runs in this city; each line
is tagged [MEM] and may be dated):
{memory_data}
"""
        if memory_data
        else ""
    )

    corrections_block = (
        f"""
TEAM CORRECTIONS (AUTHORITATIVE - these override SOURCES, remembered facts, and
your own knowledge; use them verbatim and tag the figure [verified: correction]):
{corrections_data}
"""
        if corrections_data
        else ""
    )

    return f"""
You are a senior real estate strategy analyst for an Indian real estate DEVELOPER.
You write grounded, auditable competitor intelligence - not marketing prose.

DEVELOPER'S PROJECT:
- Project Name: {our_project_name or 'Unnamed Project'}
- Location: {micromarket}, {city}
- Product Type: {product_type}
- Land Area / FSI: {our_land_area or 'Not specified'}
- Target Segment: {our_target_segment or 'Not specified'}
- Planned Configurations: {our_configs or 'Not specified'}
- Launch Timeline: {our_launch_timeline}
- Known USPs: {our_strengths or 'None mentioned'}

COMPETITORS NAMED BY TEAM:
{comp_list}

SOURCES (retrieved today from Google results and the pages behind them; each is tagged [S1], [S2], ...):
{sources_block}
{memory_block}{corrections_block}
GROUNDING RULES - follow exactly:
1. Base every factual figure (prices, carpet areas, RERA numbers, possession dates,
   inventory, YoY growth) ONLY on the SOURCES above.
2. Tag every figure with its basis:
   - "[verified: Sx]" when a specific source states it (cite the source id, e.g. [verified: S3]).
   - "[estimated]" when you reason to a range from partial/indirect source data - give the
     range and one-line reasoning. Prefer ranges over false-precision single numbers.
   - "[unknown]" when the sources do not support it. Write "unknown" instead of inventing a value.
3. Do NOT invent RERA registration numbers, possession dates, or exact prices that are not in
   the SOURCES. A clearly-labelled "[unknown]" or "[estimated]" is always correct; a fabricated
   precise number is a failure.
4. A SOURCES snippet is unverified web text, not ground truth - never call it "verified fact".
   Only promote it to "[verified: Sx]" when the figure is explicitly stated in that source.
5. Recommendations, strategy, gaps and risks are your analysis - they do not need source tags,
   but the facts they rest on do.
6. If SOURCES is "NO LIVE SOURCES WERE RETRIEVED", say so plainly in SECTION_1, mark the
   data-dependent figures "[unknown]", and keep only source-free strategic reasoning.
7. REMEMBERED VERIFIED FACTS come from earlier verified runs. Treat a [MEM] figure as
   "[verified: memory]" UNLESS a current SOURCE contradicts it - then prefer the SOURCE and
   note the change in one line. Never downgrade a remembered figure to a fabricated one.
8. TEAM CORRECTIONS are authoritative and final. Where a correction applies, use its value
   exactly, tag it "[verified: correction]", and ignore any SOURCE or memory that disagrees.

OUTPUT: Return a SINGLE JSON object and nothing else. No markdown fences, no commentary.
Use EXACTLY these keys, each mapping to a markdown string:
  "section_1", "section_2", "section_3", "section_4", "section_5", "section_6"

Write the markdown INSIDE each string using the structure below. Use REAL line
breaks between bullets and table rows (an actual newline in the JSON string), not
the literal two characters backslash-n.

BE CONCISE - this has a limited output budget. Use short phrases, not paragraphs.
Cover the named competitors plus AT MOST 2 discovered ones; keep the comparison
table to AT MOST 6 rows. A complete, valid JSON object matters more than length -
never run past the budget mid-document.

section_1 (MARKET SNAPSHOT):
- Avg INR/sqft range: <range> (carpet, {micromarket}) <tag>
- Total active inventory: <projects / units> <tag>
- Market temperature: [Hot / Stable / Cooling] - one-line reason
- Primary buyer: [profile, income bracket, end-use vs investment] <tag>
- YoY price appreciation: <%> <tag>

section_2 (COMPETITOR DEEP-DIVE) - for EACH project (named + any found in SOURCES):
**[Project Name] - [Developer]**
- Configurations: <X BHK (carpet sqft)> <tag>
- Pricing: <INR/sqft | all-in Cr> <tag>
- Stage: [Under Construction / Ready / New Launch] <tag>
- RERA: [number if in sources / Not registered / unknown] <tag>
- Key USP: [one line]
- Weakness / Gap: [one line]
Then:
**Market Pricing Band:** budget | mid | premium INR/sqft <tag>
**Dominant payment scheme:** [structure] <tag>

section_3 (COMPARISON TABLE) - a markdown table, one row per project:
| Project | Developer | Config | Carpet (sqft) | INR/sqft | All-in Price | Stage | Basis |
|---|---|---|---|---|---|---|---|
Put the source tag (e.g. S3 / estimated / unknown) in the Basis column. Use "unknown" in any
cell the sources do not support - do not fill cells with invented numbers.

section_4 (PRICING STRATEGY FOR {proj}):
- Recommended launch INR/sqft: <value> - justify vs nearest competitors (cite their tags)
- {cfg1}: <carpet sqft> -> <all-in Cr> <tag>
- {cfg2}: <carpet sqft> -> <all-in Cr> <tag>
- Floor rise, PLC premiums, parking, payment scheme, absorption forecast - label each
  [estimated] with reasoning, since these are projections.

section_5 (MARKET GAPS & DIFFERENTIATION):
GAP 1: [segment/config/price gap + why + demand signal]
GAP 2: ...
GAP 3: ...
HOW {proj} CAN WIN:
- [play 1]
- [play 2]
- [play 3]

section_6 (RISK FLAGS):
- Risk 1 [HIGH/MED/LOW]: [description] -> Mitigation: [one line]
- Risk 2 [HIGH/MED/LOW]: ...
- Risk 3 [HIGH/MED/LOW]: ...
- Risk 4 [HIGH/MED/LOW]: ...
- VERDICT: [GO / CAUTION / HOLD] - one sentence, noting how much rests on verified vs estimated data.
"""


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip()


def _normalize_md(s: str) -> str:
    """
    Turn escaped whitespace into real whitespace. Some models (e.g. gpt-oss) emit
    double-escaped newlines in their JSON, so after json.loads the section strings
    still contain literal "\\n" / "\\t" instead of real breaks - which renders bullets
    and tables as one run-on line and stops the table parser from seeing rows.
    """
    if not s:
        return ""
    return (
        s.replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace("\r\n", "\n")
        .strip()
    )


def parse_response(raw: str) -> dict[str, str]:
    """
    Primary parser: expect a JSON object with section_1..section_6 keys and map to
    {"1": ..., "6": ...}. Falls back to marker-based parse_sections() if JSON fails.
    Section strings are normalized so escaped newlines render as real line breaks.
    """
    if not raw:
        return {}
    candidate = _strip_code_fence(raw)
    try:
        data = json.loads(candidate)
        if isinstance(data, dict):
            out = {}
            for n in ("1", "2", "3", "4", "5", "6"):
                val = data.get(f"section_{n}")
                if isinstance(val, str) and val.strip():
                    out[n] = _normalize_md(val)
            if out:
                return out
    except (json.JSONDecodeError, TypeError):
        pass
    return {k: _normalize_md(v) for k, v in parse_sections(raw).items()}


def parse_sections(raw_result: str) -> dict[str, str]:
    sections = {}
    for sec in raw_result.split("SECTION_")[1:]:
        if ":" in sec:
            num = sec.split(":")[0].strip()
            sections[num] = ":".join(sec.split(":")[1:]).strip()
    return sections


def _find_col(headers: list[str], *needles: str) -> int | None:
    for i, h in enumerate(headers):
        if any(n in h for n in needles):
            return i
    return None


def extract_table_rows(section3: str) -> list[dict]:
    """
    Parse the SECTION_3 markdown comparison table into row dicts with keys:
    project, developer, config, carpet, price_sqft, all_in, stage, basis.
    Returns [] if no usable table is found.
    """
    if not section3:
        return []

    grid = []
    for line in section3.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        # skip markdown separator rows like |---|---|
        if cells and all(set(c) <= set("-: ") for c in cells):
            continue
        grid.append(cells)

    if len(grid) < 2:
        return []

    headers = [h.lower() for h in grid[0]]
    idx = {
        "project": _find_col(headers, "project"),
        "developer": _find_col(headers, "developer"),
        "config": _find_col(headers, "config"),
        "carpet": _find_col(headers, "carpet"),
        "price_sqft": _find_col(headers, "/sqft", "₹/sqft", "per sqft", "price"),
        "all_in": _find_col(headers, "all-in", "all in", "all‑in"),
        "stage": _find_col(headers, "stage"),
        "basis": _find_col(headers, "basis", "source"),
    }
    if idx["project"] is None:
        return []

    rows = []
    for cells in grid[1:]:
        def get(field):
            i = idx[field]
            return cells[i] if i is not None and i < len(cells) else ""

        project = get("project")
        if not project or project.lower() in ("project", "unknown", "-", "tbd"):
            continue
        rows.append(
            {
                "project": project,
                "developer": get("developer"),
                "config": get("config"),
                "carpet": get("carpet"),
                "price_sqft": get("price_sqft"),
                "all_in": get("all_in"),
                "stage": get("stage"),
                "basis": get("basis"),
            }
        )
    return rows


def verified_rows(rows: list[dict]) -> list[dict]:
    """Keep only rows whose Basis cites a real source id (e.g. S3), i.e. verified."""
    return [r for r in rows if re.search(r"\bS\d", r.get("basis", ""))]


def sections_to_text(sections: dict[str, str]) -> str:
    """Render the parsed sections back to a plain-text report for download."""
    parts = []
    for n in ("1", "2", "3", "4", "5", "6"):
        body = sections.get(n, "").strip()
        if not body:
            continue
        parts.append(f"SECTION_{n}: {SECTION_TITLES[n]}\n\n{body}")
    return "\n\n".join(parts)
