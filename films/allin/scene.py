"""ALL IN.: picture. scene(ctx) draws any frame of the film.

The device: one counter that changes its name. It starts as WINNINGS +₹1,300 after the first lucky six; the first loss
flips it to TO GET EVEN, and every bet made to get even makes the number bigger (₹700 to ₹37,400). The app calls him a
VIP. When he tells Kabir the real number and deletes the app, the same box is relabelled PAID BACK, in gold, and it
only ever moves one way: slowly up.
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
from studio.core import _typefaces  # noqa: E402,F401
from studio.character import Character, standing, seated, walk_x  # noqa: E402
from studio import props as P  # noqa: E402
from studio.extras import talk as _talk, free_hands, door  # noqa: E402
from timeline import (SCENES, CAPS, CUES, BUBBLES, EVENTS, DURATION, scene_at, count_at, count_changed,  # noqa: E402
                      RELABEL, TOTAL_OWED, G1_T0, G1_NIGHT, G1_LABELS, G1_BETS)
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
WINGREEN = (70, 200, 120)
TVGLOW = (110, 170, 150)
LG = "LuckiestGuy-Regular.ttf"
PH = "PatrickHand-Regular.ttf"


def beard(ctx, hx, hy, f, s):
    fx = hx + f * 14 * s
    p = poly_path([(fx - 24 * s, hy + 12 * s), (fx - 18 * s, hy + 34 * s), (fx, hy + 44 * s), (fx + 18 * s, hy + 36 * s),
                   (fx + 26 * s, hy + 14 * s), (fx + 14 * s, hy + 28 * s), (fx, hy + 31 * s), (fx - 14 * s, hy + 27 * s)], smooth=True)
    ctx.c.drawPath(p, fill((70, 52, 42)))


HIM = Character("him")
KABIR = Character("kabir", skin=(196, 156, 122), extra=beard)


def grey(name, scale=1.0):
    return Character(name, skin=(150, 150, 156), scale=scale)


# ---- text with the rupee sign (our fonts have no ₹ glyph, so it is drawn) ----------------------------
def _rupee_w(size):
    return size * 0.56


def rtext_w(s, size, face=PH):
    parts = s.split("₹")
    return sum(text_width(p, size, face) for p in parts) + _rupee_w(size) * (len(parts) - 1)


def _rupee(ctx, x, y, size, rgb, a, bold):
    w = _rupee_w(size)
    lw = size * (0.12 if bold else 0.075)
    st = stroke(rgb, lw, a)
    x0, x1 = x + w * 0.1, x + w * 0.9
    top, mid, bowl = y - size * 0.7, y - size * 0.52, y - size * 0.36
    ctx.c.drawLine(x0, top, x1, top, st)
    ctx.c.drawLine(x0, mid, x1, mid, st)
    ctx.c.drawPath(poly_path([(x0 + w * 0.05, top), (x0 + w * 0.5, top + size * 0.02), (x0 + w * 0.62, (top + bowl) / 2),
                              (x0 + w * 0.45, bowl), (x0 + w * 0.02, bowl)], closed=False, smooth=True), st)
    ctx.c.drawLine(x0 + w * 0.02, bowl, x0 + w * 0.68, y, st)


def rtext(ctx, s, x, y, size, rgb=TEXT, a=1.0, align="center", face=PH, glow_rgb=None):
    if a <= 0.001 or not s:
        return
    w = rtext_w(s, size, face)
    cx = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    parts = s.split("₹")
    bold = face == LG
    for i, p in enumerate(parts):
        if p:
            draw_text(ctx, p, cx, y, size, rgb, a, align="left", face=face, glow_rgb=glow_rgb)
            cx += text_width(p, size, face)
        if i < len(parts) - 1:
            if glow_rgb is not None:
                pass
            _rupee(ctx, cx, y, size, rgb, a, bold)
            cx += _rupee_w(size)


def money(v):
    return f"₹{v:,}"


def cap(ctx, k, y=190, size=50, rgb=TEXT, glow_rgb=None):
    t0, t1 = CAPS[k]
    rtext(ctx, CAPTIONS[k], W / 2, y, size, rgb, fade(ctx.t, t0, t1, 0.5, 0.5), glow_rgb=glow_rgb)


def vline(ctx, k, x, y, size=50):
    t0 = CUES[k]
    villain_text(ctx, VILLAIN[k], t0 - 0.05, t0 + LEN.get(k, 1.4) + 0.5, x, y, size)


def label(ctx, s, a=1.0):
    draw_text(ctx, s, 60, LETTERBOX + 170, 38, (190, 190, 196), a, align="left")


def bubble_on(who, t):
    for b in BUBBLES:
        if b[2] == who and b[0] - 0.05 <= t <= b[1] + 0.3:
            return b
    return None


def speech(ctx, t, who, x, y, size=32):
    """Speech bubble above (x, y), as in the toolkit, but able to draw ₹. His bubbles are light."""
    b = bubble_on(who, t)
    if b is None:
        return
    t0, t1, _, text = b
    a = fade(t, t0, t1, 0.15, 0.25)
    if a <= 0:
        return
    k = ease_out_back(prog(t, t0, t0 + 0.22))
    light = who == "him"
    bw, bh = rtext_w(text, size) + 44, size * 1.25 + 22
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
    bg, fg, edge = ((236, 234, 226), (30, 28, 32), (120, 118, 112)) if light else ((38, 38, 46), TEXT, (92, 92, 104))
    c.drawPath(poly_path([(-12, -6), (12, -6), (2, 18)]), fill(bg, a))
    rrect(ctx, -bw / 2, -bh, bw, bh, min(26, bh / 2), bg, edge, 2.5, a=a)
    rtext(ctx, text, 0, -bh / 2 + size * 0.36, size, fg, a)
    c.restore()


def talk(who, t):
    return _talk(BUBBLES, who, t)


def hud(ctx, t, a=1.0):
    """WINNINGS, then TO GET EVEN (the same box), then PAID BACK in gold."""
    a *= prog(t, 9.0, 9.4)
    mode, v = count_at(t)
    if a <= 0 or mode is None:
        return
    lc = count_changed(t)
    pop = prog(t, lc, lc + 0.35) if lc is not None and lc <= t <= lc + 0.35 else 0.0
    sz = 52 * (1 + 0.35 * math.sin(math.pi * min(1, pop)) if pop > 0 else 1)
    x, y = 56, LETTERBOX + 26
    box_w = 330 if mode != "paid" else 400
    rrect(ctx, x, y, box_w, 92 if mode != "paid" else 112, 14, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
    if mode == "win":
        draw_text(ctx, "WINNINGS", x + 20, y + 32, 22, (160, 160, 168), a, align="left")
        rtext(ctx, "+" + money(v), x + 22, y + 80, sz, TEXT, a, align="left", face=LG)
        return
    if mode == "even":
        flip = prog(t, 21.6, 22.2)
        draw_text(ctx, "TO GET EVEN", x + 20, y + 32, 22, (160, 160, 168), a, align="left")
        rtext(ctx, money(v), x + 22, y + 80, sz, TEXT, a, align="left", face=LG)
        if t < 22.6:  # the flip: WINNINGS struck through first
            draw_text(ctx, "WINNINGS", x + 160, y + 32, 22, (160, 160, 168), a * (1 - flip), align="left")
            ctx.c.drawLine(x + 156, y + 25, x + 156 + 116 * ease(min(1, flip * 2)), y + 25, stroke(RED, 3, a * (1 - flip)))
        return
    k = prog(t, RELABEL, RELABEL + 0.6)
    if k < 1:  # TO GET EVEN struck through, then gold
        draw_text(ctx, "TO GET EVEN", x + 20, y + 32, 22, (160, 160, 168), a * (1 - k), align="left")
        rtext(ctx, money(TOTAL_OWED), x + 22, y + 80, 52, TEXT, a * (1 - k), align="left", face=LG)
        ctx.c.drawLine(x + 16, y + 62, x + 16 + 250 * ease(min(1, k * 2)), y + 62, stroke(RED, 6, a))
        return
    draw_text(ctx, "PAID BACK", x + 20, y + 32, 22, (200, 180, 140), a, align="left")
    rtext(ctx, money(v), x + 22, y + 80, sz, GOLD, a, align="left", face=LG, glow_rgb=GOLD)
    rtext(ctx, "of " + money(TOTAL_OWED), x + 30 + rtext_w(money(v), 52, LG), y + 80, 28, (200, 190, 170), a, align="left")
    rrect(ctx, x + 22, y + 92, 356, 10, 5, (50, 46, 40), None, a=a)
    if v > 0:
        rrect(ctx, x + 22, y + 92, 356 * v / TOTAL_OWED, 10, 5, GOLD, None, a=a)


# ---- sets ----------------------------------------------------------------------------------------
SOFA_X, SEAT_Y = 960, 690
TV = (1360, 370, 300, 180)


def room(ctx, t, tv=1.0, day=0.0, match=True, flash=0.0, odds=False):
    c = ctx.c
    P.back_wall(ctx, rgb=mix((22, 22, 26), (52, 48, 46), day))
    P.floor(ctx, FY)
    # window with curtains (shut)
    wx, wy = 300, 220
    c.drawRect(skia.Rect.MakeXYWH(wx, wy, 240, 240), fill(mix((24, 28, 40), (240, 220, 170), day)))
    for cx0 in (wx - 20, wx + 130):
        c.drawRect(skia.Rect.MakeXYWH(cx0, wy - 20, 130, 290), fill(mix((40, 36, 46), (96, 80, 70), day)))
    if day > 0:
        c.drawRect(skia.Rect.MakeXYWH(wx + 108, wy, 24, 240), fill((255, 236, 190), 0.7 * day))
        glow(ctx, wx + 120, wy + 120, 300, (255, 220, 160), 0.15 * day)
    # the TV on its cabinet
    tx, ty, tw, th = TV
    wrect(ctx, tx - 20, 560, tw + 40, FY - 560, "cab", (52, 46, 44), LINE, 3, seg=2)
    if tv > 0:
        glow(ctx, tx + tw / 2, ty + th / 2, 420, mix(TVGLOW, (255, 255, 255), flash), (0.22 + 0.3 * flash) * tv)
        cone(ctx, (tx, ty + th / 2), (SOFA_X - 200, FY), (tx, FY), TVGLOW, 0.06 * tv)
    rrect(ctx, tx - 8, ty - 8, tw + 16, th + 16, 8, (16, 16, 18), LINE, 3)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(tx, ty, tw, th))
    if tv > 0 and match:
        c.drawRect(skia.Rect.MakeXYWH(tx, ty, tw, th), fill(mix((20, 22, 26), (60, 110, 70), tv)))
        c.drawOval(skia.Rect.MakeXYWH(tx + 30, ty + 30, tw - 60, th - 40), fill((80, 140, 86), tv))
        c.drawRect(skia.Rect.MakeXYWH(tx + tw / 2 - 10, ty + 60, 20, 60), fill((200, 180, 130), tv))
        for i in range(6):
            px = tx + 60 + hrand("fld", i) * (tw - 120)
            py = ty + 50 + hrand("fldy", i) * (th - 90)
            c.drawCircle(px + math.sin(t * 2 + i) * 4, py, 4, fill((236, 236, 240), tv))
        c.drawRect(skia.Rect.MakeXYWH(tx, ty + th - 30, tw, 30), fill((14, 18, 30), tv))
        draw_text(ctx, "BLUES 168/4   19.2", tx + 12, ty + th - 9, 20, TEXT, tv, align="left")
        if odds:
            rrect(ctx, tx + tw - 110, ty + 8, 100, 30, 6, WINGREEN, None, a=tv)
            draw_text(ctx, "BET NOW", tx + tw - 60, ty + 30, 18, (10, 30, 16), tv, face=LG)
        if flash > 0:
            c.drawRect(skia.Rect.MakeXYWH(tx, ty, tw, th), fill((255, 255, 255), 0.5 * flash))
            draw_text(ctx, "SIX!", tx + tw / 2, ty + th / 2 + 20, 64, (255, 230, 120), flash, face=LG)
    elif tv <= 0:
        c.drawRect(skia.Rect.MakeXYWH(tx, ty, tw, th), fill((14, 14, 16)))
    c.restore()
    # the sofa, its back behind him
    wrect(ctx, SOFA_X - 160, SEAT_Y, 360, 90, "sofa", (66, 62, 80), LINE, 3, seg=3)
    wrect(ctx, SOFA_X - 190, SEAT_Y - 150, 50, 240, "sofaback", (58, 54, 72), LINE, 3, seg=2)


def on_sofa(ctx, t, expr="neutral", look=(1, 0.5), phone=1.0, lean=0.16, glow_rgb=BLUE, phone_up=0.0, shaky=0.0):
    """Sitting on the sofa, the phone at chest height. Returns joints and the phone point."""
    hip, feet = seated(SOFA_X, SEAT_Y, 1)
    J0 = HIM.joints(hip, 1, lean)
    sh = J0["shoulder"]
    hp = (sh[0] + 56 + shaky * math.sin(t * 40) * 3, sh[1] + 60 - 16 * phone_up)
    J = HIM.draw(ctx, hip, 1, lean=lean, feet=feet, expr=expr, look=look, screen_glow=0.9 * phone,
                 hands=free_hands(HIM, hip, 1, lean, {"near": hp, "far": (hp[0] - 12, hp[1] + 6)}),
                 mouth_open=talk("him", t))
    p = J["limbs"]["arm_near"][2]
    if phone > 0:
        P.phone_held(ctx, *p, on=phone, glow_rgb=glow_rgb)
    return J, p


def pop_label(ctx, t, t0, s, x, y, rgb, dur=1.6, size=40):
    """A short app pop-up next to the phone (BET ₹500, LOST)."""
    a = fade(t, t0, t0 + dur, 0.12, 0.3)
    if a <= 0:
        return
    k = ease_out_back(prog(t, t0, t0 + 0.2))
    w = rtext_w(s, size, LG) + 36
    c = ctx.c
    c.save()
    c.translate(x, y - 24 * prog(t, t0, t0 + dur))
    c.scale(0.7 + 0.3 * k, 0.7 + 0.3 * k)
    rrect(ctx, -w / 2, -size, w, size * 1.4, 12, rgb, None, a=a)
    rtext(ctx, s, 0, size * 0.22, size, (16, 16, 18) if rgb != RED else TEXT, a, face=LG)
    c.restore()


# ---- the app (phone close-ups) ---------------------------------------------------------------------
def app(ctx, t, body, light=1.0, cy=590):
    """The betting app on a big phone. body(ctx, x0, y0, w) draws the content."""
    UI = P.PhoneUI(W / 2, cy, 560, 880)
    UI.body(ctx, light, mix(BLUE, WINGREEN, 0.4))
    with UI.screen(ctx):
        x0, y0, w = UI.x0 + 18, UI.y0 + 18, UI.w - 36
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, 120), fill((18, 26, 22)))
        ctx.c.drawCircle(x0 + 50, y0 + 80, 9, fill(RED))
        draw_text(ctx, "LIVE   BLUES vs REDS", x0 + 70, y0 + 92, 34, TEXT, align="left", face=LG)
        body(ctx, x0, y0 + 120, w)
    return UI


def field(ctx, x0, y0, w, h=220):
    c = ctx.c
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), fill((40, 86, 52)))
    c.drawOval(skia.Rect.MakeXYWH(x0 + 30, y0 + 20, w - 60, h - 40), fill((62, 120, 72)))
    c.drawRect(skia.Rect.MakeXYWH(x0 + w / 2 - 14, y0 + 70, 28, 80), fill((196, 176, 126)))


def odds_button(ctx, x, y, w, s, sel=0.0, rgb=None):
    rrect(ctx, x, y, w, 90, 16, mix((40, 44, 52), rgb or WINGREEN, sel), (90, 96, 104), 2)
    rtext(ctx, s, x + w / 2, y + 60, 40, TEXT if sel < 0.5 else (10, 26, 14), face=LG)


def result_banner(ctx, x0, y, w, s, rgb, k, sub=None):
    if k <= 0:
        return
    sc = ease_out_back(min(1, k))
    c = ctx.c
    c.save()
    c.translate(x0 + w / 2, y)
    c.scale(sc, sc)
    rrect(ctx, -w / 2 + 20, -80, w - 40, 160 if sub else 130, 22, rgb, None, a=min(1, k * 2))
    rtext(ctx, s, 0, 20, 64, (14, 20, 16) if rgb == WINGREEN else TEXT, min(1, k * 2), face=LG)
    if sub:
        rtext(ctx, sub, 0, 64, 34, (14, 20, 16) if rgb == WINGREEN else TEXT, min(1, k * 2))
    c.restore()


def coins(ctx, t, t0, cx, cy):
    k = prog(t, t0, t0 + 1.6)
    if k <= 0 or k >= 1:
        return
    for i in range(18):
        a = hrand("coin", i) * 2 * math.pi
        sp = 200 + hrand("coinsp", i) * 260
        x = cx + math.cos(a) * sp * k
        y = cy + math.sin(a) * sp * k - 200 * k + 500 * k * k
        ctx.c.drawCircle(x, y, 16, fill((240, 210, 110), 1 - k))
        ctx.c.drawCircle(x, y, 16, stroke((150, 120, 40), 3, 1 - k))


# ---- the hook -------------------------------------------------------------------------------------
def s01(ctx, t):
    with Camera(lerp(1.9, 1.7, ease(prog(t, 0, 6))), 1130, 500).apply(ctx):
        room(ctx, t, odds=True)
        J, p = on_sofa(ctx, t, expr="hopeful", look=(1, 0.6))
        pop_label(ctx, t, EVENTS["bet0"], "BET ₹500", p[0] + 190, p[1] - 130, WINGREEN, dur=2.4, size=34)
        if t > EVENTS["tap0"]:
            ctx.c.drawCircle(p[0] + 4, p[1] - 30, 18 * (1 - prog(t, EVENTS["tap0"], EVENTS["tap0"] + 0.3)) + 1,
                             stroke(TEXT, 3, 1 - prog(t, EVENTS["tap0"], EVENTS["tap0"] + 0.3)))
    cap(ctx, "C1", y=985)


def h1(ctx, t):
    six = ease(prog(t, EVENTS["six"], EVENTS["six"] + 0.3))
    won = prog(t, EVENTS["won"], EVENTS["won"] + 0.4)

    def body(ctx, x0, y0, w):
        field(ctx, x0, y0, w)
        if six > 0:
            draw_text(ctx, "SIX!", x0 + w / 2, y0 + 140, 90, (255, 230, 120), six, face=LG)
        draw_text(ctx, "NEXT BALL:", x0 + 30, y0 + 290, 36, (190, 196, 200), align="left")
        odds_button(ctx, x0 + 30, y0 + 320, w - 60, "SIX?   x3.6", sel=ease(prog(t, 6.4, 6.7)))
        rtext(ctx, "YOUR BET  ₹500", x0 + w / 2, y0 + 480, 34, (190, 196, 200))
        result_banner(ctx, x0, y0 + 600, w, "YOU WON", WINGREEN, won, sub="+₹1,800")
    app(ctx, t, body)
    coins(ctx, t, EVENTS["won"], W / 2, 640)
    hud(ctx, t)


def h2(ctx, t):
    jump = ease(prog(t, EVENTS["jump"], EVENTS["jump"] + 0.4)) * (1 - ease(prog(t, 16.0, 16.8)))
    with Camera(1.7, 1130, 500).apply(ctx):
        room(ctx, t, flash=max(0.0, 1 - prog(t, 12.0, 13.2)))
        if jump < 0.5:
            on_sofa(ctx, t, expr="happy", look=(1, -0.2), phone=1.0)
        else:
            hip, feet = standing(SOFA_X + 40, FY, 1)
            hip = (hip[0], hip[1] - 20 * math.sin(math.pi * prog(t, EVENTS["jump"] + 0.2, EVENTS["jump"] + 0.7)))
            J0 = HIM.joints(hip, 1, -0.05)
            sh = J0["shoulder"]
            J = HIM.draw(ctx, hip, 1, lean=-0.05, feet={"near": (hip[0] + 10, min(FY, hip[1] + 114)), "far": (hip[0] - 8, min(FY, hip[1] + 114))},
                         expr="happy", look=(1, -0.4), mouth_open=0.6,
                         hands=free_hands(HIM, hip, 1, -0.05, {"far": (sh[0] - 50, sh[1] - 80), "near": (sh[0] + 50, sh[1] + 60)}))
            P.phone_held(ctx, *J["limbs"]["arm_near"][2], on=1.0)
    cap(ctx, "C2", y=985)
    hud(ctx, t)


def h3(ctx, t):
    lost = prog(t, EVENTS["lost1"], EVENTS["lost1"] + 0.4)

    def body(ctx, x0, y0, w):
        field(ctx, x0, y0, w)
        draw_text(ctx, "RUNS THIS OVER:", x0 + 30, y0 + 290, 36, (190, 196, 200), align="left")
        odds_button(ctx, x0 + 30, y0 + 320, w - 60, "OVER 9.5   x1.9", sel=ease(prog(t, EVENTS["bet1"], EVENTS["bet1"] + 0.3)))
        rtext(ctx, "YOUR BET  ₹2,000", x0 + w / 2, y0 + 480, 34, (190, 196, 200))
        result_banner(ctx, x0, y0 + 600, w, "LOST", RED, lost, sub="-₹2,000")
    app(ctx, t, body)
    label(ctx, "THE NEXT NIGHT", a=prog(t, 18.0, 18.4) if t < 21 else 1.0)
    hud(ctx, t)


# ---- the wound and the stakes ---------------------------------------------------------------------
def s02(ctx, t):
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0, t1))
    with Camera(lerp(1.9, 1.6, ease(prog(t, t0 - 0.4, t1))), lerp(1080, 1140, ease(prog(t, t0 - 0.4, t1))), 500).apply(ctx):
        room(ctx, t, tv=0.6)
        if born > 0:
            P.villain(ctx, 1220, FY, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 27.0, 27.6)), lean=-0.3)
        J, p = on_sofa(ctx, t, expr="anxious" if t < 29 else "worried", look=(1, 0.7) if t < 29 else (1, -0.2))
        glow(ctx, p[0], p[1] - 20, 120, RED, 0.3 * born)
    vline(ctx, "V1", 560, 300, 58)
    vline(ctx, "V2", 560, 380, 52)
    hud(ctx, t)


def chat(ctx, t, sender, msgs, times, mine=(), avatar=(196, 156, 122)):
    """A full-screen chat (able to draw ₹)."""
    UI = P.PhoneUI(W / 2, 590, 560, 880)
    UI.body(ctx, 1.0)
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, 130), fill((26, 28, 36)))
        wcircle(ctx, x0 + 60, y0 + 84, 26, "av_" + sender, avatar, None, 0)
        draw_text(ctx, sender, x0 + 100, y0 + 96, 40, TEXT, align="left")
        y = y0 + 170
        for i, m in enumerate(msgs):
            a = ease(prog(t, times[i], times[i] + 0.2))
            if a <= 0:
                break
            lines = _wrap(m, 38, 400)
            h = len(lines) * 38 * 1.15 + 26
            bw = max(rtext_w(l, 38) for l in lines) + 40
            bx = x0 + UI.w - 62 - bw if i in mine else x0 + 26
            rrect(ctx, bx, y, bw, h, 22, (70, 110, 200) if i in mine else (58, 58, 66), None, a=a)
            for j, l in enumerate(lines):
                rtext(ctx, l, bx + 20, y + 13 + 38 * 0.85 + j * 38 * 1.15, 38, TEXT, a, align="left")
            y += h + 14


def _wrap(text, size, maxw):
    words, lines, cur = text.split(" "), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if rtext_w(trial, size) > maxw and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    return lines + [cur]


def b1(ctx, t):
    chat(ctx, t, "Kabir", ["goa in december!! ₹12k each by the 30th", "in. got it saved.", "LETS GOOO"],
         [EVENTS["k_text"], EVENTS["his_text"], EVENTS["k_text2"]], mine=(1,))
    hud(ctx, t)


# ---- the grind --------------------------------------------------------------------------------------
def g1(ctx, t):
    i = min(2, int((t - G1_T0) // G1_NIGHT))
    n0 = G1_T0 + i * G1_NIGHT
    lost_t = EVENTS["g1_lost"][i]
    with Camera(1.75, 1120, 500).apply(ctx):
        room(ctx, t, odds=True)
        if i >= 1:
            P.villain(ctx, 1230, FY, scale=0.9 + 0.1 * i, alpha=0.5 + 0.2 * i, grin=1.0, lean=-0.3)
        J, p = on_sofa(ctx, t, expr="determined" if t < lost_t else "hurt", look=(1, 0.6), lean=0.16 + 0.04 * i)
        pop_label(ctx, t, n0 + 1.2, "BET " + G1_BETS[i], p[0] + 190, p[1] - 130, WINGREEN, dur=1.8, size=34)
        pop_label(ctx, t, lost_t, "LOST", p[0] + 190, p[1] - 130, RED, dur=2.2, size=40)
    black(ctx, 1 - prog(t, n0, n0 + 0.1))
    label(ctx, G1_LABELS[i])
    vline(ctx, "V3", 600, 330, 56)
    vline(ctx, "V4", 600, 330, 56)
    vline(ctx, "V5", 600, 330, 62)
    hud(ctx, t)


def g2(ctx, t):
    with Camera(1.75, 1060, 500).apply(ctx):
        room(ctx, t, tv=0.0, day=1.0, match=False)
        J, p = on_sofa(ctx, t, expr="tired", look=(1, 0.7))
        pop_label(ctx, t, 57.0, "ODDS x4.5", p[0] + 200, p[1] - 200, WINGREEN, dur=7.5, size=26)
        speech(ctx, t, "kabir_ph", p[0] + 280, p[1] - 30)
        speech(ctx, t, "him", J["head"][0] + 40, J["head"][1] - 80)
    label(ctx, "SUNDAY")
    cap(ctx, "C3", y=985)
    hud(ctx, t)


def g3(ctx, t):
    with Camera(2.0, 1040, 500).apply(ctx):
        room(ctx, t, tv=0.0, match=False)
        rrect(ctx, 640, 380, 120, 50, 8, (14, 14, 16), (70, 70, 76), 3)
        draw_text(ctx, "3:52", 700, 420, 40, (200, 210, 220), face=LG)
        J, p = on_sofa(ctx, t, expr="tired", look=(1, 0.7), lean=0.24)
    vline(ctx, "V6", 1300, 300, 54)
    cap(ctx, "C4", y=985)
    hud(ctx, t)


def r1(ctx, t):
    if t < 80.0:
        lost = prog(t, EVENTS["lost_goa"], EVENTS["lost_goa"] + 0.4)

        def body(ctx, x0, y0, w):
            field(ctx, x0, y0, w, 180)
            moved = ease(prog(t, EVENTS["goa"], EVENTS["goa"] + 0.5))
            rrect(ctx, x0 + 30, y0 + 210, w - 60, 90, 16, (40, 44, 52), (90, 96, 104), 2)
            rtext(ctx, "GOA FUND  " + money(int(12000 * (1 - moved))), x0 + 60, y0 + 268, 34, TEXT, align="left")
            rtext(ctx, "WALLET  " + money(int(12000 * moved)) if t < EVENTS["lost_goa"] else "WALLET  ₹0",
                  x0 + 60, y0 + 350, 34, (190, 196, 200), align="left")
            odds_button(ctx, x0 + 30, y0 + 390, w - 60, "LAST BALL   x2", sel=ease(prog(t, EVENTS["allin"], EVENTS["allin"] + 0.3)))
            rtext(ctx, "YOUR BET  ₹12,000" if t > EVENTS["allin"] else "", x0 + w / 2, y0 + 540, 34, (190, 196, 200))
            result_banner(ctx, x0, y0 + 630, w, "LOST", RED, lost, sub="-₹12,000")
        app(ctx, t, body)
        vline(ctx, "V7", 1500, 300, 54)
    elif t < 88.0:
        chat(ctx, t, "Kabir", ["bro goa money? deadline tonight", "can you lend me 10k? i'll pay you back friday", "sent. no rush bro",
                               "₹10,000 received"], [EVENTS["k_msg"], EVENTS["his_ask"], EVENTS["k_sent"], EVENTS["received"]], mine=(1,))
    else:
        with Camera(1.9, 1080, 500).apply(ctx):
            room(ctx, t, odds=True)
            J, p = on_sofa(ctx, t, expr="hurt" if t > EVENTS["lost_k"] else "anxious", look=(1, 0.6), lean=0.24, shaky=1.0)
            pop_label(ctx, t, EVENTS["lost_k"], "LOST", p[0] + 190, p[1] - 130, RED, dur=2.4, size=40)
        cap(ctx, "C5", y=985)
    hud(ctx, t)


# ---- the turn and the lesson -------------------------------------------------------------------------
def t1(ctx, t):
    acc = ease(prog(t, EVENTS["account"], EVENTS["account"] + 0.5))

    def body(ctx, x0, y0, w):
        field(ctx, x0, y0, w, 180)
        k = ease_out_back(prog(t, EVENTS["vip"], EVENTS["vip"] + 0.3)) * (1 - acc)
        if k > 0:
            c = ctx.c
            c.save()
            c.translate(x0 + w / 2, y0 + 360)
            c.scale(k, k)
            rrect(ctx, -w / 2 + 24, -150, w - 48, 300, 22, (236, 232, 214), None)
            draw_text(ctx, "CONGRATULATIONS!", 0, -90, 40, (40, 40, 46), face=LG)
            draw_text(ctx, "You're now a VIP.", 0, -30, 40, (40, 40, 46))
            draw_text(ctx, "Your personal manager", 0, 30, 32, (80, 80, 86))
            draw_text(ctx, "will call you.", 0, 70, 32, (80, 80, 86))
            c.restore()
        if acc > 0:
            rrect(ctx, x0 + 24, y0 + 210, w - 48, 380, 22, (30, 32, 38), (90, 96, 104), 2, a=acc)
            draw_text(ctx, "MY ACCOUNT", x0 + 60, y0 + 280, 40, TEXT, acc, align="left", face=LG)
            draw_text(ctx, "VIP", x0 + w - 60, y0 + 280, 40, (240, 210, 110), acc, align="right", face=LG)
            draw_text(ctx, "DEPOSITED", x0 + 60, y0 + 370, 32, (190, 196, 200), acc, align="left")
            rtext(ctx, "₹52,600", x0 + w - 60, y0 + 370, 44, TEXT, acc, align="right", face=LG)
            draw_text(ctx, "WON BACK", x0 + 60, y0 + 460, 32, (190, 196, 200), acc, align="left")
            rtext(ctx, "₹15,200", x0 + w - 60, y0 + 460, 44, TEXT, acc, align="right", face=LG)
            ctx.c.drawLine(x0 + 60, y0 + 500, x0 + w - 60, y0 + 500, stroke((90, 96, 104), 2, acc))
            draw_text(ctx, "THE APP KEPT", x0 + 60, y0 + 560, 32, (190, 196, 200), acc * prog(t, 100.0, 100.5), align="left")
            rtext(ctx, "₹37,400", x0 + w - 60, y0 + 560, 44, RED, acc * prog(t, 100.0, 100.5), align="right", face=LG)
    app(ctx, t, body, cy=660)
    cap(ctx, "C6", y=180)
    cap(ctx, "C7", y=180)
    hud(ctx, t)


def l1(ctx, t):
    """The lesson drawn: a pitch. He runs for the stumps marked EVEN; every time he gets close, they slide away."""
    a = ease(prog(t, EVENTS["lesson"], EVENTS["lesson"] + 0.6))
    c = ctx.c
    c.save()
    c.saveLayerAlpha(None, int(255 * a))
    y = 760
    c.drawRect(skia.Rect.MakeXYWH(100, y, W - 200, 26), fill((150, 130, 96)))
    lt = max(0.0, t - EVENTS["lesson"] - 0.4)
    period = 2.4
    k = (lt % period) / period
    n = int(lt // period)
    stump_x = 900 + 220 * (n + ease(prog(k, 0.75, 0.95)))
    runner_x = lerp(300 + 220 * n, stump_x - 200, ease(min(1, k / 0.75)))
    stump_x = min(stump_x, 1700)
    runner_x = min(runner_x, 1460)
    for i in (-18, 0, 18):
        c.drawLine(stump_x + i, y, stump_x + i, y - 150, stroke((226, 220, 200), 9))
    c.drawLine(stump_x - 26, y - 152, stump_x + 26, y - 152, stroke((226, 220, 200), 6))
    draw_text(ctx, "EVEN", stump_x, y - 190, 44, GOLD, 1.0, face=LG)
    me = Character("l1him", scale=1.0)
    hip, feet = standing(runner_x, y, 1, step=(lt * 3.2) % 1.0)
    me.draw(ctx, hip, 1, lean=0.3, feet=feet, expr="determined", look=(1, 0.0))
    for i in range(4):  # how far he has already run
        c.drawLine(220 + i * 40, y + 50, 240 + i * 40, y + 50, stroke((90, 90, 96), 4))
    c.restore()
    c.restore()
    cap(ctx, "C8", y=190)
    cap(ctx, "C9", y=990)
    hud(ctx, t)


# ---- the final fight ----------------------------------------------------------------------------------
def f1f2(ctx, t):
    r0, r1_ = EVENTS["rise"]
    rise = ease(prog(t, r0, r1_)) * (1 - prog(t, EVENTS["crumble"], EVENTS["crumble"] + 0.05))
    inn = ease(prog(t, EVENTS["kabir_in"], EVENTS["kabir_in"] + 1.2))
    zoom = lerp(1.45, 1.7, ease(prog(t, 116, 126)))
    with Camera(zoom, 1000, 500, shake=1.6 * prog(t, 121, 124.6) * (t < 124.8)).apply(ctx):
        room(ctx, t, odds=t > EVENTS["last_ball"])
        door(ctx, 460, open_k=ease(prog(t, EVENTS["knock"] + 0.3, EVENTS["knock"] + 0.8)), key="rdoor", light=0.4)
        if rise > 0:
            P.villain(ctx, 1220, FY, scale=lerp(0.8, 1.3, rise), alpha=rise, grin=1.2, lean=-0.35,
                      reach=(1080, 560) if rise > 0.7 and t < EVENTS["delete"] else None)
        if t < EVENTS["crumble"] + 2.2 and t > EVENTS["crumble"]:
            P.villain_shards(ctx, 1220, FY, 1.3, prog(t, EVENTS["crumble"], EVENTS["crumble"] + 2.0))
        kx = lerp(420, 700, inn)
        lt = t - EVENTS["kabir_in"]
        if lt > 0:
            hipk, feetk = standing(kx, FY, 1, step=(lt * 1.8) % 1.0 if inn < 1 else 0.0)
            Jk = KABIR.draw(ctx, hipk, 1, lean=0.04, feet=feetk, expr="worried" if t < 131.8 else "hopeful", look=(1, 0.2),
                            mouth_open=talk("kabir", t))
            speech(ctx, t, "kabir", Jk["head"][0] + 40, Jk["head"][1] - 80)
        expr = "anxious" if t < 124.8 else ("hurt" if t < 131.8 else "hopeful")
        look = (1, 0.6) if t < 124.8 else (-1, 0.0)
        J, p = on_sofa(ctx, t, expr=expr, look=look, lean=0.2, shaky=1.0 if 121 < t < 124.8 else 0.0)
        if t > EVENTS["last_ball"] and t < EVENTS["delete"]:
            pop_label(ctx, t, EVENTS["last_ball"], "LAST BALL! BET NOW x5", p[0] + 230, p[1] - 160, WINGREEN, dur=5.8, size=28)
        if EVENTS["delete"] - 0.2 < t < EVENTS["delete"] + 1.4:  # the delete box
            a = fade(t, EVENTS["delete"] - 0.2, EVENTS["delete"] + 1.4, 0.15, 0.3)
            rrect(ctx, p[0] + 10, p[1] - 170, 250, 110, 14, (236, 232, 214), None, a=a)
            draw_text(ctx, "Delete app?", p[0] + 135, p[1] - 128, 30, (40, 40, 46), a)
            pressed = t > EVENTS["delete_tap"]
            rrect(ctx, p[0] + 70, p[1] - 108, 130, 38, 10, RED if not pressed else (150, 30, 30), None, a=a)
            draw_text(ctx, "DELETE", p[0] + 135, p[1] - 80, 24, TEXT, a, face=LG)
        speech(ctx, t, "him", J["head"][0] + 40, J["head"][1] - 80)
    vline(ctx, "V8", 600, 250, 62)
    vline(ctx, "V9", 600, 330, 66)
    hud(ctx, t)


INSTEAD = ["Delete the app tonight.", "Tell one person the real number.", "Pay it back slowly. Never win it back."]


def i1(ctx, t):
    a = fade(t, EVENTS["card"], 144.0, 0.3, 0.3)
    rrect(ctx, W / 2 - 500, 280, 1000, 480, 22, (236, 232, 214), LINE, 5, a=a)
    draw_text(ctx, "INSTEAD OF CHASING:", W / 2 - 440, 380, 64, (40, 40, 46), a, align="left", face=LG)
    for i, s in enumerate(INSTEAD):
        k = ease(prog(t, EVENTS["card"] + 0.4 + i * 0.6, EVENTS["card"] + 0.8 + i * 0.6))
        y = 480 + i * 90
        rrect(ctx, W / 2 - 440, y - 40, 44, 44, 6, None, (40, 40, 46), 4, a=a * k)
        draw_text(ctx, s, W / 2 - 370, y, 48, (40, 40, 46), a * k, align="left")
    hud(ctx, t)


# ---- payoff, viewer, mirror, title ----------------------------------------------------------------
def ground(ctx, t, warm=1.0):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, FY)], [col(mix((40, 50, 80), (120, 140, 190), warm)), col(mix((90, 80, 90), (250, 196, 130), warm))])
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), skia.Paint(Shader=sky))
    glow(ctx, 1560, 560, 520, GOLD, 0.35 * warm)
    c.drawCircle(1560, 600, 70, fill((255, 220, 140), warm))
    for i in range(14):
        bx = -200 + i * 160
        bh = 140 + 120 * hrand("gb", i)
        c.drawRect(skia.Rect.MakeXYWH(bx, FY - 140 - bh, 150, bh), fill(mix((40, 36, 44), (90, 70, 66), warm * 0.5)))
    wrect(ctx, -400, FY - 140, W + 800, 140, "gwall", (110, 96, 84), LINE, 3, seg=6)
    c.drawRect(skia.Rect.MakeLTRB(-600, FY, W + 600, FY + 400), fill((150, 128, 92)))
    P.floor(ctx, FY)


def stumps(ctx, x):
    for i in (-12, 0, 12):
        ctx.c.drawLine(x + i, FY, x + i, FY - 110, stroke((226, 220, 200), 7))
    ctx.c.drawLine(x - 18, FY - 112, x + 18, FY - 112, stroke((226, 220, 200), 5))


def p1(ctx, t):
    hit = EVENTS["hit"]
    swing = ease(prog(t, hit - 0.25, hit + 0.1))
    with Camera(1.6, 1020, 520).apply(ctx):
        ground(ctx, t)
        stumps(ctx, 760)
        hip, feet = standing(840, FY, 1)
        J0 = HIM.joints(hip, 1, 0.1)
        sh = J0["shoulder"]
        hand = lerp2((sh[0] - 30, sh[1] + 20), (sh[0] + 50, sh[1] + 40), swing)
        J = HIM.draw(ctx, hip, 1, lean=0.1 - 0.12 * swing, feet=feet, expr="determined" if t < hit else "happy", look=(1, -0.2 if t > hit else 0.0),
                     hands=free_hands(HIM, hip, 1, 0.1, {"near": hand, "far": (hand[0] - 8, hand[1] + 4)}), mouth_open=talk("him", t))
        hp = J["limbs"]["arm_near"][2]
        ang = lerp(-2.4, -0.5, swing)
        tip = (hp[0] + math.cos(ang) * 150, hp[1] + math.sin(ang) * 150)
        ctx.c.drawLine(hp[0], hp[1], tip[0], tip[1], stroke((150, 116, 70), 18))
        ctx.c.drawLine(hp[0], hp[1], tip[0], tip[1], stroke(LINE, 2))
        if t > hit:
            k = prog(t, hit, hit + 1.4)
            ctx.c.drawCircle(lerp(tip[0], 1700, k), lerp(tip[1], 120, k) + 300 * k * (k - 1) * -0.3, 10, fill((200, 60, 50)))
        Jk = stand(KABIR, ctx, 1260, f=-1, expr="happy" if t > hit else "smile", look=(-1, -0.3 if t > hit else 0.0), mouth_open=talk("kabir", t))
        speech(ctx, t, "kabir", Jk["head"][0] - 20, Jk["head"][1] - 80)
    label(ctx, "MARCH")
    cap(ctx, "C10", y=925)
    cap(ctx, "C11", y=995)
    hud(ctx, t)


def stand(ch, ctx, x, f=1, lean=0.04, **kw):
    hip, feet = standing(x, FY, f, ch.scale)
    if kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def vt(ctx, t):
    a = fade(t, 153.2, 160.0, 0.6, 0.6)
    UI = P.PhoneUI(W / 2, 600, 400, 640)
    c = ctx.c
    c.saveLayerAlpha(None, int(255 * a))
    UI.body(ctx, 1.0, mix(BLUE, WINGREEN, 0.4))
    with UI.screen(ctx):
        x0, y0, w = UI.x0 + 18, UI.y0 + 18, UI.w - 36
        draw_text(ctx, "MY ACCOUNT", x0 + w / 2, y0 + 120, 40, TEXT, face=LG)
        draw_text(ctx, "TOTAL DEPOSITED", x0 + w / 2, y0 + 260, 32, (190, 196, 200))
        rtext(ctx, "₹ ?", x0 + w / 2, y0 + 360, 90, GOLD if t > 157 else TEXT, face=LG)
    c.restore()
    cap(ctx, "V1", y=190, size=50)
    cap(ctx, "V2", y=190, size=56)


def x1(ctx, t):
    with Camera(1.65, 1060, 520).apply(ctx):
        ground(ctx, t, warm=0.8)
        # the stranger on the wall, phone in hand
        sx = 1260
        hip = (sx, FY - 140 - 4)
        jump = math.sin(math.pi * prog(t, EVENTS["stranger_win"], EVENTS["stranger_win"] + 0.5))
        st = grey("stranger")
        J0 = st.joints(hip, -1, 0.1)
        sh = J0["shoulder"]
        Js = st.draw(ctx, (hip[0], hip[1] - 10 * jump), -1, lean=0.1, feet={"near": (sx - 34, hip[1] + 100), "far": (sx - 24, hip[1] + 102)},
                     expr="happy" if t < 166.6 else "worried", look=(-1, 0.6) if t < 166.6 else (-1, 0.0), mouth_open=talk("stranger", t),
                     hands=free_hands(st, hip, -1, 0.1, {"near": (sh[0] - 50, sh[1] + 60), "far": (sh[0] - 40, sh[1] + 66)}), screen_glow=0.8)
        P.phone_held(ctx, *Js["limbs"]["arm_near"][2], facing=-1, on=1.0, glow_rgb=mix(BLUE, WINGREEN, 0.5))
        a = prog(t, 162.0, 162.4)
        if a > 0:
            rrect(ctx, sx - 160, Js["head"][1] - 230, 260, 74, 12, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
            draw_text(ctx, "WINNINGS", sx - 146, Js["head"][1] - 206, 18, (160, 160, 168), a, align="left")
            rtext(ctx, "+₹1,300", sx - 146, Js["head"][1] - 168, 38, TEXT, a, align="left", face=LG)
        speech(ctx, t, "stranger", Js["head"][0] - 30, Js["head"][1] - 80)
        walk = ease(prog(t, 162.6, 163.8))
        x = lerp(820, 1020, walk)
        hipm, feetm = standing(x, FY, 1, step=((t - 162.6) * 1.6) % 1.0 if 0 < walk < 1 else 0.0)
        Jm = HIM.draw(ctx, hipm, 1, lean=0.04, feet=feetm, expr="worried" if t < 164 else "hopeful", look=(1, -0.2), mouth_open=talk("him", t))
        speech(ctx, t, "him", Jm["head"][0] + 30, Jm["head"][1] - 80, size=30)


def title(ctx, t):
    a = fade(t, EVENTS["title"], 177.0, 0.8, 0.6)
    draw_text(ctx, "ALL IN.", W / 2, 520, 220, TEXT, a, face=LG)
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 330 + 660 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=48)
    cap(ctx, "T2", y=770, size=72, rgb=GOLD, glow_rgb=(170, 110, 20))


def helpline(ctx, t):
    cap(ctx, "H1", y=500, size=46)
    cap(ctx, "H2", y=580, size=38, rgb=(190, 190, 196))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "S02": s02, "B1": b1, "G1": g1, "G2": g2, "G3": g3, "R1": r1,
    "T1": t1, "L1": l1, "F1": f1f2, "F2": f1f2, "I1": i1, "P1": p1, "VT": vt, "X1": x1, "TT": title, "HL": helpline,
}
CONTINUOUS = {"F2", "HL", "G1"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1_, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS and t0 > 0:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "R1":
        for tc in (80.0, 88.0):
            black(ctx, 1 - prog(t, tc, tc + 0.08) if tc <= t < tc + 0.08 else 0)
    if sid == "HL":
        black(ctx, prog(t, DURATION - 0.8, DURATION))
