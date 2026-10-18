"""FINE.: picture. scene(ctx) draws any frame of the film.

The device: a smiling white mask with a red grin (the villain's grin) that snaps onto his face whenever someone asks
how he is. SAID FINE counts every "fine". Behind it, his real face gets worse, and only the viewer sees it, at night,
when the mask goes back on its hook by the door. A strap appears; then one night it won't come off. The turn: on the
back step at Jo's Halloween party, Jo asks twice. One true sentence cracks the mask with gold light, and the counter is
relabelled SAID TRUE, in gold.
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
from studio.extras import speech as _speech, talk as _talk, free_hands, door, street, phone_close  # noqa: E402
from timeline import (SCENES, CAPS, CUES, BUBBLES, EVENTS, DURATION, scene_at, fine_count, true_count,  # noqa: E402
                      count_changed, RELABEL, G1_T0, G1_DAY, G1_DATES)
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
MASK = (246, 242, 232)
WARM = (236, 178, 104)
PUMPKIN = (206, 122, 56)
HOOK = (1160, 430)


def headphones(ctx, hx, hy, f, s):
    c = ctx.c
    c.drawPath(poly_path([(hx - f * 26 * s, hy - 6 * s), (hx - f * 22 * s, hy - 46 * s), (hx + f * 8 * s, hy - 56 * s),
                          (hx + f * 30 * s, hy - 44 * s)], closed=False, smooth=True), stroke((46, 50, 58), 9 * s))
    rrect(ctx, hx - f * 26 * s - 13 * s, hy - 18 * s, 26 * s, 34 * s, 10 * s, (52, 58, 70), LINE, 3 * s)


def bow_tie(ctx, hx, hy, f, s):
    x, y = hx, hy + 54 * s
    ctx.c.drawPath(poly_path([(x - 16 * s, y - 9 * s), (x, y), (x - 16 * s, y + 9 * s)]), fill((70, 96, 84)))
    ctx.c.drawPath(poly_path([(x + 16 * s, y - 9 * s), (x, y), (x + 16 * s, y + 9 * s)]), fill((70, 96, 84)))
    ctx.c.drawCircle(x, y, 4 * s, fill((50, 70, 60)))


HIM = Character("him")
JO = Character("jo", skin=(190, 160, 134), extra=headphones)
SHOP = Character("shop", skin=(160, 158, 164), extra=bow_tie)


def grey(name, scale=1.0, extra=None):
    return Character(name, skin=(150, 150, 156), scale=scale, extra=extra)


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
    """SAID FINE until he tells the truth; then the same box is relabelled SAID TRUE, in gold."""
    a *= prog(t, 7.3, 7.7)
    if a <= 0:
        return
    lc = count_changed(t)
    pop = prog(t, lc, lc + 0.35) if lc is not None and lc <= t <= lc + 0.35 else 0.0
    if t < RELABEL:
        P.hud(ctx, fine_count(t), label="SAID FINE", a=a, pop=pop)
        return
    k = prog(t, RELABEL, RELABEL + 0.6)
    if k < 1:
        P.hud(ctx, fine_count(t), label="SAID FINE", a=a * (1 - ease(prog(t, RELABEL + 0.4, RELABEL + 0.6))))
        ctx.c.drawLine(70, LETTERBOX + 86, 70 + 220 * ease(min(1, k * 2)), LETTERBOX + 86, stroke(RED, 6, a))
        return
    P.hud(ctx, true_count(t), label="SAID TRUE", a=a, rgb=GOLD, pop=pop)


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


# ---- the device: the mask ----------------------------------------------------------------------
CRACKS = [
    [(6, -42), (2, -28), (9, -18), (3, -6), (8, 6)],
    [(3, -6), (-10, 2), (-16, 16), (-28, 22)],
    [(8, 6), (16, 18), (12, 30), (18, 42)],
    [(2, -28), (-14, -30), (-26, -20)],
]


def _crack_path(pts, k):
    """The first k (0..1) of a crack polyline."""
    if k <= 0:
        return None
    n = len(pts) - 1
    m = k * n
    out = [pts[0]]
    for i in range(n):
        if m >= i + 1:
            out.append(pts[i + 1])
        else:
            f = m - i
            out.append(lerp2(pts[i], pts[i + 1], f))
            break
    return poly_path(out, closed=False)


def mask(ctx, cx, cy, s=1.0, f=1, a=1.0, crack=0.0, mended=0.0, strap=None, rot=0.0, glowk=0.0, clip=None):
    """The smiling mask, centred at (cx, cy), facing f. crack 0..2: gold-lit cracks grow. mended: gold seams.
    strap: (x, y) of the back of his head, for the band that ties it on."""
    if a <= 0:
        return
    c = ctx.c
    if strap is not None:
        c.drawPath(poly_path([(cx - f * 26 * s, cy - 14 * s), lerp2((cx, cy), strap, 0.5), strap], closed=False, smooth=True),
                   stroke((58, 58, 66), 7 * s, a))
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    c.scale(f * s, s)
    if clip is not None:
        c.clipPath(clip, skia.ClipOp.kIntersect, True)
    if a < 1:
        c.saveLayerAlpha(None, int(a * 255))
    if glowk > 0:
        glow(ctx, 0, 0, 90, GOLD, 0.5 * glowk)
    shape = poly_path(wobble_points(ctx, circle_pts(0, 0, 34, 42, 26), "mask", 0.6), smooth=True)
    c.drawPath(shape, blurred(fill((0, 0, 0), 0.3), 4))
    c.drawPath(shape, fill(MASK))
    c.drawPath(poly_path([(-30, -10), (-34, 6), (-28, 24), (-18, 36)], closed=False, smooth=True), stroke((214, 208, 196), 5))
    c.drawPath(shape, stroke(LINE, 3))
    for ex in (-11, 15):  # happy crescent eye holes
        c.drawPath(poly_path([(ex - 8, -6), (ex, -15), (ex + 8, -6)], closed=False, smooth=True), stroke(LINE, 5.5))
    grin = skia.Path()
    grin.moveTo(-18, 10)
    grin.quadTo(3, 46, 26, 8)
    grin.quadTo(4, 22, -18, 10)
    grin.close()
    c.drawPath(grin, blurred(fill(RED, 0.5), 3))
    c.drawPath(grin, fill(RED))
    c.drawPath(grin, stroke(LINE, 2.5))
    for x0, d in ((-20, -1), (28, 1)):
        c.drawLine(x0, 6, x0 + d * 4, 2, stroke(LINE, 2.5))
    for i, pts in enumerate(CRACKS):
        k = crack if i == 0 else (crack - 1.0) * (1.0 if i < 3 else 0.7)
        k = clamp(k * (1.6 if i == 0 else 1.0))
        p = _crack_path(pts, k)
        if p is not None:
            c.drawPath(p, blurred(stroke(GOLD, 9, 0.9), 4))
            c.drawPath(p, stroke((255, 240, 190), 3.2))
        if mended > 0:
            pm = _crack_path(pts, 1.0)
            c.drawPath(pm, blurred(stroke(GOLD, 8, 0.6 * mended), 3))
            c.drawPath(pm, stroke(GOLD, 4.6, mended))
    if a < 1:
        c.restore()
    c.restore()


def face_mask(ctx, J, s=1.0, **kw):
    """The mask on his face (three-quarter view, like the face it covers)."""
    hx, hy = J["head"]
    f = J["facing"]
    strap = kw.pop("strap", False)
    st = (hx - f * 48 * s, hy - 8 * s) if strap else None
    mask(ctx, hx + f * 14 * s, hy + 3 * s, s, f, strap=st, **kw)


def hook(ctx, mask_on_hook=True, a=1.0, mended=0.0):
    """The coat hooks by the door: keys, a scarf, and the mask's own hook."""
    c = ctx.c
    wrect(ctx, 1040, 410, 260, 22, "hookboard", (92, 74, 60), LINE, 3, seg=2)
    for hx in (1080, HOOK[0], 1250):
        c.drawPath(poly_path([(hx, 432), (hx, 452), (hx + 10, 456)], closed=False), stroke((150, 150, 156), 5))
    jk = [(1250, 452), (1242, 520), (1234, 600), (1262, 604), (1266, 520)]
    c.drawPath(poly_path(jk, smooth=True), fill((64, 72, 92)))
    c.drawPath(poly_path(jk, smooth=True), stroke(LINE, 3))
    c.drawLine(1080, 452, 1078, 478, stroke((150, 150, 156), 2))
    rrect(ctx, 1066, 476, 24, 14, 4, (170, 160, 120), LINE, 2)
    if mask_on_hook:
        c.drawPath(poly_path([(HOOK[0] - 10, 470), (HOOK[0], 452), (HOOK[0] + 10, 470)], closed=False), stroke((90, 90, 96), 2))
        mask(ctx, HOOK[0], 500, 0.9, 1, a=a, mended=mended)


