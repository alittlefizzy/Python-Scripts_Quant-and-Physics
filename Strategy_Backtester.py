# -*- coding: utf-8 -*-
import yfinance as yf
import numpy as np
import pandas as pd

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

def generate_volatility_pairs_signals(prices_A, prices_B, window=30, z_threshold=1.5, vol_lookback=30, vol_ma_window=90):
    # 1. Unrestricted Pairs Logic
    ratio = prices_A / prices_B
    ratio_ma = ratio.rolling(window=window).mean()
    ratio_std = ratio.rolling(window=window).std()
    z_score = (ratio - ratio_ma) / ratio_std
    
    sig_A_base = np.where(z_score > z_threshold, -1, np.where(z_score < -z_threshold, 1, 0))
    sig_B_base = np.where(z_score > z_threshold, 1, np.where(z_score < -z_threshold, -1, 0))
    
    # 2. Macro Volatility Filter
    returns_A = prices_A.pct_change(1)
    rolling_vol = returns_A.rolling(window=vol_lookback).std()
    vol_ma = rolling_vol.rolling(window=vol_ma_window).mean()
    
    high_vol_condition = rolling_vol > vol_ma
    
    # 3. Apply Filter
    sig_A_final = np.where(high_vol_condition, sig_A_base, 0)
    sig_B_final = np.where(high_vol_condition, sig_B_base, 0)
    
    sig_A = pd.Series(sig_A_final, index=prices_A.index, name="Pairs_A")
    sig_B = pd.Series(sig_B_final, index=prices_B.index, name="Pairs_B")
    
    # Clean initial NaN periods required to calculate the 90-day moving average of volatility
    sig_A.loc[vol_ma.isna()] = 0
    sig_B.loc[vol_ma.isna()] = 0
    
    return sig_A, sig_B

def generate_true_momentum_signal(prices, window):
    return_window = prices.pct_change(periods=window)
    signal_array = np.where(return_window > 0, 1, -1)
    signals = pd.Series(signal_array, index=prices.index, name=f"Mom_{window}")
    signals.loc[return_window.isna()] = 0
    return signals


# ---------------- Execution Block ----------------
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

tickers = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"]
# Map each asset to its optimal momentum horizon based on prior test results
windows = {
    "BTC-USD": 30, 
    "ETH-USD": 60, 
    "SOL-USD": 7, 
    "XRP-USD": 14, 
    "ADA-USD": 30
}

print("Fetching data from 2022-01-01 to 2025-01-01...")
data_dict = {}
for ticker in tickers:
    prices, _ = fetch_crypto_data(ticker, "2022-01-01", "2025-01-01")
    data_dict[ticker] = prices

# Align all data to a common index to prevent length mismatches
df_prices = pd.DataFrame(data_dict).dropna()

net_returns_dict = {}
inv_vol_dict = {}
bench_returns_dict = {}

for ticker in tickers:
    prices = df_prices[ticker]
    window = windows[ticker]
    
    # Generate Signals & Calculate Returns
    signals = generate_true_momentum_signal(prices, window=window)
    strat_returns = calculate_strategy_returns(prices, signals)
    net_ret = calculate_net_returns(strat_returns, signals.shift(1).fillna(0), execution_cost_bps=20)
    net_returns_dict[ticker] = net_ret
    
    # Calculate Volatility for Weighting
    bench_ret = prices.pct_change(1).fillna(0)
    bench_returns_dict[ticker] = bench_ret
    
    vol = bench_ret.rolling(window=30).std()
    inv_vol = 1 / vol
    inv_vol_dict[ticker] = inv_vol

# Calculate Dynamic Inverse Volatility Weights
df_inv_vol = pd.DataFrame(inv_vol_dict)
total_inv_vol = df_inv_vol.sum(axis=1)

df_weights = df_inv_vol.div(total_inv_vol, axis=0)

# Shift weights by 1 day to prevent look-ahead bias; initialize early days to equal weight (20% each)
df_weights = df_weights.shift(1).fillna(1.0 / len(tickers))

# Calculate Portfolio Net Returns
df_net_returns = pd.DataFrame(net_returns_dict)
portfolio_net_returns = (df_net_returns * df_weights).sum(axis=1)

# Calculate Benchmark Returns (Equal Weight Buy-and-Hold)
df_bench_returns = pd.DataFrame(bench_returns_dict)
portfolio_benchmark = (df_bench_returns * (1.0 / len(tickers))).sum(axis=1)

# Evaluate Performance
portfolio_metrics = evaluate_performance(portfolio_net_returns, portfolio_benchmark)
portfolio_metrics.name = "Vol-Weighted Mom (5 Assets)"

bench_metrics = evaluate_performance(portfolio_benchmark, portfolio_benchmark)
bench_metrics.name = "Equal-Weight Benchmark"

comparison = pd.concat([portfolio_metrics, bench_metrics], axis=1)
print(comparison)


import matplotlib.pyplot as plt

# Calculate cumulative returns
cum_strategy = (1 + portfolio_net_returns).cumprod()
cum_benchmark = (1 + portfolio_benchmark).cumprod()
cum_btc = (1 + df_bench_returns["BTC-USD"]).cumprod()

# Generate the line graph
plt.figure(figsize=(10, 6))
plt.plot(cum_strategy, label="Vol-Weighted Mom (5 Assets)", color="blue")
plt.plot(cum_benchmark, label="5-Asset Buy-and-Hold", color="orange")
plt.plot(cum_btc, label="BTC Buy-and-Hold", color="gray", linestyle="--")

plt.title("Strategy vs Benchmarks Cumulative Returns (2022-2025)")
plt.xlabel("Date")
plt.ylabel("Cumulative Growth")
plt.legend()
plt.grid(True)
plt.show()
