import os, json
from datetime import datetime

class RevenueRouter:
    def __init__(self, engine):
        self.engine = engine
        self.file = os.path.expanduser("~/.red_revenue_router.json")

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                return json.load(f)
        return {"routes": [], "total_routed": 0, "total_sources": {}}

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def route(self, source_name, amount_usd, asset="USDT", auto_trade=True):
        """Route revenue from a source through the system."""
        data = self._load()

        pipeline = []

        # Step 1: Treasury deposit
        from ..blockchain.treasury import Treasury
        treasury = Treasury(self.engine)
        deposit = treasury.deposit(source_name, amount_usd)
        pipeline.append({"step": "treasury", "amount": amount_usd, "balance": deposit["balance"]})

        # Step 2: Route to exchange
        if auto_trade and amount_usd >= 1:
            from .binance import BinanceExchange
            exchange = BinanceExchange(self.engine)
            if exchange.is_configured():
                trade_result = exchange.route_revenue_to_liquidity(amount_usd)
                pipeline.append({"step": "exchange_trade", "result": trade_result})
            else:
                pipeline.append({"step": "exchange_skipped", "reason": "Binance not configured"})

        # Step 3: Add to game token liquidity
        from ..blockchain.liquidity import LiquidityPool
        pool = LiquidityPool(self.engine)
        liquidity_routes = []
        for game_token in ["RED", "FOR", "GOLD"]:
            route_amt = amount_usd * 0.05
            if route_amt >= 1:
                r = pool.route_revenue(route_amt, game_token, source_name)
                liquidity_routes.append(r)
        pipeline.append({"step": "token_liquidity", "routes": liquidity_routes})

        route_entry = {
            "id": f"route_{datetime.now().timestamp():.0f}",
            "source": source_name,
            "amount": amount_usd,
            "asset": asset,
            "auto_traded": auto_trade,
            "pipeline": pipeline,
            "time": datetime.now().isoformat()
        }
        data["routes"].append(route_entry)
        data["total_routed"] += amount_usd
        if source_name not in data["total_sources"]:
            data["total_sources"][source_name] = 0
        data["total_sources"][source_name] += amount_usd
        if len(data["routes"]) > 1000:
            data["routes"] = data["routes"][-500:]
        self._save(data)

        self.engine.log(f"Revenue routed: ${amount_usd} from {source_name} — {len(pipeline)} pipeline steps")

        return {
            "source": source_name,
            "amount": amount_usd,
            "total_routed": data["total_routed"],
            "pipeline": pipeline
        }

    def report(self):
        data = self._load()
        return {
            "total_routed": data["total_routed"],
            "route_count": len(data["routes"]),
            "sources": data["total_sources"],
            "last_routes": data["routes"][-5:] if data["routes"] else []
        }
