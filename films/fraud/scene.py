"""FRAUD.: picture. scene(ctx) draws any frame of the film.

The device: his name badge. Only he can see it flicker red: FRAUD. REVIEW IN 90 DAYS counts down to his
probation review, where he is sure they will find out. The turn: in the lift, every badge flickers FRAUD.
The lesson drawn: what he thought (every eye on him) and what was true (every eye on itself).
Gold appears only when the review reads PASSED.
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
from studio.extras import speech as _speech, talk as _talk, free_hands, office  # noqa: E402
from timeline import SCENES, CAPS, CUES, BUBBLES, EVENTS, DURATION, scene_at, review_at, review_changed  # noqa: E402
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
SCARF = (128, 80, 110)
LANYARD = (70, 90, 130)
CARD = (232, 230, 220)
STEEL = (88, 92, 102)


def glasses(ctx, hx, hy, f, s):
    for k in (-1, 1):
        cx = hx + f * 18 * s + k * 13 * s
        ctx.c.drawCircle(cx, hy - 4 * s, 9 * s, stroke(LINE, 2.5 * s))
    ctx.c.drawLine(hx + f * 18 * s - 4 * s, hy - 4 * s, hx + f * 18 * s + 4 * s, hy - 4 * s, stroke(LINE, 2.5 * s))


def scarf(ctx, hx, hy, f, s):
    y = hy + 46 * s
    ctx.c.drawPath(poly_path([(hx - 26 * s, y - 6 * s), (hx + 26 * s, y - 6 * s), (hx + 22 * s, y + 10 * s), (hx - 22 * s, y + 10 * s)], smooth=True),
                   fill(SCARF))
    ctx.c.drawPath(poly_path([(hx - f * 8 * s, y + 4 * s), (hx - f * 14 * s, y + 40 * s), (hx - f * 2 * s, y + 38 * s), (hx + f * 4 * s, y + 6 * s)]),
                   fill(mix(SCARF, (0, 0, 0), 0.2)))


HIM = Character("him")
BOSS = Character("boss", skin=(176, 172, 166), extra=glasses)
MIRA = Character("mira", skin=(190, 186, 178), extra=scarf)


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


def pop_at(t, t0, dur=0.35):
    if t0 is None:
        return 0.0
    return prog(t, t0, t0 + dur) if t0 <= t <= t0 + dur else 0.0


def hud(ctx, t, a=1.0):
    v = review_at(t)
    if v is None:
        return
    rgb = GOLD if v == "PASSED" else (RED if v in ("1 DAY", "TODAY") else TEXT)
    label_ = "REVIEW" if v == "PASSED" else "REVIEW IN" if v != "TODAY" else "REVIEW"
    P.hud(ctx, v, label=label_, a=a * prog(t, EVENTS["flicker"], EVENTS["flicker"] + 0.4), rgb=rgb, pop=pop_at(t, review_changed(t)))


def stand(ch, ctx, x, f=1, lean=0.04, step=0.0, free=False, **kw):
    hip, feet = standing(x, FY, f, ch.scale, step=step)
    if free and kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def sit(ch, ctx, x, f=1, lean=0.1, seat_y=690, chair=True, **kw):
    if chair:
        P.chair(ctx, x, seat_y, f, key=("ch", ch.name, x))
    hip, feet = seated(x, seat_y, f, ch.scale)
    if kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


# ---- the device: the badge --------------------------------------------------------------------
def badge(ctx, J, fraud=0.0, s=1.0, a=1.0, name_rgb=(60, 80, 120)):
    """Lanyard and card on his chest. fraud: 0..1, the red word only he can see."""
    f = J["facing"]
    sx, sy = J["shoulder"]
    cx, cy = sx + f * 14 * s, sy + 50 * s
    c = ctx.c
    c.drawPath(poly_path([(sx - f * 6 * s, sy - 8 * s), (cx, cy - 18 * s), (sx + f * 18 * s, sy - 6 * s)], closed=False), stroke(LANYARD, 3 * s, a))
    w, h = 26 * s, 34 * s
    rrect(ctx, cx - w / 2, cy - h / 2, w, h, 3 * s, CARD, LINE, 2 * s, a=a)
    if fraud < 1:
        c.drawRect(skia.Rect.MakeXYWH(cx - w / 2 + 3 * s, cy - h / 2 + 3 * s, w - 6 * s, 7 * s), fill(name_rgb, a * (1 - fraud)))
        c.drawCircle(cx, cy + 1 * s, 5 * s, fill((180, 176, 168), a * (1 - fraud)))
        c.drawLine(cx - 8 * s, cy + 10 * s, cx + 8 * s, cy + 10 * s, stroke((150, 146, 140), 2 * s, a * (1 - fraud)))
    if fraud > 0:
        glow(ctx, cx, cy, 40 * s, RED, 0.5 * fraud * a)
        c.drawRect(skia.Rect.MakeXYWH(cx - w / 2 + 2 * s, cy - h / 2 + 2 * s, w - 4 * s, h - 4 * s), fill((60, 10, 12), fraud * a))
        draw_text(ctx, "FRAUD", cx, cy + 4 * s, 10 * s, RED, fraud * a, face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
    return (cx, cy)


def flick(t, t0, dur=None, rate=13.0):
    """A flicker that settles on: 0..1 with on/off stutter in its first 0.6 s."""
    if t < t0:
        return 0.0
    if dur is not None and t > t0 + dur:
        return max(0.0, 1 - (t - t0 - dur) / 0.4)
    if t < t0 + 0.6:
        return 1.0 if math.sin((t - t0) * rate * 2 * math.pi) > -0.2 else 0.15
    return 1.0


# ---- sets ----------------------------------------------------------------------------------------
def home(ctx, day=1.0):
    P.back_wall(ctx, rgb=mix((20, 20, 24), (62, 62, 70), day))
    P.floor(ctx, FY)
    P.window(ctx, 1300, 200, 260, 240, "hwin", night=day < 0.5, sky=mix((26, 30, 44), (170, 190, 214), day))
    if day > 0:
        cone(ctx, (1430, 330), (900, FY), (1300, FY), (220, 226, 240), 0.14 * day)


def lobby(ctx):
    P.back_wall(ctx, rgb=(44, 46, 52))
    ctx.c.drawRect(skia.Rect.MakeLTRB(-600, FY, W + 600, H + 400), fill((60, 62, 70)))
    P.floor(ctx, FY)
    for i in range(10):
        ctx.c.drawLine(-200 + i * 260, FY, -400 + i * 300, H, stroke((72, 74, 82), 2))
    # the lift doors
    wrect(ctx, 1500, 360, 320, 420, "liftframe", (70, 72, 80), LINE, 4, seg=2)
    for k in range(2):
        wrect(ctx, 1514 + k * 148, 374, 144, 406, ("liftdoor", k), STEEL, LINE, 3, seg=2)
    draw_text(ctx, "LIFT", 1660, 340, 30, (190, 190, 196), face="LuckiestGuy-Regular.ttf")
    # a plant
    wrect(ctx, 260, 700, 80, 80, "pot", (90, 74, 60), LINE, 3, seg=2)
    for i in range(6):
        a = -math.pi / 2 + (i - 2.5) * 0.35
        ctx.c.drawLine(300, 700, 300 + math.cos(a) * 140, 700 + math.sin(a) * 140, stroke((70, 100, 70), 12))


MIRROR = (700, 230, 400, 520)


def mirror_scene(ctx, t, fraud, smile=False, step=0.0, x=None):
    """Him in front of the lobby mirror; his reflection inside it. Returns the reflection joints."""
    lobby(ctx)
    mx, my, mw, mh = MIRROR
    wrect(ctx, mx - 14, my - 14, mw + 28, mh + 28, "mframe", (120, 110, 90), LINE, 4, seg=2)
    ctx.c.drawRect(skia.Rect.MakeXYWH(mx, my, mw, mh), fill((70, 80, 92)))
    ctx.c.drawLine(mx + 40, my + 30, mx + 140, my + 130, stroke((255, 255, 255), 6, 0.12))
    x = x if x is not None else 620
    pin = ease(prog(t, EVENTS["pin"] - 0.6, EVENTS["pin"])) if t < 100 else 1.0
    # the reflection, facing back out of the glass
    rx = x + 120
    ctx.c.save()
    ctx.c.clipRect(skia.Rect.MakeXYWH(mx, my, mw, mh))
    me = Character("mirror_him", skin=(206, 202, 190))
    hip, feet = standing(rx, my + mh + 60, -1)
    JR = me.draw(ctx, hip, -1, lean=0.02, feet=feet, expr="smile" if smile else ("worried" if fraud > 0.5 else "neutral"),
                 look=(-1, 0.3))
    badge(ctx, JR, fraud=fraud, a=0.9)
    ctx.c.restore()
    hip, feet = standing(x, FY, 1, step=step)
    J = HIM.draw(ctx, hip, 1, lean=0.02, feet=feet, expr="smile" if smile else ("worried" if fraud > 0.5 else "neutral"),
                 look=(1, 0.3), hands=free_hands(HIM, hip, 1, 0.02, {"near": (x + 26, hip[1] - 70)}) if pin < 1 else None)
    badge(ctx, J, fraud=0.0)
    return JR, J


def workplace(ctx, desk_x=600, night=False):
    office(ctx, desk_x=desk_x, night=night)


def meeting_room(ctx, slide=None, slide_a=1.0):
    P.back_wall(ctx, rgb=(34, 36, 42))
    P.floor(ctx, FY)
    wrect(ctx, 1380, 220, 420, 260, "screen", (230, 232, 236), LINE, 4, seg=2)
    if slide:
        slide(ctx, 1590, 350, slide_a)
    P.table(ctx, 360, 640, 1000, key="mtable")


def bulb(ctx, x, y, s=1.0, a=1.0, rgb=(240, 220, 150)):
    c = ctx.c
    c.drawCircle(x, y, 22 * s, fill(rgb, a))
    c.drawCircle(x, y, 22 * s, stroke(LINE, 3 * s, a))
    c.drawRect(skia.Rect.MakeXYWH(x - 10 * s, y + 18 * s, 20 * s, 14 * s), fill((150, 150, 156), a))
    for i in range(5):
        ang = -math.pi / 2 + (i - 2) * 0.5
        c.drawLine(x + math.cos(ang) * 30 * s, y + math.sin(ang) * 30 * s, x + math.cos(ang) * 42 * s, y + math.sin(ang) * 42 * s,
                   stroke(LINE, 3 * s, a))


def notepad(ctx, x, y, doodle=True, a=1.0):
    rrect(ctx, x - 50, y - 12, 100, 14, 3, (236, 232, 214), LINE, 2, a=a)
    if doodle:
        bulb(ctx, x, y - 60, 0.7, a * 0.9)


def lift_inside(ctx, t, flicker=0.0):
    c = ctx.c
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), fill(mix((74, 78, 88), (30, 30, 34), flicker)))
    for i in range(6):
        c.drawLine(-200 + i * 400, 120, -200 + i * 400, FY, stroke((90, 94, 104), 3))
    c.drawRect(skia.Rect.MakeLTRB(-600, FY, W + 600, H + 400), fill((50, 52, 58)))
    P.floor(ctx, FY)
    wrect(ctx, 1640, 170, 140, 70, "lcd", (20, 20, 24), LINE, 3, seg=1)
    floor_n = min(9, 1 + int(max(0, t - 68.4) * 0.6))
    draw_text(ctx, str(floor_n), 1710, 225, 50, (230, 160, 90), face="LuckiestGuy-Regular.ttf")
    glow(ctx, 960, 60, 700, (240, 240, 230), 0.25 * (1 - flicker))


def boss_office(ctx, warm=0.0):
    P.back_wall(ctx, rgb=mix((40, 40, 46), (70, 60, 50), warm))
    P.floor(ctx, FY)
    P.window(ctx, 1440, 180, 300, 260, "bwin", night=False, moon=False, sky=mix((150, 170, 196), (250, 196, 130), warm))
    if warm > 0:
        glow(ctx, 1590, 310, 600, GOLD, 0.3 * warm)
    P.table(ctx, 820, 620, 420, key="bdesk")


# ---- the hook ---------------------------------------------------------------------------------------
def s01(ctx, t):
    UI = P.PhoneUI(W / 2, 650, 480, 740)
    UI.body(ctx, 1.0)
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, 110), fill((26, 28, 36)))
        draw_text(ctx, "Inbox", x0 + 40, y0 + 76, 40, (170, 176, 196), align="left")
        a = ease(prog(t, EVENTS["email"], EVENTS["email"] + 0.3))
        rrect(ctx, x0 + 30, y0 + 160, UI.w - 96, 260, 18, (44, 48, 60), None, a=a)
        draw_text(ctx, "Congratulations!", x0 + 56, y0 + 230, 44, TEXT, a, align="left", face="LuckiestGuy-Regular.ttf")
        draw_text(ctx, "You got the job.", x0 + 56, y0 + 290, 40, TEXT, a, align="left")
        draw_text(ctx, "Start: Monday, 9:00", x0 + 56, y0 + 350, 32, (170, 176, 196), a, align="left")
    cap(ctx, "C1", y=180)


def h1(ctx, t):
    jump = EVENTS["jump"]
    k = math.sin(math.pi * prog(t, jump, jump + 0.6))
    with Camera(1.7, 960, 560).apply(ctx):
        home(ctx, 1.0)
        hip, feet = standing(960, FY, 1)
        dy = -90 * k
        hip = (hip[0], hip[1] + dy)
        feet = {kk: (v[0], v[1] + dy) for kk, v in feet.items()}
        frozen = t > EVENTS["freeze"]
        arms = {"near": (1010, 420 + dy), "far": (920, 430 + dy)} if 3.8 < t < EVENTS["freeze"] + 0.3 else None
        HIM.draw(ctx, hip, 1, lean=0.02, feet=feet, expr="happy" if not frozen else "worried", look=(1, -0.4) if not frozen else (0.4, 0.6),
                 hands=free_hands(HIM, hip, 1, 0.02, arms) if arms else None)
    cap(ctx, "C2")


def h2(ctx, t):
    fr = flick(t, EVENTS["flicker"])
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0, t1))
    zin = ease(prog(t, 9.2, 9.8)) * (1 - ease(prog(t, 10.9, 11.5)))
    with Camera(lerp(lerp(1.5, 1.8, prog(t, 7.5, 14)), 4.2, zin), lerp(880, 726, zin), lerp(520, 612, zin)).apply(ctx):
        JR, J = mirror_scene(ctx, t, fr)
        bx, by = JR["shoulder"][0] - 14, JR["shoulder"][1] + 50
        if born > 0:
            for i in range(6):
                kk = (t * 0.6 + hrand("wisp", i)) % 1.0
                a = (1 - kk) * born * (1 - prog(t, t1, t1 + 0.8))
                ctx.c.drawCircle(lerp(bx, 470, kk) + (hrand("wx", i) - 0.5) * 40, by - kk * 200, 8 + 14 * kk, blurred(fill(RED, 0.35 * a), 8))
            P.villain(ctx, 470, FY, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 11.4, 12.0)), lean=0.2)
            # draw him again over the villain
            hip, feet = standing(620, FY, 1)
            J = HIM.draw(ctx, hip, 1, lean=0.02, feet=feet, expr="worried", look=(1, 0.3))
            badge(ctx, J, 0.0)
    vline(ctx, "V1", 1460, 300, 58)
    hud(ctx, t)


def h3(ctx, t):
    cover = ease(prog(t, EVENTS["cover"] - 0.3, EVENTS["cover"]))
    with Camera(1.7, 960, 540).apply(ctx):
        workplace(ctx, desk_x=1300)
        shake = 1.0 - ease(prog(t, 15.6, 16.0))
        hs = (980 + math.sin(t * 18) * 6 * shake, 600)
        JB = stand(BOSS, ctx, 1100, f=-1, lean=0.04, expr="happy", look=(-1, 0), mouth_open=talk("boss", t),
                   hands={"near": hs} if t < 16.0 else None, free=True)
        badge(ctx, JB, 0.0, name_rgb=(120, 80, 80))
        hip, feet = standing(860, FY, 1)
        J0 = HIM.joints(hip, 1, 0.04)
        bpos = (J0["shoulder"][0] + 14, J0["shoulder"][1] + 50)
        near = hs if t < 16.0 else lerp2((hip[0] + 40, hip[1] - 20), bpos, cover)
        J = HIM.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="smile" if t < 16.4 else "worried", look=(1, 0) if t < 16.4 else (0.3, 0.8),
                     hands=free_hands(HIM, hip, 1, 0.04, {"near": near}) if (t < 16.0 or cover > 0) else None, near_arm_front=True)
        badge(ctx, J, flick(t, 16.4) * (1 - 0.0))
        if cover > 0.9:  # his hand over the card, drawn again on top
            hp = J["limbs"]["arm_near"][2]
            ctx.c.drawCircle(hp[0], hp[1], 11, fill(SKIN))
            ctx.c.drawCircle(hp[0], hp[1], 11, stroke(LINE, 3))
        speech(ctx, t, "boss", JB["head"][0], JB["head"][1] - 70)
    vline(ctx, "V2", 520, 300, 54)
    hud(ctx, t)


def team_seated(ctx, t, laugh=0.0, clap=0.0, skip=()):
    """Three colleagues on the far side of the meeting table, facing left (toward him)."""
    out = {}
    for i, (x, ch) in enumerate(((1040, grey("m1")), (1200, MIRA), (1360, grey("m2")))):
        if ch.name in skip:
            continue
        hands = {"near": (x - 80, 628), "far": (x - 66, 632)}
        if clap > 0:
            cl = abs(math.sin(t * 14 + i)) * 20 * clap
            hands = {"near": (x - 70 + cl, 560), "far": (x - 70 - cl, 566)}
        J = sit(ch, ctx, x, f=-1, lean=0.08, expr="happy" if (laugh or clap) else "neutral", look=(-1, 0.2),
                mouth_open=0.4 * abs(math.sin(t * 8 + i)) * laugh, hands=hands)
        badge(ctx, J, 0.0, name_rgb=(100, 100, 120))
        out[ch.name] = J
    return out


def h4(ctx, t):
    om = EVENTS["open_mouth"]
    with Camera(1.6, 900, 540).apply(ctx):
        meeting_room(ctx)
        team_seated(ctx, t)
        J = sit(HIM, ctx, 560, f=1, lean=0.14, expr="hopeful" if t < om + 0.4 else "worried",
                look=(1, 0.2) if t < 20.0 else (0.6, 0.9), mouth_open=0.5 if om < t < EVENTS["close_mouth"] else 0.0,
                hands={"near": (680, 628), "far": (664, 632)})
        badge(ctx, J, flick(t, om + 0.3))
        notepad(ctx, 690, 640)
    vline(ctx, "V3", 860, 300, 54)
    hud(ctx, t)


def h5(ctx, t):
    with Camera(1.7, 760, 560).apply(ctx):
        workplace(ctx, desk_x=600, night=True)
        for i in range(6):
            wrect(ctx, 630 + (i % 3) * 30, 640 - 14 - (i // 3) * 14, 120, 12, ("paper", i), (220, 216, 200), LINE, 2, seg=1)
        J = sit(HIM, ctx, 620, f=1, lean=0.22, expr="tired", look=(1, 0.2), screen_glow=0.8, hands={"near": (760, 628), "far": (744, 632)})
        badge(ctx, J, 0.4 + 0.2 * math.sin(t * 3))
        P.wall_clock(ctx, 1110, 240, 23, 40, key="oclock2")
    vline(ctx, "V4", 960, 330, 50)
    cap(ctx, "C3", y=985)
    hud(ctx, t)


# ---- the grind --------------------------------------------------------------------------------------
def g1(ctx, t):
    if t < EVENTS["search"]:
        with Camera(1.7, 860, 540).apply(ctx):
            workplace(ctx, desk_x=600)
            J = sit(HIM, ctx, 620, f=1, lean=0.1, expr="smile", look=(1, -0.2), mouth_open=talk("him", t),
                    hands={"near": (740, 628), "far": (724, 632)})
            badge(ctx, J, 0.0)
            JC = stand(grey("colleague"), ctx, 1000, f=-1, lean=0.06, expr="happy", look=(-1, 0.4), mouth_open=talk("colleague", t))
            badge(ctx, JC, 0.0, name_rgb=(100, 100, 120))
            speech(ctx, t, "colleague", JC["head"][0], JC["head"][1] - 70)
            speech(ctx, t, "him", J["head"][0] + 20, J["head"][1] - 70)
    else:
        UI = P.PhoneUI(W / 2, 560, 900, 560)
        rrect(ctx, W / 2 - 520, 250, 1040, 620, 20, (30, 32, 40), (90, 90, 100), 6)
        rrect(ctx, W / 2 - 490, 280, 980, 90, 45, (230, 232, 236), None)
        n = int(min(1, prog(t, 33.6, 34.8)) * len("what is a pivot table"))
        draw_text(ctx, "what is a pivot table"[:n] + ("|" if int(t * 3) % 2 else ""), W / 2 - 440, 340, 44, (40, 40, 46), align="left")
        for i in range(3):
            ctx.c.drawRect(skia.Rect.MakeXYWH(W / 2 - 460, 430 + i * 120, 700 - i * 90, 22), fill((90, 120, 180)))
            ctx.c.drawRect(skia.Rect.MakeXYWH(W / 2 - 460, 470 + i * 120, 860, 14), fill((70, 74, 90)))
        # his hand shielding the screen, at the edge
        ctx.c.drawPath(poly_path([(W / 2 + 520, 900), (W / 2 + 470, 560), (W / 2 + 520, 520), (W / 2 + 600, 560), (W / 2 + 640, 900)], smooth=True), fill(SKIN))
        ctx.c.drawPath(poly_path([(W / 2 + 520, 900), (W / 2 + 470, 560), (W / 2 + 520, 520), (W / 2 + 600, 560), (W / 2 + 640, 900)], smooth=True), stroke(LINE, 5))
        vline(ctx, "V5", 1500, 200, 52)
    label(ctx, "WEEK 3")
    hud(ctx, t)


def g2(ctx, t):
    with Camera(1.7, 860, 540).apply(ctx):
        workplace(ctx, desk_x=600)
        J = sit(HIM, ctx, 620, f=1, lean=0.1, expr="smile" if t < 38.4 else "neutral", look=(1, -0.2),
                hands={"near": (740, 628), "far": (724, 632)})
        badge(ctx, J, flick(t, 38.3))
        JB = stand(BOSS, ctx, 1000, f=-1, lean=0.06, expr="happy", look=(-1, 0.4), mouth_open=talk("boss", t),
                   hands={"near": (930, 560)}, free=True)
        badge(ctx, JB, 0.0, name_rgb=(120, 80, 80))
        speech(ctx, t, "boss", JB["head"][0], JB["head"][1] - 70)
    cap(ctx, "C4")
    label(ctx, "WEEK 5")
    hud(ctx, t)


def g3(ctx, t):
    err, fixed = EVENTS["error"], EVENTS["fixed"]
    with Camera(2.0, 820, 560).apply(ctx):
        workplace(ctx, desk_x=600, night=True)
        if err < t < fixed:
            ctx.c.drawRect(skia.Rect.MakeXYWH(870, 500, 150, 100), fill(RED_D, 0.8))
            draw_text(ctx, "#REF!", 945, 562, 34, RED, face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
        J = sit(HIM, ctx, 620, f=1, lean=0.24 if t < err else 0.3, expr="shocked" if err < t < err + 1.0 else ("anxious" if t < fixed else "tired"),
                look=(1, 0.2), screen_glow=0.9, hands={"near": (760 + 6 * math.sin(t * 30) * (err < t < fixed), 628), "far": (744, 632)})
        badge(ctx, J, 1.0 if err < t < fixed + 0.5 else 0.3)
        P.wall_clock(ctx, 1110, 240, 1, 12, key="oclock3")
    vline(ctx, "V6", 1300, 330, 60)
    label(ctx, "WEEK 8")
    hud(ctx, t)


def slide_bulb(ctx, x, y, a):
    bulb(ctx, x, y - 20, 1.6, a)
    draw_text(ctx, "NEW IDEA", x, y + 90, 40, (40, 40, 46), a, face="LuckiestGuy-Regular.ttf")


def g4(ctx, t):
    clap = ease(prog(t, EVENTS["applause"], EVENTS["applause"] + 0.4)) * (1 - ease(prog(t, 52.4, 53.0)))
    with Camera(1.35, 1000, 520).apply(ctx):
        meeting_room(ctx, slide_bulb, ease(prog(t, 48.4, 49.0)))
        team_seated(ctx, t, laugh=0.0, clap=clap, skip=("mira",))
        JM = stand(MIRA, ctx, 1500, f=-1, lean=0.04, expr="happy", look=(-1, -0.1), hands={"far": (1590, 500)}, free=True)
        badge(ctx, JM, 0.0, name_rgb=(100, 80, 100))
        J = sit(HIM, ctx, 560, f=1, lean=0.2, expr="sad", look=(0.6, 1.0) if t > 50.8 else (1, -0.1),
                hands={"near": (680, 628), "far": (664, 632)})
        badge(ctx, J, flick(t, 51.0))
        notepad(ctx, 690, 640)
    vline(ctx, "V7", 520, 300, 50)
    cap(ctx, "C5", y=985)
    label(ctx, "WEEK 10")
    hud(ctx, t)


def g5(ctx, t):
    lt = EVENTS["letter"]
    if t < 59.6:
        with Camera(1.8, 860, 560).apply(ctx):
            home(ctx, 0.0)
            P.table(ctx, 640, 640, 420, key="hdesk")
            wrect(ctx, 800, 560, 130, 80, "laptop", (40, 42, 50), LINE, 3, seg=1)
            glow(ctx, 860, 600, 200, BLUE, 0.2)
            J = sit(HIM, ctx, 620, f=1, lean=0.22, expr="sad", look=(1, 0.4), screen_glow=0.8, hands={"near": (780, 628), "far": (764, 632)})
            badge(ctx, J, 0.7)
    else:
        rrect(ctx, W / 2 - 420, 240, 840, 640, 14, (236, 234, 226), LINE, 4)
        text = "I resign, effective immediately."
        n = int(prog(t, 59.8, 61.6) * len(text))
        draw_text(ctx, "Dear Ms Rao,", W / 2 - 360, 340, 44, (40, 40, 46), align="left")
        draw_text(ctx, text[:n], W / 2 - 360, 420, 40, (40, 40, 46), align="left")
    cap(ctx, "C6", y=985 if t < 59.6 else 190)
    label(ctx, "WEEK 12")
    hud(ctx, t)


# ---- rock bottom and the turn ------------------------------------------------------------------
def envelope(ctx, x, y, a=1.0, rot=0.0):
    ctx.c.save()
    ctx.c.translate(x, y)
    ctx.c.rotate(rot)
    rrect(ctx, -34, -22, 68, 44, 3, (236, 232, 220), LINE, 2.5, a=a)
    ctx.c.drawPath(poly_path([(-34, -22), (0, 4), (34, -22)], closed=False), stroke(LINE, 2.5, a))
    ctx.c.restore()


LIFT_CAST = [(560, "l1", None), (760, "mira", MIRA), (1000, "him", None), (1230, "l2", None), (1420, "l3", None)]


def r1(ctx, t):
    lin = EVENTS["lift_in"]
    with Camera(1.5, 1200, 520).apply(ctx):
        lobby(ctx)
        open_k = ease(prog(t, 66.4, 67.2)) * (1 - ease(prog(t, 70.6, 71.4)))
        for k in range(2):  # the doors slide open
            ctx.c.drawRect(skia.Rect.MakeXYWH(1514 + k * 148 + (k * 2 - 1) * 130 * open_k, 374, 144, 406), fill(STEEL))
        x, ph = walk_x(900, max(0, t - 64.4), 110)
        x = min(x, 1640)
        hip, feet = standing(x, FY, 1, step=ph if x < 1640 else 0)
        J0 = HIM.joints(hip, 1, 0.08)
        hand = (J0["shoulder"][0] + 50, J0["shoulder"][1] + 70)
        J = HIM.draw(ctx, hip, 1, lean=0.08, feet=feet, expr="tired", look=(1, 0.6), hands=free_hands(HIM, hip, 1, 0.08, {"near": hand}))
        badge(ctx, J, 0.5)
        hp = J["limbs"]["arm_near"][2]
        envelope(ctx, hp[0] + 8, hp[1] - 10)
    hud(ctx, t)


def lift_people(ctx, t, fr_all, him_fr):
    out = {}
    for x, name, ch in LIFT_CAST:
        ch = HIM if name == "him" else (ch or grey(name))
        J = stand(ch, ctx, x, f=1, lean=0.02, expr="worried" if name == "him" else "neutral", look=(1, 0.2) if name != "him" else (-0.5, 0.6))
        fr = him_fr if name == "him" else fr_all * flick(t, EVENTS["lift_flicker"] + 0.15 * hrand("lf", name), EVENTS["lift_back"] - EVENTS["lift_flicker"])
        badge(ctx, J, fr, name_rgb=(100, 100, 120))
        out[name] = J
    return out


def t1(ctx, t):
    lf = EVENTS["lift_flicker"]
    dark = 0.7 * (flick(t, lf, EVENTS["lift_back"] - lf))
    zin = ease(prog(t, lf - 0.2, lf + 0.4)) * (1 - ease(prog(t, 79.0, 79.8)))
    pan = lerp(560, 1420, ease(prog(t, lf + 0.2, 78.8)))
    with Camera(lerp(lerp(1.3, 1.45, prog(t, 72, 84)), 3.0, zin), lerp(1000, pan, zin), lerp(520, 600, zin)).apply(ctx):
        lift_inside(ctx, t, dark)
        lift_people(ctx, t, 1.0 if t > lf else 0.0, 0.6)
        # the envelope in his hand
        J0 = HIM.joints(standing(1000, FY, 1)[0], 1, 0.02)
        envelope(ctx, 1000 + 20, J0["hip"][1] + 10)
    cap(ctx, "C7")
    cap(ctx, "C8", y=260)
    hud(ctx, t)


def head_icon(ctx, x, y, r=34, rgb=SKIN):
    ctx.c.drawCircle(x, y, r, fill(rgb))
    ctx.c.drawCircle(x, y, r, stroke(LINE, 4))
    ctx.c.drawCircle(x - r * 0.3, y - r * 0.05, r * 0.08, fill(LINE))
    ctx.c.drawCircle(x + r * 0.3, y - r * 0.05, r * 0.08, fill(LINE))


def arrow(ctx, p, q, rgb, w=5, a=1.0):
    ctx.c.drawLine(p[0], p[1], q[0], q[1], stroke(rgb, w, a))
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    for s in (-1, 1):
        ctx.c.drawLine(q[0], q[1], q[0] - math.cos(ang + s * 0.5) * 18, q[1] - math.sin(ang + s * 0.5) * 18, stroke(rgb, w, a))


def t2(ctx, t):
    """The lesson drawn: what he thought, what was true."""
    a1 = ease(prog(t, EVENTS["thought"], EVENTS["thought"] + 0.6))
    a2 = ease(prog(t, EVENTS["true"], EVENTS["true"] + 0.6))
    ring = [(math.cos(i * 2 * math.pi / 8) * 300, math.sin(i * 2 * math.pi / 8) * 220) for i in range(8)]
    for panel, (cx, title_, k) in enumerate(((520, "WHAT HE THOUGHT", a1), (1400, "WHAT WAS TRUE", a2))):
        if k <= 0:
            continue
        cy = 610
        draw_text(ctx, title_, cx, 320, 52, (200, 200, 210), k, face="LuckiestGuy-Regular.ttf")
        for i, (dx, dy) in enumerate(ring):
            x, y = cx + dx, cy + dy
            head_icon(ctx, x, y, 40)
            if panel == 0:
                d = math.hypot(dx, dy)
                arrow(ctx, (x - dx / d * 52, y - dy / d * 52), (cx + dx / d * 86, cy + dy / d * 86), RED, 5, k)
            else:  # each one's eye on itself: a small loop back to its own head
                ctx.c.drawArc(skia.Rect.MakeXYWH(x - 60, y - 60, 120, 120), 200, 280, False, stroke((150, 170, 210), 5, k))
        head_icon(ctx, cx, cy, 62)
        if panel == 0:
            glow(ctx, cx, cy, 140, RED, 0.35 * k)
    cap(ctx, "C9", y=950)
    cap(ctx, "C10", y=1005)
    hud(ctx, t)


# ---- the final fight -----------------------------------------------------------------------------
def review_room(ctx, t, rise=0.0, boss_fr=0.0, warm=0.0, envelope_state="held", villain_crack=0.0, shards=None):
    boss_office(ctx, warm)
    # boss behind the desk, facing left
    JB = sit(BOSS, ctx, 1140, f=-1, lean=0.1, expr="smile" if t > 111.4 else "neutral", look=(-1, 0.2), mouth_open=talk("boss", t),
             hands={"near": (1010, 610), "far": (1024, 614)})
    badge(ctx, JB, boss_fr, name_rgb=(120, 80, 80))
    if rise > 0:
        P.villain(ctx, 400, FY, scale=lerp(0.6, 1.25, rise), alpha=rise, grin=1.1, lean=0.3, crack=villain_crack)
    if shards is not None:
        P.villain_shards(ctx, 400, FY, 1.25, shards)
    return JB


def f1(ctx, t):
    rise = ease(prog(t, EVENTS["rise"], EVENTS["rise"] + 1.6))
    up = ease(prog(t, EVENTS["envelope_up"] - 0.4, EVENTS["envelope_up"]))
    down = ease(prog(t, EVENTS["envelope_down"] - 0.4, EVENTS["envelope_down"]))
    with Camera(lerp(1.5, 1.75, prog(t, 96, 110)), 900, 540, shake=2 * prog(t, 102, 106) * (1 - down)).apply(ctx):
        JB = review_room(ctx, t, rise=rise)
        hip, feet = seated(680, 690, 1)
        J0 = HIM.joints(hip, 1, 0.12)
        lap = (hip[0] + 60, hip[1] - 30)
        held = (J0["shoulder"][0] + 70, J0["shoulder"][1] + 30)
        desk = (880, 612)
        hand = lerp2(lap, held, up) if down <= 0 else lerp2(held, desk, down)
        P.chair(ctx, 680, 690, 1, key="rchair")
        expr = "anxious" if t < EVENTS["envelope_down"] else ("determined" if t < 106 else "hopeful")
        J = HIM.draw(ctx, hip, 1, lean=0.12, feet=feet, expr=expr, look=(1, 0.2), mouth_open=talk("him", t),
                     hands=free_hands(HIM, hip, 1, 0.12, {"near": hand, "far": (hand[0] - 14, hand[1] + 6)}))
        badge(ctx, J, 0.8 if t < EVENTS["envelope_down"] else 0.6)
        hp = J["limbs"]["arm_near"][2]
        envelope(ctx, hp[0] + 6, hp[1] - 6) if down < 1 else envelope(ctx, desk[0] + 10, desk[1] - 4, rot=0.1)
        speech(ctx, t, "boss", JB["head"][0], JB["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 60, J["head"][1] - 70)
    vline(ctx, "V8", 1460, 300, 60)
    vline(ctx, "V9", 1460, 380, 52)
    vline(ctx, "V10", 1460, 300, 56)
    hud(ctx, t)


def f2(ctx, t):
    bb = EVENTS["boss_badge"]
    with Camera(1.75, 900, 540).apply(ctx):
        crack = ease(prog(t, bb, EVENTS["crumble"]))
        JB = review_room(ctx, t, rise=1.0 if t < EVENTS["crumble"] else 0.0, boss_fr=flick(t, bb, 1.4),
                         villain_crack=crack, shards=prog(t, EVENTS["crumble"], EVENTS["crumble"] + 2.0) if t >= EVENTS["crumble"] else None)
        J = sit(HIM, ctx, 680, f=1, lean=0.12, expr="shocked" if t < 113.4 else "smile", look=(1, 0.0), hands={"near": (770, 640), "far": (756, 644)})
        badge(ctx, J, 0.6 * (1 - ease(prog(t, 113.6, 115.0))))
        envelope(ctx, 890, 608, rot=0.1)
        speech(ctx, t, "boss", JB["head"][0], JB["head"][1] - 70)
    hud(ctx, t)


def f3(ctx, t):
    sl, tear = EVENTS["slide"], EVENTS["tear"]
    warm = ease(prog(t, EVENTS["passed"], EVENTS["passed"] + 1.5))
    with Camera(1.75, 900, 540).apply(ctx):
        JB = review_room(ctx, t, warm=warm)
        ex = lerp(890, 780, ease(prog(t, sl, sl + 0.6)))
        hip, feet = seated(680, 690, 1)
        J0 = HIM.joints(hip, 1, 0.12)
        held = (J0["shoulder"][0] + 70, J0["shoulder"][1] + 30)
        up = ease(prog(t, tear - 0.8, tear - 0.3))
        hand = lerp2((ex - 10, 610), held, up)
        P.chair(ctx, 680, 690, 1, key="rchair")
        J = HIM.draw(ctx, hip, 1, lean=0.12, feet=feet, expr="happy" if t > tear else "smile", look=(1, 0.2),
                     hands=free_hands(HIM, hip, 1, 0.12, {"near": hand, "far": (hand[0] - 20, hand[1] + 4)}) if t > sl + 0.6 else
                     free_hands(HIM, hip, 1, 0.12, {"near": (770, 640)}))
        badge(ctx, J, 0.0)
        hp = J["limbs"]["arm_near"][2]
        if t < tear:
            envelope(ctx, hp[0] + 6, hp[1] - 6) if t > sl + 0.6 else envelope(ctx, ex, 608, rot=0.1)
        else:
            k = prog(t, tear, tear + 1.4)
            for i in range(6):  # the pieces fall
                px = hp[0] + (i - 2.5) * 16 + k * (i - 2.5) * 40
                py = hp[1] + k * k * (FY - hp[1]) * (0.7 + 0.1 * i)
                ctx.c.save()
                ctx.c.translate(px, min(FY - 4, py))
                ctx.c.rotate(k * 200 * (i % 2 * 2 - 1))
                ctx.c.drawRect(skia.Rect.MakeXYWH(-10, -7, 20, 14), fill((236, 232, 220)))
                ctx.c.drawRect(skia.Rect.MakeXYWH(-10, -7, 20, 14), stroke(LINE, 2))
                ctx.c.restore()
    hud(ctx, t)


# ---- payoff ------------------------------------------------------------------------------------------
def p1(ctx, t):
    hu = EVENTS["hand_up"]
    laugh = ease(prog(t, EVENTS["laugh"] - 0.2, EVENTS["laugh"] + 0.2)) * (1 - prog(t, 133.4, 134.0))
    with Camera(1.5, 900, 540).apply(ctx):
        meeting_room(ctx, slide_bulb if t > 124.0 else None, ease(prog(t, 124.0, 124.6)))
        Js = team_seated(ctx, t, laugh=laugh)
        up = ease(prog(t, hu - 0.4, hu)) * (1 - ease(prog(t, 125.6, 126.2)))
        hip, feet = seated(560, 690, 1)
        P.chair(ctx, 560, 690, 1, key=("ch", "him", 560))
        hands = {"near": (680, 628), "far": (664, 632)}
        J = HIM.draw(ctx, hip, 1, lean=0.12 + 0.12 * up, feet=feet, expr="hopeful" if t < 125 else "happy", look=(1, -0.1),
                     mouth_open=talk("him", t) + 0.4 * laugh * abs(math.sin(t * 8)), hands=free_hands(HIM, hip, 1, 0.12, hands))
        badge(ctx, J, 0.0)
        notepad(ctx, 690, 640)
        speech(ctx, t, "him", J["head"][0] + 40, J["head"][1] - 70)
        if "mira" in Js:
            speech(ctx, t, "mira", Js["mira"]["head"][0], Js["mira"]["head"][1] - 70)
    hud(ctx, t)


def p2(ctx, t):
    with Camera(1.5, 900, 540).apply(ctx):
        P.back_wall(ctx, rgb=(60, 52, 46))
        P.floor(ctx, FY)
        P.window(ctx, 1200, 180, 420, 300, "pwin", night=False, moon=False, sky=(250, 190, 120))
        glow(ctx, 1410, 330, 700, GOLD, 0.4)
        cone(ctx, (1410, 400), (700, FY), (1300, FY), (255, 214, 150), 0.18)
        x, ph = walk_x(560, t - 134.0, 70)
        hip, feet = standing(x, FY, 1, step=ph)
        J = HIM.draw(ctx, hip, 1, lean=0.06, feet=feet, expr="smile", look=(1, -0.1))
        badge(ctx, J, 0.25 * flick(t, 135.0, 1.4))
    cap(ctx, "C11")
    cap(ctx, "C12", y=260, rgb=TEXT)
    hud(ctx, t)


def vt(ctx, t):
    a = fade(t, 140.4, 149.0, 0.6, 0.6)
    fr = 1 - ease(prog(t, EVENTS["badge_fade"], EVENTS["badge_fade"] + 1.2))
    cx, cy = W / 2, 640
    ctx.c.drawLine(cx, 330, cx, cy - 170, stroke(LANYARD, 10, a))
    rrect(ctx, cx - 150, cy - 190, 300, 380, 24, CARD, LINE, 6, a=a)
    ctx.c.drawRect(skia.Rect.MakeXYWH(cx - 120, cy - 160, 240, 60), fill((60, 80, 120), a * (1 - fr)))
    ctx.c.drawCircle(cx, cy + 10, 56, fill((180, 176, 168), a * (1 - fr)))
    if fr > 0:
        glow(ctx, cx, cy, 300, RED, 0.4 * fr * a)
        ctx.c.drawRect(skia.Rect.MakeXYWH(cx - 140, cy - 180, 280, 360), fill((60, 10, 12), fr * a))
        draw_text(ctx, "FRAUD", cx, cy + 34, 96, RED, fr * a, face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
    cap(ctx, "V1", y=210, size=54)
    cap(ctx, "V2", y=210, size=54)


def x1(ctx, t):
    walk = EVENTS["walk"]
    with Camera(1.6, 880, 520).apply(ctx):
        x = 620 if t < walk else 620 + (t - walk) * 110
        fr = 0.5 * flick(t, EVENTS["mirror_flicker"], 1.6)
        JR, J = mirror_scene(ctx, t, fr, smile=t > EVENTS["mirror_flicker"] + 0.8, step=((t - walk) * 110 / 104) % 1 if t > walk else 0.0, x=x)


def title(ctx, t):
    a = fade(t, EVENTS["title"], DURATION, 0.8, 1.2)
    draw_text(ctx, "FRAUD.", W / 2, 520, 220, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 330 + 660 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=46)
    cap(ctx, "T2", y=760, size=64, rgb=GOLD, glow_rgb=(170, 110, 20))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5,
    "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "R1": r1,
    "T1": t1, "T2": t2, "F1": f1, "F2": f2, "F3": f3, "P1": p1, "P2": p2, "VT": vt, "X1": x1, "TT": title,
}
CONTINUOUS = {"F2", "F3"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1_, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "TT":
        black(ctx, prog(t, DURATION - 1.0, DURATION))
