"""
Strategy Grid Search: 6 Months, Multiple Coins, Multiple Strategies
Goal: Find strategy with highest probability of doubling 100€ in 30 days
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

import sqlite3, json, os, random
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

DB = "/opt/data/home/hermes-vault/30_Projects/Trading-Agent/data/market_data.db"
COINS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
         "DOGE/USDT", "ADA/USDT", "LINK/USDT", "AVAX/USDT", "MATIC/USDT"]

def load_data(symbol: str, tf: str = "15m") -> pd.DataFrame:
    conn = sqlite3.connect(DB)
    query = "SELECT * FROM ohlcv WHERE symbol=? AND timeframe=? ORDER BY timestamp"
    df = pd.read_sql(query, conn, params=(symbol, tf), parse_dates=['timestamp'])
    conn.close()
    
    # Clean wicks (cap at 8% to avoid Binance bad ticks)
    df = df.copy()
    for idx in df.index:
        row = df.loc[idx]
        price = (row['open'] + row['close']) / 2
        max_range = price * 0.08
        if row['high'] - row['low'] > max_range:
            df.loc[idx, 'high'] = min(row['high'], max(row['open'], row['close']) + max_range * 0.5)
            df.loc[idx, 'low'] = max(row['low'], min(row['open'], row['close']) - max_range * 0.5)
    
    return df

# ════════════════════════════════════════════════════════════
# STRATEGY 1: TREND FOLLOWING (EMA CROSS + MOMENTUM)
# ════════════════════════════════════════════════════════════
def strategy_trend_following(df: pd.DataFrame, params: dict) -> List[dict]:
    """Only trade in direction of EMA50 trend, RSI confirms momentum"""
    df = df.copy()
    fast, slow, trend = params.get('fast', 9), params.get('slow', 21), params.get('trend', 50)
    sl_mult = params.get('sl_mult', 2.0)
    tp_mult = params.get('tp_mult', 4.0)
    risk = params.get('risk', 0.02)
    
    df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
    df['ema_trend'] = df['close'].ewm(span=trend, adjust=False).mean()
    df['atr'] = df['high'].rolling(14).mean() - df['low'].rolling(14).mean()
    
    d = df['close'].diff()
    gain = d.clip(lower=0)
    loss = (-d).clip(lower=0)
    avg_g = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_l = loss.ewm(alpha=1/14, adjust=False).mean()
    df['rsi'] = 100 - (100 / (1 + avg_g / avg_l))
    
    trades = []
    in_pos = False
    pos = None
    
    for i in range(trend + 20, len(df) - 1):
        row = df.iloc[i]
        if pd.isna(row['atr']) or row['atr'] == 0:
            continue
        
        # Exit
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
                raw = ((exit_px - pos['entry']) / pos['entry']) if pos['dir'] == 'long' else ((pos['entry'] - exit_px) / pos['entry'])
                pnl = raw - 0.0012
                trades.append({'dir': pos['dir'], 'pnl': pnl, 'score': pos['score'], 'reason': reason})
                in_pos = False
        
        # Entry
        if not in_pos:
            trend_up = row['ema_trend'] > df['ema_trend'].iloc[i-10]
            cross_bull = row['ema_fast'] > row['ema_slow'] and df['ema_fast'].iloc[i-1] <= df['ema_slow'].iloc[i-1]
            cross_bear = row['ema_fast'] < row['ema_slow'] and df['ema_fast'].iloc[i-1] >= df['ema_slow'].iloc[i-1]
            
            if cross_bull and trend_up and 50 < row['rsi'] < 70:
                sl = row['close'] - row['atr'] * sl_mult
                tp = row['close'] + row['atr'] * sl_mult * tp_mult
                in_pos = True
                pos = {'dir': 'long', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': 60}
            elif cross_bear and not trend_up and 30 < row['rsi'] < 50:
                sl = row['close'] + row['atr'] * sl_mult
                tp = row['close'] - row['atr'] * sl_mult * tp_mult
                in_pos = True
                pos = {'dir': 'short', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': 60}
    
    return trades


# ════════════════════════════════════════════════════════════
# STRATEGY 2: MEAN REVERSION (RSI EXTREME + BOLLINGER)
# ════════════════════════════════════════════════════════════
def strategy_mean_reversion(df: pd.DataFrame, params: dict) -> List[dict]:
    """Fade RSI extremes within Bollinger Bands"""
    df = df.copy()
    bb_p, bb_std = params.get('bb_period', 20), params.get('bb_std', 2.5)
    rsi_l, rsi_s = params.get('rsi_long', 25), params.get('rsi_short', 75)
    sl_mult, tp_mult = params.get('sl_mult', 1.5), params.get('tp_mult', 2.0)
    
    df['sma'] = df['close'].rolling(bb_p).mean()
    df['std'] = df['close'].rolling(bb_p).std()
    df['upper'] = df['sma'] + bb_std * df['std']
    df['lower'] = df['sma'] - bb_std * df['std']
    
    d = df['close'].diff()
    gain, loss = d.clip(lower=0), (-d).clip(lower=0)
    avg_g = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_l = loss.ewm(alpha=1/14, adjust=False).mean()
    df['rsi'] = 100 - (100 / (1 + avg_g / avg_l))
    
    trades = []
    in_pos = False
    pos = None
    
    for i in range(bb_p + 20, len(df) - 1):
        row = df.iloc[i]
        if pd.isna(row['lower']) or pd.isna(row['rsi']):
            continue
        
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
                raw = ((exit_px - pos['entry']) / pos['entry']) if pos['dir'] == 'long' else ((pos['entry'] - exit_px) / pos['entry'])
                pnl = raw - 0.0012
                trades.append({'dir': pos['dir'], 'pnl': pnl, 'score': pos['score'], 'reason': reason})
                in_pos = False
        
        if not in_pos:
            atr = (df['high'].iloc[i-14:i].mean() - df['low'].iloc[i-14:i].mean())
            if pd.isna(atr) or atr == 0:
                continue
            
            if row['rsi'] < rsi_l and row['close'] >= row['lower']:
                sl = row['close'] - atr * sl_mult
                tp = min(row['close'] + atr * sl_mult * tp_mult, row['sma'])
                in_pos = True
                pos = {'dir': 'long', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': int(75 - row['rsi'])}
            elif row['rsi'] > rsi_s and row['close'] <= row['upper']:
                sl = row['close'] + atr * sl_mult
                tp = max(row['close'] - atr * sl_mult * tp_mult, row['sma'])
                in_pos = True
                pos = {'dir': 'short', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': int(row['rsi'] - 25)}
    
    return trades


# ════════════════════════════════════════════════════════════
# STRATEGY 3: BREAKOUT (ATR + VOLUME SPIKE)
# ════════════════════════════════════════════════════════════
def strategy_breakout(df: pd.DataFrame, params: dict) -> List[dict]:
    """Trade breakouts of ATR-adjusted channels with volume"""
    df = df.copy()
    lookback = params.get('lookback', 20)
    vol_mult = params.get('vol_mult', 1.5)
    sl_mult, tp_mult = params.get('sl_mult', 1.5), params.get('tp_mult', 3.0)
    
    df['atr'] = (df['high'] - df['low']).rolling(14).mean()
    df['highest'] = df['high'].rolling(lookback).max().shift(1)
    df['lowest'] = df['low'].rolling(lookback).min().shift(1)
    df['vol_avg'] = df['volume'].rolling(20).mean()
    
    trades = []
    in_pos = False
    pos = None
    
    for i in range(lookback + 20, len(df) - 1):
        row = df.iloc[i]
        if pd.isna(row['atr']) or row['atr'] == 0 or pd.isna(row['highest']):
            continue
        
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
                raw = ((exit_px - pos['entry']) / pos['entry']) if pos['dir'] == 'long' else ((pos['entry'] - exit_px) / pos['entry'])
                pnl = raw - 0.0012
                trades.append({'dir': pos['dir'], 'pnl': pnl, 'score': pos['score'], 'reason': reason})
                in_pos = False
        
        if not in_pos:
            vol_ok = row['volume'] > vol_mult * row['vol_avg'] if pd.notna(row['vol_avg']) and row['vol_avg'] > 0 else False
            
            if row['close'] > row['highest'] + 0.2 * row['atr'] and vol_ok:
                sl = row['highest'] - row['atr'] * sl_mult
                tp = row['close'] + row['atr'] * sl_mult * tp_mult
                in_pos = True
                pos = {'dir': 'long', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': 55}
            elif row['close'] < row['lowest'] - 0.2 * row['atr'] and vol_ok:
                sl = row['lowest'] + row['atr'] * sl_mult
                tp = row['close'] - row['atr'] * sl_mult * tp_mult
                in_pos = True
                pos = {'dir': 'short', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': 55}
    
    return trades


# ════════════════════════════════════════════════════════════
# STRATEGY 4: RANGE BOUND (RSI IN RANGE)
# ════════════════════════════════════════════════════════════
def strategy_range_bound(df: pd.DataFrame, params: dict) -> List[dict]:
    """Trade only when RSI is in neutral range and price at band extremes"""
    df = df.copy()
    df['sma'] = df['close'].rolling(50).mean()
    df['std'] = df['close'].rolling(50).std()
    df['upper'] = df['sma'] + 2 * df['std']
    df['lower'] = df['sma'] - 2 * df['std']
    
    d = df['close'].diff()
    gain, loss = d.clip(lower=0), (-d).clip(lower=0)
    avg_g = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_l = loss.ewm(alpha=1/14, adjust=False).mean()
    df['rsi'] = 100 - (100 / (1 + avg_g / avg_l))
    
    sl_mult, tp_mult = params.get('sl_mult', 1.0), params.get('tp_mult', 2.0)
    
    trades = []
    in_pos = False
    pos = None
    
    for i in range(70, len(df) - 1):
        row = df.iloc[i]
        
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
                raw = ((exit_px - pos['entry']) / pos['entry']) if pos['dir'] == 'long' else ((pos['entry'] - exit_px) / pos['entry'])
                pnl = raw - 0.0012
                trades.append({'dir': pos['dir'], 'pnl': pnl, 'score': pos['score'], 'reason': reason})
                in_pos = False
        
        if not in_pos:
            atr = (df['high'].iloc[max(0,i-14):i].mean() - df['low'].iloc[max(0,i-14):i].mean())
            if pd.isna(atr) or atr == 0:
                continue
            
            # Only trade when RSI is in 35-65 range (no trend)
            if 35 <= row['rsi'] <= 65:
                if row['close'] <= row['lower']:
                    sl = row['close'] - atr * sl_mult
                    tp = min(row['close'] + atr * sl_mult * tp_mult, df['upper'].iloc[i])
                    in_pos = True
                    pos = {'dir': 'long', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': int(row['rsi'])}
                elif row['close'] >= row['upper']:
                    sl = row['close'] + atr * sl_mult
                    tp = max(row['close'] - atr * sl_mult * tp_mult, df['lower'].iloc[i])
                    in_pos = True
                    pos = {'dir': 'short', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': int(100 - row['rsi'])}
    
    return trades


# ════════════════════════════════════════════════════════════
# STRATEGY 5: VOLATILITY EXPANSION (TRADE THE TREND AFTER VOL SPIKE)
# ════════════════════════════════════════════════════════════
def strategy_vol_expansion(df: pd.DataFrame, params: dict) -> List[dict]:
    """Trade after volatility contraction-expansion cycle (Bollinger Squeeze)"""
    df = df.copy()
    bb_p = params.get('bb_period', 20)
    squeeze_mult = params.get('squeeze_mult', 2.0)
    
    df['sma'] = df['close'].rolling(bb_p).mean()
    df['std'] = df['close'].rolling(bb_p).std()
    df['upper'] = df['sma'] + 2 * df['std']
    df['lower'] = df['sma'] - 2 * df['std']
    df['bb_width'] = (df['upper'] - df['lower']) / df['sma']
    df['width_avg'] = df['bb_width'].rolling(50).mean()
    df['atr'] = (df['high'] - df['low']).rolling(14).mean()
    
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    
    sl_mult, tp_mult = params.get('sl_mult', 2.0), params.get('tp_mult', 4.0)
    
    trades = []
    in_pos = False
    pos = None
    squeeze_active = False
    squeeze_dir = None
    
    for i in range(70, len(df) - 1):
        row = df.iloc[i]
        
        # Detect squeeze end
        if not squeeze_active and pd.notna(row['width_avg']) and row['bb_width'] < row['width_avg'] * 0.7:
            squeeze_active = True
            squeeze_dir = None
        
        if squeeze_active and pd.notna(row['width_avg']) and row['bb_width'] > row['width_avg'] * 1.3:
            squeeze_active = False
            # Determine direction: which band was broken?
            if row['close'] > df['upper'].iloc[i-1]:
                squeeze_dir = 'long'
            elif row['close'] < df['lower'].iloc[i-1]:
                squeeze_dir = 'short'
        
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
                raw = ((exit_px - pos['entry']) / pos['entry']) if pos['dir'] == 'long' else ((pos['entry'] - exit_px) / pos['entry'])
                pnl = raw - 0.0012
                trades.append({'dir': pos['dir'], 'pnl': pnl, 'score': pos['score'], 'reason': reason})
                in_pos = False
        
        if not in_pos and squeeze_dir and not squeeze_active:
            atr = row['atr'] if pd.notna(row['atr']) else (row['high'] - row['low'])
            if atr == 0:
                continue
            
            if squeeze_dir == 'long' and row['close'] > row['ema20']:
                sl = row['close'] - atr * sl_mult
                tp = row['close'] + atr * sl_mult * tp_mult
                in_pos = True
                pos = {'dir': 'long', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': 70}
            elif squeeze_dir == 'short' and row['close'] < row['ema20']:
                sl = row['close'] + atr * sl_mult
                tp = row['close'] - atr * sl_mult * tp_mult
                in_pos = True
                pos = {'dir': 'short', 'entry': row['close'], 'sl': sl, 'tp': tp, 'score': 70}
            
            squeeze_dir = None
    
    return trades


# ════════════════════════════════════════════════════════════
# GRID SEARCH
# ════════════════════════════════════════════════════════════
STRATEGIES = {
    'Trend-Following': strategy_trend_following,
    'Mean-Reversion': strategy_mean_reversion,
    'Breakout': strategy_breakout,
    'Range-Bound': strategy_range_bound,
    'Vol-Expansion': strategy_vol_expansion,
}

PARAM_GRID = {
    'Trend-Following': [
        {'fast': 9, 'slow': 21, 'trend': 50, 'sl_mult': 1.5, 'tp_mult': 3.0, 'risk': 0.02},
        {'fast': 9, 'slow': 21, 'trend': 50, 'sl_mult': 2.0, 'tp_mult': 4.0, 'risk': 0.02},
        {'fast': 12, 'slow': 26, 'trend': 50, 'sl_mult': 1.5, 'tp_mult': 3.5, 'risk': 0.02},
    ],
    'Mean-Reversion': [
        {'bb_period': 20, 'bb_std': 2.5, 'rsi_long': 20, 'rsi_short': 80, 'sl_mult': 1.0, 'tp_mult': 2.0},
        {'bb_period': 20, 'bb_std': 2.0, 'rsi_long': 25, 'rsi_short': 75, 'sl_mult': 1.5, 'tp_mult': 2.5},
        {'bb_period': 14, 'bb_std': 2.5, 'rsi_long': 20, 'rsi_short': 80, 'sl_mult': 1.0, 'tp_mult': 1.5},
    ],
    'Breakout': [
        {'lookback': 20, 'vol_mult': 1.3, 'sl_mult': 1.5, 'tp_mult': 3.0},
        {'lookback': 15, 'vol_mult': 1.5, 'sl_mult': 1.5, 'tp_mult': 4.0},
        {'lookback': 25, 'vol_mult': 1.8, 'sl_mult': 2.0, 'tp_mult': 3.0},
    ],
    'Range-Bound': [
        {'sl_mult': 1.0, 'tp_mult': 2.0},
        {'sl_mult': 1.5, 'tp_mult': 3.0},
    ],
    'Vol-Expansion': [
        {'bb_period': 20, 'squeeze_mult': 2.0, 'sl_mult': 2.0, 'tp_mult': 4.0},
        {'bb_period': 14, 'squeeze_mult': 2.0, 'sl_mult': 1.5, 'tp_mult': 3.0},
    ],
}


def calc_metrics(trades: List[dict], coin: str) -> dict:
    if not trades:
        return None
    
    equity = 100.0
    eq_curve = [100.0]
    for t in trades:
        equity *= (1 + t['pnl'])
        eq_curve.append(equity)
    
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    
    wr = len(wins) / len(trades)
    
    gross_profit = sum(t['pnl'] for t in wins)
    gross_loss = abs(sum(t['pnl'] for t in losses))
    pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    peak = 100.0
    mdd = 0
    for e in eq_curve:
        if e > peak:
            peak = e
        dd = (peak - e) / peak
        if dd > mdd:
            mdd = dd
    
    ret = (equity - 100) / 100
    
    # Project 30-day return (assuming same number of trades)
    trades_per_month = len(trades)
    avg_pnl = np.mean([t['pnl'] for t in trades])
    proj_30d = ((1 + avg_pnl) ** trades_per_month - 1) * 100
    
    # Score for ranking
    score = pf * wr * (1 - mdd)
    
    return {
        'coin': coin,
        'trades': len(trades),
        'winrate': wr,
        'pf': pf,
        'return': ret * 100,
        'mdd': mdd * 100,
        'equity': equity,
        'proj_30d': proj_30d,
        'avg_pnl': avg_pnl * 100,
        'score': score,
    }


def run_grid_search():
    print(f"\n{'='*80}")
    print(f"  STRATEGY GRID SEARCH: 6 MONTHS | {len(COINS)} COINS | 30-DAY PROJECTION")
    print(f"{'='*80}")
    
    all_results = []
    
    for coin in COINS:
        print(f"\n{'─'*60}")
        print(f"  Coin: {coin}")
        print(f"{'─'*60}")
        
        try:
            df = load_data(coin, "15m")
            if len(df) < 500:
                print(f"  Skipping (only {len(df)} bars)")
                continue
            
            for strat_name, strat_fn in STRATEGIES.items():
                for params in PARAM_GRID[strat_name]:
                    try:
                        trades = strat_fn(df, params)
                        metrics = calc_metrics(trades, coin)
                        
                        if metrics and metrics['trades'] >= 10:
                            metrics['strategy'] = strat_name
                            metrics['params'] = str(params)
                            all_results.append(metrics)
                            
                            pf_str = f"{metrics['pf']:.2f}"
                            ret_str = f"{metrics['return']:+.1f}%"
                            proj_str = f"{metrics['proj_30d']:+.0f}%"
                            
                            print(f"  {strat_name:18s} {pf_str:6s} {metrics['winrate']*100:5.1f}% WR {ret_str:8s} (30d: {proj_str})")
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"  Error: {e}")
    
    # Rank by composite score (PF * Winrate * (1-DD))
    all_results.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"\n{'='*80}")
    print(f"  TOP 20 STRATEGIES (All Coins, All Periods)")
    print(f"{'='*80}")
    print(f"  {'Rank':>4} {'Coin':>10} {'Strategy':>15} {'PF':>6} {'WR':>6} {'Return':>8} {'30d Proj':>10} {'Drawdown':>9} {'Score':>8}")
    
    for i, r in enumerate(all_results[:20]):
        print(f"  {i+1:>4} {r['coin']:>10} {r['strategy']:>15} {r['pf']:>6.2f} {r['winrate']*100:>5.1f}% {r['return']:>7.1f}% {r['proj_30d']:>9.0f}% {r['mdd']:>7.1f}% {r['score']:>7.2f}")
    
    # Stats by strategy
    print(f"\n{'='*60}")
    print(f"  AVERAGE BY STRATEGY (All Coins)")
    print(f"{'='*60}")
    
    strat_stats = {}
    for r in all_results:
        s = r['strategy']
        if s not in strat_stats:
            strat_stats[s] = []
        strat_stats[s].append(r)
    
    for s, results in strat_stats.items():
        avg_pf = np.mean([r['pf'] for r in results])
        avg_wr = np.mean([r['winrate'] for r in results])
        avg_ret = np.mean([r['return'] for r in results])
        avg_dd = np.mean([r['mdd'] for r in results])
        avg_proj = np.mean([r['proj_30d'] for r in results])
        count = len(results)
        
        print(f"  {s:>15}: PF={avg_pf:>5.2f} WR={avg_wr*100:>5.1f}% Return={avg_ret:>6.1f}% DD={avg_dd:>6.1f}% 30dProj={avg_proj:>7.0f}% (n={count})")
    
    # Best per coin
    print(f"\n{'='*60}")
    print(f"  BEST STRATEGY PER COIN")
    print(f"{'='*60}")
    
    coin_best = {}
    for r in all_results:
        c = r['coin']
        if c not in coin_best or r['score'] > coin_best[c]['score']:
            coin_best[c] = r
    
    for coin, r in coin_best.items():
        print(f"  {coin:>10}: {r['strategy']:>15} PF={r['pf']:>5.2f} 30d={r['proj_30d']:>7.0f}% Equity=${r['equity']:>7.2f}")
    
    # Save results
    OUT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/experiments/trading_100e/data/grid_results.json")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump([{k: float(v) if isinstance(v, (np.floating, float)) and not isinstance(v, (bool,)) else v 
                  for k,v in r.items() if k != 'params'} for r in all_results], f, indent=2)
    print(f"\n\n  Results saved to {OUT}")
    
    return all_results


if __name__ == "__main__":
    import numpy as np
    run_grid_search()
