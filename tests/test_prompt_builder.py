"""
Tests for prompt_builder module — focused on parse_sections,
the fragile contract between LLM output format and the parser.
"""
from prompt_builder import parse_sections


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
