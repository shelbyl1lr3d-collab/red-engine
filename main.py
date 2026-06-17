#!/usr/bin/env python3
"""
Red Engine V2 — Full-Stack AI Gaming, Tokenomics & Vessel Ecosystem
========================================================================
Commands:
  status              — System status and AI family overview
  reskin [theme]      — Generate a reskinned game from template
  forge [count]       — Batch-generate N games
  deploy              — Deploy games to GitHub Pages / Netlify
  mint <name>         — Mint a new crypto token
  tokens_list         — List all minted tokens
  treasury_report     — Treasury compounding report
  liquidity_report    — Liquidity pool summary
  balance [exchange]  — Check Luno / Binance / treasury balance
  route_revenue       — Simulate revenue routing through the pipeline
  tournament          — Run a single tournament round
  tournament_leaderboard — Show tournament leaderboard
  tournament_start [interval_s] — Start auto tournament
  tournament_stop     — Stop auto tournament
  chat <member> <msg> — Chat with an AI family member
  search <query>      — Search the web
  trade <symbol> <side> <amount> — Execute a trade
  weekly              — Full weekly system report
  milestone_check     — Check $1B milestone progress
  scan_all [category] — Scan jobs/promos/bonuses/opportunities
  jobs <category>     — Search for income opportunities
  science <topic>     — Science & technology discoveries
  media_test          — Test music video generation
  media_stats         — YouTube channel stats
  notifications       — View system notifications
  log                 — View transaction log
  generate_contract <symbol> — Generate Solidity contract for a token
  help                — This help message
"""
import os, sys, json, time, random, urllib.parse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Load .env if exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

from core import RedEngine, Config
from factory import ReskinEngine
from deploy import GitHubDeployer, NetlifyDeployer
from blockchain import TokenEngine, Treasury, LiquidityPool
from exchange import BinanceExchange, RevenueRouter
from tournament import TournamentArena
from media import YouTubeEngine, MusicVideoGenerator
from gateway import SafetyGateway
from agents import AgentFamily

# Import new modules
sys.path.insert(0, os.path.dirname(__file__))
from lead_finder import LeadFinder
from affiliate_updater import AffiliateUpdater
from game_cloner import GameCloner
from config_vault import ConfigVault
from scheduler import MonthlyScheduler
from gui import RedEngineGUI

engine = RedEngine()

def init_all():
    engine.register("agents", AgentFamily(engine))
    engine.register("factory", ReskinEngine(engine))
    engine.register("deploy_github", GitHubDeployer(engine))
    engine.register("deploy_netlify", NetlifyDeployer(engine))
    engine.register("tokens", TokenEngine(engine))
    engine.register("treasury", Treasury(engine))
    engine.register("liquidity", LiquidityPool(engine))
    engine.register("exchange", BinanceExchange(engine))
    engine.register("router", RevenueRouter(engine))
    engine.register("tournament", TournamentArena(engine))
    engine.register("youtube", YouTubeEngine(engine))
    engine.register("music_video", MusicVideoGenerator(engine))
    engine.register("gateway", SafetyGateway(engine))
    
    # Register new modules
    engine.register("lead_finder", LeadFinder(engine))
    engine.register("affiliate_updater", AffiliateUpdater(engine))
    engine.register("game_cloner", GameCloner(engine))
    engine.register("config_vault", ConfigVault(engine))
    engine.register("scheduler", MonthlyScheduler(engine))

# ── SYSTEM ──────────────────────────────────────────────────────

def cmd_status(args=None):
    agents = engine.get("agents")
    treasury = engine.get("treasury")
    tokens = engine.get("tokens")
    tournament = engine.get("tournament")
    return json.dumps({
        "engine_version": engine.config.get("version"),
        "vision": engine.config.get("vision"),
        "goal": engine.config.get("goal_usd"),
        "family": agents.get_status() if agents else {},
        "treasury": treasury.report() if treasury else {},
        "tokens": tokens.summary() if tokens else {},
        "tournament": tournament.summary() if tournament else {},
        "modules_loaded": list(engine._modules.keys())
    }, indent=2)

