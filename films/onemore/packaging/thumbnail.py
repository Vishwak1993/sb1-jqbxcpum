"""ONE MORE MATCH. thumbnails, 1280x720. Both big faces (the channel's rule since October 18).

A: his face at 4 AM, lit blue from below by the monitor, bloodshot eyes wide, headset on, sweat; beside him the
   PLAY AGAIN? button and the clock 4:05. "ONE MORE." in white, top right.
B: a number question, like Monk Mode's "1,000 OR 1?": his face split between a glowing DIAMOND badge on one side and
   his empty goal and keeper gloves on the other. "DIAMOND OR FINAL?" across the top.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parent))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.render import frame_image  # noqa: E402
import thumbnails_face as TF  # noqa: E402
import scene as SC  # noqa: E402

LG = "LuckiestGuy-Regular.ttf"


def headset_big(ctx, hx, hy, r):
    c = ctx.c
    c.drawPath(poly_path([(hx - r * 1.02, hy + r * 0.05), (hx - r * 0.85, hy - r * 0.85), (hx, hy - r * 1.18),
                          (hx + r * 0.85, hy - r * 0.85), (hx + r * 1.02, hy + r * 0.05)], closed=False, smooth=True),
               stroke((40, 44, 52), r * 0.12))
    for side in (-1, 1):
        rrect(ctx, hx + side * r * 1.02 - r * 0.16, hy - r * 0.22, r * 0.32, r * 0.5, r * 0.12, (52, 56, 70), LINE, 6)
    c.drawPath(poly_path([(hx - r * 1.0, hy + r * 0.25), (hx - r * 0.7, hy + r * 0.6), (hx - r * 0.35, hy + r * 0.62)],
                         closed=False, smooth=True), stroke((40, 44, 52), r * 0.04))
    c.drawCircle(hx - r * 0.33, hy + r * 0.62, r * 0.05, fill((40, 44, 52)))


def scene_a(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((12, 14, 22)))
    glow(ctx, 760, 1000, 900, SC.SCREEN_GLOW, 0.3)
    hx, hy, r = 740, 600, 360
    TF.shoulders(ctx, hx, r)
    TF.head(ctx, hx, hy, r, light=(0.0, 1.0), light_rgb=(140, 180, 255), shade=(10, 12, 24))
    for side in (-1, 1):
        ex = hx + side * r * 0.3
        TF.eye(ctx, ex, hy - r * 0.04, r, open_=1.2, look=(0.0, 0.2), red=1.0)
        TF.brow(ctx, ex, hy - r * 0.04, r, side, inner_up=0.8)
        for k in range(2):
            c.drawPath(poly_path([(ex - r * 0.14, hy + r * (0.24 + 0.07 * k)), (ex, hy + r * (0.29 + 0.07 * k)),
                                  (ex + r * 0.14, hy + r * (0.24 + 0.07 * k))], closed=False, smooth=True),
                       stroke((110, 110, 150), r * 0.02, 0.8 - 0.3 * k))
    TF.mouth_line(ctx, [(hx - r * 0.14, hy + r * 0.56), (hx, hy + r * 0.53), (hx + r * 0.14, hy + r * 0.57)], r)
    headset_big(ctx, hx, hy, r)
    TF.drop(ctx, hx - r * 0.62, hy - r * 0.5, r * 0.06)
    TF.drop(ctx, hx + r * 0.66, hy - r * 0.42, r * 0.05)
    # the button and the clock
    bx, by, bw, bh = 1260, 480, 520, 130
    glow(ctx, bx + bw / 2, by + bh / 2, 360, (70, 130, 220), 0.45)
    rrect(ctx, bx, by, bw, bh, 26, (70, 130, 220), (200, 220, 255), 6)
    draw_text(ctx, "PLAY AGAIN?", bx + bw / 2, by + 88, 74, TEXT, face=LG)
    c.drawPath(poly_path([(bx + bw - 90, by + 70), (bx + bw - 90, by + 150), (bx + bw - 70, by + 130), (bx + bw - 48, by + 132)]), fill(TEXT))
    c.drawPath(poly_path([(bx + bw - 90, by + 70), (bx + bw - 90, by + 150), (bx + bw - 70, by + 130), (bx + bw - 48, by + 132)]), stroke(LINE, 4))
    rrect(ctx, 1380, 690, 280, 120, 16, (14, 14, 16), (80, 80, 90), 4)
    draw_text(ctx, "4:05", 1520, 785, 96, RED, face=LG, glow_rgb=RED_D)
    TF.outlined(ctx, "ONE MORE.", W - 70, 250, 220, align="right")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def scene_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((16, 16, 22)))
    # left: the diamond badge, cold blue; right: the empty goal at dusk, gloves on the grass
    glow(ctx, 330, 640, 520, (150, 190, 255), 0.4)
    SC.badge(ctx, 330, 640, 3.2, "DIAMOND")
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(1300, 0, W, H))
    sky = skia.GradientShader.MakeLinear([(0, 300), (0, 900)], [col((70, 60, 96)), col((220, 140, 110))])
    c.drawRect(skia.Rect.MakeLTRB(1300, 0, W, 900), skia.Paint(Shader=sky))
    c.drawRect(skia.Rect.MakeLTRB(1300, 900, W, H), fill((70, 120, 80)))
    for i in range(9):
        c.drawLine(1380 + i * 50, 560, 1360 + i * 50, 900, stroke((236, 236, 240), 3, 0.5))
    c.drawLine(1380, 560, 1840, 560, stroke((240, 240, 244), 18))
    c.drawLine(1840, 560, 1840, 900, stroke((240, 240, 244), 18))
    for gx in (1560, 1650):
        c.drawPath(poly_path([(gx - 40, 960), (gx - 48, 900), (gx - 18, 860), (gx + 26, 868), (gx + 44, 912), (gx + 36, 960)], smooth=True), fill(SC.GLOVE))
        c.drawPath(poly_path([(gx - 40, 960), (gx - 48, 900), (gx - 18, 860), (gx + 26, 868), (gx + 44, 912), (gx + 36, 960)], smooth=True), stroke(LINE, 5))
    c.restore()
    hx, hy, r = 960, 620, 340
    TF.shoulders(ctx, hx, r)
    TF.head(ctx, hx, hy, r, light=(-0.9, 0.2), light_rgb=(150, 190, 255))
    for side in (-1, 1):
        ex = hx + side * r * 0.3
        TF.eye(ctx, ex, hy - r * 0.02, r, open_=1.1, look=(side * 0.9, 0.0), red=0.6)
        TF.brow(ctx, ex, hy - r * 0.02, r, side, inner_up=1.0)
    TF.mouth_line(ctx, [(hx - r * 0.16, hy + r * 0.55), (hx, hy + r * 0.5), (hx + r * 0.16, hy + r * 0.55)], r)
    headset_big(ctx, hx, hy, r)
    TF.drop(ctx, hx - r * 0.66, hy - r * 0.45, r * 0.06)
    TF.outlined(ctx, "DIAMOND OR FINAL?", W / 2, 220, 150, align="center")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    for fn, tag in ((scene_a, ""), (scene_b, "_B")):
        img = frame_image(fn, 1.0, 30)
        save(img, 1280, 720, HERE / f"ONE_MORE_MATCH_thumbnail{tag}_1280x720.png")
        save(img, 320, 180, HERE / f"ONE_MORE_MATCH_thumbnail{tag}_320x180.png")
    print("ok")
