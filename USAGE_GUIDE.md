# Last 30 Days Skills - Complete Usage Guide

## What Are These Skills?

You now have **three powerful research tools** that search social media and web sources for recent discussions (last 30 days) on any topic:

1. **`last30days`** - Full-featured: searches Reddit + X + Web
2. **`search-reddit`** - Standalone: Reddit-only research
3. **`search-x`** - Standalone: X (Twitter)-only research

### What Makes Them Powerful?

Unlike a simple Google search, these skills:
- ✅ **Filter by recency** - Only content from the last 30 days
- ✅ **Rank by engagement** - Surface popular discussions (upvotes, likes, comments)
- ✅ **Extract insights** - Pull top comments and key takeaways
- ✅ **Score & deduplicate** - Rank results and remove duplicates
- ✅ **Structured output** - JSON, Markdown, or compact formats

---

## What Can You Accomplish?

### 1. **Technology Research**
Find what developers are actually saying about:
- Programming languages, frameworks, libraries
- Tools, platforms, services
- Best practices, patterns, anti-patterns

**Example:**
```bash
python ~/.claude/skills/search-reddit/scripts/search_reddit.py "FastAPI vs Flask 2024"
```

### 2. **Product Research**
Discover real user opinions on:
- SaaS products, apps, services
- Hardware, gadgets, tools
- Alternatives and comparisons

**Example:**
```bash
python ~/.claude/skills/search-x/scripts/search_x.py "Claude vs ChatGPT"
```

### 3. **Trend Discovery**
Track emerging topics:
- New AI models, features, releases
- Industry news and announcements
- Community reactions to events

**Example:**
```bash
python ~/.claude/skills/last30days/scripts/last30days.py "GPT-5 news" --deep
```

### 4. **Learning & Best Practices**
Find tutorials, tips, and lessons learned:
- "How to" questions
- Common pitfalls
- Real-world experiences

**Example:**
```bash
python ~/.claude/skills/search-reddit/scripts/search_reddit.py "Python async best practices"
```

### 5. **Competitive Intelligence**
Monitor what people say about:
- Your product vs competitors
- Industry shifts and sentiment
- Feature requests and pain points

**Example:**
```bash
python ~/.claude/skills/search-x/scripts/search_x.py "vercel deployment issues" --quick
```

---

## Command Options

### Basic Syntax
```bash
python [skill_path] "your search topic" [options]
```

### Available Options

| Option | Values | Description | Use When |
|--------|--------|-------------|----------|
| `--quick` | flag | Faster with fewer results<br>Reddit: 15-25 threads<br>X: 8-12 posts | You need fast insights |
| `--deep` | flag | Comprehensive research<br>Reddit: 70-100 threads<br>X: 40-60 posts | You want thorough coverage |
| `--emit` | `compact`, `json`, `md` | Output format (default: compact) | You need specific format |
| `--mock` | flag | Use test data (no API calls) | Testing without using credits |
| `--debug` | flag | Verbose logging | Troubleshooting API issues |

**Note:** Default mode (no --quick or --deep) gives balanced results: 30-50 Reddit, 20-30 X

### Output Formats (`--emit`)

#### 1. **compact** (default) - For Claude to synthesize
```markdown
## Reddit Search Results: Python async

**R1** (score:85) r/Python (2026-02-01) [542pts, 87cmt]
  Best async patterns in Python 3.12
  https://reddit.com/r/Python/...
  *Discussion of modern async best practices*
  Insights:
    - Use asyncio.TaskGroup for structured concurrency
    - Avoid mixing sync and async code
```

#### 2. **json** - For programmatic processing
```json
{
  "topic": "Python async",
  "range": {"from": "2026-01-09", "to": "2026-02-08"},
  "reddit": [
    {
      "id": "R1",
      "title": "Best async patterns...",
      "score": 85,
      "engagement": {"score": 542, "num_comments": 87}
    }
  ]
}
```

#### 3. **md** - For documentation/reports
```markdown
# Python async - Reddit Research Report

## Reddit Threads

### R1: Best async patterns in Python 3.12
- **Subreddit:** r/Python
- **Score:** 85/100
- **Engagement:** 542 points, 87 comments
```

---

## Real-World Examples

