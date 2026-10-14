"""1%.: score, sound effects, the villain's whispers and the mix. Reads the same timeline as the picture.

The theme (Am - F - C - G) starts fast and driving in the hook, wears thin in the grind (tempo and notes drop
away as the battery drains), stops at 1%, comes back slow when he sleeps, and full at the payoff.
Every battery drop is a small falling two-note "power down" chime; every gain is the rising one.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, BAT, BUBBLES  # noqa: E402

B = HERE / "build"
mix = S.Mix(DURATION)

CH = {"Am": [45, 52, 57], "F": [41, 48, 53, 57], "C": [48, 52, 55], "G": [43, 50, 55, 59], "Em": [52, 55, 59], "D": [50, 54, 57]}
PROG = ["Am", "F", "C", "G"]
WARM = ["F", "C", "G", "Am"]
MELODY = [(0, 69), (1, 72), (2, 76), (3, 74), (4, 72), (6, 71), (7, 69), (8, 71), (10, 67), (12, 69)]


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
        elif style == "drive":
            for k in range(8):
                mix.add("music", t + k * bar / 8, S.pluck(notes[0] - 12 if k % 2 == 0 else notes[1], bar / 6, vel * 0.8, seed=k))
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


bar120 = 2.0
bar96 = 4 * 60 / 96
bar70 = 4 * 60 / 70
beat70 = 60 / 70

# 0-3 black card
mix.add("music", 0.4, S.pad(CH["Am"], 3.0, 0.35, 1200, seed=1))
mix.add("music", 0.6, S.piano(69, 2.4, 0.4))

# 3-17 the hook: driving, busy
chords(3.0, 17.0, bar120, 0.4, PROG, "drive")
pads(3.0, 17.0, bar120, 0.14, 1500)
melody(3.0, 0.5, 0.3, 12, MELODY[:6], S.pluck)
melody(9.0, 0.5, 0.3, 12, MELODY[:6], S.pluck)
mix.add("music", 14.6, S.pad([33, 45], 2.6, 0.6, 380, seed=7))  # villain drone
mix.add("music", 14.6, S.pad([57, 58], 2.6, 0.12, 900, seed=8))

# 17-27 the phone charges: one warm rising arpeggio for the phone, nothing for him
pads(17.0, 24.0, bar70, 0.26, 1400, ["Am", "F"])
for i, n in enumerate([60, 64, 67, 72, 76]):
    mix.add("music", EVENTS["plug"] + 0.3 + i * 0.45, S.music_box(n, 1.4, 0.4))
mix.add("music", 24.2, S.piano(69, 2.8, 0.42))
mix.add("music", 24.2, S.pad(CH["Am"], 2.8, 0.7, 1500, seed=31))

# 27-36 Theo: the theme, bright and small
chords(27.0, 36.0, bar70, 0.24, WARM, "arp")
melody(28.4, beat70 * 0.9, 0.42, 12, MELODY[:6])

# 36-61 the grind: the drive again, slowing and thinning each week
t = 36.0
for wk, (t0, t1, vel, style) in enumerate([(36.0, 46.5, 0.36, "drive"), (46.5, 53.5, 0.32, "arp"), (53.5, 61.0, 0.3, "single")]):
    chords(t0, t1, bar96 if wk == 0 else bar70, vel, PROG, style)
    pads(t0, t1, bar70, 0.2 - 0.03 * wk, 1300 - 250 * wk)

# 61-76 rock bottom: the music stops at 1%; only low beeps, then a cold pad
mix.add("music", 68.0, S.pad(CH["Am"], 8.0, 0.32, 800, seed=40))
for i, n in enumerate([69, 67, 64, 60, 57]):
    mix.add("music", 70.4 + i * 1.2, S.piano(n, 2.6, 0.3))

# 76-99 the turn: opening up; slow theme while he sleeps
pads(76.0, 93.0, bar70, 0.3, 1600, ["F", "C", "G", "Am"])
pads(76.0, 84.0, bar70, 0.4, 1400, ["Am", "F"])
for i, n in enumerate([64, 67, 69, 72, 71]):
    mix.add("music", 76.6 + i * 1.5, S.piano(n, 2.8, 0.42))
melody(84.6, beat70, 0.45)
chords(88.0, 93.0, bar70, 0.24, ["F", "G"])
pads(93.0, 99.0, bar70 * 1.5, 0.28, 1200, ["Am", "F"])
melody(93.4, beat70 * 1.6, 0.35, 0, MELODY[:6])

# 99-108 charging: the theme in major and lighter
chords(99.0, 108.0, bar96, 0.3, WARM, "arp")
pads(99.0, 108.0, bar96, 0.2, 2000, WARM)

# 108-124 the final fight: the drive returns, harder, then the pulse and near-silence
chords(108.4, 116.0, bar120, 0.4, PROG, "drive")
chords(116.0, 122.4, bar96, 0.36, ["Am", "Am", "F", "G"], "pulse")
mix.add("music", 109.4, S.pad([33, 45, 52], 13.0, 0.55, 500, seed=10))
mix.add("music", 109.4, S.pad([57, 58], 13.0, 0.1, 900, seed=20))
mix.add("sfx", 119.6, S.whoosh(2.8, 0.25, up=True))

# 124 shut, click: dark
mix.add("sfx", EVENTS["shut"], S.thud(0.8))
mix.add("sfx", EVENTS["shut"], S.hit(0.75))
mix.add("sfx", EVENTS["lamp_off"], S.tick(0.7))
mix.add("sfx", EVENTS["lamp_off"] + 0.1, S.whoosh(1.6, 0.25, up=False, seed=63))

# 127-138 the viewer's turn: just a pad that breathes with the ring
b0, b1 = EVENTS["breath"]
mix.add("music", 127.4, S.pad(CH["F"], 11.0, 0.55, 1600, seed=50))
for i, n in enumerate([72, 69, 67]):
    mix.add("music", 127.6 + i * 1.0, S.music_box(n, 2.0, 0.42))
k = b0
while k < b1:
    mix.add("music", k, S.pad(CH["C"], 2.8, 0.42, 1900, seed=int(k)))
    mix.add("music", k, S.music_box(76, 2.4, 0.3))
    mix.add("sfx", k + 1.4, S.blow(1.3, 0.12))
    k += 2.8

# 138-163 payoff and mirror: warm, full
pads(138.0, 145.0, bar70, 0.32, 2400, WARM)
melody(138.6, beat70, 0.5)
chords(145.0, 154.0, bar70, 0.32, WARM)
pads(145.0, 154.0, bar70, 0.24, 2400, WARM)
melody(146.0, beat70, 0.55)
chords(154.0, 163.0, bar70, 0.22, WARM, "arp")
melody(156.6, beat70 * 1.2, 0.38, 0, MELODY[:5])

# 163-172.5 title, then the stinger
chords(163.4, 171.0, bar70, 0.32, ["F", "G"])
for n in CH["Am"] + [64, 69]:
    mix.add("music", 170.6, S.piano(n, 2.0, 0.34))
melody(164.0, beat70, 0.5)

# ---- sound effects ------------------------------------------------------------------------
mix.add("amb", 0, S.room_tone(DURATION, 0.03))
mix.add("amb", 8.6, S.lp(S.rng(41).normal(0, 1, int(2.6 * S.SR)).astype(np.float32), 1600) * 0.03)  # meeting murmur
mix.add("amb", 39.5, S.lp(S.rng(42).normal(0, 1, int(3.5 * S.SR)).astype(np.float32), 500) * 0.06)  # train rumble
mix.add("amb", 99.0, S.street(3.0, 0.04))
mix.add("amb", 102.0, S.bp(S.rng(43).normal(0, 1, int(3.0 * S.SR)).astype(np.float32), 250, 2500) * 0.03)  # café
mix.add("amb", 145.0, S.bp(S.rng(44).normal(0, 1, int(9.0 * S.SR)).astype(np.float32), 300, 2000) * 0.03)  # audience

# the battery: a falling two-note chime on every drop, a rising one on every gain
prev = None
for tm, v, mode in BAT:
    if prev is not None and mode == "step" and v != prev:
        notes = (79, 74) if v < prev else (74, 79)
        for i, n in enumerate(notes):
            mix.add("sfx", tm + i * 0.09, S.music_box(n + (0 if v > 20 else -5), 0.35, 0.3))
    prev = v
for tm in EVENTS["low_beep"]:
    for i in range(2):
        mix.add("sfx", tm + i * 0.16, S.music_box(62, 0.15, 0.4))

for tm in (EVENTS["alarm1"], EVENTS["alarm2"], EVENTS["alarm3"]):
    mix.add("sfx", tm, S.ringtone(1.4, 0.45))
mix.add("sfx", EVENTS["spring"], S.whoosh(0.4, 0.3, up=True, seed=51))
for k in range(int((13.8 - 6.0) / 0.12)):  # typing in the hook
    if not (8.6 <= 6.0 + k * 0.12 < 11.2):
        mix.add("sfx", 6.0 + k * 0.12, S.tap(0.16, k))
for k in range(int((61.0 - 57.0) / 0.13)):
    mix.add("sfx", 57.0 + k * 0.13, S.tap(0.14, 100 + k))
for k in range(int((122.4 - 108.4) / 0.14)):
    mix.add("sfx", 108.4 + k * 0.14, S.tap(0.15, 200 + k))
mix.add("sfx", EVENTS["plug"], S.tick(0.5))
mix.add("sfx", EVENTS["door_knock"], S.knock(0.6))
for tm in (46.8, 47.8, EVENTS["theo_text1"], EVENTS["theo_text2"], 57.6, 59.0):
    mix.add("sfx", tm, S.tick(0.35))
mix.add("sfx", EVENTS["spill"], S.thud(0.35))
mix.add("sfx", EVENTS["spill"] + 0.1, S.lp(S.rng(64).normal(0, 1, int(0.8 * S.SR)).astype(np.float32), 900) * 0.1)
mix.add("sfx", EVENTS["lowbat_popup"], S.buzz(0.4, 0.4))
for i in range(5):
    mix.add("sfx", EVENTS["email_flood"][0] + i * 0.7, S.music_box(88, 0.4, 0.3))
mix.add("sfx", 52.2, S.thud(0.2))
for tm, x in S.footsteps([99.0 + k * 0.36 for k in range(8)], 0.24):
    mix.add("sfx", tm, x)
for tm, x in S.footsteps([155.4 + k * 0.4 for k in range(5)], 0.2):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["theo_lamp"], S.tick(0.5))
mix.add("sfx", EVENTS["wave"], S.shimmer(2.0, 0.3, 84))
for t0, t1, who, text in BUBBLES:
    mix.add("sfx", t0, S.tap(0.2, seed=int(t0 * 10)))

# heartbeat under the final fight
t = 112.0
while t < EVENTS["shut"]:
    k = (t - 112.0) / (EVENTS["shut"] - 112.0)
    mix.add("heart", t, S.heartbeat(0.18 + 0.22 * k))
    t += 60 / (66 + 60 * k)

# ---- the villain's whispers ----------------------------------------------------------------
speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    mix.add("voice", t0, x, 0.9)
    speech.append((t0, t0 + len(x) / S.SR))
mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart"))

end = int((DURATION - 0.8) * S.SR)
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
