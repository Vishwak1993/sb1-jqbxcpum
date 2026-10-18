"""Second thumbnails (B versions): the villain's line as the words.

One family for every film: the villain leans out of the dark and whispers in his ear, his eyes slide toward it,
and the line he hears is the title of the thumbnail ("TREAT YOURSELF.", "NEVER FORGET."). The film's own object
sits in his hands. The villain side alternates from film to film so the row on the channel page does not repeat.

Run from this folder with the toolkit venv: python thumbnails_b.py   (writes <film>/packaging/*_thumbnail_B_*.png)
Use: upload the B version next to the A version in YouTube's thumbnail test, or swap after 48 hours if views stall.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "toolkit"))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, HEAD_R, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402

INK = (22, 18, 22)
VILLAIN_INK = (14, 6, 8)
CARD = (150, 118, 82)
STONE = (196, 58, 52)


def oval(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


# ---- him: a big head with a hand-painted face ------------------------------------------------
def shade_head(ctx, hx, hy, r, side):
    c = ctx.c
    c.save()
    c.clipPath(skia.Path.Circle(hx, hy, r * 0.985), skia.ClipOp.kIntersect, True)
    lit = skia.GradientShader.MakeRadial((hx - side * r * 0.4, hy + r * 0.1), r * 1.7,
                                         [col((255, 250, 240), 0.10), col((10, 12, 22), 0.0), col((10, 12, 22), 0.55)],
                                         [0.0, 0.45, 1.0])
    c.drawRect(oval(hx, hy, r, r), skia.Paint(Shader=lit, AntiAlias=True))
    rim = skia.GradientShader.MakeLinear([(hx + side * r, hy), (hx + side * r * 0.35, hy)], [col(RED, 0.5), col(RED, 0.0)])
    c.drawRect(oval(hx, hy, r, r), skia.Paint(Shader=rim, AntiAlias=True))
    c.restore()


def face(ctx, hx, hy, r, side, tear=False, glow_rgb=None):
    """Eyes slid toward the villain (side), worried brows, a small tight mouth, sweat."""
    c = ctx.c
    fx, fy = hx - side * r * 0.12, hy + r * 0.04
    rx, ry = r * 0.17, r * 0.21
    for k in (-1, 1):
        ex, ey = fx + k * r * 0.27, fy - r * 0.08
        c.drawOval(oval(ex, ey + ry * 0.6, rx * 1.15, ry * 0.7), blurred(fill((70, 60, 90), 0.4), rx * 0.18))
        white = skia.Path()
        white.addOval(oval(ex, ey, rx, ry))
        c.drawPath(white, fill((246, 238, 232)))
        c.save()
        c.clipPath(white, skia.ClipOp.kIntersect, True)
        for i in range(6):
            a = (i / 6) * 2 * math.pi + hrand("ev", k, i) * 0.5
            p0 = (ex + math.cos(a) * rx, ey + math.sin(a) * ry)
            p1 = (ex + math.cos(a + 0.25) * rx * 0.6, ey + math.sin(a + 0.25) * ry * 0.6)
            c.drawPath(poly_path([p0, p1], closed=False), stroke((200, 50, 55), 2.2, 0.6))
        px, py = ex + side * rx * 0.48, ey + ry * 0.05
        c.drawCircle(px, py, rx * 0.4, fill((70, 60, 58)))
        c.drawCircle(px, py, rx * 0.2, fill(INK))
        c.drawCircle(px - rx * 0.12, py - rx * 0.16, rx * 0.09, fill((255, 255, 255)))
        c.restore()
        c.drawPath(white, stroke(INK, 6))
        inner = (ex - k * rx * 0.4, ey - ry * 1.55)
        outer = (ex + k * rx * 1.2, ey - ry * 1.05)
        mid = ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 - r * 0.03)
        c.drawPath(poly_path([inner, mid, outer], closed=False, smooth=True), stroke(INK, r * 0.055))
    mw = r * 0.14
    c.drawPath(poly_path([(fx - mw, fy + r * 0.36), (fx, fy + r * 0.31), (fx + mw, fy + r * 0.35)], closed=False, smooth=True),
               stroke(INK, r * 0.04))
    for (dx, dy, s) in ((-side * 0.5, -0.55, 1.1), (-side * 0.68, -0.22, 0.8)):
        x, y, d = hx + dx * r, hy + dy * r, r * 0.055 * s
        drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
        c.drawPath(drop, fill((200, 225, 255), 0.95))
        c.drawPath(drop, stroke((90, 120, 170), 3))
    if tear:
        x, y = fx - side * r * 0.27, fy + r * 0.15
        c.drawPath(poly_path([(x, y), (x + 10, y + 40), (x, y + 60), (x - 10, y + 40)], smooth=True), fill((170, 210, 255), 0.95))
    if glow_rgb is not None:  # the object's light on his face from below
        c.save()
        c.clipPath(skia.Path.Circle(hx, hy, r * 0.985), skia.ClipOp.kIntersect, True)
        g = skia.GradientShader.MakeLinear([(hx, hy + r), (hx, hy)], [col(glow_rgb, 0.35), col(glow_rgb, 0.0)])
        c.drawRect(oval(hx, hy, r, r), skia.Paint(Shader=g))
        c.restore()


# ---- the villain, leaning in to his ear -------------------------------------------------------
def villain(ctx, side, hx, hy, R):
    """side: -1 = the villain is on the left of him. Its head at his ear, a red grin, slit eyes."""
    c = ctx.c
    vx, vy = hx + side * R * 1.3, hy - R * 0.4
    body = poly_path([(vx - R * 0.45, vy + R * 0.6), (vx - R * 1.25, vy + R * 1.35), (vx - R * 1.5, H + 80),
                      (vx + R * 1.5, H + 80), (vx + R * 1.25, vy + R * 1.35), (vx + R * 0.45, vy + R * 0.6)], smooth=True)
    head = skia.Path()
    head.addOval(oval(vx, vy, R * 0.95, R * 1.0))
    glow(ctx, vx, vy, R * 3.0, RED, 0.35)
    shape = skia.Op(head, body, skia.PathOp.kUnion_PathOp)
    c.drawPath(shape, blurred(stroke(RED, 26, 0.7), 18))
    c.drawPath(shape, fill(VILLAIN_INK))
    c.drawPath(shape, stroke(RED, 6, 0.9))
    # eyes: two red slits, narrowed with pleasure
    for k in (-1, 1):
        ex, ey = vx - side * R * 0.12 + k * R * 0.32, vy - R * 0.18
        eye = poly_path([(ex - R * 0.2, ey + R * 0.02), (ex, ey - R * 0.08), (ex + R * 0.2, ey + R * 0.02), (ex, ey + R * 0.04)], smooth=True)
        c.drawPath(eye, blurred(fill(RED, 0.8), 10))
        c.drawPath(eye, fill((255, 90, 80)))
    # the grin, close to his ear
    mx, my = vx - side * R * 0.25, vy + R * 0.32
    grin = poly_path([(mx - R * 0.42, my - R * 0.06), (mx, my + R * 0.24), (mx + R * 0.42, my - R * 0.06), (mx, my + R * 0.08)], smooth=True)
    c.drawPath(grin, blurred(fill(RED, 0.8), 12))
    c.drawPath(grin, fill((255, 80, 70)))
    return vx, vy


def claw(ctx, x, y, side, R):
    """The villain's hand resting on his shoulder: four curled, pointed fingers."""
    c = ctx.c
    palm = poly_path([(x + side * R * 0.5, y - R * 0.05), (x, y - R * 0.12), (x - side * R * 0.1, y + R * 0.12),
                      (x + side * R * 0.45, y + R * 0.2)], smooth=True)
    c.drawPath(palm, blurred(stroke(RED, 18, 0.6), 10))
    c.drawPath(palm, fill(VILLAIN_INK))
    for i in range(4):
        bx = x - side * R * 0.02 + side * i * R * 0.11
        by = y + R * 0.05 + i * R * 0.02
        f = poly_path([(bx - R * 0.04, by), (bx - side * R * 0.1, by + R * 0.2), (bx - side * R * 0.16, by + R * 0.34),
                       (bx - side * R * 0.06, by + R * 0.22), (bx + R * 0.04, by + R * 0.02)], smooth=True)
        c.drawPath(f, blurred(stroke(RED, 12, 0.5), 8))
        c.drawPath(f, fill(VILLAIN_INK))
        c.drawPath(f, stroke(RED, 3, 0.9))
    c.drawPath(palm, stroke(RED, 4, 0.9))


