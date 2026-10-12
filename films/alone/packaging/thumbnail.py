"""1280x720 thumbnail from the film's own code: his face large on the right, lit by the phone; red '0.' on the left."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
import skia
from studio.core import *
from studio.character import Character
from studio.render import frame_image

def scene(ctx):
    c = ctx.c
    glow(ctx, 1240, 470, 760, BLUE, 0.34)
    him = Character("thumb", scale=4.0)
    J = him.draw(ctx, (1420, 1180), -1, lean=0.06, expr="hurt", look=(-1, 0.7), screen_glow=1.0, tear=0.55,
                 hands={"near": (1012, 862), "far": (1050, 900)})
    # the phone, in his hand, screen toward him
    c.save(); c.translate(1000, 760); c.rotate(-12)
    rrect(ctx, -70, -190, 140, 300, 24, (30, 30, 36), (100, 100, 110), 6)
    rrect(ctx, -56, -176, 112, 272, 16, (70, 105, 170))
    c.restore()
    glow(ctx, 1000, 700, 380, BLUE, 0.3)
    draw_text(ctx, "NEW MESSAGES", 320, 300, 60, (190, 190, 200), align="center")
    draw_text(ctx, "0.", 330, 720, 440, RED, face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
    finish(ctx, bars=False, grain=0.03, vignette=0.45)

img = frame_image(scene, 1.0, 30)
big = HERE / "ALONE_thumbnail_1280x720.png"
s = skia.Surface(1280, 720); s.getCanvas().drawImageRect(img, skia.Rect.MakeWH(1280, 720), skia.SamplingOptions(skia.FilterMode.kLinear))
s.makeImageSnapshot().save(str(big))
s2 = skia.Surface(320, 180); s2.getCanvas().drawImageRect(img, skia.Rect.MakeWH(320, 180), skia.SamplingOptions(skia.FilterMode.kLinear))
s2.makeImageSnapshot().save(str(HERE / "thumbnail_phone_size_320x180.png"))
print(big)
