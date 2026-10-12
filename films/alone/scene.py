"""ALONE: picture. scene(ctx) draws any frame of the film."""
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
from timeline import SCENES, CUES, EVENTS, TYPED, TYPE_T0, TYPE_T1, DURATION, scene_at  # noqa: E402
from lines import LINES  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780  # floor line


def beanie(ctx, hx, hy, f, s):
    """Sam's one defining detail: a mustard beanie (gold = connection)."""
    p = poly_path([(hx - 50 * s, hy - 14 * s), (hx - 44 * s, hy - 46 * s), (hx, hy - 60 * s),
                   (hx + 44 * s, hy - 46 * s), (hx + 50 * s, hy - 14 * s)], closed=True, smooth=False)
    ctx.c.drawPath(p, fill((214, 160, 60)))
    ctx.c.drawPath(p, stroke(LINE, 3 * s))
    ctx.c.drawLine(hx - 50 * s, hy - 16 * s, hx + 50 * s, hy - 16 * s, stroke((170, 120, 40), 6 * s))


HIM = Character("him")
SAM = Character("sam", extra=beanie)


# ---- shared helpers -----------------------------------------------------------
def line_text(k):
    return LINES[k][2]


def say_window(k, pad=0.35):
    t0 = CUES[k]
    return t0, t0 + LEN.get(k, 1.8) + pad


def cap(ctx, k, y=190, rgb=TEXT, glow_rgb=None, hold=0.9):
    t0, t1 = say_window(k)
    caption(ctx, line_text(k), t0 - 0.15, t1 + hold, y=y, rgb=rgb, glow_rgb=glow_rgb)


def vline(ctx, k, x, y, size=46):
    t0, t1 = say_window(k)
    villain_text(ctx, line_text(k), t0 - 0.05, t1 + 0.3, x, y, size)


def day_label(ctx, s, a=1.0):
    draw_text(ctx, s, 60, LETTERBOX + 170, 38, (190, 190, 196), a, align="left")


def hud_main(ctx, value, rgb=TEXT, pop=0.0, a=1.0, x=56):
    P.hud(ctx, value, a=a, rgb=rgb, pop=pop, x=W - 268 - 56 if x is None else x)


def pop_at(t, t0, dur=0.35):
    return prog(t, t0, t0 + dur) if t0 <= t <= t0 + dur else 0.0


def kitchen_set(ctx, t, candle=1.0, night=True, rain=0.0, cake=True, plate=False):
    P.back_wall(ctx)
    P.floor(ctx, FY)
    P.window(ctx, 1380, 200, 220, 220, "kwin", rain=rain)
    P.wall_clock(ctx, 1040, 350, 21, 40, key="kclock")
    P.table(ctx, 800, 640, 360)
    P.chair(ctx, 740, 690, 1)
    flame = None
    if cake:
        flame = P.cake(ctx, 1040, 640, lit=candle)
    if plate:
        P.wrect(ctx, 990, 628, 110, 12, "plate", (180, 180, 186), LINE, 3, seg=3)
        P.wrect(ctx, 1010, 614, 70, 14, "food", (150, 120, 90), LINE, 2, seg=3)
    return flame


SEAT = seated(740, 690)
PHONE_TABLE = (858, 638)


def him_seated(ctx, expr="neutral", lean=0.28, hands=None, look=(1, 1), glowv=0.0, **kw):
    hip, feet = SEAT
    hands = hands or {"near": (832, 640), "far": (820, 642)}
    return HIM.draw(ctx, hip, 1, lean=lean, feet=feet, hands=hands, expr=expr, look=look, screen_glow=glowv, **kw)


# ---- phone screens ----------------------------------------------------------------
UI = P.PhoneUI(W / 2, 610, 420, 740)


def phone_frame(ctx, light=1.0, glow_rgb=BLUE):
    UI.body(ctx, light, glow_rgb)


def contacts_screen(ctx, t):
    x0, y0 = UI.x0 + 18, UI.y0 + 18
    draw_text(ctx, "Friends", x0 + 30, y0 + 100, 44, TEXT, align="left")
    draw_text(ctx, "214", x0 + UI.w - 70, y0 + 100, 44, (150, 190, 255), align="right", face="LuckiestGuy-Regular.ttf")
    scroll = ease(prog(t, 0.3, 4.2)) * 260
    names = ["Alex", "Ben", "Chloe", "Dan", "Ella", "Femi", "Grace", "Hugo", "Isla", "Jay", "Kim", "Leo", "Maya", "Nate"]
    with UI.screen(ctx):
        ctx.c.save()
        ctx.c.clipRect(skia.Rect.MakeLTRB(x0, y0 + 130, x0 + UI.w, y0 + UI.h))
        for i, n in enumerate(names):
            y = y0 + 170 + i * 86 - scroll
            wcircle(ctx, x0 + 60, y, 26, ("av", i), (64 + (i * 13) % 30, 72 + (i * 7) % 20, 92), None, 0)
            draw_text(ctx, n, x0 + 105, y + 11, 32, (215, 215, 222), align="left")
            ctx.c.drawLine(x0 + 30, y + 42, x0 + UI.w - 70, y + 42, stroke((50, 52, 62), 2))
        ctx.c.restore()


def chat_header(ctx, name="Sam"):
    x0, y0 = UI.x0 + 18, UI.y0 + 18
    ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, 130), fill((26, 28, 36)))
    wcircle(ctx, x0 + 60, y0 + 84, 26, "samav", (214, 160, 60), None, 0)
    draw_text(ctx, name, x0 + 100, y0 + 96, 36, TEXT, align="left")


