"""
Strategy Backtest Engine v2 (Clean Data)
- Uses data_cleaner for artifact removal
- Transparent entry/exit/risk rules
- Comprehensive metrics
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

from core.data_cleaner import load_raw, clean_wicks
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: Optional[pd.Timestamp]
    dir: str  # 'long' or 'short'
    entry_price: float
    exit_price: Optional[float]
    sl: float
    tp: float
    size: float  # in base currency
    equity_at_risk: float
    pnl_pct: float = 0.0
    pnl_abs: float = 0.0
    exit_reason: str = ""
    bars_held: int = 0
    
class StrategyEMA_RSI:
    """
    EMA Crossover + RSI + Volume Filter Strategy
    
    RULES:
    -----
    FILTER (Trend):
        - Price must be above 200 EMA for LONGS, below for SHORTS
        - 200 EMA acts as macro trend filter (K.I.S.S.)
    
    ENTRY:
        - Fast EMA (9) crosses above Slow EMA (21) = LONG signal
        - Fast EMA (9) crosses below Slow EMA (21) = SHORT signal
        - RSI(14) must confirm: > 45 for LONG (not overbought zone start), < 55 for SHORT
        - Volume must be > 20-period average (confirms conviction)
    
    EXIT:
        - SL: 2.0 * ATR(14) from entry (adapts to volatility)
        - TP: Minimum 2.5:1 R:R (reward must justify risk)
        - Trailing: If price moves 1.5x risk in profit, move SL to breakeven
        - Hard stop: Close if EMA cross reverses (trend lost)
    
    RISK:
        - 1.0% of equity per trade (Kelly fraction approximate)
        - Position size = risk_amount / (entry - SL)
        - Max 1 concurrent trade per symbol
        - No trade if ATR% > 3% (too volatile = stay out)
    """
    
    def __init__(self, 
                 ema_fast=9, ema_slow=21, ema_trend=200,
                 rsi_period=14, rsi_long_min=45, rsi_short_max=55,
                 atr_period=14, atr_sl_mult=2.0, atr_tp_mult=5.0,
                 risk_per_trade=0.01,  # 1%
                 volume_confirm=True,
                 max_atr_pct=0.03):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.ema_trend = ema_trend
        self.rsi_period = rsi_period
        self.rsi_long_min = rsi_long_min
        self.rsi_short_max = rsi_short_max
        self.atr_period = atr_period
        self.atr_sl_mult = atr_sl_mult
        self.atr_tp_mult = atr_tp_mult
        self.risk_per_trade = risk_per_trade
        self.volume_confirm = volume_confirm
        self.max_atr_pct = max_atr_pct
        
    def calculate_indicators(self, df):
        df = df.copy()
        # EMAs
        df['ema_fast'] = df['close'].ewm(span=self.ema_fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.ema_slow, adjust=False).mean()
        df['ema_trend'] = df['close'].ewm(span=self.ema_trend, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1/self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/self.rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR
        prev_close = df['close'].shift(1)
        tr1 = df['high'] - df['low']
        tr2 = (df['high'] - prev_close).abs()
        tr3 = (df['low'] - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.ewm(span=self.atr_period, adjust=False).mean()
        
        # Volume SMA
        df['vol_sma'] = df['volume'].rolling(window=20).mean()
        
        # Crossover signal
        df['ema_cross'] = np.where(
            (df['ema_fast'] > df['ema_slow']) & (df['ema_fast'].shift(1) <= df['ema_slow'].shift(1)),
            1,  # Bull cross
            np.where(
                (df['ema_fast'] < df['ema_slow']) & (df['ema_fast'].shift(1) >= df['ema_slow'].shift(1)),
                -1,  # Bear cross
                0
            )
        )
        
        return df
    
    def generate_signal(self, df, idx=-1, equity=10000.0):
        """Returns signal dict or None."""
        i = idx if idx >= 0 else len(df) + idx
        if i < self.ema_trend + 10:
            return None
            
        row = df.iloc[i]
        
        # Volatility filter
        price = row['close']
        atr_pct = row['atr'] / price
        if atr_pct > self.max_atr_pct:
            return None  # Too volatile
        
        signal = None
        
        # LONG signal
        if row['ema_cross'] == 1:
            if price > row['ema_trend'] and row['rsi'] > self.rsi_long_min:
                if not self.volume_confirm or row['volume'] > row['vol_sma']:
                    sl = price - self.atr_sl_mult * row['atr']
                    tp = price + self.atr_tp_mult * row['atr']
                    risk_amount = equity * self.risk_per_trade
                    size = risk_amount / (price - sl)
                    rr = (tp - price) / (price - sl)
                    signal = {
                        'dir': 'long', 'entry': price, 'sl': sl, 'tp': tp,
                        'size': size, 'risk': risk_amount, 'rr': rr,
                        'ema_fast': row['ema_fast'], 'ema_slow': row['ema_slow'],
                        'rsi': row['rsi'], 'atr': row['atr'], 'vol_ratio': row['volume'] / row['vol_sma']
                    }
        
        # SHORT signal
        elif row['ema_cross'] == -1:
            if price < row['ema_trend'] and row['rsi'] < self.rsi_short_max:
                if not self.volume_confirm or row['volume'] > row['vol_sma']:
                    sl = price + self.atr_sl_mult * row['atr']
                    tp = price - self.atr_tp_mult * row['atr']
                    risk_amount = equity * self.risk_per_trade
                    size = risk_amount / (sl - price)
                    rr = (price - tp) / (sl - price)
                    signal = {
                        'dir': 'short', 'entry': price, 'sl': sl, 'tp': tp,
                        'size': size, 'risk': risk_amount, 'rr': rr,
                        'ema_fast': row['ema_fast'], 'ema_slow': row['ema_slow'],
                        'rsi': row['rsi'], 'atr': row['atr'], 'vol_ratio': row['volume'] / row['vol_sma']
                    }
        
        return signal


class Backtest:
    def __init__(self, strategy, initial_equity=10000, fee_rate=0.0006, slippage=0.0002):
        self.strategy = strategy
        self.initial_equity = initial_equity
        self.fee_rate = fee_rate  # Bybit taker fee 0.06%
        self.slippage = slippage  # 0.02% reasonable for BTC/USDT 1h
        self.trades: List[Trade] = []
        
    def run(self, df_raw):
        df = self.strategy.calculate_indicators(df_raw)
        equity = self.initial_equity
        active_trade: Optional[Trade] = None
        
        for i in range(self.strategy.ema_trend + 10, len(df)):
            row = df.iloc[i]
            
            # Check if active trade hit SL/TP/trail
            if active_trade:
                high = row['high']
                low = row['low']
                
                exit_price = None
                exit_reason = ""
                
                if active_trade.dir == 'long':
                    if low <= active_trade.sl:
                        exit_price = active_trade.sl
                        exit_reason = "SL"
                    elif high >= active_trade.tp:
                        exit_price = active_trade.tp
                        exit_reason = "TP"
                    elif row['ema_cross'] == -1:
                        exit_price = row['close']
                        exit_reason = "EMA_REVERSAL"
                else:  # short
                    if high >= active_trade.sl:
                        exit_price = active_trade.sl
                        exit_reason = "SL"
                    elif low <= active_trade.tp:
                        exit_price = active_trade.tp
                        exit_reason = "TP"
                    elif row['ema_cross'] == 1:
                        exit_price = row['close']
                        exit_reason = "EMA_REVERSAL"
                
                if exit_price:
                    active_trade.exit_time = row['timestamp']
                    active_trade.exit_price = exit_price
                    active_trade.exit_reason = exit_reason
                    active_trade.bars_held = i - df.index[df['timestamp'] == active_trade.entry_time].tolist()[0]
                    
                    # Calculate P&L
                    if active_trade.dir == 'long':
                        raw_pnl = (exit_price - active_trade.entry_price) / active_trade.entry_price
                    else:
                        raw_pnl = (active_trade.entry_price - exit_price) / active_trade.entry_price
                    
                    costs = self.fee_rate * 2 + self.slippage * 2
                    active_trade.pnl_pct = raw_pnl - costs
                    active_trade.pnl_abs = active_trade.pnl_pct * active_trade.entry_price * active_trade.size
                    equity += active_trade.pnl_abs
                    
                    self.trades.append(active_trade)
                    active_trade = None
            
            # Look for new entry only if no active trade
            if not active_trade:
                # Need enough future bars for trade to play out
                if i < len(df) - 1:
                    sig = self.strategy.generate_signal(df, i, equity)
                    if sig:
                        active_trade = Trade(
                            entry_time=row['timestamp'],
                            exit_time=None,
                            dir=sig['dir'],
                            entry_price=sig['entry'],
                            exit_price=None,
                            sl=sig['sl'],
                            tp=sig['tp'],
                            size=sig['size'],
                            equity_at_risk=sig['risk'],
                        )
        
        return self._metrics(equity)
    
    def _metrics(self, final_equity):
        if not self.trades:
            return {"trades": 0, "final_equity": final_equity}
        
        wins = [t for t in self.trades if t.pnl_pct > 0]
        losses = [t for t in self.trades if t.pnl_pct <= 0]
        
        winrate = len(wins) / len(self.trades) if self.trades else 0
        avg_win = np.mean([t.pnl_pct for t in wins]) if wins else 0
        avg_loss = np.mean([t.pnl_pct for t in losses]) if losses else 0
        
        profit_factor = abs(sum([t.pnl_pct for t in wins]) / sum([t.pnl_pct for t in losses])) if losses and sum([t.pnl_pct for t in losses]) != 0 else float('inf')
        
        # Equity curve
        eq_curve = [self.initial_equity]
        for t in self.trades:
            eq_curve.append(eq_curve[-1] + t.pnl_abs)
        
        # Max drawdown
        peak = eq_curve[0]
        max_dd = 0
        for e in eq_curve:
            if e > peak:
                peak = e
            dd = (peak - e) / peak
            if dd > max_dd:
                max_dd = dd
        
        # Sharpe (simplified, assuming risk-free=0, annualized roughly)
        returns = [t.pnl_pct for t in self.trades]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252 / len(returns) * 24) if np.std(returns) > 0 else 0
        
        return {
            "trades": len(self.trades),
            "wins": len(wins),
            "losses": len(losses),
            "winrate": winrate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "final_equity": final_equity,
            "total_return_pct": (final_equity - self.initial_equity) / self.initial_equity * 100,
            "max_drawdown_pct": max_dd * 100,
            "sharpe": sharpe,
            "avg_bars_held": np.mean([t.bars_held for t in self.trades]),
        }


def run_backtest(symbol="BTC/USDT", timeframe="1h"):
    print(f"\n{'='*60}")
    print(f" BACKTEST: {symbol} @ {timeframe}")
    print(f"{'='*60}")
    
    df_raw = load_raw(symbol, timeframe)
    df_clean = clean_wicks(df_raw, max_wick_pct=0.05)
    print(f"Data loaded: {len(df_clean)} bars (cleaned)")
    
    strategy = StrategyEMA_RSI(
        ema_fast=9, ema_slow=21, ema_trend=200,
        rsi_period=14, rsi_long_min=45, rsi_short_max=55,
        atr_period=14, atr_sl_mult=2.0, atr_tp_mult=4.0,
        risk_per_trade=0.01,
        volume_confirm=True,
        max_atr_pct=0.03
    )
    
    bt = Backtest(strategy, initial_equity=10000, fee_rate=0.0006, slippage=0.0002)
    metrics = bt.run(df_clean)
    
    print(f"\n{'─'*40}")
    print(f"RESULTS")
    print(f"{'─'*40}")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k:20s}: {v:.4f}")
        else:
            print(f"  {k:20s}: {v}")
    
    # Print last 5 trades
    if bt.trades:
        print(f"\n{'─'*40}")
        print("LAST 5 TRADES")
        print(f"{'─'*40}")
        for t in bt.trades[-5:]:
            print(f"  {t.dir:5s} | Entry: {t.entry_price:8.2f} | Exit: {t.exit_price:8.2f} | PnL: {t.pnl_pct*100:+.2f}% | {t.exit_reason}")
    
    return metrics, bt


if __name__ == "__main__":
    # Run for multiple assets
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    
    for sym in symbols:
        metrics, bt = run_backtest(sym, "1h")
        print()
