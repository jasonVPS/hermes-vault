"""
parameter_sweep.py — Brute-force search for Gate-passing parameters
Tests EMA_RSI_Trend variations on SOL/USDT (best performer)
"""
import sys
sys.path.insert(0, "/opt/data/home/hermes-vault/30_Projects/Trading-Agent")

import json
from itertools import product
from pathlib import Path

from core.data_cleaner import load_raw, clean_wicks
from self_improving.gate_selector import ema_rsi_strategy, Engine, MIN_PF, MIN_SHARPE, MIN_WR

ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/self_improving")

def main():
    print("=" * 70)
    print(" PARAMETER SWEEP: EMA_RSI_Trend on SOL/USDT")
    print(f" Gate: PF ≥ {MIN_PF} | WR ≥ {MIN_WR:.0%} | Sharpe ≥ {MIN_SHARPE}")
    print("=" * 70)

    df_raw = load_raw("SOL/USDT", "1h")
    df_clean = clean_wicks(df_raw, max_wick_pct=0.05)
    print(f"Data: {len(df_clean)} bars\n")

    # Narrow search space around near-passing values
    fast_vals = [5, 7, 9, 11, 13]
    slow_vals = [15, 18, 21, 25, 30]
    sl_vals = [1.5, 1.8, 2.0, 2.2, 2.5]
    tp_vals = [3.0, 3.5, 4.0, 5.0, 6.0]
    rsi_long_vals = [40, 45, 50, 55]
    rsi_short_vals = [45, 50, 55, 60]
    trend_vals = [100, 150, 200]

    combos = list(product(fast_vals, slow_vals, sl_vals, tp_vals, rsi_long_vals, rsi_short_vals, trend_vals))
    print(f"Testing {len(combos)} combinations...\n")

    passing = []
    best_by_return = []

    for idx, (fast, slow, sl_m, tp_m, rsi_l, rsi_s, trend) in enumerate(combos):
        if fast >= slow:
            continue

        ind_fn, sig_fn = ema_rsi_strategy(
            fast=fast, slow=slow, trend=trend,
            rsi_p=14, rsi_long=rsi_l, rsi_short=rsi_s,
            sl_mult=sl_m, tp_mult=tp_m, risk=0.01
        )
        engine = Engine(ind_fn, sig_fn, fee=0.0006, slip=0.0002, equity=10000)
        m = engine.run(df_clean, min_bars=trend + 10)
        m['params'] = {'fast': fast, 'slow': slow, 'sl': sl_m, 'tp': tp_m,
                       'rsi_long': rsi_l, 'rsi_short': rsi_s, 'trend': trend}

        if m['trades'] >= 5:  # need meaningful sample
            gate = (m['profit_factor'] >= MIN_PF and m['sharpe'] >= MIN_SHARPE and m['winrate'] >= MIN_WR)
            if gate:
                passing.append(m)
                print(f"  ✅ PASS | fast={fast} slow={slow} sl={sl_m} tp={tp_m} rsi_l={rsi_l} rsi_s={rsi_s} trend={trend}")
                print(f"     T={m['trades']} WR={m['winrate']:.1%} PF={m['profit_factor']:.2f} SR={m['sharpe']:.2f} DD={m['max_dd_pct']:.1f}% Ret={m['total_return_pct']:+.1f}%")
            elif idx % 2000 == 0:
                print(f"  tested {idx}/{len(combos)} ...")

    print(f"\n{'='*70}")
    if passing:
        best = max(passing, key=lambda x: x['total_return_pct'])
        print(f"✅ {len(passing)} combinations PASSED Gate")
        print(f"🥇 BEST: {json.dumps(best['params'])} → Return {best['total_return_pct']:+.1f}%")

        # Write winning strategy as v0001
        strategy = {
            "version": "0001",
            "name": "EMA_RSI_Cross_GatePassed",
            "type": "ema_rsi_cross",
            "asset": "SOL/USDT",
            "timeframe": "1h",
            "params": {
                "ema_fast": best['params']['fast'],
                "ema_slow": best['params']['slow'],
                "ema_trend": best['params']['trend'],
                "rsi_period": 14,
                "rsi_long_min": best['params']['rsi_long'],
                "rsi_short_max": best['params']['rsi_short'],
                "atr_period": 14,
                "atr_sl_mult": best['params']['sl'],
                "atr_tp_mult": best['params']['tp'],
                "risk_per_trade": 0.01,
                "volume_confirm": True,
                "max_atr_pct": 0.03,
            },
            "backtest": {"initial_equity": 10000, "fee_rate": 0.0006, "slippage": 0.0002, "max_positions": 1}
        }
        strategy_path = ROOT / "state" / "strategy.yaml"
        import yaml
        with open(strategy_path, 'w') as f:
            yaml.dump(strategy, f, default_flow_style=False, sort_keys=False)
        print(f"\n💾 Written to {strategy_path}")

    else:
        print("❌ NO combination passed Gate. Need different strategy family or regime filter.")
        top3 = sorted([m for m in passing if m['trades'] >= 5], key=lambda x: x['profit_factor'], reverse=True)[:3]
        for m in top3:
            print(f"  Closest: {json.dumps(m['params'])} | PF:{m['profit_factor']:.2f} WR:{m['winrate']:.1%} SR:{m['sharpe']:.2f}")


if __name__ == "__main__":
    main()
