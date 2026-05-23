"""
worker.py — Self-Improving Trading Worker (Unified Engine)
Run: python3 worker.py --symbol ETH/USDT --timeframe 1h

Steps:
1. Load strategy.yaml + goal.yaml
2. Fetch clean data (via data_cleaner)
3. Run backtest with current params (using common_engine)
4. Score results vs goal
5. Log trades to trades.jsonl
6. Append score to scores.jsonl
7. If trades_since_last_reflect >= reflection_every: trigger reflect
"""
import sys
sys.path.insert(0, "/opt/data/home/hermes-vault/30_Projects/Trading-Agent")

import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime

from core.data_cleaner import load_raw, clean_wicks
from self_improving.score import score
from self_improving.common_engine import BacktestEngine
from self_improving.gate_selector import ema_rsi_strategy, calc_atr

ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/self_improving")
STATE_DIR = ROOT / "state"
STRATEGY_PATH = STATE_DIR / "strategy.yaml"
GOAL_PATH = STATE_DIR / "goal.yaml"
TRADES_PATH = STATE_DIR / "trades.jsonl"
SCORES_PATH = STATE_DIR / "scores.jsonl"
HYPOTHESES_PATH = STATE_DIR / "hypotheses.jsonl"


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def build_strategy(strategy_config: dict):
    """Build strategy functions from config."""
    p = strategy_config["params"]
    fee = strategy_config.get("backtest", {}).get("fee_rate", 0.0006)
    slip = strategy_config.get("backtest", {}).get("slippage", 0.0002)

    def indicators(df):
        return ema_rsi_strategy(
            p["ema_fast"], p["ema_slow"], p["ema_trend"], p["rsi_period"],
            p["rsi_long_min"], p["rsi_short_max"], p["atr_sl_mult"], p["atr_tp_mult"], p["risk_per_trade"]
        )[0](df)

    def signal_fn(df, i, equity):
        return ema_rsi_strategy(
            p["ema_fast"], p["ema_slow"], p["ema_trend"], p["rsi_period"],
            p["rsi_long_min"], p["rsi_short_max"], p["atr_sl_mult"], p["atr_tp_mult"], p["risk_per_trade"]
        )[1](df, i, equity)

    return indicators, signal_fn, fee, slip


def append_trades(trades: list, version: str):
    now = datetime.now().astimezone().isoformat()
    with open(TRADES_PATH, 'a') as f:
        for t in trades:
            rec = {
                "timestamp": now,
                "version": version,
                "entry_time": str(t.entry_time),
                "dir": t.dir,
                "entry": round(t.entry_price, 2),
                "exit": round(t.exit_price, 2) if t.exit_price else None,
                "pnl_pct": round(float(t.pnl_pct) * 100, 4),
                "exit_reason": t.exit_reason,
            }
            f.write(json.dumps(rec) + "\n")


def append_score(score_result: dict, version: str):
    import numpy as np
    with open(SCORES_PATH, 'a') as f:
        rec = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "version": version,
            "total": float(score_result["total"]),
            "passed_gate": bool(score_result.get("passed_gate", False)),
            "components": {k: float(v) for k, v in score_result.get("components", {}).items()},
            "actuals": {k: float(v) if isinstance(v, (int, float, np.number)) else v
                        for k, v in score_result.get("actuals", {}).items()},
        }
        f.write(json.dumps(rec) + "\n")


def run_once(symbol, timeframe):
    strategy = load_yaml(STRATEGY_PATH)
    goal = load_yaml(GOAL_PATH)

    print(f"Worker | Strategy v{strategy['version']} | {symbol} @ {timeframe}")
    print(f"  Params: ema_fast={strategy['params']['ema_fast']}, ema_slow={strategy['params']['ema_slow']}, atr_sl={strategy['params']['atr_sl_mult']}, atr_tp={strategy['params']['atr_tp_mult']}")

    # Load data
    df_raw = load_raw(symbol, timeframe)
    df_clean = clean_wicks(df_raw, max_wick_pct=0.05)
    print(f"  Data: {len(df_clean)} bars (cleaned)")

    # Build strategy + run backtest
    ind_fn, sig_fn, fee, slip = build_strategy(strategy)
    engine = BacktestEngine(ind_fn, sig_fn, fee, slip,
                            strategy.get("backtest", {}).get("initial_equity", 10000))
    metrics = engine.run(df_clean, min_bars=strategy['params']['ema_trend'] + 10)

    print(f"\n  Trades: {metrics['trades']} | WR: {metrics['winrate']:.1%} | PF: {metrics['profit_factor']:.2f} | Return: {metrics['total_return_pct']:+.2f}% | DD: {metrics['max_dd_pct']:.2f}% | Sharpe: {metrics['sharpe']:.2f}")

    # Score vs goal
    sc = score(metrics)
    print(f"  Score: {sc['total']:+.3f} | Gate: {'PASS' if sc['passed_gate'] else 'FAIL'}")
    for k, v in sc['components'].items():
        print(f"    {k}: {v:+.3f}")

    # Log trades + score
    append_trades(engine.trades, strategy['version'])
    append_score(sc, strategy['version'])

    # Trigger reflection if enough trades
    trades_count = engine.trades.__len__()  # actual trades executed
    reflection_every = goal.get("reflection_every", 5)
    if trades_count >= reflection_every:
        print(f"\n  [REFLECT TRIGGERED] {trades_count} trades >= {reflection_every}")
        from self_improving.reflect import reflect
        record = reflect(engine.trades, metrics, mode="deterministic")
        print(f"  → v{record['version']} → v{record['new_version']} | Changed: {record['changed_param']} {record['old_value']} → {record['new_value']}")
    else:
        print(f"\n  [NO REFLECT] Only {trades_count}/{reflection_every} trades — accumulating.")

    return metrics, sc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="ETH/USDT")
    parser.add_argument("--timeframe", default="1h")
    args = parser.parse_args()
    run_once(args.symbol, args.timeframe)


if __name__ == "__main__":
    main()
