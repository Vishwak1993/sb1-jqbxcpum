"""ONE MORE MATCH.: picture. scene(ctx) draws any frame of the film.

The device: his rank badge and TONIGHT: n MATCHES, top-left. The badge climbs all film (SILVER to DIAMOND) while the
real things go grey: the keeper gloves on the shelf, practice, the final. He makes Diamond the night his team loses the
final without him; three days later the season ends and every rank resets to UNRANKED. The rank was never kept. The
same box ends relabelled REAL MATCHES 1, in gold.
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
from timeline import (SCENES, CAPS, CUES, BUBBLES, EVENTS, DURATION, scene_at, rank_at, tonight_at, hud_changed,  # noqa: E402
                      RELABEL, G1_T0, G1_NIGHT, G1_DAYS, G1_CLOCKS)
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
LG = "LuckiestGuy-Regular.ttf"
SCREEN_GLOW = (110, 150, 230)
GLOVE = (90, 170, 110)
TIERS = {"SILVER": (184, 188, 200), "GOLD": (196, 164, 84), "PLATINUM": (96, 196, 184), "DIAMOND": (150, 190, 255),
         "UNRANKED": (110, 110, 118)}


def tier_rgb(name):
    return TIERS.get(name.split(" ")[0], (150, 150, 156))


def headset(ctx, hx, hy, f, s):
    c = ctx.c
    c.drawPath(poly_path([(hx - f * 30 * s, hy - 2 * s), (hx - f * 24 * s, hy - 44 * s), (hx + f * 6 * s, hy - 56 * s),
                          (hx + f * 30 * s, hy - 46 * s)], closed=False, smooth=True), stroke((40, 44, 52), 9 * s))
    rrect(ctx, hx - f * 30 * s - 14 * s, hy - 16 * s, 28 * s, 36 * s, 10 * s, (52, 56, 70), LINE, 3 * s)
    c.drawPath(poly_path([(hx - f * 22 * s, hy + 14 * s), (hx + f * 4 * s, hy + 30 * s), (hx + f * 20 * s, hy + 26 * s)],
                         closed=False, smooth=True), stroke((40, 44, 52), 4 * s))


def headband(ctx, hx, hy, f, s):
    ctx.c.drawPath(poly_path([(hx - 48 * s, hy - 18 * s), (hx, hy - 30 * s), (hx + 48 * s, hy - 18 * s)], closed=False, smooth=True),
                   stroke((226, 128, 60), 10 * s))


def glasses(ctx, hx, hy, f, s):
    fx = hx + f * 14 * s
    for side in (-1, 1):
        ctx.c.drawCircle(fx + side * 13 * s, hy - 2 * s, 9 * s, stroke(LINE, 2.5 * s))
    ctx.c.drawLine(fx - 4 * s, hy - 2 * s, fx + 4 * s, hy - 2 * s, stroke(LINE, 2.5 * s))


def mum_hair(ctx, hx, hy, f, s):
    p = poly_path([(hx - 50 * s, hy - 4 * s), (hx - 46 * s, hy - 32 * s), (hx, hy - 52 * s), (hx + 46 * s, hy - 32 * s),
                   (hx + 50 * s, hy - 4 * s), (hx + 30 * s, hy - 28 * s), (hx, hy - 34 * s), (hx - 30 * s, hy - 28 * s)], smooth=True)
    ctx.c.drawPath(p, fill((54, 40, 36)))
    ctx.c.drawCircle(hx - f * 44 * s, hy - 8 * s, 14 * s, fill((54, 40, 36)))
    ctx.c.drawCircle(hx + f * 14 * s, hy - 22 * s, 2.6 * s, fill((180, 60, 60)))


HIM_G = Character("him", extra=headset)
HIM = Character("him")
DEV = Character("dev", skin=(176, 136, 104), extra=headband)
DAD = Character("dad", skin=(214, 196, 176), extra=glasses)
MUM = Character("mum", skin=(206, 170, 140), extra=mum_hair)


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


def badge(ctx, x, y, s, tier, a=1.0, crack=0.0):
    """A rank badge: a shield in the tier's colour with a chevron, centred at (x, y)."""
    if a <= 0:
        return
    rgb = tier_rgb(tier)
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if a < 1:
        c.saveLayerAlpha(None, int(255 * a))
    shield = poly_path([(-40, -46), (40, -46), (44, 6), (0, 52), (-44, 6)], smooth=False)
    if tier != "UNRANKED":
        c.drawPath(shield, blurred(fill(rgb, 0.5), 10))
    c.drawPath(shield, fill(mix(rgb, (20, 20, 26), 0.25)))
    c.drawPath(poly_path([(-28, -34), (28, -34), (30, 4), (0, 36), (-30, 4)]), fill(rgb))
    c.drawPath(shield, stroke(LINE, 4))
    if tier.startswith("DIAMOND"):
        c.drawPath(poly_path([(0, -22), (18, 0), (0, 22), (-18, 0)]), fill((236, 246, 255)))
    elif tier != "UNRANKED":
        for k in range(len(tier.split(" ")[1]) if " " in tier else 1):
            c.drawPath(poly_path([(-16, -10 + k * 12), (0, -2 + k * 12), (16, -10 + k * 12)], closed=False), stroke((30, 30, 36), 5))
    else:
        draw_text(ctx, "?", 0, 14, 40, (60, 60, 66), face=LG)
    if crack > 0:
        for pts in ([(4, -46), (-6, -16), (8, 4), (-4, 30)], [(-6, -16), (-30, -4)], [(8, 4), (32, 10)]):
            n = max(2, int(len(pts) * min(1, crack)))
            c.drawPath(poly_path(pts[:n], closed=False), stroke((20, 20, 26), 4))
    if a < 1:
        c.restore()
    c.restore()


