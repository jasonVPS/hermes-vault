"""
Regime-Aware Strategy: Trendfolge in Trend, Mean-Reversion in Range.
"""
import pandas as pd
import numpy as np
from data.features import add_indicators, classify_regime

class RegimeAwareStrategy:
    """
    - Trend (ADX > 25): Trendfolge — Long wenn EMA9 > EMA21 > EMA100 + RSI 50-65
    - Range (ADX < 20): Mean Reversion — Long wenn RSI < 30 + Preis nahe Lower BB
    - Transition: Keine Trades
    """
    def __init__(self):
        pass

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = add_indicators(df)
        df["regime"] = classify_regime(df)
        signals = pd.Series("HOLD", index=df.index)

        for i in range(200, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i-1]

            if row["regime"] == "trend":
                # Trendfolge
                if (row["ema8"] > row["ema21"] > row["ema200"] and
                    50 < row["rsi14"] < 65 and
                    row["close"] > row["ema8"]):
                    signals.iloc[i] = "LONG"
                elif (row["ema8"] < row["ema21"] < row["ema200"] and
                      35 < row["rsi14"] < 50 and
                      row["close"] < row["ema8"]):
                    signals.iloc[i] = "SHORT"

            elif row["regime"] == "range":
                # Mean Reversion — Bollinger Bands
                std = df["close"].iloc[i-20:i].std()
                sma = df["close"].iloc[i-20:i].mean()
                lower_bb = sma - 2 * std
                upper_bb = sma + 2 * std

                if row["close"] < lower_bb and row["rsi14"] < 30:
                    signals.iloc[i] = "LONG"
                elif row["close"] > upper_bb and row["rsi14"] > 70:
                    signals.iloc[i] = "SHORT"

        return signals
