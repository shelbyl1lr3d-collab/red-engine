import os, json
from datetime import datetime

class Treasury:
    def __init__(self, engine):
        self.engine = engine
        self.file = os.path.expanduser("~/.red_treasury.json")

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                return json.load(f)
        return {
            "balance": 0,
            "total_deposits": 0,
            "total_withdrawals": 0,
            "transactions": [],
            "pools": {},
            "yield_earned": 0,
            "last_compound": None
        }

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def deposit(self, source, amount_usd, token_symbol=None):
        """Route revenue into the treasury pool."""
        data = self._load()
        data["balance"] += amount_usd
        data["total_deposits"] += amount_usd
        tx = {
            "type": "deposit",
            "source": source,
            "amount": amount_usd,
            "token": token_symbol,
            "balance_after": data["balance"],
            "time": datetime.now().isoformat()
        }
        data["transactions"].append(tx)
        if len(data["transactions"]) > 500:
            data["transactions"] = data["transactions"][-500:]

        if token_symbol:
            if "sources" not in data:
                data["sources"] = {}
            if token_symbol not in data["sources"]:
                data["sources"][token_symbol] = 0
            data["sources"][token_symbol] += amount_usd

        self._save(data)
        self.engine.log(f"Treasury deposit: ${amount_usd} from {source}")
        return {"balance": data["balance"], "deposited": amount_usd, "source": source}

    def compound(self, rate_apr=5.0):
        """Simulate yield compounding on treasury balance."""
        data = self._load()
        if data["balance"] <= 0:
            return {"error": "No balance to compound"}

        daily_rate = rate_apr / 36500
        yield_amt = data["balance"] * daily_rate
        data["balance"] += yield_amt
        data["yield_earned"] += yield_amt
        data["last_compound"] = datetime.now().isoformat()

        tx = {
            "type": "compound",
            "amount": yield_amt,
            "rate_apr": rate_apr,
            "balance_after": data["balance"],
            "time": datetime.now().isoformat()
        }
        data["transactions"].append(tx)
        self._save(data)
        self.engine.log(f"Treasury compounded: +${yield_amt:.2f} at {rate_apr}% APR")
        return {"yield": round(yield_amt, 2), "balance": round(data["balance"], 2), "apr": rate_apr}

    def report(self):
        data = self._load()
        return {
            "balance": round(data["balance"], 2),
            "total_deposits": round(data["total_deposits"], 2),
            "yield_earned": round(data["yield_earned"], 2),
            "tx_count": len(data["transactions"]),
            "last_compound": data["last_compound"],
            "sources": data.get("sources", {}),
            "progress_pct": round((data["balance"] / self.engine.config.get("goal_usd", 1_000_000_000)) * 100, 6)
        }

    def check_milestone(self):
        """Check if we hit $1B milestone."""
        data = self._load()
        goal = self.engine.config.get("goal_usd", 1_000_000_000)
        return {
            "reached": data["balance"] >= goal,
            "balance": data["balance"],
            "goal": goal,
            "remaining": max(0, goal - data["balance"]),
            "progress_pct": round((data["balance"] / goal) * 100, 6)
        }

    def withdraw(self, amount, reason="milestone"):
        """Record withdrawal (real withdrawal requires human approval)."""
        data = self._load()
        if amount > data["balance"]:
            return {"error": "Insufficient balance"}
        data["balance"] -= amount
        data["total_withdrawals"] += amount
        tx = {
            "type": "withdrawal",
            "amount": amount,
            "reason": reason,
            "balance_after": data["balance"],
            "time": datetime.now().isoformat()
        }
        data["transactions"].append(tx)
        self._save(data)
        return {"withdrawn": amount, "balance": data["balance"], "reason": reason}