def hud(ctx, t, a=1.0):
    """The rank badge and TONIGHT: n MATCHES; at the end the same box says REAL MATCHES 1, in gold."""
    a *= prog(t, 0.6, 1.0)
    if a <= 0:
        return
    x, y = 56, LETTERBOX + 26
    lc = hud_changed(t)
    pop = math.sin(math.pi * prog(t, lc, lc + 0.35)) if lc is not None and lc <= t <= lc + 0.35 else 0.0
    if t >= RELABEL:
        k = prog(t, RELABEL, RELABEL + 0.6)
        rrect(ctx, x, y, 300, 92, 14, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
        if k < 1:
            draw_text(ctx, "RANK", x + 20, y + 32, 22, (160, 160, 168), a * (1 - k), align="left")
            ctx.c.drawLine(x + 16, y + 26, x + 16 + 80 * ease(min(1, k * 2)), y + 26, stroke(RED, 4, a))
            return
        draw_text(ctx, "REAL MATCHES", x + 20, y + 32, 22, (200, 180, 140), a, align="left")
        draw_text(ctx, "1", x + 22, y + 80, 52 * (1 + 0.35 * math.sin(math.pi * prog(t, RELABEL + 0.6, RELABEL + 0.95))), GOLD, a,
                  align="left", face=LG, glow_rgb=GOLD)
        return
    tier = rank_at(t)
    rrect(ctx, x, y, 330, 104, 14, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
    badge(ctx, x + 50, y + 52, 0.75 * (1 + 0.25 * pop), tier, a)
    draw_text(ctx, "RANK", x + 100, y + 32, 22, (160, 160, 168), a, align="left")
    draw_text(ctx, tier, x + 100, y + 66, 32, tier_rgb(tier), a, align="left", face=LG)
    draw_text(ctx, f"TONIGHT: {tonight_at(t)} MATCHES", x + 100, y + 94, 20, (170, 170, 178), a, align="left")


def pop_label(ctx, t, t0, s, x, y, rgb, dur=1.6, size=40, dark_text=True):
    a = fade(t, t0, t0 + dur, 0.12, 0.3)
    if a <= 0:
        return
    k = ease_out_back(prog(t, t0, t0 + 0.2))
    w = text_width(s, size, LG) + 36
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.scale(0.7 + 0.3 * k, 0.7 + 0.3 * k)
    rrect(ctx, -w / 2, -size, w, size * 1.4, 12, rgb, None, a=a)
    draw_text(ctx, s, 0, size * 0.22, size, (16, 16, 18) if dark_text else TEXT, a, face=LG)
    c.restore()


# ---- the game on the monitor ------------------------------------------------------------------------
def game(ctx, t, x, y, w, h, banner=None, banner_t=0.0, play_again=0.0, logoff=None, cursor=None, popup=None,
         promo=False, big_badge=None, badge_crack=0.0, dark=0.0, clock=None, sticky=None, red_again=0.0):
    """The game's screen inside (x, y, w, h). s scales the UI to the screen size."""
    c = ctx.c
    s = w / 340
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill((22, 36, 44)))
    # the arena: lanes and little players
    for i in range(3):
        c.drawLine(x, y + h * (0.3 + 0.2 * i), x + w, y + h * (0.2 + 0.25 * i), stroke((40, 66, 72), 10 * s))
    for i in range(8):
        px = x + w * (0.1 + 0.8 * ((hrand("pl", i) + t * 0.05 * (1 if i % 2 else -1)) % 1.0))
        py = y + h * (0.2 + 0.6 * hrand("py", i))
        c.drawCircle(px, py, 5 * s, fill((90, 150, 230) if i % 2 else (220, 90, 90)))
    if banner:
        k = ease_out_back(prog(t, banner_t, banner_t + 0.3))
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill((0, 0, 0), 0.45))
        rgb = (120, 190, 255) if banner == "VICTORY" else RED
        draw_text(ctx, banner, x + w / 2, y + h * 0.42, 54 * s * max(0.3, k), rgb, face=LG, glow_rgb=rgb)
    if big_badge:
        badge(ctx, x + w / 2, y + h * 0.42, 1.5 * s, big_badge, 1.0, badge_crack)
        draw_text(ctx, big_badge, x + w / 2, y + h * 0.42 + 96 * s, 26 * s, tier_rgb(big_badge), face=LG)
    if promo:
        rrect(ctx, x + w * 0.15, y + h * 0.08, w * 0.7, 30 * s, 8 * s, (40, 30, 60), None)
        draw_text(ctx, "PROMO: WIN 1 FOR DIAMOND", x + w / 2, y + h * 0.08 + 21 * s, 15 * s, (200, 210, 255), face=LG)
    if play_again > 0:
        bx, by, bw, bh = x + w * 0.2, y + h * 0.66, w * 0.6, 34 * s
        rgb = mix((70, 130, 220), RED, red_again)
        glow(ctx, bx + bw / 2, by + bh / 2, 60 * s, rgb, 0.3 * play_again)
        rrect(ctx, bx, by, bw, bh, 8 * s, rgb, None, a=play_again)
        draw_text(ctx, "PLAY AGAIN?", bx + bw / 2, by + 24 * s, 20 * s, TEXT, play_again, face=LG)
    if logoff is not None:
        bx, by, bw, bh = x + w * 0.35, y + h * 0.84, w * 0.3, 22 * s
        rrect(ctx, bx, by, bw, bh, 6 * s, mix((50, 50, 58), (200, 200, 210), logoff), None)
        draw_text(ctx, "LOG OFF", bx + bw / 2, by + 16 * s, 13 * s, (20, 20, 26) if logoff > 0.5 else (200, 200, 210), face=LG)
    if popup:
        rrect(ctx, x + w * 0.12, y + 8 * s, w * 0.76, 60 * s, 10 * s, (236, 232, 214), None)
        draw_text(ctx, popup[0], x + w / 2, y + 32 * s, 18 * s, (40, 40, 46), face=LG)
        draw_text(ctx, popup[1], x + w / 2, y + 56 * s, 15 * s, RED, face=LG)
    if clock:
        c.drawRect(skia.Rect.MakeXYWH(x, y + h - 18 * s, w, 18 * s), fill((10, 12, 16), 0.9))
        draw_text(ctx, clock, x + w - 8 * s, y + h - 4 * s, 13 * s, (200, 206, 216), align="right")
    if cursor:
        cx, cy = cursor
        c.drawPath(poly_path([(cx, cy), (cx, cy + 22 * s), (cx + 6 * s, cy + 16 * s), (cx + 14 * s, cy + 16 * s)]), fill(TEXT))
        c.drawPath(poly_path([(cx, cy), (cx, cy + 22 * s), (cx + 6 * s, cy + 16 * s), (cx + 14 * s, cy + 16 * s)]), stroke(LINE, 1.5 * s))
    if dark > 0:
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill((8, 8, 10), dark))
    c.restore()
    if sticky:
        sx, sy = x + w - 60 * s, y - 14 * s
        c.save()
        c.translate(sx, sy)
        c.rotate(6)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, 72 * s, 60 * s), fill((236, 224, 150)))
        draw_text(ctx, sticky[0], 36 * s, 26 * s, 20 * s, (50, 46, 40), face=LG)
        draw_text(ctx, sticky[1], 36 * s, 48 * s, 13 * s, (50, 46, 40), face=LG)
        c.restore()


