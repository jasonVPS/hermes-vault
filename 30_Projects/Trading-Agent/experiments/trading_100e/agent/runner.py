"""
Adaptive Scalping Agent
Runs every N minutes (cron), manages positions, learns.
Target: 100€ → 200€ in 30 days
"""
import sys
sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')

import os, json, sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

from experiments.trading_100e.strategy.scalping import ScalpingStrategy
from experiments.trading_100e.learn.engine import LearningEngine
from core.data_cleaner import load_raw

# ─── STATE ───────────────────────────────────────────────────
STATE_DIR = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/experiments/trading_100e/agent")
STATE_FILE = STATE_DIR / "state.json"
DB_FILE = STATE_DIR / "trades.db"
STATE_DIR.mkdir(parents=True, exist_ok=True)

class Position:
    """Active position with multi-TP management"""
    def __init__(self, signal, equity, ts=None):
        self.ts = ts or datetime.now(timezone.utc).isoformat()
        self.symbol = "BTC/USDT"
        self.dir = signal.dir
        self.entry = signal.entry
        self.sl = signal.sl
        self.tp1 = signal.tp1
        self.tp2 = signal.tp2
        self.tp3 = signal.tp3
        self.size_pct = signal.size_pct
        self.setup_score = signal.setup_score
        self.reasons = signal.reasons
        
        # Position sizing
        self.risk_usd = equity * signal.size_pct
        sl_dist = abs(self.entry - self.sl)
        self.size = self.risk_usd / sl_dist if sl_dist > 0 else 0  # in base units
        
        # TP tracking
        self.tp1_hit = False
        self.tp2_hit = False
        self.tp3_hit = False
        self.closed = False
        self.pnl = 0.0
        self.exit_reason = ""
        self.exit_price = None
        
        # Dynamic SL
        self.current_sl = self.sl
        
    def check_exit(self, high, low, close):
        """Returns (closed, pnl, reason) if position closes this bar"""
        if self.closed:
            return False, 0, ""
        
        # Check SL
        if self.dir == 'long' and low <= self.current_sl:
            return self._close(self.current_sl, "SL")
        if self.dir == 'short' and high >= self.current_sl:
            return self._close(self.current_sl, "SL")
        
        # Check TPs
        if not self.tp1_hit:
            if self.dir == 'long' and high >= self.tp1:
                self.tp1_hit = True
                # Move SL to breakeven + buffer
                self.current_sl = self.entry * (1 + 0.001)
                print(f"  💰 TP1 hit @ {self.tp1}, SL moved to BE")
            elif self.dir == 'short' and low <= self.tp1:
                self.tp1_hit = True
                self.current_sl = self.entry * (1 - 0.001)
                print(f"  💰 TP1 hit @ {self.tp1}, SL moved to BE")
        
        if self.tp1_hit and not self.tp2_hit:
            if self.dir == 'long' and high >= self.tp2:
                self.tp2_hit = True
                self.current_sl = self.tp1  # Lock TP1
                print(f"  💰💰 TP2 hit @ {self.tp2}, SL locked at TP1")
            elif self.dir == 'short' and low <= self.tp2:
                self.tp2_hit = True
                self.current_sl = self.tp1
                print(f"  💰💰 TP2 hit @ {self.tp2}, SL locked at TP1")
        
        if self.tp2_hit and not self.tp3_hit:
            if self.dir == 'long' and high >= self.tp3:
                self.tp3_hit = True
                return self._close(self.tp3, "TP3")
            elif self.dir == 'short' and low <= self.tp3:
                self.tp3_hit = True
                return self._close(self.tp3, "TP3")
        
        # Max hold time (8h)
        entry_ts = datetime.fromisoformat(self.ts.replace('Z', '+00:00'))
        if datetime.now(timezone.utc) - entry_ts > timedelta(hours=8):
            return self._close(close, "TIME_EXPIRED")
        
        return False, 0, ""
    
    def _close(self, price, reason):
        self.closed = True
        self.exit_price = price
        self.exit_reason = reason
        
        # Calculate P&L for full position (simplified)
        if self.dir == 'long':
            raw_pnl = (price - self.entry) / self.entry
        else:
            raw_pnl = (self.entry - price) / self.entry
        
        costs = 0.0012  # 0.06% in + out
        self.pnl = raw_pnl - costs
        
        return True, self.pnl, reason
    
    def unrealized(self, current_price):
        """Current unrealized P&L %"""
        if self.dir == 'long':
            return (current_price - self.entry) / self.entry
        return (self.entry - current_price) / self.entry - 0.0012


