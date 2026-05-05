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

    def test_option_event_without_expiry_fails(self):
        with self.assertRaises(ValidationError):
            validate_trade(
                self._trade(
                    action="STO",
                    qty=1,
                    strike=12.50,
                    opt_type="C",
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


from scripts.watchlist_data import Lot, compute_positions, SHARE_ACTIONS


class TestComputePositions(unittest.TestCase):
    def test_two_lots_no_sells(self):
        trades = load_trades(FIXTURES / "trades.csv")
        share_trades = [t for t in trades if t.action in SHARE_ACTIONS]
        positions = compute_positions(share_trades)
        # Key: (account, ticker)
        f_pos = positions[("robinhood", "F")]
        self.assertEqual(f_pos.shares, 200)
        self.assertAlmostEqual(f_pos.avg_cost, 12.545, places=3)
        self.assertEqual(len(f_pos.lots), 2)
        self.assertEqual(f_pos.lots[0], Lot(qty=100, price=12.78, date=date(2026, 4, 20)))
        self.assertEqual(f_pos.lots[1], Lot(qty=100, price=12.31, date=date(2026, 4, 28)))

    def test_partial_sell_fifo(self):
        trades = [
            Trade(
                date=date(2026, 1, 1), account="a", ticker="X", action="BUY",
                qty=100, price=10.00, fees=0, strike=None, expiry=None,
                opt_type=None, strategy_id="", notes="",
            ),
            Trade(
                date=date(2026, 2, 1), account="a", ticker="X", action="BUY",
                qty=100, price=20.00, fees=0, strike=None, expiry=None,
                opt_type=None, strategy_id="", notes="",
            ),
            Trade(
                date=date(2026, 3, 1), account="a", ticker="X", action="SELL",
                qty=50, price=25.00, fees=0, strike=None, expiry=None,
                opt_type=None, strategy_id="", notes="",
            ),
        ]
        positions = compute_positions(trades)
        pos = positions[("a", "X")]
        self.assertEqual(pos.shares, 150)
        # FIFO depletes first lot: 50 @ 10 left + 100 @ 20 = (500 + 2000) / 150
        self.assertAlmostEqual(pos.avg_cost, 16.6667, places=3)
        self.assertEqual(len(pos.lots), 2)
        self.assertEqual(pos.lots[0].qty, 50)
        self.assertEqual(pos.lots[1].qty, 100)

    def test_full_liquidation_then_rebuy(self):
        trades = [
            Trade(date=date(2026, 1, 1), account="a", ticker="X", action="BUY",
                  qty=100, price=10.00, fees=0, strike=None, expiry=None,
                  opt_type=None, strategy_id="", notes=""),
            Trade(date=date(2026, 2, 1), account="a", ticker="X", action="SELL",
                  qty=100, price=15.00, fees=0, strike=None, expiry=None,
                  opt_type=None, strategy_id="", notes=""),
            Trade(date=date(2026, 3, 1), account="a", ticker="X", action="BUY",
                  qty=50, price=12.00, fees=0, strike=None, expiry=None,
                  opt_type=None, strategy_id="", notes=""),
        ]
        positions = compute_positions(trades)
        pos = positions[("a", "X")]
        self.assertEqual(pos.shares, 50)
        self.assertAlmostEqual(pos.avg_cost, 12.00, places=2)
        self.assertEqual(len(pos.lots), 1)


from scripts.watchlist_data import (
    ClosedOptionPair,
    OpenOption,
    match_options_fifo,
)


class TestMatchOptionsFifo(unittest.TestCase):
    def test_migration_data_matches_three_pairs_no_open(self):
        trades = load_trades(FIXTURES / "trades.csv")
        opens, closeds = match_options_fifo(trades)
        self.assertEqual(opens, [])
        self.assertEqual(len(closeds), 3)

    def test_match_fifo_when_two_opens_same_key(self):
        trades = [
            Trade(date=date(2026, 4, 27), account="r", ticker="F", action="STO",
                  qty=1, price=0.35, fees=0, strike=12.50, expiry=date(2026, 5, 1),
                  opt_type="C", strategy_id="", notes=""),
            Trade(date=date(2026, 4, 28), account="r", ticker="F", action="STO",
                  qty=1, price=0.26, fees=0, strike=12.50, expiry=date(2026, 5, 1),
                  opt_type="C", strategy_id="", notes=""),
            Trade(date=date(2026, 4, 30), account="r", ticker="F", action="BTC",
                  qty=1, price=0.01, fees=0, strike=12.50, expiry=date(2026, 5, 1),
                  opt_type="C", strategy_id="", notes=""),
        ]
        opens, closeds = match_options_fifo(trades)
        self.assertEqual(len(opens), 1)
        # The 4/28 STO (priced 0.26) is still open; 4/27 STO (0.35) closed first.
        self.assertEqual(opens[0].opener.price, 0.26)
        self.assertEqual(len(closeds), 1)
        self.assertEqual(closeds[0].opener.price, 0.35)

    def test_unmatched_closer_raises(self):
        trades = [
            Trade(date=date(2026, 5, 1), account="r", ticker="F", action="BTC",
                  qty=1, price=0.01, fees=0, strike=12.50, expiry=date(2026, 5, 8),
                  opt_type="C", strategy_id="", notes=""),
        ]
        with self.assertRaises(ValidationError) as cm:
            match_options_fifo(trades)
        self.assertIn("unmatched", str(cm.exception).lower())

    def test_qty_split_across_multiple_opens(self):
        trades = [
            Trade(date=date(2026, 4, 1), account="r", ticker="X", action="STO",
                  qty=1, price=1.00, fees=0, strike=50.00, expiry=date(2026, 5, 15),
                  opt_type="C", strategy_id="", notes=""),
            Trade(date=date(2026, 4, 5), account="r", ticker="X", action="STO",
                  qty=2, price=1.50, fees=0, strike=50.00, expiry=date(2026, 5, 15),
                  opt_type="C", strategy_id="", notes=""),
            Trade(date=date(2026, 4, 20), account="r", ticker="X", action="BTC",
                  qty=2, price=0.10, fees=0, strike=50.00, expiry=date(2026, 5, 15),
                  opt_type="C", strategy_id="", notes=""),
        ]
        opens, closeds = match_options_fifo(trades)
        self.assertEqual(len(opens), 1)
        self.assertEqual(opens[0].qty, 1)  # 1 of the 2 from 4/5 still open
        self.assertEqual(opens[0].opener.price, 1.50)
        self.assertEqual(len(closeds), 2)
        self.assertEqual(closeds[0].opener.date, date(2026, 4, 1))
        self.assertEqual(closeds[0].qty, 1)
        self.assertEqual(closeds[1].opener.date, date(2026, 4, 5))
        self.assertEqual(closeds[1].qty, 1)


from scripts.watchlist_data import closed_pair_pnl, premium_banked_by_ticker


class TestClosedPairPnL(unittest.TestCase):
    def test_short_sto_btc(self):
        opener = Trade(date=date(2026, 4, 27), account="r", ticker="F", action="STO",
                       qty=1, price=0.35, fees=0, strike=12.50,
                       expiry=date(2026, 5, 1), opt_type="C", strategy_id="", notes="")
        closer = Trade(date=date(2026, 4, 30), account="r", ticker="F", action="BTC",
                       qty=1, price=0.01, fees=0, strike=12.50,
                       expiry=date(2026, 5, 1), opt_type="C", strategy_id="", notes="")
        pair = ClosedOptionPair(opener=opener, closer=closer, qty=1)
        # Net = (0.35 - 0.01) * 1 * 100 - 0 - 0 = 34.00
        self.assertAlmostEqual(closed_pair_pnl(pair), 34.00, places=2)

    def test_short_sto_exp(self):
        opener = Trade(date=date(2026, 4, 20), account="r", ticker="F", action="STO",
                       qty=1, price=0.12, fees=0, strike=13.00,
                       expiry=date(2026, 4, 24), opt_type="C", strategy_id="", notes="")
        closer = Trade(date=date(2026, 4, 24), account="r", ticker="F", action="EXP",
                       qty=1, price=0, fees=0, strike=13.00,
                       expiry=date(2026, 4, 24), opt_type="C", strategy_id="",
                       notes="expired worthless")
        pair = ClosedOptionPair(opener=opener, closer=closer, qty=1)
        self.assertAlmostEqual(closed_pair_pnl(pair), 12.00, places=2)

    def test_short_with_fees(self):
        opener = Trade(date=date(2026, 4, 1), account="r", ticker="X", action="STO",
                       qty=2, price=1.00, fees=1.30, strike=50.00,
                       expiry=date(2026, 5, 15), opt_type="C", strategy_id="", notes="")
        closer = Trade(date=date(2026, 4, 30), account="r", ticker="X", action="BTC",
                       qty=2, price=0.10, fees=1.30, strike=50.00,
                       expiry=date(2026, 5, 15), opt_type="C", strategy_id="", notes="")
        pair = ClosedOptionPair(opener=opener, closer=closer, qty=2)
        # Net = (1.00 - 0.10) * 2 * 100 - 1.30 - 1.30 = 180 - 2.60 = 177.40
        self.assertAlmostEqual(closed_pair_pnl(pair), 177.40, places=2)

    def test_long_bto_stc(self):
        opener = Trade(date=date(2026, 1, 1), account="r", ticker="X", action="BTO",
                       qty=1, price=2.00, fees=0, strike=100.00,
                       expiry=date(2027, 1, 1), opt_type="C", strategy_id="", notes="")
        closer = Trade(date=date(2026, 6, 1), account="r", ticker="X", action="STC",
                       qty=1, price=5.00, fees=0, strike=100.00,
                       expiry=date(2027, 1, 1), opt_type="C", strategy_id="", notes="")
        pair = ClosedOptionPair(opener=opener, closer=closer, qty=1)
        # Long: net = (close - open) * qty * 100 - fees = (5 - 2) * 100 = 300
        self.assertAlmostEqual(closed_pair_pnl(pair), 300.00, places=2)


class TestPremiumBankedByTicker(unittest.TestCase):
    def test_f_total_71(self):
        trades = load_trades(FIXTURES / "trades.csv")
        _, closed = match_options_fifo(trades)
        banked = premium_banked_by_ticker(closed)
        # 12 + 34 + 25 = 71
        self.assertAlmostEqual(banked[("robinhood", "F")], 71.00, places=2)


if __name__ == "__main__":
    unittest.main()
