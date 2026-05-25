"""
Regime features: ADX, EMA200-Slope, 20-day ROC.
"""
import pandas as pd
import numpy as np

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add all technical indicators to the DataFrame."""
    df = df.copy()

    # EMAs
    df["ema8"] = df["close"].ewm(span=8, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

    # ATR
    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - df["close"].shift(1)).abs()
    tr3 = (df["low"] - df["close"].shift(1)).abs()
    df["true_range"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["atr14"] = df["true_range"].ewm(span=14, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    rs = gain / (loss + 1e-9)
    df["rsi14"] = 100 - (100 / (1 + rs))

    # ADX
    plus_dm = df["high"].diff()
    minus_dm = -df["low"].diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    atr = df["atr14"]
    plus_di = 100 * plus_dm.ewm(span=14, adjust=False).mean() / (atr + 1e-9)
    minus_di = 100 * minus_dm.ewm(span=14, adjust=False).mean() / (atr + 1e-9)
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)
    df["adx14"] = dx.ewm(span=14, adjust=False).mean()

    # 20-day ROC
    df["roc20"] = (df["close"] - df["close"].shift(20 * 24)) / df["close"].shift(20 * 24) * 100

    # Volume SMA
    df["vol_sma50"] = df["volume"].rolling(50, min_periods=10).mean()

    return df

def classify_regime(df: pd.DataFrame) -> pd.Series:
    """
    Classify regime per candle:
    - trend: ADX > 25
    - range: ADX < 20
    - transition: 20 <= ADX <= 25
    """
    adx = df.get("adx14", pd.Series(0, index=df.index))
    return pd.Series(np.where(adx > 25, "trend", np.where(adx < 20, "range", "transition")), index=df.index)
