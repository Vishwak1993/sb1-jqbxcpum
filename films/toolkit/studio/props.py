"""Reusable props, the villain and the HUD. Props that hands touch expose grip points."""
import math

import skia

from .core import (W, H, LETTERBOX, BG, FLOOR, LINE, SKIN, GREY, GREY_D, GREY_L, TEXT, RED, RED_D, GOLD, BLUE,
                   fill, stroke, blurred, wrect, wcircle, wline, rrect, glow, cone, draw_text, wobble_points,
                   poly_path, circle_pts, hrand, col, lerp, ease)


def floor(ctx, y=780, x0=-400, x1=W + 400, rgb=FLOOR):
    wline(ctx, (x0, y), (x1, y), "floor", rgb, 3, amp=0.8, seg=12)


def back_wall(ctx, y=780, rgb=(20, 20, 23)):
    ctx.c.drawRect(skia.Rect.MakeLTRB(-600, 0, W + 600, y), fill(rgb))


# ---- furniture ---------------------------------------------------------------
def table(ctx, x, top_y, w=330, floor_y=780, key="table"):
    wrect(ctx, x, top_y, w, 14, (key, "top"), GREY, LINE, 3)
    for lx in (x + 18, x + w - 30):
        wrect(ctx, lx, top_y + 14, 12, floor_y - top_y - 14, (key, lx), GREY_D, LINE, 3, seg=2)
    return {"top": top_y}


def chair(ctx, x, seat_y, facing=1, floor_y=780, key="chair"):
    """x = seat centre. Back is behind the sitter (opposite to facing)."""
    sw = 90
    wrect(ctx, x - sw / 2, seat_y, sw, 12, (key, "s"), GREY_L, LINE, 3, seg=2)
    bx = x - facing * sw / 2 - (8 if facing > 0 else -8) * 0
    wrect(ctx, bx - 6, seat_y - 120, 12, 120, (key, "b"), GREY_L, LINE, 3, seg=2)
    for lx in (x - sw / 2 + 4, x + sw / 2 - 14):
        wrect(ctx, lx, seat_y + 12, 10, floor_y - seat_y - 12, (key, lx), GREY_D, LINE, 3, seg=2)


def bed(ctx, x, y=780, w=520, key="bed"):
    wrect(ctx, x, y - 90, w, 50, (key, "m"), (60, 64, 92), LINE, 3, seg=6)
    wrect(ctx, x - 10, y - 140, 20, 140, (key, "hb"), GREY, LINE, 3, seg=3)
    wrect(ctx, x + 14, y - 112, 90, 24, (key, "p"), (210, 208, 200), LINE, 3, seg=3)
    for lx in (x + 6, x + w - 18):
        wrect(ctx, lx, y - 40, 12, 40, (key, lx), GREY_D, LINE, 3, seg=1)


def window(ctx, x, y, w=210, h=210, key="win", night=True, rain=0.0, moon=True, sky=(26, 30, 44), lit=0.0):
    wrect(ctx, x, y, w, h, (key, "f"), sky, (90, 90, 100), 4)
    if moon and night:
        glow(ctx, x + w * 0.72, y + h * 0.28, 50, (220, 220, 230), 0.35)
        wcircle(ctx, x + w * 0.72, y + h * 0.28, 13, (key, "moon"), (225, 225, 230), None, 0)
    if rain > 0:
        for i in range(40):
            rx = x + hrand(key, i, "rx") * w
            ph = (ctx.t * 2.2 + hrand(key, i, "ph")) % 1.0
            ry = y + ph * h
            ctx.c.drawLine(rx, ry, rx - 4, min(y + h, ry + 18), stroke((150, 160, 190), 1.6, 0.5 * rain))
    wline(ctx, (x + w / 2, y), (x + w / 2, y + h), (key, "v"), (90, 90, 100), 4)
    wline(ctx, (x, y + h / 2), (x + w, y + h / 2), (key, "h"), (90, 90, 100), 4)


def wall_clock(ctx, x, y, hh, mm, r=34, key="clock"):
    wcircle(ctx, x, y, r, key, (30, 30, 34), (170, 170, 176), 3)
    a_m = (mm / 60) * 2 * math.pi - math.pi / 2
    a_h = ((hh % 12 + mm / 60) / 12) * 2 * math.pi - math.pi / 2
    ctx.c.drawLine(x, y, x + math.cos(a_m) * r * 0.8, y + math.sin(a_m) * r * 0.8, stroke((200, 200, 205), 3))
    ctx.c.drawLine(x, y, x + math.cos(a_h) * r * 0.5, y + math.sin(a_h) * r * 0.5, stroke((200, 200, 205), 4))


