import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from twsq.alpha import Alpha

class WFO_Dynamic_Mom(Alpha):
    
    def prepare(self, tickers, test_windows, capital, rebalance_days=30, stop_loss_pct=0.15):
        self.tickers = tickers
        self.test_windows = test_windows
        self.capital = capital
        self.rebalance_days = rebalance_days
        self.days_since_rebalance = rebalance_days 
        self.stop_loss_pct = stop_loss_pct
        self.high_water_marks = {}
        
    def rebalance(self):
        # 1. Daily Crash Protection (Trailing Stop-Loss)
        current_positions = self.get_pos()
        
        for ticker in self.tickers:
            base_asset = ticker.split('/')[0]
            qty = current_positions.get(base_asset, 0)
            
            if qty > 0:
                current_price = self.get_current_price(ticker)
                peak_price = self.high_water_marks.get(ticker, current_price)
                
                if current_price > peak_price:
                    self.high_water_marks[ticker] = current_price
                    
                if current_price <= peak_price * (1 - self.stop_loss_pct):
                    self.create_order(ticker, qty, 'sell', route=True)
                    self.high_water_marks[ticker] = 0.0
                    
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


if __name__ == "__main__":
    tickers_list = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']
    test_windows_list = [7, 14, 21, 30, 60, 90]
    initial_capital = 100000
    
    print("Executing TWSQ Backtest...")
    
    # 1. Execute Backtest
    result = WFO_Dynamic_Mom.run_backtest(
        start_ts='20220101',
        freq='1d',
        name='WFO_Dynamic_Mom_Backtest',
        tickers=tickers_list,
        test_windows=test_windows_list,
        capital=initial_capital,
        stop_loss_pct=0.15,
        taker_fee=26e-4, 
        maker_fee=16e-4, 
        slip=10e-4
    )
    
    print(f"Backtest complete. Results stored in MyTWSQ/alphas/WFO_Dynamic_Mom_Backtest/backtest")
    
    # 2. Extract Strategy Returns
    df_pnl = result.pos_pnl
    
    equity = initial_capital + df_pnl['port_val']
    strat_returns = equity.pct_change().fillna(0)
    strat_returns.index = pd.to_datetime(strat_returns.index)

    # 3. Fetch Benchmark Data
    print("Fetching benchmark data for evaluation...")
    
    # 3a. BTC Benchmark
    btc_data = yf.download("BTC-USD", start="2022-01-01", end="2026-01-01", progress=False)['Close']
    if isinstance(btc_data, pd.DataFrame):
        btc_data = btc_data.iloc[:, 0]
        
    btc_returns = btc_data.pct_change().fillna(0)
    btc_returns.index = pd.to_datetime(btc_returns.index).tz_localize(None)

    # 3b. Equal-Weight Buy & Hold Basket
    yf_tickers = [t.replace('/', '-') for t in tickers_list]
    basket_data = yf.download(yf_tickers, start="2022-01-01", end="2026-01-01", progress=False)['Close']
    basket_returns = basket_data.pct_change().fillna(0)
    basket_returns.index = pd.to_datetime(basket_returns.index).tz_localize(None)
    
    # Calculate equal-weighted initial allocation drifting with price
    basket_cum = (1 + basket_returns).cumprod()
    bh_cum_raw = basket_cum.mean(axis=1)

    # 4. Align Strategy and Benchmark data
    aligned_data = pd.concat([strat_returns, btc_returns, bh_cum_raw], axis=1).dropna()
    aligned_data.columns = ['Strategy', 'BTC_Benchmark', 'Buy_Hold_Raw']
    
    strat = aligned_data['Strategy']
    bench = aligned_data['BTC_Benchmark']
    bh_aligned = aligned_data['Buy_Hold_Raw']
    
    # Normalize basket to 1.0 at the aligned starting index
    bh_cum = bh_aligned / bh_aligned.iloc[0]

    # 5. Calculate Metrics
    total_days = len(strat)
    cum_return = (1 + strat).prod() - 1
    ann_return = (1 + cum_return) ** (365 / total_days) - 1 if total_days > 0 else 0
    ann_vol = strat.std() * np.sqrt(365)
    sharpe = ann_return / ann_vol if ann_vol != 0 else 0

    cum_value = (1 + strat).cumprod()
    max_drawdown = ((cum_value - cum_value.cummax()) / cum_value.cummax()).min()

    covariance = strat.cov(bench)
    benchmark_var = bench.var()
    beta = covariance / benchmark_var if benchmark_var != 0 else 0
    alpha_ann = (strat.mean() - beta * bench.mean()) * 365

    # 6. Print Metrics
    print("\n--- TWSQ Backtest Performance vs BTC Benchmark ---")
    print(f"Total Net PnL: ${df_pnl['port_val'].iloc[-1]:,.2f}")
    print(f"Annualized Return: {ann_return:.4f}")
    print(f"Annualized Volatility: {ann_vol:.4f}")
    print(f"Sharpe Ratio: {sharpe:.4f}")
    print(f"Max Drawdown: {max_drawdown:.4f}")
    print(f"Beta: {beta:.4f}")
    print(f"Annualized Alpha: {alpha_ann:.4f}")

    # 7. Plot Comparison
    cum_bench = (1 + bench).cumprod()
    
    plt.figure(figsize=(10, 6))
    plt.plot(cum_value.index, cum_value, label="WFO Dynamic Mom (TWSQ)", color="blue")
    plt.plot(cum_bench.index, cum_bench, label="BTC Benchmark", color="gray", linestyle="--")
    plt.plot(bh_cum.index, bh_cum, label="Buy & Hold Basket", color="orange", linestyle=":")
    plt.title("WFO Cumulative Returns (2022-2026)")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Growth")
    plt.legend()
    plt.grid(True)
    plt.show()