class ScalpingAgent:
    def __init__(self):
        self.strategy = ScalpingStrategy()
        self.learner = LearningEngine()
        self.equity = 100.0  # start 100€
        self.position = None
        self._load_state()
        self._init_db()
    
    def _load_state(self):
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                s = json.load(f)
                self.equity = s.get('equity', 100.0)
    
    def _save_state(self):
        with open(STATE_FILE, 'w') as f:
            json.dump({
                'equity': self.equity,
                'last_run': datetime.now(timezone.utc).isoformat(),
            }, f, indent=2)
    
    def _init_db(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                ts TEXT,
                symbol TEXT,
                dir TEXT,
                entry REAL,
                exit REAL,
                sl REAL,
                tp1 REAL, tp2 REAL, tp3 REAL,
                tp_hit INTEGER,
                pnl_pct REAL,
                pnl_abs REAL,
                setup_score INTEGER,
                size_pct REAL,
                reasons TEXT,
                exit_reason TEXT,
                params TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def _log_trade(self, pos: Position, params: dict):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO trades (ts, symbol, dir, entry, exit, sl, tp1, tp2, tp3, 
                              tp_hit, pnl_pct, pnl_abs, setup_score, size_pct, reasons, exit_reason, params)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            pos.ts, pos.symbol, pos.dir, pos.entry, pos.exit_price, pos.sl,
            pos.tp1, pos.tp2, pos.tp3,
            3 if pos.tp3_hit else (2 if pos.tp2_hit else (1 if pos.tp1_hit else 0)),
            pos.pnl, pos.pnl * pos.entry * pos.size,
            pos.setup_score, pos.size_pct, json.dumps(pos.reasons), pos.exit_reason,
            json.dumps(params)
        ))
        conn.commit()
        conn.close()
    
    def run(self):
        """Main cycle - call this every 15m"""
        now = datetime.now(timezone.utc)
        print(f"\n{'='*60}")
        print(f"🤖 Scalping Agent | Equity: ${self.equity:.2f} | {now.strftime('%H:%M')}")
        print(f"{'='*60}")
        
        # 1. Fetch data
        try:
            df_1h = load_raw("BTC/USDT", "1h")
            df_15m = load_raw("BTC/USDT", "15m")
            if df_15m is None or len(df_15m) < 200:
                print("⚠️ Not enough 15m data")
                return
        except Exception as e:
            print(f"❌ Data error: {e}")
            return
        
        last_price = df_15m['close'].iloc[-1]
        
        # 2. Check existing position
        if self.position:
            closed, pnl, reason = self.position.check_exit(
                df_15m['high'].iloc[-1],
                df_15m['low'].iloc[-1],
                last_price
            )
            if closed:
                # Position closed this bar
                pnl_abs = pnl * self.equity
                self.equity += pnl_abs
                
                print(f"📊 POSITION CLOSED")
                print(f"   Reason: {reason}")
                print(f"   P&L: {pnl*100:+.2f}% | ${pnl_abs:+.2f}")
                print(f"   Equity: ${self.equity:.2f}")
                
                # Learn
                self.learner.update({
                    'pnl_abs': pnl_abs,
                    'pnl_pct': pnl,
                    'setup_score': self.position.setup_score,
                    'tp_hit': 3 if self.position.tp3_hit else (2 if self.position.tp2_hit else 1 if self.position.tp1_hit else 0),
                    'bars_held': (now - datetime.fromisoformat(self.position.ts.replace('Z', '+00:00'))).seconds // 900,
                    'dir': self.position.dir,
                    'reasons': self.position.reasons
                })
                
                self._log_trade(self.position, self.learner.get_params())
                self.position = None
                self._save_state()
            else:
                # Show active position status
                unr = self.position.unrealized(last_price)
                print(f"  📈 Active {self.position.dir}: Entry ${self.position.entry:.2f}")
                print(f"     Unrealized: {unr*100:+.2f}%")
                print(f"     SL: ${self.position.current_sl:.2f} | TP3: ${self.position.tp3:.2f}")
                return  # Can't enter new if active
        
        # 3. Look for entry (only if no active position)
        self.strategy = ScalpingStrategy(self.learner.get_params())
        signal = self.strategy.generate(df_15m, equity=self.equity, df_1h=df_1h)
        
        if signal:
            # Validate we can afford it
            risk_usd = self.equity * signal.size_pct
            sl_dist = abs(signal.entry - signal.sl)
            if sl_dist == 0:
                print("  ⚠️ Invalid SL distance")
                return
            
            print(f"\n🎯 SIGNAL DETECTED")
            print(f"   Direction: {signal.dir.upper()}")
            print(f"   Entry: ${signal.entry:.2f} | SL: ${signal.sl:.2f}")
            print(f"   TP1: ${signal.tp1:.2f} | TP2: ${signal.tp2:.2f} | TP3: ${signal.tp3:.2f}")
            print(f"   Risk: {signal.size_pct*100:.1f}% (${risk_usd:.2f})")
            print(f"   Score: {signal.setup_score}/100")
            print(f"   Reasons: {', '.join(signal.reasons)}")
            
            # GO
            self.position = Position(signal, self.equity)
            print(f"\n  ✅ POSITION OPENED")
            print(f"     Size: {self.position.size:.6f} BTC")
            print(f"     Risk: ${self.position.risk_usd:.2f}")
        else:
            print("  📭 No viable setup")
        
        # 4. Show stats
        stats = self.learner.get_stats()
        print(f"\n  📊 Stats: Winrate {stats['winrate']*100:.0f}% | Trades {stats['trades']} | Peak ${stats['peak']:.2f}")


if __name__ == "__main__":
    agent = ScalpingAgent()
    agent.run()
