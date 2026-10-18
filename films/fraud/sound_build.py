"""FRAUD.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Dm - Bb - F - A) on soft piano, with an unresolved A major that keeps the music waiting, like him.
Every FRAUD flicker is the same sound: a short electrical crackle with a high dissonant pair on music box.
In the lift every badge crackles at once. After "me too." the A finally resolves to D major, and on PASSED
the theme plays in full.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BUBBLES, REVIEW  # noqa: E402

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


def crackle(t, vel=0.35, seed=0):
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

# ---- score ------------------------------------------------------------------------------------
melody(0.5, 0.42, 0.45, 12, [(0, 74), (1, 78), (2, 81), (4, 86)])  # the good news, bright
mix.add("music", 0.4, S.pad(CH["D"], 3.4, 0.36, 1600, seed=1))
mix.add("music", 3.6, S.pad(CH["D"], 1.4, 0.4, 1800, seed=2))
for i, n in enumerate([62, 66, 69, 74, 78]):  # the jump: a happy run that stops short
    mix.add("music", 3.9 + i * 0.09, S.music_box(n, 0.9, 0.5))
for n in CH["D"]:
    mix.add("music", 3.9, S.piano(n, 1.2, 0.42))
mix.add("music", 5.0, S.piano(49, 2.6, 0.45))  # the doubt: a C sharp left hanging
mix.add("music", 5.1, S.pad(CH["A"], 2.6, 0.4, 1100, seed=3))

pads(7.5, 14.0, bar92, 0.2, 1200, ["Dm", "A"])
mix.add("music", 10.2, S.pad([26, 38], 4.0, 0.7, 380, seed=7))  # villain drone
mix.add("music", 10.2, S.pad([50, 51], 4.0, 0.12, 900, seed=8))
chords(14.0, 30.0, bar92, 0.28, PROG, "arp")
pads(14.0, 30.0, bar92, 0.16, 1300)

chords(30.0, 64.0, bar76, 0.32, PROG, "low")
pads(30.0, 64.0, bar76, 0.24, 1100, PROG)
for i, n in enumerate([69, 67, 65, 64]):
    mix.add("music", 36.6 + i * 6.0, S.piano(n, 3.0, 0.26))
mix.add("music", 57.0, S.pad(CH["Gm"], 6.6, 0.55, 1100, seed=57))
for i, n in enumerate([65, 64, 62, 61]):
    mix.add("music", 57.4 + i * 1.4, S.piano(n, 2.4, 0.4))

pads(64.0, 74.0, bar76, 0.3, 900, ["Dm", "A"])
chords(64.2, 72.0, bar76, 0.36, ["Dm", "Gm", "Dm", "A"], "pulse")
for i, n in enumerate([62, 61, 60, 57]):
    mix.add("music", 64.6 + i * 1.8, S.piano(n, 2.2, 0.36))
mix.add("music", 68.6, S.pad([33, 45], 6.0, 0.4, 500, seed=9))  # the lift hum
mix.add("music", 74.4, S.pad([38, 50, 51], 4.4, 0.6, 420, seed=19))
pads(78.6, 96.0, bar76, 0.32, 1700, ["Bb", "F", "Gm", "A"])
melody(79.2, beat76, 0.42, 0, MELODY[:5])
chords(84.0, 96.0, bar76, 0.24, ["Bb", "F", "Gm", "A"], "arp")
melody(88.6, beat76, 0.42, 12, MELODY[:4])

chords(96.2, 110.0, bar92, 0.34, ["Dm", "Dm", "Bb", "A"], "pulse")
mix.add("music", 97.4, S.pad([26, 38, 45], 12.6, 0.55, 500, seed=10))
mix.add("music", 97.4, S.pad([50, 51], 12.6, 0.1, 900, seed=20))

mix.add("music", 111.6, S.pad(CH["D"], 4.6, 0.55, 2000, seed=40))  # "me too.": the A resolves at last
for i, n in enumerate([62, 66, 69, 74]):
    mix.add("music", 111.7 + i * 0.35, S.music_box(n, 2.0, 0.45))
mix.add("sfx", EVENTS["crumble"], S.shimmer(2.6, 0.38, 78))
pads(116.0, 122.0, bar76, 0.32, 2000, ["Bb", "D"])

pads(122.0, 140.0, bar76, 0.3, 2400, WARM)
chords(122.0, 140.0, bar76, 0.3, WARM)
melody(122.4, beat76, 0.5, 12)
melody(134.2, beat76, 0.42)

mix.add("music", 140.4, S.pad(CH["F"], 8.6, 0.5, 1600, seed=50))
for i, n in enumerate([69, 65, 62]):
    mix.add("music", 140.6 + i * 1.3, S.music_box(n, 2.0, 0.42))
mix.add("music", EVENTS["badge_fade"] + 0.4, S.music_box(74, 2.4, 0.45))
mix.add("music", EVENTS["badge_fade"] + 0.6, S.music_box(78, 2.4, 0.4))

chords(149.0, 158.0, bar76, 0.26, WARM, "arp")
chords(158.4, 165.6, bar76, 0.32, ["Bb", "C"])
for n in CH["D"] + [62, 66]:
    mix.add("music", 165.2, S.piano(n, 2.6, 0.34))
melody(159.0, beat76, 0.5)

# ---- sound effects -----------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
office_noise = S.bp(S.rng(41).normal(0, 1, int(DURATION * SR)).astype(np.float32), 300, 1500) * 0.02
mix.add("amb", 0, office_noise)
mix.add("sfx", EVENTS["email"], S.tick(0.4))
mix.add("sfx", EVENTS["email"] + 0.1, S.music_box(86, 0.6, 0.35))
mix.add("sfx", EVENTS["jump"] + 0.55, S.thud(0.35))

# every FRAUD flicker
for i, tm in enumerate([EVENTS["flicker"], 16.4, EVENTS["open_mouth"] + 0.3, 38.3, EVENTS["error"], 51.0, EVENTS["boss_badge"], 151.4]):
    crackle(tm, 0.32 if tm < 150 else 0.16, seed=i)
for k in range(5):  # the lift: every badge at once
    crackle(EVENTS["lift_flicker"] + 0.15 * k + 0.05, 0.3, seed=20 + k)
mix.add("sfx", EVENTS["lift_flicker"], S.buzz(0.8, 0.35))
mix.add("sfx", EVENTS["lift_back"], S.tick(0.3))
mix.add("sfx", 66.4, S.music_box(76, 0.8, 0.3))  # the lift's bell
mix.add("sfx", 66.6, S.whoosh(0.8, 0.2, up=False, seed=70))

for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.2, seed=int(t0 * 10)))
for tm in (14.8, 15.4):  # the handshake
    mix.add("sfx", tm, S.tap(0.25, seed=int(tm * 10)))
for k in range(18):  # typing late at night
    mix.add("sfx", 24.4 + k * 0.28 + 0.05 * (k % 3), S.tick(0.12))
for k in range(len("what is a pivot table")):
    mix.add("sfx", 33.6 + k * 0.055, S.tick(0.12))
mix.add("sfx", EVENTS["error"], S.hit(0.5))
for k in range(30):  # applause
    mix.add("sfx", EVENTS["applause"] + k * 0.07 + 0.03 * (k % 4), S.tap(0.14, seed=100 + k))
for k in range(len("I resign, effective immediately.")):
    mix.add("sfx", 59.8 + k * 0.056, S.tick(0.12))
for tm, x in S.footsteps([64.6 + k * 0.48 for k in range(8)], 0.26):
    mix.add("sfx", tm, x)
for tm, x in S.footsteps([134.2 + k * 0.6 for k in range(9)], 0.22):
    mix.add("sfx", tm, x)
for tm, x in S.footsteps([EVENTS["walk"] + k * 0.47 for k in range(9)], 0.22):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["envelope_down"], S.tap(0.35, seed=7))
mix.add("sfx", EVENTS["slide"], S.scribble(0.5, 0.25, seed=4))
mix.add("sfx", EVENTS["tear"], S.scribble(0.6, 0.4, seed=5))
mix.add("sfx", EVENTS["passed"], S.shimmer(2.4, 0.4, 81))
mix.add("music", EVENTS["passed"], S.music_box(86, 2.4, 0.45))
for k in range(16):  # laughter in the meeting: soft taps on the table
    mix.add("sfx", EVENTS["laugh"] + k * 0.11, S.tap(0.12, seed=200 + k))

t = 100.0
while t < EVENTS["silence"][1]:
    k = (t - 100.0) / (EVENTS["silence"][1] - 100.0)
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
