"""LATER.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

One theme on piano and music box (G - D - Em - C). Every falling marble is a glass clink on its exact frame:
the clinks are the clock of the film. At the payoff the clink is gold and the theme comes in full.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, LEFT, BUBBLES  # noqa: E402

B = HERE / "build"
mix = S.Mix(DURATION)

CH = {"G": [43, 50, 55, 59], "D": [50, 54, 57], "Em": [52, 55, 59], "C": [48, 52, 55], "Am": [45, 52, 57],
      "Bm": [47, 50, 54]}
PROG = ["G", "D", "Em", "C"]
SAD = ["Em", "C", "G", "D"]
MELODY = [(0, 71), (1, 74), (2, 79), (3, 78), (4, 76), (6, 74), (7, 71), (8, 72), (10, 69), (12, 71)]


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
        elif style == "pulse":
            for k in range(4):
                for n in notes[:2]:
                    mix.add("music", t + k * bar / 4, S.piano(n - 12, bar / 5, vel * 0.7))
        elif style == "single":
            mix.add("music", t, S.piano(notes[0] + 12, bar, vel))
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
bar84 = 4 * 60 / 84

# 0-3 black card
mix.add("music", 0.4, S.music_box(79, 2.5, 0.45))
mix.add("music", 0.4, S.pad(CH["G"], 3.0, 0.3, 1200, seed=1))

# 3-15 the hook: a soft eighth-note piano pulse under the rings and the clinks
chords(3.0, 15.0, bar84, 0.26, PROG, "arp")
pads(3.0, 15.0, bar84, 0.14, 1300)

# 15-24 the sum: the theme, slow, on music box
pads(15.0, 24.0, bar70, 0.26, 1500, ["G", "Em"])
melody(15.8, beat70, 0.45, 0, MELODY[:7])

# 24-30.5 the villain is born: drone; 30.5-33.5 black card
mix.add("music", 24.8, S.pad([31, 43], 6.0, 0.7, 380, seed=7))
mix.add("music", 24.8, S.pad([55, 56], 6.0, 0.12, 900, seed=8))
mix.add("music", 30.8, S.piano(64, 2.8, 0.4))
mix.add("music", 30.8, S.pad(CH["Em"], 2.8, 0.7, 1500, seed=31))
melody(31.2, 0.6, 0.38, 0, [(0, 76), (1, 74), (2, 71)])

# 33.5-46 Dad: the same theme, sad and slow
chords(33.5, 46.0, bar70, 0.28, SAD, "single")
pads(33.5, 46.0, bar70, 0.24, 1100, SAD)
melody(36.0, beat70 * 1.2, 0.34, 0, MELODY[:5])

# 46-76 the grind: hollow arpeggio, years passing
chords(46.0, 76.0, bar84, 0.34, SAD, "arp")
pads(46.0, 76.0, bar84, 0.22, 1300, SAD)
mix.add("sfx", 53.0, S.lp(S.rng(42).normal(0, 1, int(3.5 * S.SR)).astype(np.float32), 900) * 0.04)  # party murmur
for k in range(7):
    mix.add("sfx", 53.0 + k * 0.5, S.lp(S.soft_kick(0.45), 900))

# 76-92 rock bottom: almost nothing, then the drone
mix.add("music", 76.2, S.pad(CH["Em"], 6.0, 0.35, 900, seed=40))
for i, n in enumerate([71, 69, 67, 64, 62]):
    mix.add("music", 82.6 + i * 1.6, S.piano(n, 2.8, 0.32))
mix.add("music", 83.4, S.pad([31, 43, 55], 9.0, 0.6, 420, seed=9))
mix.add("music", 83.4, S.pad([55, 56], 9.0, 0.1, 900, seed=19))

# 92-112 the turn: opening up; the memory gets the first full melody
pads(92.0, 112.0, bar70, 0.32, 1800, ["C", "G", "D", "Em"])
pads(92.0, 100.4, bar70, 0.4, 1500, ["Em", "C"])
for i, n in enumerate([64, 67, 71, 69, 67]):
    mix.add("music", 92.4 + i * 1.5, S.piano(n, 2.8, 0.4))
melody(100.4, beat70, 0.5)
chords(106.0, 112.0, bar70, 0.26, ["C", "D"])

# 112-130 the final fight: pulses, rising drone, then near-silence
chords(116.4, 128.2, bar84, 0.36, ["Em", "Em", "C", "D"], "pulse")
mix.add("music", 115.6, S.pad([31, 43, 50], 12.6, 0.55, 500, seed=10))
mix.add("music", 115.6, S.pad([55, 56], 12.6, 0.1, 900, seed=20))
mix.add("sfx", 125.2, S.whoosh(3.0, 0.25, up=True))

# 130 the slam
mix.add("sfx", EVENTS["slam"], S.hit(0.95))
mix.add("sfx", EVENTS["slam"], S.thud(0.8))
mix.add("sfx", EVENTS["burst"], S.shimmer(2.6, 0.38, 79))
mix.add("sfx", EVENTS["coat"], S.whoosh(0.4, 0.3, up=True, seed=61))

# 133-142 walking to Dad's: the theme quietly, then silence at the door
chords(133.0, 138.4, bar84, 0.26, PROG, "arp")
pads(133.0, 138.4, bar84, 0.2, 1700)

# 141-157 payoff: warm and full
chords(141.0, 157.0, bar70, 0.3, PROG)
pads(141.0, 157.0, bar70, 0.26, 2300)
melody(141.4, beat70, 0.55)
melody(150.6, beat70, 0.45, 0, MELODY[:6])

# 157-171 the gold marble, the mirror
pads(157.0, 171.0, bar70, 0.24, 2000, ["C", "G", "D", "G"])
melody(157.6, beat70 * 1.1, 0.42, 0, MELODY[:5])
chords(163.0, 171.0, bar70, 0.24, PROG, "arp")

# 171-180 title
chords(171.4, 178.0, bar70, 0.32, ["C", "D"])
for n in CH["G"] + [67, 71]:
    mix.add("music", 177.6, S.piano(n, 2.4, 0.34))
melody(172.0, beat70, 0.5)

# ---- sound effects -------------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
mix.add("amb", 13.0, S.lp(S.rng(43).normal(0, 1, int(2.0 * S.SR)).astype(np.float32), 1800) * 0.03)  # brunch
mix.add("amb", 133.0, S.street(4.0, 0.05))
mix.add("amb", 137.0, S.street(5.0, 0.03, seed=35))
mix.add("amb", 150.0, S.bp(S.rng(44).normal(0, 1, int(7.0 * S.SR)).astype(np.float32), 2000, 7000) * 0.025)  # sizzle

# every Sunday that falls: a clink (the long rolls in the grind are clinks too)
for i, (tm, v) in enumerate(LEFT[1:]):
    mix.add("sfx", tm + 0.35, S.clink(0.5 if i < 6 else 0.32, seed=i))
    mix.add("sfx", tm, S.tick(0.25))
mix.add("sfx", EVENTS["gold_drop"] + 1.2, S.clink(0.6, seed=99))
mix.add("sfx", EVENTS["gold_drop"] + 1.2, S.shimmer(2.4, 0.4, 83))
for tm in EVENTS["slip"]:
    mix.add("sfx", tm + 0.9, S.clink(0.45, seed=int(tm)))

# the rings: hook, the wound, Dad's end of the line, Maya's mum
for t0, t1 in [(EVENTS["ring1"], EVENTS["decline1"]), (9.2, 10.0), (11.2, 12.0), (13.2, 14.0),
               (EVENTS["ring6"], EVENTS["decline6"]), (46.4, 47.9), (EVENTS["maya_ring"], EVENTS["maya_answer"])]:
    mix.add("sfx", t0, S.ringtone(t1 - t0, 0.5))
    mix.add("sfx", t1, S.tap(0.4, int(t1 * 10)))
mix.add("sfx", EVENTS["dad_ring"], S.lp(S.ringtone(2.4, 0.35), 1800) * 0.8)  # heard down Dad's line
mix.add("sfx", EVENTS["plate_back"] + 1.3, S.tick(0.4))
mix.add("sfx", EVENTS["plate_out"] + 1.0, S.tick(0.4))
for tm in [40.6, 43.6, 60.4, 62.2, EVENTS["dad_text"]]:  # messages
    mix.add("sfx", tm, S.tick(0.35))
mix.add("sfx", EVENTS["dad_text"] - 0.1, S.buzz(0.5, 0.45))
for k in range(5):  # the clock in the silence before his text
    mix.add("sfx", 76.2 + k, S.tick(0.18))
mix.add("sfx", EVENTS["write"], S.scribble(1.4, 0.45, seed=3))
mix.add("sfx", EVENTS["email"], S.music_box(88, 0.5, 0.35))  # email ding
mix.add("sfx", EVENTS["brunch"], S.buzz(0.6, 0.5))
for tm, x in S.footsteps([133.0 + k * 0.3 for k in range(13)], 0.3):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["knock"], S.knock(0.7))
mix.add("sfx", EVENTS["door_open"], S.whoosh(0.6, 0.2, up=False, seed=62))
mix.add("sfx", EVENTS["dog_jump"], S.thud(0.25))
mix.add("sfx", 146.6, S.blow(0.8, 0.2))  # the hug, a breath
mix.add("sfx", EVENTS["marble_set"], S.clink(0.35, seed=77, bounces=1))
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.2, seed=int(t0 * 10)))

# heartbeat under the final fight
t = 118.0
while t < EVENTS["slam"]:
    k = (t - 118.0) / (EVENTS["slam"] - 118.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.22 * k))
    t += 60 / (66 + 60 * k)

# ---- the villain's whispers --------------------------------------------------------------------
speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    mix.add("voice", t0, x, 0.9)
    speech.append((t0, t0 + len(x) / S.SR))
mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart"))
mix.silence_window(138.4, 140.6, keep=("sfx",))  # the doorstep: only the knock

end = int((DURATION - 2.0) * S.SR)
for b in mix.buses.values():
    b[end:] *= np.linspace(1, 0, len(b) - end)

out = mix.render(-2.5, gain_db=float(sys.argv[1]) if len(sys.argv) > 1 else 4.6)
S.write_wav(B / "mix.wav", out)

rows = S.phone_levels(out, [(s[0], s[1], s[2]) for s in SCENES])
med = float(np.median([r[3] for r in rows]))
print("Phone-speaker loudness per scene (300 Hz high-pass, active parts):")
for name, t0, t1, db in rows:
    flag = "  <-- more than 6 dB quieter" if db < med - 6 else ""
    print(f"  {name:4s} {t0:6.1f}-{t1:6.1f}s  {db:6.1f} dBFS{flag}")
print(f"  median {med:.1f} dBFS")
json.dump({"phone_levels": rows, "median": med}, open(B / "levels.json", "w"), indent=1)
