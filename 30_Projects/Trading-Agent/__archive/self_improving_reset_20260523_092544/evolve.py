"""
evolve.py — Hill-Climbing Parameter Discovery
Finds the FIRST Gate-passing strategy by iteratively exploring parameter space.
Once found: freezes as strategy.yaml v0001, ready for worker/reflect loop.
Gate: PF≥1.2, Sharpe≥0.3, WR≥42%
"""
import sys, json, random
sys.path.insert(0, "/opt/data/home/hermes-vault/30_Projects/Trading-Agent")

from pathlib import Path
from datetime import datetime
import numpy as np

from core.data_cleaner import load_raw, clean_wicks
from self_improving.common_engine import BacktestEngine
from self_improving.gate_selector import ema_rsi_strategy, MIN_PF, MIN_SHARPE, MIN_WR

ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/self_improving")
STATE_DIR = ROOT / "state"

# Start from best known near-miss
BEST_BASE = {"fast": 9, "slow": 21, "trend": 200, "rsi_long": 45, "rsi_short": 55, "sl": 2.0, "tp": 4.0}

PARAM_RANGES = {
    "fast": {"min": 5, "max": 13, "step": 1},
    "slow": {"min": 15, "max": 35, "step": 2},
    "trend": {"min": 100, "max": 300, "step": 50},
    "rsi_long": {"min": 35, "max": 55, "step": 2},
    "rsi_short": {"min": 45, "max": 65, "step": 2},
    "sl": {"min": 1.2, "max": 3.0, "step": 0.2},
    "tp": {"min": 2.5, "max": 7.0, "step": 0.5},
}


def get_neighbor(params):
    """Change ONE random parameter by ±step."""
    p = dict(params)
    key = random.choice(list(PARAM_RANGES.keys()))
    r = PARAM_RANGES[key]
    delta = random.choice([-r["step"], r["step"]])
    new_val = p[key] + delta
    new_val = max(r["min"], min(r["max"], new_val))
    if isinstance(r["step"], int):
        new_val = int(round(new_val))
    else:
        new_val = round(new_val, 2)
    p[key] = new_val
    # Constraint: fast < slow
    if p["fast"] >= p["slow"]:
        p["slow"] = p["fast"] + 2
    # Constraint: rsi_long < rsi_short
    if p["rsi_long"] >= p["rsi_short"]:
        p["rsi_short"] = p["rsi_long"] + 5
    return p


def test_params(p, df):
    ind, sig = ema_rsi_strategy(
        p["fast"], p["slow"], p["trend"], 14, p["rsi_long"], p["rsi_short"], p["sl"], p["tp"]
    )
    e = BacktestEngine(ind, sig, 0.0006, 0.0002, 10000)
    m = e.run(df, min_bars=p["trend"] + 10)
    m['params'] = p
    gate = (m['profit_factor'] >= MIN_PF and m['sharpe'] >= MIN_SHARPE and m['winrate'] >= MIN_WR)
    return m, gate


def hill_climb(df, max_iter=200):
    current = dict(BEST_BASE)
    best = None
    best_score = -999
    tested = []

    # Evaluate starting point
    m, gate = test_params(current, df)
    tested.append(m)
    print(f"  Start: fast={current['fast']} slow={current['slow']} sl={current['sl']} tp={current['tp']} | T={m['trades']} WR={m['winrate']:.1%} PF={m['profit_factor']:.2f} SR={m['sharpe']:.2f}")

    if gate:
        return m

    # Score function for hill climbing: higher = better
    def calc_score(metrics):
        if metrics['trades'] < 5:
            return -999
        # Distance from gate
        pf_gap = max(0, MIN_PF - metrics['profit_factor'])
        sr_gap = max(0, MIN_SHARPE - metrics['sharpe'])
        wr_gap = max(0, MIN_WR - metrics['winrate'])
        dd_penalty = max(0, metrics['max_dd_pct'] - 10) * 0.1
        # Reward return, penalize gaps
        return metrics['total_return_pct'] - (pf_gap * 10 + sr_gap * 10 + wr_gap * 20 + dd_penalty)

    best_score = calc_score(m)
    best = m

    for i in range(max_iter):
        neighbor = get_neighbor(current)
        m, gate = test_params(neighbor, df)
        tested.append(m)

        if gate:
            print(f"\n  ✅ GATE PASSED at iteration {i+1}!")
            print(f"     Params: {json.dumps(neighbor)}")
            print(f"     T={m['trades']} WR={m['winrate']:.1%} PF={m['profit_factor']:.2f} SR={m['sharpe']:.2f} DD={m['max_dd_pct']:.1f}% Ret={m['total_return_pct']:+.1f}%")
            return m

        score = calc_score(m)
        if score > best_score:
            best_score = score
            best = m
            current = dict(neighbor)
            if (i+1) % 20 == 0:
                print(f"  ... iter {i+1}: best score {score:.1f} (PF={m['profit_factor']:.2f} WR={m['winrate']:.1%} SR={m['sharpe']:.2f})")

    print(f"\n  ❌ No Gate-passing combination found after {max_iter} iterations")
    print(f"     Best: {json.dumps(best['params'])} | PF={best['profit_factor']:.2f} WR={best['winrate']:.1%} SR={best['sharpe']:.2f}")
    return None


def discovery_mode():
    """Run hill-climb on all three assets. Return first passing strategy."""
    print("=" * 60)
    print(" EVOLVE: Discovery Mode (Hill Climbing)")
    print("=" * 60)

    assets = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    for sym in assets:
        print(f"\n--- {sym} ---")
        df = clean_wicks(load_raw(sym, "1h"), max_wick_pct=0.05)
        print(f"  Data: {len(df)} bars")
        result = hill_climb(df, max_iter=300)
        if result:
            write_strategy_yaml(result, sym)
            return result

    print("\n" + "=" * 60)
    print("❌ Discovery failed on all assets. Data regime too hostile.")
    print("   Recommend: update data with recent bull market, or lower Gate temporarily.")
    return None


def write_strategy_yaml(result, asset):
    import yaml
    p = result['params']
    strategy = {
        "version": "0001",
        "name": "EMA_RSI_Cross_Evolved",
        "type": "ema_rsi_cross",
        "asset": asset,
        "timeframe": "1h",
        "params": {
            "ema_fast": p['fast'],
            "ema_slow": p['slow'],
            "ema_trend": p['trend'],
            "rsi_period": 14,
            "rsi_long_min": p['rsi_long'],
            "rsi_short_max": p['rsi_short'],
            "atr_period": 14,
            "atr_sl_mult": p['sl'],
            "atr_tp_mult": p['tp'],
            "risk_per_trade": 0.01,
            "volume_confirm": True,
            "max_atr_pct": 0.03,
        },
        "backtest": {"initial_equity": 10000, "fee_rate": 0.0006, "slippage": 0.0002, "max_positions": 1}
    }
    with open(STATE_DIR / "strategy.yaml", 'w') as f:
        yaml.dump(strategy, f, default_flow_style=False, sort_keys=False)
    print(f"\n💾 Written strategy.yaml v0001 for {asset}")


def main():
    result = discovery_mode()
    if result:
        print("\n✅ Strategy locked. Ready to run worker.py + reflect.py loop.")
    else:
        print("\n⚠️ No viable strategy found. Manual intervention or regime change needed.")


if __name__ == "__main__":
    main()
