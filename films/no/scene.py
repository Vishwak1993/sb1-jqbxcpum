"""NO.: picture. scene(ctx) draws any frame of the film.

The device: every yes ties a red string to him. The villain holds them all, hidden in the dark,
until the turn. The SAID YES counter ticks with every string.
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
from studio.character import Character, HEAD_R, UPPER_ARM, FORE_ARM, standing, seated, walk_x  # noqa: E402
from studio import props as P  # noqa: E402
from timeline import SCENES, CAPS, CUES, BUBBLES, EVENTS, DURATION, scene_at, yes_at, yes_changed  # noqa: E402
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
STRING = (214, 52, 52)
PAPER = (222, 218, 206)
SCARF = (86, 150, 140)
TIE = (60, 74, 110)


# ---- cast: one defining detail each ------------------------------------------------
def glasses(ctx, hx, hy, f, s):
    fx = hx + f * 14 * s
    for side in (-1, 1):
        ctx.c.drawCircle(fx + side * 13 * s, hy - 2 * s, 9 * s, stroke(LINE, 3 * s))
    ctx.c.drawLine(fx - 4 * s, hy - 3 * s, fx + 4 * s, hy - 3 * s, stroke(LINE, 3 * s))


def flat_cap(ctx, hx, hy, f, s):
    p = poly_path([(hx - 52 * s, hy - 18 * s), (hx - 40 * s, hy - 50 * s), (hx + 20 * s, hy - 56 * s),
                   (hx + 50 * s, hy - 30 * s), (hx + f * 74 * s, hy - 20 * s), (hx + 46 * s, hy - 16 * s)], smooth=True)
    ctx.c.drawPath(p, fill((96, 84, 72)))
    ctx.c.drawPath(p, stroke(LINE, 3 * s))


HIM = Character("him")
DAN = Character("dan", extra=glasses)
BOSS = Character("boss")
ANA = Character("ana")
NEIGH = Character("neigh", extra=flat_cap)


def grey(name, scale=1.0):
    return Character(name, skin=(150, 150, 156), scale=scale)


def tie(ctx, J, s=1.0):
    sx, sy = J["shoulder"]
    f = J["facing"]
    x = sx + f * 10 * s
    p = poly_path([(x - 6 * s, sy + 2 * s), (x + 6 * s, sy + 2 * s), (x + 9 * s, sy + 62 * s), (x, sy + 74 * s),
                   (x - 9 * s, sy + 62 * s)])
    ctx.c.drawPath(p, fill(TIE))
    ctx.c.drawPath(p, stroke(LINE, 2.5 * s))


def scarf(ctx, J, s=1.0):
    sx, sy = J["shoulder"]
    f = J["facing"]
    wline(ctx, (sx - 22 * s, sy - 4 * s), (sx + 22 * s, sy - 4 * s), "scarf", SCARF, 16 * s, seg=2)
    wline(ctx, (sx + f * 10 * s, sy - 2 * s), (sx + f * 18 * s, sy + 46 * s), "scarf2", SCARF, 13 * s, seg=2)


# ---- shared helpers -----------------------------------------------------------------
def cap(ctx, k, y=190, size=50, rgb=TEXT, glow_rgb=None):
    t0, t1 = CAPS[k]
    caption(ctx, CAPTIONS[k], t0, t1, y=y, size=size, rgb=rgb, glow_rgb=glow_rgb)


def vline(ctx, k, x, y, size=48):
    t0 = CUES[k]
    villain_text(ctx, VILLAIN[k], t0 - 0.05, t0 + LEN.get(k, 1.6) + 0.5, x, y, size)


def week(ctx, s):
    draw_text(ctx, s, 60, LETTERBOX + 170, 38, (190, 190, 196), align="left")


def pop_at(t, t0, dur=0.35):
    if t0 is None:
        return 0.0
    return prog(t, t0, t0 + dur) if t0 <= t <= t0 + dur else 0.0


def hud(ctx, t, a=1.0):
    P.hud(ctx, yes_at(t), label="SAID YES", a=a, pop=pop_at(t, yes_changed(t)))


def hud_no(ctx, t, a=1.0):
    k = EVENTS["said_no"]
    if t < k:
        return
    P.hud(ctx, 1, label="SAID NO", a=a * ease(prog(t, k, k + 0.3)), rgb=GOLD, pop=pop_at(t, k, 0.4), x=56 + 268 + 18)


def bubble_on(who, t):
    for b in BUBBLES:
        if b[2] == who and b[0] - 0.05 <= t <= b[1] + 0.3:
            return b
    return None


def speech(ctx, t, who, x, y, size=32, tail=0.0, light=None):
    """A speech bubble above (x, y): pops in, fades out. His bubbles are light, everyone else's dark."""
    b = bubble_on(who, t)
    if b is None:
        return
    t0, t1, _, text = b
    a = fade(t, t0, t1, 0.15, 0.25)
    if a <= 0:
        return
    k = ease_out_back(prog(t, t0, t0 + 0.22))
    light = who.startswith("him") if light is None else light
    tw = text_width(text, size)
    bw, bh = tw + 44, size * 1.25 + 22
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.scale(0.6 + 0.4 * k, 0.6 + 0.4 * k)
    bg, fg, edge = ((236, 234, 226), (30, 28, 32), (120, 118, 112)) if light else ((38, 38, 46), TEXT, (92, 92, 104))
    tx = tail * bw * 0.3
    c.drawPath(poly_path([(tx - 12, -6), (tx + 12, -6), (tx + 2 + tail * 18, 18)]), fill(bg, a))
    rrect(ctx, -bw / 2, -bh, bw, bh, min(26, bh / 2), bg, edge, 2.5, a=a)
    draw_text(ctx, text, 0, -bh / 2 + size * 0.36, size, fg, a)
    c.restore()


def sweat(ctx, J, s=1.0, a=1.0):
    hx, hy = J["head"]
    f = J["facing"]
    x, y, d = hx - f * 30 * s, hy - 26 * s, 6 * s
    drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
    ctx.c.drawPath(drop, fill((200, 225, 255), 0.9 * a))
    ctx.c.drawPath(drop, stroke((90, 120, 170), 2 * s, a))


# ---- the device: strings ------------------------------------------------------------
def anchors(J, s=1.0):
    """(point, layer, which way its top leans) for each string, in the order they get added.
    Front strings (his near hand, his head) are drawn over him, the rest behind him."""
    L = J["limbs"]
    hx, hy = J["head"]
    f = J["facing"]
    return [(L["arm_near"][2], "front", f * 0.6), ((hx, hy - HEAD_R * s), "front", 0.0), (L["arm_far"][2], "back", -f * 0.6),
            (L["leg_near"][1], "back", f * 1.0), (L["leg_far"][1], "back", -f * 1.0), (L["arm_near"][1], "back", f * 1.4),
            (L["arm_far"][1], "back", -f * 1.4), (J["shoulder"], "back", -f * 1.8), ((hx - f * 34 * s, hy - 30 * s), "back", -f * 0.9),
            (J["hip"], "back", f * 2.0)]


def string_points(J, n, s=1.0):
    A = anchors(J, s)
    out = []
    for i in range(n):
        p, layer, bias = A[i % len(A)]
        k = i // len(A)
        out.append(((p[0] + (k % 2 * 2 - 1) * 5 * k * s, p[1] + 3 * k * s), layer, bias, k))
    return out


def string_tops(J, n, spread=1.0, top=-500):
    return [(p[0] + bias * 220 * spread + (hrand("sx", i) - 0.5) * (120 + 90 * k) * spread, top)
            for i, (p, layer, bias, k) in enumerate(string_points(J, n))]


def draw_strings(ctx, J, n, tops=None, t_new=None, slack=0.0, a=1.0, s=1.0, tremble=0.0, skip=(), layer=None, spread=1.0):
    """n red strings from his body up to tops (default: off the top of the frame)."""
    if n <= 0 or a <= 0:
        return
    pts = string_points(J, n, s)
    if tops is None:
        tops = string_tops(J, n, spread)
    for i, (p, lay, bias, k) in enumerate(pts):
        if i in skip or (layer is not None and lay != layer):
            continue
        top = tops[i % len(tops)]
        end = p
        if t_new is not None and i == n - 1:
            kk = ease(prog(ctx.t, t_new, t_new + 0.3))
            if kk <= 0:
                continue
            end = lerp2(top, p, kk)
        sway = math.sin(ctx.t * 1.3 + i * 1.7) * 5 + tremble * math.sin(ctx.t * 60 + i) * 3
        mid = ((top[0] + end[0]) / 2 + sway, (top[1] + end[1]) / 2 + slack * 90)
        path = poly_path([top, mid, end], closed=False, smooth=True)
        la = a * (0.7 if lay == "back" else 1.0)
        ctx.c.drawPath(path, blurred(stroke(STRING, 7, 0.22 * la), 4))
        ctx.c.drawPath(path, stroke(STRING, 2.6, 0.85 * la))
        ctx.c.drawCircle(end[0], end[1], 4, fill(STRING, a))  # the knot


