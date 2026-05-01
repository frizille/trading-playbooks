# Playbook: Income Instrument Assessment

**Trigger:** `income assessment [TICKER]`
**Output file:** `/outputs/[TICKER]-income-[YYYY-MM-DD].md`

**Use this playbook for:** Preferred stocks, REITs, BDCs, covered call ETFs, bonds/notes, structured products, and any security where yield is the primary investment thesis rather than capital appreciation.

---

## Pre-Flight
1. Check `/watchlist.md` — do I already hold this or a related instrument (e.g., the common stock of the same issuer)?
2. Identify the instrument type:
   - [ ] Preferred Stock (fixed rate)
   - [ ] Preferred Stock (variable/floating rate)
   - [ ] REIT
   - [ ] BDC (Business Development Company)
   - [ ] Covered Call ETF
   - [ ] Corporate Bond / Note
   - [ ] Structured Product (novel/hybrid)
3. Web search: `[TICKER] current yield dividend` — record current yield and price vs par/NAV.

---

## Step 1: Instrument Snapshot

- **Issuer:** Who is paying the yield? Describe the parent company in 2–3 sentences.
- **Instrument type:** From the checklist above — be specific.
- **Par / stated value:** What is the face value (typically $25 or $100)?
- **Current price vs par:** Trading at premium, discount, or par? Calculate the % difference.
- **Yield on cost vs yield on par:** If trading above/below par, calculate both.
- **Maturity / call date:** Is there a redemption date? Can the issuer call it early?
- **Payment frequency:** Monthly / Quarterly / Semi-annual?
- **Seniority:** Where does this instrument sit in the capital stack? (Senior secured → senior unsecured → subordinated → preferred → common equity)

---

## Step 2: Yield Analysis

This is the core of an income instrument assessment.

### Current Yield
- Stated annual dividend or coupon: $
- Current yield (annual payment ÷ current price): %
- If variable rate: what is the rate-setting mechanism? (SOFR-linked, board-discretion, formula-based)
- Tax treatment:
  - [ ] Qualified dividends (15–20% rate for most investors)
  - [ ] Ordinary income (taxed at marginal rate)
  - [ ] Return of Capital / ROC (tax-deferred, reduces cost basis)
  - [ ] Tax-exempt (municipal bonds)
- **Tax-equivalent yield** (adjust for treatment): %

### Yield History
- Has the rate changed over time? Direction of trend (rising / flat / declining)?
- Is there a floor or ceiling on rate adjustments?
- How many consecutive periods has the dividend been paid without interruption?

### Yield vs Alternatives
Compare the current yield against:
| Benchmark | Current Yield |
|-----------|--------------|
| 3-month T-bill | |
| 2-year Treasury | |
| 10-year Treasury | |
| Investment-grade corporate bond (avg) | |
| High-yield / junk bond (avg) | |
| S&P 500 dividend yield | |

Is the spread over Treasuries appropriate for the risk level? (See Step 4.)

---

## Step 3: Issuer Financial Health

The yield is only as good as the issuer's ability to keep paying it. Assess:

- **Revenue and cash flow:** Can the issuer cover the dividend/coupon from operations, or is it dependent on asset sales, new issuances, or price appreciation of underlying assets?
- **Debt load:** Total debt vs assets. What is the debt-to-equity or debt-to-NAV ratio?
- **Dividend coverage ratio:** (Net income or distributable cash flow) ÷ total preferred dividends. A ratio above 1.5x is comfortable; below 1.0x is a red flag.
- **Cash reserves:** How many months/years of distributions can the issuer cover from cash on hand if revenue stops?
- **Credit rating:** S&P / Moody's rating on the issuer or the specific instrument, if available. If unrated, assign an implied rating based on financial health (Investment Grade / High Yield / Distressed).
- **Collateral:** Is the yield backed by specific assets (real estate, Bitcoin, loans, etc.)? How liquid and stable are those assets?

---

## Step 4: Risk Assessment

### Price Stability Risk
- How far has this instrument traded from par over its history?
- What would cause it to break significantly below par?
- Is price stability structurally engineered (e.g., variable rate mechanism) or just a market expectation?

