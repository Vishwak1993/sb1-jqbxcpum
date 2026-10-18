"""Final render: 1080p30 master with the mix, a 720p phone copy, a <30 MB download copy, and checks on the finished files."""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
from studio.render import render_video, probe, mp4_sheet
from timeline import DURATION

out = HERE / "build"
master = out / "RAIN_master_1080p.mp4"
phone = out / "RAIN_phone_720p.mp4"
download = out / "RAIN_1080p_download.mp4"
misses = render_video(HERE / "scene.py", master, DURATION, audio=out / "mix.wav", crf=18, workers=4)
print("contact misses during render:", len(misses))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-vf", "scale=1280:720", "-c:v", "libx264", "-crf", "23",
                "-preset", "medium", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(phone)], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-c:v", "libx264", "-crf", "24", "-preset", "slow",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(download)], check=True)
info = {"master": probe(master), "phone": probe(phone), "phone_mb": round(phone.stat().st_size / 1e6, 2),
        "download_mb": round(download.stat().st_size / 1e6, 2)}
json.dump(info, open(out / "final_probe.json", "w"), indent=1)
print(json.dumps(info, indent=1))
mp4_sheet(master, out / "FINAL_CONTACT_SHEET.png", [t + 0.5 for t in range(0, int(DURATION), 8)])
