"""RAIN.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Dm - Bb - F - A) on soft piano, under a bed of rain whose loudness follows the cloud. Every complaint is
a low falling pair of notes with a soft thunder; every time he holds one back, a small rising music-box note. When he
asks Nia about her mum, the rain stops at once and the theme resolves to D major with the sun.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BUBBLES, FEEDS, SHRINKS, CLEAR_T, cloud_k, scene_at  # noqa: E402

B = HERE / "build"
mix = S.Mix(DURATION)

CH = {"Dm": [50, 53, 57], "Bb": [46, 50, 53], "F": [41, 48, 53, 57], "A": [45, 49, 52], "Gm": [43, 50, 55], "D": [50, 54, 57],
      "C": [48, 52, 55]}
PROG = ["Dm", "Bb", "F", "A"]
WARM = ["Bb", "F", "C", "D"]
MELODY = [(0, 69), (1, 74), (2, 72), (3, 69), (4, 65), (6, 67), (7, 69), (8, 65), (10, 62), (12, 66)]
SR = S.SR


def chords(t0, t1, bar, vel=0.3, prog=PROG, style="block"):
    t, i = t0, 0
    while t < t1 - 0.1:
        notes = CH[prog[i % len(prog)]]
        if style == "block":
            for n in notes:
                mix.add("music", t, S.piano(n, bar * 0.95, vel))
        elif style == "arp":
            for k in range(8):
                n = notes[k % len(notes)] + (12 if k >= 4 else 0)
                mix.add("music", t + k * bar / 8, S.piano(n, bar / 3, vel * 0.8))
        elif style == "low":
            mix.add("music", t, S.piano(notes[0] - 12, bar, vel))
            mix.add("music", t + bar / 2, S.piano(notes[1] - 12, bar / 2, vel * 0.7))
        elif style == "pulse":
            for k in range(4):
                for n in notes[:2]:
                    mix.add("music", t + k * bar / 4, S.piano(n - 12, bar / 5, vel * 0.7))
        t += bar
        i += 1


def pads(t0, t1, bar, vel=0.3, bright=1500, prog=PROG):
    t, i = t0, 0
    while t < t1 - 0.1:
        d = min(bar * 1.15, t1 - t + 0.4)
        mix.add("music", t, S.pad(CH[prog[i % len(prog)]], d, vel, bright, seed=i))
        t += bar
        i += 1


def melody(t0, beat, vel=0.5, octave=0, notes=MELODY, inst=S.music_box):
    for b, n in notes:
        mix.add("music", t0 + b * beat, inst(n + octave, beat * 2.2, vel))


def _unused_crackle(t, vel=0.35, seed=0):
    """The FRAUD flicker: a short electrical crackle and a dissonant high pair."""
    n = int(0.35 * SR)
    x = S.rng(200 + seed).normal(0, 1, n).astype(np.float32)
    gate = (S.rng(300 + seed).random(n // 400 + 1) > 0.45).repeat(400)[:n].astype(np.float32)
    x = S.bp(x * gate, 1500, 7000) * np.linspace(1, 0.2, n).astype(np.float32) * vel
    mix.add("sfx", t, x)
    mix.add("music", t, S.music_box(81, 0.8, vel * 0.9))
    mix.add("music", t + 0.02, S.music_box(82, 0.8, vel * 0.7))


bar76 = 4 * 60 / 76
beat76 = 60 / 76
bar92 = 4 * 60 / 92


bar76 = 4 * 60 / 76
beat76 = 60 / 76
bar92 = 4 * 60 / 92

# ---- score ------------------------------------------------------------------------------------
mix.add("music", 0.3, S.pad(CH["Dm"], 4.4, 0.36, 1100, seed=1))
for i, n in enumerate([62, 60, 57]):
    mix.add("music", 0.6 + i * 1.2, S.piano(n, 2.4, 0.42))
chords(4.5, 19.0, bar92, 0.28, PROG, "arp")
pads(4.5, 19.0, bar92, 0.16, 1300)
mix.add("music", 19.2, S.pad([26, 38], 7.8, 0.7, 380, seed=7))  # villain drone
mix.add("music", 19.2, S.pad([50, 51], 7.8, 0.12, 900, seed=8))
pads(27.0, 33.0, bar76, 0.28, 1500, ["F", "C"])
melody(27.6, beat76, 0.36, 0, MELODY[:4])
chords(33.0, 59.0, bar76, 0.32, PROG, "low")
pads(33.0, 59.0, bar76, 0.24, 1100, PROG)
for i, n in enumerate([69, 67, 65, 64]):
    mix.add("music", 47.4 + i * 1.4, S.piano(n, 2.4, 0.3))
pads(59.0, 68.0, bar76, 0.3, 900, ["Dm", "A"])
for i, n in enumerate([62, 61, 60, 57]):
    mix.add("music", 59.6 + i * 2.0, S.piano(n, 2.4, 0.34))
mix.add("music", 73.0, S.pad(CH["Gm"], 5.6, 0.5, 1100, seed=73))
mix.add("music", 79.0, S.pad(CH["Dm"], 3.0, 0.55, 1000, seed=79))
mix.add("music", 79.2, S.piano(50, 3.0, 0.5))
pads(82.0, 94.0, bar76, 0.32, 1700, ["Bb", "F", "Gm", "A"])
chords(82.4, 94.0, bar76, 0.26, ["Bb", "F", "Gm", "A"], "arp")
melody(86.0, beat76, 0.4, 12, MELODY[:5])
pads(94.0, 104.0, bar76, 0.3, 2000, WARM)
chords(97.4, 104.0, bar76, 0.28, WARM, "arp")
chords(104.4, 115.4, bar92, 0.34, ["Dm", "Dm", "Bb", "A"], "pulse")
mix.add("music", 106.8, S.pad([26, 38, 45], 8.6, 0.55, 500, seed=10))
mix.add("music", 106.8, S.pad([50, 51], 8.6, 0.1, 900, seed=20))
mix.add("music", CLEAR_T, S.pad(CH["D"], 5.6, 0.55, 2000, seed=40))
for i, n in enumerate([62, 66, 69, 74]):
    mix.add("music", CLEAR_T + 0.1 + i * 0.3, S.music_box(n, 2.0, 0.48))
mix.add("sfx", EVENTS["crumble"], S.shimmer(2.6, 0.38, 78))
pads(125.0, 135.0, bar76, 0.3, 2400, WARM)
chords(125.0, 135.0, bar76, 0.3, WARM)
melody(125.4, beat76, 0.5, 12)
mix.add("music", 135.4, S.pad(CH["F"], 8.6, 0.5, 1600, seed=50))
for i, n in enumerate([69, 65, 62]):
    mix.add("music", 135.6 + i * 1.3, S.music_box(n, 2.0, 0.42))
for i, n in enumerate([74, 78, 81]):
    mix.add("music", EVENTS["viewer_break"] + i * 0.12, S.music_box(n, 2.0, 0.45))
chords(144.0, 153.0, bar76, 0.26, WARM, "arp")
mix.add("music", EVENTS["stranger_up"], S.music_box(81, 2.0, 0.42))
chords(153.4, 160.6, bar76, 0.32, ["Bb", "C"])
for n in CH["D"] + [62, 66]:
    mix.add("music", 160.2, S.piano(n, 2.6, 0.34))
melody(154.0, beat76, 0.5)

# ---- the rain, as loud as the cloud is big ------------------------------------------------------
rain = S.rain(DURATION, 0.09, seed=12)
ts = np.arange(len(rain)) / SR
grid = np.arange(0, DURATION + 0.01, 0.01)
silent = {"B1", "TT", "VT"}
env = np.array([0.0 if scene_at(t)[0] in silent else cloud_k(t) for t in grid])
env = np.interp(ts, grid, env).astype(np.float32)
mix.add("amb", 0, (rain * (0.15 + 0.85 * env) * env).astype(np.float32))

# ---- sound effects -----------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
for tm in FEEDS:  # every complaint feeds the cloud: a low falling pair and a soft rumble
    mix.add("music", tm, S.piano(45, 1.4, 0.34))
    mix.add("music", tm + 0.18, S.piano(41, 1.6, 0.3))
    mix.add("sfx", tm, S.thud(0.35))
for tm in SHRINKS:  # held back: a small rising note
    mix.add("music", tm, S.music_box(74, 1.2, 0.4))
    mix.add("music", tm + 0.12, S.music_box(78, 1.2, 0.36))
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.2, seed=int(t0 * 10)))
for tm in (EVENTS["nia_text"], EVENTS["his_reply"]):
    mix.add("sfx", tm, S.tick(0.35))
mix.add("sfx", EVENTS["umbrella"], S.whoosh(0.3, 0.3, up=True, seed=71))
for k in range(2):
    mix.add("sfx", EVENTS["umbrellas"] + k * 0.25, S.whoosh(0.3, 0.3, up=True, seed=72 + k))
mix.add("sfx", EVENTS["door"], S.knock(0.3, times=(0,)))
for tm, x in S.footsteps([47.2 + k * 0.62 for k in range(9)], 0.26):
    mix.add("sfx", tm, x)
for k in range(16):
    mix.add("sfx", EVENTS["laugh"] + k * 0.11, S.tap(0.12, seed=200 + k))
mix.add("sfx", EVENTS["card"], S.scribble(0.4, 0.25, seed=3))

t = 109.0
while t < EVENTS["silence"][1]:
    k = (t - 109.0) / (EVENTS["silence"][1] - 109.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.24 * k))
    t += 60 / (66 + 60 * k)

speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    mix.add("voice", t0, x, 0.9)
    speech.append((t0, t0 + len(x) / SR))
mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart"))

end = int((DURATION - 2.0) * SR)
for b in mix.buses.values():
    b[end:] *= np.linspace(1, 0, len(b) - end)

out = mix.render(-2.5, gain_db=float(sys.argv[1]) if len(sys.argv) > 1 else 4.4)
S.write_wav(B / "mix.wav", out)

rows = S.phone_levels(out, [(s[0], s[1], s[2]) for s in SCENES])
med = float(np.median([r[3] for r in rows]))
print("Phone-speaker loudness per scene (300 Hz high-pass, active parts):")
for name, t0, t1, db in rows:
    flag = "  <-- more than 6 dB quieter" if db < med - 6 else ""
    print(f"  {name:4s} {t0:6.1f}-{t1:6.1f}s  {db:6.1f} dBFS{flag}")
print(f"  median {med:.1f} dBFS")
json.dump({"phone_levels": rows, "median": med}, open(B / "levels.json", "w"), indent=1)
