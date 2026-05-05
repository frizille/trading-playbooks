#!/usr/bin/env python3
"""
log_trade.py — Append a single trade row to data/trades.csv after validation,
then re-render watchlist.md.

Used by the manage-watchlist skill. Also runnable manually:

    .venv/bin/python scripts/log_trade.py \\
        --date 2026-05-04 --account robinhood --ticker F --action BUY \\
        --qty 100 --price 11.50

By default the renderer is invoked after a successful append. Pass
--no-render to skip (useful for batch backfills).
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.watchlist_data import (
    Trade,
    ValidationError,
    load_accounts,
    validate_trade,
)

CSV_HEADERS = [
    "date", "account", "ticker", "action", "qty", "price", "fees",
    "strike", "expiry", "opt_type", "strategy_id", "notes",
]


def _row_to_trade(row: dict) -> Trade:
    def _fdate(s):
        return datetime.strptime(s, "%Y-%m-%d").date() if s else None

    return Trade(
        date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
        account=row["account"],
        ticker=row["ticker"].upper(),
        action=row["action"].upper(),
        qty=int(row["qty"]),
        price=float(row["price"]),
        fees=float(row["fees"]) if row["fees"] else 0.0,
        strike=float(row["strike"]) if row["strike"] else None,
        expiry=_fdate(row["expiry"]),
        opt_type=row["opt_type"].upper() if row["opt_type"] else None,
        strategy_id=row["strategy_id"],
        notes=row["notes"],
    )


def _check_existing_header(trades_path: Path) -> None:
    """Verify an existing trades.csv has the expected header. Raise on mismatch."""
    with open(trades_path) as f:
        first = f.readline().rstrip("\n").rstrip("\r")
    actual = [c.strip() for c in first.split(",")]
    if actual != CSV_HEADERS:
        raise ValidationError(
            f"trades.csv header mismatch — expected {CSV_HEADERS}, got {actual}"
        )


def append_trade(
    row: dict,
    trades_path: Path,
    accounts_path: Path,
) -> None:
    """Validate and append. On invalid input prints to stderr and sys.exit(2)."""
    try:
        trade = _row_to_trade(row)
        accounts = load_accounts(accounts_path)
        valid_names = {a.name for a in accounts}
        validate_trade(trade, valid_names)
        if trades_path.exists():
            _check_existing_header(trades_path)
    except (ValueError, ValidationError) as e:
        print(f"validation error: {e}", file=sys.stderr)
        sys.exit(2)

    # Append (CSV writer; empty strings preserved for blank fields)
    file_exists = trades_path.exists()
    with open(trades_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        # Use the original row dict so blanks stay blank (don't write "None")
        writer.writerow({k: row.get(k, "") for k in CSV_HEADERS})


def _render(accounts_path: Path, trades_path: Path, wishlist_path: Path,
            output_path: Path) -> None:
    from scripts.render_watchlist import render
    rendered = render(
        accounts_path=accounts_path,
        wishlist_path=wishlist_path,
        trades_path=trades_path,
    )
    output_path.write_text(rendered)


def main() -> int:
    p = argparse.ArgumentParser(description="Append a trade event")
    p.add_argument("--date", required=True)
    p.add_argument("--account", required=True)
    p.add_argument("--ticker", required=True)
    p.add_argument("--action", required=True)
    p.add_argument("--qty", required=True)
    p.add_argument("--price", required=True)
    p.add_argument("--fees", default="0")
    p.add_argument("--strike", default="")
    p.add_argument("--expiry", default="")
    p.add_argument("--opt-type", default="", dest="opt_type")
    p.add_argument("--strategy-id", default="", dest="strategy_id")
    p.add_argument("--notes", default="")
    p.add_argument("--trades", default="data/trades.csv", type=Path)
    p.add_argument("--accounts", default="data/accounts.yaml", type=Path)
    p.add_argument("--wishlist", default="data/wishlist.csv", type=Path)
    p.add_argument("--output", default="watchlist.md", type=Path)
    p.add_argument("--no-render", action="store_true")
    args = p.parse_args()

    row = {
        "date": args.date, "account": args.account, "ticker": args.ticker,
        "action": args.action, "qty": args.qty, "price": args.price,
        "fees": args.fees, "strike": args.strike, "expiry": args.expiry,
        "opt_type": args.opt_type, "strategy_id": args.strategy_id,
        "notes": args.notes,
    }
    append_trade(row, trades_path=args.trades, accounts_path=args.accounts)

    if not args.no_render:
        _render(args.accounts, args.trades, args.wishlist, args.output)
        print(f"appended 1 row to {args.trades}; re-rendered {args.output}",
              file=sys.stderr)
    else:
        print(f"appended 1 row to {args.trades} (no render)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
