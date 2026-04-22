# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Streamlit-based real estate competition analysis tool for the Indian market. Users input a micro-market, city, project details, and known competitors. The app fetches live data from Google (via SerpAPI), sends it to Groq's LLaMA 3.3 70B model with a structured prompt, and renders the AI-generated report in six tabbed sections. Users can also download a branded PowerPoint deck or plain-text report.

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

API keys (`GROQ_API_KEY`, `SERP_API_KEY`) must be configured in Streamlit secrets (`.streamlit/secrets.toml`), not environment variables. The app reads them via `st.secrets`.

## Architecture

```
app.py              → Streamlit UI only (form, tabs, status updates, downloads)
config.py           → All constants: API params, model config, city/state/RERA mappings
data_fetcher.py     → SerpAPI live data fetching (market + competitor + RERA queries)
prompt_builder.py   → LLM prompt construction + section response parsing
style.css           → Global dark-theme CSS (loaded by app.py)
ppt/
  theme.py          → Color palette (RGBColor constants)
  helpers.py        → Low-level shape/text primitives (add_rectangle, add_textbox, etc.)
  generator.py      → 9-slide deck builder using helpers + theme
```

**Data flow:** `app.py` collects user input → `data_fetcher.fetch_live_data()` queries SerpAPI → `prompt_builder.build_prompt()` constructs the LLM prompt → Groq API call → `prompt_builder.parse_sections()` splits response into dict → tabs display sections → `ppt.generator.generate_ppt()` builds downloadable deck.

## Key Design Decisions

- **Section parsing contract**: The LLM prompt enforces `SECTION_1:` through `SECTION_6:` markers. `parse_sections()` splits on `SECTION_` and uses the number before the first `:` as a dict key. If the LLM output format drifts, parsing breaks silently (sections show "not generated").
- **PPT is pixel-positioned**: All slide elements use absolute `Inches()` coordinates. Changing slide dimensions (currently 10x7.5) requires updating every position constant across `ppt/generator.py`.
- **RERA portal targeting**: `data_fetcher` maps cities to state RERA portal domains (via `config.CITY_TO_STATE` and `config.RERA_PORTALS`) for `site:` queries, improving regulatory data quality.
- **Config centralization**: Model name, API params, max tokens, and geographic mappings all live in `config.py` to avoid scattered magic values.

## Dependencies

- `streamlit` — UI framework
- `groq` — LLM API client (uses LLaMA 3.3 70B via Groq)
- `requests` — SerpAPI HTTP calls
- `python-pptx` + `lxml` — PowerPoint generation with low-level XML manipulation for cell backgrounds

Note: `requirements.py` is a partial duplicate of `requirements.txt` (only lists `streamlit` and `groq`). The canonical dependency file is `requirements.txt`.