def input_box(ctx, text, caret=True, send_ring=0.0, send_flash=0.0):
    x0, y1 = UI.x0 + 18, UI.y0 + UI.h - 18
    rrect(ctx, x0 + 20, y1 - 96, UI.w - 150, 66, 33, (40, 42, 52), (70, 72, 84), 2)
    shown = text + ("|" if caret and int(ctx.t * 2) % 2 == 0 else "")
    if shown:
        draw_text(ctx, shown, x0 + 46, y1 - 52, 32, TEXT, align="left")
    else:
        draw_text(ctx, "Message", x0 + 46, y1 - 52, 32, (110, 112, 124), align="left")
    sx, sy = x0 + UI.w - 92, y1 - 63
    if send_flash > 0:
        glow(ctx, sx, sy, 260 * send_flash, GOLD, 0.6 * send_flash)
    rgb = mix((70, 110, 200), GOLD, send_flash)
    wcircle(ctx, sx, sy, 30, "send", rgb if text else (60, 62, 72), None, 0)
    ctx.c.drawPath(poly_path([(sx - 12, sy - 12), (sx + 14, sy), (sx - 12, sy + 12), (sx - 6, sy)]), fill(TEXT))
    if send_ring > 0:
        ctx.c.drawCircle(sx, sy, 38 + 4 * math.sin(ctx.t * 9), stroke(TEXT, 3, 0.5 * send_ring))
    return (sx, sy)


def thumb(ctx, x, y, a=1.0):
    """His thumb coming in from below, tip exactly on (x, y)."""
    if a <= 0:
        return
    p = [(x - 34, UI.y0 + UI.h + 120), (x - 30, y + 30), (x - 22, y + 4), (x, y - 8), (x + 22, y + 4), (x + 30, y + 30), (x + 34, UI.y0 + UI.h + 120)]
    path = poly_path(wobble_points(ctx, p, "thumb", 1.0), smooth=True)
    ctx.c.drawPath(path, fill(SKIN, a))
    ctx.c.drawPath(path, stroke(LINE, 3, a))


# ---- scenes ------------------------------------------------------------------------
def s01(ctx, t):
    phone_frame(ctx, 1.0)
    with UI.screen(ctx):
        contacts_screen(ctx, t)
    cap(ctx, "N1")


def s02_s03(ctx, t):
    # S02 + S03 share one continuous shot
    candle = 1.0 - ease(prog(t, EVENTS["candle_out"], EVENTS["candle_out"] + 0.35))
    zoom = lerp(1.28, 1.4, ease(prog(t, 5, 22)))
    with Camera(zoom, 960, 560).apply(ctx):
        flame = kitchen_set(ctx, t, candle)
        on = 0.0
        if t >= EVENTS["first_tap"]:
            on = 1.0
        # villain born from the phone's glow: red wisps, then the shape grows behind the table
        born = ease(prog(t, 14.2, 16.6))
        if 14.0 <= t:
            for i in range(9):
                k = (t * 0.6 + hrand("wisp", i)) % 1.0
                a = (1 - k) * min(1, prog(t, 14.0, 14.8)) * (1 - prog(t, 16.6, 17.6))
                wx = PHONE_TABLE[0] + (1260 - PHONE_TABLE[0]) * k * 0.9 + math.sin(k * 9 + i) * 18
                wy = PHONE_TABLE[1] - 20 - k * 300
                ctx.c.drawCircle(wx, wy, 10 + 18 * k, blurred(fill(RED, 0.35 * a), 8))
            P.villain(ctx, 1270, FY, scale=lerp(0.25, 1.0, born), alpha=born, grin=ease(prog(t, 16.4, 17.4)),
                      lean=-0.15)
        P.phone_side(ctx, *PHONE_TABLE, on=on)
        expr = "neutral"
        if t > 10.4:
            expr = "sad"
        if t > 17.0:
            expr = "hurt"
        if 20.3 < t < 21.3:
            expr = "closed"
        look = (1, 1) if t > EVENTS["first_tap"] - 0.3 else (0.4, 0.2)
        hands = {"near": (832, 640), "far": (820, 642)}
        if 9.0 < t < 10.2:  # reaches and taps the phone
            k = math.sin(math.pi * prog(t, 9.0, 10.2))
            hands = {"near": lerp2((832, 640), (PHONE_TABLE[0] - 6, PHONE_TABLE[1] - 6), k), "far": (820, 642)}
        lean = 0.28
        if 20.3 < t < 21.3:  # leans in to blow the candle
            lean = 0.28 + 0.22 * math.sin(math.pi * prog(t, 20.3, 21.3))
        him_seated(ctx, expr, lean=lean, hands=hands, look=look, glowv=on * 0.8,
                   tear=prog(t, 18.6, 20.0) if t < 20.2 else 0.0, mouth_open=0.6 if 20.6 < t < 21.0 else 0)
    vline(ctx, "V1", 1270, 330)
    vline(ctx, "V2", 1270, 330)
    if t < 14:
        cap(ctx, "N2")
    P.hud(ctx, 0, a=ease(prog(t, EVENTS["hud_in"], EVENTS["hud_in"] + 0.4)), pop=pop_at(t, EVENTS["first_tap"]))


