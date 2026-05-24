---
tags: [finance, tech, trading]
---

# Gate 03: Autonomous Trading Agent - 35% in 30 Tagen

**Status:** IN PROGRESS - Regeln müssen stehen bevor Code ausgeführt wird (Gate Agent).
**Scope:** Autonomer Crypto-Trading-Agent mit Paper-Trading-Integration (Hyperliquid Testnet).

---

## 1. Trading Strategy: Momentum-Reversal Scalp

**Asset Class:** Crypto Perpetuals (BTC, ETH auf Hyperliquid).
**Timeframes:** 5m (primary), 1m (entry timing), 15m (trend bias).

### Setup Regeln (Entry Conditions - ALLE müssen erfüllt sein):

1. **Trend-Bias (15m):**
   - Price über/bunter 8-EMA (Long) oder unter (Short).
   - ATR(14) muss > letzte 20 Perioden-Median (volatility expansion).

2. **Momentum-Setup (5m):**
   - Impuls-Candle (>1.5x ATR in eine Richtung).
   - Danach Pullback zu 0.382–0.618 Fibonacci des Impulses.
   - RSI(14) muss zwischen 40–60 sein (keine Overbought/Oversold-Traps).

3. **Entry Trigger (1m):**
   - Engulfing-Candle oder Pinbar in Trendrichtung am Fib-Level.
   - Volume der Entry-Candle > 50-Perioden Volume-SMA.

### Exit Regeln:

- **TP1 (60% Position):** 2R (2x Risk vom Entry).
- **TP2 (40% Position):** 3R oder bei nächstem structure break (Swing High/Low).
- **SL:** Below/Above Entry-Candle Low/High (ca. 0.5–1x ATR).

### Session Rules:

- **Nur traden:** London Open (08:00 UTC), NY Open (13:30 UTC), oder bei News-Events (Fed, CPI).
- **Keine Trades:** Asien-Session allein (22:00–08:00 UTC), Wochenende (Samstag).

---

## 2. Risk Management (Nicht verhandelbar)

| Parameter | Wert | Begründung |
|---|---|---|
| Max Risk pro Trade | 2% des Kontos | Consistent sizing |
| Max Trades pro Session | 2 | Overtrading vermeiden |
| Daily Loss Limit | -4% | Circuit Breaker |
| Max Leverage | x5 | PF-Optimierung bei >x5 sinkt |
| Min RR | 1:2 | Asymmetrie erzwingen |

**Circuit Breaker:**
- Bei -4% Daily Loss → Agent pausiert 24h.
- Nach 3 Verlusttrades in Folge → Agent switcht automatisch auf Paper-Trading.

---

## 3. Data & Execution

**Plattform:** Hyperliquid Testnet (Paper Trading).
**Datenquelle:** Hyperliquid API (1m/5m/15m via `api.hyperliquid-testnet.xyz`).
**Data Cleaning (OBLIGATORISCH vor Backtest):**
- Wick-Spikes >3σ vom lokalen Mean entfernen.
- Out-of-hours Gaps (>5% ohne Volume) interpolieren.
- API-Daten konsistent auf UTC normalisieren.

**Agent Loop:**
1. Daten abrufen → Clean → Pattern erkennen.
2. Wenn Setup → Order auf Testnet senden (Paper).
3. Position tracken → SL/TP überwachen.
4. Trade loggen (Entry, Exit, MFE, MAE, Regime).
5. End-of-Day: Performance report generieren.

---

## 4. Success Criteria (Gate Criteria)

Jede Iteration muss passen bevor Live oder nächste Phase:

| Metric | Mindestwert | Messung |
|---|---|---|
| Profit Factor (PF) | ≥ 1.2 | Gross Wins / Gross Losses |
| Sharpe Ratio | ≥ 0.3 | (Return - Risk Free) / StdDev |
| Win Rate | ≥ 42% | Winning Trades / Total |
| Max Drawdown | ≤ 8% | Peak-to-Trough |
| Expectancy | > 0 | (Win% × Avg Win) - (Loss% × Avg Loss) |

**Phasen:**
- Phase 1: 30-Tage Backtest auf 6 Monate historischer Daten.
- Phase 2: 7 Tage Paper Trading (Testnet).
- Phase 3: 50% Size Live (nur nach 7 Tagen profitabel Paper).
- Phase 4: 100% Size.

**HARD GATE:** Phase 1 & 2 müssen alle 5 Criteria erfüllen. Sonst LOCKED – Strategie anpassen.

---

## 5. Self-Improvement Mechanism

Der Agent muss täglich aus Tradings lernen:

1. **Pattern-Klassifizierung:** Welche Setups heute funktioniert? (Win/Loss pro Setup-Typ).
2. **Regime-Erkennung:** War es Trend oder Range? → Gewichtung anpassen.
3. **Parameter-Drift:** Verändert sich die Volatilität? → ATR-Perioden anpassen.
4. **Auto-Fallback:** Wenn 3 Tage in Folge PF <1.0 → Switch zu Paper + Strategie-Review.

**Logging:** Alle Trades in JSON pro Trade: `{id, timestamp, asset, direction, entry, sl, tp, mfe, mae, pnl, setup_type, regime, market_session, image_b64}`.

---

## 6. Agent Architecture

```
Data Fetcher → Data Cleaner → Strategy Engine → Risk Manager → Execution (Testnet) → Logger → Performance Analyzer
```

**Stack:**
- Python 3.13+, `hyperliquid-python-sdk`, `pandas`, `numpy`.
- Keine externen Paid-APIs. Hyperliquid = kostenlos.
- Kein Machine Learning in Phase 1 (statistische Regeln reichen).

---

## 7. Current State

- Wallet erstellt: `0x5D84363572c4c5dFF361E3855b792380b0c25DCA`
- SDK installiert: `hyperliquid-python-sdk` @ VPS.
- Next: Verbindung testen → Paper Trading loop starten.

**Previous Gates:**
- Gate 01: Initial Setup (Complete)
- Gate 02: Backtest Framework (Complete)
- Gate 03: Autonomous Agent (In Progress)

---

**Entscheidung:** Nach Genehmigung dieser Regilen (Gate-Criteria erfüllt) → Sofortiger Code-Build des autonomen Agenten.

## Siehe auch

- [[40_Areas/finance-index]]
- [[30_Projects/Trading-Agent/00_ROADMAP]]
