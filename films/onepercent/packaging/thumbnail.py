"""1%. thumbnail, 1280x720: a bright frame (ours are all dark), the device as the whole picture.

Left: a giant battery outline, only a red 1% sliver left, and him slumped inside it, exhausted.
Right: "1%." huge in red, and his phone on its charger glowing green at 100%.
Drawn with the film's own character code.
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

INK = (26, 22, 26)
CHARGE = (80, 200, 100)
S = 2.5


def scene(ctx):
    c = ctx.c
    bg = skia.GradientShader.MakeRadial((760, 560), 1300, [col((246, 242, 234)), col((214, 208, 198))], [0.3, 1.0])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=bg))
    # the battery
    bx, by, bw, bh = 90, 250, 1080, 640
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx + 14, by + 22, bw, bh), 70, 70), blurred(fill((0, 0, 0), 0.25), 24))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx, by, bw, bh), 70, 70), fill((236, 232, 224)))
    c.drawRect(skia.Rect.MakeXYWH(bx + bw, by + bh * 0.32, 70, bh * 0.36), fill(INK))
    sliver = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx + 44, by + 44, 90, bh - 88), 30, 30)
    c.drawRRect(sliver, blurred(fill(RED, 0.6), 30))
    c.drawRRect(sliver, fill(RED))
    # him, slumped against the left wall of his own battery, on the red sliver
    him = Character("thumb1p", scale=S)
    floor = by + bh - 44
    hip = (bx + 330, floor - 22 * S)
    feet = {"near": (hip[0] + 255, floor), "far": (hip[0] + 230, floor)}
    J = him.draw(ctx, hip, 1, lean=-0.32, head_tilt=0.35, feet=feet, expr="tired", look=(0.6, 0.9),
                 hands=free_hands(him, hip, 1, -0.32, {"near": (hip[0] + 150, floor - 20), "far": (hip[0] - 60, floor - 10)}))
    hx, hy = J["head"]
    f = J["facing"]
    for side in (-1, 1):  # heavy dark bags under both eyes
        ex = hx + f * 14 * S + 0.6 * 4 * S + side * 13 * S
        ey = hy + 2 * S + 0.9 * 3 * S + 4 * S
        c.drawOval(skia.Rect.MakeLTRB(ex - 26, ey + 2, ex + 26, ey + 24), blurred(fill((110, 90, 120), 0.55), 5))
    for (dx, dy, s) in ((0.6, -0.55, 1.2), (0.85, -0.2, 0.9)):  # sweat
        x, y, d = hx + dx * 120, hy + dy * 120, 14 * s
        drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
        c.drawPath(drop, fill((200, 225, 255)))
        c.drawPath(drop, stroke((90, 120, 170), 4))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx, by, bw, bh), 70, 70), stroke(INK, 30))
    # the word
    draw_text(ctx, "1%.", 1250, 330, 330, (120, 16, 18), 0.5, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "1%.", 1240, 320, 330, RED, align="left", face="LuckiestGuy-Regular.ttf")
    # his phone, fully charged, smug
    px, py = 1570, 690
    wline(ctx, (px, py + 230), (px + 40, H + 40), "cable", INK, 12, seg=3)
    glow(ctx, px, py, 380, CHARGE, 0.35)
    rrect(ctx, px - 130, py - 230, 260, 460, 40, (30, 30, 36), INK, 10)
    rrect(ctx, px - 110, py - 210, 220, 420, 26, (24, 40, 30), None)
    rrect(ctx, px - 70, py - 90, 140, 70, 14, None, CHARGE, 9)
    c.drawRect(skia.Rect.MakeXYWH(px + 70, py - 70, 12, 30), fill(CHARGE))
    rrect(ctx, px - 58, py - 78, 116, 46, 8, CHARGE, None)
    c.drawPath(poly_path([(px + 4, py - 74), (px - 14, py - 54), (px, py - 54), (px - 6, py - 36), (px + 14, py - 58), (px, py - 58)]),
               fill((24, 40, 30)))
    draw_text(ctx, "100%", px, py + 60, 70, CHARGE, face="LuckiestGuy-Regular.ttf")
    finish(ctx, bars=False, grain=0.025, vignette=0.25)


def save(img, w, h, path):
    s = skia.Surface(w, h)
    s.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    s.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "ONE_PERCENT_thumbnail_1280x720.png")
    save(img, 320, 180, HERE / "ONE_PERCENT_thumbnail_320x180.png")
    print("hand misses:", MISSES or "none")
