"""
Walk-Forward Backtest for 15m Scalping Strategy
Tests on historical data: 100€ start, 30 days simulation
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

from experiments.trading_100e.strategy.scalping import ScalpingStrategy
from experiments.trading_100e.learn.engine import LearningEngine
from core.data_cleaner import load_raw

class BacktestEngine:
    def __init__(self):
        self.learner = LearningEngine()
        self.strategy = ScalpingStrategy(self.learner.get_params())
        self.equity = 100.0
        self.trades = []
        self.equity_curve = [100.0]
        self.position = None
        
    def run(self, df_15m, df_1h=None):
        """Full walk-forward over all bars"""
        # Pre-calculate indicators on full series
        df = self.strategy.calculate(df_15m, df_1h)
        
        print(f"Running backtest on {len(df)} bars ({len(df)/4:.0f} hours)")
        
        # Walk forward bar by bar
        for i in range(210, len(df)):
            row = df.iloc[i]
            
            # Skip if not enough data ahead
            if i >= len(df) - 1:
                continue
            
            # Check position exit
            if self.position:
                pos = self.position
                closed = False
                exit_price = None
                exit_reason = ""
                
                # SL check
                if pos['dir'] == 'long' and row['low'] <= pos['current_sl']:
                    closed = True
                    exit_price = pos['current_sl']
                    exit_reason = "SL"
                elif pos['dir'] == 'short' and row['high'] >= pos['current_sl']:
                    closed = True
                    exit_price = pos['current_sl']
                    exit_reason = "SL"
                
                # TP checks (in order, update SL)
                if not closed:
                    if pos['dir'] == 'long':
                        if not pos['tp1_hit'] and row['high'] >= pos['tp1']:
                            pos['tp1_hit'] = True
                            pos['current_sl'] = pos['entry'] * 1.001  # BE + buffer
                        elif pos['tp1_hit'] and not pos['tp2_hit'] and row['high'] >= pos['tp2']:
                            pos['tp2_hit'] = True
                            pos['current_sl'] = pos['tp1']  # Lock TP1
                        elif pos['tp2_hit'] and row['high'] >= pos['tp3']:
                            closed = True
                            exit_price = pos['tp3']
                            exit_reason = "TP3"
                    else:  # short
                        if not pos['tp1_hit'] and row['low'] <= pos['tp1']:
                            pos['tp1_hit'] = True
                            pos['current_sl'] = pos['entry'] * 0.999
                        elif pos['tp1_hit'] and not pos['tp2_hit'] and row['low'] <= pos['tp2']:
                            pos['tp2_hit'] = True
                            pos['current_sl'] = pos['tp1']
                        elif pos['tp2_hit'] and row['low'] <= pos['tp3']:
                            closed = True
                            exit_price = pos['tp3']
                            exit_reason = "TP3"
                
                # Max hold time (32 bars = 8h)
                if not closed and (i - pos['entry_idx']) > 32:
                    closed = True
                    exit_price = row['close']
                    exit_reason = "TIME"
                
                if closed:
                    # Calculate P&L
                    if pos['dir'] == 'long':
                        raw = (exit_price - pos['entry']) / pos['entry']
                    else:
                        raw = (pos['entry'] - exit_price) / pos['entry']
                    
                    costs = 0.0012
                    pnl = raw - costs
                    pnl_abs = pnl * self.equity
                    self.equity += pnl_abs
                    
                    record = {
                        'entry_time': pos['entry_time'],
                        'exit_time': row['timestamp'],
                        'dir': pos['dir'],
                        'entry': pos['entry'],
                        'exit': exit_price,
                        'sl': pos['original_sl'],
                        'tp1': pos['tp1'],
                        'tp2': pos['tp2'],
                        'tp3': pos['tp3'],
                        'tp_hit': 3 if pos['tp3_hit'] else 2 if pos['tp2_hit'] else 1 if pos['tp1_hit'] else 0,
                        'pnl_pct': pnl,
                        'pnl_abs': pnl_abs,
                        'setup_score': pos['setup_score'],
                        'size_pct': pos['size_pct'],
                        'reasons': pos['reasons'],
                        'exit_reason': exit_reason,
                        'bars_held': i - pos['entry_idx'],
                    }
                    self.trades.append(record)
                    self.equity_curve.append(self.equity)
                    
                    # Learn!
                    self.learner.update({
                        'pnl_abs': pnl_abs,
                        'pnl_pct': pnl,
                        'setup_score': pos['setup_score'],
                        'tp_hit': record['tp_hit'],
                        'bars_held': record['bars_held'],
                        'dir': pos['dir'],
                        'reasons': pos['reasons']
                    })
                    
                    # Update strategy with new params
                    self.strategy = ScalpingStrategy(self.learner.get_params())
                    self.position = None
            
            # Check entry (only if no position)
            if not self.position and i < len(df) - 2:
                # Need to regenerate signal with current bar as "last"
                df_slice = df.iloc[:i+1].copy()
                
                # Use 1h trend data if available (find relevant)
                df_1h_slice = None
                if df_1h is not None:
                    ts = row['timestamp']
                    df_1h_slice = df_1h[df_1h['timestamp'] <= ts].tail(210).copy() if len(df_1h[df_1h['timestamp'] <= ts]) >= 200 else None
                
                signal = self.strategy.generate(df_slice, self.equity, df_1h_slice)
                
                if signal:
                    sl_dist = abs(signal.entry - signal.sl)
                    if sl_dist > 0:
                        risk = self.equity * signal.size_pct
                        size = risk / sl_dist
                        
                        self.position = {
                            'entry_time': row['timestamp'],
                            'entry_idx': i,
                            'dir': signal.dir,
                            'entry': signal.entry,
                            'original_sl': signal.sl,
                            'current_sl': signal.sl,
                            'tp1': signal.tp1,
                            'tp2': signal.tp2,
                            'tp3': signal.tp3,
                            'tp1_hit': False,
                            'tp2_hit': False,
                            'tp3_hit': False,
                            'size_pct': signal.size_pct,
                            'setup_score': signal.setup_score,
                            'reasons': signal.reasons,
                            'size': size,
                        }
        
        return self._report()
    
    def _report(self):
        if not self.trades:
            print("NO TRADES")
            return
        
        wins = [t for t in self.trades if t['pnl_pct'] > 0]
        losses = [t for t in self.trades if t['pnl_pct'] <= 0]
        
        wr = len(wins) / len(self.trades)
        
        total_ret = (self.equity - 100) / 100 * 100
        
        # Max drawdown
        peak = 100.0
        mdd = 0
        for e in self.equity_curve:
            if e > peak: peak = e
            dd = (peak - e) / peak
            if dd > mdd: mdd = dd
        
        # Profit factor
        gross_profit = sum(t['pnl_pct'] for t in wins)
        gross_loss = abs(sum(t['pnl_pct'] for t in losses))
        pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Sharpe (per-trade returns)
        rets = [t['pnl_pct'] for t in self.trades]
        sharpe = np.mean(rets) / np.std(rets) * np.sqrt(len(rets)) if np.std(rets) > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"  WALK-FORWARD RESULTS")
        print(f"{'='*60}")
        print(f"  Period: {self.trades[0]['entry_time']} → {self.trades[-1]['exit_time']}")
        print(f"  Trades: {len(self.trades)} | Wins: {len(wins)} | Losses: {len(losses)}")
        print(f"  Winrate: {wr*100:.1f}%")
        print(f"  Equity: ${self.equity:.2f} (start $100.00)")
        print(f"  Total Return: {total_ret:+.2f}%")
        print(f"  Max Drawdown: {mdd*100:.2f}%")
        print(f"  Profit Factor: {pf:.2f}")
        print(f"  Sharpe: {sharpe:.2f}")
        
        # TP distribution
        tps = [t['tp_hit'] for t in self.trades]
        print(f"  TP Distribution: SL={tps.count(0)} | TP1={tps.count(1)} | TP2={tps.count(2)} | TP3={tps.count(3)}")
        
        # Show last 5 trades
        print(f"\n  LAST 5 TRADES:")
        for t in self.trades[-5:]:
            print(f"    {t['dir']:5s} {str(t['entry_time'])[5:16]} {t['entry']:8.2f} → {t['exit']:8.2f} | {t['pnl_pct']*100:+.2f}% | {t['exit_reason']}")
        
        print(f"\n  FINAL STRATEGY PARAMS:")
        final_params = self.learner.get_params()
        for k, v in final_params.items():
            print(f"    {k}: {v}")


def run_experiment():
    symbol = "BTC/USDT"
    
    df_15m = load_raw(symbol, "15m")
    df_1h = load_raw(symbol, "1h")
    
    print(f"Data loaded: 15m={len(df_15m)} bars, 1h={len(df_1h)} bars")
    
    bt = BacktestEngine()
    bt.run(df_15m, df_1h)


if __name__ == "__main__":
    run_experiment()
