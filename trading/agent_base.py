from ..exchange.binance import BinanceExchange
import time, json, os
from datetime import datetime

class TradingAgent:
    def __init__(self, name, engine, config=None):
        self.name = name
        self.engine = engine
        self.config = config or {}
        self.exchange = BinanceExchange(engine)
        self.running = False
        self.trades = []
        self.pnl = 0.0
        self.start_balance = 0.0
        self._load_state()

    def _state_file(self):
        return os.path.expanduser(f"~/.red_trader_{self.name.lower()}.json")

    def _load_state(self):
        path = self._state_file()
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                self.trades = data.get("trades", [])
                self.pnl = data.get("pnl", 0.0)
                self.start_balance = data.get("start_balance", 0.0)

    def _save_state(self):
        with open(self._state_file(), "w") as f:
            json.dump({
                "trades": self.trades[-100:],
                "pnl": self.pnl,
                "start_balance": self.start_balance,
                "last_update": datetime.now().isoformat()
            }, f, indent=2)

    def is_ready(self):
        return self.exchange.is_configured()

    def get_balance(self, asset="USDT"):
        return self.exchange.get_asset_balance(asset)

    def get_price(self, symbol="BTCUSDT"):
        return self.exchange.get_price(symbol)

    def execute_trade(self, side, symbol, quantity=None, quote_qty=None):
        if not self.is_ready():
            return {"error": "Exchange not configured"}

        if side.upper() == "BUY":
            result = self.exchange.market_buy(symbol, quote_qty)
        else:
            result = self.exchange.market_sell(symbol, quantity)

        if "error" not in result:
            trade = {
                "time": datetime.now().isoformat(),
                "agent": self.name,
                "side": side,
                "symbol": symbol,
                "quantity": result.get("executedQty", quantity),
                "price": result.get("fills", [{}])[0].get("price", "0") if result.get("fills") else "0",
                "status": result.get("status", "FILLED")
            }
            self.trades.append(trade)
            self._save_state()
            self.engine.log(f"{self.name} {side} {symbol}: {result.get('status', 'EXECUTED')}")

        return result

    def log(self, msg):
        self.engine.log(f"[T:{self.name}] {msg}")

    def start(self):
        self.running = True
        self.log(f"Agent started")

    def stop(self):
        self.running = False
        self.log(f"Agent stopped")
        self._save_state()

    def status(self):
        return {
            "name": self.name,
            "running": self.running,
            "pnl": self.pnl,
            "trades_count": len(self.trades),
            "last_trade": self.trades[-1] if self.trades else None,
            "config": self.config
        }
