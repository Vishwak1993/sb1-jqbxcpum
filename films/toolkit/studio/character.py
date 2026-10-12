"""The recurring character: pale, round head, tube limbs, no hair, no nose.

Hands and feet are placed by two-bone IK on exact target points. Any target the
limb cannot reach is logged in MISSES (frame, limb, gap in px) for the contact check.
"""
import math

from .core import (LINE, SKIN, SKIN_SHADE, BLUE, fill, stroke, wobble_points, poly_path, circle_pts,
                   glow, blurred, col, lerp)

MISSES = []  # (frame, who, limb, gap_px)

# proportions (px at scale 1)
TORSO = 92
NECK = 14
HEAD_R = 50
UPPER_ARM, FORE_ARM = 52, 50
THIGH, SHIN = 60, 58
BODY_W = 50
LIMB_W = 19
OUT = 3.2  # outline thickness


def ik(a, target, l1, l2, bend):
    """Return (joint, end) for a two-bone limb from a to target. bend=+1/-1 picks the elbow side."""
    dx, dy = target[0] - a[0], target[1] - a[1]
    d = math.hypot(dx, dy)
    reach = l1 + l2 - 0.01
    gap = max(0.0, d - reach)
    d = max(min(d, reach), abs(l1 - l2) + 0.01)
    ang = math.atan2(dy, dx)
    cos_a = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    a1 = ang + bend * math.acos(max(-1, min(1, cos_a)))
    j = (a[0] + l1 * math.cos(a1), a[1] + l1 * math.sin(a1))
    e = (a[0] + d * math.cos(ang), a[1] + d * math.sin(ang))
    return j, e, gap


EXPR = {
    # brows: (inner_dy, outer_dy) +down. eyes: openness 0..1. mouth: kind, curve
    "neutral":    dict(brow=(0, 0), eye=1.0, mouth=("line", 0.0)),
    "sad":        dict(brow=(-6, 4), eye=0.8, mouth=("curve", -5)),
    "happy":      dict(brow=(-2, -2), eye=0.9, mouth=("curve", 7)),
    "smile":      dict(brow=(-1, -1), eye=0.75, mouth=("curve", 5)),
    "tired":      dict(brow=(-2, 3), eye=0.45, mouth=("line", 0.0), bags=True),
    "worried":    dict(brow=(-7, 3), eye=1.0, mouth=("curve", -3)),
    "shocked":    dict(brow=(-6, -6), eye=1.25, mouth=("o", 0)),
    "determined": dict(brow=(6, -3), eye=0.85, mouth=("line", 0.0)),
    "hurt":       dict(brow=(-8, 4), eye=0.6, mouth=("curve", -6)),
    "closed":     dict(brow=(-3, 2), eye=0.0, mouth=("line", 0.0)),
    "hopeful":    dict(brow=(-5, -1), eye=1.05, mouth=("curve", 2)),
    "anxious":    dict(brow=(-9, 2), eye=1.4, mouth=("curve", -2)),
}


