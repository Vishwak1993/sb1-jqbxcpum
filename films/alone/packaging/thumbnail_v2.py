"""Thumbnail v2, 1280x720, drawn with the film's own character code.

Close-up: his face large on the right (about half the frame), three-quarter view, anxious and wide-eyed,
staring at his phone and lit from below by its blue glow, the only light. Left: the film's NEW MESSAGES
counter, "0." huge in red. No tear, no Sam, no reply.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, HEAD_R  # noqa: E402
from studio.render import frame_image  # noqa: E402

S = 5.6                       # head diameter ~560 px of 1080: about half the frame height
PHONE = (1000, 950)            # grip point, low and in front of his face


def light_from_below(ctx, hx, hy, r):
    """One light source: the phone. Blue on the underside of the face, the top of the head falls into shadow."""
    c = ctx.c
    c.save()
    c.clipPath(skia.Path.Circle(hx, hy, r * 0.985), skia.ClipOp.kIntersect, True)
    shade = skia.GradientShader.MakeLinear([(hx, hy + r), (hx, hy - r)],
                                           [col(BLUE, 0.46), col(BLUE, 0.14), col((0, 0, 0), 0.10), col((0, 0, 0), 0.62)],
                                           [0.0, 0.30, 0.55, 1.0])
    c.drawRect(skia.Rect.MakeLTRB(hx - r, hy - r, hx + r, hy + r), skia.Paint(Shader=shade, AntiAlias=True))
    c.restore()


def phone(ctx):
    c = ctx.c
    c.save()
    c.translate(*PHONE)
    c.rotate(18)  # top tilted toward his face; we see the back and the lit edge
    rrect(ctx, -82, -230, 164, 330, 28, (24, 24, 30), (95, 95, 108), 7)
    c.drawRect(skia.Rect.MakeXYWH(74, -214, 10, 300), fill((150, 195, 255)))  # screen edge facing him
    c.restore()


def scene(ctx):
    c = ctx.c
    him = Character("thumb2", scale=S)
    hip = (1540, 1400)
    J = him.joints(hip, -1, 0.10)
    hx, hy = J["head"]
    r = HEAD_R * 1.04 * S
    # the phone's light: a cone of blue thrown up onto his face from below
    glow(ctx, PHONE[0] + 90, PHONE[1] - 120, 900, BLUE, 0.42)
    him.draw(ctx, hip, -1, lean=0.10, expr="anxious", look=(-1.6, 1.1), screen_glow=1.0,
             hands={"near": (PHONE[0] + 18, PHONE[1] + 72), "far": (PHONE[0] + 64, PHONE[1] + 88)})
    light_from_below(ctx, hx, hy, r)
    phone(ctx)
    glow(ctx, PHONE[0] + 80, PHONE[1] - 60, 260, BLUE, 0.30)
    # the counter, from the film's HUD, pushed huge
    draw_text(ctx, "NEW", 70, 250, 150, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "MESSAGES", 70, 390, 150, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "0.", 40, 960, 620, RED, align="left", face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
    finish(ctx, bars=False, grain=0.03, vignette=0.6)


def save(img, w, h, path):
    s = skia.Surface(w, h)
    s.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    s.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "ALONE_thumbnail_v2_1280x720.png")
    save(img, 320, 180, HERE / "ALONE_thumbnail_v2_320x180.png")
    from studio.character import MISSES
    print("hand misses:", MISSES or "none")
