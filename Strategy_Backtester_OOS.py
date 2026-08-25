# -*- coding: utf-8 -*-
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import MonthBegin

def fetch_crypto_data(ticker, start_date, end_date):
    crypto = yf.Ticker(ticker)
    data = crypto.history(start=start_date, end=end_date)
    return data["Close"], data["Volume"]

def calculate_strategy_returns(prices, signals):
    daily_returns = prices.pct_change(1)
    shifted_signals = signals.shift(1)
    return shifted_signals * daily_returns

def calculate_net_returns(gross_returns, shifted_signals, execution_cost_bps=20):
    turnover = shifted_signals.diff().abs().fillna(0)
    cost_per_trade = execution_cost_bps / 10000
    daily_costs = turnover * cost_per_trade
    return gross_returns - daily_costs

def evaluate_performance(net_returns, benchmark_returns):
    df = pd.concat([net_returns, benchmark_returns], axis=1).dropna()
    df.columns = ['Strategy', 'Benchmark']
    strat = df['Strategy']
    bench = df['Benchmark']
    
    total_days = len(strat)
    if total_days == 0:
        return pd.Series(dtype=float)
        
    cum_return = (1 + strat).prod() - 1
    ann_return = (1 + cum_return) ** (365 / total_days) - 1
    ann_vol = strat.std() * np.sqrt(365)
    sharpe = ann_return / ann_vol if ann_vol != 0 else 0
    
    cum_value = (1 + strat).cumprod()
    max_drawdown = ((cum_value - cum_value.cummax()) / cum_value.cummax()).min()
    
    covariance = strat.cov(bench)
    benchmark_var = bench.var()
    beta = covariance / benchmark_var if benchmark_var != 0 else 0
    alpha_ann = (strat.mean() - beta * bench.mean()) * 365
    
    return pd.Series({
        'Annualized Return': ann_return,
        'Annualized Volatility': ann_vol,
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_drawdown,
        'Beta': beta,
        'Annualized Alpha': alpha_ann
    })

def generate_long_only_momentum_signal(prices, window):
    return_window = prices.pct_change(periods=window)
    signal_array = np.where(return_window > 0, 1, 0)
    signals = pd.Series(signal_array, index=prices.index, name=f"Mom_{window}")
    signals.loc[return_window.isna()] = 0
    return signals

# ---------------- Execution Block ----------------
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

tickers = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"]
test_windows = [7, 14, 21, 30, 60, 90]
lookback_days = 365

print("Fetching full dataset (2021-01-01 to 2025-01-01)...")
# Fetching from 2021 to allow a 365-day lookback for early 2022 trades
data_dict = {}
for ticker in tickers:
    prices, _ = fetch_crypto_data(ticker, "2021-01-01", "2025-01-01")
    data_dict[ticker] = prices

df_prices = pd.DataFrame(data_dict).dropna()
# Strip timezone information to align with pd.date_range
df_prices.index = df_prices.index.tz_localize(None)

trading_months = pd.date_range(start="2022-01-01", end="2024-12-31", freq='MS')

all_portfolio_returns = []
all_benchmark_returns = []

print("Executing Walk-Forward Optimization...")

for month_start in trading_months:
    month_end = month_start + pd.offsets.MonthEnd(1)
    train_start = month_start - pd.Timedelta(days=lookback_days)
    
    # Isolate training data
    df_train = df_prices.loc[train_start:month_start - pd.Timedelta(days=1)]
    df_test = df_prices.loc[month_start:month_end]
    
    if df_train.empty or df_test.empty:
        continue
        
    month_net_returns_dict = {}
    month_inv_vol_dict = {}
    
    for ticker in tickers:
        prices_train = df_train[ticker]
        bench_ret_train = prices_train.pct_change(1).fillna(0)
        
        best_sharpe = -np.inf
        best_window = 30
        
        # Optimize on trailing 365 days
        for w in test_windows:
            sig_train = generate_long_only_momentum_signal(prices_train, window=w)
            strat_ret_train = calculate_strategy_returns(prices_train, sig_train)
            net_ret_train = calculate_net_returns(strat_ret_train, sig_train.shift(1).fillna(0), execution_cost_bps=20)
            metrics = evaluate_performance(net_ret_train, bench_ret_train)
            
            if not metrics.empty and metrics['Sharpe Ratio'] > best_sharpe:
                best_sharpe = metrics['Sharpe Ratio']
                best_window = w
                
        # Execute on current month using optimal window
        # Prepend some data to test set to calculate rolling window accurately
        data_needed = df_prices[ticker].loc[:month_end].tail(len(df_test) + best_window + 1)
        sig_test_full = generate_long_only_momentum_signal(data_needed, window=best_window)
        sig_test = sig_test_full.loc[month_start:month_end]
        
        strat_ret_test = calculate_strategy_returns(df_test[ticker], sig_test)
        net_ret_test = calculate_net_returns(strat_ret_test, sig_test.shift(1).fillna(0), execution_cost_bps=20)
        
        month_net_returns_dict[ticker] = net_ret_test
        
        # Volatility Weighting calculation
        bench_ret_test = df_test[ticker].pct_change(1).fillna(0)
        vol = data_needed.pct_change(1).rolling(window=30).std().loc[month_start:month_end]
        month_inv_vol_dict[ticker] = 1 / vol

    df_month_returns = pd.DataFrame(month_net_returns_dict)
    df_month_inv_vol = pd.DataFrame(month_inv_vol_dict)
    
    total_inv_vol = df_month_inv_vol.sum(axis=1)
    df_weights = df_month_inv_vol.div(total_inv_vol, axis=0).shift(1).fillna(1.0 / len(tickers))
    
    portfolio_net = (df_month_returns * df_weights).sum(axis=1)
    bench_net = (df_test.pct_change(1).fillna(0) * (1.0 / len(tickers))).sum(axis=1)
    
    all_portfolio_returns.append(portfolio_net)
    all_benchmark_returns.append(bench_net)

final_strategy_returns = pd.concat(all_portfolio_returns)
final_benchmark_returns = pd.concat(all_benchmark_returns)
btc_benchmark = df_prices["BTC-USD"].pct_change(1).loc[final_strategy_returns.index]

metrics_strat = evaluate_performance(final_strategy_returns, final_benchmark_returns)
metrics_strat.name = "WFO Dynamic Mom"

metrics_bench = evaluate_performance(final_benchmark_returns, final_benchmark_returns)
metrics_bench.name = "5-Asset Bench"

comparison = pd.concat([metrics_strat, metrics_bench], axis=1)
print("\n--- Walk-Forward Optimization Results (2022-2025) ---")
print(comparison)

cum_strat = (1 + final_strategy_returns).cumprod()
cum_bench = (1 + final_benchmark_returns).cumprod()
cum_btc = (1 + btc_benchmark).cumprod()

plt.figure(figsize=(10, 6))
plt.plot(cum_strat, label="WFO Dynamic Mom", color="blue")
plt.plot(cum_bench, label="5-Asset Bench", color="orange")
plt.plot(cum_btc, label="BTC Bench", color="gray", linestyle="--")
plt.title("WFO Cumulative Returns (2022-2025)")
plt.xlabel("Date")
plt.ylabel("Cumulative Growth")
plt.legend()
plt.grid(True)
plt.show()