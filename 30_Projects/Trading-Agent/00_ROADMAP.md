---
tags: [finance, tech, trading]
---

# Trading Agent — Neustart ROADMAP

**Status:** Phase 0 — Planung
**Erstellt:** 2026-05-23

---
## Zentrale Dokumente

- [[01_Gate]] — Gate-Definition (Hard Rules)
- [[02_Backtest-Engine]] — Single Source of Truth Engine Spec
- [[04_Reflection]] — Reflection-Protokoll

## Lektionen aus dem alten Projekt (100€→200€ Experiment)

| # | Lektion | Konsequenz im neuen Projekt |
|---|---------|---------------------------|
| 1 | Mean Reversion in Abwärtstrend = Fallenstrategie | **Regime-Filter zwingend** — bull/bear/sideways Erkennung |
| 2 | Lokales Lernen auf BTC generalisierte nicht auf ETH/SOL | **Multi-Asset Gate** — alle 3 Coins müssen PASS |
| 3 | 15m zu verrauscht, SL zu oft getriggert | **Timeframe: 1h oder 4h** (1h primär, 4h für Regime) |
| 4 | 50% Return/Monat war unrealistisch aggressiv | **Gate: PF≥1.5, Sharpe≥0.5, WR≥45%** — höherer Standard |
| 5 | 5000-Kombinationen Grid-Sweep → Timeout | **Bayesian Optimization oder Hill-Climbing**, kein Brute-Force |
| 6 | Divergierende Backtest-Engines → falsche Results | **Eine Engine, benutzt von ALLEM** (Gate, Evolve, Worker) |
| 7 | Cronjob lief blind, User sah keine Progression | **Journal + täglicher Status-Report** ins Chat |
| 8 | Kein Regime-Unterschied bei Reflection | **Reflection ist regime-aware** (trendfolgende vs. range-Parameter) |

---

## Neue Architektur

```
Trading-Agent/
├── 00_ROADMAP.md              # Diese Datei
├── 01_Gate.md                 # Gate-Definition (Hard Rules, nicht verhandelbar)
├── 02_Backtest-Engine.md      # Spec für die einzige Engine
├── 03_Strategien.md           # Regime-basierte Strategie-Spezifikationen
├── 04_Reflection.md           # Regime-aware Reflection-Protokoll
├── 05_Paper-Bridge.md         # Bybit Demo-Verbindung
├── 06_Live-Prep.md            # Checkliste für Live-Go (gesperrt)
├── engine/                    # EINE Backtest-Engine
│   ├── __init__.py
│   └── backtest.py
├── strategies/                # Strategie-Implementierungen
│   ├── __init__.py
│   └── regime_aware.py        # EMA-Trend + RSI MeanReversion Hybrid
├── data/                      # OHLCV + Features
│   ├── fetcher.py             # Binance Spot OHLCV (free API)
│   └── features.py            # Regime-Features (ADX, EMA200, 20d ROC)
├── gate/                      # Gate Agent
│   ├── __init__.py
│   └── gate.py                # Evaluiert Strategie auf Multi-Asset
├── evolve/                    # Strategie-Discovery
│   ├── __init__.py
│   └── discover.py            # Bayesian Opt oder Hill-Climbing
├── worker/                    # Täglicher Betrieb
│   ├── __init__.py
│   └── daily.py               # Cron-tauglich: Data→Backtest→Score→Reflect
├── journal/                   # Logging + Reporting
│   └── journal.py             # trades.jsonl + daily_summary()
├── state/                     # Versionierte Strategie-State
│   ├── current.yaml           # Aktive Strategie + Regime-Mapping
│   ├── versioned/             # v0001.yaml, v0002.yaml, ...
│   └── logs/                  # trades.jsonl, scores.jsonl
└── tests/                     # Unit + Integration Tests
    ├── test_engine.py
    ├── test_gate.py
    └── test_strategies.py
```

---

## Phase-Plan (9 Phasen)

### Phase 0: Foundation ← WIR SIND HIER
- [x] ROADMAP.md schreiben
- [x] Ordnerstruktur anlegen
- [x] 01_Gate.md definieren (Gate unverhandelbar)
- [x] 02_Backtest-Engine.md definieren (Single Source of Truth)
- [ ] **01_Gate.md und 02_Backtest-Engine.md im Vault reviewen**
- [ ] Phase 0 Exit-Test: `test_engine.py` Skeleton

### Phase 1: Data Layer
- [ ] `data/fetcher.py` — Binance Spot OHLCV, 6M Lookback, 1h + 4h
- [ ] `data/features.py` — Regime-Features: ADX, EMA200-Slope, 20-day ROC
- [ ] SQLite DB mit einheitlichem Schema (keine Daten-Silos)

### Phase 2: Engine v2 (Single Source of Truth)
- [ ] `engine/backtest.py` — Rein SL/TP-Exit, keine Reversal-Exits
- [ ] 100% deterministisch (Seed, keine Zufälligkeit)
- [ ] Instrumentiert: jeder Trade mit Entry-Context (RSI, EMA-Spread, Regime)

