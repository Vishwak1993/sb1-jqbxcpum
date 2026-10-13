"""NO.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme is played on plucked strings: bouncy and eager in the hook, hollow in the grind, tired at rock
bottom, opening up at the turn, pulses in the fight. When the strings snap, each snap is the next note
of the melody.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, YES, BUBBLES  # noqa: E402

B = HERE / "build"
mix = S.Mix(DURATION)

CH = {"C": [48, 52, 55], "G": [43, 50, 55, 59], "Am": [45, 52, 57], "F": [41, 48, 53, 57], "Em": [52, 55, 59],
      "Dm": [50, 53, 57]}
HAPPY = ["C", "G", "Am", "F"]
HOLLOW = ["Am", "F", "C", "G"]
MELODY = [(0, 72), (1, 76), (2, 79), (3, 77), (4, 76), (6, 74), (7, 72), (8, 74), (10, 67), (12, 72)]  # (beat, note)
SNAP_NOTES = [72, 74, 76, 77, 79, 81, 83, 84, 86, 88]


def pluck_bars(t0, t1, bar, vel=0.4, prog=HAPPY, pattern="bounce", bus="music"):
    t, i = t0, 0
    while t < t1 - 0.05:
        notes = CH[prog[i % len(prog)]]
        if pattern == "bounce":  # root on the beat, chord on the off-beats
            for k in range(4):
                mix.add(bus, t + k * bar / 4, S.pluck(notes[0] - 12, bar / 3, vel * 0.9, seed=k))
                for n in notes[1:3]:
                    mix.add(bus, t + k * bar / 4 + bar / 8, S.pluck(n + 12, bar / 6, vel * 0.5, bright=1.4, seed=k + 5))
        elif pattern == "arp":
            for k in range(8):
                n = notes[k % len(notes)] + (12 if k >= 4 else 0)
                mix.add(bus, t + k * bar / 8, S.pluck(n, bar / 3, vel * 0.7, seed=k))
        elif pattern == "pulse":
            for k in range(4):
                for n in notes[:2]:
                    mix.add(bus, t + k * bar / 4, S.pluck(n - 12, bar / 5, vel * 0.8, bright=0.7, seed=k))
        t += bar
        i += 1


def chords(t0, t1, bar, vel=0.3, prog=HAPPY, bus="music"):
    t, i = t0, 0
    while t < t1 - 0.1:
        for n in CH[prog[i % len(prog)]]:
            mix.add(bus, t, S.piano(n, bar * 0.95, vel))
        t += bar
        i += 1


def pads(t0, t1, bar, vel=0.3, bright=1500, prog=HAPPY):
    t, i = t0, 0
    while t < t1 - 0.1:
        d = min(bar * 1.15, t1 - t + 0.4)
        mix.add("music", t, S.pad(CH[prog[i % len(prog)]], d, vel, bright, seed=i))
        t += bar
        i += 1


def melody(t0, beat, vel=0.5, octave=0, notes=MELODY, inst=S.music_box):
    for b, n in notes:
        mix.add("music", t0 + b * beat, inst(n + octave, beat * 2.2, vel))


bar120 = 2.0
bar90 = 4 * 60 / 90
bar72 = 4 * 60 / 72
beat72 = 60 / 72

# 0-3 black card: three eager plucks
for i, n in enumerate([72, 76, 79]):
    mix.add("music", 0.5 + i * 0.5, S.pluck(n, 1.2, 0.45, seed=i))

# 3-17.6 the hook: bouncy, eager, a little too cheerful
pluck_bars(3.0, 17.6, bar120, 0.42, HAPPY, "bounce")
pads(3.0, 17.6, bar120 * 2, 0.10, 1600, ["C", "Am"])
melody(3.0, 0.5, 0.32, 12, MELODY[:6], S.pluck)
melody(11.0, 0.5, 0.32, 12, MELODY[:6], S.pluck)

# 17.6-27 home: the music drains away; the villain drone arrives with its eyes
pads(17.6, 24.0, bar72, 0.22, 900, ["Am", "F"])
mix.add("music", 17.7, S.pluck(64, 2.4, 0.3))
mix.add("music", 19.6, S.pluck(60, 2.4, 0.26))
mix.add("music", 23.6, S.pad([33, 45], 7.5, 0.7, 380, seed=7))  # villain drone (low)
mix.add("music", 23.6, S.pad([57, 58], 7.5, 0.12, 900, seed=8))  # mid-range edge so phones hear it

# 31.6-34.6 black card
mix.add("music", 31.8, S.pluck(69, 2.6, 0.45))
mix.add("music", 31.9, S.pad(CH["Am"], 2.9, 0.75, 1500, seed=31))
melody(32.2, 0.55, 0.42, 0, [(0, 76), (1, 74), (2, 72)])

# 34.6-64 the grind: the same theme, hollow
pluck_bars(34.6, 64.0, bar90, 0.4, HOLLOW, "arp")
pads(34.6, 64.0, bar90, 0.24, 1400, HOLLOW)
mix.add("amb", 37.6, S.bp(S.rng(41).normal(0, 1, int(3.6 * S.SR)).astype(np.float32), 300, 1200) * 0.03)  # office hum
for k in range(9):
    mix.add("sfx", 37.8 + k * 0.33, S.tap(0.2, 80 + k))  # typing
for k in range(int((47.8 - 44.2) / 0.5)):  # the party's muffled beat
    mix.add("sfx", 44.2 + k * 0.5, S.lp(S.soft_kick(0.5), 900))

# 64-78 rock bottom: tired single notes, drone
for i, n in enumerate([69, 67, 64, 60, 57]):
    mix.add("music", 67.2 + i * 1.4, S.piano(n, 2.5, 0.3))
mix.add("music", 71.2, S.pad([33, 45, 57], 9.0, 0.6, 420, seed=9))
mix.add("music", 71.2, S.pad([57, 58], 9.0, 0.1, 900, seed=19))
for i, n in enumerate([57, 60, 64, 62]):
    mix.add("music", 78.4 + i * 1.2, S.piano(n, 2.6, 0.36))

# 78-97 the turn: opening up, the first full melody when the fists are revealed
pads(78.0, 97.0, bar72, 0.34, 1800, ["F", "C", "G", "Am"])
melody(84.0, beat72, 0.42, 0, MELODY[:5])
chords(90.0, 97.0, bar72, 0.26, ["F", "G"])
melody(90.2, beat72, 0.5)

# 97-114 the final fight: morning, then the chords become pulses, rising drone
mix.add("music", 97.2, S.pluck(72, 1.6, 0.3))
mix.add("music", 98.0, S.pluck(76, 1.6, 0.3))
pluck_bars(103.6, 112.2, bar90, 0.38, ["Am", "Am", "F", "G"], "pulse")
mix.add("music", 101.4, S.pad([33, 45, 52], 10.8, 0.55, 500, seed=10))
mix.add("music", 101.4, S.pad([57, 58], 10.8, 0.1, 900, seed=20))
mix.add("sfx", 109.2, S.whoosh(3.0, 0.25, up=True))

# 114 "no.": the hit, then every snapping string is the next note of the melody
mix.add("sfx", EVENTS["no"], S.hit(0.95))
mix.add("sfx", EVENTS["no"], S.whoosh(0.5, 0.6, up=False, seed=21))
for k, (tm, n) in enumerate(zip(EVENTS["snaps"], SNAP_NOTES)):
    mix.add("music", tm, S.pluck(n, 1.4, 0.55, bright=1.5, seed=k))
    mix.add("sfx", tm, S.tick(0.28))
mix.add("sfx", EVENTS["burst"], S.shimmer(3.0, 0.4, 79))
pads(116.6, 121.0, bar72 * 1.2, 0.6, 2200, ["F", "C"])
for i, n in enumerate([72, 76, 79, 84]):
    mix.add("music", 117.8 + i * 0.6, S.pluck(n, 1.6, 0.42, seed=i))

# 121-140 payoff: warm and full, the theme on piano with the plucks bouncing again (gently)
chords(121.0, 140.0, bar72, 0.28, HAPPY)
pads(121.0, 140.0, bar72, 0.22, 2200, HAPPY)
melody(122.0, beat72, 0.5)
melody(129.6, beat72, 0.42, 0, MELODY[:6], S.pluck)
pluck_bars(133.0, 140.0, bar72, 0.22, HAPPY, "bounce")

# 140-149.4 mirror: quiet bounce, then her string falls on one gold note
pluck_bars(140.0, 149.4, bar72, 0.24, HAPPY, "arp")
mix.add("music", EVENTS["ana_snap"], S.pluck(84, 1.6, 0.55, bright=1.5))
mix.add("sfx", EVENTS["ana_snap"], S.shimmer(1.8, 0.25, 84))

# 149.4-160 title: the theme, full, ending on C
chords(149.6, 157.6, bar72, 0.32, ["F", "G"])
for n in CH["C"] + [60, 64]:
    mix.add("music", 157.4, S.piano(n, 2.4, 0.34))
melody(150.0, beat72, 0.5)

# ---- sound effects on every visible action --------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
mix.add("amb", 41.2, S.rain(3.0, 0.12))
mix.add("amb", 58.2, S.rain(5.8, 0.12, seed=31))
mix.add("amb", 8.2, S.lp(S.rng(40).normal(0, 1, int(2.6 * S.SR)).astype(np.float32), 1800) * 0.03)  # café murmur
mix.add("amb", 13.4, S.street(2.2, 0.05))
mix.add("amb", 34.6, S.street(3.0, 0.05, seed=33))
mix.add("amb", 83.0, S.street(3.6, 0.03, seed=34))

# every yes: a tick as the counter pops, and a tiny pluck as the new string ties on
for tm, v in YES:
    mix.add("sfx", tm, S.tick(0.38))
    if v <= 10:
        mix.add("sfx", tm + 0.28, S.pluck(84 + (v % 5) * 2, 0.4, 0.2, bright=1.6, seed=v))
# the speech bubbles pop
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.22 if who != "him_big" else 0.5, seed=int(t0 * 10)))
for t0 in [3.0, 5.6, 8.2, 10.8, 13.4, 34.6, 37.6, 41.2, 44.2, 47.8, 51.2, 54.8, 58.2]:  # cuts
    mix.add("sfx", t0 - 0.1, S.whoosh(0.3, 0.14, seed=int(t0 * 3)))
for k, t0 in enumerate([15.6, 16.1, 16.6, 17.1]):  # flurry hits
    mix.add("sfx", t0, S.thud(0.25))
mix.add("sfx", EVENTS["yank"], S.whoosh(0.35, 0.5, up=False, seed=50))
mix.add("sfx", EVENTS["yank"], S.thud(0.4))
mix.add("sfx", EVENTS["phone_buzz"], S.buzz(0.8, 0.55))
mix.add("sfx", EVENTS["strike"], S.scribble(0.4, 0.5))
mix.add("sfx", EVENTS["strike"] + 0.45, S.scribble(0.35, 0.4, seed=1))
for i in range(6):  # messages stacking up
    mix.add("sfx", 51.3 + i * 0.42, S.buzz(0.25, 0.35))
for tm, x in S.footsteps([34.6 + k * 0.37 for k in range(8)], 0.25):
    mix.add("sfx", tm, x)
for tm, x in S.footsteps([58.4 + k * 0.6 for k in range(9)], 0.22):
    mix.add("sfx", tm, x)
for tm, x in S.footsteps([17.7 + k * 0.265 for k in range(11)], 0.25):
    mix.add("sfx", tm, x)
mix.add("sfx", 55.6, S.blow(1.0, 0.25))  # yawn
mix.add("sfx", EVENTS["trip"], S.whoosh(0.3, 0.4, up=False, seed=60))
mix.add("sfx", EVENTS["crash"], S.hit(0.6))
mix.add("sfx", EVENTS["crash"] + 0.1, S.thud(0.7))
mix.add("sfx", EVENTS["spill"], S.lp(S.rng(61).normal(0, 1, int(1.0 * S.SR)).astype(np.float32), 700) * 0.12)
mix.add("sfx", EVENTS["sunday_buzz"], S.buzz(0.6, 0.55))
mix.add("sfx", EVENTS["tug"], S.pluck(40, 1.2, 0.5, bright=0.6))  # the slack string: a loose, low twang
mix.add("sfx", EVENTS["tug"], S.pluck(52, 1.2, 0.3, bright=0.6))
mix.add("sfx", EVENTS["flinch"], S.whoosh(0.4, 0.35, up=False, seed=70))
mix.add("sfx", EVENTS["knock"], S.knock(0.7))
mix.add("sfx", EVENTS["work_buzz"], S.buzz(0.8, 0.5))
mix.add("sfx", EVENTS["knock2"], S.knock(0.55))
mix.add("sfx", 130.0, S.tap(0.3, 7))
mix.add("sfx", EVENTS["gold_me"], S.scribble(1.2, 0.4, seed=2))
mix.add("sfx", EVENTS["gold_me"] + 0.6, S.shimmer(2.0, 0.3, 79))
for tm, x in S.footsteps([129.6 + k * 0.3 for k in range(7)], 0.25):
    mix.add("sfx", tm, x)

# heartbeat under the final fight: slow to fast, the only thing left in the silence
t = 104.0
while t < EVENTS["no"]:
    k = (t - 104.0) / (EVENTS["no"] - 104.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.22 * k))
    t += 60 / (66 + 60 * k)

# ---- the villain's whispers -------------------------------------------------------------
speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    mix.add("voice", t0, x, 0.9)
    speech.append((t0, t0 + len(x) / S.SR))
mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart"))

end = int((DURATION - 2.0) * S.SR)  # gentle fade-out
for b in mix.buses.values():
    b[end:] *= np.linspace(1, 0, len(b) - end)

out = mix.render(-2.5, gain_db=float(sys.argv[1]) if len(sys.argv) > 1 else 4.0)
S.write_wav(B / "mix.wav", out)

rows = S.phone_levels(out, [(s[0], s[1], s[2]) for s in SCENES])
med = float(np.median([r[3] for r in rows]))
print("Phone-speaker loudness per scene (300 Hz high-pass, active parts):")
for name, t0, t1, db in rows:
    flag = "  <-- more than 6 dB quieter" if db < med - 6 else ""
    print(f"  {name:4s} {t0:6.1f}-{t1:6.1f}s  {db:6.1f} dBFS{flag}")
print(f"  median {med:.1f} dBFS")
json.dump({"phone_levels": rows, "median": med}, open(B / "levels.json", "w"), indent=1)