def s04(ctx, t):
    buzz_on = EVENTS["mum_buzz"] <= t < EVENTS["pickup"]
    lifted = ease(prog(t, EVENTS["pickup"], EVENTS["pickup"] + 0.6))
    with Camera(1.4, 900, 540).apply(ctx):
        kitchen_set(ctx, t, candle=0.0)
        P.villain(ctx, 1270, FY, scale=1.0, alpha=0.55, grin=1.0, lean=-0.15)
        J = HIM.joints(SEAT[0], 1, 0.18, 0, None, SEAT[1])
        held = (J["head"][0] + 62, J["head"][1] + 70)  # in front, below the chin
        ph_pos = lerp2(PHONE_TABLE, held, lifted)
        jx = (hrand("buzz", ctx.frame) - 0.5) * 6 if buzz_on else 0
        P.phone_side(ctx, ph_pos[0] + jx, ph_pos[1], on=1.0, angle=-75 * lifted)
        if buzz_on:
            draw_text(ctx, "Mum", PHONE_TABLE[0], PHONE_TABLE[1] - 40, 30, TEXT, 0.9)
        expr = "neutral"
        if t > 26.6:
            expr = "smile"
        if t > 29.0:
            expr = "hurt"
        talking = 26.9 <= t <= 26.9 + LEN.get("HIM", 1.9)
        mo = 0.5 * abs(math.sin(t * 15)) if talking else 0
        hands = {"near": ph_pos if lifted > 0 else (832, 640), "far": (ph_pos[0] - 8, ph_pos[1] + 8) if lifted > 0 else (820, 642)}
        him_seated(ctx, expr, lean=lerp(0.28, 0.18, lifted), hands=hands, look=(1, 1) if t < 26.6 else (1, -0.2),
                   mouth_open=mo, glowv=1.0)
        m0, m1 = say_window("MOM", 0.6)
        P.bubble(ctx, held[0] + 30, held[1] - 150, "happy birthday sweetheart! did you do something fun?", False, 26,
                 fade(t, m0, m1 + 0.4), 330)
        h0, h1 = say_window("HIM", 0.8)
        P.bubble(ctx, J["head"][0] - 40, J["head"][1] - 150, line_text("HIM"), True, 28, fade(t, h0, h1), 330,
                 rgb=(60, 60, 70))
    cap(ctx, "N3")
    P.hud(ctx, 0)


def s05(ctx, t):
    cap(ctx, "N4", y=H / 2 + 14)


def street_back(ctx, t, y=FY, lamps=(400, 1500)):
    for i in range(14):
        bx = -60 + i * 150
        bh = 200 + hrand("bld", i) * 260
        ctx.c.drawRect(skia.Rect.MakeXYWH(bx, y - bh - 60, 140, bh), fill((24, 24, 30)))
        for j in range(int(bh // 60)):
            if hrand("bw", i, j) > 0.55:
                ctx.c.drawRect(skia.Rect.MakeXYWH(bx + 20 + (j % 2) * 60, y - bh - 40 + j * 55, 26, 20), fill((70, 70, 60), 0.5))
    for lx in lamps:
        P.wrect(ctx, lx, y - 380, 10, 380, ("lamp", lx), GREY_D, LINE, 2, seg=2)
        glow(ctx, lx + 5, y - 380, 260, (255, 210, 140), 0.18)
        cone(ctx, (lx + 5, y - 380), (lx - 140, y), (lx + 150, y), (255, 210, 140), 0.10)


def held_phone_pose(hip_x, floor_y=FY, facing=1, step=0.0, lean=0.06):
    hip, feet = standing(hip_x, floor_y, facing, step=step)
    ph = (hip[0] + facing * 46, hip[1] - 58)
    return hip, feet, ph


def m1(ctx, t):
    lt = t - 34.0
    with Camera(lerp(1.45, 1.55, lt / 3.5), 960, 560).apply(ctx):
        street_back(ctx, t)
        P.floor(ctx, FY)
        P.wrect(ctx, 1180, FY - 300, 10, 300, "busstop", GREY_L, LINE, 2, seg=2)
        P.wrect(ctx, 1150, FY - 360, 70, 70, "bussign", (60, 90, 140), LINE, 3, seg=2)
        draw_text(ctx, "BUS", 1185, FY - 314, 26, TEXT)
        hip, feet, ph = held_phone_pose(900)
        HIM.draw(ctx, hip, 1, lean=0.08, feet=feet, hands={"near": ph, "far": (ph[0] - 6, ph[1] + 6)}, expr="neutral",
                 look=(1, 1), screen_glow=0.8)
        P.phone_held(ctx, *ph)
    day_label(ctx, "DAY 3")
    P.hud(ctx, 0, pop=pop_at(t, 34.4))


def m2(ctx, t):
    lt = t - 37.5
    with Camera(lerp(1.35, 1.42, prog(t, 37.5, 41)), 780, 560).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        P.table(ctx, 760, 640, 420, key="desk")
        P.desk_computer(ctx, 1000, 640)
        P.chair(ctx, 760, 690, 1, key="dchair")
        on = 1.0 if lt > 1.0 else 0.0
        P.phone_side(ctx, 842, 638, on=on, key="dph")
        hip, feet = seated(760, 690)
        look = (1, 1) if lt > 1.0 else (1, -0.3)
        HIM.draw(ctx, hip, 1, lean=0.3, feet=feet, hands={"near": (868, 632), "far": (856, 636)} if lt < 1.0 else
                 {"near": (836, 632), "far": (866, 634)}, expr="tired", look=look, screen_glow=0.5)
        P.villain(ctx, 520, FY, scale=0.8, alpha=ease(prog(lt, 0.8, 1.4)), lean=0.2)
    vline(ctx, "V3", 330, 330)
    day_label(ctx, "DAY 9")
    P.hud(ctx, 0, pop=pop_at(t, 38.6))


def m3(ctx, t):
    lt = t - 41.0
    with Camera(lerp(1.7, 1.85, lt / 4), 760, 620).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        P.window(ctx, 1240, 200, 200, 200, "bwin")
        P.bed(ctx, 560, FY, 560)
        P.wrect(ctx, 400, FY - 110, 120, 110, "nstand", GREY_D, LINE, 3, seg=2)
        P.digital_clock(ctx, 405, FY - 170, "2:14", rgb=(190, 190, 196))
        head = (650, FY - 128)
        hip = (840, FY - 106)
        J0 = HIM.joints(hip, -1, math.pi / 2 - 0.02)
        ph = (J0["shoulder"][0] - 40, J0["shoulder"][1] - 78)
        HIM.draw(ctx, hip, -1, lean=math.pi / 2 - 0.02, feet={"near": (hip[0] + 108, FY - 100), "far": (hip[0] + 100, FY - 104)},
                 hands={"near": (ph[0] + 14, ph[1] + 4), "far": (ph[0] - 14, ph[1] + 4)}, expr="tired", look=(0, -1.4),
                 screen_glow=1.0, bend={"leg_near": 1, "leg_far": 1, "arm_near": -1, "arm_far": -1})
        glow(ctx, ph[0], ph[1] + 40, 200, BLUE, 0.25)
        rrect(ctx, ph[0] - 26, ph[1] - 6, 52, 12, 3, (40, 40, 46), LINE, 2.5)
        ctx.c.drawRect(skia.Rect.MakeXYWH(ph[0] - 23, ph[1] + 4, 46, 3), fill(BLUE))
    cap(ctx, "N5")
    day_label(ctx, "DAY 15")
    P.hud(ctx, 0, pop=pop_at(t, 41.4))


def m4(ctx, t):
    lt = t - 45.0
    phone_frame(ctx, 1.0)
    x0, y0 = UI.x0 + 18, UI.y0 + 18
    with UI.screen(ctx):
        # a warm photo of friends together, without him
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w, UI.h), fill((52, 40, 36)))
        glow(ctx, UI.cx, UI.cy - 40, 420, (255, 190, 120), 0.35)
        for i in range(4):
            ctx.c.drawRect(skia.Rect.MakeXYWH(x0 + 8, y0 + 18 + i * 3, (UI.w - 52) * (1 if i else min(1, lt / 4)), 4),
                           fill(TEXT, 0.8 if i == 0 else 0))
        draw_text(ctx, "sam  ·  2h", x0 + 30, y0 + 70, 28, TEXT, align="left")
        for i, (fx, ex) in enumerate([(-100, "happy"), (0, "happy"), (100, "happy")]):
            bob = math.sin(t * 6 + i) * 3
            ch = SAM if i == 1 else Character(f"pal{i}", scale=0.7)
            if i == 1:
                ch = Character("sam_s", scale=0.7, extra=beanie)
            ch.draw(ctx, (UI.cx + fx, UI.cy + 150 + bob), 1 if fx <= 0 else -1, expr=ex,
                    hands={"near": (UI.cx + fx + 36, UI.cy + 36 + bob), "far": (UI.cx + fx - 36, UI.cy + 44 + bob)})
    vline(ctx, "V4", W / 2 + 470, 400)
    day_label(ctx, "DAY 21")
    P.hud(ctx, 0, pop=pop_at(t, 45.3))