def hallway(ctx, t, morning=0.0, open_k=0.0):
    c = ctx.c
    P.back_wall(ctx, rgb=mix((24, 24, 28), (52, 50, 54), morning))
    c.drawRect(skia.Rect.MakeLTRB(-600, FY - 26, W + 600, FY), fill(mix((30, 30, 34), (58, 56, 58), morning)))
    P.floor(ctx, FY)
    # the front door, with a glass pane that lets the morning in
    door(ctx, 1380, open_k=open_k, key="fdoor", light=morning, rgb=(70, 62, 58))
    pane = (1420, 440, 90, 120)
    c.drawRect(skia.Rect.MakeXYWH(*pane), fill(mix((26, 30, 44), (236, 214, 170), morning)))
    if morning > 0:
        glow(ctx, 1465, 500, 300, (255, 226, 170), 0.3 * morning)
        cone(ctx, (1465, 500), (900, FY), (1380, FY), (255, 226, 170), 0.10 * morning)
    if open_k > 0:
        c.drawRect(skia.Rect.MakeXYWH(1380 + 170 * 0.2, FY - 380, 170 * 0.8 * open_k, 380), fill((246, 226, 180), 0.8 * open_k))
        glow(ctx, 1470, 600, 500, (255, 230, 180), 0.4 * open_k)
    wrect(ctx, 1290, FY - 6, 150, 8, "mat", (92, 80, 66), None, 0, seg=2)
    c.drawRect(skia.Rect.MakeXYWH(760, 560, 22, 34), fill((70, 70, 76)))  # light switch
    c.drawRect(skia.Rect.MakeXYWH(767, 568, 8, 12), fill((140, 140, 146)))


def fly(t, t0, frm, to, dur=0.45):
    """Mask position flying from one point to another."""
    k = ease(prog(t, t0, t0 + dur))
    x = lerp(frm[0], to[0], k)
    y = lerp(frm[1], to[1], k) - math.sin(math.pi * k) * 40
    return (x, y), k


# ---- sets ----------------------------------------------------------------------------------------
def shop(ctx):
    c = ctx.c
    P.back_wall(ctx, rgb=(40, 40, 44))
    P.floor(ctx, FY)
    for row in range(3):
        y = 300 + row * 110
        wrect(ctx, 1020, y, 620, 12, ("shelf", row), (90, 84, 76), LINE, 2, seg=2)
        for i in range(9):
            hh = 40 + 30 * hrand("item", row, i)
            rgb = mix((80, 90, 110), (150, 130, 100), hrand("ic", row, i))
            c.drawRect(skia.Rect.MakeXYWH(1036 + i * 66, y - hh, 46, hh), fill(rgb))
    c.drawRect(skia.Rect.MakeXYWH(560, 300, 260, 160), fill((30, 34, 40)))
    draw_text(ctx, "OPEN", 690, 400, 60, (150, 170, 190), face="LuckiestGuy-Regular.ttf")


def shopkeeper(ctx, t, lean=0.02, expr="smile", look=(-1, 0.1)):
    hip, feet = standing(1280, FY - 90, -1)
    return SHOP.draw(ctx, hip, -1, lean=lean, feet=feet, expr=expr, look=look, mouth_open=talk("shop", t))


def counter(ctx):
    wrect(ctx, 1000, 610, 520, 170, "counter", (88, 76, 66), LINE, 3, seg=3)
    wrect(ctx, 980, 596, 560, 18, "ctop", (120, 104, 88), LINE, 3, seg=3)
    wrect(ctx, 1380, 552, 90, 46, "till", (56, 58, 66), LINE, 3, seg=2)


def pitch(ctx, t, warm=0.0, night=False):
    c = ctx.c
    top = (34, 40, 66) if not night else (14, 16, 24)
    bot = (150, 100, 90) if not night else (24, 26, 36)
    if warm > 0:
        top, bot = mix(top, (110, 120, 170), warm), mix(bot, (250, 180, 110), warm)
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, FY)], [col(top), col(bot)])
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), skia.Paint(Shader=sky))
    if warm > 0:
        glow(ctx, 1500, 640, 500, GOLD, 0.35 * warm)
    for i in range(14):  # houses beyond the fence
        bx = -200 + i * 160
        bh = 120 + 90 * hrand("ph", i)
        c.drawRect(skia.Rect.MakeXYWH(bx, FY - 250 - bh * 0.4, 150, bh), fill((28, 28, 36)))
    c.drawRect(skia.Rect.MakeLTRB(-600, FY, W + 600, FY + 400), fill((44, 58, 50)))
    for px in range(-200, 2200, 260):  # the fence
        wrect(ctx, px, FY - 330, 10, 330, ("post", px), (70, 74, 80), LINE, 2, seg=2)
    for i in range(-20, 60):
        x = -200 + i * 40
        c.drawLine(x, FY - 320, x + 320, FY, stroke((90, 96, 104), 1.4, 0.35))
        c.drawLine(x + 320, FY - 320, x, FY, stroke((90, 96, 104), 1.4, 0.35))
    c.drawLine(-600, FY - 320, W + 600, FY - 320, stroke((80, 84, 92), 4))
    P.wrect(ctx, 240, FY - 560, 14, 560, "flood", GREY_D, LINE, 2, seg=2)
    rrect(ctx, 210, FY - 590, 80, 40, 6, (60, 60, 66), LINE, 3)
    if night:
        glow(ctx, 250, FY - 570, 300, (230, 236, 255), 0.35)
        cone(ctx, (250, FY - 560), (500, FY + 40), (1500, FY + 40), (230, 236, 255), 0.08)
    P.floor(ctx, FY)


def ball(ctx, x, y=FY):
    wcircle(ctx, x, y - 22, 22, "ball", (226, 224, 216), LINE, 3)
    ctx.c.drawCircle(x + 4, y - 24, 7, fill(LINE))


