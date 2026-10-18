"""RAIN. thumbnail, 1280x720: a new layout for us, an absurd picture that needs no words to read.

A warm dinner table indoors. He talks, mouth wide, grey puffs rising from him into a storm cloud under the ceiling
that pours on the whole table. Across from him his friends hold open umbrellas over their plates; Nia looks down.
"RAIN." in white on the dark wall, top right. Drawn with the film's own character, cloud and umbrella code.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
sys.path.insert(0, str(HERE.parent))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402
import scene as SC  # noqa: E402


def scene(ctx):
    with Camera(1.55, 960, 520).apply(ctx):
        SC.dining(ctx, warm=0.9)
        Js = SC.dinner_cast(ctx, 41.0, umbrellas=1.0, nia_down=True)
        J = SC.sit(SC.HIM, ctx, 620, f=1, lean=0.16, expr="determined", look=(1, -0.2), mouth_open=0.9,
                   hands={"near": (720, 560), "far": (724, 632)})
        hx, hy = J["head"]
        for i in range(6):
            k = i / 6
            ctx.c.drawCircle(hx + 50 + (i % 2) * 16, lerp(hy - 10, hy - 170, k), 9 + 12 * k, fill(SC.CLOUD, 0.85))
        SC.cloud(ctx, 1000, 300, 1.0, "thumb", 780)
    draw_text(ctx, "RAIN.", W - 70 + 8, 250 + 10, 250, (0, 0, 0), 0.6, align="right", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "RAIN.", W - 70, 250, 250, TEXT, align="right", face="LuckiestGuy-Regular.ttf")
    finish(ctx, bars=False, grain=0.03, vignette=0.4)


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 41.0, 30)
    save(img, 1280, 720, HERE / "RAIN_thumbnail_1280x720.png")
    save(img, 320, 180, HERE / "RAIN_thumbnail_320x180.png")
    print("hand misses:", MISSES or "none")
