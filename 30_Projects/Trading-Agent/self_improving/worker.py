"""
worker.py — Self-Improving Trading Worker
Run: python3 worker.py --symbol BTC/USDT --timeframe 1h

Steps:
1. Load strategy.yaml + goal.yaml
2. Fetch clean data (via data_cleaner)
3. Run backtest with current params
4. Score results vs goal
5. Log trades to trades.jsonl
6. Append score to scores.jsonl
7. If trades_since_last_reflect >= reflection_every: trigger reflect
"""
import sys, os
sys.path.insert(0, "/opt/data/home/hermes-vault/30_Projects/Trading-Agent")

import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime

from core.data_cleaner import load_raw, clean_wicks
from self_improving.score import score

ROOT = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/self_improving")
STATE_DIR = ROOT / "state"
STRATEGY_PATH = STATE_DIR / "strategy.yaml"
GOAL_PATH = STATE_DIR / "goal.yaml"
TRADES_PATH = STATE_DIR / "trades.jsonl"
SCORES_PATH = STATE_DIR / "scores.jsonl"
HYPOTHESES_PATH = STATE_DIR / "hypotheses.jsonl"

# ── Strategy runner (adapted from backtest_compare.py) ─────────

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Trade:
    entry_time: pd.Timestamp
    dir: str
    entry_price: float
    sl: float
    tp: float
    size: float
    risk_usd: float
    exit_time: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    pnl_pct: float = 0.0
    pnl_abs: float = 0.0
    exit_reason: str = ""
    bars_held: int = 0


