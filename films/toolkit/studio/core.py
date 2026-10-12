"""Drawing core: colours, hand-drawn wobble, glow, text and the film finish.

Everything is deterministic: the same (frame, id) always draws the same wobble,
so frames can be rendered in parallel and re-rendered identically.
"""
import math
from pathlib import Path

import numpy as np
import skia

W, H = 1920, 1080
FPS = 30
FONT_DIR = Path(__file__).resolve().parents[1] / "assets" / "fonts"

# ---- palette (see STYLE_BIBLE.md) ------------------------------------------
BG = (14, 14, 16)
FLOOR = (58, 58, 64)
LINE = (24, 22, 24)
SKIN = (236, 230, 214)
SKIN_SHADE = (205, 198, 182)
GREY = (70, 70, 78)
GREY_D = (44, 44, 50)
GREY_L = (110, 110, 120)
TEXT = (242, 240, 234)
RED = (226, 48, 48)
RED_D = (120, 16, 18)
GOLD = (255, 196, 92)
BLUE = (120, 170, 255)  # screen glow only

LETTERBOX = 70  # px bars top and bottom


def col(rgb, a=1.0):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(max(0, min(1, a)) * 255))


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


# ---- easing ------------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x, s=1.7):
    x = clamp(x) - 1
    return 1 + x * x * ((s + 1) * x + s)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp2(p, q, t):
    return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))


def fade(t, t0, t1, fin=0.5, fout=0.5):
    """1 inside [t0, t1] with soft edges."""
    if t < t0 or t > t1:
        return 0.0
    a = ease(prog(t, t0, t0 + fin)) if fin > 0 else 1.0
    b = 1 - ease(prog(t, t1 - fout, t1)) if fout > 0 else 1.0
    return min(a, b)


# ---- deterministic noise -----------------------------------------------------
def hrand(*keys):
    """Hash any ints/floats/strings to a stable float in [0, 1)."""
    h = 2166136261
    for k in keys:
        for ch in str(k):
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0x5BD1E995) & 0xFFFFFFFF
    h ^= h >> 15
    return (h & 0xFFFFFF) / float(0x1000000)


class Ctx:
    """Per-frame state: canvas, time and boil step (outlines redraw every 3 frames)."""

    def __init__(self, canvas, t, frame):
        self.c = canvas
        self.t = t
        self.frame = frame
        self.boil = frame // 3

    def j(self, key, amp=1.4):
        """Small stable jitter for hand-drawn wobble."""
        return (hrand(key, self.boil, "x") - 0.5) * 2 * amp, (hrand(key, self.boil, "y") - 0.5) * 2 * amp


# ---- paints ------------------------------------------------------------------
def fill(rgb, a=1.0):
    return skia.Paint(AntiAlias=True, Color=col(rgb, a), Style=skia.Paint.kFill_Style)


def stroke(rgb, w, a=1.0, cap=skia.Paint.kRound_Cap):
    return skia.Paint(AntiAlias=True, Color=col(rgb, a), Style=skia.Paint.kStroke_Style,
                      StrokeWidth=w, StrokeCap=cap, StrokeJoin=skia.Paint.kRound_Join)


def blurred(paint, sigma):
    paint.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return paint


# ---- wobbly primitives -------------------------------------------------------
def wobble_points(ctx, pts, key, amp=1.4):
    out = []
    for i, (x, y) in enumerate(pts):
        dx, dy = ctx.j((key, i), amp)
        out.append((x + dx, y + dy))
    return out


def poly_path(pts, closed=True, smooth=False):
    p = skia.Path()
    if not pts:
        return p
    if smooth and len(pts) > 2:
        n = len(pts)
        mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
        if closed:
            p.moveTo(*mids[-1])
            for i in range(n):
                p.quadTo(pts[i][0], pts[i][1], mids[i][0], mids[i][1])
            p.close()
        else:
            p.moveTo(*pts[0])
            for i in range(1, n - 1):
                p.quadTo(pts[i][0], pts[i][1], mids[i][0], mids[i][1])
            p.lineTo(*pts[-1])
        return p
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def circle_pts(cx, cy, rx, ry=None, n=28, rot=0.0):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(rot + 2 * math.pi * i / n), cy + ry * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def wcircle(ctx, cx, cy, r, key, fillc=None, line=LINE, lw=3.0, amp=1.0, a=1.0, ry=None):
    pts = wobble_points(ctx, circle_pts(cx, cy, r, ry), key, amp)
    path = poly_path(pts, smooth=True)
    if fillc is not None:
        ctx.c.drawPath(path, fill(fillc, a))
    if line is not None and lw > 0:
        ctx.c.drawPath(path, stroke(line, lw, a))
    return path


def rect_pts(x, y, w, h, seg=4):
    pts = []
    for i in range(seg):
        pts.append((x + w * i / seg, y))
    for i in range(seg):
        pts.append((x + w, y + h * i / seg))
    for i in range(seg):
        pts.append((x + w - w * i / seg, y + h))
    for i in range(seg):
        pts.append((x, y + h - h * i / seg))
    return pts


def wrect(ctx, x, y, w, h, key, fillc=None, line=LINE, lw=3.0, amp=1.2, a=1.0, seg=4):
    pts = wobble_points(ctx, rect_pts(x, y, w, h, seg), key, amp)
    path = poly_path(pts)
    if fillc is not None:
        ctx.c.drawPath(path, fill(fillc, a))
    if line is not None and lw > 0:
        ctx.c.drawPath(path, stroke(line, lw, a))
    return path


