"""Render frames in parallel and pipe them to ffmpeg; contact sheets; final-file checks."""
import json
import multiprocessing as mp
import subprocess
from pathlib import Path

import numpy as np
import skia

from .core import W, H, FPS, Ctx, BG, col, draw_text, fill

_scene_fn = None


def frame_image(scene_fn, t, frame, w=W, h=H):
    surf = skia.Surface(w, h)
    c = surf.getCanvas()
    if (w, h) != (W, H):
        c.scale(w / W, h / H)
    c.clear(col(BG))
    scene_fn(Ctx(c, t, frame))
    return surf.makeImageSnapshot()


def save_frame(scene_fn, t, path, w=W, h=H):
    img = frame_image(scene_fn, t, int(round(t * FPS)), w, h)
    img.save(str(path), skia.kPNG)
    return path


def _init(module_path):
    global _scene_fn
    import importlib.util
    spec = importlib.util.spec_from_file_location("film_scene", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _scene_fn = mod.scene


def _job(args):
    i, w, h = args
    from .character import MISSES
    MISSES.clear()
    img = frame_image(_scene_fn, i / FPS, i, w, h)
    arr = img.toarray(colorType=skia.kRGBA_8888_ColorType)
    return arr[:, :, :3].tobytes(), list(MISSES)


def render_video(module_path, out_mp4, duration, w=W, h=H, audio=None, crf=17, workers=4, start=0.0):
    """Render [start, duration) of the film module's scene(ctx) to an mp4. Returns list of contact misses."""
    n0, n1 = int(round(start * FPS)), int(round(duration * FPS))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-ss", str(start), "-i", str(audio), "-c:a", "aac", "-b:a", "256k", "-ac", "2", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(out_mp4)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    misses = []
    with mp.get_context("fork").Pool(workers, initializer=_init, initargs=(str(module_path),)) as pool:
        for k, (buf, ms) in enumerate(pool.imap(_job, [(i, w, h) for i in range(n0, n1)], chunksize=4)):
            proc.stdin.write(buf)
            misses += ms
            if k % 300 == 0:
                print(f"  frame {n0 + k}/{n1}", flush=True)
    proc.stdin.close()
    proc.wait()
    return misses


def contact_sheet(scene_fn, t0, t1, out_png, n=12, cols=4, tw=480, title=""):
    th = int(tw * 9 / 16)
    rows = (n + cols - 1) // cols
    surf = skia.Surface(cols * tw, rows * (th + 34) + 46)
    c = surf.getCanvas()
    c.clear(col((8, 8, 10)))
    times = [t0 + (t1 - t0) * (i + 0.5) / n for i in range(n)]
    from .core import Ctx as _Ctx
    hdr = _Ctx(c, 0, 0)
    draw_text(hdr, title, 14, 32, 26, (230, 230, 230), align="left")
    for i, t in enumerate(times):
        img = frame_image(scene_fn, t, int(round(t * FPS)), tw, th)
        x, y = (i % cols) * tw, 46 + (i // cols) * (th + 34)
        c.drawImage(img, x, y)
        draw_text(hdr, f"{int(t // 60)}:{t % 60:05.2f}", x + 10, y + th + 26, 22, (200, 200, 200), align="left")
    surf.makeImageSnapshot().save(str(out_png), skia.kPNG)
    return times


def mp4_sheet(mp4, out_png, times, cols=5, tw=384):
    """Contact sheet decoded from the finished mp4 itself (always check the final file)."""
    th = int(tw * 9 / 16)
    tmp = Path(out_png).with_suffix("")
    tmp.mkdir(exist_ok=True)
    imgs = []
    for i, t in enumerate(times):
        p = tmp / f"f{i:03d}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1",
                        "-vf", f"scale={tw}:{th}", str(p)], check=True)
        imgs.append(p)
    rows = (len(times) + cols - 1) // cols
    surf = skia.Surface(cols * tw, rows * (th + 30))
    c = surf.getCanvas()
    c.clear(col((8, 8, 10)))
    from .core import Ctx as _Ctx
    hdr = _Ctx(c, 0, 0)
    for i, (t, p) in enumerate(zip(times, imgs)):
        img = skia.Image.open(str(p))
        x, y = (i % cols) * tw, (i // cols) * (th + 30)
        c.drawImage(img, x, y)
        draw_text(hdr, f"{int(t // 60)}:{t % 60:04.1f}", x + 8, y + th + 22, 20, (200, 200, 200), align="left")
    surf.makeImageSnapshot().save(str(out_png), skia.kPNG)
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


def probe(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,channels,sample_rate",
                          "-of", "json", str(mp4)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)
