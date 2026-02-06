# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Guardr** is an AI-powered dating safety platform for the LGBTQ+ community, built on top of **Kallisto-OSINTer**, an open-source intelligence gathering framework.

- **Backend:** Flask API (`guardr_api.py`) wrapping Kallisto OSINT tools
- **Frontend:** Next.js 15 application (in separate `guardrV6-clean/website/` repo)
- **Core Engine:** Kallisto-OSINTer multi-agent OSINT system
- **LLM Provider:** OpenRouter (primary) with OpenAI/Anthropic fallback

## Development Setup

### Environment Setup
```bash
# Use the Python venv (REQUIRED)
source venv/bin/activate

# Load API keys from the CORRECT file
source api-keys.zsh  # NOT ~/.apikeys.zsh (that's outdated)

# Install dependencies
pip install -r requirements.txt
```

### Running Services

**Backend API:**
```bash
source venv/bin/activate && source api-keys.zsh
python guardr_api.py
# Runs on http://localhost:5000
```

**Frontend (separate repo):**
```bash
cd /home/nobby/guardrV6-clean/website
npm run dev
# Runs on http://localhost:3002 (or 3001)
```

### Testing

**Quick PERA Cycle Test (no heavy OSINT):**
```bash
source venv/bin/activate && source api-keys.zsh
python test_guardr_quick.py
```

**Backend API Tests:**
```bash
source venv/bin/activate && source api-keys.zsh
python test_backend_basic.py        # Basic functionality
python test_integration.py          # Frontend-backend integration
python test_security.py             # Security & privacy
python test_speed.py                # Performance benchmarking
python test_openrouter.py          # LLM provider testing
```

**Full Test Suite:**
```bash
./run_all_tests.sh  # Requires backend running on port 5000
```

**Note:** Tests that trigger real OSINT take 60-120 seconds per call. Use quick test modes when possible.

## Architecture

### Backend: Flask API (`guardr_api.py`)

Exposes REST endpoints for dating safety checks:
- `GET /api/health` - Health check
- `POST /api/check` - Person verification (triggers Kallisto OSINT)
  - Input: `{name, location?, username?}`
  - Output: `{risk_level, risk_score, person_verification, safety_tips}`

Safety tips rotate from 4 categories: smart_habits, friendly_reminders, did_you_know, you_decide

### Kallisto OSINT Engine

**Multi-Agent Architecture:**
1. **KnowledgeAgent** (`src/agents/knowledge_agent.py`) - Orchestrates investigation rounds (default: 1 round)
2. **WebAgent** (`src/agents/web_agent.py`) - Performs web searches and scraping (limit: 7 results)
3. **DeepDiveAgent** - Focused investigation on specific topics
4. **LLM Client** (`src/llm/llm_client.py`) - Multi-provider LLM with fallback

**Investigation Flow:**
```
person_lookup(name, question, config, location?)
  └─> KnowledgeAgent (1 round)
       └─> WebAgent.search() via Serper API (7 results)
            └─> Parallel fetch & LLM summarization
                 └─> map_reduce aggregation
```

**Key Configuration (`src/config.py`):**
- `LLM_PROVIDER_ORDER`: ["openai", "anthropic", "mistral"] (Kilocode removed - was broken)
- `LLM_MODEL_OVERRIDES`: Uses gpt-4o-mini by default
- Search limited to 7 results for speed (was 10)
- Investigation rounds: 1 (was 2)

### LLM Integration

**Current Setup:**
- **Primary:** OpenAI via `api-keys.zsh` keys
- **OpenRouter Client:** Available but not used in main flow (see `src/llm/openrouter_client.py`)
- **Removed:** Kilocode (had 405 errors, all references removed)

**To use OpenRouter in Kallisto:**
The infrastructure exists but isn't wired up. OpenRouter client is tested and working for standalone use.

### Frontend Architecture

Located in `/home/nobby/guardrV6-clean/website/`:
- Next.js 15.4.6 with React 19
- Tailwind CSS for styling
- Demo form on landing page: name (required) + location (optional)
- API calls via `NEXT_PUBLIC_API_URL` (defaults to localhost:5000)

**Important:** The "about" page with placeholder "Daniel Obregón" content was removed. Don't recreate it.

