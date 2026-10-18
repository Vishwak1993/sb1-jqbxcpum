"""FINE. thumbnail A, 1280x720: a new layout for us, a reveal split across one face.

A close-up of his head, lit from a door ajar on the right. The smiling mask, with its red grin, covers the left half
of his face and is being pulled away by his hand; the right half shows what was under it: a red-rimmed, wet eye, a
heavy worried brow, one tear, a trembling mouth. "FINE." in white, top right. The words say one thing, the face says
the other. Drawn with the film's own mask code.
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
import scene as SC  # noqa: E402

INK = (22, 18, 22)


def oval(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


def outlined(ctx, s, x, y, size, rgb, align="left"):
    for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6), (-4, -4), (4, 4), (-4, 4), (4, -4)):
        draw_text(ctx, s, x + dx, y + dy, size, (10, 10, 14), align=align, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, s, x + 8, y + 14, size, (0, 0, 0), 0.5, align=align, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, s, x, y, size, rgb, align=align, face="LuckiestGuy-Regular.ttf")


def wet_eye(ctx, ex, ey, r):
    """A sad, red-rimmed, wet eye: veins, a heavy lid, a bright wet highlight."""
    c = ctx.c
    rx, ry = r * 0.17, r * 0.2
    white = skia.Path()
    white.addOval(oval(ex, ey, rx, ry))
    c.drawPath(white, fill((246, 236, 230)))
    c.save()
    c.clipPath(white, skia.ClipOp.kIntersect, True)
    for i in range(7):  # veins
        a = i * 0.9 + 0.3
        p0 = (ex + math.cos(a) * rx, ey + math.sin(a) * ry)
        p1 = (ex + math.cos(a) * rx * 0.5 + 6, ey + math.sin(a) * ry * 0.5 - 4)
        c.drawPath(poly_path([p0, ((p0[0] + p1[0]) / 2 + 5, (p0[1] + p1[1]) / 2 - 4), p1], closed=False, smooth=True),
                   stroke((214, 90, 90), 3, 0.8))
    c.drawCircle(ex + rx * 0.05, ey + ry * 0.12, rx * 0.5, fill((84, 70, 64)))
    c.drawCircle(ex + rx * 0.05, ey + ry * 0.12, rx * 0.25, fill(INK))
    c.drawCircle(ex - rx * 0.12, ey - ry * 0.02, rx * 0.13, fill((255, 255, 255)))
    c.drawCircle(ex + rx * 0.2, ey + ry * 0.3, rx * 0.06, fill((255, 255, 255)))
    c.drawRect(skia.Rect.MakeLTRB(ex - rx, ey - ry, ex + rx, ey - ry * 0.35), fill((214, 206, 190)))  # heavy lid
    c.drawPath(poly_path([(ex - rx, ey + ry * 0.75), (ex, ey + ry * 1.05), (ex + rx, ey + ry * 0.75)], closed=False, smooth=True),
               stroke((230, 140, 140), r * 0.03, 0.9))
    c.restore()
    c.drawLine(ex - rx, ey - ry * 0.35, ex + rx, ey - ry * 0.35, stroke(INK, r * 0.035))
    c.drawPath(white, stroke(INK, 5))
    # brow: the inner end (toward the middle of the face) up
    c.drawPath(poly_path([(ex - rx * 0.9, ey - ry * 2.35), (ex + rx * 0.2, ey - ry * 1.75), (ex + rx * 1.3, ey - ry * 1.45)], closed=False, smooth=True),
               stroke(INK, r * 0.05))
    c.drawPath(poly_path([(ex - rx * 1.0, ey - ry * 2.9), (ex - rx * 0.6, ey - ry * 2.75), (ex - rx * 0.3, ey - ry * 2.85)], closed=False, smooth=True),
               stroke((190, 180, 164), r * 0.018))
    for k in range(1):  # bags
        c.drawPath(poly_path([(ex - rx * 0.8, ey + ry * (1.35 + 0.35 * k)), (ex, ey + ry * (1.55 + 0.35 * k)), (ex + rx * 0.9, ey + ry * (1.3 + 0.35 * k))],
                             closed=False, smooth=True), stroke((196, 184, 168), r * 0.02))


def scene(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((24, 24, 30)))
    # the door ajar on the right: one warm light
    c.drawRect(skia.Rect.MakeXYWH(1640, 0, 90, H), fill((246, 214, 160)))
    glow(ctx, 1690, 560, 900, (255, 210, 150), 0.32)
    c.drawRect(skia.Rect.MakeXYWH(1730, 0, 200, H), fill((40, 34, 32)))
    hx, hy, r = 840, 600, 380
    # shoulders
    c.drawPath(poly_path([(340, H + 40), (420, 1010), (640, 930), (1060, 930), (1280, 1010), (1360, H + 40)], smooth=True), fill(SKIN_SHADE))
    c.drawPath(poly_path([(340, H + 40), (420, 1010), (640, 930), (1060, 930), (1280, 1010), (1360, H + 40)], smooth=True), stroke(LINE, 8))
    # the head, shaded, lit from the right
    head = skia.Path()
    head.addOval(oval(hx, hy, r, r * 1.03))
    c.drawPath(head, blurred(fill((0, 0, 0), 0.5), 30))
    c.drawPath(head, fill(SKIN))
    c.save()
    c.clipPath(head, skia.ClipOp.kIntersect, True)
    sh = skia.GradientShader.MakeRadial((hx + r * 0.45, hy - r * 0.2), r * 1.6, [col((255, 236, 200), 0.18), col((30, 30, 50), 0.45)])
    c.drawRect(oval(hx, hy, r * 1.1, r * 1.1), skia.Paint(Shader=sh))
    c.restore()
    c.drawPath(head, stroke(LINE, 9))
    # the real face, on the right half
    wet_eye(ctx, hx + r * 0.4, hy - r * 0.04, r * 1.3)
    mx, my = hx + r * 0.3, hy + r * 0.52
    c.drawPath(poly_path([(mx - r * 0.2, my + r * 0.06), (mx - r * 0.06, my - r * 0.04), (mx + r * 0.08, my - r * 0.02), (mx + r * 0.2, my + r * 0.08)],
                         closed=False, smooth=True), stroke(INK, r * 0.04))
    for i, (tx, ty) in enumerate(((hx + r * 0.42, hy + r * 0.26), (hx + r * 0.47, hy + r * 0.44))):
        d = r * (0.05 - 0.012 * i)
        drop = poly_path([(tx, ty - d * 1.9), (tx + d, ty), (tx, ty + d), (tx - d, ty)], smooth=True)
        c.drawPath(drop, fill((196, 222, 255), 0.95))
        c.drawPath(drop, stroke((90, 120, 170), 4))
    c.drawPath(poly_path([(hx + r * 0.41, hy + r * 0.2), (hx + r * 0.42, hy + r * 0.3)], closed=False), stroke((196, 222, 255), 8, 0.6))
    # the mask, pulled away from the left half, its strap still round the head
    c.drawPath(poly_path([(hx - r * 0.3, hy - r * 0.62), (hx + r * 0.2, hy - r * 0.95), (hx + r * 0.9, hy - r * 0.5)], closed=False, smooth=True),
               stroke((58, 58, 66), 26))
    SC.mask(ctx, hx - r * 0.5, hy - r * 0.1, r / 64, 1, rot=-16)
    # his hand on the mask's edge, pulling
    c.drawPath(poly_path([(250, H + 60), (300, 860), (380, 700)], closed=False, smooth=True), stroke(LINE, 120))
    c.drawPath(poly_path([(250, H + 60), (300, 860), (380, 700)], closed=False, smooth=True), stroke(SKIN_SHADE, 104))
    c.drawCircle(400, 660, 66, fill(SKIN_SHADE))
    c.drawCircle(400, 660, 66, stroke(LINE, 8))
    for i in range(3):
        fx, fy = 440 + i * 8, 600 + i * 40
        c.drawPath(poly_path([(fx - 20, fy), (fx + 30, fy - 6)], closed=False), stroke(LINE, 46))
        c.drawPath(poly_path([(fx - 20, fy), (fx + 30, fy - 6)], closed=False), stroke(SKIN_SHADE, 32))
    outlined(ctx, "FINE.", W - 70, 250, 250, TEXT, align="right")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "FINE_thumbnail_1280x720.png")
    save(img, 320, 180, HERE / "FINE_thumbnail_320x180.png")
    print("ok")
