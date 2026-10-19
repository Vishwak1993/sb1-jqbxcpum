"""MIRROR.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Dm - Bb - F - A) on soft piano over the gym's muffled beat and the clank of dumbbells. Every body he
measures himself against is a small falling tick, and a low hum grows as his reflection shrinks. The photo session is
a run of 37 shutter clicks. At the pool: water, kids, then near-silence and his heartbeat; the hoodie comes off, the
villain breaks, a splash, and underwater everything is muffled and warm. The race resolves the theme to F major.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BUBBLES, COUNTS, RELABEL, PHOTOS, G1_T0, G1_WEEK, scene_at, refl_at  # noqa: E402

B = HERE / "build"
mix = S.Mix(DURATION)
SR = S.SR

CH = {"Dm": [50, 53, 57], "Bb": [46, 50, 53], "F": [53, 57, 60], "A": [45, 49, 52], "C": [48, 52, 55], "Gm": [55, 58, 62],
      "Am": [57, 60, 64]}
PROG = ["Dm", "Bb", "F", "A"]
WARM = ["Bb", "F", "C", "F"]
MELODY = [(0, 74), (1, 72), (2, 70), (3, 69), (4, 67), (6, 70), (7, 69), (8, 67), (10, 62), (12, 67)]
MAJOR = [(0, 72), (1, 70), (2, 69), (3, 70), (4, 72), (6, 77), (7, 76), (8, 74), (10, 72), (12, 69)]


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


def gym_beat(t0, t1, vel=0.5, cutoff=420):
    """The gym's speaker through the walls: a kick and a bass on every beat, low-passed."""
    n = int((t1 - t0 + 0.6) * SR)
    x = np.zeros(n, np.float32)
    beat = 60 / 124
    k = 0
    while k * beat < t1 - t0:
        s0 = int(k * beat * SR)
        kick = S.soft_kick(0.9)
        x[s0:s0 + len(kick)] += kick[: max(0, n - s0)]
        b = S.piano([38, 38, 41, 36][(k // 4) % 4], beat * 0.8, 0.5)
        x[s0:s0 + len(b)] += b[: max(0, n - s0)]
        k += 1
    x = S.lp(x, cutoff) * vel
    f = int(0.3 * SR)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    mix.add("amb", t0, x)


def clank(t, vel=0.18, seed=0):
    mix.add("sfx", t, S.clink(vel, seed=seed, bounces=1))


def shutter(t, vel=0.22):
    mix.add("sfx", t, S.tick(vel))
    mix.add("sfx", t + 0.04, S.tick(vel * 0.7))


def splash(t, vel=0.5, dur=1.0, seed=3):
    x = S.rain(dur, 1.0, seed=seed)
    e = np.exp(-np.linspace(0, 6, len(x))).astype(np.float32)
    mix.add("sfx", t, S.hp(x * e, 300) * vel)
    mix.add("sfx", t, S.thud(vel * 0.6))


def water(t0, dur, vel=0.05, seed=20):
    x = S.lp(S.rain(dur, 1.0, seed=seed), 900) * vel
    f = int(0.4 * SR)
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    mix.add("amb", t0, x)


bar80 = 4 * 60 / 80
beat80 = 60 / 80
bar96 = 4 * 60 / 96

# ---- score ------------------------------------------------------------------------------------
mix.add("music", 0.2, S.pad(CH["Dm"], 6.0, 0.3, 1100, seed=1))
for i, n in enumerate([62, 60, 58, 57]):
    mix.add("music", 0.4 + i * 0.9, S.piano(n, 2.0, 0.34))
chords(6.0, 14.0, bar80, 0.26, ["Dm", "Bb"], "arp")
pads(6.0, 14.0, bar80, 0.18, 1300, ["Dm", "Bb"])
mix.add("music", 14.6, S.pad([38, 50], 8.4, 0.7, 380, seed=7))  # villain drone
mix.add("music", 14.6, S.pad([62, 63], 8.4, 0.12, 900, seed=8))
pads(23.0, 29.0, bar80, 0.28, 1700, ["F", "C"])
melody(23.4, beat80, 0.34, 0, MAJOR[:4])
chords(29.0, 49.0, bar80, 0.3, PROG, "low")
pads(29.0, 49.0, bar80, 0.24, 1100, PROG)
chords(49.0, 63.0, bar80, 0.26, ["Gm", "Dm"], "arp")
pads(49.0, 63.0, bar80, 0.22, 1300, ["Gm", "Dm"])
pads(63.0, 75.0, bar96, 0.22, 700, ["Dm", "A"])
mix.add("music", 68.6, S.pad([38, 50, 57], 6.4, 0.5, 500, seed=66))
for i, n in enumerate([62, 61, 60, 58]):
    mix.add("music", 76.2 + i * 1.3, S.piano(n, 2.2, 0.34))
pads(82.0, 100.0, bar80, 0.28, 1500, ["Dm", "Bb", "F", "C"])
chords(86.0, 100.0, bar80, 0.22, ["Dm", "Bb", "F", "C"], "arp")
for i, n in enumerate([69, 65, 62]):
    mix.add("music", EVENTS["big_scroll"] + 0.4 + i * 0.5, S.music_box(n, 1.8, 0.3))
melody(95.2, beat80, 0.34, 0, MAJOR[:5])
pads(100.0, 110.0, bar80, 0.3, 1700, ["Bb", "F", "Gm", "A"])
chords(100.4, 110.0, bar80, 0.25, ["Bb", "F", "Gm", "A"], "arp")
pads(110.0, 116.0, bar80, 0.3, 2000, WARM)
chords(110.4, 116.0, bar80, 0.26, WARM, "arp")
pads(116.0, 117.6, bar80, 0.26, 1200, ["Dm", "A"])
mix.add("music", 117.6, S.pad([38, 50, 57], 7.4, 0.55, 500, seed=117))
mix.add("music", 117.6, S.pad([62, 63], 7.4, 0.1, 900, seed=118))
mix.add("music", EVENTS["crumble"], S.pad(CH["F"], 3.0, 0.4, 1600, seed=127))
for i, n in enumerate([65, 69, 72]):
    mix.add("music", EVENTS["crumble"] + 0.2 + i * 0.4, S.music_box(n + 12, 2.0, 0.3))
mix.add("sfx", EVENTS["crumble"], S.shimmer(2.6, 0.34, 77))
# underwater: the theme muffled and warm
uw = np.zeros(int(8.6 * SR), np.float32)
for i, ch in enumerate(["F", "C", "Bb", "F"]):
    p = S.pad(CH[ch] + [CH[ch][0] + 12], 2.4, 0.5, 900, seed=130 + i)
    s0 = int(i * 2.1 * SR)
    uw[s0:s0 + len(p)] += p[: len(uw) - s0]
for b, n in MAJOR[:6]:
    m = S.music_box(n, 1.4, 0.4)
    s0 = int((0.8 + b * beat80) * SR)
    uw[s0:s0 + len(m)] += m[: max(0, len(uw) - s0)]
mix.add("music", 129.6, S.lp(uw, 1400) * 1.4)
pads(138.0, 152.0, bar80, 0.3, 2400, WARM)
chords(138.0, 152.0, bar80, 0.3, WARM, "arp")
melody(139.4, beat80, 0.48, 0, MAJOR)
for i, n in enumerate([72, 77, 81, 84]):
    mix.add("music", RELABEL + i * 0.1, S.music_box(n, 1.6, 0.4))
mix.add("music", 152.2, S.pad(CH["Dm"], 6.8, 0.45, 1500, seed=152))
for i, n in enumerate([69, 65, 62]):
    mix.add("music", 152.4 + i * 1.2, S.music_box(n, 2.0, 0.4))
chords(159.0, 168.0, bar80, 0.28, WARM, "arp")
pads(159.0, 168.0, bar80, 0.22, 2000, WARM)
for i, n in enumerate([77, 81, 84]):
    mix.add("music", EVENTS["grow_kid"] + i * 0.15, S.music_box(n, 1.8, 0.34))
chords(168.4, 175.6, bar80, 0.32, ["Bb", "C"])
for n in CH["F"] + [65, 69]:
    mix.add("music", 175.2, S.piano(n, 2.6, 0.34))
melody(169.0, beat80, 0.48, 0, MAJOR)
mix.add("music", 177.0, S.pad(CH["Bb"], 5.0, 0.3, 1400, seed=177))

# ---- the device: every comparison a small falling tick, and a hum that grows as his reflection shrinks ----
for tm, v in COUNTS:
    if tm <= 0:
        continue
    mix.add("music", tm, S.music_box(81, 0.6, 0.22))
    mix.add("music", tm + 0.07, S.music_box(76.6, 0.8, 0.18))
for tm in EVENTS["weeks"]:
    mix.add("music", tm, S.piano(38, 1.4, 0.36))
    mix.add("music", tm + 0.18, S.piano(34, 1.6, 0.32))
    mix.add("sfx", tm, S.thud(0.25))
n = int(DURATION * SR)
tt = np.arange(n) / SR
hum = (np.sin(2 * np.pi * 98 * tt) * 0.5 + np.sin(2 * np.pi * 196.7 * tt) * 0.3 + np.sin(2 * np.pi * 294 * tt) * 0.15).astype(np.float32)
grid = np.arange(0, DURATION + 0.01, 0.05)
humming = {"S01", "S02", "G1", "R1"}
env = np.array([(1.0 - refl_at(g)) * 1.6 if scene_at(g)[0] in humming else 0.0 for g in grid])
env = np.interp(tt, grid, env).astype(np.float32)
mix.add("amb", 0, hum * env * env * 0.03)

# ---- the world ------------------------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
gym_beat(0.0, 6.0, 0.4)
gym_beat(29.0, 49.0, 0.36)
gym_beat(82.0, 100.0, 0.3)
gym_beat(159.0, 168.0, 0.32)
for t0, t1, rate in ((0.3, 6.0, 2.2), (29.0, 49.0, 2.4), (159.2, 160.2, 2.0)):  # the dumbbells, at the top of every curl
    period = 2 * np.pi / rate
    t = t0 + period / 2
    k = 0
    while t < t1:
        clank(t, 0.12, seed=k)
        t += period
        k += 1
for tm in EVENTS["posts"]:
    mix.add("sfx", tm - 0.05, S.whoosh(0.25, 0.12, up=True, seed=int(tm * 10)))
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.18, seed=int(t0 * 10)))
mix.add("amb", 23.0, S.street(6.0, 0.05, seed=4))
mix.add("amb", 49.0, S.street(7.0, 0.06, seed=5))
for k in range(30):  # cicadas in the heat
    mix.add("amb", 49.2 + k * 0.22, S.bp(S.rain(0.2, 0.5, seed=300 + k), 4000, 6000) * 0.4)
mix.add("amb", 56.0, S.street(7.0, 0.05, seed=6))
shutter(EVENTS["photo_flash"], 0.35)
mix.add("sfx", EVENTS["nikhil_post"], S.ringtone(0.5, 0.2))
mix.add("sfx", EVENTS["towel"], S.whoosh(0.6, 0.35, up=False, seed=75))
mix.add("sfx", EVENTS["towel"] + 0.55, S.thud(0.2))
s0, s1 = EVENTS["shots"]
for k in range(PHOTOS):
    shutter(s0 + k * (s1 - s0) / (PHOTOS - 1), 0.16)
mix.add("sfx", EVENTS["big_scroll"], S.whoosh(0.25, 0.12, up=True, seed=93))
mix.add("sfx", EVENTS["card_i"], S.scribble(0.4, 0.25, seed=3))
mix.add("sfx", EVENTS["lesson"], S.scribble(0.5, 0.2, seed=4))
# the pool
water(116.0, 14.0, 0.06)
for k in range(14):
    mix.add("sfx", 116.4 + k * 0.6, S.tap(0.08, seed=500 + k))
mix.add("sfx", EVENTS["hoodie"] - 0.3, S.whoosh(0.5, 0.3, up=True, seed=126))
mix.add("sfx", EVENTS["hoodie"] + 0.85, S.tap(0.2, seed=9))
splash(EVENTS["splash"], 0.6)
mix.add("amb", 129.4, S.lp(S.rain(9.0, 1.0, seed=40), 300) * 0.08)  # underwater rumble
for k in range(10):
    mix.add("sfx", 130.6 + k * 0.7, S.lp(S.tap(0.12, seed=700 + k), 900))
water(138.0, 14.0, 0.06, seed=21)
for k in range(9):
    splash(EVENTS["race"][0] + k * 0.5, 0.12, 0.4, seed=800 + k)
mix.add("sfx", EVENTS["touch"], S.thud(0.25))
for k in range(12):
    mix.add("sfx", EVENTS["laugh"] + k * 0.1, S.tap(0.12, seed=200 + k))
mix.add("sfx", 145.0, S.tap(0.3, seed=145))  # the high five
mix.add("sfx", EVENTS["mute"], S.tick(0.4))

t = 120.0
while t < EVENTS["silence"][1]:
    k = (t - 120.0) / (EVENTS["silence"][1] - 120.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.24 * k))
    t += 60 / (66 + 50 * k)
t = 70.0
while t < 75.0:
    k = (t - 70.0) / 5.0
    mix.add("heart", t, S.heartbeat(0.16 + 0.2 * k))
    t += 60 / (70 + 40 * k)

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

out = mix.render(-2.5, gain_db=float(sys.argv[1]) if len(sys.argv) > 1 else 4.8)
S.write_wav(B / "mix.wav", out)

rows = S.phone_levels(out, [(s[0], s[1], s[2]) for s in SCENES])
med = float(np.median([r[3] for r in rows]))
print("Phone-speaker loudness per scene (300 Hz high-pass, active parts):")
for name, t0, t1, db in rows:
    flag = "  <-- more than 6 dB quieter" if db < med - 6 else ""
    print(f"  {name:4s} {t0:6.1f}-{t1:6.1f}s  {db:6.1f} dBFS{flag}")
print(f"  median {med:.1f} dBFS")
json.dump({"phone_levels": rows, "median": med}, open(B / "levels.json", "w"), indent=1)
