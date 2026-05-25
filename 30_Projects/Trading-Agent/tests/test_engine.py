"""
Unit tests for the backtest engine.
Phase 0 exit test: one green test.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from engine.backtest import BacktestEngine, Trade
from strategies.regime_aware import RegimeAwareStrategy

class DummyStrategy:
    """Always-go-LONG strategy for testing."""
    def generate_signals(self, df):
        return pd.Series("LONG", index=df.index)

def make_dummy_df(n=100, trend="up"):
    """Create deterministic OHLCV data."""
    np.random.seed(42)
    base = 100.0 if trend == "up" else 100.0
    dates = pd.date_range("2026-01-01", periods=n, freq="1h", tz="UTC")
    
    if trend == "up":
        close = np.linspace(100, 150, n) + np.random.randn(n) * 0.5
    else:
        close = np.linspace(100, 80, n) + np.random.randn(n) * 0.5
    
    high = close + np.abs(np.random.randn(n)) * 1.5
    low = close - np.abs(np.random.randn(n)) * 1.5
    open_p = close + np.random.randn(n) * 0.3
    volume = np.abs(np.random.randn(n)) * 1000 + 500

    df = pd.DataFrame({
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }, index=dates)
    return df

def test_engine_run_produces_result():
    df = make_dummy_df(n=50, trend="up")
    engine = BacktestEngine(df, DummyStrategy(), initial_capital=10000.0)
    result = engine.run()
    
    assert result is not None
    assert "pf" in result.metrics
    assert "sharpe" in result.metrics
    assert isinstance(result.trades, list)
    print("✅ test_engine_run_produces_result PASSED")

def test_trade_open_and_close():
    df = make_dummy_df(n=50, trend="up")
    engine = BacktestEngine(df, DummyStrategy(), initial_capital=10000.0)
    result = engine.run()
    
    closed = [t for t in result.trades if t.status != "OPEN"]
    assert len(closed) >= 1, "Expected at least one closed trade"
    assert all(t.exit_price is not None for t in closed)
    print("✅ test_trade_open_and_close PASSED")

def test_metrics_in_range():
    df = make_dummy_df(n=50, trend="up")
    engine = BacktestEngine(df, DummyStrategy(), initial_capital=10000.0)
    result = engine.run()
    
    m = result.metrics
    assert -100 < m["total_return_pct"] < 1000, f"Return out of range: {m['total_return_pct']}"
    assert m["max_dd_pct"] >= 0, f"Drawdown negative: {m['max_dd_pct']}"
    print("✅ test_metrics_in_range PASSED")

def test_regime_strategy_generates_signals():
    df = make_dummy_df(n=50, trend="up")
    strat = RegimeAwareStrategy()
    signals = strat.generate_signals(df)
    
    assert len(signals) == len(df)
    assert set(signals.unique()).issubset({"HOLD", "LONG", "SHORT"})
    print("✅ test_regime_strategy_generates_signals PASSED")

if __name__ == "__main__":
    print("Running tests...")
    test_engine_run_produces_result()
    test_trade_open_and_close()
    test_metrics_in_range()
    test_regime_strategy_generates_signals()
    print("\nAll tests PASSED. Phase 0 exit criteria met.")
