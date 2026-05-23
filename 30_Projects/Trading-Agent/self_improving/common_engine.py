"""
common_engine.py — Unified Backtest Engine
Used by gate_selector, evolve, worker. IDENTICAL logic everywhere.
"""
import sys
sys.path.insert(0, "/opt/data/home/hermes-vault/30_Projects/Trading-Agent")

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Trade:
    entry_time: pd.Timestamp
    dir: str
    entry_price: float
    sl: float
    tp: float
    size: float
    risk_usd: float
    exit_time: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    pnl_pct: float = 0.0
    pnl_abs: float = 0.0
    exit_reason: str = ""
    bars_held: int = 0


class BacktestEngine:
    """Unified engine — SL/TP exits ONLY. No additional reversal exits.
    This ensures discovery and worker see exactly the same trades."""

    def __init__(self, indicators_fn, signal_fn, fee=0.0006, slip=0.0002, equity=10000):
        self.indicators_fn = indicators_fn
        self.signal_fn = signal_fn
        self.fee = fee
        self.slip = slip
        self.initial = equity
        self.trades: List[Trade] = []

    def run(self, df_raw, min_bars=50):
        df = self.indicators_fn(df_raw)
        equity = self.initial
        active = None

        for i in range(min_bars, len(df)):
            row = df.iloc[i]
            if active:
                exit_px = None
                reason = ""
                if active.dir == 'long':
                    if row['low'] <= active.sl:
                        exit_px = active.sl; reason = "SL"
                    elif row['high'] >= active.tp:
                        exit_px = active.tp; reason = "TP"
                else:  # short
                    if row['high'] >= active.sl:
                        exit_px = active.sl; reason = "SL"
                    elif row['low'] <= active.tp:
                        exit_px = active.tp; reason = "TP"

                if exit_px:
                    active.exit_time = row['timestamp']
                    active.exit_price = exit_px
                    active.exit_reason = reason
                    raw = (exit_px - active.entry_price) / active.entry_price if active.dir == 'long' else (active.entry_price - exit_px) / active.entry_price
                    costs = self.fee * 2 + self.slip * 2
                    active.pnl_pct = raw - costs
                    active.pnl_abs = active.pnl_pct * active.entry_price * active.size
                    equity += active.pnl_abs
                    self.trades.append(active)
                    active = None

            if not active and i < len(df) - 1:
                sig = self.signal_fn(df, i, equity)
                if sig:
                    active = Trade(entry_time=row['timestamp'], dir=sig['dir'],
                                   entry_price=sig['entry'], sl=sig['sl'], tp=sig['tp'],
                                   size=sig['size'], risk_usd=sig['risk'])
        return self.metrics(equity)

    def metrics(self, final):
        if not self.trades:
            return {'trades':0, 'winrate':0, 'profit_factor':0, 'sharpe':0,
                    'max_dd_pct':0, 'total_return_pct':0, 'avg_win':0, 'avg_loss':0}
        wins = [t for t in self.trades if t.pnl_pct > 0]
        losses = [t for t in self.trades if t.pnl_pct <= 0]
        wr = len(wins)/len(self.trades)
        gp = sum(t.pnl_pct for t in wins)
        gl = abs(sum(t.pnl_pct for t in losses))
        pf = gp / gl if gl > 0 else float('inf')

        eq = [self.initial]
        for t in self.trades: eq.append(eq[-1] + t.pnl_abs)
        peak = eq[0]; mdd = 0
        for e in eq:
            if e > peak: peak = e
            dd = (peak - e)/peak
            if dd > mdd: mdd = dd

        rets = [t.pnl_pct for t in self.trades]
        sharpe = np.mean(rets)/np.std(rets) * np.sqrt(len(rets)) if np.std(rets) > 0 else 0
        return {
            'trades': len(self.trades), 'winrate': wr, 'profit_factor': pf,
            'sharpe': sharpe, 'max_dd_pct': mdd * 100,
            'total_return_pct': (final - self.initial) / self.initial * 100,
            'avg_win': np.mean([t.pnl_pct for t in wins]) if wins else 0,
            'avg_loss': np.mean([t.pnl_pct for t in losses]) if losses else 0,
        }
