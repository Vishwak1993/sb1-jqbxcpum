"""FRAUD. thumbnail, 1280x720: a new layout for us, a frame within the frame.

Over his shoulder into the lobby mirror. In the glass, his reflection, close and worried, and on its chest the
badge glowing red: FRAUD. "FIRST DAY." in white across the top:
the words say one thing, the badge says another. Drawn with the film's own character and badge code.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
sys.path.insert(0, str(HERE.parent))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402
import scene as SC  # noqa: E402

MX, MY, MW, MH = 640, 150, 1100, 1000


def scene(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((36, 38, 44)))
    # the mirror
    wrect(ctx, MX - 24, MY - 24, MW + 48, MH + 48, "mframe", (130, 116, 92), LINE, 6, seg=2)
    c.drawRect(skia.Rect.MakeXYWH(MX, MY, MW, MH), fill((62, 72, 86)))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(MX, MY, MW, MH))
    s = 3.3
    me = Character("thumb_reflection", skin=(214, 210, 198), scale=s)
    hip = (MX + 600, 950)
    J = me.draw(ctx, hip, -1, lean=0.04, expr="anxious", look=(-0.4, 0.2))
    SC.badge(ctx, J, fraud=1.0, s=5.6)
    hx, hy = J["head"]
    for (dx, dy, k) in ((60, -110, 1.3), (110, -60, 0.9)):  # sweat
        px, py, d = hx + dx, hy + dy, 14 * k
        drop = poly_path([(px, py - d * 1.9), (px + d, py), (px, py + d), (px - d, py)], smooth=True)
        c.drawPath(drop, fill((200, 225, 255)))
        c.drawPath(drop, stroke((90, 120, 170), 4))
    glow(ctx, J["shoulder"][0] - 78, J["shoulder"][1] + 280, 520, RED, 0.35)
    c.drawLine(MX + 80, MY + 60, MX + 330, MY + 310, stroke((255, 255, 255), 14, 0.08))
    c.restore()
    # the lobby plant on the left
    wrect(ctx, 200, 900, 180, 180, "pot", (90, 74, 60), LINE, 5, seg=2)
    import math
    for i in range(7):
        a = -math.pi / 2 + (i - 3) * 0.3
        c.drawLine(290, 900, 290 + math.cos(a) * 380, 900 + math.sin(a) * 380, stroke((60, 92, 64), 26))
    draw_text(ctx, "FIRST DAY.", 70 + 8, 220 + 10, 190, (0, 0, 0), 0.6, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "FIRST DAY.", 70, 220, 190, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "FRAUD_thumbnail_1280x720.png")
    save(img, 320, 180, HERE / "FRAUD_thumbnail_320x180.png")
    print("hand misses:", MISSES or "none")