### Dividend Suspension Risk
- Under what conditions can the issuer legally suspend or reduce the dividend?
- Is it cumulative (missed dividends must be paid later) or non-cumulative (missed dividends are gone)?
- What is the trigger scenario for suspension?

### Call / Redemption Risk
- Can the issuer call the instrument at par? If so, when?
- If currently trading above par, a call would result in a loss — flag this.
- If interest rates fall, is early call likely?

### Underlying Asset Risk (for asset-backed instruments)
- What is the collateral, and what happens to the yield if that collateral declines in value?
- Is there a specific price level of the underlying asset at which the instrument becomes impaired?
- Assign a stress scenario: "If [underlying asset] falls X%, what happens to this instrument?"

### Capital Stack Risk
- List all instruments senior to this one and their total outstanding amount.
- In a distress scenario, how much would need to be paid out before this instrument sees any recovery?

### Liquidity Risk
- Average daily trading volume
- Bid-ask spread (wide spreads signal illiquidity)
- Can I exit a reasonably sized position without moving the market?

---

## Step 5: Portfolio Fit

- **Income role:** Does this replace or supplement existing income sources in my portfolio? (Covered call premiums, other dividends, etc.)
- **Correlation to existing holdings:** Does this add new risk or stack on top of risks I already carry? (e.g., adding a Bitcoin-collateralized preferred when I already hold BTC-adjacent equities)
- **Account fit:**
  - **Taxable account:** Best for ROC-treatment instruments (tax-deferred income) or qualified dividend payers
  - **IRA / Roth IRA:** Best for ordinary income instruments (shields from marginal rate tax); ROC treatment wasted here
  - **HSA:** Reserve for highest-conviction growth or clean income plays
- **Position sizing:** For income instruments, size by desired monthly/annual income contribution, not just % of portfolio. Example: $10,000 at 11.5% = $1,150/year or ~$96/month.
- **Concentration check:** Does adding this increase exposure to a theme or issuer I'm already concentrated in?

---

## Step 6: Scenario Analysis

Run three scenarios focused on income sustainability:

### Base Case (most likely)
- Yield continues at or near current rate
- Price stays near par
- Outcome: Annual income = $[X] on a $[Y] position

### Stress Case (adverse but not catastrophic)
- Yield is cut to [X]% (specify the floor or plausible reduction)
- Price drops to $[Y] (specify a realistic downside — use historical low or asset-coverage break-even)
- Loss of principal vs income received: at what point does capital loss exceed cumulative income?
- Break-even holding period: how long must I hold to recover a [Z]% price decline via income?

### Tail Risk Case (low probability, high impact)
- Dividend suspended entirely
- Price falls to [X] (distressed level, below par by 20%+)
- What is the total loss scenario?
- Is there any recovery mechanism (cumulative structure, asset sale, etc.)?

---

## Step 7: Verdict

**Income Quality Rating:** High / Medium / Low / Speculative
*(High = investment grade equivalent, stable cash flow coverage, low call risk. Speculative = junk-equivalent risk, asset-price-dependent, or novel/untested structure.)*

**Recommended Action:**
- [ ] Initiate income position
- [ ] Monitor — revisit at [trigger condition]
- [ ] Avoid — risk/reward unfavorable for income goal
- [ ] Substitute — better income alternative exists (specify)

**If initiating:**
- Position size: $ (targeting $[X]/month in income)
- Account: (and rationale — especially tax treatment)
- Entry: At market / Limit at $[X] / Scale in over [timeframe]
- Exit triggers: (e.g., yield drops below X%, price breaks below $Y, issuer credit event)

**Compared to existing income sources:**
- My covered call campaigns currently generate approximately $[X]/month
- This instrument would add $[Y]/month on a $[Z] position
- Is the additional income worth the incremental risk? Yes / No / Marginal

**One-line verdict:**

---

## Output
Write full assessment to `/outputs/[TICKER]-income-[YYYY-MM-DD].md`.
In chat, summarize with: instrument type, current yield, income quality rating, recommended action, and ideal account if initiating.
