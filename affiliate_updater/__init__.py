import os, json, subprocess, shutil
from datetime import datetime
from typing import Dict, List

class AffiliateUpdater:
    def __init__(self, engine):
        self.engine = engine
        self.config = engine.config
        self.landing_page_dir = os.path.join(os.path.dirname(__file__), "..", "landing_page")
        self.backup_dir = os.path.join(self.landing_page_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def update_monthly_landing_page(self, new_links_list: Dict, video_path: str = None) -> Dict:
        """Update the monthly affiliate landing page with new links and video."""
        self.engine.log(f"AffiliateUpdater: Updating landing page with {len(new_links_list)} links")
        
        # Create backup
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        shutil.copytree(self.landing_page_dir, backup_path)
        
        # Generate HTML links
        links_html = ""
        for name, url in new_links_list.items():
            links_html += f'<a href="{url}" class="affiliate-btn" style="display:block; padding:15px; margin:10px; background:gold; color:black; font-weight:bold; text-align:center; text-decoration:none; border-radius:5px;">👉 {name}</a>\n'
        
        # Create video path
        video_src = "my_promo.mp4"
        if video_path and os.path.exists(video_path):
            shutil.copy(video_path, os.path.join(self.landing_page_dir, "my_promo.mp4"))
            video_src = "my_promo.mp4"
        
        # Construct the landing page
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head><title>My Special Recommendations</title></head>
        <body style="background:#121212; color:white; font-family:sans-serif; text-align:center; padding:20px;">
            <h1>Check Out This Month's Deals!</h1>
            <video width="640" height="360" controls style="border:3px solid gold; border-radius:10px;">
                <source src="{video_src}" type="video/mp4">
            </video>
            <div style="margin-top:30px; max-width:600px; margin-left:auto; margin-right:auto;">
                {links_html}
            </div>
        </body>
        </html>
        """
        
        # Write to landing page
        index_path = os.path.join(self.landing_page_dir, "index.html")
        with open(index_path, "w") as file:
            file.write(html_template)
        
        # Create/update manifest
        manifest = {
            "updated_at": datetime.now().isoformat(),
            "links_count": len(new_links_list),
            "video_path": video_src,
            "backup_created": backup_name
        }
        
        with open(os.path.join(self.landing_page_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        
        # Deploy to GitHub Pages
        deploy_result = self._deploy_to_github()
        
        return {
            "status": "success",
            "links_updated": len(new_links_list),
            "backup_created": backup_name,
            "deployed": deploy_result,
            "manifest": manifest
        }

    def _deploy_to_github(self) -> Dict:
        """Deploy updated landing page to GitHub Pages."""
        self.engine.log("AffiliateUpdater: Deploying to GitHub Pages")
        
        # Check if git is configured
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return {"status": "skipped", "reason": "GITHUB_TOKEN not configured"}
        
        try:
            # Commit and push
            subprocess.run(["git", "add", "."], cwd=self.landing_page_dir, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Monthly Affiliate Link Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"], 
                         cwd=self.landing_page_dir, check=True, capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=self.landing_page_dir, check=True, capture_output=True)
            
            return {"status": "success", "message": "Deployed to GitHub Pages"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Git deploy failed: {e.stderr.decode() if e.stderr else str(e)}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_manifest(self) -> Dict:
        """Get current landing page manifest."""
        manifest_path = os.path.join(self.landing_page_dir, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path) as f:
                return json.load(f)
        return {"status": "no_manifest"}