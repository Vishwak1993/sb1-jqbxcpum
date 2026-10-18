"""ALL IN.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Am - F - C - E) on soft piano under a low match-crowd bed from the TV. A win is a bright run of coins and a
crowd roar; every LOST is a falling pair and a dull thud, and the crowd keeps cheering for somebody else. When he tells
Kabir the real number, the TV goes quiet, and the theme resolves to C major for the morning game.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BUBBLES, COUNTS, G1_T0, G1_NIGHT  # noqa: E402

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
chords(6.0, 18.0, bar92, 0.28, ["C", "G", "Am", "F"], "arp")
pads(6.0, 18.0, bar92, 0.16, 1600, ["C", "G", "Am", "F"])
pads(18.0, 25.0, bar76, 0.24, 900, ["Am", "E"])
mix.add("music", 25.2, S.pad([33, 45], 8.6, 0.7, 380, seed=7))  # villain drone
mix.add("music", 25.2, S.pad([57, 58], 8.6, 0.12, 900, seed=8))
pads(34.0, 40.0, bar76, 0.28, 1600, ["F", "C"])
melody(34.4, beat76, 0.34, 0, MELODY[:4])
chords(40.0, 72.0, bar76, 0.3, PROG, "low")
pads(40.0, 72.0, bar76, 0.24, 1100, PROG)
chords(58.0, 65.0, bar76, 0.26, ["Dm", "Am"], "arp")  # Sunday: a slow arpeggio so the quiet scene still plays on a phone
for i, n in enumerate([69, 67, 65, 64]):
    mix.add("music", 62.2 + i * 0.7, S.piano(n, 1.8, 0.3))
mix.add("music", 72.2, S.pad([33, 45, 52], 8.0, 0.5, 500, seed=72))
pads(80.0, 94.0, bar76, 0.28, 900, ["Am", "Dm"])
for i, n in enumerate([64, 63, 62, 60]):
    mix.add("music", 88.2 + i * 1.4, S.piano(n, 2.2, 0.34))
pads(94.0, 104.0, bar76, 0.32, 1600, ["Dm", "Am"])
chords(95.6, 104.0, bar76, 0.24, ["Dm", "Am"], "arp")
for i, n in enumerate([72, 76, 79]):  # the VIP jingle, too bright
    mix.add("music", EVENTS["vip"] + i * 0.12, S.music_box(n, 1.4, 0.4))
mix.add("music", EVENTS["account"] + 1.8, S.piano(45, 2.4, 0.42))
mix.add("music", EVENTS["account"] + 1.8, S.piano(44, 2.4, 0.3))
pads(104.0, 114.0, bar76, 0.3, 1700, ["F", "C", "Dm", "E"])
chords(104.4, 114.0, bar76, 0.25, ["F", "C", "Dm", "E"], "arp")
melody(105.0, beat76, 0.36, 0, MELODY[:5])
pads(114.0, 119.0, bar76, 0.26, 900, ["Am", "E"])
mix.add("music", 119.0, S.pad([33, 45, 52], 5.8, 0.55, 500, seed=119))
mix.add("music", 119.0, S.pad([57, 58], 5.8, 0.1, 900, seed=120))
mix.add("music", 126.4, S.pad(CH["Am"], 5.2, 0.36, 1200, seed=126))
mix.add("music", 131.8, S.pad(CH["F"], 3.0, 0.45, 1800, seed=131))
mix.add("music", EVENTS["crumble"], S.pad(CH["C"], 4.0, 0.55, 2000, seed=134))
for i, n in enumerate([60, 64, 67, 72]):
    mix.add("music", EVENTS["crumble"] + 0.1 + i * 0.3, S.music_box(n, 2.0, 0.46))
mix.add("sfx", EVENTS["crumble"], S.shimmer(2.6, 0.38, 78))
pads(138.0, 144.0, bar76, 0.3, 2000, WARM)
chords(138.4, 144.0, bar76, 0.26, WARM, "arp")
pads(144.0, 153.0, bar76, 0.3, 2400, WARM)
chords(144.0, 153.0, bar76, 0.3, WARM)
melody(144.4, beat76, 0.48, 0, MAJOR)
mix.add("music", 153.2, S.pad(CH["Am"], 6.8, 0.45, 1500, seed=153))
for i, n in enumerate([69, 64, 60]):
    mix.add("music", 153.4 + i * 1.2, S.music_box(n, 2.0, 0.4))
for i, n in enumerate([72, 76, 79]):
    mix.add("music", 157.0 + i * 0.12, S.music_box(n, 2.0, 0.4))
chords(160.0, 168.0, bar76, 0.26, WARM, "arp")
pads(160.0, 168.0, bar76, 0.2, 2000, WARM)
chords(168.4, 175.6, bar76, 0.32, ["F", "G"])
for n in CH["C"] + [72, 76]:
    mix.add("music", 175.2, S.piano(n, 2.6, 0.34))
melody(169.0, beat76, 0.48, 0, MAJOR)
mix.add("music", 177.0, S.pad(CH["F"], 5.0, 0.3, 1400, seed=177))


# ---- the match and the money ---------------------------------------------------------------------
def crowd(t0, dur, vel, cutoff=2400, seed=0):
    """A stadium crowd through a TV: band-passed noise that swells and falls."""
    n = int(dur * SR)
    x = S.rng(600 + seed).normal(0, 1, n).astype(np.float32)
    x = S.bp(x, 300, cutoff)
    sw = np.interp(np.arange(n), np.linspace(0, n, 9), 0.6 + 0.4 * S.rng(700 + seed).random(9)).astype(np.float32)
    f = int(0.4 * SR)
    x *= sw * vel
    x[:f] *= np.linspace(0, 1, f)
    x[-f:] *= np.linspace(1, 0, f)
    mix.add("amb", t0, x)


def roar(t, vel=0.5, seed=0):
    n = int(2.2 * SR)
    x = S.bp(S.rng(800 + seed).normal(0, 1, n).astype(np.float32), 350, 3000)
    e = S.env(n, 0.08, 0.9)
    mix.add("sfx", t, x * e * vel)


def coins(t, vel=0.3):
    for k in range(10):
        mix.add("sfx", t + k * 0.06, S.clink(vel * (1 - k * 0.06), seed=900 + k, bounces=1))


def lost(t):
    mix.add("music", t, S.piano(45, 1.4, 0.4))
    mix.add("music", t + 0.18, S.piano(41, 1.6, 0.36))
    mix.add("sfx", t, S.thud(0.4))


def bet(t):
    mix.add("sfx", t, S.tick(0.35))
    mix.add("music", t, S.music_box(81, 0.6, 0.3))


tv_on = [(0.0, 18.0), (18.0, 6.5), (40.0, 18.0), (88.0, 6.0), (114.0, 16.0)]
for i, (t0, d) in enumerate(tv_on):
    crowd(t0, d, 0.05, seed=i)
bet(EVENTS["bet0"])
bet(EVENTS["bet1"])
roar(EVENTS["six"], 0.45)
coins(EVENTS["won"])
mix.add("music", EVENTS["won"], S.music_box(84, 1.0, 0.4))
mix.add("music", EVENTS["won"] + 0.1, S.music_box(88, 1.2, 0.36))
roar(12.0, 0.3, seed=1)
lost(EVENTS["lost1"])
for i, tl in enumerate(EVENTS["g1_lost"]):
    bet(G1_T0 + i * G1_NIGHT + 1.2)
    lost(tl)
    roar(tl + 0.1, 0.2, seed=10 + i)  # the crowd cheers for somebody else
bet(EVENTS["allin"])
lost(EVENTS["lost_goa"])
roar(EVENTS["lost_goa"] + 0.1, 0.25, seed=20)
lost(EVENTS["lost_k"])
mix.add("sfx", EVENTS["delete_tap"], S.tick(0.4))

# ---- the world ------------------------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.18, seed=int(t0 * 10)))
for tm in (EVENTS["k_text"], EVENTS["his_text"], EVENTS["k_text2"], EVENTS["k_msg"], EVENTS["his_ask"], EVENTS["k_sent"], 58.6):
    mix.add("sfx", tm, S.tick(0.35))
mix.add("sfx", EVENTS["received"], S.music_box(86, 0.6, 0.3))
mix.add("sfx", EVENTS["knock"], S.knock(0.4))
mix.add("sfx", EVENTS["knock"] + 0.5, S.whoosh(0.4, 0.2, up=True, seed=33))
for tm, x in S.footsteps([EVENTS["kabir_in"] + k * 0.42 for k in range(3)], 0.2):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["card"], S.scribble(0.4, 0.25, seed=3))
mix.add("amb", 144.0, S.street(9.0, 0.03, seed=5))
mix.add("sfx", EVENTS["hit"], S.knock(0.5, times=(0,)))
mix.add("sfx", EVENTS["hit"], S.whoosh(0.5, 0.3, up=True, seed=44))
for k in range(12):
    mix.add("sfx", 147.2 + k * 0.1, S.tap(0.12, seed=200 + k))
mix.add("amb", 160.0, S.street(8.0, 0.03, seed=6))
coins(EVENTS["stranger_win"], 0.2)

t = 121.0
while t < EVENTS["silence"][1]:
    k = (t - 121.0) / (EVENTS["silence"][1] - 121.0)
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