def kitchen(ctx):
    c = ctx.c
    P.back_wall(ctx, rgb=(22, 22, 26))
    P.floor(ctx, FY)
    P.window(ctx, 1380, 230, 220, 200, "kwin", night=True)
    wrect(ctx, 520, 470, 220, 110, "cupboard", (46, 46, 52), LINE, 3, seg=2)
    rrect(ctx, 560, 400, 120, 50, 8, (14, 14, 16), (70, 70, 76), 3)
    draw_text(ctx, "4:40", 620, 440, 40, (200, 210, 220), face="LuckiestGuy-Regular.ttf")
    glow(ctx, 1030, 260, 260, (220, 220, 200), 0.12)
    c.drawLine(1030, 0, 1030, 250, stroke(LINE, 3))
    c.drawPath(poly_path([(990, 250), (1070, 250), (1050, 272), (1010, 272)]), fill((140, 136, 120)))
    P.table(ctx, 900, 640, 420, key="ktable")


def jo_house(ctx, t, open_k=1.0):
    c = ctx.c
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), fill((18, 20, 30)))
    glow(ctx, 300, 200, 60, (220, 220, 230), 0.4)
    c.drawCircle(300, 200, 22, fill((226, 226, 232)))
    c.drawRect(skia.Rect.MakeLTRB(760, 160, W + 600, FY), fill((50, 42, 40)))
    for i in range(10):
        c.drawLine(760, 200 + i * 60, W + 600, 200 + i * 60, stroke((58, 50, 46), 3))
    wx, wy, ww, wh = 1340, 280, 380, 240  # the party window
    c.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), fill(WARM))
    glow(ctx, wx + ww / 2, wy + wh / 2, ww, (255, 210, 140), 0.25)
    for i in range(7):
        x = wx + 30 + i * 52
        y = wy + 40 + math.sin(i * 1.3) * 8
        c.drawCircle(x, y, 7, fill((255, 236, 170)))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
    for i, dx in enumerate((0.25, 0.55, 0.8)):
        x = wx + dx * ww
        bob = math.sin(t * 5 + i * 2) * 6
        c.drawPath(poly_path([(x - 30, wy + wh), (x - 30, wy + wh - 80 + bob), (x + 30, wy + wh - 80 + bob), (x + 30, wy + wh)]), fill((80, 52, 36)))
        c.drawCircle(x, wy + wh - 110 + bob, 30, fill((80, 52, 36)))
    c.restore()
    wrect(ctx, wx - 10, wy - 10, ww + 20, wh + 20, "jwin", None, (80, 72, 70), 12, seg=2)
    # the door, open on the party
    dx0, dw, dh = 900, 190, 400
    c.drawRect(skia.Rect.MakeXYWH(dx0, FY - dh, dw, dh), fill(mix((20, 18, 18), WARM, open_k)))
    if open_k > 0:
        glow(ctx, dx0 + dw / 2, FY - dh / 2, 420, (255, 200, 130), 0.35 * open_k)
        cone(ctx, (dx0 + dw / 2, FY - dh / 2), (dx0 - 260, FY), (dx0 + dw + 120, FY), (255, 200, 130), 0.12 * open_k)
    wrect(ctx, dx0 - 12, FY - dh - 12, dw + 24, dh + 12, "jdoorf", None, (40, 36, 36), 8, seg=2)
    wrect(ctx, dx0 + dw - 20 - 30 * open_k, FY - dh, 20 + 30 * open_k, dh, "jdoor", (66, 50, 44), LINE, 3, seg=2)
    lantern(ctx, 1170, FY, t)
    P.floor(ctx, FY)


def lantern(ctx, x, y, t, s=1.0, lit=1.0):
    """A carved pumpkin with a candle in it."""
    c = ctx.c
    if lit > 0:
        glow(ctx, x, y - 34 * s, 140 * s, (255, 170, 80), 0.3 * lit * (0.9 + 0.1 * math.sin(t * 13)))
    wcircle(ctx, x, y - 34 * s, 40 * s, ("lan", x), PUMPKIN, LINE, 3, ry=34 * s)
    c.drawLine(x, y - 68 * s, x + 4 * s, y - 82 * s, stroke((70, 80, 50), 6 * s))
    face_rgb = mix((40, 24, 14), (255, 210, 120), lit)
    for side in (-1, 1):
        c.drawPath(poly_path([(x + side * 18 * s, y - 50 * s), (x + side * 8 * s, y - 38 * s), (x + side * 26 * s, y - 38 * s)]), fill(face_rgb))
    c.drawPath(poly_path([(x - 20 * s, y - 24 * s), (x - 8 * s, y - 16 * s), (x, y - 24 * s), (x + 8 * s, y - 16 * s), (x + 20 * s, y - 24 * s),
                          (x, y - 8 * s)]), fill(face_rgb))


def party_room(ctx, t):
    c = ctx.c
    P.back_wall(ctx, rgb=(66, 48, 38))
    P.floor(ctx, FY)
    for i in range(16):
        x = 160 + i * 110
        y = 200 + math.sin(i * 0.9) * 20
        c.drawCircle(x, y, 8, fill((255, 230, 160)))
        glow(ctx, x, y, 40, (255, 210, 140), 0.25)
    c.drawPath(poly_path([(160 + i * 110, 200 + math.sin(i * 0.9) * 20) for i in range(16)], closed=False, smooth=True), stroke(LINE, 2))
    P.wall_clock(ctx, 640, 330, 12, 0, r=40, key="pclock")
    for i, x in enumerate((1600, 1690)):
        lantern(ctx, x, 600, t, s=0.9)
    P.table(ctx, 1560, 600, 240, key="ptable")
    glow(ctx, 960, 500, 900, (255, 190, 120), 0.12)


def back_step(ctx, t, door_k=1.0, warm=0.0):
    c = ctx.c
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), fill(mix((16, 18, 28), (40, 34, 40), warm)))
    glow(ctx, 1500, 210, 70, (220, 220, 230), 0.4)
    c.drawCircle(1500, 210, 24, fill((226, 226, 232)))
    for i in range(30):
        c.drawCircle(-100 + hrand("st", i) * 2100, 100 + hrand("sy", i) * 260, 1.6, fill((200, 200, 210), 0.6))
    for px in range(1150, 2200, 90):  # the garden fence
        wrect(ctx, px, FY - 260, 70, 260, ("gf", px), (40, 40, 46), LINE, 2, seg=2)
    c.drawRect(skia.Rect.MakeLTRB(-600, 140, 760, FY), fill((44, 38, 38)))  # the house wall
    for i in range(10):
        c.drawLine(-600, 180 + i * 62, 760, 180 + i * 62, stroke((52, 44, 42), 3))
    dx0, dw, dh = 420, 180, 400
    c.drawRect(skia.Rect.MakeXYWH(dx0, FY - 90 - dh, dw, dh), fill(mix((18, 16, 16), WARM, door_k)))
    if door_k > 0:
        glow(ctx, dx0 + dw / 2, FY - 90 - dh / 2, 400, (255, 200, 130), 0.3 * door_k)
        cone(ctx, (dx0 + dw / 2, FY - 300), (dx0 + 40, FY), (dx0 + dw + 560, FY), (255, 200, 130), 0.10 * door_k)
    wrect(ctx, dx0 - 12, FY - 90 - dh - 12, dw + 24, dh + 12, "bdoorf", None, (36, 32, 32), 8, seg=2)
    wrect(ctx, 360, FY - 90, 860, 90, "step", (70, 66, 64), LINE, 3, seg=3)
    P.floor(ctx, FY)