def free_hands(ch, hip, f, lean, hands, head_tilt=0.0):
    """Hands that hold nothing fixed (or carry the prop with them) stay within arm's reach."""
    if not hands:
        return hands
    s = ch.scale
    sh = ch.joints(hip, f, lean, head_tilt)["shoulder"]
    base = {"near": (sh[0] + f * 4 * s, sh[1] + 6 * s), "far": (sh[0] - f * 4 * s, sh[1] + 6 * s)}
    L = (UPPER_ARM + FORE_ARM - 4) * s
    out = {}
    for k, p in hands.items():
        b = base[k]
        d = math.hypot(p[0] - b[0], p[1] - b[1])
        out[k] = p if d <= L else (b[0] + (p[0] - b[0]) * L / d, b[1] + (p[1] - b[1]) * L / d)
    return out


def lift(feet, dy):
    """The strings jerk him up: feet leave the floor with the hip."""
    return {k: (v[0], v[1] + dy) for k, v in feet.items()}


def puppet(ctx, hip, f=1, n=None, tops=None, t_new="auto", slack=0.0, tremble=0.0, skip=(), spread=1.0, sa=1.0, free=False, **kw):
    """Draw him with his strings: back strings, him, front strings. Returns his joints."""
    t = ctx.t
    if free:
        kw["hands"] = free_hands(HIM, hip, f, kw.get("lean", 0.0), kw.get("hands"), kw.get("head_tilt", 0.0))
    n = visible_strings(t) if n is None else n
    t_new = new_string_t(t) if t_new == "auto" else t_new
    J0 = HIM.joints(hip, f, kw.get("lean", 0.0), kw.get("head_tilt", 0.0), kw.get("hands"), kw.get("feet"), kw.get("bend"))
    sk = dict(tops=tops, t_new=t_new, slack=slack, a=sa, tremble=tremble, skip=skip, spread=spread)
    draw_strings(ctx, J0, n, layer="back", **sk)
    J = HIM.draw(ctx, hip, f, **kw)
    draw_strings(ctx, J, n, layer="front", **sk)
    return J


def stand_p(ctx, x, f=1, step=0.0, **kw):
    hip, feet = standing(x, FY, f, step=step)
    return puppet(ctx, hip, f, feet=feet, **kw)


def sit_p(ctx, x, f=1, seat_y=690, **kw):
    hip, feet = seated(x, seat_y, f)
    return puppet(ctx, hip, f, feet=feet, **kw)


def visible_strings(t, cap_n=14):
    return min(yes_at(t), cap_n)


def new_string_t(t):
    tc = yes_changed(t)
    return tc if tc is not None and t - tc < 0.4 else None


def puppeteer(ctx, x, scale, alpha=1.0, body=1.0, grin=1.0, lean=0.0, up=0.55, bar_dx=0.0, bar_tilt=0.0,
              crack=0.0, eyes=1.0, n=10):
    """The villain as a puppeteer standing behind him, holding a control bar. Returns the string tops."""
    if alpha <= 0:
        return None
    info = P.villain(ctx, x, FY, scale=scale, alpha=alpha * body, grin=grin, lean=lean, arms_up=up, crack=crack)
    (l, r) = info["hands"]
    cx, cy = (l[0] + r[0]) / 2 + bar_dx, (l[1] + r[1]) / 2
    half = (r[0] - l[0]) / 2 + 40 * scale
    ang = bar_tilt
    p0 = (cx - half * math.cos(ang), cy - half * math.sin(ang))
    p1 = (cx + half * math.cos(ang), cy + half * math.sin(ang))
    a = alpha * body
    if a > 0.01:
        ctx.c.drawLine(*p0, *p1, blurred(stroke(RED, 22 * scale, 0.5 * a), 8))
        ctx.c.drawLine(*p0, *p1, stroke((22, 10, 11), 14 * scale, a))
        for hp in (p0, p1):
            ctx.c.drawCircle(hp[0], hp[1], 16 * scale, fill((22, 10, 11), a))
            ctx.c.drawCircle(hp[0], hp[1], 16 * scale, stroke(RED, 3 * scale, 0.8 * a))
    if eyes > 0 and body < 1:  # in the dark, only the eyes and the grin show
        hx, hy = info["head"]
        s = scale
        glow(ctx, hx, hy, 140 * s, RED, 0.25 * eyes * alpha)
        for side in (-1, 1):
            ex, ey = hx + side * 22 * s, hy - 8 * s
            ctx.c.drawPath(poly_path([(ex - 12 * s, ey + 2 * s), (ex, ey - 4 * s), (ex + 12 * s, ey + 2 * s)], False, True),
                           stroke(RED, 5 * s, eyes * alpha))
        if grin > 0:
            ctx.c.drawPath(poly_path([(hx - 24 * s, hy + 18 * s), (hx, hy + (18 + 12 * grin) * s), (hx + 24 * s, hy + 18 * s)],
                                     False, True), stroke(RED, 4.5 * s, eyes * alpha))
    return [lerp2(p0, p1, (i % n) / max(1, n - 1)) for i in range(max(n, 1))]


def fog(ctx, y, a):
    """Darkness above the strings: hides who holds them."""
    if a <= 0:
        return
    ctx.c.drawRect(skia.Rect.MakeLTRB(-800, -800, W + 800, y), fill((6, 6, 8), a))
    sh = skia.GradientShader.MakeLinear([(0, y), (0, y + 220)], [col((6, 6, 8), a), col((6, 6, 8), 0)])
    ctx.c.drawRect(skia.Rect.MakeLTRB(-800, y, W + 800, y + 220), skia.Paint(Shader=sh))


# ---- props for this film ------------------------------------------------------------
def door(ctx, x, w=170, h=380, open_k=0.0, key="door", light=0.0):
    wrect(ctx, x - 12, FY - h - 12, w + 24, h + 12, (key, "fr"), (40, 40, 46), LINE, 3, seg=2)
    if light > 0:
        ctx.c.drawRect(skia.Rect.MakeXYWH(x, FY - h, w, h), fill((210, 200, 180), 0.25 * light))
    dw = w * (1 - 0.8 * open_k)
    wrect(ctx, x, FY - h, dw, h, (key, "d"), (74, 66, 60), LINE, 3, seg=2)
    wcircle(ctx, x + dw - 22, FY - h / 2, 7, (key, "k"), (170, 160, 130), LINE, 2)


def box(ctx, x, y, w=120, h=90, key="box"):
    wrect(ctx, x - w / 2, y - h, w, h, key, (150, 118, 82), LINE, 3, seg=2)
    wline(ctx, (x - w / 2, y - h + 18), (x + w / 2, y - h + 18), (key, "t"), (120, 92, 62), 3, seg=2)


def dog(ctx, x, y, f=1, key="dog", rgb=(150, 128, 104), s=1.0, sit=False, walk=0.0):
    """A small dog standing on y. Returns the collar point."""
    c = ctx.c
    by = y - 52 * s if not sit else y - 44 * s
    for i, lx in enumerate((-30, -18, 18, 30)):
        ph = math.sin(walk * 2 * math.pi + i * math.pi / 2) * 8 * s if walk else 0
        wline(ctx, (x + lx * s * f, by + 10 * s), (x + lx * s * f + ph, y), (key, "leg", i), LINE, 9 * s, seg=1)
        wline(ctx, (x + lx * s * f, by + 10 * s), (x + lx * s * f + ph, y), (key, "leg2", i), rgb, 5 * s, seg=1)
    wcircle(ctx, x, by, 44 * s, (key, "b"), rgb, LINE, 3, ry=22 * s)
    hx, hy = x + f * 44 * s, by - 26 * s
    wcircle(ctx, hx, hy, 20 * s, (key, "h"), rgb, LINE, 3)
    c.drawPath(poly_path([(hx - f * 6 * s, hy - 14 * s), (hx - f * 16 * s, hy + 4 * s), (hx - f * 2 * s, hy - 2 * s)]),
               fill((110, 92, 76)))
    c.drawCircle(hx + f * 9 * s, hy - 3 * s, 2.6 * s, fill(LINE))
    c.drawCircle(hx + f * 19 * s, hy + 3 * s, 3 * s, fill(LINE))
    wag = math.sin(ctx.t * 14) * 10 * s
    wline(ctx, (x - f * 42 * s, by - 4 * s), (x - f * 60 * s, by - 22 * s + wag), (key, "tail"), rgb, 6 * s, seg=1)
    return (hx - f * 10 * s, hy + 14 * s)


def easel(ctx, x, state="sketch", paint=0.0, sheet=0.0, fallen=0.0, key="easel"):
    """Easel with his canvas. state: sketch | painted. fallen: 0 standing .. 1 lying on the floor."""
    c = ctx.c
    c.save()
    if fallen > 0:
        c.translate(x + 120, FY)
        c.rotate(80 * fallen)
        c.translate(-(x + 120), -FY)
    for (a, b) in (((x - 80, FY), (x - 6, 330)), ((x + 80, FY), (x + 6, 330)), ((x, FY), (x, 340))):
        wline(ctx, a, b, (key, a[0]), (96, 76, 56), 9, seg=2)
    wrect(ctx, x - 110, 624, 220, 12, (key, "ledge"), (110, 88, 64), LINE, 3, seg=2)
    canvas(ctx, x - 110, 372, 220, 252, paint, (key, "cv"))
    if sheet > 0:
        p = [(x - 126, 360), (x + 126, 356), (x + 136, 650), (x + 40, 690), (x - 60, 668), (x - 132, 640)]
        c.drawPath(poly_path(wobble_points(ctx, p, (key, "sheet"), 1.5), smooth=True), fill((112, 112, 118), sheet))
        c.drawPath(poly_path(wobble_points(ctx, p, (key, "sheet"), 1.5), smooth=True), stroke(LINE, 3, sheet))
    c.restore()
    return (x - 100, 618)  # where the brush rests