## Key Files

### Entry Points
- `guardr_api.py` - Flask API server (main backend)
- `src/modules/person_lookup.py` - Person investigation
- `src/modules/username_search.py` - Username investigation across platforms
- `guardr_agent.py` - PERA cycle agent (experimental, not used in production)

### Configuration
- `api-keys.zsh` - **CURRENT** API keys (in Kallisto-OSINTer repo)
- `~/.apikeys.zsh` - **OLD** keys, don't use these
- `src/config.py` - System configuration and LLM settings
- `.env.local` - Frontend environment (in website/)

### Critical Tools
- `src/tools/search.py` - Serper API integration (7 result limit)
- `src/tools/read_link.py` - Web scraping via ScrapingBee
- `src/tools/llm_map_reduce.py` - Content summarization

## Important Constraints

### Performance Tuning
- **Search Results:** Limited to 7 (in `src/tools/search.py`)
- **Investigation Rounds:** 1 round only (in `src/agents/knowledge_agent.py`)
- **Timeout:** Each OSINT call takes 30-60 seconds minimum

### API Key Management
- **ALWAYS** source `api-keys.zsh` (in repo), NOT `~/.apikeys.zsh`
- Required keys: OPEN_ROUTER_API_KEY, OPENAI_API_KEY, SERPER_API_KEY, SCRAPINGBEE_API_KEY
- Keys are loaded at runtime, not hardcoded

### LLM Provider Notes
- Kilocode was removed completely (had 405 errors from api.kilocode.ai)
- OpenAI is primary, fallback to Anthropic/Mistral
- Default model: gpt-4o-mini (128K context)
- OpenRouter client exists but isn't integrated into main Kallisto flow

## Deployment

See `DEPLOYMENT_PLAN.md` for full DigitalOcean migration plan.

**Quick Deploy:**
```bash
# On DigitalOcean droplet
./deploy_to_digitalocean.sh
```

**Production Stack:**
- Backend: DigitalOcean droplet ($6/month, 33 months free with student credit)
- Frontend: Vercel (free via GitHub Student Pack)
- Domain: guardr.app
- SSL: Let's Encrypt (automatic)

## Common Issues

### "No module named 'flask'"
You're not in the venv. Run: `source venv/bin/activate`

### "KILOCODE_API_KEY not set" or Kilocode errors
Kilocode was removed. If you see this, there are leftover references. It should use OpenAI instead.

### Tests timing out
Real OSINT calls take 60-120s. Use `test_guardr_quick.py` for fast testing, or increase test timeouts to 90-120s.

### Frontend shows old API responses
The old DigitalOcean server (134.209.162.223:5000) might still be running. Frontend should use `NEXT_PUBLIC_API_URL` env var pointing to localhost:5000 in dev.

## Repository Structure

```
Kallisto-OSINTer/           # Main OSINT engine + Guardr API
├── guardr_api.py           # Flask API wrapper for Guardr
├── guardr_agent.py         # PERA cycle agent (experimental)
├── api-keys.zsh            # Current API keys (use this!)
├── src/
│   ├── agents/             # Multi-agent OSINT system
│   ├── modules/            # High-level interfaces (person_lookup, username_search)
│   ├── tools/              # Low-level tools (search, scraping, LLM)
│   ├── llm/                # LLM client with provider fallback
│   └── config.py           # System configuration
├── test_*.py               # Test suites
└── venv/                   # Python virtual environment (ALWAYS use this)

guardrV6-clean/website/     # Next.js frontend (separate repo)
├── src/app/                # Next.js 15 app router
├── .env.local              # Environment config (NEXT_PUBLIC_API_URL)
└── package.json
```

## Philosophy & Design Principles

**From the user/founder:**
- "You are an adult. You decide." - Empowering, not alarmist messaging
- 2-minute OSINT scan is a FEATURE ("captive audience" for engagement)
- Safety tips: smart_habits, friendly_reminders, did_you_know, you_decide
- No beta users needed for seed funding - just working demo + personal story
- "I'm gay" is a pitch advantage - solo founder with domain expertise
- Mobile-first: "it has to be a mobile app day one"
- $6.99 pricing is intentional (69% LGBTQ+ harassment rate reminder)
