"""
Journal: Every single trade is journaled and reflected upon.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/state/logs")
TRADE_LOG = DATA_DIR / "trades.jsonl"
REFLECT_LOG = DATA_DIR / "reflections.jsonl"

def log_trade(trade: Dict):
    """Append a trade to the journal."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRADE_LOG, "a") as f:
        f.write(json.dumps(trade, default=str) + "\n")

def reflect_trade(trade: Dict) -> Dict:
    """
    Reflect on a single trade.
    Why did it win/lose? Was the regime correct? Could parameters improve?
    """
    reflection = {
        "trade_id": trade.get("entry_time", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "asset": trade.get("asset", "UNKNOWN"),
        "direction": trade.get("direction", ""),
        "regime": trade.get("regime", "unknown"),
        "entry": trade.get("entry"),
        "exit": trade.get("exit_price"),
        "pnl": trade.get("pnl"),
        "pnl_pct": trade.get("pnl_pct"),
        "sl": trade.get("sl"),
        "tp": trade.get("tp"),
        "analysis": {},
        "suggested_change": {},
    }

    pnl = trade.get("pnl", 0)
    context = trade.get("context", {})
    rsi = context.get("rsi", 50)
    adx = context.get("adx", 0)

    if pnl > 0:
        reflection["analysis"]["outcome"] = "WIN"
        reflection["analysis"]["why"] = "Regime/strategy aligned with market."
    else:
        reflection["analysis"]["outcome"] = "LOSS"
        reasons = []
        if rsi < 30 and trade["direction"] == "SHORT":
            reasons.append("Shorted oversold market (RSI < 30)")
        if rsi > 70 and trade["direction"] == "LONG":
            reasons.append("Longed overbought market (RSI > 70)")
        if adx > 25 and trade.get("regime") == "range":
            reasons.append("Trend-strength in range regime")
        if not reasons:
            reasons.append("Normal SL hit within strategy rules")
        reflection["analysis"]["why"] = " | ".join(reasons)

        # Suggest parameter tweaks
        if abs(pnl) / 100 > 0.02:  # Loss > 2%
            reflection["suggested_change"] = {
                "action": "tighten_sl",
                "reason": "Loss was large relative to risk budget",
                "old_rr": context.get("rr", 2.0),
                "suggested_rr": context.get("rr", 2.0) + 0.5,
            }
        if adx < 20 and trade.get("regime") == "trend":
            reflection["suggested_change"] = {
                "action": "adjust_regime_threshold",
                "reason": "ADX signaled range, but trade used trend parameters",
                "old_adx_threshold": 25,
                "suggested_adx_threshold": 22,
            }

    with open(REFLECT_LOG, "a") as f:
        f.write(json.dumps(reflection, default=str) + "\n")

    return reflection

def daily_summary(lookback_days: int = 1) -> Dict:
    """Read journal and produce a daily summary."""
    if not TRADE_LOG.exists():
        return {"error": "No trades logged yet"}

    trades = []
    with open(TRADE_LOG) as f:
        for line in f:
            try:
                trades.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Filter by date
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_trades = [t for t in trades if t.get("closed_at", "").startswith(today)]

    pnls = [t["pnl"] for t in today_trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]

    return {
        "date": today,
        "trades": len(today_trades),
        "win_rate": round(len(wins) / len(pnls), 3) if pnls else 0,
        "pnl": round(sum(pnls), 2),
        "avg_win": round(sum(wins) / len(wins), 2) if wins else 0,
        "avg_loss": round(sum(losses) / len(losses), 2) if losses else 0,
        "pf": round(sum(wins) / abs(sum(losses)), 3) if losses else 0.0,
    }

if __name__ == "__main__":
    print(daily_summary())
