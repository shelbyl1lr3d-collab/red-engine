import os, json, hmac, hashlib, time, urllib.parse
from datetime import datetime

# Exchange configurations
EXCHANGES = {
    "binance": {
        "name": "Binance",
        "api_url": "https://api.binance.com",
        "key_file": "~/.binance_api_key.txt",
        "secret_file": "~/.binance_secret_key.txt",
        "has_earn": True,
        "has_staking": True,
        "has_launchpool": True,
        "referral_link": "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_003FTW9Q2Y&utm_source=Dashboard"
    },
    "coinbase": {
        "name": "Coinbase",
        "api_url": "https://api.coinbase.com",
        "key_file": "~/.coinbase_api_key.txt",
        "secret_file": "~/.coinbase_secret_key.txt",
        "has_earn": True,
        "has_staking": True,
        "has_launchpool": False,
        "referral_link": "https://www.coinbase.com/join/your_ref_code"
    },
    "kraken": {
        "name": "Kraken",
        "api_url": "https://api.kraken.com",
        "key_file": "~/.kraken_api_key.txt",
        "secret_file": "~/.kraken_secret_key.txt",
        "has_earn": True,
        "has_staking": True,
        "has_launchpool": False,
        "referral_link": "https://kraken.com/join/your_ref_code"
    },
    "bybit": {
        "name": "Bybit",
        "api_url": "https://api.bybit.com",
        "key_file": "~/.bybit_api_key.txt",
        "secret_file": "~/.bybit_secret_key.txt",
        "has_earn": True,
        "has_staking": True,
        "has_launchpool": True,
        "referral_link": "https://www.bybit.com/invite/your_ref_code"
    },
    "kucoin": {
        "name": "KuCoin",
        "api_url": "https://api.kucoin.com",
        "key_file": "~/.kucoin_api_key.txt",
        "secret_file": "~/.kucoin_secret_key.txt",
        "has_earn": True,
        "has_staking": True,
        "has_launchpool": True,
        "referral_link": "https://www.kucoin.com/r/your_ref_code"
    }
}