### Example 1: Compare Two Technologies
```bash
# Find recent Reddit discussions comparing React vs Vue
python ~/.claude/skills/search-reddit/scripts/search_reddit.py "React vs Vue 2024" --quick

# Get structured JSON output
python ~/.claude/skills/search-reddit/scripts/search_reddit.py "React vs Vue 2024" --emit=json > react-vue.json
```

**What you get:**
- Top 15-25 Reddit threads
- Real developer opinions
- Engagement metrics (upvotes/comments)
- Key insights from comments
- Ranked by relevance + popularity

---

### Example 2: Track Product Sentiment on X
```bash
# See what people are saying about a product on X
python ~/.claude/skills/search-x/scripts/search_x.py "Cursor IDE" --deep

# Quick pulse check
python ~/.claude/skills/search-x/scripts/search_x.py "Cursor IDE" --quick
```

**What you get:**
- 8-12 recent X posts (quick) or 40-60 (deep)
- Author handles and engagement (likes, reposts)
- Post text and URLs
- Scored and ranked by relevance + engagement

---

### Example 3: Comprehensive Multi-Platform Research
```bash
# Full research across Reddit + X + Web
python ~/.claude/skills/last30days/scripts/last30days.py "AI code generation tools" --deep --emit=md > research.md
```

**What you get:**
- Reddit threads with upvotes/comments
- X posts with likes/reposts
- Web pages from blogs/docs/news
- All ranked and deduplicated
- Full markdown report

---

### Example 4: Quick Daily Monitoring
```bash
# Quick daily check on a topic
python ~/.claude/skills/search-x/scripts/search_x.py "Claude Code" --quick --emit=compact
```

**What you get:**
- Fast results (8-12 posts)
- Recent 30 days only
- Top discussions surfaced
- Ready to read in seconds

---

## Understanding the Output

### Score Breakdown (0-100)

Each result gets a **composite score** based on three factors:

```
Score = (45% Relevance) + (25% Recency) + (30% Engagement)
```

- **Relevance (0-100):** How well it matches your topic (AI-determined)
- **Recency (0-100):** How recent (today=100, 30 days ago=0)
- **Engagement (0-100):** Normalized across all results
  - Reddit: upvotes + comments + ratio
  - X: likes + reposts + replies

**High score = Relevant + Recent + Popular**

### Date Confidence

Results show date confidence:
- **high** - Verified from metadata (most reliable)
- **med** - Extracted from content
- **low** - Unknown or uncertain

Items with `low` confidence get score penalty but aren't excluded.

---

## Output Files

Results are automatically saved to:

**search-reddit:**
- `~/.local/share/search-reddit/out/report.json`
- `~/.local/share/search-reddit/out/report.md`
- `~/.local/share/search-reddit/out/raw_openai.json` (API response)

**search-x:**
- `~/.local/share/search-x/out/report.json`
- `~/.local/share/search-x/out/report.md`
- `~/.local/share/search-x/out/raw_xai.json` (API response)

**last30days:**
- `~/.local/share/last30days/out/report.json`
- `~/.local/share/last30days/out/report.md`
- `~/.local/share/last30days/out/last30days.context.md` (reusable snippet)
- Raw API responses for debugging

---

## Integration with Claude

These skills are designed to be **embedded in Claude Code workflows**:

### In a SKILL.md file:
```bash
# Research phase
python3 ~/.claude/skills/search-reddit/scripts/search_reddit.py "$TOPIC" --emit=compact

# Claude reads the output and synthesizes insights
# Claude can then write prompts, create summaries, etc.
```

### As part of automation:
```python
import subprocess
import json

# Run search
result = subprocess.run([
    "python", "~/.claude/skills/search-x/scripts/search_x.py",
    "Python asyncio", "--emit=json"
], capture_output=True, text=True)

# Parse results
data = json.loads(result.stdout)
print(f"Found {len(data['x'])} posts")
```

---

## Cost & Performance

### API Usage
- **Reddit (OpenAI):** Uses web_search tool (~$0.01-0.05 per query)
- **X (xAI):** Uses x_search tool (~$0.01-0.03 per query)

### Speed
- **--quick:** 10-20 seconds per skill
- **Default:** 30-60 seconds per skill
- **--deep:** 1-3 minutes per skill