def words(ctx, lines, red_word, side, size=140, y0=180):
    """The villain's line in big caps, on the villain's side of the frame; one word in red."""
    x = 70 if side < 0 else W - 70
    align = "left" if side < 0 else "right"
    for i, line in enumerate(lines):
        y = y0 + i * size * 0.98
        draw_text(ctx, line, x + 8, y + 10, size, (0, 0, 0), 0.6, align=align, face="LuckiestGuy-Regular.ttf")
        if red_word and red_word in line:
            # draw the line in white, then the red word over its own position
            pre, post = line.split(red_word, 1)
            font_w = lambda s: text_width(s, size, "LuckiestGuy-Regular.ttf")
            total = font_w(line)
            left = x if align == "left" else x - total
            draw_text(ctx, pre, left, y, size, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
            draw_text(ctx, red_word, left + font_w(pre), y, size, RED, align="left", face="LuckiestGuy-Regular.ttf",
                      glow_rgb=RED_D)
            draw_text(ctx, post, left + font_w(pre + red_word), y, size, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
        else:
            draw_text(ctx, line, x, y, size, TEXT, align=align, face="LuckiestGuy-Regular.ttf")


# ---- the films' objects, held at his chest ----------------------------------------------------
def phone_front(ctx, x, y, w=220, h=380, rot=0.0):
    c = ctx.c
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    glow(ctx, 0, 0, w * 1.6, BLUE, 0.3)
    rrect(ctx, -w / 2, -h / 2, w, h, 34, (18, 18, 22), (90, 90, 100), 6)
    rrect(ctx, -w / 2 + 12, -h / 2 + 12, w - 24, h - 24, 24, (40, 44, 60), None)
    return c


def obj_sold(ctx, x, y):
    c = phone_front(ctx, x, y, rot=-6)
    rrect(ctx, -80, -150, 160, 140, 14, (60, 64, 80), None)
    wrect(ctx, -46, -116, 92, 70, "bx", CARD, LINE, 3, seg=2)
    c.drawRect(skia.Rect.MakeXYWH(-8, -116, 16, 30), fill((196, 170, 120)))
    draw_text(ctx, "$129", -80, 40, 44, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
    rrect(ctx, -86, 80, 172, 64, 18, RED, None)
    draw_text(ctx, "BUY NOW", 0, 124, 34, TEXT, face="LuckiestGuy-Regular.ttf")
    c.restore()
    return BLUE


def obj_heavy(ctx, x, y):
    c = ctx.c
    r = 120
    pts = [(x + math.cos(i * 2 * math.pi / 9) * r * (0.82 + 0.3 * hrand("kb", i)),
            y + math.sin(i * 2 * math.pi / 9) * r * 0.78 * (0.85 + 0.3 * hrand("kb", i, 1))) for i in range(9)]
    p = poly_path(pts, smooth=True)
    glow(ctx, x, y, r * 2.4, RED, 0.45)
    c.drawPath(p, fill(STONE))
    c.drawPath(p, stroke(LINE, 8))
    c.drawPath(poly_path([(x - r * 0.45, y - r * 0.35), (x - r * 0.1, y - r * 0.5)], closed=False), stroke((255, 255, 255), 7, 0.35))
    draw_text(ctx, "KAI", x, y + 26, 76, (250, 240, 230), face="LuckiestGuy-Regular.ttf")
    return RED


def obj_onepercent(ctx, x, y):
    c = phone_front(ctx, x, y, rot=5)
    rrect(ctx, -70, -60, 130, 80, 12, None, (200, 200, 210), 8)
    c.drawRect(skia.Rect.MakeXYWH(60, -36, 14, 32), fill((200, 200, 210)))
    c.drawRect(skia.Rect.MakeXYWH(-60, -50, 10, 60), fill(RED))
    draw_text(ctx, "1%", 0, 110, 90, RED, face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
    c.restore()
    return (150, 110, 110)


def obj_later(ctx, x, y):
    c = phone_front(ctx, x, y, rot=-5)
    c.drawCircle(0, -100, 50, fill((150, 148, 146)))
    draw_text(ctx, "Dad", 0, 0, 56, TEXT)
    draw_text(ctx, "calling...", 0, 46, 30, (170, 176, 196))
    c.drawCircle(-56, 130, 40, fill(RED))
    c.drawLine(-74, 130, -38, 130, stroke(TEXT, 9))
    c.drawCircle(56, 130, 40, fill((70, 160, 90)))
    c.restore()
    return BLUE


def obj_no(ctx, x, y):
    c = phone_front(ctx, x, y, rot=4)
    rrect(ctx, -86, -140, 172, 96, 20, (70, 74, 90), None)
    draw_text(ctx, "can you", -70, -102, 30, TEXT, align="left")
    draw_text(ctx, "cover again?", -70, -66, 30, TEXT, align="left")
    rrect(ctx, -6, -20, 92, 60, 20, (90, 140, 220), None)
    draw_text(ctx, "yes", 40, 20, 34, TEXT)
    c.restore()
    return BLUE


def obj_fraud(ctx, x, y):
    c = ctx.c
    glow(ctx, x, y, 300, RED, 0.45)
    rrect(ctx, x - 100, y - 130, 200, 260, 16, (60, 10, 12), LINE, 6)
    draw_text(ctx, "FRAUD", x, y + 22, 64, RED, face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
    return RED


FILMS = [
    # folder, file prefix, lines, red word, villain side, object, tear
    ("sold", "SOLD", ["TREAT", "YOURSELF."], "YOURSELF.", -1, obj_sold, False),
    ("heavy", "HEAVY", ["NEVER", "FORGET."], "FORGET.", 1, obj_heavy, False),
    ("onepercent", "ONE_PERCENT", ["PUSH", "THROUGH."], "THROUGH.", -1, obj_onepercent, False),
    ("later", "LATER", ["HE", "UNDERSTANDS."], "UNDERSTANDS.", 1, obj_later, True),
    ("no", "NO", ["YOU OWE", "THEM."], "THEM.", -1, obj_no, False),
    ("fraud", "FRAUD", ["THEY'LL", "FIND OUT."], "FIND OUT.", 1, obj_fraud, False),
]


def make_scene(lines, red_word, side, obj, tear):
    def scene(ctx):
        c = ctx.c
        bg = skia.GradientShader.MakeRadial((W / 2, H / 2), W * 0.7, [col((26, 24, 30)), col((8, 8, 10))])
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=bg))
        s = 4.4
        hx = W / 2 - side * 200
        hip = (hx, 1250)
        him = Character("b_him", scale=s)
        J0 = him.joints(hip, 1, 0.0)
        hx, hy = J0["head"]
        r = HEAD_R * s
        villain(ctx, side, hx, hy, r * 0.95)
        ox, oy = hx - side * r * 1.15, hy + r * 1.42
        J = him.draw(ctx, hip, 1, lean=0.0, face=False, bend={"arm_near": -1, "arm_far": -1},
                     hands={"near": (ox - 70, oy + 150), "far": (ox + 70, oy + 160)})
        glow_rgb = obj(ctx, ox, oy)
        shade_head(ctx, hx, hy, r, side)
        face(ctx, hx, hy, r, side, tear=tear, glow_rgb=glow_rgb)
        words(ctx, lines, red_word, side)
        finish(ctx, bars=False, grain=0.03, vignette=0.45)
    return scene


def save(img, w, h, path):
    sf = skia.Surface(w, h)
    sf.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    sf.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    only = sys.argv[1:]
    for folder, prefix, lines, red_word, side, obj, tear in FILMS:
        if only and folder not in only:
            continue
        img = frame_image(make_scene(lines, red_word, side, obj, tear), 1.0, 30)
        out = HERE / folder / "packaging"
        save(img, 1280, 720, out / f"{prefix}_thumbnail_B_1280x720.png")
        save(img, 320, 180, out / f"{prefix}_thumbnail_B_320x180.png")
        print(folder, "done")
