"""HEAVY.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Dm - Bb - F - C) on low piano: every stone that lands in the sack is a heavy thunk with a low note
under it, so the music sinks as the sack fills. On the hill each stone set down is a soft knock and a high note:
the theme climbs back up. Kai's stone is the last low note; then the sunrise gets the theme in full.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, STONES, DROPS, KAI_DOWN, BUBBLES  # noqa: E402

B = HERE / "build"
mix = S.Mix(DURATION)

CH = {"Dm": [50, 53, 57], "Bb": [46, 50, 53], "F": [41, 48, 53, 57], "C": [48, 52, 55], "Am": [45, 52, 57], "Gm": [43, 50, 55]}
PROG = ["Dm", "Bb", "F", "C"]
WARM = ["F", "C", "Dm", "Bb"]
MELODY = [(0, 69), (1, 72), (2, 74), (3, 72), (4, 69), (6, 67), (7, 65), (8, 67), (10, 62), (12, 65)]
UP = [62, 65, 67, 69, 72, 74, 76, 77, 79, 81, 84, 86, 88, 89]


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


bar70 = 4 * 60 / 70
beat70 = 60 / 70
bar90 = 4 * 60 / 90

mix.add("music", 0.4, S.pad(CH["Dm"], 3.0, 0.35, 1100, seed=1))
mix.add("music", 0.6, S.piano(62, 2.6, 0.42))

chords(3.0, 17.0, bar90, 0.3, PROG, "arp")
pads(3.0, 17.0, bar90, 0.16, 1300)

mix.add("music", 17.2, S.pad(CH["Dm"], 3.0, 0.3, 900, seed=4))
mix.add("music", 19.4, S.pad([26, 38], 7.0, 0.7, 380, seed=7))  # villain drone
mix.add("music", 19.4, S.pad([50, 51], 7.0, 0.12, 900, seed=8))
mix.add("music", 26.2, S.piano(62, 2.8, 0.42))
mix.add("music", 26.2, S.pad(CH["Dm"], 2.8, 0.7, 1500, seed=31))
melody(26.6, 0.6, 0.38, 0, [(0, 69), (1, 67), (2, 65)])

pads(29.0, 37.0, bar70, 0.26, 1300, ["Dm", "Bb"])
melody(34.8, beat70 * 0.9, 0.38, 12, MELODY[:4])  # the hike plan: a small bright hint

chords(37.0, 61.0, bar70, 0.34, PROG, "low")
pads(37.0, 61.0, bar70, 0.24, 1100, PROG)
for i, n in enumerate([69, 67, 65, 62]):
    mix.add("music", 41.4 + i * 4.6, S.piano(n, 3.0, 0.24))
mix.add("music", 57.0, S.pad(CH["Gm"], 4.4, 0.6, 1300, seed=57))
for i, n in enumerate([67, 65, 62]):
    mix.add("music", 57.2 + i * 1.3, S.piano(n, 2.4, 0.4))

pads(61.0, 70.0, bar70, 0.28, 900, ["Dm", "Gm"])
mix.add("music", 65.4, S.pad([26, 38, 50], 8.0, 0.6, 420, seed=9))
mix.add("music", 65.4, S.pad([50, 51], 8.0, 0.1, 900, seed=19))
for i, n in enumerate([62, 60, 57, 53]):
    mix.add("music", 70.4 + i * 1.2, S.piano(n, 2.6, 0.34))

pads(75.0, 93.0, bar70, 0.32, 1700, ["Bb", "F", "C", "Dm"])
melody(78.4, beat70, 0.45, 0, MELODY[:5])
chords(84.0, 93.0, bar70, 0.24, ["Bb", "C"])
melody(87.6, beat70, 0.42)

pads(93.0, 102.0, bar70, 0.26, 1800, WARM)

chords(104.0, 116.2, bar90, 0.36, ["Dm", "Dm", "Bb", "C"], "pulse")
mix.add("music", 103.4, S.pad([26, 38, 45], 12.8, 0.55, 500, seed=10))
mix.add("music", 103.4, S.pad([50, 51], 12.8, 0.1, 900, seed=20))
mix.add("sfx", 113.4, S.whoosh(2.8, 0.25, up=True))

mix.add("sfx", KAI_DOWN, S.hit(0.85))
mix.add("sfx", KAI_DOWN, S.thud(0.9))
mix.add("music", KAI_DOWN, S.piano(38, 3.0, 0.5))  # the last low note
mix.add("sfx", EVENTS["crumble"], S.shimmer(2.6, 0.38, 77))
pads(119.0, 121.0, bar70, 0.5, 2000, ["F"])

pads(121.0, 137.0, bar70, 0.3, 2400, WARM)
chords(122.0, 137.0, bar70, 0.3, WARM)
melody(122.4, beat70, 0.55, 12)
melody(130.6, beat70, 0.45)
mix.add("sfx", EVENTS["high_five"], S.tap(0.6, 3))

mix.add("music", 137.4, S.pad(CH["F"], 9.0, 0.5, 1600, seed=50))
for i, n in enumerate([69, 65, 62]):
    mix.add("music", 137.6 + i * 1.2, S.music_box(n, 2.0, 0.42))
mix.add("sfx", EVENTS["viewer_set"] + 0.8, S.knock(0.5, times=(0,)))
mix.add("music", EVENTS["viewer_set"] + 0.8, S.music_box(81, 2.4, 0.45))

chords(146.0, 156.0, bar70, 0.24, WARM, "arp")
melody(147.0, beat70 * 1.2, 0.36, 0, MELODY[:5])
mix.add("music", EVENTS["kid_set"], S.music_box(84, 2.0, 0.5))

chords(156.4, 163.6, bar70, 0.32, ["Bb", "C"])
for n in CH["F"] + [65, 69]:
    mix.add("music", 163.2, S.piano(n, 2.6, 0.34))
melody(157.0, beat70, 0.5)

# ---- sound effects -----------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
mix.add("amb", 3.0, S.bp(S.rng(41).normal(0, 1, int(3.6 * S.SR)).astype(np.float32), 300, 1200) * 0.03)  # office
mix.add("amb", 6.6, S.lp(S.rng(42).normal(0, 1, int(2.6 * S.SR)).astype(np.float32), 1800) * 0.03)  # café
mix.add("amb", 9.2, S.street(2.6, 0.06))
mix.add("amb", 37.0, S.street(4.0, 0.05, seed=33))
mix.add("amb", 49.0, S.bp(S.rng(43).normal(0, 1, int(4.0 * S.SR)).astype(np.float32), 800, 6000) * 0.05)  # shower
mix.add("amb", 61.0, S.bp(S.rng(44).normal(0, 1, int(60.0 * S.SR)).astype(np.float32), 400, 3000) * 0.015)  # wind on the hill
mix.add("amb", 146.0, S.street(10.0, 0.04, seed=35))

# every stone into the sack: a heavy thunk and a low piano note
for i, (tm, lab, kg) in enumerate(STONES):
    mix.add("sfx", tm, S.thud(min(1.0, 0.45 + kg * 0.05)))
    mix.add("sfx", tm, S.knock(0.35, times=(0,)))
    mix.add("music", tm, S.piano(38 + (i % 4) * 2, 1.4, 0.32))
# every stone set down: a soft knock and a note that climbs
for i, (tm, lab) in enumerate(DROPS):
    mix.add("sfx", tm + 0.3, S.knock(0.3, times=(0,)))
    mix.add("music", tm + 0.3, S.music_box(UP[min(i, len(UP) - 1)], 1.2, 0.36))

mix.add("sfx", EVENTS["splash"], S.whoosh(0.5, 0.5, up=False, seed=60))
mix.add("sfx", EVENTS["splash"] + 0.1, S.bp(S.rng(61).normal(0, 1, int(0.6 * S.SR)).astype(np.float32), 600, 4000) * 0.2)
for tm in (EVENTS["dad_text"], EVENTS["kai_text"], EVENTS["hike_text"], EVENTS["hike_text"] + 0.6):
    mix.add("sfx", tm, S.tick(0.35))
mix.add("sfx", EVENTS["slip"], S.whoosh(0.6, 0.45, up=False, seed=62))
mix.add("sfx", EVENTS["slip"] + 1.0, S.thud(0.6))
for tm, x in S.footsteps([37.2 + k * 0.6 for k in range(6)], 0.3):
    mix.add("sfx", tm, x)
for tm, x in S.footsteps([61.8 + k * 0.7 for k in range(6)], 0.28):
    mix.add("sfx", tm, x)
for tm, x in S.footsteps([121.2 + k * 0.32 for k in range(18)], 0.26):
    mix.add("sfx", tm, x)
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.2, seed=int(t0 * 10)))
mix.add("sfx", EVENTS["kid_shove"], S.thud(0.3))

t = 106.0
while t < KAI_DOWN:
    k = (t - 106.0) / (KAI_DOWN - 106.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.22 * k))
    t += 60 / (66 + 60 * k)

speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    mix.add("voice", t0, x, 0.9)
    speech.append((t0, t0 + len(x) / S.SR))
mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart"))

end = int((DURATION - 2.0) * S.SR)
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
