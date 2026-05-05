import unittest
from pathlib import Path

from scripts.render_watchlist import render

FIXTURES = Path(__file__).parent / "fixtures"


class TestRender(unittest.TestCase):
    def test_migration_round_trip(self):
        actual = render(
            accounts_path=FIXTURES / "accounts.yaml",
            wishlist_path=FIXTURES / "wishlist.csv",
            trades_path=FIXTURES / "trades.csv",
        )
        expected = (FIXTURES / "expected_watchlist.md").read_text()
        self.assertEqual(actual, expected)


class TestRenderEmptyData(unittest.TestCase):
    def test_no_trades(self):
        # Empty trades file (header only)
        empty_trades = FIXTURES / "trades_empty.csv"
        empty_trades.write_text(
            "date,account,ticker,action,qty,price,fees,strike,expiry,opt_type,strategy_id,notes\n"
        )
        try:
            actual = render(
                accounts_path=FIXTURES / "accounts.yaml",
                wishlist_path=FIXTURES / "wishlist.csv",
                trades_path=empty_trades,
            )
            self.assertIn("# Watchlist & Current Positions", actual)
            self.assertIn("_No positions._", actual)
            self.assertIn("_No active option positions._", actual)
        finally:
            empty_trades.unlink()


if __name__ == "__main__":
    unittest.main()
