import json, os
from datetime import datetime

class LiquidityPool:
    def __init__(self, engine):
        self.engine = engine
        self.file = os.path.expanduser("~/.red_liquidity_pools.json")

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                return json.load(f)
        return {"pools": []}

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def create_pool(self, token_symbol, paired_with="USDT", initial_liquidity=0):
        """Create a liquidity pool record for a token."""
        data = self._load()
        pool = {
            "id": f"{token_symbol}-{paired_with}",
            "token": token_symbol,
            "paired_with": paired_with,
            "liquidity": initial_liquidity,
            "tvl": initial_liquidity,
            "volume_24h": 0,
            "fees_earned": 0,
            "apr": 0,
            "created": datetime.now().isoformat(),
            "active": True
        }
        # Check if pool exists
        for p in data["pools"]:
            if p["id"] == pool["id"]:
                return {"error": f"Pool {pool['id']} already exists", "pool": p}

        data["pools"].append(pool)
        self._save(data)
        self.engine.log(f"Liquidity pool created: {token_symbol}/{paired_with}")
        return pool

    def add_liquidity(self, pool_id, amount_usd):
        """Add liquidity to an existing pool."""
        data = self._load()
        for p in data["pools"]:
            if p["id"] == pool_id:
                p["liquidity"] += amount_usd
                p["tvl"] += amount_usd
                self._save(data)
                self.engine.log(f"Liquidity added to {pool_id}: ${amount_usd}")
                return {"pool": pool_id, "liquidity": p["liquidity"], "tvl": p["tvl"]}
        return {"error": f"Pool {pool_id} not found"}

    def route_revenue(self, amount_usd, target_token, source_game):
        """Route ad/game revenue as liquidity for a specific token."""
        pool_id = f"{target_token}-USDT"

        data = self._load()
        pool = None
        for p in data["pools"]:
            if p["id"] == pool_id:
                pool = p
                break

        if not pool:
            pool = self.create_pool(target_token, "USDT", 0)
            if "error" in pool:
                return pool
            data = self._load()
            pool = data["pools"][-1]

        pool["liquidity"] += amount_usd
        pool["tvl"] += amount_usd

        if "revenue_sources" not in pool:
            pool["revenue_sources"] = {}
        pool["revenue_sources"][source_game] = pool["revenue_sources"].get(source_game, 0) + amount_usd

        self._save(data)

        from .treasury import Treasury
        treasury = Treasury(self.engine)
        treasury.deposit(source_game, amount_usd, target_token)

        self.engine.log(f"Revenue routed: ${amount_usd} from {source_game} → {target_token} liquidity pool")

        return {
            "pool": pool_id,
            "added": amount_usd,
            "total_liquidity": pool["liquidity"],
            "tvl": pool["tvl"],
            "token": target_token,
            "source": source_game
        }

    def get_pools(self):
        data = self._load()
        total_tvl = sum(p.get("tvl", 0) for p in data["pools"])
        return {
            "count": len(data["pools"]),
            "total_tvl": total_tvl,
            "pools": data["pools"]
        }
