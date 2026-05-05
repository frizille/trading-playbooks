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


# ---------- Validation ----------

class ValidationError(ValueError):
    pass


def validate_trade(trade: Trade, valid_accounts: set[str]) -> None:
    """Raise ValidationError if the trade is invalid. No return on success."""
    if trade.account not in valid_accounts:
        raise ValidationError(
            f"unknown account {trade.account!r}; "
            f"valid: {sorted(valid_accounts)}"
        )
    if trade.action not in VALID_ACTIONS:
        raise ValidationError(
            f"unknown action {trade.action!r}; valid: {sorted(VALID_ACTIONS)}"
        )
    if trade.qty <= 0:
        raise ValidationError(f"qty must be > 0, got {trade.qty}")
    if trade.price < 0:
        raise ValidationError(f"price must be >= 0, got {trade.price}")
    if trade.fees < 0:
        raise ValidationError(f"fees must be >= 0, got {trade.fees}")

    is_option = trade.action in OPTION_ACTIONS
    is_share = trade.action in SHARE_ACTIONS
    is_dividend = trade.action == "DIV"

    if is_option:
        if trade.strike is None:
            raise ValidationError(f"option event {trade.action} requires strike")
        if trade.expiry is None:
            raise ValidationError(f"option event {trade.action} requires expiry")
        if trade.opt_type not in ("C", "P"):
            raise ValidationError(
                f"option event {trade.action} requires opt_type C or P, "
                f"got {trade.opt_type!r}"
            )
    elif is_share or is_dividend:
        if trade.strike is not None or trade.expiry is not None or trade.opt_type:
            raise ValidationError(
                f"{trade.action} event must have blank strike/expiry/opt_type"
            )


# ---------- Position math ----------

@dataclass(frozen=True)
class Lot:
    qty: int
    price: float
    date: date


@dataclass
class Position:
    account: str
    ticker: str
    lots: list[Lot] = field(default_factory=list)

    @property
    def shares(self) -> int:
        return sum(lot.qty for lot in self.lots)

    @property
    def avg_cost(self) -> float:
        s = self.shares
        if s == 0:
            return 0.0
        return sum(lot.qty * lot.price for lot in self.lots) / s


def compute_positions(share_trades: list[Trade]) -> dict[tuple[str, str], Position]:
    """
    Build current positions from share events using FIFO depletion on SELL
    and the share legs of ASGN/EXER. Input is already filtered to share-affecting
    events.

    Returns dict keyed by (account, ticker). Tickers with zero shares are omitted.
    """
    positions: dict[tuple[str, str], Position] = {}
    # Sort by date so FIFO is deterministic across same-day events (input order
    # within a date breaks ties).
    for t in sorted(share_trades, key=lambda x: (x.date,)):
        key = (t.account, t.ticker)
        pos = positions.setdefault(key, Position(account=t.account, ticker=t.ticker))
        if t.action == "BUY":
            pos.lots.append(Lot(qty=t.qty, price=t.price, date=t.date))
        elif t.action == "SELL":
            _deplete_fifo(pos, t.qty)
        else:
            raise ValueError(f"compute_positions got non-share action {t.action!r}")
    # Drop empty positions
    return {k: v for k, v in positions.items() if v.shares > 0}


def _deplete_fifo(pos: Position, qty: int) -> None:
    remaining = qty
    while remaining > 0 and pos.lots:
        head = pos.lots[0]
        if head.qty > remaining:
            pos.lots[0] = Lot(qty=head.qty - remaining, price=head.price, date=head.date)
            remaining = 0
        else:
            remaining -= head.qty
            pos.lots.pop(0)
    if remaining > 0:
        raise ValidationError(
            f"FIFO depletion underflow on {pos.account}/{pos.ticker}: "
            f"tried to sell {qty} but only {pos.shares + (qty - remaining)} held"
        )


# ---------- Option matching ----------

@dataclass(frozen=True)
class OpenOption:
    opener: Trade
    qty: int  # remaining open qty (may be < opener.qty if partially closed)


@dataclass(frozen=True)
class ClosedOptionPair:
    opener: Trade
    closer: Trade
    qty: int  # qty of contracts in this matched pair


def _option_key(t: Trade) -> tuple[str, str, float, date, str]:
    return (t.account, t.ticker, t.strike, t.expiry, t.opt_type)


def match_options_fifo(
    trades: list[Trade],
) -> tuple[list[OpenOption], list[ClosedOptionPair]]:
    """
    Match option openers to closers FIFO. Returns (open_remaining, closed_pairs).
    Raises ValidationError if any closer cannot be matched.

    Same-day opener+closer is allowed (e.g., open and close in one session) —
    we sort by (date, action_priority) where opens come before closes on the
    same date.
    """
    # Action priority: opens (0) before closes (1) within same date so a
    # same-day open-and-close matches.
    def priority(t: Trade) -> int:
        return 0 if t.action in OPTION_OPEN else 1

    option_trades = [t for t in trades if t.action in OPTION_ACTIONS]
    option_trades.sort(key=lambda t: (t.date, priority(t)))

    # open_queues: key -> list[(opener, remaining_qty)]
    open_queues: dict[tuple, list[list]] = {}
    closed_pairs: list[ClosedOptionPair] = []

    for t in option_trades:
        key = _option_key(t)
        if t.action in OPTION_OPEN:
            open_queues.setdefault(key, []).append([t, t.qty])
        else:
            queue = open_queues.get(key, [])
            remaining = t.qty
            while remaining > 0 and queue:
                head_opener, head_qty = queue[0]
                take = min(head_qty, remaining)
                closed_pairs.append(
                    ClosedOptionPair(opener=head_opener, closer=t, qty=take)
                )
                remaining -= take
                if take == head_qty:
                    queue.pop(0)
                else:
                    queue[0][1] = head_qty - take
            if remaining > 0:
                raise ValidationError(
                    f"unmatched closer at row date {t.date} "
                    f"{t.account}/{t.ticker} {t.action} {t.qty}x "
                    f"strike={t.strike} expiry={t.expiry} {t.opt_type}: "
                    f"missing opener for {remaining} contract(s)"
                )

    open_remaining: list[OpenOption] = []
    for queue in open_queues.values():
        for opener, remaining_qty in queue:
            if remaining_qty > 0:
                open_remaining.append(OpenOption(opener=opener, qty=remaining_qty))
    # Stable sort by opener date for deterministic output
    open_remaining.sort(key=lambda o: (o.opener.date, o.opener.ticker))
    return open_remaining, closed_pairs