### Caching
Results are cached for 24 hours:
- Subsequent queries with same topic = instant (free)
- Use `--refresh` flag to bypass cache

---

## Troubleshooting

### "API error: HTTP 401: Unauthorized"
**Solution:** Check your API keys in the `.env` files:
```bash
# For search-reddit
cat ~/.config/search-reddit/.env

# For search-x
cat ~/.config/search-x/.env
```

### "No results found"
**Possible causes:**
- Topic too specific or niche
- No activity in last 30 days
- Try broader search terms
- Try `--deep` for more comprehensive search

### Getting "0 threads" or "0 posts"
**This can happen when:**
- Results are older than 30 days (hard filtered out)
- Date parsing failed (items get filtered)
- Use `--debug` to see what's being filtered

---

## Advanced Use Cases

### 1. Competitive Monitoring Dashboard
```bash
#!/bin/bash
# daily_monitor.sh

python ~/.claude/skills/search-x/scripts/search_x.py "your-product" --quick > daily_x.txt
python ~/.claude/skills/search-reddit/scripts/search_reddit.py "your-product" --quick > daily_reddit.txt

# Email or analyze results
```

### 2. Research Report Generator
```bash
# Generate comprehensive report
python ~/.claude/skills/last30days/scripts/last30days.py "AI coding assistants" --deep --emit=md > report.md

# Convert to PDF or share
```

### 3. Trend Tracker
```bash
# Track multiple topics
for topic in "AI" "blockchain" "quantum computing"; do
  python ~/.claude/skills/search-x/scripts/search_x.py "$topic" --quick --emit=json > "${topic}.json"
done

# Analyze trends programmatically
```

---

## Configuration Reference

### Environment Variables

**`~/.config/search-reddit/.env`**
```bash
OPENAI_API_KEY=sk-proj-...           # Required
OPENAI_MODEL_POLICY=auto             # auto|pinned (optional)
OPENAI_MODEL_PIN=gpt-4o              # Specific model (optional)
```

**`~/.config/search-x/.env`**
```bash
XAI_API_KEY=xai-...                  # Required
XAI_MODEL_POLICY=latest              # latest|stable|pinned (optional)
XAI_MODEL_PIN=grok-4-1-fast          # Specific model (optional)
```

**`~/.config/last30days/.env`**
```bash
OPENAI_API_KEY=sk-proj-...           # Required for Reddit
XAI_API_KEY=xai-...                  # Required for X
# Model policies (optional)
OPENAI_MODEL_POLICY=auto
XAI_MODEL_POLICY=latest
```

---

## Best Practices

### ✅ DO
- Use `--quick` for fast iterations
- Use `--deep` when you need comprehensive data
- Check cached results first (24hr TTL)
- Use specific, focused topics
- Combine multiple searches for different angles

### ❌ DON'T
- Use vague topics like "technology" (too broad)
- Run `--deep` unnecessarily (costs more)
- Ignore date confidence warnings
- Expect results older than 30 days

---

## Summary

You now have **three powerful research tools** that can:

1. **Surface real discussions** from Reddit and X in the last 30 days
2. **Rank by engagement** to find popular, valuable content
3. **Extract insights** from comments and replies
4. **Structure output** for analysis or Claude synthesis
5. **Cache results** to save time and money

**When to use each:**
- **`search-reddit`** → Deep technical discussions, how-tos, long-form
- **`search-x`** → Quick takes, news, trends, announcements
- **`last30days`** → Comprehensive multi-platform research

**Quick reference:**
```bash
# Fast Reddit research
python ~/.claude/skills/search-reddit/scripts/search_reddit.py "your topic" --quick

# Fast X research
python ~/.claude/skills/search-x/scripts/search_x.py "your topic" --quick

# Deep multi-platform
python ~/.claude/skills/last30days/scripts/last30days.py "your topic" --deep
```

---

## Next Steps

1. **Test with your own topics** - Try searching for something you're interested in
2. **Experiment with options** - Compare --quick vs --deep vs default
3. **Try different formats** - Use --emit=json for programmatic access
4. **Build workflows** - Integrate into your own automation or Claude skills
5. **Monitor trends** - Set up daily/weekly searches for topics you care about

The skills are standalone, reusable, and designed to be embedded in larger workflows. Happy researching! 🚀
