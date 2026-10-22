"""Generate pixel-art assets for the FunTime fan site.

Outputs (all nearest-neighbour upscaled pixel art):
  assets/hero.png       1920x1080 night sky + floating islands
  assets/og.png         1200x630  social preview
  assets/favicon.png    64x64     grass block
  assets/icons/*.png    64x64     mode icons
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"

W, H = 480, 270          # logical pixel-art canvas
SCALE = 4                # -> 1920x1080
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"

GRASS = ((104, 190, 84), (78, 158, 66), (58, 130, 54))
DIRT = ((122, 88, 58), (96, 68, 45), (74, 52, 34))
STONE = ((104, 106, 112), (84, 86, 94), (64, 66, 74))


def px(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, c) -> None:
    """Fill a w x h pixel block starting at (x, y)."""
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
                t = (y - y0) / max(1, y1 - y0)
                px(d, 0, y, w, 1, lerp(c0, c1, t))
                break


def glow(img: Image.Image, cx: int, cy: int, r: int, color, peak: int = 90) -> None:
    """Soft radial glow, drawn small then blurred and upscaled with the rest."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 14
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(peak * (1 - i / steps) ** 2)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(r / 6))
    img.alpha_composite(layer)


def island(d: ImageDraw.ImageDraw, rnd: random.Random, x: int, y: int, w: int, h: int) -> None:
    """A floating chunk of grass/dirt/stone with pixel jitter."""
    gh = 5
    px(d, x + 1, y, w - 2, gh, GRASS[0])
    px(d, x, y + gh - 2, w, 3, GRASS[1])
    for i in range(gh):
        for xx in range(x + 1, x + w - 1, 2):
            if rnd.random() < 0.12:
                px(d, xx, y + i, 1, 1, GRASS[2])
    body = h - gh
    for i in range(body):
        t = i / max(1, body - 1)
        cw = max(3, round(w * (1 - 0.55 * t)))
        cx = x + (w - cw) // 2
        col = DIRT[0] if t < 0.55 else (DIRT[1] if t < 0.8 else DIRT[2])
        if t > 0.86:
            col = STONE[2]
        px(d, cx, y + gh + i, cw, 1, col)
        if rnd.random() < 0.25:
            px(d, cx + rnd.randrange(0, max(1, cw - 2)), y + gh + i, 2, 1,
               tuple(max(0, c - 18) for c in col) if isinstance(col, tuple) else col)
    # stone underside
    for i in range(3):
        cw = max(2, round(w * 0.32)) - i
        px(d, x + (w - cw) // 2, y + h + i, cw, 1, STONE[2] if i else STONE[1])
    # hanging vines
    for _ in range(max(1, w // 22)):
        vx = x + rnd.randrange(2, max(3, w - 3))
        vl = rnd.randrange(3, 12)
        px(d, vx, y + h + 3, 1, vl, (44, 96, 46))


def tree(d: ImageDraw.ImageDraw, rnd: random.Random, x: int, y: int, s: int = 1) -> None:
    """Small blocky tree; (x, y) is the trunk base bottom-left."""
    tw = max(2, 3 * s)
    th = max(6, 10 * s)
    px(d, x, y - th, tw, th, (74, 52, 32))
    px(d, x, y - th, 1, th, (96, 70, 44))
    lw, lh = 18 * s, 14 * s
    lx, ly = x - (lw - tw) // 2, y - th - lh + 3 * s
    px(d, lx + 2, ly + 2, lw - 4, lh - 2, (36, 104, 48))
    px(d, lx + 1, ly - 2, lw - 2, 5, (52, 128, 56))
    px(d, lx - 1, ly + 3, lw + 2, lh - 7, (44, 114, 50))
    px(d, lx + 2, ly - 3, lw - 6, 4, (72, 158, 68))
    for _ in range(lw * lh // 12):
        px(d, lx + rnd.randrange(0, lw), ly + rnd.randrange(0, lh), 2, 2,
           rnd.choice([(30, 92, 42), (62, 144, 60), (80, 170, 72)]))


def cloud(d: ImageDraw.ImageDraw, rnd: random.Random, x: int, y: int, w: int, a: int) -> None:
    col = (132, 150, 182, a)
    bands = [(0.62, -6), (1.0, 0), (0.82, 6)]
    for width, dy in bands:
        cw = max(6, int(w * width))
        px(d, x + (w - cw) // 2, y + dy, cw, 6, col)
    # a bump or two on top for silhouette variety
    for _ in range(rnd.randrange(1, 3)):
        bw = rnd.randrange(10, max(12, w // 2))
        px(d, x + rnd.randrange(0, max(1, w - bw)), y - 8, bw, 6, col)


def hill(d: ImageDraw.ImageDraw, rnd: random.Random, base_y: int, amp: int,
         color, top, w: int, step: int = 6, h: int = H) -> None:
    for x in range(-step, w + step, step):
        v = (math.sin(x * 0.021) * 0.6 + math.sin(x * 0.057 + 1.7) * 0.4)
        top_y = int(base_y - amp * (0.5 + v / 2) + rnd.randrange(-2, 3))
        px(d, x, top_y, step, max(1, h - top_y), color)
        px(d, x, top_y, step, 2, top)


def hero() -> Image.Image:
    rnd = random.Random(7)
    img = Image.new("RGBA", (W, H), (10, 14, 26, 255))
    d = ImageDraw.Draw(img)

    sky(d, W, H, [
        (0, (8, 11, 22)),
        (90, (15, 22, 42)),
        (150, (28, 44, 74)),
        (185, (46, 72, 108)),
        (H, (62, 94, 134)),
    ])

    # stars
    for _ in range(150):
        x, y = rnd.randrange(0, W), rnd.randrange(0, 150)
        b = rnd.randrange(80, 235)
        px(d, x, y, rnd.choice([1, 1, 1, 2]), 1, (b, b, min(255, b + 12)))

    glow(img, 356, 66, 74, (255, 246, 200), peak=95)

    # moon
    px(d, 344, 56, 26, 26, (247, 244, 222))
    px(d, 344, 56, 26, 3, (255, 253, 240))
    px(d, 364, 74, 6, 8, (226, 222, 200))
    px(d, 352, 66, 5, 5, (232, 228, 206))
    px(d, 358, 78, 4, 3, (232, 228, 206))

    for _ in range(7):
        cx0 = rnd.randrange(-20, W - 40)
        cy0 = rnd.randrange(30, 130)
        cw0 = rnd.randrange(40, 96)
        # keep the moon and its halo clear of clouds and nothing too close to the top edge
        if abs((cx0 + cw0 / 2) - 357) < 70 + cw0 / 2 and cy0 < 120:
            continue
        cloud(d, rnd, cx0, cy0, cw0, rnd.randrange(26, 52))

    hill(d, rnd, 206, 26, (26, 40, 58), (44, 64, 86), W, 8)
    hill(d, rnd, 224, 18, (17, 28, 34), (40, 66, 54), W, 6)
    hill(d, rnd, H + 6, 12, (9, 16, 20), (28, 48, 40), W, 5)

    # big central floating island with a tree
    island(d, rnd, 150, 148, 118, 44)
    tree(d, rnd, 200, 150)
    # a couple of small "ore" sparks in the dirt
    for _ in range(3):
        px(d, 170 + rnd.randrange(0, 70), 168 + rnd.randrange(0, 14), 2, 2,
           rnd.choice([(96, 226, 220), (232, 200, 96)]))

    island(d, rnd, 62, 186, 56, 20)
    tree(d, rnd, 84, 188, s=1)
    island(d, rnd, 300, 112, 44, 14)
    island(d, rnd, 366, 168, 34, 12)
    island(d, rnd, 26, 96, 28, 10)

    out = img.resize((W * SCALE, H * SCALE), Image.NEAREST).convert("RGB")
    return out


def favicon() -> Image.Image:
    s = 16
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    px(d, 0, 0, s, s, (58, 130, 54))
    px(d, 0, 0, s, 4, (104, 190, 84))
    px(d, 0, 3, s, 2, (78, 158, 66))
    for y in range(5, s):
        for x in range(s):
            rnd = random.Random(x * 31 + y * 17)
            px(d, x, y, 1, 1, rnd.choice([(122, 88, 58), (96, 68, 45), (108, 78, 50)]))
    px(d, 0, 0, s, 1, (140, 220, 120))
    px(d, 0, 0, 1, s, (140, 220, 120))
    px(d, s - 1, 4, 1, s - 4, (52, 40, 28))
    px(d, 1, s - 1, s - 1, 1, (52, 40, 28))
    return img.resize((64, 64), Image.NEAREST)


def icon_sword(d: ImageDraw.ImageDraw, x0: float, y0: float, x1: float, y1: float,
               blade=(214, 220, 232)) -> None:
    """Draw a chunky pixel sword from handle (x0, y0) to tip (x1, y1)."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px_, py_ = -uy, ux

    def stamp(t: float, half: float, color) -> None:
        cx, cy = x0 + ux * t, y0 + uy * t
        for o in range(-int(half), int(half) + 1):
            d.rectangle([cx + px_ * o - 0.5, cy + py_ * o - 0.5,
                         cx + px_ * o + 1.5, cy + py_ * o + 1.5], fill=color)

    for t in range(2, 9):                        # handle
        stamp(t, 1.2, (92, 62, 38))
    for o in range(-4, 5):                       # guard
        cx, cy = x0 + ux * 10 + px_ * o, y0 + uy * 10 + py_ * o
        d.rectangle([cx - 1, cy - 1, cx + 2, cy + 2], fill=(206, 166, 62))
    for t in range(11, int(length)):
        stamp(t, 1.4, blade)
    stamp(length - 1, 0.6, (250, 252, 255))


def mode_icon(kind: str) -> Image.Image:
    s = 64
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(kind)

    if kind == "anarchy":
        icon_sword(d, 12, 52, 52, 12)
        icon_sword(d, 52, 52, 12, 12)
    elif kind == "farm":
        px(d, 14, 40, 36, 6, GRASS[0])
        px(d, 14, 44, 36, 4, GRASS[1])
        px(d, 18, 46, 28, 6, DIRT[0])
        px(d, 22, 50, 20, 6, DIRT[1])
        px(d, 28, 54, 8, 4, STONE[1])
        px(d, 30, 26, 4, 14, (74, 52, 32))
        px(d, 20, 12, 24, 16, (52, 128, 56))
        px(d, 24, 8, 16, 6, (72, 158, 68))
        px(d, 30, 20, 4, 4, (30, 92, 42))
        for yy in range(14, 24):
            for xx in range(22, 42):
                if rnd.random() < 0.15:
                    px(d, xx, yy, 1, 1, (40, 112, 46))
    elif kind == "base":
        px(d, 8, 22, 48, 6, (150, 108, 64))
        px(d, 10, 14, 44, 10, (176, 130, 78))
        px(d, 10, 14, 44, 3, (205, 160, 100))
        px(d, 14, 26, 40, 14, (196, 48, 48))
        px(d, 14, 26, 40, 3, (226, 72, 72))
        px(d, 16, 30, 14, 8, (238, 236, 226))
        px(d, 12, 40, 6, 12, (120, 86, 52))
        px(d, 46, 40, 6, 12, (120, 86, 52))
        px(d, 14, 42, 36, 4, (96, 66, 40))
    elif kind == "clan":
        px(d, 30, 6, 16, 16, (250, 214, 96))
        px(d, 30, 6, 16, 3, (255, 238, 156))
        px(d, 4, 30, 24, 10, (186, 200, 224, 190))
        px(d, 8, 26, 16, 6, (206, 216, 236, 190))
        px(d, 12, 42, 34, 5, GRASS[0])
        px(d, 16, 47, 26, 5, DIRT[0])
        px(d, 20, 52, 18, 4, DIRT[1])
        px(d, 26, 56, 6, 3, STONE[1])
        icon_sword(d, 20, 40, 56, 12)
    elif kind == "scout":
        d.ellipse([8, 8, 42, 42], outline=(226, 232, 244), width=5)
        d.ellipse([14, 14, 36, 36], fill=(70, 92, 108, 90))
        d.ellipse([14, 14, 36, 36], outline=(150, 168, 190), width=2)
        for o in range(0, 12):
            d.rectangle([38 + o, 38 + o, 41 + o, 41 + o], fill=(150, 108, 66))
        d.rectangle([48, 48, 57, 57], fill=(120, 84, 50))
        px(d, 22, 22, 4, 4, (250, 252, 255))
    elif kind == "grief":
        px(d, 8, 44, 18, 14, GRASS[0])
        px(d, 8, 44, 18, 4, (140, 216, 118))
        px(d, 8, 50, 18, 3, GRASS[1])
        px(d, 10, 56, 14, 4, DIRT[1])
        px(d, 22, 30, 26, 12, (196, 202, 214))
        px(d, 22, 30, 26, 4, (232, 236, 244))
        px(d, 22, 38, 26, 4, (150, 156, 170))
        px(d, 30, 24, 10, 8, (196, 202, 214))
        px(d, 34, 42, 6, 14, (142, 100, 60))
        px(d, 34, 42, 2, 14, (172, 124, 78))
    else:
        px(d, 20, 20, 24, 24, (200, 200, 200))

    # 1px dark outline pass for readability on any background
    out = img.copy()
    alpha = img.split()[3]
    edge = alpha.filter(ImageFilter.FIND_EDGES)
    edge = edge.point(lambda v: 255 if v > 0 else 0)
    darkness = Image.new("RGBA", img.size, (6, 10, 18, 255))
    out.paste(darkness, (0, 0), edge)
    return Image.alpha_composite(out, img)


def og(hero_img: Image.Image) -> Image.Image:
    base = hero_img.copy()
    # crop to 1200x630 keeping the interesting middle band
    target_ratio = 1200 / 630
    w, h = base.size
    crop_h = int(w / target_ratio)
    top = int(h * 0.18)
    base = base.crop((0, top, w, min(h, top + crop_h))).resize((1200, 630), Image.LANCZOS)
    base = base.convert("RGBA")

    shade = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for y in range(630):
        a = int(215 * (1 - y / 630) ** 1.1) + 30
        sd.rectangle([0, y, 1200, y], fill=(6, 9, 16, min(240, a)))
    base.alpha_composite(shade)

    d = ImageDraw.Draw(base)
    f_big = ImageFont.truetype(FONT_BOLD, 132)
    f_mid = ImageFont.truetype(FONT_BOLD, 40)
    f_small = ImageFont.truetype(FONT_REG, 30)
    d.text((78, 210), "FUNTIME", font=f_big, fill=(126, 222, 96))
    d.text((82, 356), "фан-сайт · анархия, гайды, как зайти", font=f_mid,
           fill=(234, 240, 250))
    d.text((82, 420), "mc.funtime.su", font=f_small, fill=(150, 170, 195))
    d.rectangle([78, 470, 78 + 190, 478], fill=(126, 222, 96))
    d.text((82, 500), "Java Edition · 1.8 – 1.21", font=f_small, fill=(150, 170, 195))
    return base.convert("RGB")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    ICONS.mkdir(parents=True, exist_ok=True)

    hero_img = hero()
    hero_img.save(ASSETS / "hero.png", optimize=True)
    og(hero_img).save(ASSETS / "og.png", optimize=True)
    favicon().save(ASSETS / "favicon.png", optimize=True)

    for kind in ("anarchy", "grief", "base", "farm", "scout", "clan"):
        mode_icon(kind).save(ICONS / f"{kind}.png", optimize=True)

    print("ok", sorted(p.name for p in ASSETS.rglob("*.png")))


if __name__ == "__main__":
    main()