def canvas(ctx, x, y, w, h, paint=0.0, key="cv"):
    """His painting: a pencil sunrise that fills with the film's first colour as paint goes 0..1."""
    c = ctx.c
    wrect(ctx, x, y, w, h, key, PAPER, LINE, 3, seg=2)
    hy = y + h * 0.62
    sun = (x + w * 0.5, hy)
    if paint > 0:
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(x + 4, y + 4, w - 8, h - 8))
        k = ease(prog(paint, 0.0, 0.5))
        sky = skia.GradientShader.MakeLinear([(0, y), (0, hy)], [col((120, 96, 150), k), col((250, 150, 110), k), col(GOLD, k)],
                                             [0, 0.6, 1])
        c.drawRect(skia.Rect.MakeLTRB(x, y, x + w, hy), skia.Paint(Shader=sky))
        k2 = ease(prog(paint, 0.3, 0.8))
        c.drawRect(skia.Rect.MakeLTRB(x, hy, x + w, y + h), fill((60, 74, 110), k2))
        for i in range(5):
            yy = hy + 14 + i * 16
            c.drawLine(x + 20 + i * 8, yy, x + w - 30 - i * 12, yy, stroke((250, 190, 120), 3, 0.7 * k2))
        k3 = ease(prog(paint, 0.5, 1.0))
        glow(ctx, sun[0], sun[1], 120, GOLD, 0.6 * k3)
        c.drawCircle(sun[0], sun[1], 38, fill((255, 214, 120), k3))
        c.restore()
    a = 1 - ease(prog(paint, 0.0, 0.4))
    if a > 0:  # the pencil sketch underneath
        c.drawLine(x + 16, hy, x + w - 16, hy, stroke((120, 116, 108), 2.5, a))
        c.drawPath(poly_path(circle_pts(sun[0], sun[1], 38, 38, 20)[:11], closed=False, smooth=True), stroke((120, 116, 108), 2.5, a))
        for i in range(4):
            ang = math.pi + (i + 1) * math.pi / 5
            c.drawLine(sun[0] + math.cos(ang) * 52, sun[1] + math.sin(ang) * 52, sun[0] + math.cos(ang) * 80,
                       sun[1] + math.sin(ang) * 80, stroke((120, 116, 108), 2.5, a))


CAL = (540, 410, 1.3)  # calendar position and scale on his wall
DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
WEEK_START = ["work", "Ben", "work late", "Mia", "party", "ME", "Leo"]


def calendar(ctx, x, y, names, me_k=0.0, strike=0.0, gold_me=0.0, scale=1.0, me_alpha=1.0):
    """Wall calendar, one week. names: 7 strings. Saturday (index 5) is his day."""
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    bw, bh = 66, 84
    wrect(ctx, -10, -40, bw * 7 + 20, bh + 56, "calp", (200, 196, 186), LINE, 3, seg=3)
    draw_text(ctx, "THIS WEEK", bw * 3.5, -14, 20, (90, 86, 80))
    for i in range(7):
        bx = i * bw
        wrect(ctx, bx, 0, bw, bh, ("calb", i), (226, 222, 212), (120, 116, 108), 2, seg=1)
        draw_text(ctx, DAYS[i], bx + bw / 2, 18, 15, (110, 106, 100))
        n = names[i]
        if i == 5 and n == "ME":
            continue
        draw_text(ctx, n, bx + bw / 2, 56, 18 if len(n) < 6 else 14, (50, 48, 56))
    sx = 5 * bw + bw / 2
    if names[5] == "ME" or strike > 0:
        rgb = GOLD if gold_me > 0 else (40, 40, 48)
        draw_text(ctx, "ME", sx, 60, 30, rgb, me_alpha if gold_me <= 0 else gold_me, face="LuckiestGuy-Regular.ttf",
                  glow_rgb=GOLD if gold_me > 0.5 else None)
        ring = me_k if gold_me <= 0 else ease(prog(gold_me, 0.4, 1.0))
        if ring > 0:
            pts = [(sx + math.cos(a) * 28, 50 + math.sin(a) * 26) for a in [i * 2 * math.pi / 20 for i in range(int(21 * ring))]]
            if len(pts) > 1:
                c.drawPath(poly_path(wobble_points(ctx, pts, "ring", 1.2), closed=False, smooth=True),
                           stroke(GOLD if gold_me > 0 else RED, 3))
    if strike > 0:
        k = ease(prog(strike, 0, 0.5))
        c.drawLine(sx - 26, 52, sx - 26 + 52 * k, 52, stroke(LINE, 4))
        k2 = ease(prog(strike, 0.5, 1.0))
        if k2 > 0:
            draw_text(ctx, "Dan", sx, 78, 18, (50, 48, 56), k2)
    c.restore()


def phone_close(ctx, t, sender, msgs, t0, glow_rgb=BLUE, stack_dt=None):
    UI = P.PhoneUI(W / 2, 590, 560, 880)
    UI.body(ctx, 1.0, glow_rgb)
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, 130), fill((26, 28, 36)))
        wcircle(ctx, x0 + 60, y0 + 84, 26, "av_" + sender, (90, 96, 110), None, 0)
        draw_text(ctx, sender, x0 + 100, y0 + 96, 40, TEXT, align="left")
        y = y0 + 170
        for i, m in enumerate(msgs):
            ti = t0 + (i * stack_dt if stack_dt else 0)
            a = ease(prog(t, ti, ti + 0.2))
            if a <= 0:
                break
            h = P.bubble(ctx, x0 + 26, y, m, False, 40, a, maxw=460)
            y += h + 14
    return UI


# ---- sets ------------------------------------------------------------------------------
def home(ctx, t, easel_kw=None, cal_names=None, cal_kw=None, night=True, window_gold=0.0, door_kw=None, lamp=1.0):
    P.back_wall(ctx)
    P.floor(ctx, FY)
    P.window(ctx, 1500, 210, 230, 230, "hwin", night=night, sky=mix((26, 30, 44) if night else (84, 96, 118), (150, 120, 80), window_gold), moon=night)
    if window_gold > 0:
        glow(ctx, 1615, 325, 520, GOLD, 0.35 * window_gold)
        cone(ctx, (1600, 330), (1150, FY), (1700, FY), GOLD, 0.12 * window_gold)
    door(ctx, 190, **(door_kw or {}))
    if lamp > 0:
        P.wrect(ctx, 450, FY - 260, 8, 260, "lamp", GREY_D, LINE, 2, seg=2)
        wrect(ctx, 420, FY - 300, 68, 44, "shade", (150, 140, 120), LINE, 3, seg=2)
        glow(ctx, 454, FY - 270, 300, (255, 210, 150), 0.16 * lamp)
    calendar(ctx, CAL[0], CAL[1], cal_names or WEEK_START, scale=CAL[2], **(cal_kw or {}))
    P.wrect(ctx, 1060, 690, 120, 90, "stool", GREY_D, LINE, 3, seg=2)
    return easel(ctx, 1330, **(easel_kw or {}))


def office(ctx, desk_x=700, night=False):
    P.back_wall(ctx, rgb=(26, 27, 31))
    P.floor(ctx, FY)
    P.window(ctx, 1380, 190, 300, 210, "owin", night=night, moon=False, sky=(40, 46, 58) if not night else (20, 22, 32))
    for i in range(3):
        ctx.c.drawRect(skia.Rect.MakeXYWH(1400 + i * 90, 300 - i * 20, 50, 100 + i * 20), fill((30, 34, 44)))
    P.wall_clock(ctx, 1110, 240, 18, 10, key="oclock")
    P.table(ctx, desk_x, 640, 420, key="odesk")
    P.desk_computer(ctx, desk_x + 260, 640, key="opc")


