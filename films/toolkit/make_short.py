"""Cut a vertical Short (1080x1920) from a finished film: one or more stretches of the master, the picture full width
in the middle, a hook line on top, the film's captions, whispers and speech big under the picture (the film's own text
is too small on a phone at this width), and a call to the full film at the bottom.

    python toolkit/make_short.py allin     (configs below; run from the films folder with the toolkit venv)

Writes <film>/shorts/<NAME>_short_1080x1920.mp4 and a contact sheet of it.
"""
import importlib
import subprocess
import sys
from pathlib import Path

FILMS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FILMS / "toolkit"))
sys.path.insert(0, str(FILMS))
import skia  # noqa: E402

from studio.core import Ctx, draw_text, text_width, fill, rrect, RED, GOLD, TEXT  # noqa: E402
import thumbnails_face as TF  # noqa: E402

SW, SH = 1080, 1920
VY = 560                      # top of the picture
VH = 608                      # 1920x1080 scaled to 1080 wide
SUB_Y = VY + VH + 120         # first subtitle row
CONFIGS = {
    "allin": dict(name="ALL_IN", master="release/ALL_IN_master_1080p.mp4", segments=[(0.0, 34.0), (40.0, 57.5)],
                  hook=("IT STARTED WITH", "ONE SMALL BET.")),
    "onemore": dict(name="ONE_MORE_MATCH", master="release/ONE_MORE_MATCH_master_1080p.mp4", segments=[(0.0, 28.0), (34.0, 54.0)],
                    hook=("HE SAID", "FIVE MINUTES.")),
}


def out_time(segments, t):
    """Where film time t lands in the Short, or None if it was cut."""
    acc = 0.0
    for a, b in segments:
        if a <= t < b:
            return acc + t - a
        acc += b - a
    return None


def lines_in(film_dir, segments):
    """(t0, t1, text, kind) for every caption, whisper and speech bubble that starts inside the Short."""
    sys.path.insert(0, str(film_dir))
    T = importlib.import_module("timeline")
    L = importlib.import_module("lines")
    import json
    lens = json.load(open(film_dir / "build" / "line_lengths.json")) if (film_dir / "build" / "line_lengths.json").exists() else {}
    items = [(t0, t1, L.CAPTIONS[k], "cap") for k, (t0, t1) in T.CAPS.items() if k.startswith("C")]
    items += [(t0, t0 + lens.get(k, 1.4) + 0.5, L.VILLAIN[k], "villain") for k, t0 in T.CUES.items()]
    items += [(t0, t1 + 0.3, f'"{text}"', "speech") for t0, t1, who, text in T.BUBBLES]
    out = []
    for t0, t1, text, kind in items:
        s0 = out_time(segments, t0)
        if s0 is None:
            continue
        seg_end = next(acc + b - a for (a, b), acc in zip(segments, _starts(segments)) if a <= t0 < b)
        out.append((s0, min(seg_end, s0 + t1 - t0), text, kind))
    return sorted(out)


def _starts(segments):
    acc, res = 0.0, []
    for a, b in segments:
        res.append(acc)
        acc += b - a
    return res


def png(path, draw):
    surf = skia.Surface(SW, SH)
    c = surf.getCanvas()
    c.clear(skia.Color4f(0, 0, 0, 0))
    draw(Ctx(c, 0.0, 0))
    surf.makeImageSnapshot().save(str(path))


def wrap(text, size, maxw):
    words, rows, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial.replace("₹", "Rs"), size) > maxw and cur:
            rows.append(cur)
            cur = w
        else:
            cur = trial
    return rows + [cur]


