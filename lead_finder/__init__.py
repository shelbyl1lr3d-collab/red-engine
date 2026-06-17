import os, json, requests
from datetime import datetime
from typing import Dict, List, Optional

class LeadFinder:
    def __init__(self, engine):
        self.engine = engine
        self.config = engine.config
        self.results_file = os.path.join(os.path.dirname(__file__), "leads_cache.json")
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.results_file):
            with open(self.results_file) as f:
                self.cache = json.load(f)
        else:
            self.cache = {"searches": [], "leads": []}

    def _save_cache(self):
        with open(self.results_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def search_jobs(self, query: str, category: str = "all") -> Dict:
        """Search for job leads using web search."""
        self.engine.log(f"LeadFinder: Searching for '{query}'")
        
        # Use existing web search from main.py
        results = self._web_search(query)
        
        # Convert to lead format
        leads = []
        for r in results:
            if r.get("url") and r.get("title"):
                lead = {
                    "title": r["title"],
                    "url": r["url"],
                    "snippet": r.get("snippet", ""),
                    "category": category,
                    "query": query,
                    "found_at": datetime.now().isoformat(),
                    "email": self._extract_email(r.get("snippet", ""))
                }
                leads.append(lead)
                self.cache["leads"].append(lead)
        
        self.cache["searches"].append({
            "query": query,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "results_count": len(leads)
        })
        self._save_cache()
        
        return {"query": query, "category": category, "leads": leads, "count": len(leads)}

    def _web_search(self, query: str, num: int = 8) -> List[Dict]:
        """Search using DuckDuckGo (no API key needed)."""
        results = []
        try:
            url = "https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("AbstractText"):
                    results.append({
                        "title": data.get("Heading", "Result"),
                        "snippet": data.get("AbstractText", ""),
                        "url": data.get("AbstractURL", "")
                    })
            # HTML fallback
            if len(results) < num:
                import urllib.parse
                url2 = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
                headers = {"User-Agent": "Mozilla/5.0"}
                resp2 = requests.get(url2, headers=headers, timeout=10)
                if resp2.status_code == 200:
                    import re
                    for match in re.finditer(
                        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</(?:a|div)',
                        resp2.text, re.DOTALL
                    ):
                        if len(results) >= num:
                            break
                        url_found = match.group(1)
                        title_found = re.sub(r'<[^>]+>', '', match.group(2)).strip()
                        snippet_found = re.sub(r'<[^>]+>', '', match.group(3)).strip()
                        if title_found:
                            results.append({"title": title_found[:100], "snippet": snippet_found[:200], "url": url_found})
        except Exception as e:
            self.engine.log(f"LeadFinder search error: {e}", "error")
        return results[:num] if results else []

    def _extract_email(self, text: str) -> Optional[str]:
        import re
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return emails[0] if emails else None

    def get_cached_leads(self, category: str = None) -> List[Dict]:
        leads = self.cache.get("leads", [])
        if category:
            leads = [l for l in leads if l.get("category") == category]
        return leads

    def export_leads(self, format: str = "json") -> str:
        """Export leads for external use."""
        if format == "csv":
            import csv, io
            output = io.StringIO()
            if self.cache["leads"]:
                writer = csv.DictWriter(output, fieldnames=self.cache["leads"][0].keys())
                writer.writeheader()
                writer.writerows(self.cache["leads"])
            return output.getvalue()
        return json.dumps(self.cache["leads"], indent=2)