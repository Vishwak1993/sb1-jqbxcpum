"""MIRROR. thumbnails, 1280x720. Both big faces.

A: his face close up in his hood, worried, sweat, looking into a mirror on the right where his reflection is a tiny,
   grey, hunched version of him. "MIRROR." over the mirror. The whole film in one picture: he is not that small.
B: his face beside the big man's phone: a perfect physique on the screen and PHOTO 37 / 37. "37 TRIES." The question
   the turn answers: what does it take to look like that for one second?
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
from studio.character import standing  # noqa: E402
import thumbnails_face as TF  # noqa: E402
import scene as SC  # noqa: E402

LG = "LuckiestGuy-Regular.ttf"


def hooded_face(ctx, hx, hy, r, look=(0.9, 0.0), light=(0.8, -0.2), light_rgb=(200, 220, 255)):
    c = ctx.c
    TF.shoulders(ctx, hx, r, rgb=SC.HOODIE)
    hood = poly_path([(hx - r * 1.28, hy + r * 0.9), (hx - r * 1.3, hy - r * 0.3), (hx - r * 0.8, hy - r * 1.22), (hx, hy - r * 1.4),
                      (hx + r * 0.8, hy - r * 1.22), (hx + r * 1.3, hy - r * 0.3), (hx + r * 1.28, hy + r * 0.9)], smooth=True)
    c.drawPath(hood, fill(mix(SC.HOODIE, (0, 0, 0), 0.25)))
    c.drawPath(hood, stroke(LINE, 9))
    TF.head(ctx, hx, hy, r, light=light, light_rgb=light_rgb, shade=(18, 20, 30))
    for side in (-1, 1):
        ex = hx + side * r * 0.3
        TF.eye(ctx, ex, hy - r * 0.02, r, open_=1.1, look=look, red=0.7)
        TF.brow(ctx, ex, hy - r * 0.02, r, side, inner_up=1.2)
    TF.mouth_line(ctx, [(hx - r * 0.16, hy + r * 0.56), (hx, hy + r * 0.5), (hx + r * 0.16, hy + r * 0.56)], r)
    TF.drop(ctx, hx - r * 0.66, hy - r * 0.38, r * 0.07)
    TF.drop(ctx, hx + r * 0.72, hy - r * 0.16, r * 0.055)
    # the hood's front edge over the forehead
    c.drawPath(poly_path([(hx - r * 1.02, hy + r * 0.3), (hx - r * 0.9, hy - r * 0.62), (hx, hy - r * 1.06), (hx + r * 0.9, hy - r * 0.62),
                          (hx + r * 1.02, hy + r * 0.3)], closed=False, smooth=True), stroke(SC.HOODIE, r * 0.14))
    c.drawPath(poly_path([(hx - r * 1.02, hy + r * 0.3), (hx - r * 0.9, hy - r * 0.62), (hx, hy - r * 1.06), (hx + r * 0.9, hy - r * 0.62),
                          (hx + r * 1.02, hy + r * 0.3)], closed=False, smooth=True), stroke(LINE, 5))


def scene_a(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((20, 22, 30)))
    # the mirror and the tiny reflection in it
    mx, my, mw, mh = 1160, 330, 440, 600
    glow(ctx, mx + mw / 2, my + mh / 2, 520, (150, 180, 220), 0.25)
    wrect(ctx, mx - 18, my - 18, mw + 36, mh + 36, "tm", (150, 120, 90), LINE, 8, seg=3)
    g = skia.GradientShader.MakeLinear([(mx, my), (mx + mw, my + mh)], [col((120, 140, 160)), col((70, 84, 100))])
    c.drawRect(skia.Rect.MakeXYWH(mx, my, mw, mh), skia.Paint(Shader=g))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(mx, my, mw, mh))
    c.drawRect(skia.Rect.MakeXYWH(mx, my + mh - 110, mw, 110), fill((60, 64, 74)))
    r = SC.reflection(SC.make_him(0.0), 0.95, 0.8)
    hip, feet = standing(mx + mw / 2 + 40, my + mh - 50, -1, r.scale)
    r.draw(ctx, hip, -1, lean=0.38, feet=feet, expr="hurt", look=(-1, 0.9))
    for i in range(2):
        x = mx + 50 + i * 90
        c.drawLine(x, my + 40, x + 180, my + 260, stroke((255, 255, 255), 18 - 8 * i, 0.08))
    c.restore()
    hooded_face(ctx, 600, 640, 360)
    TF.outlined(ctx, "MIRROR.", mx + mw / 2, 250, 170, align="center")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def scene_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((24, 18, 20)))
    # the big man's phone: the perfect photo, PHOTO 37
    UI_x, UI_y, UI_w, UI_h = 1150, 250, 470, 760
    glow(ctx, UI_x + UI_w / 2, UI_y + UI_h / 2, 600, (255, 170, 120), 0.3)
    rrect(ctx, UI_x, UI_y, UI_w, UI_h, 56, (18, 18, 22), (100, 100, 110), 7)
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(UI_x + 20, UI_y + 20, UI_w - 40, UI_h - 40), 40, 40), skia.ClipOp.kIntersect, True)
    g = skia.GradientShader.MakeLinear([(0, UI_y), (0, UI_y + UI_h)], [col((70, 54, 60)), col((170, 100, 76))])
    c.drawRect(skia.Rect.MakeXYWH(UI_x, UI_y, UI_w, UI_h), skia.Paint(Shader=g))
    glow(ctx, UI_x + UI_w * 0.7, UI_y + 200, 300, (255, 210, 160), 0.45)
    SC.physique(ctx, UI_x + UI_w / 2, UI_y + 450, 0.9, pose=0)
    c.restore()
    rrect(ctx, UI_x + 60, UI_y + UI_h - 150, UI_w - 120, 90, 20, (0, 0, 0), None, a=0.6)
    draw_text(ctx, "PHOTO 37", UI_x + UI_w / 2, UI_y + UI_h - 86, 64, TEXT, face=LG)
    hooded_face(ctx, 560, 660, 340, look=(0.9, -0.1), light=(0.9, 0.0), light_rgb=(255, 190, 150))
    TF.outlined(ctx, "37 TRIES.", W / 2 - 40, 220, 170, align="center")
    finish(ctx, bars=False, grain=0.03, vignette=0.45)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    for fn, tag in ((scene_a, ""), (scene_b, "_B")):
        img = frame_image(fn, 1.0, 30)
        save(img, 1280, 720, HERE / f"MIRROR_thumbnail{tag}_1280x720.png")
        save(img, 320, 180, HERE / f"MIRROR_thumbnail{tag}_320x180.png")
    print("ok")
