#!/usr/bin/env python3
"""
Mini Grid Search on 90 days BTC data to find best strategy params.
"""
import sys
from pathlib import Path
import itertools

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from data.fetcher import fetch_ohlcv
from data.features import add_indicators, classify_regime
from engine.backtest import BacktestEngine
from strategies.regime_aware import RegimeAwareStrategy

print("Loading BTC 1h last 90 days...")
df = fetch_ohlcv("BTCUSDT", "1h", lookback_days=90)

# Parameter grid
grid = {
    "rsi_long_entry": [35, 40, 45, 50],
    "rsi_short_entry": [50, 55, 60, 65],
    "rsi_bounce_min": [1.0, 2.0, 3.0],
    "adx_min": [15, 20, 25],
    "vol_multiplier": [0.3, 0.5, 0.8],
}

best = None
best_score = -999

keys = list(grid.keys())
for combo in itertools.product(*grid.values()):
    kwargs = dict(zip(keys, combo))
    strat = RegimeAwareStrategy(**kwargs)
    engine = BacktestEngine(df.copy(), strat, initial_capital=10000.0)
    result = engine.run()
    m = result.metrics

    # Filter: need at least 10 trades
    if m["trades"] < 10:
        continue

    # Score: PF * Sharpe * WR * 100 / (max_dd + 1)
    score = (m["pf"] * m["sharpe"] * (m["win_rate"] + 0.01)) / (m["max_dd_pct"] + 1)

    if score > best_score:
        best_score = score
        best = {"params": kwargs, "metrics": m, "score": score}
        print(f"NEW BEST: {kwargs} -> PF={m['pf']} Sharpe={m['sharpe']} WR={m['win_rate']} DD={m['max_dd_pct']}% Trades={m['trades']} Score={score:.4f}")

print("\n=== Best parameters ===")
if best:
    print(f"Params: {best['params']}")
    print(f"Metrics: {best['metrics']}")
else:
    print("No valid combination found in grid.")
