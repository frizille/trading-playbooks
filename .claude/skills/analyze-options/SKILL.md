---
name: analyze-options
description: Use when the user asks about options strategy on a specific ticker — covered calls, cash-secured puts, LEAPS, or long calls. Triggers on phrases like "options on [TICKER]", "covered call on [TICKER]", "what should I sell against [TICKER]", or any options-strategy question for a held or considered name.
---

# Options Analysis

**Output file:** `/outputs/[TICKER]/[TICKER]-options-[YYYY-MM-DD].md` (create the ticker folder if it doesn't exist)

Follow these steps **exactly** — do not skip or reorder.

---

## Step 0: Doctrine Gate (Aug 2026)

The systematic wheel is retired. Before any analysis, state which qualification the prospective trade meets:
- [ ] **Entry-anyway:** a CSP at a strike the investor would place a limit buy at regardless (model-based level from a current assessment)
- [ ] **Dated-event hedge:** protects against a specific, named event with a date (earnings, AGM vote, regulatory ruling)
- [ ] **Cheap-IV defined-risk long:** LEAPS/long option where IV is objectively cheap vs realized
- [ ] **Named Play:** the trade matches a written play spec in this file (currently: the Friz Special) with every entry condition satisfied — cite the checklist

If none applies, the correct verdict is `NONE` — say so and stop after Step 3. Premium being "attractive" is not a qualification.

**Also mandatory before any recommendation:** state the variance risk premium in
percentage points (see Step 3). For any structure that SELLS premium, a negative
VRP must be called out explicitly as an argument against the trade, regardless of
how the annualized return looks.

---

## Pre-Flight
1. Check `/watchlist.md` — what's the current position? Shares held, account type, current cost basis, and any existing options on this name.
2. **Pull live chain data:** run the option-chain helper from the repo root.
   - If `.venv/` exists: `.venv/bin/python scripts/option_chain.py [TICKER] --expiries 3`
   - Otherwise: `python3 scripts/option_chain.py [TICKER] --expiries 3`

   This is the canonical source for spot, IV, strikes, and delta in Steps 3–5. Output covers: spot price, risk-free rate, dividend yield, realized vol (30d / 90d), next earnings date, and tables of calls/puts at 15Δ / 25Δ / 35Δ / 50Δ for each of the next 3 expiries.
3. **If the script fails** (missing dependency, no network, ticker has no options), say so explicitly, then fall back to web search for spot + IV. Do not silently skip the script.

---

## Step 1: Position Context
- Current shares held and in which account(s)
- Current average cost basis
- Total premium collected to date on this position (if tracked in watchlist)
- Effective cost basis after premium (cost basis minus total premium collected)
- Unrealized P&L at current price

## Step 2: Stock Assessment (Brief)
This is not a full company assessment — just enough to set the options strategy context:
- Current price and recent trend (up/down/sideways over 30 days)
- Next earnings date — **critical**: never sell a covered call that expires through earnings unless intentional
- Any known near-term catalysts that could cause a sharp move

## Step 3: IV Environment

Use the script's output as the primary source.

- **Current ATM IV** — read from the 50Δ row in the nearest expiry.
- **IV percentile/rank** — yfinance does not provide a true IV rank. Approximate by comparing current ATM IV to the script's reported **realized vol 30d** and **realized vol 90d**:
  - ATM IV materially above realized vol → market pricing in elevated forward risk → richer premium
  - ATM IV near or below realized vol → compressed → consider waiting or going further out
- If a screener URL with a true IV rank is easily found via web search, prefer that and note the source.

### Variance Risk Premium — MANDATORY for every options play

Always compute and state the **variance risk premium (VRP)**:

```
VRP = implied volatility − realized volatility     (in PERCENTAGE POINTS, "pp")
```

Report it in this exact format, every time, in chat and in any artifact:

> **IV 65% / RV 96% / VRP −31.4pp / IV rank 43.5%**

Percentage points, not percent: 65% minus 96% is −31.4**pp**, not −31.4%. The
distinction matters because the latter reads as a ratio and understates the gap.

**How to read it — this is the single most important number for any premium sale:**

| VRP | Meaning | Implication |
|---|---|---|
| **Positive** | Options priced above the movement that actually occurs | Genuine edge for the SELLER — the structural case for short premium |
| **Near zero** | Fairly priced | Expected value ≈ 0 by construction, before costs |
| **Negative** | Realized vol running hotter than implied | Selling UNDERPRICED volatility; EV is negative before costs; elevated assignment risk |

Never treat IV rank alone as sufficient. IV rank says where implied vol sits in
its own history; VRP says whether implied vol is high enough *relative to what
the underlying is actually doing*. A mid-range IV rank with deeply negative VRP —
MU on 17 Aug 2026 read IV rank 43.5% with VRP −31.4pp — is a sell-premium trap:
the annualized ROC headline looks rich while the expected value is negative.

**Also state, for any short-premium structure:** a high win rate is not an edge.
A fairly priced 0.30-delta put wins roughly 67% of the time and still has zero
expected value, because the average shortfall given assignment runs about 3× the
premium collected. Edge comes only from (1) positive VRP, or (2) genuinely
wanting the shares at the strike. Say which one applies, or say neither does.

- State the conclusion: elevated / fair / compressed, with the numbers that justify it.

## Step 4: Covered Call Analysis

Read the call rows from the script output for the next 3 expiries. For each expiry, pull the 15Δ, 25Δ, and 35Δ rows (the script picks the closest available strike to each target).

Use the **mid** price as the premium estimate (script computes mid = (bid+ask)/2 when both are available, falling back to last).

| Expiry | DTE | Strike | Δ | Premium (mid) | Yield (annualized) | Upside cap vs cost basis |
|--------|-----|--------|---|---------------|-------------------|--------------------------|
| Near   |     |        |   |               |                   |                          |
| Mid    |     |        |   |               |                   |                          |
| Far    |     |        |   |               |                   |                          |

**Yield** = (premium / current stock price) × (365 / DTE).
**Upside cap** = strike vs my cost basis — flag if strike is below breakeven.

**Mechanism comparison (required):** alongside the CC table, show the plain alternative — a resting limit sell order at the same strike price. State what the CC adds (the premium) and what it costs (exit capped at strike; no execution guarantee by any deadline; upside above strike forfeited if assigned). The covered call is one mechanism, never the default. On high-momentum holdings, note explicitly that the forfeited upside has historically exceeded the premium collected.

If OI < 100 or volume = 0 for the targeted strike, flag it as illiquid and prefer the next nearest strike with reasonable depth.

## Step 5: LEAPS / Long Call Analysis
Only if I don't own shares and am considering a leveraged long position.

For LEAPS, re-run the script with `--expiries 8 --targets 0.70,0.80` to surface deep-ITM strikes on the longest-dated expiries available, e.g.:

```bash
# with venv:
.venv/bin/python scripts/option_chain.py [TICKER] --expiries 8 --targets 0.70,0.80
# without venv:
python3 scripts/option_chain.py [TICKER] --expiries 8 --targets 0.70,0.80
```

Then evaluate the longest-dated expiry shown (typically the next January LEAPS):
- Compare premium cost to owning 100 shares outright
- Breakeven at expiry = strike + premium paid
- Max loss scenario = premium paid (option goes to 0)

## Step 6: Risk Scenarios
For the recommended covered call trade:
- **If stock stays flat:** outcome
- **If stock rises through strike:** shares called away — do I want that? Tax implications?
- **If stock drops 20%:** premium cushion vs loss on shares
- **Buyback trigger:** at what premium decay level (e.g., 50% profit) should I consider closing early?

## Step 7: Recommendation

**Recommended trade** (`NONE` is a valid and common outcome under the doctrine gate):
- Doctrine qualification met: entry-anyway / dated-event hedge / cheap-IV long
- Type: Covered Call / Cash-Secured Put / LEAPS / Spread / None — if a CC, restate the limit-order alternative and why the CC is preferred *for this trade*
- Strike: $
- Expiry:
- Quantity:
- Account:
- Target entry premium: $
- Buyback at: $ (50% profit target or specify)

**Rationale (2–3 sentences):**

**What to watch:**
- Close early if: 
- Roll if:
- Do nothing if:

---

## Visualization

Include two Charts plugin blocks in the report:

**1. IV vs realized vol** (from Step 3 data):

````
```chart
type: bar
labels: [ATM IV, Realized 30d, Realized 90d]
series:
  - title: Annualized vol (%)
    data: [, , ]
```
````

State the VRP (ATM IV − Realized 30d, in pp) directly beneath this chart.

````
```chart
```
````

**2. Annualized premium yield by expiry** (from the Step 4 covered call table — use the recommended Δ row at each expiry):

````
```chart
type: bar
labels: [Near, Mid, Far]
series:
  - title: Annualized yield (%)
    data: [, , ]
```
````

---

## Output

Write full analysis to `/outputs/[TICKER]/[TICKER]-options-[YYYY-MM-DD].md` (create the ticker folder if it doesn't exist).

**Frontmatter** (in addition to the shared fields in CLAUDE.md):
```yaml
skill: analyze-options
verdict: SELL_CC          # SELL_CC / SELL_CSP / BUY_LEAPS / NONE
trade_type: CC            # CC / CSP / LEAPS / Spread / None
strike: 12                # numeric strike of the recommended trade (omit if NONE)
expiry: 2026-06-20        # YYYY-MM-DD (omit if NONE)
premium: 0.42             # mid premium per share at recommendation time
annualized_yield: 18.3    # % annualized — from Step 4
tags: [research, options]
```

In chat, summarize with: recommended trade, premium yield, and key risk to watch.

## Named Plays

### The Friz Special (opportunistic short-vol premium harvest)

**Classification:** doctrine category (d). A mean-reversion premium harvest, not an exit
mechanism and not intended to reach expiry or assignment.

**Thesis:** after an extended multi-day run, both price and implied volatility are
elevated. Selling far-OTM, long-dated calls (vega-heavy) harvests the reversion of
both. The vega does more work than the delta — the underlying merely going sideways
while IV normalizes deflates the calls materially; a pullback accelerates it.

**Entry conditions (all required):**
- Underlying up roughly 25%+ within the last 3–5 sessions (extended run, not a single gap)
- IV elevated versus recent realized vol (check via option_chain.py Step 3 method)
- Strike at least ~50% OTM at entry, or the highest strike the chain lists if that is
  nearer (chain availability often binds — see flags)
- Expiry 6+ months out (maximizes vega; keeps gamma low)
- Fully covered: contracts × 100 ≤ shares held in the same account. Never naked.
- Premium meaningful — as a reference, the inaugural trade collected ~17% of covered
  position value in one shot

**Flags to surface at entry (NOT limits — report them, then let the trader decide):**
These are diagnostics, not gates. None of them blocks a trade. Compute and state each
one plainly at entry so the decision is made with the number in view.
- **Delta at entry.** Percentage OTM is vol-blind and can badly understate risk on
  high-IV names. Worked example: NBIS Mar-27 $440C at 58% OTM carried ~0.44 delta at
  ~104% IV — close to a coin flip on assignment, not the remote tail "58% OTM"
  suggests. A hypothetical IREN Jun-27 $70C at 59% OTM priced ~0.48 delta. Same
  distance, very different risk from the same rule. State the delta; do not cap it.
- **Strike availability.** Sometimes the desired distance simply is not listed — the
  NBIS $440 was the highest strike in the March 2027 chain, so 58% OTM was the
  ceiling the chain allowed, not a preference. When the chain is the binding
  constraint, record that; it explains a higher delta that no strike selection could
  have avoided, and it is a reason to consider a further expiry where more strikes
  may exist.
- **Size as % of covered position.** State contracts as a share of the underlying
  holding and the credit as a percentage of position value (NBIS: 15/15 lots, credit
  ~16.7% of position). Full coverage of a lot is allowed; just say so out loud.
- **IV context — state the VRP in pp.** Report as "IV X% / RV Y% / VRP ±Zpp / IV
  rank N%". The play is short vega, so this is the variable doing most of the work.
  A negative VRP does not block a Friz Special (nothing does), but it must be
  surfaced: it means the vol being sold is cheap relative to actual movement, and
  the mean-reversion thesis is carrying the trade without help from pricing.
- **Assignment price sanity.** Strike + premium against the current model ladder
  (base / prob-weighted / bull). If the effective sale price sits below the base case,
  flag it prominently.

**Horizon:** 3–4 months typical. This is a position trade, not a scalp — the pullback
and IV normalization play out over months, and the long-dated expiry gives it room.

**Profit target:** buy back when the calls have lost ~30% of entry value (close at
~70% of the credit received). Do not hold for the remaining decay — the last 70% is
slow theta against open-ended event risk.

**Abandon rules (DEFAULTS — confirm or adjust per trade; deviating requires a written
reason at entry, not in the moment):**
- **Hard stop:** close if the call mark reaches 1.5× the entry credit
- **Strike proximity:** mandatory close-or-decide if the underlying reaches 85% of the
  strike — beyond that, gamma and assignment mechanics take over the trade
- **90-day re-underwrite:** if neither target nor stop has hit by day 90, re-run the
  entry checklist; close unless the conditions would justify entering fresh today
- **Never roll to defend.** Rolling a losing short-premium campaign is how the IRE
  loss compounded. One trade, one decision at target or stop.

**Binary events:** if the window contains earnings, shareholder votes, or other dated
binaries, decide IN WRITING at entry whether the play holds through each event or
exits before it. An event-driven selloff is often the pullback the play is waiting
for — but short vega marks against the position as IV bids into the event. Either
choice is valid; drifting into the event undecided is not.

**Failure fallback:** if held to assignment (a failed Friz Special), the effective
exit is strike + premium. This must be a price the holder can live with selling at —
which is why the strike-distance and covered-only conditions exist.

**Logging:** log entry date, run size that triggered entry, strike distance, IV
context, credit, target, stops, event decisions — and at close, which rule fired.
The play is only as repeatable as its log.