def digital_clock(ctx, x, y, s, key="dclock", rgb=RED):
    wrect(ctx, x, y, 110, 52, key, (28, 28, 32), LINE, 3)
    glow(ctx, x + 55, y + 26, 80, rgb, 0.18)
    draw_text(ctx, s, x + 55, y + 40, 34, rgb, 1.0, face="LuckiestGuy-Regular.ttf")


def desk_computer(ctx, x, desk_y, key="pc", screen=0.8):
    """Monitor on a desk, screen faces left (viewer sees the side + glow)."""
    wrect(ctx, x, desk_y - 150, 170, 120, (key, "m"), (36, 38, 46), LINE, 3)
    ctx.c.drawRect(skia.Rect.MakeXYWH(x + 10, desk_y - 140, 150, 100), fill((70, 100, 160), 0.6 * screen))
    wrect(ctx, x + 75, desk_y - 30, 20, 30, (key, "s"), GREY_D, LINE, 3, seg=1)
    glow(ctx, x + 85, desk_y - 90, 260, BLUE, 0.12 * screen)


def cake(ctx, x, top_y, lit=1.0, key="cake"):
    """Small cake on a table, one candle. Returns the flame point (for the blow-out)."""
    wrect(ctx, x - 40, top_y - 44, 80, 44, (key, "b"), (196, 186, 170), LINE, 3, seg=3)
    wline(ctx, (x - 40, top_y - 30), (x + 40, top_y - 30), (key, "ic"), (150, 140, 128), 3)
    wrect(ctx, x - 3, top_y - 74, 6, 30, (key, "c"), (220, 210, 196), LINE, 2, seg=1)
    fx, fy = x, top_y - 86
    if lit > 0.01:
        fl = 1 + 0.12 * math.sin(ctx.t * 17) + 0.08 * math.sin(ctx.t * 29)
        glow(ctx, fx, fy, 380 * lit, GOLD, 0.30 * lit * fl)
        p = poly_path([(fx, fy - 15 * fl), (fx + 6, fy), (fx, fy + 6), (fx - 6, fy)], smooth=True)
        ctx.c.drawPath(p, fill((255, 214, 120), lit))
    return (fx, fy)


def mug(ctx, x, y, key="mug", tipped=0.0):
    wrect(ctx, x, y - 36, 30, 36, key, (170, 170, 176), LINE, 3, seg=2)
    wcircle(ctx, x + 36, y - 20, 9, (key, "h"), None, (170, 170, 176), 4)


def phone_side(ctx, x, y, on=0.0, face_down=False, key="ph", glow_rgb=BLUE, angle=0.0):
    """Phone seen from the side. on: screen brightness 0..1. (x,y) = grip point."""
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.rotate(angle)
    if on > 0 and not face_down:
        glow(ctx, 0, -10, 260, glow_rgb, 0.22 * on)
    rrect(ctx, -22, -8, 44, 10, 3, (40, 40, 46), LINE, 2.5)
    if on > 0 and not face_down:
        c.drawRect(skia.Rect.MakeXYWH(-19, -9, 38, 3), fill(glow_rgb, on))
    c.restore()


def phone_held(ctx, x, y, facing=1, on=1.0, key="ph", glow_rgb=BLUE):
    """Phone held upright in hand at (x,y), screen toward the face."""
    c = ctx.c
    if on > 0:
        glow(ctx, x - facing * 6, y - 30, 220, glow_rgb, 0.25 * on)
    rrect(ctx, x - 7, y - 50, 14, 58, 4, (40, 40, 46), LINE, 2.5)
    c.drawRect(skia.Rect.MakeXYWH(x - facing * 6 - 2, y - 46, 4, 50), fill(glow_rgb, on))


# ---- phone close-up UI ----------------------------------------------------------
class PhoneUI:
    """Big phone insert, centred. Draw screen content inside `with ui.screen(ctx):`."""

    def __init__(self, cx=W / 2, cy=H / 2 + 10, w=460, h=820):
        self.cx, self.cy, self.w, self.h = cx, cy, w, h
        self.x0, self.y0 = cx - w / 2, cy - h / 2

    def body(self, ctx, light=1.0, glow_rgb=BLUE):
        glow(ctx, self.cx, self.cy, self.h * 0.85, glow_rgb, 0.18 * light)
        rrect(ctx, self.x0, self.y0, self.w, self.h, 54, (18, 18, 22), (90, 90, 100), 6)
        rrect(ctx, self.x0 + 18, self.y0 + 18, self.w - 36, self.h - 36, 40, (mix_c(light)), None)
        rrect(ctx, self.cx - 60, self.y0 + 30, 120, 26, 13, (10, 10, 12))

    def screen(self, ctx):
        ui = self

        class _S:
            def __enter__(s):
                ctx.c.save()
                rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(ui.x0 + 18, ui.y0 + 18, ui.w - 36, ui.h - 36), 40, 40)
                ctx.c.clipRRect(rr, skia.ClipOp.kIntersect, True)

            def __exit__(s, *a):
                ctx.c.restore()

        return _S()


