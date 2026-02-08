# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`last30days` is a Claude Code skill (`/last30days`) that researches topics across Reddit, X, and the web from the past 30 days, synthesizes community patterns, and generates actionable prompts or expert answers. The source repo is at https://github.com/mvanhorn/last30days-skill.

## Installation Location

The skill installs to `~/.claude/skills/last30days`. Config lives at `~/.config/last30days/.env` with `OPENAI_API_KEY` and `XAI_API_KEY`. Output writes to `~/.local/share/last30days/out/`.

## Running Tests

```bash
# Run all tests (uses fixture data, no API keys needed)
python -m pytest tests/

# Run a single test file
python -m pytest tests/test_score.py

# Run with mock mode (no live API calls)
python scripts/last30days.py "test topic" --mock
```

## CLI Usage

```bash
python scripts/last30days.py "topic" [options]
```

Key flags: `--mock` (fixture data), `--refresh` (bypass cache), `--emit=compact|json|md|context|path` (output format), `--sources=reddit|x|both|web` (platform filter), `--quick` (fewer sources), `--deep` (comprehensive), `--debug` (verbose logging).

## Architecture

Three-stage pipeline orchestrated by `scripts/last30days.py`:

1. **Research** — Concurrent API queries via `ThreadPoolExecutor` to Reddit (OpenAI Responses API in `openai_reddit.py`) and X (xAI Responses API in `xai_x.py`), plus optional `websearch.py` fallback
2. **Process** — Sequential enrichment (`reddit_enrich.py`), then `normalize.py` → `dates.py` filtering → `score.py` ranking → `dedupe.py`
3. **Render** — `render.py` produces output in the requested format

### Library Modules (`scripts/lib/`)

| Module | Purpose |
|---|---|
| `env.py` | Loads credentials from `~/.config/last30days/.env`, detects available sources |
| `dates.py` | 30-day window computation and confidence scoring |
| `cache.py` | 24-hour TTL file cache keyed by topic + date range |
| `http.py` | stdlib HTTP client with retry logic |
| `models.py` | Auto-selects latest OpenAI/xAI models with 7-day refresh |
| `schema.py` | Type definitions and validation |
| `openai_reddit.py` | Reddit research via OpenAI Responses API |
| `xai_x.py` | X research via xAI Responses API |
| `reddit_enrich.py` | Fetches Reddit thread JSON for engagement metrics |
| `websearch.py` | Web search fallback when no API keys configured |
| `normalize.py` | Standardizes results into common schema |
| `score.py` | Popularity-weighted ranking using engagement metrics |
| `dedupe.py` | Near-duplicate detection across sources |
| `render.py` | Multi-format output (compact, JSON, markdown, context, path) |
| `ui.py` | Progress indicators and visual feedback |

### Research Modes

- **Full**: Reddit + X + WebSearch (both API keys)
- **Partial**: One platform + WebSearch (one API key)
- **Web-Only**: WebSearch only (no API keys — still functional)

### Data Flow

The skill weights Reddit/X sources higher than web results based on engagement metrics. Reddit posts get enriched with thread-level data for better scoring. Individual enrichment failures are non-fatal — the pipeline continues with available data. If initial Reddit queries return minimal results, retry logic activates with broadened queries.

## Fixtures

Test fixtures in `fixtures/` provide sample API responses (`openai_sample.json`, `xai_sample.json`, `reddit_thread_sample.json`, `models_openai_sample.json`, `models_xai_sample.json`) used by `--mock` mode and the test suite.

## SKILL.md Conventions

When modifying the skill behavior, update `SKILL.md` — it defines the interaction protocol Claude follows when the `/last30days` command is invoked. Key rules: ground synthesis in actual research (not pre-existing knowledge), match prompt format to what research recommends, extract specific names for recommendations, do not display source lists.
