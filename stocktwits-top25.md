# StockTwits Top 25 — Pre-List Analysis

**Trigger:** `top25` or `top25 [N weeks]` (default: 5 weeks)

---

## Context

The StockTwits Top 25 newsletter tracks the 25 best-performing stocks YTD across the S&P 500, NASDAQ 100, and Russell 2000. It is a **lagging** momentum list — it reports what already happened. The purpose of this playbook is to identify what will appear on the list **before** it does, using a 4-rule predictive framework derived from pattern analysis across Weeks 13–17 (April–May 2026).

The newsletter's S&P 500 and NASDAQ 100 ranked tables are **image-only**. All YTD rankings must be reconstructed via web search — you cannot read them from the email text.

---

## Step 1 — Fetch newsletters from Gmail

Use the Gmail MCP tool to search for the most recent N StockTwits Top 25 newsletters.

```
from:newsletter@thedailyrip.stocktwits.com subject:"Stocktwits Top 25"
```

Fetch the full body of each message. Sort ascending by date (oldest first).

If Gmail is unavailable, ask the user to paste the newsletter text directly.

---

## Step 2 — Parse each newsletter

From each newsletter's plain text body, extract:

- **Subject and date**
- **Week number** (from subject line, e.g. "Week 17")
- **Top Dawg section** — the featured mover write-up(s), including: ticker, % move, company description, earnings data if mentioned, risk flags called out by the newsletter
- **Any tickers mentioned** in body text (ignore image captions, sponsor sections, and Terms & Conditions)

Note: the S&P 500, NASDAQ 100, and Russell 2000 ranked tables are images. Do not attempt to extract rankings from the email — you will hallucinate. Proceed to Step 3 for rankings.

---

## Step 3 — Reconstruct YTD rankings via web search

For each index, search for current top performers. Run these searches:

1. `S&P 500 top YTD performers 2026 ranking`
2. `NASDAQ 100 top performers year to date 2026`
3. `best performing S&P 500 stocks 2026`

Cross-reference at least two sources. Build a table of the approximate top 10 for each index with:
- Ticker
- Company name
- Approximate YTD %
- Primary theme (e.g. "AI storage", "optical networking", "power/cooling")
- Source and approximate date of data

Label all reconstructed rankings with: *"Reconstructed from [source] — not extracted from newsletter image."*

---

## Step 4 — Update the supply chain layer map

Using the rankings from Step 3 and Top Dawg data from Step 2, update the status of each layer:

| Layer | Category | Key Tickers | Status |
|-------|----------|-------------|--------|
| 1 | GPU / AI chip design | NVDA, AMD | |
| 2 | Memory & storage | SNDK, WDC, STX, MU | |
| 3 | Optical networking | LITE, CIEN, COHR, MXL | |
| 4 | Fab equipment | LRCX, AMAT, KLAC, TER | |
| 5 | Power & cooling | VRT, BE, ETN, NVTS | |
| 6 | Physical build / grid | FIX, PWR, MTZ, GEV | |
| 7 | Platform chips (non-GPU) | QCOM, ON, TXN | |
| 8 | AI applications / software | PLTR, CRWD, NOW | |

Status options: `✅ Ran` · `🟡 Entering` · `⬜ Not yet repriced`

Ask: *"What is currently preventing hyperscalers from deploying more CapEx faster?"* That answer identifies which layer reprices next.

---

## Step 5 — Apply the 4-rule framework to identify pre-list candidates

### Rule 1: Find the valuation gap

Screen for S&P 500 or NASDAQ 100 stocks that:
- Are clearly positioned in the AI infrastructure supply chain
- Are priced at their old-business-model multiple, NOT an AI infrastructure multiple
- Have forward P/E more than 25% below the NASDAQ composite average
- Have AI/data center revenue growing >50% YoY but still <15% of total revenue
- Have management explicitly naming AI data center as a strategic priority in recent calls

Prototype: **INTC** spent the first 15 weeks of 2026 near #10 on the S&P 500 list. It was priced as a legacy CPU company. After Q1 confirmed Data Center & AI segment +22% YoY and named it host CPU for NVIDIA's DGX Rubin NVL8, it more than doubled in April and jumped to #2.

### Rule 2: The earnings validation event

The newsletter reacts to **reported** revenue, not guidance or potential. Every name that entered the Top 25 in 2026 did so within 1–2 weeks of a specific earnings print. You must own the position **before** the print, not after.

### Rule 3: Watch for the leading indicator (T-30 to T-42)

Supply chain signals precede the earnings validation by 4–6 weeks. For each candidate, search for:
- New hyperscaler customer announcement (NVDA, AMZN, MSFT, GOOG, META)
- AI segment guidance raise during the quarter
- Design win or supply agreement explicitly naming AI data centers
- Backlog update with technology/data center >30% of mix and growing
- Insider buying 2–4 weeks before earnings
- Stocktwits sentiment score crossing 75+

