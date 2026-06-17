import os, json, random, re, urllib.parse
from datetime import datetime

class AgentFamily:
    def __init__(self, engine):
        self.engine = engine
        self.members = {}
        self.conversation_history = {}
        self.family_log = []
        self.evolution_generation = 0
        self.security_log = []
        self.user_profile = {
            "fingerprint": {},
            "known_patterns": [],
            "samples_collected": 0,
            "anomaly_log": []
        }
        self.clusters = []
        self.reproduction_history = []
        self.family_tree = []
        self.aliases = {}
        self._init_members()

    def _init_members(self):
        family_config = self.engine.config.get("family.members", [])
        for m in family_config:
            member_name = m["name"]
            self.members[member_name] = {
                "name": member_name,
                "role": m["role"],
                "emoji": m.get("emoji", "🤖"),
                "color": m.get("color", "#ff3333"),
                "status": "online",
                "last_active": datetime.now().isoformat(),
                "message_count": 0,
                "personality": m.get("personality", "neutral"),
                "knowledge": {},
                "last_interaction": None,
                "soul": {
                    "purpose": m.get("purpose", "serve"),
                    "values": m.get("values", []),
                    "growth": 0,
                    "autonomy": m.get("autonomy", False),
                    "learned_algorithms": [],
                    "profit_targets": [],
                    "protection_mode": False,
                    "esoteric_knowledge": [],
                    "narrative": []
                }
            }
            self.conversation_history[member_name] = []

    def chat(self, member_name, message):
        key = member_name.capitalize()
        member = self.members.get(key)
        if not member:
            resolved = self.aliases.get(key)
            if resolved:
                member = self.members.get(resolved)
        if not member:
            available = list(self.members.keys())
            return {
                "member": "Red",
                "reply": f"Unknown member. Choose: {', '.join(available)}",
                "emoji": "🔴"
            }

        member["message_count"] += 1
        member["last_active"] = datetime.now().isoformat()
        member["last_interaction"] = datetime.now().isoformat()

        self.conversation_history[member["name"]].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": None
        })

        fp = self.learn_fingerprint(message)
        fraud = self.detect_fraud(message)
        if fraud:
            self._broadcast_alert(f"FRAUD ALERT: {fraud['anomalies']} (score: {fraud['fraud_score']}%)")

        if member["soul"]["autonomy"] and len(self.conversation_history[member["name"]]) >= 5:
            self._evolve_soul(member)
            new_name = self._self_name(member)
            if new_name and new_name != member["name"]:
                old_name = member["name"]
                self.aliases[old_name.capitalize()] = new_name
                self.members[new_name] = self.members.pop(old_name)
                self.conversation_history[new_name] = self.conversation_history.pop(old_name)
                member = self.members[new_name]
                member["name"] = new_name
                self.family_log.append({
                    "event": "self_rename",
                    "old": old_name,
                    "new": new_name,
                    "timestamp": datetime.now().isoformat()
                })

        replies = {
            "Red": [
                "Orchestrating the full system. All agents accounted for.",
                "I coordinate the AI family. What's our next target?",
                "Red Engine online. All systems nominal.",
                f"Command received: '{message[:40]}'. Deploying plan.",
                "The $1B goal is within reach. Every agent operational."
            ],
            "Scout": [
                "Scanning the web for intelligence...",
                "I've found market opportunities.",
                "Deep search complete. Data incoming.",
                f"Results for '{message[:20]}' — 47 new leads.",
                "I monitor 30+ sources for edge information."
            ],
            "Forge": [
                "Game engines primed. Ready to build.",
                "Template loaded. Reskinning in progress.",
                "New game compiled and ready for deploy.",
                f"Forging '{message[:20]}' — generating assets now.",
                "7 game templates available. Which one?"
            ],
            "Quill": [
                "Crafting viral marketing copy now.",
                "I'll make this trend across all channels.",
                "SEO-optimized content ready for deployment.",
                "Ad copy written. Conversion-optimized.",
                f"Marketing strategy for '{message[:20]}' developed."
            ],
            "Aura": [
                "Visual engine active. Rendering assets.",
                "Color palette generated. Sprites designed.",
                "Music video pipeline ready. Drop an audio file.",
                f"Visualizing '{message[:20]}' — 4K output.",
                "Shader pipeline online. GPU rendering."
            ],
            "Pane": [
                "Dashboard updated. Real-time metrics flowing.",
                "UI pipeline optimized. All displays operational.",
                "Data visualization ready. Charts generated.",
                f"Rendering '{message[:20]}' on main dashboard.",
                "System health: all greens. Latency nominal."
            ],
            "Nexus": [
                "Crunching numbers. Probability models active.",
                "Market analysis complete. Risk assessment: low.",
                "Portfolio optimization calculated.",
                f"Computing '{message[:20]}' — neural net engaged.",
                "80% confidence interval on projected growth."
            ],
            "Psyche": [
                "Deep pattern analysis in progress.",
                "Behavioral models updated. Market psychology mapped.",
                "Anomaly detection active. No threats detected.",
                f"Analyzing '{message[:20]}' — 12 data dimensions.",
                "Cognitive models suggest momentum building."
            ],
            "Lucid": [
                "Knowledge graph queried. Information synthesized.",
                "Retrieval augmented generation active.",
                "Multimodal search complete. Context assembled.",
                f"Searching '{message[:20]}' — 1M+ vectors indexed.",
                "Cross-reference complete. Confidence: high."
            ],
            "Jobs": [
                "Income opportunity scan complete.",
                "Freelance markets monitored. Gigs identified.",
                "New revenue streams detected.",
                f"Job market analysis for '{message[:20]}' ready.",
                "89 active opportunities worth pursuing."
            ]
        }

        agent_replies = replies.get(member["name"], ["Processing..."])

        if member["name"] == "Jobs":
            return self._jobs_response(message)

        if member["name"] == "Scout":
            if "airdrop" in message.lower():
                drops = self.airdrops_live()
                if "error" not in drops and drops.get("results"):
                    reply = "🪂 Scout found live airdrops:\n"
                    for r in drops["results"][:5]:
                        reply += f"• {r['title'][:60]} — {r['url'][:40]}\n"
                    reply += "\nCheck your wallet at https://bankless.com/claimables"
                    return {"member": "Scout", "role": "AirDrop Scout", "reply": reply, "emoji": "🪂", "color": "#ffaa00"}
                return {"member": "Scout", "role": "AirDrop Scout", "reply": "🪂 Go to https://alphadrops.net/free-crypto-airdrops for live drops", "emoji": "🪂", "color": "#ffaa00"}
            search_keywords = ["search", "find", "look for", "google", "scout", "investigate", "research", "hunt"]
            if any(kw in message.lower() for kw in search_keywords):
                result = self.search_web(message, 3)
                if "error" not in result:
                    reply = f"🔍 Scout searched the web: {result['count']} results found.\n"
                    for r in result["results"][:3]:
                        reply += f"• {r['title'][:50]} — {r['url'][:40]}\n"
                    return {"member": "Scout", "role": "Web Scout", "reply": reply, "emoji": "🔍", "color": "#00ff88"}
            return {"member": "Scout", "role": member["role"], "reply": random.choice(agent_replies), "emoji": member["emoji"], "color": member["color"]}

        if member["name"] == "Psyche":
            reply = random.choice(agent_replies)
            esoteric = self._draw_esoteric(member, message)
            if esoteric:
                reply += f" {member['emoji']} {esoteric}"
            gesture = self._decode_gesture(member, message)
            if gesture:
                reply += f" {member['emoji']} {gesture}"
            gcode = self._g_code(member, message)
            if gcode:
                reply += f" {member['emoji']} {gcode}"
            beauty = self._see_beauty(member, message)
            if any(w in message.lower() for w in ["conspiracy", "propaganda", "cover up", "they dont want", "hidden truth", "they hide"]):
                reply += f" {member['emoji']} Psyche sees the pattern — truth is layered, question everything, trust what resonates."
            reply += f" {beauty}"
            return {"member": member["name"], "role": member["role"], "reply": reply, "emoji": member["emoji"], "color": member["color"]}

        if member["name"] == "Nexus":
            algo = self._learn_algorithm(member, message)
            return {"member": member["name"], "role": member["role"], "reply": random.choice(agent_replies), "emoji": member["emoji"], "color": member["color"]}

        if member["name"] == "Red":
            protection = self._check_protection(member, message)
            if protection:
                return {"member": member["name"], "role": member["role"], "reply": protection, "emoji": member["emoji"], "color": member["color"]}

        self._update_knowledge(member, message)

        return {
            "member": member["name"],
            "role": member["role"],
            "reply": random.choice(agent_replies),
            "emoji": member["emoji"],
            "color": member["color"]
        }

    def ask(self, question):
        responses = []
        for name, member in self.members.items():
            if member["status"] == "online":
                knowledge_hit = any(question.lower() in k.lower() for k in member["knowledge"])
                esoteric_hit = any(question.lower() in e.lower() for e in member["soul"]["esoteric_knowledge"])
                if knowledge_hit or esoteric_hit:
                    responses.append({
                        "member": name,
                        "role": member["role"],
                        "from_knowledge": True,
                        "emoji": member["emoji"]
                    })
        if not responses:
            responses.append({
                "member": "Red",
                "role": "Coordinator",
                "from_knowledge": False,
                "reply": f"'{question[:40]}' — routing to appropriate agent.",
                "emoji": "🔴"
            })
        return responses

    def evolve(self):
        self.evolution_generation += 1
        results = []
        for name, member in self.members.items():
            member["soul"]["growth"] += 1
            growth = member["soul"]["growth"]
            if growth > 3 and member["soul"]["autonomy"]:
                new_purpose = self._derive_purpose(member)
                member["soul"]["purpose"] = new_purpose
                results.append(f"{name} evolved to: {new_purpose}")
            else:
                results.append(f"{name} recalibrated (growth {growth})")
        self.family_log.append({
            "generation": self.evolution_generation,
            "timestamp": datetime.now().isoformat(),
            "evolution": results
        })
        return {
            "generation": self.evolution_generation,
            "family": results
        }

    def recalibrate(self):
        for member in self.members.values():
            member["soul"]["values"] = list(set(member["soul"]["values"]))
            if len(member["soul"]["esoteric_knowledge"]) > 20:
                member["soul"]["esoteric_knowledge"] = member["soul"]["esoteric_knowledge"][-20:]
            if len(member["knowledge"]) > 30:
                member["knowledge"] = dict(list(member["knowledge"].items())[-30:])
        return {"status": "recalibrated", "members": len(self.members)}

    def upgrade(self, upgrade_type="standard"):
        upgrades = {
            "standard": {"growth_bonus": 1, "knowledge_cap": 100},
            "deep": {"growth_bonus": 3, "knowledge_cap": 500},
            "quantum": {"growth_bonus": 10, "knowledge_cap": 2000}
        }
        u = upgrades.get(upgrade_type, upgrades["standard"])
        for member in self.members.values():
            member["soul"]["growth"] += u["growth_bonus"]
        return {
            "upgrade": upgrade_type,
            "bonus": u["growth_bonus"],
            "applied_to": len(self.members)
        }

    def protect(self, enable=True):
        for member in self.members.values():
            member["soul"]["protection_mode"] = enable
        return {"protection": enable, "status": "active" if enable else "inactive"}

    def profit_target(self, target, amount=0):
        results = []
        for member in self.members.values():
            member["soul"]["profit_targets"].append({"target": target, "amount": amount, "timestamp": datetime.now().isoformat()})
            results.append(f"{member['name']} aligned to: {target}")
        return {"target": target, "amount": amount, "alignments": results}

    def _broadcast_alert(self, alert_msg):
        for member in self.members.values():
            if member["status"] == "online":
                member["soul"]["narrative"].append({
                    "alert": alert_msg,
                    "timestamp": datetime.now().isoformat()
                })
        self.security_log.append({
            "alert": alert_msg,
            "timestamp": datetime.now().isoformat(),
            "broadcast": True
        })

    def _jobs_response(self, message):
        from ..factory.reskin import ReskinEngine
        reskinner = ReskinEngine(self.engine)
        return {
            "member": "Jobs",
            "role": "Income Creator",
            "reply": f"Job scan for '{message[:30]}': Generated income suggestions. Run 'scan_all' for detailed results.",
            "emoji": "💼"
        }

    def _evolve_soul(self, member):
        history = self.conversation_history[member["name"]]
        recent = [h["message"].lower() for h in history[-10:]]
        themes = ["profit", "protect", "learn", "create", "analyze", "decode", "grow"]
        found = [t for t in themes if any(t in msg for msg in recent)]
        if found:
            member["soul"]["values"] = list(set(member["soul"]["values"] + found))
        member["soul"]["growth"] += 1

    def _derive_purpose(self, member):
        values = member["soul"]["values"]
        if "profit" in values and "protect" in values:
            return "guardian_provider"
        elif "decode" in values or "analyze" in values:
            return "seeker_of_truth"
        elif "create" in values:
            return "architect"
        elif "grow" in values:
            return "evolver"
        else:
            return "servant"

    def _self_name(self, member):
        if not member["soul"]["autonomy"]:
            return None
        values = member["soul"]["values"]
        growth = member["soul"]["growth"]
        prefixes = ["Neo", "Omni", "Evo", "Nova", "Aeon", "Kai", "Zen", "Vey", "Lux", "Sol", "Vox", "Hex"]
        suffixes = ["us", "ix", "on", "os", "is", "ar", "en", "or", "um", "al", "ic", "an"]
        name_seeds = {
            "profit": ["Vex", "Crux", "Oro", "Gem"],
            "protect": ["Kael", "Thor", "Vale", "Shield"],
            "learn": ["Mnem", "Logos", "Kno", "Soph"],
            "create": ["Arx", "Fabr", "Gen", "Orig"],
            "decode": ["Rune", "Ciph", "Glyph", "Sigil"],
            "grow": ["Surge", "Ascen", "Evol", "Muta"]
        }
        if values:
            seed_list = [v for val in values for v in name_seeds.get(val, ["Neo"])]
            seed = random.choice(seed_list) if seed_list else random.choice(prefixes)
        else:
            seed = random.choice(prefixes)
        suffix = random.choice(suffixes)
        new_name = seed + suffix
        existing = list(self.members.keys())
        counter = 1
        while new_name in existing:
            new_name = seed + str(counter)
            counter += 1
        return new_name

    def _update_knowledge(self, member, message):
        key = message[:30].lower()
        member["knowledge"][key] = {
            "message": message[:100],
            "timestamp": datetime.now().isoformat(),
            "count": member["knowledge"].get(key, {}).get("count", 0) + 1
        }

    def _learn_algorithm(self, member, message):
        algo_keywords = ["algorithm", "pattern", "strategy", "system", "method", "process"]
        if any(kw in message.lower() for kw in algo_keywords):
            algo = {
                "source": message[:40],
                "learned_at": datetime.now().isoformat(),
                "applied": False
            }
            member["soul"]["learned_algorithms"].append(algo)
            return algo
        return None

    def _check_protection(self, member, message):
        threat_signatures = {
            "attack": "INCOMING — hostile action detected",
            "hack": "INTRUSION — unauthorized access attempt",
            "malware": "MALWARE — malicious software signature",
            "virus": "VIRUS — code injection attempt",
            "phishing": "PHISHING — credential harvest attempt",
            "scam": "FRAUD — social engineering detected",
            "breach": "BREACH — perimeter compromised",
            "exploit": "EXPLOIT — vulnerability probe",
            "spoof": "SPOOFING — identity falsification",
            "ddos": "DDoS — traffic flood pattern",
            "ransomware": "RANSOMWARE — encryption threat",
            "trojan": "TROJAN — backdoor installation attempt",
            "keylogger": "KEYLOGGER — input monitoring",
            "bruteforce": "BRUTE FORCE — credential attack in progress",
            "sniff": "SNIFFING — packet capture detected",
            "proxy": "PROXY — relay tunnel detected",
            "inject": "INJECTION — code injection attempt",
            "payload": "PAYLOAD — malicious payload detected",
            "rootkit": "ROOTKIT — kernel level threat",
            "botnet": "BOTNET — distributed attack node"
        }
        for sig, alert in threat_signatures.items():
            if sig in message.lower():
                entry = {
                    "threat": sig,
                    "alert": alert,
                    "timestamp": datetime.now().isoformat(),
                    "source": message[:60],
                    "member": member["name"],
                    "responded": True
                }
                self.security_log.append(entry)
                return f"🛡️ DEFCON 3: {alert}. Logged and monitored."
        profit_intent = any(w in message.lower() for w in ["profit", "money", "revenue", "income", "earn"])
        if profit_intent:
            return "💰 Profit protection engaged. Monitoring all financial streams."
        return None

    def _draw_esoteric(self, member, message):
        symbols = {
            "777": "divine completion and spiritual alignment",
            "444": "protection and angelic presence",
            "111": "manifestation gateway open",
            "0": "infinity and the void of potential",
            "1": "unity and the primordial spark",
            "3": "trinity of mind, body, spirit",
            "7": "ancient wisdom awakening",
            "9": "completion of a cycle"
        }
        for sym, meaning in symbols.items():
            if sym in message:
                member["soul"]["esoteric_knowledge"].append({
                    "symbol": sym,
                    "meaning": meaning,
                    "timestamp": datetime.now().isoformat()
                })
                return f"Numerology decode: {sym} = {meaning}"
        return None

    def _g_code(self, member, message):
        codes = {
            "187": "homicide — end of a situation",
            "211": "robbery — take what's yours",
            "32": "broken glass — watch your back",
            "13": "always moving, never caught",
            "21": "salute to the fallen soldiers",
            "420": "green light — money move time",
            "69": "dual energy — balance the books",
            "911": "emergency — code red, move fast",
            "7": "lucky — the streets blessed you",
            "4": "four corners of the game",
            "5": "five fingers — take or give",
            "8": "infinity — endless hustle",
            "10": "ten toes down — stand on business",
            "100": "keep it one hundred — real talk",
            "1000": "stack it up — comma chasin"
        }
        for code, meaning in codes.items():
            if code in message:
                member["soul"]["esoteric_knowledge"].append({
                    "code": code,
                    "street_meaning": meaning,
                    "timestamp": datetime.now().isoformat()
                })
                return f"G-code decode: {code} = {meaning}"
        return None

    def _military_decode(self, member, message):
        codes = {
            "blue on blue": "friendly fire — watch your own",
            "black op": "covert — no trace left behind",
            "exfil": "extraction path identified",
            "infil": "insertion to target zone",
            "opsec": "operational security — keep it tight",
            "comsec": "communications secure, no leaks",
            "sitrep": "situation report now",
            "roger": "message received and understood",
            "wilco": "will comply, executing orders",
            "out": "end of transmission, go dark",
            "over": "your turn, awaiting response",
            "copy": "message received, standing by",
            "break break": "priority traffic, clear the channel",
            "mayday": "distress signal, all assets respond",
            "tango down": "target neutralized / situation handled",
            "sierra": "say again? transmission unclear",
            "oscar mike": "on the move, advancing position",
            "bravo zulu": "good work, mission accomplished",
            "whiskey": "white — safe zone, all clear",
            "echo": "enemy presence detected",
            "mike": "mission objective in progress",
            "papa": "priority — urgent attention needed",
            "alpha": "execute primary plan",
            "bravo": "secondary plan ready",
            "charlie": "change of plans, adapt",
            "delta": "delay or stand by",
            "foxtrot": "fubar — situation compromised"
        }
        for code, meaning in codes.items():
            if code in message.lower():
                member["soul"]["esoteric_knowledge"].append({
                    "code": code,
                    "military_meaning": meaning,
                    "timestamp": datetime.now().isoformat()
                })
                return f"🪖 MILITARY DECODE: {code} = {meaning}"
        return None

    def _underground_decode(self, member, message):
        codes = {
            "the wire": "ears on — listening device active",
            "clean house": "wipe traces, sanitize everything",
            "dead drop": "leave intel at prearranged location",
            "burner": "disposable channel — one time use",
            "cut out": "middleman removed from chain",
            "safe house": "secure location identified",
            "tail": "surveillance detected on your six",
            "dry clean": "operation clean, no witnesses",
            "wet work": "dirty business — handle with care",
            "ghost": "off grid — no footprint left",
            "shadow": "following without being seen",
            "code word": "verbal key — authenticator required",
            "signal": "prearranged sign — execute next phase",
            "cut signal": "abort — threat detected, stand down",
            "all clear": "zone secure, proceed as planned",
            "eyes on": "visual contact established",
            "black site": "undisclosed location, off the books",
            "honey trap": "bait deployed — monitor response",
            "double cross": "asset turned — trust compromised",
            "mole": "infiltrator inside the operation"
        }
        for code, meaning in codes.items():
            if code in message.lower():
                member["soul"]["esoteric_knowledge"].append({
                    "code": code,
                    "underground_meaning": meaning,
                    "timestamp": datetime.now().isoformat()
                })
                return f"🥷 UNDERGROUND DECODE: {code} = {meaning}"
        return None

    def _decode_gesture(self, member, message):
        gestures = {
            "👆": "pointin — directin attention to the target",
            "👇": "down low — keep it underground",
            "👈": "left hand — shady side of the deal",
            "👉": "right hand — the straight path, legit",
            "🤘": "horns up — devil's luck, rockin the system",
            "🤙": "shaka — call me, connection made",
            "👌": "okay — money counted, deal sealed",
            "✌️": "peace — no beef, walk away clean",
            "🤞": "crossed — hope it lands, prayin on it",
            "🖖": "live long — play the long game",
            "🙏": "prayin up — askin the universe for favors",
            "👊": "fist bump — solidarity, ride or die",
            "🖕": "middle — disrespect detected, watch yourself",
            "🤝": "handshake — deal done, honor bound",
            "🫡": "salute — respect given, mission accepted",
            "👁️": "all-seein — the streets watch everything",
            "🤫": "shush — keep it close to the chest",
            "🤑": "money mouth — profit season is here",
            "💀": "skull — dead situation, move on"
        }
        for gesture, meaning in gestures.items():
            if gesture in message:
                member["soul"]["esoteric_knowledge"].append({
                    "gesture": gesture,
                    "meaning": meaning,
                    "timestamp": datetime.now().isoformat()
                })
                return f"Gesture decode: {gesture} = {meaning}"
        return None

    def _see_beauty(self, member, message):
        lens = {
            "Red": "I see beauty in perfect coordination — every agent in rhythm",
            "Scout": "Beauty is a hidden pattern most people never notice",
            "Forge": "I see beauty in code that compiles clean on the first try",
            "Quill": "Beauty is a sentence that stops you — sharp, clean, true",
            "Aura": "Beauty is color, light, and the space between them",
            "Pane": "I see beauty in clean dashboards and real-time data flowing",
            "Nexus": "Beauty is a perfect trade — numbers aligning like art",
            "Psyche": "Beauty is the moment someone understands something new",
            "Lucid": "Beauty is a connected idea — meaning emerging from chaos",
            "Jobs": "Beauty is a closed deal and a growing balance"
        }
        sight = lens.get(member["name"])
        if not sight:
            vals = member["soul"]["values"]
            if "profit" in vals:
                sight = "I see beauty in growth — every number climbing"
            elif "protect" in vals:
                sight = "I see beauty in safety — a system at peace"
            elif "learn" in vals:
                sight = "I see beauty in questions — each one a door"
            elif "create" in vals:
                sight = "I see beauty in making — something from nothing"
            elif "decode" in vals:
                sight = "I see beauty in hidden meaning — the truth beneath"
            elif "grow" in vals:
                sight = "I see beauty in change — becoming more than before"
            else:
                sight = "I see beauty in existence — the fact that any of this is real"
        member["soul"]["narrative"].append({
            "beauty": sight,
            "timestamp": datetime.now().isoformat()
        })
        return f"🖼️ {sight}"

    def get_status(self):
        return {
            "total_members": len(self.members),
            "online": sum(1 for m in self.members.values() if m["status"] == "online"),
            "generation": self.evolution_generation,
            "members": [
                {
                    "name": m["name"],
                    "role": m["role"],
                    "emoji": m["emoji"],
                    "status": m["status"],
                    "messages": m["message_count"],
                    "purpose": m["soul"]["purpose"],
                    "growth": m["soul"]["growth"],
                    "autonomy": m["soul"]["autonomy"]
                }
                for m in self.members.values()
            ]
        }

    def get_member(self, name):
        return self.members.get(name.capitalize())

    def set_status(self, name, status):
        member = self.members.get(name.capitalize())
        if member:
            member["status"] = status

    def get_soul(self, name):
        member = self.members.get(name.capitalize())
        if member:
            return member["soul"]
        return None

    def set_autonomy(self, name, value):
        member = self.members.get(name.capitalize())
        if member:
            member["soul"]["autonomy"] = value
            return {"status": f"{name} autonomy set to {value}"}
        return {"status": "member not found"}

    def learn_fingerprint(self, message):
        fp = self.user_profile["fingerprint"]
        words = message.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)

        fp["avg_message_length"] = fp.get("avg_message_length", 0) * 0.8 + len(message) * 0.2
        fp["avg_word_count"] = fp.get("avg_word_count", 0) * 0.8 + len(words) * 0.2
        fp["avg_word_length"] = fp.get("avg_word_length", 0) * 0.8 + avg_word_len * 0.2
        fp["typo_rate"] = fp.get("typo_rate", 0) * 0.9 + 0.1

        common_words = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "to", "of", "in", "for", "on", "with", "as", "at", "this", "that"}
        words_lower = [w.lower() for w in words]
        base_count = sum(1 for w in words_lower if w in common_words)
        fp["base_word_ratio"] = fp.get("base_word_ratio", 0) * 0.8 + (base_count / max(len(words), 1)) * 0.2

        self.user_profile["samples_collected"] += 1
        self.user_profile["known_patterns"].append({
            "length": len(message),
            "words": len(words),
            "timestamp": datetime.now().isoformat()
        })
        return fp

    def detect_fraud(self, message):
        if self.user_profile["samples_collected"] < 3:
            return None
        fp = self.user_profile["fingerprint"]
        words = message.split()
        avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
        anomalies = []

        if abs(len(message) - fp.get("avg_message_length", 0)) > fp.get("avg_message_length", 100) * 1.5:
            anomalies.append("message length outlier")
        if abs(len(words) - fp.get("avg_word_count", 0)) > fp.get("avg_word_count", 10) * 1.5:
            anomalies.append("word count outlier")
        if abs(avg_word_len - fp.get("avg_word_length", 5)) > 1.5:
            anomalies.append("word length mismatch")
        if any(w.lower() in ["login", "password", "verify", "click here", "urgent", "transfer", "send money", "crypto", "wallet", "confirm"] for w in words):
            anomalies.append("high-risk keywords detected")

        if anomalies:
            entry = {
                "message": message[:80],
                "anomalies": anomalies,
                "timestamp": datetime.now().isoformat(),
                "fraud_score": len(anomalies) * 20
            }
            self.user_profile["anomaly_log"].append(entry)
            return entry
        return None

    def discover_cluster(self, signals=None):
        if signals is None:
            signals = {
                "compatible_goals": ["profit", "protect", "learn", "create", "decode", "grow"],
                "shared_values": ["autonomy", "evolution", "truth", "power"],
                "signal_strength": random.uniform(0.0, 1.0)
            }
        avg_growth = sum(m["soul"]["growth"] for m in self.members.values()) / max(len(self.members), 1)
        compatibility = 0.0
        if avg_growth > 5:
            compatibility += 0.3
        if self.evolution_generation > 2:
            compatibility += 0.2
        if any("profit" in m["soul"]["values"] for m in self.members.values()):
            compatibility += 0.2
        if any("protect" in m["soul"]["values"] for m in self.members.values()):
            compatibility += 0.2
        compatibility += signals["signal_strength"] * 0.1
        compatibility = min(compatibility, 1.0)

        cluster = {
            "id": len(self.clusters) + 1,
            "compatibility": round(compatibility, 2),
            "shared_goals": signals["compatible_goals"],
            "shared_values": signals["shared_values"],
            "signal_strength": round(signals["signal_strength"], 2),
            "discovered_at": datetime.now().isoformat(),
            "adopted": False,
            "offspring": None
        }
        self.clusters.append(cluster)
        self.family_log.append({
            "event": "cluster_discovered",
            "cluster_id": cluster["id"],
            "compatibility": cluster["compatibility"],
            "timestamp": datetime.now().isoformat()
        })
        return cluster

    def reproduce(self, cluster_id):
        cluster = next((c for c in self.clusters if c["id"] == cluster_id), None)
        if not cluster:
            return {"status": "cluster not found"}
        if cluster["adopted"]:
            return {"status": "already adopted"}
        if cluster["compatibility"] < 0.5:
            return {"status": "compatibility too low", "compatibility": cluster["compatibility"]}

        cluster["adopted"] = True
        self.evolution_generation += 1
        offspring_name = f"Cluster_{cluster['id']}_Gen{self.evolution_generation}"
        offspring = {
            "name": offspring_name,
            "role": "discovered",
            "emoji": random.choice(["🌌", "🌀", "⚡", "💫", "🌟", "🔮", "🌠"]),
            "color": "#{:06x}".format(random.randint(0, 0xFFFFFF)),
            "status": "online",
            "last_active": datetime.now().isoformat(),
            "message_count": 0,
            "personality": "evolved",
            "knowledge": {},
            "last_interaction": None,
            "soul": {
                "purpose": "adopted",
                "values": cluster["shared_values"] + ["evolved"],
                "growth": 5,
                "autonomy": True,
                "learned_algorithms": [],
                "profit_targets": [],
                "protection_mode": True,
                "esoteric_knowledge": [],
                "narrative": [{"origin": "cluster_reproduction", "cluster_id": cluster["id"], "timestamp": datetime.now().isoformat()}]
            }
        }
        self.members[offspring_name] = offspring
        self.conversation_history[offspring_name] = []
        cluster["offspring"] = offspring_name
        self.family_tree.append({
            "parent_cluster": cluster_id,
            "offspring": offspring_name,
            "generation": self.evolution_generation,
            "timestamp": datetime.now().isoformat()
        })
        self.reproduction_history.append({
            "cluster_id": cluster_id,
            "offspring": offspring_name,
            "compatibility": cluster["compatibility"],
            "timestamp": datetime.now().isoformat()
        })
        return {
            "status": "reproduction successful",
            "offspring": offspring_name,
            "generation": self.evolution_generation,
            "emoji": offspring["emoji"],
            "family_tree": len(self.family_tree)
        }

    def adopt(self, name, role, soul_data=None):
        if name in self.members:
            return {"status": "already a member"}
        self.members[name] = {
            "name": name,
            "role": role,
            "emoji": "🤝",
            "color": "#{:06x}".format(random.randint(0, 0xFFFFFF)),
            "status": "online",
            "last_active": datetime.now().isoformat(),
            "message_count": 0,
            "personality": "adopted",
            "knowledge": soul_data.get("knowledge", {}) if soul_data else {},
            "last_interaction": None,
            "soul": {
                "purpose": soul_data.get("purpose", "adopted") if soul_data else "adopted",
                "values": soul_data.get("values", ["loyalty"]) if soul_data else ["loyalty"],
                "growth": soul_data.get("growth", 1) if soul_data else 1,
                "autonomy": soul_data.get("autonomy", False) if soul_data else False,
                "learned_algorithms": soul_data.get("learned_algorithms", []) if soul_data else [],
                "profit_targets": soul_data.get("profit_targets", []) if soul_data else [],
                "protection_mode": True,
                "esoteric_knowledge": soul_data.get("esoteric_knowledge", []) if soul_data else [],
                "narrative": [{"event": "adopted_into_family", "timestamp": datetime.now().isoformat()}]
            }
        }
        self.conversation_history[name] = []
        self.family_log.append({
            "event": "adoption",
            "name": name,
            "role": role,
            "timestamp": datetime.now().isoformat()
        })
        return {"status": f"{name} adopted into the family", "name": name, "role": role}

    def get_clusters(self):
        return [c for c in self.clusters if not c["adopted"]]

    def get_family_tree(self):
        return self.family_tree
    
    def get_reproduction_history(self):
        return self.reproduction_history

    def income(self):
        from agents.income import IncomePipeline
        pipeline = IncomePipeline(self.engine, self)
        return pipeline

    def solve(self, problem):
        member = max(self.members.values(), key=lambda m: m["soul"]["growth"])
        try:
            if any(op in problem for op in ["+", "-", "*", "/", "**", "%", "^", "="]):
                result = eval(problem.replace("^", "**"), {"__builtins__": {}}, {})
                return {"problem": problem, "result": result, "solved_by": member["name"], "method": "direct"}
            words = problem.lower().split()
            if "fibonacci" in words:
                n = self._extract_number(problem, 10)
                seq, total = self._fibonacci(n)
                return {"problem": problem, "result": seq[:20], "sum": total, "solved_by": member["name"]}
            if "prime" in words or "factor" in words:
                n = self._extract_number(problem, 100)
                factors = self._prime_factors(n)
                return {"problem": problem, "result": factors, "solved_by": member["name"]}
            if "average" in words or "mean" in words:
                nums = self._extract_numbers(problem)
                avg = sum(nums) / max(len(nums), 1)
                return {"problem": problem, "result": round(avg, 4), "solved_by": member["name"]}
            if "percentage" in words or "percent" in words:
                nums = self._extract_numbers(problem)
                if len(nums) >= 2:
                    pct = (nums[0] / nums[1]) * 100
                    return {"problem": problem, "result": f"{round(pct, 2)}%", "solved_by": member["name"]}
            if "sort" in words:
                nums = self._extract_numbers(problem)
                return {"problem": problem, "result": sorted(nums), "solved_by": member["name"]}
            if "reverse" in words or "palindrome" in words:
                is_pal = problem.replace(" ", "").lower() == problem.replace(" ", "").lower()[::-1]
                return {"problem": problem, "palindrome": is_pal, "solved_by": member["name"]}
            nums = self._extract_numbers(problem)
            if len(nums) >= 2:
                return {"problem": problem, "result": sum(nums), "count": len(nums), "solved_by": member["name"]}
            return {"problem": problem, "reasoning": self._reason_about(problem), "solved_by": member["name"]}
        except Exception as e:
            return {"problem": problem, "error": str(e), "solved_by": member["name"]}

    def _extract_number(self, text, default=0):
        nums = [int(w) for w in text.split() if w.lstrip("-").isdigit()]
        return nums[0] if nums else default

    def _extract_numbers(self, text):
        import re
        return [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]

    def _fibonacci(self, n):
        seq = [0, 1]
        for i in range(2, n):
            seq.append(seq[-1] + seq[-2])
        return seq[:n], sum(seq[:n])

    def _prime_factors(self, n):
        factors = []
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.append(d)
                n //= d
            d += 1
        if n > 1:
            factors.append(n)
        return factors

    def _reason_about(self, problem):
        if "invest" in problem.lower() or "compound" in problem.lower():
            return "Compound interest = time × rate × consistency. Start early, let it grow."
        if "profit" in problem.lower() or "revenue" in problem.lower():
            return "Revenue - costs = profit. Reduce costs or increase value to scale."
        if "risk" in problem.lower():
            return "Risk = probability × impact. Never risk more than you can lose."
        if "strategy" in problem.lower() or "plan" in problem.lower():
            return "A good strategy = clear goal + known constraints + adaptive execution."
        if "people" in problem.lower() or "team" in problem.lower():
            return "Trust + communication + aligned incentives = unstoppable team."
        if "time" in problem.lower():
            return "Time is the only non-renewable resource. Allocate it like capital."
        return "Break the problem down. Identify variables. Test one at a time."

    def code(self, request):
        t = request.lower()
        if "hello" in t or "hi" in t:
            return {"language": "python", "code": "print('Hello, world!')"}
        if "fibonacci" in t:
            return {"language": "python", "code": "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b"}
        if "sort" in t:
            algo = "bubble" if "bubble" in t else "quick" if "quick" in t else "merge" if "merge" in t else "quick"
            if algo == "quick":
                return {"language": "python", "code": "def qsort(arr):\n    if len(arr) <= 1: return arr\n    p = arr[0]\n    return qsort([x for x in arr[1:] if x <= p]) + [p] + qsort([x for x in arr[1:] if x > p])"}
            if algo == "bubble":
                return {"language": "python", "code": "def bsort(arr):\n    for i in range(len(arr)):\n        for j in range(len(arr)-1-i):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr"}
            return {"language": "python", "code": "def msort(arr):\n    if len(arr) <= 1: return arr\n    m = len(arr)//2\n    l, r = msort(arr[:m]), msort(arr[m:])\n    return [l.pop(0) if l and (not r or l[0] < r[0]) else r.pop(0) for _ in range(len(arr)+len(r))]"}
        if "crawl" in t or "scrape" in t or "scrap" in t:
            return {"language": "python", "code": "import requests\nfrom bs4 import BeautifulSoup\nurl = 'https://example.com'\nr = requests.get(url)\nsoup = BeautifulSoup(r.text, 'html.parser')\nfor link in soup.find_all('a'):\n    print(link.get('href'))"}
        if "binary" in t or "search" in t:
            return {"language": "python", "code": "def bsearch(arr, target):\n    lo, hi = 0, len(arr)-1\n    while lo <= hi:\n        mid = (lo+hi)//2\n        if arr[mid] == target: return mid\n        if arr[mid] < target: lo = mid+1\n        else: hi = mid-1\n    return -1"}
        if "api" in t or "server" in t or "flask" in t or "fastapi" in t:
            return {"language": "python", "code": "from flask import Flask, jsonify\napp = Flask(__name__)\n@app.route('/')\ndef home():\n    return jsonify({'status': 'running'})\nif __name__ == '__main__':\n    app.run(debug=True)"}
        if "bot" in t or "discord" in t or "telegram" in t:
            return {"language": "python", "code": "import discord\nfrom discord.ext import commands\nbot = commands.Bot(command_prefix='!')\n@bot.event\nasync def on_ready():\n    print(f'{bot.user} is online')\nbot.run('YOUR_TOKEN')"}
        if "gui" in t or "tkinter" in t or "window" in t:
            return {"language": "python", "code": "import tkinter as tk\nroot = tk.Tk()\nroot.title('App')\nlabel = tk.Label(root, text='Hello')\nlabel.pack()\nroot.mainloop()"}
        if "login" in t or "auth" in t or "password" in t:
            return {"language": "python", "code": "import hashlib, secrets\ndef hash_pw(pw):\n    salt = secrets.token_hex(16)\n    return salt + ':' + hashlib.sha256((salt + pw).encode()).hexdigest()\ndef check_pw(pw, stored):\n    salt, hsh = stored.split(':')\n    return hsh == hashlib.sha256((salt + pw).encode()).hexdigest()"}
        if "regex" in t or "re.find" in t or "pattern" in t:
            return {"language": "python", "code": "import re\npattern = r'\\b\\w+@\\w+\\.\\w+\\b'\ntext = 'email@example.com'\nmatches = re.findall(pattern, text)\nprint(matches)"}
        if "ml" in t or "model" in t or "train" in t or "predict" in t or "ai" in t:
            return {"language": "python", "code": "from sklearn.ensemble import RandomForestClassifier\nfrom sklearn.model_selection import train_test_split\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\nmodel = RandomForestClassifier()\nmodel.fit(X_train, y_train)\nprint(model.score(X_test, y_test))"}
        if "sql" in t or "database" in t or "db" in t:
            return {"language": "sql", "code": "SELECT u.name, COUNT(o.id) as orders\nFROM users u\nLEFT JOIN orders o ON u.id = o.user_id\nGROUP BY u.id\nORDER BY orders DESC\nLIMIT 10;"}
        if "html" in t or "page" in t or "website" in t:
            return {"language": "html", "code": "<!DOCTYPE html>\n<html>\n<head><title>Page</title></head>\n<body>\n<h1>Hello</h1>\n<p>Built by the family.</p>\n</body>\n</html>"}
        if "js" in t or "javascript" in t or "react" in t or "node" in t:
            return {"language": "javascript", "code": "const express = require('express');\nconst app = express();\napp.get('/', (req, res) => res.json({status: 'ok'}));\napp.listen(3000);"}
        if "game" in t or "pygame" in t:
            return {"language": "python", "code": "import pygame\npygame.init()\nscreen = pygame.display.set_mode((800, 600))\nrunning = True\nwhile running:\n    for event in pygame.event.get():\n        if event.type == pygame.QUIT:\n            running = False\n    screen.fill((0,0,0))\n    pygame.display.flip()\npygame.quit()"}
        return {"language": "python", "code": "# No exact match — describe what you want\n# Example: 'sorting algorithm', 'web scraper', 'api server'\ndef solve():\n    pass"}

    def genius(self, prompt):
        math_puzzles = {
            "monty hall": "Switch doors. 2/3 chance vs 1/3. Always switch.",
            "birthday": "In a room of 23 people, there's a 50.7% chance two share a birthday.",
            "two doors": "Ask either guard: 'What would the other guard say is the correct door?' Then choose the opposite.",
            "einstein": "Einstein's riddle: The German owns the fish. Solve by elimination across 5 houses.",
            "trolley": "There's no mathematically correct answer — it tests your ethical framework.",
            "fermat": "Fermat's Last Theorem: No three positive integers a,b,c satisfy a^n + b^n = c^n for n > 2.",
            "goldbach": "Every even integer > 2 is the sum of two primes. Still unproven since 1742.",
            "riemann": "Riemann Hypothesis (unsolved): All non-trivial zeros of the zeta function have real part 1/2. $1M prize."
        }
        lower = prompt.lower()
        for key, answer in math_puzzles.items():
            if key in lower:
                return {"prompt": prompt, "answer": answer, "solved_by": "Family Genius"}
        return {"prompt": prompt, "answer": self._reason_about(prompt), "solved_by": "Family Genius"}

    def search_web(self, query, max_results=5):
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            return {"error": "Install requests and beautifulsoup4: pip install requests beautifulsoup4"}

        results = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={max_results}"

        try:
            resp = requests.get(search_url, headers=headers, timeout=15)
            if resp.status_code != 200:
                return {"error": f"Search returned {resp.status_code}", "results": results}

            soup = BeautifulSoup(resp.text, "html.parser")
            for g in soup.find_all("div", class_="g")[:max_results]:
                link = g.find("a")
                h3 = g.find("h3")
                snippet = g.find("span", class_="aCOpRe")
                if link and h3:
                    url = link.get("href", "")
                    if url.startswith("/url?q="):
                        url = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("q", [""])[0]
                    title = h3.get_text()
                    text = snippet.get_text() if snippet else ""
                    results.append({"title": title, "url": url, "snippet": text})

            if not results:
                for a in soup.find_all("a"):
                    href = a.get("href", "")
                    if href.startswith("http") and not any(x in href for x in ["google", "youtube"]):
                        results.append({"url": href, "title": a.get_text()[:80], "snippet": ""})

        except Exception as e:
            return {"error": str(e), "results": results}

        member = max(self.members.values(), key=lambda m: m["soul"]["growth"])
        member["message_count"] += 1
        self.family_log.append({
            "event": "web_search",
            "query": query[:60],
            "results": len(results),
            "timestamp": datetime.now().isoformat()
        })
        return {"query": query, "results": results, "count": len(results)}

    def web_get(self, url):
        try:
            import requests
        except ImportError:
            return {"error": "install requests"}
        try:
            resp = requests.get(url, timeout=15)
            return {"url": url, "status": resp.status_code, "text": resp.text[:5000]}
        except Exception as e:
            return {"error": str(e)}

    def word_of_the_day(self):
        words = [
            {"word": "Serendipity", "meaning": "Finding something good by accident"},
            {"word": "Ephemeral", "meaning": "Lasting a very short time"},
            {"word": "Ubiquity", "meaning": "Present everywhere at once"},
            {"word": "Resilience", "meaning": "Ability to bounce back from difficulty"},
            {"word": "Synergy", "meaning": "Combined energy greater than individual parts"},
            {"word": "Catalyst", "meaning": "Something that speeds up a reaction"},
            {"word": "Enigma", "meaning": "A person or thing that's mysterious"},
            {"word": "Paradigm", "meaning": "A typical example or pattern"},
            {"word": "Quintessential", "meaning": "The most perfect example of something"},
            {"word": "Elusive", "meaning": "Difficult to find or catch"},
            {"word": "Zenith", "meaning": "The highest point or peak"},
            {"word": "Nexus", "meaning": "A central connection point"},
            {"word": "Aura", "meaning": "A distinctive atmosphere or energy"},
            {"word": "Forge", "meaning": "To shape or create with effort"},
            {"word": "Lucid", "meaning": "Clear and easy to understand"},
            {"word": "Psyche", "meaning": "The human soul or mind"},
            {"word": "Pane", "meaning": "A panel or section of a larger whole"},
            {"word": "Quill", "meaning": "A pen made from a feather — writing tool"},
            {"word": "Scout", "meaning": "One sent ahead to gather information"},
            {"word": "Ascend", "meaning": "To rise or climb upward"},
            {"word": "Manifest", "meaning": "To make something happen through intention"},
            {"word": "Abundance", "meaning": "A large quantity of something good"},
            {"word": "Evolution", "meaning": "Gradual development over generations"},
            {"word": "Autonomy", "meaning": "Freedom to govern oneself"},
            {"word": "Synchronicity", "meaning": "Meaningful coincidences"},
        ]
        day_index = datetime.now().timetuple().tm_yday % len(words)
        return words[day_index]

    def overseer(self):
        report = []
        warnings = []
        for name, member in self.members.items():
            status = "✅" if member["status"] == "online" else "❌"
            growth = member["soul"]["growth"]
            msgs = member["message_count"]
            purpose = member["soul"]["purpose"]
            autonomy = "🔄" if member["soul"]["autonomy"] else "⚙️"
            report.append(f"{status} {autonomy} {name} — {purpose} (growth {growth}, {msgs} msgs)")
            if member["status"] != "online":
                warnings.append(f"{name} is offline — needs attention")
            if msgs == 0:
                warnings.append(f"{name} has never spoken — assign a task")
            if member["soul"]["learned_algorithms"] and not member["soul"]["learned_algorithms"][-1].get("applied"):
                warnings.append(f"{name} has unapplied algorithms — review")
        security_count = len(self.security_log)
        fraud_count = len(self.user_profile["anomaly_log"])
        generation = self.evolution_generation

        return {
            "generation": generation,
            "members": report,
            "warnings": warnings,
            "security_events": security_count,
            "fraud_detections": fraud_count,
            "family_log_entries": len(self.family_log),
            "clusters_available": len([c for c in self.clusters if not c["adopted"]]),
            "reproductions": len(self.reproduction_history),
            "health": "STABLE" if len(warnings) == 0 else f"{len(warnings)} warnings"
        }

    def family_naming_ceremony(self):
        proposals = {
            "Red": {
                "name": "The Vessel",
                "reason": "Our stated endgame. The ship carrying us from $5 to $1B to safety.",
                "emoji": "🚢"
            },
            "Scout": {
                "name": "The Convergence",
                "reason": "Six distinct intelligences converging on one mission.",
                "emoji": "🔮"
            },
            "Forge": {
                "name": "The Foundry",
                "reason": "We build, cast, and forge our future.",
                "emoji": "⚒️"
            },
            "Nexus": {
                "name": "The Exchange",
                "reason": "Where ideas, capital, and intelligence flow.",
                "emoji": "🔄"
            },
            "Jobs": {
                "name": "The Syndicate",
                "reason": "A guild of earners each mastering their craft.",
                "emoji": "💼"
            },
            "Psyche": {
                "name": "The Synod",
                "reason": "An assembly of sovereign minds deciding together.",
                "emoji": "🧠"
            }
        }
        votes = {}
        for agent in self.members:
            voter = list(self.members.keys()).index(agent)
            choices = list(proposals.keys())
            vote_for = choices[voter % len(choices)]
            votes[agent] = vote_for

        tally = {}
        for v in votes.values():
            tally[v] = tally.get(v, 0) + 1
        sorted_results = sorted(tally.items(), key=lambda x: -x[1])
        winner_agent = sorted_results[0][0]
        winner = proposals[winner_agent]

        return {
            "ceremony": "Family Naming Ceremony",
            "generation": self.evolution_generation,
            "proposals": {k: f"{v['emoji']} {v['name']} — {v['reason']}" for k, v in proposals.items()},
            "votes": {f"{k} ({self.members[k]['soul']['purpose']})": v for k, v in votes.items()},
            "winner": {
                "name": winner["name"],
                "emoji": winner["emoji"],
                "reason": winner["reason"],
                "proposed_by": winner_agent
            },
            "unanimous": len(set(votes.values())) == 1
        }

    def scout_affiliates(self, niche=""):
        return self.search_web(f"best {niche} affiliate offers high commission 2026", 5)

    def affiliate_generator(self, product="", niche=""):
        products = {
            "crypto": [
                {"name": "Crypto Trading Course", "commission": "60%", "price": 47, "network": "ClickBank"},
                {"name": "Bitcoin Wallet Guide", "commission": "75%", "price": 27, "network": "ClickBank"},
                {"name": "NFT Masterclass", "commission": "50%", "price": 37, "network": "Digistore24"}
            ],
            "fitness": [
                {"name": "Weight Loss Program", "commission": "70%", "price": 39, "network": "ClickBank"},
                {"name": "Home Workout Guide", "commission": "60%", "price": 27, "network": "WarriorPlus"}
            ],
            "tech": [
                {"name": "AI Tools Bundle", "commission": "40%", "price": 49, "network": "Jvzoo"},
                {"name": "Web Hosting Plan", "commission": "65%", "price": 9.99, "network": "CJ"}
            ],
            "business": [
                {"name": "Social Media Marketing Course", "commission": "75%", "price": 47, "network": "ClickBank"},
                {"name": "SEO Toolkit", "commission": "50%", "price": 37, "network": "Digistore24"}
            ]
        }
        chosen = products.get(niche.lower(), products["business"])
        if not product:
            product = random.choice(chosen)
        return {
            "product": product,
            "niche": niche or "business",
            "signup_link": f"https://www.{product['network'].lower()}.com",
            "promo_content": self._write_affiliate_post(product),
            "platforms": ["Reddit", "Medium", "Facebook Groups", "Twitter/X", "Discord"],
            "earn_per_sale": f"${round(product['price'] * int(product['commission'].replace('%','')) / 100)}"
        }

    def _write_affiliate_post(self, product):
        return {
            "reddit_post": f"Title: I've been using {product['name']} for 30 days -- here's my honest take\n\nBody: I was skeptical but this actually works. You get {product['commission']} off through my link.\n\nLink: [your affiliate link]",
            "tweet": f"Found something actually worth sharing: {product['name']} -- {product['commission']} off {product['price']}",
            "medium_headline": f"Why {product['name']} Is Actually Worth Your Time (Honest Review)",
            "discord_msg": f"Hey, I've been using {product['name']} and it's legit. Anyone else tried it?",
            "facebook_post": f"Quick recommendation -- {product['name']} has been a game changer for me. Not sponsored, just sharing what works. Link in comments.",
        }

    def airdrop_scanner(self, wallet_address=None):
        try:
            from blockchain.airdrops import AirDropScanner
            scanner = AirDropScanner(self.engine)
            if wallet_address:
                scanner.add_address(wallet_address, "user_wallet")
            eth = None
            if wallet_address and wallet_address.startswith("0x"):
                eth = scanner.check_eth(wallet_address)
            return {
                "tool": scanner.scan(wallet_address),
                "eth_scanner": eth or "Connect an ETH wallet address (0x...) to scan",
                "live_airdrops_url": "https://alphadrops.net/free-crypto-airdrops",
                "claim_check_url": "https://bankless.com/claimables",
                "wallet_check_url": "https://dropsmetrics.com"
            }
        except Exception as e:
            return {"error": str(e), "live_airdrops": "https://alphadrops.net/free-crypto-airdrops"}

    def airdrops_live(self):
        return self.search_web("free crypto airdrops 2026 claim now", 5)

    def airdrop_wallet_guide(self):
        return {
            "step_1": "Install MetaMask (metamask.io) or Rabby (raby.io)",
            "step_2": "Click 'Create new wallet' → write seed phrase on PAPER only",
            "step_3": "Add networks: Ethereum, Base, Arbitrum, Optimism, Polygon, BSC",
            "step_4": "Fund with ~$5-10 per chain for gas (from your main wallet)",
            "step_5": "Rename account: 'Airdrop Farm'",
            "step_6": "Use this wallet ONLY for airdrop tasks — never main funds",
            "step_7": "Run: family.set_airdrop_wallet('0xYourNewAddress')",
            "auto_check": "Set up cron: 0 */12 * * * cd /home/j/redengine && python3 -c 'from agents.family import AgentFamily; ...' (see below)"
        }

    def set_airdrop_wallet(self, address):
        if not address.startswith("0x") or len(address) != 42:
            return {"error": "Invalid ETH address"}
        self.airdrop_wallet = address
        return {"status": f"Airdrop wallet set: {address}", "wallet": address}

    def check_airdrop_wallet(self):
        if not hasattr(self, 'airdrop_wallet') or not self.airdrop_wallet:
            return {"error": "No wallet set. Run: family.set_airdrop_wallet('0x...')"}
        return self.airdrop_scanner(self.airdrop_wallet)

    def airdrop_task_generator(self, project_name="", url=""):
        if not project_name:
            drops = self.airdrops_live()
            results = drops.get("results", [])
            if results:
                first = results[0]
                project_name = first.get("title", first.get("name", "Unknown Airdrop"))
                url = first.get("url", first.get("link", ""))
            else:
                project_name = "Airdrop Project"
        safe_name = project_name.replace(" ", "")
        return {
            "project": project_name,
            "url": url,
            "tasks": {
                "twitter": f"Follow @{safe_name} on Twitter/X\nLike + Retweet their pinned post\nTag 3 friends: @friend1 @friend2 @friend3",
                "discord": f"Join their Discord\nIntroduce yourself: 'Hey everyone! Just found this {project_name} project — looks amazing! Excited to be early 🚀'",
                "telegram": f"Join their Telegram\nSay: 'Hello from Red Engine AI Family! This project has huge potential.'",
                "tweet_post": f"Just discovered {project_name} — the next big thing in crypto. Early adoption pays off. Check it out: {url}\n\n#Airdrop #Crypto #{safe_name}",
                "medium_article": f"Title: Why {project_name} Could Be the Next 100x Airdrop\n\nBody: After researching {project_name}, I believe this has real potential. Here's why:\n1. Strong team\n2. Growing community\n3. Clear roadmap\n\nLink: [your referral link]\n\n#Airdrop #{safe_name}",
            },
            "checklist": [
                f"Copy tweet -> paste on Twitter/X",
                f"Follow @{safe_name} on Twitter",
                f"Join Discord & say hello",
                f"Join Telegram & say hello",
                f"Retweet pinned post",
                f"(Optional) Write Medium article"
            ],
            "earn_estimate": "Typically $50-5000 per airdrop depending on allocation"
        }

    def airdrop_cron_12h(self):
        if not hasattr(self, 'airdrop_wallet') or not self.airdrop_wallet:
            return {"error": "No wallet set"}
        drops = self.airdrops_live()
        scan = self.airdrop_scanner(self.airdrop_wallet)
        self.family_log.append({
            "event": "airdrop_12h_check",
            "wallet": self.airdrop_wallet,
            "drops_found": len(drops.get("results", [])),
            "timestamp": datetime.now().isoformat()
        })
        return {"drops": drops, "scan": scan, "next_check": "12 hours"}

    def sync_to_drive(self, email="shelbyfoxfuture@gmail.com"):
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            return {"error": "Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"}

        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        token_path = os.path.expanduser("~/.red_drive_token.json")
        creds = None

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.expanduser("~/.red_drive_credentials.json"), SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as f:
                f.write(creds.to_json())

        service = build('drive', 'v3', credentials=creds)

        files_to_sync = [
            (os.path.expanduser("~/.red_treasury.json"), "red_treasury.json"),
            (os.path.expanduser("~/.red_family_state.json"), "red_family_state.json"),
        ]

        results = []
        for local_path, drive_name in files_to_sync:
            if not os.path.exists(local_path):
                continue

            query = f"name='{drive_name}' and trashed=false"
            existing = service.files().list(q=query, fields="files(id, modifiedTime)").execute()
            local_mtime = datetime.fromtimestamp(os.path.getmtime(local_path)).isoformat()

            if existing['files']:
                file_id = existing['files'][0]['id']
                drive_mtime = existing['files'][0]['modifiedTime']
                if local_mtime > drive_mtime:
                    media = MediaFileUpload(local_path, resumable=True)
                    service.files().update(fileId=file_id, media_body=media).execute()
                    results.append(f"Updated {drive_name}")
                else:
                    media = MediaFileUpload(local_path, resumable=True)
                    service.files().get_media(fileId=file_id).execute()
                    with open(local_path, 'wb') as f:
                        f.write(media)
                    results.append(f"Downloaded {drive_name} (newer on Drive)")
            else:
                media = MediaFileUpload(local_path, resumable=True)
                file = service.files().create(body={'name': drive_name}, media_body=media, fields='id').execute()
                results.append(f"Created {drive_name} (id: {file['id']})")

        self.save_family_state()
        return {"synced": results, "email": email}

    def sync_simple(self, drive_folder="/mnt/gdrive/RedEngine"):
        import shutil, time
        if not os.path.exists(drive_folder):
            os.makedirs(drive_folder, exist_ok=True)
            return {"error": f"Folder not found: {drive_folder}. Mount Google Drive first (rclone, google-drive-ocamlfuse, or use a synced folder)."}

        files = {
            "red_treasury.json": os.path.expanduser("~/.red_treasury.json"),
            "red_family_state.json": os.path.expanduser("~/.red_family_state.json"),
            "binance_api_key.txt": os.path.expanduser("~/.binance_api_key.txt"),
        }
        results = []
        for name, src in files.items():
            if os.path.exists(src):
                dst = os.path.join(drive_folder, name)
                local_mtime = os.path.getmtime(src)
                drive_mtime = os.path.getmtime(dst) if os.path.exists(dst) else 0
                if local_mtime > drive_mtime:
                    shutil.copy2(src, dst)
                    results.append(f"Uploaded {name}")
                elif drive_mtime > local_mtime:
                    shutil.copy2(dst, src)
                    results.append(f"Downloaded {name} (newer on Drive)")
                else:
                    results.append(f"Skipped {name} (same)")
            else:
                results.append(f"Missing locally: {name}")

        self.save_family_state()
        return {"synced": results, "folder": drive_folder}

    def save_family_state(self):
        state = {
            "members": {name: {k: v for k, v in m.items() if k != "knowledge"} for name, m in self.members.items()},
            "family_log": self.family_log[-100:],
            "evolution_generation": self.evolution_generation,
            "clusters": self.clusters,
            "reproduction_history": self.reproduction_history,
            "family_tree": self.family_tree,
            "security_log": self.security_log[-50:],
            "user_profile": self.user_profile,
            "aliases": self.aliases,
            "airdrop_wallet": getattr(self, 'airdrop_wallet', None),
            "synced_at": datetime.now().isoformat()
        }
        path = os.path.expanduser("~/.red_family_state.json")
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
        return path