# ---- the hook ------------------------------------------------------------------------------------
def s01(ctx, t):
    on = EVENTS["mask_on"]
    morning = 1.0
    with Camera(lerp(2.2, 1.8, ease(prog(t, 3.2, 5.2))), lerp(1070, 1150, ease(prog(t, 3.2, 5.2))), 500).apply(ctx):
        hallway(ctx, t, morning=morning, open_k=ease(prog(t, EVENTS["door"], EVENTS["door"] + 0.8)))
        hook(ctx, mask_on_hook=False)
        reach = math.sin(math.pi * prog(t, on - 0.7, on + 0.2))
        J0 = HIM.joints(standing(1000, FY, 1)[0], 1, 0.04)
        hands = {"far": lerp2((J0["shoulder"][0] + 10, J0["shoulder"][1] + 90), (HOOK[0] - 40, 470), reach)} if reach > 0 else None
        J = stand(HIM, ctx, 1000, f=1, lean=0.06 - 0.03 * reach, expr="tired" if t < on else "neutral", look=(1, 0.4) if t < on - 1.2 else (1, -0.2),
                  hands=hands, near_arm_front=True)
        pos, k = fly(t, on, (HOOK[0], 500), (J["head"][0] + 14, J["head"][1] + 3))
        if k <= 0:
            mask(ctx, HOOK[0], 500, 0.9, 1)
        elif k < 1:
            mask(ctx, pos[0], pos[1], lerp(0.9, 1.0, k), 1, rot=-12 * math.sin(math.pi * k))
        else:
            face_mask(ctx, J)
    cap(ctx, "C1", y=985)


def h1(ctx, t):
    with Camera(1.7, 1080, 520).apply(ctx):
        shop(ctx)
        Js = shopkeeper(ctx, t)
        counter(ctx)
        J0 = HIM.joints(standing(900, FY, 1)[0], 1, 0.04)
        sh = J0["shoulder"]
        J = stand(HIM, ctx, 900, f=1, lean=0.04, expr="neutral", look=(1, 0.0), hands={"near": (sh[0] + 46, sh[1] + 70)})
        hp = J["limbs"]["arm_near"][2]
        wrect(ctx, hp[0] - 10, hp[1] - 48, 34, 56, "milk", (226, 228, 232), LINE, 3, seg=2)
        face_mask(ctx, J)
        speech(ctx, t, "shop", Js["head"][0] - 40, Js["head"][1] - 76)
        speech(ctx, t, "him", J["head"][0] + 80, J["head"][1] - 76)
    hud(ctx, t)


def h2(ctx, t):
    lt = t - 9.5
    with Camera(1.7, 960, 520).apply(ctx):
        street(ctx, t, lamps=(400, 1500), sky=(56, 62, 80), window_rgb=(150, 140, 110))
        x, ph = walk_x(820, lt, 50)
        hip, feet = standing(x, FY, 1, step=ph)
        J0 = HIM.joints(hip, 1, 0.06)
        ear = (J0["head"][0] - 40, J0["head"][1] - 2)
        J0 = HIM.joints(hip, 1, 0.06, hands={"far": ear})
        hp = J0["limbs"]["arm_far"][2]
        P.phone_side(ctx, hp[0] - 6, hp[1] - 4, on=0.6, angle=-70)
        J = HIM.draw(ctx, hip, 1, lean=0.06, feet=feet, expr="neutral", look=(1, 0.1), hands={"far": ear})
        face_mask(ctx, J)
        speech(ctx, t, "mum", hp[0] - 60, hp[1] - 100)
        speech(ctx, t, "him", J["head"][0] + 120, J["head"][1] - 80)
    hud(ctx, t)


def h3(ctx, t):
    with Camera(1.6, 1040, 520).apply(ctx):
        pitch(ctx, t)
        ball(ctx, 1080 + 30 * math.sin(t * 2))
        Jj = stand(JO, ctx, 1220, f=-1, lean=0.04, expr="smile", look=(-1, 0.1), mouth_open=talk("jo", t))
        J = stand(HIM, ctx, 920, f=1, lean=0.02, expr="neutral", look=(1, 0.0))
        face_mask(ctx, J)
        speech(ctx, t, "jo", Jj["head"][0] - 20, Jj["head"][1] - 76)
        speech(ctx, t, "him", J["head"][0] + 40, J["head"][1] - 80)
    cap(ctx, "C2", y=985)
    hud(ctx, t)


# ---- the wound and the stakes ---------------------------------------------------------------------
def s02(ctx, t):
    off = EVENTS["mask_off"]
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0, t1))
    with Camera(lerp(2.1, 1.7, ease(prog(t, t0 - 0.4, t1))), lerp(1080, 1130, ease(prog(t, t0 - 0.4, t1))), 500).apply(ctx):
        hallway(ctx, t, morning=0.0)
        glow(ctx, HOOK[0], 500, 160, RED, 0.25 * born)
        if born > 0:
            P.villain(ctx, 1420, FY, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 24.4, 25.0)), lean=-0.3)
        hook(ctx, mask_on_hook=False)
        J = stand(HIM, ctx, 1000, f=1, lean=0.08 + 0.06 * prog(t, off, off + 2.0), expr="neutral" if t < off + 0.3 else "hurt",
                  look=(1, 0.1) if t < off + 0.5 else (1, 0.9))
        pos, k = fly(t, off, (J["head"][0] + 14, J["head"][1] + 3), (HOOK[0], 500))
        if k <= 0:
            face_mask(ctx, J)
        elif k < 1:
            mask(ctx, pos[0], pos[1], lerp(1.0, 0.9, k), 1, rot=10 * math.sin(math.pi * k))
        else:
            mask(ctx, HOOK[0], 500, 0.9, 1)
            if born > 0:
                glow(ctx, HOOK[0] + 4, 516, 60, RED, 0.5 * born)
    cap(ctx, "C3", y=985)
    vline(ctx, "V1", 560, 300, 58)
    vline(ctx, "V2", 560, 380, 52)
    hud(ctx, t)


def b1(ctx, t):
    phone_close(ctx, t, "Jo", ["halloween at mine, sat 31st. costumes compulsory", "you alright? you've been quiet", "all good! can't wait"],
                [EVENTS["jo_text"], EVENTS["jo_text2"], EVENTS["his_reply"]], mine=(2,), avatar=(190, 160, 134))
    hud(ctx, t)