**Red flags that invalidate a setup:**
- Insider selling 2–4 weeks pre-earnings
- Revenue miss or guidance cut in most recent quarter
- Competitor announcing the same AI customer win in the same supply chain slot
- Stock already >80% YTD (late entry, risk/reward deteriorating)

### Rule 4: The scarcity layer is always next

Companies that solve the current binding constraint on hyperscaler CapEx deployment reprice the fastest. VRT solved cooling (+100% YTD). BE solved baseload power (+234% YTD). Identify what the current constraint is and find the S&P 500 / NASDAQ 100 names positioned to solve it.

---

## Step 6 — Research and score candidates

For each candidate identified in Step 5, run a targeted web search:

```
[TICKER] 2026 YTD return AI data center revenue
[TICKER] earnings 2026 data center segment results
[TICKER] AI inference data center customer announcement 2026
```

Score each candidate on these five dimensions (1 = weak, 5 = strong):

| Dimension | What to assess |
|-----------|----------------|
| **Thesis** | Is the AI supply chain position specific and defensible? |
| **Catalyst** | How close is the next earnings validation event? |
| **Valuation gap** | How far below peer multiples is this stock priced? |
| **Index** | S&P 500 or NASDAQ 100 preferred; Russell 2000 = secondary |
| **Signals** | Any leading indicators (Rule 3) already firing? |

Star rating:
- ★★★★★ = Imminent, all signals firing, high conviction
- ★★★★ = Strong, 1–2 signals present, catalyst within 60 days
- ★★★ = Building, thesis clear but catalyst distant
- ★★ = Watch only, early stage
- ★ = Speculative, thesis unproven

---

## Step 7 — Build the catalyst calendar

For each candidate and any upcoming earnings prints on the current Top 25 lists, build a calendar entry:

Search for: `[TICKER] earnings date 2026` and `[TICKER] next catalyst 2026`

Include:
- Date (or "~Month" if approximate)
- Ticker
- Event type (earnings / contract announcement / guidance update / macro event)
- What to watch for specifically
- Why it matters for list entry

---

## Step 8 — Identify risk flags

Search for anything that could invalidate the current setups:

- Any AI capex slowdown signals from hyperscalers
- Fed rate signals that could compress growth multiples
- China export restrictions affecting semiconductor equipment names
- OpenAI / hyperscaler revenue miss reports that pressure the AI narrative
- Insider selling at any top candidate
- Guidance cuts in recent quarters for any candidate

---

## Step 9 — Write and save the report

Save to `/outputs/top25-analysis-[YYYY-MM-DD].md` using this template:

---

```markdown
# StockTwits Top 25 — Pre-List Analysis
**Date:** [today]
**Newsletters analyzed:** Weeks [N]–[N] ([date range])

---

## Summary
[3–4 sentence executive summary: dominant themes, most important pre-list candidates, single most time-sensitive action item]

---

## Newsletter recap — Top Dawg movers

| Week | Ticker | Move | Theme | Risk flag noted |
|------|--------|------|-------|-----------------|
| [week] | [ticker] | [%] | [theme] | [risk] |

---

## Reconstructed Top 5 — S&P 500
*[Source note]*

| Rank | Ticker | ~YTD | Theme |
|------|--------|------|-------|

---

## Reconstructed Top 5 — NASDAQ 100
*[Source note]*

| Rank | Ticker | ~YTD | Theme |
|------|--------|------|-------|

---

## Supply chain layer status

| Layer | Category | Tickers | Status |
|-------|----------|---------|--------|

**Current binding constraint:** [What is blocking faster hyperscaler CapEx deployment?]
**Next layer to watch:** [Layer N — reasoning]

---

## Trend analysis
[2–3 paragraphs on dominant themes, sector rotation sequence, and what's driving list changes week over week]

---

## Pre-list candidates

| Ticker | Index | ~YTD | Thesis | Next catalyst | ★ |
|--------|-------|------|--------|---------------|---|

### Top pick: [TICKER]
[2–3 paragraph deep-dive on the highest-conviction candidate: why the valuation gap exists, what the leading indicators are, what the validation event looks like, what the risk is]

---

## Catalyst calendar

| Date | Ticker | Event | What to watch | Why it matters |
|------|--------|-------|---------------|----------------|

---

## Risk flags
[Bullet list of anything that could invalidate current setups, with source and date]

---

## Framework notes
[Anything new from this week's analysis that updates or extends the base framework — new supply chain dynamics, new leading indicator patterns, macro shifts]

---
*Data note: S&P 500 and NASDAQ 100 YTD rankings are reconstructed from web search — newsletter ranked tables are image-only and cannot be read directly. All reconstructed figures are approximate.*
```

---

## Output summary to chat

After saving the file, post 3–5 bullets to chat:

- Top pre-list candidate and why (one sentence each)
- Most time-sensitive catalyst (date + ticker + event)
- Any red flags that invalidate a current setup
- Supply chain layer status update (which layer is entering next)
- File saved location
