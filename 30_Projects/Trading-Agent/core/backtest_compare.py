"""
Strategy Backtest Engine v2.1
Three clean strategies tested against each other:
1. EMA_Cross: Fast/Slow EMA crossover + RSI filter
2. MeanReversion: RSI oversold/overbought + Bollinger Bands
3. Breakout: ATR channel breakout + volume
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

from core.data_cleaner import load_raw, clean_wicks
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict

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
    
class BaseStrategy:
    def __init__(self, risk_pct=0.01, sl_mult=2.0, tp_mult=3.0, fee=0.0006, slippage=0.0002):
        self.risk_pct = risk_pct
        self.sl_mult = sl_mult
        self.tp_mult = tp_mult
        self.fee = fee
        self.slippage = slippage
    
    def calc_atr(self, df, length=14):
        prev_close = df['close'].shift(1)
        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - prev_close).abs()
        tr3 = (df['low'] - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.ewm(span=length, adjust=False).mean()

# ████████████████████████████████████████████████████████████
# STRATEGY 1: EMA CROSSOVER
# ████████████████████████████████████████████████████████████
class EMA_Cross_Strategy(BaseStrategy):
    """
    ENTRY:
    - EMA(fast) crosses above EMA(slow) -> LONG
    - EMA(fast) crosses below EMA(slow) -> SHORT
    - RSI confirms: LONG if RSI < 70 (not overbought), SHORT if RSI > 30
    
    EXIT:
    - SL: entry ± ATR * sl_mult
    - TP: entry ± ATR * tp_mult
    - Optional: EMA reverse cross
    """
    def __init__(self, fast=9, slow=21, rsi_p=14, **kwargs):
        super().__init__(**kwargs)
        self.fast = fast
        self.slow = slow
        self.rsi_p = rsi_p
    
    def indicators(self, df):
        df = df.copy()
        df['ema_f'] = df['close'].ewm(span=self.fast, adjust=False).mean()
        df['ema_s'] = df['close'].ewm(span=self.slow, adjust=False).mean()
        df['atr'] = self.calc_atr(df)
        
        # RSI
        d = df['close'].diff()
        gain = d.where(d > 0, 0.0)
        loss = (-d).where(d < 0, 0.0)
        avg_g = gain.ewm(alpha=1/self.rsi_p, adjust=False).mean()
        avg_l = loss.ewm(alpha=1/self.rsi_p, adjust=False).mean()
        rs = avg_g / avg_l
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Crossover
        prev_f = df['ema_f'].shift(1)
        prev_s = df['ema_s'].shift(1)
        df['cross'] = np.where(
            (df['ema_f'] > df['ema_s']) & (prev_f <= prev_s), 1,
            np.where((df['ema_f'] < df['ema_s']) & (prev_f >= prev_s), -1, 0)
        )
        return df
    
    def signal(self, df, i, equity):
        row = df.iloc[i]
        if row['cross'] == 0 or pd.isna(row['atr']) or row['atr'] == 0:
            return None
        
        price = row['close']
        atr = row['atr']
        rsi = row['rsi']
        
        if row['cross'] == 1 and rsi < 70:  # Bull cross
            sl = price - atr * self.sl_mult
            tp = price + atr * self.tp_mult
            risk = equity * self.risk_pct
            size = risk / (price - sl)
            return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':risk,'reason':'EMA_CROSS_BULL'}
        
        if row['cross'] == -1 and rsi > 30:  # Bear cross
            sl = price + atr * self.sl_mult
            tp = price - atr * self.tp_mult
            risk = equity * self.risk_pct
            size = risk / (sl - price)
            return {'dir':'short','entry':price,'sl':sl,'tp':tp,'size':size,'risk':risk,'reason':'EMA_CROSS_BEAR'}
        return None

# ████████████████████████████████████████████████████████████
# STRATEGY 2: MEAN REVERSION (BOLLINGER)
# ████████████████████████████████████████████████████████████
class MeanRev_Strategy(BaseStrategy):
    """
    ENTRY:
    - Price touches lower Bollinger Band (oversold) -> LONG
    - Price touches upper Bollinger Band (overbought) -> SHORT
    - RSI confirms: LONG if RSI < 35, SHORT if RSI > 65
    
    EXIT:
    - SL: Beyond the band (mean ± 3*std)
    - TP: Back to mean (middle band)
    """
    def __init__(self, bb_p=20, bb_std=2.0, **kwargs):
        super().__init__(**kwargs)
        self.bb_p = bb_p
        self.bb_std = bb_std
    
    def indicators(self, df):
        df = df.copy()
        df['sma'] = df['close'].rolling(self.bb_p).mean()
        df['std'] = df['close'].rolling(self.bb_p).std()
        df['upper'] = df['sma'] + self.bb_std * df['std']
        df['lower'] = df['lower'] = df['sma'] - self.bb_std * df['std']
        df['atr'] = self.calc_atr(df)
        
        # RSI
        d = df['close'].diff()
        gain = d.where(d > 0, 0.0)
        loss = (-d).where(d < 0, 0.0)
        avg_g = gain.ewm(alpha=1/14, adjust=False).mean()
        avg_l = loss.ewm(alpha=1/14, adjust=False).mean()
        rs = avg_g / avg_l
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def signal(self, df, i, equity):
        row = df.iloc[i]
        if pd.isna(row['lower']) or pd.isna(row['upper']):
            return None
        
        price = row['close']
        atr = row['atr'] if pd.notna(row['atr']) else (row['high'] - row['low']) * 0.5
        
        # LONG: Price below lower band + RSI oversold
        if price < row['lower'] and row['rsi'] < 35:
            sl = row['sma'] - 3 * row['std']  # Beyond 3 std
            tp = row['sma']  # Mean reversion target
            sl_dist = abs(price - sl)
            risk = equity * self.risk_pct
            size = risk / sl_dist if sl_dist > 0 else 0
            rr = abs(tp - price) / sl_dist if sl_dist > 0 else 0
            if rr >= 1.5:  # Minimum R:R
                return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':risk,'reason':'BB_OVERSOLD'}
        
        # SHORT: Price above upper band + RSI overbought
        if price > row['upper'] and row['rsi'] > 65:
            sl = row['sma'] + 3 * row['std']
            tp = row['sma']
            sl_dist = abs(sl - price)
            risk = equity * self.risk_pct
            size = risk / sl_dist if sl_dist > 0 else 0
            rr = abs(price - tp) / sl_dist if sl_dist > 0 else 0
            if rr >= 1.5:
                return {'dir':'short','entry':price,'sl':sl,'tp':tp,'size':size,'risk':risk,'reason':'BB_OVERBOUGHT'}
        
        return None

# ████████████████████████████████████████████████████████████
# STRATEGY 3: ATR BREAKOUT
# ████████████████████████████████████████████████████████████
class Breakout_Strategy(BaseStrategy):
    """
    ENTRY:
    - Price closes above (prev_high + ATR*0.5) -> LONG
    - Price closes below (prev_low - ATR*0.5) -> SHORT
    - Filter: Volume > 1.5x average
    
    EXIT:
    - SL: Breakout level ± ATR
    - TP: 2x ATR or trailing
    """
    def __init__(self, lookback=20, vol_mult=1.5, **kwargs):
        super().__init__(**kwargs)
        self.lookback = lookback
        self.vol_mult = vol_mult
    
    def indicators(self, df):
        df = df.copy()
        df['atr'] = self.calc_atr(df)
        df['highest'] = df['high'].rolling(self.lookback).max().shift(1)
        df['lowest'] = df['low'].rolling(self.lookback).min().shift(1)
        df['vol_avg'] = df['volume'].rolling(20).mean()
        return df
    
    def signal(self, df, i, equity):
        row = df.iloc[i]
        prev = df.iloc[i-1] if i > 0 else row
        
        if pd.isna(row['highest']) or pd.isna(row['atr']):
            return None
        
        price = row['close']
        atr = row['atr']
        vol_ok = pd.notna(row['vol_avg']) and row['volume'] > self.vol_mult * row['vol_avg']
        
        if not vol_ok:
            return None
        
        # LONG breakout
        breakout_long = price > (row['highest'] + 0.5 * atr)
        if breakout_long:
            sl = row['highest'] - atr  # Below breakout level
            tp = price + atr * self.tp_mult
            risk = equity * self.risk_pct
            size = risk / (price - sl)
            return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':risk,'reason':'HIGH_BREAKOUT'}
        
        # SHORT breakout
        breakout_short = price < (row['lowest'] - 0.5 * atr)
        if breakout_short:
            sl = row['lowest'] + atr
            tp = price - atr * self.tp_mult
            risk = equity * self.risk_pct
            size = risk / (sl - price)
            return {'dir':'short','entry':price,'sl':sl,'tp':tp,'size':size,'risk':risk,'reason':'LOW_BREAKOUT'}
        
        return None


# ████████████████████████████████████████████████████████████
# BACKTEST ENGINE
# ████████████████████████████████████████████████████████████
class Engine:
    def __init__(self, strategy, equity=10000):
        self.s = strategy
        self.initial = equity
        self.trades: List[Trade] = []
    
    def run(self, df_raw):
        df = self.s.indicators(df_raw)
        equity = self.initial
        active = None
        
        for i in range(50, len(df)):
            row = df.iloc[i]
            
            # Check exits
            if active:
                exit_px = None
                reason = ""
                
                if active.dir == 'long':
                    if row['low'] <= active.sl:
                        exit_px = active.sl
                        reason = "SL"
                    elif row['high'] >= active.tp:
                        exit_px = active.tp
                        reason = "TP"
                else:
                    if row['high'] >= active.sl:
                        exit_px = active.sl
                        reason = "SL"
                    elif row['low'] <= active.tp:
                        exit_px = active.tp
                        reason = "TP"
                
                if exit_px:
                    active.exit_time = row['timestamp']
                    active.exit_price = exit_px
                    active.exit_reason = reason
                    active.bars_held = i - df.index[df['timestamp'] == active.entry_time].tolist()[0]
                    
                    if active.dir == 'long':
                        raw = (exit_px - active.entry_price) / active.entry_price
                    else:
                        raw = (active.entry_price - exit_px) / active.entry_price
                    
                    costs = self.s.fee * 2 + self.s.slippage * 2
                    active.pnl_pct = raw - costs
                    active.pnl_abs = active.pnl_pct * active.entry_price * active.size
                    equity += active.pnl_abs
                    
                    self.trades.append(active)
                    active = None
            
            # Check entries (only if no active trade)
            if not active and i < len(df) - 1:
                sig = self.s.signal(df, i, equity)
                if sig:
                    active = Trade(
                        entry_time=row['timestamp'],
                        dir=sig['dir'],
                        entry_price=sig['entry'],
                        sl=sig['sl'],
                        tp=sig['tp'],
                        size=sig['size'],
                        risk_usd=sig['risk']
                    )
        
        return self.metrics(equity)
    
    def metrics(self, final):
        if not self.trades:
            return self._empty(final)
        
        wins = [t for t in self.trades if t.pnl_pct > 0]
        losses = [t for t in self.trades if t.pnl_pct <= 0]
        
        win_p = len(wins)/len(self.trades)
        avg_w = np.mean([t.pnl_pct for t in wins]) if wins else 0
        avg_l = np.mean([t.pnl_pct for t in losses]) if losses else 0
        
        gross_profit = sum(t.pnl_pct for t in wins)
        gross_loss = abs(sum(t.pnl_pct for t in losses))
        pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Drawdown
        eq = [self.initial]
        for t in self.trades:
            eq.append(eq[-1] + t.pnl_abs)
        peak = eq[0]
        mdd = 0
        for e in eq:
            if e > peak: peak = e
            dd = (peak - e)/peak
            if dd > mdd: mdd = dd
        
        # Sharpe (annualized from per-trade)
        rets = [t.pnl_pct for t in self.trades]
        sharpe = np.mean(rets)/np.std(rets) * np.sqrt(len(rets)) if np.std(rets)>0 else 0
        
        return {
            'trades': len(self.trades), 'wins': len(wins), 'losses': len(losses),
            'winrate': win_p, 'profit_factor': pf,
            'avg_win': avg_w, 'avg_loss': avg_l,
            'final_equity': final, 'return_pct': (final-self.initial)/self.initial*100,
            'max_dd_pct': mdd*100, 'sharpe': sharpe,
            'avg_bars': np.mean([t.bars_held for t in self.trades])
        }
    
    def _empty(self, final):
        return {'trades':0, 'final_equity':final, 'return_pct':0}


def test_all(symbol="BTC/USDT", tf="1h"):
    df_raw = load_raw(symbol, tf)
    df_clean = clean_wicks(df_raw, max_wick_pct=0.05)
    print(f"\n{'='*60}")
    print(f" {symbol} @ {tf} | {len(df_clean)} bars")
    print(f"{'='*60}")
    
    strategies = [
        ("EMA_Cross", EMA_Cross_Strategy(fast=9, slow=21, sl_mult=2.0, tp_mult=4.0)),
        ("MeanRev_BB", MeanRev_Strategy(bb_p=20, bb_std=2.0, sl_mult=2.0, tp_mult=3.0)),
        ("Breakout_ATR", Breakout_Strategy(lookback=20, vol_mult=1.5, sl_mult=1.5, tp_mult=3.0)),
    ]
    
    results = {}
    for name, strat in strategies:
        bt = Engine(strat, equity=10000)
        m = bt.run(df_clean)
        results[name] = m
        
        print(f"\n{'─'*50}")
        print(f"📊 {name}")
        print(f"{'─'*50}")
        if m['trades'] == 0:
            print("  No trades generated")
            continue
        for k,v in m.items():
            if isinstance(v, float):
                print(f"  {k:15s}: {v:+.4f}" if k in ['avg_win','avg_loss','return_pct','sharpe'] else f"  {k:15s}: {v:.4f}")
            else:
                print(f"  {k:15s}: {v}")
        
        # Last 3 trades
        if bt.trades:
            print("  Last trades:")
            for t in bt.trades[-3:]:
                print(f"    {t.dir:5s} {t.entry_price:10.2f} -> {t.exit_price:10.2f} | {t.pnl_pct*100:+.2f}% | {t.exit_reason}")
    
    return results


if __name__ == "__main__":
    for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT"]:
        test_all(sym, "1h")
        print()
