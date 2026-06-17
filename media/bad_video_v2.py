#!/usr/bin/env python3
"""
BAD - Jessica Rabbit Cabaret Music Video Generator
Creates frame-by-frame animation using PIL
"""
import os, subprocess, tempfile, math, random
from PIL import Image, ImageDraw, ImageFont

class BadVideoGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 24
        self.frame_dir = tempfile.mkdtemp(prefix="bad_frames_")
        os.makedirs(self.frame_dir, exist_ok=True)
        
    def create_frame(self, frame_num, total_frames):
        t = frame_num / self.fps
        
        img = Image.new('RGB', (self.width, self.height), (10, 0, 15))
        draw = ImageDraw.Draw(img)
        
        # Stage and curtains
        self._draw_stage(draw, t)
        
        # Jessica Rabbit
        self._draw_jessica(draw, t, frame_num)
        
        # Animated elements
        self._draw_effects(draw, t, frame_num)
        
        # Text overlays
        self._draw_text(draw, t)
        
        return img
    
    def _draw_stage(self, draw, t):
        """Draw cabaret stage with curtains"""
        # Floor
        for y in range(1400, self.height):
            shade = int(30 + (y - 1400) * 0.1)
            draw.line([(0, y), (self.width, y)], fill=(shade, shade // 2, shade // 3))
        
        # Stage edge gold trim
        draw.rectangle([0, 1395, self.width, 1405], fill=(180, 140, 60))
        
        # Left curtain (teal like reference)
        for x in range(0, 150):
            wave = math.sin(x * 0.05 + t * 0.5) * 10
            g = int(60 + wave)
            b = int(80 + wave)
            draw.line([(x, 0), (x, 1400)], fill=(15, g, b))
        
        # Right curtain
        for x in range(self.width - 150, self.width):
            wave = math.sin(x * 0.05 + t * 0.5) * 10
            g = int(60 + wave)
            b = int(80 + wave)
            draw.line([(x, 0), (x, 1400)], fill=(15, g, b))
        
        # Back wall
        draw.rectangle([150, 0, self.width - 150, 600], fill=(12, 8, 18))
        
        # Stage lights
        for i in range(5):
            x = 200 + i * 170
            draw.ellipse([x - 15, 0, x + 15, 30], fill=(60, 60, 80))
            # Light beam
            for y in range(30, 600, 5):
                alpha = max(0, 30 - y // 20)
                width = 20 + y // 10
                draw.line([(x, y), (x - width, y + 50)], fill=(alpha, alpha, alpha), width=2)
                draw.line([(x, y), (x + width, y + 50)], fill=(alpha, alpha, alpha), width=2)
    
    def _draw_jessica(self, draw, t, frame_num):
        """Draw Jessica Rabbit"""
        cx = self.width // 2
        cy = 850
        
        # Spotlight glow
        for r in range(200, 0, -5):
            alpha = int(25 * (1 - r / 200))
            draw.ellipse([cx - r, cy - r//2, cx + r, cy + r//2], 
                        fill=(alpha * 3, alpha, alpha // 2))
        
        # Hair (red, wavy)
        hair_color = (180, 30, 30)
        hair_light = (220, 50, 50)
        
        # Hair volume
        draw.ellipse([cx - 85, cy - 340, cx + 85, cy - 200], fill=hair_color)
        
        # Hair waves
        for i in range(8):
            wave = int(math.sin(t * 0.8 + i * 0.5) * 12)
            # Left side
            x = cx - 100 + wave
            y = cy - 300 + i * 35
            draw.ellipse([x, y, x + 60, y + 45], fill=hair_color)
            # Right side
            x2 = cx + 40 + wave
            draw.ellipse([x2, y, x2 + 60, y + 45], fill=hair_color)
        
        # Hair highlights
        for i in range(6):
            x = cx - 60 + i * 25
            y = cy - 310 + i * 30
            draw.ellipse([x, y, x + 15, y + 30], fill=hair_light)
        
        # Face
        face = (230, 190, 160)
        draw.ellipse([cx - 50, cy - 200, cx + 50, cy - 85], fill=face)
        
        # Eyes (blue, glamorous)
        # Whites
        draw.ellipse([cx - 38, cy - 170, cx - 8, cy - 140], fill=(255, 255, 255))
        draw.ellipse([cx + 8, cy - 170, cx + 38, cy - 140], fill=(255, 255, 255))
        
        # Iris (blue)
        blink = math.sin(t * 2) > 0.95
        if not blink:
            draw.ellipse([cx - 30, cy - 165, cx - 16, cy - 145], fill=(80, 130, 200))
            draw.ellipse([cx + 16, cy - 165, cx + 30, cy - 145], fill=(80, 130, 200))
            # Pupils
            draw.ellipse([cx - 25, cy - 160, cx - 21, cy - 150], fill=(0, 0, 0))
            draw.ellipse([cx + 21, cy - 160, cx + 25, cy - 150], fill=(0, 0, 0))
            # Sparkle
            draw.ellipse([cx - 28, cy - 163, cx - 26, cy - 160], fill=(255, 255, 255))
            draw.ellipse([cx + 26, cy - 163, cx + 28, cy - 160], fill=(255, 255, 255))
        
        # Eyelashes
        for i in range(5):
            draw.line([(cx - 40 + i * 5, cy - 170), (cx - 45 + i * 3, cy - 182)], fill=(0, 0, 0), width=2)
            draw.line([(cx + 8 + i * 5, cy - 170), (cx + 3 + i * 3, cy - 182)], fill=(0, 0, 0), width=2)
        
        # Red lips
        draw.arc([cx - 20, cy - 120, cx + 20, cy - 100], 180, 360, fill=(200, 20, 20), width=4)
        draw.arc([cx - 16, cy - 110, cx + 16, cy - 90], 0, 180, fill=(180, 10, 10), width=4)
        
        # Neck
        draw.rectangle([cx - 15, cy - 90, cx + 15, cy - 55], fill=face)
        
        # Shoulders
        draw.ellipse([cx - 90, cy - 50, cx + 90, cy + 10], fill=face)
        
        # RED/PINK DRESS
        dress = (200, 50, 80)
        dress_light = (255, 100, 150)
        
        # Bodice (strapless sweetheart)
        draw.polygon([
            (cx - 85, cy - 40),
            (cx - 70, cy - 65),
            (cx - 20, cy - 48),
            (cx + 20, cy - 48),
            (cx + 70, cy - 65),
            (cx + 85, cy - 40),
            (cx + 60, cy + 120),
            (cx - 60, cy + 120)
        ], fill=dress)
        
        # Sequin sparkles
        for i in range(25):
            sx = cx - 50 + (i * 17) % 100
            sy = cy - 35 + (i * 23) % 135
            sparkle = int(180 + math.sin(t * 8 + i * 1.5) * 75)
            size = 2 + int(math.sin(t * 6 + i) * 2)
            draw.ellipse([sx, sy, sx + size, sy + size], fill=(sparkle, sparkle, sparkle))
        
        # Waist (narrow)
        draw.polygon([
            (cx - 60, cy + 110),
            (cx + 60, cy + 110),
            (cx + 30, cy + 190),
            (cx - 30, cy + 190)
        ], fill=dress)
        
        # Hips (curvy)
        draw.polygon([
            (cx - 30, cy + 180),
            (cx + 30, cy + 180),
            (cx + 100, cy + 380),
            (cx - 100, cy + 380)
        ], fill=dress)
        
        # More sparkles
        for i in range(15):
            sx = cx - 70 + (i * 19) % 140
            sy = cy + 130 + (i * 17) % 220
            sparkle = int(180 + math.sin(t * 8 + i * 1.3) * 75)
            draw.ellipse([sx, sy, sx + 3, sy + 3], fill=(sparkle, sparkle, sparkle))
        
        # Leg slit
        leg = (220, 180, 150)
        draw.polygon([
            (cx + 35, cy + 300),
            (cx + 95, cy + 380),
            (cx + 105, cy + 550),
            (cx + 45, cy + 550)
        ], fill=leg)
        
        # PURPLE GLOVES
        glove = (140, 110, 170)
        
        # Left arm (on hip)
        draw.polygon([
            (cx - 90, cy - 35),
            (cx - 125, cy + 25),
            (cx - 105, cy + 170),
            (cx - 75, cy + 170),
            (cx - 85, cy + 25),
            (cx - 70, cy - 25)
        ], fill=glove)
        
        # Right arm (holding mic)
        draw.polygon([
            (cx + 90, cy - 35),
            (cx + 115, cy + 15),
            (cx + 105, cy + 95),
            (cx + 75, cy + 95),
            (cx + 80, cy + 15),
            (cx + 70, cy - 25)
        ], fill=glove)
        
        # Glove sparkles
        for i in range(5):
            sx = cx - 120 + (i * 10) % 45
            sy = cy + 40 + (i * 25) % 110
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(180, 160, 200))
        
        # MICROPHONE
        mic_x = cx + 100
        mic_y = cy - 25
        draw.rectangle([mic_x, mic_y + 25, mic_x + 4, mic_y + 90], fill=(80, 80, 80))
        draw.ellipse([mic_x - 8, mic_y, mic_x + 12, mic_y + 30], fill=(60, 60, 60))
        draw.ellipse([mic_x - 6, mic_y + 3, mic_x + 10, mic_y + 27], fill=(80, 80, 80))
        
        # HIGH HEELS
        draw.polygon([
            (cx - 75, cy + 540),
            (cx - 45, cy + 560),
            (cx - 25, cy + 560),
            (cx - 55, cy + 550)
        ], fill=(180, 0, 0))
        draw.rectangle([cx - 70, cy + 560, cx - 65, cy + 585], fill=(180, 0, 0))
        
        draw.polygon([
            (cx + 45, cy + 540),
            (cx + 75, cy + 560),
            (cx + 95, cy + 560),
            (cx + 65, cy + 550)
        ], fill=(180, 0, 0))
        draw.rectangle([cx + 70, cy + 560, cx + 75, cy + 585], fill=(180, 0, 0))
    
    def _draw_effects(self, draw, t, frame_num):
        """Animated hearts and sparkles"""
        # Hearts floating up
        for i in range(12):
            x = (i * 90 + frame_num * 2) % self.width
            y = self.height - (frame_num * 3 + i * 70) % self.height
            size = 12 + int(math.sin(t + i) * 6)
            alpha = int(150 + math.sin(t * 2 + i) * 100)
            draw.text((x, y), "♥", fill=(alpha, alpha // 3, alpha // 2))
        
        # Sparkles
        for i in range(20):
            x = (i * 54 + frame_num) % self.width
            y = (i * 79 + frame_num * 2) % (self.height // 2)
            sparkle = int(180 + math.sin(t * 5 + i * 2) * 75)
            draw.ellipse([x, y, x + 2, y + 2], fill=(sparkle, sparkle, sparkle))
        
        # Musical notes
        for i in range(4):
            x = 200 + i * 200
            y = 300 + int(math.sin(t * 0.5 + i) * 50)
            draw.text((x, y), "♪", fill=(255, 200, 100))
    
    def _draw_text(self, draw, t):
        """Song title and lyrics"""
        # Title
        draw.text((self.width // 2 - 100, 50), "BAD", fill=(255, 50, 80))
        
        # Subtitle
        draw.text((self.width // 2 - 160, 160), "Jessica Rabbit Cabaret", fill=(255, 150, 200))
        
        # Lyrics
        lyrics = ["I'm not bad...", "Just drawn that way", "♥ Shelby ♥", "BAD"]
        idx = int(t / 3) % len(lyrics)
        draw.text((self.width // 2 - 100, 1780), lyrics[idx], fill=(255, 200, 150))
    
    def generate(self, audio_path, output_path, duration=None):
        """Generate the video"""
        if not duration:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip())
        
        total_frames = int(duration * self.fps)
        print(f"Generating {duration:.1f}s video ({total_frames} frames)...")
        
        # Generate frames
        frame_paths = []
        for i in range(0, total_frames, 3):  # Every 3rd frame
            if i % 50 == 0:
                print(f"  Frame {i}/{total_frames} ({i*100//total_frames}%)")
            
            img = self.create_frame(i, total_frames)
            frame_path = os.path.join(self.frame_dir, f"frame_{i:06d}.png")
            img.save(frame_path)
            frame_paths.append(frame_path)
        
        # Create concat file
        frames_list = os.path.join(self.frame_dir, "frames.txt")
        with open(frames_list, "w") as f:
            for fp in frame_paths:
                f.write(f"file '{fp}'\nduration {1/self.fps * 3}\n")
        
        # Encode
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", frames_list,
            "-i", audio_path,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-r", "24",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]
        
        print("Encoding video...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # Cleanup
        for fp in frame_paths:
            os.remove(fp)
        os.remove(frames_list)
        os.rmdir(self.frame_dir)
        
        if result.returncode != 0:
            return {"error": result.stderr[:500]}
        
        return {"path": output_path, "duration": duration}

if __name__ == "__main__":
    gen = BadVideoGenerator()
    result = gen.generate("/home/j/Music/bad.mp3", "/home/j/videos/bad_jessica_full.mp4")
    print(result)
