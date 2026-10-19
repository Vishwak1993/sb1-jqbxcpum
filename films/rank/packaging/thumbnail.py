"""RANK. thumbnails, 1280x720. Both big faces.

A: his face close up, worried, sweat, bloodshot eyes, under a huge red number pressing down on his head, "AIR 74,000",
   with "RANK." in white, top left. The number is the weight on him.
B: a question thumbnail: his face between his own red 74,000 and his dad's old grey card, "1996: 41,286".
   "YOU ARE NOT YOUR RANK?" would preach; the question is the dad's: "WHAT DID DAD GET?"
"""
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

LG = "LuckiestGuy-Regular.ttf"


def face(ctx, hx, hy, r, look=(0.0, -0.6)):
    TF.shoulders(ctx, hx, r)
    TF.head(ctx, hx, hy, r, light=(0.0, -1.0), light_rgb=(255, 150, 140), shade=(20, 14, 18))
    for side in (-1, 1):
        ex = hx + side * r * 0.3
        TF.eye(ctx, ex, hy - r * 0.02, r, open_=1.1, look=look, red=1.0)
        TF.brow(ctx, ex, hy - r * 0.02, r, side, inner_up=1.1)
    TF.mouth_line(ctx, [(hx - r * 0.16, hy + r * 0.56), (hx, hy + r * 0.5), (hx + r * 0.16, hy + r * 0.56)], r)
    TF.drop(ctx, hx - r * 0.62, hy - r * 0.42, r * 0.07)
    TF.drop(ctx, hx + r * 0.7, hy - r * 0.2, r * 0.055)


def scene_a(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((20, 14, 16)))
    glow(ctx, 1320, 260, 900, RED, 0.3)
    face(ctx, 1320, 730, 330)
    draw_text(ctx, "74,000", 1320 + 8, 340 + 12, 230, (0, 0, 0), 0.5, face=LG)
    draw_text(ctx, "74,000", 1320, 340, 230, RED, face=LG, glow_rgb=RED_D)
    draw_text(ctx, "AIR", 1320, 150, 64, (255, 190, 180), face=LG)
    for i in range(5):  # weight lines pressing down
        x = 1080 + i * 120
        c.drawLine(x, 380, x, 420, stroke(RED, 8, 0.7))
    TF.outlined(ctx, "RANK.", 70, 250, 240)
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def scene_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((18, 18, 24)))
    glow(ctx, 330, 600, 520, RED, 0.3)
    draw_text(ctx, "74,000", 330, 660, 190, RED, face=LG, glow_rgb=RED_D)
    draw_text(ctx, "HIM", 330, 780, 60, (220, 160, 160), face=LG)
    c.save()
    c.translate(1600, 640)
    c.rotate(6)
    rrect(ctx, -240, -170, 480, 320, 10, (230, 220, 196), LINE, 6)
    draw_text(ctx, "1996", 0, -70, 80, (60, 50, 40), face=LG)
    draw_text(ctx, "41,286", 0, 60, 110, (160, 50, 40), face=LG)
    c.restore()
    draw_text(ctx, "DAD", 1600, 880, 60, (220, 210, 190), face=LG)
    face(ctx, 960, 700, 310, look=(0.9, 0.2))
    TF.outlined(ctx, "WHAT DID DAD GET?", W / 2, 220, 150, align="center")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    for fn, tag in ((scene_a, ""), (scene_b, "_B")):
        img = frame_image(fn, 1.0, 30)
        save(img, 1280, 720, HERE / f"RANK_thumbnail{tag}_1280x720.png")
        save(img, 320, 180, HERE / f"RANK_thumbnail{tag}_320x180.png")
    print("ok")
