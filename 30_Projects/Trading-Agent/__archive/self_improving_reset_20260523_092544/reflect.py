"""
reflect.py — Self-Improving Strategy Reflection Engine
RULE: Exactly ONE variable changes per cycle. Scientific method.
Modes:
  --deterministic  : rule-based reflection (fallback, no LLM)
  --smart          : calls hermes for hypothesis generation
"""
import yaml
import json
import shutil
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import sys

ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/self_improving")
STATE_DIR = ROOT / "state"
HISTORY_DIR = STATE_DIR / "history"
STRATEGY_PATH = STATE_DIR / "strategy.yaml"
HYPOTHESES_PATH = STATE_DIR / "hypotheses.jsonl"
SCORE_PATH = ROOT / "score.py"

# Parameter space for search (min, max, step, type)
PARAM_SPACE = {
    "ema_fast":       {"min": 5,   "max": 25,  "step": 1,   "type": "int"},
    "ema_slow":       {"min": 15,  "max": 55,  "step": 1,   "type": "int"},
    "ema_trend":      {"min": 100, "max": 300, "step": 20,  "type": "int"},
    "rsi_period":     {"min": 7,   "max": 21,  "step": 1,   "type": "int"},
    "rsi_long_min":   {"min": 35,  "max": 55,  "step": 1,   "type": "int"},
    "rsi_short_max":  {"min": 45,  "max": 65,  "step": 1,   "type": "int"},
    "atr_sl_mult":    {"min": 1.0, "max": 4.0, "step": 0.2,  "type": "float"},
    "atr_tp_mult":    {"min": 2.0, "max": 8.0, "step": 0.5,  "type": "float"},
    "risk_per_trade": {"min": 0.005, "max": 0.03, "step": 0.001, "type": "float"},
    "max_atr_pct":    {"min": 0.01, "max": 0.05, "step": 0.005, "type": "float"},
}

BOOL_PARAMS = ["volume_confirm"]

# ── Helpers ────────────────────────────────────────────────────

def load_strategy() -> Dict[str, Any]:
    with open(STRATEGY_PATH) as f:
        return yaml.safe_load(f)

