"""
Binance Spot OHLCV fetcher — free public API, no keys.
Timeframes: 1h (primary), 4h (regime bias).
Lookback: 6 months.
"""
import requests
import pandas as pd
from datetime import datetime, timezone
import time

BASE_URL = "https://api.binance.com/api/v3/klines"
ASSETS = ["BTCUSDT", "ETHUSDT", "DOGEUSDT", "SOLUSDT"]
TF_MAP = {"1h": "1h", "4h": "4h"}
LIMIT = 500  # max per call

def fetch_ohlcv(symbol: str, interval: str = "1h", lookback_days: int = 180) -> pd.DataFrame:
    """Fetch historical klines from Binance Spot."""
    end_ms = int(time.time() * 1000)
    start_ms = int((time.time() - lookback_days * 86400) * 1000)

    all_data = []
    while start_ms < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ms,
            "limit": LIMIT,
        }
        r = requests.get(BASE_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        all_data.extend(data)
        start_ms = data[-1][0] + 1
        time.sleep(0.2)  # be nice to Binance

    df = pd.DataFrame(all_data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_vol", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.astype({
        "open": float, "high": float, "low": float,
        "close": float, "volume": float,
    })
    df.set_index("open_time", inplace=True)
    return df[["open", "high", "low", "close", "volume"]]

def load_all(lookback_days: int = 180) -> dict:
    """Load all assets for both timeframes. Returns {asset: {"1h": df, "4h": df}}."""
    result = {}
    for asset in ASSETS:
        result[asset] = {}
        for tf in TF_MAP:
            result[asset][tf] = fetch_ohlcv(asset, tf, lookback_days)
    return result

if __name__ == "__main__":
    data = load_all(lookback_days=30)
    for a in data:
        print(f"{a}: 1h={len(data[a]['1h'])} rows, 4h={len(data[a]['4h'])} rows")