class Character:
    def __init__(self, name="him", skin=SKIN, scale=1.0, extra=None):
        self.name, self.skin, self.scale, self.extra = name, skin, scale, extra

    # -- geometry ------------------------------------------------------------
    def joints(self, hip, facing=1, lean=0.0, head_tilt=0.0, hands=None, feet=None, bend=None, frame=0):
        """hip: (x,y). lean: radians (+ leans forward). hands/feet: dict near/far -> target point."""
        s = self.scale
        ang = -math.pi / 2 + facing * lean
        shoulder = (hip[0] + math.cos(ang) * TORSO * s, hip[1] + math.sin(ang) * TORSO * s)
        hang = ang + facing * head_tilt
        neck = (shoulder[0] + math.cos(ang) * NECK * s, shoulder[1] + math.sin(ang) * NECK * s)
        head = (neck[0] + math.cos(hang) * HEAD_R * 0.9 * s, neck[1] + math.sin(hang) * HEAD_R * 0.9 * s)
        sh_near = (shoulder[0] + facing * 4 * s, shoulder[1] + 6 * s)
        sh_far = (shoulder[0] - facing * 4 * s, shoulder[1] + 6 * s)
        hp_near = (hip[0] + facing * 5 * s, hip[1])
        hp_far = (hip[0] - facing * 5 * s, hip[1])
        hands = hands or {}
        feet = feet or {}
        bend = bend or {}
        out = dict(hip=hip, shoulder=shoulder, head=head, facing=facing, limbs={})
        rest_hand = lambda shp, k: (shp[0] + facing * (8 + 4 * k) * s, shp[1] + (UPPER_ARM + FORE_ARM - 3) * s)
        rest_foot = lambda hpp, k: (hpp[0] + facing * 6 * s * k, hpp[1] + (THIGH + SHIN - 2) * s)
        for side, shp, k in (("near", sh_near, 1), ("far", sh_far, -1)):
            tgt = hands.get(side) or rest_hand(shp, k)
            b = bend.get("arm_" + side, facing)
            j, e, gap = ik(shp, tgt, UPPER_ARM * s, FORE_ARM * s, b)
            if gap > 1.5 and side in hands:
                MISSES.append((frame, self.name, "hand_" + side, round(gap, 1)))
            out["limbs"]["arm_" + side] = (shp, j, e)
        for side, hpp, k in (("near", hp_near, 1), ("far", hp_far, -1)):
            tgt = feet.get(side) or rest_foot(hpp, k)
            b = bend.get("leg_" + side, -facing)
            j, e, gap = ik(hpp, tgt, THIGH * s, SHIN * s, b)
            if gap > 1.5 and side in feet:
                MISSES.append((frame, self.name, "foot_" + side, round(gap, 1)))
            out["limbs"]["leg_" + side] = (hpp, j, e)
        return out

    # -- drawing -------------------------------------------------------------
    def _limb(self, ctx, pts, key, shade=False, width=LIMB_W):
        s = self.scale
        p = wobble_points(ctx, list(pts), key, 0.8)
        path = poly_path(p, closed=False)
        ctx.c.drawPath(path, stroke(LINE, (width + OUT * 2) * s))
        ctx.c.drawPath(path, stroke(SKIN_SHADE if shade else self.skin, width * s))

    def draw(self, ctx, hip, facing=1, lean=0.0, head_tilt=0.0, hands=None, feet=None, bend=None,
             expr="neutral", look=(0, 0), blink=False, screen_glow=0.0, near_arm_front=True, alpha=1.0,
             mouth_open=0.0, tear=0.0, glow_rgb=None, face=True):
        """face=False draws a blank head so a close-up (e.g. a thumbnail) can paint its own detailed face."""
        J = self.joints(hip, facing, lean, head_tilt, hands, feet, bend, ctx.frame)
        if alpha < 1:
            ctx.c.saveLayerAlpha(None, int(alpha * 255))
        L = J["limbs"]
        key = self.name
        if glow_rgb is not None:
            glow(ctx, J["head"][0], J["head"][1] + 60 * self.scale, 220 * self.scale, glow_rgb, 0.22)
        self._limb(ctx, L["arm_far"], (key, "af"), shade=True)
        self._limb(ctx, L["leg_far"], (key, "lf"), shade=True)
        self._limb(ctx, [J["hip"], J["shoulder"]], (key, "t"), width=BODY_W)
        self._limb(ctx, L["leg_near"], (key, "ln"))
        if not near_arm_front:
            self._limb(ctx, L["arm_near"], (key, "an"))
        self._head(ctx, J, expr, look, blink, screen_glow, mouth_open, tear, face)
        if near_arm_front:
            self._limb(ctx, L["arm_near"], (key, "an"))
        if alpha < 1:
            ctx.c.restore()
        return J

    def _head(self, ctx, J, expr, look, blink, screen_glow, mouth_open, tear, face=True):
        s = self.scale
        hx, hy = J["head"]
        f = J["facing"]
        pts = wobble_points(ctx, circle_pts(hx, hy, HEAD_R * s, HEAD_R * 1.04 * s, 30), (self.name, "h"), 0.9)
        path = poly_path(pts, smooth=True)
        ctx.c.drawPath(path, fill(self.skin))
        ctx.c.drawPath(path, stroke(LINE, OUT * s))
        if self.extra:
            self.extra(ctx, hx, hy, f, s)
        if not face:
            return
        e = EXPR.get(expr, EXPR["neutral"])
        # face sits toward the facing side (three-quarter view)
        fx = hx + f * 14 * s + look[0] * 4 * s
        fy = hy + 2 * s + look[1] * 3 * s
        spread = 13 * s
        openness = 0.0 if blink else e["eye"]
        for i, side in enumerate((-1, 1)):
            ex = fx + side * spread
            ey = fy - 4 * s
            if openness <= 0.08:
                ctx.c.drawPath(poly_path([(ex - 6 * s, ey + 1 * s), (ex, ey + 3 * s), (ex + 6 * s, ey + 1 * s)], False, True),
                               stroke(LINE, 3 * s))
            else:
                ctx.c.drawOval(_oval(ex, ey, 4.6 * s, 6.5 * s * min(1.3, openness)), fill(LINE))
                if screen_glow > 0:
                    ctx.c.drawCircle(ex + 1.5 * s, ey - 2 * s, 1.8 * s, fill(BLUE, screen_glow))
            # brows: inner end toward the face centre
            bi, bo = e["brow"]
            inner = (ex - side * 1 * s, ey - 15 * s + bi * s * 0.9)
            outer = (ex + side * 9 * s, ey - 15 * s + bo * s * 0.9)
            ctx.c.drawLine(inner[0], inner[1], outer[0], outer[1], stroke(LINE, 3.2 * s))
            if e.get("bags"):
                ctx.c.drawPath(poly_path([(ex - 5 * s, ey + 8 * s), (ex, ey + 10 * s), (ex + 5 * s, ey + 8 * s)], False, True),
                               stroke(SKIN_SHADE, 2.2 * s))
        mk, curve = e["mouth"]
        my = fy + 17 * s
        mw = 9 * s
        if mouth_open > 0.05 or mk == "o":
            o = max(mouth_open, 0.6 if mk == "o" else 0)
            ctx.c.drawOval(_oval(fx, my, 5 * s, 4 * s * o + 1.5 * s), fill(LINE))
        elif mk == "curve":
            ctx.c.drawPath(poly_path([(fx - mw, my - curve * 0.25 * s), (fx, my + curve * s * 0.6), (fx + mw, my - curve * 0.25 * s)], False, True),
                           stroke(LINE, 3 * s))
        else:
            ctx.c.drawLine(fx - mw * 0.7, my, fx + mw * 0.7, my, stroke(LINE, 3 * s))
        if tear > 0:
            tx, ty = fx + spread + 2 * s, fy + 4 * s + tear * 26 * s
            ctx.c.drawOval(_oval(tx, ty, 2.6 * s, 4 * s), fill((150, 190, 255), 0.9 * (1 - max(0, tear - 0.8) * 5)))


