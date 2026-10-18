"""FINE. thumbnail B, 1280x720: a new layout, a costume party where one mask isn't a costume.

A warm Halloween party. Behind, his friends in costumes (a pumpkin head, a ghost sheet, a witch hat, Jo in a vampire
collar) laugh with their masks pushed up. In front, big, him in his smiling mask with its strap, stiff, one bead of
sweat; on the wall behind him his shadow is the villain, with the same red grin. "NO COSTUME?" across the top in white.
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


def outlined(ctx, s, x, y, size, rgb, align="center"):
    for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6), (-4, -4), (4, 4), (-4, 4), (4, -4)):
        draw_text(ctx, s, x + dx, y + dy, size, (24, 14, 10), align=align, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, s, x + 8, y + 14, size, (0, 0, 0), 0.5, align=align, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, s, x, y, size, rgb, align=align, face="LuckiestGuy-Regular.ttf")


def scene(ctx):
    t = 80.6
    with Camera(1.25, 960, 470).apply(ctx):
        SC.party_room(ctx, t)
        P.villain(ctx, 1000, SC.FY, scale=1.5, alpha=0.9, grin=1.4, lean=-0.15)  # his shadow on the wall
        SC.costume_guest(ctx, t, 330, "pumpkin", 0.0, 0)
        SC.costume_guest(ctx, t, 560, "ghost", 0.0, 1)
        SC.costume_guest(ctx, t, 1360, "witch", 0.0, 2)
        Jj0 = SC.JO.joints(SC.standing(1580, SC.FY, -1)[0], -1, 0.02)
        SC.vampire(ctx, Jj0)
        SC.stand(SC.JO, ctx, 1580, f=-1, lean=-0.04, expr="happy", look=(-1, -0.1), mouth_open=0.5)
    # him, big, in front
    s = 3.4
    me = Character("thumbB", scale=s)
    hip = (800, 1150)
    J = me.draw(ctx, hip, 1, lean=0.02, expr="neutral", look=(1, 0.0))
    SC.face_mask(ctx, J, s=s, strap=True)
    hx, hy = J["head"]
    x, y, d = hx - 90, hy - 120, 22
    drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
    ctx.c.drawPath(drop, fill((200, 225, 255)))
    ctx.c.drawPath(drop, stroke((90, 120, 170), 5))
    outlined(ctx, "NO COSTUME?", W / 2, 230, 200, TEXT)
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "FINE_thumbnail_B_1280x720.png")
    save(img, 320, 180, HERE / "FINE_thumbnail_B_320x180.png")
    print("hand misses:", MISSES or "none")
