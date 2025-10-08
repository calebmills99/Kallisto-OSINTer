# Copilot Instructions for Guardr/Kallisto-OSINTer

## Project Context
**Guardr** - AI-powered dating safety for LGBTQ+ community, built on Kallisto-OSINTer OSINT framework.

### Tech Stack
- **Backend:** Flask API (Python 3.10+) with multi-agent OSINT system
- **Frontend:** Next.js 15 + React 19 + Tailwind (separate repo: `guardrV6`)
- **AI:** OpenAI (primary), Anthropic, Mistral (fallback chain)
- **APIs:** Serper (search), ScrapingBee (scraping)

## Critical Rules

### Environment & Setup
1. **ALWAYS** activate venv: `source venv/bin/activate`
2. **ALWAYS** load keys: `source api-keys.zsh` (NOT `~/.apikeys.zsh`)
3. **DO NOT** commit API keys or `.env` files
4. Backend runs on port 5000, frontend on 3001/3002

### Code Patterns

**LLM Calls:**
- Use `LLMClient.from_config()` - handles provider fallback
- Never hardcode model names - use `config["LLM_MODEL_OVERRIDES"]`
- Rate limit: 2.0 seconds between calls (configurable)

**OSINT Searches:**
- Limit: 7 results max (performance tuning)
- Investigation rounds: 1 (not 2)
- Always include location for person disambiguation
- Use `person_lookup()` for people, `username_search()` for social media

**API Responses:**
```python
# Guardr API always returns this structure:
{
  "risk_level": "HIGH|MEDIUM|LOW",
  "risk_score": 0-100,
  "person_verification": {...},
  "safety_tips": [...]  # Rotates 4 categories
}
```

### Frontend Conventions
- Dark theme with neon accents (nightlife palette)
- Mobile-first design
- Form: name (required) + location (optional)
- API calls timeout at 120s (OSINT is slow)
- Use Tailwind utility classes, NOT inline styles

### Testing
- Quick test: `python test_guardr_quick.py` (no real OSINT)
- Real OSINT takes 60-120s per request
- Test timeout: 90-120s minimum

### Common Pitfalls
1. **Kilocode removed** - don't reference it (had 405 errors)
2. **OpenRouter exists** but not used in main flow (infrastructure only)
3. **Location matters** - common names need geographic context
4. Celebrity name collisions in search results (Master Caleb Stewart problem)
5. Frontend `.env.local` uses `NEXT_PUBLIC_API_URL=http://localhost:5000`

## File Structure
```
Kallisto-OSINTer/
├── guardr_api.py           # Main API entry point
├── src/
│   ├── agents/             # KnowledgeAgent, WebAgent, DeepDiveAgent
│   ├── modules/            # person_lookup, username_search
│   ├── tools/              # search, read_link, llm_map_reduce
│   ├── llm/llm_client.py   # Multi-provider LLM with fallback
│   └── config.py           # System configuration
└── api-keys.zsh            # API keys (gitignored)
```

## Philosophy
- **"You are an adult. You decide."** - Empowering, not alarmist
- 2-minute scan is a FEATURE (captive audience)
- Mobile-first: "it has to be a mobile app day one"
- LGBTQ+ focused but universal safety
- $6.99 pricing = 69% LGBTQ+ harassment rate reminder

## Deployment
- **Frontend:** DigitalOcean App Platform (was Vercel, caused pain)
- **Backend:** DigitalOcean droplet (Ubuntu, gunicorn + nginx)
- **Domain:** guardr.app
- Student credits: $200 DO credit (60 days)

## When Making Changes
1. Check `CLAUDE.md` for detailed context
2. Test with `test_guardr_quick.py` first
3. Real API tests take 2+ minutes
4. Don't optimize OSINT speed without asking (already tuned)
5. Safety tips rotate - don't remove categories
