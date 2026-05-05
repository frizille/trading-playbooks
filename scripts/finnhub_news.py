#!/usr/bin/env python3
"""
finnhub_news.py — Pull structured company news for a ticker from Finnhub.

Outputs a chronological list of headlines (newest first) with source, time,
URL, and a short summary. Intended to give review-position and preview-earnings
a clean, dated news feed instead of relying on web-search snippets.

Requires a free Finnhub API key (https://finnhub.io). The key is read from:
  1. FINNHUB_API_KEY environment variable, or
  2. a .env file at the repo root containing `FINNHUB_API_KEY=...`

No external dependencies — uses stdlib urllib.

Usage:
    python3 scripts/finnhub_news.py NVDA
    python3 scripts/finnhub_news.py NVDA --days 30
    python3 scripts/finnhub_news.py NVDA --from 2026-04-01 --to 2026-05-01
    python3 scripts/finnhub_news.py NVDA --days 14 --limit 25
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


FINNHUB_BASE = "https://finnhub.io/api/v1"


def load_api_key() -> str | None:
    """Return FINNHUB_API_KEY from env, falling back to a repo-root .env file."""
    key = os.environ.get("FINNHUB_API_KEY")
    if key:
        return key.strip() or None

    # Walk up from this file to find a .env at the repo root.
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        candidate = parent / ".env"
        if candidate.is_file():
            try:
                for raw in candidate.read_text().splitlines():
                    line = raw.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    name, _, value = line.partition("=")
                    if name.strip() == "FINNHUB_API_KEY":
                        value = value.strip().strip('"').strip("'")
                        return value or None
            except OSError:
                pass
            break
    return None


def fetch_company_news(ticker: str, frm: date, to: date, api_key: str) -> list[dict]:
    params = {
        "symbol": ticker,
        "from": frm.isoformat(),
        "to": to.isoformat(),
        "token": api_key,
    }
    url = f"{FINNHUB_BASE}/company-news?{urlencode(params)}"
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8")
    data = json.loads(body)
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response shape: {type(data).__name__}")
    return data


def trim(text: str, limit: int) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def main() -> int:
    ap = argparse.ArgumentParser(description="Finnhub company-news feed for a ticker.")
    ap.add_argument("ticker", help="Ticker symbol (e.g. NVDA)")
    ap.add_argument("--days", type=int, default=14,
                    help="Look-back window in days (default 14). Ignored if --from is set.")
    ap.add_argument("--from", dest="frm", type=str, default=None,
                    help="Start date YYYY-MM-DD (overrides --days)")
    ap.add_argument("--to", type=str, default=None,
                    help="End date YYYY-MM-DD (default today)")
    ap.add_argument("--limit", type=int, default=40,
                    help="Max headlines to print (default 40)")
    ap.add_argument("--summary-chars", type=int, default=240,
                    help="Truncate each summary to this many chars (default 240)")
    args = ap.parse_args()

    api_key = load_api_key()
    if not api_key:
        print(
            "ERROR: FINNHUB_API_KEY not set.\n"
            "  Get a free key at https://finnhub.io and either:\n"
            "    export FINNHUB_API_KEY=...\n"
            "  or copy .env.example to .env and fill it in.",
            file=sys.stderr,
        )
        return 2

    today = date.today()
    to_d = datetime.strptime(args.to, "%Y-%m-%d").date() if args.to else today
    if args.frm:
        frm_d = datetime.strptime(args.frm, "%Y-%m-%d").date()
    else:
        frm_d = to_d - timedelta(days=max(args.days, 1))

    if frm_d > to_d:
        print(f"ERROR: from-date {frm_d} is after to-date {to_d}", file=sys.stderr)
        return 2

    ticker = args.ticker.upper()

    try:
        items = fetch_company_news(ticker, frm_d, to_d, api_key)
    except HTTPError as e:
        if e.code == 401:
            print("ERROR: Finnhub rejected the API key (401).", file=sys.stderr)
        elif e.code == 429:
            print("ERROR: Finnhub rate limit hit (429). Free tier is 60 req/min.", file=sys.stderr)
        else:
            print(f"ERROR: Finnhub HTTP {e.code}: {e.reason}", file=sys.stderr)
        return 2
    except URLError as e:
        print(f"ERROR: network problem reaching Finnhub: {e.reason}", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, RuntimeError) as e:
        print(f"ERROR: bad response from Finnhub: {e}", file=sys.stderr)
        return 2

    items.sort(key=lambda d: d.get("datetime", 0), reverse=True)
    items = items[: args.limit]

    print(f"=== {ticker} news — {frm_d.isoformat()} → {to_d.isoformat()} ===")
    print(f"Source: Finnhub /company-news  |  {len(items)} headline(s)")
    print()

    if not items:
        print("(no headlines in range)")
        return 0

    last_day: str | None = None
    for it in items:
        ts = it.get("datetime")
        when = (
            datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%MZ")
            if isinstance(ts, (int, float)) and ts > 0
            else "—"
        )
        day = when.split(" ", 1)[0]
        if day != last_day:
            print(f"--- {day} ---")
            last_day = day

        source = trim(it.get("source") or "—", 24)
        category = trim(it.get("category") or "", 18)
        headline = trim(it.get("headline") or "(no headline)", 160)
        url = it.get("url") or ""
        summary = trim(it.get("summary") or "", args.summary_chars)

        tag = f"[{category}] " if category else ""
        print(f"  {when}  {source:<24}  {tag}{headline}")
        if summary:
            print(f"      {summary}")
        if url:
            print(f"      {url}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
