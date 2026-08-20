# Query plan template for direct last30days CLI runs

Use `query-plan-template.json` whenever you call `scripts/last30days.py` **directly from a
shell or a script**. The `/last30days` skill generates its own plan (LAW 7) and does not
need this; a bare CLI invocation does.

## Why this exists

Measured on 2026-08-19, same topic, same 30-day window, same machine:

| Invocation | Sources dispatched | Items |
|---|---|---|
| bare, no `--plan` | 2 (Hacker News, Reddit) | 12 |
| with a full `--plan` | 8 (+ X, YouTube, TikTok, Instagram, Pinterest, GitHub) | 135 |

Without `--plan` the engine falls back to its deterministic planner, which picked only
`[hackernews, reddit, grounding]`. Every other source was configured and available and
simply was never requested. The gap is the plan, not the API keys.

## Usage

```bash
cp query-plan-template.json /tmp/plan.json
# edit search_query / ranking_query / intent
python ~/.claude/skills/last30days/scripts/last30days.py "Your Topic" \
  --plan /tmp/plan.json --emit=compact
```

## Rules that matter

- **The primary subquery must list every source you want hit.** Sources absent from the
  plan are never queried, no matter how healthy `doctor` says they are.
- **1 to 4 subqueries.** Primary weight `1.0`, secondary `0.6`-`0.8`, peripheral `0.3`-`0.5`.
- **Anchor collision-prone names in EVERY subquery**, not just the primary, and mirror the
  anchor in `ranking_query`. `"kevin rose digg founder"`, not `"kevin rose"`.
- **Never put temporal words in `search_query`** - no "recent", "latest", "last 30 days",
  month names, year numbers. Use `--days N` for the window instead.
- **Never put meta-research words in `search_query`** - no "news", "updates", "analysis".
- `search_query` is keyword-heavy and matches how content is *titled*.
  `ranking_query` is a natural-language question.

## Field mappings

| intent | freshness_mode | cluster_mode |
|---|---|---|
| breaking_news | strict_recent | story |
| prediction | strict_recent | market |
| comparison | balanced_recent | debate |
| opinion | balanced_recent | debate |
| how_to | evergreen_ok | workflow |
| concept | evergreen_ok | none |
| product, factual | balanced_recent | none |

## Source names

Always available to name: `reddit`, `x`, `youtube`, `tiktok`, `instagram`, `hackernews`,
`polymarket`, `github`, `grounding`, `pinterest`.

Configured but opt-in on this machine (add to `INCLUDE_SOURCES` or pass `--search NAME`):
`linkedin`, `threads`.

Not installed here (need the Go toolchain): `arxiv`, `techmeme`, `digg`, `trustpilot`.

## Known behavior

- Reddit returns **HTTP 429** partway through wide multi-subquery runs. It is a throttle,
  not a failure; the ScrapeCreators backfill only rescues Reddit when the free path returns
  *nothing*, not when it returns partial results.
- `os.environ` **overrides** `~/.config/last30days/.env` (`lib/env.py:573`, and the
  `get_config` docstring at `env.py:398` says so). A stale shell or Windows env var will
  silently shadow a corrected key in `.env`.
