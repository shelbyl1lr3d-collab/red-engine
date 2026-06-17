import os, json, random, string, io, zipfile
from datetime import datetime
from .templates import GameTemplate

class ReskinEngine:
    def __init__(self, engine):
        self.engine = engine
        self.templates = GameTemplate(engine)
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "builds")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "assets"), exist_ok=True)

    def generate_symbol(self, name):
        words = name.replace(":", "").replace("-", " ").split()
        sym = "".join(w[0].upper() for w in words if w)[:4]
        if len(sym) < 2:
            sym = (name[:2].upper() + random.choice(string.ascii_uppercase))[:4]
        return sym

    def reskin(self, template_name=None, theme_name=None, custom_title=None):
        """Generate a fully reskinned game from template."""
        config = self.engine.config
        available = self.templates.list_templates()
        if not available:
            return {"error": "No templates available"}

        template_name = template_name or random.choice(available)
        if template_name not in available:
            return {"error": f"Template '{template_name}' not found. Available: {available}"}

        html = self.templates.get_template(template_name)
        if not html:
            return {"error": f"Failed to load template: {template_name}"}

        title = custom_title or self.templates.generate_title()
        theme = self._get_theme(theme_name) if theme_name else self.templates.random_theme()
        symbol = self.generate_symbol(title)

        game_params = {
            "CANVAS_W": "400", "CANVAS_H": random.choice(["500", "600", "400"]),
            "PLAYER_W": "30", "PLAYER_H": "30",
            "GRAVITY": "0.5", "JUMP_FORCE": "-8",
            "OBSTACLE_SPEED": "3",
            "SPAWN_RATE": "80",
            "OBSTACLE_W": "25",
            "OBSTACLE_MIN_H": "40", "OBSTACLE_MAX_H": "120",
            "GROUND_H": "60"
        }

        params = {
            "GAME_TITLE": title,
            "TOKEN_SYMBOL": symbol,
            "PRIMARY_COLOR": theme["primary"],
            "SECONDARY_COLOR": theme["secondary"],
            "BG_COLOR": theme["bg"],
            "ACCENT_COLOR": theme.get("accent", theme["primary"]),
            "AD_CODE": "",
        }
        params.update(game_params)

        game_config = {
            "title": title,
            "template": template_name,
            "theme": theme["name"],
            "token": symbol,
            "params": game_params,
            "version": "2.0",
            "engine": "Red Engine V2"
        }
        params["GAME_CONFIG_JSON"] = json.dumps(game_config)

        for key, val in params.items():
            html = html.replace(f"%{key}%", str(val))

        game_dir = os.path.join(self.output_dir, f"{title.replace(' ', '_').replace(':', '')[:40]}")
        os.makedirs(game_dir, exist_ok=True)

        with open(os.path.join(game_dir, "index.html"), "w") as f:
            f.write(html)

        with open(os.path.join(game_dir, "config.json"), "w") as f:
            json.dump(game_config, f, indent=2)

        with open(os.path.join(game_dir, ".env.template"), "w") as f:
            f.write(f"# {title} - Environment Variables\n# Never commit this file to git!\n# Game-specific API keys here\n")

        self.templates.save_game_meta(title, template_name, theme, symbol, f"file://{game_dir}")

        self.engine.log(f"Reskinned game: {title} ({symbol}) from template '{template_name}' with theme '{theme['name']}'")

        return {
            "title": title,
            "template": template_name,
            "theme": theme["name"],
            "token_symbol": symbol,
            "path": game_dir,
            "files": ["index.html", "config.json", ".env.template"],
            "params": game_params
        }

    def _get_theme(self, name):
        themes = self.templates.random_theme()
        with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
            cfg = json.load(f)
        for t in cfg["theme_palettes"]:
            if t["name"] == name:
                return t
        return themes

    def batch_reskin(self, count=5):
        """Generate multiple reskinned games in batch."""
        results = []
        for i in range(count):
            result = self.reskin()
            results.append(result)
        return results

    def create_asset_package(self, game_dir):
        """Create a deployable zip of the game."""
        zip_path = f"{game_dir}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(game_dir):
                for fn in files:
                    fp = os.path.join(root, fn)
                    zf.write(fp, os.path.relpath(fp, os.path.dirname(game_dir)))
        return zip_path
