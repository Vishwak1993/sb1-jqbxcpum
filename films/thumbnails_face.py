"""Big-face thumbnails for the films already on the channel (October 18).

The channel's first thumbnails (small figures, diagrams, a calendar, a laptop) got about 2% click-through and no clicks
from Suggested. These follow what works in the niche: one big round face filling half the frame with one pushed
emotion, one story object carrying the colour, one or two words at the top. Nothing in the bottom-right corner (the
time badge). Each keeps its film's own idea and a different colour, so the four don't look like one template.

    python thumbnails_face.py        writes <film>/packaging/<PREFIX>_thumbnail_face_1280x720.png (+ 320x180)
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "toolkit"))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.render import frame_image  # noqa: E402

INK = (22, 18, 22)
LG = "LuckiestGuy-Regular.ttf"


def oval(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


def outlined(ctx, s, x, y, size, rgb=TEXT, align="left"):
    for dx, dy in ((-7, 0), (7, 0), (0, -7), (0, 7), (-5, -5), (5, 5), (-5, 5), (5, -5)):
        draw_text(ctx, s, x + dx, y + dy, size, (10, 10, 14), align=align, face=LG)
    draw_text(ctx, s, x + 8, y + 14, size, (0, 0, 0), 0.5, align=align, face=LG)
    draw_text(ctx, s, x, y, size, rgb, align=align, face=LG)


def head(ctx, hx, hy, r, light=(0.6, -0.3), light_rgb=(255, 236, 200), shade=(20, 24, 40)):
    c = ctx.c
    hp = skia.Path()
    hp.addOval(oval(hx, hy, r, r * 1.03))
    c.drawPath(hp, blurred(fill((0, 0, 0), 0.5), 30))
    c.drawPath(hp, fill(SKIN))
    c.save()
    c.clipPath(hp, skia.ClipOp.kIntersect, True)
    sh = skia.GradientShader.MakeRadial((hx + light[0] * r * 0.6, hy + light[1] * r * 0.6), r * 1.6,
                                        [col(light_rgb, 0.3), col(shade, 0.55)])
    c.drawRect(oval(hx, hy, r * 1.1, r * 1.1), skia.Paint(Shader=sh))
    c.restore()
    c.drawPath(hp, stroke(LINE, 9))


def shoulders(ctx, hx, r, rgb=SKIN_SHADE):
    y = 930
    p = poly_path([(hx - r * 1.3, H + 40), (hx - r * 1.1, y + 80), (hx - r * 0.5, y), (hx + r * 0.5, y), (hx + r * 1.1, y + 80),
                   (hx + r * 1.3, H + 40)], smooth=True)
    ctx.c.drawPath(p, fill(rgb))
    ctx.c.drawPath(p, stroke(LINE, 8))


def eye(ctx, ex, ey, r, open_=1.0, look=(0.0, 0.0), red=0.0, lid=0.0, wet=0.0):
    """open_: height; lid: 0..1 heavy upper lid; red: veins; wet: a bright wet line on the lower lid."""
    c = ctx.c
    rx, ry = r * 0.16, r * 0.2 * open_
    white = skia.Path()
    white.addOval(oval(ex, ey, rx, ry))
    c.drawPath(white, fill((248, 240, 234)))
    c.save()
    c.clipPath(white, skia.ClipOp.kIntersect, True)
    for i in range(int(9 * red)):
        a = i * 0.72 + 0.2
        p0 = (ex + math.cos(a) * rx, ey + math.sin(a) * ry)
        p1 = (ex + math.cos(a) * rx * 0.45 + 5, ey + math.sin(a) * ry * 0.45 - 3)
        c.drawPath(poly_path([p0, ((p0[0] + p1[0]) / 2 + 4, (p0[1] + p1[1]) / 2 - 3), p1], closed=False, smooth=True),
                   stroke((214, 80, 80), 3.2, 0.85))
    px, py = ex + look[0] * rx * 0.35, ey + look[1] * ry * 0.35
    c.drawCircle(px, py, rx * 0.4, fill((70, 60, 56)))
    c.drawCircle(px, py, rx * 0.2, fill(INK))
    c.drawCircle(px - rx * 0.12, py - rx * 0.12, rx * 0.1, fill((255, 255, 255)))
    if lid > 0:
        c.drawRect(skia.Rect.MakeLTRB(ex - rx, ey - ry, ex + rx, ey - ry + 2 * ry * lid), fill((210, 202, 188)))
    if wet > 0:
        c.drawPath(poly_path([(ex - rx, ey + ry * 0.7), (ex, ey + ry * 1.0), (ex + rx, ey + ry * 0.7)], closed=False, smooth=True),
                   stroke((200, 225, 255), r * 0.025, wet))
    c.restore()
    if lid > 0:
        c.drawLine(ex - rx, ey - ry + 2 * ry * lid, ex + rx, ey - ry + 2 * ry * lid, stroke(INK, r * 0.03))
    c.drawPath(white, stroke(INK, 6))


def brow(ctx, ex, ey, r, side, inner_up=1.0):
    """side: -1 left eye, +1 right eye. inner_up > 0: worried (inner end up); < 0: angry (inner end down)."""
    rx, ry = r * 0.16, r * 0.2
    inner = (ex - side * rx * 0.9, ey - ry * (1.7 + 0.45 * inner_up))
    outer = (ex + side * rx * 1.2, ey - ry * (1.7 - 0.3 * inner_up))
    mid = ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 - ry * 0.12)
    ctx.c.drawPath(poly_path([inner, mid, outer], closed=False, smooth=True), stroke(INK, r * 0.055))


def drop(ctx, x, y, d):
    p = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
    ctx.c.drawPath(p, fill((196, 222, 255), 0.95))
    ctx.c.drawPath(p, stroke((90, 120, 170), 4))


def tear(ctx, x, y, r):
    ctx.c.drawPath(poly_path([(x, y), (x + r * 0.01, y + r * 0.25)], closed=False), stroke((200, 225, 255), r * 0.03, 0.8))
    drop(ctx, x + r * 0.01, y + r * 0.3, r * 0.045)


def mouth_line(ctx, pts, r, w=0.035):
    ctx.c.drawPath(poly_path(pts, closed=False, smooth=True), stroke(INK, r * w))


def grin(ctx, mx, my, r, wide=0.26, teeth=True):
    c = ctx.c
    p = skia.Path()
    p.moveTo(mx - r * wide, my - r * 0.03)
    p.quadTo(mx, my + r * 0.24, mx + r * wide, my - r * 0.03)
    p.quadTo(mx, my + r * 0.08, mx - r * wide, my - r * 0.03)
    p.close()
    c.drawPath(p, fill((250, 248, 240)))
    if teeth:
        for k in range(6):
            x = mx - r * wide * 0.75 + k * r * wide * 0.3
            c.drawLine(x, my + r * 0.02, x, my + r * 0.13, stroke(INK, 3))
    c.drawPath(p, stroke(INK, r * 0.03))


def hand(ctx, x, y, s=1.0, ang=-1.2):
    """A forearm coming up from the bottom of the frame to (x, y), fingers closed."""
    c = ctx.c
    base = (x + math.cos(ang + math.pi) * 420 * s, y + math.sin(ang + math.pi) * 420 * s)
    c.drawLine(base[0], base[1], x, y, stroke(LINE, 112 * s))
    c.drawLine(base[0], base[1], x, y, stroke(SKIN_SHADE, 96 * s))
    c.drawCircle(x, y, 62 * s, fill(SKIN_SHADE))
    c.drawCircle(x, y, 62 * s, stroke(LINE, 7))


def clench(ctx, mx, my, r):
    """Teeth clenched under strain: a wide box of teeth, the corners pulled down."""
    c = ctx.c
    w, h = r * 0.26, r * 0.1
    p = poly_path([(mx - w, my + h * 0.6), (mx - w * 0.8, my - h * 0.5), (mx + w * 0.8, my - h * 0.5), (mx + w, my + h * 0.6),
                   (mx + w * 0.7, my + h * 0.9), (mx - w * 0.7, my + h * 0.9)], smooth=True)
    c.drawPath(p, fill((250, 248, 240)))
    c.drawLine(mx - w * 0.85, my + h * 0.2, mx + w * 0.85, my + h * 0.2, stroke(INK, 3))
    for k in range(7):
        x = mx - w * 0.75 + k * w * 0.25
        c.drawLine(x, my - h * 0.4, x, my + h * 0.8, stroke(INK, 3))
    c.drawPath(p, stroke(INK, r * 0.03))
    for side in (-1, 1):  # strain lines at the corners
        c.drawLine(mx + side * w * 1.05, my + h * 0.5, mx + side * w * 1.2, my + h * 1.2, stroke(INK, r * 0.02))


# ---- NO.: a forced smile, red strings on his wrists ------------------------------------------------
def scene_no(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((24, 16, 18)))
    glow(ctx, 1000, 300, 900, RED, 0.18)
    hx, hy, r = 1080, 600, 360
    # strings from above to his wrists and head
    tops = [(760, -20), (1080, -20), (1420, -20)]
    wrists = [(640, 640), (1520, 640)]
    for (wx, wy), (tx, ty) in zip(wrists, (tops[0], tops[2])):
        c.drawLine(tx, ty, wx, wy - 60, blurred(stroke(RED, 10, 0.6), 4))
        c.drawLine(tx, ty, wx, wy - 60, stroke(RED, 5))
    c.drawLine(1080, -20, hx, hy - r, stroke(RED, 5))
    shoulders(ctx, hx, r)
    for (wx, wy), ang in zip(wrists, (-1.25, -1.9)):
        hand(ctx, wx, wy, 0.95, ang)
        c.drawLine(wx - 50, wy - 60, wx + 50, wy - 50, stroke(RED, 9))  # the knot
    head(ctx, hx, hy, r, light=(0.0, -0.8), light_rgb=(255, 180, 170))
    for side in (-1, 1):
        ex = hx + side * r * 0.3
        eye(ctx, ex, hy - r * 0.06, r, open_=1.15, look=(0.0, 0.2), red=1.0)
        brow(ctx, ex, hy - r * 0.06, r, side, inner_up=1.1)
    grin(ctx, hx, hy + r * 0.48, r, wide=0.3)
    drop(ctx, hx - r * 0.75, hy - r * 0.35, r * 0.07)
    drop(ctx, hx + r * 0.8, hy - r * 0.05, r * 0.055)
    outlined(ctx, "YES.", 70, 250, 240)
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


# ---- LATER.: his dad calling, his thumb over DECLINE --------------------------------------------------
def scene_later(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((16, 18, 26)))
    hx, hy, r = 620, 600, 360
    shoulders(ctx, hx, r)
    head(ctx, hx, hy, r, light=(0.9, 0.2), light_rgb=(170, 200, 255))
    for side in (-1, 1):
        ex = hx + r * 0.1 + side * r * 0.28
        eye(ctx, ex, hy - r * 0.02, r, open_=0.85, look=(0.9, 0.5), lid=0.25, wet=0.8)
        brow(ctx, ex, hy - r * 0.02, r, side, inner_up=1.0)
    mouth_line(ctx, [(hx - r * 0.06, hy + r * 0.52), (hx + r * 0.12, hy + r * 0.46), (hx + r * 0.3, hy + r * 0.52)], r)
    tear(ctx, hx + r * 0.42, hy + r * 0.12, r)
    # the phone: DAD calling
    px, py = 1360, 600
    c.save()
    c.translate(px, py)
    c.rotate(-6)
    glow(ctx, 0, 0, 420, BLUE, 0.35)
    rrect(ctx, -170, -330, 340, 620, 40, (16, 16, 18), (90, 90, 100), 6)
    rrect(ctx, -152, -312, 304, 584, 30, (40, 52, 80), None)
    c.drawCircle(0, -160, 78, fill((190, 180, 160)))
    c.drawPath(poly_path([(-50, -150), (-40, -120), (40, -120), (50, -150)], closed=False, smooth=True), stroke((90, 80, 70), 10))
    draw_text(ctx, "DAD", 0, -20, 74, TEXT, face=LG)
    draw_text(ctx, "calling...", 0, 30, 36, (190, 200, 220))
    c.drawCircle(-80, 170, 52, fill(RED))
    c.drawLine(-104, 170, -56, 170, stroke(TEXT, 10))
    c.drawCircle(80, 170, 52, fill((70, 190, 110)))
    c.restore()
    hand(ctx, 1290, 840, 0.85, ang=-1.55)
    outlined(ctx, "LATER.", W - 70, 250, 220, align="right")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


# ---- 1%.: wrecked tired, the red battery at 1% ------------------------------------------------------
def scene_one(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((18, 18, 22)))
    glow(ctx, 1450, 560, 520, RED, 0.25)
    hx, hy, r = 720, 620, 360
    shoulders(ctx, hx, r)
    head(ctx, hx, hy, r, light=(0.8, 0.0), light_rgb=(255, 170, 160), shade=(10, 12, 20))
    for side in (-1, 1):
        ex = hx + side * r * 0.3
        eye(ctx, ex, hy - r * 0.02, r, open_=0.95, look=(0.0, 0.4), red=0.9, lid=0.55)
        brow(ctx, ex, hy - r * 0.02, r, side, inner_up=0.7)
        for k in range(2):  # dark bags
            c.drawPath(poly_path([(ex - r * 0.14, hy + r * (0.2 + 0.07 * k)), (ex, hy + r * (0.25 + 0.07 * k)),
                                  (ex + r * 0.14, hy + r * (0.2 + 0.07 * k))], closed=False, smooth=True),
                       stroke((120, 110, 140), r * 0.022, 0.8 - 0.3 * k))
    mouth_line(ctx, [(hx - r * 0.16, hy + r * 0.56), (hx, hy + r * 0.52), (hx + r * 0.16, hy + r * 0.57)], r)
    drop(ctx, hx - r * 0.7, hy - r * 0.42, r * 0.06)
    # the battery
    bx, by, bw, bh = 1260, 420, 420, 220
    rrect(ctx, bx, by, bw, bh, 34, (24, 22, 26), (230, 230, 236), 16)
    rrect(ctx, bx + bw + 6, by + 70, 40, 80, 10, (230, 230, 236), None)
    rrect(ctx, bx + 26, by + 26, 30, bh - 52, 8, RED, None)
    glow(ctx, bx + 41, by + bh / 2, 120, RED, 0.6)
    draw_text(ctx, "1%", bx + bw / 2 + 30, by + bh / 2 + 44, 130, RED, face=LG, glow_rgb=RED_D)
    outlined(ctx, "RUNNING ON", W - 70, 250, 120, align="right")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


# ---- HEAVY.: straining under the red sack, teeth gritted ---------------------------------------------
def scene_heavy(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((26, 22, 30)))
    glow(ctx, 1300, 380, 700, RED, 0.18)
    # the sack, over his shoulder, bigger than he is
    sx, sy = 1300, 380
    sack = poly_path([(sx - 380, sy + 420), (sx - 420, sy + 80), (sx - 260, sy - 260), (sx + 40, sy - 330), (sx + 330, sy - 180),
                      (sx + 420, sy + 160), (sx + 300, sy + 470), (sx - 60, sy + 520)], smooth=True)
    c.drawPath(sack, blurred(fill((0, 0, 0), 0.5), 24))
    c.drawPath(sack, fill((140, 112, 80)))
    c.drawPath(sack, stroke(LINE, 9))
    for (dx, dy, rr, name) in ((-200, -120, 110, "KAI"), (40, -180, 120, "BOSS"), (230, -20, 100, "EX"), (-60, 80, 110, "DAD")):
        x, y = sx + dx, sy + dy
        c.drawCircle(x, y, rr, blurred(fill(RED, 0.5), 18))
        c.drawCircle(x, y, rr, fill((200, 40, 40)))
        c.drawCircle(x, y, rr, stroke((90, 10, 12), 7))
        rrect(ctx, x - rr * 0.7, y - 30, rr * 1.4, 60, 10, (236, 232, 214), None)
        draw_text(ctx, name, x, y + 20, 50, (40, 40, 46), face=LG)
    hx, hy, r = 620, 640, 350
    shoulders(ctx, hx, r)
    c.drawPath(poly_path([(hx + r * 0.5, 930), (sx - 380, sy + 420)], closed=False), stroke((110, 86, 60), 40))  # the strap
    head(ctx, hx, hy, r, light=(-0.6, -0.4))
    for side in (-1, 1):
        ex = hx + r * 0.08 + side * r * 0.28
        eye(ctx, ex, hy - r * 0.04, r, open_=0.6, look=(0.6, -0.2), red=0.8)
        brow(ctx, ex, hy - r * 0.04, r, side, inner_up=-1.0)
    clench(ctx, hx + r * 0.06, hy + r * 0.5, r)
    for k in range(4):
        drop(ctx, hx - r * 0.8 + k * r * 0.5, hy - r * 0.6 + (k % 2) * r * 0.2, r * 0.06)
    outlined(ctx, "HEAVY.", 70, 250, 230)
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


JOBS = [("no", "NO", scene_no), ("later", "LATER", scene_later), ("onepercent", "ONE_PERCENT", scene_one), ("heavy", "HEAVY", scene_heavy)]

if __name__ == "__main__":
    only = sys.argv[1:]
    for folder, prefix, fn in JOBS:
        if only and folder not in only:
            continue
        img = frame_image(fn, 1.0, 30)
        out = HERE / folder / "packaging"
        save(img, 1280, 720, out / f"{prefix}_thumbnail_face_1280x720.png")
        save(img, 320, 180, out / f"{prefix}_thumbnail_face_320x180.png")
        print(folder, "ok")
