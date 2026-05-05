#!/usr/bin/env python3
"""
query_trades.py — Read-only analytics helpers over data/trades.csv.

CLI usage:
    .venv/bin/python scripts/query_trades.py premium-by-ticker
    .venv/bin/python scripts/query_trades.py open-positions

Library usage:
    from scripts.query_trades import premium_by_ticker, open_positions_summary
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.watchlist_data import (
    SHARE_ACTIONS,
    compute_positions,
    load_accounts,
    load_trades,
    match_options_fifo,
    premium_banked_by_ticker,
)


def premium_by_ticker(accounts_path: Path, trades_path: Path) -> dict[str, float]:
    """Sum premium banked per ticker across all accounts."""
    trades = load_trades(trades_path)
    _, closed = match_options_fifo(trades)
    by_acct_ticker = premium_banked_by_ticker(closed)
    out: dict[str, float] = {}
    for (_, ticker), amount in by_acct_ticker.items():
        out[ticker] = out.get(ticker, 0.0) + amount
    return out


def open_positions_summary(
    accounts_path: Path, trades_path: Path
) -> dict[str, dict]:
    """For each ticker held: total shares (across accounts) and premium banked."""
    trades = load_trades(trades_path)
    share_trades = [t for t in trades if t.action in SHARE_ACTIONS]
    positions = compute_positions(share_trades)
    _, closed = match_options_fifo(trades)
    banked = premium_banked_by_ticker(closed)

    summary: dict[str, dict] = {}
    for (acct, ticker), pos in positions.items():
        row = summary.setdefault(ticker, {"shares": 0, "premium_banked": 0.0})
        row["shares"] += pos.shares
    for (acct, ticker), amount in banked.items():
        row = summary.setdefault(ticker, {"shares": 0, "premium_banked": 0.0})
        row["premium_banked"] += amount
    return summary


def main() -> int:
    p = argparse.ArgumentParser(description="Trades analytics queries")
    p.add_argument("query", choices=["premium-by-ticker", "open-positions"])
    p.add_argument("--accounts", default="data/accounts.yaml", type=Path)
    p.add_argument("--trades", default="data/trades.csv", type=Path)
    args = p.parse_args()

    if args.query == "premium-by-ticker":
        result = premium_by_ticker(args.accounts, args.trades)
    else:
        result = open_positions_summary(args.accounts, args.trades)
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
