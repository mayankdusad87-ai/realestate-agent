"""Tests for the Phase 1 authoritative source connectors (RERA)."""
from sources import RERAConnector, build_authoritative_block


def _sources():
    return [
        {  # official MahaRERA portal URL
            "id": "S1",
            "url": "https://maharera.mahaonline.gov.in/project/xyz",
            "title": "Rustomjee Ozone",
            "snippet": "registered project",
            "page_text": "",
        },
        {  # ordinary site but carries a RERA registration number
            "id": "S2",
            "url": "https://example.com/p",
            "title": "Ekta Tripolis",
            "snippet": "RERA P51800000947 Phase I, possession 2026",
            "page_text": "",
        },
        {  # unrelated news result
            "id": "S3",
            "url": "https://news.com/a",
            "title": "Market trend",
            "snippet": "prices rising in the suburbs",
            "page_text": "",
        },
    ]


def test_extract_picks_portal_and_regno_only():
    recs = RERAConnector().extract(_sources(), "Mumbai")
    assert {r["id"] for r in recs} == {"S1", "S2"}  # S3 excluded


def test_portal_flag_and_regno_captured():
    recs = {r["id"]: r for r in RERAConnector().extract(_sources(), "Mumbai")}
    assert recs["S1"]["from_portal"] is True
    assert recs["S2"]["from_portal"] is False
    assert "P51800000947" in recs["S2"]["reg_numbers"]


def test_format_block_tags_verified_rera():
    conn = RERAConnector()
    block = conn.format(conn.extract(_sources(), "Mumbai"))
    assert "[verified: RERA]" in block
    assert "P51800000947" in block


def test_build_authoritative_block_counts():
    block, total = build_authoritative_block(_sources(), "Mumbai")
    assert total == 2
    assert "RERA REGISTRY FINDINGS" in block


def test_unknown_city_has_no_portal_match():
    # city not in the map -> no portal; only the reg-number source qualifies
    recs = RERAConnector().extract(_sources(), "Nowhereville")
    assert {r["id"] for r in recs} == {"S2"}


def test_empty_sources_is_empty():
    block, total = build_authoritative_block([], "Mumbai")
    assert total == 0 and block == ""
