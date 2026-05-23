"""
score.py — Composite Scoring Engine
Reads goal.yaml + backtest metrics, returns score in [-1, +1].
Each sub-score compares actual vs target and is clamped to [-1, +1].
Weights sum to 1.0 and are defined in goal.yaml.
"""
import yaml
from pathlib import Path
import numpy as np
from typing import Dict, Any

ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/self_improving")
GOAL_PATH = ROOT / "state" / "goal.yaml"


def clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def score_return(actual_pct: float, target_pct: float) -> float:
    """
    +1 = achieved or exceeded target return
    -1 = made zero return (breakeven)
    -1 = at failure_below (-4%)
    """
    if target_pct == 0:
        return clamp(actual_pct * 10)
    return clamp(actual_pct / target_pct)


def score_drawdown(actual_dd: float, max_dd: float) -> float:
    """
    +1 = no drawdown at all
    0  = at exactly max_dd boundary
    -1 = exceeded max_dd (bail zone)
    """
    return clamp(1.0 - (actual_dd / max_dd))


def score_sharpe(actual: float, minimum: float) -> float:
    """
    +1 = Sharpe 2.0 or higher (world-class)
    0  = at minimum threshold
    -1 = negative or zero Sharpe
    """
    if minimum == 0:
        return clamp(actual)
    return clamp((actual - minimum) / minimum)


def score_winrate(actual: float, minimum: float) -> float:
    """
    +1 = 60% or higher
    0  = at minimum (42%)
    -1 = zero winrate
    """
    return clamp((actual - minimum) / (0.60 - minimum) if (0.60 - minimum) != 0 else actual)


def score_pf(actual: float, minimum: float) -> float:
    """
    +1 = PF 2.0 or higher
    0  = at minimum (1.2)
    -1 = PF 1.0 or below (no edge)
    """
    return clamp((actual - minimum) / (2.0 - minimum) if (2.0 - minimum) != 0 else actual - minimum)


def load_goal() -> Dict[str, Any]:
    with open(GOAL_PATH) as f:
        return yaml.safe_load(f)


def score(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    metrics: output from backtest engine (dict with keys like
    return_pct, max_drawdown_pct, sharpe, winrate, profit_factor, trades)
    Returns: dict with 'total' score and per-component scores.
    """
    goal = load_goal()
    w = goal.get("score_weights", {})

    # Extract actuals (handle missing with 0)
    actual_return = metrics.get("total_return_pct", metrics.get("return_pct", 0))
    actual_dd = metrics.get("max_drawdown_pct", metrics.get("max_dd_pct", 0))
    actual_sharpe = metrics.get("sharpe", 0)
    actual_wr = metrics.get("winrate", metrics.get("win_rate", metrics.get("winrate_p", 0)))
    if isinstance(actual_wr, float) and actual_wr > 1:
        actual_wr = actual_wr / 100.0  # handle percentage vs decimal
    actual_pf = metrics.get("profit_factor", metrics.get("pf", metrics.get("PF", 0)))

    sub = {
        "return_vs_target": score_return(
            actual_return, goal["target_return_30d_pct"]
        ),
        "drawdown_vs_max": score_drawdown(
            actual_dd, goal["max_drawdown_pct"]
        ),
        "sharpe_vs_min": score_sharpe(
            actual_sharpe, goal["min_sharpe"]
        ),
        "winrate_vs_min": score_winrate(
            actual_wr, goal["min_winrate"]
        ),
        "profit_factor_vs_min": score_pf(
            actual_pf, goal["min_profit_factor"]
        ),
    }

    total = (
        sub["return_vs_target"]   * w.get("return_vs_target", 0.30) +
        sub["drawdown_vs_max"]    * w.get("drawdown_vs_max", 0.25) +
        sub["sharpe_vs_min"]      * w.get("sharpe_vs_min", 0.20) +
        sub["winrate_vs_min"]     * w.get("winrate_vs_min", 0.15) +
        sub["profit_factor_vs_min"] * w.get("profit_factor_vs_min", 0.10)
    )

    # Clamp total to [-1, 1]
    total = clamp(total)

    # Gate: if any hard floor breached, floor the total score
    if actual_return <= goal.get("failure_below", -0.04) * 100:
        total = -1.0

    result = {
        "total": round(total, 4),
        "components": {k: round(v, 4) for k, v in sub.items()},
        "actuals": {
            "return_pct": round(actual_return, 2),
            "drawdown_pct": round(actual_dd, 2),
            "sharpe": round(actual_sharpe, 2),
            "winrate": round(actual_wr, 2),
            "profit_factor": round(actual_pf, 2),
            "trades": metrics.get("trades", 0),
        },
        "passed_gate": actual_pf >= goal["min_profit_factor"] and actual_sharpe >= goal["min_sharpe"] and actual_wr >= goal["min_winrate"],
    }
    return result


def main():
    import json, sys
    """CLI: python score.py '<json_metrics>'"""
    if len(sys.argv) > 1:
        metrics = json.loads(sys.argv[1])
    else:
        # Demo with sample metrics
        metrics = {
            "total_return_pct": 3.5,
            "max_drawdown_pct": 4.2,
            "sharpe": 0.45,
            "winrate": 0.48,
            "profit_factor": 1.35,
            "trades": 23,
        }
    result = score(metrics)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
