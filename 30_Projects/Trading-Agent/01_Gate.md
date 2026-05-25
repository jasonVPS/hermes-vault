---
tags: [finance, tech, trading]
Gate-Version: 1.0
---

# Gate Definition — Unverhandelbare Rules

**Erklärung:** Dieses Gate ist ein **Hard Filter**. Keine Strategie, kein Backtest, kein Paper-Trade darf ohne PASS hierdurch. Keine Ausnahmen, keine "fast genug", keine "aber bei ETH hat es funktioniert".

---

## Gate Criteria (pro Asset)

```
Profit Factor (PF)      ≥ 1.50     (Gross Profit / |Gross Loss|)
Sharpe Ratio             ≥ 1.00     (Daily returns, risk-free = 0)
Win Rate                 ≥ 50.0%    (Nicht nur statistischer Rausch-Trade)
Max Drawdown             ≤ 15.0%    (Peak-to-Trough auf Equity Curve)
Trades                   ≥ 30       (Statistisch bedeutsames Sample)
```

## Multi-Asset Rule

Strategie muss auf **BTC UND ETH UND SOL** gleichzeitig die oberen Criteria erfüllen.

- Ein Asset FAIL = Gesamt FAIL
- Kein Paper Trading bei FAIL
- Keine Parameter-Optimierung bei FAIL (zurück zu Phase 3: Regime-Strategie)

## Walk-Forward Rule

Out-of-Sample Test **letzte 30 Tage** (nicht Teil des Trainings) muss ebenfalls PASS.

- OOS-PF ≥ 1.50
- OOS-Sharpe ≥ 0.50
- OOS-WR ≥ 45%
- OOS-MaxDD ≤ 15%

## Failure Protocol

1. Gate FAIL → Schreibe Report: Welches Asset, welche Metrik, um wieviel verfehlt
2. Kein weiterer Schritt (kein Paper, kein Evolve)
3. Rückkehr zu Phase 3: Regime-Strategie
4. Ändere **maximal eine Variable** pro Zyklus
5. Re-run Gate nach jeder Änderung

## Success Protocol

1. Gate PASS (alle 3 Assets, In-Sample + OOS)
2. Speichere Strategie-State als `state/versioned/vXXXX.yaml`
3. Erlaube Phase 8: Paper Bridge (Bybit Demo)
4. Nach 5+ Gate-Pass-Versionen + 30 Tage Paper kontinuierlich → Phase 9: Live-Prep freischalten

---

**Hinweis:** Gate wird von `gate/gate.py` automatisch evaluiert. Kein menschliches Review ersetzt die Zahlen.
