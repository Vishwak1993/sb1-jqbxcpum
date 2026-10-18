"""ALL IN. thumbnails, 1280x720. Both are big-face thumbnails (the channel's click-through was 1.9% with small figures).

A: a close-up of his face lit green-and-red from below by the phone, wide bloodshot eyes, sweat, a nervous grin; the
   phone in his hand shows a red LOST over ₹37,400. "ALL IN." in white, top right.
B: the same face from the side, the villain leaning in behind his shoulder, whispering; a gold coin on the right with
   "WIN IT BACK." across the top: the villain's line as the words.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
sys.path.insert(0, str(HERE.parent))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.render import frame_image  # noqa: E402
from studio import props as P  # noqa: E402
import scene as SC  # noqa: E402

INK = (22, 18, 22)
LG = "LuckiestGuy-Regular.ttf"


def oval(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


def outlined(ctx, s, x, y, size, rgb, align="left"):
    for dx, dy in ((-7, 0), (7, 0), (0, -7), (0, 7), (-5, -5), (5, 5), (-5, 5), (5, -5)):
        draw_text(ctx, s, x + dx, y + dy, size, (10, 10, 14), align=align, face=LG)
    draw_text(ctx, s, x + 8, y + 14, size, (0, 0, 0), 0.5, align=align, face=LG)
    draw_text(ctx, s, x, y, size, rgb, align=align, face=LG)


def wide_eye(ctx, ex, ey, r, look=(0.0, 0.3)):
    """A wide, bloodshot, scared eye with a small pupil."""
    c = ctx.c
    rx, ry = r * 0.17, r * 0.21
    white = skia.Path()
    white.addOval(oval(ex, ey, rx, ry))
    c.drawPath(white, fill((248, 240, 234)))
    c.save()
    c.clipPath(white, skia.ClipOp.kIntersect, True)
    for i in range(9):
        a = i * 0.72 + 0.2
        p0 = (ex + math.cos(a) * rx, ey + math.sin(a) * ry)
        p1 = (ex + math.cos(a) * rx * 0.45 + 5, ey + math.sin(a) * ry * 0.45 - 3)
        c.drawPath(poly_path([p0, ((p0[0] + p1[0]) / 2 + 4, (p0[1] + p1[1]) / 2 - 3), p1], closed=False, smooth=True),
                   stroke((214, 80, 80), 3.2, 0.85))
    px, py = ex + look[0] * rx * 0.3, ey + look[1] * ry * 0.3
    c.drawCircle(px, py, rx * 0.36, fill((70, 60, 56)))
    c.drawCircle(px, py, rx * 0.17, fill(INK))
    c.drawCircle(px - rx * 0.1, py - ry * 0.1, rx * 0.09, fill((255, 255, 255)))
    c.restore()
    c.drawPath(white, stroke(INK, 6))


def brow(ctx, ex, ey, r, side):
    """Worried brow: the inner end (toward the middle of the face) up."""
    rx, ry = r * 0.17, r * 0.21
    inner = (ex - side * rx * 0.9, ey - ry * 2.0)
    outer = (ex + side * rx * 1.2, ey - ry * 1.3)
    ctx.c.drawPath(poly_path([inner, ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 - ry * 0.15), outer], closed=False, smooth=True),
                   stroke(INK, r * 0.055))


def drop(ctx, x, y, d):
    p = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
    ctx.c.drawPath(p, fill((196, 222, 255), 0.95))
    ctx.c.drawPath(p, stroke((90, 120, 170), 4))


def head(ctx, hx, hy, r, light_from=(0.0, 1.0), glow_rgb=SC.WINGREEN):
    c = ctx.c
    hp = skia.Path()
    hp.addOval(oval(hx, hy, r, r * 1.03))
    c.drawPath(hp, blurred(fill((0, 0, 0), 0.5), 30))
    c.drawPath(hp, fill(SKIN))
    c.save()
    c.clipPath(hp, skia.ClipOp.kIntersect, True)
    sh = skia.GradientShader.MakeRadial((hx + light_from[0] * r * 0.5, hy + light_from[1] * r * 0.7), r * 1.5,
                                        [col(glow_rgb, 0.35), col((20, 24, 40), 0.55)])
    c.drawRect(oval(hx, hy, r * 1.1, r * 1.1), skia.Paint(Shader=sh))
    c.restore()
    c.drawPath(hp, stroke(LINE, 9))


def nervous_grin(ctx, mx, my, r):
    c = ctx.c
    p = skia.Path()
    p.moveTo(mx - r * 0.24, my)
    p.quadTo(mx, my + r * 0.2, mx + r * 0.24, my - r * 0.02)
    p.quadTo(mx, my + r * 0.07, mx - r * 0.24, my)
    p.close()
    c.drawPath(p, fill((250, 248, 240)))
    for k in range(5):
        x = mx - r * 0.16 + k * r * 0.08
        c.drawLine(x, my + r * 0.01, x, my + r * 0.11, stroke(INK, 3))
    c.drawPath(p, stroke(INK, r * 0.03))


def phone_big(ctx, cx, cy, s=1.0, rot=0.0):
    c = ctx.c
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    glow(ctx, 0, -40, 380 * s, SC.WINGREEN, 0.4)
    rrect(ctx, -110 * s, -200 * s, 220 * s, 400 * s, 30 * s, (16, 16, 18), (90, 90, 100), 6)
    rrect(ctx, -96 * s, -186 * s, 192 * s, 372 * s, 22 * s, (24, 30, 28), None)
    rrect(ctx, -84 * s, -90 * s, 168 * s, 110 * s, 16 * s, RED, None)
    draw_text(ctx, "LOST", 0, -16 * s, 64 * s, TEXT, face=LG)
    SC.rtext(ctx, "₹37,400", 0, 90 * s, 46 * s, TEXT, face=LG)
    c.restore()


def hand(ctx, x, y, s=1.0):
    c = ctx.c
    c.drawPath(poly_path([(x - 30 * s, H + 60), (x - 10 * s, y + 160 * s), (x, y + 40 * s)], closed=False, smooth=True), stroke(LINE, 112 * s))
    c.drawPath(poly_path([(x - 30 * s, H + 60), (x - 10 * s, y + 160 * s), (x, y + 40 * s)], closed=False, smooth=True), stroke(SKIN_SHADE, 96 * s))
    for i in range(4):
        fx, fy = x - 70 * s, y - 40 * s + i * 42 * s
        c.drawLine(fx, fy, fx + 60 * s, fy + 6 * s, stroke(LINE, 44 * s))
        c.drawLine(fx, fy, fx + 60 * s, fy + 6 * s, stroke(SKIN_SHADE, 30 * s))


def scene_a(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((14, 16, 20)))
    glow(ctx, 760, 900, 900, SC.WINGREEN, 0.18)
    hx, hy, r = 760, 560, 380
    c.drawPath(poly_path([(260, H + 40), (340, 1010), (560, 930), (960, 930), (1180, 1010), (1260, H + 40)], smooth=True), fill(SKIN_SHADE))
    c.drawPath(poly_path([(260, H + 40), (340, 1010), (560, 930), (960, 930), (1180, 1010), (1260, H + 40)], smooth=True), stroke(LINE, 8))
    head(ctx, hx, hy, r)
    for side in (-1, 1):
        ex = hx + side * r * 0.32
        wide_eye(ctx, ex, hy - r * 0.04, r, look=(0.4, 0.8))
        brow(ctx, ex, hy - r * 0.04, r, side)
    nervous_grin(ctx, hx, hy + r * 0.5, r)
    drop(ctx, hx - r * 0.72, hy - r * 0.4, r * 0.07)
    drop(ctx, hx + r * 0.78, hy - r * 0.15, r * 0.055)
    drop(ctx, hx - r * 0.6, hy + r * 0.25, r * 0.045)
    phone_big(ctx, 1380, 720, 1.35, rot=-8)
    hand(ctx, 1470, 990, 1.1)
    outlined(ctx, "ALL IN.", W - 70, 250, 240, TEXT, align="right")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def scene_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((18, 14, 16)))
    glow(ctx, 600, 500, 800, RED, 0.18)
    # the villain behind his shoulder, leaning in to whisper
    P.villain(ctx, 600, 1380, scale=3.0, alpha=1.0, grin=1.3, lean=0.35)
    hx, hy, r = 1060, 640, 330
    c.drawPath(poly_path([(620, H + 40), (700, 1010), (900, 950), (1240, 950), (1420, 1010), (1500, H + 40)], smooth=True), fill(SKIN_SHADE))
    c.drawPath(poly_path([(620, H + 40), (700, 1010), (900, 950), (1240, 950), (1420, 1010), (1500, H + 40)], smooth=True), stroke(LINE, 8))
    head(ctx, hx, hy, r, light_from=(1.0, 0.6), glow_rgb=(255, 210, 120))
    for side in (-1, 1):
        ex = hx + r * 0.12 + side * r * 0.3
        wide_eye(ctx, ex, hy - r * 0.02, r, look=(0.8, 0.0))
        brow(ctx, ex, hy - r * 0.02, r, side)
    c.drawPath(poly_path([(hx - r * 0.06, hy + r * 0.5), (hx + r * 0.14, hy + r * 0.46), (hx + r * 0.34, hy + r * 0.5)], closed=False, smooth=True),
               stroke(INK, r * 0.04))
    drop(ctx, hx - r * 0.7, hy - r * 0.3, r * 0.07)
    # the gold coin he's staring at
    glow(ctx, 1640, 640, 360, GOLD, 0.5)
    c.drawCircle(1640, 640, 150, fill((240, 200, 90)))
    c.drawCircle(1640, 640, 150, stroke((150, 110, 30), 10))
    c.drawCircle(1640, 640, 118, stroke((200, 160, 60), 6))
    SC._rupee(ctx, 1640 - SC._rupee_w(170) / 2, 700, 170, (150, 110, 30), 1.0, True)
    outlined(ctx, "WIN IT BACK.", W / 2, 230, 200, TEXT, align="center")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    for fn, tag in ((scene_a, ""), (scene_b, "_B")):
        img = frame_image(fn, 1.0, 30)
        save(img, 1280, 720, HERE / f"ALL_IN_thumbnail{tag}_1280x720.png")
        save(img, 320, 180, HERE / f"ALL_IN_thumbnail{tag}_320x180.png")
    print("ok")
