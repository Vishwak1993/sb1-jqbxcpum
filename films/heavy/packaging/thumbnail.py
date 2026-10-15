"""HEAVY. thumbnail, 1280x720: a new layout for us, a wide low-angle shot instead of a face close-up.

A steep hill climbing to the right against a dusk sky. Him, small, bent almost double, hauling a giant sack
of glowing red stones with names on them (KAI biggest). At the top, tiny, a friend with nothing on his back.
"HEAVY." huge across the sky. Drawn with the film's own character, stone and sack code.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
sys.path.insert(0, str(HERE.parent))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, standing, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402
import scene as SC  # noqa: E402

SLOPE = 0.34
X0 = 0


def g(x):
    return 1000 - max(0, x - X0) * SLOPE


def scene(ctx):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, 1080)], [col((44, 34, 70)), col((190, 90, 80)), col((250, 170, 110))], [0, 0.6, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sky))
    glow(ctx, 1650, 520, 700, GOLD, 0.35)
    p = poly_path([(-50, 1000), (X0, 1000), (1920, 1000 - (1920 - X0) * SLOPE), (1980, 1200), (-50, 1200)])
    c.drawPath(p, fill((30, 28, 34)))
    c.drawPath(poly_path([(-50, 1000), (X0, 1000), (1920, 1000 - (1920 - X0) * SLOPE)], closed=False), stroke((20, 18, 22), 8))
    # the friend at the top, nothing on his back
    friend = Character("thumb_kai", extra=SC.kai_cap, scale=0.8)
    fx = 1740
    hip, feet = standing(fx, g(fx), -1, 0.8)
    hip = (hip[0], hip[1] + 5)
    feet = {k: (v[0], g(v[0])) for k, v in feet.items()}
    friend.draw(ctx, hip, -1, lean=0.04, feet=feet, expr="happy", look=(-1, 0.4))
    # him, bent double under the sack
    s = 1.9
    him = Character("thumb_him", scale=s)
    x = 760
    hip, feet = standing(x, g(x), 1, s, step=0.25)
    hip = (hip[0], hip[1] + 18)
    feet = {k: (v[0], g(v[0])) for k, v in feet.items()}
    lean = 0.7
    J0 = him.joints(hip, 1, lean)
    labels = [("KAI", 9), ("DAD", 5), ("EX", 4), ("BOSS", 3), ("SUE", 3)]
    sr = SC.sack_r(58) * s
    cx, cy = J0["shoulder"][0] - sr * 0.55, J0["shoulder"][1] - sr * 0.25
    for i, (lab, w) in enumerate(labels):  # the stones heaped out of the top
        rr = (24 + 4.2 * w) * s * 0.75
        ox = cx + [-0.05, -0.55, 0.45, -0.85, 0.75][i] * sr
        oy = cy - sr * 0.78 - [0.2, 0.0, 0.05, -0.15, -0.2][i] * sr
        SC.stone(ctx, ox, oy, rr, lab, key=("thumb", lab))
    body = poly_path([(cx - sr * 0.82, cy - sr * 0.7), (cx - sr * 1.02, cy + sr * 0.2), (cx - sr * 0.7, cy + sr * 0.95),
                      (cx + sr * 0.7, cy + sr * 0.95), (cx + sr * 1.02, cy + sr * 0.2), (cx + sr * 0.82, cy - sr * 0.7)], smooth=True)
    c.drawPath(body, fill(SC.SACK))
    c.drawPath(body, stroke(LINE, 8))
    c.drawLine(cx - sr * 0.85, cy - sr * 0.62, cx + sr * 0.85, cy - sr * 0.62, stroke(mix(SC.SACK, LINE, 0.4), 14))
    glow(ctx, cx, cy - sr * 0.8, sr * 1.4, RED, 0.25)
    J = him.draw(ctx, hip, 1, lean=lean, feet=feet, expr="hurt", look=(1, 0.2),
                 hands={"near": (J0["shoulder"][0] + 60, J0["shoulder"][1] + 70), "far": (J0["shoulder"][0] + 40, J0["shoulder"][1] + 80)})
    hx, hy = J["head"]
    for (dx, dy, k) in ((-0.1, -0.7, 1.2), (0.35, -0.55, 0.9)):  # sweat
        px, py, d = hx + dx * 110 * s / 2.2, hy + dy * 110 * s / 2.2, 13 * k
        drop = poly_path([(px, py - d * 1.9), (px + d, py), (px, py + d), (px - d, py)], smooth=True)
        c.drawPath(drop, fill((200, 225, 255)))
        c.drawPath(drop, stroke((90, 120, 170), 4))
    c.drawPath(poly_path([(J0["shoulder"][0] - 10, J0["shoulder"][1] - 6), (cx + sr * 0.4, cy + sr * 0.3)], closed=False), stroke(mix(SC.SACK, LINE, 0.5), 18))
    draw_text(ctx, "HEAVY.", 1880, 1010, 270, (0, 0, 0), 0.5, align="right", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "HEAVY.", 1870, 1000, 270, TEXT, align="right", face="LuckiestGuy-Regular.ttf")
    finish(ctx, bars=False, grain=0.03, vignette=0.4)


def save(img, w, h, path):
    s = skia.Surface(w, h)
    s.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    s.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "HEAVY_thumbnail_1280x720.png")
    save(img, 320, 180, HERE / "HEAVY_thumbnail_320x180.png")
    print("hand misses:", MISSES or "none")
