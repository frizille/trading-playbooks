#!/usr/bin/env python3
"""
watchlist_data.py — Shared types, loaders, validators, and derivations
for the watchlist data layer.

Used by render_watchlist.py, log_trade.py, and query_trades.py.

Requires:
    pip install -r scripts/requirements.txt
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError as e:
    print(
        f"Missing dependency: {e.name}. Install with:\n"
        f"    pip install -r scripts/requirements.txt",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------- Types ----------

VALID_ACTIONS = {"BUY", "SELL", "STO", "BTC", "BTO", "STC", "EXP", "ASGN", "EXER", "DIV"}
SHARE_ACTIONS = {"BUY", "SELL"}
OPTION_OPEN = {"STO", "BTO"}
OPTION_CLOSE = {"BTC", "STC", "EXP", "ASGN", "EXER"}
OPTION_ACTIONS = OPTION_OPEN | OPTION_CLOSE


@dataclass(frozen=True)
class Account:
    name: str
    display_name: str
    type: str  # taxable | ira | hsa | 401k
    tax_notes: str


@dataclass(frozen=True)
class Trade:
    date: date
    account: str
    ticker: str
    action: str
    qty: int
    price: float
    fees: float
    strike: Optional[float]
    expiry: Optional[date]
    opt_type: Optional[str]  # "C" | "P" | None
    strategy_id: str
    notes: str


@dataclass(frozen=True)
class WishlistEntry:
    ticker: str
    thesis: str
    priority: str
    date_added: date


# ---------- Loaders ----------

def load_accounts(path: Path) -> list[Account]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return [
        Account(
            name=row["name"],
            display_name=row["display_name"],
            type=row["type"],
            tax_notes=row["tax_notes"],
        )
        for row in data["accounts"]
    ]


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _opt_float(s: str) -> Optional[float]:
    return float(s) if s else None


def _opt_date(s: str) -> Optional[date]:
    return _parse_date(s) if s else None


def _opt_str(s: str) -> Optional[str]:
    return s if s else None


def load_trades(path: Path) -> list[Trade]:
    trades = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append(
                Trade(
                    date=_parse_date(row["date"]),
                    account=row["account"],
                    ticker=row["ticker"],
                    action=row["action"],
                    qty=int(row["qty"]),
                    price=float(row["price"]),
                    fees=float(row["fees"]) if row["fees"] else 0.0,
                    strike=_opt_float(row["strike"]),
                    expiry=_opt_date(row["expiry"]),
                    opt_type=_opt_str(row["opt_type"]),
                    strategy_id=row["strategy_id"],
                    notes=row["notes"],
                )
            )
    return trades


def load_wishlist(path: Path) -> list[WishlistEntry]:
    entries = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(
                WishlistEntry(
                    ticker=row["ticker"],
                    thesis=row["thesis"],
                    priority=row["priority"],
                    date_added=_parse_date(row["date_added"]),
                )
            )
    return entries
