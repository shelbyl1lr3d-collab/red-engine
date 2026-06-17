import os, json, random, string, hashlib
from datetime import datetime

class TokenEngine:
    def __init__(self, engine):
        self.engine = engine
        self.tokens_file = os.path.expanduser("~/.red_tokens.json")
        self.chains = {
            "ethereum": {"decimals": 18, "standard": "ERC-20"},
            "bsc": {"decimals": 18, "standard": "BEP-20"},
            "solana": {"decimals": 9, "standard": "SPL"}
        }

    def _load(self):
        if os.path.exists(self.tokens_file):
            with open(self.tokens_file) as f:
                return json.load(f)
        return {}

    def _save(self, tokens):
        with open(self.tokens_file, "w") as f:
            json.dump(tokens, f, indent=2)

    def mint(self, name, symbol=None, chain="bsc", supply=10_000_000, owner="Forge"):
        """Create a new token record (simulated minting)."""
        tokens = self._load()
        key = name.lower().replace(" ", "_")[:30]
        if key in tokens:
            return {"error": f"Token '{name}' already exists as {tokens[key]['symbol']}"}

        symbol = symbol or self._generate_symbol(name)
        token_id = hashlib.sha256(f"{name}{symbol}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        token = {
            "name": name,
            "symbol": symbol.upper(),
            "supply": supply,
            "decimals": self.chains.get(chain, {}).get("decimals", 18),
            "standard": self.chains.get(chain, {}).get("standard", "ERC-20"),
            "chain": chain,
            "token_id": token_id,
            "liquidity": 0,
            "backing_usd": 0,
            "owner": owner,
            "minted": datetime.now().isoformat(),
            "contract_address": f"0x{token_id}{'0'*24}" if chain != "solana" else token_id,
            "audited": False,
            "holders": 0
        }
        tokens[key] = token
        self._save(tokens)
        self.engine.log(f"Token minted: {name} ({symbol}) on {chain} — supply: {supply}")
        return token

    def _generate_symbol(self, name):
        words = name.replace("-", " ").split()
        sym = "".join(w[0].upper() for w in words if w)[:5]
        if len(sym) < 2:
            sym = name[:3].upper()
        return sym

    def get_all(self):
        tokens = self._load()
        return tokens

    def get(self, name_or_symbol):
        tokens = self._load()
        key = name_or_symbol.lower().replace(" ", "_")[:30]
        if key in tokens:
            return tokens[key]
        for k, v in tokens.items():
            if v["symbol"].upper() == name_or_symbol.upper():
                return v
        return None

    def add_liquidity(self, symbol, amount_usd):
        """Add liquidity backing to a token."""
        tokens = self._load()
        for k, v in tokens.items():
            if v["symbol"] == symbol.upper():
                v["liquidity"] = v.get("liquidity", 0) + amount_usd
                v["backing_usd"] = v.get("backing_usd", 0) + amount_usd
                self._save(tokens)
                self.engine.log(f"Liquidity added to {symbol}: ${amount_usd}")
                return {"symbol": symbol, "liquidity": v["liquidity"], "backing_usd": v["backing_usd"]}
        return {"error": f"Token {symbol} not found"}

    def summary(self):
        tokens = self._load()
        total_liquidity = sum(t.get("liquidity", 0) for t in tokens.values())
        total_supply = sum(t.get("supply", 0) for t in tokens.values())
        return {
            "count": len(tokens),
            "total_liquidity": total_liquidity,
            "total_supply": total_supply,
            "tokens": [
                {"name": t["name"], "symbol": t["symbol"],
                 "supply": t["supply"], "liquidity": t.get("liquidity", 0),
                 "chain": t.get("chain", "bsc")}
                for t in tokens.values()
            ]
        }

    def generate_smart_contract(self, token, chain="bsc"):
        """Generate a Solidity smart contract for the token."""
        if chain == "solana":
            return self._generate_spl_anchor(token)
        standard = self.chains.get(chain, self.chains["bsc"])
        name = token["name"]
        symbol = token["symbol"]
        supply = token["supply"]
        decimals = token["decimals"]

        contract = f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract {name.replace(' ', '')} is ERC20, Ownable {{
    uint256 public constant INITIAL_SUPPLY = {supply} * 10 ** {decimals};
    address public constant TREASURY = address(0x{TREASURY_PLACEHOLDER});

    constructor() ERC20("{name}", "{symbol}") Ownable(msg.sender) {{
        _mint(TREASURY, INITIAL_SUPPLY);
    }}

    function mint(address to, uint256 amount) external onlyOwner {{
        _mint(to, amount);
    }}

    function burn(uint256 amount) external {{
        _burn(msg.sender, amount);
    }}
}}
"""
        return {
            "contract": contract,
            "standard": standard,
            "chain": chain,
            "audit_needed": True
        }

    def _generate_spl_anchor(self, token):
        return {
            "contract": f"// SPL Token: {token['name']} ({token['symbol']})\n// Use Solana CLI: spl-token create-token && spl-token create-account",
            "standard": "SPL",
            "chain": "solana"
        }
