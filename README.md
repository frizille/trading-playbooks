# trading-playbooks

Structured research workflows for [Claude Code](https://claude.ai/code), packaged as on-demand skills. Each skill defines a repeatable, step-by-step process for a specific type of stock research or portfolio analysis.

## How to Use

1. Open this repo in Claude Code
2. Claude reads `CLAUDE.md` automatically on session start
3. Ask for the kind of research you want — the matching skill activates on intent. Examples:

| Ask something like... | Skill that runs |
|----------------------|-----------------|
| "screen the S&P 500 for stocks under $20" / "shortlist 10 REITs over 7% yield" | `screen-tickers` |
| "assess NVDA" / "deep dive on NVDA" | `assess-company` |
| "options on NVDA" / "covered call ideas for NVDA" | `analyze-options` |
| "review my NVDA position" | `review-position` |
| "earnings preview for NVDA" | `preview-earnings` |
| "income assessment on PFFA" / "is PFFA a good yield play" | `assess-income-instrument` |

For broad questions, `screen-tickers` produces a shortlist; then run a deep-dive skill on the names you want to investigate further.

Results are saved to `/outputs/` as markdown files.

## Files

```
CLAUDE.md                        ← Claude's master instructions (always loaded)
watchlist.example.md             ← Template (tracked); copy to `watchlist.md`
watchlist.md                     ← Current positions & cost basis (always loaded; gitignored)
.claude/skills/
  screen-tickers/SKILL.md        ← Funnel: ranked shortlist from a universe
  assess-company/SKILL.md        ← Full equity research template
  analyze-options/SKILL.md       ← Covered call & options strategy
  review-position/SKILL.md       ← Existing position check-in
  preview-earnings/SKILL.md      ← Pre-earnings research brief
  assess-income-instrument/SKILL.md  ← Yield-instrument assessment
scripts/
  option_chain.py                ← yfinance-based option chain helper
  finnhub_news.py                ← Finnhub-based structured news feed (optional)
  requirements.txt               ← Python deps for scripts/
.env.example                     ← Template for optional API keys (copy to .env)
outputs/                         ← Research reports saved here (gitignored)
```

## Live Options Data (one-time setup)

The `analyze-options` skill calls `scripts/option_chain.py`, which uses [`yfinance`](https://github.com/ranaroussi/yfinance) to pull live(-ish, ~15 min delayed) option chains, IV, and Greeks.

On Homebrew Python you'll hit PEP 668 ("externally-managed-environment") if you `pip install` directly. Use a venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
```

Quick test (venv must be active, or call `.venv/bin/python` directly):

```bash
python3 scripts/option_chain.py SPY --expiries 1 --targets 0.25,0.50
```

The `analyze-options` skill auto-detects `.venv/` and uses it; falls back to system `python3` if absent. If neither has the deps, the skill will fall back to web search — quality of the strike/IV/delta numbers will be much lower.

## Optional: Finnhub News API

The `review-position` and `preview-earnings` skills can pull a structured, dated headline feed via [Finnhub](https://finnhub.io). The free tier (60 requests/min) is plenty for personal research. Setup:

1. Create a free account at https://finnhub.io and copy your API key.
2. Copy the env template and fill in the key:

   ```bash
   cp .env.example .env
   # then edit .env and paste your key after FINNHUB_API_KEY=
   ```

3. The helper auto-reads `.env` from the repo root — no `source` needed. Verify:

   ```bash
   python3 scripts/finnhub_news.py NVDA --days 7
   ```

`finnhub_news.py` uses only the Python standard library (no extra `pip install` required). If `FINNHUB_API_KEY` is unset, the affected skills fall back to web search and say so explicitly.

## Updating Your Watchlist

First-time setup: `cp watchlist.example.md watchlist.md`. The real `watchlist.md` is gitignored so cost basis and share counts stay local.

Keep `watchlist.md` current — Claude reads it at the start of every session to understand your positions before making recommendations.

## Adding a Skill

To add a new research type, create `.claude/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) followed by the step-by-step process. Then add a one-line entry to the Research Skills list in `CLAUDE.md`.