# ---- the room ---------------------------------------------------------------------------------------
MON = (1000, 400, 340, 210)  # the monitor screen in the room
SEAT = (800, 690)


def room(ctx, t, morning=0.0, door_k=0.0, door_light=0.0, gloves_grey=0.0, screen_glow=1.0, clock="11:02", shelf_gloves=True, **gk):
    c = ctx.c
    P.back_wall(ctx, rgb=mix((20, 22, 28), (60, 58, 60), morning))
    P.floor(ctx, FY)
    P.window(ctx, 1500, 200, 220, 220, "rwin", night=morning < 0.5, sky=mix((24, 28, 42), (236, 214, 170), morning))
    if morning > 0:
        glow(ctx, 1610, 310, 360, (255, 226, 170), 0.2 * morning)
    door(ctx, 200, open_k=door_k, key="rdoor", light=door_light)
    if door_light > 0:
        cone(ctx, (285, FY - 200), (180, FY), (620, FY), (255, 214, 160), 0.12 * door_light)
    # the shelf with the keeper gloves and boots
    wrect(ctx, 480, 430, 240, 14, "shelf", (92, 74, 60), LINE, 3, seg=2)
    gr = mix(GLOVE, (90, 90, 96), gloves_grey)
    for i, gx in enumerate((540, 600) if shelf_gloves else ()):
        c.drawPath(poly_path([(gx - 22, 430), (gx - 26, 392), (gx - 10, 372), (gx + 14, 376), (gx + 24, 400), (gx + 20, 430)], smooth=True), fill(gr))
        c.drawPath(poly_path([(gx - 22, 430), (gx - 26, 392), (gx - 10, 372), (gx + 14, 376), (gx + 24, 400), (gx + 20, 430)], smooth=True), stroke(LINE, 3))
    if gloves_grey > 0.3:
        for i in range(10):
            c.drawCircle(520 + hrand("dust", i) * 120, 380 + hrand("dusty", i) * 50, 1.6, fill((170, 170, 176), gloves_grey * 0.6))
    wrect(ctx, 650, 404, 50, 26, "boot", (60, 60, 68), LINE, 3, seg=2)
    # desk, monitor, keyboard, clock
    P.table(ctx, 880, 640, 560, key="desk")
    x, y, w, h = MON
    if screen_glow > 0:
        glow(ctx, x + w / 2, y + h / 2, 560, SCREEN_GLOW, 0.22 * screen_glow)
        cone(ctx, (x, y + h / 2), (SEAT[0] - 120, FY), (x, FY), SCREEN_GLOW, 0.05 * screen_glow)
    wrect(ctx, x + w / 2 - 12, y + h, 24, 640 - y - h, "mstand", (40, 40, 46), LINE, 3, seg=1)
    rrect(ctx, x - 12, y - 12, w + 24, h + 24, 10, (18, 18, 22), LINE, 3)
    game(ctx, t, x, y, w, h, dark=1 - screen_glow if screen_glow < 1 else 0.0, **gk)
    rrect(ctx, 900, 626, 150, 14, 4, (46, 46, 52), LINE, 2)
    rrect(ctx, 1070, 628, 28, 12, 6, (46, 46, 52), LINE, 2)
    rrect(ctx, 1360, 590, 70, 42, 6, (14, 14, 16), (70, 70, 76), 2)
    draw_text(ctx, clock, 1395, 620, 22, (200, 210, 220), face=LG)


def at_desk(ctx, t, ch=None, expr="determined", look=(1, -0.1), lean=0.18, glow_on=1.0, hands=None, **kw):
    """Him in the gaming chair, hands on the keyboard and mouse."""
    ch = ch or HIM_G
    sx, sy = SEAT
    P.chair(ctx, sx, sy, 1, key="gchair")
    wrect(ctx, sx - 60, sy - 160, 20, 150, "gback", (60, 30, 36), LINE, 3, seg=2)
    hip, feet = seated(sx, sy, 1)
    hands = hands or {"near": (1074, 628), "far": (960, 628)}
    return ch.draw(ctx, hip, 1, lean=lean, feet=feet, expr=expr, look=look, screen_glow=0.9 * glow_on,
                   hands=free_hands(ch, hip, 1, lean, hands), mouth_open=talk("him", t), **kw)


