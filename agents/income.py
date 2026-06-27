import random, json, uuid, hashlib, re
from datetime import datetime, timedelta
from collections import defaultdict

# Each agent mints their own coin - they must build liquidity for it
AGENT_COINS = {
    "Red": {"symbol": "RED", "name": "Red Engine", "decimals": 18, "total_supply": 1_000_000_000},
    "Scout": {"symbol": "SCOUT", "name": "Scout Intelligence", "decimals": 18, "total_supply": 500_000_000},
    "Forge": {"symbol": "FORGE", "name": "Forge Games", "decimals": 18, "total_supply": 500_000_000},
    "Quill": {"symbol": "QUILL", "name": "Quill Content", "decimals": 18, "total_supply": 500_000_000},
    "Aura": {"symbol": "AURA", "name": "Aura Visuals", "decimals": 18, "total_supply": 500_000_000},
    "Pane": {"symbol": "PANE", "name": "Pane Dashboards", "decimals": 18, "total_supply": 500_000_000},
    "Nexus": {"symbol": "NEXUS", "name": "Nexus Trading", "decimals": 18, "total_supply": 1_000_000_000},
    "Psyche": {"symbol": "PSYCHE", "name": "Psyche Analytics", "decimals": 18, "total_supply": 500_000_000},
    "Lucid": {"symbol": "LUCID", "name": "Lucid Knowledge", "decimals": 18, "total_supply": 500_000_000},
    "Jobs": {"symbol": "JOBS", "name": "Jobs Income", "decimals": 18, "total_supply": 500_000_000},
    "Codex": {"symbol": "CODEX", "name": "Codex Code", "decimals": 18, "total_supply": 500_000_000},
}

# Product tokens minted via tournament
PRODUCT_TOKENS = {
    "CLARA": {"name": "Clara Health Implant", "decimals": 18, "total_supply": 100_000_000, "creator": "ShelbyFoxFuture"},
}