### Phase 3: Regime-Aware Strategie
- [ ] **Trend-Regime → Trendfolge**: Long wenn EMA(9) > EMA(21) > EMA(100) + RSI(14) 50-65
- [ ] **Range-Regime → Mean Reversion**: Long wenn RSI < 30 + Preis nahe Lower BB
- [ ] **Regime-Erkennung**: ADX > 25 = Trend, ADX < 20 = Range
- [ ] Strategie-Kontext wird an Engine übergeben ("In welchem Regime war dieser Trade?")

### Phase 4: Multi-Asset Gate v2
- [ ] Gate: **ALLE** von BTC, ETH, SOL müssen PASS
- Gate-Criteria: PF ≥ 1.50 | Sharpe ≥ 1.00 | WR ≥ 50% | Max DD ≤ 15%
- [ ] Walk-Forward: Out-of-Sample letzte 30 Tage müssen PASS
- [ ] Bei FAIL: Kein Paper, keine Evolve. Rückkehr zu Phase 3.

### Phase 5: Evolve v2 (Regime-Aware Discovery)
- [ ] `evolve/discover.py` — Optimisiert Parameter pro Regime
- [ ] Ziel: Finde eine Strategie, die in **beiden** Regimen besteht
- [ ] Method: Bayesian Optimization (effizienter als Grid-Sweep)

### Phase 6: Worker + Reflect
- [ ] `worker/daily.py` — 1x/Tag: Lädt Daten, fährt Backtest, scored
- [ ] `worker/reflect.py` — Regime-aware Reflection:
  - Wenn Trend-Regime schlecht: Trend-Parameter ändern
  - Wenn Range-Regime schlecht: MeanReversion-Parameter ändern
  - Max 1 Variable pro Zyklus

### Phase 7: Journal + Reporting
- [ ] Täglicher Summary-Report (nach Cron-Lauf)
  - Asset, Trades, Winrate, PF, Sharpe, Drawdown
  - Aktives Regime (Trend/Range/Transition)
  - Strategie-Version
- [ ] `journal/journal.py` — Kompakte JSONL-Logs

### Phase 8: Paper Bridge (Bybit Demo)
- [ ] `05_Paper-Bridge.md` spezifizieren
- [ ] CCXT-Verbindung zu Bybit Demo
- [ ] Order-Execution: Market Entry, Limit SL/TP
- [ ] Paper-Modus: Kein echtes Geld, aber echte Marktdaten + Latenz

### Phase 9: Live-Prep (LOCKED)
- [ ] `06_Live-Prep.md` als Checkliste
- [ ] 5+ Gate-Pass-Versionen in `state/versioned/`
- [ ] 30 Tage Paper mit PF ≥ 1.5 kontinuierlich
- [ ] Manuelle Freigabe durch User erforderlich (Breaking the Lock)

---

## Technische Entscheidungen

| Entscheidung | Wert | Warum |
|-------------|------|-------|
| **Language** | Python 3.11 | Einheitlich, kein Mix |
| **Engine** | Eine Datei, alle nutzen sie | Parität Gate/Evolve/Worker |
| **Daten** | Binance Spot OHLCV (kostenlos) | Keine API-Key-Abhängigkeit |
| **Timeframe** | 1h primär, 4h für Regime | Weniger Noise als 15m |
| **Assets** | BTC, ETH, SOL | Multi-Asset Gate |
| **Lookback** | 6 Monate | Genug für Regime-Erkennung |
| **Reflection** | Regime-aware, deterministisch | Kein LLM-Call, kostenlos |
| **Cron** | 1x/Tag 06:00 UTC | Genug Aktion auf 1h, nicht stündlich |

---

## Exit-Kriterien pro Phase

- **Phase darf erst abgeschlossen werden, wenn:**
  - Alle Checkboxes der Phase ✅
  - Ein `test_*.py` läuft grün für diese Phase
  - Ein kurzer Report ins Chat bestätigt, dass alles funktioniert

- **Keine Parallelisierung von Phasen.** Phase N darf erst beginnen, wenn Phase N-1 exit-kritisch abgeschlossen ist.

---

## Neue Gate-Definition (Phasen-unabhängig)

```
PF (Profit Factor)     ≥ 1.50      (Gross Profit / Gross Loss)
Sharpe Ratio           ≥ 0.50      (Risk-adjusted return)
Win Rate              ≥ 45.0%     (Nicht nur Glück)
Max Drawdown          ≤ 15.0%     (Kapitalerhaltung)
Trades                 ≥ 30        (Statistisch bedeutsam)
```

**Multi-Asset Rule:** Strategie muss auf BTC UND ETH UND SOL die Gate-Criteria erfüllen.

---

*Phase 0 bereit für Review. Keine Code-Zeile ohne vorherigen Plan.*

## Siehe auch

- [[40_Areas/finance-index]]
- [[30_Projects/TradingAgent/Gate_03_AutonomousAgent_35pct30days]]
