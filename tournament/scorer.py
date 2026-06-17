import json, os
from datetime import datetime

class PerformanceScorer:
    def __init__(self, engine):
        self.engine = engine
        self.file = os.path.expanduser("~/.red_performance.json")

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                return json.load(f)
        return {"agents": {}}

    def _save(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=2)

    def record(self, agent_name, metric, value):
        data = self._load()
        if agent_name not in data["agents"]:
            data["agents"][agent_name] = {
                "first_seen": datetime.now().isoformat(),
                "metrics": {}
            }
        if metric not in data["agents"][agent_name]["metrics"]:
            data["agents"][agent_name]["metrics"][metric] = []
        data["agents"][agent_name]["metrics"][metric].append({
            "value": value,
            "time": datetime.now().isoformat()
        })
        if len(data["agents"][agent_name]["metrics"][metric]) > 1000:
            data["agents"][agent_name]["metrics"][metric] = data["agents"][agent_name]["metrics"][metric][-500:]
        self._save(data)

    def get_scores(self, agent_name=None):
        data = self._load()
        if agent_name:
            return data["agents"].get(agent_name, {})
        return data["agents"]

    def average(self, agent_name, metric, window=10):
        data = self._load()
        if agent_name not in data["agents"]:
            return 0
        if metric not in data["agents"][agent_name]["metrics"]:
            return 0
        vals = [m["value"] for m in data["agents"][agent_name]["metrics"][metric][-window:]]
        return sum(vals) / max(len(vals), 1)

    def leaderboard(self, metric="score"):
        data = self._load()
        scores = []
        for agent, info in data["agents"].items():
            if metric in info.get("metrics", {}):
                recent = info["metrics"][metric][-5:]
                avg = sum(m["value"] for m in recent) / max(len(recent), 1)
                scores.append({"agent": agent, "avg": round(avg, 2), "samples": len(info["metrics"][metric])})
        return sorted(scores, key=lambda x: x["avg"], reverse=True)
