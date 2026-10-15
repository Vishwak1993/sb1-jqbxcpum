"""Reusable pieces first written for NO.: speech bubbles, reach-safe hands, doors, dogs, boxes, a street,
an office and a full-screen phone. Film-specific sets and devices stay in the film folder.
"""
import math

import skia

from .core import (W, H, FPS, LINE, GREY, GREY_D, GREY_L, TEXT, BLUE, fill, stroke, wrect, wcircle, wline, rrect,
                   glow, cone, draw_text, text_width, poly_path, hrand, fade, prog, ease, ease_out_back)
from .character import UPPER_ARM, FORE_ARM
from . import props as P

FY = 780


def bubble_on(bubbles, who, t):
    """bubbles: [(t0, t1, who, text)]. The one currently showing for `who`, or None."""
    for b in bubbles:
        if b[2] == who and b[0] - 0.05 <= t <= b[1] + 0.3:
            return b
    return None


def speech(ctx, t, bubbles, who, x, y, size=32, tail=0.0, light=None):
    """Speech bubble above (x, y): pops in, fades out. His bubbles (who starts with 'him') are light."""
    b = bubble_on(bubbles, who, t)
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


def talk(bubbles, who, t, dur=0.45):
    """Mouth movement while `who`'s bubble pops in."""
    b = bubble_on(bubbles, who, t)
    return 0.5 * abs(math.sin(t * 16)) if b and b[0] <= t <= b[0] + dur else 0.0


def free_hands(ch, hip, f, lean, hands, head_tilt=0.0):
    """Hands that hold nothing fixed (or carry their prop with them) stay within arm's reach."""
    if not hands:
        return hands
    s = ch.scale
    sh = ch.joints(hip, f, lean, head_tilt)["shoulder"]
    base = {"near": (sh[0] + f * 4 * s, sh[1] + 6 * s), "far": (sh[0] - f * 4 * s, sh[1] + 6 * s)}
    L = (UPPER_ARM + FORE_ARM - 4) * s
    out = {}
    for k, p in hands.items():
        if p is None:
            continue
        b = base[k]
        d = math.hypot(p[0] - b[0], p[1] - b[1])
        out[k] = p if d <= L else (b[0] + (p[0] - b[0]) * L / d, b[1] + (p[1] - b[1]) * L / d)
    return out


def lift(feet, dy):
    return {k: (v[0], v[1] + dy) for k, v in feet.items()}


def floor_sit(x, f=1, lean=-0.1, floor_y=FY):
    hip = (x, floor_y - 22)
    feet = {"near": (x + f * 104, floor_y), "far": (x + f * 94, floor_y)}
    return hip, feet, lean


def door(ctx, x, w=170, h=380, open_k=0.0, key="door", light=0.0, floor_y=FY, rgb=(74, 66, 60)):
    wrect(ctx, x - 12, floor_y - h - 12, w + 24, h + 12, (key, "fr"), (40, 40, 46), LINE, 3, seg=2)
    if light > 0:
        ctx.c.drawRect(skia.Rect.MakeXYWH(x, floor_y - h, w, h), fill((210, 200, 180), 0.25 * light))
    dw = w * (1 - 0.8 * open_k)
    wrect(ctx, x, floor_y - h, dw, h, (key, "d"), rgb, LINE, 3, seg=2)
    wcircle(ctx, x + dw - 22, floor_y - h / 2, 7, (key, "k"), (170, 160, 130), LINE, 2)


def box(ctx, x, y, w=120, h=90, key="box"):
    wrect(ctx, x - w / 2, y - h, w, h, key, (150, 118, 82), LINE, 3, seg=2)
    wline(ctx, (x - w / 2, y - h + 18), (x + w / 2, y - h + 18), (key, "t"), (120, 92, 62), 3, seg=2)


def dog(ctx, x, y, f=1, key="dog", rgb=(150, 128, 104), s=1.0, sit=False, walk=0.0, wag=1.0):
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
    w = math.sin(ctx.t * 14) * 10 * s * wag
    wline(ctx, (x - f * 42 * s, by - 4 * s), (x - f * 60 * s, by - 22 * s + w), (key, "tail"), rgb, 6 * s, seg=1)
    return (hx - f * 10 * s, hy + 14 * s)


