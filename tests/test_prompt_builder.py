"""
Tests for prompt_builder module — focused on parse_sections,
the fragile contract between LLM output format and the parser.
"""
import json

from prompt_builder import (
    extract_table_rows,
    parse_response,
    parse_sections,
    sections_to_text,
    verified_rows,
)


# ── extract_table_rows / verified_rows (Phase 1) ─────────────────────────────

_TABLE = (
    "| Project | Developer | Config | Carpet (sqft) | INR/sqft | All-in Price | Stage | Basis |\n"
    "|---|---|---|---|---|---|---|---|\n"
    "| Lodha X | Lodha | 2BHK | 650 | ₹25,000 | ₹1.6 Cr | UC | S3 |\n"
    "| Godrej Y | Godrej | 3BHK | 900 | ₹22,000 | ₹2.0 Cr | Ready | estimated |\n"
    "| unknown | | | | | | | |\n"
)


def test_extract_table_rows_maps_columns():
    rows = extract_table_rows(_TABLE)
    assert len(rows) == 2  # placeholder 'unknown' row dropped
    first = rows[0]
    assert first["project"] == "Lodha X"
    assert first["developer"] == "Lodha"
    assert first["carpet"] == "650"
    assert first["price_sqft"] == "₹25,000"
    assert first["all_in"] == "₹1.6 Cr"
    assert first["stage"] == "UC"
    assert first["basis"] == "S3"


def test_verified_rows_keeps_only_sourced():
    rows = extract_table_rows(_TABLE)
    v = verified_rows(rows)
    assert len(v) == 1
    assert v[0]["project"] == "Lodha X"


def test_extract_table_rows_no_table():
    assert extract_table_rows("No table here, just prose.") == []
    assert extract_table_rows("") == []


def test_parse_sections_standard_output():
    raw = (
        "SECTION_1: MARKET SNAPSHOT\nSome market data here\n\n"
        "SECTION_2: COMPETITOR DEEP-DIVE\nCompetitor info\n\n"
        "SECTION_3: COMPETITOR COMPARISON TABLE\n| Col1 | Col2 |\n\n"
        "SECTION_4: PRICING STRATEGY\nPricing details\n\n"
        "SECTION_5: MARKET GAPS\nGap analysis\n\n"
        "SECTION_6: RISK FLAGS\nRisk info"
    )
    result = parse_sections(raw)
    assert set(result.keys()) == {"1", "2", "3", "4", "5", "6"}
    assert "market data" in result["1"].lower()
    assert "competitor info" in result["2"].lower()


def test_parse_sections_with_preamble():
    raw = (
        "Here is your analysis:\n\n"
        "SECTION_1: MARKET SNAPSHOT\nData here"
    )
    result = parse_sections(raw)
    assert "1" in result
    assert "data here" in result["1"].lower()


def test_parse_sections_empty_input():
    assert parse_sections("") == {}


def test_parse_sections_no_markers():
    assert parse_sections("Just a plain text response with no sections.") == {}


def test_parse_sections_partial_output():
    raw = (
        "SECTION_1: MARKET SNAPSHOT\nMarket info\n\n"
        "SECTION_2: COMPETITOR DEEP-DIVE\nCompetitor info"
    )
    result = parse_sections(raw)
    assert set(result.keys()) == {"1", "2"}
    assert "3" not in result


def test_parse_sections_preserves_colons_in_content():
    raw = "SECTION_1: MARKET SNAPSHOT\nAvg price: ₹18,000 - ₹24,000/sqft"
    result = parse_sections(raw)
    assert "₹18,000" in result["1"]
    assert "₹24,000" in result["1"]


def test_parse_sections_handles_extra_whitespace():
    raw = "SECTION_1 :  MARKET SNAPSHOT \n  Some data  "
    result = parse_sections(raw)
    assert "1" in result


# ── parse_response (JSON-first, marker fallback) ─────────────────────────────

def test_parse_response_json():
    raw = json.dumps({f"section_{n}": f"body {n}" for n in range(1, 7)})
    result = parse_response(raw)
    assert set(result.keys()) == {"1", "2", "3", "4", "5", "6"}
    assert result["3"] == "body 3"


def test_parse_response_json_in_code_fence():
    payload = json.dumps({"section_1": "market", "section_2": "comp"})
    raw = f"```json\n{payload}\n```"
    result = parse_response(raw)
    assert result["1"] == "market"
    assert result["2"] == "comp"


def test_parse_response_skips_blank_sections():
    raw = json.dumps({"section_1": "data", "section_2": "   "})
    result = parse_response(raw)
    assert "1" in result
    assert "2" not in result


def test_parse_response_falls_back_to_markers():
    raw = "SECTION_1: MARKET\nmarket body\n\nSECTION_2: COMP\ncomp body"
    result = parse_response(raw)
    assert set(result.keys()) == {"1", "2"}


def test_parse_response_empty():
    assert parse_response("") == {}


def test_sections_to_text_roundtrip():
    sections = {"1": "alpha", "3": "gamma"}
    text = sections_to_text(sections)
    assert "SECTION_1: MARKET SNAPSHOT" in text
    assert "alpha" in text
    assert "SECTION_3: COMPETITOR COMPARISON TABLE" in text
    # sections not present are skipped
    assert "SECTION_2" not in text
