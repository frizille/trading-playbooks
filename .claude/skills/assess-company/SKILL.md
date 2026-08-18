---
name: assess-company
description: Use when the user asks to assess, research, deep-dive, or evaluate a stock or company by ticker. Triggers on phrases like "assess [TICKER]", "research [TICKER]", "deep dive on [TICKER]", or "what do you think about [TICKER]". Produces a structured equity research report.
---

# Company Assessment

**Output file:** `/outputs/[TICKER]/[TICKER]-assessment-[YYYY-MM-DD].md` (create the ticker folder if it doesn't exist)

Follow these steps **exactly** — do not skip or reorder.

---

## Pre-Flight
1. Check `/watchlist.md` — do I already hold this? If so, note current position, cost basis, and account type before continuing.
2. Web search: `[TICKER] stock price today` — record current price and 52-week range.

---

## Step 1: Business Snapshot
- What does the company do? One clear paragraph, no jargon.
- Revenue model (SaaS, usage-based, hardware, transactional, etc.)
- Key customers or end markets
- Where does it sit in the competitive landscape? Name 2–3 direct competitors.
- Total addressable market (TAM) — use a cited source if possible.

## Step 2: Financial Health
Search for most recent earnings and trailing twelve months (TTM) data:
- Revenue: current quarter, YoY growth rate, QoQ trend
- Gross margin: current and directional trend
- Operating income / EBITDA: profitable or burning?
- Free cash flow (FCF): positive or negative? Trajectory?
- Cash on hand and debt load
- If pre-profit: cash runway at current burn rate

## Step 3: Valuation
- P/S ratio (TTM and forward)
- P/E ratio (if profitable) — TTM and forward
- EV/EBITDA vs sector peers
- Consensus analyst price targets: low / median / high
- Current price vs 200-day moving average (above or below, % distance)
- Current price vs 52-week range (where in the range?)

## Step 4: Catalyst Map
**Upcoming catalysts (bullish):**
- Next earnings date
- Known product launches, contract announcements, or expansions
- Macro tailwinds relevant to this name

**Key risks (bearish):**
- Competitive threats
- Execution risk (management, product, scaling)
- Macro headwinds (rates, tariffs, regulation)
- Balance sheet risk if applicable

## Step 5: Options Landscape
Only complete this step if the company has liquid options.
- Current IV rank or IV percentile (if available)
- Implied move for next earnings
- Covered call reference point (informational, not a recommendation): nearest monthly expiry, 20–30 delta strike, premium yield. If any options figure is cited, also state the VRP in percentage points ("IV X% / RV Y% / VRP ±Zpp / IV rank N%") — see analyze-options Step 3 — include only as market color; per the Aug 2026 doctrine, do not convert this into a trade suggestion unless it passes the `analyze-options` doctrine gate
- Any notable unusual options activity in past 30 days

## Step 6: Verdict

**Conviction:** Low / Medium / High

**Recommended Action:**
- [ ] Initiate position
- [ ] Add to existing position
- [ ] Hold — no action
- [ ] Trim
- [ ] Avoid

**If initiating or adding:**
- Suggested position size ($ amount and % of portfolio)
- Suggested account (taxable, IRA, HSA) and rationale
- Entry strategy (buy outright, scale in, use options)

**If optioning:**
- Specific trade: strike, expiry, quantity
- Max loss / max gain scenario
- Which doctrine qualification it meets (entry-anyway / dated-event hedge / cheap-IV long) — if none, no options trade; and for any exit range, show limit orders (default) beside the optional CC

**Summary (3 bullets max):**
- 
- 
- 

---

## Visualization

Include a peer-comparison chart in the report if at least 2 peers from Step 1 have comparable P/E or P/S data. Use the Charts plugin block:

````
```chart
type: bar
labels: [TICKER, PEER1, PEER2, PEER3]
series:
  - title: Forward P/E
    data: [, , , ]
  - title: Forward P/S
    data: [, , , ]
```
````

Skip the chart if peer data is unavailable rather than fabricate values.

---

## Output

Write the full report to `/outputs/[TICKER]/[TICKER]-assessment-[YYYY-MM-DD].md` (create the ticker folder if it doesn't exist).

**Frontmatter** (in addition to the shared fields in CLAUDE.md):
```yaml
skill: assess-company
verdict: BUY            # BUY / ADD / HOLD / TRIM / AVOID
conviction: High        # Low / Medium / High
action: Initiate        # Initiate / Add / Hold / Trim / Avoid
position_pct: 5         # suggested position size as % of portfolio (omit if Hold/Avoid)
tags: [research, assessment]
```

In chat, summarize with: current price, verdict, and one-line rationale.