def street(ctx, t, rain=0.0, lamps=(400, 1500), floor_y=FY, window_rgb=(70, 70, 60), sky=None):
    if sky is not None:
        ctx.c.drawRect(skia.Rect.MakeLTRB(-600, -600, W + 600, floor_y), fill(sky))
    for i in range(16):
        bx = -200 + i * 150
        bh = 200 + hrand("bld", i) * 260
        ctx.c.drawRect(skia.Rect.MakeXYWH(bx, floor_y - bh - 60, 140, bh), fill((24, 24, 30)))
        for j in range(int(bh // 60)):
            if hrand("bw", i, j) > 0.55:
                ctx.c.drawRect(skia.Rect.MakeXYWH(bx + 20 + (j % 2) * 60, floor_y - bh - 40 + j * 55, 26, 20), fill(window_rgb, 0.5))
    for lx in lamps:
        P.wrect(ctx, lx, floor_y - 380, 10, 380, ("lamp", lx), GREY_D, LINE, 2, seg=2)
        glow(ctx, lx + 5, floor_y - 380, 260, (255, 210, 140), 0.18)
        cone(ctx, (lx + 5, floor_y - 380), (lx - 140, floor_y), (lx + 150, floor_y), (255, 210, 140), 0.10)
    P.floor(ctx, floor_y)
    if rain > 0:
        for i in range(160):
            rx = -300 + hrand("rr", i) * 2500
            ph = (ctx.t * 2.0 + hrand("rp", i)) % 1.0
            ry = -200 + ph * 1100
            ctx.c.drawLine(rx, ry, rx - 6, ry + 26, stroke((150, 160, 190), 1.6, 0.45 * rain))


def office(ctx, desk_x=700, night=False):
    P.back_wall(ctx, rgb=(26, 27, 31))
    P.floor(ctx, FY)
    P.window(ctx, 1380, 190, 300, 210, "owin", night=night, moon=False, sky=(40, 46, 58) if not night else (20, 22, 32))
    for i in range(3):
        ctx.c.drawRect(skia.Rect.MakeXYWH(1400 + i * 90, 300 - i * 20, 50, 100 + i * 20), fill((30, 34, 44)))
    P.wall_clock(ctx, 1110, 240, 18, 10, key="oclock")
    P.table(ctx, desk_x, 640, 420, key="odesk")
    P.desk_computer(ctx, desk_x + 260, 640, key="opc")


def phone_close(ctx, t, sender, msgs, t0, glow_rgb=BLUE, stack_dt=None, mine=(), avatar=(90, 96, 110)):
    """Full-screen phone with a chat. msgs appear from t0 (one every stack_dt s); indices in `mine` are his."""
    UI = P.PhoneUI(W / 2, 590, 560, 880)
    UI.body(ctx, 1.0, glow_rgb)
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, 130), fill((26, 28, 36)))
        wcircle(ctx, x0 + 60, y0 + 84, 26, "av_" + sender, avatar, None, 0)
        draw_text(ctx, sender, x0 + 100, y0 + 96, 40, TEXT, align="left")
        y = y0 + 170
        for i, m in enumerate(msgs):
            ti = t0[i] if isinstance(t0, (list, tuple)) else t0 + (i * stack_dt if stack_dt else 0)
            a = ease(prog(t, ti, ti + 0.2))
            if a <= 0:
                break
            if i in mine:
                h = P.bubble(ctx, x0 + UI.w - 62, y, m, True, 40, a, maxw=460)
            else:
                h = P.bubble(ctx, x0 + 26, y, m, False, 40, a, maxw=460)
            y += h + 14
    return UI


def sweat(ctx, J, s=1.0, a=1.0):
    hx, hy = J["head"]
    f = J["facing"]
    x, y, d = hx - f * 30 * s, hy - 26 * s, 6 * s
    drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
    ctx.c.drawPath(drop, fill((200, 225, 255), 0.9 * a))
    ctx.c.drawPath(drop, stroke((90, 120, 170), 2 * s, a))
