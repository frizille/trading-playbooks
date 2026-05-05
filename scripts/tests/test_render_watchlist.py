import tempfile
import unittest
from datetime import date
from pathlib import Path

from scripts.render_watchlist import render

FIXTURES = Path(__file__).parent / "fixtures"
# Frozen "today" for tests so DTE is deterministic regardless of wall clock.
FIXED_TODAY = date(2026, 5, 5)


class TestRender(unittest.TestCase):
    def test_migration_round_trip(self):
        actual = render(
            accounts_path=FIXTURES / "accounts.yaml",
            wishlist_path=FIXTURES / "wishlist.csv",
            trades_path=FIXTURES / "trades.csv",
            today=FIXED_TODAY,
        )
        expected = (FIXTURES / "expected_watchlist.md").read_text()
        self.assertEqual(actual, expected)


class TestRenderEmptyData(unittest.TestCase):
    def test_no_trades(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty_trades = Path(tmp) / "trades_empty.csv"
            empty_trades.write_text(
                "date,account,ticker,action,qty,price,fees,strike,expiry,opt_type,strategy_id,notes\n"
            )
            actual = render(
                accounts_path=FIXTURES / "accounts.yaml",
                wishlist_path=FIXTURES / "wishlist.csv",
                trades_path=empty_trades,
                today=FIXED_TODAY,
            )
        self.assertIn("# Watchlist & Current Positions", actual)
        self.assertIn("_No positions._", actual)
        self.assertIn("_No active option positions._", actual)


class TestRenderActiveOptions(unittest.TestCase):
    """Active-options table rendering and DTE injection."""

    def test_renders_open_option_with_injected_today(self):
        with tempfile.TemporaryDirectory() as tmp:
            trades = Path(tmp) / "trades.csv"
            trades.write_text(
                "date,account,ticker,action,qty,price,fees,strike,expiry,opt_type,strategy_id,notes\n"
                "2026-04-20,robinhood,F,BUY,100,12.78,0,,,,,\n"
                "2026-05-01,robinhood,F,STO,1,0.30,0,13.00,2026-05-15,C,,first weekly\n"
            )
            actual = render(
                accounts_path=FIXTURES / "accounts.yaml",
                wishlist_path=FIXTURES / "wishlist.csv",
                trades_path=trades,
                today=FIXED_TODAY,
            )
        self.assertIn("## Active Options Positions", actual)
        # Anchor the assertion on the full row substring so unrelated " | 10 | "
        # occurrences elsewhere in the output don't accidentally satisfy it.
        # DTE = 2026-05-15 - 2026-05-05 = 10. Account renders by display_name.
        expected_row = (
            "| F | CC | $13.00 | 2026-05-15 | 1 "
            "| Robinhood (Individual Taxable) | 10 | $0.30 | first weekly |"
        )
        self.assertIn(expected_row, actual)

    def test_pipe_in_notes_is_escaped(self):
        with tempfile.TemporaryDirectory() as tmp:
            trades = Path(tmp) / "trades.csv"
            trades.write_text(
                "date,account,ticker,action,qty,price,fees,strike,expiry,opt_type,strategy_id,notes\n"
                "2026-04-20,robinhood,F,BUY,100,12.78,0,,,,,\n"
                '2026-05-01,robinhood,F,STO,1,0.30,0,13.00,2026-05-15,C,,"weird | note"\n'
            )
            actual = render(
                accounts_path=FIXTURES / "accounts.yaml",
                wishlist_path=FIXTURES / "wishlist.csv",
                trades_path=trades,
                today=FIXED_TODAY,
            )
        self.assertIn(r"weird \| note", actual)


class TestRenderWishlist(unittest.TestCase):
    def test_renders_wishlist_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            wishlist = Path(tmp) / "wishlist.csv"
            wishlist.write_text(
                "ticker,thesis,priority,date_added\n"
                "NVDA,AI infra leader,high,2026-04-01\n"
                "AMD,GPU underdog,med,2026-04-15\n"
            )
            empty_trades = Path(tmp) / "trades.csv"
            empty_trades.write_text(
                "date,account,ticker,action,qty,price,fees,strike,expiry,opt_type,strategy_id,notes\n"
            )
            actual = render(
                accounts_path=FIXTURES / "accounts.yaml",
                wishlist_path=wishlist,
                trades_path=empty_trades,
                today=FIXED_TODAY,
            )
        self.assertIn("## Watchlist (No Position Yet)", actual)
        self.assertIn("| NVDA | AI infra leader | high |", actual)
        self.assertIn("| AMD | GPU underdog | med |", actual)
        # high should sort before med
        self.assertLess(actual.index("NVDA"), actual.index("AMD"))


class TestRenderDividends(unittest.TestCase):
    def test_dividend_reduces_effective_basis(self):
        with tempfile.TemporaryDirectory() as tmp:
            trades = Path(tmp) / "trades.csv"
            # 100 shares @ $10, then a $0.50/share dividend (= $50 total)
            trades.write_text(
                "date,account,ticker,action,qty,price,fees,strike,expiry,opt_type,strategy_id,notes\n"
                "2026-01-01,robinhood,X,BUY,100,10.00,0,,,,,\n"
                "2026-03-15,robinhood,X,DIV,100,0.50,0,,,,,Q1 div\n"
            )
            actual = render(
                accounts_path=FIXTURES / "accounts.yaml",
                wishlist_path=FIXTURES / "wishlist.csv",
                trades_path=trades,
                today=FIXED_TODAY,
            )
        # Dividends column shows $50.00; effective basis = 10.00 - 50/100 = 9.50
        self.assertIn("$50.00", actual)
        self.assertIn("$9.50", actual)


if __name__ == "__main__":
    unittest.main()
