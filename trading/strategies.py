import time, random, json

class Strategy:
    def __init__(self, agent):
        self.agent = agent
        self.name = "base"

    def analyze(self):
        """Return (action, symbol, quantity_dict) or None"""
        return None

    def __repr__(self):
        return f"{self.name}"


class DCAStrategy(Strategy):
    """Dollar Cost Average - buy fixed amount at intervals"""
    def __init__(self, agent, symbol="BTCUSDT", amount_usd=5, interval_minutes=1440):
        super().__init__(agent)
        self.name = "dca"
        self.symbol = symbol
        self.amount_usd = amount_usd
        self.interval = interval_minutes * 60
        self.last_buy = 0

    def analyze(self):
        now = time.time()
        if now - self.last_buy < self.interval:
            return None
        self.last_buy = now
        return ("BUY", self.symbol, {"quote_qty": self.amount_usd})


class ScalpStrategy(Strategy):
    """Quick scalping on volatile pairs - buy dip, sell rip"""
    def __init__(self, agent, symbol="BTCUSDT", min_drop_pct=0.5, target_profit_pct=1.0):
        super().__init__(agent)
        self.name = "scalp"
        self.symbol = symbol
        self.min_drop = min_drop_pct
        self.target = target_profit_pct
        self.position = None
        self.entry_price = 0

    def analyze(self):
        price_data = self.agent.get_price(self.symbol)
        if "error" in price_data:
            return None
        current_price = float(price_data["price"])

        if self.position is None:
            entry_price = self._get_reference_price()
            drop = (entry_price - current_price) / entry_price * 100
            if drop >= self.min_drop:
                self.position = "bought"
                self.entry_price = current_price
                return ("BUY", self.symbol, {"quote_qty": 2})
        else:
            rise = (current_price - self.entry_price) / self.entry_price * 100
            if rise >= self.target:
                self.position = None
                bal = self.agent.get_balance("BTC")
                if "error" not in bal and float(bal.get("free", 0)) > 0.0001:
                    qty = float(bal["free"]) * 0.5
                    return ("SELL", self.symbol, {"quantity": qty})
        return None

    def _get_reference_price(self):
        p = self.agent.get_price(self.symbol)
        return float(p["price"]) if "error" not in p else 50000


class GridStrategy(Strategy):
    """Place limit orders at fixed intervals around current price"""
    def __init__(self, agent, symbol="BTCUSDT", grid_levels=5, spacing_pct=2.0, amount_per_grid=2):
        super().__init__(agent)
        self.name = "grid"
        self.symbol = symbol
        self.levels = grid_levels
        self.spacing = spacing_pct
        self.amount = amount_per_grid
        self.active_orders = []

    def analyze(self):
        price_data = self.agent.get_price(self.symbol)
        if "error" in price_data:
            return None
        price = float(price_data["price"])

        if len(self.active_orders) >= self.levels * 2:
            return None

        targets = []
        for i in range(1, self.levels + 1):
            buy_price = price * (1 - self.spacing * i / 100)
            sell_price = price * (1 + self.spacing * i / 100)
            if not self._order_exists(buy_price):
                targets.append(("BUY", self.symbol, {"quote_qty": self.amount}))
            if not self._order_exists(sell_price):
                targets.append(("SELL", self.symbol, {}))
        return targets[0] if targets else None

    def _order_exists(self, price):
        return False


class ArbitrageStrategy(Strategy):
    """Monitor multiple pairs for arbitrage opportunities"""
    def __init__(self, agent, pairs=None):
        super().__init__(agent)
        self.name = "arbitrage"
        self.pairs = pairs or ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

    def analyze(self):
        prices = {}
        for pair in self.pairs:
            p = self.agent.get_price(pair)
            if "error" not in p:
                prices[pair] = float(p["price"])

        if len(prices) < 2:
            return None

        btc = prices.get("BTCUSDT", 0)
        eth = prices.get("ETHUSDT", 0)
        bnb = prices.get("BNBUSDT", 0)

        if btc and eth:
            cross = btc / eth
            if cross > 40:
                bal = self.agent.get_balance("USDT")
                if "error" not in bal and float(bal.get("free", 0)) > 5:
                    return ("BUY", "ETHUSDT", {"quote_qty": 5})

        return None


class HodlStrategy(Strategy):
    """Accumulate and hold core assets"""
    def __init__(self, agent, symbol="BTCUSDT", target_balance=0.001, buy_amount=5):
        super().__init__(agent)
        self.name = "hodl"
        self.symbol = symbol
        self.target = target_balance
        self.amount = buy_amount

    def analyze(self):
        bal = self.agent.get_balance("BTC")
        if "error" not in bal:
            btc_free = float(bal.get("free", 0))
            if btc_free < self.target:
                return ("BUY", self.symbol, {"quote_qty": self.amount})
        return None


class TripleStrategy(Strategy):
    """Compounding trades to 3x a starting position through repeated scalps"""
    def __init__(self, agent, symbol="BTCUSDT", starting_usd=10, target_multiple=3.0, target_percent=2.0):
        super().__init__(agent)
        self.name = "triple"
        self.symbol = symbol
        self.starting = starting_usd
        self.target = target_multiple
        self.target_pct = target_percent
        self.cycle = 0
        self.current_pool = 0
        self.peak = 0

    def analyze(self):
        bal_usdt = self.agent.get_balance("USDT")
        if "error" not in bal_usdt:
            free = float(bal_usdt.get("free", 0))
            if free > self.starting and self.current_pool == 0:
                self.current_pool = free
                self.peak = free

        if self.current_pool <= 0:
            return None

        price_data = self.agent.get_price(self.symbol)
        if "error" in price_data:
            return None

        results = self.current_pool * (1 + self.target_pct / 100)
        target_pool = self.starting * self.target
        mid_pool = self.current_pool + (results - self.current_pool) * 0.3

        if self.current_pool >= target_pool:
            return None

        if results < self.current_pool * 1.02:
            return None

        return ("BUY", self.symbol, {"quote_qty": round(min(self.current_pool, 100), 2)})

    def record_trade(self, profit_pct):
        growth = 1 + (profit_pct / 100)
        self.current_pool *= growth
        self.cycle += 1
        if self.current_pool > self.peak:
            self.peak = self.current_pool

    def progress(self):
        return {
            "start": self.starting,
            "current": round(self.current_pool, 2),
            "target": self.target,
            "target_value": round(self.starting * self.target, 2),
            "cycles": self.cycle,
            "progress_pct": round((self.current_pool / (self.starting * self.target)) * 100, 2) if self.starting > 0 else 0
        }
