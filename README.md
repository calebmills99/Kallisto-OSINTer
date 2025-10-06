# Kallisto-OSINTer: Drag Queen Story Time for Curious Sleuths

[Full documentation and technical deep-dive](https://github.com/avrtt/Kallisto-OSINTer/blob/main/docs/documentation.md)

## Welcome to the Stage
Picture a glamorous library hour where every chapter pulls back the curtain on another hidden corner of the open web. Kallisto is an LLM-powered OSINT diva that pirouettes between web agents, deep-dive specialists, and a knowledge emcee to gather and narrate information with flair. Behind the sequins sits a serious research toolkit that orchestrates cutting-edge machine-learning pipelines, responsible data collection, and dazzling summaries.

> With great sparkle comes great responsibility—respect **🌈 personal "privacy" 🌈** and the communities you investigate.

## Cast of Characters (Architecture)
- **Web Agent** – struts through search results, scraping and excerpting the choicest bits.
- **Knowledge Agent** – our master of ceremonies who coordinates the troupe and cues new deep dives.
- **Deep Dive Agents** – specialty performers who explore promising leads in detail.
- **LLM Map-Reduce** – slices hefty HTML monologues into digestible acts and delivers polished recaps.
- **LLM Client** – wraps GPT-4 with graceful rate limiting and now falls back to Anthropic and Mistral models when needed.

## Headline Acts (Features)
- **Person Lookup Production** – generate summaries, psychological reads, resumes, phishing simulations (for research!), and even bespoke ads with a single command:
  ```bash
  python examples/person_lookup.py "FULL_NAME" --ask "Write a summary about this person."
  ```
- **Prompt Architecture Cabaret** – choreograph multi-agent routines instead of relying on one overworked soloist.
- **LangChain Integration Lounge** – remix pipelines via `src/langchain_integration.py` and `LangChainIntegrator` utilities.
- **Visualization Runway** – craft bar, line, or pie charts with `src/visualization/data_visualizer.py` while tracking progress via `tqdm`.
- **IP & DNS Oracle** – consult `src/modules/ip_lookup.py` and `src/modules/dns_lookup.py` for network reconnaissance.
- **Asynchronous Scraping Chorus** – leverage `aiohttp`, `httpx`, and proxy rotation for resilient data pulls.
- **Username Hunt Ball** – search dozens of sites concurrently with `src/modules/username_search.py`.
- **PyQt6 Backstage Pass** – take the GUI for a spin with `src/ui/qt_interface.py`.

## Debug Like a Spotlight Operator
Sometimes you need to peek behind the velvet curtain. Enable verbose logging and debug helpers with:

```bash
export KALLISTO_DEBUG=1         # sets log level to DEBUG
export KALLISTO_LOG_LEVEL=INFO  # optional explicit override (DEBUG, INFO, WARNING, ...)
```

For a ready-made routine, run the LangChain integrator’s debug showcase:

```bash
python -c "from src.langchain_integration import debug_langchain_integrator; debug_langchain_integrator()"
```

Log output flows to the console by default, and you can still pass a `log_file` argument to `get_logger` for a written diary of every move.

## Project Structure
```
.
├── README.md
├── setup.py
├── requirements.txt
├── docs/
│   └── documentation.md
├── examples/
│   └── person_lookup.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── langchain_integration.py
│   ├── ui/
│   │   └── qt_interface.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── cache.py
│   │   ├── logger.py
│   │   ├── proxies.py
│   │   └── user_agents.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── web_agent.py
│   │   ├── knowledge_agent.py
│   │   └── deep_dive_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── read_link.py
│   │   └── llm_map_reduce.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── person_lookup.py
│   │   ├── ip_lookup.py
│   │   ├── dns_lookup.py
│   │   ├── username_search.py
│   │   └── google_filter.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   └── prompt_templates.py
│   ├── visualization/
│   │   └── data_visualizer.py
│   ├── web/
│   │   └── web_scraper.py
│   └── async_web/
│       └── async_scraper.py
└── tests/
    ├── test_llm.py
    ├── test_langchain_integration.py
    ├── test_visualization.py
    ├── test_ip_lookup.py
    ├── test_async_scraper.py
    ├── test_qt_interface.py
    └── test_agents.py
```

## Installation
Install directly from GitHub:

```bash
pip install git+https://github.com/avrtt/Kallisto-OSINTer.git
```

## Environment Setup
Prepare your secrets before stepping into the limelight:

```bash
export OPENAI_API_KEY=your_openai_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key   # optional fallback provider
export MISTRAL_API_KEY=your_mistral_api_key       # optional fallback provider
export KILOCODE_API_KEY=your_kilocode_api_key     # optional ChatGPT 3.5 via Kilocode
# export KILOCODE_API_BASE=https://api.kilocode.com/v1  # override Kilocode endpoint if needed
export SERPER_API_KEY=your_serper_api_key
export SCRAPINGBEE_API_KEY=your_scrapingbee_api_key
```

Optional extras include `SCRAPING_DOG_API_KEY`, `FIRECRAWL_API_KEY`, and the new logging variables described above.

## Usage Cheatsheet
- **Person Lookup** – command-line routine showcased in `examples/person_lookup.py`.
- **Username Search** – run `src/modules/username_search.py` for multi-threaded checks.
- **GUI Mode** – launch the PyQt experience:
  ```bash
  python -m kallisto_osinter.src.ui.qt_interface
  ```
- **LangChain Pipeline** – orchestrate custom flows with `LangChainIntegrator` utilities.

### Saving command output

Both CLI entry points (`person_lookup` and `username_search`) now accept an optional `--output` flag to save results locally. The format is inferred from the file extension or can be forced with `--output-format` (`txt`, `md`, `csv`, or `json`).

```bash
python -m src.main person_lookup "Ada Lovelace" --ask "Provide a brief bio" --output reports/ada.md
python -m src.main username_search ada --urls https://example.com --output usernames.json --output-format json
```

## Testing
Unit tests live in `tests/`. Run the full suite with:

```bash
python -m unittest discover -s tests
```

## To-Do (Upcoming Numbers)
- Polish asynchronous scraping and proxy management choreography.
- Expand LangChain routines with new customizable scenes.
- Add interactive flair to the GUI stage.
- Integrate more social-platform data sources.

## Contributing & License
PRs, issues, and encore suggestions are welcome. Licensed under MIT.
