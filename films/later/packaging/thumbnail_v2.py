"""LATER. thumbnail v2, 1280x720: a split frame instead of a face close-up.

Left, cold blue: him at his laptop, thumb on decline, the phone facing us: DAD calling.
Right, warm: Dad alone at his kitchen table, two plates set, phone to his ear, waiting.
A diagonal split between them. "LATER." across the top. Drawn with the film's own character code.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, MISSES  # noqa: E402
from studio.extras import free_hands  # noqa: E402
from studio.render import frame_image  # noqa: E402

S = 2.6
SPLIT = [(1000, 0), (860, 1080)]  # the diagonal, top to bottom


def moustache(ctx, hx, hy, f, s):
    fx = hx + f * 14 * s
    p = poly_path([(fx - 15 * s, hy + 13 * s), (fx - 6 * s, hy + 8 * s), (fx, hy + 10 * s), (fx + 6 * s, hy + 8 * s),
                   (fx + 15 * s, hy + 13 * s), (fx + 8 * s, hy + 15 * s), (fx, hy + 13 * s), (fx - 8 * s, hy + 15 * s)], smooth=True)
    ctx.c.drawPath(p, fill((150, 148, 146)))
    ctx.c.drawPath(p, stroke(LINE, 2 * s))


def side(ctx, left=True):
    p = skia.Path()
    if left:
        p.addPoly([(0, 0), SPLIT[0], SPLIT[1], (0, H)], True)
    else:
        p.addPoly([SPLIT[0], (W, 0), (W, H), SPLIT[1]], True)
    return p


def phone_front(ctx, x, y, rot=-6, sc=1.0):
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(sc, sc)
    rrect(ctx, -110, -200, 220, 400, 30, (24, 24, 30), (95, 95, 108), 7)
    screen = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-94, -184, 188, 368), 22, 22)
    c.drawRRect(screen, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, -184), (0, 184)], [col((80, 104, 160)), col((30, 36, 60))])))
    c.drawCircle(0, -100, 40, fill((150, 148, 146)))
    draw_text(ctx, "DAD", 0, 0, 70, TEXT, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "calling...", 0, 42, 28, (200, 205, 220))
    for bx, rgb in ((-50, RED), (50, (70, 190, 110))):
        c.drawCircle(bx, 120, 34, blurred(fill(rgb, 0.6), 10))
        c.drawCircle(bx, 120, 30, fill(rgb))
    th = poly_path([(-96, 240), (-80, 150), (-62, 114), (-42, 112), (-28, 140), (-20, 240)], smooth=True)
    c.drawPath(th, fill(SKIN))
    c.drawPath(th, stroke(LINE, 5))
    c.restore()


def left_half(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((16, 20, 30)))
    glow(ctx, 560, 560, 700, BLUE, 0.28)
    # desk and laptop
    wrect(ctx, 0, 900, 900, 26, "desk", GREY, LINE, 4, seg=3)
    rrect(ctx, 30, 690, 280, 200, 10, (40, 42, 50), LINE, 5)
    c.drawRect(skia.Rect.MakeXYWH(46, 706, 248, 168), fill((110, 140, 190)))
    draw_text(ctx, "URGENT", 66, 760, 34, (20, 24, 40), align="left", face="LuckiestGuy-Regular.ttf")
    for i in range(3):
        c.drawRect(skia.Rect.MakeXYWH(66, 784 + i * 26, 190 - i * 40, 12), fill((60, 70, 100)))
    him = Character("thumbl2", scale=S)
    hip = (420, 1180)
    ph = (780, 800)
    hands = free_hands(him, hip, 1, 0.16, {"near": (ph[0] - 40, ph[1] + 130), "far": (ph[0] - 60, ph[1] + 160)})
    J = him.draw(ctx, hip, 1, lean=0.16, hands=hands, expr="worried", look=(1, 1.0), screen_glow=1.0)
    hx, hy = J["head"]
    glow(ctx, hx + 80, hy + 40, 300, BLUE, 0.3)
    phone_front(ctx, *ph, rot=-4, sc=0.82)


def right_half(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((54, 40, 28)))
    glow(ctx, 1500, 420, 800, GOLD, 0.30)
    P_window = (1560, 140, 280, 260)
    x, y, w, h = P_window
    wrect(ctx, x, y, w, h, "kwin", (170, 140, 90), (110, 90, 60), 6, seg=2)
    wline(ctx, (x + w / 2, y), (x + w / 2, y + h), "kwv", (110, 90, 60), 6)
    wline(ctx, (x, y + h / 2), (x + w, y + h / 2), "kwh", (110, 90, 60), 6)
    # the table with two plates: his and the one nobody sits at
    # the empty chair, behind the plate nobody eats from
    wrect(ctx, 1188, 600, 24, 240, "chair", (90, 70, 54), LINE, 4, seg=2)
    wrect(ctx, 1110, 600, 180, 22, "chairtop", (90, 70, 54), LINE, 4, seg=2)
    wrect(ctx, 920, 840, 1100, 26, "table", (110, 86, 64), LINE, 4, seg=3)
    for i, px in enumerate((1200, 1500)):
        c.drawOval(skia.Rect.MakeXYWH(px - 90, 814, 180, 34), fill((226, 222, 212)))
        c.drawOval(skia.Rect.MakeXYWH(px - 90, 814, 180, 34), stroke(LINE, 4))
    dad = Character("thumbdad", scale=S, extra=moustache)
    hip = (1760, 1150)
    ph = (1560, 900)
    hands = free_hands(dad, hip, -1, 0.2, {"near": (ph[0] + 10, ph[1] + 40), "far": (ph[0] + 30, ph[1] + 50)})
    J = dad.draw(ctx, hip, -1, lean=0.2, hands=hands, expr="sad", look=(-1, 1.0), screen_glow=0.6)
    hp = J["limbs"]["arm_near"][2]
    c.save()
    c.translate(hp[0] - 20, hp[1] + 20)
    c.rotate(12)
    rrect(ctx, -34, -62, 68, 124, 10, (30, 30, 36), LINE, 4)
    c.drawRect(skia.Rect.MakeXYWH(-26, -54, 52, 108), fill((120, 160, 220)))
    draw_text(ctx, "son", 0, -6, 24, (20, 24, 40), face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "calling", 0, 18, 15, (20, 24, 40))
    c.restore()


def scene(ctx):
    c = ctx.c
    for left, fn in ((True, left_half), (False, right_half)):
        c.save()
        c.clipPath(side(ctx, left), skia.ClipOp.kIntersect, True)
        fn(ctx)
        c.restore()
    c.drawLine(*SPLIT[0], *SPLIT[1], stroke((10, 10, 12), 18))
    draw_text(ctx, "LATER.", W / 2 + 6, 236, 230, (10, 10, 12), 0.6, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "LATER.", W / 2, 230, 230, TEXT, face="LuckiestGuy-Regular.ttf")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    s = skia.Surface(w, h)
    s.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    s.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "LATER_thumbnail_v2_1280x720.png")
    save(img, 320, 180, HERE / "LATER_thumbnail_v2_320x180.png")
    print("hand misses:", MISSES or "none")
