"""
Gate Agent: Validates strategies before they can go live
"""
import json
from pathlib import Path
from datetime import datetime

class Gate:
    RULES = {
        'min_trades': 20,
        'min_winrate': 0.42,
        'min_profit_factor': 1.2,
        'min_sharpe': 0.3,
        'max_drawdown_pct': 20.0,
        'data_age_days': 7,
    }
    
    FILE = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/experiments/trading_100e/agent/gate_status.json")
    
    @classmethod
    def check(cls, metrics: dict):
        checks = {}
        checks['trades'] = metrics.get('trades', 0) >= cls.RULES['min_trades']
        checks['winrate'] = metrics.get('winrate', 0) >= cls.RULES['min_winrate']
        checks['pf'] = metrics.get('profit_factor', 0) >= cls.RULES['min_profit_factor']
        checks['sharpe'] = metrics.get('sharpe', 0) >= cls.RULES['min_sharpe']
        checks['dd'] = metrics.get('max_dd_pct', 999) <= cls.RULES['max_drawdown_pct']
        
        passed = all(checks.values())
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'passed': passed,
            'checks': checks,
            'metrics': metrics,
            'rules': cls.RULES,
        }
        
        cls.FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(cls.FILE, 'w') as f:
            json.dump(status, f, indent=2)
        
        return passed, status
    
    @classmethod
    def can_trade(cls):
        if not cls.FILE.exists():
            return False, {"reason": "No strategy has been validated yet"}
        with open(cls.FILE) as f:
            s = json.load(f)
        return s.get('passed', False), s

if __name__ == "__main__":
    # Test with our failed strategy
    metrics = {
        'trades': 50,
        'winrate': 0.50,
        'profit_factor': 1.03,
        'sharpe': 0.05,
        'max_dd_pct': 3.41,
        'return_pct': 0.26,
    }
    
    passed, status = Gate.check(metrics)
    print(f"Gate Result: {'PASS ✅' if passed else 'FAIL ❌'}")
    for check, result in status['checks'].items():
        print(f"  {check:10s}: {result}")
    
    if not passed:
        print("\n⚠️  Trading is LOCKED.")
        print("   Strategy does not meet minimum criteria.")
        print("   Required: WR≥42%, PF≥1.2, Sharpe≥0.3")
        print("   Actual:   WR=50%, PF=1.03, Sharpe=0.05")
        print("\n   Action: Search for NEW strategy.")
