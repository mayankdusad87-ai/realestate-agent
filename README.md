# Real Estate Competition Analysis Engine

A Streamlit-based tool that generates AI-powered competition analysis reports for the Indian real estate market. Enter a micro-market, city, project details, and known competitors — the app fetches live market data via Google (SerpAPI), sends it to Groq's LLaMA 3.3 70B model, and renders a structured report across six tabbed sections. Download the results as a branded PowerPoint deck or plain-text report.

## Features

- **Live market data** — Fetches real-time Google search results for market trends, competitor info, and RERA regulatory data
- **AI-generated analysis** — Uses LLaMA 3.3 70B (via Groq) to produce structured competition reports
- **RERA portal targeting** — Automatically maps cities to their state RERA portal for more relevant regulatory queries
- **PowerPoint export** — Download a branded 9-slide deck with the full analysis
- **Plain-text export** — Download the raw report as text
- **Caching** — SerpAPI results are cached for 1 hour to reduce redundant API calls
- **Retry logic** — Groq API calls retry automatically on failure

## Supported Cities

Mumbai, Pune, Bengaluru, Hyderabad, Delhi, Noida, Gurgaon, Ahmedabad, Surat, Chennai, Kolkata, Jaipur, Lucknow, Chandigarh, Bhopal, Indore, and more (30+ cities across 12 states).

## Prerequisites

- Python 3.9+
- A [Groq API key](https://console.groq.com/)
- A [SerpAPI key](https://serpapi.com/)

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/mayankdusad87-ai/realestate-agent.git
   cd realestate-agent
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure API keys**

   Copy the example secrets file and add your keys:

   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

   Edit `.streamlit/secrets.toml`:

   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   SERP_API_KEY = "your-serpapi-key-here"
   ```

4. **Run the app**

   ```bash
   streamlit run app.py
   ```

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## Project Structure

```
app.py              → Streamlit UI (form, tabs, status updates, downloads)
config.py           → Constants: API params, model config, city/state/RERA mappings
data_fetcher.py     → SerpAPI data fetching (market + competitor + RERA queries)
prompt_builder.py   → LLM prompt construction and section response parsing
style.css           → Dark-theme CSS
ppt/
  theme.py          → Color palette (RGBColor constants)
  helpers.py        → Shape/text primitives (add_rectangle, add_textbox, etc.)
  generator.py      → 9-slide deck builder
tests/
  test_prompt_builder.py → Tests for parse_sections() contract
```

## How It Works

1. User fills in micro-market, city, project name, product type, launch timeline, and known competitors
2. `data_fetcher.fetch_live_data()` queries SerpAPI for market data, competitor info, and RERA records
3. `prompt_builder.build_prompt()` constructs a structured prompt with the live data
4. The prompt is sent to Groq's LLaMA 3.3 70B model
5. `prompt_builder.parse_sections()` splits the response into six sections
6. Sections are displayed in Streamlit tabs
7. Users can download the report as a PowerPoint deck or plain text

## Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `groq` | LLM API client (LLaMA 3.3 70B) |
| `requests` | SerpAPI HTTP calls |
| `python-pptx` | PowerPoint generation |
| `lxml` | XML manipulation for PPT cell backgrounds |

## License

See [LICENSE](LICENSE) for details.