def cmd_weekly(args=None):
    treasury = engine.get("treasury")
    tokens = engine.get("tokens")
    agents = engine.get("agents")
    tournament = engine.get("tournament")
    return json.dumps({
        "report_date": time.strftime("%Y-%m-%d"),
        "treasury": treasury.report() if treasury else {},
        "tokens": tokens.summary() if tokens else {},
        "family": agents.get_status() if agents else {},
        "tournament": tournament.summary() if tournament else {},
        "system": engine.status
    }, indent=2)

def cmd_milestone(args=None):
    gateway = engine.get("gateway")
    treasury = engine.get("treasury")
    if not gateway or not treasury:
        return "Gateway or treasury not loaded"
    return json.dumps(gateway.check_milestone(treasury.report()["balance"]), indent=2)

def cmd_help(args=None):
    return __doc__

# ── NEW MODULES ──────────────────────────────────────────────────

def cmd_lead_finder(args):
    lead_finder = engine.get("lead_finder")
    if not lead_finder:
        return json.dumps({"error": "Lead finder module not loaded"})
    
    query = " ".join(args) if args else "Looking for music animator or crypto developer"
    category = "all"
    
    result = lead_finder.search_jobs(query, category)
    return json.dumps(result, indent=2)

def cmd_affiliate_update(args):
    affiliate_updater = engine.get("affiliate_updater")
    if not affiliate_updater:
        return json.dumps({"error": "Affiliate updater module not loaded"})
    
    # Get links from config or use default
    links = {
        "Product A": "https://example.com/product-a",
        "Product B": "https://example.com/product-b",
        "Product C": "https://example.com/product-c"
    }
    
    result = affiliate_updater.update_monthly_landing_page(links)
    return json.dumps(result, indent=2)

def cmd_game_clone(args):
    game_cloner = engine.get("game_cloner")
    if not game_cloner:
        return json.dumps({"error": "Game cloner module not loaded"})
    
    # Use default parameters if not provided
    template_repo = args[0] if len(args) > 0 else "https://github.com/example/clean-flappy-bird-template"
    game_name = args[1] if len(args) > 1 else "Flappy_Jessica_Rabbit"
    
    result = game_cloner.clone_and_retheme_game(
        template_repo, game_name, 
        "my_assets/j_rabbit_sprite.png", 
        "my_assets/cigar_bar_bg.png"
    )
    return json.dumps(result, indent=2)

def cmd_config_vault(args):
    config_vault = engine.get("config_vault")
    if not config_vault:
        return json.dumps({"error": "Config vault module not loaded"})
    
    if not args:
        return json.dumps({"error": "Usage: config_vault [list|get <key>|add <key> <value> <category> <description>]"})
    
    command = args[0]
    
    if command == "list":
        category = args[1] if len(args) > 1 else None
        result = config_vault.list_keys(category)
        return json.dumps(result, indent=2)
    
    elif command == "get":
        if len(args) < 2:
            return json.dumps({"error": "Usage: config_vault get <key>"})
        key = args[1]
        value = config_vault.get_key(key)
        if value:
            return json.dumps({"key": key, "value": value})
        else:
            return json.dumps({"error": f"Key '{key}' not found"})
    
    elif command == "add":
        if len(args) < 5:
            return json.dumps({"error": "Usage: config_vault add <key> <value> <category> <description>"})
        key = args[1]
        value = args[2]
        category = args[3]
        description = args[4]
        
        result = config_vault.add_key(key, value, description, category)
        return json.dumps(result, indent=2)
    
    elif command == "highlighted":
        result = config_vault.get_highlighted_keys()
        return json.dumps(result, indent=2)
    
    else:
        return json.dumps({"error": f"Unknown config_vault command: {command}"})

