"""Shared performance reporting for the trading scripts.

* Date alignment between TWSQ output and Yahoo Finance benchmark prices.
* Buy-and-hold statistics (total return, annualised return and volatility, Sharpe,
  maximum drawdown).
* evaluate(): the report used for Strategy v1, which re-sizes to a fixed amount of
  capital at every rebalance (no compounding).
"""
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt


def to_daily_index(index):
    """Timezone-naive, midnight-normalised dates so series from different sources align."""
    idx = pd.to_datetime(index)
    if idx.tz is not None:
        idx = idx.tz_convert(None)
    return idx.normalize()


def twsq_daily_index(index):
    """TWSQ stamps each day's PnL with the NEXT day's date (a lag test showed the
    strategy's returns line up with BTC's one day earlier). Shift back one day so
    strategy and benchmark returns cover the same day."""
    return to_daily_index(index) - pd.Timedelta(days=1)


def _buy_hold_stats(returns):
    """Metrics for a compounding buy-and-hold series of daily returns."""
    growth = (1 + returns).cumprod()
    return {
        'Total Return': growth.iloc[-1] - 1,
        'Ann. Return': returns.mean() * 365,
        'Ann. Volatility': returns.std() * np.sqrt(365),
        'Sharpe': (returns.mean() * 365) / (returns.std() * np.sqrt(365)) if returns.std() > 0 else 0,
        'Max Drawdown': ((growth - growth.cummax()) / growth.cummax()).min(),
    }, growth


def evaluate(df_pnl, capital, tickers, plot=True, verbose=True):
    """Performance of the backtest against BTC and an equal-weight buy-and-hold basket.

    TWSQ's account starts at zero and borrows USDT to buy, so `port_val` is cumulative
    PnL and `pnl` is each day's PnL. The strategy re-sizes to a fixed `capital` at every
    rebalance (it does not compound), so its daily return is that day's PnL divided by
    `capital`, and its growth curve is 1 + cumulative PnL / capital.
    """
    port_val = df_pnl['port_val'].copy()
    port_val.index = twsq_daily_index(port_val.index)
    port_val = port_val[~port_val.index.duplicated(keep='last')]

    daily_pnl = port_val.diff()
    daily_pnl.iloc[0] = port_val.iloc[0]
    strat = daily_pnl / capital

    start = strat.index.min().strftime('%Y-%m-%d')
    end = (strat.index.max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    btc = yf.download("BTC-USD", start=start, end=end, progress=False)['Close']
    if isinstance(btc, pd.DataFrame):
        btc = btc.iloc[:, 0]
    btc_ret = btc.pct_change().fillna(0)
    btc_ret.index = to_daily_index(btc_ret.index)

    basket = yf.download([t.replace('/', '-') for t in tickers], start=start, end=end, progress=False)['Close']
    basket_growth = (1 + basket.pct_change().fillna(0)).cumprod().mean(axis=1)  # equal weight, drifting
    basket_ret = basket_growth.pct_change().fillna(0)
    basket_ret.index = to_daily_index(basket_ret.index)

    aligned = pd.concat([strat, btc_ret, basket_ret], axis=1, keys=['Strategy', 'BTC', 'Basket']).dropna()
    s, b, k = aligned['Strategy'], aligned['BTC'], aligned['Basket']

    # Strategy metrics (fixed notional: additive PnL)
    pnl_path = (s * capital).cumsum()
    equity = capital + pnl_path
    strat_curve = equity / capital
    ann_vol = s.std() * np.sqrt(365)
    strat_stats = {
        'Total Return': pnl_path.iloc[-1] / capital,
        'Ann. Return': s.mean() * 365,
        'Ann. Volatility': ann_vol,
        'Sharpe': (s.mean() * 365) / ann_vol if ann_vol > 0 else 0,
        # Peak-to-trough fall in PnL, as a fraction of the capital deployed.
        'Max Drawdown': (pnl_path - pnl_path.cummax()).min() / capital,
    }
    beta = s.cov(b) / b.var() if b.var() > 0 else 0
    strat_stats['Beta vs BTC'] = beta
    strat_stats['Ann. Alpha vs BTC'] = (s.mean() - beta * b.mean()) * 365

    btc_stats, btc_curve = _buy_hold_stats(b)
    basket_stats, basket_curve = _buy_hold_stats(k)

    table = pd.DataFrame({'Strategy': strat_stats, 'BTC Buy & Hold': btc_stats,
                          'Basket Buy & Hold': basket_stats})

    if verbose:
        print(f"\nPeriod: {s.index.min().date()} to {s.index.max().date()} ({len(s)} days)")
        print(f"Total Net PnL: ${pnl_path.iloc[-1]:,.2f} on ${capital:,.0f} deployed")
        print(table.to_string(float_format=lambda x: f"{x:.4f}", na_rep=""))

    if plot:
        plt.figure(figsize=(10, 6))
        plt.plot(strat_curve.index, strat_curve, label="WFO Dynamic Mom (TWSQ)", color="blue")
        plt.plot(btc_curve.index, btc_curve, label="BTC Buy & Hold", color="gray", linestyle="--")
        plt.plot(basket_curve.index, basket_curve, label="Basket Buy & Hold", color="orange", linestyle=":")
        plt.title(f"WFO Cumulative Returns ({s.index.min().year}-{s.index.max().year})")
        plt.xlabel("Date")
        plt.ylabel("Growth of $1")
        plt.legend()
        plt.grid(True)
        plt.show()

    return table
