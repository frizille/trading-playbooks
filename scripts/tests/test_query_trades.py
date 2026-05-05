import unittest
from pathlib import Path

from scripts.query_trades import premium_by_ticker, open_positions_summary

FIXTURES = Path(__file__).parent / "fixtures"


class TestPremiumByTicker(unittest.TestCase):
    def test_f_total_71(self):
        result = premium_by_ticker(
            accounts_path=FIXTURES / "accounts.yaml",
            trades_path=FIXTURES / "trades.csv",
        )
        self.assertAlmostEqual(result["F"], 71.00, places=2)


class TestOpenPositionsSummary(unittest.TestCase):
    def test_summary_includes_f(self):
        summary = open_positions_summary(
            accounts_path=FIXTURES / "accounts.yaml",
            trades_path=FIXTURES / "trades.csv",
        )
        self.assertIn("F", summary)
        f_row = summary["F"]
        self.assertEqual(f_row["shares"], 200)
        self.assertAlmostEqual(f_row["premium_banked"], 71.00, places=2)


if __name__ == "__main__":
    unittest.main()
