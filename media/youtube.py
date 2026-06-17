import os, json, time, random
from datetime import datetime

class YouTubeEngine:
    def __init__(self, engine):
        self.engine = engine
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
        self.client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")
        self.daily_upload_count = 0
        self.daily_quota_used = 0
        self.max_daily_uploads = engine.config.get("youtube.max_daily_uploads", 6)
        self.max_daily_quota = engine.config.get("youtube.daily_api_quota", 10000)
        self._reset_date = datetime.now().date()

    def _check_quota_reset(self):
        today = datetime.now().date()
        if today != self._reset_date:
            self.daily_upload_count = 0
            self.daily_quota_used = 0
            self._reset_date = today

    def _quota_available(self, cost=100):
        self._check_quota_reset()
        return self.daily_quota_used + cost <= self.max_daily_quota

    def _can_upload(self):
        self._check_quota_reset()
        return self.daily_upload_count < self.max_daily_uploads

    def upload_shorts(self, video_path, title, description="", tags=None):
        """Upload a YouTube Short (max 30s vertical video)."""
        self._check_quota_reset()
        if not self._can_upload():
            return {"error": f"Daily upload limit ({self.max_daily_uploads}) reached"}
        if not self._quota_available(1600):
            return {"error": "Daily API quota exceeded"}

        if not self.client_id:
            return {"error": "YouTube OAuth not configured (set YOUTUBE_CLIENT_ID/SECRET)"}

        import requests
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        try:
            # Validate video exists
            if not os.path.exists(video_path):
                return {"error": f"Video not found: {video_path}"}

            creds = Credentials(
                token=os.getenv("YOUTUBE_ACCESS_TOKEN"),
                refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_uri="https://oauth2.googleapis.com/token"
            )

            youtube = build("youtube", "v3", credentials=creds)

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": (description or f"Play {title} now! #shorts #gaming #crypto #redengine")[:5000],
                    "tags": tags or ["shorts", "gaming", "crypto", "redengine", title[:20]],
                    "categoryId": "20"  # Gaming
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = request.execute()
            video_id = response.get("id", "")
            self.daily_upload_count += 1
            self.daily_quota_used += 1600

            self.engine.log(f"YouTube Shorts uploaded: {title} → https://youtube.com/shorts/{video_id}")

            return {
                "video_id": video_id,
                "url": f"https://youtube.com/shorts/{video_id}",
                "title": title,
                "uploads_today": self.daily_upload_count
            }

        except Exception as e:
            return {"error": f"YouTube upload failed: {e}"}

    def get_channel_stats(self, channel_id):
        """Fetch channel statistics."""
        if not self.api_key:
            return {"error": "YOUTUBE_API_KEY not set"}

        import requests
        url = "https://www.googleapis.com/youtube/v3/channels"
        params = {
            "part": "statistics,snippet",
            "id": channel_id,
            "key": self.api_key
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("items"):
                    item = data["items"][0]
                    self.daily_quota_used += 1
                    return {
                        "channel": item["snippet"]["title"],
                        "subscribers": int(item["statistics"].get("subscriberCount", 0)),
                        "views": int(item["statistics"].get("viewCount", 0)),
                        "videos": int(item["statistics"].get("videoCount", 0))
                    }
                return {"error": "Channel not found"}
            return {"error": f"YouTube API {resp.status_code}: {resp.text[:200]}"}
        except Exception as e:
            return {"error": str(e)}

    def generate_game_clip(self, game_url, game_name):
        """Generate a Shorts clip from a game (placeholder — requires screen recording or canvas capture)."""
        self.engine.log(f"Generated clip request for {game_name}")
        return {
            "game": game_name,
            "status": "clip_generated",
            "note": "Screen recording requires OBS or Playwright integration"
        }

    def handle(self, **kwargs):
        op = kwargs.get("op", "stats")
        if op == "stats":
            return self.get_channel_stats(kwargs.get("channel", ""))
        elif op == "upload":
            return self.upload_shorts(
                kwargs.get("video", ""),
                kwargs.get("title", "Red Engine Video"),
                kwargs.get("description", "")
            )
        return {"error": f"Unknown YouTube operation: {op}"}
