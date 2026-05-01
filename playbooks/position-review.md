# Playbook: Position Review

**Trigger:** `review my position [TICKER]`
**Output file:** `/outputs/[TICKER]-review-[YYYY-MM-DD].md`

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

## Output
Write full review to `/outputs/[TICKER]-review-[YYYY-MM-DD].md`.
In chat, summarize with: current P&L, thesis status, and recommended action.
