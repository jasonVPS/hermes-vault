"""
gate_selector.py — Strategy Gate Agent
Tests all strategies against Gate Criteria. Only passes if ALL three are met:
  PF ≥ 1.2 | Sharpe ≥ 0.3 | WR ≥ 42%
Output: Best passing strategy → frozen as strategy.yaml v0001
"""
import sys
sys.path.insert(0, "/opt/data/home/hermes-vault/30_Projects/Trading-Agent")

import json
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from core.data_cleaner import load_raw, clean_wicks

ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/self_improving")
STRATEGY_PATH = ROOT / "state" / "strategy.yaml"

# Gate Criteria (hard floor)
MIN_PF = 1.2
MIN_SHARPE = 0.3
MIN_WR = 0.42

# ── Shared: ATR calc ──────────────────────────────────────────

def calc_atr(df, length=14):
    prev_close = df['close'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - prev_close).abs()
    tr3 = (df['low'] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(span=length, adjust=False).mean()

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


class Engine:
    def __init__(self, indicators_fn, signal_fn, fee, slip, equity=10000):
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
                exit_px = None; reason = ""
                if active.dir == 'long':
                    if row['low'] <= active.sl: exit_px = active.sl; reason = "SL"
                    elif row['high'] >= active.tp: exit_px = active.tp; reason = "TP"
                else:
                    if row['high'] >= active.sl: exit_px = active.sl; reason = "SL"
                    elif row['low'] <= active.tp: exit_px = active.tp; reason = "TP"

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


# ═════════════════════════════════════════════════════════
# STRATEGY 1: EMA CROSSOVER
# ═════════════════════════════════════════════════════════

def ema_cross_strategy(fast=9, slow=21, rsi_p=14, sl_mult=2.0, tp_mult=4.0, risk=0.01):
    def ind(df):
        df = df.copy()
        df['ema_f'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_s'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['atr'] = calc_atr(df)
        d = df['close'].diff()
        gain = d.where(d > 0, 0.0); loss = (-d).where(d < 0, 0.0)
        df['rsi'] = 100 - 100 / (1 + gain.ewm(alpha=1/rsi_p, adjust=False).mean() / loss.ewm(alpha=1/rsi_p, adjust=False).mean())
        prev_f = df['ema_f'].shift(1); prev_s = df['ema_s'].shift(1)
        df['cross'] = np.where((df['ema_f'] > df['ema_s']) & (prev_f <= prev_s), 1, np.where((df['ema_f'] < df['ema_s']) & (prev_f >= prev_s), -1, 0))
        return df
    def sig(df, i, equity):
        row = df.iloc[i]
        if row['cross'] == 0 or pd.isna(row['atr']) or row['atr'] == 0: return None
        price, atr, rsi = row['close'], row['atr'], row['rsi']
        if row['cross'] == 1 and rsi < 70 and rsi > 40:
            sl = price - atr * sl_mult; tp = price + atr * tp_mult
            r = equity * risk; size = r / (price - sl)
            return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
        if row['cross'] == -1 and rsi > 30 and rsi < 60:
            sl = price + atr * sl_mult; tp = price - atr * tp_mult
            r = equity * risk; size = r / (sl - price)
            return {'dir':'short','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
        return None
    return ind, sig

# ═════════════════════════════════════════════════════════
# STRATEGY 2: MEAN REVERSION (BOLLINGER)
# ═════════════════════════════════════════════════════════

def meanrev_strategy(bb_p=20, bb_std=2.0, rsi_p=14, sl_mult=2.0, tp_mult=3.0, risk=0.01):
    def ind(df):
        df = df.copy()
        df['sma'] = df['close'].rolling(bb_p).mean()
        df['std'] = df['close'].rolling(bb_p).std()
        df['upper'] = df['sma'] + bb_std * df['std']
        df['lower'] = df['sma'] - bb_std * df['std']
        df['atr'] = calc_atr(df)
        d = df['close'].diff()
        gain = d.where(d > 0, 0.0); loss = (-d).where(d < 0, 0.0)
        df['rsi'] = 100 - 100 / (1 + gain.ewm(alpha=1/rsi_p, adjust=False).mean() / loss.ewm(alpha=1/rsi_p, adjust=False).mean())
        return df
    def sig(df, i, equity):
        row = df.iloc[i]
        if pd.isna(row['lower']) or pd.isna(row['upper']): return None
        price = row['close']; atr = row['atr'] if pd.notna(row['atr']) else (row['high'] - row['low']) * 0.5
        # LONG: oversold
        if price < row['lower'] and row['rsi'] < 35:
            sl = row['sma'] - 3 * row['std']; tp = row['sma']
            sl_dist = abs(price - sl); r = equity * risk; size = r / sl_dist if sl_dist > 0 else 0
            rr = abs(tp - price) / sl_dist if sl_dist > 0 else 0
            if rr >= 1.5: return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
        # SHORT: overbought
        if price > row['upper'] and row['rsi'] > 65:
            sl = row['sma'] + 3 * row['std']; tp = row['sma']
            sl_dist = abs(sl - price); r = equity * risk; size = r / sl_dist if sl_dist > 0 else 0
            rr = abs(price - tp) / sl_dist if sl_dist > 0 else 0
            if rr >= 1.5: return {'dir':'short','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
        return None
    return ind, sig

# ═════════════════════════════════════════════════════════
# STRATEGY 3: ATR BREAKOUT
# ═════════════════════════════════════════════════════════

def breakout_strategy(lookback=20, vol_mult=1.5, sl_mult=1.5, tp_mult=3.0, risk=0.01):
    def ind(df):
        df = df.copy()
        df['atr'] = calc_atr(df)
        df['highest'] = df['high'].rolling(lookback).max().shift(1)
        df['lowest'] = df['low'].rolling(lookback).min().shift(1)
        df['vol_avg'] = df['volume'].rolling(20).mean()
        return df
    def sig(df, i, equity):
        row = df.iloc[i]
        if pd.isna(row['highest']) or pd.isna(row['atr']): return None
        price, atr = row['close'], row['atr']
        vol_ok = pd.notna(row['vol_avg']) and row['volume'] > vol_mult * row['vol_avg']
        if not vol_ok: return None
        if price > (row['highest'] + 0.5 * atr):
            sl = row['highest'] - atr; tp = price + atr * tp_mult
            r = equity * risk; size = r / (price - sl)
            return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
        if price < (row['lowest'] - 0.5 * atr):
            sl = row['lowest'] + atr; tp = price - atr * tp_mult
            r = equity * risk; size = r / (sl - price)
            return {'dir':'short','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
        return None
    return ind, sig

# ═════════════════════════════════════════════════════════
# STRATEGY 4: EMA_RSI (from backtest_clean.py)
# ═════════════════════════════════════════════════════════

def ema_rsi_strategy(fast=9, slow=21, trend=200, rsi_p=14, rsi_long=45, rsi_short=55, sl_mult=2.0, tp_mult=4.0, risk=0.01):
    def ind(df):
        df = df.copy()
        df['ema_f'] = df['close'].ewm(span=fast, adjust=False).mean()
        df['ema_s'] = df['close'].ewm(span=slow, adjust=False).mean()
        df['ema_trend'] = df['close'].ewm(span=trend, adjust=False).mean()
        df['atr'] = calc_atr(df, length=14)
        d = df['close'].diff()
        gain = d.where(d > 0, 0.0); loss = (-d).where(d < 0, 0.0)
        df['rsi'] = 100 - 100 / (1 + gain.ewm(alpha=1/rsi_p, adjust=False).mean() / loss.ewm(alpha=1/rsi_p, adjust=False).mean())
        df['vol_sma'] = df['volume'].rolling(window=20).mean()
        prev_f = df['ema_f'].shift(1); prev_s = df['ema_s'].shift(1)
        df['cross'] = np.where((df['ema_f'] > df['ema_s']) & (prev_f <= prev_s), 1,
                               np.where((df['ema_f'] < df['ema_s']) & (prev_f >= prev_s), -1, 0))
        return df
    def sig(df, i, equity):
        row = df.iloc[i]
        if row['cross'] == 0 or pd.isna(row['atr']) or row['atr'] == 0: return None
        price = row['close']; atr = row['atr']; rsi = row['rsi']
        # Trend filter
        if row['cross'] == 1 and price <= row['ema_trend']: return None
        if row['cross'] == -1 and price >= row['ema_trend']: return None
        # Volume filter
        if pd.isna(row['vol_sma']) or row['volume'] <= row['vol_sma']: return None
        # Max ATR%
        if (atr / price) > 0.03: return None
        if row['cross'] == 1 and rsi > rsi_long:
            sl = price - atr * sl_mult; tp = price + atr * tp_mult
            r = equity * risk; size = r / (price - sl)
            return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
        if row['cross'] == -1 and rsi < rsi_short:
            sl = price + atr * sl_mult; tp = price - atr * tp_mult
            r = equity * risk; size = r / (sl - price)
            return {'dir':'short','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
        return None
    return ind, sig


# ═════════════════════════════════════════════════════════
# GATE SELECTOR
# ═════════════════════════════════════════════════════════

def run_strategy(name, ind_fn, sig_fn, df, equity=10000, fee=0.0006, slip=0.0002):
    engine = Engine(ind_fn, sig_fn, fee, slip, equity)
    m = engine.run(df)
    m['name'] = name
    m['passes_gate'] = (m['profit_factor'] >= MIN_PF and m['sharpe'] >= MIN_SHARPE and m['winrate'] >= MIN_WR)
    return m


def main():
    print("=" * 60)
    print(" GATE AGENT: Strategy Selection")
    print(f" Criteria: PF ≥ {MIN_PF} | Sharpe ≥ {MIN_SHARPE} | WR ≥ {MIN_WR:.0%}")
    print("=" * 60)

    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    all_results = []

    for sym in symbols:
        print(f"\n--- {sym} ---")
        df_raw = load_raw(sym, "1h")
        df_clean = clean_wicks(df_raw, max_wick_pct=0.05)
        print(f"  Data: {len(df_clean)} bars")

        strategies = [
            ("EMA_Cross", *ema_cross_strategy()),
            ("MeanRev_BB", *meanrev_strategy()),
            ("Breakout_ATR", *breakout_strategy()),
            ("EMA_RSI_Trend", *ema_rsi_strategy()),
        ]

        best = None
        for name, ind_fn, sig_fn in strategies:
            m = run_strategy(name, ind_fn, sig_fn, df_clean)
            gate = "✅ PASS" if m['passes_gate'] else "❌ FAIL"
            print(f"  {name:15s} | T:{m['trades']:3d} | WR:{m['winrate']:.1%} | PF:{m['profit_factor']:.2f} | SR:{m['sharpe']:.2f} | DD:{m['max_dd_pct']:.1f}% | Ret:{m['total_return_pct']:+.1f}% {gate}")
            all_results.append(m)
            if m['passes_gate'] and (best is None or m['total_return_pct'] > best['total_return_pct']):
                best = m

    # Summary
    print(f"\n{'='*60}")
    passing = [r for r in all_results if r['passes_gate']]
    if passing:
        overall_best = max(passing, key=lambda x: x['total_return_pct'])
        best_sym = overall_best['name']
        print(f"✅ BEST PASSING: {overall_best['name']} on {best_sym}")
        print(f"   Trades: {overall_best['trades']} | WR: {overall_best['winrate']:.1%} | PF: {overall_best['profit_factor']:.2f} | Sharpe: {overall_best['sharpe']:.2f} | Ret: {overall_best['total_return_pct']:+.1f}%")
        # Could write strategy.yaml here with winning params
    else:
        print("❌ NO STRATEGY PASSED GATE. Parameter sweep recommended.")
        # Show top by each criterion
        top_pf = max(all_results, key=lambda x: x['profit_factor'])
        top_wr = max(all_results, key=lambda x: x['winrate'])
        print(f"   Best PF: {top_pf['name']} ({top_pf['profit_factor']:.2f})")
        print(f"   Best WR: {top_wr['name']} ({top_wr['winrate']:.1%})")

    return passing


if __name__ == "__main__":
    main()
