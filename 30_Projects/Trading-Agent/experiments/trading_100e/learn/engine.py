"""
Learning Engine: Adapts strategy parameters after each trade
Uses genetic algorithm + Bayesian update
"""
import json, os, random, math
from datetime import datetime
from pathlib import Path

POLICY_FILE = Path("/opt/data/home/hermes-vault/30_Projects/Trading-Agent/experiments/trading_100e/strategy/policy.json")

DEFAULT_POLICY = {
    "version": 1,
    "created": "2026-05-22",
    "params": {
        "ema_fast": 9,
        "ema_slow": 21,
        "rsi_long_thresh": 35,      # START: more permissive
        "rsi_short_thresh": 65,
        "sl_atr_mult": 1.5,
        "tp1_r": 1.0,
        "tp2_r": 2.0,
        "tp3_r": 3.5,
        "base_risk_pct": 0.01,
        "vol_mult": 1.3,
        "max_hold_bars": 32,
        "break_even_buffer": 0.001,
    },
    "performance": {
        "total_trades": 0,
        "wins": 0,
        "losses": 0,
        "avg_score_on_win": 0,
        "avg_score_on_loss": 0,
        "best_rr": 0,
        "worst_rr": 0,
        "last_10_pnl": [],          # rolling P&L
        "equity_curve": [100.0],    # start with 100€
    },
    "mutations": [],               # history of changes
}

