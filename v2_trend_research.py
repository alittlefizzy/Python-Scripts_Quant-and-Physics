"""Strategy v2: ensemble trend-following with volatility targeting.

Design changes from v1, each aimed at a weakness the robustness sweep exposed:
  * No "best window" selection. v1 picked the lookback with the best trailing Sharpe,
    which chases noise. v2 averages the trend signal across ALL lookbacks.
  * No calendar rebalance. v1's result hinged on which days it happened to trade.
    v2 checks every day and trades only when a position drifts outside a band.
  * Volatility targeting. Each asset's size is scaled so it contributes similar risk,
    and total exposure never exceeds account equity (no borrowing).
  * Sized from current equity, so losses shrink future bets and the account can't go
    below zero.
  * No stop-loss: the working stop cut v1's Sharpe; vol targeting manages risk instead.

Research discipline:
  * IN-SAMPLE (2022-2024) is the only period used to judge and tune.
  * OUT-OF-SAMPLE (2025 onwards) is reported only when RUN_OUT_OF_SAMPLE = True.
    Decide the final settings BEFORE switching it on, and switch it on once.
Keep this file in the same folder as performance_report.py.
"""
import numpy as np
import pandas as pd
import yfinance as yf
from twsq.alpha import Alpha

from performance_report import to_daily_index, twsq_daily_index, _buy_hold_stats

RUN_OUT_OF_SAMPLE = True           # settings frozen at DEFAULT on 14 Oct 2026; run once
IN_SAMPLE_END = '2024-12-31'

# Settings declared in advance as the default; the grid only tests their robustness.
DEFAULT = dict(band=0.10, vol_window=30)


class Ensemble_Trend(Alpha):

    def prepare(self, tickers, lookbacks, capital, target_vol=0.40, vol_window=30, band=0.10):
        self.tickers = tickers
        self.lookbacks = lookbacks
        self.capital = capital          # starting equity
        self.target_vol = target_vol    # annualised vol each asset is scaled to
        self.vol_window = vol_window    # days used to estimate each asset's vol
        self.band = band                # trade only if a position is this far off target

    def _price(self, ticker):
        # None when the exchange has no data for this asset yet (e.g. before it listed).
        try:
            price = self.get_current_price(ticker)
        except Exception:
            return None
        return price if price is not None and np.isfinite(price) and price > 0 else None

    def _equity(self, positions, prices):
        # TWSQ's account starts at zero and borrows USDT, so equity = start + net value.
        net = positions.get('USDT', 0.0)
        for ticker in self.tickers:
            qty = positions.get(ticker.split('/')[0], 0.0)
            if qty and prices[ticker] is not None:
                net += qty * prices[ticker]
        return self.capital + net

    def rebalance(self):
        positions = self.get_pos()
        prices = {t: self._price(t) for t in self.tickers}
        equity = self._equity(positions, prices)
        if equity <= 0:
            return

        need = max(max(self.lookbacks), self.vol_window) + 1
        raw_weights = {}
        for ticker in self.tickers:
            bars = self.get_lastn_bars(ticker, need + 5, '1d') if prices[ticker] is not None else None
            if bars is None or len(bars) < need:
                raw_weights[ticker] = 0.0
                continue
            close = bars['close']

            # Trend strength in [0, 1]: share of lookbacks with a positive return (long only).
            votes = [1.0 if close.iloc[-1] > close.iloc[-(lb + 1)] else 0.0 for lb in self.lookbacks]
            strength = float(np.mean(votes))

            daily_vol = close.pct_change().tail(self.vol_window).std()
            ann_vol = daily_vol * np.sqrt(365) if daily_vol > 0 else np.inf
            raw_weights[ticker] = strength * self.target_vol / ann_vol / len(self.tickers)

        # Never hold more than 100% of equity in total.
        gross = sum(raw_weights.values())
        scale = 1.0 / gross if gross > 1.0 else 1.0

        target_positions = {}
        for ticker in self.tickers:
            base = ticker.split('/')[0]
            current_qty = positions.get(base, 0.0)
            if prices[ticker] is None:
                continue
            target_value = raw_weights[ticker] * scale * equity
            current_value = current_qty * prices[ticker]

            # No-trade band: only trade when the gap is a meaningful share of the target
            # (or the target is zero and we still hold some).
            gap = abs(target_value - current_value)
            reference = max(target_value, current_value)
            if reference > 0 and gap / reference > self.band:
                target_positions[base] = target_value / prices[ticker]
            else:
                target_positions[base] = current_qty

        self.trade_to_target(target_positions, route=True)


