"""Pixel-art scenes for the gallery section.

Renders 480x270 logical canvases and upscales them x3 (1440x810) with
nearest-neighbour, so the blocks stay crisp.

    python tools/gen_scenes.py
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "gallery"

W, H = 480, 270
SCALE = 3


# --------------------------------------------------------------------------
# tiny drawing helpers
# --------------------------------------------------------------------------
def px(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, c) -> None:
    if w <= 0 or h <= 0:
        return
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def lerp(a, b, t: float):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky(d: ImageDraw.ImageDraw, w: int, h: int, stops) -> None:
    for y in range(h):
        for i in range(len(stops) - 1):
            y0, c0 = stops[i]
            y1, c1 = stops[i + 1]
            if y0 <= y <= y1:
                px(d, 0, y, w, 1, lerp(c0, c1, (y - y0) / max(1, y1 - y0)))
                break


def glow(img: Image.Image, cx: int, cy: int, r: int, color, peak: int = 90) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 12
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(peak * (1 - i / steps) ** 2)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(r / 6)))


def stars(d: ImageDraw.ImageDraw, rnd: random.Random, w: int, top: int, count: int = 90) -> None:
    for _ in range(count):
        x, y = rnd.randrange(0, w), rnd.randrange(0, top)
        b = rnd.randrange(90, 240)
        px(d, x, y, 1, 1, (b, b, min(255, b + 14)))


def cloud(d: ImageDraw.ImageDraw, rnd: random.Random, x: int, y: int, w: int, a: int) -> None:
    col = (222, 228, 240, a)
    for width, dy in ((0.62, -6), (1.0, 0), (0.82, 6)):
        cw = max(6, int(w * width))
        px(d, x + (w - cw) // 2, y + dy, cw, 6, col)


def hill(d: ImageDraw.ImageDraw, rnd: random.Random, base_y: int, amp: int, color, top, w: int = W) -> None:
    for x in range(-6, w + 6, 6):
        v = math.sin(x * 0.021) * 0.6 + math.sin(x * 0.057 + 1.7) * 0.4
        top_y = int(base_y - amp * (0.5 + v / 2) + rnd.randrange(-2, 3))
        px(d, x, top_y, 6, max(1, H - top_y), color)
        px(d, x, top_y, 6, 2, top)


def stone_area(d, rnd, x, y, w, h, base=(58, 58, 64),
               tones=((46, 46, 52), (70, 70, 76), (52, 52, 58), (64, 64, 70))) -> None:
    px(d, x, y, w, h, base)
    for yy in range(y, y + h, 8):
        for xx in range(x, x + w, 8):
            if rnd.random() < 0.8:
                px(d, xx, yy, min(8, x + w - xx), min(8, y + h - yy), rnd.choice(tones))
    for yy in range(y, y + h, 8):
        px(d, x, yy, w, 1, (34, 34, 40))


def dirt_area(d, rnd, x, y, w, h) -> None:
    px(d, x, y, w, h, (96, 68, 45))
    for _ in range(max(1, w * h // 40)):
        px(d, x + rnd.randrange(w), y + rnd.randrange(h), 2, 2,
           rnd.choice([(74, 52, 34), (116, 84, 56), (86, 60, 40)]))


def obsidian_block(d, rnd, x, y, w, h) -> None:
    px(d, x, y, w, h, (24, 18, 34))
    for _ in range(max(1, w * h // 25)):
        px(d, x + rnd.randrange(max(1, w - 2)), y + rnd.randrange(max(1, h - 2)), 2, 2,
           rnd.choice([(46, 34, 74), (72, 54, 116), (36, 26, 54)]))
    px(d, x, y, w, 2, (78, 60, 122))
    px(d, x, y, 2, h, (60, 46, 96))


def chest(d, x: int, y: int, s: int = 1) -> None:
    w, h = 22 * s, 16 * s
    px(d, x, y, w, h, (150, 106, 58))
    px(d, x, y, w, 4 * s, (182, 132, 76))
    px(d, x, y, w, 2, (206, 152, 94))
    px(d, x, y + h - 3 * s, w, 3 * s, (112, 78, 42))
    px(d, x + w // 2 - 2, y + 5 * s, 5, 6 * s, (214, 184, 98))
    for xx in range(x, x + w, 4 * s):
        px(d, xx, y, 1, h, (132, 94, 52))


def torch(img, d, x: int, y: int) -> None:
    px(d, x, y, 3, 10, (92, 64, 38))
    px(d, x - 1, y - 5, 5, 6, (250, 176, 72))
    px(d, x, y - 6, 3, 4, (255, 226, 146))
    glow(img, x + 1, y - 4, 26, (255, 180, 90), peak=95)


def lava_band(img, d, rnd, x: int, y: int, w: int, h: int) -> None:
    for i in range(h):
        px(d, x, y + i, w, 1, lerp((240, 128, 44), (188, 48, 20), i / max(1, h - 1)))
    for _ in range(max(1, w * h // 28)):
        px(d, x + rnd.randrange(w), y + rnd.randrange(h), 2, 2,
           rnd.choice([(255, 226, 130), (255, 176, 64), (214, 84, 30)]))
    glow(img, x + w // 2, y + h // 2, 70, (255, 140, 50), peak=60)


def blast(img, d, rnd, cx: int, cy: int, r: int) -> None:
    """Smoke cloud + splattered fire, stylised like a blocky explosion."""
    smoke = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke)
    for _ in range(150):
        a = rnd.uniform(0, 2 * math.pi)
        dist = rnd.uniform(0, r * 1.2)
        sz = rnd.randrange(8, 24)
        x, y = cx + math.cos(a) * dist, cy + math.sin(a) * dist
        sd.rectangle([x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2],
                     fill=(40, 36, 42, 115))
    img.alpha_composite(smoke.filter(ImageFilter.GaussianBlur(7)))

    for _ in range(300):                      # fire splatter
        a = rnd.uniform(0, 2 * math.pi)
        t = rnd.random() ** 0.6
        col = (255, 246, 214) if t < .16 else (255, 226, 140) if t < .34 else \
              (255, 176, 74) if t < .6 else (232, 110, 44) if t < .82 else (150, 64, 38)
        px(d, int(cx + math.cos(a) * t * r), int(cy + math.sin(a) * t * r),
           rnd.choice([3, 4, 4, 5, 6]), rnd.choice([3, 4, 5]), col)

    for _ in range(40):                       # hot core
        a = rnd.uniform(0, 2 * math.pi)
        dist = rnd.uniform(0, r * 0.17)
        px(d, int(cx + math.cos(a) * dist), int(cy + math.sin(a) * dist), 5, 5,
           (255, 252, 232))

    for _ in range(16):                       # debris chunks
        a = rnd.uniform(0, 2 * math.pi)
        dist = rnd.uniform(r * 0.95, r * 1.55)
        px(d, int(cx + math.cos(a) * dist), int(cy + math.sin(a) * dist),
           rnd.choice([5, 6, 8]), rnd.choice([4, 5, 6]),
           rnd.choice([(58, 56, 64), (150, 106, 58), (96, 68, 45)]))

    glow(img, cx, cy, r + 26, (255, 150, 60), peak=95)


# --------------------------------------------------------------------------
# scenes
# --------------------------------------------------------------------------
def scene_base(img, d, rnd) -> None:
    stone_area(d, rnd, 0, 0, W, H)
    dirt_area(d, rnd, 20, 24, 130, 70)
    dirt_area(d, rnd, 320, 170, 140, 80)
    obsidian_block(d, rnd, 148, 76, 186, 128)
    px(d, 158, 86, 166, 108, (30, 30, 36))
    stone_area(d, rnd, 158, 86, 166, 108, base=(34, 34, 40),
               tones=((28, 28, 34), (42, 42, 48), (36, 36, 42)))
    chest(d, 186, 150, 2)
    chest(d, 244, 150, 2)
    torch(img, d, 168, 120)
    torch(img, d, 300, 120)
    for i in range(9):
        px(d, 120, 52 + i * 12, 3, 12, (122, 88, 50))
        px(d, 116, 54 + i * 12, 12, 2, (156, 114, 68))
    lava_band(img, d, rnd, 0, 240, W, 30)


def scene_raid(img, d, rnd) -> None:
    sky(d, W, H, [(0, (18, 14, 30)), (110, (32, 24, 48)), (190, (58, 40, 60)), (H, (72, 48, 62))])
    stars(d, rnd, W, 120, 70)
    px(d, 372, 38, 18, 18, (226, 220, 200))
    glow(img, 380, 46, 44, (220, 214, 200), peak=45)
    hill(d, rnd, 208, 22, (20, 18, 28), (34, 30, 44))
    stone_area(d, rnd, 292, 128, 168, 92)
    for _ in range(26):
        px(d, 330 + rnd.randrange(0, 60), 152 + rnd.randrange(0, 38), 7, 5, (24, 22, 30))
    blast(img, d, rnd, 248, 156, 56)
    for tx, ty in ((120, 218), (146, 218), (133, 200)):
        px(d, tx, ty, 24, 18, (186, 44, 40))
        px(d, tx, ty + 6, 24, 5, (232, 228, 220))
        px(d, tx, ty, 24, 2, (214, 66, 58))
    for _ in range(40):
        px(d, rnd.randrange(80, 470), rnd.randrange(40, 200), rnd.choice([3, 4, 5]),
           rnd.choice([3, 4]), rnd.choice([(60, 58, 66), (150, 106, 58), (80, 60, 40)]))
    for _ in range(18):
        px(d, rnd.randrange(180, 380), rnd.randrange(30, 120),
           rnd.randrange(6, 14), rnd.randrange(4, 10), (46, 44, 52, 150))


def scene_bed(img, d, rnd) -> None:
    for y in range(0, 190, 14):
        px(d, 0, y, W, 14, (150, 108, 66) if (y // 14) % 2 else (138, 98, 60))
        px(d, 0, y, W, 2, (170, 124, 78))
        for _ in range(3):
            px(d, rnd.randrange(0, W), y + 4, rnd.randrange(4, 12), 2, (120, 84, 50))
    stone_area(d, rnd, 0, 190, W, 80, base=(56, 56, 62))
    px(d, 44, 34, 92, 74, (110, 78, 46))
    px(d, 50, 40, 80, 62, (20, 26, 44))
    for _ in range(18):
        px(d, 52 + rnd.randrange(0, 76), 42 + rnd.randrange(0, 58), 1, 2,
           rnd.choice([(220, 220, 210), (160, 170, 200)]))
    px(d, 88, 40, 3, 62, (110, 78, 46))
    px(d, 50, 68, 80, 3, (110, 78, 46))
    px(d, 176, 128, 8, 58, (120, 86, 52))
    px(d, 176, 128, 116, 8, (140, 100, 60))
    px(d, 184, 150, 108, 38, (186, 46, 46))
    px(d, 184, 150, 108, 4, (214, 66, 66))
    px(d, 188, 156, 30, 20, (238, 236, 226))
    px(d, 184, 186, 108, 6, (120, 86, 52))
    for xx in range(184, 292, 14):
        px(d, xx, 190, 6, 14, (110, 78, 46))
    chest(d, 330, 168, 2)
    px(d, 398, 92, 20, 20, (250, 226, 150))
    glow(img, 408, 102, 60, (255, 214, 120), peak=80)


def scene_market(img, d, rnd) -> None:
    sky(d, W, H, [(0, (66, 116, 170)), (150, (110, 158, 200)), (H, (150, 186, 214))])
    for _ in range(5):
        cloud(d, rnd, rnd.randrange(-30, W), rnd.randrange(20, 90), rnd.randrange(40, 90), 70)
    stone_area(d, rnd, 0, 196, W, 74, base=(126, 126, 132),
               tones=((112, 112, 118), (140, 140, 146), (120, 120, 126)))
    for x0, c1 in ((40, (196, 60, 60)), (250, (70, 150, 84))):
        px(d, x0, 128, 168, 66, (140, 100, 62))
        px(d, x0, 194, 168, 8, (110, 78, 44))
        for i in range(0, 168, 24):
            px(d, x0 + i, 96, 24, 32, c1)
            px(d, x0 + i + 12, 96, 12, 32, (238, 232, 222))
        px(d, x0, 92, 168, 6, (196, 148, 92))
        px(d, x0 + 8, 96, 4, 100, (120, 86, 52))
        px(d, x0 + 156, 96, 4, 100, (120, 86, 52))
        for cx in (x0 + 18, x0 + 120):
            chest(d, cx, 168, 1)
    for gx, gy, col in ((70, 74, (96, 226, 140)), (110, 62, (250, 214, 96)),
                        (280, 70, (120, 180, 250)), (322, 60, (250, 214, 96))):
        px(d, gx, gy, 12, 12, col)
        px(d, gx + 3, gy + 3, 6, 6, tuple(min(255, c + 40) for c in col))
        glow(img, gx + 6, gy + 6, 22, col, peak=45)
    for lx in (210, 430):
        px(d, lx, 40, 2, 18, (90, 80, 70))
        px(d, lx - 4, 56, 10, 12, (250, 214, 130))
        glow(img, lx + 1, 62, 30, (255, 210, 120), peak=55)


def scene_map(img, d, rnd) -> None:
    px(d, 0, 0, W, H, (226, 210, 172))
    for _ in range(1400):
        px(d, rnd.randrange(W), rnd.randrange(H), 1, 1,
           rnd.choice([(216, 200, 162), (236, 222, 186)]))
    for _ in range(26):
        px(d, rnd.randrange(20, W - 20), rnd.randrange(20, H - 20),
           rnd.randrange(24, 60), rnd.randrange(16, 40),
           rnd.choice([(126, 168, 96), (110, 152, 86), (146, 180, 108)]))
    for x in range(0, W, 4):
        y = int(H * 0.62 + math.sin(x * 0.02) * 26)
        px(d, x, y, 4, 10, (104, 148, 190))
        px(d, x, y, 4, 2, (140, 180, 216))
    for _ in range(120):
        px(d, rnd.randrange(20, W - 20), rnd.randrange(20, H - 20), 3, 3, (72, 116, 74))
    for mx in (70, 150, 230):
        for i in range(14):
            px(d, mx + i * 2, 116 - i * 2, 44 - i * 4, 2, (140, 136, 128))
    for vx, vy in ((330, 70), (360, 96)):
        px(d, vx, vy, 20, 14, (166, 126, 88))
        px(d, vx - 2, vy - 6, 24, 6, (146, 92, 64))
    for i in range(0, 100, 14):
        px(d, 170 + i, 190 - i // 2, 6, 4, (140, 60, 50))
    for i in range(26):
        px(d, 300 + i, 130 + i, 4, 4, (188, 52, 44))
        px(d, 326 - i, 130 + i, 4, 4, (188, 52, 44))
    glow(img, 313, 143, 40, (220, 70, 56), peak=55)
    for _ in range(6):
        px(d, 0, 0, W, 6, (96, 70, 46))
        px(d, 0, H - 6, W, 6, (96, 70, 46))
        px(d, 0, 0, 6, H, (96, 70, 46))
        px(d, W - 6, 0, 6, H, (96, 70, 46))
    px(d, 226, 22, 3, 26, (86, 62, 42))
    px(d, 221, 26, 13, 4, (86, 62, 42))
    px(d, 224, 20, 7, 7, (160, 40, 36))


def scene_ruins(img, d, rnd) -> None:
    sky(d, W, H, [(0, (28, 18, 44)), (70, (86, 40, 66)), (140, (196, 96, 62)),
                  (196, (244, 168, 92)), (H, (250, 200, 130))])
    px(d, 336, 136, 30, 30, (255, 236, 190))
    glow(img, 350, 150, 90, (255, 210, 140), peak=90)
    for _ in range(10):
        cloud(d, rnd, rnd.randrange(-40, W), rnd.randrange(40, 120), rnd.randrange(50, 110), 40)
    hill(d, rnd, 206, 26, (44, 30, 46), (60, 40, 54))
    px(d, 60, 120, 90, 92, (28, 20, 34))
    px(d, 60, 120, 90, 8, (44, 32, 50))
    for i in range(0, 90, 18):
        px(d, 60 + i, 108, 10, 14, (28, 20, 34))
    px(d, 176, 140, 60, 72, (34, 24, 38))
    for i in range(0, 60, 18):
        px(d, 176 + i, 130, 10, 12, (34, 24, 38))
    for _ in range(30):
        px(d, rnd.randrange(60, 236), rnd.randrange(160, 210), 6, 4, (22, 16, 28))
    lava_band(img, d, rnd, 0, 226, W, 44)
    obsidian_block(d, rnd, 250, 150, 40, 30)
    obsidian_block(d, rnd, 300, 176, 26, 20)
    for bx, by in ((300, 60), (322, 52), (282, 48)):
        px(d, bx, by, 4, 2, (40, 28, 40))
        px(d, bx - 4, by - 2, 4, 2, (40, 28, 40))
    px(d, 380, 196, 90, 74, (24, 18, 30))
    for i in range(0, 90, 14):
        px(d, 380 + i, 186, 10, 12, (24, 18, 30))


SCENES = {
    "base": scene_base,
    "raid": scene_raid,
    "bed": scene_bed,
    "market": scene_market,
    "map": scene_map,
    "ruins": scene_ruins,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, maker in SCENES.items():
        img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        maker(img, ImageDraw.Draw(img), random.Random(name))
        img.resize((W * SCALE, H * SCALE), Image.NEAREST).convert("RGB").save(
            OUT / f"{name}.png", optimize=True)
    print("ok", sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
