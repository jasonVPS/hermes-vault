"""
Bybit Paper Trading Agent
Führt Trades auf Bybit Demo aus, trackt Ergebnisse,
und lernt daraus.
"""
import os
import sys
import time
import json
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

sys.path.insert(0, '/opt/data/home/hermes-vault/30_Projects/Trading-Agent')
from core.broker import BrokerFactory, TradingMode, Order
from strategies.backtest_engine import (MeanReversionStrategy, TrendFollowingStrategy,
                                         MomentumStrategy, BreakoutStrategy, BacktestEngine)
from agents.journal import TradeJournal, TradeRecord

import pandas as pd
import sqlite3


class BybitPaperAgent:
    """Autonomer Paper-Trading-Agent für Bybit Demo."""

    def __init__(self):
        self.mode = TradingMode.PAPER
        self.broker = BrokerFactory.create("bybit", self.mode)
        self.journal = TradeJournal()
        self.population_path = "/opt/data/home/hermes-vault/30_Projects/Trading-Agent/population/genesis.json"
        self.db_path = "/opt/data/home/hermes-vault/30_Projects/Trading-Agent/data/market_data.db"
        
        # Load strategy population
        self.population = self._load_population()
        
        # Strategy map
        self.strategy_classes = {
            "MeanReversion_Bollinger": MeanReversionStrategy,
            "TrendFollowing_EMA": TrendFollowingStrategy,
            "Momentum_Supertrend": MomentumStrategy,
            "Breakout_Donchian": BreakoutStrategy,
        }

    def _load_population(self) -> Dict:
        with open(self.population_path) as f:
            return json.load(f)

    def _save_population(self):
        with open(self.population_path, 'w') as f:
            json.dump(self.population, f, indent=2)

    def connect(self) -> bool:
        print("[BybitPaper] Connecting to Bybit DEMO...")
        ok = self.broker.connect()
        if ok:
            print(f"[BybitPaper] ✅ Connected to DEMO")
            # Try balance - if no API keys, use simulated
            try:
                bal = self.broker.get_balance()
                print(f"[BybitPaper] Balance: {bal}")
            except Exception as e:
                print(f"[BybitPaper] ⚠️ API Keys needed for balance. Using simulated equity: 1000 USDT")
                self.simulated_equity = 1000.0
        return ok

    def get_market_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
        """Fetch latest market data from local DB or broker."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            f"SELECT * FROM ohlcv WHERE symbol='{symbol}' AND timeframe='{timeframe}' ORDER BY timestamp DESC LIMIT {limit}",
            conn,
            parse_dates=['timestamp']
        )
        conn.close()
        
        if len(df) < 50:
            # Fallback: fetch fresh
            df = self.broker.get_ohlcv(symbol, timeframe, limit)
            if df is not None:
                df['symbol'] = symbol
                df['timeframe'] = timeframe
            return df
        
        df.sort_index(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame, symbol: str, timeframe: str) -> List[Dict]:
        """Generiert Signale für alle aktiven Strategien."""
        signals = []
        
        for strat_config in self.population['strategies']:
            if not strat_config.get('active', True):
                continue
            
            strat_name = strat_config['name']
            strat_id = strat_config['id']
            params = strat_config['params']
            
            # Instantiate strategy with params
            strat_cls = self.strategy_classes.get(strat_name)
            if not strat_cls:
                continue
            
            try:
                strat = strat_cls(**params)
                signal = strat.generate_signal(df, len(df) - 1)
                
                if signal and signal.direction != 0:
                    signals.append({
                        'strategy_id': strat_id,
                        'strategy_name': strat_name,
                        'direction': 'long' if signal.direction == 1 else 'short',
                        'entry_price': signal.entry_price,
                        'stop_loss': signal.stop_loss,
                        'take_profit': signal.take_profit,
                        'confidence': signal.confidence,
                        'symbol': symbol,
                        'timeframe': timeframe,
                        'params_snapshot': params,
                        'signal_obj': signal,
                    })
            except Exception as e:
                print(f"[BybitPaper] ⚠️ {strat_name} error: {e}")
        
        return signals

    def execute_paper_trade(self, signal: Dict, equity: float = 1000.0) -> Optional[Dict]:
        """Executes a paper trade on Bybit Demo."""
        dir_mult = 1 if signal['direction'] == 'long' else -1
        entry = signal['entry_price']
        sl = signal['stop_loss']
        tp = signal['take_profit']
        
        # Position sizing: 1% risk
        risk_pct = 0.01
        risk_amount = equity * risk_pct
        risk_per_unit = abs(entry - sl)
        if risk_per_unit == 0:
            return None
        
        size = risk_amount / risk_per_unit
        
        # Leverage based on confidence (higher confidence = more leverage, capped at 5x)
        leverage = min(1 + signal['confidence'] * 4, 5.0)
        
        print(f"[BybitPaper] 📊 PAPER TRADE")
        print(f"  Strategy: {signal['strategy_name']} ({signal['strategy_id']})")
        print(f"  Direction: {signal['direction']} | Size: {size:.6f} | Leverage: {leverage:.1f}x")
        print(f"  Entry: {entry:.2f} | SL: {sl:.2f} | TP: {tp:.2f}")
        print(f"  Risk: {risk_amount:.2f} USDT ({risk_pct*100:.0f}% of equity)")
        
        trade_id = f"paper_{signal['strategy_id']}_{int(time.time())}_{random.randint(1000,9999)}"
        
        # Record in journal
        trade_record = TradeRecord(
            trade_id=trade_id,
            strategy_id=signal['strategy_id'],
            strategy_name=signal['strategy_name'],
            symbol=signal['symbol'],
            timeframe=signal['timeframe'],
            direction=signal['direction'],
            entry_time=datetime.utcnow().isoformat() + 'Z',
            exit_time=None,
            entry_price=entry,
            exit_price=None,
            size=size,
            leverage=leverage,
            stop_loss=sl,
            take_profit=tp,
            pnl_abs=0,
            pnl_pct=0,
            exit_reason='open',
            fees=0,
            market_context=None,
            indicators_at_entry=None,
            generation=self.population.get('generation', 1),
            params_snapshot=signal['params_snapshot'],
        )
        
        self.journal.record_entry(trade_record)
        
        # Simulate order placement (DEMO)
        simulated_order = {
            'trade_id': trade_id,
            'status': 'filled',
            'symbol': signal['symbol'],
            'side': signal['direction'],
            'size': size,
            'entry_price': entry,
            'stop_loss': sl,
            'take_profit': tp,
            'leverage': leverage,
            'equity_at_risk': risk_amount,
            'confidence': signal['confidence'],
            'paper': True,
        }
        
        print(f"[BybitPaper] ✅ Trade recorded: {trade_id}")
        return simulated_order

    def check_open_trades(self):
        """Überprüft offene Trades und schließt bei SL/TP."""
        conn = sqlite3.connect(self.journal.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT trade_id, symbol, direction, entry_price, stop_loss, take_profit, entry_time, strategy_id
            FROM trades WHERE exit_time IS NULL
        ''')
        
        open_trades = c.fetchall()
        
        for trade in open_trades:
            trade_id, symbol, direction, entry, sl, tp, entry_time, strat_id = trade
            
            # Get current price
            ticker = self.broker.get_ticker(symbol)
            current_price = ticker.get('last') or ticker.get('ask')
            
            if current_price is None:
                continue
            
            exit_triggered = False
            exit_price = None
            exit_reason = None
            
            if direction == 'long':
                if current_price <= sl:
                    exit_triggered = True
                    exit_price = current_price
                    exit_reason = 'sl'
                elif current_price >= tp:
                    exit_triggered = True
                    exit_price = current_price
                    exit_reason = 'tp'
            elif direction == 'short':
                if current_price >= sl:
                    exit_triggered = True
                    exit_price = current_price
                    exit_reason = 'sl'
                elif current_price <= tp:
                    exit_triggered = True
                    exit_price = current_price
                    exit_reason = 'tp'
            
            if exit_triggered:
                # Calculate PnL
                if direction == 'long':
                    pnl = (exit_price - entry) * 1  # size simplification
                else:
                    pnl = (entry - exit_price) * 1
                
                pnl_pct = (pnl / entry) * 100 if entry != 0 else 0
                
                self.journal.record_exit(
                    trade_id,
                    datetime.utcnow().isoformat() + 'Z',
                    exit_price,
                    pnl,
                    pnl_pct,
                    exit_reason
                )
                
                emoji = "🔴" if pnl < 0 else "🟢"
                print(f"[BybitPaper] {emoji} EXIT {trade_id}: {exit_reason.upper()}")
                print(f"  Entry: {entry:.2f} | Exit: {exit_price:.2f} | PnL: {pnl_pct:+.2f}%")
        
        conn.close()

    def run_cycle(self, symbols: List[str] = None):
        """Ein vollständiger Trading-Zyklus."""
        if not self.broker.connected:
            print("[BybitPaper] Not connected!")
            return
        
        if symbols is None:
            symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT"]
        
        print(f"\n[BybitPaper] {'='*60}")
        print(f"[BybitPaper] 🔄 Trading Cycle: {datetime.utcnow().isoformat()}Z")
        print(f"[BybitPaper] {'='*60}")
        
        # 1. Check exits
        self.check_open_trades()
        
        # 2. Check entries
        for symbol in symbols:
            print(f"\n[BybitPaper] Checking {symbol}...")
            df = self.get_market_data(symbol, "1h", limit=200)
            
            if df is None or len(df) < 50:
                print(f"  ⛔ Not enough data")
                continue
            
            signals = self.generate_signals(df, symbol, "1h")
            
            if not signals:
                print(f"  📭 No signals")
                continue
            
            # Take best signal (highest confidence)
            best_signal = max(signals, key=lambda s: s['confidence'])
            
            if best_signal['confidence'] > 0.3:  # Only trade if confidence > 30%
                trade = self.execute_paper_trade(best_signal)
                if trade:
                    print(f"  ✅ Paper trade executed")
            else:
                print(f"  ⚠️  Best signal confidence too low ({best_signal['confidence']:.2%})")

        # 3. Check evolution trigger
        perf = self.journal.get_strategy_performance()
        if perf.get('num_trades', 0) >= 5:  # After 5 trades, show performance
            print(f"\n[BybitPaper] 📈 Performance: {perf}")

    def evolve(self):
        """Lässt die Evolution laufen (nach genügend Trades)."""
        print("\n[BybitPaper] 🧬 EVOLUTION CHECK")
        
        # Get all strategies with performance
        for strat in self.population['strategies']:
            strat_id = strat['id']
            perf = self.journal.get_strategy_performance(strat_id)
            
            if perf['num_trades'] >= self.population['evolution_rules']['min_trades_before_evolution']:
                strat['fitness'] = {
                    'trades': perf['num_trades'],
                    'win_rate': perf['win_rate'],
                    'total_pnl_pct': perf['total_pnl_pct'],
                    'profit_factor': perf['profit_factor'],
                    'sharpe': perf['sharpe'],
                    'last_updated': datetime.utcnow().isoformat() + 'Z'
                }
                
                print(f"  {strat_id}: {perf['num_trades']} trades, {perf['win_rate']}% WR, {perf['total_pnl_pct']}% PnL")
        
        # Save updated population
        self._save_population()
        print("  ✅ Population updated")


if __name__ == "__main__":
    print("=" * 70)
    print(" BYBIT PAPER TRADING AGENT")
    print(" Mode: DEMO | Auto-learn: ENABLED")
    print("=" * 70)
    
    agent = BybitPaperAgent()
    
    if agent.connect():
        # Run one cycle
        agent.run_cycle()
        
        # Check evolution
        agent.evolve()
        
        print("\n✅ Cycle complete. Open trades tracked in journal.")
    else:
        print("\n❌ Could not connect to Bybit Demo.")