def mix_c(light):
    return (int(20 + 14 * light), int(22 + 16 * light), int(30 + 24 * light))


def bubble(ctx, x, y, text, mine=False, size=34, a=1.0, maxw=330, rgb=None):
    """Chat bubble. mine=True: right-aligned, his colour."""
    if a <= 0:
        return 0
    words = text.split(" ")
    lines, cur = [], ""
    from .core import text_width
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_width(trial, size) > maxw - 40 and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    lines.append(cur)
    tw = max(text_width(l, size) for l in lines)
    bw, bh = tw + 40, len(lines) * size * 1.15 + 26
    bx = x - bw if mine else x
    bg = rgb or ((70, 110, 200) if mine else (58, 58, 66))
    rrect(ctx, bx, y, bw, bh, 22, bg, None, a=a)
    for i, l in enumerate(lines):
        draw_text(ctx, l, bx + 20, y + 13 + size * 0.85 + i * size * 1.15, size, TEXT, a, align="left")
    return bh


# ---- the villain -------------------------------------------------------------
def villain(ctx, x, floor_y, scale=1.0, alpha=1.0, grin=1.0, lean=0.0, key="villain", reach=None, crack=0.0,
            arms_up=0.0):
    """Dark person-shaped silhouette with a red glow, standing on floor_y. reach: a long arm to a point.
    Returns the head and hand points (e.g. to hang a puppet's control bar from its hands)."""
    if scale <= 0.01:
        return None
    c = ctx.c
    s = scale
    hx = x + lean * 40 * s
    hy = floor_y - 330 * s
    ink = (16, 8, 9)
    body = [(x - 46 * s, floor_y), (x - 52 * s, floor_y - 120 * s), (x - 66 * s, floor_y - 230 * s),
            (hx - 54 * s, hy + 46 * s), (hx, hy + 30 * s), (hx + 54 * s, hy + 46 * s),
            (x + 66 * s, floor_y - 230 * s), (x + 52 * s, floor_y - 120 * s), (x + 46 * s, floor_y)]
    shapes = [poly_path(wobble_points(ctx, body, key, 2.5 * s), smooth=True),
              poly_path(wobble_points(ctx, circle_pts(hx, hy, 56 * s, 60 * s, 24), (key, "h"), 2.2 * s), smooth=True)]
    arms = []
    for side in (-1, 1):
        sh = (hx + side * 56 * s, hy + 60 * s)
        if reach is not None and side == 1:
            mid = ((sh[0] + reach[0]) / 2, min(sh[1], reach[1]) - 30 * s)
            arms.append([sh, mid, reach])
        else:
            up = arms_up
            el = (sh[0] + side * (16 + 40 * up) * s, sh[1] + (90 - 150 * up) * s)
            hd = (el[0] + side * (8 + 50 * up) * s, el[1] + (95 - 120 * up) * s)
            arms.append([sh, el, hd])
    geometry = {"head": (hx, hy), "hands": (arms[0][2], arms[1][2])}
    if alpha <= 0.01:
        return geometry
    c.saveLayerAlpha(None, int(alpha * 255))
    for sp in shapes:
        c.drawPath(sp, blurred(fill(RED, 0.7), 24 * s))
    for a in arms:
        ap = poly_path(wobble_points(ctx, a, (key, "arm", a[0][0] > hx), 2), closed=False, smooth=True)
        c.drawPath(ap, blurred(stroke(RED, 34 * s, 0.6), 12 * s))
        c.drawPath(ap, stroke(RED, 30 * s, 0.9))
        c.drawPath(ap, stroke(ink, 24 * s))
        _villain_hand(ctx, a[-2], a[-1], s, ink, (key, "hand", a[0][0] > hx))
    for sp in shapes:
        c.drawPath(sp, stroke(RED, 7 * s, 0.9))
    for sp in shapes:
        c.drawPath(sp, fill(ink))
    for side in (-1, 1):
        ex, ey = hx + side * 22 * s, hy - 8 * s
        c.drawPath(poly_path([(ex - 12 * s, ey + 2 * s), (ex, ey - 4 * s), (ex + 12 * s, ey + 2 * s)], False, True),
                   stroke(RED, 5 * s))
    if grin > 0:
        c.drawPath(poly_path([(hx - 24 * s, hy + 18 * s), (hx, hy + (18 + 12 * grin) * s), (hx + 24 * s, hy + 18 * s)], False, True),
                   stroke(RED, 4.5 * s))
    if crack > 0:
        for i in range(8):
            a = hrand(key, i, "ca") * 2 * math.pi
            L = (40 + 260 * crack) * s
            p0 = (hx, hy + 120 * s)
            p1 = (p0[0] + math.cos(a) * L, p0[1] + math.sin(a) * L)
            c.drawLine(p0[0], p0[1], p1[0], p1[1], blurred(stroke(GOLD, 9 * s * crack), 4))
            c.drawLine(p0[0], p0[1], p1[0], p1[1], stroke((255, 236, 180), 4 * s * crack))
    c.restore()
    return geometry