def cmd_scheduler(args):
    scheduler = engine.get("scheduler")
    if not scheduler:
        return json.dumps({"error": "Scheduler module not loaded"})
    
    if not args:
        result = scheduler.get_status()
        return json.dumps(result, indent=2)
    
    command = args[0]
    
    if command == "status":
        result = scheduler.get_status()
        return json.dumps(result, indent=2)
    
    elif command == "monthly":
        result = scheduler.run_monthly_tasks()
        return json.dumps(result, indent=2)
    
    elif command == "weekly":
        result = scheduler.run_weekly_tasks()
        return json.dumps(result, indent=2)
    
    elif command == "daily":
        result = scheduler.run_daily_tasks()
        return json.dumps(result, indent=2)
    
    elif command == "add":
        if len(args) < 5:
            return json.dumps({"error": "Usage: scheduler add <name> <type> <parameters>"})
        name = args[1]
        task_type = args[2]
        import json as json_module
        try:
            parameters = json_module.loads(" ".join(args[3:]))
        except:
            return json.dumps({"error": "Invalid parameters JSON"})
        
        result = scheduler.add_task(name, task_type, parameters)
        return json.dumps(result, indent=2)
    
    else:
        return json.dumps({"error": f"Unknown scheduler command: {command}"})

def cmd_gui(args=None):
    """Launch the GUI interface."""
    try:
        gui = RedEngineGUI(engine)
        gui.run()
        return json.dumps({"status": "GUI launched"})
    except Exception as e:
        return json.dumps({"error": f"Failed to launch GUI: {str(e)}"})

# ── GAME FACTORY ───────────────────────────────────────────────

def cmd_reskin(args):
    factory = engine.get("factory")
    if not factory:
        return json.dumps({"error": "Factory module not loaded"})
    theme_name = args[0] if args else None
    result = factory.reskin(theme_name=theme_name)
    return json.dumps(result, indent=2)

def cmd_forge(args):
    factory = engine.get("factory")
    if not factory:
        return json.dumps({"error": "Factory not loaded"})
    template_name = None
    count = 1
    if args:
        if args[0].isdigit():
            count = int(args[0])
        else:
            template_name = args[0]
    if count > 1:
        results = factory.batch_reskin(count)
        return json.dumps({"generated": len(results), "games": results}, indent=2)
    result = factory.reskin(template_name=template_name)
    return json.dumps(result, indent=2)

def cmd_deploy(args):
    gh = engine.get("deploy_github")
    nl = engine.get("deploy_netlify")
    builds_dir = os.path.join(os.path.dirname(__file__), "builds")
    if not os.path.exists(builds_dir):
        return json.dumps({"error": "No builds found. Run 'reskin' or 'forge' first."})

    games = [d for d in os.listdir(builds_dir)
             if os.path.isdir(os.path.join(builds_dir, d)) and d != "assets"]
    if not games:
        return json.dumps({"error": "No game builds to deploy."})

    results = []
    for game_name in games:
        game_dir = os.path.join(builds_dir, game_name)
        entry = {"game": game_name}
        if gh and gh.is_configured():
            r = gh.deploy_game(game_name, game_dir)
            entry["github"] = r
        else:
            entry["github"] = "skipped (no GITHUB_TOKEN)"
        if nl and nl.is_configured():
            r = nl.deploy(game_dir, game_name)
            entry["netlify"] = r
        else:
            entry["netlify"] = "skipped (no NETLIFY_AUTH_TOKEN)"
        results.append(entry)

    return json.dumps({"deployed": len(results), "games": results}, indent=2)

# ── TOKENS & BLOCKCHAIN ────────────────────────────────────────

def cmd_mint(args):
    tokens = engine.get("tokens")
    if not tokens:
        return json.dumps({"error": "Token engine not loaded"})
    name = " ".join(args) if args else "Red Coin V2"
    result = tokens.mint(name)
    return json.dumps(result, indent=2)

