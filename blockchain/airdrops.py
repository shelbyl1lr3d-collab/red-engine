import json
from datetime import datetime

class AirDropScanner:
    def __init__(self, engine):
        self.engine = engine
        self.watched_addresses = []
        self.found_airdrops = []

    def scan(self, address=None):
        results = []
        sources = [
            "https://airdropalert.com",
            "https://coinmarketcap.com/airdrop/",
            "https://coingecko.com/airdrops"
        ]
        result = {
            "address": address or "not provided",
            "sources_to_check": sources,
            "note": "Connect wallet to these platforms and check eligibility.",
            "timestamp": datetime.now().isoformat()
        }
        self.found_airdrops.append(result)
        return result

    def add_address(self, address, label=""):
        self.watched_addresses.append({
            "address": address,
            "label": label,
            "added": datetime.now().isoformat()
        })
        return {"status": f"watching {address}"}

    def check_eth(self, address):
        return {
            "address": address,
            "note": "Check https://etherscan.io/address/" + address + "#tokentxns for unclaimed tokens.",
            "tools": ["app.zerion.io", "debank.com", "zapper.fi"]
        }

    def check_solana(self, address):
        return {
            "address": address,
            "note": "Check https://solscan.io/account/" + address + " for token balances.",
            "tools": ["step.finance", "raydium.io"]
        }

    def report(self):
        return {
            "watched_addresses": len(self.watched_addresses),
            "scans_run": len(self.found_airdrops),
            "latest": self.found_airdrops[-1] if self.found_airdrops else None
        }
