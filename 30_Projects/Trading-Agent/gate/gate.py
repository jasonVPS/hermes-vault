"""
Multi-Asset Gate. Evaluates strategy on all assets, returns PASS/FAIL.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List

from data.fetcher import load_all
from engine.backtest import BacktestEngine
from strategies.regime_aware import RegimeAwareStrategy

RULES = {
    "pf": {"min": 1.50, "label": "Profit Factor"},
    "sharpe": {"min": 1.00, "label": "Sharpe Ratio"},
    "win_rate": {"min": 0.50, "label": "Win Rate"},
    "max_dd_pct": {"max": 15.0, "label": "Max Drawdown"},
    "trades": {"min": 30, "label": "Trade Count"},
}

ASSETS = ["BTCUSDT", "ETHUSDT", "DOGEUSDT", "SOLUSDT"]

def evaluate(asset_data: Dict) -> Dict:
    """Run backtest and return results + PASS/FAIL per metric."""
    strategy = RegimeAwareStrategy()
    engine = BacktestEngine(asset_data["1h"], strategy, initial_capital=10000.0)
    result = engine.run()

    m = result.metrics
    checks = {}
    all_pass = True

    for key, rule in RULES.items():
        val = m.get(key, 0)
        if "min" in rule and val < rule["min"]:
            checks[key] = {"value": val, "pass": False, "reason": f"{val} < {rule['min']}"}
            all_pass = False
        elif "max" in rule and val > rule["max"]:
            checks[key] = {"value": val, "pass": False, "reason": f"{val} > {rule['max']}"}
            all_pass = False
        else:
            checks[key] = {"value": val, "pass": True}

    return {
        "asset": asset_data.get("symbol", "UNKNOWN"),
        "pass": all_pass,
        "metrics": m,
        "checks": checks,
        "trades": [t.__dict__ for t in result.trades if t.status != "OPEN"],
    }

def run_gate() -> Dict:
    """Full gate run across all assets."""
    print("Loading data (6 months, 1h + 4h)...")
    all_data = load_all(lookback_days=180)

    results = []
    global_pass = True

    for asset in ASSETS:
        print(f"Evaluating {asset}...")
        all_data[asset]["symbol"] = asset
        r = evaluate(all_data[asset])
        results.append(r)
        if not r["pass"]:
            global_pass = False
            print(f"  FAIL: {r['checks']}")
        else:
            print(f"  PASS: PF={r['metrics']['pf']} Sharpe={r['metrics']['sharpe']} WR={r['metrics']['win_rate']}")

    report = {
        "global_pass": global_pass,
        "timestamp": str(pd.Timestamp.now(tz="UTC")),
        "results": results,
    }

    # Save report
    out_dir = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/state/logs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"gate_{pd.Timestamp.now(tz='UTC').strftime('%Y%m%d_%H%M')}.json"
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nGate result: {'✅ PASS' if global_pass else '❌ FAIL'}")
    print(f"Report: {out_file}")
    return report

if __name__ == "__main__":
    import pandas as pd
    report = run_gate()
    sys.exit(0 if report["global_pass"] else 1)
