"""
Bulk 6-Month Data Fetcher + Strategy Grid-Search
Compares multiple strategies over 6 months on multiple coins
Finds the best for 100% in 30 days goal
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

import sqlite3
import requests
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict

DB = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/data/market_data.db")
URL = "https://api.binance.com/api/v3/klines"

COINS = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
    "DOGE/USDT", "ADA/USDT", "LINK/USDT", "AVAX/USDT", "MATIC/USDT"
]

def fetch_klines(symbol: str, interval: str, months: int = 6) -> List[tuple]:
    """Fetch historical klines from Binance"""
    raw = symbol.replace("/", "")
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=30*months)
    
    all_rows = []
    current = start
    chunk = timedelta(minutes=(15 if interval == "15m" else 60) * 999)
    
    while current < end:
        chunk_end = min(current + chunk, end)
        params = {
            "symbol": raw,
            "interval": interval,
            "startTime": int(current.timestamp() * 1000),
            "endTime": int(chunk_end.timestamp() * 1000),
            "limit": 1000,
        }
        try:
            r = requests.get(URL, params=params, timeout=30)
            if r.status_code == 429:
                time.sleep(2)
                continue
            data = r.json()
            if not data or not isinstance(data, list):
                break
        except Exception as e:
            print(f"  Error: {e}")
            break
        
        for candle in data:
            ts = datetime.fromtimestamp(candle[0]/1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            all_rows.append((
                symbol, interval, ts,
                float(candle[1]), float(candle[2]),
                float(candle[3]), float(candle[4]), float(candle[5])
            ))
        
        current = chunk_end
        time.sleep(0.3)
    
    return all_rows

def save_rows(rows: List[tuple]):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.executemany("""
        INSERT OR REPLACE INTO ohlcv 
        (symbol, timeframe, timestamp, open, high, low, close, volume)
        VALUES (?,?,?,?,?,?,?,?)
    """, rows)
    conn.commit()
    conn.close()

def verify():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT symbol, timeframe, COUNT(*) FROM ohlcv GROUP BY symbol, timeframe ORDER BY symbol")
    print("\n=== DATABASE STATE ===")
    for row in c.fetchall():
        print(f"  {row[0]:12s} {row[1]:4s} {row[2]:5d} rows")
    conn.close()

if __name__ == "__main__":
    total = 0
    for coin in COINS:
        for tf in ["15m", "1h"]:
            print(f"Fetching {coin} {tf} (6 months)...")
            rows = fetch_klines(coin, tf, months=6)
            if rows:
                save_rows(rows)
                total += len(rows)
                print(f"  Saved {len(rows)} rows")
    
    print(f"\n{'='*60}")
    print(f"Total rows added: {total}")
    verify()
