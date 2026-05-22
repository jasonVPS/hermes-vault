# Live Trading - Plattform-Vergleich

**Status:** Research abgeschlossen
**Kriterium:** API = 100% kostenlos, keine monatlichen Gebühren

---

## Executive Summary: Krypto Live

| Plattform | API Kosten | Spot Fees | Futures Fees | KYC | SEPA | EUR-Paare | Empfehlung |
|-----------|------------|-----------|--------------|-----|------|-----------|------------|
| **Binance** | **0€** | 0.1% / 0.1% | 0.02% / 0.05% | Ja | Ja* | ✅ 15+ | **#1 KRYPTO** |
| **Bybit** | **0€** | 0.1% / 0.1% | 0.005% / 0.055% | Ja | Ja* | ✅ 10+ | **#1 FUTURES** |
| **Kraken** | **0€** | 0.16% / 0.26% | 0.00% / 0.10%** | Ja | ✅ Fidor Bank | ✅ 30+ | **#1 EUR** |
| **KuCoin** | **0€** | 0.1% / 0.1% | 0.02% / 0.06% | Ja | Nein | ✅ 10+ | ALTCOINS |
| **Coinbase** | **0€** | 0.4% / 0.6% | - | Ja | Ja | ✅ | TEUER |

*Via Third-Party-Provider
** ab $10M Volumen, sonst 0.02% / 0.05%

---

## Executive Summary: Forex Live

| Plattform | API Kosten | Spread EUR/USD | Kommission | KYC | SEPA | Regulierung | Empfehlung |
|-----------|------------|----------------|------------|-----|------|-------------|------------|
| **OANDA** | **0€** | 1.6 pips | $0 (Standard) | Ja | ✅ Ja | FCA, ASIC | **#1 FOREX** |
| **Forex.com** | **0€** | 1.0 pips | $0 | Ja | ✅ Ja | FCA, NFA, CFTC | #2 FOREX |
| **XTB** | **0€** | 0.8 pips* | $0 | Ja | ✅ Ja | FCA, KNF | #3 FOREX (EU) |

*XTB hat variable Spreads ab 0.8 pips, typisch 1.2-1.5 pips

---

## Detaillierte Analyse

### Krypto: Binance (Empfohlener Live-Broker)

**Warum #1:**
- Größte Liquidität weltweit (3562 Spot-Paare)
- Tiefste Fees für Retail (0.1%)
- Beste API-Stabilität
- Spot + Margin + Futures + Earn
- Niedrigste Slippage

**Kosten:**
```
Maker Fee:    0.1% (Spot) / 0.02% (Futures)
Taker Fee:    0.1% (Spot) / 0.05% (Futures)
Mit BNB Rabatt: -25% auf alle Fees
VIP 1 ab 50 BTC 30-Tage-Vol: -20% Maker/Taker
```

**Limits:**
- Withdrawal Limit (Tier 1): 2 BTC / Tag
- Withdrawal Limit (Tier 2): 100 BTC / Tag

**Nachteile:**
- Keine echten EUR-Paare (nur Stablecoins EUR/USDT)
- Regulierungsunsicherheit in EU
- SEPA Überweisung nur via Third-Party (Banxa, Simplex)

---

### Krypto: Bybit (Empfohlener Futures-Broker)

**Warum für Futures:**
- Tiefste Maker-Fee: 0.005% (essentiell für Maker-Strategien)
- Top #2 Liquidität für Perpetuals
- Unified Trading Account (UTA)
- Option Trading

**Kosten:**
```
Spot Maker/Taker: 0.1% / 0.1%
Perp Maker/Taker: 0.005% / 0.055%
Option Fees: 0.03% / 0.03%
```

**Nachteile:**
- Keine SEPA
- KYC verpflichtend seit 2024
- Weniger Spot-Paare als Binance

---

### Krypto: Kraken (Empfohlener EUR-Broker)

**Warum für EUR:**
- Fidor Bank = Direktes EUR Banking in Deutschland
- EUR/USD, EUR/BTC, EUR/ETH etc.
- FCA reguliert, transparent
- Spot + Margin + Futures