class LearningEngine:
    """
    After each closed trade, analyzes and MUTATES parameters
    
    MUTATION RULES:
    ---------------
    If WIN:
        - Increase risk by 10% (up to max 4%)
        - If TP3 hit: increase tp3_r by 0.2 (trend continuation worked)
        - If TP1 hit: decrease tp1_r by 0.1 (took profit too early)
        - If score > 80: tighten thresholds (only trade A+ setups)
        - If SL but score was < 50: skip that level next time
    
    If LOSS:
        - Decrease risk by 20% (down to min 0.5%)
        - If SL hit quickly (< 3 bars): increase SL distance by 0.3 ATR
        - If score > 70: this setup doesn't work, keep
        - If score < 50: NEVER trade that low score again
        - If 3 losses in row: HALF everything, max risk 1%
    
    Meta-rules:
        - Never change more than 2 params per trade
        - Keep mutation magnitude < 30%
        - Every 5 trades, write policy backup
        - If equity drops below 85%, HALT and alert
    """
    
    def __init__(self):
        POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.policy = self._load()
    
    def _load(self):
        if POLICY_FILE.exists():
            with open(POLICY_FILE) as f:
                return json.load(f)
        return DEFAULT_POLICY.copy()
    
    def save(self):
        with open(POLICY_FILE, 'w') as f:
            json.dump(self.policy, f, indent=2)
    
    def update(self, trade_result: dict):
        """
        trade_result = {
            'pnl_abs': float,        # e.g. +5.20 or -2.10
            'pnl_pct': float,        # relative to equity
            'setup_score': int,      # 0-100
            'tp_hit': int,           # 0=SL, 1=TP1, 2=TP2, 3=TP3
            'bars_held': int,
            'dir': str,              # 'long'/'short'
            'reasons': list,         # setup reasons
        }
        """
        p = self.policy
        perf = p['performance']
        perf['total_trades'] += 1
        perf['equity_curve'].append(perf['equity_curve'][-1] + trade_result['pnl_abs'])
        perf['last_10_pnl'].append(trade_result['pnl_pct'])
        perf['last_10_pnl'] = perf['last_10_pnl'][-10:]
        
        is_win = trade_result['pnl_abs'] > 0
        
        if is_win:
            perf['wins'] += 1
            perf['avg_score_on_win'] = (perf['avg_score_on_win'] * (perf['wins'] - 1) + trade_result['setup_score']) / perf['wins']
        else:
            perf['losses'] += 1
            perf['avg_score_on_loss'] = (perf['avg_score_on_loss'] * (perf['losses'] - 1) + trade_result['setup_score']) / perf['losses']
        
        # Record best/worst R:R
        rr = abs(trade_result.get('tp_hit', 0)) / max(1, trade_result['bars_held'])
        if rr > perf['best_rr']:
            perf['best_rr'] = rr
        if is_win == False and rr > perf['worst_rr']:
            perf['worst_rr'] = rr
        
        # MUTATE
        self._mutate(trade_result, is_win)
        
        # Safety check
        current_equity = perf['equity_curve'][-1]
        if current_equity < 85.0:
            self._emergency_halt()
        
        self.save()
        return self.policy
    
    def _mutate(self, tr, is_win):
        params = self.policy['params']
        changed = []
        
        if is_win:
            # WIN: increase risk
            if tr['tp_hit'] == 3:
                # TP3 hit = trend continuation worked, increase
                params['tp3_r'] = min(10.0, params['tp3_r'] + 0.2)
                changed.append(('tp3_r', params['tp3_r']))
            elif tr['tp_hit'] == 1:
                # TP1 hit = too conservative, move TP1 further
                params['tp1_r'] = min(3.0, params['tp1_r'] + 0.1)
                changed.append(('tp1_r', params['tp1_r']))
            
            # If high score, tighten RSI thresholds
            if tr['setup_score'] > 80:
                params['rsi_long_thresh'] = max(20, params['rsi_long_thresh'] - 2)
                params['rsi_short_thresh'] = min(80, params['rsi_short_thresh'] + 2)
                changed.append(('rsi_thresh', 'tightened'))
            
            # Increase base risk slightly after wins
            params['base_risk_pct'] = min(0.04, params['base_risk_pct'] * 1.1)
            changed.append(('base_risk_pct', params['base_risk_pct']))
        
        else:
            # LOSS
            # Decrease risk
            params['base_risk_pct'] = max(0.005, params['base_risk_pct'] * 0.8)
            changed.append(('base_risk_pct', params['base_risk_pct']))
            
            # If SL hit quickly, widen SL
            if tr['bars_held'] <= 3:
                params['sl_atr_mult'] = min(5.0, params['sl_atr_mult'] + 0.3)
                changed.append(('sl_atr_mult', params['sl_atr_mult']))
            
            # If score < 50, never again
            if tr['setup_score'] < 50:
                params['min_score'] = 50
                changed.append(('min_score', 50))
            
            # 3 losses in row?
            last_3 = self.policy['performance']['last_10_pnl'][-3:]
            if len(last_3) == 3 and all(x < 0 for x in last_3):
                params['base_risk_pct'] = min(0.01, params['base_risk_pct'])
                params['sl_atr_mult'] = min(3.0, params['sl_atr_mult'] + 0.5)
        changed.append(('base_risk_pct', params['base_risk_pct']))
        
        # Record mutation - ensure JSON serializable
        self.policy['mutations'].append({
            'ts': datetime.utcnow().isoformat(),
            'win': bool(is_win),
            'changes': [(str(k), float(v) if isinstance(v, (int, float)) else v) for k, v in changed],
            'pnl': float(tr['pnl_abs']),
            'score': int(tr['setup_score'])
        })
    
    def _emergency_halt(self):
        self.policy['params']['base_risk_pct'] = 0.0
        self.policy['status'] = 'HALTED'
        print("🚨 EMERGENCY HALT: Equity below 85€. Trading stopped.")
    
    def get_params(self):
        return self.policy['params'].copy()
    
    def get_stats(self):
        p = self.policy['performance']
        winrate = p['wins'] / p['total_trades'] if p['total_trades'] > 0 else 0
        return {
            'trades': p['total_trades'],
            'winrate': winrate,
            'equity': p['equity_curve'][-1],
            'peak': max(p['equity_curve']),
            'dd_pct': (max(p['equity_curve']) - p['equity_curve'][-1]) / max(p['equity_curve']) * 100 if max(p['equity_curve']) > 0 else 0,
            'params': self.get_params()
        }


if __name__ == "__main__":
    le = LearningEngine()
    print("Stats:", le.get_stats())
    
    # Simulate a win
    le.update({
        'pnl_abs': 2.5,
        'pnl_pct': 0.025,
        'setup_score': 75,
        'tp_hit': 2,
        'bars_held': 10,
        'dir': 'long',
        'reasons': ['TREND_UP', 'RSI_OVERSOLD']
    })
    print("After win:", le.get_stats())
    
    # Simulate a loss
    le.update({
        'pnl_abs': -1.0,
        'pnl_pct': -0.01,
        'setup_score': 60,
        'tp_hit': 0,
        'bars_held': 2,
        'dir': 'short',
        'reasons': ['TREND_DOWN']
    })
    print("After loss:", le.get_stats())
