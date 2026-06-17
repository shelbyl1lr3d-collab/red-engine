import os, json, io, zipfile, time
from datetime import datetime

class NetlifyDeployer:
    def __init__(self, engine):
        self.engine = engine
        self.token = os.getenv("NETLIFY_AUTH_TOKEN", "")
        self.site_id = os.getenv("NETLIFY_SITE_ID", "")
        self.api = "https://api.netlify.com/api/v1"

    def is_configured(self):
        return bool(self.token)

    def deploy(self, game_dir, game_name, subdomain=None):
        """Deploy a game directory to Netlify as a zip deploy."""
        if not self.is_configured():
            return {"error": "NETLIFY_AUTH_TOKEN not set in environment"}

        import requests
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(game_dir):
                for fn in files:
                    fp = os.path.join(root, fn)
                    if ".env" in fn and fn != ".env.example":
                        continue
                    arcname = os.path.relpath(fp, game_dir)
                    zf.write(fp, arcname)

        zip_buffer.seek(0)
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/zip"
        }

        site_url = f"{self.api}/sites/{self.site_id}/deploys" if self.site_id else f"{self.api}/sites"
        try:
            resp = requests.post(site_url, headers=headers, data=zip_buffer.read(), timeout=30)
            if resp.status_code in [200, 201]:
                data = resp.json()
                url = data.get("ssl_url") or data.get("url") or data.get("site_url", "")
                deploy_id = data.get("id", "")
                self.engine.log(f"Netlify deploy: {game_name} → {url}")
                return {
                    "game": game_name,
                    "url": url,
                    "deploy_id": deploy_id,
                    "status": "deployed"
                }
            return {"error": f"Netlify deploy failed: {resp.status_code} - {resp.text[:200]}"}
        except Exception as e:
            return {"error": f"Netlify exception: {e}"}

    def deploy_zip(self, zip_path, game_name):
        """Deploy a pre-built zip file to Netlify."""
        if not self.is_configured():
            return {"error": "NETLIFY_AUTH_TOKEN not set"}

        import requests
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/zip"}
        site_url = f"{self.api}/sites/{self.site_id}/deploys" if self.site_id else f"{self.api}/sites"

        with open(zip_path, "rb") as f:
            data = f.read()

        try:
            resp = requests.post(site_url, headers=headers, data=data, timeout=30)
            if resp.status_code in [200, 201]:
                d = resp.json()
                url = d.get("ssl_url") or d.get("url") or d.get("site_url", "")
                return {"game": game_name, "url": url, "status": "deployed"}
            return {"error": f"Netlify deploy failed: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}