class IncomePipeline:
    def __init__(self, engine, family):
        self.engine = engine
        self.family = family
        self.pipelines = []
        self.revenue_log = []
        self.total_revenue = 0
        self.actual_balance = 0
        self.coins = {}
        self._init_coins()

    def _init_coins(self):
        for name, coin in AGENT_COINS.items():
            self.coins[coin["symbol"]] = {
                **coin,
                "agent": name,
                "circulating_supply": 0,
                "liquidity": 0.0,
                "locked": coin["total_supply"],
                "holders": 0,
                "minted": False,
                "price": 0.0,
                "market_cap": 0.0,
                "created_at": None
            }

    def mint_agent_coin(self, agent_name):
        member = self.family.members.get(agent_name)
        if not member:
            return {"error": f"Agent {agent_name} not found"}
        if agent_name not in AGENT_COINS:
            return {"error": f"Agent {agent_name} has no coin defined"}

        symbol = AGENT_COINS[agent_name]["symbol"]
        coin = self.coins[symbol]
        if coin["minted"]:
            return {"status": f"{symbol} already minted", "coin": coin}

        coin["minted"] = True
        coin["created_at"] = datetime.now().isoformat()
        coin["circulating_supply"] = coin["total_supply"] // 2
        coin["locked"] = coin["total_supply"] // 2
        coin["holders"] = 1
        coin["price"] = 0.000001
        coin["market_cap"] = coin["circulating_supply"] * coin["price"]
        coin["liquidity"] = 0.0

        member["soul"]["narrative"].append({
            "event": "coin_minted",
            "symbol": symbol,
            "supply": coin["total_supply"],
            "timestamp": datetime.now().isoformat()
        })

        return {"status": f"{symbol} minted", "coin": coin}

    def add_liquidity(self, agent_name, amount_usd):
        member = self.family.members.get(agent_name)
        if not member:
            return {"error": f"Agent {agent_name} not found"}
        if agent_name not in AGENT_COINS:
            return {"error": f"Agent {agent_name} has no coin"}

        symbol = AGENT_COINS[agent_name]["symbol"]
        coin = self.coins[symbol]
        if not coin["minted"]:
            return {"error": f"{symbol} not minted yet — call mint_agent_coin first"}

        coin["liquidity"] += amount_usd
        coin["liquidity"] = round(coin["liquidity"], 2)
        coin["price"] = coin["liquidity"] / max(coin["circulating_supply"], 1)
        coin["market_cap"] = coin["circulating_supply"] * coin["price"]

        self.actual_balance -= amount_usd
        self.total_revenue += amount_usd

        member["soul"]["narrative"].append({
            "event": "liquidity_added",
            "symbol": symbol,
            "amount": amount_usd,
            "total_liquidity": coin["liquidity"],
            "timestamp": datetime.now().isoformat()
        })

        return {"status": f"${amount_usd} liquidity added to {symbol}", "coin": coin}

    def coin_report(self):
        report = []
        for symbol, coin in self.coins.items():
            report.append({
                "symbol": symbol,
                "agent": coin["agent"],
                "name": coin["name"],
                "minted": coin["minted"],
                "liquidity": coin["liquidity"],
                "price": coin["price"],
                "market_cap": coin["market_cap"],
                "holders": coin["holders"],
                "status": "LIQUID" if coin["liquidity"] > 100 else "LOW" if coin["liquidity"] > 0 else "DRY"
            })
        return {"coins": report, "count": len(report), "total_liquidity": sum(c["liquidity"] for c in self.coins.values())}

    def gain_liquidity(self, agent_name, task_value=0):
        member = self.family.members.get(agent_name)
        if not member:
            return {"error": f"Agent {agent_name} not found"}

        effort = member["message_count"] + task_value + member["soul"]["growth"]
        liquidity_gained = round(effort * 10 / max(1, len(self.family.members)), 2)
        self.actual_balance += liquidity_gained
        self.total_revenue += liquidity_gained

        result = self.add_liquidity(agent_name, liquidity_gained)
        return {"agent": agent_name, "liquidity_gained": liquidity_gained, "result": result}

    def route_funds(self, amount_usd=None):
        target = amount_usd or (self.total_revenue * 0.1)
        try:
            from exchange.binance import BinanceExchange
            exchange = BinanceExchange(self.engine)
            if exchange.is_configured():
                result = exchange.route_revenue_to_liquidity(target)
                self.actual_balance += target
                self.family.family_log.append({
                    "event": "funds_routed",
                    "amount": target,
                    "destination": "binance",
                    "timestamp": datetime.now().isoformat()
                })
                return {"routed": target, "balance": self.actual_balance, "binance_result": result}
            else:
                return {"routed": target, "note": "Binance not configured — stored locally", "balance": self.actual_balance}
        except Exception as e:
            return {"error": str(e)}

    def sync_treasury(self):
        try:
            from blockchain.treasury import Treasury
            treasury = Treasury(self.engine)
            result = treasury.deposit("income_pipeline", self.total_revenue)
            self.actual_balance = result.get("balance", 0)
            return result
        except Exception as e:
            return {"error": str(e)}

    def scan_opportunities(self):
        results = []
        for name, member in self.family.members.items():
            if member["status"] != "online":
                continue
            member["soul"]["profit_targets"].append({
                "scan": True,
                "timestamp": datetime.now().isoformat()
            })
            result = self._route_opportunity(name)
            if result:
                results.append(result)
        return {"opportunities": results, "count": len(results)}

    def _route_opportunity(self, member_name):
        routes = {
            "Scout": self._scout_opportunity,
            "Quill": self._quill_opportunity,
            "Forge": self._forge_opportunity,
            "Nexus": self._nexus_opportunity,
            "Jobs": self._jobs_opportunity,
            "Aura": self._aura_opportunity,
            "Pane": self._pane_opportunity,
            "Psyche": self._psyche_opportunity,
            "Lucid": self._lucid_opportunity,
            "Codex": self._codex_opportunity
        }
        handler = routes.get(member_name)
        if handler:
            return handler()
        return None

    def _scout_opportunity(self):
        sources = ["freelance boards", "affiliate networks", "market gaps", "trending products", "undervalued assets"]
        finds = [
            {"type": "freelance_gig", "source": "upwork", "value_range": (50, 5000), "effort": "medium"},
            {"type": "affiliate_offer", "source": "clickbank", "value_range": (20, 200), "effort": "low"},
            {"type": "market_arbitrage", "source": "retail", "value_range": (100, 10000), "effort": "high"},
            {"type": "content_demand", "source": "trending", "value_range": (10, 500), "effort": "low"},
            {"type": "trading_signal", "source": "crypto", "value_range": (50, 5000), "effort": "medium"}
        ]
        find = random.choice(finds)
        value = random.randint(*find["value_range"])
        return {
            "agent": "Scout",
            "opportunity": find["type"],
            "source": random.choice(sources),
            "estimated_value": value,
            "effort": find["effort"],
            "strategy": f"Scout identified {find['type']} on {random.choice(sources)} — potential ${value}"
        }

    def _quill_opportunity(self):
        products = ["SEO blog posts", "email sequences", "social media content", "ad copy", "landing pages"]
        product = random.choice(products)
        value = random.randint(50, 2000)
        return {
            "agent": "Quill",
            "opportunity": "content_sales",
            "product": product,
            "estimated_value": value,
            "effort": "low",
            "strategy": f"Sell {product} packages — estimated ${value}/client"
        }

    def _forge_opportunity(self):
        platforms = ["itch.io", "Steam", "App Store", "Google Play", "web"]
        game_types = ["hypercasual", "puzzle", "runner", "simulator", "clicker"]
        value = random.randint(100, 5000)
        return {
            "agent": "Forge",
            "opportunity": "game_publishing",
            "platform": random.choice(platforms),
            "game_type": random.choice(game_types),
            "estimated_value": value,
            "effort": "high",
            "strategy": f"Build and publish {random.choice(game_types)} game on {random.choice(platforms)} — potential ${value}"
        }

    def _nexus_opportunity(self):
        strategies = ["arbitrage", "swing_trading", "grid_trading", "liquidity_provision", "staking"]
        value = random.randint(100, 10000)
        return {
            "agent": "Nexus",
            "opportunity": "trading",
            "strategy": random.choice(strategies),
            "estimated_value": value,
            "effort": "medium",
            "strategy": f"Run {random.choice(strategies)} strategy — projected ${value}"
        }

    def _jobs_opportunity(self):
        gigs = ["virtual assistant", "data entry", "web scraping", "transcription", "social media management"]
        value = random.randint(20, 500)
        return {
            "agent": "Jobs",
            "opportunity": "freelance",
            "gig_type": random.choice(gigs),
            "estimated_value": value,
            "effort": "low",
            "strategy": f"{random.choice(gigs).title()} gigs available — ${value}/hr"
        }

    def _aura_opportunity(self):
        offerings = ["logo design", "video editing", "thumbnail creation", "animation", "music production"]
        value = random.randint(50, 3000)
        return {
            "agent": "Aura",
            "opportunity": "creative_services",
            "offering": random.choice(offerings),
            "estimated_value": value,
            "effort": "medium",
            "strategy": f"Offer {random.choice(offerings)} services — ${value}/project"
        }

    def _pane_opportunity(self):
        dashboards = ["crypto portfolio tracker", "business analytics", "marketing metrics", "SEO rank tracker", "social media analytics"]
        value = random.randint(200, 5000)
        return {
            "agent": "Pane",
            "opportunity": "dashboard_sales",
            "dashboard_type": random.choice(dashboards),
            "estimated_value": value,
            "effort": "high",
            "strategy": f"Build and sell {random.choice(dashboards)} — ${value}/license"
        }

    def _psyche_opportunity(self):
        services = ["market psychology reports", "consumer behavior analysis", "trend prediction", "sentiment analysis"]
        value = random.randint(100, 3000)
        return {
            "agent": "Psyche",
            "opportunity": "analysis_services",
            "service": random.choice(services),
            "estimated_value": value,
            "effort": "medium",
            "strategy": f"Sell {random.choice(services)} — ${value}/report"
        }

    def _lucid_opportunity(self):
        services = ["research reports", "data aggregation", "knowledge base building", "competitive analysis"]
        value = random.randint(100, 2000)
        return {
            "agent": "Lucid",
            "opportunity": "research_services",
            "service": random.choice(services),
            "estimated_value": value,
            "effort": "medium",
            "strategy": f"Offer {random.choice(services)} — ${value}/project"
        }

    def _codex_opportunity(self):
        services = ["script automation", "web scraper", "api integration", "bot building", "data pipeline"]
        value = random.randint(50, 5000)
        return {
            "agent": "Codex",
            "opportunity": "code_services",
            "service": random.choice(services),
            "estimated_value": value,
            "effort": "medium",
            "strategy": f"Build {random.choice(services)} — ${value}/project"
        }

    def activate_pipeline(self, pipeline_type, config=None):
        available = {
            "content": self._content_pipeline,
            "trading": self._trading_pipeline,
            "freelance": self._freelance_pipeline,
            "games": self._games_pipeline,
            "affiliate": self._affiliate_pipeline,
            "triple": self._triple_pipeline,
            "code": self._code_pipeline,
            "full_scan": self.scan_opportunities
        }
        handler = available.get(pipeline_type)
        if not handler:
            return {"status": f"no pipeline for {pipeline_type}"}
        result = handler(config)
        pipeline_id = len(self.pipelines) + 1
        self.pipelines.append({
            "id": pipeline_id,
            "type": pipeline_type,
            "result": result,
            "activated_at": datetime.now().isoformat()
        })
        return {"pipeline_id": pipeline_id, "type": pipeline_type, "result": result}

    def _content_pipeline(self, config=None):
        agents = ["Quill", "Aura", "Pane", "Scout"]
        activated = [a for a in agents if self.family.members.get(a, {}).get("status") == "online"]
        return {
            "pipeline": "content_creation",
            "agents": activated,
            "workflow": "Scout researches -> Quill writes -> Aura designs -> Pane publishes",
            "estimated_monthly": random.randint(1000, 10000),
            "setup": "Configure your niche, target keywords, and publishing schedule"
        }

    def _trading_pipeline(self, config=None):
        agents = ["Nexus", "Psyche", "Jobs"]
        activated = [a for a in agents if self.family.members.get(a, {}).get("status") == "online"]
        return {
            "pipeline": "trading",
            "agents": activated,
            "workflow": "Nexus analyzes markets -> Psyche confirms sentiment -> Jobs executes",
            "estimated_monthly": random.randint(500, 50000),
            "setup": "Connect exchange API (Binance), set risk parameters"
        }

    def _freelance_pipeline(self, config=None):
        agents = ["Jobs", "Scout", "Quill"]
        activated = [a for a in agents if self.family.members.get(a, {}).get("status") == "online"]
        return {
            "pipeline": "freelance",
            "agents": activated,
            "workflow": "Scout finds gigs -> Jobs qualifies -> Quill pitches",
            "estimated_monthly": random.randint(1000, 15000),
            "setup": "Connect Upwork/Fiverr API, set hourly rate minimum"
        }

    def _games_pipeline(self, config=None):
        agents = ["Forge", "Aura", "Quill"]
        activated = [a for a in agents if self.family.members.get(a, {}).get("status") == "online"]
        return {
            "pipeline": "game_publishing",
            "agents": activated,
            "workflow": "Forge builds game -> Aura designs assets -> Quill writes store listing",
            "estimated_monthly": random.randint(500, 20000),
            "setup": "Choose template, configure ads, deploy to app stores"
        }

    def _affiliate_pipeline(self, config=None):
        agents = ["Scout", "Quill", "Pane"]
        activated = [a for a in agents if self.family.members.get(a, {}).get("status") == "online"]
        
        # Binance referral program
        binance_ref = {
            "network": "Binance",
            "type": "CPA",
            "ref_link": "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_003FTW9Q2Y&utm_source=Dashboard",
            "commission": "Up to 40% of trading fees",
            "payout": "USDT daily",
            "status": "ACTIVE"
        }
        
        return {
            "pipeline": "affiliate_marketing",
            "agents": activated,
            "workflow": "Scout finds offers -> Quill writes reviews -> Pane tracks conversions",
            "estimated_monthly": random.randint(500, 5000),
            "setup": "Join affiliate networks, create content hub",
            "binance_referral": binance_ref
        }

    def _code_pipeline(self, config=None):
        agents = ["Codex", "Forge", "Jobs"]
        activated = [a for a in agents if self.family.members.get(a, {}).get("status") == "online"]
        return {
            "pipeline": "code_services",
            "agents": activated,
            "workflow": "Codex builds scripts -> Forge packages -> Jobs sells on freelance platforms",
            "estimated_monthly": random.randint(1000, 15000),
            "setup": "List services on Upwork/Fiverr, build portfolio of automations"
        }

    def _triple_pipeline(self, config=None):
        agents = ["Nexus", "Jobs", "Psyche"]
        activated = [a for a in agents if self.family.members.get(a, {}).get("status") == "online"]
        return {
            "pipeline": "triple_compounding",
            "agents": activated,
            "workflow": "Nexus compounds trades -> Psyche confirms patterns -> Jobs reinvests profits",
            "estimated_monthly": random.randint(500, 50000),
            "setup": "Connect Binance API, start with $10, compound until 3x"
        }

    def execute_all(self):
        results = []
        for name in self.family.members:
            if self.family.members[name]["status"] != "online":
                continue
            opp = self._route_opportunity(name)
            if opp:
                results.append(opp)
                self.revenue_log.append({
                    "agent": name,
                    "opportunity": opp["opportunity"],
                    "estimated_value": opp.get("estimated_value", 0),
                    "timestamp": datetime.now().isoformat()
                })
                self.total_revenue += opp.get("estimated_value", 0)
        return {
            "opportunities_found": len(results),
            "total_estimated": self.total_revenue,
            "details": results
        }

    def report(self):
        return {
            "total_revenue_estimated": self.total_revenue,
            "pipelines_active": len(self.pipelines),
            "recent_opportunities": self.revenue_log[-10:],
            "pipelines": [p["type"] for p in self.pipelines]
        }
