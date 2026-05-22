"""
Bulk OHLCV fetcher for Binance Spot (public API, no key needed)
Fetches 6 months of 1h data per symbol
Stores to existing SQLite DB
"""
import requests
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path

URL = "https://api.binance.com/api/v3/klines"
DB = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/data/market_data.db")

def fetch_binance(symbol, interval="1h", start_ms=None, end_ms=None, limit=1000):
    """symbol = BTCUSDT (no slash)"""
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    if start_ms:
        params["startTime"] = start_ms
    if end_ms:
        params["endTime"] = end_ms
    
    r = requests.get(URL, params=params, timeout=30)
    if r.status_code != 200:
        print(f"  ❌ HTTP {r.status_code}: {r.text[:100]}")
        return []
    data = r.json()
    if not data:
        return []
    
    rows = []
    for candle in data:
        # Binance kline: [open_time, open, high, low, close, volume, close_time, ...]
        ts = datetime.utcfromtimestamp(candle[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
        rows.append((
            f"{symbol[:-4]}/USDT",  # BTCUSDT -> BTC/USDT
            interval,
            ts,
            float(candle[1]),  # open
            float(candle[2]),  # high
            float(candle[3]),  # low
            float(candle[4]),  # close
            float(candle[5]),  # volume
        ))
    return rows

def fetch_months(symbol, months=6, interval="1h"):
    """Fetch N months of historical data"""
    symbol_raw = symbol.replace("/", "")
    end = datetime.utcnow()
    start = end - timedelta(days=30*months)
    
    all_rows = []
    current = start
    chunk_size = timedelta(hours=999)  # 1000 bars max
    
    print(f"Fetching {symbol} {interval} from {start.date()} to {end.date()}...")
    
    while current < end:
        chunk_end = min(current + chunk_size, end)
        start_ms = int(current.timestamp() * 1000)
        end_ms = int(chunk_end.timestamp() * 1000)
        
        rows = fetch_binance(symbol_raw, interval, start_ms, end_ms)
        if not rows:
            break
        all_rows.extend(rows)
        current = chunk_end
        print(f"  ... fetched {len(rows)} rows, now at {chunk_end}")
        time.sleep(0.5)  # rate limit friendly
    
    print(f"Total: {len(all_rows)} rows for {symbol}")
    return all_rows

def save_to_db(rows):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executemany("""
        INSERT OR REPLACE INTO ohlcv (symbol, timeframe, timestamp, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    c.execute("SELECT symbol, timeframe, COUNT(*) FROM ohlcv GROUP BY symbol, timeframe")
    print("\n=== DB STATE ===")
    for r in c.fetchall():
        print(f"  {r[0]:12s} {r[1]:3s} : {r[2]:5d} rows")
    conn.close()

if __name__ == "__main__":
    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    all_rows = []
    for sym in symbols:
        rows = fetch_months(sym, months=6, interval="1h")
        all_rows.extend(rows)
    
    if all_rows:
        save_to_db(all_rows)
        print(f"\n✅ Saved {len(all_rows)} total rows to database")
    else:
        print("\n⚠️ No data fetched")
