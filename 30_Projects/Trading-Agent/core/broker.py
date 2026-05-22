"""
Trading Agent - Broker Interface
Unified brokerage abstraction for all supported trading venues.
Phase: backtest → paper → live

Supported:
  - Binance (Testnet + Live) via CCXT
  - Bybit (Demo + Live) via CCXT
  - Hyperliquid (Live only) via custom SDK
  - OANDA (Practice + Live) via v20 SDK
"""
from __future__ import annotations
import os
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

try:
    import ccxt
except ImportError:
    ccxt = None

try:
    import pandas as pd
except ImportError:
    pd = None


class TradingMode(Enum):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


class AssetClass(Enum):
    CRYPTO_SPOT = "crypto_spot"
    CRYPTO_PERP = "crypto_perp"
    FOREX = "forex"


@dataclass
class Order:
    symbol: str
    side: str  # "buy" | "sell"
    amount: float
    order_type: str = "market"  # market | limit | stop_loss_limit
    price: Optional[float] = None
    leverage: Optional[float] = None


@dataclass
class Position:
    symbol: str
    side: str  # "long" | "short"
    size: float
    entry_price: float
    unrealized_pnl: float
    leverage: Optional[float] = None


class BrokerInterface(ABC):
    """Abstract broker interface. All concrete brokers implement this."""

    def __init__(self, mode: TradingMode):
        self.mode = mode
        self.exchange = None
        self.connected = False

    @abstractmethod
    def connect(self) -> bool:
        """Authenticate and establish connection."""
        pass

    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """Return {asset: free, ...} balances."""
        pass

    @abstractmethod
    def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV candles. Returns DataFrame with columns [timestamp, open, high, low, close, volume]."""
        pass

    @abstractmethod
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """Return {bids: [[price, size], ...], asks: [[price, size], ...]}."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Return open positions."""
        pass

    @abstractmethod
    def place_order(self, order: Order) -> Dict:
        """Execute an order. Return order details."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        """Cancel an open order."""
        pass

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict:
        """Return {bid, ask, last, volume, change_pct}."""
        pass

    def _rate_limit_sleep(self, weight: int = 1):
        """Basic rate limit guard. Override per broker."""
        time.sleep(0.1 * weight)


class BinanceBroker(BrokerInterface):
    """Binance Spot + Futures via CCXT (Testnet / Live)."""

    def __init__(self, mode: TradingMode):
        super().__init__(mode)
        if ccxt is None:
            raise RuntimeError("ccxt required. Run: uv pip install ccxt")

        api_key = os.getenv("BINANCE_TESTNET_API_KEY" if mode != TradingMode.LIVE else "BINANCE_LIVE_API_KEY")
        secret = os.getenv("BINANCE_TESTNET_SECRET" if mode != TradingMode.LIVE else "BINANCE_LIVE_SECRET")

        self.exchange = ccxt.binance({
            "apiKey": api_key,
            "secret": secret,
            "sandbox": (mode != TradingMode.LIVE),
            "enableRateLimit": True,
            "options": {
                "defaultType": "spot",
            }
        })
        self.exchange.set_sandbox_mode(mode != TradingMode.LIVE)

    def connect(self) -> bool:
        try:
            self.exchange.load_markets()
            self.connected = True
            return True
        except Exception as e:
            print(f"[Binance] Connection failed: {e}")
            return False

    def get_balance(self) -> Dict[str, float]:
        if not self.connected:
            return {}
        bal = self.exchange.fetch_balance()
        return {a: v["free"] for a, v in bal.get("total", {}).items() if v and v != 0}

    def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100):
        if not self.connected:
            return None
        data = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if pd is None:
            return data
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        if not self.connected:
            return {}
        ob = self.exchange.fetch_order_book(symbol, limit=limit)
        return {"bids": ob["bids"], "asks": ob["asks"]}

    def get_positions(self) -> List[Position]:
        # Spot only; for futures override with defaultType: "future"
        return []

    def place_order(self, order: Order) -> Dict:
        if not self.connected:
            return {"error": "Not connected"}
        self._rate_limit_sleep(weight=1)
        try:
            return self.exchange.create_order(
                order.symbol,
                order.order_type,
                order.side,
                order.amount,
                order.price
            )
        except Exception as e:
            return {"error": str(e)}

    def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        if not self.connected:
            return False
        try:
            self.exchange.cancel_order(order_id, symbol)
            return True
        except Exception:
            return False

    def get_ticker(self, symbol: str) -> Dict:
        if not self.connected:
            return {}
        t = self.exchange.fetch_ticker(symbol)
        return {
            "bid": t.get("bid"),
            "ask": t.get("ask"),
            "last": t.get("last"),
            "volume": t.get("quoteVolume"),
            "change_pct": t.get("percentage"),
        }


class BybitBroker(BrokerInterface):
    """Bybit Spot + Perps via CCXT (Demo / Live)."""

    def __init__(self, mode: TradingMode):
        super().__init__(mode)
        if ccxt is None:
            raise RuntimeError("ccxt required.")

        api_key = os.getenv("BYBIT_DEMO_API_KEY" if mode != TradingMode.LIVE else "BYBIT_LIVE_API_KEY")
        secret = os.getenv("BYBIT_DEMO_SECRET" if mode != TradingMode.LIVE else "BYBIT_LIVE_SECRET")

        self.exchange = ccxt.bybit({
            "apiKey": api_key,
            "secret": secret,
            "sandbox": (mode != TradingMode.LIVE),
            "enableRateLimit": True,
        })

    def connect(self) -> bool:
        try:
            self.exchange.load_markets()
            self.connected = True
            return True
        except Exception as e:
            print(f"[Bybit] Connection failed: {e}")
            return False

    def get_balance(self) -> Dict[str, float]:
        if not self.connected:
            return {}
        bal = self.exchange.fetch_balance()
        return {a: v["free"] for a, v in bal.get("total", {}).items() if v and v != 0}

    def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100):
        if not self.connected:
            return None
        data = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if pd is None:
            return data
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        if not self.connected:
            return {}
        ob = self.exchange.fetch_order_book(symbol, limit=limit)
        return {"bids": ob["bids"], "asks": ob["asks"]}

    def get_positions(self) -> List[Position]:
        if not self.connected:
            return []
        try:
            positions = self.exchange.fetch_positions()
            return [
                Position(
                    symbol=p["symbol"],
                    side="long" if p["side"] == "long" else "short",
                    size=abs(float(p["contracts"])),
                    entry_price=float(p["entryPrice"] or 0),
                    unrealized_pnl=float(p["unrealizedPnl"] or 0),
                    leverage=float(p.get("leverage", 1)),
                )
                for p in positions if p["contracts"] and float(p["contracts"]) != 0
            ]
        except Exception:
            return []

    def place_order(self, order: Order) -> Dict:
        if not self.connected:
            return {"error": "Not connected"}
        self._rate_limit_sleep(weight=1)
        params = {}
        if order.leverage:
            params["leverage"] = order.leverage
        try:
            return self.exchange.create_order(
                order.symbol,
                order.order_type,
                order.side,
                order.amount,
                order.price,
                params
            )
        except Exception as e:
            return {"error": str(e)}

    def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        if not self.connected:
            return False
        try:
            self.exchange.cancel_order(order_id, symbol)
            return True
        except Exception:
            return False

    def get_ticker(self, symbol: str) -> Dict:
        if not self.connected:
            return {}
        t = self.exchange.fetch_ticker(symbol)
        return {
            "bid": t.get("bid"),
            "ask": t.get("ask"),
            "last": t.get("last"),
            "volume": t.get("quoteVolume"),
            "change_pct": t.get("percentage"),
        }


class HyperliquidBroker(BrokerInterface):
    """Hyperliquid Perp DEX (Live ONLY — no paper mode)."""

    BASE_URL = "https://api.hyperliquid.xyz"

    def __init__(self, mode: TradingMode = TradingMode.LIVE):
        if mode != TradingMode.LIVE:
            print("[WARNING] Hyperliquid has no paper/demo mode. LIVE only.")
        super().__init__(mode)
        self.wallet_key = os.getenv("HYPERLIQUID_WALLET_KEY")
        self.wallet_address = os.getenv("HYPERLIQUID_ADDRESS")

    def connect(self) -> bool:
        try:
            import requests
            r = requests.post(f"{self.BASE_URL}/info", json={"type": "meta"})
            r.raise_for_status()
            meta = r.json()
            print(f"[Hyperliquid] Connected. Perps: {len(meta.get('universe', []))}")
            self.connected = True
            return True
        except Exception as e:
            print(f"[Hyperliquid] Connection failed: {e}")
            return False

    def get_balance(self) -> Dict[str, float]:
        import requests
        r = requests.post(f"{self.BASE_URL}/info", json={
            "type": "clearinghouseState",
            "user": self.wallet_address
        })
        data = r.json()
        total = float(data.get("marginSummary", {}).get("accountValue", 0))
        return {"USDC": total}

    def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100):
        """Hyperliquid has no native OHLCV endpoint. Use Hyperliquid Python SDK or aggregate from trades."""
        # Placeholder: recommend external data source or SDK
        print("[Hyperliquid] Use hyperliquid-python-sdk for candles. Returning None.")
        return None

    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        import requests
        r = requests.post(f"{self.BASE_URL}/info", json={
            "type": "l2Book",
            "coin": symbol
        })
        data = r.json()
        levels = data.get("levels", [[], []])
        return {
            "bids": [[float(b["px"]), float(b["sz"])] for b in levels[0][:limit]],
            "asks": [[float(a["px"]), float(a["sz"])] for a in levels[1][:limit]],
        }

    def get_positions(self) -> List[Position]:
        import requests
        r = requests.post(f"{self.BASE_URL}/info", json={
            "type": "clearinghouseState",
            "user": self.wallet_address
        })
        data = r.json()
        positions = []
        for p in data.get("assetPositions", []):
            pos_data = p.get("position", {})
            positions.append(Position(
                symbol=pos_data.get("coin", ""),
                side="long" if float(pos_data.get("szi", 0)) > 0 else "short",
                size=abs(float(pos_data.get("szi", 0))),
                entry_price=float(pos_data.get("entryPx", 0)),
                unrealized_pnl=float(p.get("unrealizedPnl", 0)),
                leverage=float(pos_data.get("leverage", {}).get("value", 1)),
            ))
        return positions

    def place_order(self, order: Order) -> Dict:
        """Requires signed transactions via hyperliquid-python-sdk. Placeholder."""
        print("[Hyperliquid] Wallet signature required. Use hyperliquid-python-sdk.")
        return {"status": "placeholder", "note": "Requires SDK for signed execution."}

    def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        """Requires signed transactions. Placeholder."""
        return False

    def get_ticker(self, symbol: str) -> Dict:
        ob = self.get_orderbook(symbol, limit=1)
        return {
            "bid": ob["bids"][0][0] if ob.get("bids") else None,
            "ask": ob["asks"][0][0] if ob.get("asks") else None,
            "last": None,
            "volume": None,
            "change_pct": None,
        }


class OandaBroker(BrokerInterface):
    """OANDA Forex (Practice / Live) via v20 SDK."""

    def __init__(self, mode: TradingMode = TradingMode.PAPER):
        super().__init__(mode)
        self.env = "practice" if mode != TradingMode.LIVE else "live"
        self.token = os.getenv("OANDA_PRACTICE_TOKEN" if mode != TradingMode.LIVE else "OANDA_LIVE_TOKEN")
        self.account_id = os.getenv("OANDA_PRACTICE_ACCOUNT_ID" if mode != TradingMode.LIVE else "OANDA_LIVE_ACCOUNT_ID")
        self.api = None

    def connect(self) -> bool:
        try:
            from oandapyV20 import API
            self.api = API(access_token=self.token, environment=self.env)
            self.connected = True
            return True
        except Exception as e:
            print(f"[OANDA] Connection failed: {e}")
            return False

    def get_balance(self) -> Dict[str, float]:
        if not self.connected:
            return {}
        from oandapyV20.endpoints.accounts import AccountDetails
        r = AccountDetails(accountID=self.account_id)
        self.api.request(r)
        bal = r.response["account"]["balance"]
        return {"USD": float(bal)}

    def get_ohlcv(self, symbol: str, timeframe: str = "H1", limit: int = 100):
        if not self.connected:
            return None
        from oandapyV20.endpoints.instruments import InstrumentsCandles
        gran_map = {"1m": "M1", "5m": "M5", "15m": "M15", "1h": "H1", "4h": "H4", "1d": "D"}
        gran = gran_map.get(timeframe, "H1")
        params = {"granularity": gran, "count": limit, "price": "M"}
        r = InstrumentsCandles(instrument=symbol, params=params)
        self.api.request(r)
        candles = r.response["candles"]
        data = [[
            c["time"],
            float(c["mid"]["o"]),
            float(c["mid"]["h"]),
            float(c["mid"]["l"]),
            float(c["mid"]["c"]),
            float(c["volume"]),
        ] for c in candles]
        if pd is None:
            return data
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        # OANDA does not provide L2 orderbook via REST
        return {"bids": [], "asks": [], "note": "OANDA REST has no L2 orderbook"}

    def get_positions(self) -> List[Position]:
        if not self.connected:
            return []
        from oandapyV20.endpoints.positions import OpenPositions
        r = OpenPositions(accountID=self.account_id)
        self.api.request(r)
        positions = []
        for p in r.response["positions"]:
            for side_key, side_val in [("long", "long"), ("short", "short")]:
                units = float(p[side_key].get("units", 0))
                if units != 0:
                    positions.append(Position(
                        symbol=p["instrument"],
                        side=side_val,
                        size=abs(units),
                        entry_price=float(p[side_key].get("averagePrice", 0)),
                        unrealized_pnl=float(p[side_key].get("unrealizedPL", 0)),
                    ))
        return positions

    def place_order(self, order: Order) -> Dict:
        if not self.connected:
            return {"error": "Not connected"}
        from oandapyV20.endpoints.orders import OrderCreate
        units = order.amount if order.side == "buy" else -order.amount
        body = {
            "order": {
                "units": str(units),
                "instrument": order.symbol,
                "type": "MARKET" if order.order_type == "market" else "LIMIT",
                "positionFill": "DEFAULT",
            }
        }
        if order.price and order.order_type == "limit":
            body["order"]["price"] = str(order.price)
        r = OrderCreate(accountID=self.account_id, data=body)
        self.api.request(r)
        return r.response

    def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        if not self.connected:
            return False
        from oandapyV20.endpoints.orders import OrderCancel
        r = OrderCancel(accountID=self.account_id, orderID=order_id)
        try:
            self.api.request(r)
            return True
        except Exception:
            return False

    def get_ticker(self, symbol: str) -> Dict:
        if not self.connected:
            return {}
        from oandapyV20.endpoints.pricing import PricingInfo
        r = PricingInfo(accountID=self.account_id, params={"instruments": symbol})
        self.api.request(r)
        price = r.response["prices"][0]
        return {
            "bid": float(price["bid"]),
            "ask": float(price["ask"]),
            "last": float(price["closeoutBid"]),
            "volume": None,
            "change_pct": None,
        }


class BrokerFactory:
    """Factory to instantiate correct broker based on phase config."""

    BROKERS = {
        "binance": BinanceBroker,
        "bybit": BybitBroker,
        "hyperliquid": HyperliquidBroker,
        "oanda": OandaBroker,
    }

    @classmethod
    def create(cls, name: str, mode: TradingMode) -> BrokerInterface:
        broker_cls = cls.BROKERS.get(name.lower())
        if not broker_cls:
            raise ValueError(f"Unknown broker: {name}. Available: {list(cls.BROKERS.keys())}")
        return broker_cls(mode)


# ═══════════════════════════════════════════════════════
# QUICK TEST
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    print("Trading Agent - Broker Interface Tests")
    print("=" * 50)

    # Test 1: Binance Testnet (no keys = public endpoints only)
    print("\n[Test] Binance Testnet (public)…")
    b = BrokerFactory.create("binance", TradingMode.BACKTEST)
    b.connect()
    if b.connected:
        t = b.get_ticker("BTC/USDT")
        print(f"  BTC/USDT bid={t.get('bid')} ask={t.get('ask')}")
        ob = b.get_orderbook("BTC/USDT", limit=3)
        print(f"  Orderbook bids={len(ob.get('bids', []))} asks={len(ob.get('asks', []))}")

    # Test 2: Bybit Demo (public)
    print("\n[Test] Bybit Demo (public)…")
    bb = BrokerFactory.create("bybit", TradingMode.PAPER)
    bb.connect()
    if bb.connected:
        t = bb.get_ticker("BTC/USDT:USDT")
        print(f"  BTC/USDT:USDT bid={t.get('bid')} ask={t.get('ask')}")

    # Test 3: Hyperliquid (public, no auth needed)
    print("\n[Test] Hyperliquid (public)…")
    hl = BrokerFactory.create("hyperliquid", TradingMode.LIVE)
    hl.connect()
    if hl.connected:
        ob = hl.get_orderbook("BTC", limit=3)
        print(f"  BTC best_bid={ob['bids'][0] if ob['bids'] else None}")
        print(f"  BTC best_ask={ob['asks'][0] if ob['asks'] else None}")

    print("\nTests complete.")
