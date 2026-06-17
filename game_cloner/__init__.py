import os, json, shutil, subprocess
from datetime import datetime
from typing import Dict, Optional, List

class GameCloner:
    def __init__(self, engine):
        self.engine = engine
        self.config = engine.config
        self.games_dir = os.path.join(os.path.dirname(__file__), "..", "games")
        os.makedirs(self.games_dir, exist_ok=True)

    def clone_and_retheme_game(self, template_repo_url: str, output_game_name: str, 
                             new_character_img: str, new_bg_img: str, 
                             inject_ads: bool = True) -> Dict:
        """Clone a game template and retheme it with custom assets."""
        self.engine.log(f"GameCloner: Cloning '{output_game_name}' from {template_repo_url}")
        
        target_folder = os.path.join(self.games_dir, output_game_name)
        
        # 1. Download the game template if it doesn't exist yet
        if not os.path.exists(target_folder):
            self.engine.log("GameCloner: Downloading clean game template from GitHub...")
            os.makedirs(self.games_dir, exist_ok=True)
            
            # Clone using git
            result = subprocess.run(["git", "clone", template_repo_url, target_folder], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return {"error": f"Failed to clone template: {result.stderr}"}
            
            # Remove old git history
            git_dir = os.path.join(target_folder, ".git")
            if os.path.exists(git_dir):
                shutil.rmtree(git_dir, ignore_errors=True)
        
        # 2. SWAP THE VISUAL THEME FILES
        self.engine.log("GameCloner: Swapping graphics for custom theme...")
        
        # Copy character sprite
        if os.path.exists(new_character_img):
            shutil.copy(new_character_img, os.path.join(target_folder, "assets", "hero.png"))
        
        # Copy background
        if os.path.exists(new_bg_img):
            shutil.copy(new_bg_img, os.path.join(target_folder, "assets", "background.png"))
        
        # 3. INJECT AD REVENUE BANNER
        if inject_ads:
            self._inject_ad_banner(target_folder)
        
        # 4. Update game metadata
        self._update_game_metadata(target_folder, output_game_name)
        
        self.engine.log(f"GameCloner: Game '{output_game_name}' successfully re-themed!")
        
        return {
            "game_name": output_game_name,
            "path": target_folder,
            "template_repo": template_repo_url,
            "character_image": new_character_img,
            "background_image": new_bg_img,
            "ads_injected": inject_ads,
            "timestamp": datetime.now().isoformat()
        }

    def _inject_ad_banner(self, game_dir: str):
        """Inject ad revenue banner into the game HTML."""
        index_path = os.path.join(game_dir, "index.html")
        
        # Get ad client ID from config
        ad_client_id = self.config.get("ad_client_id_secret") or os.getenv("AD_CLIENT_ID_SECRET")
        
        ad_code = f"""
        <div id="game-ad" style="text-align:center; padding:5px; background:#000;">
            <script src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
            <ins class="adsbygoogle" style="display:inline-block;width:320;height:50" 
                 data-ad-client="{ad_client_id}"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({{}})</script>
        </div>
        """
        
        if os.path.exists(index_path):
            with open(index_path, "r") as file:
                html_content = file.read()
            
            if "game-ad" not in html_content:
                html_content = html_content.replace("<body>", f"<body>\n{ad_code}")
                with open(index_path, "w") as file:
                    file.write(html_content)

    def _update_game_metadata(self, game_dir: str, game_name: str):
        """Update game metadata and config files."""
        config_path = os.path.join(game_dir, "config.json")
        
        metadata = {
            "name": game_name,
            "cloned_from_template": True,
            "cloned_at": datetime.now().isoformat(),
            "engine_version": "Red Engine V2",
            "ads_enabled": True,
            "last_updated": datetime.now().isoformat()
        }
        
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                existing_config = json.load(f)
            
            existing_config.update(metadata)
            
            with open(config_path, "w") as f:
                json.dump(existing_config, f, indent=2)
        else:
            with open(config_path, "w") as f:
                json.dump(metadata, f, indent=2)

    def list_cloned_games(self) -> List[str]:
        """List all cloned games."""
        if os.path.exists(self.games_dir):
            return [d for d in os.listdir(self.games_dir) 
                   if os.path.isdir(os.path.join(self.games_dir, d))]
        return []