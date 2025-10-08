# AI Instructions for GitKraken - Kallisto-OSINTer Backend

## Project Context
Kallisto-OSINTer - Multi-agent OSINT framework powering Guardr dating safety platform.

## Commit Message Guidelines

### Format
```
<type>: <subject>

<body (optional)>
```

### Types
- `feat:` New feature (e.g., "feat: add age filter to person_lookup")
- `fix:` Bug fix (e.g., "fix: handle celebrity name collisions in search")
- `perf:` Performance (e.g., "perf: reduce search results to 7")
- `refactor:` Code restructuring (e.g., "refactor: extract LLM fallback logic")
- `test:` Test additions (e.g., "test: add quick PERA cycle test")
- `docs:` Documentation (e.g., "docs: update API endpoint descriptions")
- `chore:` Maintenance (e.g., "chore: remove Kilocode references")

### Subject Rules
- Use imperative mood: "add" not "added"
- No period at end
- Capitalize first letter
- Max 50 characters
- Be specific about which module changed

### Examples
```
feat: add location disambiguation to person_lookup

Passes location parameter to search queries to help filter
common names. Reduces false positives like "Master Caleb Stewart"
appearing for all "Caleb Stewart" searches.

---

perf: optimize OSINT investigation to 1 round

Reduced from 2 rounds to 1 for faster response times.
Average investigation now completes in 60-90s instead of 120s.
Search results also limited to 7 (down from 10).

---

fix: handle LLM provider fallback correctly

OpenAI now primary, Anthropic/Mistral as fallbacks.
Removed Kilocode (had 405 errors from api.kilocode.ai).
```

## Code Review Focus Areas

1. **Environment & API Keys**
   - ALWAYS use `source api-keys.zsh` (not `~/.apikeys.zsh`)
   - Check `venv/bin/activate` is called first
   - Never commit API keys

2. **LLM Integration**
   - Use `LLMClient.from_config()` for provider fallback
   - Never hardcode model names
   - Check rate limiting (2.0s default)
   - Provider order: OpenAI → Anthropic → Mistral

3. **OSINT Performance**
   - Search results: 7 max (not 10)
   - Investigation rounds: 1 (not 2)
   - Location parameter for disambiguation
   - Timeout expectations: 60-120s

4. **Agent Architecture**
   - KnowledgeAgent orchestrates
   - WebAgent performs searches (7 results)
   - DeepDiveAgent for focused investigation
   - LLM map-reduce for summarization

5. **API Response Structure**
   ```python
   {
     "risk_level": "HIGH|MEDIUM|LOW",
     "risk_score": 0-100,
     "person_verification": {...},
     "safety_tips": [...]  # 4 rotating categories
   }
   ```

## Code Explanation Context

When explaining code:
- Mention multi-agent architecture
- Note LLM provider fallback chain
- Highlight performance optimizations (7 results, 1 round)
- Reference Serper API (search) and ScrapingBee (scraping)
- Call out common pitfalls (celebrity names, API keys)

## Branch Naming
- `feat/description` - New features
- `fix/description` - Bug fixes
- `perf/description` - Performance improvements
- `refactor/description` - Code restructuring
- `test/description` - Test additions

Examples:
- `feat/add-age-filter`
- `fix/celebrity-name-collision`
- `perf/reduce-investigation-rounds`

## Don't Reference
- Kilocode (removed - had 405 errors)
- 2 investigation rounds (now 1)
- 10 search results (now 7)
- Old API key location (~/.apikeys.zsh)

## Key Architecture Concepts

**Multi-Agent Flow:**
```
person_lookup(name, question, config, location?)
  └─> KnowledgeAgent (1 round)
       └─> WebAgent.search() via Serper (7 results)
            └─> Parallel fetch & LLM summarization
                 └─> map_reduce aggregation
```

**LLM Provider Fallback:**
1. OpenAI (gpt-4o-mini) - Primary
2. Anthropic (claude-3-sonnet) - Fallback
3. Mistral (mistral-large-latest) - Last resort

**Configuration Priority:**
- Environment variables override config
- `LLM_PROVIDER_ORDER` sets fallback chain
- `LLM_MODEL_OVERRIDES` sets models per provider

## Testing Commands
```bash
# Quick test (no real OSINT)
python test_guardr_quick.py

# Real API tests (60-120s each)
python test_backend_basic.py
python test_integration.py
python test_security.py

# Full suite
./run_all_tests.sh
```

## Common Issues to Watch For

1. **"No providers configured"** - API keys not loaded
2. **Celebrity name collisions** - Need better disambiguation
3. **Timeout errors** - OSINT calls take 60-120s
4. **Rate limiting** - 2.0s between LLM calls
5. **Module imports** - Always relative to `src/`