**Kosten:**
```
Starter:    0.16% Maker / 0.26% Taker
Intermediate: 0.14% / 0.24%
Pro (ab $10M Vol): 0.00% / 0.10%
Futures: 0.02% / 0.05%
```

**Vorteile:**
- Echte SEPA Ein- und Auszahlung
- Stärkste Regulierung
- EUR-Paare ohne USDT-Conversion

**Nachteile:**
- Höhere Spot-Fees als Binance
- Weniger Perpetuals
- API manchmal langsamer als Binance

---

### Forex: OANDA (Empfohlener Forex-Broker)

**Warum #1:**
- #1 Retail Forex Broker weltweit
- Practice Account = identisch mit Live
- Keine Mindesteinlage (Standard)
- Full REST API identisch für Demo/Live
- 70+ Währungspaare

**Kosten:**
```
Standard Account: Spread only, no commission
EUR/USD: 0.6 - 1.6 pips average
RAW Spread Account: $5 per round turn + 0.1 pips
Swap Rates: Rollover-Interest auf Übernachtpositionen
```

**API:**
- Rest API v3: Identisch für Demo und Live
- Python SDK: v20
- Rate Limit: 100 requests / 2 seconds

**Regulierung:**
- FCA (UK) #186171
- ASIC (Australien)
- CIRO (Kanada)
- MAS (Singapur)

---

## Konsequenzen für unser Setup

### Paper → Live Migration

| Asset | Paper Account | Live Account | Code-Änderung |
|-------|---------------|--------------|---------------|
| Krypto Spot | Binance Testnet | Binance Live | API-URL ändern, KYC abschließen |
| Krypto Futures | Bybit Demo | Bybit Live | API-URL ändern, KYC abschließen |
| Forex | OANDA Practice | OANDA Live | Account ID ändern, Geld einzahlen |

### Empfohlene Live-Strategie

**Für dein Setup (VPS, nicht EU-geprägt):**

**PRIMARY KRYPTO:**
- **Binance** für Spot + Futures
- API Key = kostenlos
- SEPA via Third-Party

**PRIMARY FOREX:**
- **OANDA** für alle Währungspaare
- API Key = kostenlos
- Direkte SEPA Ein-/Auszahlung

**BACKUP:
- Bybit für Perpetuals (falls Binance Probleme)
- Kraken für EUR-Konvertierung

---

## Code-Beispiel: Paper → Live Switch

```python
import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

# --- KRYPTO ---
mode = os.getenv('TRADING_MODE', 'paper')  # 'paper' oder 'live'

if mode == 'paper':
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_TESTNET_API_KEY'),
        'secret': os.getenv('BINANCE_TESTNET_SECRET'),
        'sandbox': True,
    })
else:
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_LIVE_API_KEY'),
        'secret': os.getenv('BINANCE_LIVE_SECRET'),
    })

# --- FOREX ---
if mode == 'paper':
    OANDA_ENV = "practice"
    OANDA_ACCOUNT = os.getenv('OANDA_PRACTICE_ACCOUNT_ID')
else:
    OANDA_ENV = "live"
    OANDA_ACCOUNT = os.getenv('OANDA_LIVE_ACCOUNT_ID')
```

---

## Fazit

| Dein Ziel | Beste Plattform | Warum |
|-----------|-----------------|-------|
| Krypto Spot/Futures Live | **Binance** + **Bybit** | Tiefste Fees, beste API, 0€ API-Kosten |
| Forex Live | **OANDA** | #1 Retail, starke Regulierung, 0€ API |
| EUR-Konvertierung | **Kraken** | SEPA, Fidor Bank, transparent |
| Altcoins | **KuCoin** | Kleine Coins, gute API |

**Unser Setup bleibt identisch:**
- Paper: Binance Testnet + OANDA Practice
- Live: Binance Live + OANDA Live
- Code-Unterschied: nur API-Keys und `sandbox`-Flag

---
*Erstellt: 2026-05-22*
*Autor: Hermes Agent*
