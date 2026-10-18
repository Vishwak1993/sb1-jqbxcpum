"""1%.: picture. scene(ctx) draws any frame of the film.

The device: his own BATTERY meter, draining all film, while his phone on its charger sits at 100%.
Low means red (failure). At the payoff he wakes at 100% and the meter turns gold.
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
from studio.extras import speech as _speech, talk as _talk, free_hands, floor_sit, door, office, phone_close  # noqa: E402
from timeline import SCENES, CAPS, CUES, BUBBLES, EVENTS, DURATION, scene_at, bat_at, bat_changed  # noqa: E402
from lines import CAPTIONS, VILLAIN, LESSON  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
CHARGE = (110, 210, 120)  # the phone's charging green: phones only


# ---- cast -----------------------------------------------------------------------------
def tuft(ctx, hx, hy, f, s):
    for dx, h in ((-14, 22), (0, 30), (14, 20)):
        p = poly_path([(hx + dx * s - 7 * s, hy - 46 * s), (hx + dx * s + f * 4 * s, hy - (46 + h) * s), (hx + dx * s + 7 * s, hy - 46 * s)])
        ctx.c.drawPath(p, fill((70, 62, 58)))
        ctx.c.drawPath(p, stroke(LINE, 2.5 * s))


HIM = Character("him")
THEO = Character("theo", scale=0.72, extra=tuft)


def grey(name, scale=1.0):
    return Character(name, skin=(150, 150, 156), scale=scale)


# ---- shared helpers ----------------------------------------------------------------------
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


def bat_colour(v, gold=False):
    if gold:
        return GOLD
    if v <= 20:
        return RED
    return TEXT


def battery_icon(ctx, x, y, w, h, v, rgb, a=1.0, lw=4):
    """Battery outline at (x, y) (top-left), filled v percent."""
    c = ctx.c
    rrect(ctx, x, y, w, h, h * 0.22, None, rgb, lw, a=a)
    c.drawRect(skia.Rect.MakeXYWH(x + w, y + h * 0.3, w * 0.07, h * 0.4), fill(rgb, a))
    pad = lw + 3
    fw = max(0.0, (w - 2 * pad) * v / 100)
    if fw > 0:
        rrect(ctx, x + pad, y + pad, fw, h - 2 * pad, h * 0.12, rgb, None, a=a)


def hud(ctx, t, a=1.0, gold=False, x=56):
    v = bat_at(t)
    if v is None or a <= 0:
        return
    y = LETTERBOX + 26
    low = v <= 20
    blink = 1.0 if not (v <= 1.5 and int(t * 2) % 2 == 0) else 0.35
    rgb = bat_colour(v, gold)
    rrect(ctx, x, y, 300, 92, 14, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
    draw_text(ctx, "BATTERY", x + 20, y + 32, 22, (160, 160, 168), a, align="left")
    pop = pop_at(t, bat_changed(t))
    battery_icon(ctx, x + 20, y + 44, 110, 36, v, rgb, a * blink, 3)
    sz = 50 * (1 + 0.3 * math.sin(math.pi * pop) if pop > 0 else 1)
    draw_text(ctx, f"{int(round(v))}%", x + 152, y + 80, sz, rgb, a * blink, align="left", face="LuckiestGuy-Regular.ttf",
              glow_rgb=rgb if (low or gold) else None)


def charging_phone(ctx, x, y, full=100, a=1.0, cable_to=None):
    """His phone lying on the desk, plugged in, its screen showing a green charging battery."""
    if cable_to:
        wline(ctx, (x + 40, y - 4), cable_to, "cable", (40, 40, 44), 5, seg=3)
    P.phone_side(ctx, x, y, on=1.0, key="cph", glow_rgb=CHARGE)
    glow(ctx, x, y - 30, 120, CHARGE, 0.25 * a)
    battery_icon(ctx, x - 34, y - 96, 60, 26, full, CHARGE, a, 3)
    draw_text(ctx, f"{full}%", x + 36, y - 74, 26, CHARGE, a, align="left", face="LuckiestGuy-Regular.ttf")


def laptop(ctx, x, desk_y, open_k=1.0, glow_a=1.0, text=None, key="lap", cable=False):
    wrect(ctx, x - 90, desk_y - 10, 180, 10, (key, "base"), (60, 62, 70), LINE, 3, seg=2)
    if cable:
        wline(ctx, (x + 90, desk_y - 6), (x + 200, FY), (key, "cab"), (40, 40, 44), 5, seg=3)
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


def mugs(ctx, n, x=620, y=640):
    for i in range(n):
        P.mug(ctx, x + i * 46 - (i // 4) * 170, y - (i // 4) * 0, key=("mug", i))


def clock_text(ctx, x, y, s, rgb=(200, 200, 206), size=30):
    rrect(ctx, x - 78, y - 32, 156, 50, 10, (16, 16, 20), (70, 70, 80), 3)
    draw_text(ctx, s, x, y + 6, size, rgb, face="LuckiestGuy-Regular.ttf")


def lamp(ctx, x, on=1.0, key="dlamp", desk_y=640):
    wline(ctx, (x, desk_y - 4), (x - 20, desk_y - 120), (key, "arm"), GREY_D, 7, seg=1)
    p = poly_path([(x - 60, desk_y - 140), (x + 10, desk_y - 140), (x - 6, desk_y - 108), (x - 44, desk_y - 108)])
    ctx.c.drawPath(p, fill(GREY_L))
    ctx.c.drawPath(p, stroke(LINE, 3))
    if on > 0:
        glow(ctx, x - 25, desk_y - 100, 320, (255, 214, 160), 0.22 * on)
        cone(ctx, (x - 25, desk_y - 108), (x - 140, desk_y), (x + 90, desk_y), (255, 214, 160), 0.10 * on)


def room(ctx, t, sky="night", desk=True, lap=1.0, lap_text=None, mug_n=0, lamp_on=1.0, phone_full=None, bed=False, sofa=False,
         window_gold=0.0, lap_cable=False, lap_x=800):
    skies = {"night": (22, 26, 38), "dawn": (100, 96, 116), "day": (84, 96, 118), "gold": (190, 150, 90)}
    P.back_wall(ctx, rgb=mix((20, 20, 23), (56, 44, 30), window_gold))
    P.floor(ctx, FY)
    P.window(ctx, 1500, 200, 230, 230, "rwin", night=sky == "night", sky=skies[sky], moon=sky == "night")
    if window_gold > 0:
        glow(ctx, 1615, 315, 600, GOLD, 0.35 * window_gold)
        cone(ctx, (1600, 330), (1100, FY), (1720, FY), GOLD, 0.14 * window_gold)
    if bed:
        P.bed(ctx, 1100, FY, 560)
        P.wrect(ctx, 980, FY - 110, 100, 110, "nstand", GREY_D, LINE, 3, seg=2)
    if sofa:
        wrect(ctx, 1040, 690, 440, 90, "sofa", (64, 66, 86), LINE, 3, seg=3)
        wrect(ctx, 1020, 600, 40, 180, "sofaarm", (64, 66, 86), LINE, 3, seg=2)
    scr = None
    if desk:
        P.table(ctx, 560, 640, 460, key="desk")
        P.chair(ctx, 640, 690, 1, key="dchair")
        lamp(ctx, 980, lamp_on)
        scr = laptop(ctx, lap_x, 640, open_k=lap, text=lap_text, cable=lap_cable)
        mugs(ctx, mug_n)
        if phone_full is not None:
            charging_phone(ctx, 900, 636, phone_full, cable_to=(940, FY))
    return scr


def him_at_desk(ctx, t, expr="tired", look=(1, 0.4), lean=0.26, hands=None, **kw):
    hip, feet = seated(640, 690, 1)
    hands = hands or {"near": (760, 634), "far": (744, 638)}
    return HIM.draw(ctx, hip, 1, lean=lean, feet=feet, hands=free_hands(HIM, hip, 1, lean, hands), expr=expr, look=look,
                    screen_glow=0.6, **kw)


def typing(t, k=1.0):
    return {"near": (760 + 10 * math.sin(t * 23), 632 - 4 * abs(math.sin(t * 17)) * k),
            "far": (740 + 10 * math.sin(t * 19 + 1), 636 - 4 * abs(math.sin(t * 21)) * k)}


def villain_from_glow(ctx, t, src, t0, t1, x, scale=1.0):
    """Red wisps rise from a screen and gather into the villain."""
    born = ease(prog(t, t0 + 0.6, t1))
    for i in range(8):
        k = (t * 0.6 + hrand("wisp", i)) % 1.0
        a = (1 - k) * prog(t, t0, t0 + 0.5) * (1 - prog(t, t1, t1 + 0.8))
        ctx.c.drawCircle(src[0] + (hrand("wx", i) - 0.5) * 100 + (x - src[0]) * k, src[1] - k * 260, 10 + 16 * k,
                         blurred(fill(RED, 0.35 * a), 8))
    return born


def stand(ch, ctx, x, f=1, lean=0.04, step=0.0, free=False, **kw):
    hip, feet = standing(x, FY, f, ch.scale, step=step)
    if free and kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def sit(ch, ctx, x, seat_y=690, f=1, lean=0.2, **kw):
    hip, feet = seated(x, seat_y, f, ch.scale)
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def in_bed(ctx, expr="closed", look=(0, -1)):
    """Lying on his back on the bed (bed at x=1100, mattress top FY-90), head on the pillow, legs under the duvet."""
    hip = (1330, FY - 132)
    HIM.draw(ctx, hip, -1, lean=math.pi / 2, feet={"near": (hip[0] + 114, FY - 126), "far": (hip[0] + 112, FY - 128)},
             expr=expr, look=look, hands={"near": (hip[0] - 20, FY - 104), "far": (hip[0] - 10, FY - 106)},
             bend={"leg_near": 1, "leg_far": 1, "arm_near": 1, "arm_far": 1})
    P.wrect(ctx, 1250, FY - 136, 300, 46, "duvet", (60, 64, 92), LINE, 3, seg=3)


# ---- the hook -------------------------------------------------------------------------------
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


def h1(ctx, t):
    up = ease(prog(t, EVENTS["spring"], EVENTS["spring"] + 0.5))
    with Camera(1.7, 1150, 540).apply(ctx):
        room(ctx, t, sky="dawn", desk=False, bed=True)
        ring = EVENTS["alarm1"] <= t < EVENTS["spring"]
        jx = (hrand("al", ctx.frame) - 0.5) * 6 if ring else 0
        clock_text(ctx, 1030 + jx, FY - 140, "6:00", rgb=RED if ring else (200, 200, 206))
        if up < 0.5:
            in_bed(ctx, "closed" if t < 3.6 else "shocked")
        else:
            x = lerp(1240, 1000, ease(prog(t, 4.4, 5.8)))
            stand(HIM, ctx, x, f=-1, lean=0.06, expr="happy", look=(-1, 0), step=(t * 2) % 1 if t > 4.4 else 0,
                  hands={"near": (x - 150, 600), "far": (x + 140, 610)}, free=True)
            P.wrect(ctx, 1250, FY - 136, 300, 46, "duvet", (60, 64, 92), LINE, 3, seg=3)
    hud(ctx, t)


def h2(ctx, t):
    with Camera(2.0, 760, 560).apply(ctx):
        room(ctx, t, sky="day", lap_text=["INBOX 48", "re: re: urgent", "FW: today pls"], mug_n=1)
        him_at_desk(ctx, t, "neutral", hands=typing(t))
    hud(ctx, t)


def h3(ctx, t):
    with Camera(1.7, 960, 560).apply(ctx):
        office(ctx, desk_x=700)
        P.chair(ctx, 760, 690, 1, key="mc")
        J = sit(HIM, ctx, 760, f=1, lean=0.2, expr="worried", look=(1, -0.3), hands={"near": (866, 632), "far": (850, 638)})
        J1 = stand(grey("m1"), ctx, 1220, f=-1, lean=0.14, expr="neutral", look=(-1, 0.4), mouth_open=0.4 * abs(math.sin(t * 14)))
        J2 = stand(grey("m2"), ctx, 560, f=1, lean=0.14, expr="neutral", look=(1, 0.4), mouth_open=0.4 * abs(math.sin(t * 13 + 1)))
        speech(ctx, t, "m1", J1["head"][0] - 40, J1["head"][1] - 70)
        speech(ctx, t, "m2", J2["head"][0] + 40, J2["head"][1] - 70)
    hud(ctx, t)


def h4(ctx, t):
    with Camera(2.0, 760, 560).apply(ctx):
        room(ctx, t, sky="day", lap_text=["Q3 report", "slides v7"], mug_n=2)
        P.wrect(ctx, 660, 626, 70, 14, "sandwich", (200, 160, 110), LINE, 2, seg=1)
        hip, _ = seated(640, 690, 1)
        J0 = HIM.joints(hip, 1, 0.26, 0.25)
        ear = (J0["head"][0] - 34, J0["head"][1] + 6)
        rrect(ctx, ear[0] - 9, ear[1] - 34, 18, 46, 4, (40, 40, 46), LINE, 2.5)
        J = him_at_desk(ctx, t, "tired", look=(1, 0.4), hands={"near": (770, 632), "far": (ear[0], ear[1] + 14)}, head_tilt=0.25,
                        mouth_open=talk("him", t))
        speech(ctx, t, "him", J["head"][0] + 40, J["head"][1] - 70)
    hud(ctx, t)


def h5(ctx, t):
    t0, t1 = EVENTS["villain_born"]
    with Camera(1.8, 860, 520).apply(ctx):
        scr = room(ctx, t, sky="night", lap_text=["one more slide"], mug_n=3, lamp_on=0.6)
        born = villain_from_glow(ctx, t, scr, t0, t1, 1120)
        P.villain(ctx, 1120, FY, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 15.4, 16.2)), lean=-0.2)
        him_at_desk(ctx, t, "tired", hands=typing(t, 0.6))
    vline(ctx, "V1", 960, 250, 60)
    hud(ctx, t)


def h6(ctx, t):
    plug = EVENTS["plug"]
    with Camera(lerp(2.0, 2.5, ease(prog(t, 17, 24))), 800, 540).apply(ctx):
        room(ctx, t, sky="night", lap=0.0, mug_n=3, lamp_on=0.6, phone_full=None)
        P.villain(ctx, 1220, FY, scale=1.0, alpha=0.45, grin=1.0, lean=-0.2)
        full = int(lerp(23, 100, ease(prog(t, plug + 0.3, plug + 2.6))))
        if t >= plug:
            charging_phone(ctx, 900, 636, full, cable_to=(940, FY))
        else:
            P.phone_side(ctx, 900, 636, on=0.3, key="cph")
            battery_icon(ctx, 866, 540, 60, 26, 23, RED, 1.0, 3)
        reach = math.sin(math.pi * prog(t, plug - 1.0, plug + 0.4))
        hands = {"near": lerp2((760, 634), (900, 630), reach), "far": (744, 638)}
        if t < plug:
            wline(ctx, (940, FY), lerp2((940, FY), (900, 630), reach), "cable2", (40, 40, 44), 5, seg=2)
        J = him_at_desk(ctx, t, "tired", look=(1, 0.8) if t < plug + 2.8 else (0, -1.2), hands=hands)
        if t > plug + 2.4:
            hx, hy = J["head"]
            k = ease(prog(t, plug + 2.4, plug + 2.9))
            battery_icon(ctx, hx - 50, hy - 120, 100, 40, 41, TEXT, k, 4)
            draw_text(ctx, "41%", hx + 66, hy - 88, 30, TEXT, k, align="left", face="LuckiestGuy-Regular.ttf")
    cap(ctx, "C2", y=975)
    hud(ctx, t)


def h7(ctx, t):
    cap(ctx, "C3", y=H / 2 + 16, size=58)
    hud(ctx, t, a=0.0)


# ---- stakes: Theo ------------------------------------------------------------------------------
def star_paper(ctx, x, y, s=1.0, rgb=(226, 222, 212)):
    pts = []
    for i in range(10):
        r = (34 if i % 2 == 0 else 15) * s
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    p = poly_path(pts)
    ctx.c.drawPath(p, fill(rgb))
    ctx.c.drawPath(p, stroke(LINE, 3 * s))


def b1(ctx, t):
    open_k = ease(prog(t, EVENTS["door_knock"] + 0.4, EVENTS["door_knock"] + 1.0))
    with Camera(1.75, 760, 560).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        door(ctx, 300, open_k=open_k, light=open_k)
        x = lerp(280, 520, ease(prog(t, 28.0, 29.0)))
        JT = stand(THEO, ctx, x, f=1, lean=0.04, expr="happy", look=(1, -0.6), mouth_open=talk("theo", t),
                   hands={"near": (x + 50, 600)}, free=True)
        star_paper(ctx, *JT["limbs"]["arm_near"][2])
        JH = stand(HIM, ctx, 800, f=-1, lean=0.08, expr="smile" if t > 31.6 else "tired", look=(-1, 0.6),
                   mouth_open=talk("him", t), hands={"near": (760, 660), "far": (790, 640)}, free=True)
        P.phone_held(ctx, 780, 650, facing=-1, on=1.0)
        speech(ctx, t, "theo", JT["head"][0] + 20, JT["head"][1] - 60)
        speech(ctx, t, "him", JH["head"][0] - 10, JH["head"][1] - 70)
    hud(ctx, t)


# ---- the grind ----------------------------------------------------------------------------------
def g1(ctx, t):
    if t < 37.8:
        with Camera(2.3, 1100, 600).apply(ctx):
            room(ctx, t, sky="dawn", desk=False, bed=True)
            clock_text(ctx, 1030, FY - 140, "6:00", rgb=RED)
            in_bed(ctx, "tired")
    else:
        with Camera(2.2, 760, 580).apply(ctx):
            room(ctx, t, sky="day", lap_text=["INBOX 61"], mug_n=1 + int(prog(t, 37.8, 39.3) * 2.99))
            him_at_desk(ctx, t, "tired", hands=typing(t))
    label(ctx, "WEEK 1")
    hud(ctx, t)


def g2(ctx, t):
    with Camera(1.6, 960, 560).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeLTRB(-600, 0, W + 600, FY), fill((40, 42, 50)))
        for i in range(4):  # windows with the city streaming past
            x0 = 300 + i * 360
            wrect(ctx, x0, 260, 280, 180, ("tw", i), (30, 34, 46), (80, 82, 92), 4, seg=2)
            ctx.c.save()
            ctx.c.clipRect(skia.Rect.MakeXYWH(x0, 260, 280, 180))
            for j in range(6):
                bx = x0 + ((j * 90 - t * 600) % 480) - 100
                ctx.c.drawRect(skia.Rect.MakeXYWH(bx, 330 + hrand("tb", j) * 60, 60, 200), fill((22, 24, 32)))
            ctx.c.restore()
        P.floor(ctx, FY)
        for x in (640, 1120):
            wrect(ctx, x - 70, 610, 160, 80, ("seat", x), (70, 60, 80), LINE, 3, seg=2)
            wrect(ctx, x - 90, 500, 30, 190, ("seatb", x), (70, 60, 80), LINE, 3, seg=2)
        sit(grey("p1"), ctx, 1120, seat_y=690, f=1, lean=0.1, expr="neutral", look=(1, 0.3))
        nod = 0.5 + 0.5 * math.sin(t * 1.6)
        J = sit(HIM, ctx, 640, seat_y=690, f=1, lean=0.2 + 0.1 * nod, expr="closed" if nod > 0.6 else "tired", look=(1, 0.8),
                head_tilt=0.2 * nod, hands={"near": (740, 660), "far": (726, 664)})
        laptop(ctx, 770, 690, open_k=0.7, glow_a=0.8, key="tlap")
    vline(ctx, "V2", 960, 220, 52)
    label(ctx, "WEEK 2")
    hud(ctx, t)


def g3(ctx, t):
    lt = t - 43.0
    with Camera(1.5, 960, 540).apply(ctx):
        office(ctx, desk_x=700, night=True)
        P.chair(ctx, 760, 690, 1, key="oc")
        sit(HIM, ctx, 760, f=1, lean=0.3, expr="tired", look=(1, 0.5), hands={"near": (866, 632), "far": (850, 638)})
        for i in range(5):  # empty desks, lights off
            ctx.c.drawRect(skia.Rect.MakeXYWH(-200 + i * 0, 0, 0, 0), fill(BG))
        x, ph = walk_x(1500, lt, -90)
        stand(grey("cleaner"), ctx, x, f=-1, lean=0.2, step=ph, expr="neutral", look=(-1, 0.6),
              hands={"near": (x - 70, 700), "far": (x - 50, 690)}, free=True)
        wline(ctx, (x - 70, 700), (x - 140, FY), "mop", (120, 110, 90), 6, seg=1)
        wrect(ctx, x - 180, FY - 14, 80, 14, "mophead", (190, 186, 170), LINE, 2, seg=1)
    vline(ctx, "V3", 1200, 300, 52)
    label(ctx, "WEEK 3")
    hud(ctx, t)


def g4(ctx, t):
    phone_close(ctx, t, "Theo", ["rehearsal went great!!", "i get a cape"], [46.8, 47.8], avatar=(200, 160, 110))
    if t > 48.8:
        draw_text(ctx, "Read 18:02", W / 2 + 230, 700, 26, (160, 162, 172), ease(prog(t, 48.8, 49.1)), align="right")
    label(ctx, "WEEK 4")
    hud(ctx, t)


def g5(ctx, t):
    grab = ease(prog(t, 52.2, 52.9))
    with Camera(1.8, 1240, 560).apply(ctx):
        room(ctx, t, sky="night", desk=False, sofa=True)
        wrect(ctx, 1500, 660, 120, 20, "stable", GREY, LINE, 3, seg=2)
        if grab < 1:
            laptop(ctx, 1560, 660, open_k=0.0, key="slap")
        if grab < 0.5:
            hip = (1290, 666)
            jig = math.sin(t * 22) * 6
            HIM.draw(ctx, hip, -1, lean=math.pi / 2 - 0.04, feet={"near": (1404, 662 + jig), "far": (1404, 664)},
                     expr="tired", look=(0, -1), hands={"near": (1294, 672), "far": (1288, 674)},
                     bend={"leg_near": -1, "leg_far": -1, "arm_near": 1, "arm_far": -1})
        else:
            hip, feet = seated(1260, 694, 1)
            HIM.draw(ctx, hip, 1, lean=0.14, feet=feet, expr="tired", look=(1, 1.0), screen_glow=0.8,
                     hands=free_hands(HIM, hip, 1, 0.14, {"near": (1366, 690), "far": (1350, 694)}))
            laptop(ctx, 1404, 712, open_k=0.85, key="slap2")
    vline(ctx, "V4", 960, 300, 52)
    label(ctx, "WEEK 5")
    hud(ctx, t)


def g6(ctx, t):
    with Camera(1.0, 960, 540).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((30, 32, 36)))
        wrect(ctx, 560, 160, 800, 760, "mirror", (60, 66, 74), (140, 140, 150), 10, seg=3)
        ctx.c.save()
        ctx.c.clipRect(skia.Rect.MakeXYWH(560, 160, 800, 760))
        tired = Character("himgrey", skin=(196, 194, 186), scale=2.6)
        J = tired.joints((960, 960), 1, 0.0)
        tired.draw(ctx, (960, 960), 1, lean=0.0, expr="tired", look=(0, 0.3))
        hx, hy = J["head"]
        for side in (-1, 1):  # deep bags under his eyes
            ex = hx + 14 * 2.6 + side * 13 * 2.6
            ctx.c.drawPath(poly_path([(ex - 20, hy + 26), (ex, hy + 36), (ex + 20, hy + 26)], False, True), stroke((120, 110, 120), 7))
        ctx.c.restore()
    cap(ctx, "C4", y=980)
    label(ctx, "WEEK 6")
    hud(ctx, t)


def g7(ctx, t):
    with Camera(2.0, 800, 560).apply(ctx):
        room(ctx, t, sky="night", lap_text=["DEADLINE 20:00"], mug_n=5, lamp_on=0.6)
        J = him_at_desk(ctx, t, "anxious", hands=typing(t))
        clock_text(ctx, 640, 380, "FRI 18:30")
        P.bubble(ctx, 880, 470, "it starts at 7!", False, 26, fade(t, 57.6, 60.8, 0.2, 0.3), 260, rgb=(70, 60, 50))
        P.bubble(ctx, 880, 520, "on my way", True, 26, fade(t, 59.0, 60.8, 0.2, 0.3), 260)
    label(ctx, "FRIDAY")
    hud(ctx, t)


# ---- rock bottom --------------------------------------------------------------------------------
def r1(ctx, t):
    spill = ease(prog(t, EVENTS["spill"], EVENTS["spill"] + 0.8))
    slump = ease(prog(t, 61.6, 63.0))
    with Camera(lerp(1.8, 2.1, prog(t, 61, 68)), 780, 560).apply(ctx):
        room(ctx, t, sky="night", lap_text=["DEADLINE 20:00"], mug_n=4, lamp_on=0.6, lap_x=lerp(800, 880, slump))
        clock_text(ctx, 640, 380, "FRI 19:40")
        mx, my = 830, 640
        ctx.c.save()
        ctx.c.translate(mx, my)
        ctx.c.rotate(-90 * spill)
        P.mug(ctx, -16, 0, key="mug5")
        ctx.c.restore()
        if spill > 0:
            ctx.c.drawOval(skia.Rect.MakeLTRB(mx - 20, my - 8, mx + 40 + 120 * spill, my + 4), fill((90, 60, 40)))
        hip, feet = seated(640, 690, 1)
        ln = lerp(0.26, 0.86, slump)
        HIM.draw(ctx, hip, 1, lean=ln, feet=feet, expr="closed", look=(1, 1), head_tilt=0.4 * slump, near_arm_front=False,
                 hands=free_hands(HIM, hip, 1, ln, {"near": lerp2((770, 630), (722, 634), slump), "far": lerp2((750, 636), (706, 636), slump)}))
        if slump > 0.9:
            draw_text(ctx, "z", 760 + 8 * math.sin(t * 2), 470 - (t * 30) % 40, 40, TEXT, 0.5)
    hud(ctx, t)


def r2(ctx, t):
    if t < 71.8:
        phone_close(ctx, t, "Theo", ["you weren't there", "its ok"], [EVENTS["theo_text1"], EVENTS["theo_text2"]],
                    avatar=(200, 160, 110))
        draw_text(ctx, "21:15", W / 2, 150, 36, (190, 190, 196))
        vline(ctx, "V5", W / 2 + 520, 420, 54)
    else:
        with Camera(1.9, 760, 560).apply(ctx):
            room(ctx, t, sky="night", lap_text=["DEADLINE 20:00"], mug_n=4, lamp_on=0.6)
            ctx.c.drawOval(skia.Rect.MakeLTRB(810, 632, 970, 644), fill((90, 60, 40)))
            hip, feet = seated(640, 690, 1)
            J = HIM.draw(ctx, hip, 1, lean=0.4, feet=feet, expr="hurt", look=(1, 1), head_tilt=0.2,
                         hands=free_hands(HIM, hip, 1, 0.4, {"near": (752, 640), "far": (736, 646)}))
            P.phone_held(ctx, *J["limbs"]["arm_near"][2], on=1.0)
        cap(ctx, "C5")
    hud(ctx, t)


# ---- the turn ------------------------------------------------------------------------------------
def t1(ctx, t):
    if t < 79.0:
        UI = P.PhoneUI(W / 2, 590, 560, 880)
        UI.body(ctx, 0.6, BLUE)
        with UI.screen(ctx):
            battery_icon(ctx, UI.cx - 90, UI.cy - 160, 180, 70, 3, RED, 1.0, 5)
            a = ease(prog(t, EVENTS["lowbat_popup"], EVENTS["lowbat_popup"] + 0.3))
            rrect(ctx, UI.x0 + 50, UI.cy - 40, UI.w - 100, 170, 26, (48, 50, 62), None, a=a)
            draw_text(ctx, "Battery low.", UI.cx, UI.cy + 30, 44, TEXT, a)
            draw_text(ctx, "Plug in to charge.", UI.cx, UI.cy + 86, 36, (190, 192, 204), a)
        hud(ctx, t)
        return
    look = (1, 0.8) if t < 80.6 else ((1, 1.0) if t < 81.8 else (0, 0.6))
    with Camera(lerp(1.9, 2.3, prog(t, 79, 84)), 800, 560).apply(ctx):
        room(ctx, t, sky="night", lap_text=None, mug_n=4, lamp_on=0.6, phone_full=100, lap_cable=True)
        hip, feet = seated(640, 690, 1)
        J = HIM.draw(ctx, hip, 1, lean=0.3, feet=feet, expr="worried" if t < 81.8 else "hurt", look=look,
                     hands=free_hands(HIM, hip, 1, 0.3, {"near": (760, 634) if t < 81.8 else (704, 616), "far": (744, 638)}))
        if t > 81.8:  # his own battery, above his head
            hx, hy = J["head"]
            battery_icon(ctx, hx - 50, hy - 140, 100, 36, 1, RED, ease(prog(t, 81.8, 82.3)), 4)
    cap(ctx, "C6", y=930)
    cap(ctx, "C7", y=995)
    hud(ctx, t)


def t2(ctx, t):
    c = ctx.c
    k = ease(prog(t, 84.2, 85.0))
    bx, by, bw, bh = 760, 380, 400, 220
    battery_icon(ctx, bx, by, bw, bh, 0, TEXT, k, 8)
    fill_v = 70 * ease(prog(t, 86.0, 88.0)) - 30 * ease(prog(t, 88.4, 89.4))
    if fill_v > 0:
        rrect(ctx, bx + 16, by + 16, (bw - 32) * fill_v / 100, bh - 32, 18, GOLD if False else TEXT, None, a=0.85 * k)
    for i, s in enumerate(LESSON["in"]):
        a = ease(prog(t, 85.0 + i * 0.4, 85.4 + i * 0.4))
        y = 300 + i * 90
        draw_text(ctx, s, 600, y + 12, 40, TEXT, a, align="right", face="LuckiestGuy-Regular.ttf")
        c.drawLine(612, y, 740, by + bh / 2, stroke(TEXT, 3, 0.6 * a))
    for i, s in enumerate(LESSON["out"]):
        a = ease(prog(t, 88.0 + i * 0.4, 88.4 + i * 0.4))
        y = 340 + i * 100
        draw_text(ctx, s, 1340, y + 12, 40, RED, a, align="left", face="LuckiestGuy-Regular.ttf")
        c.drawLine(1200, by + bh / 2, 1324, y, stroke(RED, 3, 0.6 * a))
    cap(ctx, "C8", y=860)
    cap(ctx, "C9", y=930)
    hud(ctx, t)


def t3(ctx, t):
    with Camera(1.6, 1150, 520).apply(ctx):
        room(ctx, t, sky="night", desk=False, bed=True)
        k = prog(t, 93.0, 99.0)
        glow(ctx, 1540 + 160 * k, 260 - 40 * math.sin(math.pi * k), 60, (220, 220, 230), 0.4)
        clock_text(ctx, 1030, FY - 140, f"{(22 + int(k * 8.9)) % 24}:00")
        in_bed(ctx, "closed")
        if t > 94.0:
            draw_text(ctx, "z", 1180 + 8 * math.sin(t * 2), 560 - (t * 30) % 50, 40, TEXT, 0.5)
        v = bat_at(t)
        battery_icon(ctx, 1250, 480, 110, 44, v, bat_colour(v), 1.0, 4)
        draw_text(ctx, f"{int(v)}%", 1380, 516, 32, bat_colour(v), 1.0, align="left", face="LuckiestGuy-Regular.ttf")
    hud(ctx, t)


# ---- practice: charging --------------------------------------------------------------------------
def c1(ctx, t):
    lt = t - 99.0
    with Camera(1.6, 1000, 560).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, FY), fill((140, 132, 140)))
        glow(ctx, 1500, 260, 700, (255, 210, 150), 0.5)
        for i in range(7):
            x = 200 + i * 260
            wline(ctx, (x, FY), (x, FY - 200), ("trunk", i), (70, 56, 46), 16, seg=1)
            wcircle(ctx, x, FY - 260, 90, ("crown", i), (70, 96, 74), LINE, 3)
        P.floor(ctx, FY, rgb=(90, 110, 80))
        x, ph = walk_x(800, lt, 110)
        stand(HIM, ctx, x, f=1, lean=0.02, step=ph, expr="smile", look=(1, -0.6))
    hud(ctx, t)


def c2(ctx, t):
    with Camera(1.75, 980, 560).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeLTRB(-600, 0, W + 600, FY), fill((44, 38, 34)))
        P.wrect(ctx, 640, 170, 680, 300, "cwin", (120, 110, 90), (110, 100, 80), 5, seg=4)
        glow(ctx, 980, 320, 500, (255, 220, 160), 0.3)
        P.floor(ctx, FY, rgb=(80, 70, 60))
        P.table(ctx, 870, 640, 220, key="ctable")
        P.chair(ctx, 800, 690, 1, key="cc1")
        P.chair(ctx, 1160, 690, -1, key="cc2")
        laugh = 0.5 + 0.5 * math.sin(t * 9)
        sit(HIM, ctx, 800, f=1, lean=0.12, expr="happy", look=(1, 0), mouth_open=0.5 * laugh * (t > 104.6),
            hands={"near": (900, 626), "far": (884, 636)})
        JC = sit(grey("colleague"), ctx, 1160, f=-1, lean=0.12, expr="happy", look=(-1, 0), mouth_open=talk("colleague", t),
                 hands={"near": (1060, 626), "far": (1076, 636)})
        speech(ctx, t, "colleague", JC["head"][0], JC["head"][1] - 70)
    hud(ctx, t)


def c3(ctx, t):
    with Camera(1.8, 1240, 560).apply(ctx):
        room(ctx, t, sky="day", desk=False, sofa=True)
        hip, feet = seated(1260, 694, 1)
        J = HIM.draw(ctx, hip, 1, lean=-0.05, feet=feet, expr="smile", look=(1, 0.6),
                     hands=free_hands(HIM, hip, 1, -0.05, {"near": (1350, 600), "far": (1336, 606)}))
        bp = J["limbs"]["arm_near"][2]
        wrect(ctx, bp[0] - 6, bp[1] - 44, 60, 50, "book", (150, 70, 60), LINE, 3, seg=1)
    hud(ctx, t)


# ---- the final fight --------------------------------------------------------------------------------
EMAILS = ["URGENT: tonight", "need this by 9am", "where are we on this?", "?? ", "call me"]


def f1f2(ctx, t):
    rise = ease(prog(t, 109.4, 111.0))
    z = lerp(1.35, 1.6, ease(prog(t, 108, 123)))
    with Camera(z, 840, 500, shake=2 * prog(t, 119, 124)).apply(ctx):
        n = int(min(len(EMAILS), max(0, (t - 108.6) / 0.7 + 1)))
        scr = room(ctx, t, sky="night", lap_text=EMAILS[:n][-3:] if n else None, mug_n=1, lamp_on=1.0)
        glow(ctx, scr[0], scr[1], 300 + 60 * n, BLUE, 0.06 * n)
        P.villain(ctx, 1160, FY, scale=lerp(0.6, 1.55, rise), alpha=rise, grin=1.3, lean=-0.35,
                  reach=(860, 520) if t > 115 else None)
        # Theo's flyer on the wall: the final show is Saturday
        wrect(ctx, 420, 360, 110, 140, "flyer", (226, 222, 212), LINE, 3, seg=1)
        star_paper(ctx, 475, 410, 0.9, (220, 190, 120))
        draw_text(ctx, "SAT 10am", 475, 480, 20, (50, 46, 44), face="LuckiestGuy-Regular.ttf")
        expr = "neutral" if t < 109 else "worried"
        if rise > 0.5:
            expr = "anxious"
        if t > EVENTS["eyes_closed"]:
            expr = "closed"
        if t > EVENTS["eyes_open"]:
            expr = "determined"
        look = (1, 0.6) if not (116.0 < t < 118.4) else (-1, -0.4)  # a glance at the flyer
        him_at_desk(ctx, t, expr, look=look, hands=typing(t, 1.0 if t < 119 else 0.0))
    vline(ctx, "V6", 760, 250, 60)
    vline(ctx, "V7", 760, 250, 52)
    vline(ctx, "V8", 760, 330, 52)
    vline(ctx, "V9", 760, 250, 52)
    vline(ctx, "V10", 760, 250, 66)
    hud(ctx, t)


def f3(ctx, t):
    lt = t - EVENTS["shut"]
    off = ease(prog(t, EVENTS["lamp_off"], EVENTS["lamp_off"] + 0.1))
    with Camera(1.6, 840, 500).apply(ctx):
        shut = ease(prog(lt, 0.0, 0.2))
        room(ctx, t, sky="night", lap=1 - shut, mug_n=1, lamp_on=1 - off)
        wrect(ctx, 420, 360, 110, 140, "flyer", (226, 222, 212), LINE, 3, seg=1)
        star_paper(ctx, 475, 410, 0.9, (220, 190, 120))
        # made of screen light: with the light gone it comes apart into dim embers
        if off < 1:
            P.villain(ctx, 1160, FY, scale=1.55, alpha=1.0 - 0.6 * shut, grin=0.0, lean=-0.35)
        else:
            k = prog(t, EVENTS["lamp_off"] + 0.1, EVENTS["lamp_off"] + 2.2)
            for i in range(60):
                a = hrand("emb", i) * 2 * math.pi
                r = 40 + hrand("embr", i) * 300
                x = 1160 + math.cos(a) * r * (0.4 + k)
                y = FY - 260 + math.sin(a) * r * (0.6 + 0.4 * k) - 200 * k
                ctx.c.drawCircle(x, y, 5 * (1 - k), fill(RED, 0.8 * (1 - k)))
        reach = math.sin(math.pi * prog(t, EVENTS["shut"] - 0.3, EVENTS["lamp_off"] + 0.3))
        hands = {"near": lerp2((760, 634), (950, 500), reach), "far": (744, 638)}
        him_at_desk(ctx, t, "determined", look=(1, 0.2), hands=hands)
    black(ctx, 0.55 * off)
    hud(ctx, t)


# ---- the viewer's turn --------------------------------------------------------------------------------
def v1(ctx, t):
    b0, b1 = EVENTS["breath"]
    if b0 <= t <= b1 + 0.6:
        k = (t - b0) / 2.8  # one slow breath every 2.8 s
        r = 120 + 90 * (0.5 - 0.5 * math.cos(2 * math.pi * k))
        a = fade(t, b0, b1 + 0.6, 0.5, 0.6)
        glow(ctx, W / 2, 560, r * 2.2, GOLD, 0.18 * a)
        ctx.c.drawCircle(W / 2, 560, r, stroke(GOLD, 6, a))
        inhale = (k % 1) < 0.5
        draw_text(ctx, "in" if inhale else "out", W / 2, 576, 54, TEXT, a * 0.9)
    cap(ctx, "V1", y=300, size=60)
    cap(ctx, "V2", y=300, size=60)
    cap(ctx, "V3", y=300, size=60)


# ---- payoff ---------------------------------------------------------------------------------------------
def p1(ctx, t):
    wake = ease(prog(t, EVENTS["wake"], EVENTS["wake"] + 1.0))
    with Camera(1.6, 1150, 520).apply(ctx):
        room(ctx, t, sky="gold", desk=False, bed=True, window_gold=ease(prog(t, 138.0, 140.0)))
        clock_text(ctx, 1030, FY - 140, "SAT 8:00")
        if wake < 1:
            in_bed(ctx, "closed" if t < 139.4 else "smile")
        else:
            stretch = math.sin(math.pi * prog(t, 140.4, 142.4))
            hip, feet = standing(1180, FY, -1)
            HIM.draw(ctx, hip, -1, lean=0.02, feet=feet, expr="happy", look=(-1, -0.6),
                     hands=free_hands(HIM, hip, -1, 0.02, {"near": (1180 - 150, 640 - 170 * stretch), "far": (1180 + 150, 640 - 170 * stretch)}))
            P.wrect(ctx, 1250, FY - 136, 300, 46, "duvet", (60, 64, 92), LINE, 3, seg=3)
    hud(ctx, t, gold=t > 140.6)


def p2(ctx, t):
    wave = math.sin(t * 8) if t > EVENTS["wave"] else 0
    with Camera(1.6, 820, 560).apply(ctx):
        P.back_wall(ctx, rgb=(40, 32, 30))
        wrect(ctx, 300, 520, 1320, 30, "stage", (110, 80, 60), LINE, 4, seg=3)
        ctx.c.drawRect(skia.Rect.MakeXYWH(300, 550, 1320, 230), fill((70, 52, 42)))
        for x in (300, 1520):
            wrect(ctx, x, 120, 100, 400, ("curt", x), (120, 40, 40), LINE, 3, seg=2)
        glow(ctx, 960, 300, 400, GOLD, 0.35)
        cone(ctx, (960, 80), (800, 520), (1120, 520), (255, 230, 170), 0.16)
        hipT, feetT = standing(960, 520, -1, THEO.scale)
        JT = THEO.draw(ctx, hipT, -1, lean=0.04, feet=feetT, expr="happy", look=(-1, 0.8), mouth_open=talk("theo", t),
                       hands=free_hands(THEO, hipT, -1, 0.04, {"near": (900, 330 + 20 * wave) if t > EVENTS["wave"] else (920, 470),
                                                                "far": (1000, 470)}))
        star_paper(ctx, JT["head"][0], JT["head"][1] - 40, 1.2, GOLD)
        speech(ctx, t, "theo", JT["head"][0] + 60, JT["head"][1] - 80)
        for i, x in enumerate((420, 1260, 1460)):
            hp, ft = seated(x, 850, 1, floor_y=940)
            grey(f"aud{i}").draw(ctx, hp, 1, lean=0.04, feet=ft, expr="smile", look=(1, -1))
        hip, feet = seated(640, 850, 1, floor_y=940)
        HIM.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="happy", look=(1, -1),
                 hands=free_hands(HIM, hip, 1, 0.04, {"near": (700, 790),
                                                      "far": (556 + 10 * wave, 690) if t > EVENTS["wave"] + 0.4 else (690, 796)}))
    hud(ctx, t, gold=True)


def x1(ctx, t):
    off = ease(prog(t, EVENTS["theo_lamp"], EVENTS["theo_lamp"] + 0.1))
    with Camera(1.7, 860, 560).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        P.window(ctx, 1300, 220, 200, 200, "xwin", night=True)
        P.table(ctx, 640, 660, 360, key="tdesk")
        P.chair(ctx, 700, 700, 1, key="tchair")
        lamp(ctx, 940, 1 - off, key="tlamp", desk_y=660)
        closed = t > 158.4
        if not closed:
            wrect(ctx, 760, 640, 120, 20, "tbook", (226, 222, 212), LINE, 3, seg=1)
        else:
            wrect(ctx, 760, 640, 60, 20, "tbook2", (150, 70, 60), LINE, 3, seg=1)
        hipT, feetT = seated(700, 700, 1, THEO.scale, floor_y=FY)
        yawn = 155.0 < t < 156.2
        tl = 0.3 if not closed else 0.1
        JT = THEO.draw(ctx, hipT, 1, lean=tl, feet=feetT, expr="closed" if yawn else ("tired" if not closed else "smile"),
                       mouth_open=0.9 if yawn else 0, look=(1, 0.8),
                       hands=free_hands(THEO, hipT, 1, tl, {"near": (790, 640), "far": (776, 644)}))
        hx, hy = JT["head"]
        if not closed:
            battery_icon(ctx, hx - 32, hy - 96, 64, 24, 12, RED, ease(prog(t, 154.6, 155.0)), 3)
            if 155.6 < t < 157.6:
                villain_text(ctx, "push through.", 155.6, 157.6, hx + 40, hy - 130, 30)
        x = lerp(1240, 960, ease(prog(t, 155.4, 157.4)))
        reach = ease(prog(t, 157.6, 158.4)) * (1 - ease(prog(t, 160.4, 161.0)))
        stand(HIM, ctx, x, f=-1, lean=0.1 + 0.2 * reach, expr="smile", look=(-1, 0.6), step=(t * 1.6) % 1 if 155.4 < t < 157.4 else 0,
              hands={"near": lerp2((x - 20, 690), (840, 630), reach) if t < 159.4 else lerp2((x - 20, 690), (946, 640), ease(prog(t, 159.4, 160.0)))},
              free=True)
    black(ctx, 0.4 * off)


def title(ctx, t):
    a = fade(t, EVENTS["title"], 172.5, 0.8, 0.8)
    draw_text(ctx, "1%.", W / 2, 520, 230, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 170 + 340 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=46)
    cap(ctx, "T2", y=760, size=64, rgb=GOLD, glow_rgb=(170, 110, 20))


def stinger(ctx, t):
    ring = EVENTS["alarm3"] <= t
    a = ease(prog(t, 172.8, 173.2))
    jx = (hrand("al3", ctx.frame) - 0.5) * 6 if ring and int(t * 6) % 2 == 0 else 0
    clock_text(ctx, W / 2 + jx, 520, "MON 6:00", rgb=RED if ring else (200, 200, 206), size=40)
    vline(ctx, "V11", W / 2, 640, 50)
    black(ctx, 1 - a)


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5, "H6": h6, "H7": h7, "B1": b1,
    "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6, "G7": g7, "R1": r1, "R2": r2,
    "T1": t1, "T2": t2, "T3": t3, "C1": c1, "C2": c2, "C3": c3, "F1": f1f2, "F2": f1f2, "F3": f3,
    "V1": v1, "P1": p1, "P2": p2, "X1": x1, "TT": title, "ST": stinger,
}
CONTINUOUS = {"S01", "H1", "F2"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "ST":
        black(ctx, prog(t, DURATION - 0.6, DURATION))