def rrect(ctx, x, y, w, h, r, fillc=None, line=None, lw=3.0, a=1.0):
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    if fillc is not None:
        ctx.c.drawRRect(rr, fill(fillc, a))
    if line is not None:
        ctx.c.drawRRect(rr, stroke(line, lw, a))


def wline(ctx, p, q, key, rgb=LINE, w=3.0, a=1.0, amp=1.0, seg=3):
    pts = [lerp2(p, q, i / seg) for i in range(seg + 1)]
    pts = wobble_points(ctx, pts, key, amp)
    ctx.c.drawPath(poly_path(pts, closed=False), stroke(rgb, w, a))


def glow(ctx, x, y, r, rgb, a=0.5):
    """Soft radial light. Light is emotion: only what matters gets lit."""
    shader = skia.GradientShader.MakeRadial(
        (x, y), r, [col(rgb, a), col(rgb, a * 0.35), col(rgb, 0)], [0, 0.35, 1])
    ctx.c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=shader))


def cone(ctx, apex, left, right, rgb, a=0.25):
    path = poly_path([apex, left, right])
    shader = skia.GradientShader.MakeLinear([apex, ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2)],
                                            [col(rgb, a), col(rgb, 0)])
    ctx.c.drawPath(path, skia.Paint(AntiAlias=True, Shader=shader))


# ---- text --------------------------------------------------------------------
_typefaces = {}


def typeface(name="PatrickHand-Regular.ttf"):
    if name not in _typefaces:
        _typefaces[name] = skia.Typeface.MakeFromFile(str(FONT_DIR / name))
    return _typefaces[name]


def text_width(s, size, face="PatrickHand-Regular.ttf"):
    return skia.Font(typeface(face), size).measureText(s)


def draw_text(ctx, s, x, y, size, rgb=TEXT, a=1.0, align="center", face="PatrickHand-Regular.ttf", glow_rgb=None):
    if a <= 0.001 or not s:
        return
    font = skia.Font(typeface(face), size)
    font.setEdging(skia.Font.Edging.kAntiAlias)
    w = font.measureText(s)
    ox = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    if glow_rgb is not None:
        ctx.c.drawString(s, ox, y, font, blurred(fill(glow_rgb, a * 0.8), size * 0.25))
    ctx.c.drawString(s, ox, y, font, fill(rgb, a))
    return w


def caption(ctx, s, t0, t1, y=190, size=50, rgb=TEXT, glow_rgb=None):
    """Narration caption: calm, white, centred near the top, fades in 0.5 s."""
    a = fade(ctx.t, t0, t1, 0.5, 0.5)
    draw_text(ctx, s, W / 2, y, size, rgb, a, glow_rgb=glow_rgb)


def villain_text(ctx, s, t0, t1, x, y, size=44):
    """Villain voice: small, red, lower-case, drifting up and trembling."""
    if not (t0 <= ctx.t <= t1):
        return
    a = fade(ctx.t, t0, t1, 0.25, 0.45)
    k = prog(ctx.t, t0, t1)
    dx, dy = ctx.j(("vt", s), 1.6)
    draw_text(ctx, s, x + dx, y - 26 * k + dy, size, RED, a, glow_rgb=RED_D)


# ---- film finish -------------------------------------------------------------
_grain = None
_vignette = None


def _grain_tiles():
    global _grain
    if _grain is None:
        rng = np.random.default_rng(1234)
        tiles = []
        for _ in range(8):
            g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
            v = np.clip(128 + g * 60, 0, 255).astype(np.uint8)
            rgba = np.dstack([v, v, v, np.full_like(v, 255)])
            tiles.append(skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType))
        _grain = tiles
    return _grain


def finish(ctx, bars=True, grain=0.045, vignette=0.55):
    c = ctx.c
    # vignette
    shader = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.62,
                                            [col((0, 0, 0), 0), col((0, 0, 0), 0), col((0, 0, 0), vignette)],
                                            [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=shader))
    # grain (overlay-style, changes every 2 frames, repeatable)
    tile = _grain_tiles()[(ctx.frame // 2) % 8]
    p = skia.Paint(Alphaf=grain)
    p.setBlendMode(skia.BlendMode.kOverlay)
    c.drawImageRect(tile, skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.FilterMode.kLinear), p)
    if bars:
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, LETTERBOX), fill((0, 0, 0)))
        c.drawRect(skia.Rect.MakeXYWH(0, H - LETTERBOX, W, LETTERBOX), fill((0, 0, 0)))


def black(ctx, a):
    if a > 0:
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((0, 0, 0), a))


class Camera:
    """Zoom about a focus point, pan and shake. Use with `with cam.apply(ctx):`."""

    def __init__(self, zoom=1.0, cx=W / 2, cy=H / 2, shake=0.0):
        self.zoom, self.cx, self.cy, self.shake = zoom, cx, cy, shake

    def apply(self, ctx):
        cam = self

        class _C:
            def __enter__(s):
                ctx.c.save()
                sx = sy = 0
                if cam.shake > 0:
                    sx = (hrand("shake", ctx.frame, 1) - 0.5) * 2 * cam.shake
                    sy = (hrand("shake", ctx.frame, 2) - 0.5) * 2 * cam.shake
                ctx.c.translate(W / 2 + sx, H / 2 + sy)
                ctx.c.scale(cam.zoom, cam.zoom)
                ctx.c.translate(-cam.cx, -cam.cy)

            def __exit__(s, *a):
                ctx.c.restore()

        return _C()
