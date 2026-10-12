"""ALONE: score, sound effects, voices and the mix. Reads the same timeline as the picture."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "toolkit"))
sys.path.insert(0, str(HERE))

from studio import sound as S  # noqa: E402
from timeline import DURATION, SCENES, CUES, EVENTS, TYPED, TYPE_T0, TYPE_T1  # noqa: E402

B = HERE / "build"
LEN = json.load(open(B / "line_lengths.json"))
mix = S.Mix(DURATION)

# ---- the theme: Em - C - G - D, music-box melody --------------------------------
CH = {"Em": [52, 55, 59], "C": [48, 52, 55], "G": [43, 50, 55, 59], "D": [50, 54, 57]}
PROG = ["Em", "C", "G", "D"]
MELODY = [(0, 76), (1, 79), (2, 83), (3, 81), (4, 79), (6, 76), (7, 74), (8, 76), (10, 71), (12, 74), (14, 76)]  # (beat, note)


def chords(t0, t1, bar, vel=0.4, style="block", prog=PROG, bus="music"):
    t, i = t0, 0
    while t < t1 - 0.1:
        notes = CH[prog[i % len(prog)]]
        if style == "block":
            for n in notes:
                mix.add(bus, t, S.piano(n, bar * 0.95, vel))
        elif style == "arp":
            for k in range(8):
                n = notes[k % len(notes)] + (12 if k >= 4 else 0)
                mix.add(bus, t + k * bar / 8, S.piano(n, bar / 3, vel * 0.8))
        elif style == "pulse":
            for k in range(4):
                for n in notes[:2]:
                    mix.add(bus, t + k * bar / 4, S.piano(n - 12, bar / 5, vel * 0.7))
        elif style == "single":
            mix.add(bus, t, S.piano(notes[0] + 12, bar, vel))
        t += bar
        i += 1


def pads(t0, t1, bar, vel=0.35, bright=1500, prog=PROG):
    t, i = t0, 0
    while t < t1 - 0.1:
        d = min(bar * 1.15, t1 - t + 0.4)
        mix.add("music", t, S.pad(CH[prog[i % len(prog)]], d, vel, bright, seed=i))
        t += bar
        i += 1


def melody(t0, beat, vel=0.5, octave=0, notes=MELODY, inst=S.music_box):
    for b, n in notes:
        mix.add("music", t0 + b * beat, inst(n + octave, beat * 2.2, vel))


bar70 = 4 * 60 / 70  # 3.43 s
bar80 = 4 * 60 / 80  # 3.0 s
beat70 = 60 / 70

# 0-31 wound and stakes: quiet, sparse
mix.add("music", 0.6, S.piano(64, 3, 0.35))
mix.add("music", 2.4, S.piano(59, 3, 0.3))
pads(0.0, 31.0, bar70, 0.18, 900)
chords(5.0, 16.0, bar70, 0.28, "single")
mix.add("music", 16.2, S.pad([28, 40], 15.0, 0.7, 380, seed=7))  # villain drone (low)
mix.add("music", 16.2, S.pad([52, 53], 15.0, 0.12, 900, seed=8))  # mid-range edge so phones hear it
mix.add("music", 31.6, S.piano(52, 3, 0.3))

# 34-64 grind montage: hollow 80 bpm arpeggio, one chord per cut
chords(34.0, 64.0, bar80, 0.32, "arp")
pads(34.0, 64.0, bar80, 0.16, 1100)

# 64-76 rock bottom: tired single notes, drone
for i, n in enumerate([64, 62, 59, 55, 52]):
    mix.add("music", 69.4 + i * 1.3, S.piano(n, 2.5, 0.32))
mix.add("music", 69.1, S.pad([28, 40, 52], 7.0, 0.6, 420, seed=9))

mix.add("music", 76.0, S.pad([40, 47, 52], 6.0, 0.35, 900, seed=12))
# 76-96 the turn: opening up, first full melody on the reveal
pads(76.0, 96.0, bar70, 0.30, 1800)
melody(82.0, beat70, 0.5)
chords(82.0, 96.0, bar70, 0.30, "block")
mix.add("sfx", 88.0, S.shimmer(2.4, 0.25))

# 96-113.2 final fight: the chords become pulses, rising drone
chords(100.0, 113.2, bar80, 0.32, "pulse", prog=["Em", "Em", "C", "D"])
mix.add("music", 96.0, S.pad([28, 40, 47], 17.2, 0.55, 500, seed=10))
riser = S.whoosh(3.0, 0.25, up=True)
mix.add("sfx", 110.2, riser)

# 115.2 SEND, then warmth
mix.add("sfx", 115.2, S.hit(0.95))
mix.add("sfx", 115.2, S.whoosh(0.5, 0.6, up=False, seed=21))
mix.add("sfx", 115.4, S.shimmer(3.0, 0.45, 79))
pads(115.2, 124.0, bar70 * 1.3, 0.55, 2400, prog=["G", "D", "Em"])
melody(118.4, beat70 * 1.25, 0.6, notes=MELODY[:6])

# 124-148 payoff and mirror: warm, full
chords(124.0, 148.0, bar70, 0.30, "block", prog=["C", "G", "D", "Em"])
pads(124.0, 148.0, bar70, 0.24, 2000, prog=["C", "G", "D", "Em"])
melody(127.0, beat70, 0.55)
melody(140.6, beat70, 0.42, notes=MELODY[:5])

# 148-158 title: the theme, full, ending on G
chords(148.4, 155.3, bar70, 0.34, "block", prog=["C", "D"])
for n in CH["G"] + [67]:
    mix.add("music", 155.2, S.piano(n, 2.6, 0.36))
melody(148.6, beat70, 0.5)

# ---- sound effects on every visible action --------------------------------------
room = S.room_tone(DURATION, 0.035)
mix.add("amb", 0, room)
mix.add("amb", 58.0, S.rain(18.0, 0.10))
mix.add("amb", 76.0, S.rain(5.0, 0.10, seed=31))
mix.add("amb", 34.0, S.street(3.5, 0.06))
mix.add("amb", 140.0, S.street(8.0, 0.06, seed=32))
cafe = S.bp(S.rng(40).normal(0, 1, int(6 * S.SR)).astype(np.float32), 250, 2500) * 0.03
mix.add("amb", 134.0, cafe)

mix.add("sfx", EVENTS["hud_in"], S.tick(0.4))
mix.add("sfx", EVENTS["first_tap"], S.tap(0.5))
mix.add("sfx", EVENTS["first_tap"] + 0.05, S.tick(0.35))
mix.add("sfx", EVENTS["candle_out"] - 0.2, S.blow(0.7, 0.35))
mix.add("sfx", EVENTS["mum_buzz"], S.buzz(0.9, 0.55))
mix.add("sfx", EVENTS["pickup"], S.thud(0.2))
for t0 in [34.0, 37.5, 41.0, 45.0, 49.0, 54.0, 58.0]:  # montage cuts
    mix.add("sfx", t0 - 0.12, S.whoosh(0.35, 0.18, seed=int(t0)))
for t0 in [34.4, 38.6, 41.4, 45.3, 49.3, 54.3, 58.3]:  # HUD pops: still 0
    mix.add("sfx", t0, S.tick(0.35))
mix.add("sfx", 38.5, S.tap(0.3, 2))
for k, tm in enumerate([49.8, 50.1, 50.4, 52.0, 52.25, 52.5]):  # type 'hey', delete it
    mix.add("sfx", tm, S.tap(0.35, k))
mix.add("sfx", EVENTS["storage_buzz"], S.buzz(0.8, 0.6))
mix.add("sfx", 64.7, S.tick(0.5))
mix.add("sfx", 65.4, S.thud(0.2))
mix.add("sfx", EVENTS["hud_red"], S.thud(0.5))
mix.add("sfx", EVENTS["hud_red"], S.tick(0.4))
mix.add("sfx", EVENTS["face_down"], S.thud(0.55))
for tm, x in S.footsteps([76.0 + k * 0.289 for k in range(11)], 0.5):
    mix.add("sfx", tm, x)
mix.add("sfx", 96.9, S.thud(0.18))
n = len(TYPED)
for k in range(n):
    mix.add("sfx", TYPE_T0 + (k + 1) * (TYPE_T1 - TYPE_T0) / n, S.tap(0.35, k + 10))
mix.add("sfx", 118.6, S.tick(0.3))
mix.add("sfx", EVENTS["read"], S.tick(0.3))
for k in range(5):
    mix.add("sfx", EVENTS["typing"][0] + k * 0.28, S.tap(0.12, 40 + k))
mix.add("sfx", EVENTS["reply1"], S.tick(0.5))
mix.add("sfx", EVENTS["reply1"], S.shimmer(2.0, 0.35, 84))
mix.add("sfx", EVENTS["reply2"], S.tick(0.4))
mix.add("sfx", 135.6, S.tick(0.3))  # cup on table
mix.add("sfx", 137.0, S.tick(0.25))
for tm, x in S.footsteps([140.0 + k * 0.236 for k in range(11)], 0.28):
    mix.add("sfx", tm, x)
mix.add("sfx", EVENTS["mirror_tap"], S.tap(0.45, 60))
mix.add("sfx", EVENTS["mirror_gold"], S.shimmer(2.0, 0.3, 79))
mix.add("sfx", EVENTS["mirror_gold"], S.tick(0.4))

# heartbeat under the final fight: slow to fast, the only thing left in the silence
t = 100.0
while t < 115.2:
    k = (t - 100.0) / 15.2
    bpm = 66 + 54 * k
    mix.add("heart", t, S.heartbeat(0.16 + 0.22 * k))
    t += 60 / bpm

# ---- voices ---------------------------------------------------------------------
speech = []
for k, t0 in CUES.items():
    x = np.load(B / f"line_{k}.npy")
    gain = {"V": 0.85, "N": 1.0}.get(k[0], 1.0)
    if k == "MOM":
        gain = 1.1
    mix.add("voice", t0, x, gain)
    speech.append((t0, t0 + len(x) / S.SR))

mix.duck("music", speech, -7)
mix.duck("amb", speech, -4)
mix.silence_window(*EVENTS["silence"], keep=("voice", "heart"))

# gentle fade-out at the end
end = int((DURATION - 2.0) * S.SR)
for b in mix.buses.values():
    b[end:] *= np.linspace(1, 0, len(b) - end)

out = mix.render(-2.5, gain_db=3.0)
S.write_wav(B / ("mix_v2.wav" if "--v2" in sys.argv else "mix.wav"), out)

rows = S.phone_levels(out, [(s[0], s[1], s[2]) for s in SCENES])
med = float(np.median([r[3] for r in rows]))
print("Phone-speaker loudness per scene (300 Hz high-pass, active parts):")
for name, t0, t1, db in rows:
    flag = "  <-- more than 6 dB quieter" if db < med - 6 else ""
    print(f"  {name:4s} {t0:6.1f}-{t1:6.1f}s  {db:6.1f} dBFS{flag}")
print(f"  median {med:.1f} dBFS")
json.dump({"phone_levels": rows, "median": med}, open(B / "levels.json", "w"), indent=1)