# ---- the grind ---------------------------------------------------------------------------------------
def g1(ctx, t):
    """One locked shot, five days. Night: the mask comes off, his face is worse. Morning: it goes back on."""
    i = min(4, int((t - G1_T0) // G1_DAY))
    d0 = G1_T0 + i * G1_DAY
    night = t < d0 + 1.2
    worse = i / 4
    with Camera(1.7, 1110, 500).apply(ctx):
        hallway(ctx, t, morning=0.0 if night else 1.0)
        hook(ctx, mask_on_hook=False)
        hip, feet = standing(1000, FY, 1)
        lean = 0.06 + (0.12 + 0.1 * worse if night else 0.02)
        J = HIM.draw(ctx, hip, 1, lean=lean, feet=feet, expr=("tired" if i < 2 else "hurt") if night else "neutral",
                     look=(1, 0.6 + 0.3 * worse) if night else (1, 0.0))
        strap = i >= 2
        if night:
            pos, k = fly(t, d0 + 0.2, (J["head"][0] + 14, J["head"][1] + 3), (HOOK[0], 500), dur=0.35 + 0.25 * worse)
            if k <= 0:
                face_mask(ctx, J, strap=strap)
            elif k < 1:
                mask(ctx, pos[0], pos[1], 1.0, 1)
            else:
                mask(ctx, HOOK[0], 500, 0.9, 1)
        else:
            pos, k = fly(t, d0 + 1.3, (HOOK[0], 500), (J["head"][0] + 14, J["head"][1] + 3), dur=0.3)
            if k <= 0:
                mask(ctx, HOOK[0], 500, 0.9, 1)
            elif k < 1:
                mask(ctx, pos[0], pos[1], 1.0, 1)
            else:
                face_mask(ctx, J, strap=strap)
    label(ctx, G1_DATES[i])
    vline(ctx, "V3", 600, 330, 54)
    hud(ctx, t)


def g2(ctx, t):
    jo_off = EVENTS["jo_off"]
    with Camera(1.6, 1040, 520).apply(ctx):
        pitch(ctx, t, night=True)
        ball(ctx, 1100)
        lt = max(0.0, t - jo_off)
        jx, ph = walk_x(1240, lt, 120)
        Jj = stand(JO, ctx, jx, f=-1 if lt <= 0 else 1, lean=0.04, step=ph if lt > 0 else 0.0, expr="worried" if lt <= 0 else "neutral",
                   look=(-1, 0.1) if lt <= 0 else (1, 0.0), mouth_open=talk("jo", t))
        J = stand(HIM, ctx, 920, f=1, lean=0.04, expr="neutral", look=(1, 0.0))
        face_mask(ctx, J, strap=True)
        speech(ctx, t, "jo", Jj["head"][0] - 20, Jj["head"][1] - 76)
        speech(ctx, t, "him", J["head"][0] + 60, J["head"][1] - 80)
    cap(ctx, "C4", y=985)
    hud(ctx, t)


def g3(ctx, t):
    with Camera(1.6, 1060, 520).apply(ctx):
        kitchen(ctx)
        ctx.c.drawOval(skia.Rect.MakeXYWH(1130, 626, 110, 18), fill((226, 222, 210)))
        ctx.c.drawOval(skia.Rect.MakeXYWH(1150, 620, 70, 14), fill((150, 120, 80)))
        J = sit(HIM, ctx, 980, f=1, lean=0.26, expr="hurt", look=(1, 0.9), hands={"near": (1080, 632), "far": (1066, 636)})
        mask(ctx, 1300, 614, 0.8, 1, rot=-80)
    vline(ctx, "V4", 1340, 300, 50)
    cap(ctx, "C5", y=985)
    hud(ctx, t)


def r1(ctx, t):
    p0, p1 = EVENTS["pull"]
    pull = prog(t, p0, p1)
    jerk = math.sin(t * 22) * (1 if p0 < t < p1 else 0)
    with Camera(lerp(1.7, 2.1, ease(prog(t, 60.5, 66.0))), 1060, 500).apply(ctx):
        hallway(ctx, t, morning=0.0)
        hook(ctx, mask_on_hook=False)
        hip, feet = standing(1000, FY, 1)
        J0 = HIM.joints(hip, 1, 0.06, head_tilt=0.08 * jerk)
        hx, hy = J0["head"]
        grip = (hx + 44 + 4 * jerk, hy + 6) if p0 < t < p1 + 0.5 else None
        hands = {"near": grip, "far": (hx + 16, hy - 40)} if grip else None
        J = HIM.draw(ctx, hip, 1, lean=0.06, head_tilt=0.08 * jerk, feet=feet, expr="anxious", look=(1, 0.2),
                     hands=free_hands(HIM, hip, 1, 0.06, hands, 0.08 * jerk) if hands else None, near_arm_front=False)
        face_mask(ctx, J, strap=True, rot=3 * jerk)
        if hands:
            hp = J["limbs"]["arm_near"][2]
            ctx.c.drawCircle(hp[0], hp[1], 11, fill(HIM.skin))
            ctx.c.drawCircle(hp[0], hp[1], 11, stroke(LINE, 3))
    label(ctx, "OCT 30")
    vline(ctx, "V5", 600, 330, 56)
    cap(ctx, "C6", y=985)
    vline(ctx, "V6", 600, 330, 56)
    hud(ctx, t)


# ---- the party and the turn ---------------------------------------------------------------------
def vampire(ctx, J, s=1.0):
    """Jo's costume: a high dark collar behind the head."""
    hx, hy = J["head"]
    c = ctx.c
    p = poly_path([(hx - 60 * s, hy + 60 * s), (hx - 74 * s, hy - 10 * s), (hx - 30 * s, hy + 30 * s), (hx, hy + 50 * s),
                   (hx + 30 * s, hy + 30 * s), (hx + 74 * s, hy - 10 * s), (hx + 60 * s, hy + 60 * s)])
    c.drawPath(p, fill((30, 26, 34)))
    c.drawPath(p, stroke(LINE, 3 * s))


def t1(ctx, t):
    open_k = ease(prog(t, EVENTS["jo_door"], EVENTS["jo_door"] + 0.6))
    with Camera(1.6, 1000, 500).apply(ctx):
        jo_house(ctx, t, open_k=open_k)
        Jj0 = JO.joints(standing(1000, FY, -1)[0], -1, 0.02)
        if open_k > 0:
            vampire(ctx, Jj0)
            laugh = ease(prog(t, 74.2, 74.5))
            Jj = stand(JO, ctx, 1000, f=-1, lean=0.02 - 0.06 * laugh, expr="happy" if laugh > 0.5 else "smile", look=(-1, 0.1),
                       mouth_open=talk("jo", t) + 0.3 * laugh * abs(math.sin(t * 9)) * (1 - prog(t, 75.4, 75.8)), alpha=open_k)
            speech(ctx, t, "jo", Jj["head"][0] + 20, Jj["head"][1] - 80)
        pt = ease(prog(t, EVENTS["point"], EVENTS["point"] + 0.3)) * (1 - ease(prog(t, 74.2, 74.6)))
        J0 = HIM.joints(standing(760, FY, 1)[0], 1, 0.04)
        hands = {"far": lerp2((J0["shoulder"][0], J0["shoulder"][1] + 96), (J0["head"][0] + 50, J0["head"][1] + 30), pt)} if pt > 0 else None
        J = stand(HIM, ctx, 760, f=1, lean=0.04, expr="neutral", look=(1, 0.0), hands=hands)
        face_mask(ctx, J, strap=True)
        speech(ctx, t, "him", J["head"][0] + 20, J["head"][1] - 80)
    label(ctx, "OCT 31")
    cap(ctx, "C7", y=985)
    hud(ctx, t)


def costume_guest(ctx, t, x, kind, off, i):
    """A party guest. kind: 'pumpkin' (a pumpkin over the head), 'ghost' (a sheet), 'witch' (a hat). off: 0..1 taken off."""
    ch = grey(f"guest{i}")
    laugh = off > 0.5
    J = stand(ch, ctx, x, f=-1 if x > 1000 else 1, lean=0.02, expr="happy" if laugh else "smile", look=(0, 0.0),
              mouth_open=(0.4 * abs(math.sin(t * 9 + i)) if laugh else 0.0) + (talk("guest", t) if i == 0 else 0.0))
    hx, hy = J["head"]
    lift_y = -260 * ease(off)
    a = 1 - ease(prog(off, 0.6, 1.0))
    if kind == "pumpkin":
        ctx.c.save()
        ctx.c.translate(0, lift_y)
        c = ctx.c
        c.saveLayerAlpha(None, int(255 * a))
        wcircle(ctx, hx, hy + 4, 64, ("pk", i), PUMPKIN, LINE, 3, ry=58)
        for side in (-1, 1):
            c.drawPath(poly_path([(hx + side * 26, hy - 14), (hx + side * 12, hy + 4), (hx + side * 38, hy + 4)]), fill((50, 26, 12)))
        c.drawPath(poly_path([(hx - 30, hy + 22), (hx, hy + 40), (hx + 30, hy + 22), (hx, hy + 30)]), fill((50, 26, 12)))
        c.restore()
        c.restore()
    elif kind == "ghost":
        c = ctx.c
        c.save()
        c.translate(0, lift_y)
        c.saveLayerAlpha(None, int(255 * a))
        p = poly_path([(hx - 70, hy + 150), (hx - 66, hy - 20), (hx - 40, hy - 60), (hx + 40, hy - 60), (hx + 66, hy - 20), (hx + 70, hy + 150),
                       (hx + 40, hy + 136), (hx, hy + 152), (hx - 40, hy + 136)], smooth=True)
        c.drawPath(p, fill((232, 230, 226)))
        c.drawPath(p, stroke(LINE, 3))
        for side in (-1, 1):
            c.drawOval(skia.Rect.MakeXYWH(hx + side * 18 - 8, hy - 16, 16, 22), fill(LINE))
        c.restore()
        c.restore()
    else:
        c = ctx.c
        c.save()
        c.translate(0, lift_y)
        c.saveLayerAlpha(None, int(255 * a))
        c.drawPath(poly_path([(hx - 70, hy - 34), (hx + 70, hy - 34), (hx + 20, hy - 50), (hx + 10, hy - 150), (hx - 20, hy - 50)]), fill((30, 28, 40)))
        c.drawPath(poly_path([(hx - 70, hy - 34), (hx + 70, hy - 34), (hx + 20, hy - 50), (hx + 10, hy - 150), (hx - 20, hy - 50)]), stroke(LINE, 3))
        c.restore()
        c.restore()
    return J


def t2(ctx, t):
    off = prog(t, EVENTS["masks_off"], EVENTS["masks_off"] + 0.9)
    p0, p1 = EVENTS["his_pull"]
    jerk = math.sin(t * 22) * (1 if p0 < t < p1 else 0)
    lt = max(0.0, t - EVENTS["leave"])
    with Camera(1.45, 980, 500).apply(ctx):
        party_room(ctx, t)
        Jg = costume_guest(ctx, t, 520, "pumpkin", off, 0)
        costume_guest(ctx, t, 1100, "ghost", prog(t, EVENTS["masks_off"] + 0.2, EVENTS["masks_off"] + 1.1), 1)
        costume_guest(ctx, t, 1260, "witch", prog(t, EVENTS["masks_off"] + 0.1, EVENTS["masks_off"] + 1.0), 2)
        Jj0 = JO.joints(standing(1420, FY, -1)[0], -1, 0.02)
        vampire(ctx, Jj0)
        stand(JO, ctx, 1420, f=-1, lean=0.02, expr="happy" if off > 0.5 else "smile", look=(-1, 0.0),
              mouth_open=0.4 * abs(math.sin(t * 8)) if off > 0.5 else 0.0)
        if lt <= 0:
            hip, feet = standing(840, FY, 1)
            J0 = HIM.joints(hip, 1, 0.04, head_tilt=0.08 * jerk)
            hx, hy = J0["head"]
            hands = {"near": (hx + 44 + 4 * jerk, hy + 6), "far": (hx + 16, hy - 40)} if p0 < t < p1 else None
            J = HIM.draw(ctx, hip, 1, lean=0.04, head_tilt=0.08 * jerk, feet=feet, expr="anxious", look=(1, 0.0),
                         hands=free_hands(HIM, hip, 1, 0.04, hands, 0.08 * jerk) if hands else None, near_arm_front=False)
            face_mask(ctx, J, strap=True, rot=3 * jerk)
            if hands:
                hp = J["limbs"]["arm_near"][2]
                ctx.c.drawCircle(hp[0], hp[1], 11, fill(HIM.skin))
                ctx.c.drawCircle(hp[0], hp[1], 11, stroke(LINE, 3))
        else:
            x, ph = walk_x(840, lt, -110)
            hip, feet = standing(x, FY, -1, step=ph)
            J = HIM.draw(ctx, hip, -1, lean=0.1, feet=feet, expr="sad", look=(-1, 0.5))
            face_mask(ctx, J, strap=True)
        speech(ctx, t, "guest", Jg["head"][0] + 40, Jg["head"][1] - 90)
    hud(ctx, t)


def t3(ctx, t):
    sits = EVENTS["jo_sits"]
    rise0, rise1 = EVENTS["rise"]
    rise = ease(prog(t, rise0, rise1)) * (1 - prog(t, EVENTS["fall"], EVENTS["fall"] + 0.1))
    fall = prog(t, EVENTS["fall"], EVENTS["fall"] + 1.4)
    crack = ease(prog(t, EVENTS["crack1"], EVENTS["crack1"] + 0.8)) + ease(prog(t, EVENTS["crack2"], EVENTS["crack2"] + 0.9))
    arm = ease(prog(t, EVENTS["arm"], EVENTS["arm"] + 0.6))
    zoom = lerp(1.5, 1.9, ease(prog(t, 91.0, 100.8))) - 0.25 * ease(prog(t, 105.6, 108.0))
    with Camera(zoom, lerp(860, 900, ease(prog(t, 91.0, 100.8))), 520).apply(ctx):
        back_step(ctx, t, warm=0.6 * ease(prog(t, EVENTS["fall"], EVENTS["fall"] + 2.0)))
        if rise > 0:
            P.villain(ctx, 680, FY - 90, scale=lerp(0.55, 0.95, rise), alpha=rise, grin=1.2, lean=0.25)
        if fall > 0 and fall < 1:
            P.villain_shards(ctx, 680, FY - 90, 0.95, fall)
        if fall > 0:
            glow(ctx, 900, 480, 500, GOLD, 0.25 * min(1, fall * 2))
        # Jo: out of the door, down to the step
        jl = prog(t, EVENTS["back_door"], sits)
        if t < sits:
            if jl > 0:
                x, ph = walk_x(560, (t - EVENTS["back_door"]), 260)
                hip, feet = standing(min(x, 1060), FY - 90, 1, step=ph)
                Jj = JO.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="worried", look=(1, 0.3), alpha=min(1, jl * 4))
        else:
            hip, feet = seated(1080, FY - 90 - 4, -1, floor_y=FY)
            hands = None
            if arm > 0:
                hs = HIM.joints(seated(880, FY - 90 - 4, 1, floor_y=FY)[0], 1, 0.2)["shoulder"]
                hands = {"far": (lerp(1040, hs[0] - 6, arm), lerp(650, hs[1] + 4, arm))}
                hands = free_hands(JO, hip, -1, 0.12 + 0.1 * arm, hands)
            Jj = JO.draw(ctx, hip, -1, lean=0.12 + 0.1 * arm, feet=feet, expr="worried" if t < 105.6 else "smile", look=(-1, 0.3),
                         mouth_open=talk("jo", t), hands=hands)
            speech(ctx, t, "jo", Jj["head"][0] + 40, Jj["head"][1] - 80)
        hip, feet = seated(880, FY - 90 - 4, 1, floor_y=FY)
        expr = "sad" if t < EVENTS["fall"] else ("hurt" if t < 107.2 else "hopeful")
        J = HIM.draw(ctx, hip, 1, lean=0.2 - 0.06 * prog(t, 92.0, 93.0), feet=feet, expr=expr,
                     look=(1, 0.7) if t < 92.0 else (1, 0.2), hands=free_hands(HIM, hip, 1, 0.2, {"near": (960, 660), "far": (948, 664)}),
                     tear=prog(t, EVENTS["tear"], EVENTS["tear"] + 1.6) if t < 108 else 0.0, mouth_open=talk("him", t))
        hx, hy = J["head"]
        if fall <= 0:
            face_mask(ctx, J, strap=True, crack=crack, glowk=0.6 * min(1, crack))
        else:
            for i, (dx, dy, rot) in enumerate(((-130, -40, -120), (120, -20, 110), (10, 30, 50))):
                wedge = skia.Path()
                a0 = -math.pi / 2 + i * 2 * math.pi / 3 + 0.3
                wedge.moveTo(6, 0)
                for j in range(9):
                    aa = a0 + j * (2 * math.pi / 3) / 8
                    wedge.lineTo(6 + math.cos(aa) * 80, math.sin(aa) * 80)
                wedge.close()
                k = ease(fall)
                px = hx + 14 + dx * k
                py = hy + 3 + dy * k + 420 * fall * fall
                mask(ctx, px, py, 1.0, 1, rot=rot * k, crack=2.0, a=1 - prog(fall, 0.5, 0.9), clip=wedge)
            glow(ctx, hx + 14, hy, 120, GOLD, 0.5 * (1 - fall))
        speech(ctx, t, "him", J["head"][0] - 20, J["head"][1] - 90)
    cap(ctx, "C8", y=985)
    vline(ctx, "V7", 1420, 300, 58)
    vline(ctx, "V8", 1420, 380, 62)
    hud(ctx, t)


# ---- the lesson and the practice -------------------------------------------------------------------
def l1(ctx, t):
    """The mask from the side: the hurt bounces back in; every 'you ok?' bounces off."""
    a1 = ease(prog(t, EVENTS["inside"], EVENTS["inside"] + 0.6))
    a2 = ease(prog(t, EVENTS["outside"], EVENTS["outside"] + 0.6))
    c = ctx.c
    hx, hy, R = 820, 560, 230
    wcircle(ctx, hx, hy, R, "lhead", (40, 40, 46), (110, 110, 120), 5, a=a1)
    if a1 > 0:
        c.save()
        c.saveLayerAlpha(None, int(255 * a1))
        # the mask: a thick white arc on the front of the head, the grin showing
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(hx - R - 14, hy - R - 14, 2 * R + 28, 2 * R + 28), -60, 120)
        c.drawPath(arc, stroke(MASK, 46))
        c.drawPath(arc, stroke(LINE, 3))
        c.drawPath(poly_path([(hx + R + 22, hy + 40), (hx + R + 40, hy + 70), (hx + R + 10, hy + 110)], closed=False, smooth=True), stroke(RED, 9))
        # the hurt: a knot inside, its lines bounce off the mask's inside
        for i in range(26):
            a = i * 0.7 + t * 0.6
            r = 30 + 26 * hrand("knot", i)
            c.drawLine(hx - 20 + math.cos(a) * r, hy + math.sin(a * 1.3) * r, hx - 20 + math.cos(a + 2) * r, hy + math.sin(a * 1.3 + 2) * r,
                       stroke((140, 150, 176), 3, 0.8))
        for i in range(3):
            k = (t * 0.7 + i / 3) % 1.0
            ang = -0.5 + i * 0.5
            ex, ey = hx - 20 + math.cos(ang) * (R - 30), hy + math.sin(ang) * (R - 30)
            if k < 0.5:
                p = lerp2((hx - 20, hy), (ex, ey), k * 2)
            else:
                p = lerp2((ex, ey), (hx - 60, hy + (i - 1) * 60), (k - 0.5) * 2)
            c.drawCircle(p[0], p[1], 12, fill((140, 150, 176)))
        draw_text(ctx, "THE HURT", hx - 20, hy + 120, 40, (170, 176, 196), 1.0, face="LuckiestGuy-Regular.ttf")
        c.restore()
        c.restore()
    if a2 > 0:
        for i in range(3):
            k = (t * 0.45 + i / 3) % 1.0
            y = hy - 150 + i * 150
            x0, x1 = 1620, hx + R + 70
            x = lerp(x0, x1, k * 2) if k < 0.5 else lerp(x1, x0 - 80, (k - 0.5) * 2)
            yy = y + (0 if k < 0.5 else (k - 0.5) * 120 * (1 if i % 2 else -1))
            aa = a2 * (1 - max(0, k - 0.75) * 4)
            rrect(ctx, x - 110, yy - 34, 220, 62, 24, (236, 234, 226), None, a=aa)
            draw_text(ctx, "you ok?", x, yy + 11, 42, (40, 40, 46), aa)
    cap(ctx, "C9", y=190)
    cap(ctx, "C10", y=990)
    hud(ctx, t)


