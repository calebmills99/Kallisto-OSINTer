[Documentation](https://github.com/avrtt/Kallisto-OSINTer/blob/main/docs/documentation.md)

<br/>

Kallisto is an LLM-based OSINT tool designed to perform deep web searches by orchestrating multiple web agents and a knowledge agent that uses state-of-the-art machine learning methods. The tool crawls the entire web to gather massive amounts of publicly available data, then leverages advanced LLM techniques to perform natural language tasks on that information.

> It's important to recognize the responsibility that comes with using public intelligence. Respect **🌈 personal "privacy" 🌈**.

The tool uses a multi-agent architecture:
- **Web agent** performs initial searches, scrapes results and extracts relevant text
- **Knowledge agent** orchestrates the web agents and recursively launches deep-dive agents to explore promising areas
- **Deep dive agents** target specific topics for additional context
- **LLM map-reduce** chunks large HTML pages and summarizes content to reduce token usage
- **LLM client** wraps calls to GPT-4 (or other LLM backends) for natural language processing tasks

## Features & examples
- **Person lookup**  
  For example, you can look up a person with a simple command:
  ```bash
  $ python examples/person_lookup.py "FULL_NAME" --ask "Write a summary about this person."
  ```
  The tool can then:
  - predict top 3 Myers-Briggs types with confidence levels
  - generate a psychological report
  - create a markdown resume
  - build a table of personal information
  - propose hypothetical account infiltration methods
  - draft a phishing email (for the sake of science ofc)
  - even generate a personalized ad if required

- **Prompt architecture**  
  Instead of a single greedy agent, the OSINT task is split into:
  - an initial search agent
  - a knowledge agent that asks for deep-dive topics
  - multiple deep-dive agents that target specific areas
  - a final LLM summary prompt

- **LangChain integration**  
  Build and run advanced LangChain pipelines to process OSINT data, generate insights and customize LLM chains using `src/langchain_integration.py` module.

- **Visualization**  
  Generate bar/line/pie charts based on OSINT data. Visual progress tracking is supported via tqdm in `src/visualization/data_visualizer.py`.

- **IP and DNS lookup**  
  With `src/modules/ip_lookup.py` and `src/modules/dns_lookup.py` modules, you can perform comprehensive IP analysis using ipwhois and retrieve DNS records with dnspython.

- **Alternative web scraping**  
  Utilize aiohttp and httpx for high-performance, asynchronous web scraping with proxy rotation and randomized user agents.

- **Tools & techniques**
  - **Search:** uses the Serper API for Google-powered searches with advanced filtering (country, language, date range)
  - **Read link:** uses ScrapingBee to reliably bypass bot detection and perform JS rendering
  - **Chunk & summarize:** a recursive method to chunk HTML, strip it to text and summarize via LLM
  - **Proxy & user-agent management:** validates proxies and randomizes user-agents to mimic human behavior
  - **Username search:** searches through a list of URLs concurrently for a given username

- **GUI**  
  `src/ui/qt_interface.py` module is a PyQt6-based interface to interactively run OSINT tasks, view aggregated knowledge and display visualizations.

- [to be expanded]


## Project structure

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

## Dependencies
```
anyio
langchain
zipp
validators
tqdm
ipwhois
fake_useragent
PyQt6
requests
openai
beautifulsoup4
lxml
colorama
google-search-results
httpx
tenacity
requests_html
aiohttp
urllib3
asyncio
lxml_html_clean
html_clean
dnspython
aiohttp-socks
python-socks[asyncio]
matplotlib
```

## Installation
Install the package directly via pip:

```bash
pip install git+https://github.com/avrtt/Kallisto-OSINTer.git
```

## Environment setup

Before running, ensure you set the following environment variables:

```bash
export OPENAI_API_KEY=your_openai_api_key
export SERPER_API_KEY=your_serper_api_key
export SCRAPINGBEE_API_KEY=your_scrapingbee_api_key
```

## Usage

- **Person lookup**  
  See `examples/person_lookup.py` for a command-line interface that uses the Kallisto to research individuals.

- **Username search**  
  See `src/modules/username_search.py` for multi-threaded username checks over lists of URLs.

- **GUI mode**  
  Run the GUI using:  
  ```bash
  python -m kallisto_osinter.src.ui.qt_interface
  ```

- [to be expanded]

## Testing
Unit tests are located in the `tests` folder. Run all tests using:

```bash
python -m unittest discover -s tests
```

## To-do
- Improve asynchronous scraping and proxy management
- Expand LangChain pipelines with more customizable chains
- Enhance GUI functionalities with interactive elements
- Integrate additional data sources and APIs (social platforms mostly)

## Contributing
PRs and issues are welcome.

## License
MIT