def make(film):
    cfg = CONFIGS[film]
    film_dir = FILMS / film
    out_dir = film_dir / "shorts"
    work = out_dir / "work"
    work.mkdir(parents=True, exist_ok=True)
    segs = cfg["segments"]
    dur = sum(b - a for a, b in segs)
    film_scene = None
    try:
        sys.path.insert(0, str(film_dir))
        film_scene = importlib.import_module("scene")
    except Exception:
        pass
    text = getattr(film_scene, "rtext", None)

    def say(ctx, s, x, y, size, rgb, face="PatrickHand-Regular.ttf", glow_rgb=None):
        if text and "₹" in s:
            text(ctx, s, x, y, size, rgb, 1.0, face=face, glow_rgb=glow_rgb)
        else:
            draw_text(ctx, s, x, y, size, rgb, 1.0, face=face, glow_rgb=glow_rgb)

    def base(ctx):
        TF.outlined(ctx, cfg["hook"][0], SW / 2, 300, 92, align="center")
        TF.outlined(ctx, cfg["hook"][1], SW / 2, 430, 118, rgb=GOLD, align="center")
        rrect(ctx, SW / 2 - 330, 1560, 660, 120, 60, (255, 196, 92), None, a=0.95)
        draw_text(ctx, "FULL FILM ON THE CHANNEL", SW / 2, 1637, 50, (30, 24, 20), face="LuckiestGuy-Regular.ttf")
        draw_text(ctx, "@quietlyhumanfilms", SW / 2, 1740, 40, (190, 190, 196))

    png(work / "base.png", base)
    subs = lines_in(film_dir, segs)
    overlays = []
    for i, (s0, s1, line, kind) in enumerate(subs):
        row = sum(1 for (p0, p1, _, _) in subs[:i] if p0 < s1 and s0 < p1)  # stack lines that overlap in time
        size = 66 if kind != "speech" else 56
        rgb = {"cap": TEXT, "villain": RED, "speech": (200, 220, 255)}[kind]
        rows = wrap(line, size, 940)

        def draw(ctx, rows=rows, size=size, rgb=rgb, row=row, kind=kind):
            y = SUB_Y + row * 150
            for k, r in enumerate(rows):
                say(ctx, r, SW / 2, y + k * size * 1.15, size, rgb, glow_rgb=(120, 16, 18) if kind == "villain" else None)

        p = work / f"sub_{i:02d}.png"
        png(p, draw)
        overlays.append((p, s0, s1))
    # the picture: the chosen stretches of the master, joined
    master = film_dir / cfg["master"]
    parts = []
    for k, (a, b) in enumerate(segs):
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{k}];")
    cat = "".join(f"[v{k}][a{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=1[vc][ac];"
    fc = "".join(parts) + cat
    fc += f"color=c=0x101014:s={SW}x{SH}:r=30:d={dur}[bg];[vc]scale={SW}:{VH}[vs];[bg][vs]overlay=0:{VY}[x0];"
    fc += "[x0][1:v]overlay=0:0[x1];"
    last = "x1"
    for k, (p, s0, s1) in enumerate(overlays):
        fade = f"[{k + 2}:v]format=rgba,fade=t=in:st=0:d=0.2:alpha=1[o{k}];"
        fc += fade + f"[{last}][o{k}]overlay=0:0:enable='between(t,{s0:.2f},{s1:.2f})'[y{k}];"
        last = f"y{k}"
    fc += f"[ac]afade=t=out:st={dur - 1.5}:d=1.5[aout]"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(master), "-loop", "1", "-i", str(work / "base.png")]
    for p, _, _ in overlays:
        cmd += ["-loop", "1", "-i", str(p)]
    out = out_dir / f"{cfg['name']}_short_1080x1920.mp4"
    cmd += ["-filter_complex", fc, "-map", f"[{last}]", "-map", "[aout]", "-t", f"{dur}", "-c:v", "libx264", "-crf", "20",
            "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    # contact sheet: one frame every 4 s
    sheet = out_dir / f"{cfg['name']}_short_sheet.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-vf", "fps=1/4,scale=270:480,tile=7x2", "-frames:v", "1",
                    str(sheet)], check=True)
    print(out, f"{dur:.1f}s", f"{out.stat().st_size / 1e6:.1f} MB", len(overlays), "subtitles")


if __name__ == "__main__":
    make(sys.argv[1])
