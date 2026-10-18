"""Unique B thumbnails for the earlier films: a new layout for each, none in the villain-whisper template.

  NO.     a dialog box that fills the frame: a giant green YES and a tiny "no" in the corner
  LATER.  a wall calendar: every Sunday scrawled "later", Dad's photo pinned in the corner
  1%.     scale: a laptop as big as a wall, tiny him in its glow
  HEAVY.  a diagram on paper: the seesaw, Kai floating, him pinned under the stones
  SOLD.   a till receipt: every feeling with a price, THE SEA $0
  FRAUD.  a stage: him alone in a spotlight, rows of watching eyes

Run from this folder with the toolkit venv: python thumbnails_b2.py [film ...]
Writes <film>/packaging/<PREFIX>_thumbnail_B_1280x720.png (and 320x180), replacing the old villain-whisper versions.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "toolkit"))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, standing, seated, HEAD_R, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402
from studio import props as P  # noqa: E402

INK = (30, 28, 32)


def big(ctx, s, x, y, size, rgb=TEXT, align="left", shadow=(0, 0, 0), a=1.0):
    draw_text(ctx, s, x + 8, y + 10, size, shadow, 0.6 * a, align=align, face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, s, x, y, size, rgb, a, align=align, face="LuckiestGuy-Regular.ttf")


def sweat(ctx, x, y, d):
    drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
    ctx.c.drawPath(drop, fill((200, 225, 255)))
    ctx.c.drawPath(drop, stroke((90, 120, 170), 4))


# ---- NO.: the dialog box -------------------------------------------------------------------------
def no_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((24, 26, 32)))
    for i in range(6):
        c.drawRect(skia.Rect.MakeXYWH(i * 340 - 40, 120, 260, 180), fill((34, 38, 48)))
    x0, y0, w, h = 150, 110, 1620, 860
    c.drawRect(skia.Rect.MakeXYWH(x0 + 16, y0 + 20, w, h), blurred(fill((0, 0, 0), 0.6), 20))
    rrect(ctx, x0, y0, w, h, 34, (238, 238, 242), (120, 120, 130), 6)
    rrect(ctx, x0, y0, w, 110, 34, (210, 212, 220), None)
    c.drawRect(skia.Rect.MakeXYWH(x0, y0 + 70, w, 40), fill((210, 212, 220)))
    c.drawCircle(x0 + 70, y0 + 55, 26, fill((150, 148, 146)))
    draw_text(ctx, "Boss", x0 + 116, y0 + 72, 50, INK, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "can you cover the weekend again?", x0 + 80, y0 + 210, 66, INK, align="left")
    # the giant YES
    bx, by, bw, bh = x0 + 80, y0 + 300, w - 160, 440
    rrect(ctx, bx, by + 18, bw, bh, 60, (40, 120, 60), None)
    rrect(ctx, bx, by, bw, bh, 60, (70, 190, 100), (40, 120, 60), 6)
    draw_text(ctx, "YES", bx + bw / 2 + 6, by + bh / 2 + 120, 330, (40, 120, 60), face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "YES", bx + bw / 2, by + bh / 2 + 110, 330, (255, 255, 255), face="LuckiestGuy-Regular.ttf")
    # the tiny no
    rrect(ctx, x0 + w - 150, y0 + h - 86, 90, 50, 10, (226, 226, 230), (150, 150, 160), 3)
    draw_text(ctx, "no", x0 + w - 105, y0 + h - 51, 30, (120, 120, 130))
    # his finger, already on its way to YES, shaking
    fx, fy = 1180, 700
    finger = poly_path([(fx - 60, H + 60), (fx - 55, fy + 60), (fx - 26, fy - 6), (fx + 20, fy - 10), (fx + 50, fy + 50), (fx + 70, H + 60)], smooth=True)
    c.drawPath(finger, fill(SKIN))
    c.drawPath(finger, stroke(LINE, 7))
    for k in (-1, 1):
        c.drawLine(fx + k * 90, fy + 10, fx + k * 120, fy - 20, stroke((255, 255, 255), 6, 0.8))
    sweat(ctx, fx + 110, fy + 90, 20)


# ---- LATER.: the calendar ----------------------------------------------------------------------------
def moustache(ctx, hx, hy, f, s):
    fx = hx + f * 14 * s
    p = poly_path([(fx - 15 * s, hy + 13 * s), (fx - 6 * s, hy + 8 * s), (fx, hy + 10 * s), (fx + 6 * s, hy + 8 * s),
                   (fx + 15 * s, hy + 13 * s), (fx + 8 * s, hy + 15 * s), (fx, hy + 13 * s), (fx - 8 * s, hy + 15 * s)], smooth=True)
    ctx.c.drawPath(p, fill((150, 148, 146)))
    ctx.c.drawPath(p, stroke(LINE, 2 * s))


def later_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((40, 36, 34)))
    x0, y0, w, h = 120, 250, 1300, 790
    c.drawRect(skia.Rect.MakeXYWH(x0 + 14, y0 + 18, w, h), blurred(fill((0, 0, 0), 0.6), 18))
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, h), fill((240, 236, 226)))
    c.drawRect(skia.Rect.MakeXYWH(x0, y0, w, 90), fill((120, 60, 56)))
    draw_text(ctx, "SUNDAYS", x0 + w / 2, y0 + 66, 60, (250, 240, 230), face="LuckiestGuy-Regular.ttf")
    cw, ch = w / 7, (h - 90) / 5
    for r in range(5):
        for k in range(7):
            cx, cy = x0 + k * cw, y0 + 90 + r * ch
            c.drawRect(skia.Rect.MakeXYWH(cx, cy, cw, ch), stroke((180, 172, 160), 3))
            if r * 7 + k + 1 <= 31:
                draw_text(ctx, str(r * 7 + k + 1), cx + 14, cy + 34, 26, (120, 112, 104), align="left")
            if k == 6 and not (r == 4):
                c.save()
                c.translate(cx + cw / 2, cy + ch / 2 + 16)
                c.rotate(-8)
                draw_text(ctx, "later", 0, 0, 52, RED, face="PatrickHand-Regular.ttf")
                c.restore()
    # this Sunday: empty, his hand bringing the red pen to it
    k, r = 6, 4
    cx, cy = x0 + k * cw, y0 + 90 + r * ch
    c.drawRect(skia.Rect.MakeXYWH(cx + 3, cy + 3, cw - 6, ch - 6), stroke(RED, 6, 0.6))
    pen = (cx + cw * 0.6, cy + ch * 0.6)
    c.drawLine(pen[0], pen[1], pen[0] + 140, pen[1] + 260, stroke(RED, 22))
    c.drawLine(pen[0], pen[1], pen[0] + 14, pen[1] + 26, stroke(INK, 10))
    hand = poly_path([(pen[0] + 60, pen[1] + 120), (pen[0] + 160, pen[1] + 110), (pen[0] + 220, pen[1] + 260),
                      (pen[0] + 120, pen[1] + 300)], smooth=True)
    c.drawPath(hand, fill(SKIN))
    c.drawPath(hand, stroke(LINE, 6))
    # Dad's photo, pinned to the wall
    px, py = 1560, 330
    c.save()
    c.translate(px, py)
    c.rotate(6)
    c.drawRect(skia.Rect.MakeXYWH(-160, -150, 320, 380), fill((246, 244, 238)))
    c.drawRect(skia.Rect.MakeXYWH(-140, -130, 280, 280), fill((150, 170, 190)))
    c.drawRect(skia.Rect.MakeXYWH(-140, 70, 280, 80), fill((90, 120, 150)))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(-140, -130, 280, 280))
    dad = Character("b2dad", skin=(214, 206, 192), scale=1.6, extra=moustache)
    dad.draw(ctx, (0, 240), 1, lean=0.02, expr="happy", look=(0.4, 0))
    c.restore()
    c.drawRect(skia.Rect.MakeXYWH(-160, 150, 320, 80), fill((246, 244, 238)))
    draw_text(ctx, "Dad, 71", 0, 205, 44, INK)
    c.drawCircle(0, -136, 12, fill(RED_D))
    c.restore()
    big(ctx, "NEXT WEEK.", 120, 190, 170)


# ---- 1%.: scale ----------------------------------------------------------------------------------------
def onepercent_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((10, 12, 18)))
    sx, sy, sw, sh = 640, 60, 1200, 840
    glow(ctx, sx + sw / 2, sy + sh / 2, 1200, BLUE, 0.35)
    rrect(ctx, sx - 30, sy - 30, sw + 60, sh + 60, 30, (30, 32, 40), (70, 74, 90), 8)
    c.drawRect(skia.Rect.MakeXYWH(sx, sy, sw, sh), fill((214, 226, 246)))
    c.drawRect(skia.Rect.MakeXYWH(sx, sy, sw, 90), fill((70, 110, 190)))
    draw_text(ctx, "Inbox (147)", sx + 40, sy + 64, 54, (255, 255, 255), align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "23:58", sx + sw - 40, sy + 64, 54, (255, 255, 255), align="right", face="LuckiestGuy-Regular.ttf")
    for i in range(7):
        y = sy + 130 + i * 100
        c.drawCircle(sx + 70, y + 30, 26, fill((150, 160, 190)))
        c.drawRect(skia.Rect.MakeXYWH(sx + 120, y + 6, 500 - (i % 3) * 80, 22), fill((60, 70, 100)))
        c.drawRect(skia.Rect.MakeXYWH(sx + 120, y + 40, 700 - (i % 4) * 100, 16), fill((140, 150, 175)))
        draw_text(ctx, "URGENT", sx + sw - 60, y + 40, 34, RED, align="right", face="LuckiestGuy-Regular.ttf")
    c.drawRect(skia.Rect.MakeXYWH(sx - 200, sy + sh + 30, sw + 400, 60), fill((44, 46, 56)))
    # tiny him at the bottom, in the glow, looking up
    P.chair(ctx, 1240, 960, 1, floor_y=1060, key="b2ch")
    him = Character("b2op", scale=0.95)
    hip, feet = seated(1240, 960, 1, 0.95, floor_y=1060)
    him.draw(ctx, hip, 1, lean=-0.12, feet=feet, expr="tired", look=(0.4, -1.2), screen_glow=1.0)
    big(ctx, "ONE", 50, 330, 160)
    big(ctx, "MORE", 50, 490, 160)
    big(ctx, "HOUR.", 50, 650, 160, rgb=RED)


# ---- HEAVY.: the diagram ------------------------------------------------------------------------------
STONE = (196, 58, 52)


def stone(ctx, x, y, r, lab, key):
    pts = [(x + math.cos(i * 2 * math.pi / 9) * r * (0.82 + 0.3 * hrand(key, i)),
            y + math.sin(i * 2 * math.pi / 9) * r * 0.78 * (0.85 + 0.3 * hrand(key, i, 1))) for i in range(9)]
    p = poly_path(pts, smooth=True)
    ctx.c.drawPath(p, blurred(fill(RED, 0.4), r * 0.3))
    ctx.c.drawPath(p, fill(STONE))
    ctx.c.drawPath(p, stroke(LINE, max(3, r * 0.08)))
    draw_text(ctx, lab, x, y + r * 0.2, max(16, r * 0.45), (250, 240, 230), face="LuckiestGuy-Regular.ttf")


def kai_cap(ctx, hx, hy, f, s):
    p = poly_path([(hx - 50 * s, hy - 16 * s), (hx - 44 * s, hy - 48 * s), (hx, hy - 58 * s), (hx + 44 * s, hy - 48 * s),
                   (hx + 50 * s, hy - 16 * s)], smooth=True)
    ctx.c.drawPath(p, fill((60, 150, 150)))
    ctx.c.drawPath(p, stroke(LINE, 3 * s))


def heavy_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((238, 232, 218)))
    for i in range(30):
        c.drawLine(0, 40 + i * 36, W, 40 + i * 36, stroke((214, 206, 190), 2))
    tilt = 0.3
    px, py = 960, 860
    c.drawPath(poly_path([(px - 70, py + 140), (px + 70, py + 140), (px, py)]), fill((120, 110, 100)))
    c.drawPath(poly_path([(px - 70, py + 140), (px + 70, py + 140), (px, py)]), stroke(LINE, 5))
    L = 820
    lx, ly = px - math.cos(tilt) * L, py - math.sin(tilt) * L
    rx, ry = px + math.cos(tilt) * L, py + math.sin(tilt) * L
    c.drawLine(lx, ly, rx, ry, stroke(LINE, 34))
    c.drawLine(lx, ly, rx, ry, stroke((170, 130, 90), 24))
    kai = Character("b2kai", extra=kai_cap, scale=1.5)
    hip, feet = standing(lx + 90, ly - 14, 1, 1.5)
    kai.draw(ctx, hip, 1, lean=0.02, feet=feet, expr="happy", look=(0.6, -0.3), hands={"near": (hip[0] + 70, hip[1] - 250), "far": (hip[0] - 40, hip[1] - 240)})
    him = Character("b2him", scale=1.5)
    hip = (rx - 170, ry - 40)
    him.draw(ctx, hip, 1, lean=0.75, feet={"near": (rx - 30, ry - 16), "far": (rx - 50, ry - 16)}, expr="hurt", look=(0.2, 0.8),
             hands={"near": (rx - 40, ry - 30), "far": (rx - 70, ry - 26)})
    for i, (dx, dy, r, lab) in enumerate(((-250, -230, 120, "KAI"), (-90, -280, 80, "DAD"), (-370, -120, 70, "EX"),
                                           (-180, -400, 64, "BOSS"), (-40, -150, 60, "SUE"))):
        stone(ctx, rx + dx, ry + dy, r, lab, ("b2s", i))
    big(ctx, "WHO'S", 1860, 200, 140, rgb=INK, shadow=(200, 190, 170), align="right")
    big(ctx, "CARRYING IT?", 1860, 350, 140, rgb=INK, shadow=(200, 190, 170), align="right")


# ---- SOLD.: the receipt -------------------------------------------------------------------------------
def sold_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((62, 44, 34)))
    for i in range(9):
        c.drawLine(0, i * 130 + 30, W, i * 130 + 60, stroke((70, 50, 38), 6))
    c.save()
    c.translate(1240, 700)
    c.rotate(-7)
    w, h = 640, 1500
    edge = [(-w / 2, -h / 2)] + [(-w / 2 + i * w / 16, h / 2 - (14 if i % 2 else 0)) for i in range(17)][::-1]
    paper = poly_path([(-w / 2, -h / 2), (w / 2, -h / 2)] + [(w / 2 - i * w / 16, h / 2 - (16 if i % 2 else 0)) for i in range(17)])
    c.drawPath(paper, blurred(fill((0, 0, 0), 0.5), 20))
    c.drawPath(paper, fill((248, 246, 238)))
    draw_text(ctx, "RECEIPT", 0, -540, 70, INK, face="LuckiestGuy-Regular.ttf")
    c.drawLine(-260, -500, 260, -500, stroke(INK, 3))
    items = [("BORED", "$45"), ("BAD DAY", "$60"), ("SUNDAY", "$35"), ("LONELY", "$85"), ("TIRED", "$70"), ("2AM", "$52"),
             ("CAN'T SLEEP", "$39"), ("JUST BECAUSE", "$113")]
    for i, (a, b) in enumerate(items):
        y = -430 + i * 64
        draw_text(ctx, a, -260, y, 44, INK, align="left")
        draw_text(ctx, b, 260, y, 44, INK, align="right")
    c.drawLine(-260, 110, 260, 110, stroke(INK, 3, 0.6))
    draw_text(ctx, "TOTAL", -260, 180, 60, INK, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "$640", 260, 180, 60, INK, align="right", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "THE SEA", -260, 270, 52, RED, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "$0", 260, 270, 52, RED, align="right", face="LuckiestGuy-Regular.ttf")
    c.restore()
    # his hand holding the top of it
    hand = poly_path([(1000, -80), (1150, -60), (1170, 50), (1070, 90), (990, 50)], smooth=True)
    c.drawPath(hand, fill(SKIN))
    c.drawPath(hand, stroke(LINE, 6))
    big(ctx, "WHAT DID", 70, 380, 150)
    big(ctx, "I BUY?", 70, 540, 150)


# ---- FRAUD.: the spotlight ----------------------------------------------------------------------------
def fraud_b(ctx):
    c = ctx.c
    c.drawRect(skia.Rect.MakeWH(W, H), fill((10, 10, 14)))
    cx = 1180
    cone(ctx, (cx, -40), (cx - 330, 880), (cx + 330, 880), (255, 240, 200), 0.32)
    c.drawOval(skia.Rect.MakeXYWH(cx - 330, 840, 660, 90), fill((80, 74, 66)))
    P.chair(ctx, cx, 760, 1, floor_y=880, key="b2fch")
    him = Character("b2fr", scale=1.7)
    hip, feet = seated(cx, 760, 1, 1.7, floor_y=880)
    J = him.draw(ctx, hip, 1, lean=0.08, feet=feet, expr="anxious", look=(-0.2, 0.4),
                 hands={"near": (cx + 70, 700), "far": (cx + 50, 708)})
    sxx, syy = J["shoulder"]
    bx, by = sxx + 26, syy + 90
    c.drawLine(sxx - 10, syy - 14, bx, by - 32, stroke((70, 90, 130), 5))
    glow(ctx, bx, by, 90, RED, 0.6)
    rrect(ctx, bx - 26, by - 34, 52, 66, 6, (60, 10, 12), LINE, 3)
    draw_text(ctx, "FRAUD", bx, by + 6, 17, RED, face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
    hx, hy = J["head"]
    sweat(ctx, hx + 70, hy - 60, 14)
    sweat(ctx, hx + 90, hy - 20, 10)
    # the audience: rows of dark heads with white eyes, all turned to him
    for row, (y, r, n) in enumerate(((1000, 70, 8), (1090, 90, 7))):
        for i in range(n):
            x = 80 + i * (1920 / n) + (row * 60)
            c.drawCircle(x, y, r, fill((24, 24, 30)))
            c.drawRect(skia.Rect.MakeXYWH(x - r * 1.1, y + r * 0.6, r * 2.2, 200), fill((24, 24, 30)))
            for k in (-1, 1):
                ex = x + k * r * 0.28 + (cx - x) * 0.02
                c.drawOval(skia.Rect.MakeXYWH(ex - r * 0.12, y - r * 0.32, r * 0.24, r * 0.16), fill((236, 236, 240)))
    big(ctx, "THEY", 70, 240, 190)
    big(ctx, "KNOW.", 70, 420, 190, rgb=RED)


FILMS = {
    "no": ("NO", no_b), "later": ("LATER", later_b), "onepercent": ("ONE_PERCENT", onepercent_b),
    "heavy": ("HEAVY", heavy_b), "sold": ("SOLD", sold_b), "fraud": ("FRAUD", fraud_b),
}


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    only = sys.argv[1:]
    for folder, (prefix, fn) in FILMS.items():
        if only and folder not in only:
            continue

        def scene(ctx, fn=fn):
            fn(ctx)
            finish(ctx, bars=False, grain=0.025, vignette=0.3)
        img = frame_image(scene, 1.0, 30)
        out = HERE / folder / "packaging"
        save(img, 1280, 720, out / f"{prefix}_thumbnail_B_1280x720.png")
        save(img, 320, 180, out / f"{prefix}_thumbnail_B_320x180.png")
        print(folder, "done")
