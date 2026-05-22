# Trading Agent - Architektur

**Status:** In Entwicklung
**Phasen:** Backtest ➜ Paper ➜ Live

---

## Multi-Phase-Setup

| Phase | Broker | Ziel | Kapitalrisiko |
|-------|--------|------|---------------|
| **P0: Backtest** | Binance Testnet (Krypto) + OANDA Practice (Forex) | Strategien validieren | **0%** |
| **P1: Paper** | Bybit Demo (Perps + Spot) | Realdaten, kein echtes Geld | **0%** |
| **P2: Live** | Hyperliquid (Perps) + Binance (Spot) + OANDA (Forex) | Echtes Geld verdienen | **100%** |

---

## Core-Architektur

```
Trading-Agent/
├── core/
│   ├── broker.py          # Unified Broker Interface (CCXT + OANDA + Hyperliquid)
│   ├── config.py          # Phase-basierte Konfiguration (.env)
│   ├── executor.py        # Order-Routing, SL/TP, Position-Sizing
│   └── logger.py          # Trade-Logging, Performance-Tracking
├── strategies/
│   ├── base.py            # Abstract Strategy Base
│   ├── indicators.py      # RSI, MACD, EMA, ATR, etc.
│   └── example_rsi_macd.py # Erste Demo-Strategie
├── data/
│   ├── fetcher.py         # Marktdaten-Abzug (OHLCV, Orderbook)
│   ├── cache.py           # Lokale Datenbank (SQLite)
│   └── backtest.py        # Backtesting-Engine
├── agents/
│   ├── market_monitor.py   # 24/7 Marktüberwachung
│   ├── signal_generator.py # Signale basierend auf Strategie
│   └── risk_manager.py   # Exposure, Drawdown, Position-Limits
├── tests/
│   └── connection_tests.py # Broker-Verbindungs-Validierung
└── run.py                  # Main Entry Point (Phase-gesteuert)
```

---

## Phase-Konfiguration

Die Phase wird über eine einzige Umgebungsvariable gesteuert:

```bash
# .env
TRADING_MODE=paper    # backtest | paper | live

# P0: Binance Testnet
BINANCE_TESTNET_API_KEY=xxx
BINANCE_TESTNET_SECRET=xxx

# P0: OANDA Practice
OANDA_PRACTICE_ACCOUNT_ID=xxx
OANDA_PRACTICE_TOKEN=xxx

# P1: Bybit Demo
BYBIT_DEMO_API_KEY=xxx
BYBIT_DEMO_SECRET=xxx

# P2: Hyperliquid Live
HYPERLIQUID_WALLET_KEY=xxx   # Private Key für Wallet-Signatur
HYPERLIQUID_ADDRESS=xxx      # Wallet Address

# P2: Binance Live
BINANCE_LIVE_API_KEY=xxx
BINANCE_LIVE_SECRET=xxx

# P2: OANDA Live
OANDA_LIVE_ACCOUNT_ID=xxx
OANDA_LIVE_TOKEN=xxx
```

---

## Broker-Abstraktion

Alle Broker sprechen dasselbe Python-Interface:

```python
class BrokerInterface:
    def connect(self) -> bool: ...
    def get_balance(self) -> dict: ...
    def get_ohlcv(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame: ...
    def get_orderbook(self, symbol: str) -> dict: ...
    def place_order(self, symbol: str, side: str, amount: float, 
                    order_type: str = 'market', price: float = None) -> dict: ...
    def get_positions(self) -> list: ...
    def cancel_order(self, order_id: str) -> bool: ...
```

---

## Risiko-Management (Non-Negotiable)

| Regel | Wert | Warum |
|-------|------|-------|
| Max Drawdown pro Tag | 2% | Keine Katastrophe |
| Max Position Size | 5% Equity | Kein All-in |
| Max Leverage | 5x (Phase 1-2) | Überleben lernen |
| Stop-Loss | 1x ATR | Mechanischer Ausstieg |
| Max offene Trades | 3 gleichzeitig | Fokus + Kapital |

---

## Nächste Schritte

1. [[01_Research/API-Keys einrichten]]
2. [[04_Agents/Broker-Interface bauen]]
3. [[04_Agents/Erste Bybit Demo Verbindung]]
4. [[02_Strategies/RSI+MACD Strategie coden]]

---
*Erstellt: 2026-05-22*
*Autor: Hermes Agent*
