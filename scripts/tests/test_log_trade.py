import csv
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.log_trade import append_trade, main as log_main

FIXTURES = Path(__file__).parent / "fixtures"


class TestAppendTrade(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        # Copy fixture files
        for name in ("accounts.yaml", "wishlist.csv", "trades.csv"):
            shutil.copy(FIXTURES / name, self.tmp / name)
        self.trades = self.tmp / "trades.csv"
        self.accounts = self.tmp / "accounts.yaml"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_appends_valid_share_buy(self):
        append_trade(
            row={
                "date": "2026-05-04",
                "account": "robinhood",
                "ticker": "F",
                "action": "BUY",
                "qty": "100",
                "price": "11.50",
                "fees": "0",
                "strike": "",
                "expiry": "",
                "opt_type": "",
                "strategy_id": "",
                "notes": "added on dip",
            },
            trades_path=self.trades,
            accounts_path=self.accounts,
        )
        with open(self.trades) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 9)  # 8 + 1
        self.assertEqual(rows[-1]["price"], "11.50")
        self.assertEqual(rows[-1]["notes"], "added on dip")

    def test_rejects_unknown_account(self):
        with self.assertRaises(SystemExit):
            append_trade(
                row={
                    "date": "2026-05-04",
                    "account": "fidelity",
                    "ticker": "F",
                    "action": "BUY",
                    "qty": "100",
                    "price": "11.50",
                    "fees": "0",
                    "strike": "",
                    "expiry": "",
                    "opt_type": "",
                    "strategy_id": "",
                    "notes": "",
                },
                trades_path=self.trades,
                accounts_path=self.accounts,
            )
        # File unchanged
        with open(self.trades) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 8)

    def test_rejects_option_event_missing_strike(self):
        with self.assertRaises(SystemExit):
            append_trade(
                row={
                    "date": "2026-05-04",
                    "account": "robinhood",
                    "ticker": "F",
                    "action": "STO",
                    "qty": "1",
                    "price": "0.50",
                    "fees": "0",
                    "strike": "",
                    "expiry": "2026-05-15",
                    "opt_type": "C",
                    "strategy_id": "",
                    "notes": "",
                },
                trades_path=self.trades,
                accounts_path=self.accounts,
            )


if __name__ == "__main__":
    unittest.main()
