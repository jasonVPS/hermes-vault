"""
Adaptive Scalping Strategy for 100€ → 200€ in 30 days
Timeframe: 15m primary, 1h trend filter
3 TPs, dynamic position sizing, trailing SL
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

import numpy as np
import pandas as pd
from core.data_cleaner import load_raw, clean_wicks
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime
import json
import sqlite3

@dataclass
class Signal:
    dir: str                    # 'long' or 'short'
    entry: float
    sl: float
    tp1: float                  # 25% position
    tp2: float                  # 25% position
    tp3: float                  # 50% position
    size_pct: float             # % of equity (0.01 to 0.05)
    setup_score: float          # 0-100
    reasons: List[str]          # transparency

class ScalpingStrategy:
    """
    TREND-PULLBACK STRATEGY
    ----------------------
    1. TREND (1h): Price must be aligned with 200 EMA
       - Long only if close > EMA200
       - Short only if close < EMA200
    
    2. PULLBACK (15m): RSI oversold/overbought in trend direction
       - Long: Price touches lower 20-EMA band (15m) + RSI < 40
       - Short: Price touches upper 20-EMA band (15m) + RSI > 60
    
    3. CONFIRMATION: Volume spike (> 1.3x 20-period average)
       OR bullish/bearish engulfing on 15m
    
    4. SETUP SCORE (0-100):
       - Trend alignment: +30
       - RSI extreme: +20 (RSI<30 for long, >70 for short)
       - Volume confirmation: +15
       - Price at support/resistance: +15
       - No major news/whale volatility: +10
       - EMA slope steep: +10
    
    RISK & PROFITS
    --------------
    Entry: Market oder Limit bei EMA-Band
    SL: 1.5 ATR (14) oder unter/over letztes Swing-Low/High
    TP1 (25%): 1.0 R (SL-Abstand)
    TP2 (25%): 2.0 R
    TP3 (50%): 3.5 R (Trend-Continuation)
    
    DYNAMIC RISK
    ------------
    Base: 1% of equity per trade
    Adjusted by setup_score:
       0-50:  0.5%
       50-70: 1.0%
       70-85: 2.0%
       85+:   4.0% (nur bei "perfect storm")
    
    STOP MANAGEMENT
    ---------------
    - TP1 hit: Move SL to breakeven + 0.1%
    - TP2 hit: Move SL to TP1 level (lock 1R)
    - Wenn price 5m close gegen Trend schließt: Früher aussteigen
    - Max hold time: 8h (32 bars @ 15m), sonst manuell schließen
    """
    
    def __init__(self, params=None):
        self.p = params or {
            'ema_fast': 9,
            'ema_slow': 21,
            'ema_trend': 200,
            'rsi_period': 14,
            'volume_avg': 20,
            'atr_period': 14,
            'sl_atr_mult': 1.5,
            'tp1_r': 1.0,
            'tp2_r': 2.0,
            'tp3_r': 3.5,
            'base_risk_pct': 0.01,
            'rsi_long_thresh': 40,
            'rsi_short_thresh': 60,
            'vol_mult': 1.3,
            'max_hold_bars': 32,  # 8h @ 15m
            'break_even_buffer': 0.001,  # 0.1%
        }
    
    def atr(self, series_high, series_low, series_close, period=14):
        prev_close = series_close.shift(1)
        tr1 = series_high - series_low
        tr2 = (series_high - prev_close).abs()
        tr3 = (series_low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.ewm(span=period, adjust=False).mean()
    
    def calculate(self, df_15m, df_1h=None):
        """Calculate all indicators. If df_1h provided, use last known trend."""
        df = df_15m.copy()
        
        # EMAs
        df['ema_f'] = df['close'].ewm(span=self.p['ema_fast'], adjust=False).mean()
        df['ema_s'] = df['close'].ewm(span=self.p['ema_slow'], adjust=False).mean()
        
        # ATR
        df['atr'] = self.atr(df['high'], df['low'], df['close'], self.p['atr_period'])
        
        # RSI
        d = df['close'].diff()
        gain = d.where(d > 0, 0.0)
        loss = (-d).where(d < 0, 0.0)
        avg_g = gain.ewm(alpha=1/self.p['rsi_period'], adjust=False).mean()
        avg_l = loss.ewm(alpha=1/self.p['rsi_period'], adjust=False).mean()
        rs = avg_g / avg_l
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Volume
        df['vol_avg'] = df['volume'].rolling(self.p['volume_avg']).mean()
        df['vol_ratio'] = df['volume'] / df['vol_avg']
        
        # Bollinger für Pullback-Zone
        df['bb_mid'] = df['close'].rolling(20).mean()
        df['bb_std'] = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
        df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
        
        # Trend filter from 1h if available
        if df_1h is not None and len(df_1h) > 0:
            df_1h = df_1h.copy()
            df_1h['ema200'] = df_1h['close'].ewm(span=200, adjust=False).mean()
            # Map 1h trend to 15m bars (forward fill)
            df_1h_map = df_1h[['timestamp', 'ema200']].set_index('timestamp')
            df['trend_ema200'] = df['timestamp'].map(lambda x: df_1h_map.loc[:x].iloc[-1]['ema200'] if len(df_1h_map.loc[:x]) > 0 else None)
        else:
            # Fallback: 200-period EMA on 15m
            df['trend_ema200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        return df
    
    def score(self, row, price, atr, rsi, trend_ema, ema_f, ema_s):
        """Calculate setup score 0-100"""
        score = 0
        reasons = []
        
        # Trend alignment (30 pts)
        if price > trend_ema:
            score += 30
            reasons.append("TREND_UP")
        elif price < trend_ema:
            score += 30
            reasons.append("TREND_DOWN")
        
        # RSI extreme (20 pts)
        if rsi < 30:
            score += 20
            reasons.append("RSI_OVERSOLD")
        elif rsi > 70:
            score += 20
            reasons.append("RSI_OVERBOUGHT")
        elif rsi < 40 or rsi > 60:
            score += 10
            reasons.append("RSI_PULLBACK")
        
        # Volume (15 pts)
        if row['vol_ratio'] > 2.0:
            score += 15
            reasons.append("VOL_SPIKE")
        elif row['vol_ratio'] > 1.3:
            score += 8
            reasons.append("VOL_CONFIRM")
        
        # Price at band (15 pts)
        if price < row['bb_lower']:
            score += 15
            reasons.append("AT_LOWER_BAND")
        elif price > row['bb_upper']:
            score += 15
            reasons.append("AT_UPPER_BAND")
        elif abs(price - row['bb_mid']) / price < 0.005:
            score += 5
            reasons.append("AT_MID_BAND")
        
        # No volatility spike (10 pts)
        atr_pct = atr / price
        if atr_pct < 0.02:  # < 2% ATR
            score += 10
            reasons.append("LOW_VOL")
        
        # EMA slope (10 pts)
        slope = (ema_f - ema_s) / ema_s
        if abs(slope) > 0.005:
            score += 10
            reasons.append("STEEP_EMA")
        
        return score, reasons
    
    def generate(self, df, equity=100, df_1h=None):
        """
        Returns Signal or None
        Scans last bar for setup
        """
        df = self.calculate(df, df_1h)
        
        if len(df) < 210:  # 200 + buffer
            return None
        
        i = len(df) - 1
        row = df.iloc[i]
        
        price = row['close']
        atr = row['atr']
        rsi = row['rsi']
        trend_ema = row['trend_ema200']
        
        if pd.isna(trend_ema) or pd.isna(atr) or atr == 0:
            return None
        
        setup_score, reasons = self.score(row, price, atr, rsi, trend_ema, row['ema_f'], row['ema_s'])
        
        # Minimum score to trade
        if setup_score < 40:
            return None
        
        # Determine direction
        if price > trend_ema and rsi < self.p['rsi_long_thresh']:
            dir = 'long'
        elif price < trend_ema and rsi > self.p['rsi_short_thresh']:
            dir = 'short'
        else:
            return None
        
        # Calculate levels
        if dir == 'long':
            sl = price - atr * self.p['sl_atr_mult']
            tp1 = price + atr * self.p['tp1_r'] * self.p['sl_atr_mult']
            tp2 = price + atr * self.p['tp2_r'] * self.p['sl_atr_mult']
            tp3 = price + atr * self.p['tp3_r'] * self.p['sl_atr_mult']
        else:
            sl = price + atr * self.p['sl_atr_mult']
            tp1 = price - atr * self.p['tp1_r'] * self.p['sl_atr_mult']
            tp2 = price - atr * self.p['tp2_r'] * self.p['sl_atr_mult']
            tp3 = price - atr * self.p['tp3_r'] * self.p['sl_atr_mult']
        
        # Validate TP1 makes sense (must be > 0.3% from entry)
        if abs(tp1 - price) / price < 0.003:
            return None
        
        # Dynamic position sizing
        if setup_score >= 85:
            size_pct = min(0.05, self.p['base_risk_pct'] * 4)
        elif setup_score >= 70:
            size_pct = min(0.03, self.p['base_risk_pct'] * 2)
        elif setup_score >= 50:
            size_pct = self.p['base_risk_pct']
        else:
            size_pct = self.p['base_risk_pct'] * 0.5
        
        # Cap risk based on ATR% (dont trade if > 3% ATR)
        atr_pct = atr / price
        if atr_pct > 0.03:
            return None
        
        return Signal(
            dir=dir,
            entry=round(price, 2),
            sl=round(sl, 2),
            tp1=round(tp1, 2),
            tp2=round(tp2, 2),
            tp3=round(tp3, 2),
            size_pct=round(size_pct, 4),
            setup_score=setup_score,
            reasons=reasons
        )


if __name__ == "__main__":
    # Quick test
    df_raw = load_raw("BTC/USDT", "1h")
    df_clean = clean_wicks(df_raw, max_wick_pct=0.05)
    
    strat = ScalpingStrategy()
    sig = strat.generate(df_clean, equity=100)
    
    if sig:
        print(f"SIGNAL: {sig.dir} @ {sig.entry}")
        print(f"  SL: {sig.sl} | TP1: {sig.tp1} | TP2: {sig.tp2} | TP3: {sig.tp3}")
        print(f"  Size: {sig.size_pct*100}% of equity | Score: {sig.setup_score}/100")
        print(f"  Reasons: {', '.join(sig.reasons)}")
    else:
        print("No signal on current data")