def monitor_close(ctx, t, **gk):
    """The monitor filling the frame (with a bezel), for the game's own moments."""
    x, y, w, h = 300, 150, 1320, 700
    glow(ctx, W / 2, H / 2, 900, SCREEN_GLOW, 0.15)
    rrect(ctx, x - 26, y - 26, w + 52, h + 52, 22, (14, 14, 18), (70, 70, 80), 4)
    game(ctx, t, x, y, w, h, **gk)
    return x, y, w, h


def chat(ctx, t, sender, msgs, times, mine=(), avatar=(176, 136, 104), system=()):
    """A phone chat, smaller than the toolkit's, so a caption fits underneath."""
    UI = P.PhoneUI(W / 2, 540, 480, 760)
    UI.body(ctx, 1.0)
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, 110), fill((26, 28, 36)))
        wcircle(ctx, x0 + 54, y0 + 72, 24, "av_" + sender, avatar, None, 0)
        draw_text(ctx, sender, x0 + 92, y0 + 84, 38, TEXT, align="left")
        yy = y0 + 150
        for i, m in enumerate(msgs):
            a = ease(prog(t, times[i], times[i] + 0.2))
            if a <= 0:
                break
            if i in system:
                draw_text(ctx, m, W / 2, yy + 26, 30, (230, 120, 110), a, face=LG)
                yy += 56
                continue
            hgt = P.bubble(ctx, x0 + UI.w - 62 if i in mine else x0 + 22, yy, m, i in mine, 34, a, maxw=400)
            yy += hgt + 12


def stand(ch, ctx, x, f=1, lean=0.04, step=0.0, **kw):
    hip, feet = standing(x, FY, f, ch.scale, step=step)
    if kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


# ---- the hook ----------------------------------------------------------------------------------------
def s01(ctx, t):
    vic = t >= EVENTS["victory0"]
    with Camera(lerp(1.95, 1.7, ease(prog(t, 0, 6))), 1100, 500).apply(ctx):
        room(ctx, t, clock="11:02", banner="VICTORY" if vic else None, banner_t=EVENTS["victory0"])
        at_desk(ctx, t, expr="happy" if vic else "determined", look=(1, -0.2))
    cap(ctx, "C1", y=985)
    hud(ctx, t)


def h1(ctx, t):
    clicks = EVENTS["clicks"]
    times = ["11:40", "12:25", "1:10"]
    i = sum(1 for c_ in clicks if t >= c_)
    clock = "11:02" if i == 0 else times[i - 1]
    last = clicks[i - 1] if i else 6.0
    x, y, w, h = 300, 150, 1320, 700
    bx, by = x + w * 0.5, y + h * 0.66 + 40
    nxt = clicks[i] if i < len(clicks) else 99
    k = ease(prog(t, nxt - 0.9, nxt - 0.2))
    cur = (lerp(x + w * 0.8, bx, k), lerp(y + h * 0.9, by, k))
    flash = t - last < 0.35 and i > 0
    monitor_close(ctx, t, banner="VICTORY" if not flash else None, banner_t=last + 0.35 if i else 1.0,
                  play_again=1.0 if not flash else 0.0, cursor=cur, clock=clock)
    if flash:
        draw_text(ctx, "MATCH FOUND", W / 2, H / 2, 90, (200, 220, 255), 1 - prog(t, last, last + 0.35), face=LG)
    hud(ctx, t)


def h2(ctx, t):
    knock = EVENTS["knock"]
    open_k = ease(prog(t, knock + 0.3, knock + 0.8))
    with Camera(1.45, 760, 500).apply(ctx):
        room(ctx, t, door_k=open_k, door_light=open_k, clock="11:58", play_again=1.0)
        if open_k > 0.3:
            Jm = stand(MUM, ctx, 330, f=1, lean=0.02, expr="worried", look=(1, 0.1), mouth_open=talk("mum", t),
                       alpha=min(1, (open_k - 0.3) * 3))
            speech(ctx, t, "mum", Jm["head"][0] + 60, Jm["head"][1] - 76)
        J = at_desk(ctx, t, expr="determined", look=(1, -0.1))
        speech(ctx, t, "him", J["head"][0] + 60, J["head"][1] - 80)
    cap(ctx, "C2", y=985)
    hud(ctx, t)


# ---- the wound and the stakes ------------------------------------------------------------------------
def s02(ctx, t):
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0, t1))
    with Camera(lerp(1.9, 1.6, ease(prog(t, t0 - 0.4, t1))), lerp(1060, 1140, ease(prog(t, t0 - 0.4, t1))), 500).apply(ctx):
        glow(ctx, 1170, 500, 300, RED, 0.25 * born)
        room(ctx, t, clock="1:40", play_again=1.0)
        if born > 0:
            P.villain(ctx, 1540, FY, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 21.0, 21.6)), lean=-0.3)
        at_desk(ctx, t, expr="tired" if t < 22 else "anxious", look=(1, -0.1))
    vline(ctx, "V1", 560, 300, 58)
    vline(ctx, "V2", 560, 380, 52)
    hud(ctx, t)


def b1(ctx, t):
    chat(ctx, t, "Dev", ["final on saturday, 10am. we need our keeper", "i'll be there.", "practice tmrw 6pm"],
         [EVENTS["dev_text"], EVENTS["his_text"], EVENTS["dev_text2"]], mine=(1,))
    hud(ctx, t)


