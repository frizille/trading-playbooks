---
name: analyze-options
description: Use when the user asks about options strategy on a specific ticker — covered calls, cash-secured puts, LEAPS, or long calls. Triggers on phrases like "options on [TICKER]", "covered call on [TICKER]", "what should I sell against [TICKER]", or any options-strategy question for a held or considered name.
---

# Options Analysis

**Output file:** `/outputs/[TICKER]-options-[YYYY-MM-DD].md`

Follow these steps **exactly** — do not skip or reorder.

---

## Pre-Flight
1. Check `/watchlist.md` — what's the current position? Shares held, account type, current cost basis, and any existing options on this name.
2. **Pull live chain data:** run `python3 scripts/option_chain.py [TICKER] --expiries 3` from the repo root. This is the canonical source for spot, IV, strikes, and delta in Steps 3–5. Output covers: spot price, risk-free rate, dividend yield, realized vol (30d / 90d), next earnings date, and tables of calls/puts at 15Δ / 25Δ / 35Δ / 50Δ for each of the next 3 expiries.
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

If OI < 100 or volume = 0 for the targeted strike, flag it as illiquid and prefer the next nearest strike with reasonable depth.

## Step 5: LEAPS / Long Call Analysis
Only if I don't own shares and am considering a leveraged long position.

For LEAPS, re-run the script with `--expiries 8 --targets 0.70,0.80` to surface deep-ITM strikes on the longest-dated expiries available, e.g.:

```
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

**Recommended trade:**
- Type: Covered Call / Cash-Secured Put / LEAPS / Spread
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

## Output
Write full analysis to `/outputs/[TICKER]-options-[YYYY-MM-DD].md`.
In chat, summarize with: recommended trade, premium yield, and key risk to watch.
