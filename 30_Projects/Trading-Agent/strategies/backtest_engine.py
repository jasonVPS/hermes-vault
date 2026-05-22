"""
Trading Agent - Strategy Backtesting Engine
Implements 4 proven trading strategies, backtests them on historical data,
outputs metrics + best strategy per asset/timeframe.

Strategies:
  1. Mean Reversion (Bollinger Bands)
  2. Trend Following (Heikin Ashi + EMA Cross)
  3. Momentum (Supertrend + RSI)
  4. Breakout (Donchian Channel)

Risk Management:
  - 1% Risk per trade (ATR-based position sizing)
  - Stop Loss = 1.5x ATR
  - Take Profit = 3x ATR (1:2 R:R)
  - Max concurrent positions = 3
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import sqlite3
from datetime import datetime


@dataclass
class Signal:
    direction: int  # 1 = long, -1 = short, 0 = hold
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float  # 0-1
    timestamp: pd.Timestamp


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: Optional[pd.Timestamp]
    symbol: str
    direction: int
    entry_price: float
    exit_price: Optional[float]
    size: float
    pnl: float
    pnl_pct: float
    max_drawdown: float
    reason: str  # 'tp' | 'sl' | 'signal'


class Strategy(ABC):
    """Abstract base for all strategies."""

    def __init__(self, name: str, params: Dict = None):
        self.name = name
        self.params = params or {}

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame, i: int) -> Optional[Signal]:
        pass

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean().iloc[-1]

    def calculate_position_size(self, equity: float, entry: float, stop: float, risk_pct: float = 0.01) -> float:
        risk_amount = equity * risk_pct
        risk_per_unit = abs(entry - stop)
        if risk_per_unit == 0:
            return 0
        return risk_amount / risk_per_unit


class MeanReversionStrategy(Strategy):
    """Bollinger Bands Mean Reversion.
    Long when price touches lower band + RSI oversold.
    Short when price touches upper band + RSI overbought.
    """

    def __init__(self, bb_period: int = 20, bb_std: float = 2.0,
                 rsi_period: int = 14, rsi_oversold: int = 30, rsi_overbought: int = 70):
        super().__init__("MeanReversion_Bollinger", {
            'bb_period': bb_period,
            'bb_std': bb_std,
            'rsi_period': rsi_period,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
        })

    def generate_signal(self, df: pd.DataFrame, i: int) -> Optional[Signal]:
        if i < max(self.params['bb_period'], self.params['rsi_period']) + 5:
            return None

        window = df.iloc[:i+1]
        close = window['close']

        # Bollinger Bands
        sma = close.rolling(self.params['bb_period']).mean().iloc[-1]
        std = close.rolling(self.params['bb_period']).std().iloc[-1]
        upper = sma + self.params['bb_std'] * std
        lower = sma - self.params['bb_std'] * std

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(self.params['rsi_period']).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(self.params['rsi_period']).mean().iloc[-1]
        rs = gain / loss if loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))

        current_close = close.iloc[-1]
        atr = self.calculate_atr(window)

        # Long signal: price below lower band + RSI oversold (but not too low)
        if current_close < lower and rsi < self.params['rsi_oversold'] + 10:
            return Signal(
                direction=1,
                entry_price=current_close,
                stop_loss=current_close - 1.5 * atr,
                take_profit=current_close + 3.0 * atr,
                confidence=(self.params['rsi_oversold'] + 10 - rsi) / 40,
                timestamp=window.index[-1]
            )

        # Short signal: price above upper band + RSI overbought
        if current_close > upper and rsi > self.params['rsi_overbought'] - 10:
            return Signal(
                direction=-1,
                entry_price=current_close,
                stop_loss=current_close + 1.5 * atr,
                take_profit=current_close - 3.0 * atr,
                confidence=(rsi - (self.params['rsi_overbought'] - 10)) / 40,
                timestamp=window.index[-1]
            )

        return None


class TrendFollowingStrategy(Strategy):
    """Heikin Ashi + EMA Cross Trend Following.
    Long when HA is bullish + EMA(9) > EMA(21).
    Short when HA is bearish + EMA(9) < EMA(21).
    """

    def __init__(self, ema_fast: int = 9, ema_slow: int = 21,
                 adx_period: int = 14, adx_min: int = 25):
        super().__init__("TrendFollowing_EMA", {
            'ema_fast': ema_fast,
            'ema_slow': ema_slow,
            'adx_period': adx_period,
            'adx_min': adx_min,
        })

    def generate_signal(self, df: pd.DataFrame, i: int) -> Optional[Signal]:
        if i < max(self.params['ema_slow'], self.params['adx_period']) + 5:
            return None

        window = df.iloc[:i+1]
        close = window['close']

        # EMAs
        ema_fast = close.ewm(span=self.params['ema_fast']).mean().iloc[-1]
        ema_slow = close.ewm(span=self.params['ema_slow']).mean().iloc[-1]

        # Heikin Ashi
        ha_close = (window['open'] + window['high'] + window['low'] + window['close']) / 4
        ha_open = ((window['open'] + window['close']) / 2).shift(1).fillna(window['open'])
        ha_bullish = ha_close.iloc[-1] > ha_open.iloc[-1]
        ha_bearish = ha_close.iloc[-1] < ha_open.iloc[-1]

        # ADX for trend strength
        tr = pd.concat([window['high'] - window['low'],
                        np.abs(window['high'] - window['close'].shift()),
                        np.abs(window['low'] - window['close'].shift())], axis=1).max(axis=1)
        atr = tr.rolling(self.params['adx_period']).mean().iloc[-1]

        current_close = close.iloc[-1]

        # Long: bullish HA + fast > slow
        if ha_bullish and ema_fast > ema_slow:
            return Signal(
                direction=1,
                entry_price=current_close,
                stop_loss=current_close - 2.0 * atr,
                take_profit=current_close + 4.0 * atr,
                confidence=min((ema_fast - ema_slow) / current_close * 100, 1.0),
                timestamp=window.index[-1]
            )

        # Short: bearish HA + fast < slow
        if ha_bearish and ema_fast < ema_slow:
            return Signal(
                direction=-1,
                entry_price=current_close,
                stop_loss=current_close + 2.0 * atr,
                take_profit=current_close - 4.0 * atr,
                confidence=min((ema_slow - ema_fast) / current_close * 100, 1.0),
                timestamp=window.index[-1]
            )

        return None


class MomentumStrategy(Strategy):
    """Supertrend + RSI Momentum.
    Long when Supertrend is bullish + RSI > 50.
    Short when Supertrend is bearish + RSI < 50.
    """

    def __init__(self, atr_period: int = 10, factor: float = 3.0,
                 rsi_period: int = 14):
        super().__init__("Momentum_Supertrend", {
            'atr_period': atr_period,
            'factor': factor,
            'rsi_period': rsi_period,
        })

    def generate_signal(self, df: pd.DataFrame, i: int) -> Optional[Signal]:
        if i < max(self.params['atr_period'], self.params['rsi_period']) + 5:
            return None

        window = df.iloc[:i+1]
        close = window['close']
        high = window['high']
        low = window['low']

        # ATR
        tr = pd.concat([high - low, np.abs(high - close.shift()), np.abs(low - close.shift())], axis=1).max(axis=1)
        atr = tr.rolling(self.params['atr_period']).mean()

        # Supertrend
        upper_band = (high + low) / 2 + self.params['factor'] * atr
        lower_band = (high + low) / 2 - self.params['factor'] * atr

        # Trend detection via Supertrend
        trend = np.where(close > upper_band, 1, np.where(close < lower_band, -1, 0))
        trend = pd.Series(trend, index=close.index).ffill().fillna(0)

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(self.params['rsi_period']).mean().iloc[-1]
        loss = (-delta.clip(upper=0)).rolling(self.params['rsi_period']).mean().iloc[-1]
        rs = gain / loss if loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))

        current_close = close.iloc[-1]
        current_atr = atr.iloc[-1]
        current_trend = trend.iloc[-1]

        # Long: Supertrend bullish + RSI confirmation
        if current_trend == 1 and rsi > 55:
            return Signal(
                direction=1,
                entry_price=current_close,
                stop_loss=current_close - 1.5 * current_atr,
                take_profit=current_close + 3.5 * current_atr,
                confidence=min((rsi - 55) / 45, 1.0),
                timestamp=window.index[-1]
            )

        # Short: Supertrend bearish + RSI confirmation
        if current_trend == -1 and rsi < 45:
            return Signal(
                direction=-1,
                entry_price=current_close,
                stop_loss=current_close + 1.5 * current_atr,
                take_profit=current_close - 3.5 * current_atr,
                confidence=min((45 - rsi) / 45, 1.0),
                timestamp=window.index[-1]
            )

        return None


class BreakoutStrategy(Strategy):
    """Donchian Channel Breakout.
    Long when price breaks above N-period high.
    Short when price breaks below N-period low.
    Filtered by volume confirmation.
    """

    def __init__(self, period: int = 20, volume_multiplier: float = 1.5):
        super().__init__("Breakout_Donchian", {
            'period': period,
            'volume_multiplier': volume_multiplier,
        })

    def generate_signal(self, df: pd.DataFrame, i: int) -> Optional[Signal]:
        if i < self.params['period'] + 5:
            return None

        window = df.iloc[:i+1]
        close = window['close']
        high = window['high']
        low = window['low']
        volume = window['volume']

        # Donchian channels
        upper = high.rolling(self.params['period']).max().iloc[-2]  # prior bar
        lower = low.rolling(self.params['period']).min().iloc[-2]

        current_close = close.iloc[-1]
        prev_close = close.iloc[-2]
        atr = self.calculate_atr(window)

        avg_volume = volume.rolling(20).mean().iloc[-1]
        current_volume = volume.iloc[-1]

        # Long breakout: price breaks above upper band + volume
        if prev_close <= upper and current_close > upper and current_volume > avg_volume * self.params['volume_multiplier']:
            return Signal(
                direction=1,
                entry_price=current_close,
                stop_loss=current_close - 2.0 * atr,
                take_profit=current_close + 4.0 * atr,
                confidence=min((current_volume / (avg_volume * self.params['volume_multiplier'])) - 1, 1.0),
                timestamp=window.index[-1]
            )

        # Short breakout: price breaks below lower band + volume
        if prev_close >= lower and current_close < lower and current_volume > avg_volume * self.params['volume_multiplier']:
            return Signal(
                direction=-1,
                entry_price=current_close,
                stop_loss=current_close + 2.0 * atr,
                take_profit=current_close - 4.0 * atr,
                confidence=min((current_volume / (avg_volume * self.params['volume_multiplier'])) - 1, 1.0),
                timestamp=window.index[-1]
            )

        return None


class BacktestEngine:
    """Unified backtest engine for all strategies."""

    def __init__(self, initial_equity: float = 10000.0,
                 risk_per_trade: float = 0.01,
                 max_positions: int = 3,
                 fee_pct: float = 0.001):
        self.initial_equity = initial_equity
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.fee_pct = fee_pct

    def run(self, df: pd.DataFrame, strategy: Strategy) -> Dict:
        equity = self.initial_equity
        trades: List[Trade] = []
        active_signals: List[Signal] = []
        equity_curve = [equity]

        for i in range(50, len(df)):
            current_bar = df.iloc[i]
            current_price = current_bar['close']

            # Check exits for active positions
            for sig in active_signals[:]:
                exit_triggered = False
                exit_price = None
                exit_reason = None

                # Long exits
                if sig.direction == 1:
                    if current_price <= sig.stop_loss:
                        exit_triggered = True
                        exit_price = current_price
                        exit_reason = 'sl'
                    elif current_price >= sig.take_profit:
                        exit_triggered = True
                        exit_price = current_price
                        exit_reason = 'tp'

                # Short exits
                elif sig.direction == -1:
                    if current_price >= sig.stop_loss:
                        exit_triggered = True
                        exit_price = current_price
                        exit_reason = 'sl'
                    elif current_price <= sig.take_profit:
                        exit_triggered = True
                        exit_price = current_price
                        exit_reason = 'tp'

                if exit_triggered:
                    position_size = strategy.calculate_position_size(
                        equity, sig.entry_price, sig.stop_loss, self.risk_per_trade
                    )
                    if sig.direction == 1:
                        pnl = (exit_price - sig.entry_price) * position_size
                    else:
                        pnl = (sig.entry_price - exit_price) * position_size

                    fees = (sig.entry_price + exit_price) * position_size * self.fee_pct
                    pnl -= fees
                    equity += pnl

                    trades.append(Trade(
                        entry_time=sig.timestamp,
                        exit_time=current_bar.name,
                        symbol=str(df.index.name or ''),
                        direction=sig.direction,
                        entry_price=sig.entry_price,
                        exit_price=exit_price,
                        size=position_size,
                        pnl=pnl,
                        pnl_pct=(pnl / self.initial_equity) * 100,
                        max_drawdown=0,  # Simplified
                        reason=exit_reason
                    ))
                    active_signals.remove(sig)

            # Check new entry (simplified: max 1 trade per bar)
            if len(active_signals) < self.max_positions:
                signal = strategy.generate_signal(df, i)
                if signal:
                    # Check if signal is not immediately stopped out
                    if signal.direction == 1 and current_price <= signal.stop_loss:
                        continue
                    if signal.direction == -1 and current_price >= signal.stop_loss:
                        continue
                    active_signals.append(signal)

            equity_curve.append(equity)

        # Close remaining positions at last price
        for sig in active_signals:
            position_size = strategy.calculate_position_size(
                equity, sig.entry_price, sig.stop_loss, self.risk_per_trade
            )
            last_price = df['close'].iloc[-1]
            if sig.direction == 1:
                pnl = (last_price - sig.entry_price) * position_size
            else:
                pnl = (sig.entry_price - last_price) * position_size
            fees = (sig.entry_price + last_price) * position_size * self.fee_pct
            pnl -= fees
            equity += pnl
            trades.append(Trade(
                entry_time=sig.timestamp,
                exit_time=df.index[-1],
                symbol=str(df.index.name or ''),
                direction=sig.direction,
                entry_price=sig.entry_price,
                exit_price=last_price,
                size=position_size,
                pnl=pnl,
                pnl_pct=(pnl / self.initial_equity) * 100,
                max_drawdown=0,
                reason='signal'
            ))

        return self._calculate_metrics(equity_curve, trades)

    def _calculate_metrics(self, equity_curve: List[float], trades: List[Trade]) -> Dict:
        if not trades:
            return {"trades": 0, "win_rate": 0, "total_pnl": 0}

        equity_series = pd.Series(equity_curve)

        total_pnl = sum(t.pnl for t in trades)
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        win_rate = (winning_trades / len(trades)) * 100

        # Max drawdown
        peak = equity_series.expanding().max()
        drawdown = (equity_series - peak) / peak
        max_drawdown = abs(drawdown.min()) * 100

        # Sharpe (simplified, assuming risk-free = 0)
        returns = equity_series.pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0

        # Profit factor
        gross_profit = sum(t.pnl for t in trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in trades if t.pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')

        avg_trade = total_pnl / len(trades)
        avg_win = gross_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = gross_loss / (len(trades) - winning_trades) if len(trades) > winning_trades else 0

        return {
            'trades': len(trades),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'sharpe': round(sharpe, 2),
            'max_drawdown_pct': round(max_drawdown, 2),
            'total_pnl_pct': round((total_pnl / self.initial_equity) * 100, 2),
            'avg_trade_pct': round((avg_trade / self.initial_equity) * 100, 4),
            'avg_win_pct': round((avg_win / self.initial_equity) * 100, 4) if avg_win else 0,
            'avg_loss_pct': round((avg_loss / self.initial_equity) * 100, 4) if avg_loss else 0,
            'final_equity': round(equity_curve[-1], 2),
        }


# ═══════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

    print("=== STRATEGIE BACKTESTS ===\n")

    # Load data from SQLite
    DB_PATH = "/opt/data/home/hermes-vault/30_Projects/Trading-Agent/data/market_data.db"
    conn = sqlite3.connect(DB_PATH)

    strategies = [
        MeanReversionStrategy(),
        TrendFollowingStrategy(),
        MomentumStrategy(),
        BreakoutStrategy(),
    ]

    symbols_timeframes = [
        ("BTC/USDT", "1h"),
        ("BTC/USDT", "4h"),
        ("ETH/USDT", "1h"),
        ("ETH/USDT", "4h"),
    ]

    results = []

    for symbol, tf in symbols_timeframes:
        print(f"\n{'='*60}")
        print(f"  {symbol} @ {tf}")
        print(f"{'='*60}")

        df = pd.read_sql_query(
            f"SELECT * FROM ohlcv WHERE symbol='{symbol}' AND timeframe='{tf}' ORDER BY timestamp",
            conn,
            parse_dates=['timestamp']
        )
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)

        if len(df) < 100:
            print(f"  ⚠️  Nur {len(df)} candles - zu wenig Daten")
            continue

        engine = BacktestEngine(initial_equity=10000, fee_pct=0.001)

        best_strategy = None
        best_metrics = None
        best_pnl = -float('inf')

        for strat in strategies:
            metrics = engine.run(df, strat)
            results.append({
                'symbol': symbol,
                'timeframe': tf,
                'strategy': strat.name,
                **metrics
            })

            pnl = metrics['total_pnl_pct']
            indicator = "🟢" if pnl > 0 else "🔴"
            print(f"\n  {indicator} {strat.name}")
            print(f"      Trades: {metrics['trades']} | Win: {metrics['win_rate']}% | PF: {metrics['profit_factor']}")
            print(f"      PnL: {metrics['total_pnl_pct']}% | Sharpe: {metrics['sharpe']} | MaxDD: {metrics['max_drawdown_pct']}%")

            if pnl > best_pnl:
                best_pnl = pnl
                best_strategy = strat.name
                best_metrics = metrics

        if best_strategy:
            print(f"\n  ⭐ BESTE STRATEGIE: {best_strategy} (+{best_pnl}%)")

    conn.close()

    # Global leaderboard
    print(f"\n\n{'='*60}")
    print("  🏆 GLOBAL LEADERBOARD")
    print(f"{'='*60}")
    df_results = pd.DataFrame(results)
    top5 = df_results.nlargest(5, 'total_pnl_pct')
    print(top5[['symbol', 'timeframe', 'strategy', 'total_pnl_pct', 'sharpe', 'win_rate', 'profit_factor']].to_string(index=False))
