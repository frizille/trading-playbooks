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
watchlist.md                     ← Current positions & cost basis (always loaded)
.claude/skills/
  screen-tickers/SKILL.md        ← Funnel: ranked shortlist from a universe
  assess-company/SKILL.md        ← Full equity research template
  analyze-options/SKILL.md       ← Covered call & options strategy
  review-position/SKILL.md       ← Existing position check-in
  preview-earnings/SKILL.md      ← Pre-earnings research brief
  assess-income-instrument/SKILL.md  ← Yield-instrument assessment
outputs/                         ← Research reports saved here
```

## Updating Your Watchlist

Keep `watchlist.md` current — Claude reads it at the start of every session to understand your positions before making recommendations.

## Adding a Skill

To add a new research type, create `.claude/skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) followed by the step-by-step process. Then add a one-line entry to the Research Skills list in `CLAUDE.md`.