def m5(ctx, t):
    lt = t - 49.0
    phone_frame(ctx, 1.0)
    x0, y0 = UI.x0 + 18, UI.y0 + 18
    with UI.screen(ctx):
        chat_header(ctx)
        draw_text(ctx, "3 years ago", UI.cx, y0 + 200, 24, (130, 132, 144))
        P.bubble(ctx, x0 + 26, y0 + 230, "see you around!", False, 32)
        seq = [(0.8, "h"), (1.1, "he"), (1.4, "hey"), (3.0, "he"), (3.25, "h"), (3.5, "")]
        typed = ""
        for tm, s in seq:
            if lt >= tm:
                typed = s
        input_box(ctx, typed)
    vline(ctx, "V5", W / 2 + 470, 420)
    day_label(ctx, "DAY 22")
    P.hud(ctx, 0, pop=pop_at(t, 49.3))


def m6(ctx, t):
    with Camera(1.32, 940, 560).apply(ctx):
        kitchen_set(ctx, t, cake=False, plate=False)
        P.wrect(ctx, 830, 628, 110, 12, "plate", (180, 180, 186), LINE, 3, seg=3)
        P.wrect(ctx, 850, 614, 70, 14, "food", (150, 120, 90), LINE, 2, seg=3)
        P.phone_side(ctx, 1000, 638, on=1.0)
        him_seated(ctx, "tired", lean=0.4, hands={"near": (856, 626), "far": (822, 640)},
                   look=(1, 1), glowv=0.6)
    cap(ctx, "N6")
    day_label(ctx, "DAY 30")
    P.hud(ctx, 0, pop=pop_at(t, 54.3))


def m7(ctx, t):
    lt = t - 58.0
    with Camera(lerp(1.1, 1.22, lt / 6), 1250, 520).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        P.window(ctx, 1260, 220, 300, 320, "rwin", rain=1.0, moon=False, sky=(22, 26, 38))
        hip, feet = standing(1180, FY)
        ph = (hip[0] + 36, hip[1] - 50)
        HIM.draw(ctx, hip, 1, lean=0.02, feet=feet, hands={"near": ph, "far": (ph[0] - 6, ph[1] + 6)}, expr="sad",
                 look=(1, -0.6))
        P.phone_held(ctx, *ph, on=0.15)
    day_label(ctx, "DAY 41")
    P.hud(ctx, 0, pop=pop_at(t, 58.3))


