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
2. Web search: `[TICKER] stock price options chain` — get current price and confirm options liquidity.

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
- Current implied volatility (IV) — absolute number and percentile/rank if available
- Is IV elevated (>50th percentile) or compressed (<25th percentile)?
- Interpretation: elevated IV = better premium, compressed IV = consider waiting or go further out

## Step 4: Covered Call Analysis
Evaluate three scenarios for the nearest 3 monthly expiries:

For each expiry, find strikes at approximately **15 delta**, **25 delta**, and **35 delta**:

| Expiry | Strike | Delta | Premium | Yield (annualized) | Upside cap vs cost basis |
|--------|--------|-------|---------|-------------------|--------------------------|
| Near   |        |       |         |                   |                          |
| Mid    |        |       |         |                   |                          |
| Far    |        |       |         |                   |                          |

**Yield** = premium / current stock price, annualized.
**Upside cap** = strike vs my cost basis — flag if strike is below breakeven.

## Step 5: LEAPS / Long Call Analysis
Only if I don't own shares and am considering a leveraged long position:
- Evaluate Jan 2026 and Jan 2027 calls at 70–80 delta (deep ITM, synthetic stock)
- Compare premium cost to owning 100 shares outright
- Breakeven at expiry
- Max loss scenario

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
