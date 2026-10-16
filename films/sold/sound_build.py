"""SOLD.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Am - F - C - G) on soft piano. Every purchase is the same little sting: a tap, a bright rising music-box
run (the feeling) and a coin clinking out of the jar on a falling note. The run never resolves; it is cut off by a
low thud when the box lands. In the payoff the coins come back on rising notes and the run finally resolves.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BUYS, RETURNS, BUBBLES  # noqa: E402

B = HERE / "build"
mix = S.Mix(DURATION)

CH = {"Am": [45, 52, 57, 60], "F": [41, 48, 53, 57], "C": [48, 52, 55, 60], "G": [43, 50, 55, 59], "Dm": [50, 53, 57],
      "E": [40, 47, 52, 56]}
PROG = ["Am", "F", "C", "G"]
WARM = ["F", "C", "G", "Am"]
MELODY = [(0, 69), (1, 72), (2, 76), (3, 74), (4, 72), (6, 71), (7, 69), (8, 71), (10, 64), (12, 69)]
RUN = [72, 76, 79, 83]      # the feeling: up, never resolving
RESOLVE = [72, 76, 79, 84]  # the payoff: up, home
UP = [64, 67, 69, 72, 74, 76, 79, 81, 84]


def chords(t0, t1, bar, vel=0.3, prog=PROG, style="block"):
    t, i = t0, 0
    while t < t1 - 0.1:
        notes = CH[prog[i % len(prog)]]
        if style == "block":
            for n in notes[:3]:
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


def sting(t, vel=0.42, notes=RUN, gap=0.07):
    """The feeling: a quick bright run."""
    for i, n in enumerate(notes):
        mix.add("music", t + i * gap, S.music_box(n, 0.9, vel * (0.8 + 0.1 * i)))


bar76 = 4 * 60 / 76
beat76 = 60 / 76
bar92 = 4 * 60 / 92

# ---- score ------------------------------------------------------------------------------------
mix.add("music", 0.3, S.pad(CH["Am"], 4.0, 0.34, 1100, seed=1))
mix.add("music", 0.5, S.piano(57, 3.0, 0.46))
mix.add("music", 1.6, S.piano(60, 2.4, 0.4))
mix.add("music", 2.6, S.piano(64, 2.0, 0.4))
mix.add("music", 0.5, S.music_box(69, 2.4, 0.36))

chords(7.0, 17.0, bar92, 0.28, PROG, "arp")
pads(4.0, 17.0, bar92, 0.16, 1300)

mix.add("music", 17.2, S.pad(CH["Am"], 3.0, 0.3, 900, seed=4))
mix.add("music", 19.2, S.pad([33, 45], 6.0, 0.7, 380, seed=7))  # villain drone
mix.add("music", 19.2, S.pad([57, 58], 6.0, 0.12, 900, seed=8))

pads(25.0, 33.0, bar76, 0.28, 1500, ["F", "C"])
melody(25.6, beat76, 0.4, 0, MELODY[:5])  # the sea: the theme, small and far away
mix.add("music", 30.0, S.piano(52, 2.0, 0.34))

chords(33.0, 58.0, bar76, 0.32, PROG, "low")
pads(33.0, 58.0, bar76, 0.24, 1100, PROG)
for i, n in enumerate([69, 67, 64, 60]):
    mix.add("music", 37.6 + i * 5.0, S.piano(n, 3.0, 0.24))
mix.add("music", 54.8, S.pad(CH["Dm"], 3.4, 0.6, 1100, seed=55))
for i, n in enumerate([64, 60, 57]):
    mix.add("music", 55.2 + i * 0.9, S.piano(n, 2.4, 0.4))

pads(58.0, 68.0, bar76, 0.28, 900, ["Am", "E"])
mix.add("music", 63.4, S.pad([33, 45, 57], 5.0, 0.55, 420, seed=9))
pads(68.0, 74.0, bar76, 0.3, 1200, ["F", "Am"])
for i, n in enumerate([64, 62, 60, 57]):
    mix.add("music", 68.6 + i * 1.3, S.piano(n, 2.6, 0.34))

pads(74.0, 94.0, bar76, 0.32, 1700, ["F", "C", "G", "Am"])
chords(74.2, 84.0, bar76, 0.32, ["F", "C", "G", "Am"], "arp")
melody(77.2, beat76, 0.42, 0, MELODY[:6])
chords(84.0, 94.0, bar76, 0.24, ["F", "G"])
melody(84.6, beat76, 0.36, 12, MELODY[:4])

pads(94.0, 112.0, bar76, 0.28, 2000, WARM)
chords(104.0, 112.0, bar76, 0.26, WARM, "arp")

chords(112.4, 124.0, bar92, 0.36, ["Am", "Am", "F", "E"], "pulse")
mix.add("music", 113.8, S.pad([33, 45, 52], 11.0, 0.55, 500, seed=10))
mix.add("music", 113.8, S.pad([57, 58], 11.0, 0.1, 900, seed=20))
mix.add("sfx", 121.8, S.whoosh(2.4, 0.25, up=True))

mix.add("music", EVENTS["zero"], S.piano(33, 3.0, 0.5))
mix.add("sfx", 128.0, S.shimmer(2.6, 0.38, 76))
pads(128.0, 133.0, bar76, 0.4, 1800, ["F", "C"])

pads(133.0, 150.0, bar76, 0.32, 2400, WARM)
chords(133.4, 150.0, bar76, 0.3, WARM)
melody(141.2, beat76, 0.55, 12)
sting(EVENTS["gold"], 0.55, RESOLVE, 0.1)

mix.add("music", 150.4, S.pad(CH["F"], 8.0, 0.5, 1600, seed=50))
for i, n in enumerate([69, 72, 76]):
    mix.add("music", 150.6 + i * 1.2, S.music_box(n, 2.0, 0.42))
mix.add("music", EVENTS["cart_tomorrow"] + 0.2, S.music_box(81, 2.4, 0.45))

chords(158.0, 165.0, bar76, 0.24, WARM, "arp")
mix.add("music", EVENTS["face_down"] + 0.4, S.music_box(84, 2.0, 0.45))

chords(165.4, 172.6, bar76, 0.32, ["F", "G"])
for n in CH["Am"] + [64, 69]:
    mix.add("music", 172.2, S.piano(n, 2.6, 0.34))
melody(166.0, beat76, 0.5)

# ---- sound effects -----------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
mix.add("amb", 33.0, S.lp(S.rng(41).normal(0, 1, int(5.0 * S.SR)).astype(np.float32), 500) * 0.12)  # the bus
mix.add("amb", 104.0, S.street(2.6, 0.05, seed=33))
mix.add("amb", 109.2, S.bp(S.rng(42).normal(0, 1, int(2.8 * S.SR)).astype(np.float32), 1500, 6000) * 0.03)  # the pan
waves = S.lp(S.rng(43).normal(0, 1, int(9.0 * S.SR)).astype(np.float32), 900)
env = 0.5 + 0.5 * np.sin(np.linspace(0, 9.0 * 2 * np.pi / 4.5, len(waves)))
mix.add("amb", 141.0, waves * env.astype(np.float32) * 0.09)  # the sea

# every purchase: a tap, the feeling, a coin out of the jar, the box landing
for i, (tm, sticker, price) in enumerate(BUYS):
    hook = tm < 20
    mix.add("sfx", tm - 0.02, S.tick(0.4))
    if tm in (5.4, 36.4, 41.4, 46.0):
        sting(tm + 0.05, 0.4)
    mix.add("sfx", tm - 0.35, S.clink(0.32, seed=i, bounces=1))
    mix.add("music", tm - 0.3, S.music_box(UP[-1 - (i % 4)] - 12, 0.6, 0.24))
    if tm != 5.4 and tm != 36.4:
        mix.add("sfx", tm, S.thud(0.45 + 0.02 * i))
        mix.add("sfx", tm, S.knock(0.3, times=(0,)))
mix.add("sfx", EVENTS["doorbell"], S.music_box(76, 1.0, 0.4))
mix.add("sfx", EVENTS["doorbell"] + 0.3, S.music_box(72, 1.2, 0.4))
mix.add("sfx", EVENTS["open"], S.scribble(0.4, 0.3, seed=3))
sting(EVENTS["open"], 0.45)
mix.add("music", EVENTS["open"] + 1.6, S.piano(52, 1.6, 0.3))
mix.add("sfx", EVENTS["coin"], S.clink(0.4, seed=30, bounces=2))
mix.add("sfx", EVENTS["bro_text"], S.tick(0.35))
for tm in (33.4,):
    mix.add("sfx", tm, S.tick(0.35))

# the tower falls
mix.add("sfx", EVENTS["pull"], S.scribble(0.3, 0.3, seed=5))
mix.add("sfx", EVENTS["collapse"], S.whoosh(0.7, 0.5, up=False, seed=62))
for k in range(8):
    mix.add("sfx", EVENTS["collapse"] + 0.25 + k * 0.09 + 0.03 * (k % 3), S.thud(0.7 - k * 0.05))
    mix.add("sfx", EVENTS["collapse"] + 0.25 + k * 0.09, S.knock(0.3, times=(0,)))
mix.add("sfx", EVENTS["sale_buzz"], S.buzz(0.7, 0.45))

# the turn: each sticker a soft tap; the graph's spikes are the feeling, the drops a low note
for tm, _ in [(74.6, 0), (75.3, 0), (76.0, 0), (76.7, 0), (77.4, 0), (78.1, 0)]:
    mix.add("sfx", tm + 1.6, S.tap(0.3, seed=int(tm * 10)))
for n in range(4):
    t0 = 84.4 + 5.6 * (n * 340 + 60) / 1720
    sting(t0 + 0.25, 0.34 - 0.05 * n)
    mix.add("music", t0 + 0.75, S.piano(40 - n, 1.6, 0.36))

# returns: a stamp, a slide, a coin back in on a rising note
for k, (tm, i) in enumerate(RETURNS):
    mix.add("sfx", tm - 0.55, S.knock(0.35, times=(0,)))
    mix.add("sfx", tm - 0.2, S.whoosh(0.4, 0.2, up=True, seed=70 + k))
    mix.add("sfx", tm + 0.45, S.clink(0.35, seed=40 + k, bounces=1))
    mix.add("music", tm + 0.45, S.music_box(UP[min(k, len(UP) - 1)], 1.0, 0.34))

for tm, x in S.footsteps([104.2 + k * 0.33 for k in range(7)], 0.26):
    mix.add("sfx", tm, x)
for tm, x in S.footsteps([58.2 + k * 0.45 for k in range(5)], 0.26):
    mix.add("sfx", tm, x)
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.2, seed=int(t0 * 10)))

# the final fight: the flash sale, the countdown, nothing
mix.add("sfx", EVENTS["flash"], S.buzz(0.6, 0.5))
for k in range(14):
    tm = 113.0 + k
    if tm < EVENTS["zero"]:
        mix.add("sfx", tm, S.tick(0.22 + 0.02 * k))
mix.add("sfx", EVENTS["set_down"], S.tap(0.4, seed=5))
t = 116.0
while t < EVENTS["zero"]:
    k = (t - 116.0) / (EVENTS["zero"] - 116.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.24 * k))
    t += 60 / (66 + 60 * k)
mix.add("sfx", EVENTS["zero"], S.hit(0.6))
mix.add("sfx", EVENTS["new_sale"], S.buzz(0.4, 0.3))
mix.add("sfx", EVENTS["new_sale"] + 0.1, S.music_box(79, 0.6, 0.3))

# payoff: coins dropping in
for k in range(10):
    tm = 133.6 + k * 0.5 + 0.4
    mix.add("sfx", tm, S.clink(0.32, seed=80 + k, bounces=1))
    mix.add("music", tm, S.music_box(UP[min(k, len(UP) - 1)], 0.9, 0.3))
mix.add("sfx", EVENTS["postcard"], S.scribble(0.3, 0.25, seed=9))
mix.add("sfx", EVENTS["face_down"], S.tap(0.35, seed=6))

speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    mix.add("voice", t0, x, 0.9)
    speech.append((t0, t0 + len(x) / S.SR))
mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart", "sfx"))

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
