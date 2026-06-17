#!/usr/bin/env python3
"""
Bad - Jessica Rabbit Cabaret Music Video
Divine soul expression through art
"""
import os, subprocess, tempfile, math, random
from PIL import Image, ImageDraw, ImageFont

class BadMusicVideo:
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fps = 30
        self.frame_dir = tempfile.mkdtemp(prefix="bad_frames_")
        
    def create_frame(self, frame_num, total_frames):
        t = frame_num / self.fps
        
        img = Image.new('RGB', (self.width, self.height), (5, 0, 5))
        draw = ImageDraw.Draw(img)
        
        # Layer 1: Stage background with curtains
        self._stage(draw, t)
        
        # Layer 2: Martini glass stage prop
        self._martini_glass(draw, t)
        
        # Layer 3: Cartoon animal band
        self._band(draw, t, frame_num)
        
        # Layer 4: Jessica performing
        self._jessica(draw, t, frame_num)
        
        # Layer 5: Spotlights
        self._spotlights(draw, t)
        
        # Layer 6: Floating elements
        self._floating_elements(draw, t, frame_num)
        
        # Layer 7: Text
        self._text(draw, t)
        
        # Layer 8: Vignette
        self._vignette(img)
        
        return img
    
    def _stage(self, draw, t):
        """Draw the cabaret stage"""
        # Floor (wooden stage)
        for y in range(1400, self.height):
            shade = int(40 + (y - 1400) * 0.1)
            draw.line([(0, y), (self.width, y)], fill=(shade, shade // 2, shade // 3))
        
        # Stage edge
        draw.rectangle([0, 1390, self.width, 1410], fill=(180, 140, 60))
        
        # Left curtain (dark teal like reference)
        curtain_color = (20, 60, 80)
        for x in range(0, 180):
            wave = math.sin((x + t * 15) * 0.04) * 15
            r = max(0, min(255, 20 + int(wave)))
            g = max(0, min(255, 60 + int(wave * 2)))
            b = max(0, min(255, 80 + int(wave * 2)))
            draw.line([(x, 0), (x, 1400)], fill=(r, g, b))
        
        # Right curtain
        for x in range(self.width - 180, self.width):
            wave = math.sin((x + t * 15) * 0.04) * 15
            r = max(0, min(255, 20 + int(wave)))
            g = max(0, min(255, 60 + int(wave * 2)))
            b = max(0, min(255, 80 + int(wave * 2)))
            draw.line([(x, 0), (x, 1400)], fill=(r, g, b))
        
        # Curtain folds
        for i in range(5):
            x = 40 + i * 30
            draw.line([(x, 0), (x, 1400)], fill=(15, 45, 65), width=3)
            x2 = self.width - 40 - i * 30
            draw.line([(x2, 0), (x2, 1400)], fill=(15, 45, 65), width=3)
        
        # Back wall (dark)
        draw.rectangle([180, 0, self.width - 180, 600], fill=(15, 10, 20))
        
        # Stars/sparkles on back wall
        for i in range(30):
            x = 200 + (i * 37) % (self.width - 400)
            y = 50 + (i * 23) % 500
            sparkle = int(150 + math.sin(t * 3 + i * 0.7) * 100)
            size = 1 + int(math.sin(t * 2 + i) * 1)
            draw.ellipse([x, y, x + size, y + size], fill=(sparkle, sparkle, sparkle))
    
    def _martini_glass(self, draw, t):
        """Draw giant martini glass stage prop (from reference)"""
        cx = self.width // 2
        cy = 450
        
        # Glass stem
        draw.rectangle([cx - 8, cy + 100, cx + 8, cy + 300], fill=(100, 100, 120))
        
        # Glass base
        draw.ellipse([cx - 60, cy + 280, cx + 60, cy + 320], fill=(80, 80, 100))
        
        # Glass bowl (martini shape)
        glass_points = [
            (cx - 150, cy - 100),  # Left top
            (cx - 20, cy + 100),   # Left bottom
            (cx + 20, cy + 100),   # Right bottom
            (cx + 150, cy - 100),  # Right top
        ]
        draw.polygon(glass_points, fill=(60, 80, 100), outline=(120, 140, 160))
        
        # Glass shine
        draw.line([(cx - 120, cy - 80), (cx - 30, cy + 80)], fill=(150, 170, 190), width=2)
        
        # Liquid in glass (blue like reference)
        liquid_points = [
            (cx - 130, cy - 60),
            (cx - 25, cy + 80),
            (cx + 25, cy + 80),
            (cx + 130, cy - 60),
        ]
        draw.polygon(liquid_points, fill=(40, 100, 150))
        
        # Olive on toothpick
        draw.line([(cx - 20, cy - 80), (cx + 30, cy - 40)], fill=(180, 160, 140), width=3)
        draw.ellipse([cx + 20, cy - 55, cx + 40, cy - 35], fill=(80, 120, 50))
    
    def _band(self, draw, t, frame_num):
        """Draw cartoon animal musicians"""
        band_members = [
            {"x": 150, "y": 1200, "type": "dog", "instrument": "drums", "color": (100, 80, 60)},
            {"x": 400, "y": 1250, "type": "wolf", "instrument": "bass", "color": (120, 120, 120)},
            {"x": 700, "y": 1250, "type": "cat", "instrument": "piano", "color": (80, 80, 80)},
            {"x": 950, "y": 1200, "type": "dog", "instrument": "sax", "color": (140, 100, 70)},
        ]
        
        for i, member in enumerate(band_members):
            mx, my = member["x"], member["y"]
            
            # Body (in suit)
            suit_color = (30, 30, 40)
            draw.ellipse([mx - 40, my, mx + 40, my + 80], fill=suit_color)
            
            # Head
            head_color = member["color"]
            draw.ellipse([mx - 30, my - 50, mx + 30, my + 10], fill=head_color)
            
            # Animal ears
            if member["type"] == "dog":
                draw.ellipse([mx - 35, my - 70, mx - 15, my - 40], fill=head_color)
                draw.ellipse([mx + 15, my - 70, mx + 35, my - 40], fill=head_color)
            elif member["type"] == "wolf":
                draw.polygon([(mx - 30, my - 45), (mx - 15, my - 80), (mx, my - 45)], fill=head_color)
                draw.polygon([(mx, my - 45), (mx + 15, my - 80), (mx + 30, my - 45)], fill=head_color)
            elif member["type"] == "cat":
                draw.polygon([(mx - 25, my - 45), (mx - 10, my - 75), (mx + 5, my - 45)], fill=head_color)
                draw.polygon([(mx + 5, my - 45), (mx + 20, my - 75), (mx + 35, my - 45)], fill=head_color)
            
            # Eyes (looking at Jessica)
            draw.ellipse([mx - 18, my - 30, mx - 8, my - 15], fill=(255, 255, 255))
            draw.ellipse([mx + 8, my - 30, mx + 18, my - 15], fill=(255, 255, 255))
            pupil_x = int(math.sin(t + i) * 3)
            draw.ellipse([mx - 15 + pupil_x, my - 27, mx - 11 + pupil_x, my - 20], fill=(0, 0, 0))
            draw.ellipse([mx + 11 + pupil_x, my - 27, mx + 15 + pupil_x, my - 20], fill=(0, 0, 0))
            
            # Nose
            draw.ellipse([mx - 4, my - 15, mx + 4, my - 8], fill=(20, 20, 20))
            
            # Open mouth (jaw drop when Jessica is near)
            mouth_open = int(5 + math.sin(t * 4 + i * 2) * 8)
            draw.ellipse([mx - 12, my - 2, mx + 12, my + mouth_open], fill=(60, 20, 20))
            
            # Musical notes coming from instruments
            if frame_num % 20 < 10:
                note_x = mx + int(math.sin(t * 5 + i) * 30)
                note_y = my - 80 - (frame_num % 40)
                draw.text((note_x, note_y), "♪", fill=(200, 200, 100))
            
            # Instruments
            if member["instrument"] == "drums":
                # Drum kit
                draw.ellipse([mx - 60, my + 30, mx, my + 80], fill=(150, 50, 50))  # Bass drum
                draw.ellipse([mx, my + 20, mx + 40, my + 60], fill=(180, 180, 50))  # Tom
                draw.rectangle([mx + 10, my - 10, mx + 30, my + 30], fill=(200, 200, 200))  # Cymbal stand
                draw.ellipse([mx - 5, my - 25, mx + 35, my - 10], fill=(200, 180, 50))  # Cymbal
                
            elif member["instrument"] == "bass":
                # Upright bass
                draw.rectangle([mx + 30, my - 80, mx + 45, my + 100], fill=(100, 60, 30))
                draw.ellipse([mx + 15, my - 40, mx + 60, my + 60], fill=(120, 70, 40))
                # Strings
                for s in range(4):
                    draw.line([(mx + 25 + s * 8, my - 70), (mx + 25 + s * 8, my + 80)], 
                             fill=(200, 200, 200), width=1)
                
            elif member["instrument"] == "piano":
                # Piano keys
                draw.rectangle([mx - 50, my + 20, mx + 50, my + 60], fill=(255, 255, 255))
                for k in range(7):
                    draw.rectangle([mx - 48 + k * 14, my + 20, mx - 42 + k * 14, my + 55], fill=(20, 20, 20))
                # Piano body
                draw.rectangle([mx - 55, my + 10, mx + 55, my + 25], fill=(20, 20, 20))
                
            elif member["instrument"] == "sax":
                # Saxophone
                draw.arc([mx + 20, my - 30, mx + 60, my + 30], 0, 180, fill=(200, 160, 50), width=8)
                draw.ellipse([mx + 50, my + 20, mx + 70, my + 50], fill=(200, 160, 50))
                # Keys
                for k in range(3):
                    draw.ellipse([mx + 25 + k * 12, my - 10, mx + 30 + k * 12, my - 5], fill=(255, 255, 255))
    
    def _jessica(self, draw, t, frame_num):
        """Draw Jessica Rabbit performing center stage"""
        cx = self.width // 2
        cy = 850
        
        # Spotlight on her
        for r in range(250, 0, -5):
            alpha = int(40 * (1 - r / 250))
            draw.ellipse([cx - r, cy - r//2, cx + r, cy + r//2], 
                        fill=(alpha * 3, alpha, alpha // 2))
        
        # === HAIR (long red wavy) ===
        hair_color = (180, 30, 30)
        hair_highlight = (220, 50, 50)
        
        # Hair flowing animation
        for i in range(10):
            wave = int(math.sin(t * 0.8 + i * 0.4) * 15)
            # Left side
            x = cx - 110 + wave
            y = cy - 300 + i * 35
            draw.ellipse([x, y, x + 70, y + 50], fill=hair_color)
            # Right side
            x2 = cx + 40 + wave
            draw.ellipse([x2, y, x2 + 70, y + 50], fill=hair_color)
        
        # Hair top volume
        draw.ellipse([cx - 90, cy - 350, cx + 90, cy - 220], fill=hair_color)
        # Highlights
        for i in range(8):
            wave = int(math.sin(t * 0.5 + i) * 8)
            x = cx - 70 + i * 22 + wave
            y = cy - 320 + i * 25
            draw.ellipse([x, y, x + 18, y + 35], fill=hair_highlight)
        
        # === HEAD ===
        face_color = (230, 190, 160)
        draw.ellipse([cx - 55, cy - 210, cx + 55, cy - 90], fill=face_color)
        
        # === EYES ===
        # Whites
        draw.ellipse([cx - 40, cy - 175, cx - 10, cy - 145], fill=(255, 255, 255))
        draw.ellipse([cx + 10, cy - 175, cx + 40, cy - 145], fill=(255, 255, 255))
        
        # Blue iris
        blink = math.sin(t * 2) > 0.95
        if not blink:
            draw.ellipse([cx - 32, cy - 170, cx - 18, cy - 150], fill=(100, 150, 220))
            draw.ellipse([cx + 18, cy - 170, cx + 32, cy - 150], fill=(100, 150, 220))
            # Pupils
            draw.ellipse([cx - 27, cy - 165, cx - 23, cy - 155], fill=(0, 0, 0))
            draw.ellipse([cx + 23, cy - 165, cx + 27, cy - 155], fill=(0, 0, 0))
            # Sparkle
            draw.ellipse([cx - 30, cy - 168, cx - 28, cy - 165], fill=(255, 255, 255))
            draw.ellipse([cx + 28, cy - 168, cx + 30, cy - 165], fill=(255, 255, 255))
        
        # Long eyelashes
        for i in range(6):
            draw.line([(cx - 42 + i * 4, cy - 175), (cx - 48 + i * 2, cy - 188)], 
                     fill=(0, 0, 0), width=2)
            draw.line([(cx + 8 + i * 4, cy - 175), (cx + 2 + i * 2, cy - 188)], 
                     fill=(0, 0, 0), width=2)
        
        # === RED LIPS ===
        draw.arc([cx - 22, cy - 125, cx + 22, cy - 105], 180, 360, fill=(200, 20, 20), width=4)
        draw.arc([cx - 18, cy - 115, cx + 18, cy - 95], 0, 180, fill=(180, 10, 10), width=5)
        draw.arc([cx - 10, cy - 120, cx + 10, cy - 105], 180, 360, fill=(255, 80, 80), width=2)
        
        # === NECK ===
        draw.rectangle([cx - 18, cy - 95, cx + 18, cy - 55], fill=face_color)
        
        # === SHOULDERS ===
        draw.ellipse([cx - 95, cy - 55, cx + 95, cy + 5], fill=face_color)
        
        # === SPARKLY PINK DRESS ===
        dress_color = (200, 50, 80)
        dress_light = (255, 100, 150)
        
        # Bodice (strapless sweetheart neckline)
        draw.polygon([
            (cx - 90, cy - 45),
            (cx - 75, cy - 70),
            (cx - 25, cy - 50),
            (cx + 25, cy - 50),
            (cx + 75, cy - 70),
            (cx + 90, cy - 45),
            (cx + 65, cy + 130),
            (cx - 65, cy + 130)
        ], fill=dress_color)
        
        # Sequin sparkles (animated)
        for i in range(30):
            sx = cx - 55 + (i * 19) % 110
            sy = cy - 40 + (i * 23) % 150
            sparkle = int(200 + math.sin(t * 10 + i * 1.7) * 55)
            size = 2 + int(math.sin(t * 8 + i) * 2)
            draw.ellipse([sx, sy, sx + size, sy + size], fill=(sparkle, sparkle, sparkle))
        
        # Waist (very narrow)
        draw.polygon([
            (cx - 65, cy + 120),
            (cx + 65, cy + 120),
            (cx + 35, cy + 200),
            (cx - 35, cy + 200)
        ], fill=dress_color)
        
        # Hips (curvy)
        draw.polygon([
            (cx - 35, cy + 190),
            (cx + 35, cy + 190),
            (cx + 110, cy + 400),
            (cx - 110, cy + 400)
        ], fill=dress_color)
        
        # More sparkles on body
        for i in range(20):
            sx = cx - 80 + (i * 17) % 160
            sy = cy + 130 + (i * 19) % 250
            sparkle = int(200 + math.sin(t * 10 + i * 1.3) * 55)
            draw.ellipse([sx, sy, sx + 3, sy + 3], fill=(sparkle, sparkle, sparkle))
        
        # Leg slit (right side)
        leg_color = (220, 180, 150)
        draw.polygon([
            (cx + 40, cy + 320),
            (cx + 100, cy + 400),
            (cx + 110, cy + 600),
            (cx + 50, cy + 600)
        ], fill=leg_color)
        
        # === PURPLE/LAVENDER GLOVES ===
        glove_color = (140, 110, 170)
        
        # Left arm (hand on hip)
        draw.polygon([
            (cx - 95, cy - 40),
            (cx - 130, cy + 30),
            (cx - 110, cy + 180),
            (cx - 80, cy + 180),
            (cx - 90, cy + 30),
            (cx - 75, cy - 30)
        ], fill=glove_color)
        
        # Right arm (holding mic near face)
        draw.polygon([
            (cx + 95, cy - 40),
            (cx + 120, cy + 10),
            (cx + 110, cy + 100),
            (cx + 80, cy + 100),
            (cx + 85, cy + 10),
            (cx + 75, cy - 30)
        ], fill=glove_color)
        
        # Glove sparkles
        for i in range(6):
            sx = cx - 125 + (i * 10) % 50
            sy = cy + 50 + (i * 20) % 100
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(180, 160, 200))
        for i in range(6):
            sx = cx + 88 + (i * 8) % 30
            sy = cy + 20 + (i * 15) % 70
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(180, 160, 200))
        
        # === MICROPHONE ===
        mic_x = cx + 105
        mic_y = cy - 30
        draw.rectangle([mic_x, mic_y + 30, mic_x + 5, mic_y + 100], fill=(80, 80, 80))
        draw.ellipse([mic_x - 10, mic_y, mic_x + 15, mic_y + 35], fill=(60, 60, 60))
        draw.ellipse([mic_x - 8, mic_y + 3, mic_x + 13, mic_y + 32], fill=(80, 80, 80))
        draw.ellipse([mic_x - 5, mic_y + 5, mic_x, mic_y + 12], fill=(120, 120, 120))
        
        # === HIGH HEELS ===
        # Left shoe
        draw.polygon([
            (cx - 80, cy + 580),
            (cx - 50, cy + 600),
            (cx - 30, cy + 600),
            (cx - 60, cy + 590)
        ], fill=(180, 0, 0))
        # Heel
        draw.rectangle([cx - 75, cy + 600, cx - 70, cy + 630], fill=(180, 0, 0))
        
        # Right shoe
        draw.polygon([
            (cx + 50, cy + 580),
            (cx + 80, cy + 600),
            (cx + 100, cy + 600),
            (cx + 70, cy + 590)
        ], fill=(180, 0, 0))
        draw.rectangle([cx + 75, cy + 600, cx + 80, cy + 630], fill=(180, 0, 0))
    
    def _spotlights(self, draw, t):
        """Animated spotlights"""
        spotlights = [
            {"x": 200, "color": (255, 200, 100)},
            {"x": 540, "color": (255, 150, 150)},
            {"x": 880, "color": (200, 200, 255)},
        ]
        
        for spot in spotlights:
            sx = spot["x"] + int(math.sin(t * 0.5) * 50)
            color = spot["color"]
            
            # Light cone
            for i in range(100):
                width = 50 + i * 3
                alpha = int(30 * (1 - i / 100))
                r = min(255, color[0] * alpha // 255)
                g = min(255, color[1] * alpha // 255)
                b = min(255, color[2] * alpha // 255)
                y = 600 + i * 8
                draw.polygon([
                    (sx - 20, 0),
                    (sx + 20, 0),
                    (sx + width, y),
                    (sx - width, y)
                ], fill=(r, g, b))
    
    def _floating_elements(self, draw, t, frame_num):
        """Floating hearts, notes, and sparkles"""
        # Hearts
        for i in range(8):
            x = (i * 137 + frame_num * 2) % self.width
            y = self.height - (frame_num * 3 + i * 80) % self.height
            size = 15 + int(math.sin(t + i) * 8)
            alpha = int(150 + math.sin(t * 2 + i) * 100)
            draw.text((x, y), "♥", fill=(alpha, alpha // 3, alpha // 2))
        
        # Musical notes
        for i in range(5):
            x = (i * 200 + frame_num * 3) % self.width
            y = 300 + int(math.sin(t * 0.5 + i) * 100)
            draw.text((x, y), "♪", fill=(255, 255, 100))
        
        # Sparkles
        for i in range(15):
            x = (i * 73 + frame_num) % self.width
            y = (i * 97 + frame_num * 2) % (self.height // 2)
            sparkle = int(200 + math.sin(t * 5 + i * 2) * 55)
            draw.ellipse([x, y, x + 3, y + 3], fill=(sparkle, sparkle, sparkle))
    
    def _text(self, draw, t):
        """Song title and lyrics"""
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
            font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font_large = ImageFont.load_default()
            font_med = font_large
            font_small = font_large
        
        # Title
        title_y = 40 + int(math.sin(t * 0.5) * 5)
        draw.text((self.width // 2 - 120, title_y), "BAD", fill=(255, 50, 80), font=font_large)
        
        # Artist
        draw.text((self.width // 2 - 180, title_y + 85), "Shelby Griessel", 
                 fill=(200, 150, 100), font=font_small)
        
        # Lyrics
        lyrics = [
            "I'm not bad...",
            "I'm just drawn that way",
            "~ BAD ~",
            "♥ Divine Expression ♥"
        ]
        lyric_idx = int(t / 3) % len(lyrics)
        lyric_y = 1780 + int(math.sin(t * 1.5) * 5)
        draw.text((self.width // 2 - 180, lyric_y), lyrics[lyric_idx], 
                 fill=(255, 200, 150), font=font_med)
    
    def _vignette(self, img):
        """Dark vignette edges"""
        vignette = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        vdraw = ImageDraw.Draw(vignette)
        
        for i in range(50):
            alpha = int(255 * (i / 50))
            margin = i * 10
            if margin < self.width // 2 and margin < self.height // 2:
                vdraw.rectangle([margin, margin, self.width - margin, self.height - margin], 
                              fill=(alpha, alpha, alpha))
        
        from PIL import ImageChops
        return ImageChops.multiply(img, vignette)
    
    def generate(self, audio_path, output_path, preview=False):
        """Generate the full music video"""
        # Get audio duration
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        
        if preview:
            duration = min(duration, 30)
        
        total_frames = int(duration * self.fps)
        
        print(f"Generating {duration:.1f}s video ({total_frames} frames)...")
        
        # Generate frames
        frame_paths = []
        frame_interval = 3  # Every 3rd frame
        for i in range(0, total_frames, frame_interval):
            if i % 30 == 0:
                print(f"  Frame {i}/{total_frames} ({i*100//total_frames}%)")
            
            img = self.create_frame(i, total_frames)
            frame_path = os.path.join(self.frame_dir, f"frame_{i:06d}.png")
            img.save(frame_path)
            frame_paths.append(frame_path)
        
        # Create concat file
        frames_list = os.path.join(self.frame_dir, "frames.txt")
        with open(frames_list, "w") as f:
            for fp in frame_paths:
                f.write(f"file '{fp}'\nduration {1/self.fps * frame_interval}\n")
        
        # Encode video
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", frames_list,
            "-i", audio_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-r", "30",
            "-c:a", "aac", "-b:a", "192k",
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
        
        return {"path": output_path, "duration": duration, "frames": total_frames}


if __name__ == "__main__":
    gen = BadMusicVideo()
    
    # Generate preview first
    print("=== Generating 30s Preview ===")
    result = gen.generate("/home/j/Music/bad.mp3", "/home/j/videos/bad_preview_v3.mp4", preview=True)
    print(result)