def rock(ctx, t):
    if 67.0 <= t < 69.0:
        phone_frame(ctx, 1.0)
        with UI.screen(ctx):
            draw_text(ctx, "9:47", UI.cx, UI.y0 + 210, 110, TEXT, face="LuckiestGuy-Regular.ttf")
            rrect(ctx, UI.x0 + 40, UI.y0 + 300, UI.w - 80, 120, 26, (48, 50, 62), None)
            draw_text(ctx, "Settings", UI.x0 + 70, UI.y0 + 344, 26, (160, 162, 172), align="left")
            draw_text(ctx, "Storage almost full.", UI.x0 + 70, UI.y0 + 390, 32, TEXT, align="left")
        P.hud(ctx, 1)
        return
    buzz_on = EVENTS["storage_buzz"] <= t < EVENTS["storage_buzz"] + 0.8
    grabbed = ease(prog(t, 65.4, 65.9))
    down = ease(prog(t, 71.6, EVENTS["face_down"]))
    with Camera(lerp(1.3, 1.45, ease(prog(t, 69, 76))), 860, 540).apply(ctx):
        kitchen_set(ctx, t, cake=False, rain=1.0)
        big = ease(prog(t, 69.4, 70.4)) if t >= 69 else 0.0
        if t >= 69:
            P.villain(ctx, 560, FY, scale=lerp(0.9, 1.35, big), alpha=big, grin=1.2, lean=0.35,
                      reach=(800, 560) if big > 0.6 else None)
        J = HIM.joints(SEAT[0], 1, 0.28, 0, None, SEAT[1])
        held = (J["head"][0] + 58, J["head"][1] + 50)
        if t < 69:
            pp = lerp2(PHONE_TABLE, held, grabbed)
            jx = (hrand("buzz2", ctx.frame) - 0.5) * 6 if buzz_on and grabbed < 0.05 else 0
            P.phone_side(ctx, pp[0] + jx, pp[1], on=1.0, angle=-70 * grabbed)
            hands = {"near": pp, "far": (820, 642)}
            expr = "hopeful" if t > 64.8 else "tired"
            him_seated(ctx, expr, hands=hands, look=(1, 0.5), glowv=1.0)
        else:
            pp = lerp2(held, PHONE_TABLE, down)
            P.phone_side(ctx, pp[0], pp[1], on=0.0 if down >= 1 else 1.0, face_down=down >= 1, angle=-70 * (1 - down))
            slump = ease(prog(t, 72.4, 73.6))
            him_seated(ctx, "hurt" if slump < 0.5 else "closed", lean=0.28 + 0.55 * slump,
                       hands={"near": pp if down < 1 else (PHONE_TABLE[0] + 2, PHONE_TABLE[1] - 4), "far": (830, 642)},
                       look=(1, 1), head_tilt=0.3 * slump)
    vline(ctx, "V6", 900, 230, size=52)
    if t < 69:
        P.hud(ctx, 1 if t >= 64.7 else 0, pop=pop_at(t, 64.7))
    else:
        flash = 1 - prog(t, 69.1, 70.5)
        P.hud(ctx, 0, rgb=RED if t < 72.5 else TEXT, pop=pop_at(t, 69.1))


def windows_grid():
    cells = []
    for r in range(3):
        for cidx in range(6):
            x = 300 + cidx * 230
            y = 300 + r * 210
            cells.append((r, cidx, x, y))
    return cells


def building(ctx, t, lit_mode="all", gold_cell=None, gold_k=0.0):
    ctx.c.drawRect(skia.Rect.MakeXYWH(240, 250, 1440, 700), fill((30, 30, 36)))
    ctx.c.drawRect(skia.Rect.MakeXYWH(240, 250, 1440, 700), stroke((60, 60, 70), 4))
    poses = ["sit", "stand", "lie", "sit", "stand", "sit"]
    for (r, cidx, x, y) in windows_grid():
        i = r * 6 + cidx
        is_lit = lit_mode == "all" or (lit_mode == "one" and (r, cidx) == gold_cell)
        P.wrect(ctx, x, y, 170, 150, ("bw", i), (16, 18, 26) if is_lit else (14, 14, 18), (70, 70, 80), 3, seg=2)
        if not is_lit:
            continue
        ctx.c.save()
        ctx.c.clipRect(skia.Rect.MakeXYWH(x, y, 170, 150))
        g = gold_k if (r, cidx) == gold_cell else 0.0
        rgb = mix(BLUE, GOLD, g)
        glow(ctx, x + 95, y + 80, 110, rgb, 0.35)
        pose = poses[(i * 5 + r) % 6]
        s = 0.34
        ch = Character(f"w{i}", scale=s)
        f = 1 if hrand("wf", i) > 0.5 else -1
        fl = y + 148
        if pose == "stand":
            hip, feet = standing(x + 85, fl, f, s)
        else:
            hip = (x + 85, fl - 34)
            feet = {"near": (x + 85 + f * 20, fl), "far": (x + 85 + f * 16, fl)}
        J = ch.joints(hip, f, 0.12, 0, None, feet)
        ph = (J["head"][0] + f * 24, J["head"][1] + 30)
        expr = "smile" if g > 0.6 else ("sad" if i % 3 == 0 else "tired")
        ch.draw(ctx, hip, f, lean=0.12, feet=feet, hands={"near": ph, "far": (ph[0] - f * 4, ph[1] + 3)},
                expr=expr, look=(1, 1) if g < 0.6 else (0, -1), screen_glow=1.0)
        ctx.c.drawRect(skia.Rect.MakeXYWH(ph[0] - 3, ph[1] - 18, 6, 20), fill(rgb))
        ctx.c.restore()
        tiny_rgb = GOLD if g > 0.5 else TEXT
        P.tiny_hud(ctx, x + 12, y + 30, "1" if g > 0.5 else "0", rgb=tiny_rgb, a=0.85)