# ---- the grind --------------------------------------------------------------------------------------
def g1(ctx, t):
    """One locked shot, four nights. The rank climbs; the gloves go grey."""
    i = min(3, int((t - G1_T0) // G1_NIGHT))
    n0 = G1_T0 + i * G1_NIGHT
    vic = t > n0 + 2.6
    with Camera(1.6, 1060, 500).apply(ctx):
        room(ctx, t, clock=G1_CLOCKS[i], gloves_grey=0.25 * (i + 1) + 0.2 * prog(t, n0, n0 + G1_NIGHT),
             banner="VICTORY" if vic else None, banner_t=n0 + 2.6, play_again=1.0 if vic else 0.0)
        if i >= 1:
            P.villain(ctx, 1540, FY, scale=0.9 + 0.08 * i, alpha=0.5 + 0.15 * i, grin=1.0, lean=-0.3)
        J = at_desk(ctx, t, expr="determined" if not vic else "happy", look=(1, -0.1), lean=0.18 + 0.03 * i)
        if i >= 1:  # practice texts he leaves unread
            pop_label(ctx, t, n0 + 1.0, "Dev: practice?", 1150, 560, (70, 110, 200), dur=3.2, size=26, dark_text=False)
    black(ctx, 1 - prog(t, n0, n0 + 0.1))
    label(ctx, G1_DAYS[i])
    vline(ctx, "V3", 600, 300, 56)
    vline(ctx, "V4", 600, 300, 54)
    vline(ctx, "V5", 600, 300, 54)
    hud(ctx, t)


def pitch(ctx, t, warm=0.0, dusk=0.0):
    c = ctx.c
    top = mix(mix((100, 140, 200), (60, 60, 96), dusk), (130, 170, 220), warm)
    bot = mix(mix((190, 210, 230), (220, 140, 110), dusk), (250, 210, 150), warm)
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, FY)], [col(top), col(bot)])
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), skia.Paint(Shader=sky))
    if warm > 0:
        glow(ctx, 1600, 300, 500, GOLD, 0.3 * warm)
    for i in range(16):
        x = -200 + i * 150
        hgt = 60 + 50 * hrand("tree", i)
        c.drawCircle(x, FY - 120 - hgt * 0.4, hgt, fill(mix((60, 90, 70), (40, 50, 50), dusk)))
    c.drawRect(skia.Rect.MakeLTRB(-600, FY - 130, W + 600, FY + 400), fill(mix((80, 150, 90), (60, 100, 70), dusk)))
    for i in range(12):
        c.drawRect(skia.Rect.MakeXYWH(-600 + i * 260, FY - 130, 130, 530), fill((255, 255, 255), 0.04))
    c.drawLine(-600, FY, W + 600, FY, stroke((236, 240, 236), 4, 0.6))


def goal(ctx, x):
    c = ctx.c
    for i in range(8):
        c.drawLine(x - 160 + i * 20, FY - 300, x - 200 + i * 20, FY, stroke((236, 236, 240), 1.5, 0.5))
    for j in range(6):
        c.drawLine(x - 200, FY - 300 + j * 50, x, FY - 300 + j * 50, stroke((236, 236, 240), 1.5, 0.5))
    wrect(ctx, x - 6, FY - 310, 14, 310, "post", (240, 240, 244), LINE, 3, seg=1)
    wrect(ctx, x - 200, FY - 312, 206, 14, "bar", (240, 240, 244), LINE, 3, seg=2)


def ball(ctx, x, y, r=18):
    wcircle(ctx, x, y, r, "ball", (240, 240, 240), LINE, 3)
    ctx.c.drawCircle(x + 3, y - 2, r * 0.35, fill(LINE))


def g2(ctx, t):
    with Camera(1.5, 900, 520).apply(ctx):
        pitch(ctx, t, dusk=1.0)
        goal(ctx, 560)
        stand(grey("tm1"), ctx, 1240, f=-1, lean=0.02, expr="neutral", look=(-1, 0.1))
        Jd = stand(DEV, ctx, 920, f=-1, lean=0.04, expr="worried", look=(-1, 0.1), mouth_open=talk("dev", t))
        ball(ctx, 860, FY - 18)
        speech(ctx, t, "dev", Jd["head"][0] - 20, Jd["head"][1] - 80)
    label(ctx, "PRACTICE")
    cap(ctx, "C3", y=985)
    hud(ctx, t)


def g3(ctx, t):
    open_k = ease(prog(t, 61.4, 61.9))
    with Camera(1.45, 760, 500).apply(ctx):
        room(ctx, t, morning=1.0, door_k=open_k, door_light=0.6 * open_k, clock="6:05", banner="VICTORY", play_again=1.0)
        if open_k > 0.3:
            Jd = stand(DAD, ctx, 330, f=1, lean=0.02, expr="neutral", look=(1, 0.1), mouth_open=talk("dad", t),
                       hands={"far": (290, 640)}, alpha=min(1, (open_k - 0.3) * 3))
            hp = Jd["limbs"]["arm_far"][2]
            wrect(ctx, hp[0] - 30, hp[1], 60, 44, "bag", (70, 54, 44), LINE, 3, seg=2)
            speech(ctx, t, "dad", Jd["head"][0] + 50, Jd["head"][1] - 76)
        J = at_desk(ctx, t, expr="tired", look=(1, 0.0), lean=0.26)
        speech(ctx, t, "him", J["head"][0] + 60, J["head"][1] - 80)
    cap(ctx, "C4", y=985)
    hud(ctx, t)


