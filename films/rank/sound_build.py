"""RANK.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Am - F - C - E) on soft piano. Every mock result lands as a low falling pair; the number over his head has
a low hum that grows with it. The exam hall has a ticking clock that gets louder as he panics, then near-silence and
a heartbeat. On the front step the theme turns gentle; the kites at Sankranti resolve it to C major.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BUBBLES, G1_T0, G1_TEST, RELABEL, weight  # noqa: E402

B = HERE / "build"
mix = S.Mix(DURATION)
SR = S.SR

CH = {"Am": [57, 60, 64], "F": [53, 57, 60], "C": [48, 55, 60, 64], "E": [52, 56, 59], "G": [55, 59, 62], "Dm": [50, 53, 57]}
PROG = ["Am", "F", "C", "E"]
WARM = ["F", "C", "G", "C"]
MELODY = [(0, 76), (1, 74), (2, 72), (3, 71), (4, 69), (6, 72), (7, 71), (8, 69), (10, 64), (12, 69)]
MAJOR = [(0, 76), (1, 74), (2, 72), (3, 74), (4, 76), (6, 79), (7, 77), (8, 76), (10, 72), (12, 72)]


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


def party(t0, t1, cutoff, vel):
    """A party band heard through a wall: a bouncy bass-and-chord loop, low-passed."""
    n = int((t1 - t0 + 1.0) * SR)
    x = np.zeros(n, np.float32)
    beat = 60 / 118
    prog = ["C", "Am", "F", "G"]
    k = 0
    while k * beat < t1 - t0:
        ch = CH[prog[(k // 4) % 4]]
        s0 = int(k * beat * SR)
        kick = S.soft_kick(0.9)
        x[s0:s0 + len(kick)] += kick[: max(0, n - s0)]
        if k % 2 == 1:
            for nn in ch:
                p = S.piano(nn, beat * 0.6, 0.35)
                x[s0:s0 + len(p)] += p[: max(0, n - s0)]
        b = S.piano(ch[0] - 24, beat * 0.9, 0.6)
        x[s0:s0 + len(b)] += b[: max(0, n - s0)]
        k += 1
    x = S.lp(x, cutoff) * vel
    fade = int(0.4 * SR)
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    mix.add("amb", t0, x)


def chime(t, vel=0.36):
    """Every "fine": bright, and a little flat underneath."""
    mix.add("music", t, S.music_box(84, 1.0, vel))
    mix.add("music", t + 0.09, S.music_box(79.6, 1.2, vel * 0.8))


def click(t, vel=0.3):
    mix.add("sfx", t, S.tick(vel))
    mix.add("sfx", t, S.whoosh(0.22, vel * 0.6, up=True, seed=int(t * 7)))


bar76 = 4 * 60 / 76
beat76 = 60 / 76
bar92 = 4 * 60 / 92

# ---- score ------------------------------------------------------------------------------------
mix.add("music", 0.2, S.pad(CH["Am"], 6.0, 0.32, 1100, seed=1))
for i, n in enumerate([64, 62, 60]):
    mix.add("music", 0.5 + i * 0.8, S.piano(n, 2.0, 0.36))
chords(6.0, 14.0, bar76, 0.28, ["Am", "F"], "arp")
pads(6.0, 14.0, bar76, 0.18, 1300, ["Am", "F"])
mix.add("music", 14.6, S.pad([33, 45], 8.4, 0.7, 380, seed=7))  # villain drone
mix.add("music", 14.6, S.pad([57, 58], 8.4, 0.12, 900, seed=8))
pads(23.0, 29.0, bar76, 0.28, 1600, ["F", "C"])
melody(23.4, beat76, 0.34, 0, MELODY[:4])
chords(29.0, 63.0, bar76, 0.3, PROG, "low")
pads(29.0, 63.0, bar76, 0.24, 1100, PROG)
chords(49.0, 63.0, bar76, 0.24, ["Dm", "Am"], "arp")
pads(63.0, 75.4, bar92, 0.22, 700, ["Am", "E"])
mix.add("music", 66.0, S.pad([33, 45, 52], 9.4, 0.5, 500, seed=66))
for i, n in enumerate([64, 63, 62, 60]):
    mix.add("music", 76.6 + i * 1.2, S.piano(n, 2.2, 0.34))
pads(82.0, 100.0, bar76, 0.3, 1500, ["Am", "F", "C", "G"])
chords(86.0, 100.0, bar76, 0.24, ["Am", "F", "C", "G"], "arp")
for i, n in enumerate([60, 64, 67]):
    mix.add("music", EVENTS["card"] + i * 0.2, S.music_box(n + 12, 1.6, 0.34))
melody(92.4, beat76, 0.36, 0, MAJOR[:5])
pads(100.0, 110.0, bar76, 0.3, 1700, ["F", "C", "Dm", "E"])
chords(100.4, 110.0, bar76, 0.25, ["F", "C", "Dm", "E"], "arp")
pads(110.0, 116.0, bar76, 0.3, 2000, WARM)
chords(110.4, 116.0, bar76, 0.26, WARM, "arp")
pads(116.0, 117.6, bar76, 0.26, 900, ["Am", "E"])
mix.add("music", 117.6, S.pad([33, 45, 52], 7.4, 0.55, 500, seed=117))
mix.add("music", 117.6, S.pad([57, 58], 7.4, 0.1, 900, seed=118))
mix.add("music", EVENTS["crumble"], S.pad(CH["C"], 3.0, 0.4, 1600, seed=127))
for i, n in enumerate([60, 64, 67]):
    mix.add("music", EVENTS["crumble"] + 0.2 + i * 0.4, S.music_box(n + 12, 2.0, 0.3))
mix.add("sfx", EVENTS["crumble"], S.shimmer(2.6, 0.34, 78))
pads(130.0, 138.0, bar76, 0.3, 1800, ["F", "C"])
chords(135.6, 138.0, bar76, 0.26, ["F", "C"], "arp")
pads(138.0, 152.0, bar76, 0.3, 2400, WARM)
chords(138.0, 152.0, bar76, 0.3, WARM)
melody(140.6, beat76, 0.48, 0, MAJOR)
for i, n in enumerate([72, 76, 79, 84]):
    mix.add("music", RELABEL + i * 0.1, S.music_box(n, 1.6, 0.4))
mix.add("music", 152.2, S.pad(CH["Am"], 6.8, 0.45, 1500, seed=152))
for i, n in enumerate([69, 64, 60]):
    mix.add("music", 152.4 + i * 1.2, S.music_box(n, 2.0, 0.4))
chords(159.0, 168.0, bar76, 0.28, WARM, "arp")
pads(159.0, 168.0, bar76, 0.22, 2000, WARM)
mix.add("music", EVENTS["fade_kid"], S.music_box(81, 2.0, 0.36))
chords(168.4, 175.6, bar76, 0.32, ["F", "G"])
for n in CH["C"] + [72, 76]:
    mix.add("music", 175.2, S.piano(n, 2.6, 0.34))
melody(169.0, beat76, 0.48, 0, MAJOR)
mix.add("music", 177.0, S.pad(CH["F"], 5.0, 0.3, 1400, seed=177))


# ---- the device ----------------------------------------------------------------------------------
def result(t):
    mix.add("music", t, S.piano(45, 1.4, 0.38))
    mix.add("music", t + 0.18, S.piano(41, 1.6, 0.34))
    mix.add("sfx", t, S.thud(0.3))


result(EVENTS["result"])
for tm in EVENTS["g1_results"]:
    result(tm)
    mix.add("sfx", tm - 1.0, S.tap(0.12, seed=int(tm)))
result(EVENTS["times_up"])
# the number's hum, as loud as the number is big
n = int(DURATION * SR)
tt = np.arange(n) / SR
hum = (np.sin(2 * np.pi * 110 * tt) * 0.5 + np.sin(2 * np.pi * 220.7 * tt) * 0.3 + np.sin(2 * np.pi * 330 * tt) * 0.15).astype(np.float32)
grid = np.arange(0, DURATION + 0.01, 0.05)
silent = {"L1", "I1", "VT", "TT", "HL", "P1", "F2", "X1", "B1", "H1"}
from timeline import scene_at  # noqa: E402
env = np.array([0.0 if (scene_at(g)[0] in silent or g < EVENTS["result"]) else weight(g) for g in grid])
env = np.interp(tt, grid, env).astype(np.float32)
mix.add("amb", 0, hum * env * env * 0.03)

# ---- the world ------------------------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.18, seed=int(t0 * 10)))
for k in range(int((75.4 - 63.0) / 0.5)):  # the exam-hall clock, louder as he panics
    t_ = 63.0 + k * 0.5
    mix.add("sfx", t_, S.tick(0.12 + 0.3 * min(1.0, (t_ - 63.0) / 11.0)))
mix.add("sfx", EVENTS["pencil"] + 0.4, S.tap(0.3, seed=7))
mix.add("sfx", EVENTS["times_up"], S.knock(0.35, times=(0,)))
for k in range(5):  # Pihu and Dad in the lane
    mix.add("sfx", 49.4 + k * 0.9, S.tap(0.1, seed=600 + k))
mix.add("sfx", EVENTS["curtain"], S.whoosh(0.5, 0.25, up=False, seed=51))
for tm, x in S.footsteps([82.2 + k * 0.38 for k in range(3)], 0.18):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["card"], S.scribble(0.3, 0.2, seed=8))
mix.add("sfx", EVENTS["card_i"], S.scribble(0.4, 0.25, seed=3))
mix.add("sfx", EVENTS["book"], S.thud(0.3))
mix.add("sfx", EVENTS["lamp"], S.tick(0.4))
mix.add("sfx", EVENTS["lamp_vt"], S.tick(0.4))
for k in range(3):  # the breaths
    mix.add("sfx", EVENTS["breath"] + k * 1.67, S.whoosh(0.8, 0.12, up=True, seed=80 + k))
    mix.add("sfx", EVENTS["breath"] + k * 1.67 + 0.83, S.whoosh(0.8, 0.12, up=False, seed=90 + k))
for k in range(16):
    mix.add("sfx", EVENTS["write"] + k * 0.15, S.scribble(0.12, 0.08, seed=100 + k))
mix.add("sfx", EVENTS["buzz"], S.ringtone(0.5, 0.2))
mix.add("amb", 138.0, S.street(14.0, 0.04, seed=5))
for k in range(12):
    mix.add("sfx", EVENTS["laugh"] + k * 0.1, S.tap(0.12, seed=200 + k))
mix.add("amb", 159.0, S.street(9.0, 0.04, seed=6))

t = 70.0
while t < 75.4:
    k = (t - 70.0) / 5.4
    mix.add("heart", t, S.heartbeat(0.2 + 0.25 * k))
    t += 60 / (80 + 50 * k)
t = 120.0
while t < EVENTS["silence"][1]:
    k = (t - 120.0) / (EVENTS["silence"][1] - 120.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.24 * k))
    t += 60 / (66 + 50 * k)

speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    mix.add("voice", t0, x, 0.9)
    speech.append((t0, t0 + len(x) / SR))
mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart"))
mix.silence_window(75.4, 76.4, keep=("voice", "heart", "sfx"))

end = int((DURATION - 2.0) * SR)
for b in mix.buses.values():
    b[end:] *= np.linspace(1, 0, len(b) - end)

out = mix.render(-2.5, gain_db=float(sys.argv[1]) if len(sys.argv) > 1 else 5.8)
S.write_wav(B / "mix.wav", out)

rows = S.phone_levels(out, [(s[0], s[1], s[2]) for s in SCENES])
med = float(np.median([r[3] for r in rows]))
print("Phone-speaker loudness per scene (300 Hz high-pass, active parts):")
for name, t0, t1, db in rows:
    flag = "  <-- more than 6 dB quieter" if db < med - 6 else ""
    print(f"  {name:4s} {t0:6.1f}-{t1:6.1f}s  {db:6.1f} dBFS{flag}")
print(f"  median {med:.1f} dBFS")
json.dump({"phone_levels": rows, "median": med}, open(B / "levels.json", "w"), indent=1)
