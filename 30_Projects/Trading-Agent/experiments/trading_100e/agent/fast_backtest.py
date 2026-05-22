"""
Fast Scalping Backtest for 100€ → 200€ challenge
Optimized for speed, 15m timeframe, simple mean reversion
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

import pandas as pd
import numpy as np
from core.data_cleaner import load_raw
from experiments.trading_100e.learn.engine import LearningEngine

class FastStrategy:
    """
    SIMPLE MEAN REVERSION (15m)
    ===========
    Long:  RSI(7) < 30 AND Close > Lower BB(20,2)
    Short: RSI(7) > 70 AND Close < Upper BB(20,2)
    
    SL: 1.0 ATR(14)
    TP: 2.0 ATR(14)   (2:1 R:R minimum)
    
    Risk: 2% per trade
    
    Filter: Skip if ATR%> 1.5% (too volatile)
    """
    def __init__(self, params=None):
        defaults = {
            'rsi_period': 7,
            'rsi_long': 30,
            'rsi_short': 70,
            'bb_period': 20,
            'bb_std': 2.0,
            'atr_period': 14,
            'sl_mult': 1.0,
            'tp_mult': 2.0,
            'risk_pct': 0.02,
            'max_atr_pct': 0.015,
        }
        self.p = {**defaults, **(params or {})}
    
    def calc(self, df):
        df = df.copy()
        close = df['close']
        high = df['high']
        low = df['low']
        
        # Bollinger
        df['sma'] = close.rolling(int(self.p['bb_period'])).mean()
        std = close.rolling(int(self.p['bb_period'])).std()
        df['upper'] = df['sma'] + self.p['bb_std'] * std
        df['lower'] = df['sma'] - self.p['bb_std'] * std
        
        # ATR
        prev = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev).abs()
        tr3 = (low - prev).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(int(self.p['atr_period'])).mean()
        df['atr_pct'] = df['atr'] / close
        
        # RSI(7) - Wilder
        d = close.diff()
        gain = d.clip(lower=0)
        loss = (-d).clip(lower=0)
        avg_g = gain.ewm(alpha=1/self.p['rsi_period'], adjust=False).mean()
        avg_l = loss.ewm(alpha=1/self.p['rsi_period'], adjust=False).mean()
        rs = avg_g / avg_l
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df
    
    def signals(self, df, equity=100):
        df = self.calc(df)
        trades = []
        in_pos = False
        pos = None
        
        for i in range(50, len(df) - 1):
            row = df.iloc[i]
            
            # Skip if indicators not ready or too volatile
            if pd.isna(row['rsi']) or pd.isna(row['atr']) or row['atr'] == 0:
                continue
            if row['atr_pct'] > self.p['max_atr_pct']:
                continue
            
            # Check exit first
            if in_pos:
                exit_px = None
                reason = ""
                
                if pos['dir'] == 'long':
                    if row['low'] <= pos['sl']:
                        exit_px = pos['sl']
                        reason = "SL"
                    elif row['high'] >= pos['tp']:
                        exit_px = pos['tp']
                        reason = "TP"
                else:
                    if row['high'] >= pos['sl']:
                        exit_px = pos['sl']
                        reason = "SL"
                    elif row['low'] <= pos['tp']:
                        exit_px = pos['tp']
                        reason = "TP"
                
                if exit_px:
                    # Calculate PnL
                    if pos['dir'] == 'long':
                        raw = (exit_px - pos['entry']) / pos['entry']
                    else:
                        raw = (pos['entry'] - exit_px) / pos['entry']
                    pnl = raw - 0.0012  # 0.12% fees
                    
                    trades.append({
                        'dir': pos['dir'], 'entry': pos['entry'], 'exit': exit_px,
                        'sl': pos['sl'], 'tp': pos['tp'],
                        'pnl': pnl, 'reason': reason, 'score': pos['score'],
                        'bars': i - pos['idx']
                    })
                    in_pos = False
                    pos = None
                    continue
            
            # Check entry
            if not in_pos:
                if row['rsi'] < self.p['rsi_long'] and row['close'] > row['lower']:
                    sl = row['close'] - row['atr'] * self.p['sl_mult']
                    tp = row['close'] + row['atr'] * self.p['tp_mult']
                    risk = equity * self.p['risk_pct']
                    size = risk / (row['close'] - sl)
                    in_pos = True
                    pos = {
                        'dir': 'long', 'entry': row['close'], 'sl': sl, 'tp': tp,
                        'idx': i, 'score': 50 + (self.p['rsi_long'] - row['rsi']),
                        'size': size, 'risk': risk
                    }
                
                elif row['rsi'] > self.p['rsi_short'] and row['close'] < row['upper']:
                    sl = row['close'] + row['atr'] * self.p['sl_mult']
                    tp = row['close'] - row['atr'] * self.p['tp_mult']
                    risk = equity * self.p['risk_pct']
                    size = risk / (sl - row['close'])
                    in_pos = True
                    pos = {
                        'dir': 'short', 'entry': row['close'], 'sl': sl, 'tp': tp,
                        'idx': i, 'score': 50 + (row['rsi'] - self.p['rsi_short']),
                        'size': size, 'risk': risk
                    }
        
        return trades


def run_fast_backtest(symbol="BTC/USDT", tf="15m"):
    print(f"\n{'='*60}")
    print(f"  FAST BACKTEST: {symbol} @ {tf}")
    print(f"{'='*60}")
    
    df = load_raw(symbol, tf)
    print(f"Data: {len(df)} bars = {len(df)/4:.0f} hours = {len(df)/96:.1f} days")
    
    strat = FastStrategy()
    learner = LearningEngine()
    
    # Iterative training: run, learn, repeat
    equity = 100.0
    all_trades = []
    equity_curve = [100.0]
    
    # Run strategy
    trades = strat.signals(df, equity)
    
    for t in trades[:50]:  # Limit to first 50 trades for speed
        equity *= (1 + t['pnl'])
        all_trades.append(t)
        equity_curve.append(equity)
        
        # Learn
        learner.update({
            'pnl_abs': t['pnl'] * equity,
            'pnl_pct': t['pnl'],
            'setup_score': int(t['score']),
            'tp_hit': 3 if t['reason'] == 'TP' else 0,
            'bars_held': t['bars'],
            'dir': t['dir'],
            'reasons': ['RSI_EXTREME']
        })
    
    # Results
    if not all_trades:
        print("No trades")
        return
    
    wins = [t for t in all_trades if t['pnl'] > 0]
    losses = [t for t in all_trades if t['pnl'] <= 0]
    
    print(f"\nTrades: {len(all_trades)} | Wins: {len(wins)} | Losses: {len(losses)}")
    print(f"Winrate: {len(wins)/len(all_trades)*100:.1f}%")
    print(f"Final Equity: ${equity:.2f}")
    print(f"Return: {(equity-100)*100/100:+.2f}%")
    
    # Drawdown
    peak = 100.0
    mdd = 0
    for e in equity_curve:
        if e > peak: peak = e
        dd = (peak - e)/peak
        if dd > mdd: mdd = dd
    print(f"Max Drawdown: {mdd*100:.2f}%")
    
    # Profit factor
    gp = sum(t['pnl'] for t in wins)
    gl = abs(sum(t['pnl'] for t in losses))
    pf = gp/gl if gl > 0 else float('inf')
    print(f"Profit Factor: {pf:.2f}")
    
    # Show last 5
    print(f"\nLast 5 trades:")
    for t in all_trades[-5:]:
        print(f"  {t['dir']:5s} {t['entry']:8.2f} → {t['exit']:8.2f} | {t['pnl']*100:+.2f}% | {t['reason']}")
    
    return all_trades, equity_curve

if __name__ == "__main__":
    run_fast_backtest("BTC/USDT", "15m")
    run_fast_backtest("ETH/USDT", "15m")
    run_fast_backtest("SOL/USDT", "15m")
