---
tags: [finance]
---

# Experiment: 100€ → 200€ in 30 Tagen

## Status: ❌ LOCKED (Gate Check Failed)

**Datum:** 2026-05-22
**Zeitrahmen:** 15m / 1h
**Ziel:** 100% Return in 30 Tagen

---

## Was wurde getestet

### Strategie: RSI Mean Reversion (15m)
- **Long:** RSI(7) < 30 + Close > Lower BB(20,2)
- **Short:** RSI(7) > 70 + Close < Upper BB(20,2)
- **SL:** 1.0 ATR(14)
- **TP:** 2.0 ATR(14) = 2:1 R:R
- **Risk:** 2% / Trade

### Datengrundlage
- Quelle: Binance Spot (echte historische Daten)
- Periode: 30 Tage (2880 x 15m Bars)
- Assets: BTC/USDT, ETH/USDT, SOL/USDT

---

## Ergebnisse

| Asset | Trades | Winrate | Return | Profit Factor | Max DD |
|-------|--------|---------|--------|---------------|--------|
| BTC   | 50     | 50.0%   | +0.26% | 1.03          | 3.41%  |
| ETH   | 50     | 34.0%   | -5.25% | 0.62          | 6.09%  |
| SOL   | 50     | 38.0%   | -5.83% | 0.54          | 7.45%  |

**Profit Factor BTC: 1.03** → Fast gleich Random Walk
**Profit Factor ETH/SOL: < 0.7** → Klare Verluststrategie

---

## Warum hat es nicht funktioniert?

### 1. Marktregime: Abwärtstrend
BTC fiel in der Testperiode von ~85k auf ~77k. "Oversold" kaufen im Abwärtstrend ist die klassische **Fallenstrategie**. RSI < 30 bedeutet nicht "muss steigen" – es bedeutet "verkauft wird hart".

### 2. Mean Reversion braucht Seitwärtsphase
Mean Reversion funktioniert in **Range-Märkten**, nicht in Trendmärkten. Die letzten 30 Tage waren trend-gesteuert.

### 3. Winrate 50% reicht nicht
Bei 2:1 R:R braucht man nur 33% Winrate. Aber die Stop-Loss-Abstände auf 15m waren oft zu eng bei der realen Volatilität. Die Strategie wurde bei kleinen Gegenbewegungen gestoppt, bevor der TP erreicht wurde.

### 4. Kein Trend-Filter
Keine 200-EMA- oder Marktstruktur-Überprüfung. Long-Trades in einem Abwärtstrend sind statistisch benachteiligt.

---

## Gate-Entscheidung

**Gate Status:** `FAIL ❌`
- ✅ Trades: 50+ (Pass)
- ✅ Winrate: > 42% (Pass)
- ❌ Profit Factor: 1.03 < 1.20 (Fail)
- ❌ Sharpe: ~0.05 < 0.30 (Fail)
- ✅ Drawdown: < 20% (Pass)

**Konsequenz:** Trading ist **gesperrt**. Der Adaptiv-Engine darf keine Live-Trades ausführen, bis eine gültige Strategie mit PF ≥ 1.2 gefunden wurde.

---

## Lernfortschritt des Agenten

Der Learning Engine hat folgende Anpassungen vorgenommen:
- Base Risk nach Loss-Cluster: 1.0% → 0.77% (Reduktion)
- RSI Thresholds nach Wins: Verschärft (35→31 / 65→69) → Aber: Die Anpassung war auf BTC-Daten optimiert und hat ETH/SOL nicht geholfen.

**Meta-Lektion:** Lokales Lernen auf einem Asset (BTC) generalisiert nicht automatisch auf andere Assets.

---

## Nächste Schritte

### Option A: Trendfolge-Strategie statt Mean Reversion
- EMA-Crossover mit MACD-Filter
- Trades NUR in Trendrichtung (Long wenn EMA200 steigt)
- Testen auf trend-perfodischen Märkten

### Option B: Multi-Asset-Portfolio
- Korrelation zwischen BTC/ETH/SOL nutzen
- Hedging-Trades statt Einzelasset
- Risiko-Reduktion durch Diversifikation

### Option C: Session-basiertes Scalping
- Nur zu bestimmten Zeiten traden (9-11 UTC, 13-15 UTC)
- Krypto hat Intraday-Patterns
- Weniger Trades, aber selektiver

### Option D: ML-Feature-Engineering
- Mehr Indikatoren als Features
- Random Forest für Setup-Scoring
- Erfordert längere Datenhistorie (6+ Monate)

---

## Regeln für zukünftige Strategien

1. **Jede Strategie muss Walk-Forward-Backtest bestehen** (mindestens 30 Tage Out-of-Sample)
2. **Mindestens 2 Coins müsten positiv sein** → Kein Single-Asset-Overfitting
3. **Gate entscheidet autonom Go/No-Go** → Keine manuelle Intervention nötig
4. **Max Drawdown 20% ist Hard-Stop** → Keine Martingale-/Recovery-Strategien

---

## Systemzustand

- Data Agent: ✅ Aktiv (15m Daten vorhanden)
- Research Agent: ✅ Aktiv (Backtest-Engine läuft)
- Gate Agent: ✅ Aktiv (sperrt bei PF < 1.2)
- Execution Agent: ❌ Gesperrt (warte auf Gate-Freigabe)
- Vault Agent: ✅ Aktiv (dokumentiert automatisch)

**Experiment läuft weiter** – aber mit rigoroser Disziplin.

## Siehe auch
- [[40_Areas/finance-index|Finance Index]]
