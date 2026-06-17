import os, json, subprocess, tempfile, random
from datetime import datetime

class MusicVideoGenerator:
    def __init__(self, engine):
        self.engine = engine
        self.output_dir = os.path.expanduser("/home/j/videos")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, audio_path, title="Red Engine Video", style="abstract", shorts=False, effect="waveform"):
        """Generate a music video from an audio file with visual effects.
        
        Args:
            shorts: If True, generate 1080x1920 vertical for YouTube Shorts
            effect: waveform, jessica_rabbit, neon_pulse, fire, hearts, matrix
        """
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found: {audio_path}"}

        output_path = os.path.join(self.output_dir, f"mv_{datetime.now().timestamp():.0f}.mp4")
        
        # Resolution: Shorts = 1080x1920, Standard = 1920x1080
        if shorts:
            width, height = 1080, 1920
        else:
            width, height = 1920, 1080
        
        # Visual effect filters
        effects = {
            "waveform": (
                f"[0:a]showwaves=s={width}x{height}:mode=cline:rate=30:colors=0xff3333|0xff6600|0xffaa00[waves];"
                f"color=c=#0a0a0a:s={width}x{height}:d=5[bg];"
                "[bg][waves]overlay=format=auto:shortest=1[v]"
            ),
            "jessica_rabbit": (
                f"color=c=#1a0000:s={width}x{height}:d=5[bg];"
                f"[0:a]showwaves=s={width}x{height//2}:mode=cline:rate=30:colors=0xff0000|0xff3366|0xff6699[waves];"
                f"[bg]drawtext=text='I'm not bad...':fontsize=48:fontcolor=0xff0000:x=(w-text_w)/2:y=50:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf[t1];"
                f"[t1]drawtext=text='I'm just drawn that way':fontsize=48:fontcolor=0xff3366:x=(w-text_w)/2:y=120:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf[t2];"
                f"[waves]colorbalance=rs=0.5:gs=0.0:bs=0.0[red];"
                f"[t2][red]overlay=0:main_h/2[final];"
                f"[final]vignette=PI/4[v]"
            ),
            "neon_pulse": (
                f"[0:a]showwaves=s={width}x{height}:mode=cline:rate=30:colors=0x00ff00|0x00ffff|0xff00ff:split_channels=1[waves];"
                f"color=c=#000000:s={width}x{height}:d=5[bg];"
                f"[bg][waves]overlay=format=auto:shortest=1,"
                f"geq=random(1)*20*(1+sin(2*PI*t)):128:128[v]"
            ),
            "fire": (
                f"[0:a]showwaves=s={width}x{height//2}:mode=cline:rate=30:colors=0xff0000|0xff6600|0xffaa00[waves];"
                f"color=c=#1a0000:s={width}x{height}:d=5[bg];"
                f"[waves]hue=H=20:s=2[fire];"
                f"[bg][fire]overlay=0:main_h/2:format=auto:shortest=1,"
                f"vignette=PI/3[v]"
            ),
            "hearts": (
                f"color=c=#1a0010:s={width}x{height}:d=5[bg];"
                f"[0:a]showwaves=s={width}x{height//3}:mode=cline:rate=30:colors=0xff1493|0xff69b4|0xffc0cb[waves];"
                f"[bg]drawtext=text='♥':fontsize=120:fontcolor=0xff1493:x=100:y=200:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf[h1];"
                f"[h1]drawtext=text='♥':fontsize=80:fontcolor=0xff69b4:x=300:y=400:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf[h2];"
                f"[h2]drawtext=text='♥':fontsize=100:fontcolor=0xffc0cb:x=500:y=150:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf[h3];"
                f"[h3][waves]overlay=0:main_h/2:format=auto:shortest=1[v]"
            ),
            "matrix": (
                f"color=c=#000a00:s={width}x{height}:d=5[bg];"
                f"[0:a]showwaves=s={width}x{height}:mode=cline:rate=30:colors=0x00ff00|0x004400|0x008800[waves];"
                f"[bg][waves]overlay=format=auto:shortest=1,"
                f"colorbalance=gs=0.3:bs=-0.2[v]"
            )
        }
        
        filter_str = effects.get(effect, effects["waveform"])

        # Use FFmpeg to generate a visualizer-based music video
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", audio_path,
                "-filter_complex", filter_str,
                "-map", "[v]", "-map", "0:a",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-r", "30",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                return {"error": f"FFmpeg error: {result.stderr[:500]}"}

            self.engine.log(f"Music video generated: {output_path}")
            return {"path": output_path, "title": title, "style": style, "effect": effect, "duration_sec": self._get_duration(output_path), "shorts": shorts}

        except FileNotFoundError:
            return {"error": "FFmpeg not found. Install with: sudo apt install ffmpeg"}
        except subprocess.TimeoutExpired:
            return {"error": "Video generation timed out (300s)"}
        except Exception as e:
            return {"error": str(e)}

    def generate_with_images(self, audio_path, image_dir, title="Red Engine", shorts=False):
        """Generate a music video with image slideshow and audio.
        
        Args:
            shorts: If True, generate 1080x1920 vertical for YouTube Shorts
        """
        if not os.path.exists(audio_path):
            return {"error": f"Audio not found: {audio_path}"}

        images = [os.path.join(image_dir, f) for f in sorted(os.listdir(image_dir))
                  if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        if not images:
            return {"error": "No images found in directory"}

        output_path = os.path.join(self.output_dir, f"mv_{datetime.now().timestamp():.0f}.mp4")
        
        # Resolution: Shorts = 1080x1920, Standard = 1920x1080
        if shorts:
            width, height = 1080, 1920
        else:
            width, height = 1920, 1080

        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                for img in images:
                    f.write(f"file '{img}'\nduration 3\n")
                f.write(f"file '{images[-1]}'\nduration 3\n")
                list_path = f.name

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", list_path,
                "-i", audio_path,
                "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-r", "30",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            os.unlink(list_path)

            if result.returncode != 0:
                return {"error": f"FFmpeg slideshow error: {result.stderr[:300]}"}

            return {"path": output_path, "title": title, "images_used": len(images), "shorts": shorts}

        except Exception as e:
            return {"error": str(e)}

    def _get_duration(self, video_path):
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return round(float(result.stdout.strip()), 2) if result.stdout else 0
        except Exception:
            return 0

    def cleanup_old_videos(self, max_age_days=7):
        """Remove music videos older than max_age_days"""
        import time
        cutoff = time.time() - (max_age_days * 86400)
        removed = 0
        for f in os.listdir(self.output_dir):
            if f.startswith("mv_") and f.endswith(".mp4"):
                fp = os.path.join(self.output_dir, f)
                if os.path.getmtime(fp) < cutoff:
                    os.remove(fp)
                    removed += 1
        return {"removed": removed, "cutoff_days": max_age_days}

    def batch_generate(self, audio_dir, shorts=True, count=5):
        """Generate multiple videos from audio files in a directory"""
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith((".mp3", ".wav", ".ogg", ".m4a"))]
        if not audio_files:
            return {"error": "No audio files found"}
        
        results = []
        for i, audio_file in enumerate(audio_files[:count]):
            audio_path = os.path.join(audio_dir, audio_file)
            title = f"Red Engine Video {i+1}"
            result = self.generate(audio_path, title=title, shorts=shorts)
            results.append(result)
        
        return {"generated": len(results), "results": results}