INSTEAD = ["Pick one person.", "Say one true sentence.", "Let them help."]


def i1(ctx, t):
    a = fade(t, EVENTS["card"], 124.0, 0.3, 0.3)
    rrect(ctx, W / 2 - 460, 280, 920, 480, 22, (236, 232, 214), LINE, 5, a=a)
    draw_text(ctx, "INSTEAD OF \"FINE\":", W / 2 - 400, 380, 64, (40, 40, 46), a, align="left", face="LuckiestGuy-Regular.ttf")
    for i, s in enumerate(INSTEAD):
        k = ease(prog(t, EVENTS["card"] + 0.4 + i * 0.6, EVENTS["card"] + 0.8 + i * 0.6))
        y = 480 + i * 90
        rrect(ctx, W / 2 - 400, y - 40, 44, 44, 6, None, (40, 40, 46), 4, a=a * k)
        draw_text(ctx, s, W / 2 - 330, y, 48, (40, 40, 46), a * k, align="left")
    hud(ctx, t)


# ---- the final fight -----------------------------------------------------------------------------
def f1(ctx, t):
    o0, o1 = EVENTS["offer"]
    offer = ease(prog(t, o0, o1)) * (1 - ease(prog(t, EVENTS["drop"], EVENTS["drop"] + 0.3)))
    vis = ease(prog(t, 124.4, 125.4)) * (1 - ease(prog(t, EVENTS["drop"], EVENTS["drop"] + 1.0)))
    answer = t >= EVENTS["answer"]
    with Camera(lerp(1.6, 1.85, ease(prog(t, 126, 130))), 1080, 500, shake=1.5 * prog(t, 127.6, 129.2) * (t < 130.2)).apply(ctx):
        hallway(ctx, t, morning=1.0)
        hook(ctx, mask_on_hook=False)
        hip, feet = standing(1000, FY, 1)
        ear = None
        if answer:
            J0 = HIM.joints(hip, 1, 0.06)
            ear = (J0["head"][0] - 34, J0["head"][1] + 4)
            J0 = HIM.joints(hip, 1, 0.06, hands={"far": ear})
            hp = J0["limbs"]["arm_far"][2]
            P.phone_side(ctx, hp[0], hp[1], on=0.6, angle=-80)
        else:
            P.phone_side(ctx, 1250, 404, on=0.8 if int(t * 6) % 2 else 0.4)
        geo = P.villain(ctx, 1230, FY, scale=0.95, alpha=vis, grin=1.0, lean=-0.3,
                        reach=(lerp(1150, 1064, offer), lerp(630, 522, offer)))
        J = HIM.draw(ctx, hip, 1, lean=0.06, feet=feet, expr="worried" if t < EVENTS["drop"] else "hopeful",
                     look=(1, 0.1), hands={"far": ear} if ear else None, mouth_open=talk("him", t))
        if vis > 0 and geo:
            hp = geo["hands"][0]
            if t < EVENTS["drop"]:
                mask(ctx, hp[0] - 26, hp[1], 0.95, -1, a=vis)
            else:
                dk = prog(t, EVENTS["drop"], EVENTS["drop"] + 0.6)
                mask(ctx, hp[0] - 26, hp[1] + 230 * dk * dk, 0.95, -1, a=vis * (1 - dk), rot=60 * dk)
        speech(ctx, t, "mum", J["head"][0] - 120, J["head"][1] - 110)
        speech(ctx, t, "him", J["head"][0] + 30, J["head"][1] - 90, size=30)
    label(ctx, "MONDAY")
    vline(ctx, "V9", 560, 330, 60)
    hud(ctx, t)