def _oval(cx, cy, rx, ry):
    import skia
    return skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)


# -- poses -------------------------------------------------------------------
def standing(hip_x, floor_y, facing=1, s=1.0, step=0.0):
    """Hip point and foot targets for standing/walking. step: walk phase in cycles."""
    hip = (hip_x, floor_y - (THIGH + SHIN - 4) * s)
    if step == 0.0:
        return hip, {"near": (hip_x + facing * 10 * s, floor_y), "far": (hip_x - facing * 8 * s, floor_y)}
    ph = step * 2 * math.pi
    stride = 26 * s
    near_x = hip_x + facing * stride * math.sin(ph)
    far_x = hip_x - facing * stride * math.sin(ph)
    lift_n = max(0, math.cos(ph)) * 10 * s
    lift_f = max(0, -math.cos(ph)) * 10 * s
    bob = abs(math.sin(ph)) * 4 * s
    hip = (hip_x, floor_y - (THIGH + SHIN - 6) * s + bob)
    return hip, {"near": (near_x, floor_y - lift_n), "far": (far_x, floor_y - lift_f)}


def walk_x(x0, t, speed, s=1.0):
    """Ground speed matched to stride so feet never slide: one cycle = 4 * stride."""
    stride = 26 * s
    x = x0 + speed * t
    phase = abs(speed * t) / (4 * stride)
    return x, phase


def seated(seat_x, seat_y, facing=1, s=1.0, floor_y=780):
    """Hip on the seat, feet planted on the floor in front. Seat should be ~90 px above floor."""
    hip = (seat_x, seat_y - 4 * s)
    dy = floor_y - hip[1]
    reach = (THIGH + SHIN - 6) * s
    dx = max(20 * s, (max(0.0, reach ** 2 - dy ** 2)) ** 0.5)
    return hip, {"near": (seat_x + facing * dx, floor_y), "far": (seat_x + facing * (dx - 10 * s), floor_y)}
