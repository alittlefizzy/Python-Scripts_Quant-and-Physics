import json
import os

import numpy as np
import pandas as pd
from twsq.alpha import Alpha

# Peak prices are saved here so the trailing stop survives a restart of the live trader.
HWM_FILE = 'high_water_marks_live.json'


class WFO_Dynamic_Mom(Alpha):

    def prepare(self, tickers, test_windows, capital, rebalance_days=30, stop_loss_pct=0.15):
        self.tickers = tickers
        self.test_windows = test_windows
        self.capital = capital
        self.rebalance_days = rebalance_days
        self.days_since_rebalance = rebalance_days
        self.stop_loss_pct = stop_loss_pct
        self.high_water_marks = self._load_hwm()

    # --- Persistence helpers -------------------------------------------------

    def _load_hwm(self):
        if os.path.exists(HWM_FILE):
            try:
                with open(HWM_FILE, 'r') as f:
                    return {k: float(v) for k, v in json.load(f).items()}
            except (json.JSONDecodeError, OSError, ValueError):
                pass
        return {}

    def _save_hwm(self):
        try:
            with open(HWM_FILE, 'w') as f:
                json.dump(self.high_water_marks, f)
        except OSError:
            pass

    # --- Strategy --------------------------------------------------------------

    def rebalance(self):
        # 1. Daily Crash Protection (Trailing Stop-Loss)
        current_positions = self.get_pos()

        for ticker in self.tickers:
            base_asset = ticker.split('/')[0]
            qty = current_positions.get(base_asset, 0)

            if qty > 0:
                current_price = self.get_current_price(ticker)
                peak_price = self.high_water_marks.get(ticker, current_price)

                # A peak of 0.0 means the last position was stopped out; start a fresh peak.
                if peak_price <= 0:
                    peak_price = current_price

                if current_price > peak_price:
                    peak_price = current_price
                self.high_water_marks[ticker] = peak_price

                if current_price <= peak_price * (1 - self.stop_loss_pct):
                    self.create_order(ticker, qty, 'sell', route=True)
                    self.high_water_marks[ticker] = 0.0

        self._save_hwm()

        # 2. Monthly Rebalance Throttle
        if self.days_since_rebalance < self.rebalance_days:
            self.days_since_rebalance += 1
            return

        self.days_since_rebalance = 0
        target_positions = {}
        inv_vols = {}
        signals = {}

        # 3. Optimization and Signal Generation
        for ticker in self.tickers:
            bars = self.get_lastn_bars(ticker, 365, '1d')
            if bars is None or len(bars) < max(self.test_windows) + 30:
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

                total_days = len(strat_ret)
                if total_days > 0:
                    ann_ret = strat_ret.mean() * 365
                    ann_vol = strat_ret.std() * np.sqrt(365)
                    sharpe = ann_ret / ann_vol if ann_vol != 0 else 0

                    if sharpe > best_sharpe:
                        best_sharpe = sharpe
                        best_window = w

            current_ret = (prices.iloc[-1] - prices.iloc[-(best_window+1)]) / prices.iloc[-(best_window+1)]
            signals[ticker] = 1 if current_ret > 0 else 0

            recent_vol = daily_returns.tail(30).std()
            inv_vols[ticker] = 1.0 / recent_vol if recent_vol > 0 else 0.0

        # 4. Capital Allocation and Route Order
        total_inv_vol = sum([inv_vols[t] for t in self.tickers if signals.get(t, 0) > 0])

        for ticker in self.tickers:
            base_asset = ticker.split('/')[0]

            if signals.get(ticker, 0) > 0 and total_inv_vol > 0:
                weight = inv_vols[ticker] / total_inv_vol
                dollar_allocation = self.capital * weight
                current_price = self.get_current_price(ticker)

                target_positions[base_asset] = dollar_allocation / current_price
            else:
                target_positions[base_asset] = 0.0

        self.trade_to_target(target_positions, route=True)

    def on_exit(self):
        self._save_hwm()
        self.cancel_all_orders()


if __name__ == "__main__":
    tickers_list = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']
    test_windows_list = [7, 14, 21, 30, 60, 90]
    initial_capital = 250

    print("Initializing TWSQ Live Trader on Kraken...")

    WFO_Dynamic_Mom.run_live(
        freq='1d',
        name='WFO_Dynamic_Mom_Live',
        tickers=tickers_list,
        test_windows=test_windows_list,
        capital=initial_capital,
        stop_loss_pct=0.15
    )
