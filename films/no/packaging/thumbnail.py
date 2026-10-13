"""NO. thumbnail, 1280x720, drawn with the film's own character code.

Close-up: his face large on the right, three-quarter view, wide frightened eyes over a forced smile, sweat.
Both hands hoisted up like a puppet's, red strings tied to his wrists and head, rising into a red glow.
Left: "YES." huge in white, the word he can't stop saying. No villain face, no snapping, no gold.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, HEAD_R, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402

S = 6.2
HIP = (1520, 1580)
INK = (22, 18, 22)
STRING = (226, 48, 48)


def oval(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


def shade_head(ctx, hx, hy, r):
    """One cold light from the front-left, a red rim from the glow above."""
    c = ctx.c
    c.save()
    c.clipPath(skia.Path.Circle(hx, hy, r * 0.985), skia.ClipOp.kIntersect, True)
    lit = skia.GradientShader.MakeRadial((hx - r * 0.45, hy + r * 0.1), r * 1.7,
                                         [col((255, 250, 240), 0.10), col((10, 12, 22), 0.0), col((10, 12, 22), 0.6)],
                                         [0.0, 0.45, 1.0])
    c.drawRect(skia.Rect.MakeLTRB(hx - r, hy - r, hx + r, hy + r), skia.Paint(Shader=lit, AntiAlias=True))
    rim = skia.GradientShader.MakeLinear([(hx, hy - r), (hx, hy - r * 0.3)], [col(RED, 0.40), col(RED, 0.0)])
    c.drawRect(skia.Rect.MakeLTRB(hx - r, hy - r, hx + r, hy + r), skia.Paint(Shader=rim, AntiAlias=True))
    c.restore()


def eye(ctx, ex, ey, rx, ry, look, key):
    c = ctx.c
    c.drawOval(oval(ex, ey + ry * 0.55, rx * 1.15, ry * 0.75), blurred(fill((70, 60, 90), 0.4), rx * 0.18))
    white = skia.Path()
    white.addOval(oval(ex, ey, rx, ry))
    c.drawPath(white, fill((246, 238, 232)))
    c.save()
    c.clipPath(white, skia.ClipOp.kIntersect, True)
    for i in range(7):  # strained, bloodshot
        a = (i / 7) * 2 * math.pi + hrand(key, i) * 0.5
        p0 = (ex + math.cos(a) * rx, ey + math.sin(a) * ry)
        k = 0.5 + hrand(key, i, 1) * 0.2
        p1 = (ex + math.cos(a + 0.25) * rx * k, ey + math.sin(a + 0.25) * ry * k)
        c.drawPath(poly_path([p0, p1], closed=False), stroke((200, 50, 55), 2.4, 0.7))
    px, py = ex + look[0] * rx * 0.25, ey + look[1] * ry * 0.25
    c.drawCircle(px, py, rx * 0.36, fill((70, 60, 58)))
    c.drawCircle(px, py, rx * 0.16, fill(INK))  # tiny, scared pupil
    c.drawCircle(px - rx * 0.12, py - rx * 0.14, rx * 0.08, fill((255, 255, 255)))
    c.restore()
    c.drawPath(white, stroke(INK, 6))


def face(ctx, hx, hy, r):
    c = ctx.c
    fx, fy = hx - r * 0.18, hy + r * 0.02
    rx, ry = r * 0.19, r * 0.22
    for side in (-1, 1):
        ex = fx + side * r * 0.26
        eye(ctx, ex, fy - r * 0.10, rx, ry, (-0.3, 0.1), ("eye", side))
        inner = (ex - side * rx * 0.45, fy - r * 0.47)  # worried brows over a smile: the forced smile
        outer = (ex + side * rx * 1.25, fy - r * 0.30)
        mid = ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 - r * 0.03)
        c.drawPath(poly_path([inner, mid, outer], closed=False, smooth=True), stroke(INK, r * 0.06))
    # a wide, stretched grin with clenched teeth
    w = r * 0.30
    top = [(fx - w, fy + r * 0.26), (fx, fy + r * 0.31), (fx + w, fy + r * 0.24)]
    bot = [(fx + w, fy + r * 0.24), (fx + w * 0.6, fy + r * 0.44), (fx, fy + r * 0.48), (fx - w * 0.6, fy + r * 0.45),
           (fx - w, fy + r * 0.26)]
    mouth = poly_path(top + bot[1:], closed=True, smooth=True)
    c.drawPath(mouth, fill((60, 30, 34)))
    c.save()
    c.clipPath(mouth, skia.ClipOp.kIntersect, True)
    c.drawRect(skia.Rect.MakeLTRB(fx - w, fy + r * 0.24, fx + w, fy + r * 0.38), fill((246, 242, 232)))
    for i in range(1, 6):
        x = fx - w + i * w * 2 / 6
        c.drawLine(x, fy + r * 0.25, x, fy + r * 0.38, stroke((160, 150, 140), 3))
    c.drawLine(fx - w, fy + r * 0.38, fx + w, fy + r * 0.38, stroke((160, 150, 140), 3))
    c.restore()
    c.drawPath(mouth, stroke(INK, 7))
    for side in (-1, 1):  # strained corners
        c.drawPath(poly_path([(fx + side * w * 1.02, fy + r * 0.19), (fx + side * w * 1.12, fy + r * 0.27),
                              (fx + side * w * 1.02, fy + r * 0.33)], closed=False, smooth=True), stroke(INK, 5))
    for (dx, dy, s) in ((0.36, -0.52, 1.1), (0.55, -0.20, 0.85), (-0.60, -0.40, 0.7)):  # sweat
        x, y, d = hx + dx * r, hy + dy * r, r * 0.055 * s
        drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
        c.drawPath(drop, fill((200, 225, 255), 0.95))
        c.drawPath(drop, stroke((90, 120, 170), 3))
        c.drawCircle(x - d * 0.35, y - d * 0.1, d * 0.28, fill((255, 255, 255)))


def string(ctx, p, top):
    mid = ((p[0] + top[0]) / 2 + 8, (p[1] + top[1]) / 2)
    path = poly_path([top, mid, p], closed=False, smooth=True)
    ctx.c.drawPath(path, blurred(stroke(STRING, 34, 0.4), 10))
    ctx.c.drawPath(path, stroke(STRING, 11, 0.95))
    ctx.c.drawCircle(p[0], p[1], 16, fill(STRING))


def scene(ctx):
    glow(ctx, 1450, -120, 900, RED, 0.35)  # the glow above, where the strings go
    him = Character("thumbno", scale=S)
    hands = {"near": (1010, 760), "far": (1960, 780)}  # hoisted up like a puppet's
    J = him.draw(ctx, HIP, -1, lean=0.04, face=False, hands=hands)
    hx, hy = J["head"]
    r = HEAD_R * 1.04 * S
    shade_head(ctx, hx, hy, r)
    face(ctx, hx, hy, r)
    for p, top in ((J["limbs"]["arm_near"][2], (980, -60)), (J["limbs"]["arm_far"][2], (1900, -60)),
                   ((hx + 20, hy - r), (hx + 80, -60)), (J["limbs"]["arm_near"][1], (1180, -60))):
        string(ctx, p, top)
    draw_text(ctx, "YES.", 80, 640, 330, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
    finish(ctx, bars=False, grain=0.035, vignette=0.6)


def save(img, w, h, path):
    s = skia.Surface(w, h)
    s.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    s.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "NO_thumbnail_1280x720.png")
    save(img, 320, 180, HERE / "NO_thumbnail_320x180.png")
    print("hand misses:", MISSES or "none")