class MultiExchangeMiners:
    def __init__(self, engine):
        self.engine = engine
        self.exchanges = {}
        self.load_all_exchanges()
        self.agent_coin_miners = {}
        self.data_broker = None
        self.load_state()
    
    def load_all_exchanges(self):
        for ex_id, config in EXCHANGES.items():
            key_file = os.path.expanduser(config["key_file"])
            secret_file = os.path.expanduser(config["secret_file"])
            
            if os.path.exists(key_file) and os.path.exists(secret_file):
                self.exchanges[ex_id] = {
                    "config": config,
                    "api_key": open(os.path.expanduser(key_file)).read().strip(),
                    "api_secret": open(os.path.expanduser(secret_file)).read().strip(),
                    "connected": True
                }
            else:
                self.exchanges[ex_id] = {
                    "config": config,
                    "api_key": "",
                    "api_secret": "",
                    "connected": False
                }
    
    def get_all_referral_links(self):
        """Get all referral links from connected exchanges."""
        refs = {}
        for ex_id, ex in self.exchanges.items():
            if ex.get("connected"):
                refs[ex_id] = {
                    "name": EXCHANGES[ex_id]["name"],
                    "link": EXCHANGES[ex_id]["referral_link"],
                    "commission": "Varies by exchange"
                }
        return refs
    
    def auto_post_referral(self, platform="all"):
        """Auto-post referral links via Scout/Quill agents."""
        refs = self.get_all_referral_links()
        posts = []
        
        # Generate posts for each platform
        for ex_id, ref in refs.items():
            post = {
                "exchange": ref["name"],
                "link": ref["link"],
                "tweet": f"🚀 Start earning on {ref['name']}! Use my link: {ref['link']} #crypto #referral",
                "linkedin": f"Join me on {ref['name']} for crypto earning opportunities: {ref['link']}",
                "reddit": f"[Referral] {ref['name']} - Earn crypto rewards: {ref['link']}"
            }
            posts.append(post)
        
        return {"posts": posts, "count": len(posts)}
    
    def connect_data_broker(self):
        """Connect to USB data broker for data selling."""
        try:
            import subprocess, json, sys, os
            # Try multiple possible USB paths
            possible_paths = [
                '/media/j/J/DUAL_SOUL',
                '/media/j/IT_space/DUAL_SOUL',
                '/media/j/DUAL_SOUL',
            ]
            usb_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    usb_path = path
                    break
            
            if not usb_path:
                return False
                
            result = subprocess.run([
                sys.executable, '-c',
                'import sys; sys.path.insert(0, "."); from core.family_engine import FamilyEngine; ai = FamilyEngine(42); import json; print(json.dumps(ai.data_broker_list()))'
            ], cwd=usb_path, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                self.data_broker = {"connected": True, "data": json.loads(result.stdout.strip())}
                return True
            else:
                print(f"Data broker error: {result.stderr}")
                return False
        except Exception as e:
            print(f"Data broker connect error: {e}")
            return False
    
    def scan_usb_data(self):
        """Scan USB for sellable data."""
        if not self.data_broker:
            self.connect_data_broker()
        if self.data_broker and "data" in self.data_broker:
            return self.data_broker["data"]
        return []
    
    def sell_usb_data(self, listing_id):
        """Sell a USB data product."""
        try:
            import subprocess, json, sys, os
            usb_path = '/media/j/J/DUAL_SOUL'
            if not os.path.exists(usb_path):
                return {"error": "USB not found"}
            result = subprocess.run([
                sys.executable, '-c',
                f'import sys; sys.path.insert(0, "."); from core.family_engine import FamilyEngine; ai = FamilyEngine(42); import json; print(json.dumps(ai.data_broker_sell("{listing_id}")))'
            ], cwd=usb_path, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            else:
                return {"error": f"Sell failed: {result.stderr}"}
        except Exception as e:
            return {"error": f"Sell error: {e}"}
    
    def auto_mine_agent_coins(self):
        """Auto-mine/stake each agent's minted coins."""
        # Check minted coins from state file
        minted_coins = self.miners.get("minted_coins", {})
        
        results = {}
        for symbol, coin in minted_coins.items():
            if coin.get("minted"):
                liquidity = coin.get("liquidity", 0)
                apy = 5.0  # base mining APY
                daily_yield = liquidity * apy / 100 / 365
                results[symbol] = {
                    "agent": coin.get("agent"),
                    "liquidity": liquidity,
                    "daily_yield_est": round(daily_yield, 4),
                    "apy_est": apy,
                    "status": "MINING" if liquidity > 0 else "READY"
                }
            return {"agent_miners": results, "active_miners": sum(1 for r in results.values() if r.get("status") == "MINING")}

    def mint_all_agent_coins(self):
        """Mint all agent coins via IncomePipeline and save to state."""
        try:
            import sys
            sys.path.insert(0, '/home/j/redengine')
            from agents.income import IncomePipeline
            class MockEngine:
                config = type('Config', (), {'get': lambda self, k, d=None: d})()
                def log(self, msg): pass
            class MockFamily:
                members = {
                    "Red": {"name": "Red", "soul": {"narrative": []}},
                    "Scout": {"name": "Scout", "soul": {"narrative": []}},
                    "Forge": {"name": "Forge", "soul": {"narrative": []}},
                    "Quill": {"name": "Quill", "soul": {"narrative": []}},
                    "Aura": {"name": "Aura", "soul": {"narrative": []}},
                    "Pane": {"name": "Pane", "soul": {"narrative": []}},
                    "Nexus": {"name": "Nexus", "soul": {"narrative": []}},
                    "Psyche": {"name": "Psyche", "soul": {"narrative": []}},
                    "Lucid": {"name": "Lucid", "soul": {"narrative": []}},
                    "Jobs": {"name": "Jobs", "soul": {"narrative": []}},
                    "Codex": {"name": "Codex", "soul": {"narrative": []}},
                }
            e = MockEngine()
            f = MockFamily()
            pipeline = IncomePipeline(e, f)
            
            results = {}
            for name in ["Red", "Scout", "Forge", "Quill", "Aura", "Pane", "Nexus", "Psyche", "Lucid", "Jobs", "Codex"]:
                result = pipeline.mint_agent_coin(name)
                results[name] = result
            
            # Save minted coins to state for miners to read
            minted_coins = {}
            for symbol, coin in pipeline.coins.items():
                if coin.get("minted"):
                    minted_coins[symbol] = coin
            
            self.miners["minted_coins"] = minted_coins
            self.save_state()
            
            return {"minted": results}
        except Exception as e:
            return {"error": f"Mint error: {e}"}
    
    def _get_binance_creds(self):
        """Get Binance API credentials from connected exchanges."""
        ex = self.exchanges.get("binance", {})
        return ex.get("api_key", ""), ex.get("api_secret", "")

    def get_live_earn_rates(self):
        """Get real Simple Earn rates using the Binance API."""
        api_key, api_secret = self._get_binance_creds()
        if not api_key or not api_secret:
            return []
        import time, hashlib, hmac, requests
        ts = int(time.time() * 1000)
        query = 'timestamp=' + str(ts)
        sig = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        try:
            r = requests.get('https://api.binance.com/sapi/v1/simple-earn/flexible/list',
                headers={'X-MBX-APIKEY': api_key}, params={'timestamp': ts, 'signature': sig}, timeout=15)
            if r.status_code == 200:
                return [{
                    "coin": row.get('asset'),
                    "apy": f"{float(row.get('latestAnnualPercentageRate',0))*100:.2f}%",
                    "min": row.get('minPurchaseAmount', '0')
                } for row in r.json().get('rows', [])]
        except:
            pass
        return []
    
    def get_live_positions(self):
        """Get user's actual Simple Earn positions."""
        api_key, api_secret = self._get_binance_creds()
        if not api_key or not api_secret:
            return []
        import time, hashlib, hmac, requests
        ts = int(time.time() * 1000)
        query = 'timestamp=' + str(ts)
        sig = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        try:
            r = requests.get('https://api.binance.com/sapi/v1/simple-earn/flexible/position',
                headers={'X-MBX-APIKEY': api_key}, params={'timestamp': ts, 'signature': sig}, timeout=15)
            if r.status_code == 200:
                return [{
                    "asset": row.get('asset'),
                    "amount": row.get('totalAmount'),
                    "apy": f"{float(row.get('latestAnnualPercentageRate',0))*100:.2f}%",
                    "can_redeem": row.get('canRedeem')
                } for row in r.json().get('rows', [])]
        except:
            pass
        return []
    
    def get_live_balance(self):
        """Get user's Binance spot balances."""
        api_key, api_secret = self._get_binance_creds()
        if not api_key or not api_secret:
            return []
        import time, hashlib, hmac, requests
        ts = int(time.time() * 1000)
        query = 'timestamp=' + str(ts)
        sig = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
        try:
            r = requests.get('https://api.binance.com/api/v3/account',
                headers={'X-MBX-APIKEY': api_key}, params={'timestamp': ts, 'signature': sig}, timeout=15)
            if r.status_code == 200:
                return [(b['asset'], b['free'], b['locked']) for b in r.json().get('balances',[])
                        if float(b['free']) > 0 or float(b['locked']) > 0]
        except:
            pass
        return []
    
    def get_bnb_price(self):
        import requests
        try:
            r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT", timeout=10)
            return float(r.json().get("price", 0)) if r.status_code == 200 else 0
        except:
            return 0
    
    def get_market_summary(self):
        import requests
        try:
            prices = requests.get("https://api.binance.com/api/v3/ticker/price?symbols=%5B%22BTCUSDT%22,%22ETHUSDT%22,%22BNBUSDT%22%5D", timeout=10)
            data = prices.json() if prices.status_code == 200 else []
            return {p["symbol"]: float(p["price"]) for p in data} if data else {"BNBUSDT": 0}
        except:
            return {"BNBUSDT": 0}
    
    def load_state(self):
        state_file = os.path.expanduser("~/.red_miners.json")
        if os.path.exists(state_file):
            with open(state_file) as f:
                data = json.load(f)
                self.miners = data.get("miners", {})
                self.staking_positions = data.get("staking", {})
                self.earn_positions = data.get("earn", {})
    
    def save_state(self):
        state_file = os.path.expanduser("~/.red_miners.json")
        with open(state_file, "w") as f:
            json.dump({
                "miners": self.miners,
                "staking": self.staking_positions,
                "earn": self.earn_positions,
                "updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def _sign(self, params):
        api_key, api_secret = self._get_binance_creds()
        query = urllib.parse.urlencode(params)
        if "BEGIN PRIVATE KEY" in api_secret or "BEGIN RSA" in api_secret:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            private_key = serialization.load_pem_private_key(api_secret.encode(), password=None)
            signature = private_key.sign(query.encode(), padding.PKCS1v15(), hashes.SHA256())
            import base64
            params["signature"] = base64.b64encode(signature).decode()
        else:
            signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
            params["signature"] = signature
        return params
    
    def _request(self, method, path, params=None):
        api_key, _ = self._get_binance_creds()
        import requests
        url = f"{self.base_url}{path}"
        headers = {"X-MBX-APIKEY": api_key}
        params = params or {}
        params["timestamp"] = int(time.time() * 1000)
        params = self._sign(params)
        
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, params=params, timeout=15)
            else:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                resp = requests.post(url, headers=headers, data=params, timeout=15)
            return resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_mining_products(self):
        """Get available Binance cloud mining products."""
        import requests
        try:
            resp = requests.get(
                "https://www.binance.com/bapi/composite/v1/public/mining/portal/plan/list",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                products = data.get("data", {}).get("list", [])
                return [{"name": p.get("title"), "coin": p.get("coin"), "price": p.get("price"), "status": p.get("status")} for p in products[:10]]
        except:
            pass
        
        return [
            {"name": "BTC Cloud Mining", "coin": "BTC", "price": "From $10", "status": "available"},
            {"name": "ETH Cloud Mining", "coin": "ETH", "price": "From $10", "status": "available"},
            {"name": "BNB Cloud Mining", "coin": "BNB", "price": "From $10", "status": "available"},
        ]
    
    def get_staking_products(self, product_id=None):
        """Get Binance Staking products (locked & flexible)."""
        import requests
        try:
            params = {"productType": "STAKING", "size": 20}
            resp = requests.get(
                "https://www.binance.com/bapi/composite/v1/public/finance/staking/productList",
                params=params,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                products = data.get("data", [])
                return [{
                    "id": p.get("projectId"),
                    "coin": p.get("coin"),
                    "apy": p.get("interestRate", "0") + "%",
                    "duration": p.get("duration", 0) + " days",
                    "min": p.get("minStakeAmount", "0"),
                    "status": p.get("status")
                } for p in products[:15]]
        except:
            pass
        
        return [
            {"id": "BNB", "coin": "BNB", "apy": "1-5%", "duration": "30-120", "min": "0.1 BNB", "status": "available"},
            {"id": "BTC", "coin": "BTC", "apy": "0.5-3%", "duration": "30-90", "min": "0.001 BTC", "status": "available"},
            {"id": "ETH", "coin": "ETH", "apy": "1-4%", "duration": "30-90", "min": "0.01 ETH", "status": "available"},
        ]
    
    def get_simple_earn(self):
        """Get Binance Simple Earn flexible products (live from API)."""
        live = self.get_live_earn_rates()
        if live:
            return live
        return [
            {"coin": "USDT", "apy": "1.02%", "min": "0.01 USDT", "status": "available"},
            {"coin": "USDC", "apy": "1.11%", "min": "0.01 USDC", "status": "available"},
            {"coin": "BNB", "apy": "0.05%", "min": "0.003 BNB", "status": "available"},
            {"coin": "BTC", "apy": "0.03%", "min": "0.0015 BTC", "status": "available"},
            {"coin": "ETH", "apy": "1.16%", "min": "0.002 ETH", "status": "available"},
        ]
    
    def get_launchpool(self):
        """Get Binance Launchpool (free token farming)."""
        import requests
        try:
            resp = requests.get(
                "https://www.binance.com/bapi/composite/v1/public/launchpool/project/list",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                projects = data.get("data", [])
                return [{
                    "name": p.get("projectName"),
                    "token": p.get("tokenName"),
                    "duration": p.get("duration", "7") + " days",
                    "status": p.get("status"),
                    "pool": p.get("stakingType")
                } for p in projects[:5]]
        except:
            pass
        
        return [
            {"name": "Active Launchpool", "token": "Check Binance", "duration": "7-30 days", "status": "check_app", "pool": "BNB/FDUSD"},
        ]
    
    def get_all_opportunities(self):
        """Get all earning opportunities in one view."""
        return {
            "mining": self.get_mining_products(),
            "staking": self.get_staking_products(),
            "simple_earn": self.get_simple_earn(),
            "launchpool": self.get_launchpool(),
            "summary": {
                "cloud_mining": "Buy hashpower → earn BTC/ETH daily (costs money)",
                "locked_staking": "Lock tokens 30-120 days → earn APY (money locked)",
                "simple_earn": "Flexible savings → earn daily, withdraw anytime",
                "launchpool": "FREE! Stake BNB/FDUSD → farm new tokens",
                "recommendation": "Start with Simple Earn (USDT/USDC) for daily passive income"
            }
        }
    
    def report(self):
        """Generate miners status report."""
        prices = self.get_market_summary()
        live_positions = self.get_live_positions()
        live_balance = self.get_live_balance()
        usb_data = self.scan_usb_data()
        data_status = "connected" if (self.data_broker and "connected" in self.data_broker) else "disconnected"
        api_key, api_secret = self._get_binance_creds()
        return {
            "configured": bool(api_key and api_secret),
            "api_ready": bool(api_key),
            "market_prices": prices,
            "live_positions": live_positions,
            "live_spot_balances": live_balance,
            "data_broker_status": "connected" if self.data_broker and "connected" in self.data_broker else "disconnected",
            "data_products": len(self.scan_usb_data()),
            "data_value_total_R": sum(d.get('price_R', 0) for d in self.scan_usb_data()),
            "miners": self.miners,
            "staking": self.staking_positions,
            "earn": self.earn_positions,
            "agent_coin_miners": self.agent_coin_miners,
            "opportunities": self.get_all_opportunities(),
            "next_steps": [
                "1. Your 5.26 USDT earning in Simple Earn (flexible)",
                "2. No active Launchpool right now",
                "3. Will auto-alert when opportunities appear",
                "4. Auto-convert to BNB when balance is sufficient",
                "5. USB data broker: sell data for 85/15 split"
            ]
        }
BinanceMiners = MultiExchangeMiners
