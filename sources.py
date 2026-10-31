"""
Authoritative source connectors (Phase 1 of the multi-source data model).

A connector takes the sources already fetched (by data_fetcher) and extracts
higher-trust, structured records from them - no new network calls, no scraping of
gated portals. The first connector is RERA: it identifies results that came from
an official state RERA portal or that carry a RERA registration number, and marks
those figures as the highest-trust public source (after team corrections).

The design is additive: connectors only ADD a prioritized block to the prompt;
the existing source flow is unchanged. Future connectors (e-ASR price floor,
NHB RESIDEX / RBI HPI trend) plug in the same way.
"""
import re

from config import CITY_TO_STATE, RERA_PORTALS

# MahaRERA-style registration numbers, e.g. P51800000947. Other states differ;
# the stronger signal is the official-portal URL, handled separately below.
RERA_REG_RE = re.compile(r"\bP\d{9,}\b")


class SourceConnector:
    """Base class: turn fetched sources into tagged, prioritized records."""

    name = "base"
    tag = ""

    def extract(self, sources: list[dict], city: str) -> list[dict]:
        raise NotImplementedError

    def format(self, records: list[dict]) -> str:
        raise NotImplementedError


class RERAConnector(SourceConnector):
    name = "RERA"
    tag = "RERA"

    def _portal(self, city: str) -> str:
        state = CITY_TO_STATE.get((city or "").lower(), "")
        return RERA_PORTALS.get(state, "")

    def extract(self, sources: list[dict], city: str) -> list[dict]:
        portal = self._portal(city)
        records = []
        for s in sources:
            url = s.get("url", "") or ""
            blob = " ".join(
                str(s.get(k, "")) for k in ("title", "snippet", "page_text")
            )
            from_portal = bool(portal) and portal in url
            regs = list(dict.fromkeys(RERA_REG_RE.findall(blob)))
            if from_portal or regs:
                records.append(
                    {
                        "id": s.get("id", ""),
                        "url": url,
                        "title": s.get("title", ""),
                        "reg_numbers": regs,
                        "from_portal": from_portal,
                    }
                )
        return records

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""
        lines = [
            "RERA REGISTRY FINDINGS (from the official RERA portal or RERA "
            "registration numbers in the sources above). Figures these support are "
            "[verified: RERA] - the highest-trust PUBLIC source, below only team "
            "corrections:"
        ]
        for r in records:
            why = "official portal" if r["from_portal"] else "reg no. in source"
            regs = (" | regs: " + ", ".join(r["reg_numbers"])) if r["reg_numbers"] else ""
            title = (r.get("title") or "").strip()[:80]
            lines.append(f"- [{r['id']}] {title} ({why}){regs}")
        return "\n".join(lines)


# Ordered list of active connectors. Add e-ASR / RESIDEX connectors here later.
CONNECTORS: list[SourceConnector] = [RERAConnector()]


def build_authoritative_block(sources: list[dict], city: str) -> tuple[str, int]:
    """
    Run every connector over the fetched sources and return
    (prioritized_prompt_block, total_record_count). Empty block if nothing found.
    """
    blocks = []
    total = 0
    for conn in CONNECTORS:
        records = conn.extract(sources, city)
        total += len(records)
        block = conn.format(records)
        if block:
            blocks.append(block)
    return ("\n\n".join(blocks), total)
