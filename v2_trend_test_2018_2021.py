"""Second independent test of Strategy v2, on data never used: 2018 to 2021.

The strategy and its settings are frozen exactly as in v2_trend_research.py
(band = 10%, 30-day volatility window). Nothing here may be tuned.

Declared before running:
  * PASS if the strategy's Sharpe beats BTC buy-and-hold over the whole test period.
  * The test period starts once the strategy has its 91 days of warm-up data, so it is
    never credited with sitting in cash through a crash it could not have traded.
  * Bear (2018-19) and bull (2020-21) sub-periods are reported for information only.
SOL is left out because it only started trading in 2020.
Keep this file in the same folder as v2_trend_research.py and performance_report.py.
"""
import pandas as pd

from performance_report import twsq_daily_index
from v2_trend_research import DEFAULT, period_stats, plot_growth, run

if __name__ == "__main__":
    tickers_list = ['BTC/USD', 'ETH/USD', 'XRP/USD', 'ADA/USD']
    lookbacks = [7, 14, 21, 30, 60, 90]
    initial_capital = 100000

    TEST_START = '2018-04-15'      # 2018-01-01 + 91-day warm-up + margin
    TEST_END = '2021-12-31'

    print(f"Running frozen Strategy v2 {DEFAULT} from 2018 ...")
    result = run('Ensemble_Trend_pre2022', initial_capital, tickers_list, lookbacks,
                 start_ts='20180101', **DEFAULT)
    pnl = result.pos_pnl

    # Data coverage: when did TWSQ's data start, and when did the strategy first trade?
    idx = twsq_daily_index(pnl.index)
    held = pnl[[t.split('/')[0] for t in tickers_list]].abs().sum(axis=1)
    first_trade = idx[held.values > 0].min() if (held.values > 0).any() else None
    print(f"\nTWSQ data from {idx.min().date()} to {idx.max().date()}; first position taken on "
          f"{first_trade.date() if first_trade is not None else 'never'}")
    for ticker in tickers_list:
        base = ticker.split('/')[0]
        traded = idx[pnl[base].abs().values > 0]
        print(f"  {base}: first held {traded.min().date() if len(traded) else 'never'}")
    if idx.min() > pd.Timestamp(TEST_START):
        print(f"\nWARNING: TWSQ data starts after {TEST_START}; the test covers less than planned.")

    fmt = lambda x: f"{x:.4f}"
    print(f"\n=== PRE-2022 TEST {TEST_START} to {TEST_END} (the pass/fail result) ===")
    whole = period_stats(pnl, initial_capital, tickers_list, TEST_START, TEST_END)
    print(whole.to_string(float_format=fmt, na_rep=""))
    s_sharpe = whole.loc['Sharpe', 'Strategy']
    b_sharpe = whole.loc['Sharpe', 'BTC Buy & Hold']
    print(f"\nRESULT: {'PASS' if s_sharpe > b_sharpe else 'FAIL'} "
          f"(strategy Sharpe {s_sharpe:.3f} vs BTC {b_sharpe:.3f})")

    for label, start, end in [('Bear market', TEST_START, '2019-12-31'),
                              ('Bull market', '2020-01-01', TEST_END)]:
        print(f"\n--- {label} {start} to {end} (information only) ---")
        print(period_stats(pnl, initial_capital, tickers_list, start, end)
              .to_string(float_format=fmt, na_rep=""))

    plot_growth(pnl, initial_capital, tickers_list, TEST_START, TEST_END,
                'Strategy v2 vs BTC vs equal-weight basket, Apr 2018 to Dec 2021 (unseen test)',
                save_as='v2_growth_2018_2021.png')
