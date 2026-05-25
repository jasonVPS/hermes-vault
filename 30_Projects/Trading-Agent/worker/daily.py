"""
Daily Worker: Data -> Backtest -> Score -> Reflect -> Report.
Runs 1x/day at 06:00 UTC via cron after Gate passes.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent")
sys.path.insert(0, str(ROOT))

from data.fetcher import load_all
from data.features import add_indicators, classify_regime
from engine.backtest import BacktestEngine
from strategies.regime_aware import RegimeAwareStrategy
from gate.gate import evaluate
from journal.journal import log_trade, reflect_trade, daily_summary

ASSETS = ["BTCUSDT", "ETHUSDT", "DOGEUSDT", "SOLUSDT", "HYPEUSDT"]
DATA_DIR = ROOT / "state" / "logs"

def run_daily_cycle(asset_data: dict) -> dict:
    """Run full cycle for one asset."""
    strategy = RegimeAwareStrategy()
    engine = BacktestEngine(asset_data["1h"], strategy, initial_capital=10000.0)
    result = engine.run()

    # Journal every closed trade
    for t in result.trades:
        if t.status != "OPEN":
            trade_dict = t.__dict__
            trade_dict["asset"] = asset_data.get("symbol", "UNKNOWN")
            log_trade(trade_dict)
            reflect_trade(trade_dict)

    return {
        "metrics": result.metrics,
        "trades": len([t for t in result.trades if t.status != "OPEN"]),
        "log": result.log[:5],  # first 5 log entries
    }

def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Daily Worker Start")
    print("Loading data...")
    all_data = load_all(lookback_days=30)

    reports = {}
    for asset in ASSETS:
        print(f"Processing {asset}...")
        reports[asset] = run_daily_cycle(all_data[asset])
        m = reports[asset]["metrics"]
        print(f"  Trades: {reports[asset]['trades']} | PF: {m['pf']} | Sharpe: {m['sharpe']} | WR: {m['win_rate']} | DD: {m['max_dd_pct']}%")

    # Save daily report
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    out_file = DATA_DIR / f"daily_report_{timestamp}.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(reports, f, indent=2)

    # Daily summary
    summary = daily_summary()
    print(f"\nDaily Summary: {summary}")

    print("Daily Worker complete.")
    return reports

if __name__ == "__main__":
    main()
