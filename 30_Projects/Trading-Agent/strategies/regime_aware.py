"""
Parameterized Swing Strategy v5.
All key variables exposed for optimization.
"""
import pandas as pd
from data.features import add_indicators, classify_regime

class RegimeAwareStrategy:
    def __init__(self,
                 rsi_long_entry: float = 50.0,
                 rsi_short_entry: float = 65.0,
                 rsi_bounce_min: float = 1.0,
                 adx_min: float = 15.0,
                 vol_multiplier: float = 0.3,
                 enable_trend: bool = True,
                 enable_range: bool = False,
                 enable_transition: bool = False):
        self.rsi_long_entry = rsi_long_entry
        self.rsi_short_entry = rsi_short_entry
        self.rsi_bounce_min = rsi_bounce_min
        self.adx_min = adx_min
        self.vol_multiplier = vol_multiplier
        self.enable_trend = enable_trend
        self.enable_range = enable_range
        self.enable_transition = enable_transition

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = add_indicators(df)
        df["regime"] = classify_regime(df)
        signals = pd.Series("HOLD", index=df.index)

        for i in range(200, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i-1] if i >= 1 else row
            prev2 = df.iloc[i-2] if i >= 2 else prev
            prev3 = df.iloc[i-3] if i >= 3 else prev2

            # Regime filter
            regime = row.get("regime", "unknown")
            if regime == "trend" and not self.enable_trend:
                continue
            if regime == "range" and not self.enable_range:
                continue
            if regime == "transition" and not self.enable_transition:
                continue

            if row["adx14"] < self.adx_min:
                continue

            direction = None

            # LONG
            in_uptrend = row["close"] > row["ema21"] and row["ema21"] > row["ema200"]
            if in_uptrend:
                pull = prev3.get("rsi14", 50) > (self.rsi_long_entry + 10) and prev2.get("rsi14", prev3.get("rsi14")) < prev3.get("rsi14", 50)
                bounce = prev.get("rsi14", 50) < self.rsi_long_entry and row["rsi14"] > prev.get("rsi14", 50) + self.rsi_bounce_min
                vol = row.get("vol_sma50", row["volume"])
                vol_ok = row["volume"] > vol * self.vol_multiplier
                if pull and bounce and vol_ok:
                    direction = "LONG"

            # SHORT
            in_downtrend = row["close"] < row["ema21"] and row["ema21"] < row["ema200"]
            if in_downtrend:
                pull = prev3.get("rsi14", 50) < (self.rsi_short_entry - 10) and prev2.get("rsi14", prev3.get("rsi14")) > prev3.get("rsi14", 50)
                bounce = prev.get("rsi14", 50) > self.rsi_short_entry and row["rsi14"] < prev.get("rsi14", 50) - self.rsi_bounce_min
                vol = row.get("vol_sma50", row["volume"])
                vol_ok = row["volume"] > vol * self.vol_multiplier
                if pull and bounce and vol_ok:
                    direction = "SHORT"

            if direction:
                signals.iloc[i] = direction

        return signals