def save_strategy(data: Dict[str, Any]):
    with open(STRATEGY_PATH, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

def bump_version(current: str) -> str:
    """v01 -> v02, v99 -> v100 (4-digit zero-padded)"""
    current_clean = current.lstrip('v')
    try:
        n = int(current_clean)
        return f"{n + 1:04d}"
    except ValueError:
        return "0002"

def archive_strategy(current_strat: Dict[str, Any]):
    """Save current version to history before any change."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    ver = current_strat.get("version", "01")
    dest = HISTORY_DIR / f"v{ver.zfill(4)}.yaml"
    shutil.copy2(STRATEGY_PATH, dest)
    return dest

def append_hypothesis(record: Dict[str, Any]):
    with open(HYPOTHESES_PATH, 'a') as f:
        f.write(json.dumps(record, default=str) + "\n")

# ── Deterministic Reflection ───────────────────────────────────

def deterministic_pick(trades: list, metrics: Dict[str, Any]) -> Tuple[str, Any, str]:
    """
    Analyse metrics and deterministic rules to pick ONE variable.
    Returns: (param_name, new_value, reasoning)
    """
    current = load_strategy()
    params = current["params"]

    wr = metrics.get("winrate", metrics.get("win_rate", 0))
    if isinstance(wr, float) and wr <= 1:
        wr *= 100
    dd = metrics.get("max_drawdown_pct", metrics.get("max_dd_pct", 0))
    sharpe = metrics.get("sharpe", 0)
    pf = metrics.get("profit_factor", metrics.get("pf", 0))
    ret = metrics.get("total_return_pct", metrics.get("return_pct", 0))
    trades_count = len(trades) if trades else metrics.get("trades", 0)

    # Rule precedence: most obvious problem first

    # 1. Too few trades: loosen entry filter
    if trades_count < 10:
        if params.get("volume_confirm", True):
            return "volume_confirm", False, "Too few trades: disable volume confirmation to get more signals"
        # Widen RSI thresholds
        return "rsi_long_min", max(35, params["rsi_long_min"] - 3), "Too few trades: lower RSI long threshold for more entries"

    # 2. Win rate too low < 40%: tighten entry or widen SL
    if wr < 40:
        if params["atr_sl_mult"] > 1.0:
            new_sl = round(max(1.0, params["atr_sl_mult"] - 0.2), 1)
            return "atr_sl_mult", new_sl, f"Low WR ({wr:.1f}%): tighten SL from {params['atr_sl_mult']} to {new_sl} — stop bad entries faster"
        else:
            # Tighten RSI
            new_rsi = min(55, params["rsi_long_min"] + 2)
            return "rsi_long_min", new_rsi, f"Low WR ({wr:.1f}%): raise RSI threshold for stronger confirmation"

    # 3. High drawdown > 6%: tighten risk or widen SL
    if dd > 6:
        if params["risk_per_trade"] > 0.005:
            new_risk = round(params["risk_per_trade"] - 0.002, 3)
            return "risk_per_trade", new_risk, f"High DD ({dd:.1f}%): reduce risk from {params['risk_per_trade']} to {new_risk}"
        if params["atr_sl_mult"] < 4.0:
            new_sl = round(min(4.0, params["atr_sl_mult"] + 0.2), 1)
            return "atr_sl_mult", new_sl, f"High DD ({dd:.1f}%): widen SL from {params['atr_sl_mult']} to {new_sl}"

    # 4. Negative return: explore faster signal
    if ret < 0:
        if params["ema_fast"] > 5:
            new_fast = max(5, params["ema_fast"] - 1)
            return "ema_fast", new_fast, f"Negative return ({ret:.1f}%): faster EMA for earlier entries"

    # 5. Sharpe too low < 0.3: improve R:R
    if sharpe < 0.3:
        if params["atr_tp_mult"] < 8.0:
            new_tp = round(min(8.0, params["atr_tp_mult"] + 0.5), 1)
            return "atr_tp_mult", new_tp, f"Low Sharpe ({sharpe:.2f}): improve R:R — TP from {params['atr_tp_mult']} to {new_tp}"

    # 6. Conservative exploration if nothing obvious
    # Pick the parameter that was changed longest ago
    if HYPOTHESES_PATH.exists():
        lines = open(HYPOTHESES_PATH).readlines()
        if lines:
            last_changed = []
            for line in reversed(lines):
                rec = json.loads(line)
                last_changed.append(rec.get("changed_param", ""))
            # Find parameter NOT changed recently
            candidates = [p for p in PARAM_SPACE if p not in last_changed[:5]]
            if candidates:
                param = random.choice(candidates)
            else:
                param = random.choice(list(PARAM_SPACE.keys()))
        else:
            param = random.choice(list(PARAM_SPACE.keys()))
    else:
        param = random.choice(list(PARAM_SPACE.keys()))

    meta = PARAM_SPACE[param]
    if meta["type"] == "int":
        new_val = random.choice(range(meta["min"], meta["max"] + 1, meta["step"]))
    else:
        steps = int((meta["max"] - meta["min"]) / meta["step"]) + 1
        idx = random.randint(0, steps - 1)
        new_val = round(meta["min"] + idx * meta["step"], 3)
    return param, new_val, f"Exploration: probing {param} = {new_val} (no obvious problem detected)"


# ── Core Reflection ────────────────────────────────────────────

def reflect(trades: list, metrics: Dict[str, Any], mode: str = "deterministic") -> Dict[str, Any]:
    """
    Perform one reflection cycle.
    Archives old strategy, changes ONE variable, logs hypothesis.
    Returns record of what happened.
    """
    current = load_strategy()
    ver = current.get("version", "01")

    # 1. Archive current version (BEFORE change)
    archive_path = archive_strategy(current)

    # 2. Pick the ONE variable to change
    if mode == "deterministic":
        param, new_val, reasoning = deterministic_pick(trades, metrics)
    else:
        # TODO: smart mode — call hermes or LLM for hypothesis generation
        param, new_val, reasoning = deterministic_pick(trades, metrics)

    # 3. Apply change (ONE variable only)
    old_val = current["params"].get(param)
    current["params"][param] = new_val
    new_ver = bump_version(ver)
    current["version"] = new_ver

    # 4. Save new strategy
    save_strategy(current)

    # 5. Build hypothesis record
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": ver,
        "new_version": new_ver,
        "changed_param": param,
        "old_value": old_val,
        "new_value": new_val,
        "reasoning": reasoning,
        "metrics_at_change": {
            "return_pct": metrics.get("total_return_pct", metrics.get("return_pct", 0)),
            "drawdown_pct": metrics.get("max_drawdown_pct", metrics.get("max_dd_pct", 0)),
            "sharpe": metrics.get("sharpe", 0),
            "winrate": metrics.get("winrate", metrics.get("win_rate", 0)),
            "profit_factor": metrics.get("profit_factor", 0),
            "trades": len(trades) if trades else metrics.get("trades", 0),
        },
        "mode": mode,
    }

    # 6. Append to hypotheses log
    append_hypothesis(record)

    return record


def main():
    """CLI usage: reflect on live data."""
    import argparse
    parser = argparse.ArgumentParser(description="Reflect and adapt strategy")
    parser.add_argument("--metrics-file", help="JSON file with backtest metrics")
    parser.add_argument("--mode", default="deterministic", choices=["deterministic", "smart"])
    args = parser.parse_args()

    if args.metrics_file:
        with open(args.metrics_file) as f:
            data = json.load(f)
        metrics = data.get("metrics", data)
        trades = data.get("trades", [])
    else:
        # Demo mode with synthetic data
        metrics = {"total_return_pct": 2.1, "max_drawdown_pct": 5.5, "sharpe": 0.25,
                   "winrate": 0.38, "profit_factor": 1.05, "trades": 8}
        trades = []

    result = reflect(trades, metrics, mode=args.mode)
    print(json.dumps(result, indent=2, default=str))
    print(f"\n✓ Strategy updated: v{result['version']} → v{result['new_version']}")
    print(f"  Changed: {result['changed_param']} = {result['old_value']} → {result['new_value']}")


if __name__ == "__main__":
    main()
