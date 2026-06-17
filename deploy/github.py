import os, json, base64, time
from datetime import datetime

class GitHubDeployer:
    def __init__(self, engine):
        self.engine = engine
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.org = os.getenv("GITHUB_ORG", "red-engine")
        self.api = "https://api.github.com"
        self.headers = {}
        if self.token:
            self.headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }

    def is_configured(self):
        return bool(self.token)

    def create_repo(self, repo_name, private=False, description=""):
        """Create a new GitHub repository for a game."""
        if not self.is_configured():
            return {"error": "GITHUB_TOKEN not set in environment"}

        import requests
        data = {
            "name": repo_name,
            "private": private,
            "description": description or f"Red Engine game: {repo_name}",
            "auto_init": True,
            "license_template": "mit",
            "gitignore_template": "Python"
        }
        url = f"{self.api}/user/repos"
        try:
            resp = requests.post(url, json=data, headers=self.headers, timeout=15)
            if resp.status_code == 201:
                r = resp.json()
                self.engine.log(f"GitHub repo created: {r['full_name']} → {r['html_url']}")
                return {"name": r["name"], "full_name": r["full_name"], "url": r["html_url"], "clone_url": r["clone_url"]}
            elif resp.status_code == 422:
                # Repo may already exist
                existing = self.get_repo(repo_name)
                if existing:
                    return existing
            return {"error": f"GitHub API error {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"error": str(e)}

    def get_repo(self, repo_name):
        import requests
        url = f"{self.api}/repos/{self.org}/{repo_name}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                r = resp.json()
                return {"name": r["name"], "full_name": r["full_name"], "url": r["html_url"], "clone_url": r["clone_url"]}
        except Exception:
            pass
        return None

    def push_files(self, repo_name, files, commit_msg=None):
        """Push files to a GitHub repo using the API (no local git needed)."""
        if not self.is_configured():
            return {"error": "GITHUB_TOKEN not set"}

        import requests
        commit_msg = commit_msg or f"Red Engine deploy {datetime.now().isoformat()[:19]}"
        repo_path = f"{self.org}/{repo_name}"
        url = f"{self.api}/repos/{repo_path}/contents/"

        results = []
        for file_path, content in files.items():
            file_url = url + file_path
            encoded = base64.b64encode(content.encode() if isinstance(content, str) else content).decode()
            data = {
                "message": commit_msg,
                "content": encoded,
                "branch": "main"
            }
            try:
                resp = requests.put(file_url, json=data, headers=self.headers, timeout=15)
                if resp.status_code in [200, 201]:
                    results.append({"file": file_path, "status": "pushed"})
                elif resp.status_code == 422:
                    # File exists, update it
                    existing = requests.get(file_url, headers=self.headers, timeout=10)
                    if existing.status_code == 200:
                        data["sha"] = existing.json().get("sha")
                        resp = requests.put(file_url, json=data, headers=self.headers, timeout=15)
                        if resp.status_code in [200, 201]:
                            results.append({"file": file_path, "status": "updated"})
                        else:
                            results.append({"file": file_path, "status": f"update failed: {resp.status_code}"})
                    else:
                        results.append({"file": file_path, "status": f"error: {resp.status_code}"})
                else:
                    results.append({"file": file_path, "status": f"error: {resp.status_code}"})
            except Exception as e:
                results.append({"file": file_path, "status": f"exception: {e}"})

        return {"repo": repo_name, "files_pushed": len(results), "results": results}

    def enable_pages(self, repo_name, branch="main", path="/"):
        """Enable GitHub Pages for a repo."""
        if not self.is_configured():
            return {"error": "GITHUB_TOKEN not set"}

        import requests
        url = f"{self.api}/repos/{self.org}/{repo_name}/pages"
        data = {"source": {"branch": branch, "path": path}}
        try:
            resp = requests.post(url, json=data, headers=self.headers, timeout=15)
            if resp.status_code in [200, 201]:
                r = resp.json()
                return {"pages_url": r.get("html_url") or r.get("url"), "status": "enabled"}
            elif resp.status_code == 409:
                return {"pages_url": f"https://{self.org}.github.io/{repo_name}", "status": "already enabled"}
            return {"error": f"Pages error {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"error": str(e)}

    def deploy_game(self, game_name, game_dir):
        """Full deploy: create repo, push files, enable Pages."""
        repo_name = game_name.lower().replace(" ", "-").replace("_", "-")
        repo_name = "".join(c for c in repo_name if c.isalnum() or c in "-")[:50]

        files = {}
        for root, dirs, fnames in os.walk(game_dir):
            for fn in fnames:
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, game_dir)
                with open(fp) as f:
                    files[rel] = f.read()

        env_template = files.pop(".env.template", None)
        if env_template:
            files[".env.example"] = env_template

        repo = self.create_repo(repo_name, private=False, description=f"Red Engine game: {game_name}")
        if "error" in repo:
            return repo

        push = self.push_files(repo_name, files)
        pages = self.enable_pages(repo_name)

        deploy_url = pages.get("pages_url") or repo.get("url", "")

        self.engine.log(f"Deployed {game_name} → {deploy_url}")

        return {
            "game": game_name,
            "repo": repo["full_name"],
            "repo_url": repo["url"],
            "deploy_url": deploy_url,
            "files": push["files_pushed"],
            "pages": pages.get("status")
        }
