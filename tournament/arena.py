import os, json, random, threading, time
from datetime import datetime

class TournamentArena:
    def __init__(self, engine):
        self.engine = engine
        self.file = os.path.expanduser("~/.red_tournament.json")
        self._running = False
        self._thread = None

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                return json.load(f)
        return {
            "rounds": [],
            "leaderboard": {},
            "total_rounds": 0,
            "current_season": 1
        }

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def run_round(self, agents=None):
        """Execute one tournament round where AI agents compete."""
        data = self._load()
        family = self.engine.config.get("family.members", [])
        agents = agents or [m["name"] for m in family]

        if len(agents) < 2:
            return {"error": "Need at least 2 agents to compete"}

        round_num = data["total_rounds"] + 1
        season = data["current_season"]

        # Simulate agent performance in a round
        scores = {}
        for agent in agents:
            base = random.uniform(50, 100)
            consistency = random.uniform(0.7, 1.3)
            luck = random.uniform(0.8, 1.2)
            score = round(base * consistency * luck, 2)
            scores[agent] = max(0, score)

        # Rank them
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard = {}
        for i, (agent, score) in enumerate(ranked):
            leaderboard[agent] = {
                "rank": i + 1,
                "score": score,
                "wins": data.get("leaderboard", {}).get(agent, {}).get("wins", 0) + (1 if i == 0 else 0),
                "total_score": data.get("leaderboard", {}).get(agent, {}).get("total_score", 0) + score,
                "rounds": data.get("leaderboard", {}).get(agent, {}).get("rounds", 0) + 1
            }

        # Token rewards
        token_rewards = {}
        total_liquidity = len(agents) * 100
        for i, (agent, score) in enumerate(ranked):
            share = int(total_liquidity * (len(agents) - i) / sum(range(1, len(agents) + 1)))
            token_rewards[agent] = share

        round_data = {
            "round": round_num,
            "season": season,
            "scores": scores,
            "rankings": [(a, s) for a, s in ranked],
            "token_rewards": token_rewards,
            "winner": ranked[0][0] if ranked else None,
            "time": datetime.now().isoformat()
        }

        data["rounds"].append(round_data)
        data["leaderboard"] = leaderboard
        data["total_rounds"] = round_num
        if len(data["rounds"]) > 100:
            data["rounds"] = data["rounds"][-100:]
        self._save(data)

        self.engine.log(f"Tournament Round {round_num}: {ranked[0][0]} wins with {ranked[0][1]:.1f} pts")

        return {
            "round": round_num,
            "season": season,
            "winner": round_data["winner"],
            "scores": scores,
            "rankings": round_data["rankings"],
            "token_rewards": token_rewards,
            "leaderboard": leaderboard
        }

    def get_leaderboard(self):
        data = self._load()
        sorted_leaderboard = sorted(
            data.get("leaderboard", {}).items(),
            key=lambda x: x[1]["total_score"],
            reverse=True
        )
        return {
            "season": data["current_season"],
            "rounds": data["total_rounds"],
            "leaderboard": [
                {
                    "name": agent,
                    "rank": i + 1,
                    "total_score": stats["total_score"],
                    "wins": stats["wins"],
                    "rounds": stats["rounds"],
                    "avg_score": round(stats["total_score"] / max(stats["rounds"], 1), 2)
                }
                for i, (agent, stats) in enumerate(sorted_leaderboard)
            ]
        }

    def start_auto_tournament(self, interval_seconds=300):
        """Run tournament rounds automatically on a timer."""
        if self._running:
            return {"error": "Tournament already running"}

        self._running = True
        self._thread = threading.Thread(target=self._auto_loop, args=(interval_seconds,), daemon=True)
        self._thread.start()
        self.engine.log(f"Auto tournament started: every {interval_seconds}s")
        return {"status": "started", "interval": interval_seconds}

    def stop_auto_tournament(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.engine.log("Auto tournament stopped")
        return {"status": "stopped"}

    def _auto_loop(self, interval):
        while self._running:
            try:
                self.run_round()
            except Exception as e:
                self.engine.log(f"Tournament round error: {e}", "error")
            time.sleep(interval)

    def summary(self):
        data = self._load()
        return {
            "total_rounds": data["total_rounds"],
            "current_season": data["current_season"],
            "running": self._running,
            "leaderboard_count": len(data.get("leaderboard", {})),
            "last_round": data["rounds"][-1] if data["rounds"] else None
        }