def cmd_tokens_list(args=None):
    tokens = engine.get("tokens")
    if not tokens:
        return json.dumps({"error": "Token engine not loaded"})
    return json.dumps(tokens.summary(), indent=2)

def cmd_treasury_report(args=None):
    treasury = engine.get("treasury")
    if not treasury:
        return json.dumps({"error": "Treasury not loaded"})
    t = treasury.report()
    # Also compound yield
    t["compounded"] = treasury.compound(rate_apr=5.0)
    return json.dumps(t, indent=2)

def cmd_liquidity_report(args=None):
    liq = engine.get("liquidity")
    if not liq:
        return json.dumps({"error": "Liquidity module not loaded"})
    return json.dumps(liq.get_pools(), indent=2)

def cmd_generate_contract(args):
    tokens = engine.get("tokens")
    if not tokens:
        return json.dumps({"error": "Token engine not loaded"})
    symbol = args[0] if args else ""
    if not symbol:
        return json.dumps({"error": "Usage: generate_contract <SYMBOL>"})
    t = tokens.get(symbol)
    if not t:
        return json.dumps({"error": f"Token '{symbol}' not found"})
    contract = tokens.generate_smart_contract(t)
    return json.dumps(contract, indent=2)

# ── EXCHANGE / BALANCE / TRADE ─────────────────────────────────

