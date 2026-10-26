"""
Live market data fetching via SerpAPI.

Besides Google result snippets, this module now fetches and extracts the text of
the actual pages behind the top results, numbers every source so the LLM can cite
it, and returns a status payload so the UI can tell the user loudly when the live
fetch produced nothing (instead of silently falling back to a hallucinated report).
"""
import html
import logging
import re

import requests
import streamlit as st

logger = logging.getLogger(__name__)

from config import (
    CITY_TO_STATE,
    RERA_PORTALS,
    LIVE_DATA_SNIPPET_LIMIT,
    MAX_COMPETITORS,
    MAX_PAGES_TO_FETCH,
    PAGE_FETCH_ENABLED,
    PAGE_FETCH_TIMEOUT,
    PAGE_FETCH_USER_AGENT,
    PAGE_TEXT_CHAR_LIMIT,
    SERPAPI_COUNTRY,
    SERPAPI_LANGUAGE,
    SERPAPI_NUM_RESULTS,
    SERPAPI_TIMEOUT,
    SERPAPI_URL,
)


def _build_queries(
    micromarket: str,
    city: str,
    product_type: str,
    competitors: list[str],
    portal: str,
) -> list[str]:
    queries = [
        f"property price per sqft {micromarket} {city} {product_type.lower()}",
        f"new residential projects launch {micromarket} {city}",
        f"real estate market trend {micromarket} {city} latest",
        f"site:{portal} {micromarket} {city} registered project carpet area",
        f"RERA registered projects {micromarket} {city} carpet area possession date",
        f"RERA {city} {micromarket} project registration number possession date delayed",
    ]

    for comp in competitors[:MAX_COMPETITORS]:
        queries.append(f"{comp} {city} price sqft carpet area configurations")
        queries.append(f"RERA registration {comp} {city} carpet area possession status")

    return queries


# Messages SerpAPI returns when a query simply has no organic results. These are
# expected (especially for strict site:/RERA queries) and must not alarm the user.
_BENIGN_SERP_ERRORS = (
    "hasn't returned any results",
    "has not returned any results",
    "no results found",
)


def _is_benign_serp_error(msg: str) -> bool:
    low = msg.lower()
    return any(p in low for p in _BENIGN_SERP_ERRORS)


def _fetch_organic(query: str, serp_key: str) -> tuple[list[dict], str]:
    """Return (organic_results, error_message). error_message is '' on success."""
    try:
        res = requests.get(
            SERPAPI_URL,
            params={
                "q": query,
                "api_key": serp_key,
                "num": SERPAPI_NUM_RESULTS,
                "gl": SERPAPI_COUNTRY,
                "hl": SERPAPI_LANGUAGE,
            },
            timeout=SERPAPI_TIMEOUT,
        )
        data = res.json()
    except Exception as e:  # network / JSON error
        logger.warning("SerpAPI request failed for %r: %s", query, e)
        return [], f"request failed: {e}"

    # SerpAPI reports problems (bad key, out of searches, etc.) in an "error" field.
    # But it ALSO uses that field for the benign "no results for this query" case,
    # which is normal for strict site:/RERA queries - that is an empty result, not
    # a failure, so we must not surface it as an error banner.
    if isinstance(data, dict) and data.get("error"):
        msg = str(data["error"])
        if _is_benign_serp_error(msg):
            return [], ""
        logger.warning("SerpAPI error for %r: %s", query, msg)
        return [], msg

    return data.get("organic_results", [])[:4], ""


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_DROP_RE = re.compile(r"<(script|style|noscript|template|svg)[^>]*>.*?</\1>", re.I | re.S)


def _html_to_text(raw_html: str) -> str:
    """Very small, dependency-free HTML -> text reducer."""
    no_blocks = _DROP_RE.sub(" ", raw_html)
    no_tags = _TAG_RE.sub(" ", no_blocks)
    text = html.unescape(no_tags)
    return _WS_RE.sub(" ", text).strip()


def _fetch_page_text(url: str) -> str:
    """Fetch a URL and return a trimmed plain-text extract, or '' on any failure."""
    try:
        res = requests.get(
            url,
            headers={"User-Agent": PAGE_FETCH_USER_AGENT},
            timeout=PAGE_FETCH_TIMEOUT,
        )
        ctype = res.headers.get("Content-Type", "")
        if "html" not in ctype and "text" not in ctype:
            return ""
        return _html_to_text(res.text)[:PAGE_TEXT_CHAR_LIMIT]
    except Exception as e:
        logger.info("Page fetch failed for %s: %s", url, e)
        return ""


def _format_sources(sources: list[dict]) -> str:
    blocks = []
    for s in sources:
        parts = [f"[{s['id']}] {s.get('source') or ''} | {s.get('title') or ''}".strip(" |")]
        if s.get("url"):
            parts.append(f"URL: {s['url']}")
        if s.get("snippet"):
            parts.append(f"Snippet: {s['snippet']}")
        if s.get("page_text"):
            parts.append(f"Page extract: {s['page_text']}")
        blocks.append("\n".join(parts))
    return ("\n\n---\n\n".join(blocks))[:LIVE_DATA_SNIPPET_LIMIT]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_live_data(
    micromarket: str,
    city: str,
    product_type: str,
    competitors: tuple[str, ...],
    serp_key: str,
) -> dict:
    """
    Returns a dict:
      text       -> formatted, numbered sources block for the prompt ([S1], [S2], ...)
      sources    -> list of source dicts (id, url, source, title, snippet, page_text)
      live_ok    -> True if at least one source carries real content
      stats      -> counts for the UI
      errors     -> SerpAPI error messages encountered (deduped)
    """
    state = CITY_TO_STATE.get(city.lower(), "")
    portal = RERA_PORTALS.get(state, "rera")

    queries = _build_queries(micromarket, city, product_type, list(competitors), portal)

    sources: list[dict] = []
    errors: list[str] = []
    seen_urls: set[str] = set()

    for query in queries:
        organic, err = _fetch_organic(query, serp_key)
        if err and err not in errors:
            errors.append(err)
        for item in organic:
            url = item.get("link", "")
            key = url or item.get("title", "")
            if key and key in seen_urls:
                continue
            if key:
                seen_urls.add(key)
            sources.append(
                {
                    "id": f"S{len(sources) + 1}",
                    "url": url,
                    "source": item.get("source", ""),
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "page_text": "",
                }
            )

    pages_fetched = 0
    if PAGE_FETCH_ENABLED:
        for s in sources:
            if pages_fetched >= MAX_PAGES_TO_FETCH:
                break
            if not s["url"]:
                continue
            text = _fetch_page_text(s["url"])
            if text:
                s["page_text"] = text
                pages_fetched += 1

    live_ok = any(s.get("snippet") or s.get("page_text") for s in sources)

    return {
        "text": _format_sources(sources) if live_ok else "",
        "sources": sources,
        "live_ok": live_ok,
        "stats": {
            "queries": len(queries),
            "sources": len(sources),
            "pages_fetched": pages_fetched,
        },
        "errors": errors,
    }
