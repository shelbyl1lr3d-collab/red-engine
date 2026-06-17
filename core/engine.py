import os, sys, json, threading, time
from datetime import datetime
from .config import Config

class RedEngine:
    def __init__(self):
        self.config = Config()
        self.config.load()
        self._running = False
        self._modules = {}
        self._events = []
        self._log_callback = None

    def log(self, message, level="info"):
        entry = {
            "time": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self._events.append(entry)
        if len(self._events) > 1000:
            self._events = self._events[-500:]
        if self._log_callback:
            self._log_callback(message, level)

    def set_log_callback(self, cb):
        self._log_callback = cb

    def register(self, name, module):
        self._modules[name] = module
        self.log(f"Module registered: {name}")

    def get(self, name):
        return self._modules.get(name)

    def start(self):
        self._running = True
        self.log("Red Engine V2 — Starting all systems")
        for name, mod in self._modules.items():
            if hasattr(mod, "start"):
                try:
                    mod.start()
                    self.log(f"{name} started")
                except Exception as e:
                    self.log(f"{name} failed to start: {e}", "error")

    def stop(self):
        self._running = False
        self.log("Red Engine — Shutting down")
        for name, mod in self._modules.items():
            if hasattr(mod, "stop"):
                try:
                    mod.stop()
                except Exception as e:
                    self.log(f"{name} stop error: {e}", "error")

    @property
    def status(self):
        return {
            "running": self._running,
            "modules": list(self._modules.keys()),
            "uptime": "running",
            "version": self.config.get("version"),
            "goal": self.config.get("goal_usd"),
            "events_tracked": len(self._events)
        }

    def command(self, cmd, **kwargs):
        """Route a command to the appropriate module."""
        cmd_map = {
            "status": lambda: self.status,
            "chat": lambda: self._modules.get("agents").chat(kwargs.get("member", "Red"), kwargs.get("message", "hello")),
            "forge": lambda: self._modules.get("factory").forge(kwargs.get("theme"), kwargs.get("name")),
            "deploy": lambda: self._modules.get("deploy").deploy_all(),
            "trade": lambda: self._modules.get("exchange").trade(**kwargs),
            "treasury": lambda: self._modules.get("treasury").report(),
            "tournament": lambda: self._modules.get("tournament").run_round(),
            "youtube": lambda: self._modules.get("media").handle(**kwargs),
            "milestone_check": lambda: self._modules.get("gateway").check_milestone(),
        }
        handler = cmd_map.get(cmd)
        if handler:
            return handler()
        return {"error": f"Unknown command: {cmd}"}

    def get_logs(self, count=50):
        return self._events[-count:]
