"""LATER.: picture. scene(ctx) draws any frame of the film.

The device: a jar of marbles on his shelf, one for every Sunday his dad has left. Every Sunday one falls out,
whether he goes or not. The SUNDAYS LEFT counter ticks down with each one. At the payoff the marble falls gold,
into a new jar: WITH DAD.
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
from studio.extras import (speech as _speech, talk as _talk, free_hands, lift, floor_sit, door, box, dog, street,  # noqa: E402
                           office, phone_close)
from timeline import SCENES, CAPS, CUES, BUBBLES, EVENTS, LEFT, DURATION, scene_at, left_at, left_changed  # noqa: E402
from lines import CAPTIONS, VILLAIN, MATH  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
GLASS = (190, 205, 220)
MARBLE = (130, 156, 196)


# ---- cast -------------------------------------------------------------------------------
def moustache(ctx, hx, hy, f, s):
    fx = hx + f * 14 * s
    p = poly_path([(fx - 15 * s, hy + 13 * s), (fx - 6 * s, hy + 8 * s), (fx, hy + 10 * s), (fx + 6 * s, hy + 8 * s),
                   (fx + 15 * s, hy + 13 * s), (fx + 8 * s, hy + 15 * s), (fx, hy + 13 * s), (fx - 8 * s, hy + 15 * s)], smooth=True)
    ctx.c.drawPath(p, fill((150, 148, 146)))
    ctx.c.drawPath(p, stroke(LINE, 2 * s))


def bun(ctx, hx, hy, f, s):
    wcircle(ctx, hx - f * 30 * s, hy - 44 * s, 20 * s, "bun", (60, 54, 58), LINE, 3 * s)


HIM = Character("him")
DAD = Character("dad", extra=moustache)
MAYA = Character("maya", extra=bun)


def grey(name, scale=1.0):
    return Character(name, skin=(150, 150, 156), scale=scale)


# ---- shared helpers -----------------------------------------------------------------------
def cap(ctx, k, y=190, size=50, rgb=TEXT, glow_rgb=None):
    t0, t1 = CAPS[k]
    caption(ctx, CAPTIONS[k], t0, t1, y=y, size=size, rgb=rgb, glow_rgb=glow_rgb)


def vline(ctx, k, x, y, size=48):
    t0 = CUES[k]
    villain_text(ctx, VILLAIN[k], t0 - 0.05, t0 + LEN.get(k, 1.4) + 0.5, x, y, size)


def label(ctx, s):
    draw_text(ctx, s, 60, LETTERBOX + 170, 38, (190, 190, 196), align="left")


def speech(ctx, t, who, x, y, **kw):
    _speech(ctx, t, BUBBLES, who, x, y, **kw)


def talk(who, t):
    return _talk(BUBBLES, who, t)


def pop_at(t, t0, dur=0.35):
    if t0 is None:
        return 0.0
    return prog(t, t0, t0 + dur) if t0 <= t <= t0 + dur else 0.0


def hud(ctx, t, a=1.0):
    v = left_at(t)
    if v is None:
        return
    P.hud(ctx, v, label="SUNDAYS LEFT", a=a * ease(prog(t, LEFT[0][0], LEFT[0][0] + 0.4)), pop=pop_at(t, left_changed(t)))


def hud_dad(ctx, t, a=1.0):
    k = EVENTS["gold_drop"] + 0.6
    if t < k:
        return
    P.hud(ctx, 1, label="WITH DAD", a=a * ease(prog(t, k, k + 0.3)), rgb=GOLD, pop=pop_at(t, k, 0.4), x=56 + 268 + 18)


def stand(ch, ctx, x, f=1, lean=0.04, step=0.0, free=False, **kw):
    hip, feet = standing(x, FY, f, ch.scale, step=step)
    if free and kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def sit(ch, ctx, x, seat_y=690, f=1, lean=0.2, **kw):
    hip, feet = seated(x, seat_y, f)
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


# ---- the device: the jar and its marbles ------------------------------------------------------
JAR_MAX = 780


def marble(ctx, x, y, r=9, rgb=MARBLE, a=1.0, gold=False):
    rgb = GOLD if gold else rgb
    if gold:
        glow(ctx, x, y, r * 4, GOLD, 0.45 * a)
    ctx.c.drawCircle(x, y, r, fill(rgb, a))
    ctx.c.drawCircle(x, y, r, stroke(LINE, 2, a))
    ctx.c.drawCircle(x - r * 0.35, y - r * 0.35, r * 0.3, fill((255, 255, 255), 0.8 * a))


def jar(ctx, x, base_y, value, key="jar", w=130, h=180, name="SUNDAYS", gold_n=0, max_v=JAR_MAX, r=9):
    """A glass jar standing on base_y, filled in proportion to value/max_v. Returns its rim point."""
    c = ctx.c
    x0, y0 = x - w / 2, base_y - h
    n_rows, n_cols = int((h - 30) / (r * 2)), int((w - 16) / (r * 2))
    cap_n = n_rows * n_cols
    shown = int(round(cap_n * value / max_v)) if gold_n == 0 else gold_n
    for i in range(shown):
        row, col_ = divmod(i, n_cols)
        mx = x0 + 8 + r + col_ * r * 2 + (row % 2) * r * 0.5 + (hrand(key, i) - 0.5) * 2
        my = base_y - 8 - r - row * r * 1.8
        marble(ctx, mx, my, r, rgb=mix(MARBLE, (100, 120, 160), hrand(key, i, 1)), gold=gold_n > 0)
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0, w, h), 18, 18)
    c.drawRRect(body, fill(GLASS, 0.10))
    c.drawRRect(body, stroke(GLASS, 4, 0.75))
    c.drawRect(skia.Rect.MakeXYWH(x0 - 6, y0 - 4, w + 12, 12), stroke(GLASS, 4, 0.75))
    c.drawLine(x0 + 16, y0 + 24, x0 + 16, base_y - 30, stroke((255, 255, 255), 4, 0.25))
    if name:
        wrect(ctx, x - 46, y0 + 34, 92, 30, (key, "lbl"), (214, 206, 186), LINE, 2, seg=1)
        draw_text(ctx, name, x, y0 + 56, 18 if len(name) < 9 else 15, (50, 46, 44), face="LuckiestGuy-Regular.ttf")
    return (x, y0)


def falling_marble(ctx, t, t0, rim, floor_y=FY, dirx=1, gold=False, land=None, dur=1.5):
    """A marble lifts out over the rim and drops (to the floor, or into `land`)."""
    k = (t - t0) / dur
    if k < 0 or k > 1:
        return
    x0, y0 = rim
    if k < 0.25:  # pops up over the rim
        q = k / 0.25
        x, y = x0 + dirx * 30 * q, y0 - 40 * math.sin(math.pi * q * 0.5)
    else:
        q = (k - 0.25) / 0.75
        tx = land[0] if land else x0 + dirx * 140
        ty = land[1] if land else floor_y - 9
        x = lerp(x0 + dirx * 30, tx, q)
        y = lerp(y0 - 40, ty, q * q)
        if land is None and q > 0.85:
            x += dirx * (q - 0.85) * 600  # rolls away
    marble(ctx, x, y, 9, gold=gold, a=1.0 if k < 0.9 else (1 - k) * 10)


def drops_between(t0, t1):
    """Times the counter ticks down between t0 and t1."""
    return [tm for tm, _ in LEFT[1:] if t0 <= tm < t1]


def wall_clock_text(ctx, x, y, s):
    rrect(ctx, x - 78, y - 32, 156, 50, 10, (16, 16, 20), (70, 70, 80), 3)
    draw_text(ctx, s, x, y + 6, 30, (200, 200, 206), face="LuckiestGuy-Regular.ttf")


# ---- props and sets --------------------------------------------------------------------------
def laptop(ctx, x, desk_y, open_k=1.0, glow_a=1.0, text=None, key="lap"):
    """A laptop on the desk; open_k 1 open .. 0 shut. Returns the screen centre."""
    wrect(ctx, x - 90, desk_y - 10, 180, 10, (key, "base"), (60, 62, 70), LINE, 3, seg=2)
    hgt = 110 * open_k
    if hgt > 4:
        sx, sy = x - 80, desk_y - 10 - hgt
        rrect(ctx, sx, sy, 160, hgt, 6, (40, 42, 50), LINE, 3)
        ctx.c.drawRect(skia.Rect.MakeXYWH(sx + 8, sy + 8, 144, max(0, hgt - 16)), fill((110, 140, 190), glow_a))
        glow(ctx, x, sy + hgt / 2, 260, BLUE, 0.18 * glow_a)
        if text and open_k > 0.9:
            for i, ln in enumerate(text):
                draw_text(ctx, ln, sx + 16, sy + 34 + i * 26, 18, (20, 24, 40), glow_a, align="left")
        return (x, sy + hgt / 2)
    return (x, desk_y - 10)


def ringing(ctx, t, x, y, t_ring, t_end, who="Dad", declined=True, key="ph"):
    """A phone lying on a surface, ringing from t_ring until t_end (declined: a red flash, then dark)."""
    on = t_ring <= t < t_end
    jx = (hrand(key, ctx.frame) - 0.5) * 7 if on and int(t * 8) % 2 == 0 else 0
    P.phone_side(ctx, x + jx, y, on=1.0 if on else 0.0, key=key)
    if on:
        a = ease(prog(t, t_ring, t_ring + 0.2))
        rrect(ctx, x - 70, y - 96, 140, 56, 20, (30, 32, 40), (90, 92, 104), 2, a=a)
        draw_text(ctx, who, x, y - 58, 34, TEXT, a)
        for i in range(2):
            ctx.c.drawCircle(x, y - 20, 40 + 30 * ((t * 1.6 + i * 0.5) % 1), stroke(TEXT, 2, 0.35 * a * (1 - (t * 1.6 + i * 0.5) % 1)))
    elif declined and t_end <= t < t_end + 0.35:
        draw_text(ctx, "declined", x, y - 58, 28, RED, 1 - prog(t, t_end, t_end + 0.35))


SEASON = {"night": (22, 26, 38), "day": (84, 96, 118), "autumn": (70, 60, 52), "winter": (60, 66, 80), "dawn": (110, 104, 120)}

SHELF = (1300, 520)  # shelf board left end, top y
JAR_X = 1410


def flat(ctx, t, sky="night", value=None, desk=True, lap=1.0, lap_text=None, jar2=None, door_kw=None, lamp=1.0, coat=True):
    P.back_wall(ctx)
    P.floor(ctx, FY)
    P.window(ctx, 1560, 200, 220, 220, "fwin", night=sky == "night", sky=SEASON[sky], moon=sky == "night")
    if sky == "autumn":
        for i in range(10):
            ph = (t * 0.4 + hrand("leaf", i)) % 1
            ctx.c.drawCircle(1570 + hrand("lx", i) * 200, 205 + ph * 210, 6, fill((190, 120, 60), 0.8))
    door(ctx, 160, **(door_kw or {}))
    if coat:
        wline(ctx, (390, 330), (420, 330), "hook", GREY_L, 5, seg=1)
        P.wrect(ctx, 384, 336, 46, 150, "coat", (78, 70, 64), LINE, 3, seg=2)
    if lamp > 0:
        P.wrect(ctx, 560, FY - 300, 8, 300, "lamp", GREY_D, LINE, 2, seg=2)
        wrect(ctx, 530, FY - 340, 68, 44, "shade", (150, 140, 120), LINE, 3, seg=2)
        glow(ctx, 564, FY - 310, 300, (255, 210, 150), 0.14 * lamp)
    wrect(ctx, SHELF[0], SHELF[1], 260, 14, "shelf", (96, 80, 66), LINE, 3, seg=2)
    rim = None
    if value is not None:
        rim = jar(ctx, JAR_X, SHELF[1], value)
    if jar2 is not None:
        jar(ctx, JAR_X + 120 + 10, SHELF[1], 0, key="jar2", w=90, h=130, name="WITH DAD", gold_n=jar2, r=8)
    scr = None
    if desk:
        P.table(ctx, 700, 640, 420, key="desk")
        P.chair(ctx, 760, 690, 1, key="dchair")
        scr = laptop(ctx, 940, 640, open_k=lap, text=lap_text)
        wall_clock_text(ctx, 1200, 420, "SUN 10:00" if sky != "night" else "SUN 23:40")
    return rim, scr


def kitchen(ctx, t, warm=0.0, plates=2, cup_open=0.0, plate_held=None):
    P.back_wall(ctx, rgb=mix((24, 24, 27), (52, 40, 30), warm))
    if warm > 0:
        glow(ctx, 960, 380, 900, GOLD, 0.22 * warm)
    P.floor(ctx, FY, rgb=mix(P.FLOOR, (96, 78, 58), warm))
    P.window(ctx, 1420, 220, 220, 200, "kwin", night=False, moon=False, sky=mix((70, 78, 92), (170, 140, 90), warm))
    wrect(ctx, 520, 250, 240, 150, "cup", (90, 84, 76), LINE, 3, seg=2)  # cupboard
    wline(ctx, (640, 250), (640, 400), "cupm", LINE, 3)
    if cup_open > 0:
        ctx.c.drawRect(skia.Rect.MakeXYWH(644, 254, 112 * cup_open, 142), fill((40, 36, 32)))
        for i in range(3):
            P.wrect(ctx, 660, 360 - i * 10, 80 * cup_open, 8, ("cplate", i), (220, 218, 210), LINE, 2, seg=1)
    P.table(ctx, 820, 640, 380, key="ktable")
    P.chair(ctx, 860, 690, 1, key="kc1")
    P.chair(ctx, 1160, 690, -1, key="kc2")
    for i in range(plates):
        px = 900 + i * 160
        P.wrect(ctx, px, 628, 90, 10, ("plate", i), (220, 218, 210), LINE, 3, seg=2)
    if plate_held is not None:
        P.wrect(ctx, plate_held[0] - 45, plate_held[1] - 5, 90, 10, "pheld", (220, 218, 210), LINE, 3, seg=2)
    wrect(ctx, 1300, 600, 180, 180, "stove", (70, 70, 76), LINE, 3, seg=2)
    wrect(ctx, 1330, 586, 110, 14, "pan", (40, 40, 44), LINE, 3, seg=2)


def phone_on(ctx, t, x, y, who, t0, t1, key="ph"):
    ringing(ctx, t, x, y, t0, t1, who=who, key=key)


# ---- the hook ----------------------------------------------------------------------------------
def s01(ctx, t):
    """Opens on the first picture, not a black card: the next scene's first frame with a slow push-in, the caption
    over it (October 18: strangers were leaving within 5 seconds of a black opening)."""
    k = ease(prog(t, 0.0, 3.0))
    z = 1.0 + 0.05 * k
    ctx.c.save()
    ctx.c.translate(W / 2, H / 2)
    ctx.c.scale(z, z)
    ctx.c.translate(-W / 2, -H / 2)
    h1(ctx, 3.0)
    ctx.c.restore()
    ctx.c.drawRect(skia.Rect.MakeXYWH(0, H - 260, W, 260), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [(0, H - 260), (0, H)], [col((0, 0, 0), 0.0), col((0, 0, 0), 0.6)])))
    cap(ctx, "C1", y=985, size=58)


def him_at_desk(ctx, t, expr="neutral", reach=None, look=(1, 0.4), glowv=0.6, **kw):
    hands = {"near": (880, 634), "far": (862, 638)}
    if reach is not None:
        hands["near"] = reach
    hip, feet = seated(760, 690, 1)
    return HIM.draw(ctx, hip, 1, lean=0.24, feet=feet, hands=free_hands(HIM, hip, 1, 0.24, hands), expr=expr, look=look,
                    screen_glow=glowv, **kw)


def h1(ctx, t):
    dec = EVENTS["decline1"]
    with Camera(2.1, 960, 560).apply(ctx):
        flat(ctx, t, sky="day", value=780)
        ph = (1080, 636)
        tap = math.sin(math.pi * prog(t, dec - 0.4, dec + 0.2))
        reach = lerp2((880, 634), (ph[0] - 6, ph[1] - 4), tap)
        ringing(ctx, t, *ph, EVENTS["ring1"], dec)
        him_at_desk(ctx, t, "neutral" if t < 4.0 else "tired", reach=reach, look=(1, 0.6) if t > 3.8 else (1, -0.2))
    hud(ctx, t)


def h2(ctx, t):
    with Camera(2.6, JAR_X, 400).apply(ctx):
        rim, _ = flat(ctx, t, sky="day", value=left_at(t) or 780, desk=False)
        falling_marble(ctx, t, EVENTS["drop1"], rim)
    hud(ctx, t)


def h3(ctx, t):
    with Camera(2.1, 1040, 580).apply(ctx):
        P.back_wall(ctx, rgb=(26, 28, 30))
        P.floor(ctx, FY)
        for i in range(4):
            P.wrect(ctx, 400 + i * 120, 300, 80, 40, ("mirr", i), (60, 66, 76), LINE, 2, seg=1)
        wrect(ctx, 780, FY - 40, 420, 40, "tread", (50, 50, 56), LINE, 3, seg=3)
        wline(ctx, (1180, FY - 40), (1150, 560), "rail", GREY_L, 8, seg=1)
        wrect(ctx, 1110, 540, 90, 30, "console", (60, 62, 70), LINE, 3, seg=1)
        x, ph = walk_x(960, 0, 0)
        hip, feet = standing(960, FY - 40, 1, step=(t * 1.8) % 1)
        HIM.draw(ctx, hip, 1, lean=0.08, feet=feet, expr="tired", look=(1, 0.5),
                 hands=free_hands(HIM, hip, 1, 0.08, {"near": (1100, 556) if 9.6 < t < 10.2 else (1010, 600)}))
        ringing(ctx, t, 1150, 530, 9.2, 10.0, key="gph")
    hud(ctx, t)


def h4(ctx, t):
    with Camera(2.0, 1020, 580).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        wrect(ctx, 1300, 380, 300, 180, "tv", (30, 32, 40), LINE, 4, seg=2)
        ctx.c.drawRect(skia.Rect.MakeXYWH(1312, 392, 276, 156), fill((90, 120, 170), 0.8 + 0.2 * math.sin(t * 9)))
        glow(ctx, 1450, 470, 400, BLUE, 0.2)
        wrect(ctx, 640, 690, 420, 90, "sofa", (64, 66, 86), LINE, 3, seg=3)
        wrect(ctx, 620, 600, 40, 180, "sofaarm", (64, 66, 86), LINE, 3, seg=2)
        hip, feet = seated(860, 694, 1)
        HIM.draw(ctx, hip, 1, lean=-0.1, feet=feet, expr="neutral", look=(1, -0.3), screen_glow=0.8,
                 hands=free_hands(HIM, hip, 1, -0.1, {"near": (930, 664) if not (11.8 < t < 12.3) else (1040, 684), "far": (900, 670)}))
        P.wrect(ctx, 900, 656, 50, 16, "pad", (40, 40, 44), LINE, 2, seg=1)
        ringing(ctx, t, 1080, 684, 11.2, 12.0, key="sph")
    hud(ctx, t)


def h5(ctx, t):
    with Camera(2.0, 1060, 580).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeLTRB(-600, 0, W + 600, FY), fill((30, 27, 26)))
        P.wrect(ctx, 620, 170, 720, 300, "cwin", (44, 40, 38), (80, 74, 66), 5, seg=4)
        P.floor(ctx, FY, rgb=(80, 70, 60))
        P.table(ctx, 820, 640, 320, key="btable")
        for i, (x, f) in enumerate(((760, 1), (1220, -1))):
            P.chair(ctx, x, 690, f, key=("bc", i))
        sit(grey("b1"), ctx, 760, f=1, lean=0.12, expr="happy", mouth_open=0.4 * abs(math.sin(t * 8)),
            hands={"near": (866, 630), "far": (852, 638)})
        stand(grey("b2"), ctx, 990, f=1, lean=0.04, expr="happy", look=(1, 0))
        hip, feet = seated(1220, 690, -1)
        HIM.draw(ctx, hip, -1, lean=0.14, feet=feet, expr="happy", look=(-1, 0.4),
                 hands=free_hands(HIM, hip, -1, 0.14, {"near": (1070, 630) if 13.8 < t < 14.3 else (1110, 628), "far": (1124, 636)}))
        ringing(ctx, t, 1060, 632, 13.2, 14.0, key="bph")
    hud(ctx, t)


def m1(ctx, t):
    z = lerp(1.35, 1.6, ease(prog(t, 15, 24)))
    with Camera(z, lerp(1000, 1180, ease(prog(t, 15, 24))), 470).apply(ctx):
        flat(ctx, t, sky="night", value=left_at(t))
        hip, feet = standing(1180, FY, 1)
        HIM.draw(ctx, hip, 1, lean=0.02, feet=feet, expr="neutral" if t < 21 else "worried", look=(1, -0.6))
    # the sum, written up line by line like chalk
    for i, s in enumerate(MATH):
        t0 = 15.8 + i * 1.4
        a = fade(t, t0, 24.0, 0.4, 0.4)
        face = "LuckiestGuy-Regular.ttf" if i == 3 else "PatrickHand-Regular.ttf"
        draw_text(ctx, s, 140, 340 + i * 110, 92 if i == 3 else 62, GOLD if False else (TEXT if i < 3 else TEXT), a,
                  align="left", face=face)
    cap(ctx, "C2")
    hud(ctx, t)


def h6(ctx, t):
    dec = EVENTS["decline6"]
    born = ease(prog(t, 25.2, 26.4))
    with Camera(lerp(1.5, 1.65, prog(t, 24, 30.5)), 1000, 520).apply(ctx):
        rim, scr = flat(ctx, t, sky="day", value=left_at(t))
        falling_marble(ctx, t, EVENTS["drop6"], rim)
        for i in range(8):  # the villain rises out of the laptop's glow
            k = (t * 0.6 + hrand("wisp", i)) % 1.0
            a = (1 - k) * prog(t, 24.8, 25.4) * (1 - prog(t, 26.4, 27.2))
            ctx.c.drawCircle(scr[0] + (hrand("wx", i) - 0.5) * 120 + k * 200, scr[1] - k * 280, 10 + 18 * k, blurred(fill(RED, 0.35 * a), 8))
        P.villain(ctx, 1200, FY, scale=lerp(0.3, 1.05, born), alpha=born, grin=ease(prog(t, 26.0, 26.8)), lean=-0.2)
        ph = (1080, 636)
        hover = ease(prog(t, 25.0, 25.6))
        tap = ease(prog(t, dec - 0.3, dec))
        reach = lerp2((880, 634), (ph[0] - 10, ph[1] - 24 + 20 * tap), hover)
        ringing(ctx, t, *ph, EVENTS["ring6"], dec)
        him_at_desk(ctx, t, "worried" if t < dec else "tired", reach=reach, look=(1, 0.8))
    vline(ctx, "V1", 1240, 300, 60)
    hud(ctx, t)


def s04(ctx, t):
    cap(ctx, "C3", y=H / 2 + 16, size=58)


# ---- stakes: Dad -------------------------------------------------------------------------------
def d1(ctx, t):
    back = ease(prog(t, EVENTS["plate_back"], EVENTS["plate_back"] + 1.4))
    with Camera(1.5, 900, 520).apply(ctx):
        kitchen(ctx, t, warm=0.0, plates=1, cup_open=1.0 if 37.2 < t < 39.8 else 0.0,
                plate_held=lerp2((1060, 633), (700, 360), back) if t > EVENTS["plate_back"] else None)
        if t <= EVENTS["plate_back"]:
            P.wrect(ctx, 1015, 628, 90, 10, "plate2", (220, 218, 210), LINE, 3, seg=2)
        dog(ctx, 560, FY, f=1, key="olddog", rgb=(140, 130, 120), sit=True, wag=0.3)
        if t < EVENTS["plate_back"]:
            ph = (948, 528)  # at the side of his head
            J = stand(DAD, ctx, 960, f=1, lean=0.12, expr="hopeful" if t < 36.4 else "sad", look=(1, 0),
                      hands={"near": ph}, free=True)
            hp = J["limbs"]["arm_near"][2]
            rrect(ctx, hp[0] - 8, hp[1] - 34, 16, 40, 4, (40, 40, 46), LINE, 2.5)
            if t < 36.4:
                draw_text(ctx, "ringing...", 1120, 420, 30, (170, 170, 176), 0.8 * (0.5 + 0.5 * math.sin(t * 6)))
        else:
            hand = lerp2((1060, 633), (700, 360), back)
            x = lerp(960, 760, back)
            stand(DAD, ctx, x, f=1 if back < 0.3 else -1, lean=0.14, expr="sad", look=(1, 0.6) if back < 0.3 else (-1, -0.3),
                  hands={"near": hand}, free=True, step=(t * 1.4) % 1 if 0.1 < back < 0.9 else 0.0)
    hud(ctx, t)


def d2(ctx, t):
    phone_close(ctx, t, "Dad", ["no worries son! next week then :)", "next week for sure!"], [40.6, 43.6], mine=(1,),
                avatar=(150, 148, 146))
    vline(ctx, "V2", W / 2 + 520, 420, 56)
    hud(ctx, t)


# ---- the grind -----------------------------------------------------------------------------------
def g1(ctx, t):
    with Camera(1.55, 1000, 540).apply(ctx):
        office(ctx, desk_x=560)
        P.chair(ctx, 620, 690, 1, key="g1c")
        sit(HIM, ctx, 620, f=1, lean=0.26, expr="tired", look=(1, 0.2), hands={"near": (730, 634), "far": (714, 638)})
        P.table(ctx, 1150, 640, 300, key="mdesk")
        P.chair(ctx, 1360, 690, -1, key="g1c2")
        sit(MAYA, ctx, 1360, f=-1, lean=0.14, expr="tired", look=(-1, 0.6),
            hands={"near": (1250, 632) if not (47.4 < t < 48.2) else (1246, 630), "far": (1280, 636)})
        ringing(ctx, t, 1200, 632, 46.4, 47.9, who="Mum", key="mph")
    label(ctx, "YEAR 1")
    hud(ctx, t)


def g2(ctx, t):
    with Camera(2.0, JAR_X, 470).apply(ctx):
        rim, _ = flat(ctx, t, sky="night", value=left_at(t), desk=False, lamp=0.5)
        for tm in drops_between(49.5, 53.0):
            falling_marble(ctx, t, tm, rim, dirx=1 if int(tm * 10) % 2 else -1, dur=1.2)
    vline(ctx, "V3", 520, 360, 58)
    hud(ctx, t)


def g3(ctx, t):
    with Camera(1.45, 1000, 560).apply(ctx):
        P.back_wall(ctx, rgb=(26, 22, 30))
        P.floor(ctx, FY)
        for i in range(24):
            x = 300 + i * 60
            y = 250 + math.sin(i * 0.6) * 18
            glow(ctx, x, y, 24, (255, 210, 150), 0.25 + 0.15 * math.sin(t * 4 + i))
            ctx.c.drawCircle(x, y, 5, fill((240, 220, 180)))
        for i, x in enumerate((520, 680, 1240, 1400)):
            bob = abs(math.sin(t * 7 + i)) * 12
            f = 1 if i % 2 else -1
            hip, feet = standing(x, FY, f)
            ch = grey(f"p{i}")
            hp = (hip[0], hip[1] - bob)
            ch.draw(ctx, hp, f, lean=0.05, feet=lift(feet, -bob), expr="happy", mouth_open=0.5,
                    hands=free_hands(ch, hp, f, 0.05, {"near": (x + f * 70, hp[1] - 200), "far": (x - f * 64, hp[1] - 150)}))
        stand(HIM, ctx, 960, f=1, lean=0.04, expr="happy", look=(1, 0), mouth_open=0.4 * abs(math.sin(t * 9)),
              hands={"near": (1010, 600)}, free=True)
        P.wrect(ctx, 1002, 570, 22, 40, "drink", (180, 120, 80), LINE, 2, seg=1)
        P.table(ctx, 1080, 700, 140, key="ptab")
        P.phone_side(ctx, 1150, 698, on=1.0 if 53.6 < t < 55.2 else 0.0, face_down=True, key="pph")
        if t > 54.0:
            draw_text(ctx, "1 missed call: Dad", 1150, 660, 26, TEXT, ease(prog(t, 54.0, 54.3)))
    label(ctx, "YEAR 2")
    hud(ctx, t)


def g4(ctx, t):
    with Camera(1.5, 1180, 470).apply(ctx):
        flat(ctx, t, sky="autumn", value=left_at(t))
        him_at_desk(ctx, t, "tired", look=(1, 0.5))
        P.phone_side(ctx, 1110, 636, on=0.0, key="aph")
        draw_text(ctx, "Missed call: Dad", 1110, 600, 24, (200, 200, 206), ease(prog(t, 57.0, 57.4)))
    cap(ctx, "C4")
    hud(ctx, t)


def g5(ctx, t):
    phone_close(ctx, t, "Dad", ["merry christmas son. proud of you.", "thx dad u too"], [60.4, 62.2], mine=(1,),
                avatar=(150, 148, 146))
    vline(ctx, "V4", W / 2 + 520, 420, 56)
    label(ctx, "YEAR 3")
    hud(ctx, t)


def g6(ctx, t):
    lt = t - 63.5
    with Camera(1.4, 1080, 520).apply(ctx):
        P.back_wall(ctx, rgb=(28, 28, 32))
        P.floor(ctx, FY)
        P.window(ctx, 1560, 200, 220, 220, "nwin", night=False, sky=SEASON["winter"], moon=False)
        for i, (bx, by) in enumerate(((560, FY), (560, FY - 90), (690, FY), (820, FY))):
            box(ctx, bx, by, key=("nb", i))
        wrect(ctx, SHELF[0], SHELF[1], 260, 14, "shelf2", (96, 80, 66), LINE, 3, seg=2)
        jar(ctx, JAR_X, SHELF[1], left_at(t))
        x, ph = walk_x(980, lt, 70)
        stand(HIM, ctx, x, f=1, lean=0.12, step=ph, expr="tired", look=(1, 0), hands={"near": (x + 60, 600), "far": (x + 44, 610)},
              free=True)
        box(ctx, x + 64, 640, 110, 80, key="carry")
    cap(ctx, "C5")
    label(ctx, "YEAR 4")
    hud(ctx, t)


def g7(ctx, t):
    with Camera(1.55, 960, 520).apply(ctx):
        kitchen(ctx, t, warm=0.0, plates=1)
        dog(ctx, 600, FY, f=1, key="olddog", rgb=(150, 146, 140), sit=True, wag=0.1)
        sit(DAD, ctx, 860, f=1, lean=0.3, expr="sad", look=(1, 0.8), hands={"near": (960, 626), "far": (944, 632)})
    label(ctx, "YEAR 5")
    hud(ctx, t)


def g8(ctx, t):
    with Camera(lerp(1.6, 1.9, prog(t, 70.5, 76)), 1000, 560).apply(ctx):
        flat(ctx, t, sky="day", value=left_at(t))
        him_at_desk(ctx, t, "neutral" if t < 73 else "worried", look=(1, 0.8))
        P.phone_side(ctx, 1110, 636, on=0.0, key="sph2")
    label(ctx, "YEAR 6")
    hud(ctx, t)


# ---- rock bottom ---------------------------------------------------------------------------------
def r1(ctx, t):
    if t < EVENTS["dad_text"]:
        with Camera(2.4, 1060, 600).apply(ctx):
            flat(ctx, t, sky="day", value=left_at(t))
            P.phone_side(ctx, 1110, 636, on=0.0, key="sph2")
            wall_clock_text(ctx, 1200, 470, "SUN 10:01")
        hud(ctx, t)
        return
    phone_close(ctx, t, "Dad", ["i'll stop calling on sundays. i know you're busy. love you son."], EVENTS["dad_text"],
                avatar=(150, 148, 146))
    hud(ctx, t)


def r2(ctx, t):
    rise = ease(prog(t, 83.4, 84.6))
    with Camera(lerp(1.6, 1.75, prog(t, 82, 92)), 1280, 540).apply(ctx):
        rim, _ = flat(ctx, t, sky="day", value=left_at(t), desk=False)
        for tm in drops_between(82.0, 92.0):
            falling_marble(ctx, t, tm, rim, dirx=-1, dur=1.4)
        for i in range(6):  # the ones that already fell, scattered on the floor
            marble(ctx, 1180 + hrand("fl", i) * 360, FY - 9, 9, a=0.7)
        P.villain(ctx, 980, FY, scale=1.25, alpha=rise, grin=1.2, lean=0.4, reach=(1190, 600) if rise > 0.7 else None)
        hip, feet, lean = floor_sit(1220)
        HIM.draw(ctx, hip, 1, lean=lean, feet=feet, expr="hurt" if t < 88 else "closed", look=(1, -0.4), head_tilt=0.2,
                 hands=free_hands(HIM, hip, 1, lean, {"near": (hip[0] + 70, FY - 80), "far": (hip[0] + 60, FY - 76)}))
    vline(ctx, "V5", 980, 250, 56)
    cap(ctx, "C6")
    hud(ctx, t)


# ---- the turn ------------------------------------------------------------------------------------
def arm(ctx, pts, key):
    path = poly_path(wobble_points(ctx, pts, key, 0.8), closed=False, smooth=True)
    ctx.c.drawPath(path, stroke(LINE, 30))
    ctx.c.drawPath(path, stroke(SKIN, 24))


def t1(ctx, t):
    with Camera(2.5, JAR_X - 30, 400).apply(ctx):
        rim, _ = flat(ctx, t, sky="day", value=left_at(t), desk=False)
        # his far hand wraps the side of the jar, his near hand is cupped flat over the top
        arm(ctx, [(JAR_X - 330, 760), (JAR_X - 160, 560), (JAR_X - 74, 470)], "farm")
        wcircle(ctx, JAR_X - 64, 456, 22, "fhand", SKIN, LINE, 3, ry=30)
        for i in range(3):
            ctx.c.drawLine(JAR_X - 52, 432 + i * 18, JAR_X - 20, 436 + i * 18, stroke(LINE, 3))
        arm(ctx, [(JAR_X - 360, 600), (JAR_X - 180, 360), (JAR_X - 40, 316)], "narm")
        cup = skia.Rect.MakeLTRB(JAR_X - 70, 300, JAR_X + 56, 336)
        ctx.c.drawOval(cup, fill(SKIN))
        ctx.c.drawOval(cup, stroke(LINE, 3))
        for tm in EVENTS["slip"]:  # out through the gap between his fingers anyway
            falling_marble(ctx, t, tm, (JAR_X + 58, 330), dirx=1, dur=1.4)
    cap(ctx, "C7")
    hud(ctx, t)


def t2(ctx, t):
    with Camera(1.0, 960, 540).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((20, 20, 24)))
        p = poly_path([(560, 1100), (600, 720), (760, 640), (1160, 640), (1340, 700), (1380, 760), (1300, 800), (1180, 760),
                       (1240, 1100)], smooth=True)
        ctx.c.drawPath(p, fill(SKIN))
        ctx.c.drawPath(p, stroke(LINE, 5))
        cx, cy, r = 960, 600, 150
        k = ease(prog(t, 100.4, 102.4))
        ctx.c.drawCircle(cx, cy, r, fill(MARBLE))
        ctx.c.save()
        ctx.c.clipPath(skia.Path.Circle(cx, cy, r - 6), skia.ClipOp.kIntersect, True)
        # the memory inside it: a lake at dusk, a man and a small boy fishing
        ctx.c.drawRect(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + 30), fill(mix(MARBLE, (200, 170, 140), k)))
        ctx.c.drawRect(skia.Rect.MakeLTRB(cx - r, cy + 30, cx + r, cy + r), fill(mix(MARBLE, (80, 96, 120), k)))
        for (fx, s_, f) in ((cx - 30, 0.42, 1), (cx + 30, 0.28, 1)):
            ch = DAD if s_ > 0.3 else HIM
            Character(ch.name + "_m", scale=s_, extra=ch.extra).draw(ctx, (fx, cy + 30 - 66 * s_ * 1.7), f, lean=0.1, alpha=k,
                                                                   expr="smile", look=(1, 0))
            ctx.c.drawLine(fx + 20 * s_ * 2, cy - 10, fx + 120 * s_ * 2, cy - 80 * s_ * 2, stroke(LINE, 2, k))
        ctx.c.restore()
        ctx.c.drawCircle(cx, cy, r, stroke(LINE, 5))
        ctx.c.drawCircle(cx - 50, cy - 50, 26, fill((255, 255, 255), 0.7))
    cap(ctx, "C8", y=200)
    hud(ctx, t)


def t3(ctx, t):
    with Camera(2.4, 960, 560).apply(ctx):
        P.back_wall(ctx)
        P.table(ctx, 700, 640, 520, key="desk3")
        k = ease(prog(t, EVENTS["write"], EVENTS["write"] + 1.6))
        x, base = 960, 640
        jar(ctx, x, base, 0, key="jar2", w=120, h=170, name="", gold_n=0)
        wrect(ctx, x - 50, base - 136, 100, 34, "lbl2", (214, 206, 186), LINE, 2, seg=1)
        ctx.c.save()
        ctx.c.clipRect(skia.Rect.MakeXYWH(x - 50, base - 140, 100 * k, 40))
        draw_text(ctx, "WITH DAD", x, base - 112, 18, (50, 46, 44), face="LuckiestGuy-Regular.ttf")
        ctx.c.restore()
        if 0 < k < 1 or t < EVENTS["write"]:
            px = x - 50 + 100 * k
            ctx.c.drawLine(px, base - 116, px + 50, base - 40, stroke((40, 40, 46), 8))
    hud(ctx, t)


# ---- the final fight -------------------------------------------------------------------------------
EMAIL = ["URGENT", "need this by monday"]


def f1f2(ctx, t):
    rise = ease(prog(t, 115.6, 117.4))
    z = lerp(1.3, 1.55, ease(prog(t, 112, 129)))
    with Camera(z, 900, 500, shake=2 * prog(t, 124, 129)).apply(ctx):
        rim, scr = flat(ctx, t, sky="dawn", value=left_at(t), lap_text=EMAIL if t > EVENTS["email"] else None)
        P.villain(ctx, 1220, FY, scale=lerp(0.6, 1.55, rise), alpha=rise, grin=1.3, lean=-0.35,
                  reach=(980, 520) if t > 121 else None)
        ringing(ctx, t, 1080, 636, EVENTS["brunch"], EVENTS["brunch"] + 1.6, who="brunch? 11?", declined=False, key="fph")
        lean_in = ease(prog(t, 124.0, 125.0))
        hands = {"near": lerp2((830, 690), (930, 628), lean_in), "far": (820, 696)}
        x = 820
        hip, feet = standing(x, FY, 1)
        expr = "neutral" if t < EVENTS["email"] else "worried"
        if rise > 0.5:
            expr = "anxious"
        if t > EVENTS["eyes_closed"]:
            expr = "closed"
        if t > EVENTS["eyes_open"]:
            expr = "determined"
        look = (1, 0.6)
        if 118.8 < t < 121.5:
            look = (-1, -0.2)  # a glance at his coat by the door
        HIM.draw(ctx, hip, 1, lean=0.06 + 0.2 * lean_in, feet=feet, hands=free_hands(HIM, hip, 1, 0.06 + 0.2 * lean_in, hands),
                 expr=expr, look=look, screen_glow=0.6)
    vline(ctx, "V6", 1300, 260, 60)
    vline(ctx, "V7", 1300, 260, 54)
    vline(ctx, "V8", 1300, 260, 54)
    vline(ctx, "V9", 1300, 260, 54)
    vline(ctx, "V10", 1300, 260, 88)
    hud(ctx, t)


def f3(ctx, t):
    lt = t - EVENTS["slam"]
    with Camera(1.55, 900, 500, shake=16 * (1 - prog(lt, 0, 0.5))).apply(ctx):
        shut = ease(prog(lt, 0.0, 0.12))
        flat(ctx, t, sky="dawn", value=left_at(t), lap=1 - shut, coat=t < EVENTS["coat"])
        if t < EVENTS["burst"]:
            P.villain(ctx, 1220, FY, scale=1.55, alpha=1.0, grin=0.0, lean=-0.35, crack=ease(prog(lt, 0, 0.9)))
        else:
            P.villain_shards(ctx, 1220, FY, 1.55, prog(t, EVENTS["burst"], EVENTS["burst"] + 1.8))
        if t < EVENTS["coat"]:
            hip, feet = standing(820, FY, 1)
            HIM.draw(ctx, hip, 1, lean=0.26, feet=feet, hands=free_hands(HIM, hip, 1, 0.26, {"near": (930, 628), "far": (820, 696)}),
                     expr="determined", look=(1, 0.6))
        else:
            lt2 = t - EVENTS["coat"]
            x, ph = walk_x(820, lt2, -300)
            hip, feet = standing(x, FY, -1, step=ph)
            J = HIM.draw(ctx, hip, -1, lean=0.08, feet=feet, expr="determined", look=(-1, 0),
                         hands=free_hands(HIM, hip, -1, 0.08, {"near": (x - 40, 610)}))
            P.wrect(ctx, J["limbs"]["arm_near"][2][0] - 20, J["limbs"]["arm_near"][2][1], 46, 140, "coat2", (78, 70, 64), LINE, 3, seg=2)
    flash = 1 - prog(lt, 0, 0.25)
    if flash > 0:
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((255, 236, 190), 0.45 * flash))
    hud(ctx, t)


def dad_house(ctx, t, open_k=0.0):
    ctx.c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, FY), fill((96, 100, 112)))
    wrect(ctx, 600, 260, 720, 520, "house", (72, 66, 62), LINE, 4, seg=3)
    P.window(ctx, 1080, 360, 180, 150, "hw", night=False, moon=False, sky=(150, 130, 100))
    door(ctx, 760, open_k=open_k, light=open_k, key="ddoor", rgb=(110, 70, 50))
    glow(ctx, 845, 380, 120, (255, 220, 160), 0.3)
    P.floor(ctx, FY)


def f4(ctx, t):
    if t < 137.0:
        lt = t - 133.0
        with Camera(1.5, 960 + lt * 60, 540).apply(ctx):
            street(ctx, t, lamps=(500, 1500), sky=(96, 100, 112), window_rgb=(150, 140, 110))
            x, ph = walk_x(760, lt, 260)
            hip, feet = standing(x, FY, 1, step=ph)
            HIM.draw(ctx, hip, 1, lean=0.1, feet=feet, expr="determined", look=(1, 0))
        hud(ctx, t)
        return
    with Camera(1.7, 900, 520).apply(ctx):
        open_k = ease(prog(t, EVENTS["door_open"], EVENTS["door_open"] + 0.6))
        dad_house(ctx, t, open_k)
        if open_k > 0.2:
            stand(DAD, ctx, 820, f=1, lean=0.1, expr="shocked", look=(1, 0), alpha=min(1, open_k * 1.5))
        knock = EVENTS["knock"]
        rap = math.sin(math.pi * prog(t, knock, knock + 0.5)) if t < knock + 0.5 else 0
        hand = (948 - 20 * rap, 560) if t < EVENTS["door_open"] else (1000, 690)
        stand(HIM, ctx, 1040, f=-1, lean=0.04, expr="worried", look=(-1, 0), hands={"near": hand}, free=True)
        if knock <= t < knock + 0.8:
            draw_text(ctx, "knock knock", 960, 300, 34, (40, 40, 46), 1 - prog(t, knock, knock + 0.8))
    hud(ctx, t)


# ---- payoff ------------------------------------------------------------------------------------------
def p1(ctx, t):
    jump = abs(math.sin(math.pi * prog(t, EVENTS["dog_jump"], EVENTS["dog_jump"] + 0.8) * 2)) * 50
    with Camera(1.8, 920, 540).apply(ctx):
        dad_house(ctx, t, 1.0)
        hug = ease(prog(t, 146.4, 147.4))
        stand(DAD, ctx, lerp(820, 880, hug), f=1, lean=0.1, expr="happy" if t > 141.4 else "shocked", look=(1, 0),
              mouth_open=talk("dad", t), hands={"near": (lerp(870, 990, hug), 600)}, free=True)
        stand(HIM, ctx, lerp(1040, 990, hug), f=-1, lean=0.04, expr="smile" if t > 142 else "worried", look=(-1, 0),
              hands={"near": (lerp(1000, 900, hug), 600)}, free=True)
        dog(ctx, 760 + 80 * prog(t, 142.0, 143.0), FY - jump, f=1, key="olddog", rgb=(150, 146, 140), wag=1.5)
        speech(ctx, t, "dad", 820, 420)
    hud(ctx, t)


def p2(ctx, t):
    out = ease(prog(t, EVENTS["plate_out"], EVENTS["plate_out"] + 1.0))
    with Camera(1.5, 980, 520).apply(ctx):
        kitchen(ctx, t, warm=ease(prog(t, 150.0, 152.0)), plates=1, cup_open=1.0 if 150.6 < t < 152.6 else 0.0,
                plate_held=None)
        if out > 0:
            P.wrect(ctx, *lerp2((660, 360), (1015, 628), out), 90, 10, "plate2", (220, 218, 210), LINE, 3, seg=2)
        dog(ctx, 600, FY, f=1, key="olddog", rgb=(150, 146, 140), sit=True, wag=1.2)
        laugh = 0.5 + 0.5 * math.sin(t * 9)
        lk = t > 153.0
        JD = stand(DAD, ctx, lerp(760, 1290, ease(prog(t, 152.4, 153.4))), f=1 if t < 152.4 else 1, lean=0.1,
                   expr="happy", look=(1, 0), mouth_open=talk("dad", t) or (0.5 * laugh if lk else 0),
                   hands={"near": lerp2((700, 380), (1060, 630), out) if t < 152.4 else (1360, 586)}, free=True)
        JH = stand(HIM, ctx, 1180, f=1, lean=0.08, expr="happy", look=(1, 0), mouth_open=talk("him", t) or (0.5 * laugh if lk else 0),
                   hands={"near": (1330, 590)}, free=True)
        speech(ctx, t, "dad", JD["head"][0], JD["head"][1] - 70)
        speech(ctx, t, "him", JH["head"][0] - 40, JH["head"][1] - 70)
    hud(ctx, t)


def p3(ctx, t):
    gd = EVENTS["gold_drop"]
    with Camera(2.2, JAR_X + 60, 450).apply(ctx):
        n_in = 1 if t > gd + 1.3 else 0
        rim, _ = flat(ctx, t, sky="night", value=left_at(t), desk=False, jar2=n_in if n_in else 0, lamp=0.6)
        if n_in == 0:
            jar(ctx, JAR_X + 130, SHELF[1], 0, key="jar2", w=90, h=130, name="WITH DAD", gold_n=0, r=8)
        falling_marble(ctx, t, gd, rim, gold=True, land=(JAR_X + 130, SHELF[1] - 16), dur=1.3)
    cap(ctx, "C9")
    hud(ctx, t)
    hud_dad(ctx, t)


# ---- mirror and title ----------------------------------------------------------------------------------
def x1(ctx, t):
    with Camera(1.5, 1100, 540).apply(ctx):
        office(ctx, desk_x=560)
        P.table(ctx, 1150, 640, 300, key="mdesk")
        P.chair(ctx, 1360, 690, -1, key="xc2")
        answered = t > EVENTS["maya_answer"]
        ph = (1200, 632)
        if not answered:
            ringing(ctx, t, *ph, EVENTS["maya_ring"], EVENTS["maya_answer"], who="Mum", declined=False, key="mph")
        hold = (1290, 520)
        JM = sit(MAYA, ctx, 1360, f=-1, lean=0.14 if not answered else 0.04, expr="tired" if t < 166.2 else ("hopeful" if not answered else "happy"),
                 look=(-1, 0.6) if t < 166.6 else (-1, 0), mouth_open=talk("maya", t),
                 hands=free_hands(MAYA, seated(1360, 690, -1)[0], -1, 0.14, {"near": (1230, 628) if not answered else hold, "far": (1280, 636)}))
        if answered:
            P.phone_held(ctx, *JM["limbs"]["arm_near"][2], facing=-1, on=1.0)
        set_k = ease(prog(t, EVENTS["marble_set"] - 0.6, EVENTS["marble_set"]))
        x = lerp(820, 1060, ease(prog(t, 163.0, 164.8)))
        stand(HIM, ctx, x, f=1, lean=0.1 + 0.2 * set_k * (t < 166.4), expr="smile", look=(1, 0.6),
              step=(t * 1.6) % 1 if t < 164.8 else 0.0, hands={"near": (1140, 626) if 164.8 < t < 166.4 else (x + 30, 690)}, free=True)
        if t > EVENTS["marble_set"]:
            marble(ctx, 1150, 621, 10, gold=True)
        speech(ctx, t, "maya", JM["head"][0], JM["head"][1] - 70)


def title(ctx, t):
    a = fade(t, EVENTS["title"], DURATION, 0.8, 1.2)
    draw_text(ctx, "LATER.", W / 2, 520, 220, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 300 + 600 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=46)
    cap(ctx, "T2", y=760, size=64, rgb=GOLD, glow_rgb=(170, 110, 20))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5, "M1": m1, "H6": h6, "S04": s04,
    "D1": d1, "D2": d2, "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6, "G7": g7, "G8": g8,
    "R1": r1, "R2": r2, "T1": t1, "T2": t2, "T3": t3, "F1": f1f2, "F2": f1f2, "F3": f3, "F4": f4,
    "P1": p1, "P2": p2, "P3": p3, "X1": x1, "TT": title,
}
CONTINUOUS = {"S01", "H1", "F2"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "TT":
        black(ctx, prog(t, DURATION - 1.0, DURATION))
