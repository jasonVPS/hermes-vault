"""
Stricter Regime-Aware Strategy v2.
Tighter filters, higher quality signals.
"""
import pandas as pd
from data.features import add_indicators, classify_regime

class RegimeAwareStrategy:
    def __init__(self, adx_threshold: float = 25.0, min_rsi: float = 40.0, max_rsi: float = 60.0):
        self.adx_threshold = adx_threshold
        self.min_rsi = min_rsi
        self.max_rsi = max_rsi

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = add_indicators(df)
        df["regime"] = classify_regime(df)
        signals = pd.Series("HOLD", index=df.index)

        for i in range(200, len(df)):
            row = df.iloc[i]
            atr = row.get("atr14", row["high"] - row["low"])
            if atr <= 0:
                continue

            # Skip transition regime
            if row["regime"] == "transition":
                continue

            in_zone = False
            direction = None

            if row["regime"] == "trend":
                # Strong trend requirement
                if row["adx14"] < self.adx_threshold + 5:
                    continue

                # LONG: EMA stack in uptrend + RSI in zone
                if (row["ema8"] > row["ema21"] > row["ema200"] and
                    45 < row["rsi14"] < 62 and
                    row["close"] > row["ema8"]):
                    direction = "LONG"
                    in_zone = True

                # SHORT: EMA stack in downtrend + RSI in zone
                elif (row["ema8"] < row["ema21"] < row["ema200"] and
                      38 < row["rsi14"] < 55 and
                      row["close"] < row["ema8"]):
                    direction = "SHORT"
                    in_zone = True

            elif row["regime"] == "range":
                # Mean Reversion — Bollinger Bands
                std = df["close"].iloc[i-20:i].std()
                sma = df["close"].iloc[i-20:i].mean()
                lower_bb = sma - 2 * std
                upper_bb = sma + 2 * std

                # Require price OUTSIDE BB AND RSI extreme
                if row["close"] < lower_bb and row["rsi14"] < 30:
                    direction = "LONG"
                    in_zone = True
                elif row["close"] > upper_bb and row["rsi14"] > 70:
                    direction = "SHORT"
                    in_zone = True

            if in_zone and direction:
                signals.iloc[i] = direction

        return signals
