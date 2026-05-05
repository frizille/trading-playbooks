import unittest
from datetime import date
from pathlib import Path

from scripts.watchlist_data import (
    Account,
    Trade,
    WishlistEntry,
    load_accounts,
    load_trades,
    load_wishlist,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestLoadAccounts(unittest.TestCase):
    def test_loads_two_accounts(self):
        accounts = load_accounts(FIXTURES / "accounts.yaml")
        self.assertEqual(len(accounts), 2)
        self.assertEqual(accounts[0].name, "robinhood")
        self.assertEqual(accounts[0].display_name, "Robinhood (Individual Taxable)")
        self.assertEqual(accounts[0].type, "taxable")
        self.assertIn("short-term", accounts[0].tax_notes.lower())
        self.assertEqual(accounts[1].name, "simple_ira")
        self.assertEqual(accounts[1].type, "ira")


class TestLoadTrades(unittest.TestCase):
    def test_loads_eight_rows(self):
        trades = load_trades(FIXTURES / "trades.csv")
        self.assertEqual(len(trades), 8)

    def test_share_buy_parses(self):
        trades = load_trades(FIXTURES / "trades.csv")
        first = trades[0]
        self.assertEqual(first.date, date(2026, 4, 20))
        self.assertEqual(first.account, "robinhood")
        self.assertEqual(first.ticker, "F")
        self.assertEqual(first.action, "BUY")
        self.assertEqual(first.qty, 100)
        self.assertEqual(first.price, 12.78)
        self.assertEqual(first.fees, 0.0)
        self.assertIsNone(first.strike)
        self.assertIsNone(first.expiry)
        self.assertIsNone(first.opt_type)
        self.assertEqual(first.strategy_id, "")
        self.assertEqual(first.notes, "")

    def test_option_event_parses(self):
        trades = load_trades(FIXTURES / "trades.csv")
        sto = trades[1]  # 2026-04-20 STO
        self.assertEqual(sto.action, "STO")
        self.assertEqual(sto.qty, 1)
        self.assertEqual(sto.price, 0.12)
        self.assertEqual(sto.strike, 13.00)
        self.assertEqual(sto.expiry, date(2026, 4, 24))
        self.assertEqual(sto.opt_type, "C")


class TestLoadWishlist(unittest.TestCase):
    def test_empty_wishlist(self):
        entries = load_wishlist(FIXTURES / "wishlist.csv")
        self.assertEqual(entries, [])


from scripts.watchlist_data import ValidationError, validate_trade


class TestValidateTrade(unittest.TestCase):
    VALID_ACCOUNTS = {"robinhood", "simple_ira"}

    def _trade(self, **overrides):
        defaults = dict(
            date=date(2026, 5, 4),
            account="robinhood",
            ticker="F",
            action="BUY",
            qty=100,
            price=12.50,
            fees=0.0,
            strike=None,
            expiry=None,
            opt_type=None,
            strategy_id="",
            notes="",
        )
        defaults.update(overrides)
        return Trade(**defaults)

    def test_valid_share_buy_passes(self):
        validate_trade(self._trade(), self.VALID_ACCOUNTS)  # no raise

    def test_valid_option_open_passes(self):
        validate_trade(
            self._trade(
                action="STO",
                qty=1,
                price=0.35,
                strike=12.50,
                expiry=date(2026, 5, 8),
                opt_type="C",
            ),
            self.VALID_ACCOUNTS,
        )

    def test_unknown_account_fails(self):
        with self.assertRaises(ValidationError) as cm:
            validate_trade(self._trade(account="fidelity"), self.VALID_ACCOUNTS)
        self.assertIn("fidelity", str(cm.exception))
        self.assertIn("robinhood", str(cm.exception))

    def test_invalid_action_fails(self):
        with self.assertRaises(ValidationError):
            validate_trade(self._trade(action="WAT"), self.VALID_ACCOUNTS)

    def test_share_event_with_strike_fails(self):
        with self.assertRaises(ValidationError):
            validate_trade(
                self._trade(action="BUY", strike=12.50), self.VALID_ACCOUNTS
            )

    def test_option_event_without_strike_fails(self):
        with self.assertRaises(ValidationError):
            validate_trade(
                self._trade(
                    action="STO",
                    qty=1,
                    expiry=date(2026, 5, 8),
                    opt_type="C",
                ),
                self.VALID_ACCOUNTS,
            )

    def test_option_event_without_opt_type_fails(self):
        with self.assertRaises(ValidationError):
            validate_trade(
                self._trade(
                    action="STO",
                    qty=1,
                    strike=12.50,
                    expiry=date(2026, 5, 8),
                ),
                self.VALID_ACCOUNTS,
            )

    def test_zero_qty_fails(self):
        with self.assertRaises(ValidationError):
            validate_trade(self._trade(qty=0), self.VALID_ACCOUNTS)

    def test_negative_price_fails(self):
        with self.assertRaises(ValidationError):
            validate_trade(self._trade(price=-1.00), self.VALID_ACCOUNTS)

    def test_negative_fees_fails(self):
        with self.assertRaises(ValidationError):
            validate_trade(self._trade(fees=-0.50), self.VALID_ACCOUNTS)


if __name__ == "__main__":
    unittest.main()
