"""
Multi-Timeframe Regime-Aware Strategy v6.
Uses 4h trend confirmation for 1h entries.
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

    def generate_signals(self, df_1h: pd.DataFrame, df_4h: pd.DataFrame) -> pd.Series:
        # Process both timeframes
        df_1h = add_indicators(df_1h)
        df_1h["regime"] = classify_regime(df_1h)
        df_4h = add_indicators(df_4h)

        # Resample 4h EMA confirmation to 1h
        df_4h_1h = df_4h.reindex(df_1h.index, method="ffill")
        
        signals = pd.Series("HOLD", index=df_1h.index)

        for i in range(200, len(df_1h)):
            row = df_1h.iloc[i]
            row_4h = df_4h_1h.iloc[i] if i < len(df_4h_1h) else row
            prev = df_1h.iloc[i-1] if i >= 1 else row
            prev2 = df_1h.iloc[i-2] if i >= 2 else prev
            prev3 = df_1h.iloc[i-3] if i >= 3 else prev2

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
            in_uptrend_1h = row["close"] > row["ema21"] and row["ema21"] > row["ema200"]
            in_uptrend_4h = row_4h["close"] > row_4h["ema21"] and row_4h["ema21"] > row_4h["ema200"]
            
            if in_uptrend_1h and in_uptrend_4h:
                pull = prev3.get("rsi14", 50) > (self.rsi_long_entry + 10) and prev2.get("rsi14", prev3.get("rsi14")) < prev3.get("rsi14", 50)
                bounce = prev.get("rsi14", 50) < self.rsi_long_entry and row["rsi14"] > prev.get("rsi14", 50) + self.rsi_bounce_min
                vol = row.get("vol_sma50", row["volume"])
                vol_ok = row["volume"] > vol * self.vol_multiplier
                if pull and bounce and vol_ok:
                    direction = "LONG"

            # SHORT
            in_downtrend_1h = row["close"] < row["ema21"] and row["ema21"] < row["ema200"]
            in_downtrend_4h = row_4h["close"] < row_4h["ema21"] and row_4h["ema21"] < row_4h["ema200"]
            
            if in_downtrend_1h and in_downtrend_4h:
                pull = prev3.get("rsi14", 50) < (self.rsi_short_entry - 10) and prev2.get("rsi14", prev3.get("rsi14")) > prev3.get("rsi14", 50)
                bounce = prev.get("rsi14", 50) > self.rsi_short_entry and row["rsi14"] < prev.get("rsi14", 50) - self.rsi_bounce_min
                vol = row.get("vol_sma50", row["volume"])
                vol_ok = row["volume"] > vol * self.vol_multiplier
                if pull and bounce and vol_ok:
                    direction = "SHORT"

            if direction:
                signals.iloc[i] = direction

        return signals