def _period_returns(df_pnl, capital, tickers, start, end):
    """Daily returns over [start, end]: strategy and BTC on common dates, plus the basket."""
    port_val = df_pnl['port_val'].copy()
    port_val.index = twsq_daily_index(port_val.index)
    port_val = port_val[~port_val.index.duplicated(keep='last')]
    equity = capital + port_val
    strat = equity.pct_change()
    strat.iloc[0] = equity.iloc[0] / capital - 1

    dl_start = strat.index.min().strftime('%Y-%m-%d')
    dl_end = (strat.index.max() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    btc = yf.download("BTC-USD", start=dl_start, end=dl_end, progress=False)['Close']
    if isinstance(btc, pd.DataFrame):
        btc = btc.iloc[:, 0]
    btc_ret = btc.pct_change().fillna(0)
    btc_ret.index = to_daily_index(btc_ret.index)
    basket = yf.download([t.replace('/', '-') for t in tickers], start=dl_start, end=dl_end,
                         progress=False)['Close']

    aligned = pd.concat([strat, btc_ret], axis=1, keys=['Strategy', 'BTC']).dropna()
    aligned = aligned.loc[start:end]
    basket = basket.copy()
    basket.index = to_daily_index(basket.index)
    basket = basket.loc[start:end]
    basket_ret = (basket / basket.iloc[0]).mean(axis=1).pct_change().fillna(0)
    return aligned['Strategy'], aligned['BTC'], basket_ret


def period_stats(df_pnl, capital, tickers, start, end):
    """Compounding-equity metrics for the strategy, BTC and the basket over [start, end]."""
    s, b, k = _period_returns(df_pnl, capital, tickers, start, end)
    out = {}
    for name, series in [('Strategy', s), ('BTC Buy & Hold', b), ('Basket Buy & Hold', k)]:
        out[name], _ = _buy_hold_stats(series)
    beta = s.cov(b) / b.var() if b.var() > 0 else 0
    out['Strategy']['Beta vs BTC'] = beta
    out['Strategy']['Ann. Alpha vs BTC'] = (s.mean() - beta * b.mean()) * 365
    return pd.DataFrame(out)


# Validated categorical colours (blue, orange, aqua); line style is a second cue so the
# series stay distinguishable in greyscale or for colour-blind readers.
SERIES_STYLE = {
    'Strategy v2':       dict(color='#2a78d6', linestyle='-',  linewidth=2.2, zorder=3),
    'BTC buy & hold':    dict(color='#eb6834', linestyle='--', linewidth=1.6, zorder=2),
    'Basket buy & hold': dict(color='#1baf7a', linestyle=':',  linewidth=1.9, zorder=2),
}
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e4e3df'


def plot_growth(df_pnl, capital, tickers, start, end, title, split=None, save_as=None):
    """Growth of $1 for the strategy, BTC and the basket (log scale).

    split: a date marking where the unseen test period begins; the test period is shaded
    and the legend omits whole-period stats, which would blend the two periods.
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

    s, b, k = _period_returns(df_pnl, capital, tickers, start, end)
    curves = {'Strategy v2': s, 'BTC buy & hold': b, 'Basket buy & hold': k}

    fig, ax = plt.subplots(figsize=(11, 6))
    fig.patch.set_facecolor('white')
    ends = {}
    for name, rets in curves.items():
        growth = (1 + rets).cumprod()
        stats, _ = _buy_hold_stats(rets)
        label = name if split else (f"{name}   Sharpe {stats['Sharpe']:.2f}, "
                                    f"worst fall {stats['Max Drawdown']:.0%}")
        ax.plot(growth.index, growth.values, label=label, **SERIES_STYLE[name])
        ends[name] = (growth.index[-1], growth.iloc[-1])

    ax.set_yscale('log')
    ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5)))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y:g}"))
    ax.axhline(1.0, color=MUTED, linewidth=0.8, zorder=1)

    if split:
        split_ts = pd.Timestamp(split)
        ax.axvspan(split_ts, max(t for t, _ in ends.values()), color='#f1f0ec', zorder=0)
        ax.axvline(split_ts, color=MUTED, linewidth=0.8, linestyle='-', zorder=1)
        ax.text(split_ts, 1.01, '  Unseen test period', transform=ax.get_xaxis_transform(),
                color=MUTED, fontsize=9, va='bottom', ha='left')
        ax.text(split_ts, 1.01, 'Development period  ', transform=ax.get_xaxis_transform(),
                color=MUTED, fontsize=9, va='bottom', ha='right')

    # Direct labels at the line ends, nudged apart (in log space) so they never overlap.
    from matplotlib.transforms import offset_copy
    label_transform = offset_copy(ax.transData, fig=fig, x=8, y=0, units='points')
    last_log_y = None
    for name, (t, y) in sorted(ends.items(), key=lambda kv: kv[1][1]):
        log_y = np.log10(y)
        if last_log_y is not None and log_y - last_log_y < 0.06:
            log_y = last_log_y + 0.06
        last_log_y = log_y
        ax.text(t, 10 ** log_y, f"{name.split(' ')[0]}  ${y:.2f}", transform=label_transform,
                va='center', ha='left', fontsize=9, color=INK, clip_on=False)

    ax.set_title(title, loc='left', fontsize=13, color=INK, pad=18)
    ax.set_ylabel('Growth of $1 (log scale)', color=MUTED)
    ax.grid(True, which='major', color=GRID, linewidth=0.8)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED)
    ax.legend(loc='upper left', frameon=False, fontsize=9, labelcolor=INK)
    ax.margins(x=0.01)
    fig.subplots_adjust(right=0.88)

    if save_as:
        fig.savefig(save_as, dpi=150, bbox_inches='tight')
        print(f"Chart saved to {save_as}")
    plt.show()


def run(run_name, capital, tickers, lookbacks, start_ts='20220101', **settings):
    return Ensemble_Trend.run_backtest(
        start_ts=start_ts,
        freq='1d',
        name=run_name,
        tickers=tickers,
        lookbacks=lookbacks,
        capital=capital,
        taker_fee=26e-4,
        maker_fee=16e-4,
        slip=10e-4,
        **settings
    )


if __name__ == "__main__":
    tickers_list = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']
    lookbacks = [7, 14, 21, 30, 60, 90]
    initial_capital = 100000

    # Robustness grid around the declared default (in-sample only).
    grid = [dict(band=b, vol_window=v) for b in [0.05, 0.10, 0.20, 0.30] for v in [20, 30, 60]]
    rows = []
    btc_sharpe = None
    for i, settings in enumerate(grid, start=1):
        print(f"Run {i}/{len(grid)}: {settings}")
        result = run(f'Ensemble_Trend_{i}', initial_capital, tickers_list, lookbacks, **settings)
        table = period_stats(result.pos_pnl, initial_capital, tickers_list, '2022-01-01', IN_SAMPLE_END)
        btc_sharpe = table.loc['Sharpe', 'BTC Buy & Hold']
        s = table['Strategy']
        rows.append({**settings, 'Total Return': s['Total Return'], 'Sharpe': s['Sharpe'],
                     'Max Drawdown': s['Max Drawdown'], 'Beats BTC Sharpe': s['Sharpe'] > btc_sharpe})

    df = pd.DataFrame(rows)
    print(f"\n=== IN-SAMPLE 2022-2024 robustness grid (BTC Sharpe = {btc_sharpe:.4f}) ===")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(f"\nRuns beating BTC on Sharpe: {int(df['Beats BTC Sharpe'].sum())} of {len(df)}")
    print(f"Median Sharpe: {df['Sharpe'].median():.3f}   (BTC: {btc_sharpe:.3f})")

    print(f"\n=== IN-SAMPLE 2022-2024, default settings {DEFAULT} ===")
    default_result = run('Ensemble_Trend_default', initial_capital, tickers_list, lookbacks, **DEFAULT)
    print(period_stats(default_result.pos_pnl, initial_capital, tickers_list, '2022-01-01', IN_SAMPLE_END)
          .to_string(float_format=lambda x: f"{x:.4f}", na_rep=""))

    if RUN_OUT_OF_SAMPLE:
        print(f"\n=== OUT-OF-SAMPLE 2025 onwards, default settings {DEFAULT} ===")
        print(period_stats(default_result.pos_pnl, initial_capital, tickers_list, '2025-01-01', None)
              .to_string(float_format=lambda x: f"{x:.4f}", na_rep=""))
    else:
        print("\nOut-of-sample results hidden. Freeze the settings first, then set RUN_OUT_OF_SAMPLE = True once.")

    if RUN_OUT_OF_SAMPLE:
        plot_growth(default_result.pos_pnl, initial_capital, tickers_list, '2022-01-01', None,
                    'Strategy v2 vs BTC vs equal-weight basket, 2022 to 2026',
                    split='2025-01-01', save_as='v2_growth_2022_2026.png')
    else:
        plot_growth(default_result.pos_pnl, initial_capital, tickers_list, '2022-01-01', IN_SAMPLE_END,
                    'Strategy v2 vs BTC vs equal-weight basket, 2022 to 2024 (development period)',
                    save_as='v2_growth_2022_2024.png')
