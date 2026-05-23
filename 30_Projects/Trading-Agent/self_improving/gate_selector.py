"""
gate_selector.py — Strategy Gate Agent (Unified Engine Version)
Tests all strategies against Gate Criteria. Only passes if ALL three are met:
  PF ≥ 1.2 | Sharpe ≥ 0.3 | WR ≥ 42%
Output: Best passing strategy → frozen as strategy.yaml v0001
"""
import sys
sys.path.insert(0, "/opt/data/home/hermes-vault/30_Projects/Trading-Agent")

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from core.data_cleaner import load_raw, clean_wicks
from self_improving.common_engine import BacktestEngine

# Gate Criteria (hard floor)
MIN_PF = 1.2
MIN_SHARPE = 0.3
MIN_WR = 0.42

ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/self_improving")
STRATEGY_PATH = ROOT / "state" / "strategy.yaml"

# ── Shared: ATR calc ──────────────────────────────────────────

def calc_atr(df, length=14):
    prev_close = df['close'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - prev_close).abs()
    tr3 = (df['low'] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(span=length, adjust=False).mean()


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
        if price < row['lower'] and row['rsi'] < 35:
            sl = row['sma'] - 3 * row['std']; tp = row['sma']
            sl_dist = abs(price - sl); r = equity * risk; size = r / sl_dist if sl_dist > 0 else 0
            rr = abs(tp - price) / sl_dist if sl_dist > 0 else 0
            if rr >= 1.5: return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':r}
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
    engine = BacktestEngine(ind_fn, sig_fn, fee, slip, equity)
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
        print(f"✅ BEST PASSING: {overall_best['name']} on {overall_best.get('symbol', 'best_sym')}")
        print(f"   Trades: {overall_best['trades']} | WR: {overall_best['winrate']:.1%} | PF: {overall_best['profit_factor']:.2f} | Sharpe: {overall_best['sharpe']:.2f} | Ret: {overall_best['total_return_pct']:+.1f}%")
    else:
        print("❌ NO STRATEGY PASSED GATE. Parameter sweep recommended.")
        top_pf = max(all_results, key=lambda x: x['profit_factor'])
        top_wr = max(all_results, key=lambda x: x['winrate'])
        print(f"   Best PF: {top_pf['name']} ({top_pf['profit_factor']:.2f})")
        print(f"   Best WR: {top_wr['name']} ({top_wr['winrate']:.1%})")

    return passing


if __name__ == "__main__":
    main()
