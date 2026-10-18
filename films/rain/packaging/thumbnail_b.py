"""RAIN. thumbnail B, 1280x720: a new layout, the only bright, sunny thumbnail we have made.

A blue summer sky, a sun, green grass, people in the background enjoying it. In front, big, him: soaked, flat
and fed-up, looking up at the one small black cloud that rains on him and nobody else. "ONLY ME?" in white with
a dark outline, top right. It asks the question the film answers (no: everyone has weather).
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
sys.path.insert(0, str(HERE.parent))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, HEAD_R, standing, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402

INK = (22, 18, 22)
RAINC = (120, 150, 200)


def oval(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


def outlined(ctx, s, x, y, size, rgb, align="left"):
    for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6), (-4, -4), (4, 4), (-4, 4), (4, -4)):
        draw_text(ctx, s, x + dx, y + dy, size, (20, 30, 50), align=align, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, s, x + 6, y + 12, size, (20, 30, 50), 0.5, align=align, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, s, x, y, size, rgb, align=align, face="LuckiestGuy-Regular.ttf")


def face(ctx, hx, hy, r):
    """Fed-up: heavy half-closed lids, eyes rolled up toward the cloud, a flat pressed mouth, wet."""
    c = ctx.c
    for k in (-1, 1):
        ex, ey = hx + k * r * 0.3 + r * 0.05, hy - r * 0.02
        rx, ry = r * 0.17, r * 0.2
        white = skia.Path()
        white.addOval(oval(ex, ey, rx, ry))
        c.drawPath(white, fill((246, 240, 234)))
        c.save()
        c.clipPath(white, skia.ClipOp.kIntersect, True)
        c.drawCircle(ex + rx * 0.1, ey - ry * 0.2, rx * 0.42, fill((70, 60, 58)))
        c.drawCircle(ex + rx * 0.1, ey - ry * 0.2, rx * 0.2, fill(INK))
        c.drawRect(skia.Rect.MakeLTRB(ex - rx, ey - ry, ex + rx, ey - ry * 0.5), fill((222, 216, 200)))  # the heavy lid
        c.restore()
        c.drawLine(ex - rx, ey - ry * 0.5, ex + rx, ey - ry * 0.5, stroke(INK, r * 0.05))
        c.drawPath(white, stroke(INK, 6))
        c.drawLine(ex - rx * 1.1, ey - ry * 1.5 - k * 2, ex + rx * 1.1, ey - ry * 1.45 + k * 2, stroke(INK, r * 0.055))  # flat brows
    c.drawLine(hx - r * 0.12, hy + r * 0.42, hx + r * 0.2, hy + r * 0.4, stroke(INK, r * 0.045))
    for (dx, dy, s) in ((-0.62, -0.1, 1.0), (0.66, 0.05, 0.8), (-0.3, 0.6, 0.7), (0.4, -0.62, 0.9)):  # water on his face
        x, y, d = hx + dx * r, hy + dy * r, r * 0.06 * s
        drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
        c.drawPath(drop, fill((200, 225, 255), 0.95))
        c.drawPath(drop, stroke((90, 120, 170), 3))


def scene(ctx):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, 600)], [col((70, 150, 230)), col((160, 210, 245))])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sky))
    glow(ctx, 1700, 150, 420, (255, 236, 150), 0.6)
    c.drawCircle(1700, 150, 90, fill((255, 226, 110)))
    for i in range(12):
        a = i * math.pi / 6
        c.drawLine(1700 + math.cos(a) * 115, 150 + math.sin(a) * 115, 1700 + math.cos(a) * 160, 150 + math.sin(a) * 160,
                   stroke((255, 226, 110), 10))
    c.drawPath(poly_path([(-50, 700), (600, 640), (1300, 680), (1980, 640), (1980, 1200), (-50, 1200)], smooth=True), fill((110, 180, 90)))
    # people in the background, happy in the sun
    for i, (x, s, f) in enumerate(((900, 1.3, 1), (1060, 1.25, -1), (1200, 1.3, -1))):
        ch = Character(f"bg{i}", skin=(236, 226, 206), scale=s)
        hip, feet = standing(x, 720, f, s)
        J0 = ch.joints(hip, f, 0.02)
        sh = J0["shoulder"]
        hands = {"far": (sh[0] - f * 30, sh[1] - 110)} if i == 2 else ({"near": (sh[0] + f * 50, sh[1] + 40)} if i == 0 else None)
        Jb = ch.draw(ctx, hip, f, lean=0.02, feet=feet, expr="happy", look=(f, -0.2), hands=hands)
        if i == 0:  # an ice cream
            hp = Jb["limbs"]["arm_near"][2]
            c.drawPath(poly_path([(hp[0] - 12, hp[1] - 6), (hp[0] + 12, hp[1] - 6), (hp[0], hp[1] + 26)]), fill((220, 180, 120)))
            c.drawCircle(hp[0], hp[1] - 16, 15, fill((250, 200, 210)))
            c.drawCircle(hp[0], hp[1] - 16, 15, stroke(LINE, 3))
    # him, big, soaked
    s = 4.6
    him = Character("b2him", scale=s)
    hip = (560, 1340)
    J = him.draw(ctx, hip, 1, lean=-0.04, face=False)
    hx, hy = J["head"]
    r = HEAD_R * s
    c.save()
    c.clipPath(skia.Path.Circle(hx, hy, r * 0.985), skia.ClipOp.kIntersect, True)
    sh = skia.GradientShader.MakeRadial((hx - r * 0.3, hy - r * 0.2), r * 1.6, [col((255, 255, 255), 0.0), col((30, 50, 80), 0.35)])
    c.drawRect(oval(hx, hy, r, r), skia.Paint(Shader=sh))
    c.restore()
    face(ctx, hx, hy, r)
    # his cloud, pouring on him only
    cx, cy = hx + 20, hy - r - 120
    for i in range(46):
        rx = cx - 230 + (i * 47) % 460
        ry = cy + 40 + (i * 83) % 760
        c.drawLine(rx, ry, rx - 6, ry + 40, stroke(RAINC, 6, 0.85))
    p = skia.Path()
    for dx, dy, rr in ((-170, 20, 100), (-70, -50, 130), (70, -35, 120), (180, 25, 90), (0, 40, 120)):
        p.addCircle(cx + dx, cy + dy, rr)
    p = skia.Op(p, skia.Path(), skia.PathOp.kUnion_PathOp) or p
    c.drawPath(p, blurred(fill((0, 0, 0), 0.3), 14))
    c.drawPath(p, fill((60, 62, 72)))
    c.drawPath(p, stroke(LINE, 8))
    c.drawPath(poly_path([(cx - 120, cy - 70), (cx - 30, cy - 110)], closed=False, smooth=True), stroke((120, 124, 136), 8))
    outlined(ctx, "ONLY", 1880, 520, 200, TEXT, align="right")
    outlined(ctx, "ME?", 1880, 740, 250, TEXT, align="right")
    finish(ctx, bars=False, grain=0.02, vignette=0.25)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "RAIN_thumbnail_B_1280x720.png")
    save(img, 320, 180, HERE / "RAIN_thumbnail_B_320x180.png")
    print("hand misses:", MISSES or "none")