def street(ctx, t, rain=0.0, lamps=(400, 1500)):
    for i in range(16):
        bx = -200 + i * 150
        bh = 200 + hrand("bld", i) * 260
        ctx.c.drawRect(skia.Rect.MakeXYWH(bx, FY - bh - 60, 140, bh), fill((24, 24, 30)))
        for j in range(int(bh // 60)):
            if hrand("bw", i, j) > 0.55:
                ctx.c.drawRect(skia.Rect.MakeXYWH(bx + 20 + (j % 2) * 60, FY - bh - 40 + j * 55, 26, 20), fill((70, 70, 60), 0.5))
    for lx in lamps:
        P.wrect(ctx, lx, FY - 380, 10, 380, ("lamp", lx), GREY_D, LINE, 2, seg=2)
        glow(ctx, lx + 5, FY - 380, 260, (255, 210, 140), 0.18)
        cone(ctx, (lx + 5, FY - 380), (lx - 140, FY), (lx + 150, FY), (255, 210, 140), 0.10)
    P.floor(ctx, FY)
    if rain > 0:
        for i in range(160):
            rx = -300 + hrand("rr", i) * 2500
            ph = (ctx.t * 2.0 + hrand("rp", i)) % 1.0
            ry = -200 + ph * 1100
            ctx.c.drawLine(rx, ry, rx - 6, ry + 26, stroke((150, 160, 190), 1.6, 0.45 * rain))


def stand(ch, ctx, x, f=1, lean=0.04, expr="neutral", look=(0, 0), hands=None, step=0.0, s=1.0, **kw):
    hip, feet = standing(x, FY, f, s, step=step)
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, hands=hands, expr=expr, look=look, **kw)


def sit(ch, ctx, x, seat_y=690, f=1, lean=0.2, expr="neutral", look=(0, 0), hands=None, **kw):
    hip, feet = seated(x, seat_y, f)
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, hands=hands, expr=expr, look=look, **kw)


def him_joints(x, f=1, lean=0.04, step=0.0, hands=None):
    hip, feet = standing(x, FY, f, step=step)
    return HIM.joints(hip, f, lean, 0, hands, feet)




# ---- the hook ---------------------------------------------------------------------------
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


def talk(t, who, dur=0.45):
    """Mouth open while his own bubble pops in."""
    b = bubble_on(who, t)
    return 0.5 * abs(math.sin(t * 16)) if b and b[0] <= t <= b[0] + dur else 0.0


