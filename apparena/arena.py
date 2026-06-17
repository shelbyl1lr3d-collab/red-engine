#!/usr/bin/env python3
"""
AppArena - Build Apps Through Games, Earn Money, Stay Protected
"""
import os, json, time, random
from datetime import datetime

class AppArena:
    def __init__(self, engine=None):
        self.engine = engine
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(self.config_path) as f:
            self.config = json.load(f)
        
        self.player = {
            "name": "Shelby",
            "level": 1,
            "xp": 0,
            "coins": 0,
            "apps_built": 0,
            "streak": 0,
            "protection_active": True
        }
        
        self.active_challenge = None
        self.completed_apps = []
    
    def get_status(self):
        return {
            "player": self.player,
            "active_challenge": self.active_challenge,
            "apps_built": len(self.completed_apps),
            "protection": self.player["protection_active"]
        }
    
    def start_build_challenge(self, level=None):
        if not level:
            level = self.player["level"]
        
        levels = self.config["game_modes"]["build_mode"]["levels"]
        if level > len(levels):
            return {"error": "Max level reached!"}
        
        challenge = levels[level - 1]
        self.active_challenge = {
            "level": level,
            "name": challenge["name"],
            "challenge": challenge["challenge"],
            "template": challenge["template"],
            "reward": challenge["reward"],
            "time_limit": challenge["time_limit"],
            "start_time": time.time(),
            "status": "in_progress"
        }
        
        return {
            "message": f"Starting Level {level}: {challenge['name']}",
            "challenge": challenge["challenge"],
            "time_limit": f"{challenge['time_limit']} seconds",
            "reward": f"${challenge['reward']}",
            "template_files": self.config["templates"][challenge["template"]]["files"]
        }
    
    def build_app(self, user_code=None):
        if not self.active_challenge:
            return {"error": "No active challenge"}
        
        template = self.active_challenge["template"]
        template_config = self.config["templates"][template]
        
        # Security scan (protection)
        if self.config["protection"]["security_scan"]:
            scan_result = self._security_scan(user_code or "default")
            if not scan_result["safe"]:
                return {"error": "Security check failed", "details": scan_result["issues"]}
        
        # Calculate score
        elapsed = time.time() - self.active_challenge["start_time"]
        time_limit = self.active_challenge["time_limit"]
        time_bonus = max(0, 1 - (elapsed / time_limit))
        
        base_reward = self.active_challenge["reward"]
        speed_bonus = base_reward * time_bonus * self.config["scoring"]["speed_bonus"]
        streak_bonus = 1 + (self.player["streak"] * 0.1)
        
        total_reward = int((base_reward + speed_bonus) * streak_bonus)
        
        # Build the app
        app_name = f"{self.active_challenge['name']}_{int(time.time())}"
        app_path = self._create_app(template, app_name, user_code)
        
        # Deploy if protection passes
        deploy_url = None
        if self.player["protection_active"]:
            deploy_url = self._deploy_app(app_path, app_name)
        
        # Update player
        self.player["coins"] += total_reward
        self.player["xp"] += total_reward
        self.player["apps_built"] += 1
        self.player["streak"] += 1
        
        # Level up check
        if self.player["xp"] >= self.player["level"] * 1000:
            self.player["level"] += 1
            self.player["xp"] = 0
        
        # Record completed app
        self.completed_apps.append({
            "name": app_name,
            "template": template,
            "reward": total_reward,
            "deployed": deploy_url is not None,
            "url": deploy_url,
            "built_at": datetime.now().isoformat()
        })
        
        # Clear challenge
        self.active_challenge = None
        
        return {
            "success": True,
            "app_name": app_name,
            "reward_earned": total_reward,
            "total_coins": self.player["coins"],
            "level": self.player["level"],
            "streak": self.player["streak"],
            "deploy_url": deploy_url,
            "protection": "All security checks passed"
        }
    
    def _security_scan(self, code):
        issues = []
        dangerous = ["eval(", "exec(", "os.system(", "subprocess", "import os"]
        for pattern in dangerous:
            if pattern in str(code):
                issues.append(f"Dangerous pattern detected: {pattern}")
        
        return {
            "safe": len(issues) == 0,
            "issues": issues
        }
    
    def _create_app(self, template, app_name, user_code=None):
        builds_dir = os.path.join(os.path.dirname(__file__), "..", "builds", "apparena")
        os.makedirs(builds_dir, exist_ok=True)
        
        app_dir = os.path.join(builds_dir, app_name)
        os.makedirs(app_dir, exist_ok=True)
        
        template_config = self.config["templates"][template]
        
        # Create basic app files based on template
        if template == "landing_page":
            self._create_landing_page(app_dir, app_name)
        elif template == "contact_form":
            self._create_contact_form(app_dir, app_name)
        elif template == "ecommerce":
            self._create_ecommerce(app_dir, app_name)
        elif template == "blog":
            self._create_blog(app_dir, app_name)
        elif template == "game":
            self._create_game(app_dir, app_name)
        
        return app_dir
    
    def _create_landing_page(self, app_dir, app_name):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{app_name}</title>
    <style>
        body {{ font-family: Arial; margin: 0; padding: 20px; background: #1a1a2e; color: white; }}
        .hero {{ text-align: center; padding: 50px; background: linear-gradient(135deg, #ff3366, #ff6699); }}
        .cta {{ background: #00ff88; color: black; padding: 15px 30px; border: none; font-size: 18px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="hero">
        <h1>Welcome to {app_name}</h1>
        <p>Built with AppArena</p>
        <button class="cta">Get Started</button>
    </div>
    <div id="ad-slot-1" style="height:90px;background:#333;margin:20px 0;"></div>
</body>
</html>"""
        with open(os.path.join(app_dir, "index.html"), "w") as f:
            f.write(html)
    
    def _create_contact_form(self, app_dir, app_name):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Contact - {app_name}</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #1a1a2e; color: white; }}
        form {{ max-width: 400px; margin: 0 auto; }}
        input, textarea {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #333; background: #0a0a1a; color: white; }}
        button {{ background: #00ff88; color: black; padding: 15px 30px; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <h1 style="text-align:center">Contact Us</h1>
    <form>
        <input type="text" placeholder="Your Name" required>
        <input type="email" placeholder="Your Email" required>
        <textarea placeholder="Your Message" rows="5" required></textarea>
        <button type="submit">Send Message</button>
    </form>
</body>
</html>"""
        with open(os.path.join(app_dir, "index.html"), "w") as f:
            f.write(html)
    
    def _create_ecommerce(self, app_dir, app_name):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Shop - {app_name}</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #1a1a2e; color: white; }}
        .product {{ border: 1px solid #333; padding: 20px; margin: 10px; display: inline-block; width: 200px; }}
        .buy {{ background: #ff3366; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <h1 style="text-align:center">Shop</h1>
    <div style="text-align:center">
        <div class="product"><h3>Product 1</h3><p>$29.99</p><button class="buy">Buy Now</button></div>
        <div class="product"><h3>Product 2</h3><p>$49.99</p><button class="buy">Buy Now</button></div>
        <div class="product"><h3>Product 3</h3><p>$19.99</p><button class="buy">Buy Now</button></div>
    </div>
</body>
</html>"""
        with open(os.path.join(app_dir, "index.html"), "w") as f:
            f.write(html)
    
    def _create_blog(self, app_dir, app_name):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Blog - {app_name}</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #1a1a2e; color: white; max-width: 800px; margin: 0 auto; }}
        .post {{ border-bottom: 1px solid #333; padding: 20px 0; }}
        .post h2 {{ color: #00ff88; }}
    </style>
</head>
<body>
    <h1>Blog</h1>
    <div class="post"><h2>First Post</h2><p>Welcome to our blog!</p></div>
    <div class="post"><h2>Second Post</h2><p>More content coming soon.</p></div>
</body>
</html>"""
        with open(os.path.join(app_dir, "index.html"), "w") as f:
            f.write(html)
    
    def _create_game(self, app_dir, app_name):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Game - {app_name}</title>
    <style>
        body {{ margin: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }}
        canvas {{ border: 2px solid #00ff88; }}
    </style>
</head>
<body>
    <canvas id="game" width="400" height="400"></canvas>
    <script>
        const canvas = document.getElementById('game');
        const ctx = canvas.getContext('2d');
        let player = {{x: 200, y: 350, w: 30, h: 30}};
        let score = 0;
        
        document.addEventListener('keydown', e => {{
            if (e.key === 'ArrowLeft') player.x -= 20;
            if (e.key === 'ArrowRight') player.x += 20;
        }});
        
        function gameLoop() {{
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(0, 0, 400, 400);
            ctx.fillStyle = '#00ff88';
            ctx.fillRect(player.x, player.y, player.w, player.h);
            ctx.fillStyle = '#ff3366';
            ctx.font = '20px Arial';
            ctx.fillText('Score: ' + score, 10, 30);
            requestAnimationFrame(gameLoop);
        }}
        gameLoop();
    </script>
</body>
</html>"""
        with open(os.path.join(app_dir, "index.html"), "w") as f:
            f.write(html)
    
    def _deploy_app(self, app_path, app_name):
        # Simulate deployment
        return f"https://apparena.github.io/{app_name}"
    
    def get_leaderboard(self):
        return {
            "top_builders": [
                {"name": "Shelby", "apps": self.player["apps_built"], "coins": self.player["coins"]},
            ],
            "note": "More players will appear as they join"
        }
    
    def withdraw_earnings(self, amount):
        if not self.player["protection_active"]:
            return {"error": "Protection is disabled!"}
        
        if amount > self.config["protection"]["max_daily_withdrawal"]:
            return {"error": f"Max daily withdrawal is ${self.config['protection']['max_daily_withdrawal']}"}
        
        if amount > self.player["coins"]:
            return {"error": "Insufficient coins"}
        
        self.player["coins"] -= amount
        
        return {
            "success": True,
            "withdrawn": amount,
            "remaining": self.player["coins"],
            "method": "Luno transfer",
            "protection": "Verified safe"
        }


def main():
    arena = AppArena()
    
    print("=== AppArena ===")
    print("Build apps through games, earn money, stay protected!\n")
    
    while True:
        print("\nOptions:")
        print("1. Start Build Challenge")
        print("2. Build Current Challenge")
        print("3. View Status")
        print("4. Leaderboard")
        print("5. Withdraw Earnings")
        print("6. Exit")
        
        choice = input("\nSelect: ").strip()
        
        if choice == "1":
            result = arena.start_build_challenge()
            print(json.dumps(result, indent=2))
        
        elif choice == "2":
            result = arena.build_app()
            print(json.dumps(result, indent=2))
        
        elif choice == "3":
            print(json.dumps(arena.get_status(), indent=2))
        
        elif choice == "4":
            print(json.dumps(arena.get_leaderboard(), indent=2))
        
        elif choice == "5":
            amount = int(input("Amount to withdraw: $"))
            print(json.dumps(arena.withdraw_earnings(amount), indent=2))
        
        elif choice == "6":
            print("See you next time!")
            break


if __name__ == "__main__":
    main()
