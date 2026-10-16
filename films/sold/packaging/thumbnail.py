"""SOLD. thumbnail, 1280x720: a new layout for us, a full-bleed pattern with a stamp across it.

The whole frame is a wall of cardboard boxes, each with a sticker naming a feeling (BORED, LONELY, 2AM...).
In a gap in the wall, his face, lit blue from below by the phone he is holding. Across the right half,
slapped at an angle, a red stamp: SOLD. Drawn with the film's own character and box code.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
sys.path.insert(0, str(HERE.parent))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402
from studio import props as P  # noqa: E402
import scene as SC  # noqa: E402

LABELS = ["BORED", "LONELY", "2AM", "BAD DAY", "SUNDAY", "TIRED", "SALE", "CAN'T SLEEP", "JUST BECAUSE"]
GAP = (300, 140, 560, 940)  # x, y, w, h: the hole in the wall where he is


def scene(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((16, 14, 14)))
    # him, in the gap, lit by the phone
    gx, gy, gw, gh = GAP
    c.drawRect(skia.Rect.MakeXYWH(gx, gy, gw, gh), fill((10, 12, 20)))
    glow(ctx, gx + gw / 2, gy + gh * 0.7, 420, BLUE, 0.35)
    s = 3.0
    him = Character("thumb_him", scale=s)
    hip = (gx + gw / 2 - 20, 880)
    J0 = him.joints(hip, 1, 0.05)
    sh = J0["shoulder"]
    hand = (sh[0] + 76, sh[1] + 126)
    J = him.draw(ctx, hip, 1, lean=0.05, expr="anxious", look=(0.6, 0.9), screen_glow=1.0,
                 hands={"near": hand, "far": (hand[0] - 30, hand[1] + 10)})
    hp = J["limbs"]["arm_near"][2]
    c.save()
    c.translate(hp[0], hp[1])
    c.scale(2.6, 2.6)
    P.phone_held(ctx, 0, 0, on=1.0)
    c.restore()
    hx, hy = J["head"]
    drop = poly_path([(hx - 150, hy - 150), (hx - 126, hy - 96), (hx - 150, hy - 74), (hx - 174, hy - 96)], smooth=True)
    c.drawPath(drop, fill((200, 225, 255)))
    c.drawPath(drop, stroke((90, 120, 170), 5))
    # the wall of boxes, with the gap left open
    bw, bh = 300, 170
    k = 0
    for row in range(-1, 8):
        for col_ in range(-1, 8):
            x = col_ * bw + (row % 2) * bw / 2 - 40
            y = row * bh - 30
            cx, cy = x + bw / 2, y + bh / 2
            if gx - 40 < cx < gx + gw + 40 and gy - 20 < cy < gy + gh + 60:
                continue
            lab = LABELS[k % len(LABELS)]
            k += 1
            SC.box(ctx, cx, y + bh, bw - 12, bh - 10, lab, key=("tb", row, col_))
    # shading so the wall is darker away from the gap
    sh_ = skia.GradientShader.MakeRadial((gx + gw / 2, gy + gh / 2), 1300, [col((0, 0, 0), 0), col((0, 0, 0), 0.6)], [0.25, 1])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh_))
    # the stamp
    c.save()
    c.translate(1420, 560)
    c.rotate(-11)
    tw = text_width("SOLD.", 330, "LuckiestGuy-Regular.ttf")
    rrect(ctx, -tw / 2 - 50, -230, tw + 100, 300, 34, RED, (255, 255, 255), 14)
    c.drawRect(skia.Rect.MakeXYWH(-tw / 2 - 70, 90, tw + 140, 0), fill(RED))
    draw_text(ctx, "SOLD.", 8, 60, 330, (90, 10, 12), 0.6, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "SOLD.", 0, 52, 330, (255, 255, 255), face="LuckiestGuy-Regular.ttf")
    c.restore()
    finish(ctx, bars=False, grain=0.03, vignette=0.35)


def save(img, w, h, path):
    s = skia.Surface(w, h)
    s.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    s.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "SOLD_thumbnail_1280x720.png")
    save(img, 320, 180, HERE / "SOLD_thumbnail_320x180.png")
    print("hand misses:", MISSES or "none")
