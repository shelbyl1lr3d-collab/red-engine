#!/usr/bin/env python3
"""
Jessica Rabbit Cabaret Video Generator
Creates a stylized cabaret music video with cartoon animal reactions
"""
import os, subprocess, tempfile, math, random
from PIL import Image, ImageDraw, ImageFont

class CabaretVideoGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 30
        self.frame_dir = tempfile.mkdtemp(prefix="cabaret_frames_")
        
    def create_frame(self, frame_num, total_frames, audio_duration):
        """Create a single frame of the video"""
        t = frame_num / self.fps  # time in seconds
        progress = frame_num / total_frames
        
        img = Image.new('RGB', (self.width, self.height), (10, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Stage background with curtains
        self._draw_curtains(draw, t)
        
        # Spotlight effect (moves slowly)
        self._draw_spotlight(draw, t)
        
        # Smoke/fog effect
        self._draw_smoke(draw, t, frame_num)
        
        # Cabaret bar counter
        self._draw_bar(draw, t)
        
        # Jessica silhouette (center stage)
        self._draw_jessica(draw, t, frame_num)
        
        # Cartoon animals in audience
        self._draw_audience(draw, t, frame_num)
        
        # Text overlays
        self._draw_text(draw, t, frame_num)
        
        # Hearts floating up
        self._draw_hearts(draw, t, frame_num)
        
        # Vignette effect
        self._draw_vignette(img)
        
        return img
    
    def _draw_curtains(self, draw, t):
        """Draw red velvet curtains"""
        # Left curtain
        for x in range(0, 200):
            wave = math.sin((x + t * 20) * 0.05) * 10
            r = max(0, min(255, 120 + int(wave * 2)))
            g = max(0, min(255, int(wave * 0.5)))
            b = max(0, min(255, int(wave * 0.3)))
            draw.line([(x, 0), (x, self.height)], fill=(r, g, b))
        
        # Right curtain
        for x in range(self.width - 200, self.width):
            wave = math.sin((x + t * 20) * 0.05) * 10
            r = max(0, min(255, 120 + int(wave * 2)))
            g = max(0, min(255, int(wave * 0.5)))
            b = max(0, min(255, int(wave * 0.3)))
            draw.line([(x, 0), (x, self.height)], fill=(r, g, b))
        
        # Gold trim
        draw.rectangle([180, 0, 210, self.height], fill=(180, 140, 50))
        draw.rectangle([self.width - 210, 0, self.width - 180, self.height], fill=(180, 140, 50))
    
    def _draw_spotlight(self, draw, t):
        """Animated spotlight on stage"""
        cx = self.width // 2 + int(math.sin(t * 0.3) * 100)
        cy = 600
        radius = 250
        
        for r in range(radius, 0, -2):
            alpha = int(60 * (1 - r / radius))
            # Warm spotlight color
            color = (255, 200 + int(math.sin(t * 2) * 30), 150)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline=None)
    
    def _draw_smoke(self, draw, t, frame_num):
        """Animated smoke/fog"""
        for i in range(20):
            x = (i * 137 + t * 30) % self.width
            y = 800 + int(math.sin(t + i) * 50)
            alpha = int(30 + math.sin(t * 0.5 + i) * 20)
            size = 80 + int(math.sin(t * 0.3 + i * 0.7) * 40)
            draw.ellipse([x - size, y - size//3, x + size, y + size//3], 
                        fill=(alpha, alpha, alpha))
    
    def _draw_bar(self, draw, t):
        """Draw the cabaret bar counter"""
        # Bar top
        draw.rectangle([100, 1400, self.width - 100, 1450], fill=(80, 40, 20))
        # Bar front
        draw.rectangle([100, 1450, self.width - 100, 1550], fill=(60, 30, 15))
        # Gold trim
        draw.rectangle([100, 1445, self.width - 100, 1455], fill=(200, 160, 80))
        
        # Bottles on bar
        for i in range(5):
            x = 200 + i * 150
            # Bottle
            draw.rectangle([x, 1350, x + 30, 1440], fill=(20, 60, 20))
            draw.rectangle([x + 5, 1320, x + 25, 1360], fill=(20, 60, 20))
            # Liquid glow
            glow = int(100 + math.sin(t * 2 + i) * 50)
            draw.rectangle([x + 3, 1380, x + 27, 1435], fill=(glow, int(glow * 0.8), int(glow * 0.3)))
    
    def _draw_jessica(self, draw, t, frame_num):
        """Draw Jessica Rabbit silhouette - accurate to reference image"""
        cx = self.width // 2
        cy = 850
        
        # Warm ambient glow behind her
        for r in range(300, 0, -5):
            alpha = int(30 * (1 - r / 300))
            draw.ellipse([cx - r, cy - r//2, cx + r, cy + r//2], 
                        fill=(alpha * 3, alpha, alpha // 2))
        
        # === HAIR (long red wavy) ===
        # Main hair mass
        hair_color = (180, 30, 30)  # Deep red
        hair_highlight = (220, 50, 50)
        
        # Left side hair flowing down
        for i in range(8):
            wave = int(math.sin(t * 0.5 + i * 0.5) * 10)
            x = cx - 100 + wave
            y = cy - 280 + i * 40
            draw.ellipse([x, y, x + 80, y + 60], fill=hair_color)
        
        # Right side hair flowing down
        for i in range(8):
            wave = int(math.sin(t * 0.5 + i * 0.5 + 1) * 10)
            x = cx + 20 + wave
            y = cy - 280 + i * 40
            draw.ellipse([x, y, x + 80, y + 60], fill=hair_color)
        
        # Hair highlights
        for i in range(5):
            wave = int(math.sin(t * 0.3 + i) * 5)
            x = cx - 60 + i * 30 + wave
            y = cy - 250 + i * 35
            draw.ellipse([x, y, x + 20, y + 40], fill=hair_highlight)
        
        # Hair top volume
        draw.ellipse([cx - 80, cy - 320, cx + 80, cy - 200], fill=hair_color)
        # Hair wave details
        for i in range(6):
            x = cx - 60 + i * 25
            draw.ellipse([x, cy - 300, x + 30, cy - 240], fill=hair_highlight)
        
        # === HEAD ===
        # Face (pale skin)
        face_color = (230, 190, 160)
        draw.ellipse([cx - 55, cy - 200, cx + 55, cy - 80], fill=face_color)
        
        # === EYES (glamorous, blue) ===
        # Eye whites
        draw.ellipse([cx - 40, cy - 165, cx - 10, cy - 135], fill=(255, 255, 255))
        draw.ellipse([cx + 10, cy - 165, cx + 40, cy - 135], fill=(255, 255, 255))
        
        # Blue iris
        blink = math.sin(t * 2) > 0.95
        if not blink:
            draw.ellipse([cx - 32, cy - 160, cx - 18, cy - 140], fill=(100, 150, 220))
            draw.ellipse([cx + 18, cy - 160, cx + 32, cy - 140], fill=(100, 150, 220))
            # Pupils
            draw.ellipse([cx - 27, cy - 155, cx - 23, cy - 145], fill=(0, 0, 0))
            draw.ellipse([cx + 23, cy - 155, cx + 27, cy - 145], fill=(0, 0, 0))
            # Eye sparkle
            draw.ellipse([cx - 30, cy - 158, cx - 28, cy - 155], fill=(255, 255, 255))
            draw.ellipse([cx + 28, cy - 158, cx + 30, cy - 155], fill=(255, 255, 255))
        
        # Eyelashes (long, dramatic)
        for i in range(5):
            draw.line([(cx - 40 + i * 5, cy - 165), (cx - 45 + i * 3, cy - 175)], 
                     fill=(0, 0, 0), width=2)
            draw.line([(cx + 10 + i * 5, cy - 165), (cx + 5 + i * 3, cy - 175)], 
                     fill=(0, 0, 0), width=2)
        
        # === RED LIPS (full, glamorous) ===
        # Upper lip
        draw.arc([cx - 25, cy - 120, cx + 25, cy - 100], 180, 360, fill=(200, 20, 20), width=4)
        # Lower lip (fuller)
        draw.arc([cx - 20, cy - 110, cx + 20, cy - 90], 0, 180, fill=(180, 10, 10), width=5)
        # Lip shine
        draw.arc([cx - 12, cy - 115, cx + 12, cy - 100], 180, 360, fill=(255, 80, 80), width=2)
        
        # === NECK ===
        draw.rectangle([cx - 18, cy - 90, cx + 18, cy - 50], fill=face_color)
        
        # === BODY (hourglass figure) ===
        # Shoulders
        draw.ellipse([cx - 90, cy - 50, cx + 90, cy + 10], fill=face_color)
        
        # === RED/PINK SEQUIN DRESS ===
        dress_color = (200, 50, 80)  # Pink-red like reference
        dress_sparkle = (255, 150, 180)
        
        # Bodice (strapless, sweetheart neckline)
        draw.polygon([
            (cx - 85, cy - 40),
            (cx - 70, cy - 60),  # Left dip
            (cx - 20, cy - 45),  # Center dip
            (cx + 20, cy - 45),  # Center dip
            (cx + 70, cy - 60),  # Right dip
            (cx + 85, cy - 40),
            (cx + 60, cy + 120),
            (cx - 60, cy + 120)
        ], fill=dress_color)
        
        # Sequin sparkles on dress
        for i in range(25):
            sx = cx - 50 + (i * 17) % 100
            sy = cy - 30 + (i * 23) % 130
            sparkle = int(200 + math.sin(t * 8 + i * 1.5) * 55)
            size = 2 + int(math.sin(t * 6 + i) * 2)
            draw.ellipse([sx, sy, sx + size, sy + size], fill=(sparkle, sparkle, sparkle))
        
        # === WAIST (very narrow - Jessica style) ===
        draw.polygon([
            (cx - 60, cy + 110),
            (cx + 60, cy + 110),
            (cx + 35, cy + 180),
            (cx - 35, cy + 180)
        ], fill=dress_color)
        
        # More sparkles on waist
        for i in range(10):
            sx = cx - 25 + (i * 12) % 50
            sy = cy + 120 + (i * 8) % 50
            sparkle = int(200 + math.sin(t * 8 + i * 2) * 55)
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(sparkle, sparkle, sparkle))
        
        # === HIPS (curvy) ===
        draw.polygon([
            (cx - 35, cy + 170),
            (cx + 35, cy + 170),
            (cx + 100, cy + 350),
            (cx - 100, cy + 350)
        ], fill=dress_color)
        
        # Dress slit (showing leg)
        leg_color = (220, 180, 150)
        draw.polygon([
            (cx + 30, cy + 280),
            (cx + 90, cy + 350),
            (cx + 100, cy + 500),
            (cx + 40, cy + 500)
        ], fill=leg_color)
        
        # Dress sparkles on hips
        for i in range(15):
            sx = cx - 70 + (i * 19) % 140
            sy = cy + 200 + (i * 17) % 130
            sparkle = int(200 + math.sin(t * 8 + i * 1.3) * 55)
            draw.ellipse([sx, sy, sx + 3, sy + 3], fill=(sparkle, sparkle, sparkle))
        
        # === PURPLE/LAVENDER GLOVES ===
        glove_color = (150, 120, 180)  # Purple/lavender
        
        # Left glove (arm extended)
        draw.polygon([
            (cx - 90, cy - 30),
            (cx - 120, cy + 20),
            (cx - 140, cy + 150),
            (cx - 110, cy + 150),
            (cx - 95, cy + 20),
            (cx - 75, cy - 20)
        ], fill=glove_color)
        
        # Right glove (holding microphone)
        draw.polygon([
            (cx + 90, cy - 30),
            (cx + 120, cy + 20),
            (cx + 130, cy + 80),
            (cx + 100, cy + 80),
            (cx + 95, cy + 20),
            (cx + 75, cy - 20)
        ], fill=glove_color)
        
        # Glove sparkle
        for i in range(8):
            sx = cx - 130 + (i * 10) % 40
            sy = cy + 50 + (i * 15) % 80
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(200, 180, 220))
        for i in range(8):
            sx = cx + 105 + (i * 10) % 30
            sy = cy + 30 + (i * 10) % 50
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(200, 180, 220))
        
        # === MICROPHONE ===
        mic_x = cx + 125
        mic_y = cy - 10
        # Mic stand
        draw.rectangle([mic_x, mic_y + 20, mic_x + 5, mic_y + 100], fill=(80, 80, 80))
        # Mic head
        draw.ellipse([mic_x - 10, mic_y - 15, mic_x + 15, mic_y + 25], fill=(60, 60, 60))
        draw.ellipse([mic_x - 8, mic_y - 12, mic_x + 13, mic_y + 22], fill=(80, 80, 80))
        # Mic shine
        draw.ellipse([mic_x - 5, mic_y - 8, mic_x, mic_y], fill=(120, 120, 120))
    
    def _draw_audience(self, draw, t, frame_num):
        """Draw cartoon animal audience with head explosion reactions"""
        animals = [
            {"x": 150, "y": 1600, "type": "wolf", "color": (150, 150, 150)},
            {"x": 350, "y": 1650, "type": "rabbit", "color": (200, 200, 200)},
            {"x": 550, "y": 1600, "type": "cat", "color": (100, 100, 100)},
            {"x": 750, "y": 1650, "type": "dog", "color": (180, 140, 100)},
            {"x": 950, "y": 1600, "type": "bear", "color": (120, 80, 50)},
        ]
        
        for i, animal in enumerate(animals):
            ax, ay = animal["x"], animal["y"]
            
            # Head explosion effect (cycles every few seconds)
            explosion_cycle = (t + i * 0.7) % 4.0
            is_exploding = explosion_cycle < 0.3
            
            if is_exploding:
                # HEAD EXPLOSION!
                # Eyes popping out
                eye_offset = int(explosion_cycle * 200)
                draw.ellipse([ax - 30, ay - 60 - eye_offset, ax - 15, ay - 40 - eye_offset], 
                           fill=(255, 255, 255))
                draw.ellipse([ax + 15, ay - 60 - eye_offset, ax + 30, ay - 40 - eye_offset], 
                           fill=(255, 255, 255))
                # Pupils
                draw.ellipse([ax - 25, ay - 55 - eye_offset, ax - 20, ay - 45 - eye_offset], 
                           fill=(0, 0, 0))
                draw.ellipse([ax + 20, ay - 55 - eye_offset, ax + 25, ay - 45 - eye_offset], 
                           fill=(0, 0, 0))
                
                # Steam from ears
                for s in range(3):
                    steam_x = ax - 30 + s * 30
                    steam_y = ay - 80 - int(explosion_cycle * 100)
                    draw.ellipse([steam_x, steam_y, steam_x + 20, steam_y + 15], 
                               fill=(200, 200, 200))
                
                # Stars around head
                for star in range(4):
                    angle = (star * 90 + t * 500) % 360
                    star_x = ax + int(math.cos(math.radians(angle)) * 50)
                    star_y = ay - 70 + int(math.sin(math.radians(angle)) * 30)
                    draw.text((star_x, star_y), "★", fill=(255, 255, 0))
                
                # "HELLO NURSE!" text
                if explosion_cycle < 0.15:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                    except:
                        font = ImageFont.load_default()
                    draw.text((ax - 60, ay - 120 - eye_offset), "HELLO NURSE!", 
                             fill=(255, 255, 0), font=font)
            else:
                # Normal animal head
                # Body
                draw.ellipse([ax - 40, ay, ax + 40, ay + 60], fill=animal["color"])
                
                # Head
                draw.ellipse([ax - 35, ay - 50, ax + 35, ay + 10], fill=animal["color"])
                
                # Ears
                if animal["type"] == "rabbit":
                    draw.ellipse([ax - 25, ay - 90, ax - 10, ay - 40], fill=animal["color"])
                    draw.ellipse([ax + 10, ay - 90, ax + 25, ay - 40], fill=animal["color"])
                elif animal["type"] == "cat":
                    draw.polygon([(ax - 30, ay - 40), (ax - 15, ay - 80), (ax, ay - 40)], 
                               fill=animal["color"])
                    draw.polygon([(ax, ay - 40), (ax + 15, ay - 80), (ax + 30, ay - 40)], 
                               fill=animal["color"])
                elif animal["type"] == "wolf":
                    draw.polygon([(ax - 35, ay - 40), (ax - 20, ay - 70), (ax - 5, ay - 40)], 
                               fill=animal["color"])
                    draw.polygon([(ax + 5, ay - 40), (ax + 20, ay - 70), (ax + 35, ay - 40)], 
                               fill=animal["color"])
                elif animal["type"] == "bear":
                    draw.ellipse([ax - 40, ay - 55, ax - 20, ay - 35], fill=animal["color"])
                    draw.ellipse([ax + 20, ay - 55, ax + 40, ay - 35], fill=animal["color"])
                
                # Eyes (looking at Jessica)
                draw.ellipse([ax - 20, ay - 30, ax - 8, ay - 15], fill=(255, 255, 255))
                draw.ellipse([ax + 8, ay - 30, ax + 20, ay - 15], fill=(255, 255, 255))
                # Pupils (track to center)
                pupil_offset = int(math.sin(t + i) * 3)
                draw.ellipse([ax - 16 + pupil_offset, ay - 27, ax - 12 + pupil_offset, ay - 20], fill=(0, 0, 0))
                draw.ellipse([ax + 12 + pupil_offset, ay - 27, ax + 16 + pupil_offset, ay - 20], fill=(0, 0, 0))
                
                # Nose
                draw.ellipse([ax - 5, ay - 18, ax + 5, ay - 10], fill=(20, 20, 20))
                
                # Open mouth (jaw drop)
                mouth_open = int(5 + math.sin(t * 3 + i) * 5)
                draw.ellipse([ax - 15, ay - 5, ax + 15, ay + mouth_open], fill=(50, 0, 0))
                
                # Hearts coming out (when not exploding)
                if int(t * 2 + i) % 3 == 0:
                    heart_y = ay - 80 - (frame_num % 30)
                    heart_x = ax + int(math.sin(t * 5 + i) * 20)
                    draw.text((heart_x, heart_y), "♥", fill=(255, 50, 100))
    
    def _draw_text(self, draw, t, frame_num):
        """Draw song title and lyrics"""
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        except:
            font_large = ImageFont.load_default()
            font_med = ImageFont.load_default()
        
        # Title at top
        title_y = 50 + int(math.sin(t * 0.5) * 10)
        draw.text((self.width // 2 - 100, title_y), "BAD", fill=(255, 0, 0), font=font_large)
        
        # Subtitle
        draw.text((self.width // 2 - 150, title_y + 80), "Jessica Rabbit Style", 
                 fill=(255, 200, 150), font=font_med)
        
        # Lyrics cycle
        lyrics = [
            "I'm not bad...",
            "I'm just drawn that way",
            "~ BAD ~",
            "♥ Shelby's Song ♥"
        ]
        lyric_idx = int(t / 3) % len(lyrics)
        lyric_alpha = int(200 + math.sin(t * 2) * 55)
        draw.text((self.width // 2 - 150, 1750), lyrics[lyric_idx], 
                 fill=(lyric_alpha, lyric_alpha // 2, lyric_alpha // 3), font=font_med)
    
    def _draw_hearts(self, draw, t, frame_num):
        """Floating hearts"""
        for i in range(10):
            x = (i * 107 + frame_num * 2) % self.width
            y = self.height - (frame_num * 3 + i * 50) % self.height
            size = 20 + int(math.sin(t + i) * 10)
            alpha = int(150 + math.sin(t * 2 + i) * 100)
            draw.text((x, y), "♥", fill=(alpha, alpha // 3, alpha // 2))
    
    def _draw_vignette(self, img):
        """Add dark vignette edges"""
        vignette = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        vdraw = ImageDraw.Draw(vignette)
        
        for i in range(50):
            alpha = int(255 * (i / 50))
            margin = i * 8
            if margin < self.width // 2 and margin < self.height // 2:
                vdraw.rectangle([margin, margin, self.width - margin, self.height - margin], 
                              fill=(alpha, alpha, alpha))
        
        # Blend with original
        from PIL import ImageChops
        return ImageChops.multiply(img, vignette)
    
    def generate(self, audio_path, output_path, preview=False):
        """Generate the full video
        
        Args:
            preview: If True, generate only first 30 seconds
        """
        # Get audio duration
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        
        if preview:
            duration = min(duration, 30)
        
        total_frames = int(duration * self.fps)
        
        print(f"Generating {duration:.1f}s video ({total_frames} frames)...")
        
        # Generate frames (every 5th frame for speed, then duplicate)
        frame_paths = []
        frame_interval = 5
        for i in range(0, total_frames, frame_interval):
            if i % 30 == 0:
                print(f"  Frame {i}/{total_frames} ({i*100//total_frames}%)")
            
            img = self.create_frame(i, total_frames, duration)
            frame_path = os.path.join(self.frame_dir, f"frame_{i:06d}.png")
            img.save(frame_path)
            frame_paths.append(frame_path)
        
        # Create video from frames
        frames_list = os.path.join(self.frame_dir, "frames.txt")
        with open(frames_list, "w") as f:
            for fp in frame_paths:
                f.write(f"file '{fp}'\nduration {1/self.fps * frame_interval}\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", frames_list,
            "-i", audio_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-r", "30",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path
        ]
        
        print("Encoding video...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # Cleanup frames
        for fp in frame_paths:
            os.remove(fp)
        os.remove(frames_list)
        os.rmdir(self.frame_dir)
        
        if result.returncode != 0:
            return {"error": result.stderr[:500]}
        
        return {"path": output_path, "duration": duration, "frames": total_frames}


if __name__ == "__main__":
    gen = CabaretVideoGenerator()
    result = gen.generate("/home/j/Music/bad.mp3", "/home/j/videos/bad_jessica_rabbit.mp4")
    print(result)
