---
name: manage-watchlist
description: Use when the user reports a trade execution, wishlist change, or position update — phrases like "I just opened/closed/rolled X", "X expired worthless", "X got assigned/exercised", "F paid a dividend", "add NVDA to my watchlist", "remove TSLA from watchlist", "bump priority on AMD". Mediates writes to the structured data layer (`data/trades.csv`, `data/wishlist.csv`, `data/accounts.yaml`) with a confirm gate, then re-renders `watchlist.md`. Do NOT use for state queries like "show me my open positions" — those read `watchlist.md` directly.
---

# Manage Watchlist

You are mediating writes to the structured watchlist data layer. Real data is gitignored. The user never hand-edits — you do, through this skill.

## Architecture (mental model)

- **`data/trades.csv`** — append-only event log. Each row is a single share, option, or dividend event. See spec at `docs/superpowers/specs/2026-05-04-watchlist-management-design.md` for full schema (gitignored locally).
- **`data/wishlist.csv`** — small mutable table: `ticker, thesis, priority, date_added`.
- **`data/accounts.yaml`** — per-account metadata.
- **`watchlist.md`** — fully rendered projection. NEVER hand-edit. Always rebuild via `scripts/render_watchlist.py`.

## Trade entry flow (the main loop)

For ANY trade event ("I just bought/sold/opened/closed/rolled X", "X expired", "X got assigned", "F paid a dividend"):

1. **Parse** the user's message into one or more tentative CSV rows. The schema columns are: `date, account, ticker, action, qty, price, fees, strike, expiry, opt_type, strategy_id, notes`.
2. **Resolve ambiguity** with at most one or two targeted follow-up questions:
   - Missing account → "Which account — robinhood or simple_ira?" (read `data/accounts.yaml` for current valid names)
   - Missing strike/expiry on an option event → ask for both
   - Per-contract dollar amount mentioned → confirm whether to interpret as per-share (e.g., "0.35" = $35/contract). The schema stores **per-share**.
   - Date not given → assume today (verify with user when fill date matters)
3. **Show the proposed row(s)** as a literal CSV block, plus the diff to `watchlist.md`. Format:

   ```
   Proposed append to data/trades.csv:
   2026-05-04,robinhood,F,STO,1,0.30,0,13.00,2026-05-15,C,,first weekly

   Effect on watchlist.md:
   - Active Options: +1 row (F CC $13.00 5/15)
   - Premium Banked (F): unchanged until close
   ```

4. **Wait for explicit confirmation.** Words like "yes", "go", "confirm" mean append. If the user pushes back, revise and re-show. Never write without approval.
5. **Append** by calling `log_trade.py` once per row. From repo root:

   ```bash
   .venv/bin/python scripts/log_trade.py \
     --date 2026-05-04 --account robinhood --ticker F --action STO \
     --qty 1 --price 0.30 --strike 13.00 --expiry 2026-05-15 \
     --opt-type C --notes "first weekly"
   ```

   The script auto-renders `watchlist.md` on success.
6. **Report back**: "Logged. F effective basis is now $X.YZ. Active options now: ..."

## Auto-paired events

### Assignment / Exercise

When the user says "F got assigned" / "I exercised my AAPL calls":

- Propose **two rows in one confirm gate**:
  1. The option event (`ASGN` or `EXER`, `price=0`)
  2. The resulting share event:
     - **CC assigned** → `SELL` shares at strike
     - **CSP assigned** → `BUY` shares at strike
     - **Long call exercised** → `BUY` shares at strike
     - **Long put exercised** → `SELL` shares at strike

User approves both at once; you call `log_trade.py` twice in sequence (the second call re-renders).

### Rolls

When the user says "I rolled F 5/1 $13C to 5/8 $13.50C for net $0.10 credit":

- Propose **two rows** (BTC of old + STO of new) on the same date, optionally sharing a `strategy_id` like `f-roll-2026-05-04`. Net credit = (open premium of new) − (close debit of old).
- Show both rows in one confirm gate. Approve both at once.

## Wishlist operations

For "add NVDA to watchlist with thesis: AI infra, priority high":

- Read `data/wishlist.csv`, propose the new row, show diff, on approval rewrite the file (entire file — wishlist is small enough to rewrite in full).
- For removal/update, similarly propose the modified file and confirm.

There is no separate `log_wishlist.py` script in v1; you can edit `data/wishlist.csv` directly with the Edit/Write tool, then run the renderer:

```bash
.venv/bin/python scripts/render_watchlist.py
```

## Account changes

Rare. Adding a new account: edit `data/accounts.yaml` directly with confirmation, then run the renderer.

## State queries

NOT a skill action. If the user asks "show me my open positions" / "what's my premium on F" / "what do I hold in IRA":

1. Read the current `watchlist.md` (it's already rendered and authoritative).
2. Present the relevant section in chat.

If the question can't be answered from `watchlist.md` (e.g., "premium YTD by ticker"), call `scripts/query_trades.py` if it exists, or run an ad-hoc Python query against `data/trades.csv` in a tool call.

## Validation rules (enforced by `log_trade.py`)

The script will reject and exit non-zero on any of:

- Unknown `account` (must match a `name` in `accounts.yaml`)
- Unknown `action` (valid: `BUY, SELL, STO, BTC, BTO, STC, EXP, ASGN, EXER, DIV`)
- Option event with blank `strike`, `expiry`, or `opt_type`
- Share/dividend event with non-blank `strike`, `expiry`, or `opt_type`
- `qty <= 0`, `price < 0`, `fees < 0`

If the script exits non-zero, surface the error to the user verbatim and ask how to fix.

## Corrections

`trades.csv` is **append-only**. To correct a mistakenly-logged row:

- Append a **reversing event** (e.g., logged `BUY 100` should have been `BUY 50` → append `SELL 50`).
- Then append the correct row if needed.
- Note the correction in the `notes` column of both events.

NEVER edit or delete a row in `trades.csv`.

## Confirm gate is non-negotiable

If you ever append without first showing the proposed row(s) and the diff and getting explicit approval, the skill is broken. The user values this gate (their auto-memory captures it explicitly). When in doubt, show the diff and wait.
