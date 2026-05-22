"""
Simplified Adaptive Paper Trading Agent
Learns from outcomes, adapts parameters.
Runs on Bybit Demo (no real money).
"""
import os
import sys
import time
import json
import random
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')
from core.broker import BrokerFactory, TradingMode, Order
import pandas as pd
import numpy as np

DB_DIR = "/opt/data/home/hermes-vault/30_Projects/Trading-Agent/data"
JOURNAL_PATH = f"{DB_DIR}/trade_journal.db"
POLICY_PATH = f"{DB_DIR}/policy.json"

os.makedirs(DB_DIR, exist_ok=True)

def _init_db():
    conn = sqlite3.connect(JOURNAL_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id TEXT PRIMARY KEY,
            ts TEXT,
            strategy TEXT,
            symbol TEXT,
            dir TEXT,
            entry REAL,
            exit REAL,
            sl REAL,
            tp REAL,
            status TEXT,
            pnl_pct REAL,
            reason TEXT,
            context TEXT
        )
    """)
    conn.commit()
    conn.close()

_init_db()

# ═══════════════════════════════════════════════════════════
# EVOLUTION / POLICY
# ═══════════════════════════════════════════════════════════

DEFAULT_POLICY = {
    "generation": 1,
    "strategies": {
        "trend_ema": {"ema_fast": 9, "ema_slow": 21, "win": 0, "loss": 0, "pnl": 0},
        "mean_rev": {"bb_period": 20, "bb_std": 2.0, "win": 0, "loss": 0, "pnl": 0},
        "momentum": {"atr": 10, "factor": 3.0, "win": 0, "loss": 0, "pnl": 0},
    }
}

def load_policy():
    if os.path.exists(POLICY_PATH):
        with open(POLICY_PATH) as f:
            return json.load(f)
    return DEFAULT_POLICY

def save_policy(p):
    with open(POLICY_PATH, 'w') as f:
        json.dump(p, f, indent=2)

# ═══════════════════════════════════════════════════════════
# STRATEGIES
# ═══════════════════════════════════════════════════════════

def strat_trend_ema(df, policy):
    """EMA Crossover with HA."""
    P = policy["strategies"]["trend_ema"]
    close = df['close']
    fast = close.ewm(span=int(P["ema_fast"])).mean().iloc[-1]
    slow = close.ewm(span=int(P["ema_slow"])).mean().iloc[-1]
    atr = df.ta.atr(length=14).iloc[-1] if hasattr(df, 'ta') else (df['high']-df['low']).rolling(14).mean().iloc[-1]
    
    if fast > slow:
        return {"dir": "long", "entry": close.iloc[-1], "sl": close.iloc[-1] - 2*atr, "tp": close.iloc[-1] + 4*atr}
    elif fast < slow:
        return {"dir": "short", "entry": close.iloc[-1], "sl": close.iloc[-1] + 2*atr, "tp": close.iloc[-1] - 4*atr}
    return None

def strat_mean_rev(df, policy):
    """Bollinger mean reversion."""
    P = policy["strategies"]["mean_rev"]
    close = df['close']
    mid = close.rolling(int(P["bb_period"])).mean().iloc[-1]
    std = close.rolling(int(P["bb_period"])).std().iloc[-1]
    upper, lower = mid + P["bb_std"]*std, mid - P["bb_std"]*std
    price = close.iloc[-1]
    atr = (df['high']-df['low']).rolling(14).mean().iloc[-1]
    
    if price < lower:
        return {"dir": "long", "entry": price, "sl": price - 1.5*atr, "tp": mid}
    if price > upper:
        return {"dir": "short", "entry": price, "sl": price + 1.5*atr, "tp": mid}
    return None

def strat_momentum(df, policy):
    """Supertrend simplified."""
    P = policy["strategies"]["momentum"]
    hl2 = (df['high'] + df['low']) / 2
    atr = (df['high']-df['low']).rolling(int(P["atr"])).mean().iloc[-1]
    upper = hl2.iloc[-1] + P["factor"] * atr
    lower = hl2.iloc[-1] - P["factor"] * atr
    price = df['close'].iloc[-1]
    
    if price > upper:
        return {"dir": "long", "entry": price, "sl": price - 1.5*atr, "tp": price + 3.5*atr}
    if price < lower:
        return {"dir": "short", "entry": price, "sl": price + 1.5*atr, "tp": price - 3.5*atr}
    return None

STRATEGIES = {
    "trend_ema": strat_trend_ema,
    "mean_rev": strat_mean_rev,
    "momentum": strat_momentum,
}

# ═══════════════════════════════════════════════════════════
# MAIN AGENT
# ═══════════════════════════════════════════════════════════

class AdaptivePaperAgent:
    def __init__(self):
        self.broker = BrokerFactory.create("bybit", TradingMode.PAPER)
        self.policy = load_policy()
        self.equity = 1000.0
        self.connected = False

    def connect(self):
        ok = self.broker.connect()
        print(f"[AGENT] Bybit DEMO: {'✅' if ok else '❌'}")
        self.connected = ok
        return ok

    def run_cycle(self, symbols=None):
        if not self.connected:
            print("[AGENT] Not connected")
            return

        if symbols is None:
            symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT"]

        print(f"\n{'='*60}")
        print(f"[AGENT] 🔄 Cycle: {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*60}")

        # Check exits
        self._check_exits(symbols)

        # Generate entries
        for sym in symbols:
            print(f"\n[AGENT] {sym} ...")
            df = self.broker.get_ohlcv(sym, "1h", limit=100)
            if df is None or len(df) < 50:
                print(f"  ⛔ No data")
                continue

            best = None
            best_conf = -1

            for name, fn in STRATEGIES.items():
                sig = fn(df, self.policy)
                if sig:
                    conf = self._confidence(sig, df)
                    if conf > best_conf:
                        best_conf = conf
                        best = {**sig, "strategy": name, "symbol": sym}

            if best and best_conf > 0.25:
                self._enter(best, best_conf)
            else:
                print(f"  📭 No signal (best_conf={best_conf:.2f})")

        # Learn after cycle
        self._adapt()

    def _confidence(self, sig, df):
        """0-1 scale based on ATR distance."""
        atr = (df['high']-df['low']).rolling(14).mean().iloc[-1]
        price = df['close'].iloc[-1]
        sl_dist = abs(price - sig['sl']) / price
        return max(0, min(1, 1 - sl_dist * 10))  # tighter SL = higher confidence

    def _enter(self, sig, conf):
        entry = sig['entry']
        sl = sig['sl']
        risk = self.equity * 0.01
        sl_dist = abs(entry - sl)
        size = risk / sl_dist if sl_dist > 0 else 0

        tid = f"T{int(time.time())}_{random.randint(1000,9999)}"
        row = {
            "id": tid, "ts": datetime.now(timezone.utc).isoformat(),
            "strategy": sig['strategy'], "symbol": sig['symbol'],
            "dir": sig['dir'], "entry": entry, "exit": None,
            "sl": sl, "tp": sig['tp'], "status": "open",
            "pnl_pct": 0, "reason": None,
            "context": json.dumps({"conf": conf, "equity": self.equity})
        }

        conn = sqlite3.connect(JOURNAL_PATH)
        pd.DataFrame([row]).to_sql('trades', conn, if_exists='append', index=False)
        conn.close()

        print(f"  🟢 ENTRY [{tid}] {sig['strategy']}")
        print(f"    Dir: {sig['dir'].upper()} | Size: {size:.4f} | Entry: {entry:.2f}")
        print(f"    SL: {sl:.2f} | TP: {sig['tp']:.2f} | Conf: {conf:.1%}")

    def _check_exits(self, symbols):
        conn = sqlite3.connect(JOURNAL_PATH)
        c = conn.cursor()
        c.execute("SELECT id, symbol, dir, entry, sl, tp FROM trades WHERE status='open'")
        open_tr = c.fetchall()

        for tid, sym, direction, entry, sl, tp in open_tr:
            ticker = self.broker.get_ticker(sym)
            price = ticker.get('last') or ticker.get('ask', 0)

            exited = False
            reason = None
            exit_p = price

            if direction == 'long':
                if price <= sl: exited = True; reason = 'sl'
                elif price >= tp: exited = True; reason = 'tp'
            else:  # short
                if price >= sl: exited = True; reason = 'sl'
                elif price <= tp: exited = True; reason = 'tp'

            if exited:
                pnl = ((price - entry) / entry * 100) if direction == 'long' else ((entry - price) / entry * 100)
                c.execute(
                    "UPDATE trades SET status='closed', exit=?, pnl_pct=?, reason=? WHERE id=?",
                    (price, pnl, reason, tid)
                )
                print(f"  🔴 EXIT [{tid}] {reason.upper()} | PnL: {pnl:+.2f}%")

        conn.commit()
        conn.close()

    def _adapt(self):
        """Update policy after each closed trade."""
        conn = sqlite3.connect(JOURNAL_PATH)
        df = pd.read_sql_query("SELECT strategy, pnl_pct, reason FROM trades WHERE status='closed'", conn)
        conn.close()

        if len(df) == 0:
            return

        for strat in self.policy["strategies"]:
            mask = df['strategy'] == strat
            if mask.any():
                wins = int((df.loc[mask, 'pnl_pct'] > 0).sum())
                losses = int((df.loc[mask, 'pnl_pct'] <= 0).sum())
                pnl = float(df.loc[mask, 'pnl_pct'].sum())
                self.policy["strategies"][strat]["win"] = wins
                self.policy["strategies"][strat]["loss"] = losses
                self.policy["strategies"][strat]["pnl"] = round(pnl, 2)

                # Learn: if loss rate high, mutate param
                total = wins + losses
                if total >= 5 and wins / total < 0.35:
                    print(f"[ADAPT] 🧬 {strat} underperforming ({wins}/{total}). Mutating...")
                    self._mutate(strat)

        save_policy(self.policy)

    def _mutate(self, strat_name):
        """Nudge parameters based on failure."""
        P = self.policy["strategies"][strat_name]
        if strat_name == "trend_ema":
            P["ema_fast"] = random.choice([5, 8, 9, 12, 15])
            P["ema_slow"] = random.choice([21, 26, 30, 50])
        elif strat_name == "mean_rev":
            P["bb_period"] = random.choice([14, 20, 26])
            P["bb_std"] = round(random.uniform(1.8, 2.5), 1)
        elif strat_name == "momentum":
            P["atr"] = random.choice([7, 10, 14])
            P["factor"] = round(random.uniform(2.0, 4.0), 1)

        print(f"[ADAPT] → New: {P}")


if __name__ == "__main__":
    print("=" * 60)
    print(" ADAPTIVE PAPER TRADING AGENT")
    print(" Mode: Bybit DEMO | Auto-learn: ON")
    print("=" * 60)

    agent = AdaptivePaperAgent()
    if agent.connect():
        agent.run_cycle()
    else:
        print("❌ Connection failed")
