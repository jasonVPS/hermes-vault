---
tags: [finance, tech, trading]
Spec-Version: 1.0
---

# Backtest Engine v2 — Single Source of Truth

**Erklärung:** EINE Engine. Gate, Evolve, Worker — alle nutzen dieselbe `engine/backtest.py`. Keine divergierenden Implementierungen mehr.

---

## Design Principles

1. **Determinismus:** Seedbar, keine Zufälligkeit
2. **SL/TP-Only:** Keine Reversal-Exits, kein Trailing-Stop
3. **Instrumentiert:** Jeder Trade logged: Entry-Context (RSI, EMA-Spread, Regime-Label)
4. **OHLCV-Only:** Keine Orderbook- oder Tick-Daten

## Interface

```python
from engine.backtest import BacktestEngine

engine = BacktestEngine(df_ohlcv, strategy, initial_capital=10000.0)
result = engine.run()
# result: {trades: DataFrame, equity_curve: list, metrics: dict, log: list}
```

## Trade Rules

- Entry: Next-Candle-Open nach Signal (kein Same-Bar-Entry)
- SL/TP: Intra-Candle-Hit möglich (High/Low berühren Level)
- Size: Fixed Fractional (`risk_pct / atr_based_risk`)
- Kein Partial Close, kein Scale-In
- Max 1 offene Position pro Asset

## Output Metrics

```
metrics = {
    "pf": float,           # Profit Factor
    "sharpe": float,       # Sharpe Ratio (daily)
    "win_rate": float,     # 0.0 - 1.0
    "max_dd_pct": float,   # Peak-to-Trough %
    "trades": int,         # N
    "avg_trade": float,    # $/Trade
    "total_return_pct": float,
}
```

## Equity Curve Format

```python
equity_curve = [
    {"timestamp": "2026-01-01T00:00:00Z", "equity": 10000.0, "drawdown": 0.0},
    ...
]
```

## Trade Log Format

```python
trades = [
    {
        "entry_time": str, "exit_time": str,
        "direction": "LONG|SHORT",
        "entry": float, "sl": float, "tp": float, "exit": float,
        "pnl": float, "pnl_pct": float,
        "regime": "trend|range|transition",
        "context": {"rsi": float, "ema_spread": float, "adx": float}
    }
]
```

---

**Warnung:** Engine-Änderungen müssen retroaktiv alle Gate-Results invalidieren (Versions-Tag in State).
