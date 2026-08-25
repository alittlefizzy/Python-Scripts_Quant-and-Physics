import numpy as np
import pandas as pd
from twsq.alpha import Alpha

class WFO_Dynamic_Mom(Alpha):
    
    def prepare(self, tickers, test_windows, capital, rebalance_days=30):
        self.tickers = tickers
        self.test_windows = test_windows
        self.capital = capital
        self.rebalance_days = rebalance_days
        self.days_since_rebalance = rebalance_days 
        
    def rebalance(self):
        if self.days_since_rebalance < self.rebalance_days:
            self.days_since_rebalance += 1
            return
            
        self.days_since_rebalance = 0
        target_positions = {}
        inv_vols = {}
        signals = {}
        
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
        capital=initial_capital
    )