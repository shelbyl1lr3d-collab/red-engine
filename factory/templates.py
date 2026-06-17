import os, json, random
from datetime import datetime

class GameTemplate:
    def __init__(self, engine):
        self.engine = engine
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(self.config_path) as f:
            self.cfg = json.load(f)

    def get_template(self, name):
        path = os.path.join(os.path.dirname(__file__), "templates", f"{name}.html")
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return f.read()

    def list_templates(self):
        tdir = os.path.join(os.path.dirname(__file__), "templates")
        files = [f.replace(".html", "") for f in os.listdir(tdir) if f.endswith(".html")]
        return files

    def generate_title(self):
        p = random.choice(self.cfg["title_generators"][0]["prefix"])
        m = random.choice(self.cfg["title_generators"][1]["middle"])
        s = random.choice(self.cfg["title_generators"][2]["suffix"])
        variants = [
            f"{p} {m}",
            f"{m} {s}",
            f"{p} {m}: {s}",
            f"{p} {s}",
            f"The {p} {m}"
        ]
        return random.choice(variants)

    def random_theme(self):
        return random.choice(self.cfg["theme_palettes"])

    def save_game_meta(self, game_name, template_used, theme, token_symbol, deploy_url):
        if "games" not in self.cfg:
            self.cfg["games"] = []
        self.cfg["games"].append({
            "name": game_name,
            "template": template_used,
            "theme": theme["name"],
            "token": token_symbol,
            "url": deploy_url,
            "created": datetime.now().isoformat()
        })
        with open(self.config_path, "w") as f:
            json.dump(self.cfg, f, indent=2)
