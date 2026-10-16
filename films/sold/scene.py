"""SOLD.: picture. scene(ctx) draws any frame of the film.

The device: a jar on the shelf labelled THE SEA, counted top-left. Every purchase takes a coin out of it, and
every box joins a tower in front of the window, with a sticker naming the feeling it was bought for. The tower
blocks the light and the postcard of the sea. When it falls, the boxes are still taped shut: he wasn't buying
things, he was buying a feeling. Returned, they put the coins back. Gold appears only when the jar is full.
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
from studio.extras import speech as _speech, talk as _talk, free_hands, floor_sit, door, street, phone_close  # noqa: E402
from timeline import (SCENES, CAPS, CUES, BUBBLES, EVENTS, BUYS, OPENED, RETURNS, GOAL, DURATION, scene_at,  # noqa: E402
                      jar_at, jar_changed, tower, fallen)
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
CARD = (150, 118, 82)
CARD_D = (112, 86, 60)
TAPE = (196, 170, 120)
STICKER = (232, 230, 220)
COIN = (168, 170, 178)
SEA = (70, 104, 140)
NIGHT_WALL = (20, 20, 24)

HIM = Character("him")


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
    v = jar_at(t)
    rgb = GOLD if v >= GOAL else (RED if v <= 0 else TEXT)
    P.hud(ctx, f"${v:,}", label="THE SEA", a=a, rgb=rgb, pop=pop_at(t, jar_changed(t) if t < 133 else None))


def coin(ctx, x, y, r=11, a=1.0, gold=False):
    rgb = GOLD if gold else COIN
    ctx.c.drawCircle(x, y, r, fill(rgb, a))
    ctx.c.drawCircle(x, y, r, stroke(LINE, 2.5, a))
    ctx.c.drawCircle(x, y, r * 0.55, stroke(mix(rgb, LINE, 0.35), 1.6, a))


def burst(ctx, x, y, k, r=160):
    """The feeling: a soft burst of pale light that fades. k: 0..1 over its life."""
    if not 0 < k < 1:
        return
    a = math.sin(math.pi * min(1, k * 2.2)) if k < 0.45 else (1 - k) / 0.55
    glow(ctx, x, y, r * (0.8 + 0.6 * k), (230, 236, 255), 0.5 * a)
    for i in range(10):
        ang = i * math.pi / 5 + 0.3
        d0, d1 = r * (0.35 + 0.5 * k), r * (0.55 + 0.7 * k)
        ctx.c.drawLine(x + math.cos(ang) * d0, y + math.sin(ang) * d0, x + math.cos(ang) * d1, y + math.sin(ang) * d1,
                       stroke((240, 244, 255), 4, a))


# ---- the device: boxes, the tower, the jar ---------------------------------------------------
def box(ctx, x, yb, w, h, sticker="", opened=False, key="bx", a=1.0, rot=0.0, stamp=None):
    """A cardboard box standing on yb, centred on x. Tape across the top unless opened."""
    if a <= 0:
        return
    c = ctx.c
    c.save()
    c.translate(x, yb - h / 2)
    c.rotate(rot)
    wrect(ctx, -w / 2, -h / 2, w, h, (key, "b"), CARD, LINE, 3, seg=2, a=a)
    if opened:
        for s in (-1, 1):
            flap = poly_path([(s * w / 2, -h / 2), (s * w * 0.62, -h / 2 - h * 0.3), (s * w * 0.1, -h / 2 - h * 0.2), (0, -h / 2)])
            c.drawPath(flap, fill(CARD_D, a))
            c.drawPath(flap, stroke(LINE, 3, a))
    else:
        c.drawRect(skia.Rect.MakeXYWH(-w * 0.09, -h / 2, w * 0.18, h * 0.45), fill(TAPE, a))
        c.drawLine(-w / 2, -h / 2 + 2, w / 2, -h / 2 + 2, stroke(TAPE, 7, a))
    if sticker:
        size = min(26, max(14, w * 0.15))
        tw = text_width(sticker, size) + 18
        rrect(ctx, -tw / 2, -h * 0.05, tw, size + 12, 4, STICKER, (150, 146, 136), 2, a=a)
        draw_text(ctx, sticker, 0, -h * 0.05 + size + 2, size, (40, 38, 36), a)
    if stamp is not None and stamp > 0:
        c.save()
        c.rotate(-0.18)
        k = ease_out_back(min(1, stamp))
        c.scale(1.6 - 0.6 * k, 1.6 - 0.6 * k)
        rrect(ctx, -w * 0.38, -h * 0.42, w * 0.76, 36, 6, None, (90, 140, 200), 4, a=a * min(1, stamp * 2))
        draw_text(ctx, "RETURN", 0, -h * 0.42 + 28, 28, (90, 140, 200), a * min(1, stamp * 2), face="LuckiestGuy-Regular.ttf")
        c.restore()
    c.restore()


BW, BH = 158, 92


def tower_slot(i):
    col_ = i % 2
    row = i // 2
    x = 1452 + col_ * (BW + 6) + (hrand("tw", i) - 0.5) * 14
    w = BW - 10 + hrand("tww", i) * 14
    return x, FY - row * BH, w, BH - 4


def draw_tower(ctx, t):
    for i in tower(t):
        tm = BUYS[i][0]
        x, yb, w, h = tower_slot(i)
        k = prog(t, tm - 0.4, tm)
        yy = yb - (1 - k * k) * 700
        box(ctx, x, yy, w, h, BUYS[i][1], i in OPENED, key=("tw", i))


def tower_top(t):
    ids = tower(t)
    if not ids:
        return FY
    return min(tower_slot(i)[1] - tower_slot(i)[3] for i in ids)


FALL = {  # where each box lands after the collapse: (x, y bottom, rotation)
    0: (1290, FY, 0.0), 1: (1470, FY, 0.06), 2: (1640, FY, -0.08), 3: (1150, FY, 0.1), 4: (1800, FY, 0.0),
    5: (1560, FY - 88, 0.22), 6: (1010, FY, -0.05), 7: (1380, FY - 88, -0.3), 8: (1720, FY - 88, 0.12),
    9: (1240, FY - 86, 0.4), 10: (880, FY, 0.18),
}


def draw_fallen(ctx, t):
    k = ease(prog(t, EVENTS["collapse"], EVENTS["collapse"] + 0.8))
    ret = {i: tm for tm, i in RETURNS}
    for i in sorted(fallen(t), key=lambda i: FALL[i][1] != FY):
        sx, syb, sw, sh = tower_slot(i)
        fx, fyb, rot = FALL[i]
        # the arc from the tower to the floor, staggered by height
        kk = ease(prog(k, 0.0, 0.6 + 0.04 * (i // 2)))
        x = lerp(sx, fx, kk)
        yb = lerp(syb, fyb, kk * kk)
        stamp = None
        a = 1.0
        if i in ret:
            r0 = ret[i]
            stamp = prog(t, r0 - 0.7, r0 - 0.4) * 1.0
        box(ctx, x, yb, sw, sh, BUYS[i][1], i in OPENED, key=("tw", i), rot=rot * kk, stamp=stamp, a=a)


def leaving(ctx, t):
    """T3: returned boxes slide out through the door."""
    for r0, i in RETURNS:
        k = prog(t, r0 - 0.4, r0 + 0.2)
        if 0 < k < 1:
            fx, fyb, rot = FALL[i]
            box(ctx, lerp(fx, 2100, ease(k)), FY, tower_slot(i)[2], BH - 4, BUYS[i][1], key=("tw", i), stamp=1.0, a=1 - k * 0.3)


SHELF = (930, 430, 250)
JAR = (1050, 430)


def jar(ctx, t, x=None, y=None, s=1.0, lab="THE SEA", amount=None, gold=None):
    x = JAR[0] if x is None else x
    y = JAR[1] if y is None else y
    v = jar_at(t) if amount is None else amount
    gold = (v >= GOAL) if gold is None else gold
    w, h = 96 * s, 124 * s
    c = ctx.c
    fill_h = (h - 26 * s) * max(0, min(1, v / GOAL))
    if fill_h > 0:
        rgb = GOLD if gold else COIN
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 8 * s, y - 6 * s - fill_h, w - 16 * s, fill_h), fill(mix(rgb, LINE, 0.15)))
        for i in range(int(fill_h / (10 * s))):
            for j in range(4):
                cx = x - w / 2 + 18 * s + j * 20 * s + (i % 2) * 8 * s
                c.drawLine(cx - 7 * s, y - 10 * s - i * 10 * s, cx + 7 * s, y - 10 * s - i * 10 * s, stroke(mix(rgb, LINE, 0.4), 2 * s))
        if gold:
            glow(ctx, x, y - fill_h / 2, 160 * s, GOLD, 0.25)
    wrect(ctx, x - w / 2, y - h, w, h, ("jar", lab), None, (170, 180, 196), 4 * s, seg=2)
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 - 4 * s, y - h - 14 * s, w + 8 * s, 16 * s), fill(GREY_L))
    rrect(ctx, x - w * 0.42, y - h * 0.62, w * 0.84, 30 * s, 4, STICKER, (150, 146, 136), 2)
    draw_text(ctx, lab, x, y - h * 0.62 + 23 * s, 20 * s, (40, 38, 36), face="LuckiestGuy-Regular.ttf")
    c.drawLine(x - w / 2 + 10 * s, y - h + 10 * s, x - w / 2 + 10 * s, y - 20 * s, stroke((255, 255, 255), 3 * s, 0.25))


def coin_out(ctx, t, tm, to=(1900, 300), src=None):
    """A coin leaving the jar (just before the box lands)."""
    k = prog(t, tm - 0.5, tm)
    if 0 < k < 1:
        sx, sy = src or (JAR[0], JAR[1] - 100)
        x = lerp(sx, to[0], k)
        y = lerp(sy, to[1], k) - math.sin(math.pi * k) * 180
        coin(ctx, x, y, 12, 1 - k * 0.3)


def coins_out(ctx, t):
    for tm, _, _ in BUYS:
        coin_out(ctx, t, tm)


def postcard(ctx, x, y, w=96, h=66, warm=0.0, a=1.0):
    sky = mix((120, 140, 160), (250, 190, 120), warm)
    sea = mix(SEA, (60, 120, 170), warm)
    ctx.c.save()
    ctx.c.translate(x, y)
    ctx.c.rotate(0.06)
    ctx.c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), fill((236, 232, 222), a))
    ctx.c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 6, -h / 2 + 6, w - 12, h * 0.45), fill(sky, a))
    ctx.c.drawRect(skia.Rect.MakeXYWH(-w / 2 + 6, -h / 2 + 6 + h * 0.45, w - 12, h * 0.55 - 12), fill(sea, a))
    ctx.c.drawCircle(w * 0.18, -h * 0.05, h * 0.12, fill(mix((230, 230, 220), GOLD, warm), a))
    ctx.c.drawLine(-w / 2 + 12, h * 0.18, w / 2 - 12, h * 0.18, stroke((210, 226, 236), 2, a * 0.8))
    ctx.c.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), stroke(LINE, 2.5, a))
    ctx.c.drawRect(skia.Rect.MakeXYWH(-10, -h / 2 - 6, 20, 10), fill((220, 214, 190), 0.8 * a))
    ctx.c.restore()


WIN = (1440, 250, 260, 220)
POSTCARD = (1640, 430)


def flat(ctx, t, day=0.0, lamp_on=0.0, card=True, warm=0.0):
    """The one-room flat: bed left, nightstand, shelf with the jar, the window right, the box tower in front of it."""
    c = ctx.c
    wall = mix(NIGHT_WALL, (54, 56, 62), day)
    P.back_wall(ctx, rgb=wall)
    wx, wy, ww, wh = WIN
    sky = mix((26, 30, 44), mix((150, 170, 196), (250, 200, 140), warm), day)
    P.window(ctx, wx, wy, ww, wh, "win", night=day < 0.5, sky=sky)
    if card:
        postcard(ctx, *POSTCARD, warm=warm)
    # light from the window, cut off by the tower
    open_frac = clamp((tower_top(t) - wy) / wh)
    if day > 0:
        cone(ctx, (wx + ww / 2, wy + wh * 0.6), (wx - 500, FY), (wx + 200, FY), mix((200, 210, 230), (255, 220, 160), warm),
             0.16 * day * open_frac)
    P.floor(ctx, FY)
    # shelf and jar
    sx, sy, sw = SHELF
    wrect(ctx, sx, sy, sw, 14, "shelf", GREY, LINE, 3, seg=2)
    for bx in (sx + 20, sx + sw - 30):
        c.drawLine(bx, sy + 14, bx + 10, sy + 44, stroke(GREY_D, 6))
    for i, (hh, rgb) in enumerate(((70, (80, 84, 104)), (60, (96, 84, 76)))):
        wrect(ctx, sx + 150 + i * 24, sy - hh, 20, hh, ("bk", i), rgb, LINE, 2, seg=1)
    # bed and nightstand
    P.bed(ctx, 120, FY, 560)
    wrect(ctx, 700, FY - 112, 110, 112, "nstand", GREY_D, LINE, 3, seg=2)
    if t >= EVENTS["open"] + 1.5 or t > 30:  # the lamp he bought in the hook
        lamp(ctx, 780, FY - 112, lamp_on)


def lamp(ctx, x, y, on=0.0):
    c = ctx.c
    c.drawLine(x, y, x, y - 70, stroke(LINE, 7))
    c.drawLine(x, y, x, y - 70, stroke(GREY_L, 4))
    shade = poly_path([(x - 30, y - 64), (x + 30, y - 64), (x + 18, y - 104), (x - 18, y - 104)])
    c.drawPath(shade, fill((150, 150, 140)))
    c.drawPath(shade, stroke(LINE, 3))
    c.drawRect(skia.Rect.MakeXYWH(x - 22, y - 6, 44, 8), fill(GREY))
    if on > 0:
        glow(ctx, x, y - 60, 260, (240, 220, 180), 0.25 * on)


# ---- him in bed with the phone ---------------------------------------------------------------
DUVET_PHONE = (322, FY - 138)


def bed_sit(ctx, t, expr="tired", look=(1, 0.6), phone=1.0, hand=None, glow_rgb=BLUE, phone_rgb=BLUE, shaky=0.0, lean=-0.22):
    """Sitting up in bed against the headboard, the phone at chest height. Returns joints."""
    hip = (236, FY - 94)
    J0 = HIM.joints(hip, 1, lean)
    sh = J0["shoulder"]
    hp = hand or (sh[0] + 58 + shaky * math.sin(t * 40) * 3, sh[1] + 62)
    wrect(ctx, 150, FY - 160, 70, 70, "pillow2", (200, 198, 190), LINE, 3, seg=2)
    J = HIM.draw(ctx, hip, 1, lean=lean, feet={"near": (hip[0] + 112, FY - 96), "far": (hip[0] + 108, FY - 98)},
                 expr=expr, look=look, screen_glow=phone * 0.9 if phone else 0.0,
                 hands=free_hands(HIM, hip, 1, lean, {"near": hp, "far": (hp[0] - 12, hp[1] + 6)}))
    wrect(ctx, 286, FY - 132, 384, 46, "duvet", (60, 64, 92), LINE, 3, seg=3)
    if phone > 0:
        P.phone_held(ctx, *J["limbs"]["arm_near"][2], on=phone, glow_rgb=phone_rgb)
    return J


def in_bed(ctx, expr="closed", look=(0, -1)):
    hip = (350, FY - 132)
    HIM.draw(ctx, hip, -1, lean=math.pi / 2, feet={"near": (hip[0] + 114, FY - 126), "far": (hip[0] + 112, FY - 128)},
             expr=expr, look=look, hands={"near": (hip[0] - 20, FY - 104), "far": (hip[0] - 10, FY - 106)},
             bend={"leg_near": 1, "leg_far": 1, "arm_near": 1, "arm_far": 1})
    wrect(ctx, 270, FY - 136, 400, 46, "duvet", (60, 64, 92), LINE, 3, seg=3)


def clock(ctx, s, x=755, y=FY - 140):
    draw_text(ctx, s, x, y, 30, (110, 140, 190), face="LuckiestGuy-Regular.ttf", glow_rgb=(60, 90, 140))


# ---- the phone close-up: a shop page ------------------------------------------------------------
def thumb(ctx, x, y, a=1.0):
    p = poly_path([(x - 44, y + 400), (x - 40, y + 20), (x - 20, y - 26), (x + 16, y - 30), (x + 38, y + 4), (x + 46, y + 400)], smooth=True)
    ctx.c.drawPath(p, fill(SKIN, a))
    ctx.c.drawPath(p, stroke(LINE, 5, a))
    ctx.c.drawPath(poly_path([(x - 16, y - 6), (x + 12, y - 10), (x + 22, y + 10), (x - 14, y + 14)], smooth=True), fill(SKIN_SHADE, a))


def item_icon(ctx, kind, x, y, s=1.0):
    c = ctx.c
    if kind == "lamp":
        ctx.c.save()
        ctx.c.translate(x, y + 90)
        ctx.c.scale(2.4, 2.4)
        lamp(ctx, 0, 0, 0.0)
        ctx.c.restore()
    elif kind == "phones":
        c.drawArc(skia.Rect.MakeXYWH(x - 70 * s, y - 70 * s, 140 * s, 140 * s), 180, 180, False, stroke(LINE, 18 * s))
        c.drawArc(skia.Rect.MakeXYWH(x - 70 * s, y - 70 * s, 140 * s, 140 * s), 180, 180, False, stroke(GREY_L, 12 * s))
        for sx in (-1, 1):
            rrect(ctx, x + sx * 70 * s - 22 * s, y - 10 * s, 44 * s, 70 * s, 14, (60, 62, 72), LINE, 4)
    else:
        box(ctx, x, y + 60 * s, 130 * s, 100 * s, key=("icon", kind))


def shop_close(ctx, t, name, price, kind, tap_t=None, banner=None, left=None, hover=None, claw=0.0, ui=None):
    """Full-screen phone: a product, a price and the red BUY NOW. tap_t: the thumb taps; then ORDER PLACED."""
    UI = ui or P.PhoneUI(W / 2, 580, 520, 900)
    UI.body(ctx, 1.0)
    bx, by, bw, bh = UI.x0 + 50, UI.y0 + UI.h - 210, UI.w - 100, 96
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, 110), fill((26, 28, 36)))
        draw_text(ctx, "shop", x0 + 40, y0 + 80, 40, (170, 176, 196), align="left", face="LuckiestGuy-Regular.ttf")
        ytop = y0 + 130
        if banner:
            ctx.c.drawRect(skia.Rect.MakeXYWH(x0, ytop, UI.w - 36, 64), fill(RED_D))
            draw_text(ctx, banner, UI.cx, ytop + 44, 30, TEXT, face="LuckiestGuy-Regular.ttf")
            ytop += 64
        rrect(ctx, x0 + 40, ytop + 30, UI.w - 116, 300, 18, (44, 48, 60), None)
        item_icon(ctx, kind, UI.cx, ytop + 170)
        draw_text(ctx, name, x0 + 44, ytop + 400, 40, TEXT, align="left")
        draw_text(ctx, price, x0 + 44, ytop + 460, 50, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
        if left:
            draw_text(ctx, left, UI.x0 + UI.w - 60, ytop + 460, 30, (240, 120, 120), align="right")
        placed = tap_t is not None and t >= tap_t + 0.15
        press = 1.0 - 0.06 * (1 - prog(t, tap_t, tap_t + 0.2)) if tap_t is not None and tap_t <= t < tap_t + 0.2 else 1.0
        if placed:
            rrect(ctx, bx, by, bw, bh, 22, (60, 70, 84), None)
            draw_text(ctx, "ORDER PLACED", UI.cx, by + 64, 40, TEXT, face="LuckiestGuy-Regular.ttf")
        else:
            ctx.c.save()
            ctx.c.translate(UI.cx, by + bh / 2)
            ctx.c.scale(press, press)
            rrect(ctx, -bw / 2, -bh / 2, bw, bh, 22, RED, None)
            draw_text(ctx, "BUY NOW", 0, 18, 46, TEXT, face="LuckiestGuy-Regular.ttf")
            ctx.c.restore()
    # the thumb
    if tap_t is not None:
        k_in = ease(prog(t, tap_t - 0.9, tap_t))
        k_out = ease(prog(t, tap_t + 0.3, tap_t + 0.9))
        y = lerp(H + 60, by + bh / 2 + 10, k_in) + k_out * 500
        if k_in > 0 and y < H + 60:
            thumb(ctx, UI.cx + 40, y)
    if hover is not None:
        thumb(ctx, UI.cx + 40 + math.sin(t * 30) * 3 * hover[1], lerp(H + 60, by + bh / 2 + 70, hover[0]))
    if claw > 0:
        for i in range(3):  # the villain's claw tips at the button
            px, py = UI.cx + 140 + i * 30, by + bh + 40 - claw * 90 - i * 6
            ctx.c.drawPath(poly_path([(px - 12, py + 60), (px, py - 18), (px + 12, py + 60)]), fill((16, 8, 9), claw))
            ctx.c.drawPath(poly_path([(px - 12, py + 60), (px, py - 18), (px + 12, py + 60)]), blurred(fill(RED, 0.5 * claw), 8))
    return UI


# ---- the hook ---------------------------------------------------------------------------------------
def s01(ctx, t):
    with Camera(2.2, 420, 600).apply(ctx):
        flat(ctx, t)
        bed_sit(ctx, t, "tired", look=(1, 0.7))
        clock(ctx, "2:07")
    cap(ctx, "C1")
    hud(ctx, t, a=prog(t, 1.0, 1.6))


def h1(ctx, t):
    shop_close(ctx, t, "Desk lamp", "$39", "lamp", tap_t=EVENTS["tap"])
    hud(ctx, t)


def h2(ctx, t):
    ring = EVENTS["doorbell"]
    with Camera(1.7, 1000, 560).apply(ctx):
        P.back_wall(ctx, rgb=(30, 30, 34))
        P.floor(ctx, FY)
        door(ctx, 1080, open_k=ease(prog(t, ring + 0.1, ring + 0.5)), light=ease(prog(t, ring + 0.1, ring + 0.5)), key="fdoor")
        hand_over = ease(prog(t, 8.0, 8.5))
        # the courier in the doorway
        JC = None
        if t < 10.6:
            c_x = 1250 if t < 10.0 else lerp(1250, 1500, prog(t, 10.0, 10.6))
            cg = grey("courier")
            hipc, feetc = standing(c_x, FY, -1, step=((t - 10.0) * 2.4) % 1 if t > 10.0 else 0.0)
            held = lerp2((c_x - 70, 620), (1070, 626), hand_over)
            JC = cg.draw(ctx, hipc, -1, lean=0.06, feet=feetc, expr="smile", look=(-1, 0), mouth_open=talk("courier", t),
                         hands=free_hands(cg, hipc, -1, 0.06, {"near": held, "far": (held[0] + 20, held[1] + 4)}) if hand_over < 1 else None)
            P.wrect(ctx, c_x - 40, 470, 80, 20, "ccap", (90, 100, 120), LINE, 3, seg=1)  # his cap
            if hand_over < 1:
                box(ctx, held[0] - 10, held[1] + 40, 110, 76, key="hbox")
        # him
        op = t >= EVENTS["open"]
        hip, feet = standing(880, FY, 1)
        bx = (1000, 626) if hand_over >= 1 else None
        expr = "neutral"
        if op:
            expr = "happy" if t < 10.8 else ("smile" if t < 11.3 else "neutral")
        rx = lerp(1060, 980, ease(prog(t, 8.5, 8.9)))
        hands = {"near": (rx, 630), "far": (rx - 20, 636)} if t > 8.2 else None
        J = HIM.draw(ctx, hip, 1, lean=0.04, feet=feet, expr=expr, look=(1, 0.5) if not op else (1, 0.8),
                     hands=free_hands(HIM, hip, 1, 0.04, hands) if hands else None)
        if hand_over >= 1:
            box(ctx, rx + 10, 676, 110, 76, sticker="CAN'T SLEEP", opened=op, key="hbox")
        burst(ctx, J["head"][0] + 20, J["head"][1] - 10, prog(t, EVENTS["open"], EVENTS["open"] + 2.2))
        if JC is not None:
            speech(ctx, t, "courier", JC["head"][0], JC["head"][1] - 70)
    hud(ctx, t)


def h3(ctx, t):
    with Camera(1.4, 1150, 520).apply(ctx):
        flat(ctx, t)
        coins_out(ctx, t)
        draw_tower(ctx, t)
        hip, feet = seated(600, FY - 92, 1)
        J = HIM.draw(ctx, hip, 1, lean=0.12, feet=feet, expr="tired", look=(1, 0.8), screen_glow=0.8,
                     hands=free_hands(HIM, hip, 1, 0.12, {"near": (680, 640), "far": (668, 646)}))
        P.phone_held(ctx, *J["limbs"]["arm_near"][2])
        jar(ctx, t)
    hud(ctx, t)


# ---- the wound and the stakes --------------------------------------------------------------------------
def s02(ctx, t):
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0 + 0.6, t1))
    with Camera(lerp(1.5, 1.65, prog(t, 17, 25)), 520, 520).apply(ctx):
        flat(ctx, t)
        draw_tower(ctx, t)
        # wisps of the phone's glow drifting up into the villain
        ph = (236 + 60, FY - 230)
        for i in range(8):
            k = (t * 0.6 + hrand("wisp", i)) % 1.0
            a = (1 - k) * prog(t, t0, t0 + 0.5) * (1 - prog(t, t1, t1 + 0.8))
            ctx.c.drawCircle(lerp(ph[0], 450, k) + (hrand("wx", i) - 0.5) * 60, ph[1] - k * 220, 10 + 16 * k, blurred(fill(RED, 0.35 * a), 8))
        P.villain(ctx, 450, FY - 40, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 20.2, 21.0)), lean=-0.25)
        P.wrect(ctx, 120, FY - 90, 560, 50, ("bed", "m"), (60, 64, 92), LINE, 3, seg=6)  # the mattress in front of its feet
        bed_sit(ctx, t, "tired" if t < 21 else "sad", look=(1, 0.7), phone_rgb=mix(BLUE, RED, born * 0.6))
        clock(ctx, "2:13")
    vline(ctx, "V1", 1380, 300, 58)
    vline(ctx, "V2", 1380, 390, 52)
    hud(ctx, t)


def b1(ctx, t):
    with Camera(2.1, 1300, 420).apply(ctx):
        flat(ctx, t)
        draw_tower(ctx, t)
        jar(ctx, t)
        k = prog(t, EVENTS["coin"] - 0.2, EVENTS["coin"] + 0.9)
        if 0 < k < 1:
            coin(ctx, lerp(JAR[0], 860, k), lerp(JAR[1] - 110, 520, k) - math.sin(math.pi * k) * 120, 12)
    cap(ctx, "C2", y=180)
    cap(ctx, "C3", y=250)
    hud(ctx, t)


# ---- the grind --------------------------------------------------------------------------------------------
def bus(ctx, t):
    c = ctx.c
    c.drawRect(skia.Rect.MakeLTRB(-600, 0, W + 600, FY), fill((30, 34, 44)))
    for i in range(5):
        x = 260 + i * 360
        c.drawRect(skia.Rect.MakeXYWH(x, 300, 300, 180), fill((16, 18, 26)))
        for j in range(3):
            lx = (x + 300 - ((t * 500 + hrand("bl", i, j) * 300) % 300))
            glow(ctx, lx, 360 + j * 40, 30, (230, 200, 140), 0.25)
        c.drawRect(skia.Rect.MakeXYWH(x, 300, 300, 180), stroke((70, 76, 90), 6))
    c.drawLine(-600, 230, W + 600, 230, stroke(GREY_L, 8))
    P.floor(ctx, FY)
    for x in (520, 900, 1280):
        wrect(ctx, x - 50, FY - 92, 110, 18, ("seat", x), (70, 80, 110), LINE, 3, seg=2)
        wrect(ctx, x - 64, FY - 210, 22, 130, ("seatb", x), (70, 80, 110), LINE, 3, seg=2)


def g1(ctx, t):
    with Camera(1.7, 960, 560).apply(ctx):
        bus(ctx, t)
        hip, feet = seated(900, FY - 90, 1)
        J = HIM.draw(ctx, hip, 1, lean=0.14, feet=feet, expr="hurt" if t < 36.4 else "smile", look=(1, 0.8), screen_glow=0.9,
                     hands=free_hands(HIM, hip, 1, 0.14, {"near": (976, 640), "far": (964, 646)}))
        hp = J["limbs"]["arm_near"][2]
        P.phone_held(ctx, *hp)
        speech(ctx, t, "boss", hp[0] + 40, hp[1] - 80, size=28, light=False)
        k = prog(t, 36.4, 36.7)
        if t > 36.4:
            a = fade(t, 36.4, 37.8, 0.2, 0.4)
            rrect(ctx, hp[0] - 10, hp[1] - 150, 230, 50, 20, (60, 70, 84), None, a=a)
            draw_text(ctx, "ORDER PLACED", hp[0] + 105, hp[1] - 114, 24, TEXT, a, face="LuckiestGuy-Regular.ttf")
            burst(ctx, J["head"][0] + 20, J["head"][1], prog(t, 36.4, 38.4))
    vline(ctx, "V3", 1350, 320, 52)
    cap(ctx, "C4")
    label(ctx, "WEEK 1")
    hud(ctx, t)


def g2(ctx, t):
    with Camera(1.3, 1180, 520).apply(ctx):
        flat(ctx, t, day=0.8)
        draw_tower(ctx, t)
        coin_out(ctx, t, 41.4)
        jar(ctx, t)
        hip, feet, lean = floor_sit(800)
        J = HIM.draw(ctx, hip, 1, lean=0.2, feet=feet, expr="tired", look=(1, 0.9), screen_glow=0.8,
                     hands=free_hands(HIM, hip, 1, 0.2, {"near": (hip[0] + 64, hip[1] - 60), "far": (hip[0] + 54, hip[1] - 54)}))
        P.phone_held(ctx, *J["limbs"]["arm_near"][2])
        burst(ctx, J["head"][0] + 20, J["head"][1], prog(t, 41.6, 43.4))
    vline(ctx, "V4", 1150, 270, 52)
    label(ctx, "WEEK 2")
    draw_text(ctx, "SUNDAY", 60, LETTERBOX + 214, 30, (150, 150, 160), align="left")
    hud(ctx, t)


def g3(ctx, t):
    if t < 45.2:
        phone_close(ctx, t, "Leo", ["call me sometime?"], EVENTS["bro_text"], avatar=(110, 120, 150))
        if t > 44.7:
            draw_text(ctx, "Read 22:41", W / 2 + 230, 700, 26, (160, 162, 172), ease(prog(t, 44.7, 45.0)), align="right")
        label(ctx, "WEEK 3")
        hud(ctx, t)
        return
    with Camera(1.6, 1380, 500).apply(ctx):
        flat(ctx, t)
        coin_out(ctx, t, 46.0, to=(1520, 300))
        draw_tower(ctx, t)
        jar(ctx, t)
        hip, feet = standing(1260, FY, 1)
        J = HIM.draw(ctx, hip, 1, lean=0.06, feet=feet, expr="sad" if t < 46.0 else ("smile" if t < 46.9 else "sad"), look=(1, -0.2),
                     hands=free_hands(HIM, hip, 1, 0.06, {"near": (1320, 640), "far": (1306, 646)}))
        P.phone_held(ctx, *J["limbs"]["arm_near"][2], on=0.6)
        burst(ctx, J["head"][0] + 20, J["head"][1], prog(t, 46.0, 47.4))
    cap(ctx, "C5")
    label(ctx, "WEEK 3")
    hud(ctx, t)


def g4(ctx, t):
    lt = t - 48.0
    with Camera(1.35, 1100, 520).apply(ctx):
        flat(ctx, t, day=0.5)
        draw_tower(ctx, t)
        jar(ctx, t)
        x, ph = walk_x(1300, lt, -55)
        hip, feet = standing(x, FY, -1, step=ph)
        HIM.draw(ctx, hip, -1, lean=0.1, feet=feet, expr="tired", look=(-1, 0.5))
    vline(ctx, "V5", 520, 330, 52)
    label(ctx, "WEEK 4")
    hud(ctx, t)


def g5(ctx, t):
    with Camera(2.6, JAR[0], 380).apply(ctx):
        flat(ctx, t)
        draw_tower(ctx, t)
        jar(ctx, t)
        coin_out(ctx, t, 55.0, to=(1500, 200))
    cap(ctx, "C6", y=985)
    label(ctx, "WEEK 5")
    hud(ctx, t)


# ---- rock bottom: the tower falls ---------------------------------------------------------------------------
def him_rb(ctx, t, expr=None, look=None):
    """R1/R2/T1: he walks to the tower, pulls a box, and ends up sitting in the fallen boxes."""
    pull, col_ = EVENTS["pull"], EVENTS["collapse"]
    if t < pull - 0.6:
        lt = t - 58.0
        x, ph = walk_x(1000, max(0, lt), 70)
        x = min(x, 1300)
        hip, feet = standing(x, FY, 1, step=ph if x < 1300 else 0)
        return HIM.draw(ctx, hip, 1, lean=0.06, feet=feet, expr=expr or "sad", look=look or (1, -0.6))
    if t < col_ + 0.4:
        hip, feet = standing(1300, FY, 1)
        reach = lerp2((1340, 600), (1380, 520), ease(prog(t, pull - 0.6, pull)))
        if t > col_:
            reach = lerp2((1380, 520), (1330, 420), ease(prog(t, col_, col_ + 0.3)))
        ln = -0.1 if t > col_ else 0.04
        return HIM.draw(ctx, hip, 1, lean=ln, feet=feet, expr="shocked" if t > col_ else "worried", look=(1, -1),
                        hands=free_hands(HIM, hip, 1, ln, {"near": reach, "far": (reach[0] - 20, reach[1] - 30) if t > col_ else None}))
    hip, feet, lean = floor_sit(1210)
    return HIM.draw(ctx, hip, 1, lean=-0.06, feet=feet, expr=expr or "hurt", look=look or (1, 0.3),
                    hands=free_hands(HIM, hip, 1, -0.06, {"near": (hip[0] + 60, FY - 8), "far": (hip[0] - 50, FY - 6)}))


def r1(ctx, t):
    col_ = EVENTS["collapse"]
    with Camera(lerp(1.3, 1.5, prog(t, 58, 68)), 1300, 520, shake=10 * (1 - prog(t, col_, col_ + 0.8)) if t > col_ else 0).apply(ctx):
        flat(ctx, t, day=0.3)
        jar(ctx, t)
        if t < col_:
            draw_tower(ctx, t)
            him_rb(ctx, t)
        else:
            draw_fallen(ctx, t)
            him_rb(ctx, t)
        # a sale buzz on the floor
        sb = EVENTS["sale_buzz"]
        if t > sb:
            a = fade(t, sb, 67.8, 0.2, 0.5)
            P.phone_side(ctx, 1100, FY - 4, on=a)
            rrect(ctx, 1020, FY - 120, 170, 50, 18, RED_D, None, a=a)
            draw_text(ctx, "48% OFF", 1105, FY - 84, 28, TEXT, a, face="LuckiestGuy-Regular.ttf")
    vline(ctx, "V6", 915, 300, 54)
    hud(ctx, t)


def r2(ctx, t):
    with Camera(2.1, 1300, 660).apply(ctx):
        flat(ctx, t, day=0.3)
        draw_fallen(ctx, t)
        him_rb(ctx, t, expr="hurt" if t < 71 else "sad", look=(1, 0.2) if t < 71 else (-0.4, 0.6))
    cap(ctx, "C7")
    hud(ctx, t)


# ---- the turn -----------------------------------------------------------------------------------------------
STICKERS = [(74.6, "BORED"), (75.3, "BAD DAY"), (76.0, "SUNDAY"), (76.7, "LONELY"), (77.4, "TIRED"), (78.1, "2AM")]


def t1(ctx, t):
    if t < 76.2:
        # he holds a box up to his face and reads the sticker
        with Camera(2.2, 1260, 560).apply(ctx):
            flat(ctx, t, day=0.3)
            draw_fallen(ctx, t)
            hip, feet, lean = floor_sit(1210)
            held = (hip[0] + 80, hip[1] - 70)
            J = HIM.draw(ctx, hip, 1, lean=0.0, feet=feet, expr="worried", look=(1, 0.5),
                         hands=free_hands(HIM, hip, 1, 0.0, {"near": held, "far": (held[0] - 16, held[1] + 6)}))
            hp = J["limbs"]["arm_near"][2]
            box(ctx, hp[0] + 40, hp[1] + 40, 110, 76, "LONELY", key="held_t1")
        hud(ctx, t)
        return
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((40, 32, 26)))
    for i, (tm, s) in enumerate(STICKERS):
        k = ease_out_back(prog(t, tm + 1.6, tm + 1.9))
        if k <= 0:
            continue
        x = 420 + (i % 3) * 540
        y = 520 + (i // 3) * 190
        c.save()
        c.translate(x, y)
        c.rotate((hrand("st", i) - 0.5) * 0.16)
        c.scale(k, k)
        tw = text_width(s, 64) + 60
        rrect(ctx, -tw / 2, -50, tw, 100, 8, STICKER, (150, 146, 136), 3)
        draw_text(ctx, s, 0, 22, 64, (40, 38, 36))
        c.restore()
    cap(ctx, "C8", y=250)
    cap(ctx, "C9", y=330)
    hud(ctx, t)


def t2(ctx, t):
    """The lesson drawn: how he felt. A spike at BUY NOW and ON ITS WAY, a drop at the door, a little lower each time."""
    c = ctx.c
    x0, x1, base = 280, 1680, 640
    c.drawLine(x0, 360, x0, 860, stroke(GREY_L, 4))
    c.drawLine(x0, 860, x1, 860, stroke(GREY_L, 4))
    draw_text(ctx, "HOW HE FELT", x0, 310, 40, (170, 170, 180), align="left", face="LuckiestGuy-Regular.ttf")
    c.drawLine(x0, base, x1, base, stroke(GREY, 2, 0.6))
    pts = [(x0, base)]
    cycle = 340
    for n in range(4):
        cx = x0 + 60 + n * cycle
        low = base + 40 + n * 40
        pts += [(cx, base + n * 40), (cx + 50, base - 170 + n * 40), (cx + 130, base - 210 + n * 40), (cx + 170, low + 10), (cx + cycle - 60, low)]
    k = prog(t, 84.4, 90.0)
    L = []
    tot = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    goal, acc = k * tot, 0.0
    L.append(pts[0])
    for i in range(len(pts) - 1):
        d = math.dist(pts[i], pts[i + 1])
        if acc + d >= goal:
            q = (goal - acc) / d if d else 0
            L.append(lerp2(pts[i], pts[i + 1], q))
            break
        L.append(pts[i + 1])
        acc += d
    if len(L) > 1:
        c.drawPath(poly_path(L, closed=False), stroke(TEXT, 6))
    head = L[-1]
    c.drawCircle(head[0], head[1], 9, fill(TEXT))
    # the labels under the first cycle
    cx = x0 + 60
    for (lx, ly, s, tm) in ((cx + 50, base - 210, "BUY NOW", 85.0), (cx + 130, base - 250, "ON ITS WAY", 85.5), (cx + 180, base + 120, "AT THE DOOR", 86.0)):
        a = ease(prog(t, tm, tm + 0.3))
        draw_text(ctx, s, lx, ly, 30, RED if s == "AT THE DOOR" else (190, 196, 210), a, face="LuckiestGuy-Regular.ttf")
    cap(ctx, "C10", y=985)
    hud(ctx, t)


def t3(ctx, t):
    with Camera(1.3, 1300, 520).apply(ctx):
        flat(ctx, t, day=0.7)
        jar(ctx, t)
        door(ctx, 1780, open_k=1.0, light=0.6, key="tdoor", w=150)
        draw_fallen(ctx, t)
        leaving(ctx, t)
        for r0, i in RETURNS:  # each return puts a coin back in the jar
            k = prog(t, r0 - 0.1, r0 + 0.5)
            if 0 < k < 1:
                coin(ctx, lerp(1760, JAR[0], k), lerp(560, JAR[1] - 120, k) - math.sin(math.pi * k) * 160, 12)
        hip, feet = standing(1000, FY, 1)
        J = HIM.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="hopeful", look=(1, 0.4), screen_glow=0.5,
                     hands=free_hands(HIM, hip, 1, 0.04, {"near": (1070, 640), "far": (1056, 646)}))
        P.phone_held(ctx, *J["limbs"]["arm_near"][2], on=0.7)
    hud(ctx, t)


def kitchen(ctx, t):
    P.back_wall(ctx, rgb=(40, 40, 44))
    P.floor(ctx, FY)
    P.table(ctx, 820, 640, 520, key="counter")
    wrect(ctx, 960, 610, 200, 30, "stove", (40, 40, 46), LINE, 3, seg=2)
    ctx.c.drawOval(skia.Rect.MakeLTRB(980, 588, 1120, 614), fill((60, 60, 66)))
    ctx.c.drawOval(skia.Rect.MakeLTRB(980, 588, 1120, 614), stroke(LINE, 3))
    for i in range(5):
        k = (t * 0.5 + hrand("stm", i)) % 1
        ctx.c.drawCircle(1000 + hrand("stx", i) * 100 + math.sin(k * 6 + i) * 10, 580 - k * 200, 18 + 20 * k,
                         blurred(fill((230, 230, 236), 0.2 * (1 - k)), 10))
    glow(ctx, 1050, 600, 200, (240, 200, 150), 0.12)


def t4(ctx, t):
    if t < 106.6:  # BORED: a walk at dusk
        lt = t - 104.0
        with Camera(1.6, 1000, 560).apply(ctx):
            street(ctx, t, lamps=(500, 1500), sky=(70, 74, 96), window_rgb=(150, 140, 110))
            x, ph = walk_x(820, lt, 80)
            hip, feet = standing(x, FY, 1, step=ph)
            HIM.draw(ctx, hip, 1, lean=0.06, feet=feet, expr="smile", look=(1, -0.2))
        label(ctx, "BORED")
    elif t < 109.2:  # LONELY: he calls Leo
        with Camera(1.9, 1360, 540).apply(ctx):
            flat(ctx, t, day=0.6)
            jar(ctx, t)
            hip, feet = standing(1260, FY, 1)
            J0 = HIM.joints(hip, 1, 0.02)
            hx, hy = J0["head"]
            ear = (hx - 50, hy + 12)  # the far ear, behind the head
            P.phone_held(ctx, ear[0] + 6, ear[1] + 20, on=0.6)
            J = HIM.draw(ctx, hip, 1, lean=0.02, feet=feet, expr="happy" if t > 107.6 else "hopeful", look=(1, 0),
                         mouth_open=0.4 * abs(math.sin(t * 9)) if t > 108.8 else 0, near_arm_front=True,
                         hands={"far": ear})
            speech(ctx, t, "bro", hx + 150, hy - 50, light=False)
        label(ctx, "LONELY")
    else:  # BAD DAY: he cooks
        with Camera(1.7, 980, 560).apply(ctx):
            kitchen(ctx, t)
            hip, feet = standing(880, FY, 1)
            stir = (1020 + math.sin(t * 6) * 18, 596 + math.cos(t * 6) * 4)
            J = HIM.draw(ctx, hip, 1, lean=0.08, feet=feet, expr="smile", look=(1, 0.8),
                         hands=free_hands(HIM, hip, 1, 0.08, {"near": stir, "far": (960, 620)}))
            hp = J["limbs"]["arm_near"][2]
            ctx.c.drawLine(hp[0], hp[1], hp[0] + 16, hp[1] + 30, stroke((150, 120, 90), 7))
        label(ctx, "BAD DAY")
    cap(ctx, "C11")
    hud(ctx, t)


# ---- the final fight -----------------------------------------------------------------------------------------
def countdown(t):
    return max(0, math.ceil(EVENTS["zero"] - t))


def f1(ctx, t):
    banner = f"FLASH SALE ENDS IN 00:{countdown(t):02d}"
    if t < 114.0:
        shop_close(ctx, t, "Headphones", "$129", "phones", banner=banner, left="only 1 left")
        hud(ctx, t)
        return
    if 117.4 <= t < 119.4:
        hv = ease(prog(t, 117.4, 118.4)) * (1 - ease(prog(t, 118.9, 119.4)))
        shop_close(ctx, t, "Headphones", "$129", "phones", banner=banner, left="only 1 left", hover=(hv, 1.0), claw=ease(prog(t, 117.6, 118.4)))
        vline(ctx, "V8", 1450, 400, 52)
        hud(ctx, t)
        return
    rise = ease(prog(t, 114.0, 115.6))
    down = ease(prog(t, EVENTS["set_down"] - 0.6, EVENTS["set_down"]))
    back = ease(prog(t, EVENTS["set_down"] + 0.3, EVENTS["set_down"] + 0.9))
    with Camera(lerp(1.6, 1.85, prog(t, 114, 124)), 480, 520, shake=2 * prog(t, 119.5, 122)).apply(ctx):
        flat(ctx, t, lamp_on=0.0)
        hip = (236, FY - 94)
        lean = -0.22 + 0.34 * down * (1 - back)
        J0 = HIM.joints(hip, 1, lean)
        sh = J0["shoulder"]
        chest = (sh[0] + 58, sh[1] + 62)
        P.villain(ctx, 470, FY - 40, scale=lerp(0.6, 1.15, rise), alpha=rise, grin=1.2, lean=-0.3,
                  reach=(chest[0] + 14, chest[1] - 14) if rise > 0.6 and down < 0.3 else None)
        P.wrect(ctx, 120, FY - 90, 560, 50, ("bed", "m"), (60, 64, 92), LINE, 3, seg=6)
        hand = lerp2(chest, DUVET_PHONE, down) if t < EVENTS["set_down"] + 0.3 else lerp2(DUVET_PHONE, chest, back)
        expr = "anxious" if t < 121.6 else ("determined" if t < EVENTS["set_down"] else "closed")
        J = bed_sit(ctx, t, expr, look=(1, 0.7) if t < EVENTS["set_down"] - 0.6 else (1, 1.2), phone=0.0,
                    hand=free_hands(HIM, hip, 1, lean, {"near": hand})["near"], shaky=1.0 - down, lean=lean)
        hp = J["limbs"]["arm_near"][2]
        if t < EVENTS["set_down"]:
            P.phone_held(ctx, *hp, on=1.0, glow_rgb=mix(BLUE, RED, 0.5))
        else:
            P.phone_side(ctx, DUVET_PHONE[0], DUVET_PHONE[1] + 4, on=1.0, glow_rgb=mix(BLUE, RED, 0.5))
        clock(ctx, "2:07")
    vline(ctx, "V7", 1460, 300, 56)
    vline(ctx, "V9", 1460, 390, 52)
    vline(ctx, "V10", 1460, 300, 64)
    label(ctx, "FRIDAY")
    hud(ctx, t)


def f2(ctx, t):
    z = EVENTS["zero"]
    UI = P.PhoneUI(W / 2, 580, 520, 900)
    UI.body(ctx, 1.0)
    red = 1 - prog(t, z, z + 0.6)
    with UI.screen(ctx):
        n = countdown(t)
        if t < z:
            draw_text(ctx, "ENDS IN", UI.cx, 400, 44, (220, 160, 160))
            draw_text(ctx, f"00:{n:02d}", UI.cx, 600, 170, mix(TEXT, RED, 0.6), face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
        else:
            draw_text(ctx, "SALE ENDED", UI.cx, 560, 70, (150, 154, 166), ease(prog(t, z, z + 0.3)), face="LuckiestGuy-Regular.ttf")
    if red > 0:
        glow(ctx, UI.cx, UI.cy, 600, RED, 0.18 * red)
    hud(ctx, t)


def f3(ctx, t):
    with Camera(1.6, 480, 520).apply(ctx):
        flat(ctx, t)
        P.villain_shards(ctx, 600, FY - 40, 1.15, prog(t, 128.0, 130.0))
        P.wrect(ctx, 120, FY - 90, 560, 50, ("bed", "m"), (60, 64, 92), LINE, 3, seg=6)
        laugh = t > EVENTS["laugh"]
        bed_sit(ctx, t, "happy" if laugh else "closed", look=(1, 0.4), phone=0.0,
                hand=(236 - 20 + 58, FY - 94 - 89 + 62 + 30))
        ns = EVENTS["new_sale"]
        P.phone_side(ctx, DUVET_PHONE[0], DUVET_PHONE[1] + 4, on=1.0 if t > ns else 0.3)
        if t > ns:
            a = fade(t, ns, 132.8, 0.2, 0.4)
            ctx.c.drawLine(DUVET_PHONE[0] + 10, DUVET_PHONE[1] - 10, 420, FY - 200, stroke((120, 60, 62), 3, a))
            rrect(ctx, 400, FY - 300, 320, 110, 18, (60, 30, 32), None, a=a)
            draw_text(ctx, "NEW SALE!", 560, FY - 258, 34, TEXT, a, face="LuckiestGuy-Regular.ttf")
            draw_text(ctx, "ENDS IN 23:59:59", 560, FY - 214, 30, (240, 160, 160), a, face="LuckiestGuy-Regular.ttf")
        clock(ctx, "2:08")
    cap(ctx, "C12")
    cap(ctx, "C13", y=260)
    hud(ctx, t)


# ---- payoff -------------------------------------------------------------------------------------------------
def p1(ctx, t):
    gold = EVENTS["gold"]
    warm = ease(prog(t, 133.0, gold))
    with Camera(lerp(1.25, 1.5, prog(t, 133, 141)), 1260, 500).apply(ctx):
        flat(ctx, t, day=1.0, lamp_on=0.0, warm=warm, card=t < EVENTS["postcard"] + 0.4)
        jar(ctx, t)
        for i in range(10):  # coins dropping in, week after week
            tm = 133.6 + i * 0.5
            k = prog(t, tm, tm + 0.4)
            if 0 < k < 1:
                coin(ctx, JAR[0], lerp(JAR[1] - 300, JAR[1] - 60, k * k), 12, gold=t > gold - 0.5)
        if t > gold:
            glow(ctx, JAR[0], JAR[1] - 60, 300, GOLD, 0.3 * (1 - prog(t, gold, gold + 1.5)) + 0.1)
        # him: walks to the window and takes the postcard down
        pc = EVENTS["postcard"]
        x = lerp(1100, 1560, ease(prog(t, 137.4, 139.0)))
        hip, feet = standing(x, FY, 1, step=(t * 1.6) % 1 if 137.4 < t < 139.0 else 0)
        reach = lerp2((x + 60, 640), (POSTCARD[0] - 10, POSTCARD[1] + 14), ease(prog(t, pc - 0.5, pc)))
        if t > pc + 0.4:
            reach = lerp2((POSTCARD[0] - 10, POSTCARD[1] + 14), (x + 70, 600), ease(prog(t, pc + 0.4, pc + 1.0)))
        J = HIM.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="happy" if t > gold else "hopeful", look=(1, -0.4),
                     hands=free_hands(HIM, hip, 1, 0.04, {"near": reach}) if t > pc - 0.5 else None)
        if t > pc + 0.4:
            hp = J["limbs"]["arm_near"][2]
            postcard(ctx, hp[0] + 10, hp[1] - 26, warm=1.0)
    hud(ctx, t)


def sea(ctx, t):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, 640)], [col((90, 80, 120)), col((236, 150, 110)), col((255, 200, 120))], [0, 0.6, 1])
    c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, 640), skia.Paint(Shader=sky))
    glow(ctx, 1500, 610, 600, GOLD, 0.5)
    c.drawCircle(1500, 620, 80, fill((255, 214, 130)))
    sea_sh = skia.GradientShader.MakeLinear([(0, 620), (0, 820)], [col((80, 110, 150)), col((50, 70, 100))])
    c.drawRect(skia.Rect.MakeLTRB(-600, 620, W + 600, 830), skia.Paint(Shader=sea_sh))
    c.drawRect(skia.Rect.MakeXYWH(1380, 626, 240, 8), fill(GOLD, 0.6))
    for i in range(8):
        y = 650 + i * 22
        ph = t * (0.8 + 0.1 * i) + i
        for j in range(6):
            x = -200 + j * 400 + math.sin(ph) * 40 + i * 37
            c.drawLine(x, y, x + 120, y, stroke((200, 214, 230), 3, 0.35))
    sand = poly_path([(-600, 830), (W + 600, 800), (W + 600, 1200), (-600, 1200)])
    c.drawPath(sand, fill((150, 128, 100)))
    wave = 820 + math.sin(t * 1.4) * 8
    c.drawPath(poly_path([(-600, wave), (W + 600, wave - 26), (W + 600, wave - 8), (-600, wave + 16)], smooth=False), fill((220, 230, 236), 0.6))


def p2(ctx, t):
    with Camera(lerp(1.1, 1.25, prog(t, 141, 150)), 1100, 600).apply(ctx):
        sea(ctx, t)
        hip, feet = standing(1000, 822, 1)
        HIM.draw(ctx, hip, 1, lean=0.0, feet=feet, expr="happy", look=(1, -0.3), glow_rgb=GOLD,
                 hands=free_hands(HIM, hip, 1, 0.0, {"near": (1050, 700)}))
    cap(ctx, "C14")
    cap(ctx, "C15", y=260)
    hud(ctx, t)


def vt(ctx, t):
    UI = P.PhoneUI(W / 2, 640, 420, 700)
    a = 1.0
    UI.body(ctx, 1.0)
    turn = ease(prog(t, EVENTS["cart_tomorrow"], EVENTS["cart_tomorrow"] + 0.5))
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, 100), fill((26, 28, 36)))
        draw_text(ctx, "YOUR CART (3)", x0 + 30, y0 + 68, 34, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
        for i in range(3):
            y = y0 + 140 + i * 110
            rrect(ctx, x0 + 26, y, 80, 80, 12, (52, 56, 70), None)
            ctx.c.drawRect(skia.Rect.MakeXYWH(x0 + 130, y + 20, 160 - i * 30, 14), fill((90, 94, 110)))
            ctx.c.drawRect(skia.Rect.MakeXYWH(x0 + 130, y + 50, 70, 14), fill((70, 74, 90)))
        bx, by, bw, bh = UI.x0 + 50, UI.y0 + UI.h - 170, UI.w - 100, 84
        rgb = mix(RED, (70, 84, 110), turn)
        rrect(ctx, bx, by, bw, bh, 22, rgb, None)
        draw_text(ctx, "BUY NOW", UI.cx, by + 56, 40, TEXT, 1 - turn, face="LuckiestGuy-Regular.ttf")
        draw_text(ctx, "TOMORROW", UI.cx, by + 56, 40, TEXT, turn, face="LuckiestGuy-Regular.ttf")
    cap(ctx, "V1", y=190, size=60)
    cap(ctx, "V2", y=190, size=60)


def x1(ctx, t):
    fd = EVENTS["face_down"]
    if t < 159.6:
        UI = P.PhoneUI(W / 2, 580, 520, 900)
        UI.body(ctx, 1.0)
        with UI.screen(ctx):
            draw_text(ctx, "YOUR CART (1)", UI.cx, 300, 44, TEXT, face="LuckiestGuy-Regular.ttf")
            rrect(ctx, UI.cx - 150, 360, 300, 260, 18, (44, 48, 60), None)
            item_icon(ctx, "box", UI.cx, 450)
        return
    with Camera(1.4, 600, 520).apply(ctx):
        flat(ctx, t)
        jar(ctx, t, x=JAR[0] - 60, lab="THE SEA", amount=GOAL, gold=True)
        jar(ctx, t, x=JAR[0] + 60, lab="SNOW", amount=40, gold=False, s=0.85)
        # the seashell from the sea
        ctx.c.drawPath(poly_path([(1150, 430), (1130, 404), (1150, 392), (1170, 404)], smooth=True), fill((236, 214, 196)))
        if t < fd + 1.0:
            down = ease(prog(t, fd - 0.6, fd))
            back = ease(prog(t, fd + 0.2, fd + 0.8))
            lean = -0.22 + 0.34 * down * (1 - back)
            sh = HIM.joints((236, FY - 94), 1, lean)["shoulder"]
            chest = (sh[0] + 58, sh[1] + 62)
            hand = lerp2(chest, DUVET_PHONE, down) if t < fd + 0.2 else lerp2(DUVET_PHONE, chest, back)
            J = bed_sit(ctx, t, "tired" if t < fd else "smile", look=(1, 0.6) if t < fd - 0.6 else (1, 1.2), phone=0.0, lean=lean,
                        hand=free_hands(HIM, (236, FY - 94), 1, lean, {"near": hand})["near"])
            if t < fd:
                P.phone_held(ctx, *J["limbs"]["arm_near"][2])
            else:
                P.phone_side(ctx, DUVET_PHONE[0], DUVET_PHONE[1] + 4, face_down=True)
        else:
            in_bed(ctx)
            P.phone_side(ctx, 600, FY - 134, face_down=True)
        clock(ctx, "2:07")


def title(ctx, t):
    a = fade(t, EVENTS["title"], DURATION, 0.8, 1.2)
    draw_text(ctx, "SOLD.", W / 2, 520, 220, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 260 + 520 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=46)
    cap(ctx, "T2", y=760, size=64, rgb=GOLD, glow_rgb=(170, 110, 20))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "S02": s02, "B1": b1,
    "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "R1": r1, "R2": r2,
    "T1": t1, "T2": t2, "T3": t3, "T4": t4, "F1": f1, "F2": f2, "F3": f3, "P1": p1, "P2": p2, "VT": vt, "X1": x1, "TT": title,
}
CONTINUOUS = {"R2"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1_, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "TT":
        black(ctx, prog(t, DURATION - 1.0, DURATION))
