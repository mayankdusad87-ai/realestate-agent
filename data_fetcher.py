"""
Live market data fetching via SerpAPI.
"""
import logging

import requests
import streamlit as st

logger = logging.getLogger(__name__)

from config import (
    CITY_TO_STATE,
    RERA_PORTALS,
    SERPAPI_COUNTRY,
    SERPAPI_LANGUAGE,
    SERPAPI_NUM_RESULTS,
    SERPAPI_TIMEOUT,
    SERPAPI_URL,
    MAX_COMPETITORS,
)


def _build_queries(
    micromarket: str,
    city: str,
    product_type: str,
    competitors: list[str],
    portal: str,
) -> list[str]:
    queries = [
        f"property price per sqft {micromarket} {city} 2025 2026 {product_type.lower()}",
        f"new residential projects launch {micromarket} {city} 2026",
        f"real estate market trend {micromarket} {city} latest",
        f"site:{portal} {micromarket} {city} registered project carpet area",
        f"RERA registered projects {micromarket} {city} carpet area possession date 2026 2027",
        f"RERA {city} {micromarket} project registration number possession date delayed",
    ]

    for comp in competitors[:MAX_COMPETITORS]:
        queries.append(f"{comp} {city} price sqft carpet area configurations")
        queries.append(f"RERA registration {comp} {city} carpet area possession status")

    return queries


def _fetch_snippets(queries: list[str], serp_key: str) -> list[str]:
    snippets = []
    for query in queries:
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
            for item in data.get("organic_results", [])[:4]:
                snippet = item.get("snippet", "")
                source = item.get("source", "")
                title = item.get("title", "")
                if snippet:
                    snippets.append(f"[{source}] {title}: {snippet}")
        except Exception:
            continue
    return snippets


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_live_data(
    micromarket: str,
    city: str,
    product_type: str,
    competitors: tuple[str, ...],
    serp_key: str,
) -> str:
    state = CITY_TO_STATE.get(city.lower(), "")
    portal = RERA_PORTALS.get(state, "rera")

    queries = _build_queries(micromarket, city, product_type, list(competitors), portal)
    snippets = _fetch_snippets(queries, serp_key)

    return (
        "\n\n".join(snippets)
        if snippets
        else "Live data unavailable - AI will use knowledge base."
    )