def turn(ctx, t):
    if t < 81.0:
        lt = t - 76.0
        with Camera(lerp(1.3, 1.5, ease(prog(lt, 2.5, 5))), lerp(1000, 1260, ease(prog(lt, 0, 5))), 520).apply(ctx):
            P.back_wall(ctx)
            P.floor(ctx, FY)
            P.window(ctx, 1380, 200, 240, 260, "twin", rain=0.4, moon=False)
            # lights in the opposite building, seen through his window
            for i in range(6):
                ctx.c.drawRect(skia.Rect.MakeXYWH(1400 + (i % 3) * 70, 240 + (i // 3) * 90, 34, 28), fill(BLUE, 0.35))
            P.table(ctx, 600, 640, 300, key="ttable")
            x, ph = walk_x(760, max(0, min(lt, 3.0)), 180)
            step = ph if lt < 3.0 else 0.0
            hip, feet = standing(x, FY, 1, step=step)
            HIM.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="sad" if lt < 3.2 else "worried",
                     look=(1, -1.2) if lt > 3.2 else (1, 0))
        P.hud(ctx, 0)
        return
    lt = t - 81.0
    focus = (1305, 585)  # window (1, 4) centre
    z = lerp(3.4, 0.9, ease(prog(lt, 0.4, 6.5)))
    cx = lerp(focus[0], 960, ease(prog(lt, 0.4, 6.5)))
    cy = lerp(focus[1], 640, ease(prog(lt, 0.4, 6.5)))
    with Camera(z, cx, cy).apply(ctx):
        building(ctx, t)
    cap(ctx, "N7")
    cap(ctx, "N8")


def fight(ctx, t):
    if 110.0 <= t < 115.2:
        lt = t - 110.0
        dim = 1 - 0.35 * prog(t, 113.2, 113.6)
        phone_frame(ctx, dim)
        n = int(len(TYPED) * prog(t, TYPE_T0, TYPE_T1))
        typed = TYPED[:n]
        with UI.screen(ctx):
            chat_header(ctx)
            draw_text(ctx, "3 years ago", UI.cx, UI.y0 + 218, 24, (130, 132, 144))
            P.bubble(ctx, UI.x0 + 44, UI.y0 + 248, "see you around!", False, 32)
            sx, sy = input_box(ctx, typed, caret=t < 113.2, send_ring=prog(t, 113.2, 113.8))
        # thumb: types over the keyboard area, then hovers over send, trembling
        if t < TYPE_T1:
            k = (t * 7) % 1.0
            tx, ty = UI.cx - 120 + hrand("key", int(t * 7)) * 240, UI.y0 + UI.h - 200 + k * 10
        else:
            hover = ease(prog(t, TYPE_T1, 113.6))
            tx = lerp(UI.cx, sx, hover) + (math.sin(t * 40) * 2 if t > 113.6 else 0)
            ty = lerp(UI.y0 + UI.h - 200, sy - 70, hover)
        thumb(ctx, tx, ty)
        black(ctx, 0.0)
        return
    lt = t - 96.0
    rise = ease(prog(t, 100.6, 102.0))
    z = lerp(1.05, 1.22, ease(prog(t, 96, 110)))
    with Camera(z, 820, 500).apply(ctx):
        kitchen_set(ctx, t, cake=False)
        P.villain(ctx, 470, FY, scale=lerp(0.6, 1.5, rise), alpha=rise, grin=1.3, lean=0.4,
                  arms_up=0.6 * ease(prog(t, 106, 109)), reach=(780, 470) if t > 104 else None)
        J = HIM.joints(SEAT[0], 1, 0.22, 0, None, SEAT[1])
        held = (J["head"][0] + 58, J["head"][1] + 56)
        pick = ease(prog(t, 96.6, 97.6))
        pp = lerp2(PHONE_TABLE, held, pick)
        P.phone_side(ctx, *pp, on=prog(t, 97.0, 97.3), face_down=t < 97.0, angle=-70 * pick)
        expr = "worried"
        if t > 104:
            expr = "hurt"
        if t > 107.5:
            expr = "closed"
        him_seated(ctx, expr, lean=0.22, hands={"near": pp, "far": (pp[0] - 14, pp[1] + 4)}, look=(1, 0.6),
                   glowv=1.0 if t > 97.2 else 0)
    vline(ctx, "V7", 1180, 255, size=54)
    vline(ctx, "V8", 1180, 255, size=54)
    vline(ctx, "V9", 1180, 255, size=54)
    vline(ctx, "V10", 1180, 255, size=72)
    P.hud(ctx, 0)


def send_burst(ctx, t):
    lt = t - 115.2
    shake = 14 * (1 - prog(lt, 0, 0.5))
    with Camera(1.22, 820, 500, shake=shake).apply(ctx):
        kitchen_set(ctx, t, cake=False)
        crack = ease(prog(lt, 0.0, 0.7))
        if lt < 0.9:
            P.villain(ctx, 470, FY, scale=1.5, alpha=1.0, grin=0.0, lean=0.4, crack=crack)
        else:
            P.villain_shards(ctx, 470, FY, 1.5, prog(lt, 0.9, 2.6))
        J = HIM.joints(SEAT[0], 1, 0.22, 0, None, SEAT[1])
        held = (J["head"][0] + 58, J["head"][1] + 56)
        P.phone_side(ctx, *held, on=1.0, angle=-70, glow_rgb=GOLD)
        glow(ctx, held[0], held[1], 600 * (1 - prog(lt, 0, 1.4)), GOLD, 0.5)
        him_seated(ctx, "closed" if lt < 1.2 else "worried", lean=0.22,
                   hands={"near": held, "far": (held[0] - 8, held[1] + 8)}, look=(1, 0.6), glowv=1.0)
    flash = 1 - prog(lt, 0, 0.25)
    if flash > 0:
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((255, 236, 190), 0.55 * flash))
    P.hud(ctx, 0)


def calm(ctx, t):
    with Camera(lerp(1.3, 1.42, prog(t, 118, 124)), 860, 520).apply(ctx):
        kitchen_set(ctx, t, cake=False)
        J = HIM.joints(SEAT[0], 1, 0.22, 0, None, SEAT[1])
        held = (J["head"][0] + 58, J["head"][1] + 56)
        P.phone_side(ctx, *held, on=1.0, angle=-70)
        breathe = math.sin(math.pi * prog(t, 119.5, 121.5))
        expr = "closed" if 119.4 < t < 121.6 else "worried"
        him_seated(ctx, expr, lean=0.22 - 0.06 * breathe, hands={"near": held, "far": (held[0] - 8, held[1] + 8)},
                   look=(1, 0.6), glowv=1.0)
        draw_text(ctx, "Delivered", held[0] + 30, held[1] - 120, 30, (170, 172, 184), fade(t, 118.6, 124.0, 0.6, 0.2))
    P.hud(ctx, 0)


def payoff_phone(ctx, t):
    phone_frame(ctx, 1.0, glow_rgb=mix(BLUE, GOLD, prog(t, 127.0, 128.0)))
    with UI.screen(ctx):
        chat_header(ctx)
        draw_text(ctx, "3 years ago", UI.cx, UI.y0 + 182, 22, (130, 132, 144))
        P.bubble(ctx, UI.x0 + 44, UI.y0 + 196, "see you around!", False, 30)
        draw_text(ctx, "today", UI.cx, UI.y0 + 292, 22, (130, 132, 144))
        bh = P.bubble(ctx, UI.x0 + UI.w - 44, UI.y0 + 306, TYPED, True, 32)
        draw_text(ctx, "Read" if t >= EVENTS["read"] else "Delivered", UI.x0 + UI.w - 50, UI.y0 + 306 + bh + 26, 22,
                  (140, 142, 154), align="right")
        y = UI.y0 + 306 + bh + 44
        if EVENTS["typing"][0] <= t < EVENTS["typing"][1]:
            rrect(ctx, UI.x0 + 44, y, 110, 56, 28, (58, 58, 66))
            for i in range(3):
                a = 0.4 + 0.6 * max(0, math.sin(t * 8 - i * 0.9))
                ctx.c.drawCircle(UI.x0 + 72 + i * 27, y + 28, 7, fill(TEXT, a))
        a1 = ease(prog(t, EVENTS["reply1"], EVENTS["reply1"] + 0.3))
        h1 = P.bubble(ctx, UI.x0 + 44, y, "i thought you forgot about me.", False, 32, a1, rgb=(120, 92, 40)) if a1 > 0 else 0
        a2 = ease(prog(t, EVENTS["reply2"], EVENTS["reply2"] + 0.3))
        if a2 > 0:
            P.bubble(ctx, UI.x0 + 44, y + (h1 or 70) + 14, "coffee saturday?", False, 32, a2, rgb=(120, 92, 40))
        input_box(ctx, "", caret=False)
    if t >= EVENTS["reply1"]:
        P.hud(ctx, 1, rgb=GOLD, pop=pop_at(t, EVENTS["reply1"]))
    else:
        P.hud(ctx, 0)


def smile(ctx, t):
    with Camera(lerp(1.5, 1.6, prog(t, 130, 134)), 840, 520).apply(ctx):
        kitchen_set(ctx, t, cake=False)
        J = HIM.joints(SEAT[0], 1, 0.22, 0, None, SEAT[1])
        held = (J["head"][0] + 58, J["head"][1] + 56)
        glow(ctx, held[0], held[1], 420, GOLD, 0.35)
        P.phone_side(ctx, *held, on=1.0, angle=-70, glow_rgb=GOLD)
        him_seated(ctx, "happy" if t > 130.6 else "hopeful", lean=0.18, hands={"near": held, "far": (held[0] - 8, held[1] + 8)},
                   look=(1, 0.6), glowv=1.0)
    cap(ctx, "N9")
    P.hud(ctx, 1, rgb=GOLD)


def cafe(ctx, t):
    lt = t - 134.0
    with Camera(lerp(1.55, 1.65, lt / 6), 960, 560).apply(ctx):
        ctx.c.drawRect(skia.Rect.MakeLTRB(-600, 0, W + 600, FY), fill((34, 28, 24)))
        glow(ctx, 960, 320, 900, GOLD, 0.25)
        P.wrect(ctx, 620, 160, 680, 330, "cwin", (90, 70, 40), (120, 100, 70), 5, seg=4)
        glow(ctx, 960, 320, 420, (255, 220, 150), 0.45)
        wline(ctx, (960, 160), (960, 490), "cwv", (120, 100, 70), 5)
        P.floor(ctx, FY, rgb=(90, 74, 56))
        P.table(ctx, 860, 640, 200, key="ctable")
        P.wrect(ctx, 890, 606, 34, 34, "cup1", (230, 226, 216), LINE, 3, seg=2)
        P.wrect(ctx, 1000, 606, 34, 34, "cup2", (230, 226, 216), LINE, 3, seg=2)
        P.chair(ctx, 800, 690, 1, key="cc1")
        P.chair(ctx, 1120, 690, -1, key="cc2")
        laugh = lambda ph: 0.5 + 0.5 * math.sin(t * 9 + ph)
        lk = 1 if 1.0 < lt < 4.0 else 0
        hip, feet = seated(800, 690, 1)
        HIM.draw(ctx, (hip[0], hip[1] - 3 * laugh(0) * lk), 1, lean=0.12 + 0.05 * lk * laugh(0), feet=feet,
                 hands={"near": (900, 618), "far": (880, 640)}, expr="happy", mouth_open=0.7 * lk * laugh(0), look=(1, 0))
        hip2, feet2 = seated(1120, 690, -1)
        SAM.draw(ctx, (hip2[0], hip2[1] - 3 * laugh(1) * lk), -1, lean=0.12 + 0.05 * lk * laugh(1), feet=feet2,
                 hands={"near": (1022, 618), "far": (1040, 640)}, expr="happy", mouth_open=0.8 * lk * laugh(1), look=(-1, 0))


def mirror(ctx, t):
    cell = (0, 3)
    if t < 145.0:
        lt = t - 140.0
        with Camera(1.0, 960, 540).apply(ctx):
            ctx.c.drawRect(skia.Rect.MakeXYWH(900, 120, 760, 660), fill((26, 26, 32)))
            for r in range(3):
                for cidx in range(3):
                    x, y = 960 + cidx * 230, 170 + r * 200
                    lit = (r, cidx) == cell[0:1] + (0,) if False else (r == 0 and cidx == 1)
                    P.wrect(ctx, x, y, 160, 130, ("mw", r, cidx), (16, 18, 26), (60, 60, 70), 3, seg=2)
                    if lit:
                        glow(ctx, x + 80, y + 70, 120, BLUE, 0.4)
                        ch = Character("mw", scale=0.3)
                        ch.draw(ctx, (x + 80, y + 95), -1, lean=0.15, expr="sad", look=(-1, 1), screen_glow=1.0,
                                feet={"near": (x + 66, y + 126), "far": (x + 70, y + 126)},
                                hands={"near": (x + 58, y + 76), "far": (x + 62, y + 79)})
                        ctx.c.drawRect(skia.Rect.MakeXYWH(x + 55, y + 60, 5, 18), fill(BLUE))
                        P.tiny_hud(ctx, x + 12, y + 28, "0", a=0.85)
            street_back(ctx, t, lamps=(300,))
            ctx.c.drawRect(skia.Rect.MakeXYWH(900, 120, 760, 660), stroke((60, 60, 70), 4))
            P.floor(ctx, FY)
            x, ph = walk_x(200, min(lt, 2.5), 220)
            step = ph if lt < 2.5 else 0.0
            hip, feet = standing(x, FY, 1, step=step)
            if lt < 3.2:
                HIM.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="smile", look=(1, -1) if lt > 2.5 else (1, 0))
            else:
                k = ease(prog(lt, 3.2, 3.8))
                php = (hip[0] + 44, lerp(hip[1] - 4, hip[1] - 56, k))
                HIM.draw(ctx, hip, 1, lean=0.06, feet=feet, hands={"near": php, "far": (php[0] - 6, php[1] + 6)},
                         expr="smile", look=(1, 1) if lt < 4.3 else (1, -1))
                P.phone_held(ctx, *php, on=k)
        return
    lt = t - 145.0
    with Camera(1.0, 960, 540).apply(ctx):
        x, y, w, h = 560, 200, 800, 650
        P.wrect(ctx, x, y, w, h, "mwin_big", (16, 18, 26), (60, 60, 70), 6, seg=3)
        g = ease(prog(t, EVENTS["mirror_gold"], EVENTS["mirror_gold"] + 0.5))
        rgb = mix(BLUE, GOLD, g)
        glow(ctx, x + w / 2, y + h / 2, 500, rgb, 0.4)
        ch = Character("mw", scale=1.3)
        fl = y + h - 10
        ch.draw(ctx, (x + w / 2 + 40, fl - 140), -1, lean=0.15, expr="smile" if g > 0.6 else "sad", look=(-1, 1),
                screen_glow=1.0, feet={"near": (x + w / 2 - 30, fl), "far": (x + w / 2 - 14, fl)},
                hands={"near": (x + w / 2 - 34, fl - 300), "far": (x + w / 2 - 20, fl - 290)})
        rrect(ctx, x + w / 2 - 52, fl - 362, 22, 74, 5, (40, 40, 46), LINE, 2.5)
        ctx.c.drawRect(skia.Rect.MakeXYWH(x + w / 2 - 56, fl - 356, 5, 64), fill(rgb))
        P.tiny_hud(ctx, x + 30, y + 70, "1" if g > 0.5 else "0", rgb=GOLD if g > 0.5 else TEXT)
        if g > 0:
            draw_text(ctx, "1", x + 30, y + 70, 70 * (1 + 0.3 * pop_at(t, EVENTS["mirror_gold"], 0.4)), GOLD, g,
                      align="left", face="LuckiestGuy-Regular.ttf", glow_rgb=GOLD)


