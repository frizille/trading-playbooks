---
name: preview-earnings
description: Use when the user asks for an earnings preview, pre-earnings analysis, or what to watch for in an upcoming quarterly report. Triggers on phrases like "earnings preview [TICKER]", "what to watch for [TICKER] earnings", or "[TICKER] reports next week".
---

# Earnings Preview

**Output file:** `/outputs/[TICKER]-earnings-[YYYY-MM-DD].md`

Follow these steps **exactly** — do not skip or reorder.

---

## Pre-Flight
1. Check `/watchlist.md` for current position and any active options near the earnings date.
2. Web search: `[TICKER] earnings date Q[X] [YEAR]` — confirm exact date and whether it's before or after market.

---

## Step 1: Earnings Fast Facts
- Confirmed earnings date and time (BMO / AMC)
- Analyst consensus EPS estimate
- Analyst consensus revenue estimate
- Company guidance (if previously issued)
- Last quarter's results vs estimates (beat/miss/in-line on EPS and revenue)

## Step 2: Last Quarter Recap
- What did management say on the last call? Key themes and forward guidance.
- What drove the stock reaction post-last earnings? (% move, direction)
- What did analysts revise after last quarter?

## Step 3: What the Market Is Expecting
- Options-implied move for earnings (ATM straddle / strangle price as % of stock price)
- Historical average earnings move over last 4–8 quarters
- Is the implied move larger or smaller than historical average?
- Analyst sentiment: ratio of Buy / Hold / Sell ratings, and any recent revisions

## Step 4: Key Things to Watch
List the 3–5 metrics or themes that will most likely drive the reaction. These are the things to listen for on the call:

1. **[Metric]:** Consensus expects X. Beat threshold is Y. Why it matters: 
2. **[Metric]:** 
3. **[Metric]:** 
4. **[Theme]:** (e.g., guidance commentary, margin expansion, end-market demand signals)
5. **[Theme]:**

## Step 5: Bull vs Bear Scenarios

**Bull case (stock up 10%+):**
- What would need to happen (EPS beat + raised guidance + strong commentary)
- Upside price target in this scenario

**Base case (stock flat ±5%):**
- In-line results, guidance maintained
- Expected price range

**Bear case (stock down 10%+):**
- Miss on revenue, guidance cut, or negative macro commentary
- Downside price level and whether it approaches my cost basis

## Step 6: Options & Position Management
Check all active options expiring within 2 weeks of earnings:

**Active options risk:**
| Position | Expiry | Strike | Risk if stock moves up | Risk if stock moves down |
|----------|--------|--------|------------------------|--------------------------|
|          |        |        |                        |                          |

**Pre-earnings action needed?**
- Should any covered calls be closed or rolled before earnings?
- Is there an opportunity to play the implied move (straddle, etc.)?
- If holding no position: is there a post-earnings entry opportunity in any scenario?

## Step 7: Game Plan

**Before earnings:**
- [ ] Action on existing options (specify)
- [ ] No changes needed

**Reaction playbook:**
- If stock beats and gaps up: 
- If stock is in-line: 
- If stock misses and drops: 

**Watch for on the call:**
- Demand commentary in core end markets
- Any changes to capex plans
- Commentary on competitive environment

---

## Output
Write full preview to `/outputs/[TICKER]-earnings-[YYYY-MM-DD].md`.
In chat, summarize with: earnings date, implied move, the one most important metric to watch, and pre-earnings action needed.
