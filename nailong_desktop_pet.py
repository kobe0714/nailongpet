"""
奶龙桌面宠物 - Desktop Pet
基于 Codex 奶龙 spritesheet 的桌面宠物，可变帧率渲染管线。
"""

import tkinter as tk
from tkinter import Menu
from PIL import Image, ImageTk, ImageDraw
import pygame
import random
import math
import sys
import os
import time


def resource_path(relative_path):
    """获取资源文件的绝对路径（支持 PyInstaller 打包）"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)


# ─── 帧配置（Codex spritesheet 规格）─────────────────────────

FRAME_W = 192
FRAME_H = 208
COLS = 8
ROWS = 9

FRAME_CONFIG = {
    "idle":          {"row": 0, "durations": [280, 110, 110, 140, 140, 320]},
    "running_right": {"row": 1, "durations": [120, 120, 120, 120, 120, 120, 120, 220]},
    "running_left":  {"row": 2, "durations": [120, 120, 120, 120, 120, 120, 120, 220]},
    "waving":        {"row": 3, "durations": [140, 140, 140, 280]},
    "jumping":       {"row": 4, "durations": [140, 140, 140, 140, 280]},
    "failed":        {"row": 5, "durations": [140, 140, 140, 140, 140, 140, 140, 240]},
    "waiting":       {"row": 6, "durations": [150, 150, 150, 150, 150, 260]},
    "running":       {"row": 7, "durations": [120, 120, 120, 120, 120, 220]},
    "review":        {"row": 8, "durations": [150, 150, 150, 150, 150, 280]},
}


class FrameCache:
    """预提取 spritesheet 全部帧到内存，每帧存 (PIL.Image, duration_ms)"""

    def __init__(self, spritesheet_path, display_w, display_h, alpha_threshold=128):
        sheet = Image.open(spritesheet_path).convert("RGBA")
        self.frames = {}  # {state_name: [(PIL.Image, duration_ms), ...]}
        for state, cfg in FRAME_CONFIG.items():
            row = cfg["row"]
            durations = cfg["durations"]
            state_frames = []
            for col, dur in enumerate(durations):
                x = col * FRAME_W
                y = row * FRAME_H
                frame = sheet.crop((x, y, x + FRAME_W, y + FRAME_H))
                frame.thumbnail((display_w, display_h), Image.LANCZOS)
                frame = self._clean_alpha(frame, alpha_threshold)
                state_frames.append((frame, dur))
            self.frames[state] = state_frames

    @staticmethod
    def _clean_alpha(img, threshold):
        """二值化 alpha 通道，消除半透明边缘，防止 chroma-key 绿边。"""
        alpha = img.getchannel('A')
        alpha = alpha.point(lambda x: 255 if x >= threshold else 0)
        img.putalpha(alpha)
        return img

    def get(self, state):
        return self.frames.get(state, [])


class Particle:
    def __init__(self, x, y, lifetime=30):
        self.x, self.y = x, y
        self.lifetime = lifetime
        self.age = 0
        self.alive = True

    def update(self):
        self.age += 1
        if self.age >= self.lifetime:
            self.alive = False
        return self.alive

    def get_alpha(self):
        if self.age < self.lifetime * 0.3:
            return 1.0
        return max(0.0, 1.0 - (self.age - self.lifetime * 0.3) / (self.lifetime * 0.7))


class HeartParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, lifetime=40)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-3.0, -1.5)
        self.size = random.randint(8, 14)

    def update(self):
        super().update()
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.02


class StarParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, lifetime=25)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.randint(4, 8)

    def update(self):
        super().update()
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92


class NailongPet:
    """奶龙桌面宠物"""

    TRANS_COLOR = "#01FF00"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("奶龙")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", self.TRANS_COLOR)
        self.root.config(bg=self.TRANS_COLOR)

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        # 显示尺寸（LANCZOS 缩放后的帧大小）
        self.display_w = 150
        self.display_h = 163

        # 窗口略大于帧，给粒子效果留余地
        self.win_w = 180
        self.win_h = 210
        self.root.geometry(f"{self.win_w}x{self.win_h}")

        self.GROUND_OFFSET = 60

        self.x = (self.sw - self.win_w) // 2
        self.y = self.sh - self.win_h - self.GROUND_OFFSET
        self.root.geometry(f"+{self.x}+{self.y}")

        self.canvas = tk.Canvas(
            self.root, width=self.win_w, height=self.win_h,
            bg=self.TRANS_COLOR, highlightthickness=0
        )
        self.canvas.pack()
        self._img_item = self.canvas.create_image(
            self.win_w // 2, self.win_h // 2, image=None
        )

        self.root.bind("<Escape>", lambda e: self._quit())

        # 预提取帧缓存
        spritesheet_path = resource_path("spritesheet.webp")
        self.cache = FrameCache(spritesheet_path, self.display_w, self.display_h)
        print(f"Loaded {len(self.cache.frames)} animation states")

        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<ButtonPress-3>", self._on_right_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)

        self._build_menu()

        # 状态常量
        self.ST_IDLE = "idle"
        self.ST_WALK_LEFT = "running_left"
        self.ST_WALK_RIGHT = "running_right"
        self.ST_DANCE = "running"
        self.ST_JUMP = "jumping"
        self.ST_WAVE = "waving"
        self.ST_WAIT = "waiting"
        self.ST_FAIL = "failed"
        self.ST_REVIEW = "review"
        self.ST_FALL = "falling"

        self.state = self.ST_IDLE
        self._anim_idx = 0
        self._cycle_count = 0
        self._state_after_id = None
        self._anim_after_id = None

        # 物理
        self.vy = 0
        self.vx = 0

        # 拖拽
        self.dragging = False
        self._drag_ox = 0
        self._drag_oy = 0
        self._drag_vx = 0
        self._drag_vy = 0
        self._last_click_time = 0
        self.pet_count = 0
        self.GRAVITY = 1.2
        self.MAX_FALL_SPEED = 18
        self._target_x = self.x
        self.WALK_SPEED = 4
        self.particles = []

        # 首次启动
        self._schedule_state_change()
        self._animate()

        # 音频
        self._audio_on = True
        try:
            pygame.mixer.init()
            music_path = resource_path("Banda AK-47 - 我是奶龙（星光闪闪）.flac")
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
            else:
                self._audio_on = False
        except Exception:
            self._audio_on = False

    def _on_mouse_down(self, event):
        now = time.time()
        if now - self._last_click_time < 0.4:
            self._last_click_time = 0
            self.dragging = False
            self._do_pet()
            return
        self._last_click_time = now
        self.dragging = True
        self._drag_ox = event.x
        self._drag_oy = event.y

    def _on_drag(self, event):
        if not self.dragging:
            return
        nx = self.root.winfo_x() + event.x - self._drag_ox
        ny = self.root.winfo_y() + event.y - self._drag_oy
        self._drag_vx = (nx - self.x) * 0.5
        self._drag_vy = (ny - self.y) * 0.5
        self.x, self.y = nx, ny
        self.root.geometry(f"+{self.x}+{self.y}")

    def _on_mouse_up(self, event):
        if not self.dragging:
            return
        self.dragging = False
        ground_y = self.sh - self.win_h - self.GROUND_OFFSET
        if self.y < ground_y - 20:
            self.vy = self._drag_vy
            self.vx = self._drag_vx
            self._change_state(self.ST_FALL)
        else:
            self.y = ground_y
            self.root.geometry(f"+{self.x}+{self.y}")
            self._change_state(self.ST_IDLE)
            self._schedule_state_change()

    def _on_double_click(self, event):
        if self._last_click_time == 0:
            return
        self._last_click_time = 0
        self._do_pet()

    def _do_pet(self):
        self.pet_count += 1
        cx = self.x + self.win_w // 2
        cy = self.y + self.win_h // 4
        for _ in range(6):
            px = cx + random.randint(-20, 20)
            py = cy + random.randint(-10, 10)
            self.particles.append(HeartParticle(px, py))
        self._update_pet_menu()
        self._change_state(self.ST_WAVE)
        self._schedule_state_change()

    def _animate(self):
        if self._anim_after_id is not None:
            self.root.after_cancel(self._anim_after_id)
            self._anim_after_id = None

        if not self.dragging:
            if self.state == self.ST_FALL:
                self._update_fall()
            elif self.state in (self.ST_WALK_LEFT, self.ST_WALK_RIGHT):
                self._update_walk()

        for p in self.particles[:]:
            if not p.update():
                self.particles.remove(p)

        frames = self.cache.get(self.state)
        if not frames:
            self._anim_after_id = self.root.after(100, self._animate)
            return

        frame_img, duration = frames[self._anim_idx]

        # 粒子叠加合成
        if self.particles:
            if self.state == self.ST_FALL and self.cache.get(self.ST_JUMP):
                jump_frames = self.cache.get(self.ST_JUMP)
                frame_img, _ = jump_frames[self._anim_idx % len(jump_frames)]
                angle = 5 * math.sin(self._cycle_count * len(jump_frames) * 0.35)
                frame_img = frame_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            bg = Image.new("RGBA", (self.win_w, self.win_h), (1, 255, 0, 255))
            bx = (self.win_w - frame_img.width) // 2
            by = (self.win_h - frame_img.height) // 2
            bg.paste(frame_img, (bx, by), frame_img)
            draw = ImageDraw.Draw(bg)
            for p in self.particles:
                alpha = p.get_alpha()
                if alpha <= 0:
                    continue
                px = int(p.x - self.x + self.win_w // 2)
                py = int(p.y - self.y + self.win_h // 2)
                if isinstance(p, HeartParticle):
                    self._draw_heart(draw, px, py, p.size, alpha)
                elif isinstance(p, StarParticle):
                    self._draw_star(draw, px, py, p.size, alpha)
            result = Image.new("RGB", (self.win_w, self.win_h), (1, 255, 0))
            result.paste(bg, (0, 0), bg)
            self._current_photo = ImageTk.PhotoImage(result)
            self.canvas.itemconfig(self._img_item, image=self._current_photo)
        elif self.state == self.ST_FALL and self.cache.get(self.ST_JUMP):
            jump_frames = self.cache.get(self.ST_JUMP)
            f_img, _ = jump_frames[self._anim_idx % len(jump_frames)]
            angle = 5 * math.sin(self._cycle_count * len(jump_frames) * 0.35)
            rotated = f_img.rotate(angle, expand=True, resample=Image.BICUBIC)
            bg = Image.new("RGBA", (self.win_w, self.win_h), (1, 255, 0, 255))
            rbx = (self.win_w - rotated.width) // 2
            rby = (self.win_h - rotated.height) // 2
            bg.paste(rotated, (rbx, rby), rotated)
            result = Image.new("RGB", (self.win_w, self.win_h), (1, 255, 0))
            result.paste(bg, (0, 0), bg)
            self._current_photo = ImageTk.PhotoImage(result)
            self.canvas.itemconfig(self._img_item, image=self._current_photo)
        else:
            bg = Image.new("RGBA", (self.win_w, self.win_h), (1, 255, 0, 255))
            bx = (self.win_w - frame_img.width) // 2
            by = (self.win_h - frame_img.height) // 2
            bg.paste(frame_img, (bx, by), frame_img)
            result = Image.new("RGB", (self.win_w, self.win_h), (1, 255, 0))
            result.paste(bg, (0, 0), bg)
            self._current_photo = ImageTk.PhotoImage(result)
            self.canvas.itemconfig(self._img_item, image=self._current_photo)

        # 前进帧
        self._anim_idx += 1
        if self._anim_idx >= len(frames):
            self._anim_idx = 0
            self._cycle_count += 1

        self._anim_after_id = self.root.after(duration, self._animate)

    def _update_fall(self):
        self.vy = min(self.vy + self.GRAVITY, self.MAX_FALL_SPEED)
        self.x += int(self.vx)
        self.y += int(self.vy)
        self.vx *= 0.95

        ground_y = self.sh - self.win_h - self.GROUND_OFFSET
        if self.y >= ground_y:
            self.y = ground_y
            self.vy = 0
            self.vx = 0
            self._change_state(self.ST_IDLE)
            self._schedule_state_change()

        if self.x <= 0:
            self.x = 0
            self.vx = abs(self.vx) * 0.5
        elif self.x >= self.sw - self.win_w:
            self.x = self.sw - self.win_w
            self.vx = -abs(self.vx) * 0.5

        self.root.geometry(f"+{self.x}+{self.y}")

    def _update_walk(self):
        dx = self._target_x - self.x
        if abs(dx) < 6:
            self._change_state(self.ST_IDLE)
            self._schedule_state_change()
        else:
            step = self.WALK_SPEED if dx > 0 else -self.WALK_SPEED
            self.x += step
            self.root.geometry(f"+{self.x}+{self.y}")

    def _change_state(self, new_state):
        if new_state not in self.cache.frames:
            return
        self.state = new_state
        self._anim_idx = 0
        self._cycle_count = 0

        margin = 100
        if new_state == self.ST_WALK_LEFT:
            self._target_x = random.randint(margin, max(margin + 1, self.x - 200))
        elif new_state == self.ST_WALK_RIGHT:
            min_x = min(self.x + 50, self.sw - self.win_w - margin)
            self._target_x = random.randint(min_x, self.sw - self.win_w - margin)

    def _schedule_state_change(self):
        if self._state_after_id is not None:
            self.root.after_cancel(self._state_after_id)
            self._state_after_id = None

        frames = self.cache.get(self.state)
        if frames:
            total_duration = sum(d for _, d in frames) * 2
            extra = random.randint(1500, 4000)
            delay = total_duration + extra
        else:
            delay = 3000
        self._state_after_id = self.root.after(delay, self._auto_state_change)

    def _auto_state_change(self):
        if self.state == self.ST_IDLE:
            choices = [
                (self.ST_WALK_LEFT,  0.20),
                (self.ST_WALK_RIGHT, 0.20),
                (self.ST_DANCE,      0.20),
                (self.ST_JUMP,       0.10),
                (self.ST_WAVE,       0.15),
                (self.ST_WAIT,       0.10),
                (self.ST_REVIEW,     0.05),
            ]
            r = random.random()
            cum = 0.0
            nxt = self.ST_WALK_RIGHT
            for st, prob in choices:
                cum += prob
                if r < cum:
                    nxt = st
                    break
            self._change_state(nxt)
        else:
            self._change_state(self.ST_IDLE)

        self._schedule_state_change()

    def _on_right_click(self, event):
        self.menu.post(event.x_root, event.y_root)

    def _build_menu(self):
        self.menu = Menu(self.root, tearoff=0)
        self.menu.add_command(label="  奶龙", state="disabled")
        self.menu.add_separator()
        self.menu.add_command(label="  跳舞", command=lambda: self._force_state(self.ST_DANCE))
        self.menu.add_command(label="  散步", command=self._force_walk)
        self.menu.add_command(label="  跳跳", command=lambda: self._force_state(self.ST_JUMP))
        self.menu.add_command(label="  招手", command=lambda: self._force_state(self.ST_WAVE))
        self.menu.add_command(label="  等待", command=lambda: self._force_state(self.ST_WAIT))
        self.menu.add_separator()
        self.menu.add_command(label="  被摸: 0 次", state="disabled")
        self._pet_menu_idx = self.menu.index("end")
        self.menu.add_command(label="  音效: 开", command=self._toggle_audio)
        self._audio_menu_idx = self.menu.index("end")
        self.menu.add_separator()
        self.menu.add_command(label="  退出", command=self._quit)

    def _update_pet_menu(self):
        try:
            self.menu.entryconfigure(
                self._pet_menu_idx, label=f"  被摸: {self.pet_count} 次"
            )
        except Exception:
            pass

    def _force_state(self, state):
        self._change_state(state)
        self._schedule_state_change()

    def _force_walk(self):
        if random.random() < 0.5:
            self._change_state(self.ST_WALK_LEFT)
        else:
            self._change_state(self.ST_WALK_RIGHT)
        self._schedule_state_change()

    def _draw_heart(self, draw, x, y, size, alpha):
        color = (255, int(80 * alpha + 50), int(80 * alpha + 50))
        r = size // 3
        draw.ellipse([x - r * 2, y - r, x, y + r], fill=color)
        draw.ellipse([x, y - r, x + r * 2, y + r], fill=color)
        draw.polygon([(x - r * 2, y), (x + r * 2, y), (x, y + r * 2)], fill=color)

    def _draw_star(self, draw, x, y, size, alpha):
        color = (255, int(220 * alpha), int(50 * alpha))
        draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
        draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
        s2 = size // 2
        draw.line([(x - s2, y - s2), (x + s2, y + s2)], fill=color, width=1)
        draw.line([(x + s2, y - s2), (x - s2, y + s2)], fill=color, width=1)

    def _toggle_audio(self):
        self._audio_on = not self._audio_on
        try:
            if self._audio_on:
                pygame.mixer.music.unpause()
                self.menu.entryconfigure(self._audio_menu_idx, label="  音效: 开")
            else:
                pygame.mixer.music.pause()
                self.menu.entryconfigure(self._audio_menu_idx, label="  音效: 关")
        except Exception:
            pass

    def _quit(self):
        if self._anim_after_id is not None:
            self.root.after_cancel(self._anim_after_id)
        if self._state_after_id is not None:
            self.root.after_cancel(self._state_after_id)
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    pet = NailongPet()
    pet.run()