def title(ctx, t):
    a = fade(t, EVENTS["title"], DURATION, 0.8, 1.2)
    draw_text(ctx, "ALONE", W / 2, 520, 210, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 290 + 580 * i / 10, 560 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    t0, t1 = say_window("N10")
    caption(ctx, line_text("N10"), t0 - 0.15, DURATION - 0.3, y=670, size=46)
    t0, t1 = say_window("N11")
    caption(ctx, line_text("N11"), t0 - 0.1, DURATION - 0.3, y=750, size=60, rgb=GOLD, glow_rgb=(170, 110, 20))


DISPATCH = {
    "S01": s01, "S02": s02_s03, "S03": s02_s03, "S04": s04, "S05": s05,
    "M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5, "M6": m6, "M7": m7,
    "R1": rock, "R2": rock, "R3": rock, "T1": turn, "T2": turn,
    "F1": fight, "F2": fight, "F3": send_burst, "F4": calm,
    "P1": payoff_phone, "P2": smile, "P3": cafe, "X1": mirror, "X2": mirror, "TT": title,
}
# soft starts: shots that begin with a cut fade up from black over 0.1 s (continuous shots don't)
CONTINUOUS = {"S03"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.1))
    if sid == "S01":
        black(ctx, 1 - prog(t, 0, 0.6))
    if sid == "TT":
        black(ctx, prog(t, DURATION - 1.0, DURATION))
