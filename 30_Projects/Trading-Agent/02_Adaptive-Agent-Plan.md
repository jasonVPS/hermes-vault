---
tags: [finance]
---

# Adaptive Trading Agent - Lernziel

Wir bauen keinen statischen Bot. Wir bauen einen Agenten, der:

1. **Paper Trading** auf Bybit Demo durchführt (Echte Marktdaten, kein echtes Geld)
2. **Jeden Trade tracked** mit Marktkontext (Lage der Indikatoren, Zeit der Entry)
3. **Aus Ergebnis lernt** (Gewinn = Parameter beibehalten/verstärken, Verlust = Parameter anpassen)
4. **Strategie-Population** unterhält (mehrere Strategie-Varianten, Darwinsche Auslese)

## Architektur

```
AdaptiveTradingAgent/
├── journals/           # Trade-Journals pro Strategie
├── population/         # Aktive Strategie-Varianten (JSON)
├── evolution.py        # Lernt aus Trade-Ergebnissen, mutiert Parameter
├── bybit_paper.py     # Bybit Demo-Verbindung, Order-Execution
├── strategies/        # Basis-Strategien (bereits vorhanden)
└── journal.py         # Trade-Tracking + Marktkontext-Speicher

Adaptiver Kreislauf:
  1. Trade ausführen
  2. Ergebnis aufzeichnen (Journal)
  3. Nach N Trades: Analyse
  4. Belohnung = Strategie beibehalten + Mutation
  5. Strafe = Ersetzen durch besser performende Variante
```

## Nächster Schritt: Bybit Demo verbinden

## Siehe auch
- [[40_Areas/finance-index|Finance Index]]
