"""FINE.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Am - F - C - E) on soft piano. Every "fine" is a bright two-note chime with the second note a little
flat: cheerful on top, hollow underneath. The mask snaps on with a small click. At the party a muffled party band
plays through the wall. When he tells the truth the cracks ring like glass with a rising shimmer, the pieces clink
on the step, and the theme resolves to C major.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BUBBLES, FINES, TRUES, RELABEL, G1_T0, G1_DAY  # noqa: E402

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
mix.add("music", 0.2, S.pad(CH["Am"], 5.4, 0.36, 1100, seed=1))
for i, n in enumerate([64, 62, 60]):
    mix.add("music", 0.5 + i * 0.8, S.piano(n, 2.0, 0.4))
chords(5.5, 19.0, bar92, 0.26, PROG, "arp")
pads(5.5, 19.0, bar92, 0.15, 1300)
mix.add("music", 19.2, S.pad(CH["Am"], 4.4, 0.32, 900, seed=3))
for i, n in enumerate([69, 67, 64, 60]):
    mix.add("music", 19.8 + i * 0.9, S.piano(n, 2.0, 0.32))
mix.add("music", 23.4, S.pad([33, 45], 5.8, 0.7, 380, seed=7))  # villain drone
mix.add("music", 23.4, S.pad([57, 58], 5.8, 0.12, 900, seed=8))
pads(29.0, 34.5, bar76, 0.28, 1500, ["F", "C"])
melody(29.4, beat76, 0.34, 0, MELODY[:4])
chords(34.5, 60.5, bar76, 0.3, PROG, "low")
pads(34.5, 60.5, bar76, 0.24, 1100, PROG)
for i, n in enumerate([72, 71, 69, 64]):
    mix.add("music", 50.8 + i * 1.3, S.piano(n, 2.2, 0.3))
pads(53.5, 60.5, bar76, 0.2, 800, ["Am", "Dm"])
mix.add("music", 60.6, S.pad([33, 45, 52], 8.4, 0.5, 500, seed=60))
for i, n in enumerate([64, 63, 62, 60]):
    mix.add("music", 61.0 + i * 1.8, S.piano(n, 2.2, 0.34))
party(69.0, 84.0, 900, 0.5)
mix.add("music", 69.4, S.pad(CH["F"], 8.0, 0.22, 1600, seed=69))
party(84.0, 94.0, 380, 0.4)
pads(84.0, 94.0, bar76, 0.28, 1000, ["Am", "F"])
mix.add("music", 94.0, S.pad([33, 45], 5.3, 0.6, 450, seed=94))  # villain drone
mix.add("music", 94.0, S.pad([57, 58], 5.3, 0.1, 900, seed=95))
mix.add("music", 100.8, S.pad(CH["Am"], 4.4, 0.4, 1200, seed=100))
mix.add("music", 105.0, S.pad(CH["C"], 4.4, 0.55, 2000, seed=105))
for i, n in enumerate([60, 64, 67, 72]):
    mix.add("music", 105.1 + i * 0.3, S.music_box(n, 2.0, 0.46))
pads(109.0, 118.0, bar76, 0.3, 1700, ["F", "C", "Dm", "E"])
chords(109.4, 118.0, bar76, 0.25, ["F", "C", "Dm", "E"], "arp")
melody(110.0, beat76, 0.38, 0, MELODY[:5])
pads(118.0, 124.0, bar76, 0.3, 2000, WARM)
chords(118.4, 124.0, bar76, 0.26, WARM, "arp")
pads(124.0, 130.2, bar76, 0.26, 900, ["Am", "E"])
mix.add("music", 127.4, S.pad([33, 45, 52], 2.0, 0.5, 500, seed=127))
mix.add("music", 130.2, S.pad(CH["F"], 4.8, 0.5, 1800, seed=130))
for i, n in enumerate([65, 69, 72]):
    mix.add("music", 130.4 + i * 0.25, S.music_box(n, 2.0, 0.42))
pads(135.0, 144.0, bar76, 0.3, 2400, WARM)
chords(135.0, 144.0, bar76, 0.3, WARM)
melody(135.4, beat76, 0.48, 0, MAJOR)
mix.add("music", 144.2, S.pad(CH["Am"], 6.4, 0.45, 1500, seed=144))
for i, n in enumerate([69, 64, 60]):
    mix.add("music", 144.4 + i * 1.2, S.music_box(n, 2.0, 0.4))
for i, n in enumerate([72, 76, 79, 84]):
    mix.add("music", EVENTS["viewer_crack"] + i * 0.12, S.music_box(n, 2.0, 0.42))
chords(150.5, 161.0, bar76, 0.26, WARM, "arp")
pads(150.5, 161.0, bar76, 0.2, 2000, WARM)
mix.add("music", EVENTS["shop_crack"], S.music_box(81, 2.0, 0.4))
chords(161.4, 168.6, bar76, 0.32, ["F", "G"])
for n in CH["C"] + [72, 76]:
    mix.add("music", 168.2, S.piano(n, 2.6, 0.34))
melody(162.0, beat76, 0.48, 0, MAJOR)
mix.add("music", 170.0, S.pad(CH["F"], 5.0, 0.3, 1400, seed=170))

# ---- the device ----------------------------------------------------------------------------------
for tm, v in FINES:
    if tm == 60.5:
        continue
    chime(tm)
click(EVENTS["mask_on"] + 0.42)
mix.add("sfx", EVENTS["mask_off"], S.whoosh(0.3, 0.25, up=False, seed=11))
for i in range(5):
    d0 = G1_T0 + i * G1_DAY
    mix.add("sfx", d0 + 0.2, S.whoosh(0.3, 0.22, up=False, seed=20 + i))
    click(d0 + 1.6, 0.26)
for k in range(10):  # tugging at a mask that won't move
    mix.add("sfx", EVENTS["pull"][0] + k * 0.42, S.thud(0.18))
    mix.add("sfx", EVENTS["pull"][0] + k * 0.42, S.tap(0.22, seed=300 + k))
for k in range(4):
    mix.add("sfx", EVENTS["his_pull"][0] + k * 0.4, S.thud(0.16))
mix.add("sfx", EVENTS["crack1"], S.clink(0.4, seed=1, bounces=1))
mix.add("sfx", EVENTS["crack1"], S.shimmer(1.6, 0.3, 84))
mix.add("sfx", EVENTS["crack2"], S.clink(0.45, seed=2, bounces=1))
mix.add("sfx", EVENTS["crack2"], S.shimmer(1.8, 0.34, 86))
mix.add("sfx", EVENTS["fall"], S.shimmer(2.6, 0.4, 78))
for k in range(3):
    mix.add("sfx", EVENTS["fall"] + 0.45 + k * 0.12, S.clink(0.4, seed=10 + k, bounces=3))
for i, n in enumerate([72, 76, 79]):
    mix.add("music", RELABEL + 0.6 + i * 0.12, S.music_box(n, 1.6, 0.36))
for tm, v in TRUES[1:2]:
    for i, n in enumerate([76, 79]):
        mix.add("music", tm + i * 0.12, S.music_box(n, 1.6, 0.36))
mix.add("sfx", EVENTS["drop"] + 0.5, S.clink(0.35, seed=40, bounces=2))
mix.add("sfx", EVENTS["viewer_crack"], S.shimmer(2.4, 0.38, 80))
mix.add("sfx", EVENTS["shop_crack"], S.clink(0.3, seed=50, bounces=1))

# ---- the world ------------------------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
mix.add("amb", 9.5, S.street(4.0, 0.05, seed=3))
mix.add("sfx", 5.6, S.music_box(88, 0.8, 0.25))  # the shop door bell
mix.add("sfx", 153.6, S.music_box(88, 0.8, 0.25))
mix.add("sfx", EVENTS["door"], S.knock(0.2, times=(0,)))
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.18, seed=int(t0 * 10)))
for tm in (EVENTS["jo_text"], EVENTS["jo_text2"], EVENTS["his_reply"]):
    mix.add("sfx", tm, S.tick(0.35))
for tm, x in S.footsteps([9.6 + k * 0.52 for k in range(8)], 0.2):
    mix.add("sfx", tm, x)
for tm in (13.8, 15.2, 16.6, 18.0, 47.0, 49.4, 136.0, 138.0):  # the ball
    mix.add("sfx", tm, S.thud(0.22))
for tm, x in S.footsteps([EVENTS["jo_off"] + k * 0.22 for k in range(10)], 0.18):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["jo_door"], S.whoosh(0.4, 0.2, up=True, seed=33))
for k in range(14):
    mix.add("sfx", EVENTS["masks_off"] + k * 0.1, S.tap(0.14, seed=500 + k))
for tm, x in S.footsteps([EVENTS["leave"] + k * 0.4 for k in range(5)], 0.2):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["back_door"], S.whoosh(0.4, 0.2, up=True, seed=34))
for tm, x in S.footsteps([EVENTS["back_door"] + 0.2 + k * 0.38 for k in range(4)], 0.18):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["card"], S.scribble(0.4, 0.25, seed=3))
mix.add("sfx", EVENTS["ring"], S.ringtone(0.8, 0.3))
for k in range(14):
    mix.add("sfx", EVENTS["laugh"] + k * 0.11, S.tap(0.12, seed=200 + k))
for tm, x in S.footsteps([EVENTS["walk_past"] + k * 0.36 for k in range(6)], 0.2):
    mix.add("sfx", tm, x)
mix.add("sfx", 152.6, S.whoosh(0.4, 0.2, up=True, seed=35))

t = 95.0
while t < EVENTS["silence"][1]:
    k = (t - 95.0) / (EVENTS["silence"][1] - 95.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.24 * k))
    t += 60 / (66 + 50 * k)
t = 128.0
while t < 130.2:
    mix.add("heart", t, S.heartbeat(0.26))
    t += 0.62

speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    mix.add("voice", t0, x, 0.9)
    speech.append((t0, t0 + len(x) / SR))
mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart"))
mix.silence_window(129.2, 130.2, keep=("voice", "heart"))

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
