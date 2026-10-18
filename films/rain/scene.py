"""RAIN.: picture. scene(ctx) draws any frame of the film.

The device: a small grey cloud over his head that rains on him and anyone near him. Every complaint is a grey
puff that floats up out of his mouth into the cloud, and the cloud grows. HIS FORECAST counts it (RAIN, STORM,
CLOUDY) and ends on a word: CLEAR, in gold. The turn: Nia, who has had the worst month of anyone, has a cloud too,
a small one; she never fed it.
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
from studio.extras import speech as _speech, talk as _talk, free_hands, office, street, phone_close  # noqa: E402
from timeline import (SCENES, CAPS, CUES, BUBBLES, EVENTS, FEEDS, DURATION, scene_at, cloud_k, forecast,  # noqa: E402
                      forecast_changed, CLEAR_T)
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
CLOUD = (92, 96, 108)
CLOUD_D = (64, 66, 76)
RAINC = (150, 165, 195)
WARM = (236, 178, 104)
UMB = (70, 96, 120)


def bun(ctx, hx, hy, f, s):
    ctx.c.drawCircle(hx - f * 22 * s, hy - 46 * s, 20 * s, fill((78, 58, 48)))
    ctx.c.drawCircle(hx - f * 22 * s, hy - 46 * s, 20 * s, stroke(LINE, 3 * s))
    ctx.c.drawPath(poly_path([(hx - 46 * s, hy - 22 * s), (hx, hy - 52 * s), (hx + 46 * s, hy - 22 * s)], closed=False, smooth=True),
                   stroke((78, 58, 48), 10 * s))


def cap_hat(ctx, hx, hy, f, s):
    p = poly_path([(hx - 48 * s, hy - 18 * s), (hx - 40 * s, hy - 48 * s), (hx + 40 * s, hy - 48 * s), (hx + 48 * s, hy - 18 * s)], smooth=True)
    ctx.c.drawPath(p, fill((96, 110, 90)))
    ctx.c.drawPath(p, stroke(LINE, 3 * s))
    ctx.c.drawPath(poly_path([(hx + f * 30 * s, hy - 22 * s), (hx + f * 72 * s, hy - 16 * s), (hx + f * 30 * s, hy - 12 * s)]), fill((76, 90, 72)))


HIM = Character("him")
NIA = Character("nia", skin=(206, 188, 170), extra=bun)
BEN = Character("ben", skin=(176, 172, 166), extra=cap_hat)


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


def hud(ctx, t, a=1.0):
    v = forecast(t)
    rgb = GOLD if v == "CLEAR" else TEXT
    lc = forecast_changed(t)
    pop = prog(t, lc, lc + 0.35) if lc is not None and lc <= t <= lc + 0.35 else 0.0
    P.hud(ctx, v, label="HIS FORECAST", a=a, rgb=rgb, pop=pop)


def stand(ch, ctx, x, f=1, lean=0.04, step=0.0, free=True, **kw):
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


# ---- the device: the cloud ---------------------------------------------------------------------
def cloud(ctx, x, y, k, key="cloud", floor=FY, a=1.0, rain=True, glow_gold=0.0):
    """A grey cloud centred at (x, y). k: 0..1 size and rain. Rain falls to `floor`."""
    if k <= 0.02 or a <= 0:
        return 0
    c = ctx.c
    w = 70 + 330 * k
    h = 34 + 70 * k
    rgb = mix(CLOUD, CLOUD_D, k)
    if rain:
        n = int(8 + 46 * k)
        for i in range(n):
            rx = x + (hrand(key, "rx", i) - 0.5) * w * 0.85
            ph = (ctx.t * (1.6 + 0.3 * hrand(key, "sp", i)) + hrand(key, "ph", i)) % 1.0
            ry = y + h * 0.2 + ph * (floor - y)
            c.drawLine(rx, ry, rx - 3, ry + 22, stroke(RAINC, 2.2, 0.55 * a * min(1, k * 2)))
        for i in range(int(3 + 6 * k)):  # splashes on the floor
            sx = x + (hrand(key, "sx", i) - 0.5) * w * 0.8
            kk = (ctx.t * 2 + hrand(key, "sk", i)) % 1.0
            c.drawOval(skia.Rect.MakeXYWH(sx - 10 * kk, floor - 3 * kk, 20 * kk, 6 * kk), stroke(RAINC, 2, 0.5 * (1 - kk) * a))
    puffs = [(-0.38, 0.1, 0.36), (-0.12, -0.16, 0.46), (0.18, -0.08, 0.42), (0.4, 0.12, 0.32), (0.02, 0.14, 0.4)]
    path = skia.Path()
    for dx, dy, r in puffs:
        path.addCircle(x + dx * w, y + dy * h * 1.4, r * w * 0.55)
    p = skia.Op(path, skia.Path(), skia.PathOp.kUnion_PathOp) or path
    c.drawPath(p, blurred(fill((0, 0, 0), 0.25 * a), 8))
    c.drawPath(p, fill(rgb, a))
    c.drawPath(p, stroke(LINE, 3, a))
    c.drawPath(poly_path([(x - w * 0.3, y - h * 0.4), (x - w * 0.05, y - h * 0.62)], closed=False, smooth=True),
               stroke((150, 154, 166), 4, 0.5 * a))
    if glow_gold > 0:
        glow(ctx, x, y, w, GOLD, 0.4 * glow_gold)
    return w


def his_cloud(ctx, t, J, floor=FY, k=None, dy=150):
    k = cloud_k(t) if k is None else k
    hx, hy = J["head"]
    return cloud(ctx, hx, hy - dy - 40 * k, k, "his", floor)


def puffs_up(ctx, t, J, dy=150):
    """Each complaint: grey puffs drift from his mouth up into the cloud."""
    hx, hy = J["head"]
    f = J["facing"]
    for b in BUBBLES:
        if b[2] != "him" or b[3].startswith("how") or b[3].startswith("nice") or b[3].startswith("the train"):
            continue
        t0, t1 = b[0], b[1] + 0.4
        k = prog(t, t0 + 0.2, t1 + 0.8)
        if 0 < k < 1:
            for i in range(4):
                kk = (k + i * 0.18) % 1.0
                x = hx + f * 40 + math.sin(kk * 7 + i) * 18
                y = lerp(hy + 20, hy - dy, kk)
                ctx.c.drawCircle(x, y, 8 + 10 * kk, fill(CLOUD, 0.8 * (1 - kk * 0.6)))


def umbrella(ctx, hand, f=1, s=1.0, a=1.0):
    """An open umbrella held at `hand`, canopy above the head."""
    x, y = hand
    top = (x - f * 6 * s, y - 170 * s)
    ctx.c.drawLine(x, y, top[0], top[1], stroke(LINE, 5 * s, a))
    p = poly_path([(top[0] - 90 * s, top[1] + 30 * s), (top[0], top[1] - 22 * s), (top[0] + 90 * s, top[1] + 30 * s)], smooth=True)
    ctx.c.drawPath(p, fill(UMB, a))
    ctx.c.drawPath(p, stroke(LINE, 3 * s, a))
    for k in (-45, 0, 45):
        ctx.c.drawLine(top[0], top[1] - 10 * s, top[0] + k * s, top[1] + 28 * s, stroke(LINE, 2 * s, a))
    ctx.c.drawPath(poly_path([(x, y), (x + f * 8 * s, y + 10 * s), (x + f * 14 * s, y + 2 * s)], closed=False), stroke(LINE, 4 * s, a))


# ---- sets ---------------------------------------------------------------------------------------
def bus_stop(ctx, t, board="DELAYED", sky=(70, 74, 92), board_rgb=(230, 160, 90)):
    street(ctx, t, lamps=(300,), sky=sky, window_rgb=(150, 140, 110))
    P.wrect(ctx, 1240, FY - 330, 10, 330, "busstop", GREY_L, LINE, 2, seg=2)
    P.wrect(ctx, 1212, FY - 390, 70, 70, "bussign", (60, 90, 140), LINE, 3, seg=2)
    draw_text(ctx, "BUS", 1247, FY - 344, 26, TEXT)
    wrect(ctx, 1300, FY - 300, 240, 90, "board", (20, 22, 26), LINE, 3, seg=1)
    draw_text(ctx, board, 1420, FY - 242, 36, board_rgb, face="LuckiestGuy-Regular.ttf")
    wrect(ctx, 760, 680, 360, 18, "bench", (120, 96, 70), LINE, 3, seg=2)
    for lx in (780, 1080):
        wrect(ctx, lx, 698, 14, 82, ("bl", lx), GREY_D, LINE, 2, seg=1)


def dining(ctx, warm=0.6, sun=0.0):
    c = ctx.c
    P.back_wall(ctx, rgb=mix((34, 32, 36), (70, 58, 48), warm))
    P.floor(ctx, FY)
    P.window(ctx, 1500, 200, 280, 240, "dwin", night=sun <= 0, moon=False, sky=mix((26, 30, 44), (250, 196, 130), sun))
    if sun > 0:
        glow(ctx, 1640, 320, 600, GOLD, 0.35 * sun)
        cone(ctx, (1640, 360), (900, FY), (1500, FY), (255, 214, 150), 0.18 * sun)
    c.drawLine(960, 0, 960, 230, stroke(LINE, 3))
    c.drawPath(poly_path([(900, 230), (1020, 230), (990, 260), (930, 260)]), fill((170, 150, 110)))
    glow(ctx, 960, 270, 360, (255, 220, 160), 0.25 * warm)
    P.table(ctx, 520, 640, 820, key="dtable")
    for i, x in enumerate((640, 820, 1020, 1200)):
        c.drawOval(skia.Rect.MakeXYWH(x - 34, 630, 68, 12), fill((226, 222, 210)))


def dinner_cast(ctx, t, ben_talk=0.0, laugh=0.0, umbrellas=0.0, nia_down=False, nia_cloud=0.0, nia_expr=None):
    """Nia, Ben and Kit on the far side of the table, facing left toward him."""
    out = {}
    for i, (x, ch) in enumerate(((1100, NIA), (1280, BEN), (1440, grey("kit")))):
        hands = {"near": (x - 90, 628), "far": (x - 76, 632)}
        if umbrellas > 0 and ch is not NIA:
            hands = {"near": None, "far": (x - 30, 560)}
        expr = "happy" if laugh > 0.2 else ("sad" if (ch is NIA and nia_down) else "neutral")
        if ch is NIA and nia_expr:
            expr = nia_expr
        J = sit(ch, ctx, x, f=-1, lean=0.1 if not (ch is NIA and nia_down) else 0.22, expr=expr,
                look=(-1, 0.9) if (ch is NIA and nia_down) else (-1, 0.1),
                mouth_open=(talk("ben", t) if ch is BEN else 0.0) + 0.4 * laugh * abs(math.sin(t * 9 + i)) + (talk("nia", t) if ch is NIA else 0.0),
                hands=hands)
        if umbrellas > 0 and ch is not NIA:
            umbrella(ctx, J["limbs"]["arm_far"][2], f=-1, a=umbrellas)
        if ch is NIA and nia_cloud > 0:
            cloud(ctx, J["head"][0], J["head"][1] - 120, 0.16 * nia_cloud, "nia", FY, a=nia_cloud)
        out[ch.name] = J
    return out


def nia_house(ctx, t, inside=True, porch=0.0):
    c = ctx.c
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), fill((26, 28, 36)))
    c.drawRect(skia.Rect.MakeLTRB(700, 120, W + 600, FY), fill((52, 46, 44)))
    for i in range(10):
        c.drawLine(700, 160 + i * 64, W + 600, 160 + i * 64, stroke((60, 54, 50), 3))
    # the big lit window with the dinner inside
    wx, wy, ww, wh = 1100, 260, 560, 300
    c.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), fill(WARM))
    glow(ctx, wx + ww / 2, wy + wh / 2, ww, (255, 210, 140), 0.25)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
    for i, dx in enumerate((0.2, 0.42, 0.66, 0.85)):
        x = wx + dx * ww
        h = 120
        c.drawPath(poly_path([(x - 30, wy + wh), (x - 34, wy + wh - h * 0.7), (x - 22, wy + wh - h), (x + 22, wy + wh - h),
                              (x + 34, wy + wh - h * 0.7), (x + 30, wy + wh)], smooth=True), fill((70, 46, 32)))
        c.drawCircle(x + math.sin(t * 3 + i) * 3, wy + wh - h - 34, 34, fill((70, 46, 32)))
    c.drawRect(skia.Rect.MakeXYWH(wx + 40, wy + wh - 70, ww - 80, 14), fill((90, 60, 40)))
    c.restore()
    wrect(ctx, wx - 10, wy - 10, ww + 20, wh + 20, "nwin", None, (80, 72, 70), 12, seg=2)
    c.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, stroke((80, 72, 70), 10))
    # the door and the porch light
    wrect(ctx, 820, 380, 180, 400, "ndoor", (74, 58, 50), LINE, 4, seg=2)
    c.drawCircle(980, 580, 7, fill((180, 160, 120)))
    c.drawRect(skia.Rect.MakeXYWH(895, 330, 30, 30), fill((200, 190, 150) if porch > 0 else (90, 86, 80)))
    if porch > 0:
        glow(ctx, 910, 345, 300, (255, 230, 170), 0.35 * porch)
        cone(ctx, (910, 360), (700, FY), (1120, FY), (255, 230, 170), 0.14 * porch)
    P.floor(ctx, FY)


# ---- the hook ---------------------------------------------------------------------------------------
def him_at_stop(ctx, t, x=900, expr="tired", look=(1, 0.3), **kw):
    J = stand(HIM, ctx, x, f=1, lean=0.04, expr=expr, look=look, mouth_open=talk("him", t), **kw)
    puffs_up(ctx, t, J)
    his_cloud(ctx, t, J)
    return J


def s01(ctx, t):
    with Camera(1.6, 1000, 470).apply(ctx):
        bus_stop(ctx, t)
        stand(grey("w1"), ctx, 1160, f=-1, lean=0.02, expr="neutral", look=(-1, 0.2))
        him_at_stop(ctx, t)
    cap(ctx, "C1", y=985)
    hud(ctx, t, a=prog(t, 1.0, 1.6))


def h1(ctx, t):
    with Camera(1.6, 1000, 470).apply(ctx):
        bus_stop(ctx, t)
        stand(grey("w1"), ctx, 1160, f=-1, lean=0.02, expr="neutral", look=(-1, 0.2))
        J = him_at_stop(ctx, t, expr="hurt" if t > 5.4 else "tired", look=(1, -0.1) if t > 5.4 else (1, 0.3))
        speech(ctx, t, "him", J["head"][0] + 150, J["head"][1] - 70)
    hud(ctx, t)


def h2(ctx, t):
    with Camera(1.8, 980, 540).apply(ctx):
        office(ctx, desk_x=300)
        wrect(ctx, 1120, 470, 150, 210, "coffee", (56, 58, 66), LINE, 4, seg=2)
        P.table(ctx, 1080, 680, 240, key="ctable")
        ctx.c.drawCircle(1240, 500, 7, fill((110, 170, 255)))
        stepped = ease(prog(t, 11.8, 12.6))
        stand(grey("col"), ctx, lerp(1380, 1520, stepped), f=-1, lean=0.04, expr="neutral" if t < 11.8 else "shocked", look=(-1, -0.4))
        J0 = HIM.joints(standing(980, FY, 1)[0], 1, 0.04)
        hand = (J0["shoulder"][0] + 50, J0["shoulder"][1] + 70)
        J = stand(HIM, ctx, 980, f=1, lean=0.04, expr="hurt", look=(1, 0.6) if t < 9.8 else (1, 0.0), mouth_open=talk("him", t),
                  hands={"near": hand})
        hp = J["limbs"]["arm_near"][2]
        wrect(ctx, hp[0] - 4, hp[1] - 32, 26, 32, "cup", (230, 226, 216), LINE, 3, seg=2)
        puffs_up(ctx, t, J)
        his_cloud(ctx, t, J)
        speech(ctx, t, "him", J["head"][0] + 150, J["head"][1] - 70)
    hud(ctx, t)


def h3(ctx, t):
    with Camera(1.5, 1000, 520).apply(ctx):
        P.back_wall(ctx, rgb=(46, 44, 46))
        P.floor(ctx, FY)
        P.table(ctx, 520, 640, 820, key="ltable")
        moved = ease(prog(t, 16.4, 17.0))
        for x in (840 + 60 * moved, 1000):
            ctx.c.drawOval(skia.Rect.MakeXYWH(x - 34, 630, 68, 12), fill((226, 222, 210)))
        for i, (x, ch) in enumerate(((1120, NIA), (1300, BEN))):
            sit(ch, ctx, x + (40 * moved if ch is BEN else 0), f=-1, lean=0.1 if ch is NIA else 0.06,
                expr="neutral" if t < 15 else ("sad" if ch is NIA else "shocked"), look=(-1, 0.2),
                hands={"near": (x - 90, 628), "far": (x - 76, 632)})
        J = sit(HIM, ctx, 620, f=1, lean=0.14, expr="determined", look=(1, 0.0), mouth_open=talk("him", t),
                hands={"near": (740, 628), "far": (724, 632)})
        puffs_up(ctx, t, J)
        his_cloud(ctx, t, J)
        speech(ctx, t, "him", J["head"][0] + 150, J["head"][1] - 70)
    cap(ctx, "C2", y=985)
    hud(ctx, t)


# ---- the wound and the stakes ---------------------------------------------------------------------
def flat(ctx, night=True):
    P.back_wall(ctx)
    P.floor(ctx, FY)
    P.window(ctx, 1460, 200, 220, 220, "fwin", night=night)
    wrect(ctx, 940, 690, 440, 90, "sofa", (64, 66, 86), LINE, 3, seg=3)
    wrect(ctx, 920, 600, 40, 180, "sofaarm", (64, 66, 86), LINE, 3, seg=2)


def s02(ctx, t):
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0, t1))
    with Camera(1.6, 1100, 500).apply(ctx):
        flat(ctx)
        hip, feet = seated(1080, 690, 1)
        J = HIM.draw(ctx, hip, 1, lean=0.2, feet=feet, expr="tired" if t < 21 else "hurt", look=(1, 0.8),
                     hands=free_hands(HIM, hip, 1, 0.2, {"near": (1170, 640), "far": (1156, 646)}))
        his_cloud(ctx, t, J, dy=160)
        if born > 0:
            P.villain(ctx, 1320, FY, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 20.6, 21.2)), lean=-0.3)
    vline(ctx, "V1", 560, 300, 58)
    vline(ctx, "V2", 560, 380, 52)
    hud(ctx, t)


def b1(ctx, t):
    phone_close(ctx, t, "Nia", ["rough week. could really use friday x", "same. mine was HELL"],
                [EVENTS["nia_text"], EVENTS["his_reply"]], mine=(1,), avatar=(206, 188, 170))
    hud(ctx, t)


# ---- the grind ---------------------------------------------------------------------------------------
def g1(ctx, t):
    with Camera(1.7, 1000, 520).apply(ctx):
        bus_stop(ctx, t, board="CANCELLED", sky=(60, 62, 76), board_rgb=(230, 120, 100))
        up = ease(prog(t, EVENTS["umbrella"], EVENTS["umbrella"] + 0.5))
        Js = stand(grey("str"), ctx, 1160, f=-1, lean=0.02, expr="neutral" if t < 35 else "shocked", look=(-1, 0.1),
                   hands={"far": (1130, 560)} if up > 0 else None)
        if up > 0:
            umbrella(ctx, Js["limbs"]["arm_far"][2], f=-1, a=up)
        J = him_at_stop(ctx, t, x=900, expr="determined", look=(1, 0.0))
        speech(ctx, t, "him", J["head"][0] + 150, J["head"][1] - 70)
    label(ctx, "MONDAY")
    hud(ctx, t)


def g2(ctx, t):
    um = ease(prog(t, EVENTS["umbrellas"], EVENTS["umbrellas"] + 0.6))
    with Camera(1.35, 980, 500).apply(ctx):
        dining(ctx)
        dinner_cast(ctx, t, umbrellas=um, nia_down=t > 41.0)
        J = sit(HIM, ctx, 620, f=1, lean=0.14, expr="determined", look=(1, -0.1), mouth_open=talk("him", t) + 0.2 * abs(math.sin(t * 7)),
                hands={"near": (740, 600 + 20 * math.sin(t * 5)), "far": (724, 632)})
        puffs_up(ctx, t, J)
        cloud(ctx, 960, J["head"][1] - 190, cloud_k(t), "his", FY)
        speech(ctx, t, "him", J["head"][0] + 60, J["head"][1] - 70)
    vline(ctx, "V3", 1420, 240, 50)
    label(ctx, "FRIDAY")
    hud(ctx, t)


def g3(ctx, t):
    lt = t - 47.0
    with Camera(1.7, 960, 540).apply(ctx):
        street(ctx, t, rain=0.0, lamps=(500, 1500))
        x, ph = walk_x(760, lt, 60)
        hip, feet = standing(x, FY, 1, step=ph)
        J = HIM.draw(ctx, hip, 1, lean=0.12, feet=feet, expr="sad", look=(1, 0.7))
        his_cloud(ctx, t, J)
    cap(ctx, "C3", y=985)
    hud(ctx, t)


def g4(ctx, t):
    with Camera(1.5, 1100, 480).apply(ctx):
        flat(ctx)
        hip, feet = seated(1080, 690, 1)
        J = HIM.draw(ctx, hip, 1, lean=0.24, feet=feet, expr="hurt", look=(1, 0.9),
                     hands=free_hands(HIM, hip, 1, 0.24, {"near": (1150, 650), "far": (1136, 654)}))
        cloud(ctx, 1100, 250, 1.0, "his", FY)
    vline(ctx, "V4", 560, 320, 54)
    cap(ctx, "C4", y=985)
    hud(ctx, t)


# ---- rock bottom and the turn ------------------------------------------------------------------
def r1(ctx, t):
    with Camera(1.35, 960, 460).apply(ctx):
        nia_house(ctx, t)
        J = stand(HIM, ctx, 560, f=1, lean=0.08, expr="sad", look=(1, -0.2))
        his_cloud(ctx, t, J)
    vline(ctx, "V5", 820, 900, 54)
    label(ctx, "NEXT FRIDAY")
    hud(ctx, t)


def t1(ctx, t):
    door = EVENTS["door"]
    porch = ease(prog(t, door, door + 0.4))
    nc = ease(prog(t, EVENTS["nia_cloud"], EVENTS["nia_cloud"] + 1.0))
    with Camera(lerp(1.5, 1.8, ease(prog(t, 72.8, 74.0))), lerp(800, 760, ease(prog(t, 72.8, 74.0))), 470).apply(ctx):
        nia_house(ctx, t, porch=porch)
        nx = lerp(910, 840, ease(prog(t, door, door + 1.0)))
        if t > door:
            JN = stand(NIA, ctx, nx, f=-1, lean=0.06, expr="sad" if t > 72.8 else "neutral", look=(-1, 0.2) if t < 79 else (-1, 0.0),
                       mouth_open=talk("nia", t), hands={"near": (nx - 40, 640)})
            bag = JN["limbs"]["arm_near"][2]
            ctx.c.drawPath(poly_path([(bag[0] - 26, bag[1]), (bag[0] + 26, bag[1]), (bag[0] + 34, bag[1] + 70), (bag[0] - 34, bag[1] + 70)], smooth=True),
                           fill((30, 30, 34)))
            cloud(ctx, JN["head"][0], JN["head"][1] - 130, 0.18 * nc, "nia", FY, a=nc)
            speech(ctx, t, "nia", JN["head"][0], JN["head"][1] - 80)
        J = stand(HIM, ctx, 560, f=1, lean=0.06, expr="determined" if t < 72.8 else ("shocked" if t < 77 else "sad"),
                  look=(1, 0.0) if t < 79 else (0.4, 0.8), mouth_open=talk("him", t))
        puffs_up(ctx, t, J)
        his_cloud(ctx, t, J)
        speech(ctx, t, "him", J["head"][0] + 20, J["head"][1] - 80)
    hud(ctx, t)


def t2(ctx, t):
    """The lesson drawn: his words go up into his cloud; hers go out to other people."""
    a1 = ease(prog(t, EVENTS["thought"], EVENTS["thought"] + 0.6))
    a2 = ease(prog(t, EVENTS["true"], EVENTS["true"] + 0.6))
    c = ctx.c
    draw_text(ctx, "HIM", 440, 150, 56, (200, 200, 210), a1, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "NIA", 1506, 150, 56, (200, 200, 210), a2, face="LuckiestGuy-Regular.ttf")
    cam = Camera(1.3, 960, 640)
    cam.apply(ctx).__enter__()
    if a1 > 0:
        me = Character("t2him", scale=0.9)
        hip, feet = standing(540, 900, 1, 0.9)
        J = me.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="hurt", look=(1, -0.4), alpha=a1)
        for i in range(5):  # his words rising into the cloud
            k = (t * 0.5 + i * 0.2) % 1.0
            c.drawCircle(J["head"][0] + 30 + math.sin(k * 6 + i) * 14, lerp(J["head"][1], 470, k), 9 + 9 * k, fill(CLOUD, a1 * (1 - k * 0.5)))
        cloud(ctx, 560, 420, 0.9, "t2a", 900, a=a1)
        for i, x in enumerate((330, 790)):  # the people standing near him, in his rain
            ch = grey(f"t2n{i}", 0.75)
            h, fe = standing(x, 900, 1 if i else -1, 0.75)
            ch.draw(ctx, h, -1 if i else 1, lean=0.02, feet=fe, expr="sad", look=(0, 0.6), alpha=a1)
    if a2 > 0:
        n2 = Character("t2nia", skin=(206, 188, 170), extra=bun, scale=0.9)
        hip, feet = standing(1380, 900, 1, 0.9)
        J = n2.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="smile", look=(1, 0.1), alpha=a2)
        cloud(ctx, 1380, J["head"][1] - 110, 0.16, "t2b", 900, a=a2)
        for i, x in enumerate((1180, 1600)):
            ch = grey(f"t2m{i}", 0.75)
            h, fe = standing(x, 900, -1 if i else 1, 0.75)
            ch.draw(ctx, h, -1 if i else 1, lean=0.02, feet=fe, expr="smile", look=(0, 0), alpha=a2)
            side = 1 if i else -1
            k = (t * 0.6 + i * 0.5) % 1.0
            bx = lerp(J["head"][0] + side * 40, x - side * 50, k)
            rrect(ctx, bx - 70, 560 - 22, 140, 40, 14, (236, 234, 226), None, a=a2 * (1 - abs(k - 0.5)))
            draw_text(ctx, "how are you?", bx, 566, 24, (40, 40, 46), a2 * (1 - abs(k - 0.5)))
    ctx.c.restore()
    cap(ctx, "C5", y=930)
    cap(ctx, "C6", y=990)
    hud(ctx, t)


INSTEAD = ["Catch it before you say it.", "Name one thing that's fine.", "Ask them first."]


def t3(ctx, t):
    if t < 97.4:
        c = ctx.c
        a = fade(t, 94.2, 97.4, 0.3, 0.3)
        rrect(ctx, W / 2 - 440, 280, 880, 480, 22, (236, 232, 214), LINE, 5, a=a)
        draw_text(ctx, "INSTEAD:", W / 2 - 380, 380, 64, (40, 40, 46), a, align="left", face="LuckiestGuy-Regular.ttf")
        for i, s in enumerate(INSTEAD):
            k = ease(prog(t, 94.6 + i * 0.6, 95.0 + i * 0.6))
            y = 480 + i * 90
            rrect(ctx, W / 2 - 380, y - 40, 44, 44, 6, None, (40, 40, 46), 4, a=a * k)
            draw_text(ctx, s, W / 2 - 310, y, 46, (40, 40, 46), a * k, align="left")
        hud(ctx, t)
        return
    if t < 100.6:
        with Camera(1.8, 980, 520).apply(ctx):
            bus_stop(ctx, t)
            up = t > EVENTS["look_up"] - 0.6
            J = stand(HIM, ctx, 900, f=1, lean=0.02 if not up else -0.08, expr="hurt" if not up else "smile",
                      look=(1, -0.1) if not up else (0.6, -1.2), mouth_open=0.4 if 98.0 < t < 98.6 else 0.0)
            his_cloud(ctx, t, J)
        label(ctx, "TUESDAY")
    else:
        with Camera(1.8, 980, 540).apply(ctx):
            office(ctx, desk_x=300)
            wrect(ctx, 1120, 470, 150, 210, "coffee", (56, 58, 66), LINE, 4, seg=2)
            P.table(ctx, 1080, 680, 240, key="ctable")
            J0 = HIM.joints(standing(980, FY, 1)[0], 1, 0.04)
            hand = (J0["shoulder"][0] + 50, J0["shoulder"][1] + 70)
            shrug = math.sin(math.pi * prog(t, EVENTS["shrug"], EVENTS["shrug"] + 0.6))
            hip, feet = standing(980, FY, 1)
            hip = (hip[0], hip[1] - 3 * shrug)
            J = HIM.draw(ctx, hip, 1, lean=0.04, feet={k: (v[0], v[1] - 0) for k, v in feet.items()}, expr="smile", look=(1, 0.4),
                         hands=free_hands(HIM, hip, 1, 0.04, {"near": hand}))
            hp = J["limbs"]["arm_near"][2]
            wrect(ctx, hp[0] - 4, hp[1] - 32, 26, 32, "cup", (230, 226, 216), LINE, 3, seg=2)
            his_cloud(ctx, t, J)
        label(ctx, "WEDNESDAY")
    hud(ctx, t)


# ---- the final fight -----------------------------------------------------------------------------
def f1f2(ctx, t):
    rise = ease(prog(t, EVENTS["rise"], EVENTS["rise"] + 1.6))
    turn = ease(prog(t, EVENTS["turn_to_nia"], EVENTS["turn_to_nia"] + 0.5))
    with Camera(lerp(1.35, 1.6, prog(t, 104, 116)), 960, 520, shake=2 * prog(t, 110, 115.4)).apply(ctx):
        dining(ctx)
        Js = dinner_cast(ctx, t, nia_down=True, nia_cloud=1.0)
        if rise > 0:
            P.villain(ctx, 360, FY, scale=lerp(0.6, 1.25, rise), alpha=rise, grin=1.2, lean=0.3)
        J = sit(HIM, ctx, 620, f=1, lean=0.14 + 0.08 * turn, expr="anxious" if t < 113.8 else ("closed" if t < EVENTS["turn_to_nia"] else "hopeful"),
                look=(1, -0.1) if t < 113.8 else (1, 0.3), mouth_open=talk("him", t), hands={"near": (740, 628), "far": (724, 632)})
        cloud(ctx, 900, J["head"][1] - 200, cloud_k(t), "his", FY)
        speech(ctx, t, "ben", Js["ben"]["head"][0], Js["ben"]["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 80, J["head"][1] - 70)
    vline(ctx, "V6", 1500, 210, 60)
    vline(ctx, "V7", 1500, 290, 54)
    vline(ctx, "V8", 1500, 210, 54)
    vline(ctx, "V9", 1500, 290, 64)
    hud(ctx, t)


def f3(ctx, t):
    sun = ease(prog(t, EVENTS["sun"], EVENTS["sun"] + 1.4))
    with Camera(1.6, 960, 520).apply(ctx):
        dining(ctx, warm=0.6 + 0.3 * sun, sun=sun)
        Js = dinner_cast(ctx, t, nia_cloud=1 - ease(prog(t, 122.0, 123.0)), nia_expr="smile" if t > 120.2 else "sad")
        if t < EVENTS["crumble"] + 2.2:
            P.villain_shards(ctx, 360, FY, 1.25, prog(t, EVENTS["crumble"], EVENTS["crumble"] + 2.0))
        J = sit(HIM, ctx, 620, f=1, lean=0.2, expr="hopeful" if t < 120.4 else "smile", look=(1, 0.3), hands={"near": (740, 628), "far": (724, 632)})
        k = cloud_k(t)
        cloud(ctx, 900, J["head"][1] - 200, k, "his", FY, glow_gold=sun * (1 - k))
        speech(ctx, t, "nia", Js["nia"]["head"][0], Js["nia"]["head"][1] - 70)
    hud(ctx, t)


# ---- payoff ------------------------------------------------------------------------------------------
def p1(ctx, t):
    laugh = ease(prog(t, EVENTS["laugh"] - 0.4, EVENTS["laugh"])) * (1 - prog(t, 134.0, 135.0))
    with Camera(1.4, 960, 520).apply(ctx):
        dining(ctx, warm=0.9, sun=1.0)
        Js = dinner_cast(ctx, t, laugh=laugh, nia_expr="happy" if laugh > 0.2 else "smile")
        J = sit(HIM, ctx, 620, f=1, lean=0.12, expr="happy", look=(1, -0.1),
                mouth_open=talk("him", t) + 0.4 * laugh * abs(math.sin(t * 9)), hands={"near": (740, 600 + 18 * math.sin(t * 6)), "far": (724, 632)})
        speech(ctx, t, "ben", Js["ben"]["head"][0], Js["ben"]["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 120, J["head"][1] - 70)
    cap(ctx, "C7")
    cap(ctx, "C8", y=260)
    hud(ctx, t)


def vt(ctx, t):
    a = fade(t, 135.4, 144.0, 0.6, 0.6)
    br = ease(prog(t, EVENTS["viewer_break"], EVENTS["viewer_break"] + 1.2))
    if br < 1:
        cloud(ctx, W / 2, 560, 0.7 * (1 - br), "vt", 900, a=a)
    if br > 0:
        glow(ctx, W / 2, 600, 500, GOLD, 0.4 * br * a)
        for i in range(10):
            ang = i * math.pi / 5
            d0, d1 = 140 + 80 * br, 220 + 140 * br
            ctx.c.drawLine(W / 2 + math.cos(ang) * d0, 600 + math.sin(ang) * d0, W / 2 + math.cos(ang) * d1, 600 + math.sin(ang) * d1,
                           stroke(GOLD, 5, a * br * 0.8))
    cap(ctx, "V1", y=200, size=58)
    cap(ctx, "V2", y=200, size=58)


def x1(ctx, t):
    up = ease(prog(t, EVENTS["stranger_up"], EVENTS["stranger_up"] + 0.6))
    with Camera(1.7, 1000, 520).apply(ctx):
        bus_stop(ctx, t, sky=(140, 160, 190))
        st = grey("x1str")
        Js = stand(st, ctx, 1140, f=-1, lean=0.02 - 0.12 * up, expr="hurt" if up < 0.5 else "smile",
                   look=(-1, 0.0) if up < 0.5 else (-0.4, -1.2), mouth_open=talk("stranger", t))
        cloud(ctx, Js["head"][0], Js["head"][1] - 150, 0.3 * (1 - ease(prog(t, 150.8, 152.0))), "x1s", FY)
        J = stand(HIM, ctx, 900, f=1, lean=0.02, expr="smile", look=(1, -0.6) if t > 148 else (1, 0.0), mouth_open=talk("him", t))
        speech(ctx, t, "stranger", Js["head"][0] + 60, Js["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 20, J["head"][1] - 80)


def title(ctx, t):
    a = fade(t, EVENTS["title"], DURATION, 0.8, 1.2)
    draw_text(ctx, "RAIN.", W / 2, 520, 220, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 250 + 500 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=46)
    cap(ctx, "T2", y=760, size=64, rgb=GOLD, glow_rgb=(170, 110, 20))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "S02": s02, "B1": b1, "G1": g1, "G2": g2, "G3": g3, "G4": g4,
    "R1": r1, "T1": t1, "T2": t2, "T3": t3, "F1": f1f2, "F2": f1f2, "F3": f3, "P1": p1, "VT": vt, "X1": x1, "TT": title,
}
CONTINUOUS = {"F2", "F3", "H1"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1_, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "TT":
        black(ctx, prog(t, DURATION - 1.0, DURATION))
