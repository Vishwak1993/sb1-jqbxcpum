"""Thumbnail v3, 1280x720: v2's composition with the emotion and rendering pushed, per the style bible's
thumbnail rules. Same character (same rig, head and proportions), but a detailed close-up face:
frightened wide eyes with red veins, dark bags, heavy raised brows, sweat, soft shading lit from below by
the phone. Left: NEW MESSAGES over a huge red "0.". No tear, no Sam, no reply.
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "toolkit"))
import skia  # noqa: E402

from studio.core import *  # noqa: E402,F401
from studio.character import Character, HEAD_R, MISSES  # noqa: E402
from studio.render import frame_image  # noqa: E402

S = 5.6
PHONE = (1000, 950)
HIP = (1540, 1400)
INK = (22, 18, 22)


def oval(cx, cy, rx, ry):
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


def curve(pts, w, rgb, a=1.0):
    return poly_path(pts, closed=False, smooth=True), stroke(rgb, w, a)


def shade_head(ctx, hx, hy, r):
    """Soft rendering: light from the phone (below-left), shadow up and to the right, a faint mottled texture."""
    c = ctx.c
    c.save()
    c.clipPath(skia.Path.Circle(hx, hy, r * 0.985), skia.ClipOp.kIntersect, True)
    lit = skia.GradientShader.MakeRadial((hx - r * 0.55, hy + r * 0.85), r * 1.9,
                                         [col((150, 190, 255), 0.42), col((120, 160, 230), 0.12), col((10, 12, 22), 0.0),
                                          col((10, 12, 22), 0.62)], [0.0, 0.30, 0.55, 1.0])
    c.drawRect(skia.Rect.MakeLTRB(hx - r, hy - r, hx + r, hy + r), skia.Paint(Shader=lit, AntiAlias=True))
    rim = skia.GradientShader.MakeRadial((hx - r * 0.12, hy - r * 0.05), r, [col((0, 0, 0), 0), col((0, 0, 0), 0), col((0, 0, 0), 0.35)], [0, 0.78, 1])
    c.drawRect(skia.Rect.MakeLTRB(hx - r, hy - r, hx + r, hy + r), skia.Paint(Shader=rim, AntiAlias=True))
    for i in range(500):  # mottled skin texture, repeatable
        a = hrand("tex", i) * 2 * math.pi
        d = math.sqrt(hrand("tex", i, 1)) * r
        x, y = hx + math.cos(a) * d, hy + math.sin(a) * d
        tone = (255, 250, 235) if i % 2 else (120, 110, 100)
        c.drawCircle(x, y, 1.0 + hrand("tex", i, 2) * 2.0, fill(tone, 0.025))
    c.restore()


def eye(ctx, ex, ey, rx, ry, look, key):
    c = ctx.c
    socket = oval(ex, ey + ry * 0.55, rx * 1.15, ry * 0.75)  # dark bag under the eye
    c.drawOval(socket, blurred(fill((70, 60, 90), 0.45), rx * 0.18))
    white = skia.Path(); white.addOval(oval(ex, ey, rx, ry))
    c.drawPath(white, fill((246, 238, 232)))
    c.save(); c.clipPath(white, skia.ClipOp.kIntersect, True)
    c.drawOval(oval(ex, ey, rx, ry), skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (ex, ey), rx * 1.05, [col((255, 255, 255), 0), col((235, 140, 140), 0.55)], [0.55, 1.0])))
    for i in range(9):  # bloodshot veins from the edge inward
        a = (i / 9) * 2 * math.pi + hrand(key, i) * 0.5
        p0 = (ex + math.cos(a) * rx, ey + math.sin(a) * ry)
        k = 0.45 + hrand(key, i, 1) * 0.25
        p1 = (ex + math.cos(a + 0.25) * rx * k, ey + math.sin(a + 0.25) * ry * k)
        p2 = (ex + math.cos(a - 0.1) * rx * (k - 0.15), ey + math.sin(a - 0.1) * ry * (k - 0.15))
        c.drawPath(poly_path([p0, p1, p2], closed=False, smooth=True), stroke((200, 50, 55), 2.4, 0.8))
    px, py = ex + look[0] * rx * 0.32, ey + look[1] * ry * 0.30
    c.drawCircle(px, py, rx * 0.40, fill((70, 60, 58)))      # iris
    c.drawCircle(px, py, rx * 0.19, fill(INK))               # small, scared pupil
    c.drawCircle(px - rx * 0.12, py - rx * 0.14, rx * 0.09, fill((170, 205, 255)))  # phone glint
    c.restore()
    c.drawPath(white, stroke(INK, 6))
    c.drawPath(poly_path([(ex - rx * 1.05, ey - ry * 0.55), (ex, ey - ry * 1.12), (ex + rx * 1.05, ey - ry * 0.55)], closed=False, smooth=True),
               stroke(INK, 7))  # upper lid line


def face(ctx, hx, hy, r):
    c = ctx.c
    fx, fy = hx - r * 0.24, hy + r * 0.04
    rx, ry = r * 0.205, r * 0.235
    look = (-1.0, 0.9)  # down and left, at the phone
    for side in (-1, 1):
        ex = fx + side * r * 0.27
        eye(ctx, ex, fy - r * 0.05, rx, ry, look, ("eye", side))
        # heavy brows, inner ends pulled up: fear
        inner = (ex - side * rx * 0.50, fy - r * 0.43)
        outer = (ex + side * rx * 1.20, fy - r * 0.24)
        mid = ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 - r * 0.035)
        c.drawPath(poly_path([inner, mid, outer], closed=False, smooth=True), stroke(INK, r * 0.065))
    # worry creases between the brows
    for k in (-1, 1):
        x = fx + k * r * 0.035
        c.drawPath(poly_path([(x, fy - r * 0.40), (x + k * r * 0.012, fy - r * 0.47), (x, fy - r * 0.54)], closed=False, smooth=True),
                   stroke((150, 140, 130), 4, 0.8))
    # mouth: small, tight, pulled down at one side
    top = [(fx - r * 0.15, fy + r * 0.40), (fx - r * 0.05, fy + r * 0.35), (fx + r * 0.06, fy + r * 0.37), (fx + r * 0.16, fy + r * 0.43)]
    bot = [(fx + r * 0.16, fy + r * 0.43), (fx + r * 0.06, fy + r * 0.47), (fx - r * 0.05, fy + r * 0.46), (fx - r * 0.15, fy + r * 0.40)]
    mouth = poly_path(top + bot[1:], closed=True, smooth=True)
    c.drawPath(mouth, fill((60, 30, 34)))
    c.drawPath(poly_path([(fx - r * 0.09, fy + r * 0.375), (fx + r * 0.10, fy + r * 0.395)], closed=False), stroke((240, 236, 226), 7))
    c.drawPath(mouth, stroke(INK, 7))
    # sweat drops on the temple and forehead
    for (dx, dy, s) in ((0.33, -0.50, 1.1), (0.50, -0.24, 0.8), (-0.62, -0.36, 0.65)):
        x, y, d = hx + dx * r, hy + dy * r, r * 0.055 * s
        drop = poly_path([(x, y - d * 1.9), (x + d, y), (x, y + d), (x - d, y)], smooth=True)
        c.drawPath(drop, fill((200, 225, 255), 0.95))
        c.drawPath(drop, stroke((90, 120, 170), 3))
        c.drawCircle(x - d * 0.35, y - d * 0.1, d * 0.28, fill((255, 255, 255)))


def phone(ctx):
    c = ctx.c
    c.save()
    c.translate(*PHONE)
    c.rotate(18)
    # seen at three-quarters: a thin dark back edge, then the glowing screen turned toward his face
    rrect(ctx, -92, -230, 176, 330, 28, (24, 24, 30), (95, 95, 108), 7)
    screen = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-62, -212, 132, 294), 18, 18)
    c.drawRRect(screen, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(0, -212), (0, 82)], [col((150, 190, 245)), col((85, 125, 200))])))
    c.drawRRect(screen, blurred(fill((140, 185, 255), 0.55), 22))
    for i, w in enumerate((96, 70, 84)):  # faint chat-list rows, all empty: still waiting
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-46, -170 + i * 62, w, 30), 12, 12), fill((210, 225, 255), 0.35))
    c.restore()


def scene(ctx):
    him = Character("thumb3", scale=S)
    J = him.joints(HIP, -1, 0.10)
    hx, hy = J["head"]
    r = HEAD_R * 1.04 * S
    glow(ctx, PHONE[0] + 90, PHONE[1] - 120, 900, BLUE, 0.42)
    him.draw(ctx, HIP, -1, lean=0.10, face=False,
             hands={"near": (PHONE[0] + 18, PHONE[1] + 72), "far": (PHONE[0] + 64, PHONE[1] + 88)})
    shade_head(ctx, hx, hy, r)
    c = ctx.c  # the screen's light spilling onto the underside of his face
    c.save(); c.clipPath(skia.Path.Circle(hx, hy, r * 0.985), skia.ClipOp.kIntersect, True)
    glow(ctx, hx - r * 0.55, hy + r * 0.85, r * 1.1, (140, 185, 255), 0.40)
    c.restore()
    face(ctx, hx, hy, r)
    phone(ctx)
    glow(ctx, PHONE[0] + 40, PHONE[1] - 80, 420, BLUE, 0.38)
    draw_text(ctx, "NEW", 70, 250, 150, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "MESSAGES", 70, 390, 150, TEXT, align="left", face="LuckiestGuy-Regular.ttf")
    draw_text(ctx, "0.", 40, 960, 620, RED, align="left", face="LuckiestGuy-Regular.ttf", glow_rgb=RED_D)
    finish(ctx, bars=False, grain=0.035, vignette=0.6)


def save(img, w, h, path):
    s = skia.Surface(w, h)
    s.getCanvas().drawImageRect(img, skia.Rect.MakeWH(w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    s.makeImageSnapshot().save(str(path))


if __name__ == "__main__":
    img = frame_image(scene, 1.0, 30)
    save(img, 1280, 720, HERE / "ALONE_thumbnail_v3_1280x720.png")
    save(img, 320, 180, HERE / "ALONE_thumbnail_v3_320x180.png")
    print("hand misses:", MISSES or "none")
