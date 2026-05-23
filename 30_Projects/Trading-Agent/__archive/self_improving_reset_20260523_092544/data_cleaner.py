"""
Data Quality Pipeline for OHLCV
- Detects and corrects wick-spike artifacts
- Validates OHLC consistency
- Produces clean DataFrames for backtesting
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

DB_PATH = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/data/market_data.db")

def load_raw(symbol="BTC/USDT", timeframe="1h"):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM ohlcv WHERE symbol=? AND timeframe=? ORDER BY timestamp"
    df = pd.read_sql(query, conn, params=(symbol, timeframe), parse_dates=['timestamp'])
    conn.close()
    return df

def clean_wicks(df, max_wick_pct=0.05):
    """
    Correct wicks that exceed max_wick_pct of median body.
    Assumption: massive single-candle spikes are data artifacts.
    """
    df = df.copy()
    median_body = (df['high'] - df['low']).median()
    
    # Upper wick = high - max(open,close)
    # Lower wick = min(open,close) - low
    upper_wick = df['high'] - np.maximum(df['open'], df['close'])
    lower_wick = np.minimum(df['open'], df['close']) - df['low']
    
    # Cap wicks at max_wick_pct * price (default 5%)
    price_ref = (df['open'] + df['close']) / 2
    max_wick = price_ref * max_wick_pct
    
    # Correct excessive upper wicks
    mask_high = upper_wick > max_wick
    df.loc[mask_high, 'high'] = np.maximum(df['open'], df['close']) + max_wick[mask_high]
    
    # Correct excessive lower wicks
    mask_low = lower_wick > max_wick
    df.loc[mask_low, 'low'] = np.minimum(df['open'], df['close']) - max_wick[mask_low]
    
    # Ensure high >= low
    df['high'] = np.maximum(df['high'], df['low'])
    
    return df

def validate(df):
    """Check O <= H, L <= H, L <= C, O >= L etc."""
    checks = {
        'low_leq_high': (df['low'] <= df['high']).all(),
        'low_leq_close': (df['low'] <= df['close']).all(),
        'low_leq_open': (df['low'] <= df['open']).all(),
        'high_geq_close': (df['high'] >= df['close']).all(),
        'high_geq_open': (df['high'] >= df['open']).all(),
        'no_nan': not df[['open','high','low','close']].isnull().any().any(),
    }
    return checks

if __name__ == "__main__":
    df_raw = load_raw("BTC/USDT", "1h")
    print(f"Raw loaded: {len(df_raw)} rows")
    
    df_clean = clean_wicks(df_raw, max_wick_pct=0.05)
    print(f"Cleaned: {len(df_clean)} rows")
    
    checks = validate(df_clean)
    print(f"Validation: {checks}")
    
    # Show before/after of worst candle
    worst_idx = (df_raw['high'] - df_raw['low']).idxmax()
    print(f"\n=== WORST CANDLE FIX ===")
    print("RAW:")
    print(df_raw.loc[worst_idx][['timestamp','open','high','low','close']])
    print("CLEAN:")
    print(df_clean.loc[worst_idx][['timestamp','open','high','low','close']])