def _check_luno_balance():
    """Check Luno exchange balance via REST API."""
    key = os.getenv("LUNO_API_KEY_ID", "")
    secret = os.getenv("LUNO_API_KEY_SECRET", "")
    if not key or not secret:
        return None
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        resp = requests.get(
            "https://api.luno.com/api/1/balance",
            auth=HTTPBasicAuth(key, secret),
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            balances = []
            for b in data.get("balance", []):
                amt = float(b.get("balance", 0))
                if amt > 0:
                    balances.append({
                        "asset": b["asset"],
                        "balance": amt,
                        "reserved": float(b.get("reserved", 0)),
                        "available": float(b.get("balance", 0)) - float(b.get("reserved", 0))
                    })
            return {"exchange": "Luno", "balances": balances}
        else:
            return {"exchange": "Luno", "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except Exception as e:
        return {"exchange": "Luno", "error": str(e)}

def cmd_balance(args):
    exchange_name = args[0].lower() if args else "luno"
    exchange = engine.get("exchange")
    treasury = engine.get("treasury")

    result = {"exchange": exchange_name}

    if exchange_name == "luno":
        luno = _check_luno_balance()
        if luno:
            result["balance"] = luno
        else:
            result["balance"] = "Luno not configured (set LUNO_API_KEY_ID/SECRET)"
    elif exchange_name == "binance" and exchange and exchange.is_configured():
        bal = exchange.get_asset_balance()
        result["balance"] = bal
    elif exchange_name == "treasury" and treasury:
        tr = treasury.report()
        result["balance"] = {"balance": tr["balance"], "yield": tr.get("yield_earned", 0)}
    else:
        # Show all available
        result["balance"] = {}
        luno = _check_luno_balance()
        if luno:
            result["balance"]["luno"] = luno
        if treasury:
            tr = treasury.report()
            result["balance"]["treasury"] = {"balance": tr["balance"], "yield": tr.get("yield_earned", 0)}
        if not result["balance"]:
            result["balance"]["note"] = "No exchanges configured. Set LUNO or BINANCE API keys."

    return json.dumps(result, indent=2)

def cmd_trade(args):
    exchange_name = args[0].lower() if len(args) > 0 else "luno"
    symbol = args[1].upper() if len(args) > 1 else "XBTZAR"
    side = args[2].upper() if len(args) > 2 else "BUY"
    amount = float(args[3]) if len(args) > 3 else 10.0

    if exchange_name == "luno":
        key = os.getenv("LUNO_API_KEY_ID", "")
        secret = os.getenv("LUNO_API_KEY_SECRET", "")
        if not key or not secret:
            return json.dumps({"error": "Luno not configured. Set LUNO_API_KEY_ID/SECRET"})
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            pair = symbol
            if not pair.endswith("ZAR") and not pair.endswith("USDT"):
                pair = f"{pair}ZAR"
            params = {
                "pair": pair,
                "type": side.upper(),
                "volume": str(amount),
            }
            resp = requests.post(
                "https://api.luno.com/api/1/marketorder",
                auth=HTTPBasicAuth(key, secret),
                data=params,
                timeout=15
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                return json.dumps({
                    "exchange": "Luno",
                    "order": data.get("order_id", "pending"),
                    "pair": pair,
                    "side": side,
                    "volume": amount,
                    "status": "placed"
                }, indent=2)
            return json.dumps({"error": f"Luno trade failed: {resp.status_code} - {resp.text[:200]}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif exchange_name == "binance":
        exchange = engine.get("exchange")
        if not exchange or not exchange.is_configured():
            return json.dumps({"error": "Binance not configured"})
        if side == "BUY":
            r = exchange.market_buy(symbol, amount)
        else:
            r = exchange.market_sell(symbol, amount)
        return json.dumps({"exchange": "Binance", "symbol": symbol, "side": side, "result": r}, indent=2)

    return json.dumps({"error": f"Unknown exchange: {exchange_name}"})

def cmd_route_revenue(args):
    router = engine.get("router")
    if not router:
        return json.dumps({"error": "Router not loaded"})
    source = args[0] if args else "Test Revenue"
    amount = float(args[1]) if len(args) > 1 else 100.0
    result = router.route(source, amount)
    return json.dumps(result, indent=2)

# ── TOURNAMENT ─────────────────────────────────────────────────

def cmd_tournament(args):
    arena = engine.get("tournament")
    if not arena:
        return json.dumps({"error": "Tournament not loaded"})
    result = arena.run_round()
    return json.dumps(result, indent=2)

def cmd_tournament_leaderboard(args=None):
    arena = engine.get("tournament")
    if not arena:
        return json.dumps({"error": "Tournament not loaded"})
    return json.dumps(arena.get_leaderboard(), indent=2)

def cmd_tournament_start(args):
    arena = engine.get("tournament")
    if not arena:
        return json.dumps({"error": "Tournament not loaded"})
    interval = int(args[0]) if args else 300
    return json.dumps(arena.start_auto_tournament(interval), indent=2)

def cmd_tournament_stop(args=None):
    arena = engine.get("tournament")
    if not arena:
        return json.dumps({"error": "Tournament not loaded"})
    return json.dumps(arena.stop_auto_tournament(), indent=2)

# ── CHAT ───────────────────────────────────────────────────────

def cmd_chat(args):
    agents = engine.get("agents")
    if not agents:
        return json.dumps({"error": "Agents not loaded"})
    member = args[0] if args else "Red"
    message = " ".join(args[1:]) if len(args) > 1 else "hello"
    result = agents.chat(member, message)
    return json.dumps(result, indent=2)

# ── WEB SEARCH ─────────────────────────────────────────────────

def _web_search(query, num=5):
    """Search the web using DuckDuckGo (no API key needed)."""
    import requests
    results = []
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading", "Result"),
                    "snippet": data.get("AbstractText", ""),
                    "url": data.get("AbstractURL", "")
                })
        # Also try HTML scraping fallback
        if len(results) < num:
            url2 = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp2 = requests.get(url2, headers=headers, timeout=10)
            if resp2.status_code == 200:
                import re
                for i, match in enumerate(re.finditer(
                    r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</(?:a|div)',
                    resp2.text, re.DOTALL
                )):
                    if len(results) >= num:
                        break
                    url_found = match.group(1)
                    title_found = re.sub(r'<[^>]+>', '', match.group(2)).strip()
                    snippet_found = re.sub(r'<[^>]+>', '', match.group(3)).strip()
                    if title_found:
                        results.append({"title": title_found[:100], "snippet": snippet_found[:200], "url": url_found})
    except Exception as e:
        results.append({"error": str(e)})

    return results[:num] if results else [{"title": f"No results for '{query}'", "url": "", "snippet": "Try a different query"}]

def cmd_search(args):
    query = " ".join(args) if args else "latest news"
    results = _web_search(query)
    return json.dumps({"query": query, "count": len(results), "results": results}, indent=2)

# ── SCAN / SCIENCE / JOBS ──────────────────────────────────────

def cmd_scan_all(args):
    category = args[0] if args else "all"
    queries = {
        "jobs": "urgent hiring remote work 2026 entry level",
        "promotions": "crypto exchange bonus signup reward 2026",
        "bonuses": "free crypto bonus no deposit airdrop 2026",
        "giveaways": "free crypto giveaway airdrop claim",
        "all": "jobs promotions bonuses giveaways free crypto remote work 2026"
    }
    q = queries.get(category.lower(), f"{category} 2026")
    results = _web_search(q, num=8)
    return json.dumps({"category": category, "query": q, "count": len(results), "results": results}, indent=2)

def cmd_jobs(args):
    query_parts = args if args else ["all"]
    query_str = " ".join(query_parts)
    qs = {
        "freelance": "freelance remote gig earn money online 2026",
        "survey": "paid online surveys earn money 2026",
        "crypto": "crypto airdrop play to earn game free 2026",
        "write": "content writer freelance remote paid 2026",
        "data": "data entry remote job no experience 2026",
        "bio": "biology biotech entry level job 2026",
        "clinical": "clinical research trial job 2026",
        "lab": "lab technician job 2026",
        "sa": "remote work South Africa online job 2026",
        "all": "remote job freelance gig work from home 2026 paid"
    }
    q = qs.get(query_str.lower(), f"{query_str} job 2026")
    results = _web_search(q, num=8)
    return json.dumps({"type": query_str, "query": q, "count": len(results), "results": results}, indent=2)

def cmd_science(args):
    topic = args[0] if args else "general"
    queries = {
        "agriculture": "latest agriculture discoveries vertical farming 2026",
        "mining": "mining technology rare earth elements discovery 2026",
        "mri": "MRI machine technology brain imaging innovation 2026",
        "neuralink": "Neuralink latest updates brain computer interface 2026",
        "general": "amazing science discoveries technology breakthroughs 2026"
    }
    q = queries.get(topic.lower(), f"{topic} science discovery 2026")
    results = _web_search(q, num=5)
    return json.dumps({"topic": topic, "query": q, "count": len(results), "results": results}, indent=2)

# ── MEDIA ──────────────────────────────────────────────────────

def cmd_media_stats(args):
    channel_id = args[0] if args else ""
    yt = engine.get("youtube")
    if not yt:
        return json.dumps({"error": "YouTube engine not loaded"})
    if not channel_id:
        return json.dumps({"note": "Provide a YouTube Channel ID to fetch stats", "example": "UC..."})
    result = yt.get_channel_stats(channel_id)
    return json.dumps(result, indent=2)

def cmd_media_test(args):
    mv = engine.get("music_video")
    if not mv:
        return json.dumps({"error": "Music video engine not loaded"})
    test_audio = "/home/j/redengine/factory/assets/test.wav"
    if not os.path.exists(test_audio):
        # Generate a simple test audio file
        try:
            import struct, wave, math
            with wave.open(test_audio, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(44100)
                for i in range(44100 * 3):
                    val = int(math.sin(2 * math.pi * 440 * i / 44100) * 16000)
                    wf.writeframes(struct.pack("<h", val))
        except Exception as e:
            return json.dumps({"error": f"Failed to create test audio: {e}"})
    result = mv.generate(test_audio, "Red Engine Test")
    return json.dumps(result, indent=2)

# ── NOTIFICATIONS & LOGS ──────────────────────────────────────

def cmd_notifications(args=None):
    notes_file = os.path.expanduser("~/.red_notifications.json")
    if os.path.exists(notes_file):
        with open(notes_file) as f:
            return json.dumps(json.load(f), indent=2)
    return json.dumps({"notifications": []})

def cmd_log(args=None):
    log_file = os.path.expanduser("~/.red_transactions.json")
    if os.path.exists(log_file):
        with open(log_file) as f:
            return json.dumps(json.load(f), indent=2)
    return json.dumps({"transactions": []})

# ── COMMAND REGISTRY ───────────────────────────────────────────

COMMANDS = {
    # System
    "status": cmd_status,
    "weekly": cmd_weekly,
    "milestone_check": cmd_milestone,
    "help": cmd_help,
    "--help": cmd_help,
    "-h": cmd_help,
    # Games
    "reskin": cmd_reskin,
    "forge": cmd_forge,
    "deploy": cmd_deploy,
    # Tokens
    "mint": cmd_mint,
    "mint_token": cmd_mint,
    "tokens_list": cmd_tokens_list,
    "treasury_report": cmd_treasury_report,
    "liquidity_report": cmd_liquidity_report,
    "generate_contract": cmd_generate_contract,
    # Exchange
    "balance": cmd_balance,
    "trade": cmd_trade,
    "route_revenue": cmd_route_revenue,
    # Tournament
    "tournament": cmd_tournament,
    "tournament_round": cmd_tournament,
    "tournament_leaderboard": cmd_tournament_leaderboard,
    "tournament_start": cmd_tournament_start,
    "tournament_stop": cmd_tournament_stop,
    # Chat
    "chat": cmd_chat,
    # Search / Scan
    "search": cmd_search,
    "scan_all": cmd_scan_all,
    "jobs": cmd_jobs,
    "science": cmd_science,
    # Media
    "media_stats": cmd_media_stats,
    "media_test": cmd_media_test,
    # New Modules
    "lead_finder": cmd_lead_finder,
    "affiliate_update": cmd_affiliate_update,
    "game_clone": cmd_game_clone,
    "config_vault": cmd_config_vault,
    "scheduler": cmd_scheduler,
    "gui": cmd_gui,
    # Data
    "notifications": cmd_notifications,
    "log": cmd_log,
}

def main():
    init_all()

    # STDIN mode (web UI sends JSON payloads)
    from_stdin = False
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw:
            from_stdin = True
            try:
                payload = json.loads(raw)
                cmd = payload.get("command", "")
                # Build args list from payload
                args_list = []
                for field in ["target", "query", "symbol", "side", "amount", "channel", "video", "title", "source", "name", "topic", "category"]:
                    v = payload.get(field)
                    if v is not None:
                        args_list.append(str(v))
                member = payload.get("member")
                message = payload.get("message")
                if cmd == "chat":
                    args_list = [member or "Red", message or "hello"]
                elif cmd == "search":
                    q = payload.get("query", "")
                    args_list = [q] if q else []
                handler = COMMANDS.get(cmd)
                if handler:
                    result = handler(args_list)
                    print(result)
                else:
                    print(json.dumps({"error": f"Unknown command: {cmd}"}))
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON input"}))

    if from_stdin and len(sys.argv) < 2:
        engine.start()
        return

    # CLI mode
    if len(sys.argv) < 2:
        print(cmd_help())
        return

    command = sys.argv[1]
    args = sys.argv[2:]
    handler = COMMANDS.get(command)
    if handler:
        result = handler(args)
        if isinstance(result, str):
            print(result)
        else:
            print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {command}\n")
        print(cmd_help())

if __name__ == "__main__":
    main()