# ---- rock bottom and the turn --------------------------------------------------------------------
def r1(ctx, t):
    if t < EVENTS["phone"]:
        won = t >= EVENTS["promo_win"]
        dia = t >= 72.4
        jump = ease(prog(t, EVENTS["jump"], EVENTS["jump"] + 0.3))
        with Camera(1.6, 1060, 500).apply(ctx):
            room(ctx, t, clock="3:52", gloves_grey=1.0, promo=not won, banner=None if dia else ("VICTORY" if won else None),
                 banner_t=EVENTS["promo_win"], big_badge="DIAMOND" if dia else None)
            if jump < 0.5:
                at_desk(ctx, t, expr="anxious" if not won else "happy", look=(1, -0.1), lean=0.22)
            else:
                hip, feet = standing(860, FY, 1)
                hop = 18 * abs(math.sin((t - EVENTS["jump"]) * 7)) * (1 - prog(t, 74.5, 75.5))
                hip = (hip[0], hip[1] - hop)
                J0 = HIM_G.joints(hip, 1, -0.05)
                sh = J0["shoulder"]
                HIM_G.draw(ctx, hip, 1, lean=-0.05, feet={k: (v[0], min(FY, v[1] - hop)) for k, v in feet.items()},
                           expr="happy", look=(1, -0.5), mouth_open=0.6,
                           hands=free_hands(HIM_G, hip, 1, -0.05, {"far": (sh[0] - 30, sh[1] - 95), "near": (sh[0] + 50, sh[1] - 85)}))
        label(ctx, "FRI 3:52 AM")
        vline(ctx, "V6", 600, 300, 54)
    else:
        chat(ctx, t, "Dev", ["9 missed calls", "where are you??", "we lost 2-1. no keeper."],
             [EVENTS["missed"], EVENTS["missed"] + 0.5, EVENTS["dev_lost"]], system=(0,))
        label(ctx, "SAT 11:48 AM")
        cap(ctx, "C5", y=990)
    hud(ctx, t)


def t1(ctx, t):
    crack = prog(t, EVENTS["crack"], EVENTS["crack"] + 1.2)
    reset = t >= EVENTS["reset"]
    fall = ease(prog(t, EVENTS["reset"] - 0.4, EVENTS["reset"]))
    x, y, w, h = 300, 150, 1320, 700
    glow(ctx, W / 2, H / 2, 900, SCREEN_GLOW, 0.15)
    rrect(ctx, x - 26, y - 26, w + 52, h + 52, 22, (14, 14, 18), (70, 70, 80), 4)
    game(ctx, t, x, y, w, h, popup=("SEASON 4 ENDS IN 3 DAYS", "ALL RANKS WILL RESET") if t > EVENTS["season"] else None)
    s = w / 340
    if not reset:
        ctx.c.save()
        ctx.c.translate(0, 80 * fall * fall)
        badge(ctx, W / 2, y + h * 0.6, 0.62 * s, "DIAMOND", 1 - fall, crack)
        draw_text(ctx, "DIAMOND", W / 2, y + h * 0.6 + 44 * s, 15 * s, tier_rgb("DIAMOND"), 1 - fall, face=LG)
        ctx.c.restore()
    else:
        k = ease(prog(t, EVENTS["reset"], EVENTS["reset"] + 0.4))
        badge(ctx, W / 2, y + h * 0.6, 0.62 * s, "UNRANKED", k)
        draw_text(ctx, "UNRANKED", W / 2, y + h * 0.6 + 44 * s, 15 * s, tier_rgb("UNRANKED"), k, face=LG)
    cap(ctx, "C6", y=935)
    cap(ctx, "C7", y=1000)
    hud(ctx, t)


