#!/usr/bin/env python3
"""
render_watchlist.py — Pure projection: read trades.csv + wishlist.csv +
accounts.yaml, write watchlist.md.

Run from repo root:
    .venv/bin/python scripts/render_watchlist.py

Or with custom paths:
    python3 scripts/render_watchlist.py --accounts data/accounts.yaml \\
        --trades data/trades.csv --wishlist data/wishlist.csv \\
        --output watchlist.md
"""

from __future__ import annotations

import argparse
import sys
from datetime import date as _date
from pathlib import Path

# Allow running as a script from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.watchlist_data import (
    Account,
    ClosedOptionPair,
    OpenOption,
    SHARE_ACTIONS,
    Trade,
    closed_pair_pnl,
    compute_positions,
    load_accounts,
    load_trades,
    load_wishlist,
    match_options_fifo,
    premium_banked_by_ticker,
)


def render(
    accounts_path: Path,
    wishlist_path: Path,
    trades_path: Path,
) -> str:
    accounts = load_accounts(accounts_path)
    wishlist = load_wishlist(wishlist_path)
    trades = load_trades(trades_path)

    share_trades = [t for t in trades if t.action in SHARE_ACTIONS]
    positions = compute_positions(share_trades)
    open_options, closed_pairs = match_options_fifo(trades)
    banked = premium_banked_by_ticker(closed_pairs)

    parts: list[str] = []
    parts.append("# Watchlist & Current Positions\n")
    parts.append(_render_positions(accounts, positions, banked))
    parts.append(_render_active_options(open_options))
    parts.append(_render_closed_history(closed_pairs))
    parts.append(_render_wishlist(wishlist))
    parts.append(_render_notes(accounts))
    return "\n".join(parts)


def _money(x: float) -> str:
    return f"${x:.2f}"


def _signed_money(x: float) -> str:
    return f"+{_money(x)}" if x >= 0 else f"-{_money(-x)}"


def _render_positions(accounts, positions, banked) -> str:
    out: list[str] = ["## Positions by Account\n"]
    for acct in accounts:
        out.append(f"### {acct.display_name}\n")
        rows = [
            (key, pos) for key, pos in positions.items() if key[0] == acct.name
        ]
        rows.sort(key=lambda r: r[0][1])  # by ticker
        if not rows:
            out.append("_No positions._\n")
            continue
        out.append(
            "| Ticker | Shares | Avg Cost | Lots | Premium Banked | Effective Basis |"
        )
        out.append(
            "|--------|--------|----------|------|----------------|-----------------|"
        )
        for key, pos in rows:
            premium = banked.get(key, 0.0)
            eff_basis = pos.avg_cost - (premium / pos.shares) if pos.shares else 0.0
            lots_str = "<br>".join(
                f"{lot.qty} @ {_money(lot.price)} ({lot.date.isoformat()})"
                for lot in pos.lots
            )
            out.append(
                f"| {key[1]} | {pos.shares} | {_money(pos.avg_cost)} | "
                f"{lots_str} | {_money(premium)} | {_money(eff_basis)} |"
            )
        out.append("")  # trailing blank line
    return "\n".join(out)


def _opt_type_label(opener: Trade) -> str:
    if opener.action == "STO" and opener.opt_type == "C":
        return "CC"
    if opener.action == "STO" and opener.opt_type == "P":
        return "CSP"
    if opener.action == "BTO" and opener.opt_type == "C":
        return "long call"
    if opener.action == "BTO" and opener.opt_type == "P":
        return "long put"
    return f"{opener.action} {opener.opt_type}"


def _outcome_label(closer_action: str) -> str:
    return {
        "BTC": "bought to close",
        "STC": "sold to close",
        "EXP": "expired worthless",
        "ASGN": "assigned",
        "EXER": "exercised",
    }.get(closer_action, closer_action)


def _render_active_options(open_options: list[OpenOption]) -> str:
    out: list[str] = ["---\n", "## Active Options Positions\n"]
    if not open_options:
        out.append("_No active option positions._\n")
        return "\n".join(out)
    out.append(
        "| Ticker | Type | Strike | Expiry | Qty | Account | DTE | Open Credit | Notes |"
    )
    out.append(
        "|--------|------|--------|--------|-----|---------|-----|-------------|-------|"
    )
    today = _date.today()
    for o in sorted(open_options, key=lambda x: (x.opener.expiry, x.opener.ticker)):
        op = o.opener
        dte = (op.expiry - today).days
        out.append(
            f"| {op.ticker} | {_opt_type_label(op)} | {_money(op.strike)} | "
            f"{op.expiry.isoformat()} | {o.qty} | {op.account} | {dte} | "
            f"{_money(op.price)} | {op.notes} |"
        )
    out.append("")
    return "\n".join(out)


def _render_closed_history(closed_pairs: list[ClosedOptionPair]) -> str:
    out: list[str] = ["---\n", "## Closed Options History\n"]
    if not closed_pairs:
        out.append("_No closed options yet._\n")
        return "\n".join(out)
    out.append(
        "| Ticker | Type | Strike | Expiry | Opened | Closed | Open Credit | "
        "Close Debit | Net P&L | Account | Outcome |"
    )
    out.append(
        "|--------|------|--------|--------|--------|--------|-------------|"
        "-------------|---------|---------|---------|"
    )
    for pair in sorted(
        closed_pairs, key=lambda p: (p.closer.date, p.opener.date), reverse=True
    ):
        op = pair.opener
        cl = pair.closer
        pnl = closed_pair_pnl(pair)
        out.append(
            f"| {op.ticker} | {_opt_type_label(op)} | {_money(op.strike)} | "
            f"{op.expiry.isoformat()} | {op.date.isoformat()} | "
            f"{cl.date.isoformat()} | {_money(op.price)} | {_money(cl.price)} | "
            f"{_signed_money(pnl)} | {op.account} | {_outcome_label(cl.action)} |"
        )
    out.append("")
    return "\n".join(out)


def _render_wishlist(wishlist) -> str:
    out: list[str] = ["---\n", "## Watchlist (No Position Yet)\n"]
    if not wishlist:
        out.append("_None._\n")
        return "\n".join(out)
    out.append("| Ticker | Thesis | Priority |")
    out.append("|--------|--------|----------|")
    pri = {"high": 0, "med": 1, "low": 2}
    for entry in sorted(
        wishlist, key=lambda e: (pri.get(e.priority.lower(), 99), e.date_added)
    ):
        out.append(f"| {entry.ticker} | {entry.thesis} | {entry.priority} |")
    out.append("")
    return "\n".join(out)


def _render_notes(accounts: list[Account]) -> str:
    out: list[str] = ["---\n", "## Notes\n"]
    for acct in accounts:
        out.append(f"- **{acct.display_name}:** {acct.tax_notes}")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render watchlist.md")
    parser.add_argument("--accounts", default="data/accounts.yaml", type=Path)
    parser.add_argument("--trades", default="data/trades.csv", type=Path)
    parser.add_argument("--wishlist", default="data/wishlist.csv", type=Path)
    parser.add_argument("--output", default="watchlist.md", type=Path)
    args = parser.parse_args()

    rendered = render(
        accounts_path=args.accounts,
        wishlist_path=args.wishlist,
        trades_path=args.trades,
    )
    args.output.write_text(rendered)
    print(f"wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