def h1(ctx, t):
    with Camera(1.75, 1050, 560).apply(ctx):
        office(ctx, desk_x=840)
        P.chair(ctx, 800, 690, 1, key="hc")
        JB = stand(BOSS, ctx, 1310, f=-1, lean=0.24, expr="neutral", look=(-1, 0.6),
                   hands={"near": (1236, 634), "far": (1272, 676)})
        tie(ctx, JB)
        J = sit_p(ctx, 800, f=1, lean=0.2, expr="happy" if t > 4.1 else "neutral", look=(1, -0.6),
                  hands={"near": (905, 634), "far": (888, 638)}, mouth_open=talk(t, "him"))
        speech(ctx, t, "boss", JB["head"][0] - 30, JB["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 10, J["head"][1] - 70)
    hud(ctx, t)


def h2(ctx, t):
    took = t > 7.2
    with Camera(1.85, 1060, 560).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        door(ctx, 740, open_k=1.0, light=1.0)
        cp = dog(ctx, 1080, FY, f=-1, sit=True)
        JN = stand(NEIGH, ctx, 1260, f=-1, lean=0.08, expr="smile", look=(-1, 0.3),
                   hands={"near": (1170, 640) if not took else (1222, 676)})
        J = stand_p(ctx, 900, f=1, lean=0.06, expr="happy" if t > 6.7 else "neutral", look=(1, 0.2),
                    hands={"near": (990, 640) if took else (924, 676)}, mouth_open=talk(t, "him"), free=True)
        hold = (990, 640) if took else (1170, 640)
        wline(ctx, hold, cp, "leash", (60, 50, 44), 3, seg=3)
        speech(ctx, t, "neighbour", JN["head"][0] - 30, JN["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0], J["head"][1] - 70)
    hud(ctx, t)


def cafe_set(ctx):
    ctx.c.drawRect(skia.Rect.MakeLTRB(-600, 0, W + 600, FY), fill((30, 27, 26)))
    P.wrect(ctx, 620, 170, 720, 300, "cwin", (44, 40, 38), (80, 74, 66), 5, seg=4)
    wline(ctx, (980, 170), (980, 470), "cwv", (80, 74, 66), 5)
    P.floor(ctx, FY, rgb=(80, 70, 60))
    P.table(ctx, 870, 640, 220, key="ctable")
    for i, cx in enumerate((900, 980, 1040)):
        P.wrect(ctx, cx, 606, 30, 34, ("cup", i), (200, 196, 188), LINE, 3, seg=2)


def h3(ctx, t):
    with Camera(1.75, 990, 560).apply(ctx):
        cafe_set(ctx)
        P.chair(ctx, 780, 690, 1, key="cc1")
        P.chair(ctx, 1180, 690, -1, key="cc2")
        sit(grey("f1"), ctx, 780, f=1, lean=0.15, expr="happy", look=(1, 0), hands={"near": (895, 628), "far": (880, 640)})
        JF = stand(grey("f2"), ctx, 990, f=1, lean=0.05, expr="happy", look=(1, -0.2), hands={"near": (1070, 560)})
        J = sit_p(ctx, 1180, f=-1, lean=0.15, expr="happy" if t > 9.3 else "neutral", look=(-1, -0.3),
                  hands={"near": (1080, 626), "far": (1096, 640)}, mouth_open=talk(t, "him"))
        speech(ctx, t, "friend", JF["head"][0], JF["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 20, J["head"][1] - 70)
    hud(ctx, t)


def shop_set(ctx):
    P.back_wall(ctx, rgb=(24, 26, 28))
    for r in range(3):
        y = 300 + r * 120
        wrect(ctx, 400, y, 760, 10, ("shelf", r), GREY, LINE, 2, seg=3)
        for i in range(12):
            hgt = 40 + hrand("item", r, i) * 40
            ctx.c.drawRect(skia.Rect.MakeXYWH(420 + i * 62, y - hgt, 40, hgt), fill((70 + i * 3 % 40, 70, 76)))
    P.floor(ctx, FY)
    wrect(ctx, 1480, 560, 380, 220, "counter", GREY_D, LINE, 3, seg=3)
    wrect(ctx, 1600, 500, 90, 60, "till", GREY, LINE, 3, seg=2)


def h4(ctx, t):
    cut_in = ease(prog(t, 10.85, 11.35))
    with Camera(1.75, 1180, 560).apply(ctx):
        shop_set(ctx)
        stand(grey("q1"), ctx, 1460, f=1, lean=0.04, expr="neutral", look=(1, 0))
        x = lerp(1420, 1210, cut_in)
        J2 = stand(grey("cutter"), ctx, x, f=-1 if t > 11.2 else 1, lean=0.06, expr="smile", look=(-1, 0),
                   step=(t * 2.2) % 1 if cut_in < 1 else 0.0)
        J = stand_p(ctx, 1010, f=1, lean=0.04, expr="happy" if t > 11.9 else "neutral", look=(1, 0),
                    hands={"near": (1050, 652)}, mouth_open=talk(t, "him"))
        P.wrect(ctx, 1030, 652, 60, 46, "basket", (120, 120, 130), LINE, 3, seg=2)
        speech(ctx, t, "stranger", J2["head"][0] + 20, J2["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] - 40, J["head"][1] - 70)
    hud(ctx, t)


def h5(ctx, t):
    with Camera(1.85, 1050, 560).apply(ctx):
        street(ctx, t)
        for i, (bx, by) in enumerate(((1290, FY), (1290, FY - 90), (1400, FY))):
            box(ctx, bx, by, key=("hb", i))
        JD = stand(DAN, ctx, 1160, f=-1, lean=0.06, expr="hopeful", look=(-1, 0), hands={"near": (1104, 600), "far": (1130, 610)})
        box(ctx, 1110, 640, 110, 80, key="dbox")
        J = stand_p(ctx, 900, f=1, lean=0.04, expr="happy" if t > 14.3 else "neutral", look=(1, 0), mouth_open=talk(t, "him"))
        speech(ctx, t, "dan", JD["head"][0], JD["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0], J["head"][1] - 70)
    hud(ctx, t)


FLURRY = [(15.6, "sure!", (34, 36, 44)), (16.1, "happy to!", (40, 34, 34)), (16.6, "of course!", (30, 38, 40)),
          (17.1, "anything!", (38, 36, 30))]


def h6(ctx, t):
    i = min(3, int((t - 15.6) / 0.5))
    t0, word, bg = FLURRY[i]
    ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill(bg))
    side = i % 2 * 2 - 1
    x = 960 - side * 120
    with Camera(2.7, x, 500).apply(ctx):
        stand_p(ctx, x, f=side, lean=0.04, expr="happy", look=(0.5 * side, 0), mouth_open=0.4 + 0.2 * abs(math.sin(t * 14)))
    k = ease_out_back(prog(t, t0, t0 + 0.18))
    draw_text(ctx, word, W / 2 + side * 470, 560, 110 * (0.7 + 0.3 * k), TEXT, 1.0, face="LuckiestGuy-Regular.ttf")
    hud(ctx, t)


# ---- wound and stakes -----------------------------------------------------------------------
BRUSH_REST = (1230, 618)


def brush(ctx, p, ang=-0.6, a=1.0, wet=None):
    q = (p[0] + math.cos(ang) * 46, p[1] + math.sin(ang) * 46)
    ctx.c.drawLine(*p, *q, stroke((120, 90, 60), 6, a))
    ctx.c.drawCircle(q[0], q[1], 5, fill(wet or (60, 56, 52), a))


def s02(ctx, t):
    # walk in, see the calendar and the canvas, reach for the brush, get yanked back, tilt up to the dark
    tilt = ease(prog(t, 23.4, 25.6))
    cx = lerp(lerp(840, 1120, ease(prog(t, 17.6, 21.0))), 1140, tilt)
    cy = lerp(540, 360, tilt)
    z = lerp(1.4, 1.5, tilt)
    shake = 6 * (1 - prog(t, 23.0, 23.4)) if t > 23 else 0
    with Camera(z, cx, cy, shake=shake).apply(ctx):
        home(ctx, t, cal_kw={"me_k": ease(prog(t, 19.4, 20.4))})
        brush(ctx, BRUSH_REST)
        lt = min(t, 20.6) - 17.6
        x, ph = walk_x(560, lt, 196)
        step = ph if t < 20.6 else 0.0
        reach = ease(prog(t, 21.6, 22.8)) * (1 - ease(prog(t, 23.0, 23.25)))
        yanked = ease(prog(t, 23.0, 23.25))
        hip, feet = standing(x, FY, 1, step=step)
        rest = (x + 30, hip[1] + 10)
        hand = lerp2(rest, (BRUSH_REST[0] - 6, BRUSH_REST[1] - 8), reach)
        if yanked > 0:
            hand = lerp2(hand, (x + 30, 470), yanked)
        expr = "tired" if t < 20.4 else ("hopeful" if t < 23.0 else "shocked")
        if t > 24.6:
            expr = "anxious"
        look = (1, 0.6) if t < 23.0 else (0, -1.3)
        if 19.3 < t < 20.4:
            look = (-0.6, -0.8)  # glance at the calendar on the way
        J = puppet(ctx, (hip[0] - 14 * yanked, hip[1]), 1, n=9, lean=0.04 - 0.12 * yanked, feet=feet,
                   hands={"near": hand}, expr=expr, look=look, tremble=yanked * (1 - prog(t, 23.2, 24.0)), free=True)
        fog(ctx, 210, ease(prog(t, 23.3, 23.9)))
        puppeteer(ctx, 1150, 2.0, alpha=ease(prog(t, 23.9, 24.6)), body=0.0, eyes=ease(prog(t, EVENTS["eyes_open"], 24.9)),
                  grin=ease(prog(t, 25.0, 25.6)), n=9)
    cap(ctx, "C2")
    vline(ctx, "V1", 1400, 330)
    hud(ctx, t)


def s03(ctx, t):
    if t < 28.8:
        phone_close(ctx, t, "Dan", ["free saturday? need a favour"], 27.3)
        vline(ctx, "V2", W / 2 + 520, 420, 56)
        hud(ctx, t)
        return
    with Camera(1.8, 900, 480).apply(ctx):
        strike = prog(t, EVENTS["strike"], EVENTS["strike"] + 0.8)
        home(ctx, t, cal_kw={"me_k": 1.0, "strike": strike})
        ph = (1130, 600)
        J = stand_p(ctx, 1190, f=-1, lean=0.04, expr="anxious" if t < 29.4 else "smile", look=(-1, 0.6),
                    hands={"near": ph, "far": (ph[0] + 8, ph[1] + 6)}, mouth_open=talk(t, "him"))
        P.phone_held(ctx, *ph, facing=-1)
        sweat(ctx, J, 1.0, ease(prog(t, 29.0, 29.4)))
        speech(ctx, t, "him", J["head"][0] - 20, J["head"][1] - 70)
    hud(ctx, t)


def s04(ctx, t):
    cap(ctx, "C3", y=H / 2 + 16, size=58)


# ---- the grind -----------------------------------------------------------------------------
def jerk(t, k=1.0):
    """Puppet-like twitch: little upward tugs on the hip."""
    return -abs(math.sin(t * 5.5)) ** 8 * 10 * k


def g1(ctx, t):
    lt = t - 34.6
    with Camera(1.6, 1100, 560).apply(ctx):
        street(ctx, t)
        door(ctx, 1400, open_k=1.0, light=0.8, key="dandoor")
        stand(DAN, ctx, 1620, f=-1, lean=0.04, expr="happy", look=(-1, 0), hands={"near": (1560, 560)})
        x, ph = walk_x(760, lt, 140)
        hip, feet = standing(x, FY, 1, step=ph)
        hip, feet = (hip[0], hip[1] + jerk(t)), lift(feet, jerk(t))
        J = puppet(ctx, hip, 1, lean=0.14, feet=feet, hands={"near": (x + 70, hip[1] - 60), "far": (x + 50, hip[1] - 70)},
                   expr="tired", look=(1, 0))
        box(ctx, x + 72, hip[1] - 14, 130, 120, key="g1box")
    week(ctx, "WEEK 1")
    hud(ctx, t)


def g2(ctx, t):
    with Camera(1.55, 1000, 560).apply(ctx):
        office(ctx, desk_x=560)
        P.chair(ctx, 620, 690, 1, key="g2c")
        P.table(ctx, 1150, 640, 300, key="adesk")
        P.chair(ctx, 1360, 690, -1, key="g2c2")
        JA = sit(ANA, ctx, 1360, f=-1, lean=0.12, expr="hopeful", look=(-1, 0), hands={"near": (1260, 632), "far": (1280, 636)})
        scarf(ctx, JA)
        J = sit_p(ctx, 620, f=1, lean=0.26, expr="tired" if t < 39.2 else "smile", look=(1, 0) if t < 38.6 else (1, -0.2),
                  hands={"near": (730, 634), "far": (714, 638)}, mouth_open=talk(t, "him"))
        speech(ctx, t, "ana", JA["head"][0] - 20, JA["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] + 20, J["head"][1] - 70)
    week(ctx, "WEEK 2")
    hud(ctx, t)


def g3(ctx, t):
    lt = t - 41.2
    with Camera(1.5, 980, 560).apply(ctx):
        street(ctx, t, rain=1.0)
        x = 940 + math.sin(lt * 3.0) * 30
        hip, feet = standing(x, FY, 1, step=(lt * 1.6) % 1)
        hip, feet = (hip[0], hip[1] + jerk(t, 1.2)), lift(feet, jerk(t, 1.2))
        hand = (x + 56, hip[1] - 10)
        for i, (dx, f, rgb) in enumerate(((1240, 1, (150, 128, 104)), (1380, 1, (110, 104, 100)), (640, -1, (170, 160, 140)))):
            cp = dog(ctx, dx + math.sin(lt * 4 + i) * 20, FY, f=f, key=("gd", i), rgb=rgb, s=0.9, walk=lt * 2.5)
            wline(ctx, hand, cp, ("gl", i), (60, 50, 44), 3, seg=2)
        J = puppet(ctx, hip, 1, lean=0.22 + 0.08 * math.sin(lt * 6), feet=feet, hands={"near": hand, "far": (x + 44, hip[1])},
                   expr="worried", look=(1, 0.3))
    vline(ctx, "V3", 1250, 330)
    week(ctx, "WEEK 3")
    hud(ctx, t)


def g4(ctx, t):
    with Camera(1.4, 1000, 560).apply(ctx):
        P.back_wall(ctx, rgb=(26, 22, 30))
        P.floor(ctx, FY)
        for i in range(24):  # fairy lights
            x = 300 + i * 60
            y = 250 + math.sin(i * 0.6) * 18
            glow(ctx, x, y, 24, (255, 210, 150), 0.25 + 0.15 * math.sin(t * 4 + i))
            ctx.c.drawCircle(x, y, 5, fill((240, 220, 180)))
        draw_text(ctx, "PARTY!", 1000, 380, 70, (180, 170, 190), 0.8, face="LuckiestGuy-Regular.ttf")
        P.table(ctx, 1240, 640, 300, key="ptable")
        for i in range(4):
            P.wrect(ctx, 1270 + i * 60, 606, 28, 34, ("pcup", i), (200, 196, 188), LINE, 3, seg=2)
        for i, x in enumerate((480, 640, 800, 960)):
            bob = abs(math.sin(t * 7 + i)) * 14
            f = 1 if i % 2 else -1
            hip, feet = standing(x, FY, f)
            ch = grey(f"d{i}")
            hp = (hip[0], hip[1] - bob)
            ch.draw(ctx, hp, f, lean=0.05, feet=lift(feet, -bob), expr="happy", mouth_open=0.5,
                    hands=free_hands(ch, hp, f, 0.05, {"near": (x + f * 70, hp[1] - 200), "far": (x - f * 64, hp[1] - 150)}))
        pour = math.sin(t * 3)
        J = stand_p(ctx, 1420, f=-1, lean=0.12, expr="tired", look=(-1, 0.4),
                    hands={"near": (1330, 590 + 10 * pour), "far": (1360, 600)})
        P.wrect(ctx, 1318, 560 + 10 * pour, 24, 44, "bottle", (90, 110, 90), LINE, 3, seg=2)
    cap(ctx, "C4")
    week(ctx, "WEEK 5")
    hud(ctx, t)


FULL_WEEK = ["work", "Ben", "Dan", "Mia", "party", "Dan", "Leo"]


def g5(ctx, t):
    lt = t - 47.8
    with Camera(1.35, 940, 540).apply(ctx):
        home(ctx, t, cal_names=FULL_WEEK, easel_kw={"sheet": 1.0})
        x, ph = walk_x(420, lt, 120)
        hip, feet = standing(x, FY, 1, step=ph)
        puppet(ctx, (hip[0], hip[1] + jerk(t)), 1, lean=0.12, feet=lift(feet, jerk(t)), expr="tired", look=(1, 0.3))
    cap(ctx, "C5")
    week(ctx, "WEEK 6")
    hud(ctx, t)


FAVOURS = ["quick favour?", "can you cover friday?", "u free sat?", "need a lift to the airport", "you're the best!!",
           "can you sort the tickets?"]


def g6(ctx, t):
    phone_close(ctx, t, "Messages", FAVOURS, 51.3, stack_dt=0.42)
    vline(ctx, "V4", W / 2 + 520, 420, 56)
    week(ctx, "WEEK 8")
    hud(ctx, t)


def g7(ctx, t):
    with Camera(1.75, 860, 560).apply(ctx):
        P.back_wall(ctx)
        P.floor(ctx, FY)
        P.table(ctx, 700, 640, 380, key="ldesk")
        rrect(ctx, 860, 560, 150, 80, 6, (40, 42, 50), LINE, 3)
        ctx.c.drawRect(skia.Rect.MakeXYWH(868, 568, 134, 64), fill((110, 140, 190)))
        draw_text(ctx, "UPDATING 3%", 935, 606, 18, TEXT)
        glow(ctx, 935, 600, 220, BLUE, 0.2)
        P.digital_clock(ctx, 1040, 600, "1:40", rgb=(190, 190, 196))
        P.chair(ctx, 750, 690, 1, key="lc")
        yawn = 55.6 < t < 56.6
        sit_p(ctx, 750, f=1, lean=0.3, expr="closed" if yawn else "tired", look=(1, 0.5),
              hands={"near": (866, 636), "far": (850, 638)}, mouth_open=0.9 if yawn else 0, screen_glow=0.6)
    cap(ctx, "C6")
    week(ctx, "WEEK 9")
    hud(ctx, t)


def g8(ctx, t):
    lt = t - 58.2
    with Camera(lerp(1.35, 1.6, lt / 5.8), 960, 540).apply(ctx):
        street(ctx, t, rain=1.0, lamps=(700,))
        x, ph = walk_x(800, lt, 60)
        hip, feet = standing(x, FY, 1, step=ph)
        puppet(ctx, (hip[0], hip[1] + jerk(t, 0.6)), 1, lean=0.2, feet=lift(feet, jerk(t, 0.6)), expr="sad", look=(1, 0.8), head_tilt=0.15,
               spread=2.2)
    vline(ctx, "V5", 1260, 330)
    week(ctx, "WEEK 11")
    hud(ctx, t)


# ---- rock bottom ---------------------------------------------------------------------------
def floor_sit(x, f=1, lean=-0.1):
    hip = (x, FY - 22)
    feet = {"near": (x + f * 104, FY), "far": (x + f * 94, FY)}
    return hip, feet, lean


def spill_pool(ctx, k):
    if k > 0:
        ctx.c.drawOval(skia.Rect.MakeLTRB(1380 - 170 * k, FY - 6, 1470 + 170 * k, FY + 10), fill((120, 120, 126), 0.9))
    jx = 1440 + 50 * k
    if k <= 0:
        P.wrect(ctx, jx, FY - 40, 30, 40, "jar", (150, 150, 156), LINE, 3, seg=2)
    else:
        P.wrect(ctx, jx, FY - 26, 40, 26, "jar", (150, 150, 156), LINE, 3, seg=2)


def r1(ctx, t):
    lt = t - 64.0
    shake = 10 * (1 - prog(t, EVENTS["crash"], EVENTS["crash"] + 0.5)) if t > EVENTS["crash"] else 0
    with Camera(1.4, 1000, 540, shake=shake).apply(ctx):
        fallen = ease(prog(t, EVENTS["crash"], EVENTS["crash"] + 0.45))
        home(ctx, t, cal_names=FULL_WEEK, easel_kw={"fallen": fallen}, lamp=0.4)
        spill_pool(ctx, ease(prog(t, EVENTS["spill"], EVENTS["spill"] + 1.2)))
        if t < EVENTS["trip"]:
            x, ph = walk_x(520, lt, 280)
            hip, feet = standing(x, FY, 1, step=ph)
            puppet(ctx, hip, 1, lean=0.1, feet=feet, expr="tired", look=(1, 0.4))
        else:
            k1 = ease(prog(t, EVENTS["trip"], EVENTS["trip"] + 0.35))
            k2 = ease(prog(t, EVENTS["trip"] + 0.35, EVENTS["trip"] + 0.9))
            x = 1100 + 80 * k1
            hip0, feet0 = standing(x, FY, 1)
            hipS, feetS, _ = floor_sit(x - 20)
            hip = lerp2(hip0, hipS, k2)
            feet = {kk: lerp2(feet0[kk], feetS[kk], k2) for kk in feet0}
            puppet(ctx, hip, 1, lean=0.1 + 0.6 * k1 - 0.75 * k2, feet=feet, expr="shocked" if k2 < 1 else "hurt",
                   look=(1, 0.6), slack=0.3, free=True,
                   hands={"near": (hip[0] + 70, FY - 70 - 30 * (1 - k2)), "far": (hip[0] + 56, FY - 66 - 30 * (1 - k2))})
    hud(ctx, t)


def r2(ctx, t):
    lean_down = ease(prog(t, 71.4, 72.6))
    with Camera(lerp(1.45, 1.6, prog(t, 70, 78)), 1100, 520).apply(ctx):
        home(ctx, t, cal_names=FULL_WEEK, easel_kw={"fallen": 1.0}, lamp=0.4)
        spill_pool(ctx, 1.0)
        hip, feet, lean = floor_sit(1120)
        ph = (hip[0] + 72, hip[1] - 96)
        J = puppet(ctx, hip, 1, lean=lean, feet=feet, hands={"near": ph, "far": (ph[0] - 8, ph[1] + 6)},
                   expr="hurt" if t < 74.4 else "closed", look=(1, 1), screen_glow=1.0, head_tilt=0.2, slack=0.15)
        jx = (hrand("bz", ctx.frame) - 0.5) * 6 if EVENTS["sunday_buzz"] <= t < EVENTS["sunday_buzz"] + 0.6 else 0
        P.phone_held(ctx, ph[0] + jx, ph[1])
        P.bubble(ctx, ph[0] + 30, ph[1] - 160, "can you do sunday too?", False, 30, fade(t, 70.7, 74.6, 0.2, 0.3), 340)
        speech(ctx, t, "him", J["head"][0] - 10, J["head"][1] - 70)
        fog(ctx, 340, 1.0)
        puppeteer(ctx, lerp(1300, 1240, lean_down), lerp(1.45, 1.65, lean_down), alpha=1.0, body=0.0,
                  lean=-0.6 * lean_down, eyes=1.0, grin=1.3, n=10)
    vline(ctx, "V6", 1320, 260, size=54)
    cap(ctx, "C7", y=985)
    hud(ctx, t)


# ---- the turn ------------------------------------------------------------------------------
def t1(ctx, t):
    tug = EVENTS["tug"]
    pan = ease(prog(t, 81.0, 83.0))
    with Camera(lerp(2.1, 1.5, pan), lerp(1180, 1400, pan), lerp(560, 460, pan)).apply(ctx):
        home(ctx, t, cal_names=FULL_WEEK, easel_kw={"fallen": 1.0}, lamp=0.4)
        spill_pool(ctx, 1.0)
        hip, feet, lean = floor_sit(1120)
        pull = math.sin(math.pi * prog(t, tug, tug + 0.6))
        hand = (hip[0] + 76, hip[1] - 136 + 36 * pull)
        J = puppet(ctx, hip, 1, n=visible_strings(t) - 1, lean=lean, feet=feet, hands={"near": hand},
                   expr="worried" if t < tug + 0.6 else "shocked", look=(1, -0.6) if t < 81 else (1, -0.9), slack=0.15, free=True)
        # the one string he tugs runs off to the window, and sags: nobody pulls back
        slack = 0.0 if t < tug else ease(prog(t, tug, tug + 0.5))
        a = J["limbs"]["arm_near"][2]
        win = (1615, 300)
        mid = ((a[0] + win[0]) / 2, (a[1] + win[1]) / 2 - 40 + slack * 150)
        ctx.c.drawPath(poly_path([a, mid, win], closed=False, smooth=True), blurred(stroke(STRING, 8, 0.3), 4))
        ctx.c.drawPath(poly_path([a, mid, win], closed=False, smooth=True), stroke(STRING, 3.2, 0.95))
        fog(ctx, 160, 1.0)
    hud(ctx, t)


def t2(ctx, t):
    if t < 86.6:
        lt = t - 83.0
        with Camera(lerp(1.05, 1.3, lt / 3.6), 1200, 520).apply(ctx):
            ctx.c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, H + 600), fill((16, 18, 26)))
            for i in range(14):
                ctx.c.drawCircle(hrand("stx", i) * W, 100 + hrand("st", i) * 260, 1.8, fill(TEXT, 0.5))
            for i in range(9):  # rooftops
                bx = i * 230 - 40
                top = 600 + hrand("rt", i) * 120
                ctx.c.drawRect(skia.Rect.MakeLTRB(bx, top, bx + 220, 1400), fill((24, 24, 30)))
            wx, wy, ww, wh = 1000, 300, 560, 380
            ctx.c.drawRect(skia.Rect.MakeLTRB(wx - 80, wy - 80, wx + ww + 80, 1400), fill((30, 30, 36)))
            wrect(ctx, wx, wy, ww, wh, "danwin", (30, 34, 46), (70, 70, 80), 5, seg=3)
            ctx.c.save()
            ctx.c.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
            glow(ctx, wx + 470, wy + 170, 240, BLUE, 0.3)  # tv
            fl = wy + wh - 20
            wrect(ctx, wx + 70, fl - 96, 300, 66, "sofa", (70, 74, 96), LINE, 3, seg=3)
            DAN.draw(ctx, (wx + 250, fl - 104), -1, lean=1.3, expr="closed", head_tilt=-0.2,
                     feet={"near": (wx + 360, fl - 100), "far": (wx + 350, fl - 104)},
                     hands={"near": (wx + 190, fl - 100), "far": (wx + 200, fl - 102)},
                     bend={"leg_near": 1, "leg_far": 1, "arm_near": -1, "arm_far": -1})
            # the string comes in through the window and just lies on the floor: nobody holds it
            pts = [(wx - 10, wy + 90), (wx + 160, fl - 8), (wx + 300, fl - 2), (wx + 380, fl - 12), (wx + 340, fl - 2)]
            ctx.c.drawPath(poly_path(pts, closed=False, smooth=True), stroke(STRING, 3.2, 0.95))
            ctx.c.restore()
            sag = [(-300, 200), (300, 420), (700, 300), (wx - 10, wy + 90)]
            ctx.c.drawPath(poly_path(sag, closed=False, smooth=True), stroke(STRING, 3.2, 0.95))
            if lt > 1.0:
                draw_text(ctx, "z", wx + 230 + 10 * math.sin(t * 2), fl - 200 - (t * 30) % 40, 44, TEXT, 0.6)
    else:
        with Camera(1.7, 860, 560).apply(ctx):
            office(ctx, desk_x=840, night=True)
            P.chair(ctx, 800, 690, 1, key="emptych")
            pts = [(560, 200), (700, 560), (770, 682), (830, 688), (860, 678), (810, 686)]
            ctx.c.drawPath(poly_path(pts, closed=False, smooth=True), stroke(STRING, 3.2, 0.95))
    cap(ctx, "C8")
    hud(ctx, t)


def calendar_close(ctx, t, names, **kw):
    with Camera(2.4, CAL[0] + 7 * 66 * CAL[2] / 2, CAL[1] + 40).apply(ctx):
        P.back_wall(ctx)
        calendar(ctx, CAL[0], CAL[1], names, scale=CAL[2], **kw)


def t3(ctx, t):
    if t < 93.6:
        lift = ease(prog(t, 90.2, 91.4))
        flinch = math.sin(math.pi * prog(t, EVENTS["flinch"], EVENTS["flinch"] + 0.5)) * 30
        with Camera(1.3, 1120, 450).apply(ctx):
            home(ctx, t, cal_names=FULL_WEEK, easel_kw={"fallen": 1.0}, lamp=0.4)
            spill_pool(ctx, 1.0)
            hip, feet, lean = floor_sit(1120)
            tops = puppeteer(ctx, 1150, 2.0, alpha=1.0, body=lift, eyes=1.0, grin=0.3, bar_dx=-flinch, n=10)
            puppet(ctx, hip, 1, lean=lean, feet=feet, expr="shocked" if t < 92 else "determined", look=(0, -1.4),
                   tops=tops if lift > 0.5 else None)
            fog(ctx, 330, 1 - lift)
            if lift < 1:
                puppeteer(ctx, 1150, 2.0, alpha=1.0, body=0.0, eyes=1.0, grin=0.3, n=10)
        cap(ctx, "C9", y=985)
        hud(ctx, t)
        return
    calendar_close(ctx, t, FULL_WEEK, strike=1.0)
    cap(ctx, "C10", y=960)
    hud(ctx, t)


# ---- the final fight -----------------------------------------------------------------------
def f1f2(ctx, t):
    drag = ease(prog(t, 103.6, 108.0))
    resist = ease(prog(t, 108.4, 110.0))
    rise = ease(prog(t, 101.4, 103.4))
    z = lerp(1.25, 1.45, ease(prog(t, 97, 113)))
    with Camera(z, 1060, 480, shake=3 * resist).apply(ctx):
        home(ctx, t, cal_names=FULL_WEEK, night=False, lamp=0.0)
        has_brush = t > 99.6
        if not has_brush:
            brush(ctx, BRUSH_REST)
        x = 1150 - 150 * drag + 60 * resist
        lean = 0.04 - 0.35 * drag + 0.45 * resist
        hip, feet = standing(x, FY, 1)
        if resist > 0:
            feet = {"near": (x + 38, FY), "far": (x - 34, FY)}
        tops = puppeteer(ctx, 1100 - 120 * drag, lerp(1.4, 2.3, rise), alpha=rise, body=1.0, grin=1.3,
                         up=0.55 + 0.25 * drag, lean=-0.4 * drag, bar_dx=-260 * drag + 60 * resist, bar_tilt=-0.15 * drag, n=10)
        held = (x + 74, hip[1] - 70)
        reach_k = ease(prog(t, 98.8, 99.6)) * (1 - ease(prog(t, 99.6, 100.0)))
        near = lerp2((x + 30, hip[1] + 10), (BRUSH_REST[0] - 6, BRUSH_REST[1] - 8), reach_k) if not has_brush else \
            lerp2(held, (x - 60, hip[1] - 230), drag * (1 - 0.6 * resist))
        expr = "hopeful" if t < 100.6 else "worried"
        if drag > 0.3:
            expr = "anxious"
        if t > EVENTS["eyes_closed"]:
            expr = "closed"
        if t > EVENTS["eyes_open2"]:
            expr = "determined"
        far = lerp2((x - 10, hip[1] + 10), (x - 80, hip[1] - 200), drag)
        J = puppet(ctx, hip, 1, lean=lean, feet=feet, hands={"near": near, "far": far}, expr=expr,
                   look=(-1, 0) if 100.6 < t < 103 else (1, 0), tops=tops if rise > 0.05 else None, tremble=resist, free=True)
        if has_brush:
            brush(ctx, J["limbs"]["arm_near"][2], ang=-0.9)
        speech(ctx, t, "door", 470, 380)
        speech(ctx, t, "phone", 820, 330)
        if EVENTS["knock"] <= t < EVENTS["knock"] + 0.7:
            draw_text(ctx, "knock knock", 470, 300, 34, (170, 170, 176), 1 - prog(t, EVENTS["knock"], EVENTS["knock"] + 0.7))
    vline(ctx, "V7", 1300, 260, 54)
    vline(ctx, "V8", 1300, 260, 54)
    vline(ctx, "V9", 1300, 260, 54)
    vline(ctx, "V10", 1300, 260, 84)
    hud(ctx, t)


def f3(ctx, t):
    lt = t - 114.0
    shake = 16 * (1 - prog(lt, 0, 0.5))
    with Camera(1.45, 1060, 480, shake=shake).apply(ctx):
        home(ctx, t, cal_names=FULL_WEEK, night=False, lamp=0.0)
        x = 1060
        hip = standing(x, FY, 1)[0]
        feet = {"near": (x + 38, FY), "far": (x - 34, FY)}
        crack = ease(prog(lt, 0.0, 0.9))
        tops = None
        if t < EVENTS["burst"]:
            tops = puppeteer(ctx, 980, 2.3, alpha=1.0, body=1.0, grin=0.0, up=0.8, lean=-0.4, bar_dx=-200,
                             bar_tilt=-0.15, crack=crack, n=10)
        else:
            P.villain_shards(ctx, 980, FY, 2.3, prog(t, EVENTS["burst"], EVENTS["burst"] + 2.0))
        n = visible_strings(t)
        snaps = EVENTS["snaps"]
        per = math.ceil(n / len(snaps))
        snapped = sum(1 for s_ in snaps if t >= s_)
        gone = set(range(min(n, snapped * per)))
        held = (x + 74, hip[1] - 70)
        J = puppet(ctx, hip, 1, n=n if tops else 0, lean=0.08, feet=feet, hands={"near": held}, expr="determined",
                   look=(1, 0), tops=tops, skip=gone)
        brush(ctx, held, ang=-0.9)
        # snapped strings: the lower half drops away, a gold spark where it broke
        for i, (p, lay, bias, k) in enumerate(string_points(J, n)):
            if i not in gone:
                continue
            ks = snaps[min(len(snaps) - 1, i // per)]
            k = prog(t, ks, ks + 0.6)
            if k >= 1:
                continue
            brk = (p[0] + bias * 40, p[1] - 170 + 220 * k * k)
            ctx.c.drawLine(p[0], p[1], brk[0], brk[1], stroke(STRING, 2.6, 1 - k))
            glow(ctx, brk[0], brk[1] - 10, 46, GOLD, 0.8 * (1 - k))
    speech(ctx, t, "him_big", 1000, 360, size=100)
    flash = 1 - prog(lt, 0, 0.25)
    if flash > 0:
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((255, 236, 190), 0.5 * flash))
    hud(ctx, t)
    hud_no(ctx, t)


def f4(ctx, t):
    with Camera(1.35, 900, 520).apply(ctx):
        home(ctx, t, cal_names=FULL_WEEK, night=False, lamp=0.0)
        x = 1060
        breathe = math.sin(math.pi * prog(t, 118.4, 120.4))
        hip, feet = standing(x, FY, 1)
        held = (x + 60, hip[1] - 40)
        HIM.draw(ctx, hip, 1, lean=0.04 - 0.05 * breathe, feet=feet, hands={"near": held},
                 expr="closed" if 118.4 < t < 119.8 else "smile", look=(-1, 0) if t < 118.4 else (0, -0.3))
        brush(ctx, held, ang=-1.2)
        speech(ctx, t, "door", 470, 380)
        speech(ctx, t, "phone", 820, 330)
    hud(ctx, t)
    hud_no(ctx, t)


# ---- payoff ----------------------------------------------------------------------------------
def p1(ctx, t):
    lt = t - 121.0
    paint = ease(prog(t, 121.6, 128.4))
    with Camera(lerp(1.5, 1.65, lt / 8), 1250, 500).apply(ctx):
        home(ctx, t, cal_names=FULL_WEEK, night=False, window_gold=ease(prog(t, 121.0, 124.0)), lamp=0.0,
             easel_kw={"paint": paint})
        x = 1150
        x = 1170
        hand = (1214 + 10 * math.sin(t * 2.3), 520 + 34 * math.sin(t * 1.7))
        hip, feet = standing(x, FY, 1)
        J = HIM.draw(ctx, hip, 1, lean=0.08, feet=feet, hands=free_hands(HIM, hip, 1, 0.08, {"near": hand}),
                     expr="smile" if paint < 0.6 else "happy", look=(1, -0.2))
        brush(ctx, J["limbs"]["arm_near"][2], ang=-0.3, wet=mix((60, 56, 52), GOLD, paint))
    cap(ctx, "C11")
    hud(ctx, t)
    hud_no(ctx, t)


def p2(ctx, t):
    lt = t - 129.0
    come_in = ease(prog(t, 129.6, 131.6))
    sit_k = ease(prog(t, 132.8, 133.8))
    with Camera(1.4, 960, 520).apply(ctx):
        home(ctx, t, cal_names=FULL_WEEK, night=True, lamp=1.0, easel_kw={"paint": 1.0},
             door_kw={"open_k": ease(prog(t, EVENTS["knock2"], EVENTS["knock2"] + 0.5)), "light": 1.0})
        glow(ctx, 1330, 500, 380, GOLD, 0.24)
        if sit_k <= 0:
            dx = lerp(270, 820, come_in)
            JD = stand(DAN, ctx, dx, f=1, lean=0.04, expr="happy", look=(1, 0), step=(lt * 1.6) % 1 if come_in < 1 else 0,
                       hands={"near": (dx + 60, 662), "far": (dx + 50, 668)})
            box(ctx, dx + 60, 690, 120, 26, key="pizza")
            stand(HIM, ctx, 1080, f=-1, lean=0.04, expr="happy", look=(-1, 0))
        else:
            box(ctx, 1000, FY, 120, 26, key="pizza")
            hipD, feetD, _ = floor_sit(860)
            f0 = standing(820, FY)[1]
            feetD = {k: lerp2(f0[k], feetD[k], sit_k) for k in f0}
            JD = DAN.draw(ctx, lerp2(standing(820, FY)[0], hipD, sit_k), 1, lean=-0.05, feet=feetD, expr="happy", look=(1, -0.4),
                          mouth_open=0.6 * abs(math.sin(t * 9)) if t > 134 else 0)
            hipH, feetH, _ = floor_sit(1060)
            f1 = standing(1080, FY)[1]
            feetH = {k: lerp2(f1[k], feetH[k], sit_k) for k in f1}
            HIM.draw(ctx, lerp2(standing(1080, FY)[0], hipH, sit_k), 1, lean=-0.05, feet=feetH, expr="happy", look=(1, -0.4),
                     mouth_open=0.6 * abs(math.sin(t * 9 + 1)) if t > 134 else 0)
        speech(ctx, t, "dan", JD["head"][0], JD["head"][1] - 70)
    hud(ctx, t)
    hud_no(ctx, t)


def p3(ctx, t):
    gold = ease(prog(t, EVENTS["gold_me"], EVENTS["gold_me"] + 1.4))
    calendar_close(ctx, t, ["work", "Ben", "Dan", "Mia", "party", "ME", "Leo"], gold_me=gold, me_alpha=0.0)
    k = prog(t, EVENTS["gold_me"], EVENTS["gold_me"] + 1.4)
    # his hand with the pen, writing in his box
    px = 1415 + 24 * math.sin(k * 14) * (1 - k) * (k > 0)
    py = 612
    ctx.c.drawLine(px, py, px + 90, py + 200, stroke((40, 40, 46), 12))
    ctx.c.drawPath(poly_path([(px + 50, py + 120), (px + 200, py + 330), (px + 280, py + 270), (px + 110, py + 90)], smooth=True),
                   fill(SKIN))
    ctx.c.drawPath(poly_path([(px + 50, py + 120), (px + 200, py + 330), (px + 280, py + 270), (px + 110, py + 90)], smooth=True),
                   stroke(LINE, 4))
    hud(ctx, t, a=1 - prog(t, 139.0, 140.0))
    hud_no(ctx, t, a=1 - prog(t, 139.0, 140.0))


# ---- mirror and title ------------------------------------------------------------------------------
def x1(ctx, t):
    with Camera(1.45, 960, 540).apply(ctx):
        office(ctx, desk_x=420)
        P.chair(ctx, 480, 690, 1, key="xc")
        JH = sit(HIM, ctx, 480, f=1, lean=0.2, expr="smile", look=(1, -0.2), hands={"near": (590, 634), "far": (572, 638)})
        P.table(ctx, 1150, 640, 300, key="adesk2")
        P.chair(ctx, 1360, 690, -1, key="xc2")
        said = t > 145.2
        JA = sit(ANA, ctx, 1360, f=-1, lean=0.12, expr="worried" if t < 144.6 else ("determined" if not said else "smile"),
                 look=(-1, 0) if 142.6 < t < 145 else (-1, -0.5), hands={"near": (1260, 632), "far": (1280, 636)})
        scarf(ctx, JA)
        JB = stand(BOSS, ctx, 980, f=1, lean=0.12, expr="neutral", look=(1, 0.4))
        tie(ctx, JB)
        fall = ease(prog(t, EVENTS["ana_snap"], EVENTS["ana_snap"] + 0.7))
        a = JA["limbs"]["arm_near"][2]
        if fall < 1:
            top = (a[0] + 60, -300)
            end = lerp2(a, (a[0] + 80, FY), fall)
            mid = ((top[0] + end[0]) / 2, (top[1] + end[1]) / 2 + 220 * fall)
            ctx.c.drawPath(poly_path([lerp2(top, end, fall * 0.7), mid, end], closed=False, smooth=True),
                           stroke(STRING, 2.6, 0.9 * (1 - fall)))
            ctx.c.drawCircle(end[0], end[1], 4, fill(STRING, 1 - fall))
        speech(ctx, t, "boss", JB["head"][0] + 30, JB["head"][1] - 70)
        speech(ctx, t, "him", JH["head"][0], JH["head"][1] - 70, size=30)
        speech(ctx, t, "ana", JA["head"][0], JA["head"][1] - 70)


def title(ctx, t):
    a = fade(t, EVENTS["title"], DURATION, 0.8, 1.2)
    draw_text(ctx, "NO.", W / 2, 520, 230, TEXT, a, face="LuckiestGuy-Regular.ttf")
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 200 + 400 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=46)
    cap(ctx, "T2", y=760, size=64, rgb=GOLD, glow_rgb=(170, 110, 20))


DISPATCH = {
    "S01": s01, "H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5, "H6": h6, "S02": s02, "S03": s03, "S04": s04,
    "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6, "G7": g7, "G8": g8,
    "R1": r1, "R2": r2, "T1": t1, "T2": t2, "T3": t3, "F1": f1f2, "F2": f1f2, "F3": f3, "F4": f4,
    "P1": p1, "P2": p2, "P3": p3, "X1": x1, "TT": title,
}
CONTINUOUS = {"S01", "H1", "F2", "R2"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "TT":
        black(ctx, prog(t, DURATION - 1.0, DURATION))
