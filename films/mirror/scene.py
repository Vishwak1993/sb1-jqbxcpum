"""MIRROR.: picture. scene(ctx) draws any frame of the film.

The device: in every mirror his reflection is smaller than he is, grey and hunched, and it shrinks a little more with
every body he measures himself against (COMPARED TO, top-left), even while he really gets stronger. Only he and the
viewer see it. The turn: the big man he envies asks him to take his photo, needs 37 tries, deletes them all ("i look
tiny"), and in the mirror his reflection shrinks and greys too. The payoff is not a bigger body: he takes the hoodie
off and swims, and the counter ends on a word, ME, in gold.
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
from studio.character import Character, standing, seated, walk_x, LIMB_W, OUT  # noqa: E402
from studio import props as P  # noqa: E402
from studio.extras import speech as _speech, talk as _talk, free_hands, sweat  # noqa: E402
from timeline import (SCENES, CAPS, CUES, BUBBLES, EVENTS, DURATION, scene_at, count_at, count_changed,  # noqa: E402
                      refl_at, his_scale, RELABEL, G1_T0, G1_WEEK, G1_LABELS, PHOTOS)
from lines import CAPTIONS, VILLAIN  # noqa: E402

try:
    LEN = json.load(open(HERE / "build" / "line_lengths.json"))
except FileNotFoundError:
    LEN = {}

FY = 780
LG = "LuckiestGuy-Regular.ttf"
HOODIE = (74, 84, 112)
TROUSERS = (52, 54, 64)
SHORTS = (40, 70, 120)
TEE = (70, 150, 146)
GLASS = (92, 108, 122)
WATER = (70, 150, 200)
GREYED = (150, 150, 156)


# ---- clothes: a character whose torso and limbs can be covered -----------------------------------------
class Dressed(Character):
    """top: hoodie/tee/tank colour (None = bare). sleeves: the top covers the arms. bulk: wider torso and arms.
    legs: trouser colour (None = skin). shorts: a shorts colour over bare legs."""

    def __init__(self, name, top=None, legs=None, shorts=None, bulk=1.0, sleeves=True, hood=False, **kw):
        super().__init__(name, **kw)
        self.top, self.legs, self.shorts, self.bulk, self.sleeves, self.hood = top, legs, shorts, bulk, sleeves, hood

    def _cloth(self, ctx, pts, key, rgb, w):
        s = self.scale
        p = wobble_points(ctx, list(pts), key, 0.8)
        path = poly_path(p, closed=False)
        ctx.c.drawPath(path, stroke(LINE, (w + OUT * 2) * s))
        ctx.c.drawPath(path, stroke(rgb, w * s))

    def _limb(self, ctx, pts, key, shade=False, width=LIMB_W):
        part = key[1]
        s = self.scale
        dark = (lambda rgb: mix(rgb, (0, 0, 0), 0.18)) if shade else (lambda rgb: rgb)
        if part == "t":
            w = width * self.bulk
            if self.top:
                if self.hood:
                    hx, hy = pts[1]
                    ctx.c.drawCircle(hx, hy - 4 * s, 24 * s, fill(LINE))
                    ctx.c.drawCircle(hx, hy - 4 * s, 21 * s, fill(dark(mix(self.top, (0, 0, 0), 0.12))))
                self._cloth(ctx, pts, key, self.top, w + 12)
                return
            return super()._limb(ctx, pts, key, shade, w)
        if part in ("af", "an"):
            w = width * (0.55 + 0.45 * self.bulk)
            if self.top and self.sleeves:
                self._cloth(ctx, pts, key, dark(self.top), w + 5)
                hx, hy = pts[-1]
                ctx.c.drawCircle(hx, hy, 10.5 * s, fill(LINE))
                ctx.c.drawCircle(hx, hy, 8 * s, fill(SKIN_SHADE if shade else self.skin))
                return
            return super()._limb(ctx, pts, key, shade, w)
        if part in ("lf", "ln"):
            w = width * (0.7 + 0.3 * self.bulk)
            if self.legs:
                self._cloth(ctx, pts, key, dark(self.legs), w + 3)
                return
            super()._limb(ctx, pts, key, shade, w)
            if self.shorts:
                hip, knee = pts[0], pts[1]
                mid = lerp2(hip, knee, 0.6)
                self._cloth(ctx, [hip, mid], (key, "sh"), dark(self.shorts), w + 6)
            return
        return super()._limb(ctx, pts, key, shade, width)


def nikhil_extra(ctx, hx, hy, f, s):
    # short black hair and swim goggles pushed up on his forehead
    ctx.c.drawPath(poly_path([(hx - 48 * s, hy - 12 * s), (hx - 40 * s, hy - 40 * s), (hx, hy - 54 * s), (hx + 40 * s, hy - 40 * s),
                              (hx + 48 * s, hy - 12 * s), (hx + 26 * s, hy - 34 * s), (hx - 26 * s, hy - 34 * s)], smooth=True),
                   fill((36, 30, 30)))
    ctx.c.drawLine(hx - 50 * s, hy - 26 * s, hx + 50 * s, hy - 26 * s, stroke((40, 40, 46), 4 * s))
    for side in (-1, 1):
        gx = hx + f * 12 * s + side * 15 * s
        ctx.c.drawOval(skia.Rect.MakeXYWH(gx - 11 * s, hy - 36 * s, 22 * s, 16 * s), fill((90, 190, 230)))
        ctx.c.drawOval(skia.Rect.MakeXYWH(gx - 11 * s, hy - 36 * s, 22 * s, 16 * s), stroke(LINE, 2.5 * s))


def big_extra(ctx, hx, hy, f, s):
    # a short black crop and a beard line
    ctx.c.drawPath(poly_path([(hx - 46 * s, hy - 18 * s), (hx - 36 * s, hy - 44 * s), (hx, hy - 54 * s), (hx + 36 * s, hy - 44 * s),
                              (hx + 46 * s, hy - 18 * s), (hx + 24 * s, hy - 36 * s), (hx - 24 * s, hy - 36 * s)], smooth=True),
                   fill((30, 26, 26)))
    fx = hx + f * 14 * s
    ctx.c.drawPath(poly_path([(fx - 30 * s, hy + 6 * s), (fx - 18 * s, hy + 34 * s), (fx, hy + 40 * s), (fx + 18 * s, hy + 34 * s),
                              (fx + 30 * s, hy + 6 * s)], closed=False, smooth=True), stroke((40, 34, 34), 6 * s, 0.7))


def kid_extra(ctx, hx, hy, f, s):
    ctx.c.drawPath(poly_path([(hx - 44 * s, hy - 20 * s), (hx, hy - 52 * s), (hx + 44 * s, hy - 20 * s), (hx + f * 30 * s, hy - 30 * s)],
                             smooth=True), fill((60, 46, 40)))


def make_him(t, top=HOODIE, legs=TROUSERS, shorts=None, hood=True):
    return Dressed("him", top=top, legs=legs, shorts=shorts, hood=hood and top == HOODIE, scale=his_scale(t))


NIKHIL = Dressed("nikhil", skin=(204, 160, 124), top=(220, 140, 60), legs=(60, 64, 80), sleeves=False, extra=nikhil_extra)
NIKHIL_SWIM = Dressed("nikhil", skin=(204, 160, 124), shorts=(200, 80, 60), extra=nikhil_extra)
BIG = Dressed("big", skin=(196, 150, 118), top=(170, 70, 64), legs=(60, 60, 70), bulk=1.75, sleeves=False, scale=1.16, extra=big_extra)
KID = Dressed("kid", skin=(220, 190, 160), top=(120, 104, 96), legs=(56, 60, 70), hood=True, scale=0.9, extra=kid_extra)


def grey(name, scale=1.0, top=None, legs=(70, 70, 78), sleeves=False):
    return Dressed(name, skin=GREYED, top=top, legs=legs, sleeves=sleeves, scale=scale)


def reflection(base, k, g, name=None):
    """A copy of `base` drawn at k times its size, greyed by g (0..1). The reflection that lies."""
    return Dressed(name or base.name + "_r", skin=mix(base.skin, (128, 132, 140), g),
                   top=mix(base.top, (96, 98, 106), g) if base.top else None,
                   legs=mix(base.legs, (70, 72, 80), g) if base.legs else None,
                   shorts=base.shorts, bulk=base.bulk, sleeves=base.sleeves, hood=base.hood,
                   scale=base.scale * k, extra=base.extra)


# ---- shared helpers -------------------------------------------------------------------------
def cap(ctx, k, y=190, size=50, rgb=TEXT, glow_rgb=None):
    t0, t1 = CAPS[k]
    caption(ctx, CAPTIONS[k], t0, t1, y=y, size=size, rgb=rgb, glow_rgb=glow_rgb)


def vline(ctx, k, x, y, size=50):
    t0 = CUES[k]
    villain_text(ctx, VILLAIN[k], t0 - 0.05, t0 + LEN.get(k, 1.4) + 0.5, x, y, size)


def band(ctx, k, y, h=70):
    """A dark strip behind a caption that would sit on something bright."""
    t0, t1 = CAPS[k]
    a = fade(ctx.t, t0, t1, 0.5, 0.5)
    if a > 0:
        ctx.c.drawRect(skia.Rect.MakeXYWH(0, y - h * 0.72, W, h), fill((0, 0, 0), 0.55 * a))


def label(ctx, s, a=1.0):
    draw_text(ctx, s, 60, LETTERBOX + 170, 38, (190, 190, 196), a, align="left")


def speech(ctx, t, who, x, y, **kw):
    _speech(ctx, t, BUBBLES, who, x, y, **kw)


def talk(who, t):
    return _talk(BUBBLES, who, t)


def hud(ctx, t, a=1.0):
    """COMPARED TO, top-left; at the payoff it ends on a word, ME, in gold."""
    a *= prog(t, 0.6, 1.0)
    if a <= 0:
        return
    x, y = 56, LETTERBOX + 26
    rrect(ctx, x, y, 300, 92, 14, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
    draw_text(ctx, "COMPARED TO", x + 20, y + 32, 22, (160, 160, 168), a, align="left")
    if t >= RELABEL:
        k = prog(t, RELABEL, RELABEL + 0.5)
        sz = 52 * (1 + 0.35 * math.sin(math.pi * k))
        draw_text(ctx, "ME", x + 22, y + 80, sz, GOLD, a * k, align="left", face=LG, glow_rgb=GOLD)
        return
    lc = count_changed(t)
    pop = prog(t, lc, lc + 0.35) if lc is not None and lc <= t <= lc + 0.35 else 0.0
    sz = 52 * (1 + 0.35 * math.sin(math.pi * pop) if pop > 0 else 1)
    v = count_at(t)
    draw_text(ctx, f"{v:,}", x + 22, y + 80, sz, RED if v > 1000 else TEXT, a, align="left", face=LG,
              glow_rgb=RED_D if v > 1000 else None)


def stand(ch, ctx, x, f=1, lean=0.04, step=0.0, floor_y=FY, **kw):
    hip, feet = standing(x, floor_y, f, ch.scale, step=step)
    if kw.get("hands"):
        kw["hands"] = free_hands(ch, hip, f, lean, kw["hands"])
    return ch.draw(ctx, hip, f, lean=lean, feet=feet, **kw)


def dumbbell(ctx, x, y, s=1.0, ang=0.0, rgb=(60, 60, 66)):
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.drawLine(-26 * s, 0, 26 * s, 0, stroke(LINE, 9 * s))
    c.drawLine(-26 * s, 0, 26 * s, 0, stroke((150, 150, 156), 5 * s))
    for side in (-1, 1):
        rrect(ctx, side * 26 * s - 9 * s, -18 * s, 18 * s, 36 * s, 4 * s, rgb, LINE, 2.5)
    c.restore()


def curl_hands(J0, f, ph, s=1.0):
    """Hand targets for a dumbbell curl: the near hand goes from the hip up to the shoulder."""
    sh = J0["shoulder"]
    k = 0.5 - 0.5 * math.cos(ph)
    near = (sh[0] + f * lerp(14, 34, k) * s, sh[1] + lerp(96, 22, k) * s)
    far = (sh[0] - f * 4 * s, sh[1] + 96 * s)
    return {"near": near, "far": far}


def physique(ctx, cx, cy, s, rgb=(206, 166, 136), pose=0):
    """A posed physique for the posts: a V-shaped torso, arms up in a double-biceps (pose 0) or on the hips (1)."""
    c = ctx.c
    shw, waist, th = 120 * s, 62 * s, 150 * s
    sy = cy - th / 2
    if pose == 0:
        for side in (-1, 1):
            sh = (cx + side * shw * 0.9, sy + 18 * s)
            el = (cx + side * shw * 1.6, sy + 10 * s)
            hd = (cx + side * shw * 1.5, sy - 70 * s)
            arm = poly_path([sh, el, hd], closed=False)
            c.drawPath(arm, stroke(LINE, 40 * s))
            c.drawPath(arm, stroke(rgb, 33 * s))
            c.drawCircle(lerp(sh[0], el[0], 0.55), sy - 6 * s, 24 * s, fill(rgb))
            c.drawCircle(lerp(sh[0], el[0], 0.55), sy - 6 * s, 24 * s, stroke(LINE, 3 * s))
            c.drawCircle(hd[0], hd[1], 16 * s, fill(rgb))
            c.drawCircle(hd[0], hd[1], 16 * s, stroke(LINE, 3 * s))
    else:
        for side in (-1, 1):
            arm = poly_path([(cx + side * shw * 0.9, sy + 18 * s), (cx + side * shw * 1.25, sy + 80 * s), (cx + side * waist * 1.0, sy + th - 20 * s)],
                            closed=False)
            c.drawPath(arm, stroke(LINE, 40 * s))
            c.drawPath(arm, stroke(rgb, 33 * s))
    torso = poly_path([(cx - shw, sy), (cx + shw, sy), (cx + waist, sy + th), (cx - waist, sy + th)], smooth=False)
    c.drawPath(torso, fill(rgb))
    c.drawPath(torso, stroke(LINE, 4 * s))
    c.drawLine(cx, sy + 20 * s, cx, sy + th - 10 * s, stroke(mix(rgb, LINE, 0.4), 3 * s))
    for k in range(3):
        y = sy + (70 + k * 26) * s
        c.drawLine(cx - 26 * s, y, cx + 26 * s, y, stroke(mix(rgb, LINE, 0.35), 3 * s))
    c.drawPath(poly_path([(cx - 70 * s, sy + 34 * s), (cx - 6 * s, sy + 50 * s)], closed=False), stroke(mix(rgb, LINE, 0.35), 3 * s))
    c.drawPath(poly_path([(cx + 70 * s, sy + 34 * s), (cx + 6 * s, sy + 50 * s)], closed=False), stroke(mix(rgb, LINE, 0.35), 3 * s))
    rrect(ctx, cx - waist - 4 * s, sy + th - 4 * s, (waist + 4 * s) * 2, 46 * s, 8 * s, (40, 40, 48), LINE, 3)
    c.drawCircle(cx, sy - 42 * s, 40 * s, fill(rgb))
    c.drawCircle(cx, sy - 42 * s, 40 * s, stroke(LINE, 4 * s))
    c.drawRect(skia.Rect.MakeXYWH(cx - 14 * s, sy - 8 * s, 28 * s, 12 * s), fill(rgb))


HANDLES = ["@shred.max", "@aesthetic.raj", "@vtaper", "@iron.dev", "@cutsquad", "@alpha.arms", "@leanking", "@bulk.season"]
LIKES = ["84.2K", "1.2M", "310K", "96K", "2.4M", "540K", "77K", "1.9M"]


def heart(ctx, x, y, r, rgb):
    p = poly_path([(x, y + r), (x - r * 1.1, y - r * 0.1), (x - r * 0.6, y - r * 0.8), (x, y - r * 0.35),
                   (x + r * 0.6, y - r * 0.8), (x + r * 1.1, y - r * 0.1)], smooth=True)
    ctx.c.drawPath(p, fill(rgb))


def post(ctx, x0, y0, w, i, a=1.0, muted=0.0):
    """One post in the feed, w wide, at the top-left (x0, y0). Returns its height."""
    h = w * 1.25 + 130
    c = ctx.c
    c.saveLayerAlpha(None, int(255 * a))
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), fill((24, 24, 30)))
    wcircle(ctx, x0 + 40, y0 + 36, 20, ("pav", i), mix((200, 120, 80), (90, 130, 200), (i % 3) / 2), LINE, 2)
    draw_text(ctx, HANDLES[i % len(HANDLES)], x0 + 72, y0 + 46, 30, TEXT, align="left")
    iy = y0 + 72
    bg = skia.GradientShader.MakeLinear([(0, iy), (0, iy + w * 1.25)], [col((60, 50, 56)), col((150, 90, 70))])
    c.drawRect(skia.Rect.MakeXYWH(x0, iy, w, w * 1.25), skia.Paint(Shader=bg))
    glow(ctx, x0 + w * 0.7, iy + w * 0.3, w * 0.6, (255, 200, 150), 0.35)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x0, iy, w, w * 1.25))
    physique(ctx, x0 + w / 2, iy + w * 0.78, w / 520, pose=i % 2)
    c.restore()
    heart(ctx, x0 + 36, iy + w * 1.25 + 34, 14, RED)
    draw_text(ctx, LIKES[i % len(LIKES)], x0 + 64, iy + w * 1.25 + 46, 30, TEXT, align="left")
    if muted > 0:
        c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), fill((30, 30, 34), 0.82 * muted))
    c.restore()
    return h


# ---- mirrors ----------------------------------------------------------------------------------
class Mirror:
    def __init__(self, x, y, w, h, key, frame=(150, 150, 156)):
        self.x, self.y, self.w, self.h, self.key, self.frame = x, y, w, h, key, frame

    def back(self, ctx, glass=GLASS):
        wrect(ctx, self.x - 12, self.y - 12, self.w + 24, self.h + 24, self.key, self.frame, LINE, 4, seg=3)
        g = skia.GradientShader.MakeLinear([(self.x, self.y), (self.x + self.w, self.y + self.h)],
                                           [col(mix(glass, (255, 255, 255), 0.12)), col(glass), col(mix(glass, (0, 0, 0), 0.15))])
        ctx.c.drawRect(skia.Rect.MakeXYWH(self.x, self.y, self.w, self.h), skia.Paint(Shader=g))

    def inside(self, ctx):
        m = self

        class _M:
            def __enter__(s):
                ctx.c.save()
                ctx.c.clipRect(skia.Rect.MakeXYWH(m.x, m.y, m.w, m.h))

            def __exit__(s, *a):
                for i in range(2):
                    x = m.x + 40 + i * 70
                    ctx.c.drawLine(x, m.y + 30, x + 150, m.y + 200, stroke((255, 255, 255), 14 - 6 * i, 0.07))
                ctx.c.restore()

        return _M()


def refl_floor(ctx, m, y, rgb=(70, 74, 82)):
    """The floor seen in the mirror, so a reflection stands on something."""
    ctx.c.drawRect(skia.Rect.MakeXYWH(m.x, y, m.w, m.y + m.h - y), fill(rgb))
    ctx.c.drawLine(m.x, y, m.x + m.w, y, stroke(mix(rgb, (0, 0, 0), 0.3), 3))


# ---- the gym ----------------------------------------------------------------------------------
GYM_M = Mirror(900, 150, 700, 610, "gymm")


def gym(ctx, t, lights=1.0):
    c = ctx.c
    P.back_wall(ctx, rgb=(34, 36, 42))
    for i in range(3):  # overhead strip lights
        x = 300 + i * 600
        c.drawRect(skia.Rect.MakeXYWH(x - 120, 92, 240, 12), fill((236, 240, 244)))
        cone(ctx, (x, 104), (x - 360, FY), (x + 360, FY), (230, 236, 255), 0.05 * lights)
    # dumbbell rack, left
    wrect(ctx, 120, 560, 520, 18, "rack1", (80, 80, 88), LINE, 3, seg=3)
    wrect(ctx, 120, 680, 520, 18, "rack2", (80, 80, 88), LINE, 3, seg=3)
    for i in range(7):
        dumbbell(ctx, 160 + i * 72, 545, 0.8 + i * 0.06)
        dumbbell(ctx, 160 + i * 72, 665, 0.9 + i * 0.07)
    for x in (130, 630):
        c.drawLine(x, 560, x, FY, stroke(LINE, 8))
    rrect(ctx, 270, 330, 280, 90, 10, (190, 60, 50), LINE, 4)
    draw_text(ctx, "IRON HOUSE", 410, 390, 42, TEXT, face=LG)
    GYM_M.back(ctx, glass=(62, 74, 88))
    P.floor(ctx, FY, rgb=(44, 44, 50))


def curler(ctx, t, ch, x, f, ph, db_s=1.0, lean=0.06, **kw):
    """A character curling a dumbbell at x; returns the joints."""
    hip, feet = standing(x, FY, f, ch.scale)
    J0 = ch.joints(hip, f, lean)
    hands = curl_hands(J0, f, ph, ch.scale)
    J = ch.draw(ctx, hip, f, lean=lean, feet=feet, hands=hands, **kw)
    hp = J["limbs"]["arm_near"][2]
    dumbbell(ctx, hp[0], hp[1], db_s * ch.scale, ang=90)
    return J


def refl_curler(ch, k, g, x, f, ph, db_s=1.0, lean=0.06, **kw):
    """Draw a reflection curling too (the mirror copy of curler) inside the open mirror clip."""
    def run(ctx):
        r = reflection(ch, k, g)
        hip, feet = standing(x, 742, f, r.scale)
        J0 = r.joints(hip, f, lean)
        J = r.draw(ctx, hip, f, lean=lean, feet=feet, hands=curl_hands(J0, f, ph, r.scale), **kw)
        hp = J["limbs"]["arm_near"][2]
        dumbbell(ctx, hp[0], hp[1], db_s * r.scale, ang=90)
        return J
    return run


# ---- the hook ---------------------------------------------------------------------------------------
def s01(ctx, t):
    glance = any(g - 0.5 <= t <= g + 0.9 for g in EVENTS["glance"])
    k = refl_at(t)
    him = make_him(t)
    with Camera(lerp(1.56, 1.45, ease(prog(t, 0, 6))), 900, 470).apply(ctx):
        gym(ctx, t)
        with GYM_M.inside(ctx):
            refl_floor(ctx, GYM_M, 700)
            refl_curler(BIG, 0.92, 0.0, 1040, -1, t * 2.6, 1.3, expr="determined", look=(-1, 0.0))(ctx)
            refl_curler(him, k, 0.75, 1330, -1, t * 2.2, 1.0, lean=0.22, expr="sad", look=(-1, 0.6))(ctx)
        curler(ctx, t, BIG, 720, 1, t * 2.6, 1.3, expr="determined", look=(1, 0.0))
        J = curler(ctx, t, him, 500, 1, t * 2.2, 1.0, lean=0.1, expr="worried" if glance else "tired",
                   look=(1, -0.3) if glance else (1, 0.1))
    cap(ctx, "C1", y=985)
    hud(ctx, t)


# ---- night, the feed ------------------------------------------------------------------------------
def bedroom(ctx, t, night=True, morning=0.0):
    c = ctx.c
    P.back_wall(ctx, rgb=mix((24, 24, 32), (70, 64, 60), morning) if night else (60, 58, 60))
    P.floor(ctx, FY)
    P.window(ctx, 380, 210, 220, 220, "bwin", night=morning < 0.5, moon=False,
             sky=mix((22, 26, 40), (236, 212, 170), morning))
    if morning > 0:
        glow(ctx, 490, 320, 380, (255, 220, 160), 0.3 * morning)
    # the shelf: his old swim medal and a photo of two boys in a pool
    wrect(ctx, 690, 330, 220, 12, "bshelf", (92, 74, 60), LINE, 3, seg=2)
    c.drawLine(740, 250, 760, 292, stroke((60, 110, 200), 5))
    c.drawLine(780, 250, 760, 292, stroke((200, 60, 60), 5))
    c.drawCircle(760, 304, 18, fill(GOLD))
    c.drawCircle(760, 304, 18, stroke(LINE, 3))
    draw_text(ctx, "1", 760, 313, 22, (120, 80, 20), face=LG)
    rrect(ctx, 806, 260, 80, 66, 4, (236, 232, 220), LINE, 2)
    c.drawRect(skia.Rect.MakeXYWH(812, 266, 68, 54), fill(WATER))
    for i, px in enumerate((832, 858)):
        c.drawCircle(px, 292, 9, fill((236, 230, 214) if i == 0 else (204, 160, 124)))
        c.drawCircle(px, 292, 9, stroke(LINE, 1.5))
    c.drawLine(812, 300, 880, 300, stroke((220, 240, 255), 2))


WARD_M = Mirror(1130, 190, 300, 570, "wardm", frame=(120, 96, 76))


def wardrobe(ctx):
    wrect(ctx, 1080, 150, 400, 630, "ward", (96, 76, 62), LINE, 4, seg=3)
    WARD_M.back(ctx, glass=(84, 96, 110))


def h1(ctx, t):
    posts = EVENTS["posts"]
    i = sum(1 for p in posts if t >= p)
    slide = ease(prog(t, posts[i - 1], posts[i - 1] + 0.3)) if i > 0 else 1.0
    with Camera(1.5, 760, 470).apply(ctx):
        bedroom(ctx, t)
        P.bed(ctx, 300, FY, 640, key="bed")
        hip, feet = seated(560, 690, 1, floor_y=FY)
        him = make_him(t)
        J0 = him.joints(hip, 1, -0.12)
        sh = J0["shoulder"]
        thumb = 4 * math.sin(t * 6) if any(p - 0.4 < t < p for p in posts) else 0.0
        hands = {"near": (sh[0] + 64, sh[1] + 40 + thumb), "far": (sh[0] + 50, sh[1] + 46)}
        J = him.draw(ctx, hip, 1, lean=-0.12, feet=feet, expr="sad", look=(1, 0.6), screen_glow=1.0,
                     hands=free_hands(him, hip, 1, -0.12, hands), glow_rgb=BLUE)
        hp = J["limbs"]["arm_near"][2]
        P.phone_held(ctx, hp[0], hp[1], on=1.0)
    # the feed, close
    UI = P.PhoneUI(1430, 520, 440, 780)
    UI.body(ctx, 1.0)
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        ph = 0
        for k in range(2):
            j = max(0, i - 1 + k)
            yy = y0 + 40 + (k - slide) * 620 + 620
            ph = post(ctx, x0, yy - 620, UI.w - 36, j)
    cap(ctx, "C2", y=985)
    hud(ctx, t)


# ---- the wound -----------------------------------------------------------------------------------
def at_mirror(ctx, t, x=880, k=None, g=0.75, expr="sad", look=(1, 0.2), villain_k=0.0, refl_x=1320, **kw):
    him = make_him(t)
    k = refl_at(t) if k is None else k
    with WARD_M.inside(ctx):
        refl_floor(ctx, WARD_M, 700, rgb=(60, 58, 62))
        r = reflection(him, k, g)
        hip, feet = standing(refl_x, 742, -1, r.scale)
        r.draw(ctx, hip, -1, lean=0.12 + 0.4 * (0.64 - k), feet=feet, expr="hurt", look=(-1, 0.7))
    return stand(him, ctx, x, f=1, lean=0.04, expr=expr, look=look, **kw)


def s02(ctx, t):
    t0, t1 = EVENTS["born"]
    born = ease(prog(t, t0, t1))
    with Camera(lerp(1.6, 1.75, ease(prog(t, 14, 23))), 1080, 470).apply(ctx):
        bedroom(ctx, t)
        glow(ctx, 1560, 520, 300, RED, 0.22 * born)
        wardrobe(ctx)
        if born > 0:
            P.villain(ctx, 1600, FY, scale=lerp(0.3, 1.0, born), alpha=born, grin=ease(prog(t, 15.6, 16.2)), lean=-0.3)
        at_mirror(ctx, t, expr="worried" if t < 16 else "hurt")
    vline(ctx, "V1", 400, 640, 58)
    vline(ctx, "V2", 400, 720, 54)
    hud(ctx, t)


# ---- the stakes --------------------------------------------------------------------------------------
def gym_front(ctx, t):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, FY)], [col((120, 160, 210)), col((230, 214, 186))])
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), skia.Paint(Shader=sky))
    wrect(ctx, 200, 200, 1500, 580, "gfront", (96, 92, 96), LINE, 4, seg=3)
    rrect(ctx, 640, 230, 520, 110, 12, (190, 60, 50), LINE, 4)
    draw_text(ctx, "IRON HOUSE GYM", 900, 306, 58, TEXT, face=LG)
    wrect(ctx, 820, 400, 180, 380, "gdoor", (50, 60, 70), LINE, 4, seg=2)
    c.drawRect(skia.Rect.MakeXYWH(836, 420, 148, 200), fill((90, 120, 140), 0.6))
    for i, wx in enumerate((300, 1180)):
        wrect(ctx, wx, 420, 300, 200, ("gw", i), (110, 140, 160), LINE, 4, seg=2)
    P.floor(ctx, FY, rgb=(110, 106, 100))


def b1(ctx, t):
    him = make_him(t)
    with Camera(1.55, 960, 480).apply(ctx):
        gym_front(ctx, t)
        Jn = stand(NIKHIL, ctx, 720, f=1, lean=0.02, expr="happy", look=(1, -0.1), mouth_open=talk("nikhil", t))
        # the towel round his neck
        sh = Jn["shoulder"]
        ctx.c.drawPath(poly_path([(sh[0] - 30, sh[1] - 10), (sh[0], sh[1] + 4), (sh[0] + 30, sh[1] - 10)], closed=False, smooth=True),
                       stroke((240, 240, 236), 18))
        ctx.c.drawLine(sh[0] + 24, sh[1] - 6, sh[0] + 28, sh[1] + 60, stroke((240, 240, 236), 16))
        J = stand(him, ctx, 1100, f=-1, lean=0.06, expr="worried" if t < 26 else "sad", look=(-1, 0.3) if t < 26 else (-1, 0.8),
                  mouth_open=talk("him", t))
        # gym bag on his far shoulder
        hp = J["limbs"]["arm_far"][2]
        rrect(ctx, hp[0] - 50, hp[1] - 10, 100, 50, 14, (40, 40, 46), LINE, 3)
        speech(ctx, t, "nikhil", Jn["head"][0] + 40, Jn["head"][1] - 70)
        speech(ctx, t, "him", J["head"][0] - 30, J["head"][1] - 70)
    hud(ctx, t)


# ---- the grind --------------------------------------------------------------------------------------
def g1(ctx, t):
    i = min(3, int((t - G1_T0) // G1_WEEK))
    n0 = G1_T0 + i * G1_WEEK
    k = refl_at(t)
    him = make_him(t)
    db = 1.0 + 0.18 * i
    with Camera(1.45, 900, 470).apply(ctx):
        gym(ctx, t)
        with GYM_M.inside(ctx):
            refl_floor(ctx, GYM_M, 700)
            refl_curler(grey("g1", 1.0, top=(60, 62, 70)), 0.92, 0.3, 1040, -1, t * 2.0 + i, 1.1, look=(-1, 0.0))(ctx)
            refl_curler(him, k, 0.7 + 0.06 * i, 1330, -1, t * 2.4, db, lean=0.2 + 0.05 * i, expr="hurt", look=(-1, 0.6))(ctx)
        if i >= 1:
            P.villain(ctx, 260, FY, scale=0.9 + 0.08 * i, alpha=0.5 + 0.15 * i, grin=1.0, lean=0.3)
        curler(ctx, t, grey("g1", 1.0, top=(60, 62, 70)), 720, 1, t * 2.0 + i, 1.1, look=(1, 0.0))
        curler(ctx, t, him, 500, 1, t * 2.4, db, lean=0.1, expr="determined" if t - n0 > 1.4 else "worried",
               look=(1, 0.0) if t - n0 > 1.4 else (1, -0.2))
    black(ctx, 1 - prog(t, n0, n0 + 0.1))
    label(ctx, G1_LABELS[i])
    vline(ctx, "V3", 1280, 250, 56)
    vline(ctx, "V4", 1280, 250, 56)
    vline(ctx, "V5", 1280, 250, 54)
    hud(ctx, t)


def hot_street(ctx, t):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, FY)], [col((150, 196, 236)), col((250, 226, 170))])
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, FY), skia.Paint(Shader=sky))
    glow(ctx, 1500, 160, 420, (255, 236, 160), 0.6)
    c.drawCircle(1500, 160, 70, fill((255, 240, 170)))
    for i in range(8):
        bx = -200 + i * 300
        bh = 280 + 120 * hrand("hb", i)
        c.drawRect(skia.Rect.MakeXYWH(bx, FY - bh, 270, bh), fill(mix((200, 170, 140), (170, 150, 150), hrand("hc", i))))
        for j in range(2):
            c.drawRect(skia.Rect.MakeXYWH(bx + 40 + j * 110, FY - bh + 50, 70, 60), fill((120, 130, 150)))
    # the pharmacy sign with the temperature
    rrect(ctx, 860, 330, 260, 120, 10, (20, 24, 22), LINE, 4)
    draw_text(ctx, "38°C", 990, 420, 84, (255, 110, 60), face=LG, glow_rgb=(160, 40, 20))
    for i in range(6):  # heat shimmer
        y = FY - 30 - i * 14
        pts = [(x, y + math.sin(x * 0.02 + t * 4 + i) * 4) for x in range(-200, 2200, 80)]
        c.drawPath(poly_path(pts, closed=False, smooth=True), stroke((255, 255, 255), 2, 0.06))
    P.floor(ctx, FY, rgb=(150, 140, 126))


def g2(ctx, t):
    him = make_him(t)
    x, ph = walk_x(560, t - 49.0, 90)
    with Camera(1.5, 960, 480).apply(ctx):
        hot_street(ctx, t)
        for j, (px, f, top) in enumerate(((380, 1, (220, 200, 90)), (1340, -1, (230, 120, 110)), (1560, -1, (120, 190, 160)))):
            ch = grey(f"hs{j}", 1.0, top=top)
            hip, feet = standing(px, FY, f)
            J0 = ch.joints(hip, f, 0.02)
            fan = math.sin(t * 9 + j) * 8
            sh = J0["shoulder"]
            Jh = ch.draw(ctx, hip, f, lean=0.02, feet=feet, expr="tired", look=(f, 0.0),
                         hands={"near": (sh[0] + f * 84, sh[1] - 4 + fan)})
            hp = Jh["limbs"]["arm_near"][2]
            ctx.c.save()
            ctx.c.translate(hp[0], hp[1])
            ctx.c.rotate(-f * 30 + 20 * math.sin(t * 9 + j))
            ctx.c.drawPath(poly_path([(0, 0), (-26, -50), (26, -50)]), fill((236, 230, 210)))
            ctx.c.drawPath(poly_path([(0, 0), (-26, -50), (26, -50)]), stroke(LINE, 3))
            ctx.c.restore()
        hip, feet = standing(x, FY, 1, him.scale, step=ph)
        J = him.draw(ctx, hip, 1, lean=0.08, feet=feet, expr="tired", look=(1, 0.5))
        for k in range(2):
            sweat(ctx, J, 1.0, 0.6 + 0.4 * math.sin(t * 3 + k))
    cap(ctx, "C3", y=985)
    hud(ctx, t)


def g3(ctx, t):
    flash = EVENTS["photo_flash"]
    him = make_him(t)
    behind = ease(prog(t, 57.0, 58.4))
    shot = t >= flash
    with Camera(1.5, 960, 480).apply(ctx):
        P.back_wall(ctx, rgb=(64, 54, 60))
        for i in range(12):  # string lights at the café
            x = 300 + i * 120
            y = 220 + 30 * math.sin(i * 0.9)
            glow(ctx, x, y, 40, (255, 220, 150), 0.4)
            ctx.c.drawCircle(x, y, 7, fill((255, 230, 170)))
        ctx.c.drawPath(poly_path([(300 + i * 120, 220 + 30 * math.sin(i * 0.9)) for i in range(12)], closed=False, smooth=True),
                       stroke(LINE, 2))
        P.floor(ctx, FY)
        # the waiter taking the photo, the phone held out at chest height
        wt = grey("waiter", 1.0, top=(230, 230, 226))
        Jw = stand(wt, ctx, 560, f=1, lean=0.06, expr="smile", look=(1, 0.0), hands={"near": (630, 590), "far": (620, 596)})
        hp = Jw["limbs"]["arm_near"][2]
        rrect(ctx, hp[0] - 6, hp[1] - 60, 16, 64, 4, (40, 40, 46), LINE, 2.5)
        # him stepping in behind the tallest
        stand(him, ctx, lerp(1440, 1150, behind), f=-1, lean=0.04, expr="worried", look=(-1, 0.2),
              step=behind * 3 if 0 < behind < 1 else 0.0)
        cols = [(200, 90, 80), (90, 150, 200), (230, 190, 80), (120, 170, 110)]
        xs = [820, 970, 1110, 1270]
        for j, x in enumerate(xs):
            ch = Dressed(f"fr{j}", skin=(214, 180, 150) if j % 2 else (196, 156, 126), top=cols[j], legs=(60, 60, 70),
                         sleeves=False, scale=1.16 if j == 2 else 1.0, extra=nikhil_extra if j == 0 else None)
            stand(ch, ctx, x, f=-1, lean=0.0, expr="happy", look=(-1, 0.0))
    if shot:
        a = 1 - prog(t, flash, flash + 0.35)
        ctx.c.drawRect(skia.Rect.MakeWH(W, H), fill((255, 255, 255), 0.9 * a))
        # the photo: a white border frames what the phone kept
        paper = (240, 238, 232)
        ctx.c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 60), fill(paper))
        ctx.c.drawRect(skia.Rect.MakeXYWH(0, H - 170, W, 170), fill(paper))
        ctx.c.drawRect(skia.Rect.MakeXYWH(0, 0, 60, H), fill(paper))
        ctx.c.drawRect(skia.Rect.MakeXYWH(W - 60, 0, 60, H), fill(paper))
    cap(ctx, "C4", y=985 if not shot else 975, rgb=TEXT if not shot else (40, 40, 46))
    if not shot:
        hud(ctx, t)


# ---- rock bottom --------------------------------------------------------------------------------------
def r1(ctx, t):
    him = make_him(t)
    morning = 0.7
    if t < 68.0:
        with Camera(1.5, 760, 470).apply(ctx):
            bedroom(ctx, t, morning=morning)
            P.bed(ctx, 760, FY, 640, key="bed")
            hip, feet = seated(640, 690, 1)
            J0 = him.joints(hip, 1, 0.2)
            sh = J0["shoulder"]
            J = him.draw(ctx, hip, 1, lean=0.2, feet=feet, expr="hurt" if t > EVENTS["nikhil_post"] + 0.6 else "tired",
                         look=(1, 0.8), hands=free_hands(him, hip, 1, 0.2, {"near": (sh[0] + 60, sh[1] + 54), "far": (sh[0] + 50, sh[1] + 60)}))
            hp = J["limbs"]["arm_near"][2]
            P.phone_held(ctx, hp[0], hp[1], on=1.0)
        UI = P.PhoneUI(1430, 520, 440, 780)
        UI.body(ctx, 1.0)
        a = ease(prog(t, EVENTS["nikhil_post"], EVENTS["nikhil_post"] + 0.3))
        with UI.screen(ctx):
            x0, y0 = UI.x0 + 18, UI.y0 + 18
            ctx.c.drawRect(skia.Rect.MakeXYWH(x0, y0, UI.w - 36, UI.h - 36), fill((24, 24, 30), a))
            if a > 0:
                ctx.c.saveLayerAlpha(None, int(255 * a))
                wcircle(ctx, x0 + 40, y0 + 60, 20, "nav", (204, 160, 124), LINE, 2)
                draw_text(ctx, "nikhil", x0 + 72, y0 + 70, 30, TEXT, align="left")
                iy, iw = y0 + 100, UI.w - 36
                ctx.c.drawRect(skia.Rect.MakeXYWH(x0, iy, iw, iw), fill(WATER))
                for k2 in range(5):
                    ctx.c.drawLine(x0, iy + 80 + k2 * 60, x0 + iw, iy + 80 + k2 * 60, stroke((200, 236, 255), 3, 0.4))
                for j, (px, sk) in enumerate(((x0 + 90, (204, 160, 124)), (x0 + 190, (214, 180, 150)), (x0 + 290, (196, 156, 126)))):
                    ctx.c.drawCircle(px, iy + 170, 40, fill(sk))
                    ctx.c.drawCircle(px, iy + 170, 40, stroke(LINE, 3))
                    ctx.c.drawPath(poly_path([(px - 14, iy + 180), (px, iy + 192), (px + 14, iy + 180)], closed=False, smooth=True), stroke(LINE, 3))
                    ctx.c.drawLine(px - 50, iy + 214, px + 50, iy + 214, stroke((220, 245, 255), 4))
                draw_text(ctx, "missed you again bro", x0 + 24, iy + iw + 60, 34, TEXT, align="left")
                draw_text(ctx, "SUNDAY 7:40 AM", x0 + 24, iy + iw + 110, 24, (150, 150, 160), align="left")
                ctx.c.restore()
    else:
        rise = ease(prog(t, 68.6, 71.4))
        towel = prog(t, EVENTS["towel"], EVENTS["towel"] + 0.6)
        with Camera(lerp(1.6, 1.85, ease(prog(t, 68, 80))), 1120, 470, shake=1.2 * prog(t, 71, 74) * (t < 75)).apply(ctx):
            bedroom(ctx, t, morning=morning)
            glow(ctx, 1560, 500, 380, RED, 0.25 * rise)
            wardrobe(ctx)
            P.villain(ctx, 1620, FY, scale=lerp(0.9, 1.35, rise), alpha=0.6 + 0.4 * rise, grin=1.2, lean=-0.35)
            hip, feet = standing(880, FY, 1, him.scale)
            J0 = him.joints(hip, 1, 0.04)
            sh = J0["shoulder"]
            throw = towel > 0
            if throw:
                hands = {"near": (sh[0] + lerp(110, 60, towel), sh[1] + lerp(-60, 80, towel))}
            else:
                hands = {"near": (sh[0] + 40, sh[1] + 92)}
            with WARD_M.inside(ctx):
                refl_floor(ctx, WARD_M, 700, rgb=(60, 58, 62))
                r = reflection(him, refl_at(t), 0.85)
                hipr, feetr = standing(1320, 742, -1, r.scale)
                r.draw(ctx, hipr, -1, lean=0.35, feet=feetr, expr="hurt", look=(-1, 0.9))
            J = him.draw(ctx, hip, 1, lean=0.04 if t < EVENTS["towel"] + 0.6 else 0.18, feet=feet,
                         expr="hurt" if t < EVENTS["towel"] else "closed", look=(1, 0.3),
                         hands=free_hands(him, hip, 1, 0.04, hands))
            # the towel: in his hand, then thrown over the glass
            if t < EVENTS["towel"]:
                hp = J["limbs"]["arm_near"][2]
                ctx.c.drawRect(skia.Rect.MakeXYWH(hp[0] - 14, hp[1], 28, 70), fill((236, 236, 230)))
                ctx.c.drawRect(skia.Rect.MakeXYWH(hp[0] - 14, hp[1], 28, 70), stroke(LINE, 2.5))
            else:
                k = ease(towel)
                m = WARD_M
                top = lerp(m.y + 300, m.y - 16, k)
                bot = lerp(top + 90, m.y + m.h - 20, k)
                wave = [(m.x + m.w + 24 - i * (m.w + 48) / 8, bot + (12 if i % 2 else -4)) for i in range(9)]
                sheet = poly_path([(m.x - 20, top), (m.x + m.w + 20, top)] + wave)
                ctx.c.drawPath(sheet, fill((236, 236, 230)))
                ctx.c.drawPath(sheet, stroke(LINE, 3))
                for s_ in range(3):
                    ctx.c.drawLine(m.x + 40 + s_ * 100, top + 20, m.x + 50 + s_ * 100, lerp(top + 60, m.y + m.h - 60, k), stroke((200, 200, 196), 3))
        vline(ctx, "V6", 380, 420, 60)
        band(ctx, "C5", 990)
        cap(ctx, "C5", y=990)
    hud(ctx, t)


# ---- the turn: the big man's photo --------------------------------------------------------------------
def t1(ctx, t):
    him = make_him(t)
    s0, s1 = EVENTS["shots"]
    shooting = s0 <= t < s1 + 0.3
    n = 0 if t < s0 else min(PHOTOS, 1 + int((t - s0) / (s1 - s0) * (PHOTOS - 1)))
    b0, b1_ = EVENTS["big_shrink"]
    shrink = ease(prog(t, b0, b1_))
    scrolling = t >= EVENTS["big_scroll"]
    holding = 84.6 <= t < 92.8  # he holds the big man's phone
    pose = 0.0 if not (85.4 <= t < 92.0) else ease(prog(t, 85.4, 86.0))
    pump = 0.08 * math.sin(t * 3.5) * pose
    with Camera(lerp(1.45, 1.62, ease(prog(t, 92, 98))), 900, 470).apply(ctx):
        gym(ctx, t)
        big_r = Dressed("big_r", skin=BIG.skin, top=BIG.top, legs=BIG.legs, bulk=BIG.bulk + pump, sleeves=False,
                        scale=BIG.scale, extra=big_extra)
        with GYM_M.inside(ctx):
            refl_floor(ctx, GYM_M, 700)
            r = reflection(big_r, lerp(0.92, 0.6, shrink), 0.85 * shrink)
            hip, feet = standing(1040, 742, -1, r.scale)
            J0 = r.joints(hip, -1, 0.02)
            sh = J0["shoulder"]
            hs = {"near": (sh[0] - 92 * r.scale, sh[1] - 36 * r.scale), "far": (sh[0] + 56 * r.scale, sh[1] - 40 * r.scale)} if pose > 0.5 else None
            if scrolling:
                hs = {"near": (sh[0] - 50 * r.scale, sh[1] + 52 * r.scale)}
            r.draw(ctx, hip, -1, lean=0.02 + 0.2 * shrink, feet=feet, hands=hs, expr="hurt" if scrolling else "determined", look=(-1, 0.6 if scrolling else 0.0))
            rh = reflection(him, refl_at(t), 0.75)
            hip, feet = standing(1330, 742, -1, rh.scale)
            rh.draw(ctx, hip, -1, lean=0.3, feet=feet, expr="sad", look=(-1, 0.3))
        # the big man posing at the mirror
        hip, feet = standing(720, FY, 1, BIG.scale)
        big = Dressed("big", skin=BIG.skin, top=BIG.top, legs=BIG.legs, bulk=BIG.bulk + pump, sleeves=False, scale=BIG.scale, extra=big_extra)
        J0 = big.joints(hip, 1, 0.02)
        sh = J0["shoulder"]
        if pose > 0.5:
            hs = {"near": (sh[0] + 92, sh[1] - 36), "far": (sh[0] - 56, sh[1] - 40)}
        elif scrolling:
            hs = {"near": (sh[0] + 56, sh[1] + 56), "far": (sh[0] + 46, sh[1] + 62)}
        elif t < 84.6:
            hs = {"near": (sh[0] - 40, sh[1] + 70)}
        else:
            hs = None
        Jb = big.draw(ctx, hip, 1 if t >= 84.6 else -1, lean=0.02, feet=feet, hands=free_hands(big, hip, 1, 0.02, hs) if hs else None,
                      expr="hurt" if scrolling else ("determined" if pose > 0.5 else "neutral"),
                      look=(1, 0.7) if scrolling else (1, 0.0), mouth_open=talk("big", t))
        if scrolling or t < 84.6:
            hp = Jb["limbs"]["arm_near"][2]
            P.phone_held(ctx, hp[0], hp[1], on=1.0)
        # him with the phone, shooting the mirror
        hip, feet = standing(480, FY, 1, him.scale)
        J0 = him.joints(hip, 1, 0.04)
        sh = J0["shoulder"]
        hands = {"near": (sh[0] + 76, sh[1] - 6), "far": (sh[0] + 66, sh[1])} if holding else None
        J = him.draw(ctx, hip, 1, lean=0.04, feet=feet, hands=free_hands(him, hip, 1, 0.04, hands) if hands else None,
                     expr="worried" if t < 93 else ("shocked" if t < 96 else "hopeful"), look=(1, 0.0))
        if holding:
            hp = J["limbs"]["arm_near"][2]
            rrect(ctx, hp[0] - 10, hp[1] - 60, 20, 66, 4, (40, 40, 46), LINE, 2.5)
            if shooting and (t - s0) % 0.1 < 0.03:
                glow(ctx, hp[0] + 10, hp[1] - 30, 120, (255, 255, 255), 0.6)
        speech(ctx, t, "big", Jb["head"][0] + 150, Jb["head"][1] - 90)
    if 85.4 <= t < 92.8 and n > 0:
        a = fade(t, s0, 92.8, 0.15, 0.3)
        rrect(ctx, W - 380, LETTERBOX + 26, 320, 92, 14, (0, 0, 0), (60, 60, 66), 2, a=a * 0.65)
        draw_text(ctx, "PHOTO", W - 360, LETTERBOX + 58, 22, (160, 160, 168), a, align="left")
        draw_text(ctx, str(n), W - 358, LETTERBOX + 106, 52, TEXT, a, align="left", face=LG)
    cap(ctx, "C6", y=925)
    cap(ctx, "C7", y=995)
    hud(ctx, t)


# ---- the lesson and the practice -------------------------------------------------------------------
def l1(ctx, t):
    a = ease(prog(t, EVENTS["lesson"], EVENTS["lesson"] + 0.6))
    c = ctx.c
    c.saveLayerAlpha(None, int(255 * a))
    c.save()
    c.translate(W / 2, 560)
    c.scale(1.18, 1.18)
    c.translate(-W / 2, -560)
    # left: their photo, one frame
    px, py, pw, ph = 330, 330, 420, 500
    rrect(ctx, px - 16, py - 16, pw + 32, ph + 70, 6, (236, 232, 220), LINE, 4)
    g = skia.GradientShader.MakeLinear([(0, py), (0, py + ph)], [col((60, 50, 56)), col((150, 90, 70))])
    c.drawRect(skia.Rect.MakeXYWH(px, py, pw, ph), skia.Paint(Shader=g))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(px, py, pw, ph))
    glow(ctx, px + pw * 0.7, py + 120, 260, (255, 200, 150), 0.4)
    physique(ctx, px + pw / 2, py + ph * 0.66, 0.62, pose=0)
    c.restore()
    draw_text(ctx, "THEIR PHOTO", px + pw / 2, py - 50, 44, TEXT, face=LG)
    for i, s in enumerate(["1 SECOND", "37 TRIES", "BEST LIGHT", "PUMPED", "EDITED"]):
        k = ease(prog(t, 101.0 + i * 0.5, 101.4 + i * 0.5))
        draw_text(ctx, s, px + pw + 50, py + 70 + i * 64, 36, GOLD if i == 1 else (230, 200, 160), k, align="left", face=LG)
    # right: his mirror, a strip of ordinary days
    k2 = ease(prog(t, 103.6, 104.4))
    draw_text(ctx, "HIS MIRROR", 1420, py - 50, 44, TEXT, k2, face=LG)
    for i in range(10):
        fx = 1180 + (i % 5) * 96
        fy = py + (i // 5) * 190
        kk = ease(prog(t, 103.8 + i * 0.12, 104.1 + i * 0.12))
        if kk <= 0:
            continue
        c.drawRect(skia.Rect.MakeXYWH(fx, fy, 84, 170), fill(mix((70, 80, 96), (110, 100, 90), hrand("dl", i)), kk))
        ch = Dressed(f"d{i}", top=HOODIE if i % 3 else TEE, legs=TROUSERS, scale=0.42)
        hip, feet = standing(fx + 42, fy + 166, 1 if i % 2 else -1, 0.42)
        ch.draw(ctx, hip, 1 if i % 2 else -1, lean=0.05 * (i % 3), feet=feet, expr=["tired", "neutral", "smile", "sad", "neutral"][i % 5],
                alpha=kk)
    for i, s in enumerate(["EVERY DAY", "ANY LIGHT", "REAL"]):
        k = ease(prog(t, 105.2 + i * 0.5, 105.6 + i * 0.5))
        draw_text(ctx, s, 1420, py + 440 + i * 56, 36, (170, 200, 230), k, face=LG)
    c.restore()
    c.restore()
    cap(ctx, "C8", y=190)
    cap(ctx, "C9", y=990)
    hud(ctx, t)


INSTEAD = ["Compare with you, a year ago.", "Mute accounts that make you feel small.", "Train for what your body can do."]


def i1(ctx, t):
    a = fade(t, EVENTS["card_i"], 116.0, 0.3, 0.3)
    rrect(ctx, W / 2 - 520, 280, 1040, 480, 22, (236, 232, 214), LINE, 5, a=a)
    draw_text(ctx, "INSTEAD OF COMPARING:", W / 2 - 460, 380, 64, (40, 40, 46), a, align="left", face=LG)
    for i, s in enumerate(INSTEAD):
        k = ease(prog(t, EVENTS["card_i"] + 0.4 + i * 0.6, EVENTS["card_i"] + 0.8 + i * 0.6))
        y = 480 + i * 90
        rrect(ctx, W / 2 - 460, y - 40, 44, 44, 6, None, (40, 40, 46), 4, a=a * k)
        draw_text(ctx, s, W / 2 - 390, y, 46, (40, 40, 46), a * k, align="left")
    hud(ctx, t)


# ---- the pool --------------------------------------------------------------------------------------
DECK = 700        # the deck's surface
EDGE = 820        # where the deck ends and the pool begins
WL = 736          # the water line


def pool(ctx, t, under=False):
    c = ctx.c
    sky = skia.GradientShader.MakeLinear([(0, 0), (0, DECK)], [col((120, 176, 230)), col((236, 226, 196))])
    c.drawRect(skia.Rect.MakeLTRB(-600, -400, W + 600, DECK), skia.Paint(Shader=sky))
    glow(ctx, 300, 200, 300, (255, 236, 180), 0.5)
    for i in range(10):  # the colony blocks behind the fence
        bx = -300 + i * 260
        bh = 200 + 90 * hrand("pb", i)
        c.drawRect(skia.Rect.MakeXYWH(bx, DECK - 120 - bh, 230, bh), fill(mix((200, 186, 170), (170, 176, 186), hrand("pbc", i))))
        for j in range(3):
            c.drawRect(skia.Rect.MakeXYWH(bx + 30 + (j % 2) * 100, DECK - 120 - bh + 30 + j * 56, 50, 34), fill((110, 130, 150)))
    for i in range(40):  # the fence
        c.drawLine(-300 + i * 64, DECK - 120, -300 + i * 64, DECK, stroke((70, 90, 80), 4))
    c.drawLine(-300, DECK - 120, 2300, DECK - 120, stroke((70, 90, 80), 6))
    # the deck (left) and the pool in cutaway (right)
    c.drawRect(skia.Rect.MakeLTRB(-600, DECK, EDGE, H + 400), fill((206, 200, 186)))
    for i in range(14):
        c.drawLine(-600 + i * 110, DECK, -600 + i * 110, H + 400, stroke((186, 180, 166), 2))
    c.drawRect(skia.Rect.MakeLTRB(EDGE, DECK + 14, W + 600, H + 400), fill((210, 226, 232)))
    for i in range(30):
        c.drawLine(EDGE + i * 60, DECK + 14, EDGE + i * 60, H + 400, stroke((180, 200, 210), 2))
    for j in range(8):
        c.drawLine(EDGE, DECK + 40 + j * 60, W + 600, DECK + 40 + j * 60, stroke((180, 200, 210), 2))
    c.drawLine(-600, DECK, EDGE, DECK, stroke(LINE, 4))
    c.drawLine(EDGE, DECK, EDGE, H + 400, stroke(LINE, 4))
    # the ladder
    for x in (900, 950):
        c.drawPath(poly_path([(x, WL + 120), (x, DECK - 60), (x - 50, DECK - 60), (x - 50, DECK)], closed=False, smooth=True),
                   stroke((200, 204, 210), 7))


def water(ctx, t):
    """The water over everything in the pool: drawn after the swimmers so their bodies sit inside it."""
    c = ctx.c
    pts = [(x, WL + math.sin(x * 0.012 + t * 2.2) * 5) for x in range(EDGE, W + 640, 40)]
    path = poly_path(pts + [(W + 600, H + 400), (EDGE, H + 400)])
    c.drawPath(path, fill(WATER, 0.55))
    c.drawPath(poly_path(pts, closed=False, smooth=True), stroke((220, 245, 255), 4, 0.9))
    for i in range(12):
        x = EDGE + 60 + i * 110 + 20 * math.sin(t + i)
        y = WL + 50 + 60 * hrand("caus", i)
        c.drawLine(x, y, x + 50, y + 6 * math.sin(t * 2 + i), stroke((230, 250, 255), 3, 0.25))


def swimmer_head(ctx, ch, x, y, f=1, expr="happy", look=(0, 0), arms=None, mouth=0.0):
    """A swimmer in the water: hip below the surface, head and shoulders out."""
    hip = (x, y + 120 * ch.scale)
    J0 = ch.joints(hip, f, 0.0)
    sh = J0["shoulder"]
    hands = arms(sh) if arms else {"near": (sh[0] + f * 40, sh[1] + 40), "far": (sh[0] - f * 40, sh[1] + 40)}
    feet = {"near": (x + f * 20 * ch.scale, hip[1] + 104 * ch.scale), "far": (x - f * 20 * ch.scale, hip[1] + 96 * ch.scale)}
    return ch.draw(ctx, hip, f, lean=0.0, feet=feet, hands=hands, expr=expr, look=look, mouth_open=mouth)


def f1(ctx, t):
    r0, r1_ = EVENTS["rise"]
    rise = ease(prog(t, r0, r1_)) * (1 - prog(t, EVENTS["crumble"], EVENTS["crumble"] + 0.05))
    off = t >= EVENTS["hoodie"]
    dive = prog(t, EVENTS["dive"], EVENTS["splash"])
    lr0, lr1 = EVENTS["look_round"]
    looking = lr0 <= t < lr1
    zoom = lerp(1.45, 1.62, ease(prog(t, 117, 125))) if t < EVENTS["hoodie"] else lerp(1.62, 1.45, ease(prog(t, EVENTS["hoodie"], 128)))
    him = make_him(t, top=None if off else HOODIE, legs=None, shorts=SHORTS)
    with Camera(zoom, 1000, 610, shake=1.2 * prog(t, 121, 125) * (t < 125)).apply(ctx):
        pool(ctx, t)
        # the others in the water: nobody is looking at him
        swimmer_head(ctx, NIKHIL_SWIM, 1080, WL - 96, f=-1, expr="happy", look=(-1, -0.2), mouth=talk("nikhil", t),
                     arms=lambda sh: {"near": (sh[0] - 40, sh[1] + 40),
                                      "far": (sh[0] + 80, sh[1] - 50 + 8 * math.sin(t * 6)) if t < 118.6 else (sh[0] + 40, sh[1] + 40)})
        uncle = Dressed("uncle", skin=GREYED, scale=1.05)
        hip = (1440, WL - 6)
        uncle.draw(ctx, hip, -1, lean=1.45, feet={"near": (1555, WL - 2), "far": (1550, WL + 6)},
                   hands={"near": (1384, WL + 66), "far": (1398, WL + 60)}, expr="closed" if looking or t > 124 else "smile", look=(0, -1))
        ctx.c.drawOval(skia.Rect.MakeXYWH(1400, WL - 40, 70, 40), fill(GREYED))
        ctx.c.drawOval(skia.Rect.MakeXYWH(1400, WL - 40, 70, 40), stroke(LINE, 3))
        for j, kx in enumerate((1570, 1640)):
            kid = Dressed(f"pk{j}", skin=GREYED, scale=0.7)
            fk = -1 if j == 0 else 1
            swimmer_head(ctx, kid, kx, WL - 66 + 6 * math.sin(t * 7 + j), f=fk, expr="happy",
                         arms=lambda sh, j=j, fk=fk: {"near": (sh[0] + fk * (50 + 14 * math.sin(t * 9 + j)), sh[1] + 34),
                                                      "far": (sh[0] - fk * 30, sh[1] + 40)})
        for k in range(10):
            sx = 1605 + 60 * math.sin(k * 2.1)
            sy = WL - 20 - ((t * 3 + k * 0.17) % 1.0) * 90
            ctx.c.drawCircle(sx, sy, 5, fill((230, 248, 255), 0.8))
        lx = 1000 + ((t - 116) * 60) % 900  # a lady doing laps, far side
        lady = Dressed("lady", skin=GREYED, scale=0.62)
        lady.draw(ctx, (lx, WL + 34), 1, lean=1.5, feet={"near": (lx - 70, WL + 40 + 6 * math.sin(t * 8)), "far": (lx - 70, WL + 34)},
                  hands={"near": (lx + 70 + 20 * math.sin(t * 4), WL + 10), "far": (lx + 60, WL + 30)}, expr="closed")
        water(ctx, t)
        # the villain behind him on the deck
        if rise > 0:
            P.villain(ctx, 470, DECK, scale=lerp(0.7, 1.1, rise), alpha=rise, grin=1.2, lean=0.35,
                      reach=(650, DECK - 220) if rise > 0.7 else None)
        if EVENTS["crumble"] < t < EVENTS["crumble"] + 2.2:
            P.villain_shards(ctx, 470, DECK, 1.1, prog(t, EVENTS["crumble"], EVENTS["crumble"] + 2.0))
        if t < EVENTS["dive"]:
            hip, feet = standing(740, DECK, 1, him.scale)
            J0 = him.joints(hip, 1, 0.04)
            sh = J0["shoulder"]
            pull = prog(t, EVENTS["hoodie"] - 0.5, EVENTS["hoodie"])
            if 0 < pull < 1:
                hands = {"near": (sh[0] + 10, sh[1] - 60 * pull - 20), "far": (sh[0] - 6, sh[1] - 60 * pull - 16)}
            else:
                hands = None
            lk = (1, 0.4)
            if looking:
                lk = (-1, 0.0) if (t - lr0) < 0.8 else (1, -0.2)
            J = him.draw(ctx, hip, 1 if not (looking and (t - lr0) < 0.8) else -1, lean=0.04, feet=feet, hands=hands,
                         expr="anxious" if t < 124.4 else ("worried" if t < EVENTS["hoodie"] else "hopeful"), look=lk)
        else:
            # the dive: an arc from the edge into the water, rotating head-first
            k = dive
            x = lerp(760, 1010, k)
            y = lerp(DECK - 110, WL + 60, k) - math.sin(math.pi * k) * 70
            lean = lerp(0.9, 2.5, ease(k))
            hip = (x, y)
            J0 = him.joints(hip, 1, lean)
            sh, hd = J0["shoulder"], J0["head"]
            ang = -math.pi / 2 + lean
            tip = (hd[0] + math.cos(ang) * 60, hd[1] + math.sin(ang) * 60)
            hands = {"near": tip, "far": (tip[0] - 6, tip[1] + 4)}
            back = (hip[0] - math.cos(ang) * 110, hip[1] - math.sin(ang) * 110)
            feet = {"near": back, "far": (back[0] + 6, back[1] + 4)}
            if k < 1.0:
                him.draw(ctx, hip, 1, lean=lean, feet=feet, hands=free_hands(him, hip, 1, lean, hands), expr="closed")
        if off:
            # the hoodie, flung away and landing on the deck
            k = ease(prog(t, EVENTS["hoodie"], EVENTS["hoodie"] + 0.9))
            hx = lerp(760, 340, k)
            hy = lerp(DECK - 200, DECK - 14, k) - math.sin(math.pi * k) * 160
            ctx.c.save()
            ctx.c.translate(hx, hy)
            ctx.c.rotate(lerp(0, -200, k))
            ctx.c.drawPath(poly_path([(-60, -30), (60, -30), (70, 26), (-70, 26)], smooth=True), fill(HOODIE))
            ctx.c.drawPath(poly_path([(-60, -30), (60, -30), (70, 26), (-70, 26)], smooth=True), stroke(LINE, 3))
            ctx.c.restore()
        if t > EVENTS["splash"] - 0.1:
            k = prog(t, EVENTS["splash"] - 0.1, EVENTS["splash"] + 0.8)
            for i in range(26):
                a_ = -math.pi / 2 + (hrand("spl", i) - 0.5) * 2.0
                sp = 120 + 260 * hrand("spv", i)
                sx = 1010 + math.cos(a_) * sp * k
                sy = WL + math.sin(a_) * sp * k + 400 * k * k
                if sy < WL + 10:
                    ctx.c.drawCircle(sx, sy, 7 * (1 - k) + 2, fill((230, 248, 255), 1 - k))
        speech(ctx, t, "nikhil", 1080 - 40, WL - 250)
    label(ctx, "SUNDAY, 7:00 AM", 1 - prog(t, r0 - 0.6, r0))
    vline(ctx, "V7", 1180, 300, 58)
    vline(ctx, "V8", 1180, 380, 54)
    vline(ctx, "V9", 1180, 300, 62)
    hud(ctx, t, 1 - ease(prog(t, r0 - 0.6, r0)) * (1 - prog(t, EVENTS["crumble"], EVENTS["crumble"] + 0.6)))


def f2(ctx, t):
    c = ctx.c
    g = skia.GradientShader.MakeLinear([(0, 0), (0, H)], [col((90, 180, 220)), col((20, 60, 110))])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=g))
    for i in range(6):  # light from the surface
        x = 200 + i * 320 + 40 * math.sin(t * 0.7 + i)
        cone(ctx, (x, 0), (x - 120 + 200 * hrand("ray", i), H), (x + 60 + 200 * hrand("ray", i), H), (230, 250, 255), 0.07)
    c.drawLine(0, 90, W, 90, stroke((220, 245, 255), 6, 0.5))
    k = prog(t, 130.0, 138.0)
    x = lerp(300, 1500, k)
    with Camera(1.55, lerp(520, 1280, k), 540).apply(ctx):
        y = 560 + 16 * math.sin(t * 2.4)
        lean = 1.5
        stroke_ph = t * 3.2
        hip = (x, y)
        him = make_him(t, top=None, legs=None, shorts=SHORTS)
        J0 = him.joints(hip, 1, lean)
        sh = J0["shoulder"]
        a = 0.5 - 0.5 * math.cos(stroke_ph)
        hands = {"near": (sh[0] + lerp(100, 20, a), sh[1] + lerp(-10, 70, a)), "far": (sh[0] + lerp(96, 16, a), sh[1] + lerp(-4, 60, a))}
        kick = math.sin(t * 6) * 18
        feet = {"near": (hip[0] - 116, hip[1] + kick), "far": (hip[0] - 116, hip[1] - kick)}
        J = him.draw(ctx, hip, 1, lean=lean, feet=feet, hands=hands, expr="smile" if t > 131.2 else "closed", look=(1, 0.0))
        for i in range(14):
            bx = J["head"][0] + 30 - (t - 130 - i * 0.3) * 40 + 10 * math.sin(i)
            by = J["head"][1] - ((t * 1.4 + i * 0.23) % 1.0) * 400
            if bx < J["head"][0] + 40:
                c.drawCircle(bx, by, 4 + 5 * hrand("bub", i), stroke((230, 248, 255), 2.5, 0.7))
    cap(ctx, "C10", y=190)
    hud(ctx, t)


def swim_flat(ctx, ch, x, y, t, ph=0.0, expr="determined"):
    """Front crawl seen from the side: the body flat at the surface, one arm reaching ahead, legs kicking."""
    lean = 1.5
    hip = (x, y)
    J0 = ch.joints(hip, 1, lean)
    sh = J0["shoulder"]
    a = t * 6 + ph
    near = (sh[0] + 70 * math.cos(a), sh[1] - 40 * max(0.0, math.sin(a)) + 30 * max(0.0, -math.sin(a)))
    far = (sh[0] - 70 * math.cos(a), sh[1] + 30 * max(0.0, math.sin(a)) - 40 * max(0.0, -math.sin(a)))
    kick = math.sin(t * 10 + ph) * 14
    feet = {"near": (hip[0] - 112, hip[1] + kick), "far": (hip[0] - 112, hip[1] - kick)}
    return ch.draw(ctx, hip, 1, lean=lean, feet=feet, hands=free_hands(ch, hip, 1, lean, {"near": near, "far": far}),
                   expr=expr, look=(1, 0.0))


def p1(ctx, t):
    r0, r1_ = EVENTS["race"]
    touch = t >= EVENTS["touch"]
    laugh = ease(prog(t, EVENTS["laugh"] - 0.3, EVENTS["laugh"]))
    five = math.sin(math.pi * prog(t, 144.4, 145.6))
    him = make_him(t, top=None, legs=None, shorts=SHORTS)
    wall = 1820
    with Camera(1.4, 1350, 600).apply(ctx):
        pool(ctx, t)
        c = ctx.c
        c.drawRect(skia.Rect.MakeLTRB(wall, DECK, W + 900, H + 400), fill((206, 200, 186)))
        c.drawLine(wall, DECK, wall, H + 400, stroke(LINE, 4))
        c.drawLine(wall, DECK, W + 900, DECK, stroke(LINE, 4))
        if not touch:
            for j, (ch, lag) in reversed(list(enumerate(((him, 0.0), (NIKHIL_SWIM, 0.35))))):
                kk = ease(prog(t, r0, r1_ + lag))
                x = lerp(1080 - 160 * j, wall - 200 - 60 * j, kk)
                swim_flat(ctx, ch, x, WL + 14 + j * 40, t, ph=j * 1.7, expr="determined" if j == 0 else "happy")
                for i in range(12):  # the splash behind each swimmer
                    ctx.c.drawCircle(x - 140 - i * 20, WL - 4 - 10 * abs(math.sin(t * 9 + i + j)), 6, fill((230, 248, 255), 0.7 * (1 - i / 12)))
        else:
            mid = (wall - 155, WL - 140)
            Jh = swimmer_head(ctx, him, wall - 90, WL - 96, f=-1, expr="happy", look=(-1, -0.2),
                              arms=lambda sh: {"near": (lerp(sh[0] - 40, mid[0] + 8, five), lerp(sh[1] + 40, mid[1], five)),
                                               "far": (wall - 4, WL - 18)},
                              mouth=0.4 * laugh * abs(math.sin(t * 9)))
            Jn = swimmer_head(ctx, NIKHIL_SWIM, wall - 220, WL - 96, f=1, expr="happy", look=(1, -0.2),
                              arms=lambda sh: {"near": (lerp(sh[0] + 40, mid[0] - 8, five), lerp(sh[1] + 40, mid[1], five)),
                                               "far": (sh[0] - 40, sh[1] + 40)},
                              mouth=0.4 * laugh * abs(math.sin(t * 9 + 1)))
            if 0.85 < five:
                glow(ctx, mid[0], mid[1], 60, GOLD, 0.5 * five)
        water(ctx, t)
    band(ctx, "C11", 975, 150)
    cap(ctx, "C11", y=925)
    cap(ctx, "C12", y=995)
    hud(ctx, t)


# ---- viewer, mirror, title ----------------------------------------------------------------
def vt(ctx, t):
    a = fade(t, 152.2, 159.0, 0.6, 0.6)
    mute = ease(prog(t, EVENTS["mute"], EVENTS["mute"] + 0.5))
    c = ctx.c
    c.saveLayerAlpha(None, int(255 * a))
    UI = P.PhoneUI(W / 2, 600, 460, 800)
    UI.body(ctx, 1.0)
    with UI.screen(ctx):
        x0, y0 = UI.x0 + 18, UI.y0 + 18
        post(ctx, x0, y0 + 60, UI.w - 36, 1, 1.0, muted=mute)
        # the menu with MUTE
        bx, by = x0 + 100, y0 + 520
        if t > EVENTS["mute"] - 1.0:
            ka = ease(prog(t, EVENTS["mute"] - 1.0, EVENTS["mute"] - 0.7)) * (1 - prog(t, EVENTS["mute"] + 0.4, EVENTS["mute"] + 0.7))
            rrect(ctx, bx, by, 220, 80, 16, (236, 232, 220) if t < EVENTS["mute"] else GOLD, LINE, 3, a=ka)
            draw_text(ctx, "MUTE", bx + 110, by + 54, 44, (40, 40, 46), ka, face=LG)
        if mute > 0:
            draw_text(ctx, "muted", x0 + (UI.w - 36) / 2, y0 + 400, 44, (200, 200, 206), mute)
    c.restore()
    cap(ctx, "V1", y=170, size=52)
    cap(ctx, "V2", y=170, size=52)


def x1(ctx, t):
    grow = ease(prog(t, EVENTS["grow_kid"], EVENTS["grow_kid"] + 1.2))
    him = make_him(t, top=TEE, legs=TROUSERS)
    with Camera(1.45, 900, 470).apply(ctx):
        gym(ctx, t)
        with GYM_M.inside(ctx):
            refl_floor(ctx, GYM_M, 700)
            r = reflection(him, 0.96, 0.0)
            hip, feet = standing(1040, 742, -1, r.scale)
            r.draw(ctx, hip, -1, lean=0.02, feet=feet, expr="smile", look=(-1, 0.0))
            refl_curler(KID, lerp(0.56, 0.95, grow), lerp(0.75, 0.0, grow), 1330, -1, t * 2.0, 0.7,
                        lean=lerp(0.3, 0.06, grow), expr="sad" if grow < 0.5 else "smile", look=(-1, 0.6 - 0.6 * grow))(ctx)
        J = stand(him, ctx, 720, f=-1, lean=0.02, expr="smile", look=(-1, 0.2), mouth_open=talk("him", t))
        Jk = curler(ctx, t, KID, 500, 1, t * 2.0 if t < 160.2 else 0.0, 0.7, lean=0.08,
                    expr="sad" if t < 162.6 else ("hopeful" if grow < 0.5 else "smile"), look=(1, 0.3) if t < 160.4 else (1, 0.0),
                    mouth_open=talk("kid", t))
        speech(ctx, t, "him", J["head"][0] + 120, J["head"][1] - 80)
        speech(ctx, t, "kid", Jk["head"][0] + 90, Jk["head"][1] - 80)


def title(ctx, t):
    a = fade(t, EVENTS["title"], 177.0, 0.8, 0.6)
    draw_text(ctx, "MIRROR.", W / 2, 520, 220, TEXT, a, face=LG)
    k = ease(prog(t, EVENTS["title"] + 0.4, EVENTS["title"] + 1.3))
    if k > 0:
        pts = [(W / 2 - 330 + 660 * i / 10, 562 + math.sin(i * 1.7) * 4) for i in range(int(10 * k) + 1)]
        ctx.c.drawPath(poly_path(wobble_points(ctx, pts, "ul", 1.5), closed=False), stroke(RED, 9, a))
    cap(ctx, "T1", y=670, size=48)
    cap(ctx, "T2", y=770, size=72, rgb=GOLD, glow_rgb=(170, 110, 20))


def helpline(ctx, t):
    cap(ctx, "H1", y=500, size=44)
    cap(ctx, "H2", y=580, size=38, rgb=(190, 190, 196))


DISPATCH = {
    "S01": s01, "H1": h1, "S02": s02, "B1": b1, "G1": g1, "G2": g2, "G3": g3, "R1": r1, "T1": t1, "L1": l1, "I1": i1,
    "F1": f1, "F2": f2, "P1": p1, "VT": vt, "X1": x1, "TT": title, "HL": helpline,
}
CONTINUOUS = {"S01", "G1", "HL"}


def scene(ctx):
    t = ctx.t
    sid, t0, t1_, *_ = scene_at(t)
    DISPATCH[sid](ctx, t)
    finish(ctx)
    if sid not in CONTINUOUS:
        black(ctx, 1 - prog(t, t0, t0 + 0.08))
    if sid == "R1" and t >= 68.0:
        black(ctx, 1 - prog(t, 68.0, 68.08))
    if sid == "HL":
        black(ctx, prog(t, DURATION - 0.8, DURATION))
