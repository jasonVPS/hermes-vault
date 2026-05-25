"""
Single Source of Truth Backtest Engine v2.
Deterministic, SL/TP-only, instrumented.
"""
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from data.features import add_indicators, classify_regime

@dataclass
class Trade:
    entry_time: str
    exit_time: Optional[str] = None
    direction: str = ""
    entry: float = 0.0
    sl: float = 0.0
    tp: float = 0.0
    exit_price: Optional[float] = None
    pnl: float = 0.0
    pnl_pct: float = 0.0
    regime: str = ""
    context: Dict = field(default_factory=dict)
    status: str = "OPEN"

@dataclass
class BacktestResult:
    trades: List[Trade]
    equity_curve: List[dict]
    metrics: dict
    log: List[str]

def compute_metrics(equity: List[float], trades: List[Trade]) -> dict:
    eq_arr = np.array(equity)
    if len(eq_arr) < 2:
        daily_returns = np.array([0.0])
    else:
        daily_returns = np.diff(eq_arr) / eq_arr[:-1]
    sharpe = np.mean(daily_returns) / (np.std(daily_returns) + 1e-9) * np.sqrt(365)

    peak = np.maximum.accumulate(eq_arr)
    drawdown = (peak - eq_arr) / peak
    max_dd = np.max(drawdown)

    pnls = [t.pnl for t in trades if t.status != "OPEN"]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    pf = sum(wins) / (abs(sum(losses)) + 1e-9)
    wr = len(wins) / len(pnls) if pnls else 0.0

    return {
        "pf": round(pf, 3),
        "sharpe": round(sharpe, 3),
        "win_rate": round(wr, 3),
        "max_dd_pct": round(max_dd * 100, 2),
        "trades": len(pnls),
        "avg_trade": round(sum(pnls) / len(pnls), 2) if pnls else 0.0,
        "total_return_pct": round((eq_arr[-1] / eq_arr[0] - 1) * 100, 2),
    }

class BacktestEngine:
    def __init__(self, df: pd.DataFrame, strategy, initial_capital: float = 10000.0):
        self.df = df.copy()
        self.strategy = strategy
        self.capital = initial_capital
        self.equity = [initial_capital]
        self.trades: List[Trade] = []
        self.log: List[str] = []
        self._i = 0

    def run(self) -> BacktestResult:
        # Enrich dataframe with features and regime
        self.df = add_indicators(self.df)
        self.df["regime"] = classify_regime(self.df)
        
        signals = self.strategy.generate_signals(self.df)
        self.df["signal"] = signals

        for i in range(1, len(self.df)):
            self._i = i
            row = self.df.iloc[i]
            prev = self.df.iloc[i - 1]

            # Check exits for open trade
            self._check_exits(row)

            # New entry if no open position
            if not any(t.status == "OPEN" for t in self.trades):
                if prev["signal"] in ("LONG", "SHORT"):
                    self._open_trade(prev["signal"], row, i)

            self.equity.append(self._current_equity(row))

        # Close any remaining open trade at last price
        last_price = self.df.iloc[-1]["close"]
        for t in self.trades:
            if t.status == "OPEN":
                t.status = "CLOSED_EOD"
                t.exit_price = last_price
                t.exit_time = str(self.df.index[-1])
                size = t.context.get("size", 0)
                t.pnl = (last_price - t.entry) * size if t.direction == "LONG" else (t.entry - last_price) * size
                t.pnl_pct = t.pnl / self.capital * 100

        metrics = compute_metrics(self.equity, self.trades)
        return BacktestResult(trades=self.trades, equity_curve=self._make_curve(), metrics=metrics, log=self.log)

    def _current_equity(self, row) -> float:
        eq = self.capital
        for t in self.trades:
            if t.status == "OPEN":
                size = t.context.get("size", 0)
                if t.direction == "LONG":
                    eq += (row["close"] - t.entry) * size
                else:
                    eq += (t.entry - row["close"]) * size
        return eq

    def _open_trade(self, direction: str, row, idx: int):
        entry = row["open"]  # next-candle-open entry
        atr = abs(row.get("atr14", row["high"] - row["low"]))
        risk_amt = self.capital * 0.02
        size = risk_amt / (atr + 1e-9)
        sl = entry - 1.5 * atr if direction == "LONG" else entry + 1.5 * atr
        tp = entry + 3.0 * atr if direction == "LONG" else entry - 3.0 * atr

        regime = row.get("regime", "unknown")
        context = {
            "rsi": round(float(row.get("rsi14", 0)), 2),
            "ema_spread": round(float(row.get("ema21", 0)) - float(row.get("ema8", 0)), 2),
            "adx": round(float(row.get("adx14", 0)), 2),
            "size": size,
            "rr": 2.0,
        }

        trade = Trade(
            entry_time=str(self.df.index[idx]),
            direction=direction,
            entry=round(entry, 2),
            sl=round(sl, 2),
            tp=round(tp, 2),
            regime=regime,
            context=context,
        )
        self.trades.append(trade)
        self.log.append(f"OPEN {direction} @ {entry} SL={sl} TP={tp} regime={regime}")

    def _check_exits(self, row):
        for t in self.trades:
            if t.status != "OPEN":
                continue
            if t.direction == "LONG":
                if row["low"] <= t.sl:
                    t.exit_price = t.sl
                    t.status = "CLOSED_SL"
                elif row["high"] >= t.tp:
                    t.exit_price = t.tp
                    t.status = "CLOSED_TP"
            else:  # SHORT
                if row["high"] >= t.sl:
                    t.exit_price = t.sl
                    t.status = "CLOSED_SL"
                elif row["low"] <= t.tp:
                    t.exit_price = t.tp
                    t.status = "CLOSED_TP"

            if t.status != "OPEN":
                t.exit_time = str(self.df.index[self._i])
                size = t.context.get("size", 0)
                t.pnl = (t.exit_price - t.entry) * size if t.direction == "LONG" else (t.entry - t.exit_price) * size
                t.pnl_pct = t.pnl / self.capital * 100
                self.capital += t.pnl
                self.log.append(f"{t.status} {t.direction} @ {t.exit_price} PnL={t.pnl:.2f}")

    def _make_curve(self) -> List[dict]:
        return [
            {"timestamp": str(self.df.index[i]), "equity": self.equity[i], "drawdown": 0.0}
            for i in range(len(self.equity))
        ]
