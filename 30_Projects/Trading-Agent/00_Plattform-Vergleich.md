# Trading Agent - Plattform-Vergleich

**Status:** Research abgeschlossen, Implementierung steht an
**Ziel:** 100% kostenlose APIs mit Paper Trading für Krypto + Forex

---

## Executive Summary

| Plattform | Kosten | Paper/Demo | Forex | Krypto | Marktanteil | Empfehlung |
|-----------|--------|------------|-------|--------|-------------|------------|
| **Binance Testnet** | 0€ | ✅ TESTNET | Stablecoins | ✅ Spot/Futures/Margin | #1 Global | **PRIMARY** |
| **OANDA Practice** | 0€ | ✅ PRACTICE | ✅ #1 Forex | ❌ | #1 Forex | **FOREX** |
| **Bybit Demo** | 0€ | ✅ DEMO | ❌ | ✅ Spot/Perps | #2 Global | BACKUP |
| **Kraken Sandbox** | 0€ | ✅ SANDBOX | ❌ | ✅ Spot/Margin | Top 5 EUR | BACKUP |
| **KuCoin Sandbox** | 0€ | ✅ SANDBOX | ❌ | ✅ Spot/Margin | Top 10 | ALTCOINS |
| **Alpaca Paper** | 0€ | ✅ PAPER | ❌ | ✅ Spot | US Stocks | US MARKET |

---

## Detaillierter Vergleich

### 1. Binance Testnet ⭐ PRIMARY

**API Endpoints:**
- REST: `https://testnet.binance.vision/api/v3/...`
- WebSocket: `wss://testnet.binance.vision/ws/...`
- Futures Testnet: `https://testnet.binancefuture.com/...`

**Limits:**
- 6,000 request weight/min
- 50 orders/10 Sekunden
- 160,000 orders/Tag

**Kosten:** 0€ für API, 0€ Maker/Taker auf Testnet
**KYC:** Nicht nötig für Testnet (nur API Key)
**Features:** Spot, Margin, Futures, Options (Partial)
**CCXT:** `binance` (testnet über Sandbox-Flag)

**Vorteile:**
- Größte Liquidität weltweit
- Beste API-Dokumentation
- Umfangreichste Datenhistorie
- Multi-Asset (Krypto + Stable-Fiat-Paare)

**Nachteile:**
- Kein echtes Forex (nur Stablecoin-Paare: BTC/EUR, BTC/USDT)
- Testnet Liquidität ist simuliert

---

### 2. OANDA Practice ⭐ FOREX

**API Endpoints:**
- REST: `https://api-fxpractice.oanda.com/v3/accounts`
- Streaming: `https://stream-fxpractice.oanda.com/v3/accounts/{id}/pricing/stream`

**Limits:**
- 100 requests/2 Sekunden
- Streaming-Connection dauerhaft

**Kosten:** 0€ für Practice Account
**KYC:** E-Mail-Registrierung nötig
**Features:** 70+ Währungspaare (EUR/USD, GBP/USD, CHF/EUR, etc.)
**Python SDK:** `oandapyV20` oder `v20`

**Vorteile:**
- #1 Broker für Retail Forex
- Echte Marktdaten in Practice
- MT4/MT5 kompatibel
- CFDs auf Indizes, Commodities

**Nachteile:**
- Nur Forex + CFDs
- Spread-basiert (keine Kommission)
- Kein Krypto

---

### 3. Bybit Demo

**API Endpoints:**
- REST: `https://api-demo.bybit.com/v5/...`
- WebSocket: `wss://stream-demo.bybit.com/v5/...`

**Limits:**
- 50 requests/Sekunde
- 500 orders/Tag

**Kosten:** 0€ für Demo
**Features:** Spot, Perpetual Futures, Options

**Vorteile:**
- Starke Futures-Plattform
- Demo-Account ohne KYC
- Unified Trading Account

---

### 4. Kraken Sandbox

**API Endpoints:**
- REST: `https://api.sandbox.kraken.com/0/...`
- WebSocket: `wss://sandbox.kraken.com/...`

**Limits:**
- 60 requests/min
- Rate-Limits per Tier

**Kosten:** 0€ für Sandbox
**KYC:** Nicht für Sandbox nötig
**Features:** Spot, Margin, Futures

**Vorteile:**
- EUR-freundlich (SEPA, EUR-Paare)
- Streng reguliert
- Gute API

---

### 5. Alpaca Paper

**API Endpoints:**
- REST: `https://paper-api.alpaca.markets/v2/...`
- WebSocket: `wss://paper-api.alpaca.markets/stream`
**Limits:** 200 requests/min
**Kosten:** 0€ für Paper-Trading
**KYC:** Nicht nötig
**Features:** US Stocks + Crypto Spot

---

## Unified Access via CCXT

```python
import ccxt

# Binance Testnet
binance = ccxt.binance({'sandbox': True, 'apiKey': '...', 'secret': '...'})
binance.set_sandbox_mode(True)

# OANDA (über oandapyV20)
# Bybit Demo
bybit = ccxt.bybit({'sandbox': True})

# Kraken Sandbox
kraken = ccxt.kraken({'sandbox': True})
```

---

## Entscheidung

**PRIMARY STACK:**
1. **Krypto:** Binance Testnet (Spot + Futures)
2. **Forex:** OANDA Practice (70+ Paare)
3. **Fallback:** Bybit Demo, Kraken Sandbox

**WARUM:**
- Beide Plattformen sind 100% kostenlos
- Beide haben dedicated Paper/Demo-Umgebungen
- Beide haben Python-SDKs mit ausgereifter Dokumentation
- Keine Live-Kapital-Risiken während der Entwicklung

---

## Nächste Schritte

1. [[01_Research/API-Keys einrichten]]
2. [[02_Strategies/Technische Analyse Grundlagen]]
3. [[03_Backtests/Backtesting-Framework evaluieren]]
4. [[04_Agents/Trading-Agent-Architektur]]

---
*Erstellt: 2026-05-22*
*Autor: Hermes Agent | Projekt: Trading-Agent*