def calc_atr(df, length=14):
    prev_close = df['close'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - prev_close).abs()
    tr3 = (df['low'] - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(span=length, adjust=False).mean()


def build_strategy(strategy_config: dict):
    """Build a closure-based strategy from config."""
    p = strategy_config["params"]
    fee = strategy_config.get("backtest", {}).get("fee_rate", 0.0006)
    slip = strategy_config.get("backtest", {}).get("slippage", 0.0002)
    risk = p["risk_per_trade"]
    sl_mult = p["atr_sl_mult"]
    tp_mult = p["atr_tp_mult"]

    def indicators(df):
        df = df.copy()
        df['ema_f'] = df['close'].ewm(span=p["ema_fast"], adjust=False).mean()
        df['ema_s'] = df['close'].ewm(span=p["ema_slow"], adjust=False).mean()
        df['ema_trend'] = df['close'].ewm(span=p["ema_trend"], adjust=False).mean()
        df['atr'] = calc_atr(df, length=p["atr_period"])
        # RSI
        d = df['close'].diff()
        gain = d.where(d > 0, 0.0)
        loss = (-d).where(d < 0, 0.0)
        avg_g = gain.ewm(alpha=1/p["rsi_period"], adjust=False).mean()
        avg_l = loss.ewm(alpha=1/p["rsi_period"], adjust=False).mean()
        rs = avg_g / avg_l
        df['rsi'] = 100 - (100 / (1 + rs))
        df['vol_sma'] = df['volume'].rolling(window=20).mean()
        prev_f = df['ema_f'].shift(1)
        prev_s = df['ema_s'].shift(1)
        df['cross'] = np.where(
            (df['ema_f'] > df['ema_s']) & (prev_f <= prev_s), 1,
            np.where((df['ema_f'] < df['ema_s']) & (prev_f >= prev_s), -1, 0)
        )
        return df

    def signal(df, i, equity):
        row = df.iloc[i]
        if row['cross'] == 0 or pd.isna(row['atr']) or row['atr'] == 0:
            return None
        price = row['close']
        atr = row['atr']
        rsi = row['rsi']
        # Macro trend filter
        if p["ema_trend"] > 0:
            if row['cross'] == 1 and price <= row['ema_trend']:
                return None
            if row['cross'] == -1 and price >= row['ema_trend']:
                return None
        # Volume filter
        if p.get("volume_confirm", True):
            if pd.isna(row['vol_sma']) or row['volume'] <= row['vol_sma']:
                return None
        # Max ATR% filter
        if (atr / price) > p.get("max_atr_pct", 0.03):
            return None
        # RSI confirmation
        if row['cross'] == 1 and rsi > p["rsi_long_min"]:
            sl = price - atr * sl_mult
            tp = price + atr * tp_mult
            risk_amt = equity * risk
            size = risk_amt / (price - sl)
            return {'dir':'long','entry':price,'sl':sl,'tp':tp,'size':size,'risk':risk_amt,'reason':'EMA_CROSS_BULL'}
        if row['cross'] == -1 and rsi < p["rsi_short_max"]:
            sl = price + atr * sl_mult
            tp = price - atr * tp_mult
            risk_amt = equity * risk
            size = risk_amt / (sl - price)
            return {'dir':'short','entry':price,'sl':sl,'tp':tp,'size':size,'risk':risk_amt,'reason':'EMA_CROSS_BEAR'}
        return None

    return indicators, signal, fee, slip


class Engine:
    def __init__(self, indicators_fn, signal_fn, fee, slip, equity=10000):
        self.indicators_fn = indicators_fn
        self.signal_fn = signal_fn
        self.fee = fee
        self.slip = slip
        self.initial = equity
        self.trades: List[Trade] = []

    def run(self, df_raw, strategy_config):
        df = self.indicators_fn(df_raw)
        equity = self.initial
        active = None
        lookback = strategy_config["params"]["ema_trend"] + 10

        for i in range(lookback, len(df)):
            row = df.iloc[i]
            # Check exits
            if active:
                exit_px = None
                reason = ""
                if active.dir == 'long':
                    if row['low'] <= active.sl:
                        exit_px = active.sl
                        reason = "SL"
                    elif row['high'] >= active.tp:
                        exit_px = active.tp
                        reason = "TP"
                    elif row['cross'] == -1:
                        exit_px = row['close']
                        reason = "EMA_REVERSAL"
                else:
                    if row['high'] >= active.sl:
                        exit_px = active.sl
                        reason = "SL"
                    elif row['low'] <= active.tp:
                        exit_px = active.tp
                        reason = "TP"
                    elif row['cross'] == 1:
                        exit_px = row['close']
                        reason = "EMA_REVERSAL"

                if exit_px:
                    active.exit_time = row['timestamp']
                    active.exit_price = exit_px
                    active.exit_reason = reason
                    if active.dir == 'long':
                        raw = (exit_px - active.entry_price) / active.entry_price
                    else:
                        raw = (active.entry_price - exit_px) / active.entry_price
                    costs = self.fee * 2 + self.slip * 2
                    active.pnl_pct = raw - costs
                    active.pnl_abs = active.pnl_pct * active.entry_price * active.size
                    equity += active.pnl_abs
                    self.trades.append(active)
                    active = None

            # Check entries
            if not active and i < len(df) - 1:
                sig = self.signal_fn(df, i, equity)
                if sig:
                    active = Trade(
                        entry_time=row['timestamp'],
                        dir=sig['dir'],
                        entry_price=sig['entry'],
                        sl=sig['sl'],
                        tp=sig['tp'],
                        size=sig['size'],
                        risk_usd=sig['risk']
                    )

        return self.metrics(equity)

    def metrics(self, final):
        if not self.trades:
            return {'trades':0, 'final_equity':final, 'return_pct':0,
                    'winrate':0, 'profit_factor':0, 'sharpe':0, 'max_dd_pct':0}
        wins = [t for t in self.trades if t.pnl_pct > 0]
        losses = [t for t in self.trades if t.pnl_pct <= 0]
        win_p = len(wins)/len(self.trades)
        gross_profit = sum(t.pnl_pct for t in wins)
        gross_loss = abs(sum(t.pnl_pct for t in losses))
        pf = gross_profit / gross_loss if gross_loss > 0 else float('inf')

        eq = [self.initial]
        for t in self.trades:
            eq.append(eq[-1] + t.pnl_abs)
        peak = eq[0]
        mdd = 0
        for e in eq:
            if e > peak: peak = e
            dd = (peak - e)/peak
            if dd > mdd: mdd = dd

        rets = [t.pnl_pct for t in self.trades]
        sharpe = np.mean(rets)/np.std(rets) * np.sqrt(len(rets)) if np.std(rets) > 0 else 0
        avg_w = np.mean([t.pnl_pct for t in wins]) if wins else 0
        avg_l = np.mean([t.pnl_pct for t in losses]) if losses else 0

        return {
            'trades': len(self.trades),
            'wins': len(wins), 'losses': len(losses),
            'winrate': win_p,
            'profit_factor': pf,
            'avg_win': avg_w, 'avg_loss': avg_l,
            'final_equity': final,
            'total_return_pct': (final - self.initial) / self.initial * 100,
            'max_dd_pct': mdd * 100,
            'sharpe': sharpe,
            'avg_bars': np.mean([t.bars_held for t in self.trades]),
        }


# ── Main ─────────────────────────────────────────────────────

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def count_trades_since_reflect() -> int:
    """Count trades in trades.jsonl that happened after last hypothesis."""
    if not HYPOTHESES_PATH.exists():
        return TRADES_PATH.stat().st_size if TRADES_PATH.exists() else 0
    # Simple heuristic: all trades in current file are "since last reflect"
    # (In production: compare timestamps.)
    return sum(1 for _ in open(TRADES_PATH)) if TRADES_PATH.exists() else 0


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
    with open(SCORES_PATH, 'a') as f:
        # Convert numpy booleans & floats to native Python types
        rec = {
            "timestamp": datetime.now(datetime.now().astimezone().tzinfo).isoformat(),
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
    engine = Engine(ind_fn, sig_fn, fee, slip,
                    equity=strategy.get("backtest", {}).get("initial_equity", 10000))
    metrics = engine.run(df_clean, strategy)

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
    trades_count = len(engine.trades)
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
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1h")
    args = parser.parse_args()
    run_once(args.symbol, args.timeframe)


if __name__ == "__main__":
    main()