# ---- payoff, viewer, mirror, title ------------------------------------------------------------------
def p1(ctx, t):
    laugh = ease(prog(t, EVENTS["laugh"] - 0.3, EVENTS["laugh"])) * (1 - prog(t, 143.0, 144.0))
    with Camera(1.6, 1040, 520).apply(ctx):
        pitch(ctx, t, warm=1.0)
        ball(ctx, 1080 + 20 * math.sin(t * 2))
        Jj = stand(JO, ctx, 1220, f=-1, lean=0.04 - 0.05 * laugh, expr="happy" if laugh > 0.3 else "smile", look=(-1, 0.1),
                   mouth_open=talk("jo", t) + 0.4 * laugh * abs(math.sin(t * 9)))
        J = stand(HIM, ctx, 920, f=1, lean=0.04 - 0.05 * laugh, expr="happy" if laugh > 0.3 else "smile", look=(1, 0.0),
                  mouth_open=talk("him", t) + 0.4 * laugh * abs(math.sin(t * 9 + 1)))
        speech(ctx, t, "jo", Jj["head"][0] - 20, Jj["head"][1] - 76)
        speech(ctx, t, "him", J["head"][0] + 40, J["head"][1] - 80)
    label(ctx, "NOVEMBER")
    cap(ctx, "C11", y=925)
    cap(ctx, "C12", y=995)
    hud(ctx, t)


