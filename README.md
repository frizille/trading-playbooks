# trading-playbooks

Structured research playbooks for Claude Code. Each playbook defines a repeatable, step-by-step process for a specific type of stock research or portfolio analysis.

## How to Use

1. Open this repo in [Claude Code](https://claude.ai/code)
2. Claude reads `CLAUDE.md` automatically on session start
3. Use a trigger phrase to run a playbook:

| Say this... | Claude runs... |
|-------------|---------------|
| `assess NBIS` | Full company deep-dive |
| `options on IREN` | Covered call / options analysis |
| `review my position CRWV` | Position health check |
| `earnings preview RDDT` | Pre-earnings research brief |

Results are saved to `/outputs/` as markdown files.

## Files

```
CLAUDE.md                        ← Claude's master instructions
watchlist.md                     ← Current positions & cost basis
playbooks/
  company-assessment.md          ← Full equity research template
  options-analysis.md            ← Covered call & options strategy
  position-review.md             ← Existing position check-in
  earnings-preview.md            ← Pre-earnings research brief
outputs/                         ← Research reports saved here
```

## Updating Your Watchlist

Keep `watchlist.md` current — Claude reads it at the start of every session to understand your positions before making recommendations.

## Adding Playbooks

To add a new research type, create a new `.md` file in `/playbooks/` and add its trigger phrase to the table in `CLAUDE.md`.
