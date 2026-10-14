"""Which strategy change moved the results?

Runs the backtest with the original v1 logic, then with each of the four
strategy changes switched on one at a time, then with all four. Every run is scored
by the corrected evaluate() in performance_report.py, so the numbers compare
like with like. Keep this file in the same folder as performance_report.py.
"""
import numpy as np
import pandas as pd
from twsq.alpha import Alpha

from performance_report import evaluate


class WFO_Compare(Alpha):
    stop_count = 0  # stops fired in the most recent run

    def prepare(self, tickers, test_windows, capital, rebalance_days=30, stop_loss_pct=0.15,
                peak_daily=True, no_same_day_rebuy=True, throttle_fix=True, equal_scoring=True):
        self.tickers = tickers
        self.test_windows = test_windows
        self.capital = capital
        self.rebalance_days = rebalance_days
        self.days_since_rebalance = rebalance_days
        self.stop_loss_pct = stop_loss_pct
        self.high_water_marks = {}
        self.peak_daily = peak_daily
        self.no_same_day_rebuy = no_same_day_rebuy
        self.throttle_fix = throttle_fix
        self.equal_scoring = equal_scoring
        type(self).stop_count = 0

    def rebalance(self):
        current_positions = self.get_pos()
        stopped_today = set()

        for ticker in self.tickers:
            base_asset = ticker.split('/')[0]
            qty = current_positions.get(base_asset, 0)

            if qty > 0:
                current_price = self.get_current_price(ticker)
                peak_price = self.high_water_marks.get(ticker, current_price)

                if self.peak_daily:
                    if peak_price <= 0:
                        peak_price = current_price
                    if current_price > peak_price:
                        peak_price = current_price
                    self.high_water_marks[ticker] = peak_price
                else:  # original: peak stored only on a new high
                    if current_price > peak_price:
                        self.high_water_marks[ticker] = current_price

                if current_price <= peak_price * (1 - self.stop_loss_pct):
                    self.create_order(ticker, qty, 'sell', route=True)
                    self.high_water_marks[ticker] = 0.0
                    stopped_today.add(ticker)
                    type(self).stop_count += 1

        if not self.no_same_day_rebuy:
            stopped_today = set()

        if self.throttle_fix:
            self.days_since_rebalance += 1
            if self.days_since_rebalance < self.rebalance_days:
                return
        else:  # original: rebalances every rebalance_days + 1 bars
            if self.days_since_rebalance < self.rebalance_days:
                self.days_since_rebalance += 1
                return

        self.days_since_rebalance = 0
        target_positions = {}
        inv_vols = {}
        signals = {}
        warmup = max(self.test_windows)

        for ticker in self.tickers:
            if ticker in stopped_today:
                continue

            bars = self.get_lastn_bars(ticker, 365, '1d')
            if bars is None or len(bars) < warmup + 30:
                target_positions[ticker.split('/')[0]] = 0.0
                continue

            prices = bars['close']
            daily_returns = prices.pct_change(1).fillna(0)

            best_sharpe = -np.inf
            best_window = 30

            for w in self.test_windows:
                ret_window = prices.pct_change(periods=w)
                sig_array = np.where(ret_window > 0, 1, 0)
                sig_series = pd.Series(sig_array, index=prices.index).shift(1).fillna(0)

                strat_ret = sig_series * daily_returns
                if self.equal_scoring:
                    strat_ret = strat_ret.iloc[warmup + 1:]

                if len(strat_ret) > 1:
                    ann_ret = strat_ret.mean() * 365
                    ann_vol = strat_ret.std() * np.sqrt(365)
                    sharpe = ann_ret / ann_vol if ann_vol != 0 else 0

                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_window = w

            current_ret = (prices.iloc[-1] - prices.iloc[-(best_window + 1)]) / prices.iloc[-(best_window + 1)]
            signals[ticker] = 1 if current_ret > 0 else 0

            recent_vol = daily_returns.tail(30).std()
            inv_vols[ticker] = 1.0 / recent_vol if recent_vol > 0 else 0.0

        total_inv_vol = sum(inv_vols[t] for t in signals if signals[t] > 0)

        for ticker in self.tickers:
            if ticker in stopped_today:
                continue

            base_asset = ticker.split('/')[0]

            if signals.get(ticker, 0) > 0 and total_inv_vol > 0:
                weight = inv_vols[ticker] / total_inv_vol
                dollar_allocation = self.capital * weight
                current_price = self.get_current_price(ticker)

                target_positions[base_asset] = dollar_allocation / current_price
            else:
                target_positions[base_asset] = 0.0

        self.trade_to_target(target_positions, route=True)


if __name__ == "__main__":
    tickers_list = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']
    test_windows_list = [7, 14, 21, 30, 60, 90]
    initial_capital = 100000

    original = dict(peak_daily=False, no_same_day_rebuy=False, throttle_fix=False, equal_scoring=False)
    variants = {
        '1. Original v1': original,
        '2. + peak stored daily': {**original, 'peak_daily': True},
        '3. + no same-day rebuy': {**original, 'no_same_day_rebuy': True},
        '4. + 30-day throttle': {**original, 'throttle_fix': True},
        '5. + equal-period scoring': {**original, 'equal_scoring': True},
        '6. All four changes': {},
    }

    rows = {}
    for i, (label, flags) in enumerate(variants.items(), start=1):
        print(f"Running {label} ...")
        result = WFO_Compare.run_backtest(
            start_ts='20220101',
            freq='1d',
            name=f'WFO_Compare_{i}',
            tickers=tickers_list,
            test_windows=test_windows_list,
            capital=initial_capital,
            stop_loss_pct=0.15,
            taker_fee=26e-4,
            maker_fee=16e-4,
            slip=10e-4,
            **flags
        )
        table = evaluate(result.pos_pnl, initial_capital, tickers_list, plot=False, verbose=False)
        row = table['Strategy'].copy()
        row['Stops Fired'] = WFO_Compare.stop_count
        rows[label] = row
        if i == 1:
            rows['BTC Buy & Hold'] = table['BTC Buy & Hold']

    summary = pd.DataFrame(rows).T
    cols = ['Total Return', 'Ann. Return', 'Ann. Volatility', 'Sharpe', 'Max Drawdown',
            'Ann. Alpha vs BTC', 'Stops Fired']
    print("\n--- Strategy versions compared (same evaluation for all) ---")
    print(summary[cols].to_string(float_format=lambda x: f"{x:.4f}", na_rep=""))
