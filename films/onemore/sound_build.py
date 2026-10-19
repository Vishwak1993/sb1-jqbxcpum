"""ONE MORE MATCH.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Am - F - C - E) on soft piano under the game's own noise: a bright victory sting, the matchmaking blip, a
flat defeat buzz. The rank-up chimes get hollower as the gloves go grey. When he logs off, the room goes quiet, and the
theme resolves to C major on the real pitch, with a whistle and a crowd of six.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BUBBLES, RANKS, G1_T0, G1_NIGHT  # noqa: E402

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
mix.add("music", 0.2, S.pad(CH["Am"], 6.0, 0.3, 1100, seed=1))
for i, n in enumerate([64, 62, 60]):
    mix.add("music", 0.5 + i * 0.8, S.piano(n, 2.0, 0.36))
chords(6.0, 19.0, bar92, 0.28, ["C", "G", "Am", "F"], "arp")
pads(6.0, 19.0, bar92, 0.16, 1600, ["C", "G", "Am", "F"])
mix.add("music", 19.2, S.pad([33, 45], 8.6, 0.7, 380, seed=7))  # villain drone
mix.add("music", 19.2, S.pad([57, 58], 8.6, 0.12, 900, seed=8))
pads(28.0, 34.0, bar76, 0.28, 1600, ["F", "C"])
melody(28.4, beat76, 0.34, 0, MELODY[:4])
chords(34.0, 68.0, bar76, 0.3, PROG, "low")
pads(34.0, 68.0, bar76, 0.24, 1100, PROG)
chords(54.0, 68.0, bar76, 0.26, ["Dm", "Am"], "arp")
mix.add("music", 68.2, S.pad([33, 45, 52], 8.0, 0.45, 500, seed=68))
pads(76.0, 84.0, bar76, 0.3, 900, ["Am", "Dm"])
for i, n in enumerate([64, 63, 62, 60]):
    mix.add("music", 79.0 + i * 1.2, S.piano(n, 2.2, 0.34))
pads(84.0, 94.0, bar76, 0.3, 1400, ["Dm", "Am"])
chords(85.0, 94.0, bar76, 0.22, ["Dm", "Am"], "arp")
pads(94.0, 104.0, bar76, 0.3, 1700, ["F", "C", "Dm", "E"])
chords(94.4, 104.0, bar76, 0.25, ["F", "C", "Dm", "E"], "arp")
melody(95.0, beat76, 0.36, 0, MELODY[:5])
pads(104.0, 110.0, bar76, 0.3, 2000, WARM)
chords(104.4, 110.0, bar76, 0.26, WARM, "arp")
pads(110.0, 112.4, bar76, 0.26, 900, ["Am", "E"])
mix.add("music", 112.4, S.pad([33, 45, 52], 7.4, 0.55, 500, seed=112))
mix.add("music", 112.4, S.pad([57, 58], 7.4, 0.1, 900, seed=113))
mix.add("music", EVENTS["logoff"], S.pad(CH["C"], 4.0, 0.5, 2000, seed=121))
for i, n in enumerate([60, 64, 67, 72]):
    mix.add("music", EVENTS["logoff"] + 0.1 + i * 0.3, S.music_box(n, 2.0, 0.46))
mix.add("sfx", EVENTS["crumble"], S.shimmer(2.6, 0.38, 78))
pads(124.0, 129.0, bar76, 0.28, 1800, ["F", "C"])
chords(124.2, 129.0, bar76, 0.3, ["F", "C"], "arp")
melody(124.4, beat76, 0.34, 0, MAJOR[:4])
pads(129.0, 140.0, bar76, 0.3, 2400, WARM)
chords(129.0, 140.0, bar76, 0.3, WARM)
melody(129.4, beat76, 0.48, 0, MAJOR)
mix.add("music", 140.2, S.pad(CH["Am"], 6.8, 0.45, 1500, seed=140))
for i, n in enumerate([69, 64, 60]):
    mix.add("music", 140.4 + i * 1.2, S.music_box(n, 2.0, 0.4))
for i, n in enumerate([72, 76, 79]):
    mix.add("music", 143.8 + i * 0.12, S.music_box(n, 2.0, 0.4))
chords(147.0, 156.0, bar76, 0.26, WARM, "arp")
pads(147.0, 156.0, bar76, 0.2, 2000, WARM)
chords(156.4, 163.6, bar76, 0.32, ["F", "G"])
for n in CH["C"] + [72, 76]:
    mix.add("music", 163.2, S.piano(n, 2.6, 0.34))
melody(157.0, beat76, 0.48, 0, MAJOR)


# ---- the game -------------------------------------------------------------------------------------
def victory(t, vel=0.4, hollow=0.0):
    for i, n in enumerate([72, 76, 79, 84]):
        mix.add("music", t + i * 0.07, S.music_box(n - (1 if hollow > 0.5 and i == 3 else 0), 1.0, vel * (1 - 0.4 * hollow)))
    mix.add("sfx", t, S.whoosh(0.4, 0.25, up=True, seed=int(t * 3)))


def defeat(t):
    n = int(0.9 * SR)
    tt = np.arange(n) / SR
    x = (np.sign(np.sin(2 * np.pi * 110 * tt)) * 0.3 + np.sin(2 * np.pi * 116 * tt) * 0.3).astype(np.float32)
    x = S.lp(x, 1800) * np.exp(-tt * 2.2).astype(np.float32) * 0.35
    mix.add("sfx", t, x)
    mix.add("music", t, S.piano(45, 1.4, 0.38))
    mix.add("music", t + 0.18, S.piano(41, 1.6, 0.34))


def blip(t, vel=0.3):
    mix.add("sfx", t, S.tick(vel))
    mix.add("music", t, S.music_box(88, 0.4, vel))


def clicks(t, n=6, vel=0.12):
    for k in range(n):
        mix.add("sfx", t + k * 0.13 + 0.03 * ((k * 7) % 3), S.tap(vel, seed=900 + int(t) + k))


victory(EVENTS["victory0"])
for c_ in EVENTS["clicks"]:
    blip(c_)
    victory(c_ + 0.6, 0.3)
for i in range(4):
    n0 = G1_T0 + i * G1_NIGHT
    clicks(n0 + 0.4, 10)
    victory(n0 + 2.6, 0.34, hollow=i / 3)
    if i >= 1:
        mix.add("sfx", n0 + 1.0, S.tick(0.25))  # Dev's text, ignored
for tm in (2.0, 20.0, 69.2, 110.4, 147.4):
    clicks(tm, 14)
victory(EVENTS["promo_win"], 0.45)
mix.add("sfx", EVENTS["promo_win"] + 0.4, S.shimmer(1.8, 0.34, 84))
for k in range(9):
    mix.add("sfx", EVENTS["missed"] + k * 0.1, S.tick(0.18))
mix.add("sfx", EVENTS["dev_lost"], S.tick(0.35))
mix.add("music", EVENTS["season"], S.music_box(81, 0.8, 0.35))
mix.add("sfx", EVENTS["crack"], S.clink(0.4, seed=1, bounces=1))
mix.add("sfx", EVENTS["crack"] + 0.6, S.clink(0.4, seed=2, bounces=1))
mix.add("sfx", EVENTS["reset"], S.thud(0.4))
mix.add("music", EVENTS["reset"], S.piano(36, 2.4, 0.42))
defeat(EVENTS["defeat"])
mix.add("sfx", EVENTS["logoff"], S.tick(0.45))
mix.add("sfx", EVENTS["logoff"] + 0.1, S.whoosh(0.5, 0.25, up=False, seed=31))
victory(EVENTS["x_victory"], 0.36)
mix.add("sfx", EVENTS["x_logoff"], S.tick(0.45))
mix.add("sfx", EVENTS["x_logoff"] + 0.1, S.whoosh(0.5, 0.25, up=False, seed=32))

# ---- the world ------------------------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.18, seed=int(t0 * 10)))
for tm in (EVENTS["dev_text"], EVENTS["his_text"], EVENTS["dev_text2"]):
    mix.add("sfx", tm, S.tick(0.35))
mix.add("sfx", EVENTS["knock"], S.knock(0.4))
mix.add("sfx", 61.4, S.whoosh(0.4, 0.2, up=True, seed=33))
mix.add("amb", 54.0, S.street(7.0, 0.04, seed=4))
mix.add("sfx", EVENTS["card"], S.scribble(0.4, 0.25, seed=3))
mix.add("sfx", EVENTS["alarm"], S.ringtone(0.8, 0.25))
for gx in (125.0, 125.4):
    mix.add("sfx", gx, S.thud(0.18))
mix.add("amb", 129.0, S.street(11.0, 0.04, seed=5))
mix.add("music", EVENTS["whistle"], S.music_box(96, 0.5, 0.3))
mix.add("sfx", EVENTS["shot"], S.knock(0.45, times=(0,)))
mix.add("sfx", EVENTS["catch"], S.thud(0.45))
for k in range(14):
    mix.add("sfx", 132.6 + k * 0.1, S.tap(0.12, seed=200 + k))
mix.add("sfx", 143.8, S.scribble(0.3, 0.22, seed=5))

t = 114.0
while t < EVENTS["silence"][1]:
    k = (t - 114.0) / (EVENTS["silence"][1] - 114.0)
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

end = int((DURATION - 2.0) * SR)
for b in mix.buses.values():
    b[end:] *= np.linspace(1, 0, len(b) - end)

out = mix.render(-2.5, gain_db=float(sys.argv[1]) if len(sys.argv) > 1 else 5.4)
S.write_wav(B / "mix.wav", out)

rows = S.phone_levels(out, [(s[0], s[1], s[2]) for s in SCENES])
med = float(np.median([r[3] for r in rows]))
print("Phone-speaker loudness per scene (300 Hz high-pass, active parts):")
for name, t0, t1, db in rows:
    flag = "  <-- more than 6 dB quieter" if db < med - 6 else ""
    print(f"  {name:4s} {t0:6.1f}-{t1:6.1f}s  {db:6.1f} dBFS{flag}")
print(f"  median {med:.1f} dBFS")
json.dump({"phone_levels": rows, "median": med}, open(B / "levels.json", "w"), indent=1)
