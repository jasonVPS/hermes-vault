"""
Adaptive Agent - Journal System
Speichert jeden Trade mit Marktkontext.
Lernt aus Ergebnissen und passt Strategie-Parameter an.
"""
import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TradeRecord:
    """Einzelner Trade mit vollem Kontext."""
    trade_id: str
    strategy_id: str
    strategy_name: str
    symbol: str
    timeframe: str
    direction: str  # 'long' | 'short'
    entry_time: str
    exit_time: Optional[str]
    entry_price: float
    exit_price: Optional[float]
    size: float
    leverage: float
    stop_loss: float
    take_profit: float
    pnl_abs: float
    pnl_pct: float
    exit_reason: str  # 'tp' | 'sl' | 'manual' | 'signal_flip'
    fees: float
    
    # Marktkontext zum Zeitpunkt des Entry
    market_context: Optional[Dict] = None
    
    # Indikatoren zum Zeitpunkt des Entry
    indicators_at_entry: Optional[Dict] = None
    
    # Adaptiv: Was hat zu diesem Trade geführt?
    generation: int = 1
    params_snapshot: Optional[Dict] = None


class TradeJournal:
    """SQLite-basiertes Trade-Journal mit Lernfähigkeit."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = "/opt/data/home/hermes-vault/30_Projects/Trading-Agent/journals/trade_journal.db"
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        
        # Trades
        c.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                trade_id TEXT PRIMARY KEY,
                strategy_id TEXT,
                strategy_name TEXT,
                symbol TEXT,
                timeframe TEXT,
                direction TEXT,
                entry_time TEXT,
                exit_time TEXT,
                entry_price REAL,
                exit_price REAL,
                size REAL,
                leverage REAL,
                stop_loss REAL,
                take_profit REAL,
                pnl_abs REAL,
                pnl_pct REAL,
                exit_reason TEXT,
                fees REAL,
                market_context TEXT,
                indicators_at_entry TEXT,
                generation INTEGER,
                params_snapshot TEXT
            )
        ''')
        
        # Lern-Metriken pro Strategie/Generation
        c.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                strategy_id TEXT,
                generation INTEGER,
                symbol TEXT,
                timeframe TEXT,
                num_trades INTEGER,
                win_rate REAL,
                avg_pnl_pct REAL,
                total_pnl_pct REAL,
                profit_factor REAL,
                max_drawdown REAL,
                sharpe REAL,
                avg_trade_duration TEXT,
                best_exit_reason TEXT,
                worst_exit_reason TEXT,
                params TEXT,
                updated_at TEXT,
                PRIMARY KEY (strategy_id, generation, symbol, timeframe)
            )
        ''')
        
        # Adaption History
        c.execute('''
            CREATE TABLE IF NOT EXISTS adaptions (
                adaption_id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_id TEXT,
                generation INTEGER,
                old_params TEXT,
                new_params TEXT,
                reason TEXT,
                performance_before REAL,
                performance_after REAL,
                timestamp TEXT
            )
        ''')
        
        self.conn.commit()

    def record_entry(self, trade: TradeRecord):
        """Speichert Trade beim Entry (ohne Exit-Daten)."""
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO trades VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
        ''', (
            trade.trade_id, trade.strategy_id, trade.strategy_name,
            trade.symbol, trade.timeframe, trade.direction,
            trade.entry_time, None, trade.entry_price, None,
            trade.size, trade.leverage, trade.stop_loss, trade.take_profit,
            0, 0, 'open', trade.fees,
            json.dumps(trade.market_context) if trade.market_context else None,
            json.dumps(trade.indicators_at_entry) if trade.indicators_at_entry else None,
            trade.generation,
            json.dumps(trade.params_snapshot) if trade.params_snapshot else None
        ))
        self.conn.commit()

    def record_exit(self, trade_id: str, exit_time: str, exit_price: float,
                    pnl_abs: float, pnl_pct: float, exit_reason: str):
        """Aktualisiert Trade mit Exit-Daten."""
        c = self.conn.cursor()
        c.execute('''
            UPDATE trades 
            SET exit_time=?, exit_price=?, pnl_abs=?, pnl_pct=?, exit_reason=?
            WHERE trade_id=?
        ''', (exit_time, exit_price, pnl_abs, pnl_pct, exit_reason, trade_id))
        self.conn.commit()

    def get_strategy_performance(self, strategy_id: str, generation: int = None,
                                  symbol: str = None, timeframe: str = None) -> Dict:
        """Berechnet Performance-Metriken einer Strategie."""
        c = self.conn.cursor()
        
        query = '''SELECT * FROM trades WHERE strategy_id=?'''
        params = [strategy_id]
        
        if generation:
            query += ' AND generation=?'
            params.append(generation)
        if symbol:
            query += ' AND symbol=?'
            params.append(symbol)
        if timeframe:
            query += ' AND timeframe=?'
            params.append(timeframe)
        
        c.execute(query + ' AND exit_time IS NOT NULL', params)
        rows = c.fetchall()
        
        if not rows:
            return {'num_trades': 0, 'win_rate': 0, 'total_pnl_pct': 0}
        
        trades = [r for r in rows]
        pnls = [r[15] for r in trades]  # pnl_pct column
        wins = sum(1 for p in pnls if p > 0)
        
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p < 0))
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
        
        # Max Drawdown
        equity = np.cumsum(pnls)
        peak = np.maximum.accumulate(equity)
        drawdown = np.min((equity - peak) / peak) * 100 if np.any(peak != 0) else 0
        
        return {
            'strategy_id': strategy_id,
            'generation': generation,
            'num_trades': len(trades),
            'win_rate': round(wins / len(trades) * 100, 2),
            'avg_pnl_pct': round(np.mean(pnls), 4),
            'total_pnl_pct': round(sum(pnls), 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(abs(drawdown), 2),
            'sharpe': round(np.mean(pnls) / np.std(pnls) * np.sqrt(252), 2) if np.std(pnls) != 0 else 0,
        }

    def update_strategy_performance_table(self, strategy_id: str, generation: int,
                                           symbol: str, timeframe: str,
                                           params: Dict):
        """Aktualisiert die Performance-Tabelle für die Evolution."""
        perf = self.get_strategy_performance(strategy_id, generation, symbol, timeframe)
        
        c = self.conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO strategy_performance 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            strategy_id, generation, symbol, timeframe,
            perf['num_trades'],
            perf['win_rate'],
            perf['avg_pnl_pct'],
            perf['total_pnl_pct'],
            perf['profit_factor'],
            perf['max_drawdown'],
            perf['sharpe'],
            '~',
            'tp',  # best_exit - todo: calculate
            'sl',  # worst_exit - todo: calculate
            json.dumps(params),
            datetime.utcnow().isoformat()
        ))
        self.conn.commit()

    def get_all_trades(self, strategy_id: str = None, limit: int = 100) -> pd.DataFrame:
        """Liefert Trades als DataFrame für Analyse."""
        c = self.conn.cursor()
        
        query = 'SELECT * FROM trades WHERE exit_time IS NOT NULL'
        params = []
        
        if strategy_id:
            query += ' AND strategy_id=?'
            params.append(strategy_id)
        
        query += ' ORDER BY entry_time DESC LIMIT ?'
        params.append(limit)
        
        c.execute(query, params)
        rows = c.fetchall()
        
        columns = ['trade_id', 'strategy_id', 'strategy_name', 'symbol', 'timeframe',
                   'direction', 'entry_time', 'exit_time', 'entry_price', 'exit_price',
                   'size', 'leverage', 'stop_loss', 'take_profit', 'pnl_abs', 'pnl_pct',
                   'exit_reason', 'fees', 'market_context', 'indicators_at_entry',
                   'generation', 'params_snapshot']
        
        return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)

    def get_adaption_candidates(self, min_trades: int = 20, win_rate_threshold: float = 40.0) -> List[Dict]:
        """Strategien, die Adaption brauchen (schlechte Performance)."""
        c = self.conn.cursor()
        c.execute('''
            SELECT strategy_id, generation, symbol, timeframe, num_trades, win_rate, total_pnl_pct
            FROM strategy_performance
            WHERE num_trades >= ? AND win_rate < ?
            ORDER BY total_pnl_pct ASC
        ''', (min_trades, win_rate_threshold))
        
        rows = c.fetchall()
        return [
            {
                'strategy_id': r[0],
                'generation': r[1],
                'symbol': r[2],
                'timeframe': r[3],
                'num_trades': r[4],
                'win_rate': r[5],
                'total_pnl_pct': r[6]
            }
            for r in rows
        ]

    def get_best_performers(self, limit: int = 3) -> List[Dict]:
        """Top-Performing Strategien für Crossover/Replikation."""
        c = self.conn.cursor()
        c.execute('''
            SELECT strategy_id, generation, symbol, timeframe, 
                   num_trades, win_rate, total_pnl_pct, profit_factor, params
            FROM strategy_performance
            WHERE num_trades >= 10
            ORDER BY total_pnl_pct DESC
            LIMIT ?
        ''', (limit,))
        
        rows = c.fetchall()
        return [
            {
                'strategy_id': r[0],
                'generation': r[1],
                'symbol': r[2],
                'timeframe': r[3],
                'num_trades': r[4],
                'win_rate': r[5],
                'total_pnl_pct': r[6],
                'profit_factor': r[7],
                'params': json.loads(r[8]) if r[8] else {}
            }
            for r in rows
        ]

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    print("Testing TradeJournal...")
    
    journal = TradeJournal()
    
    # Test entry
    trade = TradeRecord(
        trade_id="test_001",
        strategy_id="meanrev_v1",
        strategy_name="MeanReversion_Bollinger",
        symbol="BTC/USDT",
        timeframe="1h",
        direction="long",
        entry_time="2026-05-22T10:00:00Z",
        exit_time=None,
        entry_price=50000,
        exit_price=None,
        size=0.1,
        leverage=1,
        stop_loss=49000,
        take_profit=51500,
        pnl_abs=0,
        pnl_pct=0,
        exit_reason="open",
        fees=5,
        market_context={"volatility": "high", "trend": "sideways"},
        indicators_at_entry={"rsi": 28, "bb_position": 0.05},
        generation=1,
        params_snapshot={"bb_period": 20, "bb_std": 2.0}
    )
    
    journal.record_entry(trade)
    journal.record_exit("test_001", "2026-05-22T12:00:00Z", 51200, 1200, 2.4, "tp")
    
    perf = journal.get_strategy_performance("meanrev_v1", generation=1)
    print(f"Performance: {perf}")
    
    trades = journal.get_all_trades(limit=5)
    print(f"Trades logged: {len(trades)}")
    
    journal.close()
    print("✅ Journal system ready.")
