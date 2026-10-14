"""Is the strategy's edge robust, or an artefact of one parameter choice?

Re-runs the original strategy logic (no stop-loss) across a range of rebalance
intervals and both window-scoring choices, and compares each run's Sharpe ratio
with BTC buy-and-hold. A real edge should beat BTC across most of the grid, not
only at one setting. Keep this file in the same folder as
v1_audit_fix_by_fix.py and performance_report.py.
"""
import pandas as pd

from v1_audit_fix_by_fix import WFO_Compare
from performance_report import evaluate

if __name__ == "__main__":
    tickers_list = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'XRP/USD', 'ADA/USD']
    test_windows_list = [7, 14, 21, 30, 60, 90]
    initial_capital = 100000

    rebalance_grid = [20, 25, 28, 29, 30, 31, 32, 33, 35, 40]
    scoring_grid = {'full 365-day scoring': False, 'equal-period scoring': True}

    rows = []
    btc_sharpe = None
    run = 0
    for scoring_label, equal_scoring in scoring_grid.items():
        for days in rebalance_grid:
            run += 1
            print(f"Run {run}/{len(rebalance_grid) * len(scoring_grid)}: every {days} days, {scoring_label}")
            result = WFO_Compare.run_backtest(
                start_ts='20220101',
                freq='1d',
                name=f'WFO_Sweep_{run}',
                tickers=tickers_list,
                test_windows=test_windows_list,
                capital=initial_capital,
                rebalance_days=days,
                stop_loss_pct=1.0,        # 100% stop = stop-loss switched off
                peak_daily=True,
                no_same_day_rebuy=True,
                throttle_fix=True,        # rebalances exactly every `days` bars
                equal_scoring=equal_scoring,
                taker_fee=26e-4,
                maker_fee=16e-4,
                slip=10e-4
            )
            table = evaluate(result.pos_pnl, initial_capital, tickers_list, plot=False, verbose=False)
            btc_sharpe = table.loc['Sharpe', 'BTC Buy & Hold']
            s = table['Strategy']
            rows.append({'Scoring': scoring_label, 'Rebalance (days)': days,
                         'Total Return': s['Total Return'], 'Sharpe': s['Sharpe'],
                         'Max Drawdown': s['Max Drawdown'], 'Beats BTC Sharpe': s['Sharpe'] > btc_sharpe})

    df = pd.DataFrame(rows)
    print(f"\n--- Robustness sweep (BTC buy & hold Sharpe = {btc_sharpe:.4f}) ---")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    print("\nSharpe ratio by setting:")
    print(df.pivot(index='Rebalance (days)', columns='Scoring', values='Sharpe')
            .to_string(float_format=lambda x: f"{x:.3f}"))

    print(f"\nRuns beating BTC on Sharpe: {int(df['Beats BTC Sharpe'].sum())} of {len(df)}")
    print(f"Median Sharpe: {df['Sharpe'].median():.3f}   (BTC: {btc_sharpe:.3f})")
