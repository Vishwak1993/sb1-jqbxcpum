"""Render one frame of every building block so the look can be checked as a picture."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.core import *
from studio.character import Character, standing, seated, MISSES, EXPR
from studio import props as P
from studio.render import save_frame

him = Character("him")

def scene(ctx):
    P.back_wall(ctx)
    P.floor(ctx, 780)
    P.window(ctx, 1500, 180, rain=1.0)
    P.wall_clock(ctx, 1260, 220, 2, 14)
    hip, feet = standing(220, 780)
    him.draw(ctx, hip, 1, feet=feet, expr="neutral")
    hip, feet = standing(420, 780, step=0.3)
    him.draw(ctx, hip, 1, lean=0.08, feet=feet, expr="determined")
    P.table(ctx, 760, 640, 300)
    P.chair(ctx, 680, 690, 1)
    hip, feet = seated(680, 690)
    ph = (800, 610)
    him.draw(ctx, hip, 1, lean=0.25, feet=feet, hands={"near": ph, "far": (790, 625)}, expr="sad", look=(1, 1), screen_glow=0.8)
    P.phone_held(ctx, *ph)
    P.cake(ctx, 990, 640)
    P.villain(ctx, 1300, 780, 0.9)
    for i, e in enumerate(["neutral","sad","happy","tired","worried","shocked","determined","hurt","closed","hopeful"]):
        Character("e%d" % i, scale=0.55).draw(ctx, (120 + i * 175, 960), 1, expr=e)
        draw_text(ctx, e, 130 + i * 175, 1000, 22, (160,160,160))
    P.hud(ctx, 0)
    caption(ctx, "It was his birthday.", 0, 10)
    villain_text(ctx, "nobody remembered.", 0, 10, 1300, 420)
    finish(ctx)

save_frame(scene, 5.0, sys.argv[1] if len(sys.argv) > 1 else "style_sheet.png")
print("misses:", MISSES)
