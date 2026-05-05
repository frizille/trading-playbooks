import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.log_trade import append_trade

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

    def test_lowercase_opt_type_normalized(self):
        """opt_type='c' should be uppercased to 'C' before validation."""
        append_trade(
            row={
                "date": "2026-05-04",
                "account": "robinhood",
                "ticker": "F",
                "action": "STO",
                "qty": "1",
                "price": "0.30",
                "fees": "0",
                "strike": "13.00",
                "expiry": "2026-05-15",
                "opt_type": "c",  # lowercase — should still succeed
                "strategy_id": "",
                "notes": "",
            },
            trades_path=self.trades,
            accounts_path=self.accounts,
        )
        with open(self.trades) as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 9)


class TestLogTradeMainEndToEnd(unittest.TestCase):
    """End-to-end: invoke log_trade.main() and confirm watchlist.md updates."""

    def test_main_appends_and_renders(self):
        import sys
        from scripts.log_trade import main as log_main

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for name in ("accounts.yaml", "wishlist.csv", "trades.csv"):
                shutil.copy(FIXTURES / name, tmp_path / name)
            output = tmp_path / "watchlist.md"

            saved_argv = sys.argv
            try:
                sys.argv = [
                    "log_trade.py",
                    "--date", "2026-05-04",
                    "--account", "robinhood",
                    "--ticker", "F",
                    "--action", "BUY",
                    "--qty", "50",
                    "--price", "11.50",
                    "--notes", "smoke",
                    "--trades", str(tmp_path / "trades.csv"),
                    "--accounts", str(tmp_path / "accounts.yaml"),
                    "--wishlist", str(tmp_path / "wishlist.csv"),
                    "--output", str(output),
                ]
                rc = log_main()
            finally:
                sys.argv = saved_argv

            self.assertEqual(rc, 0)
            # Trade row appended
            with open(tmp_path / "trades.csv") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 9)
            self.assertEqual(rows[-1]["notes"], "smoke")
            # watchlist.md exists and reflects the new shares (200 + 50 = 250)
            rendered = output.read_text()
            self.assertIn("# Watchlist & Current Positions", rendered)
            self.assertIn("| F | 250 |", rendered)


if __name__ == "__main__":
    unittest.main()
