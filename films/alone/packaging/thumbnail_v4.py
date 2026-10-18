"""Thumbnail v4, 1280x720: a new layout, the whole frame is the building across the street at night.

Every window is lit warm, with silhouettes together inside: a dinner, a couple, friends laughing. One window
is cold blue: him, alone at a small table, a birthday cake with one candle, staring at his phone. "ALONE." in
white across the dark band at the top. It shows what he believes (everyone else is together), not the turn.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, seated, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402
from studio import props as P  # noqa: E402

WARM = (236, 178, 104)
WALL = (30, 28, 34)
COLS = [(-120, 380), (300, 400), (750, 640), (1440, 400)]  # x, width
ROWS = [(330, 300), (720, 300)]
HIS = (2, 0)  # column 2, top row: his window (wider)


def silhouette(ctx, x, floor, s=1.0, sit=False, lean=0.0, rgb=(60, 40, 30)):
    c = ctx.c
    h = 150 * s if not sit else 110 * s
    if not sit:  # an arm around the next one, or raised with a glass
        side = 1 if lean <= 0 else -1
        c.drawLine(x, floor - h * 0.75, x - side * 70 * s, floor - h * 0.85, stroke(rgb, 16 * s))
    body = poly_path([(x - 30 * s, floor), (x - 34 * s, floor - h * 0.7), (x + lean * 30 - 22 * s, floor - h),
                      (x + lean * 30 + 22 * s, floor - h), (x + 34 * s, floor - h * 0.7), (x + 30 * s, floor)], smooth=True)
    c.drawPath(body, fill(rgb))
    c.drawCircle(x + lean * 40, floor - h - 34 * s, 34 * s, fill(rgb))


def warm_window(ctx, x, y, w, h, people, key):
    c = ctx.c
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill(WARM))
    glow(ctx, x + w / 2, y + h / 2, w, (255, 210, 140), 0.25)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    floor = y + h - 10
    for (dx, s, sit, lean) in people:
        silhouette(ctx, x + dx * w, floor, s, sit, lean)
    if any(p[2] for p in people):  # a table in front of seated people
        c.drawRect(skia.Rect.MakeXYWH(x + w * 0.2, floor - 70, w * 0.6, 14), fill((70, 46, 32)))
    c.restore()
    frame(ctx, x, y, w, h, key)


def frame(ctx, x, y, w, h, key):
    wrect(ctx, x - 10, y - 10, w + 20, h + 20, (key, "f"), None, (70, 66, 74), 12, seg=2)
    ctx.c.drawLine(x + w / 2, y, x + w / 2, y + h, stroke((70, 66, 74), 10))
    ctx.c.drawRect(skia.Rect.MakeXYWH(x - 20, y + h + 10, w + 40, 18), fill((54, 50, 58)))


def his_window(ctx, x, y, w, h):
    c = ctx.c
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill((20, 26, 40)))
    glow(ctx, x + w * 0.55, y + h * 0.6, w * 0.6, BLUE, 0.35)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    c.translate(x, y)
    k = 0.95
    c.translate(-150 * k, 0)
    c.scale(k, k)
    # inside, in the film's own scale: a small table, the cake, him with his phone
    floor_y = h / k - 20
    P.table(ctx, 330, floor_y - 140, 300, floor_y=floor_y, key="t4table")
    P.cake(ctx, 520, floor_y - 140, lit=1.0, key="t4cake")
    him = Character("t4him", scale=1.0)
    P.chair(ctx, 300, floor_y - 90, 1, floor_y=floor_y, key="t4chair")
    hip, feet = seated(300, floor_y - 90, 1, floor_y=floor_y)
    J = him.draw(ctx, hip, 1, lean=0.2, feet=feet, expr="sad", look=(1, 0.9), screen_glow=0.9,
                 hands={"near": (392, floor_y - 150), "far": (378, floor_y - 146)})
    P.phone_held(ctx, *J["limbs"]["arm_near"][2], on=1.0)
    c.restore()
    frame(ctx, x, y, w, h, "his")


def scene(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill(WALL))
    for i in range(14):  # brick courses, faint
        c.drawLine(0, 300 + i * 56, W, 300 + i * 56, stroke((36, 34, 40), 3))
    people = [
        [(0.3, 0.9, True, 0.3), (0.7, 0.9, True, -0.3)],              # dinner for two
        [(0.25, 1.0, False, 0.2), (0.5, 0.95, False, 0.0), (0.78, 1.0, False, -0.2)],  # friends laughing
        None,
        [(0.35, 1.0, False, 0.4), (0.62, 1.0, False, -0.4)],          # a couple
        [(0.3, 0.85, True, 0.2), (0.55, 0.7, True, 0.0), (0.78, 0.9, True, -0.2)],     # a family dinner
        [(0.4, 1.0, False, 0.3), (0.65, 0.95, False, -0.3)],
        [(0.5, 1.0, False, 0.0), (0.25, 0.9, False, 0.3), (0.75, 0.9, False, -0.3)],
        [(0.35, 0.95, True, 0.3), (0.65, 0.95, True, -0.3)],
    ]
    k = 0
    for r, (y, h) in enumerate(ROWS):
        for col_i, (x, w) in enumerate(COLS):
            if (col_i, r) == HIS:
                his_window(ctx, x, y - 70, w, h + 140)
            else:
                warm_window(ctx, x, y, w, h, people[k % len(people)] or people[0], ("w", r, col_i))
            k += 1
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, 300)], [col((8, 8, 12), 0.95), col((8, 8, 12), 0.0)])
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 300), skia.Paint(Shader=sh))
    draw_text(ctx, "ALONE.", 78, 238, 230, (0, 0, 0), 0.6, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "ALONE.", 70, 228, 230, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "ALONE_thumbnail_v4_1280x720.png")
    save(img, 320, 180, HERE / "ALONE_thumbnail_v4_320x180.png")
    print("hand misses:", MISSES or "none")
