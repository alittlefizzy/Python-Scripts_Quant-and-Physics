"""Live trader for Strategy v2 (ensemble trend + volatility targeting) on Kraken.

The trading logic is imported from v2_trend_research.py, so the live trader runs
exactly the code that was backtested, with the same frozen settings (DEFAULT).
Live-only additions, none of which change the signal:
  * DRY_RUN: logs what it WOULD trade without sending orders. Starts switched on.
  * Minimum order size: trades smaller than MIN_ORDER_USD are skipped, because the
    exchange rejects tiny orders.
  * Equity sanity guard: if computed equity looks wrong (e.g. the account reports
    balances differently from the backtest), it refuses to trade and says why.

First run: leave DRY_RUN = True for a few days, check the log (equity close to your
capital, sensible target sizes), then set DRY_RUN = False.
Keep this file in the same folder as v2_trend_research.py and performance_report.py.
"""
from datetime import datetime, timezone

from v2_trend_research import DEFAULT, Ensemble_Trend

DRY_RUN = True            # set to False only after checking the dry-run log
MIN_ORDER_USD = 10.0      # skip trades smaller than this (exchange minimums)
QUOTE_KEYS = ('USD', 'ZUSD', 'USDT')   # how the account may name its cash balance


class Ensemble_Trend_Live(Ensemble_Trend):

    def prepare(self, tickers, lookbacks, capital, dry_run=True, min_order_usd=10.0, **settings):
        super().prepare(tickers, lookbacks, capital, **settings)
        self.dry_run = dry_run
        self.min_order_usd = min_order_usd
        self.halted = False

    def _log(self, message):
        stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        print(f"[{stamp}] {message}")

    def _equity(self, positions, prices):
        # Same accounting as the backtest (account starts at zero, cash goes negative as
        # it buys), but accepts the cash balance under whichever name the exchange uses.
        cash = sum(positions.get(key, 0.0) for key in QUOTE_KEYS)
        net = cash
        for ticker in self.tickers:
            qty = positions.get(ticker.split('/')[0], 0.0)
            if qty and prices[ticker] is not None:
                net += qty * prices[ticker]
        equity = self.capital + net

        # Guards. In the backtest's accounting cash starts at zero and goes negative as it
        # buys, so a large POSITIVE cash balance means the account is reporting real
        # balances instead, and capital would be counted twice. Separately, a day-to-day
        # strategy should not move equity outside 0.3x - 3x capital.
        problem = None
        if cash > 0.5 * self.capital:
            problem = (f"cash balance {cash:,.2f} is positive and large, so positions look like "
                       f"real account balances; capital would be double-counted")
        elif not (0.3 * self.capital <= equity <= 3.0 * self.capital):
            problem = f"computed equity {equity:,.2f} is implausible for capital {self.capital:,.2f}"
        if problem:
            if not self.halted:
                self._log(f"HALTED: {problem}. Positions reported: {positions}. "
                          f"No orders will be sent until this is resolved.")
            self.halted = True
            return 0.0      # rebalance() skips trading when equity <= 0
        self.halted = False
        self._log(f"Equity {equity:,.2f} (capital {self.capital:,.2f})")
        return equity

    def trade_to_target(self, target_positions, route=True):
        positions = self.get_pos()
        final = {}
        for base, target_qty in target_positions.items():
            ticker = next(t for t in self.tickers if t.split('/')[0] == base)
            price = self._price(ticker)
            current_qty = positions.get(base, 0.0)
            change_usd = abs(target_qty - current_qty) * price if price else 0.0
            if change_usd < self.min_order_usd:
                final[base] = current_qty           # too small to trade
            else:
                final[base] = target_qty
                self._log(f"{'WOULD TRADE' if self.dry_run else 'TRADE'} {base}: "
                          f"{current_qty:.6f} -> {target_qty:.6f} (~${change_usd:,.2f})")

        if self.dry_run:
            return
        super().trade_to_target(final, route=route)

    def on_exit(self):
        if not self.dry_run:
            self.cancel_all_orders()


if __name__ == "__main__":
    tickers_list = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']
    lookbacks = [7, 14, 21, 30, 60, 90]
    initial_capital = 250

    print(f"Initializing Strategy v2 live trader on Kraken {DEFAULT} "
          f"({'DRY RUN - no orders sent' if DRY_RUN else 'LIVE - orders will be sent'})...")

    Ensemble_Trend_Live.run_live(
        freq='1d',
        name='Ensemble_Trend_Live',
        tickers=tickers_list,
        lookbacks=lookbacks,
        capital=initial_capital,
        dry_run=DRY_RUN,
        min_order_usd=MIN_ORDER_USD,
        **DEFAULT
    )
