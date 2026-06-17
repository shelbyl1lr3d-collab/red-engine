import os, json
from pathlib import Path

class Config:
    _instance = None
    _data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self, path=None):
        if self._loaded:
            return
        path = path or os.path.join(os.path.dirname(__file__), "..", "config", "default.json")
        with open(path) as f:
            self._data = json.load(f)
        self._data.update(self._load_env_overrides())
        self._loaded = True

    def _load_env_overrides(self):
        overrides = {}
        family = self._data.get("family", {}).get("members", [])
        for i, m in enumerate(family):
            key = f"AGENT_{m['name'].upper()}_KEY"
            val = os.getenv(key)
            if val:
                if "agents" not in overrides:
                    overrides["agents"] = {}
                overrides["agents"][m["name"]] = {"api_key": val}
        return overrides

    def get(self, key, default=None):
        parts = key.split(".")
        val = self._data
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                return default
        return val if val is not None else default

    def set(self, key, value):
        parts = key.split(".")
        target = self._data
        for p in parts[:-1]:
            if p not in target:
                target[p] = {}
            target = target[p]
        target[parts[-1]] = value

    def save(self, path=None):
        path = path or os.path.join(os.path.dirname(__file__), "..", "config", "default.json")
        with open(path, "w") as f:
            json.dump(self._data, f, indent=2)

    @property
    def data(self):
        return self._data