def l1(ctx, t):
    """The lesson drawn: the rank staircase that drops back every season; the days that stay grey."""
    a = ease(prog(t, EVENTS["lesson"], EVENTS["lesson"] + 0.6))
    c = ctx.c
    c.saveLayerAlpha(None, int(255 * a))
    draw_text(ctx, "THE RANK", 480, 330, 52, (200, 200, 210), face=LG)
    draw_text(ctx, "THE DAYS", 1440, 330, 52, (200, 200, 210), face=LG)
    c.drawLine(W / 2, 300, W / 2, 860, stroke((60, 60, 66), 3))
    lt = max(0.0, t - EVENTS["lesson"] - 0.4)
    period = 3.2
    k = (lt % period) / period
    tiers = ["SILVER", "GOLD", "PLATINUM", "DIAMOND"]
    collapse = ease(prog(k, 0.8, 0.95))
    for i, tn in enumerate(tiers):
        x = 260 + i * 140
        top = 820 - (i + 1) * 90 * (1 - collapse)
        wrect(ctx, x - 60, top, 120, 820 - top + 1, ("step", i), (44, 44, 52), LINE, 3, seg=2)
        badge(ctx, x, top - 50, 0.55, tn + " I", 1.0 - 0.6 * collapse)
    step = min(3, int(k / 0.2))
    rx = 260 + step * 140 if collapse < 0.5 else 260
    ry = 820 - (step + 1) * 90 * (1 - collapse)
    me = Character("l1him", scale=0.7)
    hip, feet = standing(rx, ry, 1, 0.7)
    me.draw(ctx, hip, 1, lean=0.08, feet=feet, expr="determined" if collapse < 0.5 else "shocked", look=(1, -0.2))
    draw_text(ctx, "SEASON RESET", 480, 900, 34, RED, collapse, face=LG)
    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    grey_n = min(7, int(lt / 1.1))
    for i, d in enumerate(days):
        x = 1140 + (i % 4) * 150
        y = 460 + (i // 4) * 180
        gone = i < grey_n
        rrect(ctx, x - 60, y, 120, 140, 14, (60, 60, 66) if gone else (120, 150, 200), LINE, 3)
        draw_text(ctx, d, x, y + 50, 34, (120, 120, 126) if gone else TEXT, face=LG)
        if d == "SAT":
            draw_text(ctx, "FINAL", x, y + 100, 26, (120, 120, 126) if gone else TEXT, face=LG)
    c.restore()
    cap(ctx, "C8", y=190)
    cap(ctx, "C9", y=990)
    hud(ctx, t)


INSTEAD = ["Pick the number before you log in.", "Log off when you reach it. Win or lose.", "Plan one real thing for tomorrow."]


def i1(ctx, t):
    a = fade(t, EVENTS["card"], 110.0, 0.3, 0.3)
    rrect(ctx, W / 2 - 500, 280, 1000, 480, 22, (236, 232, 214), LINE, 5, a=a)
    draw_text(ctx, "INSTEAD OF \"ONE MORE\":", W / 2 - 440, 380, 64, (40, 40, 46), a, align="left", face=LG)
    for i, s in enumerate(INSTEAD):
        k = ease(prog(t, EVENTS["card"] + 0.4 + i * 0.6, EVENTS["card"] + 0.8 + i * 0.6))
        y = 480 + i * 90
        rrect(ctx, W / 2 - 440, y - 40, 44, 44, 6, None, (40, 40, 46), 4, a=a * k)
        draw_text(ctx, s, W / 2 - 370, y, 46, (40, 40, 46), a * k, align="left")
    hud(ctx, t)


# ---- the final fight --------------------------------------------------------------------------------
def f1(ctx, t):
    r0, r1_ = EVENTS["rise"]
    rise = ease(prog(t, r0, r1_)) * (1 - prog(t, EVENTS["crumble"], EVENTS["crumble"] + 0.05))
    off = t >= EVENTS["logoff"]
    x, y, w, h = MON
    s = w / 340
    pa = (x + w * 0.5, y + h * 0.66 + 17 * s)
    lo = (x + w * 0.5, y + h * 0.84 + 11 * s)
    move = ease(prog(t, 120.0, 120.8))
    cur = lerp2(pa, lo, move) if t > 115 else None
    zoom = lerp(1.5, 1.8, ease(prog(t, 112, 120)))
    with Camera(zoom, 980, 500, shake=1.4 * prog(t, 116, 119.6) * (t < 119.8)).apply(ctx):
        room(ctx, t, clock="11:46", screen_glow=1.0 - ease(prog(t, EVENTS["logoff"] + 0.1, EVENTS["logoff"] + 0.5)),
             banner="DEFEAT" if t >= EVENTS["defeat"] else "VICTORY", banner_t=EVENTS["defeat"] if t >= EVENTS["defeat"] else 110.0,
             play_again=1.0, red_again=rise, logoff=1.0 if move > 0.9 else 0.0, cursor=cur, sticky=("2", "MATCHES"),
             gloves_grey=0.6)
        if rise > 0:
            P.villain(ctx, 520, FY, scale=lerp(0.7, 1.25, rise), alpha=rise, grin=1.2, lean=0.3,
                      reach=(860, 560) if rise > 0.7 else None)
        if EVENTS["crumble"] < t < EVENTS["crumble"] + 2.2:
            P.villain_shards(ctx, 520, FY, 1.25, prog(t, EVENTS["crumble"], EVENTS["crumble"] + 2.0))
        expr = "anxious" if t < 119.8 else ("closed" if t < 120.6 else ("determined" if not off else "hopeful"))
        at_desk(ctx, t, expr=expr, look=(1, -0.1), lean=0.18, glow_on=0.0 if off else 1.0)
    label(ctx, "SEASON 5")
    vline(ctx, "V7", 1200, 250, 58)
    vline(ctx, "V8", 1200, 330, 54)
    vline(ctx, "V9", 1200, 250, 64)
    hud(ctx, t)


def f2(ctx, t):
    with Camera(1.5, 600, 520).apply(ctx):
        room(ctx, t, clock="11:52", screen_glow=0.0, gloves_grey=0.0, shelf_gloves=False)
        for gx in (420, 470):  # the gloves by the door
            ctx.c.drawPath(poly_path([(gx - 20, FY), (gx - 24, FY - 34), (gx - 8, FY - 52), (gx + 12, FY - 48), (gx + 22, FY - 26), (gx + 18, FY)], smooth=True), fill(GLOVE))
            ctx.c.drawPath(poly_path([(gx - 20, FY), (gx - 24, FY - 34), (gx - 8, FY - 52), (gx + 12, FY - 48), (gx + 22, FY - 26), (gx + 18, FY)], smooth=True), stroke(LINE, 3))
        J0 = HIM.joints(standing(600, FY, -1)[0], -1, 0.04)
        sh = J0["shoulder"]
        J = stand(HIM, ctx, 600, f=-1, lean=0.06, expr="smile", look=(-1, 0.6), hands={"near": (sh[0] - 40, sh[1] + 66)})
        hp = J["limbs"]["arm_near"][2]
        P.phone_held(ctx, hp[0], hp[1], facing=-1, on=1.0)
        pop_label(ctx, t, EVENTS["alarm"], "ALARM 6:30  PRACTICE", hp[0] + 150, hp[1] - 230, (236, 232, 214), dur=2.2, size=30)
    hud(ctx, t)


# ---- payoff, viewer, mirror, title ----------------------------------------------------------------
def p1(ctx, t):
    shot, catch = EVENTS["shot"], EVENTS["catch"]
    jump = math.sin(math.pi * prog(t, catch - 0.35, catch + 0.6))
    with Camera(1.45, 900, 520).apply(ctx):
        pitch(ctx, t, warm=1.0)
        goal(ctx, 460)
        # the striker
        kick = math.sin(math.pi * prog(t, shot - 0.3, shot + 0.2))
        hipk, feetk = standing(1320, FY, -1)
        feetk["near"] = (hipk[0] - 40 * kick, FY - 30 * kick)
        grey("striker").draw(ctx, hipk, -1, lean=0.08, feet=feetk, expr="determined", look=(-1, 0.3))
        Jd = stand(DEV, ctx, 980, f=-1, lean=0.04 - 0.06 * (t > 132.4), expr="happy" if t > 132.4 else "worried", look=(-1, 0.0),
                   mouth_open=talk("dev", t))
        # him in goal
        hip, feet = standing(560, FY, 1)
        hip = (hip[0], hip[1] - 60 * jump)
        J0 = HIM.joints(hip, 1, -0.05)
        sh = J0["shoulder"]
        hands = {"near": (sh[0] + 56, sh[1] - 60 * jump - 10), "far": (sh[0] + 40, sh[1] - 66 * jump - 4)}
        J = HIM.draw(ctx, hip, 1, lean=-0.05, feet={k: (v[0], FY - 60 * jump) for k, v in feet.items()},
                     expr="determined" if t < catch else "happy", look=(1, -0.3), hands=free_hands(HIM, hip, 1, -0.05, hands))
        for side in ("arm_near", "arm_far"):
            p = J["limbs"][side][2]
            ctx.c.drawCircle(p[0], p[1], 14, fill(GLOVE))
            ctx.c.drawCircle(p[0], p[1], 14, stroke(LINE, 3))
        if t < shot:
            ball(ctx, 1270, FY - 18)
        elif t < catch:
            k = prog(t, shot, catch)
            p = J["limbs"]["arm_near"][2]
            ball(ctx, lerp(1270, p[0] + 16, k), lerp(FY - 18, p[1] - 10, k) - 160 * math.sin(math.pi * k))
        else:
            p = J["limbs"]["arm_near"][2]
            ball(ctx, p[0] + 16, p[1] - 10)
        speech(ctx, t, "dev", Jd["head"][0] - 20, Jd["head"][1] - 80)
    label(ctx, "SATURDAY")
    cap(ctx, "C10", y=925)
    cap(ctx, "C11", y=995)
    hud(ctx, t)


def vt(ctx, t):
    a = fade(t, 140.2, 147.0, 0.6, 0.6)
    c = ctx.c
    c.save()
    c.translate(W / 2, 600)
    c.rotate(-3)
    c.drawRect(skia.Rect.MakeXYWH(-260, -220, 520, 440), fill((236, 224, 150), a))
    c.drawRect(skia.Rect.MakeXYWH(-260, -220, 520, 440), stroke(LINE, 4, a))
    draw_text(ctx, "TONIGHT:", 0, -90, 70, (50, 46, 40), a, face=LG)
    draw_text(ctx, "MATCHES", 0, 130, 60, (50, 46, 40), a, face=LG)
    c.drawLine(-80, 50, 80, 50, stroke((50, 46, 40), 5, a))
    k = ease(prog(t, 143.8, 144.4))
    if k > 0:
        draw_text(ctx, "2", 0, 40, 120 * k, GOLD, a, face=LG, glow_rgb=(170, 110, 20))
    c.restore()
    cap(ctx, "V1", y=190, size=54)
    cap(ctx, "V2", y=190, size=54)


def x1(ctx, t):
    x, y, w, h = MON
    s = w / 340
    pa = (x + w * 0.5, y + h * 0.66 + 17 * s)
    lo = (x + w * 0.5, y + h * 0.84 + 11 * s)
    move = ease(prog(t, 150.2, 151.0))
    off = t >= EVENTS["x_logoff"]
    with Camera(lerp(1.95, 1.7, ease(prog(t, 147, 153))), 1100, 500).apply(ctx):
        room(ctx, t, clock="11:02", screen_glow=1.0 - ease(prog(t, EVENTS["x_logoff"] + 0.1, EVENTS["x_logoff"] + 0.5)),
             banner="VICTORY" if t > EVENTS["x_victory"] else None, banner_t=EVENTS["x_victory"], play_again=1.0,
             logoff=1.0 if move > 0.9 else 0.0, cursor=lerp2(pa, lo, move) if t > 149.4 else None, gloves_grey=0.0)
        if t < 152.4:
            at_desk(ctx, t, expr="smile" if t > EVENTS["x_victory"] else "determined", look=(1, -0.2), glow_on=0.0 if off else 1.0)
        else:  # headset off, a stretch
            st = math.sin(math.pi * prog(t, 152.6, 155.6))
            hip, feet = seated(SEAT[0], SEAT[1], 1)
            P.chair(ctx, SEAT[0], SEAT[1], 1, key="gchair")
            wrect(ctx, SEAT[0] - 60, SEAT[1] - 160, 20, 150, "gback", (60, 30, 36), LINE, 3, seg=2)
            J0 = HIM.joints(hip, 1, -0.05)
            sh = J0["shoulder"]
            J = HIM.draw(ctx, hip, 1, lean=0.1 - 0.15 * st, feet=feet, expr="closed" if st > 0.5 else "smile", look=(1, -0.3),
                         hands=free_hands(HIM, hip, 1, -0.05, {"far": (sh[0] - 20, sh[1] - 90 * st), "near": (1030, 630)}))
            headset(ctx, 1080, 600, 1, 0.9)


def title(ctx, t):
    a = fade(t, EVENTS["title"], DURATION, 0.8, 1.2)
    draw_text(ctx, "ONE MORE MATCH.", W / 2, 520, 160, TEXT, a, face=LG)
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 520 + 1040 * i / 12, 562 + math.sin(i * 1.7) * 4) for i in range(int(12 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=48)
    cap(ctx, "T2", y=770, size=72, rgb=GOLD, glow_rgb=(170, 110, 20))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "S02": s02, "B1": b1, "G1": g1, "G2": g2, "G3": g3, "R1": r1, "T1": t1, "L1": l1,
    "I1": i1, "F1": f1, "F2": f2, "P1": p1, "VT": vt, "X1": x1, "TT": title,
}
CONTINUOUS = {"S01", "G1"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1_, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "R1" and EVENTS["phone"] <= t < EVENTS["phone"] + 0.08:
        black(ctx, 1 - prog(t, EVENTS["phone"], EVENTS["phone"] + 0.08))
    if sid == "TT":
        black(ctx, prog(t, DURATION - 1.0, DURATION))
