"""Contact sheets and the contact check.
  python check.py sheet S02 [S03 ...]   12-frame sheet per scene into build/sheets/
  python check.py contact              hands/feet that miss their targets, whole film
  python check.py frame 12.5           one full-res frame
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scene as S
from studio.render import contact_sheet, save_frame
from studio.character import MISSES
from studio.core import FPS, Ctx, W, H
from timeline import SCENES, DURATION

out = HERE / "build" / "sheets"
out.mkdir(parents=True, exist_ok=True)
cmd = sys.argv[1]
if cmd == "sheet":
    ids = sys.argv[2:] or [s[0] for s in SCENES]
    for sid, t0, t1, beat, what in SCENES:
        if sid in ids:
            contact_sheet(S.scene, t0, t1, out / f"{sid}.png", title=f"{sid} {t0:.1f}-{t1:.1f}s  {beat}: {what[:90]}")
            print("sheet", sid)
elif cmd == "frame":
    t = float(sys.argv[2])
    save_frame(S.scene, t, out / f"frame_{t:07.2f}.png")
elif cmd == "contact":
    import skia
    surf = skia.Surface(320, 180)
    for i in range(int(DURATION * FPS)):
        c = surf.getCanvas(); c.save(); c.scale(320 / W, 180 / H)
        n0 = len(MISSES)
        S.scene(Ctx(c, i / FPS, i)); c.restore()
        for k in range(n0, len(MISSES)):  # helper joints() calls default to frame 0: stamp the real frame
            MISSES[k] = (i,) + tuple(MISSES[k][1:])
    if not MISSES:
        print("CONTACT CHECK: no misses")
    else:
        from collections import defaultdict
        from timeline import scene_at
        agg = defaultdict(list)
        for f, who, limb, gap in MISSES:
            agg[(scene_at(f / FPS)[0], who, limb)].append((f, gap))
        for (sid, who, limb), v in sorted(agg.items()):
            print(f"MISS {sid} {who} {limb}: {len(v)} frames, {v[0][0]/FPS:.2f}-{v[-1][0]/FPS:.2f}s, max gap {max(g for _, g in v)} px")
        for _ in []:
            print(f"MISS {who} {limb}: {len(v)} frames, {v[0][0]/FPS:.2f}-{v[-1][0]/FPS:.2f}s, max gap {max(g for _, g in v)} px")
