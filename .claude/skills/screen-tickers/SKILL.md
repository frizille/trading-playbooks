---
name: screen-tickers
description: Use when the user asks to screen, scan, filter, rank, or shortlist multiple tickers from a universe (e.g., S&P 500, Nasdaq 100, a sector, a custom list) by criteria like price, market cap, valuation, or yield. Triggers on phrases like "screen the S&P 500 for...", "find stocks under $X", "which [universe] names look interesting", or "shortlist [N] candidates for...". Produces a ranked shortlist with one-line rationale per name — does NOT run full deep dives.
---

# Screen Tickers

**Output file:** `/outputs/_screens/[descriptor]-[YYYY-MM-DD].md`
*(descriptor = short slug for the screen, e.g., `sp500-under-20`, `reits-yield-over-7`. Screens aren't ticker-specific, so they live in the shared `_screens/` folder rather than a per-ticker one.)*

This skill is a **funnel step**, not a deep analysis. The goal is to surface a ranked shortlist of candidates that warrant a follow-up `assess-company` (or `assess-income-instrument`) run. Do not produce full reports here.

---

## Pre-Flight

1. **Confirm the universe.** If the user said "S&P 500" or "Nasdaq 100" or "REITs" — fine. If ambiguous (e.g., "tech stocks"), ask before proceeding.
2. **Confirm the criteria.** Distinguish:
   - **Hard filters** (must pass — e.g., "price ≤ $20", "market cap > $1B")
   - **Soft ranking criteria** (used to order survivors — e.g., "best value", "highest momentum", "lowest debt")
   If the user only gave hard filters, ask what to rank survivors by, or default to a sensible mix (valuation + recent price action).
3. **Check `/watchlist.md`** — note which screened names the user already holds, so they can be flagged in the output.

---

## Step 1: Universe & Filters Recap

State plainly, before searching:
- Universe and approximate size (e.g., "S&P 500, ~500 names")
- Hard filters (the cuts that survivors must pass)
- Soft ranking criteria (how survivors will be ordered)
- Any data freshness caveat (intraday vs prior close)

## Step 2: Pull Data

Use web search to retrieve current screener data. Prefer one query that returns the filtered set directly (e.g., `S&P 500 stocks under $20 today`, `REITs with yield over 7% screener`) over fetching individual quotes for hundreds of names.

If the screener doesn't cover all hard filters, do a second pass on survivors.

**Flag any data freshness concern** — if results may be from a prior session, say so.

## Step 3: Apply Hard Filters

List every name that passes. If the count is large (>30), keep going — don't truncate yet.

## Step 4: Rank Survivors

Rank by the soft criteria from Pre-Flight. Show the rank order. If multiple criteria are in play, briefly note how they were weighted.

## Step 5: Shortlist Output

Produce a table — keep rationales to one line each:

| Rank | Ticker | Price | Key metric(s) | One-line rationale | Already held? |
|------|--------|-------|---------------|--------------------|----------------| 
| 1    |        |       |               |                    |                |
| 2    |        |       |               |                    |                |
| ...  |        |       |               |                    |                |

Cap the table at **15 names** unless the user asked for more. Mark held positions in the rightmost column with the account (IRA / Taxable / HSA).

## Step 6: Recommend Deep-Dive Candidates

Pick **3–5 names** from the top of the shortlist that are best worth a full `assess-company` (or `assess-income-instrument` if yield-focused). For each, give a one-sentence reason it stands out from the others on the list.

Format:

> **Top candidates for full assessment:**
> 1. **[TICKER]** — [why this one over the others]
> 2. **[TICKER]** — [why]
> 3. **[TICKER]** — [why]

Suggest the user trigger the deep-dive skill explicitly — do **not** auto-run it.

---

## Output

Write the screen results to `/outputs/_screens/[descriptor]-[YYYY-MM-DD].md`.

**Frontmatter** (in addition to the shared fields in CLAUDE.md — note `ticker` is the descriptor for screens, and `price` is omitted):
```yaml
ticker: sp500-under-20            # screen descriptor, not a real ticker
date: 2026-05-04
skill: screen-tickers
verdict: SHORTLIST                # always SHORTLIST for screens
universe: S&P 500
survivors: 23                     # count after hard filters
top_candidates: [F, RIG, KSS]     # tickers from the "Top candidates for full assessment" list
tags: [research, screen]
```

In chat, summarize with: universe, number of survivors, top 3 names with one-liners, and the recommended next step.

## Boundaries

- Do **not** run `assess-company`, `analyze-options`, or any other deep-dive skill from inside this skill.
- Do **not** produce per-ticker output files — one screen file only.
- Do **not** invent data when the screener doesn't cover a filter — say what's missing instead.
