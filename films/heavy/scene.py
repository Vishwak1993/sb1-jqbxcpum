"""HEAVY.: picture. scene(ctx) draws any frame of the film.

The device: every slight becomes a red stone with a name on it, dropped into the sack on his back. CARRYING
counts the kilograms; he bends lower and walks slower as it fills. On the hill he sets the stones down one by
one; set down, a stone turns grey. The last and heaviest is Kai's.
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
from studio.extras import speech as _speech, talk as _talk, free_hands, floor_sit, door, office, street, phone_close  # noqa: E402
from timeline import (SCENES, CAPS, CUES, BUBBLES, EVENTS, STONES, DROPS, KAI_DOWN, DURATION, scene_at, carried,  # noqa: E402
                      kg_at, kg_changed)
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
STONE = (196, 58, 52)
STONE_D = (120, 30, 30)
GREYSTONE = (128, 126, 122)
SACK = (124, 104, 80)
CAP = (60, 150, 150)


# ---- cast ----------------------------------------------------------------------------------
def kai_cap(ctx, hx, hy, f, s):
    p = poly_path([(hx - 50 * s, hy - 16 * s), (hx - 44 * s, hy - 48 * s), (hx, hy - 58 * s), (hx + 44 * s, hy - 48 * s),
                   (hx + 50 * s, hy - 16 * s)], smooth=True)
    ctx.c.drawPath(p, fill(CAP))
    ctx.c.drawPath(p, stroke(LINE, 3 * s))
    ctx.c.drawPath(poly_path([(hx + f * 30 * s, hy - 20 * s), (hx + f * 74 * s, hy - 16 * s), (hx + f * 70 * s, hy - 8 * s),
                              (hx + f * 30 * s, hy - 12 * s)], smooth=True), fill(mix(CAP, (0, 0, 0), 0.25)))


def tie(ctx, J, s=1.0):
    sx, sy = J["shoulder"]
    f = J["facing"]
    x = sx + f * 10 * s
    p = poly_path([(x - 6 * s, sy + 2 * s), (x + 6 * s, sy + 2 * s), (x + 9 * s, sy + 62 * s), (x, sy + 74 * s), (x - 9 * s, sy + 62 * s)])
    ctx.c.drawPath(p, fill((60, 74, 110)))
    ctx.c.drawPath(p, stroke(LINE, 2.5 * s))


HIM = Character("him")
KAI = Character("kai", extra=kai_cap)
KID = Character("kid", scale=0.7)
KID2 = Character("kid2", scale=0.72, skin=(190, 186, 176))


def grey(name, scale=1.0):
    return Character(name, skin=(150, 150, 156), scale=scale)


# ---- shared helpers -------------------------------------------------------------------------
def cap(ctx, k, y=190, size=50, rgb=TEXT, glow_rgb=None):
    t0, t1 = CAPS[k]
    caption(ctx, CAPTIONS[k], t0, t1, y=y, size=size, rgb=rgb, glow_rgb=glow_rgb)


def vline(ctx, k, x, y, size=50):
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
    kg = kg_at(t)
    gold = t >= KAI_DOWN
    rgb = GOLD if gold else TEXT
    P.hud(ctx, f"{kg} kg", label="CARRYING", a=a, rgb=rgb, pop=pop_at(t, kg_changed(t)))


def lean_for(kg):
    return 0.05 + min(0.5, kg / 110)


def sack_r(kg):
    return 0 if kg <= 0 else 30 + 8.5 * math.sqrt(kg)


# ---- the device: stones and the sack ----------------------------------------------------------
def stone(ctx, x, y, r, lab="", rgb=STONE, a=1.0, glow_a=1.0, key="st"):
    """A rough rock. Red ones glow faintly; grey ones are set down and dead."""
    if a <= 0:
        return
    pts = [(x + math.cos(i * 2 * math.pi / 9) * r * (0.82 + 0.3 * hrand(key, i)),
            y + math.sin(i * 2 * math.pi / 9) * r * 0.78 * (0.85 + 0.3 * hrand(key, i, 1))) for i in range(9)]
    p = poly_path(pts, smooth=True)
    if glow_a > 0 and rgb != GREYSTONE:
        ctx.c.drawPath(p, blurred(fill(RED, 0.5 * a * glow_a), r * 0.4))
    ctx.c.drawPath(p, fill(rgb, a))
    ctx.c.drawPath(p, stroke(LINE, max(2, r * 0.08), a))
    ctx.c.drawPath(poly_path([(x - r * 0.4, y - r * 0.3), (x - r * 0.1, y - r * 0.45)], closed=False), stroke((255, 255, 255), max(1.5, r * 0.06), 0.35 * a))
    if lab:
        draw_text(ctx, lab, x, y + r * 0.18, max(12, r * 0.42), (250, 240, 230) if rgb != GREYSTONE else (60, 58, 56), a,
                  face="LuckiestGuy-Regular.ttf")


def sack_geo(J, kg, s=1.0):
    f = J["facing"]
    sx, sy = J["shoulder"]
    r = sack_r(kg) * s
    cx, cy = sx - f * (r * 0.75 + 14 * s), sy + r * 0.55
    return cx, cy, r


def draw_sack(ctx, J, t, kg=None, s=1.0, labels=None, new_t=None):
    """The sack on his back, drawn behind him. Returns the opening point."""
    kg = kg_at(t) if kg is None else kg
    if kg <= 0:
        return None
    cx, cy, r = sack_geo(J, kg, s)
    c = ctx.c
    labels = carried(t) if labels is None else labels
    # the top stones peek out of the opening
    for i, (lab, w) in enumerate(labels[:3]):
        sr = (16 + 3.2 * w) * s
        ox = cx + (i - 1) * r * 0.42
        oy = cy - r * 0.82 - sr * 0.3 + (i % 2) * 8 * s
        stone(ctx, ox, oy, sr, lab if sr > 26 * s else "", key=("top", lab))
    body = poly_path([(cx - r * 0.82, cy - r * 0.7), (cx - r * 1.02, cy + r * 0.2), (cx - r * 0.7, cy + r * 0.95),
                      (cx + r * 0.7, cy + r * 0.95), (cx + r * 1.02, cy + r * 0.2), (cx + r * 0.82, cy - r * 0.7)], smooth=True)
    c.drawPath(body, fill(SACK))
    c.drawPath(body, stroke(LINE, 3.5 * s))
    for i in range(3):  # rough stitching
        c.drawLine(cx - r * 0.5 + i * r * 0.5, cy + r * 0.4, cx - r * 0.4 + i * r * 0.5, cy + r * 0.6, stroke(mix(SACK, LINE, 0.5), 2.5 * s))
    c.drawLine(cx - r * 0.85, cy - r * 0.62, cx + r * 0.85, cy - r * 0.62, stroke(mix(SACK, LINE, 0.4), 6 * s))
    glow(ctx, cx, cy - r * 0.7, r * 1.2, RED, 0.12)
    return (cx, cy - r * 0.8)


def strap(ctx, J, kg, s=1.0):
    if kg <= 0:
        return
    cx, cy, r = sack_geo(J, kg, s)
    sx, sy = J["shoulder"]
    f = J["facing"]
    ctx.c.drawPath(poly_path([(cx - f * r * 0.2, cy - r * 0.6), (sx + f * 8 * s, sy - 4 * s), (sx + f * 12 * s, sy + 60 * s),
                              (cx + f * r * 0.3, cy + r * 0.3)], closed=False, smooth=True), stroke(mix(SACK, LINE, 0.5), 9 * s))


def drop_in(ctx, t, opening, s=1.0):
    """The newest stone falling into the sack."""
    if opening is None:
        return
    for tm, lab, w in STONES:
        k = (t - (tm - 0.45)) / 0.45
        if 0 <= k <= 1:
            sr = (16 + 3.2 * w) * s
            x = opening[0]
            y = lerp(opening[1] - 420 * s, opening[1], k * k)
            stone(ctx, x, y, sr, lab, key=("drop", lab), a=1.0)


def carrier(ctx, t, hip, f, kg=None, feet=None, s=1.0, ch=None, labels=None, extra_lean=0.0, **kw):
    """Him with the sack: sack behind, him, strap in front. Returns his joints."""
    ch = ch or HIM
    kg = kg_at(t) if kg is None else kg
    lean = kw.pop("lean", lean_for(kg)) + extra_lean
    J0 = ch.joints(hip, f, lean, kw.get("head_tilt", 0.0))
    op = draw_sack(ctx, J0, t, kg, s, labels)
    if "hands" in kw and kw["hands"]:
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"], kw.get("head_tilt", 0.0))
    J = ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)
    strap(ctx, J, kg, s)
    drop_in(ctx, t, op, s)
    return J


def walk_carry(ctx, t, x, f=1, step=0.0, **kw):
    hip, feet = standing(x, FY, f, step=step)
    return carrier(ctx, t, hip, f, feet=feet, **kw)


# ---- the hill ---------------------------------------------------------------------------------
HILL_X0, HILL_X1, SLOPE = 620, 1560, 0.42
CREST_Y = FY - (HILL_X1 - HILL_X0) * SLOPE


def ground(x):
    if x <= HILL_X0:
        return FY
    if x >= HILL_X1:
        return CREST_Y
    return FY - (x - HILL_X0) * SLOPE


def hill(ctx, t, dawn=0.0):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, -400), (0, FY)], [col(mix((22, 26, 42), (120, 100, 150), dawn)),
                                                                 col(mix((40, 40, 58), (250, 170, 110), dawn))])
    c.drawRect(skia.Rect.MakeLTRB(-1200, -800, W + 1200, FY + 400), skia.Paint(Shader=sky))
    if dawn > 0:
        glow(ctx, HILL_X1 + 260, CREST_Y - 20, 700, GOLD, 0.55 * dawn)
        c.drawCircle(HILL_X1 + 260, CREST_Y + 40 - 120 * dawn, 90, fill((255, 214, 130), dawn))
    for i in range(18):
        if dawn < 0.8:
            c.drawCircle(-300 + hrand("hs", i) * 2600, -200 + hrand("hy", i) * 500, 1.8, fill(TEXT, 0.5 * (1 - dawn)))
    p = poly_path([(-1200, FY), (HILL_X0, FY), (HILL_X1, CREST_Y), (W + 1400, CREST_Y), (W + 1400, FY + 600), (-1200, FY + 600)])
    c.drawPath(p, fill(mix((30, 34, 30), (70, 80, 56), dawn)))
    c.drawPath(poly_path([(-1200, FY), (HILL_X0, FY), (HILL_X1, CREST_Y), (W + 1400, CREST_Y)], closed=False), stroke(mix(GREY, (110, 120, 80), dawn), 4))
    for i in range(10):  # tufts of grass
        gx = -200 + i * 230
        gy = ground(gx)
        for k in (-1, 0, 1):
            c.drawLine(gx + k * 8, gy, gx + k * 14, gy - 18, stroke(mix(GREY_D, (90, 110, 60), dawn), 3))
    # the boulder by the path, where he sets Kai's stone down
    wcircle(ctx, BOULDER[0], BOULDER[1], 70, "boulder", mix((70, 70, 74), (110, 104, 96), dawn), LINE, 4, ry=46)


BOULDER = (430, FY - 44)


def stand_on(ch, ctx, x, f=1, step=0.0, s=1.0, **kw):
    """Standing on the hill: each foot on the ground under it."""
    hip, feet = standing(x, FY, f, s, step=step)
    gy = ground(x)
    hip = (hip[0], hip[1] - (FY - gy) + (6 * s if HILL_X0 - 40 < x < HILL_X1 + 40 else 0))
    feet = {k: (v[0], v[1] - (FY - ground(v[0]))) for k, v in feet.items()}
    return hip, feet


def friends_at_top(ctx, t, dawn=0.0, kai_laugh=True, s=0.75, kai_x=1640):
    for i, (x, f) in enumerate(((kai_x + 130, -1), (kai_x + 250, -1))):
        hip, feet = stand_on(grey(f"fr{i}", s), ctx, x, f, s=s)
        grey(f"fr{i}", s).draw(ctx, hip, f, lean=0.04, feet=feet, expr="happy", mouth_open=0.4 * abs(math.sin(t * 8 + i)))
    kai = Character("kai_s", extra=kai_cap, scale=s)
    hip, feet = stand_on(kai, ctx, kai_x, 1, s=s)
    return kai.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="happy", look=(1, 0),
                    mouth_open=0.5 * abs(math.sin(t * 9)) if kai_laugh else 0)


# ---- the hook -----------------------------------------------------------------------------------
def s01(ctx, t):
    cap(ctx, "C1", y=H / 2 + 16, size=60)


def h1(ctx, t):
    with Camera(1.4, 1080, 520).apply(ctx):
        office(ctx, desk_x=400)
        wrect(ctx, 1080, 260, 360, 220, "board", (220, 222, 226), LINE, 4, seg=2)
        for i, hgt in enumerate((60, 100, 140)):
            ctx.c.drawRect(skia.Rect.MakeXYWH(1140 + i * 80, 440 - hgt, 50, hgt), fill((90, 140, 200)))
        draw_text(ctx, "OUR PROJECT", 1260, 300, 28, (40, 40, 46), face="LuckiestGuy-Regular.ttf")
        JK = stand(KAI, ctx, 1020, f=1, lean=0.04, expr="happy", look=(1, 0), hands={"near": (1110, 380)}, free=True)
        JB = stand(grey("boss"), ctx, 1560, f=-1, lean=0.06, expr="happy", look=(-1, 0), mouth_open=talk("boss", t))
        tie(ctx, JB)
        P.chair(ctx, 640, 690, 1, key="h1c")
        hip, feet = seated(640, 690, 1)
        carrier(ctx, t, hip, 1, feet=feet, lean=0.18, expr="neutral" if t < 4.4 else "hurt", look=(1, -0.2),
                hands={"near": (720, 632), "far": (706, 636)})
        speech(ctx, t, "boss", JB["head"][0] - 30, JB["head"][1] - 70)
    hud(ctx, t)


def stand(ch, ctx, x, f=1, lean=0.04, step=0.0, free=False, **kw):
    hip, feet = standing(x, FY, f, ch.scale, step=step)
    if free and kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def h2(ctx, t):
    with Camera(1.8, 1000, 560).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeLTRB(-600, 0, W + 600, FY), fill((44, 38, 34)))
        wrect(ctx, 1080, 600, 560, 180, "counter", (90, 70, 56), LINE, 4, seg=3)
        for i in range(3):
            P.wrect(ctx, 1150 + i * 140, 330, 100, 40, ("menu", i), (200, 196, 186), LINE, 2, seg=1)
        P.floor(ctx, FY, rgb=(80, 70, 60))
        JB = stand(grey("barista"), ctx, 1300, f=-1, lean=0.08, expr="smile", look=(-1, 0), hands={"near": (1150, 590)}, free=True,
                   mouth_open=talk("barista", t))
        cup = JB["limbs"]["arm_near"][2]
        P.wrect(ctx, cup[0] - 14, cup[1] - 30, 28, 34, "cup", (230, 226, 216), LINE, 3, seg=2)
        draw_text(ctx, "TEA", cup[0], cup[1] - 6, 14, (60, 56, 52), face="LuckiestGuy-Regular.ttf")
        walk_carry(ctx, t, 900, 1, expr="neutral" if t < 7.6 else "hurt", look=(1, 0.4), hands={"near": (1000, 600)})
        speech(ctx, t, "barista", JB["head"][0], JB["head"][1] - 70)
    hud(ctx, t)


def h3(ctx, t):
    sp = EVENTS["splash"]
    with Camera(1.7, 960, 560).apply(ctx):
        street(ctx, t)
        cx = lerp(-300, 2200, prog(t, sp - 0.5, sp + 0.5))
        wrect(ctx, cx - 160, FY - 110, 320, 80, "car", (90, 110, 140), LINE, 4, seg=2)
        wrect(ctx, cx - 100, FY - 160, 200, 60, "carroof", (90, 110, 140), LINE, 4, seg=2)
        for wx in (cx - 100, cx + 100):
            wcircle(ctx, wx, FY - 26, 26, ("wheel", wx > cx), (30, 30, 34), LINE, 3)
        ctx.c.drawOval(skia.Rect.MakeLTRB(860, FY - 6, 1100, FY + 8), fill((60, 70, 90)))
        k = prog(t, sp, sp + 0.7)
        if 0 < k < 1:
            for i in range(24):
                a = math.pi + hrand("spl", i) * math.pi
                d = 60 + 260 * k * (0.5 + hrand("spd", i))
                ctx.c.drawCircle(980 + math.cos(a) * d * 0.5, FY - 10 + math.sin(a) * d * 0.8 + 300 * k * k, 6, fill((120, 140, 180), 1 - k))
        J = walk_carry(ctx, t, 980, -1, expr="neutral" if t < sp else "shocked", look=(1, 0.2) if t < sp else (0, 0))
        if t > sp + 0.2:
            for i in range(6):
                ctx.c.drawCircle(J["hip"][0] - 30 + i * 12, J["hip"][1] - 60 + (i % 3) * 30, 5, fill((120, 140, 180), 0.8))
    hud(ctx, t)


def h4(ctx, t):
    if t < 12.9:
        phone_close(ctx, t, "Dad", ["still in that job?"], EVENTS["dad_text"], avatar=(150, 148, 146))
        hud(ctx, t)
        return
    with Camera(1.9, 900, 560).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        P.window(ctx, 1300, 220, 220, 220, "h4w", night=True)
        hip, feet = standing(900, FY, 1)
        J = carrier(ctx, t, hip, 1, feet=feet, expr="hurt", look=(1, 1),
                    hands={"near": (980, 640), "far": (964, 646)})
        P.phone_held(ctx, *J["limbs"]["arm_near"][2], on=1.0)
    hud(ctx, t)


FLURRY = [(14.4, "BUS", (34, 36, 44)), (15.0, "MIA", (40, 34, 34)), (15.6, "GROUP CHAT", (30, 38, 40)), (16.2, "NEIGHBOUR", (38, 36, 30))]


def h5(ctx, t):
    i = min(3, int((t - 14.4) / 0.65))
    t0, lab, bg = FLURRY[i]
    ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill(bg))
    side = i % 2 * 2 - 1
    x = 960 - side * 120
    with Camera(2.2, x, 520).apply(ctx):
        stagger = math.sin(math.pi * prog(t, t0 + 0.2, t0 + 0.55)) * 0.12
        walk_carry(ctx, t, x, side, expr="hurt", look=(0.5 * side, 0.4), extra_lean=stagger)
    hud(ctx, t)


# ---- the wound and the stakes ---------------------------------------------------------------------
def bedroom(ctx, night=True):
    P.back_wall(ctx)
    P.floor(ctx, FY)
    P.window(ctx, 1560, 200, 220, 220, "bwin", night=night)
    P.bed(ctx, 1100, FY, 560)
    P.wrect(ctx, 980, FY - 110, 100, 110, "nstand", GREY_D, LINE, 3, seg=2)


def in_bed(ctx, expr="closed", look=(0, -1)):
    hip = (1330, FY - 132)
    HIM.draw(ctx, hip, -1, lean=math.pi / 2, feet={"near": (hip[0] + 114, FY - 126), "far": (hip[0] + 112, FY - 128)},
             expr=expr, look=look, hands={"near": (hip[0] - 20, FY - 104), "far": (hip[0] - 10, FY - 106)},
             bend={"leg_near": 1, "leg_far": 1, "arm_near": 1, "arm_far": 1})
    P.wrect(ctx, 1250, FY - 136, 300, 46, "duvet", (60, 64, 92), LINE, 3, seg=3)


def sack_on_floor(ctx, t, x, kg=None, glow_k=1.0):
    kg = kg_at(t) if kg is None else kg
    r = sack_r(kg)
    fake = {"facing": 1, "shoulder": (x + r * 0.75 + 14, FY - r * 0.55 - r * 0.95)}
    op = draw_sack(ctx, fake, t, kg)
    glow(ctx, x, FY - r * 1.5, r * 2, RED, 0.18 * glow_k)
    return op


def s02(ctx, t):
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0 + 0.6, t1))
    with Camera(lerp(1.5, 1.7, prog(t, 17, 26)), 1060, 520).apply(ctx):
        bedroom(ctx, True)
        op = sack_on_floor(ctx, t, 760)
        for i in range(8):
            k = (t * 0.6 + hrand("wisp", i)) % 1.0
            a = (1 - k) * prog(t, t0, t0 + 0.5) * (1 - prog(t, t1, t1 + 0.8))
            ctx.c.drawCircle(op[0] + (hrand("wx", i) - 0.5) * 80 + k * 40, op[1] - k * 300, 10 + 16 * k, blurred(fill(RED, 0.35 * a), 8))
        P.villain(ctx, 820, FY, scale=lerp(0.3, 1.05, born), alpha=born, grin=ease(prog(t, 20.2, 21.0)), lean=0.2)
        in_bed(ctx, "worried" if t < 22 else "hurt", look=(-1, -0.4))
    vline(ctx, "V1", 1240, 300, 58)
    vline(ctx, "V2", 1240, 380, 52)
    hud(ctx, t)


def s03(ctx, t):
    cap(ctx, "C2", y=H / 2 + 16, size=56)


def b1(ctx, t):
    if t < 33.8:
        phone_close(ctx, t, "Kai", ["drinks friday? miss you man"], EVENTS["kai_text"], avatar=CAP)
        if t > 31.2:
            draw_text(ctx, "Read 21:04", W / 2 + 230, 700, 26, (160, 162, 172), ease(prog(t, 31.2, 31.5)), align="right")
        vline(ctx, "V3", W / 2 + 520, 420, 54)
    else:
        phone_close(ctx, t, "the old crew", ["sunrise hike sat!", "5am, the old hill"], [EVENTS["hike_text"], EVENTS["hike_text"] + 0.6],
                    avatar=(120, 160, 120))
    hud(ctx, t)


# ---- the grind ------------------------------------------------------------------------------------
def g1(ctx, t):
    lt = t - 37.0
    with Camera(1.6, 1000, 560).apply(ctx):
        street(ctx, t, lamps=(500, 1500))
        x, ph = walk_x(820, lt, 70)
        walk_carry(ctx, t, x, 1, step=ph, expr="tired", look=(1, 0.8))
    cap(ctx, "C3")
    label(ctx, "WEEK 1")
    hud(ctx, t)


def g2(ctx, t):
    with Camera(1.5, 960, 560).apply(ctx):
        office(ctx, desk_x=360)
        P.table(ctx, 1080, 640, 460, key="team")
        for i, (x, f) in enumerate(((1100, 1), (1460, -1))):
            P.chair(ctx, x, 690, f, key=("tc", i))
        laugh = 0.5 + 0.5 * math.sin(t * 8)
        hip, feet = seated(1100, 690, 1)
        grey("t1").draw(ctx, hip, 1, lean=0.1, feet=feet, expr="happy", mouth_open=0.5 * laugh,
                        hands=free_hands(grey("t1"), hip, 1, 0.1, {"near": (1200, 630), "far": (1186, 636)}))
        hip, feet = seated(1460, 690, -1)
        KAI.draw(ctx, hip, -1, lean=0.1, feet=feet, expr="happy", mouth_open=0.5 * (1 - laugh),
                 hands=free_hands(KAI, hip, -1, 0.1, {"near": (1350, 630), "far": (1366, 636)}))
        P.chair(ctx, 600, 690, 1, key="g2c")
        hip, feet = seated(600, 690, 1)
        carrier(ctx, t, hip, 1, feet=feet, lean=0.3, expr="sad", look=(1, 0.8), hands={"near": (700, 632), "far": (684, 636)})
        P.wrect(ctx, 680, 626, 60, 14, "lunch", (200, 160, 110), LINE, 2, seg=1)
    cap(ctx, "C4")
    label(ctx, "WEEK 2")
    hud(ctx, t)


def g3(ctx, t):
    with Camera(1.7, 900, 560).apply(ctx):
        office(ctx, desk_x=440)
        P.chair(ctx, 640, 690, 1, key="g3c")
        hip, feet = seated(640, 690, 1)
        snap = t > EVENTS["snap"]
        J = carrier(ctx, t, hip, 1, feet=feet, lean=0.24, expr="determined" if snap else "tired", look=(1, 0) if snap else (1, 0.8),
                    mouth_open=talk("him", t), hands={"near": (740, 632), "far": (724, 636)})
        JS = stand(grey("sue"), ctx, 1000, f=-1, lean=0.04, expr="happy" if not snap else "shocked", look=(-1, 0.2),
                   mouth_open=talk("sue", t))
        speech(ctx, t, "sue", JS["head"][0], JS["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 30, J["head"][1] - 70)
    vline(ctx, "V4", 1300, 300, 52)
    label(ctx, "WEEK 3")
    hud(ctx, t)


def g4(ctx, t):
    with Camera(1.0, 960, 540).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((40, 46, 54)))
        for r in range(8):
            for cidx in range(14):
                ctx.c.drawRect(skia.Rect.MakeXYWH(cidx * 140, r * 140, 136, 136), stroke((56, 64, 74), 3))
        sh = Character("shower", scale=2.4)
        sh.draw(ctx, (760, 1120), 1, lean=0.05, expr="sad", look=(1, 0.6), head_tilt=0.15)
        # the sack on its hook, glowing through the steam
        hook = (1400, 300)
        wline(ctx, (hook[0], 250), hook, "hook", GREY_L, 6, seg=1)
        fake = {"facing": 1, "shoulder": (hook[0] + 90, hook[1] - 20)}
        draw_sack(ctx, fake, t)
        glow(ctx, 1370, 360, 360, RED, 0.25 + 0.08 * math.sin(t * 3))
        for i in range(10):
            k = (t * 0.15 + hrand("steam", i)) % 1
            ctx.c.drawCircle(200 + hrand("sx", i) * 1500, 900 - k * 900, 80 + 60 * hrand("sr", i), blurred(fill((220, 226, 232), 0.12 * (1 - k)), 40))
    label(ctx, "WEEK 4")
    hud(ctx, t)


def g5(ctx, t):
    with Camera(1.8, 1240, 580).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        P.window(ctx, 1560, 200, 220, 220, "sw", night=True)
        wrect(ctx, 1040, 690, 440, 90, "sofa", (64, 66, 86), LINE, 3, seg=3)
        wrect(ctx, 1020, 600, 40, 180, "sofaarm", (64, 66, 86), LINE, 3, seg=2)
        kg = kg_at(t)
        r = sack_r(kg)
        fake = {"facing": 1, "shoulder": (1250 + r * 0.75 + 14, 690 - r * 0.55 - r * 0.95)}
        draw_sack(ctx, fake, t)
        hip, feet, lean = floor_sit(1500, -1)
        HIM.draw(ctx, hip, -1, lean=0.05, feet=feet, expr="tired", look=(-1, -0.4),
                 hands=free_hands(HIM, hip, -1, 0.05, {"near": (1440, FY - 30), "far": (1450, FY - 28)}))
    vline(ctx, "V5", 900, 330, 56)
    label(ctx, "WEEK 5")
    hud(ctx, t)


def g6(ctx, t):
    with Camera(1.0, 960, 540).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((30, 32, 36)))
        wrect(ctx, 560, 160, 800, 760, "mirror", (60, 66, 74), (140, 140, 150), 10, seg=3)
        ctx.c.save()
        ctx.c.clipRect(skia.Rect.MakeXYWH(560, 160, 800, 760))
        me = Character("mirror_him", skin=(200, 196, 186), scale=2.3)
        hip = (1000, 1010)
        kg = kg_at(t)
        carrier(ctx, t, hip, 1, kg=kg, s=2.3, ch=me, lean=lean_for(kg) + 0.1, expr="tired", look=(0.6, 0.6))
        ctx.c.restore()
    cap(ctx, "C5", y=985)
    label(ctx, "WEEK 6")
    hud(ctx, t)


# ---- rock bottom: the hill --------------------------------------------------------------------------
def climber(ctx, t):
    """R1: he climbs, the sack drags him back, he slides down and sits."""
    slip = EVENTS["slip"]
    if t < slip:
        lt = t - 61.6
        x = 520 + max(0, lt) * 52
        hip, feet = stand_on(HIM, ctx, x, 1, step=(lt * 1.2) % 1 if lt > 0 else 0)
        return carrier(ctx, t, hip, 1, feet=feet, expr="worried", look=(1, -0.6), extra_lean=0.12)
    k = ease(prog(t, slip, slip + 1.2))
    x0 = 520 + (slip - 61.6) * 52
    x = lerp(x0, 560, k)
    if k < 0.7:
        hip, feet = stand_on(HIM, ctx, x, 1)
        return carrier(ctx, t, hip, 1, feet=feet, expr="shocked", look=(0, -1), lean=-0.2)
    hip, feet, lean = floor_sit(560)
    return carrier(ctx, t, hip, 1, feet=feet, lean=-0.1, expr="hurt", look=(1, -0.8),
                   hands={"near": (hip[0] + 60, FY - 6), "far": (hip[0] - 50, FY - 4)})


def r1(ctx, t):
    with Camera(lerp(0.85, 1.0, prog(t, 61, 70)), 1000, 480).apply(ctx):
        hill(ctx, t, 0.0)
        draw_text(ctx, "SAT 5:00", 260, 200, 40, (200, 200, 206), face="LuckiestGuy-Regular.ttf")
        friends_at_top(ctx, t, 0.0)
        climber(ctx, t)
    vline(ctx, "V6", 900, 260, 56)
    hud(ctx, t)


def r2(ctx, t):
    with Camera(2.0, 600, 640).apply(ctx):
        hill(ctx, t, 0.05)
        hip, feet, lean = floor_sit(560)
        carrier(ctx, t, hip, 1, feet=feet, lean=-0.1, expr="hurt" if t < 72 else "closed", look=(1, 0.6), head_tilt=0.2,
                hands={"near": (hip[0] + 60, FY - 6), "far": (hip[0] - 50, FY - 4)})
    cap(ctx, "C6")
    hud(ctx, t)


# ---- the turn -------------------------------------------------------------------------------------------
def t1(ctx, t):
    up = ease(prog(t, 76.4, 79.4))
    with Camera(lerp(2.0, 2.2, up), lerp(600, 1740, up), lerp(640, CREST_Y - 120, up)).apply(ctx):
        hill(ctx, t, 0.1)
        JK = friends_at_top(ctx, t, 0.1, kai_x=1620, s=0.75)
        hip, feet, lean = floor_sit(560)
        carrier(ctx, t, hip, 1, feet=feet, lean=-0.18, expr="shocked", look=(1, -1.2),
                hands={"near": (hip[0] + 60, FY - 6), "far": (hip[0] - 50, FY - 4)})
    cap(ctx, "C7", y=930)
    cap(ctx, "C8", y=995)
    hud(ctx, t)


def t2(ctx, t):
    c = ctx.c
    k = ease(prog(t, 84.2, 85.6))
    tilt = 0.32 * k
    px, py = W / 2, 720
    c.drawPath(poly_path([(px - 40, py + 80), (px + 40, py + 80), (px, py)]), fill(GREY_L))
    L = 560
    lx, ly = px - math.cos(tilt) * L, py - math.sin(tilt) * L
    rx, ry = px + math.cos(tilt) * L, py + math.sin(tilt) * L
    wline(ctx, (lx, ly), (rx, ry), "plank", (150, 120, 90), 22, seg=2)
    # left end: Kai, light, floating up
    kai = Character("kai_t2", extra=kai_cap, scale=0.9)
    hip, feet = standing(lx + 40, ly - 6, 1, 0.9)
    kai.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="happy", look=(1, -0.2))
    # right end: him, pinned under the stones
    hip, feet, _ = floor_sit(rx - 120, 1)
    hip = (hip[0], ry - 26)
    feet = {"near": (rx - 30, ry - 8), "far": (rx - 36, ry - 8)}
    HIM.draw(ctx, hip, 1, lean=0.5, feet=feet, expr="hurt", look=(0, 0.6), head_tilt=0.2)
    for i, (lab, w) in enumerate(carried(83.0)[:6]):
        sr = 20 + 3.2 * w
        stone(ctx, rx - 210 + (i % 3) * 70, ry - 160 - (i // 3) * 60, sr, lab if sr > 26 else "", key=("t2", lab))
    cap(ctx, "C9", y=210)
    cap(ctx, "C10", y=280)
    hud(ctx, t)


def path_stones(ctx, t, upto=None, s=1.0):
    """Stones he has set down beside him on the path, grey."""
    n = 0
    for i, (tm, lab) in enumerate(DROPS):
        if t >= tm + 0.5 and tm < (upto or 999):
            w = dict((l, k) for _, l, k in STONES)[lab]
            sr = (14 + 2.6 * w) * s
            x = 700 + (n % 7) * 64 - (n // 7) * 24
            stone(ctx, x, FY - sr * 0.7 - (n // 7) * 24, sr, lab if sr > 22 else "", GREYSTONE, key=("ps", lab))
            n += 1


def unpack_hand(t):
    """Where his near hand is while unpacking: in the sack, then out to the path."""
    for i, (tm, lab) in enumerate(DROPS):
        if tm - 0.9 <= t < tm + 0.5:
            k = prog(t, tm - 0.9, tm + 0.3)
            return lab, k, i
    return None, 0.0, 0


def t3(ctx, t):
    with Camera(2.0, 640, 620).apply(ctx):
        hill(ctx, t, 0.15)
        path_stones(ctx, t)
        hip, feet, lean = floor_sit(520)
        lab, k, i = unpack_hand(t)
        J0 = HIM.joints(hip, 1, -0.05)
        cx, cy, r = sack_geo(J0, kg_at(t))
        inside = (cx + 10, cy - r * 0.6)
        n_down = sum(1 for tm, _ in DROPS if t >= tm + 0.5)
        dest = (700 + (n_down % 7) * 64, FY - 24)
        hand = lerp2(inside, dest, ease(k)) if lab else (hip[0] + 70, FY - 10)
        J = carrier(ctx, t, hip, 1, feet=feet, lean=-0.05, expr="hopeful", look=(1, 0.8), near_arm_front=True,
                    hands={"near": hand, "far": (hip[0] - 50, FY - 4)})
        if lab and k < 1:
            w = dict((l, kk) for _, l, kk in STONES)[lab]
            hp = J["limbs"]["arm_near"][2]
            stone(ctx, hp[0], hp[1] - 6, 14 + 2.6 * w, lab, mix(STONE, GREYSTONE, ease(prog(k, 0.75, 1.0))), key=("held", lab))
    hud(ctx, t)


# ---- the final fight -------------------------------------------------------------------------------------
def f1f2(ctx, t):
    rise = ease(prog(t, 102.4, 104.0))
    z = lerp(1.6, 1.9, ease(prog(t, 102, 118)))
    with Camera(z, 560, 560, shake=2 * prog(t, 112, 118)).apply(ctx):
        hill(ctx, t, 0.2)
        path_stones(ctx, t)
        stand_up = ease(prog(t, 102.0, 103.0))
        x = 560
        hip_s, feet_s, _ = floor_sit(520)
        hip_t, feet_t = standing(x, FY, 1)
        hip = lerp2(hip_s, hip_t, stand_up)
        feet = {k: lerp2(feet_s[k], feet_t[k], stand_up) for k in feet_t}
        expr = "worried"
        if rise > 0.5:
            expr = "anxious"
        if t > EVENTS["eyes_closed"]:
            expr = "closed"
        if t > EVENTS["eyes_open"]:
            expr = "determined"
        kg = kg_at(t)
        J0 = HIM.joints(hip, 1, lean_for(kg))
        cx, cy, r = sack_geo(J0, kg)
        # the villain behind him, its arms wrapped around the sack, holding it on
        P.villain(ctx, cx - 120, FY, scale=lerp(0.6, 1.25, rise), alpha=rise, grin=1.2, lean=0.3,
                  reach=(cx + 10, cy) if rise > 0.6 else None, arms_up=0.2 * rise)
        lift = ease(prog(t, 113.6, 115.4))
        stone_pos = lerp2((cx, cy - r * 0.6), (hip[0] + 74, hip[1] - 70), lift)
        J = carrier(ctx, t, hip, 1, feet=feet, kg=kg, expr=expr, look=(1, 0.2), extra_lean=0.15 * rise * (1 - lift),
                    hands={"near": stone_pos if lift > 0 else (hip[0] + 40, hip[1] - 20), "far": (stone_pos[0] - 26, stone_pos[1] + 10) if lift > 0 else None})
        if lift > 0:
            stone(ctx, stone_pos[0] - 10, stone_pos[1] - 4, 48, "KAI", key="kai_big")
    vline(ctx, "V7", 1300, 230, 58)
    vline(ctx, "V8", 1300, 310, 52)
    vline(ctx, "V9", 1300, 230, 52)
    vline(ctx, "V10", 1300, 310, 60)
    hud(ctx, t)


def f3(ctx, t):
    lt = t - KAI_DOWN
    with Camera(1.9, 560, 560, shake=10 * (1 - prog(lt, 0, 0.5))).apply(ctx):
        hill(ctx, t, 0.25)
        path_stones(ctx, t)
        hip, feet = standing(560, FY, 1)
        k = ease(prog(t, KAI_DOWN - 0.4, KAI_DOWN + 0.2))
        top = (BOULDER[0] + 10, BOULDER[1] - 64)
        held = lerp2((hip[0] - 74, hip[1] - 70), (top[0] + 24, top[1] - 6), k)
        if t < EVENTS["crumble"]:
            P.villain(ctx, 380, FY, scale=1.25, alpha=1.0 - 0.4 * prog(lt, 0, 0.4), grin=0.0, lean=0.3, crack=ease(prog(lt, 0, 0.5)))
        else:
            P.villain_shards(ctx, 380, FY, 1.25, prog(t, EVENTS["crumble"], EVENTS["crumble"] + 2.0))
        grey_k = ease(prog(lt, 0.0, 0.8))
        HIM.draw(ctx, hip, -1, lean=0.04 + 0.5 * k * (1 - prog(lt, 0.6, 1.6)), feet=feet,
                 expr="closed" if lt < 0.8 else "smile", look=(-1, 0.6),
                 hands=free_hands(HIM, hip, -1, 0.04 + 0.5 * k, {"near": held, "far": (held[0] + 26, held[1] + 10)}) if lt < 0.6 else None)
        stone(ctx, held[0] - 6, held[1] - 4, 48, "KAI", mix(STONE, GREYSTONE, grey_k), glow_a=1 - grey_k, key="kai_big")
    flash = 1 - prog(lt, 0, 0.25)
    if flash > 0 and lt >= 0:
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((255, 236, 190), 0.4 * flash))
    hud(ctx, t)


# ---- payoff ------------------------------------------------------------------------------------------------
def p1(ctx, t):
    lt = t - 121.0
    dawn = ease(prog(t, 121.0, 125.0))
    x = min(1540, 600 + lt * 150)
    with Camera(lerp(1.2, 1.5, prog(t, 121, 131)), lerp(900, 1500, ease(prog(t, 121, 127))), lerp(560, CREST_Y - 140, ease(prog(t, 121, 127)))).apply(ctx):
        hill(ctx, t, dawn)
        stone(ctx, BOULDER[0] + 4, BOULDER[1] - 60, 48, "KAI", GREYSTONE, glow_a=0, key="kai_big")
        hf = ease(prog(t, EVENTS["high_five"] - 0.6, EVENTS["high_five"])) * (1 - ease(prog(t, EVENTS["high_five"] + 0.6, EVENTS["high_five"] + 1.2)))
        for i, (fx, f) in enumerate(((1820, -1), (1950, -1))):
            hip, feet = stand_on(grey(f"fr{i}"), ctx, fx, f)
            grey(f"fr{i}").draw(ctx, hip, f, lean=0.04, feet=feet, expr="happy", mouth_open=0.4 * abs(math.sin(t * 8 + i)))
        kx = 1680
        hipK, feetK = stand_on(KAI, ctx, kx, -1)
        meet = ((kx + x) / 2, CREST_Y - 230)
        JK = KAI.draw(ctx, hipK, -1, lean=0.04, feet=feetK, expr="happy", look=(-1, 0), mouth_open=talk("kai", t),
                      hands=free_hands(KAI, hipK, -1, 0.04, {"near": meet if hf > 0.1 else (kx - 30, CREST_Y - 120)}))
        moving = x < 1540
        hip, feet = stand_on(HIM, ctx, x, 1, step=(lt * 1.9) % 1 if moving else 0)
        HIM.draw(ctx, hip, 1, lean=0.12 if moving else 0.04, feet=feet, expr="happy", look=(1, -0.4 if moving else 0),
                 hands=free_hands(HIM, hip, 1, 0.04, {"near": meet if hf > 0.1 else (x + 30, ground(x) - 120)}))
        speech(ctx, t, "kai", JK["head"][0], JK["head"][1] - 70)
    hud(ctx, t)


def p2(ctx, t):
    with Camera(1.1, 1500, CREST_Y - 90).apply(ctx):
        hill(ctx, t, 1.0)
        for i, (fx, f, ch) in enumerate(((1560, 1, HIM), (1690, -1, KAI), (1820, -1, grey("fr0")), (1950, -1, grey("fr1")))):
            hip, feet = stand_on(ch, ctx, fx, f)
            ch.draw(ctx, hip, f, lean=0.02, feet=feet, expr="happy", look=(f, -0.3), mouth_open=0.3 * abs(math.sin(t * 6 + i)) if i else 0)
    cap(ctx, "C11", y=820)
    cap(ctx, "C12", y=890)
    hud(ctx, t)


def vt(ctx, t):
    down = ease(prog(t, EVENTS["viewer_set"], EVENTS["viewer_set"] + 0.8))
    y = lerp(520, 760, down)
    ctx.c.drawLine(560, 812, 1360, 812, stroke(GREY, 4, fade(t, 137.4, 146.0, 0.6, 0.6)))
    a = fade(t, 137.4, 146.0, 0.6, 0.6)
    grey_k = ease(prog(t, EVENTS["viewer_set"] + 0.6, EVENTS["viewer_set"] + 1.6))
    stone(ctx, W / 2, y, 110, "", mix(STONE, GREYSTONE, grey_k), a, glow_a=1 - grey_k, key="viewer")
    ctx.c.drawLine(W / 2 - 60, y + 10, W / 2 + 60, y + 10, stroke((250, 240, 230) if grey_k < 0.5 else (60, 58, 56), 4, a))
    cap(ctx, "V1", y=300, size=60)
    cap(ctx, "V2", y=300, size=60)


# ---- mirror and title --------------------------------------------------------------------------------------
def x1(ctx, t):
    shove = EVENTS["kid_shove"]
    with Camera(1.6, 1000, 580).apply(ctx):
        street(ctx, t, lamps=(400,), sky=(96, 104, 120), window_rgb=(150, 140, 110))
        P.wrect(ctx, 1240, FY - 330, 10, 330, "busstop", GREY_L, LINE, 2, seg=2)
        P.wrect(ctx, 1212, FY - 390, 70, 70, "bussign", (60, 90, 140), LINE, 3, seg=2)
        draw_text(ctx, "BUS", 1247, FY - 344, 26, TEXT)
        wrect(ctx, 760, 680, 360, 18, "bench", (120, 96, 70), LINE, 3, seg=2)
        for lx in (780, 1080):
            wrect(ctx, lx, 698, 14, 82, ("bl", lx), GREY_D, LINE, 2, seg=1)
        # the other kid shoves past
        if t < shove + 1.4:
            k = prog(t, shove - 0.6, shove + 1.4)
            x2 = lerp(1400, 400, k)
            hip, feet = standing(x2, FY, -1, KID2.scale, step=(t * 2.4) % 1)
            JK2 = KID2.draw(ctx, hip, -1, lean=0.1, feet=feet, expr="determined", look=(-1, 0), mouth_open=talk("kid2", t))
            speech(ctx, t, "kid2", JK2["head"][0], JK2["head"][1] - 50, size=26)
        kid_x = 1000
        hipK = (kid_x, 676)
        feetK = {"near": (kid_x - 34, 744), "far": (kid_x - 28, 746)}  # his feet dangle above the ground
        set_k = ease(prog(t, EVENTS["kid_set"] - 0.6, EVENTS["kid_set"]))
        pocket = (kid_x - 6, 620)
        bench_spot = (kid_x - 70, 668)
        kid_hand = lerp2(pocket, bench_spot, set_k) if t > shove + 0.3 else (kid_x - 30, 650)
        JK = KID.draw(ctx, hipK, -1, lean=0.08, feet=feetK, expr="hurt" if t < EVENTS["kid_set"] else "smile", look=(-1, 0.4) if t < 151 else (-1, 0.8),
                      hands=free_hands(KID, hipK, -1, 0.08, {"near": kid_hand}))
        pebble_grey = ease(prog(t, EVENTS["kid_set"] + 0.2, EVENTS["kid_set"] + 1.0))
        if t > shove + 0.3:
            stone(ctx, JK["limbs"]["arm_near"][2][0], JK["limbs"]["arm_near"][2][1] - 4 if set_k < 1 else bench_spot[1] - 6, 12,
                  "", mix(STONE, GREYSTONE, pebble_grey), glow_a=1 - pebble_grey, key="kidpeb")
        # him: sits, sets his grey pebble on the bench between them
        hip, feet = seated(860, 680, 1)
        sk = ease(prog(t, EVENTS["pebble_set"] - 0.6, EVENTS["pebble_set"]))
        hand = lerp2((900, 650), (930, 670), sk)
        J = HIM.draw(ctx, hip, 1, lean=0.08, feet=feet, expr="smile", look=(1, 0.6),
                     hands=free_hands(HIM, hip, 1, 0.08, {"near": hand, "far": (848, 668)}))
        if t > EVENTS["pebble_set"] - 0.6:
            stone(ctx, J["limbs"]["arm_near"][2][0], J["limbs"]["arm_near"][2][1] - 6, 12, "", GREYSTONE, glow_a=0, key="hispeb")


def title(ctx, t):
    a = fade(t, EVENTS["title"], DURATION, 0.8, 1.2)
    draw_text(ctx, "HEAVY.", W / 2, 520, 220, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 300 + 600 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=46)
    cap(ctx, "T2", y=760, size=64, rgb=GOLD, glow_rgb=(170, 110, 20))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5, "S02": s02, "S03": s03, "B1": b1,
    "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6, "R1": r1, "R2": r2,
    "T1": t1, "T2": t2, "T3": t3, "F1": f1f2, "F2": f1f2, "F3": f3, "P1": p1, "P2": p2, "VT": vt, "X1": x1, "TT": title,
}
CONTINUOUS = {"F2", "R2"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "TT":
        black(ctx, prog(t, DURATION - 1.0, DURATION))