def _villain_hand(ctx, prev, tip, s, ink, key):
    """A clawed hand at the end of a villain arm: a palm and four long, thin, curved fingers, pointing along the arm."""
    c = ctx.c
    ang = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
    palm = (tip[0] + math.cos(ang) * 6 * s, tip[1] + math.sin(ang) * 6 * s)
    fingers = []
    for i, spread in enumerate((-0.62, -0.2, 0.2, 0.62)):
        a = ang + spread + math.sin(ctx.t * 3 + i) * 0.04
        L = (34 if i in (1, 2) else 28) * s
        base = (palm[0] + math.cos(a) * 12 * s, palm[1] + math.sin(a) * 12 * s)
        mid = (base[0] + math.cos(a) * L * 0.55, base[1] + math.sin(a) * L * 0.55)
        end = (mid[0] + math.cos(a + 0.35) * L * 0.5, mid[1] + math.sin(a + 0.35) * L * 0.5)  # claws curl inward
        fingers.append(poly_path([base, mid, end], closed=False, smooth=True))
    for fp in fingers:
        c.drawPath(fp, blurred(stroke(RED, 13 * s, 0.6), 6 * s))
        c.drawPath(fp, stroke(RED, 11 * s, 0.9))
    c.drawCircle(palm[0], palm[1], 17 * s, blurred(fill(RED, 0.6), 8 * s))
    c.drawCircle(palm[0], palm[1], 17 * s, fill(RED, 0.9))
    for fp in fingers:
        c.drawPath(fp, stroke(ink, 7 * s))
    c.drawCircle(palm[0], palm[1], 14 * s, fill(ink))


def villain_shards(ctx, x, floor_y, scale, k, key="villain"):
    """Villain bursting into red flakes that fade (k: 0..1)."""
    for i in range(70):
        a = hrand(key, i, "a") * 2 * math.pi
        sp = 200 + hrand(key, i, "s") * 700
        px = x + math.cos(a) * sp * k * scale
        py = floor_y - 250 * scale + math.sin(a) * sp * k * scale - 120 * k * k
        r = (6 + hrand(key, i, "r") * 14) * scale * (1 - k)
        if r > 0.3:
            ctx.c.drawCircle(px, py, r, fill(RED if i % 3 else (40, 10, 12), 1 - k))


# ---- HUD ---------------------------------------------------------------------
def hud(ctx, value, label="NEW MESSAGES", a=1.0, rgb=TEXT, pop=0.0, x=56, y=LETTERBOX + 26, day=None):
    """Small top-left counter. pop: 0..1 overshoot when the number changes."""
    if a <= 0:
        return
    rrect(ctx, x, y, 268, 92, 14, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
    draw_text(ctx, label, x + 20, y + 32, 22, (160, 160, 168), a, align="left")
    sz = 52 * (1 + 0.35 * math.sin(math.pi * min(1, pop)) if pop > 0 else 1)
    glow_rgb = rgb if rgb != TEXT else None
    draw_text(ctx, str(value), x + 22, y + 80, sz, rgb, a, align="left", face="LuckiestGuy-Regular.ttf", glow_rgb=glow_rgb)
    if day:
        draw_text(ctx, day, W - 60, y + 36, 30, (170, 170, 176), a, align="right")


def tiny_hud(ctx, x, y, value, rgb=TEXT, a=1.0):
    draw_text(ctx, str(value), x, y, 22, rgb, a, face="LuckiestGuy-Regular.ttf", glow_rgb=rgb if rgb != TEXT else None)
