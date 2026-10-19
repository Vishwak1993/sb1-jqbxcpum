"""RANK.: picture. scene(ctx) draws any frame of the film.

The device: his mock-test All India Rank, top-left, and the same number floating over his head in red, where his
family can see it. It grows with every test (the number weighs more the more he studies), until in the exam hall it
fills the frame and the words on the paper swim. The turn: his dad shows him his own old rank card; a faint grey number
shows over Dad's head and fades, and his own shrinks to nothing. The HUD ends on the real result, in gold, which is
not the topper's rank and is enough.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, standing, seated, walk_x  # noqa: E402
from studio import props as P  # noqa: E402
from studio.extras import speech as _speech, talk as _talk, free_hands, door  # noqa: E402
from timeline import (SCENES, CAPS, CUES, BUBBLES, EVENTS, DURATION, scene_at, air_at, air_changed, weight,  # noqa: E402
                      RELABEL, FINAL_AIR, G1_T0, G1_TEST, G1_LABELS, G1_CLOCKS)
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
LG = "LuckiestGuy-Regular.ttf"
LAMP = (255, 220, 160)
KITE = (226, 120, 60)


def dad_face(ctx, hx, hy, f, s):
    fx = hx + f * 14 * s
    for side in (-1, 1):
        ctx.c.drawCircle(fx + side * 13 * s, hy - 2 * s, 9 * s, stroke(LINE, 2.5 * s))
    ctx.c.drawLine(fx - 4 * s, hy - 2 * s, fx + 4 * s, hy - 2 * s, stroke(LINE, 2.5 * s))
    ctx.c.drawPath(poly_path([(fx - 12 * s, hy + 12 * s), (fx, hy + 9 * s), (fx + 12 * s, hy + 12 * s)], closed=False, smooth=True),
                   stroke((70, 60, 56), 5 * s))
    ctx.c.drawPath(poly_path([(hx - 44 * s, hy - 26 * s), (hx, hy - 50 * s), (hx + 44 * s, hy - 26 * s)], closed=False, smooth=True),
                   stroke((150, 150, 156), 5 * s))


def mum_hair(ctx, hx, hy, f, s):
    p = poly_path([(hx - 50 * s, hy - 4 * s), (hx - 46 * s, hy - 32 * s), (hx, hy - 52 * s), (hx + 46 * s, hy - 32 * s),
                   (hx + 50 * s, hy - 4 * s), (hx + 30 * s, hy - 28 * s), (hx, hy - 34 * s), (hx - 30 * s, hy - 28 * s)], smooth=True)
    ctx.c.drawPath(p, fill((54, 40, 36)))
    ctx.c.drawCircle(hx - f * 44 * s, hy - 8 * s, 14 * s, fill((54, 40, 36)))
    ctx.c.drawCircle(hx + f * 14 * s, hy - 22 * s, 2.6 * s, fill((180, 60, 60)))


def pigtails(ctx, hx, hy, f, s):
    for side in (-1, 1):
        ctx.c.drawCircle(hx + side * 46 * s, hy - 26 * s, 16 * s, fill((54, 40, 36)))
        ctx.c.drawCircle(hx + side * 40 * s, hy - 34 * s, 6 * s, fill((220, 90, 110)))
    ctx.c.drawPath(poly_path([(hx - 44 * s, hy - 20 * s), (hx, hy - 50 * s), (hx + 44 * s, hy - 20 * s)], closed=False, smooth=True),
                   stroke((54, 40, 36), 12 * s))


def uncle_face(ctx, hx, hy, f, s):
    fx = hx + f * 14 * s
    ctx.c.drawPath(poly_path([(fx - 14 * s, hy + 12 * s), (fx, hy + 8 * s), (fx + 14 * s, hy + 12 * s)], closed=False, smooth=True),
                   stroke((60, 56, 56), 6 * s))


HIM = Character("him")
DAD = Character("dad", skin=(200, 170, 140), extra=dad_face)
MUM = Character("mum", skin=(206, 170, 140), extra=mum_hair)
PIHU = Character("pihu", skin=(214, 180, 150), scale=0.72, extra=pigtails)
UNCLE = Character("uncle", skin=(150, 150, 156), extra=uncle_face)


def grey(name, scale=1.0):
    return Character(name, skin=(150, 150, 156), scale=scale)


# ---- shared helpers -------------------------------------------------------------------------
def cap(ctx, k, y=190, size=50, rgb=TEXT, glow_rgb=None):
    t0, t1 = CAPS[k]
    caption(ctx, CAPTIONS[k], t0, t1, y=y, size=size, rgb=rgb, glow_rgb=glow_rgb)


def vline(ctx, k, x, y, size=50):
    t0 = CUES[k]
    villain_text(ctx, VILLAIN[k], t0 - 0.05, t0 + LEN.get(k, 1.4) + 0.5, x, y, size)


def label(ctx, s, a=1.0):
    draw_text(ctx, s, 60, LETTERBOX + 170, 38, (190, 190, 196), a, align="left")


def speech(ctx, t, who, x, y, **kw):
    _speech(ctx, t, BUBBLES, who, x, y, **kw)


def talk(who, t):
    return _talk(BUBBLES, who, t)


def fmt(v):
    return f"{v:,}" if v is not None else "--"


def hud(ctx, t, a=1.0):
    """MOCK TEST AIR, top-left; in the park the same box shows the real result in gold."""
    a *= prog(t, 0.6, 1.0)
    if a <= 0:
        return
    x, y = 56, LETTERBOX + 26
    rrect(ctx, x, y, 300, 92, 14, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
    if t >= RELABEL:
        k = prog(t, RELABEL, RELABEL + 0.5)
        draw_text(ctx, "JEE MAIN AIR", x + 20, y + 32, 22, (200, 180, 140), a, align="left")
        sz = 52 * (1 + 0.35 * math.sin(math.pi * k))
        draw_text(ctx, fmt(FINAL_AIR), x + 22, y + 80, sz, GOLD, a * k, align="left", face=LG, glow_rgb=GOLD)
        return
    lc = air_changed(t)
    pop = prog(t, lc, lc + 0.35) if lc is not None and lc <= t <= lc + 0.35 else 0.0
    sz = 52 * (1 + 0.35 * math.sin(math.pi * pop) if pop > 0 else 1)
    v = air_at(t)
    draw_text(ctx, "MOCK TEST AIR", x + 20, y + 32, 22, (160, 160, 168), a, align="left")
    draw_text(ctx, fmt(v), x + 22, y + 80, sz, RED if v and v > 50000 else TEXT, a, align="left", face=LG,
              glow_rgb=RED_D if v and v > 50000 else None)


def number_over(ctx, J, value, k, rgb=RED, a=1.0, dy=0.0, dx=0.0):
    """The rank floating over a head, k: 0..1 how big (how heavy) it is."""
    if a <= 0.01 or value is None or k <= 0.01:
        return
    hx, hy = J["head"]
    hx += dx
    size = 30 + 150 * k
    y = hy - 70 - 30 * k - size * 0.15 + dy + math.sin(ctx.t * 2.2) * 3
    glow(ctx, hx, y - size * 0.3, size * 1.4, rgb, 0.25 * a)
    draw_text(ctx, fmt(value), hx, y, size, rgb, a, face=LG, glow_rgb=RED_D if rgb == RED else None)


def stand(ch, ctx, x, f=1, lean=0.04, step=0.0, **kw):
    hip, feet = standing(x, FY, f, ch.scale, step=step)
    if kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def sit(ch, ctx, x, f=1, lean=0.1, seat_y=690, chair=True, **kw):
    if chair:
        P.chair(ctx, x, seat_y, f, key=("ch", ch.name, x))
    hip, feet = seated(x, seat_y, f, ch.scale)
    if kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def kite(ctx, x, y, s=1.0, rgb=KITE, rot=0.0, tail=True):
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    p = poly_path([(0, -60 * s), (42 * s, 0), (0, 70 * s), (-42 * s, 0)])
    c.drawPath(p, fill(rgb))
    c.drawPath(p, stroke(LINE, 3 * s))
    c.drawLine(0, -60 * s, 0, 70 * s, stroke(LINE, 2 * s))
    c.drawLine(-42 * s, 0, 42 * s, 0, stroke(LINE, 2 * s))
    if tail:
        pts = [(0, 70 * s + i * 22 * s) for i in range(6)]
        pts = [(px + math.sin(ctx.t * 4 + i) * 10 * s, py) for i, (px, py) in enumerate(pts)]
        c.drawPath(poly_path(pts, closed=False, smooth=True), stroke(LINE, 2 * s))
        for i in (2, 4):
            c.drawPath(poly_path([(pts[i][0] - 8 * s, pts[i][1]), (pts[i][0] + 8 * s, pts[i][1] + 4 * s)], closed=False), stroke(rgb, 5 * s))
    c.restore()


# ---- his room ---------------------------------------------------------------------------------------
SEAT = (820, 690)
LAPTOP = (1000, 640)


def room(ctx, t, lamp=1.0, dawn=0.0, curtain=0.0, result=None, clock=None, lane=False):
    c = ctx.c
    P.back_wall(ctx, rgb=mix((22, 22, 28), (50, 48, 54), dawn))
    P.floor(ctx, FY)
    # the window (the lane outside), with a curtain that can be pulled
    wx, wy, ww, wh = 1340, 220, 300, 260
    sky = mix(mix((24, 28, 42), (150, 190, 230), 1.0 if lane else 0.0), (236, 214, 170), dawn)
    c.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), fill(sky))
    if lane:
        c.drawRect(skia.Rect.MakeXYWH(wx, wy + wh - 60, ww, 60), fill((120, 110, 100)))
        lt = t - 49.0
        kite(ctx, wx + 160 + 30 * math.sin(lt * 1.1), wy + 70 + 10 * math.sin(lt * 1.7), 0.55, rot=8 * math.sin(lt))
        c.drawLine(wx + 150, wy + wh - 40, wx + 160 + 30 * math.sin(lt * 1.1), wy + 100, stroke((240, 240, 240), 1.5))
        for i, (px, ch) in enumerate(((wx + 120, 0.5), (wx + 190, 0.8))):
            c.drawCircle(px, wy + wh - 80 * ch - 20, 16 * ch + 6, fill((90, 76, 70)))
            c.drawRect(skia.Rect.MakeXYWH(px - 8 * ch - 4, wy + wh - 80 * ch, 16 * ch + 8, 60 * ch), fill((90, 76, 70)))
    wrect(ctx, wx - 8, wy - 8, ww + 16, wh + 16, "win", None, (90, 90, 100), 8, seg=2)
    cw = lerp(40, ww / 2 + 10, curtain)
    for side in (0, 1):
        x0 = wx - 30 if side == 0 else wx + ww + 30 - cw
        c.drawRect(skia.Rect.MakeXYWH(x0, wy - 30, cw, wh + 60), fill((90, 64, 70)))
        c.drawRect(skia.Rect.MakeXYWH(x0, wy - 30, cw, wh + 60), stroke(LINE, 3))
    # the wall of sticky notes and the timetable
    for i in range(18):
        sx = 360 + (i % 6) * 64 + hrand("sn", i) * 10
        sy = 230 + (i // 6) * 70 + hrand("sny", i) * 10
        c.drawRect(skia.Rect.MakeXYWH(sx, sy, 46, 46), fill(mix((236, 224, 150), (230, 170, 170), hrand("snc", i) > 0.7)))
        for k in range(3):
            c.drawLine(sx + 6, sy + 12 + k * 10, sx + 38 - hrand("snl", i, k) * 14, sy + 12 + k * 10, stroke((90, 80, 70), 2))
    rrect(ctx, 760, 220, 170, 200, 8, (226, 226, 220), LINE, 3)
    draw_text(ctx, "TIMETABLE", 845, 254, 22, (40, 40, 46), face=LG)
    for i, s in enumerate(["5:00 WAKE", "6-12 PHY", "1-6 CHEM", "7-2 MATHS"]):
        draw_text(ctx, s, 845, 292 + i * 32, 20, (60, 60, 66))
    # the shelf with the kite he made her
    wrect(ctx, 220, 420, 160, 12, "shelf", (92, 74, 60), LINE, 3, seg=2)
    kite(ctx, 300, 370, 0.5, rot=-10, tail=False)
    # desk, books, lamp, laptop
    P.table(ctx, 880, 640, 520, key="desk")
    for i in range(5):
        wrect(ctx, 1180 + (i % 2) * 6, 640 - 22 * (i + 1), 150, 22, ("book", i), mix((90, 110, 150), (150, 90, 80), i / 4), LINE, 2, seg=2)
    lx, ly = 1300, 520
    if lamp > 0:
        glow(ctx, lx - 40, ly + 30, 420, LAMP, 0.3 * lamp)
        cone(ctx, (lx - 40, ly + 20), (900, 640), (1260, 640), LAMP, 0.10 * lamp)
    c.drawLine(lx, 640, lx - 10, ly + 10, stroke((60, 60, 66), 6))
    c.drawPath(poly_path([(lx - 80, ly + 30), (lx - 40, ly - 10), (lx + 10, ly + 6)]), fill((70, 70, 78)))
    c.drawPath(poly_path([(lx - 80, ly + 30), (lx - 40, ly - 10), (lx + 10, ly + 6)]), stroke(LINE, 3))
    # the laptop
    x0, y0 = LAPTOP
    c.drawPath(poly_path([(x0, y0), (x0 + 30, y0 - 150), (x0 + 220, y0 - 150), (x0 + 200, y0)]), fill((40, 40, 46)))
    c.drawPath(poly_path([(x0 + 8, y0 - 8), (x0 + 34, y0 - 142), (x0 + 212, y0 - 142), (x0 + 192, y0 - 8)]),
               fill((40, 52, 76) if result else (24, 26, 32)))
    if result:
        glow(ctx, x0 + 110, y0 - 76, 220, BLUE, 0.25)
        draw_text(ctx, result[0], x0 + 114, y0 - 104, 18, (190, 200, 220), face=LG)
        draw_text(ctx, result[1], x0 + 112, y0 - 56, 34, RED if result[2] else TEXT, face=LG)
    rrect(ctx, x0 - 20, y0 - 6, 240, 10, 4, (60, 60, 66), LINE, 2)
    if clock:
        rrect(ctx, 600, 560, 110, 46, 6, (14, 14, 16), (70, 70, 76), 2)
        draw_text(ctx, clock, 655, 596, 30, (200, 210, 220), face=LG)


def at_desk(ctx, t, expr="tired", look=(1, 0.6), lean=0.22, writing=True, glow_on=0.8, **kw):
    sx, sy = SEAT
    P.chair(ctx, sx, sy, 1, key="dchair")
    hip, feet = seated(sx, sy, 1)
    wv = 6 * math.sin(t * 9) if writing else 0.0
    hands = {"near": (980 + wv, 630), "far": (940, 634)}
    return HIM.draw(ctx, hip, 1, lean=lean, feet=feet, expr=expr, look=look, screen_glow=glow_on,
                    hands=free_hands(HIM, hip, 1, lean, hands), mouth_open=talk("him", t), **kw)


# ---- the hook ---------------------------------------------------------------------------------------
def s01(ctx, t):
    up = ease(prog(t, EVENTS["result"], EVENTS["result"] + 1.0))
    with Camera(lerp(1.9, 1.7, ease(prog(t, 0, 6))), 1050, 480).apply(ctx):
        room(ctx, t, result=("MOCK TEST 14", "AIR 48,210", False) if t > EVENTS["result"] - 0.4 else None, clock="2:14")
        J = at_desk(ctx, t, expr="tired" if t < EVENTS["result"] else "worried", look=(1, 0.3), writing=t < 2.4)
        number_over(ctx, J, 48210, 0.35 * up, a=up, dy=40 * (1 - up))
    cap(ctx, "C1", y=985)
    hud(ctx, t)


def dining(ctx):
    P.back_wall(ctx, rgb=(46, 40, 38))
    P.floor(ctx, FY)
    ctx.c.drawLine(960, 0, 960, 230, stroke(LINE, 3))
    ctx.c.drawPath(poly_path([(900, 230), (1020, 230), (990, 260), (930, 260)]), fill((170, 150, 110)))
    glow(ctx, 960, 270, 360, (255, 220, 160), 0.25)
    P.table(ctx, 620, 640, 680, key="dtable")
    for x in (720, 900, 1080, 1220):
        ctx.c.drawOval(skia.Rect.MakeXYWH(x - 34, 630, 68, 12), fill((226, 222, 210)))


def h1(ctx, t):
    with Camera(1.4, 960, 480).apply(ctx):
        dining(ctx)
        Jd = sit(DAD, ctx, 1180, f=-1, lean=0.08, expr="neutral", look=(-1, 0.0), mouth_open=talk("dad", t),
                 hands={"near": (1100, 628), "far": (1110, 632)})
        Jm = sit(MUM, ctx, 1360, f=-1, lean=0.08, expr="worried", look=(-1, 0.0), mouth_open=talk("mum", t),
                 hands={"near": (1280, 628), "far": (1290, 632)})
        J = sit(HIM, ctx, 640, f=1, lean=0.24, expr="hurt", look=(1, 0.9), hands={"near": (740, 628), "far": (724, 632)})
        number_over(ctx, J, 48210, 0.42)
        speech(ctx, t, "dad", Jd["head"][0] - 10, Jd["head"][1] - 76)
        speech(ctx, t, "mum", Jm["head"][0] - 30, Jm["head"][1] - 76)
    cap(ctx, "C2", y=985)
    hud(ctx, t)


# ---- the wound and the stakes ------------------------------------------------------------------------
def s02(ctx, t):
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0, t1))
    with Camera(lerp(1.9, 1.6, ease(prog(t, t0 - 0.4, t1))), lerp(1080, 1120, ease(prog(t, t0 - 0.4, t1))), 480).apply(ctx):
        glow(ctx, 1260, 540, 300, RED, 0.25 * born)
        room(ctx, t, result=("MOCK TEST 14", "AIR 48,210", False), clock="2:20")
        if born > 0:
            P.villain(ctx, 1480, FY, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 15.6, 16.2)), lean=-0.3)
        J = at_desk(ctx, t, expr="tired" if t < 16 else "hurt", look=(1, 0.6))
        number_over(ctx, J, 48210, 0.42)
    vline(ctx, "V1", 1240, 200, 58)
    vline(ctx, "V2", 1240, 280, 52)
    hud(ctx, t)


def b1(ctx, t):
    with Camera(1.5, 760, 480).apply(ctx):
        room(ctx, t, clock="7:40")
        door(ctx, 120, open_k=1.0, key="rdoor", light=0.7)
        Jp = stand(PIHU, ctx, 230, f=1, lean=0.02, expr="hopeful", look=(1, -0.2), mouth_open=talk("pihu", t),
                   hands={"far": (250, 560)})
        kite(ctx, Jp["limbs"]["arm_far"][2][0] + 6, Jp["limbs"]["arm_far"][2][1] - 70, 0.55, rot=-8)
        J = at_desk(ctx, t, expr="tired", look=(1, 0.6))
        number_over(ctx, J, 48210, 0.42)
        speech(ctx, t, "pihu", Jp["head"][0] + 160, Jp["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 40, J["head"][1] - 160)
    hud(ctx, t)


# ---- the grind --------------------------------------------------------------------------------------
def g1(ctx, t):
    i = min(3, int((t - G1_T0) // G1_TEST))
    n0 = G1_T0 + i * G1_TEST
    res_t = EVENTS["g1_results"][i]
    shown = t >= res_t
    v = air_at(t)
    with Camera(1.65, 1060, 480).apply(ctx):
        room(ctx, t, clock=G1_CLOCKS[i], result=(G1_LABELS[i], "AIR " + fmt(v), v > 50000) if shown else None)
        if i >= 1:
            P.villain(ctx, 1500, FY, scale=0.9 + 0.08 * i, alpha=0.5 + 0.15 * i, grin=1.0, lean=-0.3)
        J = at_desk(ctx, t, expr="determined" if not shown else "hurt", look=(1, 0.6) if not shown else (1, 0.2),
                    lean=0.22 + 0.03 * i, writing=not shown)
        number_over(ctx, J, v, weight(t))
    black(ctx, 1 - prog(t, n0, n0 + 0.1))
    label(ctx, G1_LABELS[i])
    vline(ctx, "V3", 1560, 470, 56)
    vline(ctx, "V4", 1560, 470, 54)
    vline(ctx, "V5", 1560, 470, 54)
    hud(ctx, t)


def g2(ctx, t):
    pull = ease(prog(t, EVENTS["curtain"], EVENTS["curtain"] + 0.8))
    with Camera(1.6, 1300, 460).apply(ctx):
        room(ctx, t, clock="5:10", lane=True, curtain=pull)
        hip, feet = standing(1250, FY, 1)
        J0 = HIM.joints(hip, 1, 0.04)
        sh = J0["shoulder"]
        reach = math.sin(math.pi * prog(t, EVENTS["curtain"] - 0.4, EVENTS["curtain"] + 1.0))
        hands = {"far": (sh[0] + 60 * reach + 10, sh[1] - 40 * reach + 60)} if reach > 0 else None
        J = stand(HIM, ctx, 1250, f=1, lean=0.04, expr="sad", look=(1, -0.2) if t < EVENTS["curtain"] else (-1, 0.8), hands=hands)
        number_over(ctx, J, air_at(t), 0.42)
    cap(ctx, "C3", y=985)
    hud(ctx, t)


def g3(ctx, t):
    c = ctx.c
    with Camera(1.6, 960, 470).apply(ctx):
        P.back_wall(ctx, rgb=(60, 66, 72))
        P.floor(ctx, FY)
        for i in range(10):
            c.drawLine(0, 160 + i * 64, W, 160 + i * 64, stroke((70, 76, 82), 2))
        wrect(ctx, 760, 600, 380, 60, "sink", (220, 222, 226), LINE, 3, seg=2)
        mx, my, mw, mh = 820, 220, 260, 330
        wrect(ctx, mx - 10, my - 10, mw + 20, mh + 20, "mframe", (160, 150, 130), LINE, 4, seg=2)
        c.drawRect(skia.Rect.MakeXYWH(mx, my, mw, mh), fill((150, 170, 186)))
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(mx, my, mw, mh))
        refl = Character("refl", scale=1.0)
        hip_r, feet_r = standing(mx + mw / 2, my + mh + 160, -1)
        Jr = refl.draw(ctx, hip_r, -1, lean=0.02, feet=feet_r, face=False)
        hx, hy = Jr["head"]
        c.drawCircle(hx, hy, 52, fill((236, 230, 214)))
        c.drawCircle(hx, hy, 52, stroke(LINE, 3))
        k = ease(prog(t, 57.0, 58.0))
        draw_text(ctx, fmt(air_at(t)), hx, hy + 16, 46, RED, k, face=LG, glow_rgb=RED_D)
        c.drawLine(mx + 30, my + 40, mx + 120, my + 130, stroke((255, 255, 255), 10, 0.1))
        c.restore()
        J = stand(HIM, ctx, 640, f=1, lean=0.04, expr="hurt", look=(1, -0.1))
    cap(ctx, "C4", y=985)
    hud(ctx, t)


# ---- rock bottom: the exam hall ----------------------------------------------------------------------
def exam_hall(ctx, t, morning=0.0, tick=True):
    c = ctx.c
    P.back_wall(ctx, rgb=mix((40, 42, 48), (70, 66, 60), morning))
    P.floor(ctx, FY)
    for i, wx in enumerate((300, 1500)):
        P.window(ctx, wx, 200, 200, 220, ("hw", i), night=False, moon=False, sky=mix((130, 150, 170), (240, 216, 170), morning))
    if morning > 0:
        glow(ctx, 1600, 310, 400, (255, 226, 170), 0.25 * morning)
    # the clock
    cx, cy = 960, 230
    c.drawCircle(cx, cy, 60, fill((236, 234, 226)))
    c.drawCircle(cx, cy, 60, stroke(LINE, 5))
    sec = (t * (6 if tick else 0)) * math.pi / 180 * 6
    c.drawLine(cx, cy, cx + math.sin(sec) * 48, cy - math.cos(sec) * 48, stroke(RED, 3))
    c.drawLine(cx, cy, cx + 20, cy - 26, stroke(LINE, 5))
    c.drawLine(cx, cy, cx - 6, cy - 40, stroke(LINE, 4))


def exam_desk(ctx, x, key):
    P.table(ctx, x, 640, 220, key=key)


def r1(ctx, t):
    panic = ease(prog(t, 66.0, 74.0))
    times = t >= EVENTS["times_up"]
    with Camera(lerp(1.5, 2.0, panic), lerp(900, 860, panic), lerp(500, 470, panic), shake=1.5 * panic * (not times)).apply(ctx):
        exam_hall(ctx, t)
        for i, x in enumerate((340, 1300)):
            exam_desk(ctx, x, ("ed", i))
            sit(grey(f"st{i}"), ctx, x - 40, f=1, lean=0.2, expr="neutral", look=(1, 0.9),
                hands={"near": (x + 90 + 4 * math.sin(t * 8 + i), 630), "far": (x + 60, 634)})
        exam_desk(ctx, 820, "edme")
        # the paper, its lines swimming as he panics
        px, py = 880, 626
        ctx.c.drawRect(skia.Rect.MakeXYWH(px, py, 120, 14), fill((240, 240, 236)))
        for k in range(4):
            w = math.sin(t * 6 + k) * 6 * panic
            ctx.c.drawLine(px + 8 + w, py - 4 - k * 0.1, px + 110 - w, py - 4, stroke((120, 120, 130), 1.4, 0.4))
        sx, sy = 780, 690
        P.chair(ctx, sx, sy, 1, key="mechair")
        hip, feet = seated(sx, sy, 1)
        shake = math.sin(t * 40) * 4 * panic * (not times)
        drop = t >= EVENTS["pencil"]
        hands = {"near": (920 + shake, 626), "far": (880, 632)}
        J = HIM.draw(ctx, hip, 1, lean=0.24 + 0.08 * panic, feet=feet, expr="anxious" if not times else "hurt", look=(1, 0.8),
                     hands=free_hands(HIM, hip, 1, 0.24, hands))
        hp = J["limbs"]["arm_near"][2]
        if not drop:
            ctx.c.drawLine(hp[0], hp[1] - 4, hp[0] + 26, hp[1] - 30, stroke((230, 190, 70), 6))
        else:
            k = prog(t, EVENTS["pencil"], EVENTS["pencil"] + 0.4)
            y = lerp(hp[1], FY - 4, k * k)
            ctx.c.drawLine(hp[0] + 10, y, hp[0] + 40, y - (30 if k < 1 else 4), stroke((230, 190, 70), 6))
        for k in range(3):
            if panic > 0.3:
                extras_sweat(ctx, J, k)
        number_over(ctx, J, air_at(t) if times else 62400, 0.6 + 0.4 * panic)
    if times:
        a = prog(t, EVENTS["times_up"], EVENTS["times_up"] + 0.3)
        rrect(ctx, W / 2 - 220, 800, 440, 100, 16, (0, 0, 0), None, a=0.6 * a)
        draw_text(ctx, "TIME'S UP", W / 2, 875, 80, TEXT, a, face=LG)
    label(ctx, "MOCK 19")
    vline(ctx, "V6", 1500, 640, 56)
    cap(ctx, "C5", y=990)
    hud(ctx, t)


def extras_sweat(ctx, J, k):
    hx, hy = J["head"]
    x, y, d = hx - 34 + k * 26, hy - 40 + (k % 2) * 16, 5
    drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
    ctx.c.drawPath(drop, fill((200, 225, 255), 0.9))
    ctx.c.drawPath(drop, stroke((90, 120, 170), 2))


# ---- the turn: the front step --------------------------------------------------------------------
def front_step(ctx, t):
    c = ctx.c
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), fill((18, 20, 30)))
    glow(ctx, 1500, 200, 70, (220, 220, 230), 0.4)
    c.drawCircle(1500, 200, 24, fill((226, 226, 232)))
    for i in range(30):
        c.drawCircle(-100 + hrand("st", i) * 2100, 90 + hrand("sy", i) * 260, 1.6, fill((200, 200, 210), 0.6))
    c.drawRect(skia.Rect.MakeLTRB(-600, 160, 820, FY), fill((56, 48, 46)))
    for i in range(10):
        c.drawLine(-600, 200 + i * 60, 820, 200 + i * 60, stroke((64, 56, 52), 3))
    wrect(ctx, 420, FY - 90 - 400, 180, 400, "fdoor", (74, 58, 50), LINE, 4, seg=2)
    c.drawRect(skia.Rect.MakeXYWH(495, FY - 90 - 450, 30, 30), fill((210, 196, 150)))
    glow(ctx, 510, FY - 90 - 435, 320, (255, 230, 170), 0.3)
    cone(ctx, (510, FY - 520), (300, FY), (1100, FY), (255, 230, 170), 0.10)
    wrect(ctx, 360, FY - 90, 860, 90, "step", (90, 84, 80), LINE, 3, seg=3)
    P.floor(ctx, FY)


def t1(ctx, t):
    sits = EVENTS["dad_sits"]
    d0, d1 = EVENTS["dad_num"]
    dad_num = fade(t, d0, d1, 0.6, 1.2)
    card = t >= EVENTS["card"]
    s0, s1 = EVENTS["shrink"]
    grey_k = prog(t, s0, s1)
    with Camera(lerp(1.5, 1.8, ease(prog(t, 84, 96))), 860, 500).apply(ctx):
        front_step(ctx, t)
        hip, feet = seated(780, FY - 94, 1, floor_y=FY)
        J = HIM.draw(ctx, hip, 1, lean=0.3 - 0.1 * prog(t, 92, 95), feet=feet, expr="hurt" if t < 92 else "hopeful",
                     look=(1, 0.8) if t < 87 else (1, 0.3), mouth_open=talk("him", t),
                     hands=free_hands(HIM, hip, 1, 0.3, {"near": (880, 640), "far": (868, 646)}),
                     tear=prog(t, 85.0, 86.6) if t < 88 else 0.0)
        val = 74000
        number_over(ctx, J, val, 0.5 * (1 - 0.85 * grey_k), rgb=mix(RED, (150, 150, 156), grey_k), a=1 - prog(t, s1 - 0.4, s1 + 0.6), dx=-60)
        if t < sits:
            k = prog(t, 82.0, sits)
            x, ph = walk_x(560, (t - 82.0), 240)
            hipd, feetd = standing(min(x, 1000), FY - 90, -1, step=ph)
            DAD.draw(ctx, hipd, -1, lean=0.04, feet=feetd, expr="worried", look=(-1, 0.4), alpha=min(1, k * 3))
        else:
            hipd, feetd = seated(1000, FY - 94, -1, floor_y=FY)
            hold = card
            hands = {"near": (920, 620), "far": (930, 626)} if hold else {"near": (930, 650), "far": (940, 654)}
            Jd = DAD.draw(ctx, hipd, -1, lean=0.14, feet=feetd, expr="sad" if t < 92 else "smile", look=(-1, 0.5),
                          mouth_open=talk("dad", t), hands=free_hands(DAD, hipd, -1, 0.14, hands))
            if hold:
                hp = Jd["limbs"]["arm_near"][2]
                a = prog(t, EVENTS["card"], EVENTS["card"] + 0.4)
                rrect(ctx, hp[0] - 66, hp[1] - 50, 96, 64, 4, (230, 220, 196), LINE, 2, a=a)
                draw_text(ctx, "1996", hp[0] - 18, hp[1] - 24, 18, (60, 50, 40), a, face=LG)
                draw_text(ctx, "41,286", hp[0] - 18, hp[1] + 2, 20, (160, 50, 40), a, face=LG)
            number_over(ctx, Jd, 41286, 0.22, rgb=(150, 150, 156), a=0.55 * dad_num, dx=90)
            speech(ctx, t, "dad", Jd["head"][0] + 120, Jd["head"][1] + 10)
        speech(ctx, t, "him", J["head"][0] - 150, J["head"][1] + 10)
    cap(ctx, "C6", y=935)
    cap(ctx, "C7", y=1000)
    hud(ctx, t)


# ---- the lesson and the practice -------------------------------------------------------------------
def l1(ctx, t):
    a = ease(prog(t, EVENTS["lesson"], EVENTS["lesson"] + 0.6))
    c = ctx.c
    c.saveLayerAlpha(None, int(255 * a))
    y = 600
    x0, x1 = 260, 1660
    c.drawLine(x0, y, x1, y, stroke((200, 200, 210), 6))
    for age in range(20, 81, 10):
        x = lerp(x0, x1, (age - 17) / 63)
        c.drawLine(x, y - 14, x, y + 14, stroke((200, 200, 210), 4))
        draw_text(ctx, str(age), x, y + 60, 34, (170, 170, 180), face=LG)
    draw_text(ctx, "17", x0, y + 60, 34, (170, 170, 180), face=LG)
    draw_text(ctx, "AGE", x0 - 90, y + 60, 30, (140, 140, 150), face=LG)
    k = ease(prog(t, 101.6, 104.4))
    dx = lerp(W / 2, x0 + 22, k)
    dy = lerp(420, y, k)
    size = lerp(150, 0, k)
    if size > 4:
        draw_text(ctx, "74,000", dx, dy, size, RED, 1.0, face=LG, glow_rgb=RED_D)
    c.drawCircle(x0 + 22, y, 12 * k, fill(RED))
    draw_text(ctx, "JEE", x0 + 22, y - 36, 30, RED, k, face=LG)
    # the rest of the line fills with small things: family, friends, kites, work, travel
    things = ["FAMILY", "FRIENDS", "KITES", "WORK", "LOVE", "TRAVEL", "HOME"]
    for i, s in enumerate(things):
        kk = ease(prog(t, 104.6 + i * 0.4, 105.0 + i * 0.4))
        x = lerp(x0, x1, (i + 1.3) / 8)
        draw_text(ctx, s, x, y - 50 - (i % 2) * 44, 28, GOLD if i == 2 else (170, 190, 220), kk, face=LG)
    c.restore()
    cap(ctx, "C8", y=190)
    cap(ctx, "C9", y=990)
    hud(ctx, t)


INSTEAD = ["Sleep 7 hours, even before a test.", "Learn from one mistake, not the rank.", "Tell someone when it's too much."]


def i1(ctx, t):
    a = fade(t, EVENTS["card_i"], 116.0, 0.3, 0.3)
    rrect(ctx, W / 2 - 500, 280, 1000, 480, 22, (236, 232, 214), LINE, 5, a=a)
    draw_text(ctx, "INSTEAD OF MORE HOURS:", W / 2 - 440, 380, 64, (40, 40, 46), a, align="left", face=LG)
    for i, s in enumerate(INSTEAD):
        k = ease(prog(t, EVENTS["card_i"] + 0.4 + i * 0.6, EVENTS["card_i"] + 0.8 + i * 0.6))
        y = 480 + i * 90
        rrect(ctx, W / 2 - 440, y - 40, 44, 44, 6, None, (40, 40, 46), 4, a=a * k)
        draw_text(ctx, s, W / 2 - 370, y, 46, (40, 40, 46), a * k, align="left")
    hud(ctx, t)


# ---- the final fight -------------------------------------------------------------------------------
def f1(ctx, t):
    r0, r1_ = EVENTS["rise"]
    rise = ease(prog(t, r0, r1_)) * (1 - prog(t, EVENTS["crumble"], EVENTS["crumble"] + 0.05))
    lamp = 1.0 - ease(prog(t, EVENTS["lamp"], EVENTS["lamp"] + 0.2))
    zoom = lerp(1.55, 1.85, ease(prog(t, 117, 125)))
    with Camera(zoom, 1040, 480, shake=1.4 * prog(t, 121, 125) * (t < 125)).apply(ctx):
        room(ctx, t, lamp=lamp, clock="11:40")
        if rise > 0:
            P.villain(ctx, 1500, FY, scale=lerp(0.7, 1.3, rise), alpha=rise, grin=1.2, lean=-0.35,
                      reach=(1200, 540) if rise > 0.7 else None)
        if EVENTS["crumble"] < t < EVENTS["crumble"] + 2.2:
            P.villain_shards(ctx, 1500, FY, 1.3, prog(t, EVENTS["crumble"], EVENTS["crumble"] + 2.0))
        closed = t >= EVENTS["book"]
        expr = "anxious" if t < 125 else ("closed" if t < 126.4 else "hopeful")
        J = at_desk(ctx, t, expr=expr, look=(1, 0.6) if t < 125 else (1, 0.0), writing=t < 118, glow_on=0.8 * lamp)
        # the open book in front of him, closing
        bx, by = 900, 626
        w = 60 if not closed else lerp(60, 30, prog(t, EVENTS["book"], EVENTS["book"] + 0.3))
        ctx.c.drawRect(skia.Rect.MakeXYWH(bx, by - 6, w, 8), fill((236, 232, 220)))
        ctx.c.drawRect(skia.Rect.MakeXYWH(bx, by - 6, w, 8), stroke(LINE, 2))
    label(ctx, "JAN 21, 11:40 PM")
    vline(ctx, "V7", 1060, 210, 58)
    vline(ctx, "V8", 1060, 290, 54)
    vline(ctx, "V9", 1060, 210, 62)
    hud(ctx, t)


def f2(ctx, t):
    br = EVENTS["breath"]
    with Camera(1.6, 900, 480).apply(ctx):
        exam_hall(ctx, t, morning=1.0, tick=False)
        for i, x in enumerate((340, 1300)):
            exam_desk(ctx, x, ("ed", i))
            sit(grey(f"st{i}"), ctx, x - 40, f=1, lean=0.2, expr="neutral", look=(1, 0.9),
                hands={"near": (x + 90, 630), "far": (x + 60, 634)})
        exam_desk(ctx, 820, "edme")
        ctx.c.drawRect(skia.Rect.MakeXYWH(880, 626, 120, 14), fill((240, 240, 236)))
        sx, sy = 780, 690
        P.chair(ctx, sx, sy, 1, key="mechair")
        hip, feet = seated(sx, sy, 1)
        breathing = prog(t, br, br + 5.0)
        writing = t >= EVENTS["write"]
        wv = 6 * math.sin(t * 9) if writing else 0.0
        lean = 0.12 + (0.1 if writing else -0.04 * math.sin(2 * math.pi * breathing * 1.5))
        J = HIM.draw(ctx, hip, 1, lean=lean, feet=feet, expr="closed" if not writing else "determined", look=(1, 0.8),
                     hands=free_hands(HIM, hip, 1, lean, {"near": (930 + wv, 626), "far": (880, 632)}))
        hp = J["limbs"]["arm_near"][2]
        ctx.c.drawLine(hp[0], hp[1] - 4, hp[0] + 26, hp[1] - 30, stroke((230, 190, 70), 6))
    if not writing:
        k = 0.5 - 0.5 * math.cos(2 * math.pi * breathing * 1.5)
        a = fade(t, br, EVENTS["write"], 0.4, 0.4)
        r = 60 + 90 * k
        glow(ctx, W / 2, 330, r * 1.6, (170, 210, 255), 0.25 * a)
        ctx.c.drawCircle(W / 2, 330, r, stroke((200, 225, 255), 6, a))
        draw_text(ctx, "breathe in" if math.sin(2 * math.pi * breathing * 1.5) >= 0 else "breathe out", W / 2, 345, 40, TEXT, a)
    label(ctx, "JEE MAIN")
    hud(ctx, t)


# ---- payoff, viewer, mirror, title ----------------------------------------------------------------
def park(ctx, t, warm=1.0):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, FY)], [col((110, 160, 220)), col((236, 220, 180))])
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), skia.Paint(Shader=sky))
    glow(ctx, 1640, 220, 300, (255, 236, 180), 0.5 * warm)
    c.drawCircle(1640, 220, 60, fill((255, 230, 150)))
    for i in range(9):
        kx = 200 + i * 190 + 30 * math.sin(t * 0.8 + i)
        ky = 140 + 60 * hrand("ky", i) + 12 * math.sin(t * 1.3 + i)
        rgb = [(226, 80, 80), (80, 150, 226), (236, 200, 70), (120, 190, 110), (200, 110, 200)][i % 5]
        kite(ctx, kx, ky, 0.32, rgb=rgb, rot=10 * math.sin(t + i), tail=False)
    for i in range(14):
        x = -200 + i * 160
        hgt = 60 + 40 * hrand("pt", i)
        c.drawCircle(x, FY - 120 - hgt * 0.4, hgt, fill((80, 130, 90)))
    c.drawRect(skia.Rect.MakeLTRB(-600, FY - 130, W + 600, FY + 400), fill((120, 170, 100)))
    P.floor(ctx, FY)


def p1(ctx, t):
    buzz = EVENTS["buzz"]
    pocket = t >= EVENTS["pocket"]
    flying = ease(prog(t, EVENTS["kite"], EVENTS["kite"] + 1.6))
    laugh = ease(prog(t, EVENTS["laugh"] - 0.3, EVENTS["laugh"]))
    with Camera(1.45, 960, 480).apply(ctx):
        park(ctx, t)
        Jp = stand(PIHU, ctx, 1180, f=-1, lean=0.02 - 0.05 * laugh, expr="happy" if laugh > 0.3 or flying > 0.5 else "hopeful",
                   look=(-1, -0.8) if flying > 0.3 else (-1, 0.0), mouth_open=0.4 * laugh * abs(math.sin(t * 9)))
        hip, feet = standing(860, FY, 1)
        J0 = HIM.joints(hip, 1, 0.0)
        sh = J0["shoulder"]
        if not pocket:
            hands = {"near": (sh[0] + 50, sh[1] + 60)}
        else:
            hands = {"far": (sh[0] + 40 * flying, sh[1] - 60 * flying + 40)}
        J = HIM.draw(ctx, hip, 1, lean=0.02 - 0.06 * flying, feet=feet, expr="smile" if t > buzz + 0.6 else "worried",
                     look=(1, 0.5) if not pocket else (0.6, -0.8 * flying), mouth_open=0.4 * laugh * abs(math.sin(t * 9 + 1)),
                     hands=free_hands(HIM, hip, 1, 0.0, hands))
        if not pocket:
            hp = J["limbs"]["arm_near"][2]
            P.phone_held(ctx, *hp, on=1.0)
            if t > buzz:
                a = prog(t, buzz, buzz + 0.3)
                rrect(ctx, hp[0] + 40, hp[1] - 150, 330, 90, 14, (236, 232, 214), None, a=a)
                draw_text(ctx, "JEE MAIN RESULT", hp[0] + 205, hp[1] - 116, 24, (60, 60, 66), a, face=LG)
                draw_text(ctx, "AIR 21,480", hp[0] + 205, hp[1] - 78, 36, (40, 40, 46), a, face=LG)
        else:
            hp = J["limbs"]["arm_far"][2]
            kx, ky = lerp(hp[0] + 60, 1400, flying), lerp(hp[1] - 40, 220, flying)
            kx += 20 * math.sin(t * 1.3)
            ky += 10 * math.sin(t * 1.9)
            ctx.c.drawPath(poly_path([hp, ((hp[0] + kx) / 2, (hp[1] + ky) / 2 + 60), (kx, ky + 60)], closed=False, smooth=True),
                           stroke((250, 250, 250), 2))
            kite(ctx, kx, ky, 0.7, rot=12 * math.sin(t))
    label(ctx, "SANKRANTI")
    cap(ctx, "C10", y=925)
    cap(ctx, "C11", y=995)
    hud(ctx, t)


def vt(ctx, t):
    a = fade(t, 152.2, 159.0, 0.6, 0.6)
    off = ease(prog(t, EVENTS["lamp_vt"], EVENTS["lamp_vt"] + 0.3))
    c = ctx.c
    c.saveLayerAlpha(None, int(255 * a))
    lx, ly = W / 2 + 80, 560
    glow(ctx, lx - 80, ly + 60, 600, LAMP, 0.35 * (1 - off))
    c.drawLine(lx, 820, lx - 20, ly + 20, stroke((70, 70, 78), 12))
    c.drawPath(poly_path([(lx - 170, ly + 60), (lx - 80, ly - 30), (lx + 30, ly + 12)]), fill((80, 80, 88)))
    c.drawPath(poly_path([(lx - 170, ly + 60), (lx - 80, ly - 30), (lx + 30, ly + 12)]), stroke(LINE, 5))
    c.drawCircle(lx - 90, ly + 70, 26, fill(mix(LAMP, (60, 60, 66), off)))
    wrect(ctx, W / 2 - 360, 820, 720, 30, "vtdesk", (70, 66, 64), LINE, 4, seg=2)
    c.restore()
    cap(ctx, "V1", y=190, size=52)
    cap(ctx, "V2", y=190, size=52)


def x1(ctx, t):
    fade_k = prog(t, EVENTS["fade_kid"], EVENTS["fade_kid"] + 1.2)
    with Camera(1.55, 960, 480).apply(ctx):
        c = ctx.c
        sky = skia.GradientShader.MakeLinear([(0, 0), (0, FY)], [col((130, 170, 220)), col((236, 220, 190))])
        c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), skia.Paint(Shader=sky))
        for i in range(12):
            bx = -200 + i * 190
            bh = 220 + 80 * hrand("ap", i)
            c.drawRect(skia.Rect.MakeXYWH(bx, FY - bh, 170, bh), fill((150, 140, 130)))
            for j in range(3):
                c.drawRect(skia.Rect.MakeXYWH(bx + 30 + (j % 2) * 70, FY - bh + 30 + j * 60, 40, 30), fill((90, 100, 120)))
        for gx in (560, 1360):
            wrect(ctx, gx - 20, FY - 300, 40, 300, ("gp", gx), (120, 110, 100), LINE, 3, seg=2)
        for i in range(12):
            c.drawLine(600 + i * 64, FY - 220, 600 + i * 64, FY, stroke((60, 60, 66), 4))
        c.drawLine(580, FY - 220, 1340, FY - 220, stroke((60, 60, 66), 6))
        P.floor(ctx, FY)
        Jd = stand(DAD, ctx, 760, f=1, lean=0.02, expr="smile" if t > 162.4 else "neutral", look=(1, 0.0), mouth_open=talk("dad", t))
        Ju = stand(UNCLE, ctx, 1060, f=-1, lean=0.04, expr="neutral" if t < 164.2 else "worried", look=(-1, 0.0) if t < 164.4 else (1, 0.6),
                   mouth_open=talk("uncle", t))
        kid = grey("kid", 0.78)
        Jk = stand(kid, ctx, 1220, f=-1, lean=0.06, expr="sad" if fade_k < 0.5 else "hopeful", look=(-1, 0.6))
        number_over(ctx, Jk, 63510, 0.26, a=1 - fade_k, dx=60)
        speech(ctx, t, "uncle", Ju["head"][0] - 150, Ju["head"][1] - 70)
        speech(ctx, t, "dad", Jd["head"][0] + 60, Jd["head"][1] - 80)


def title(ctx, t):
    a = fade(t, EVENTS["title"], 177.0, 0.8, 0.6)
    draw_text(ctx, "RANK.", W / 2, 520, 220, TEXT, a, face=LG)
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 250 + 500 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=48)
    cap(ctx, "T2", y=770, size=72, rgb=GOLD, glow_rgb=(170, 110, 20))


def helpline(ctx, t):
    cap(ctx, "H1", y=500, size=44)
    cap(ctx, "H2", y=580, size=38, rgb=(190, 190, 196))


DISPATCH = {
    "S01": s01, "H1": h1, "S02": s02, "B1": b1, "G1": g1, "G2": g2, "G3": g3, "R1": r1, "T1": t1, "L1": l1, "I1": i1,
    "F1": f1, "F2": f2, "P1": p1, "VT": vt, "X1": x1, "TT": title, "HL": helpline,
}
CONTINUOUS = {"S01", "G1", "HL"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1_, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "HL":
        black(ctx, prog(t, DURATION - 0.8, DURATION))
