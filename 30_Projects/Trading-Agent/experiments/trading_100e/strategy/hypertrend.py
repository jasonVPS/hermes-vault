"""
Hyperliquid Aggressive Growth Strategy
Target: 100% in 30 days on Hyperliquid Perps
Focus: SOL, HYPE, ETH (higher beta than BTC)
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

import pandas as pd
import numpy as np
from core.data_cleaner import load_raw
from experiments.trading_100e.learn.engine import LearningEngine
from datetime import datetime, timedelta

class HyperTrendStrategy:
    """
    TREND-FOLLOWING MOMENTUM (not mean reversion!)
    
    HYPERLIQUID ADVANTAGES:
    - Perpetuals = no expiry, 24/7
    - Funding rates as sentiment indicator
    - Higher leverage = smaller moves matter
    
    STRATEGY RULES:
    --------------
    1. TREND (4h): Price > 50 EMA = BULL regime, only LONGS
                    Price < 50 EMA = BEAR regime, only SHORTS
    
    2. MOMENTUM (1h): RSI(14) > 50 and < 70 for LONGS
                      RSI(14) < 50 and > 30 for SHORTS
       → We trade WITH momentum, not against it
    
    3. BREAKOUT (15m): Price breaks above 20-period high (Long)
                       Price breaks below 20-period low (Short)
       → Entry on strength, not weakness
    
    4. VOLUME: > 1.5x 20-period average
    
    5. SETUP SCORE (0-100):
       - Trend alignment: +25
       - RSI in momentum zone: +20
       - Breakout confirmed: +20
       - Volume spike: +15
       - EMA slope steep: +10
       - ATR expansion: +10
    
    RISK FRAMEWORK FOR 100% IN 30 DAYS:
    ------------------------------------
    - Base risk: 5% per trade (Kelly optimal for 40% WR @ 3:1)
    - Max risk: 15% for "perfect storm" setups (score > 85)
    - Max 2 concurrent positions
    - Correlation hedge: No 2 LONGs on correlated assets
    
    EXITS (Aggressive Scaling):
    - SL: 2.0 ATR(14) from entry
    - TP1 (50%): 1.5 R  → Move SL to BE
    - TP2 (50%): 4.0 R  → Trailing SL at TP1
    - TP3: 8.0 R  → Trailing SL at TP2
    
    → Average R:R = 4.5:1
    → Required Winrate @ 4.5:1 = 18% (we target 40%+)
    """
    
    def __init__(self, params=None):
        defaults = {
            'trend_ema': 50,        # 4h trend
            'momentum_rsi': 14,     # 1h momentum
            'breakout_lookback': 20, # 15m
            'volume_avg': 20,
            'atr_period': 14,
            'sl_atr_mult': 2.0,
            'tp1_r': 1.5,
            'tp2_r': 4.0,
            'tp3_r': 8.0,
            'base_risk_pct': 0.05,
            'max_risk_pct': 0.15,
            'min_score': 50,
        }
        self.p = {**defaults, **(params or {})}
    
    def calc(self, df_15m, df_1h=None, df_4h=None):
        """Calculate all indicators"""
        df = df_15m.copy()
        
        # ATR
        prev = df['close'].shift(1)
        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - prev).abs()
        tr3 = (df['low'] - prev).abs()
        df['atr'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(self.p['atr_period']).mean()
        df['atr_pct'] = df['atr'] / df['close']
        
        # Trend from 1h (200-period roughly = 50 on 4h)
        df['ema_trend'] = df['close'].ewm(span=self.p['trend_ema'], adjust=False).mean()
        
        # RSI
        d = df['close'].diff()
        gain = d.clip(lower=0)
        loss = (-d).clip(lower=0)
        avg_g = gain.ewm(alpha=1/self.p['momentum_rsi'], adjust=False).mean()
        avg_l = loss.ewm(alpha=1/self.p['momentum_rsi'], adjust=False).mean()
        df['rsi'] = 100 - (100 / (1 + avg_g / avg_l))
        
        # Breakout levels
        df['highest_20'] = df['high'].rolling(self.p['breakout_lookback']).max()
        df['lowest_20'] = df['low'].rolling(self.p['breakout_lookback']).min()
        
        # Volume
        df['vol_avg'] = df['volume'].rolling(self.p['volume_avg']).mean()
        df['vol_ratio'] = df['volume'] / df['vol_avg']
        
        return df
    
    def scan(self, df_15m, equity=100, df_1h=None, df_4h=None):
        """Scan for signals on last bar"""
        df = self.calc(df_15m, df_1h, df_4h)
        
        if len(df) < 70:
            return None
        
        i = len(df) - 1
        row = df.iloc[i]
        
        if pd.isna(row['atr']) or row['atr'] == 0 or pd.isna(row['ema_trend']):
            return None
        
        price = row['close']
        atr = row['atr']
        rsi = row['rsi']
        trend_ema = row['ema_trend']
        
        score = 0
        reasons = []
        
        # Determine direction from trend
        if price > trend_ema:
            # BULL regime - ONLY longs
            if rsi < 50 or rsi > 75:
                return None  # Too weak or too overbought
            
            # Breakout check
            if row['high'] >= row['highest_20'] * 0.999:
                score += 30
                reasons.append("HIGH_BREAKOUT")
            elif price > row['highest_20'] * 0.998:
                score += 15
                reasons.append("NEAR_HIGH")
            else:
                return None
            
            # RSI momentum
            if 55 <= rsi <= 65:
                score += 25
                reasons.append("RSI_SWEET")
            elif 50 <= rsi < 75:
                score += 15
                reasons.append("RSI_OK")
            
            # Volume
            if row['vol_ratio'] > 1.8:
                score += 20
                reasons.append("VOL_SPIKE")
            elif row['vol_ratio'] > 1.3:
                score += 10
                reasons.append("VOL_OK")
            
            # Trend steepness
            ema_slope = (trend_ema - df['ema_trend'].iloc[i-5]) / trend_ema
            if ema_slope > 0.005:
                score += 15
                reasons.append("STEEP_UP")
            
            # ATR expansion
            if row['atr_pct'] > df['atr_pct'].rolling(20).mean().iloc[i] * 1.2:
                score += 10
                reasons.append("VOL_EXP")
            
            if score < self.p['min_score']:
                return None
            
            # Calculate levels
            sl = price - atr * self.p['sl_atr_mult']
            tp1 = price + atr * self.p['sl_atr_mult'] * self.p['tp1_r']
            tp2 = price + atr * self.p['sl_atr_mult'] * self.p['tp2_r']
            tp3 = price + atr * self.p['sl_atr_mult'] * self.p['tp3_r']
            
            # Risk sizing
            if score >= 85:
                risk_pct = min(self.p['max_risk_pct'], self.p['base_risk_pct'] * 3)
            elif score >= 70:
                risk_pct = self.p['base_risk_pct'] * 2
            elif score >= 55:
                risk_pct = self.p['base_risk_pct']
            else:
                return None
            
            sl_dist = price - sl
            size = equity * risk_pct / sl_dist
            
            return {
                'dir': 'long',
                'entry': price,
                'sl': sl,
                'tp1': tp1,
                'tp2': tp2,
                'tp3': tp3,
                'risk_pct': risk_pct,
                'size': size,
                'score': score,
                'reasons': reasons,
                'rr': (tp3 - price) / sl_dist,
            }
        
        else:
            # BEAR regime - ONLY shorts
            if rsi > 50 or rsi < 25:
                return None
            
            if row['low'] <= row['lowest_20'] * 1.001:
                score += 30
                reasons.append("LOW_BREAKOUT")
            elif price < row['lowest_20'] * 1.002:
                score += 15
                reasons.append("NEAR_LOW")
            else:
                return None
            
            if 35 <= rsi <= 45:
                score += 25
                reasons.append("RSI_SWEET")
            elif 25 < rsi <= 50:
                score += 15
                reasons.append("RSI_OK")
            
            if row['vol_ratio'] > 1.8:
                score += 20
                reasons.append("VOL_SPIKE")
            elif row['vol_ratio'] > 1.3:
                score += 10
                reasons.append("VOL_OK")
            
            ema_slope = (trend_ema - df['ema_trend'].iloc[i-5]) / trend_ema
            if ema_slope < -0.005:
                score += 15
                reasons.append("STEEP_DOWN")
            
            if row['atr_pct'] > df['atr_pct'].rolling(20).mean().iloc[i] * 1.2:
                score += 10
                reasons.append("VOL_EXP")
            
            if score < self.p['min_score']:
                return None
            
            sl = price + atr * self.p['sl_atr_mult']
            tp1 = price - atr * self.p['sl_atr_mult'] * self.p['tp1_r']
            tp2 = price - atr * self.p['sl_atr_mult'] * self.p['tp2_r']
            tp3 = price - atr * self.p['sl_atr_mult'] * self.p['tp3_r']
            
            if score >= 85:
                risk_pct = min(self.p['max_risk_pct'], self.p['base_risk_pct'] * 3)
            elif score >= 70:
                risk_pct = self.p['base_risk_pct'] * 2
            elif score >= 55:
                risk_pct = self.p['base_risk_pct']
            else:
                return None
            
            sl_dist = sl - price
            size = equity * risk_pct / sl_dist
            
            return {
                'dir': 'short',
                'entry': price,
                'sl': sl,
                'tp1': tp1,
                'tp2': tp2,
                'tp3': tp3,
                'risk_pct': risk_pct,
                'size': size,
                'score': score,
                'reasons': reasons,
                'rr': (price - tp3) / sl_dist,
            }
        
        return None


class HyperBacktest:
    def __init__(self):
        self.equity = 100.0
        self.trades = []
        self.equity_curve = [100.0]
        
    def run(self, df_15m):
        """Walk-forward backtest"""
        strat = HyperTrendStrategy()
        df = strat.calc(df_15m)
        
        in_pos = False
        pos = None
        
        for i in range(60, len(df) - 1):
            row = df.iloc[i]
            
            # Check exits
            if in_pos:
                exit_px = None
                reason = None
                tp_hit = 0
                
                # Update trailing stops if TPs hit
                if not pos.get('tp1_hit', False):
                    if pos['dir'] == 'long' and row['high'] >= pos['tp1']:
                        pos['tp1_hit'] = True
                        pos['current_sl'] = max(pos['current_sl'], pos['entry'] * 0.999)
                        tp_hit = 1
                    elif pos['dir'] == 'short' and row['low'] <= pos['tp1']:
                        pos['tp1_hit'] = True
                        pos['current_sl'] = min(pos['current_sl'], pos['entry'] * 1.001)
                        tp_hit = 1
                
                if pos.get('tp1_hit', False) and not pos.get('tp2_hit', False):
                    if pos['dir'] == 'long' and row['high'] >= pos['tp2']:
                        pos['tp2_hit'] = True
                        pos['current_sl'] = pos['tp1']
                        tp_hit = 2
                    elif pos['dir'] == 'short' and row['low'] <= pos['tp2']:
                        pos['tp2_hit'] = True
                        pos['current_sl'] = pos['tp1']
                        tp_hit = 2
                
                if pos.get('tp2_hit', False):
                    if pos['dir'] == 'long' and row['high'] >= pos['tp3']:
                        exit_px = pos['tp3']
                        reason = "TP3"
                        tp_hit = 3
                    elif pos['dir'] == 'short' and row['low'] <= pos['tp3']:
                        exit_px = pos['tp3']
                        reason = "TP3"
                        tp_hit = 3
                
                # SL check
                if exit_px is None:
                    if pos['dir'] == 'long' and row['low'] <= pos['current_sl']:
                        exit_px = pos['current_sl']
                        reason = "SL"
                    elif pos['dir'] == 'short' and row['high'] >= pos['current_sl']:
                        exit_px = pos['current_sl']
                        reason = "SL"
                
                # Max hold: 48 bars (12h)
                if exit_px is None and i - pos['idx'] > 48:
                    exit_px = row['close']
                    reason = "TIME"
                
                if exit_px:
                    if pos['dir'] == 'long':
                        raw = (exit_px - pos['entry']) / pos['entry']
                    else:
                        raw = (pos['entry'] - exit_px) / pos['entry']
                    
                    costs = 0.0012  # 0.12% taker fees
                    pnl = raw - costs
                    pnl_abs = pnl * self.equity
                    self.equity += pnl_abs
                    
                    self.trades.append({
                        'dir': pos['dir'], 'entry': pos['entry'], 'exit': exit_px,
                        'sl': pos['sl'], 'tp3': pos['tp3'], 'pnl': pnl,
                        'reason': reason, 'tp_hit': tp_hit, 'score': pos['score']
                    })
                    self.equity_curve.append(self.equity)
                    in_pos = False
                    pos = None
            
            # Check entry
            if not in_pos and i < len(df) - 2:
                df_slice = df.iloc[:i+1].copy()
                sig = strat.scan(df_slice, self.equity)
                
                if sig:
                    risk_usd = self.equity * sig['risk_pct']
                    sl_dist = abs(sig['entry'] - sig['sl'])
                    if sl_dist > 0:
                        in_pos = True
                        pos = {
                            'dir': sig['dir'],
                            'entry': sig['entry'],
                            'sl': sig['sl'],
                            'current_sl': sig['sl'],
                            'tp1': sig['tp1'],
                            'tp2': sig['tp2'],
                            'tp3': sig['tp3'],
                            'idx': i,
                            'score': sig['score'],
                            'risk_pct': sig['risk_pct'],
                        }
        
        return self._report()
    
    def _report(self):
        if not self.trades:
            print("NO TRADES")
            return
        
        wins = [t for t in self.trades if t['pnl'] > 0]
        losses = [t for t in self.trades if t['pnl'] <= 0]
        wr = len(wins) / len(self.trades) if self.trades else 0
        
        ret = (self.equity - 100) / 100 * 100
        
        peak = 100.0
        mdd = 0
        for e in self.equity_curve:
            if e > peak: peak = e
            dd = (peak - e) / peak
            if dd > mdd: mdd = dd
        
        gp = sum(t['pnl'] for t in wins)
        gl = abs(sum(t['pnl'] for t in losses))
        pf = gp / gl if gl > 0 else 999
        
        sharpe = np.mean([t['pnl'] for t in self.trades]) / np.std([t['pnl'] for t in self.trades]) * np.sqrt(len(self.trades)) if len(self.trades) > 1 else 0
        
        print(f"\n{'='*60}")
        print(f"  HYPERTREND BACKTEST")
        print(f"{'='*60}")
        print(f"  Trades: {len(self.trades)} | Wins: {len(wins)} | Losses: {len(losses)}")
        print(f"  Winrate: {wr*100:.1f}%")
        print(f"  Profit Factor: {pf:.2f}")
        print(f"  Sharpe: {sharpe:.2f}")
        print(f"  Final Equity: ${self.equity:.2f}")
        print(f"  Return: {ret:+.2f}%")
        print(f"  Max DD: {mdd*100:.2f}%")
        
        print(f"\n  TP Distribution: SL={sum(1 for t in self.trades if t['reason']=='SL')} | TP1={sum(1 for t in self.trades if t['tp_hit']==1)} | TP2={sum(1 for t in self.trades if t['tp_hit']==2)} | TP3={sum(1 for t in self.trades if t['reason']=='TP3')}")
        
        # Projection
        monthly_trades = len(self.trades)
        daily_avg = (self.equity - 100) / len(self.trades) if self.trades else 0
        proj_30d = 100 * (1 + daily_avg / 100) ** 30 if daily_avg > 0 else 100
        print(f"\n  Projection (30 days, same rate): ${proj_30d:.2f}")
        
        print(f"\n  Last 5 trades:")
        for t in self.trades[-5:]:
            print(f"    {t['dir']:5s} {t['entry']:8.2f} → {t['exit']:8.2f} | {t['pnl']*100:+.2f}% | {t['reason']:6s} | Score {t['score']}")


if __name__ == "__main__":
    import numpy as np
    for sym in ["BTC/USDT", "ETH/USDT", "SOL/USDT"]:
        try:
            df = load_raw(sym, "15m")
            print(f"\n{'#'*60}")
            print(f"# {sym}")
            print(f"{'#'*60}")
            bt = HyperBacktest()
            bt.run(df)
        except Exception as e:
            print(f"Error on {sym}: {e}")
