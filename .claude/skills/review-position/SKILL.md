---
name: review-position
description: Use when the user asks to review, check on, revisit, or reassess an existing held position. Triggers on phrases like "review my position [TICKER]", "how is my [TICKER] doing", "check on [TICKER]", or "should I still be holding [TICKER]".
---

# Position Review

**Output file:** `/outputs/[TICKER]/[TICKER]-review-[YYYY-MM-DD].md` (create the ticker folder if it doesn't exist)

Follow these steps **exactly** — do not skip or reorder.

---

## Pre-Flight
Load full position detail from `/watchlist.md` for this ticker across all accounts.

---

## Step 1: Position Summary
Build a complete snapshot:
- Total shares held (all accounts combined)
- Weighted average cost basis
- Total cost basis (dollars invested)
- Current market value at today's price
- Unrealized P&L ($) and (%)
- Account breakdown (IRA vs taxable vs HSA)
- Active options: list all open calls/puts on this name

## Step 2: Effective Cost Basis
Calculate the real cost basis after options income:
- Total premium collected on this position to date (from watchlist if tracked)
- Effective cost basis = original cost basis minus premium per share
- Break-even price at effective cost basis

## Step 3: Thesis Check
Web search for recent news, earnings, and analyst updates:
- Is the original investment thesis still intact? State the thesis in one sentence, then evaluate.
- What has changed since the position was opened (positively or negatively)?
- Any new risks that weren't present at entry?
- Management changes, product pivots, competitive shifts?

## Step 4: Technical Snapshot
- Current price vs 200-day MA (above/below, %)
- Current price vs 52-week high and low
- Recent trend: is it above or below my cost basis? By how much?
- Volume trend: any unusual activity recently?

## Step 5: Options Assessment
Review all active options on this name:
- Are any covered calls at risk of being in-the-money (ITM) near expiry?
- Should any positions be rolled, closed early, or left to expire?
- Is there an opportunity to sell additional calls given current IV?

For each active option:
| Position | Status | Action |
|----------|--------|--------|
|          |        |        |

## Step 6: Portfolio Fit
- Current position as % of total portfolio
- Is this above or below target allocation?
- Does concentration need to be addressed?
- Account type fit: is this in the right account for tax efficiency?

## Step 7: Decision

**Overall thesis:** Intact / Weakened / Broken

**Recommended action:**
- [ ] Hold — no changes
- [ ] Add — rationale and suggested size
- [ ] Trim — how much and why
- [ ] Manage options — specific action
- [ ] Exit — full or partial, and which account first

**Time horizon check:** Am I still comfortable with the original time horizon for this position?

**Next review trigger:** Set a condition that would prompt another review (e.g., price drops below $X, earnings in 30 days, options expiring).

---

## Visualization

Include a Charts plugin block showing cost basis vs effective cost basis vs current price (from Steps 1–2):

````
```chart
type: bar
labels: [Cost basis, Effective cost basis, Current price]
series:
  - title: $ per share
    data: [, , ]
```
````

Skip if no premium has been collected (effective cost basis = cost basis makes the chart redundant).

---

## Output

Write full review to `/outputs/[TICKER]/[TICKER]-review-[YYYY-MM-DD].md` (create the ticker folder if it doesn't exist).

**Frontmatter** (in addition to the shared fields in CLAUDE.md):
```yaml
skill: review-position
verdict: HOLD             # HOLD / ADD / TRIM / EXIT / MANAGE_OPTIONS
thesis: Intact            # Intact / Weakened / Broken
pnl_pct: 12.4             # unrealized P&L % at current price
position_pct: 7.2         # current % of total portfolio
tags: [research, review]
```

In chat, summarize with: current P&L, thesis status, and recommended action.