def vt(ctx, t):
    a = fade(t, 144.2, 150.5, 0.6, 0.6)
    br = ease(prog(t, EVENTS["viewer_crack"], EVENTS["viewer_crack"] + 1.6))
    crack = 2.0 * ease(prog(t, EVENTS["viewer_crack"] - 0.8, EVENTS["viewer_crack"] + 0.4))
    glow(ctx, W / 2, 560, 420, GOLD, 0.45 * br * a)
    mask(ctx, W / 2, 560, 5.2, 1, a=a * (1 - br), crack=crack, glowk=crack * 0.4)
    if br > 0:
        for i in range(12):
            ang = i * math.pi / 6
            d0, d1 = 160 + 90 * br, 240 + 160 * br
            ctx.c.drawLine(W / 2 + math.cos(ang) * d0, 560 + math.sin(ang) * d0, W / 2 + math.cos(ang) * d1, 560 + math.sin(ang) * d1,
                           stroke(GOLD, 5, a * br * 0.8))
    cap(ctx, "V1", y=200, size=56)
    cap(ctx, "V2", y=200, size=56)


def x1(ctx, t):
    if t < 153.5:
        lt = max(0.0, t - EVENTS["walk_past"])
        pull = ease(prog(t, 151.2, 152.4))
        with Camera(lerp(3.2, 1.7, pull), lerp(HOOK[0], 1130, pull), lerp(500, 520, pull)).apply(ctx):
            hallway(ctx, t, morning=1.0, open_k=ease(prog(t, 152.6, 153.3)))
            hook(ctx, mask_on_hook=True, mended=1.0)
            x, ph = walk_x(940, lt, 150)
            hip, feet = standing(min(x, 1290), FY, 1, step=ph if x < 1290 else 0.0)
            HIM.draw(ctx, hip, 1, lean=0.04, feet=feet, expr="smile", look=(1, 0.0))
        return
    shop_mask = ease(prog(t, EVENTS["shop_mask"], EVENTS["shop_mask"] + 0.4))
    cr = ease(prog(t, EVENTS["shop_crack"], EVENTS["shop_crack"] + 0.6))
    with Camera(1.7, 1080, 520).apply(ctx):
        shop(ctx)
        Js = shopkeeper(ctx, t, lean=0.02 + 0.06 * cr, expr="hopeful" if cr > 0.3 else "smile", look=(-1, 0.1) if cr < 0.3 else (-1, 0.5))
        if shop_mask > 0:
            face_mask(ctx, Js, a=shop_mask * 0.85 * (1 - ease(prog(t, 160.2, 160.9))), crack=1.6 * cr, glowk=0.9 * cr)
        counter(ctx)
        J = stand(HIM, ctx, 900, f=1, lean=0.04, expr="smile" if t < 158.4 else "hopeful", look=(1, 0.0), mouth_open=talk("him", t))
        speech(ctx, t, "shop", Js["head"][0] - 40, Js["head"][1] - 76)
        speech(ctx, t, "him", J["head"][0] + 80, J["head"][1] - 76)


def title(ctx, t):
    a = fade(t, EVENTS["title"], 170.0, 0.8, 0.6)
    draw_text(ctx, "FINE.", W / 2, 520, 220, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 250 + 500 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=48)
    cap(ctx, "T2", y=770, size=72, rgb=GOLD, glow_rgb=(170, 110, 20))


def helpline(ctx, t):
    cap(ctx, "H1", y=500, size=46)
    cap(ctx, "H2", y=580, size=40, rgb=(190, 190, 196))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "S02": s02, "B1": b1, "G1": g1, "G2": g2, "G3": g3, "R1": r1,
    "T1": t1, "T2": t2, "T3": t3, "L1": l1, "I1": i1, "F1": f1, "P1": p1, "VT": vt, "X1": x1, "TT": title, "HL": helpline,
}
CONTINUOUS = {"G1", "HL"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1_, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "HL":
        black(ctx, prog(t, DURATION - 0.8, DURATION))
