"""MIRROR.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 182.0

SCENES = [
    ("S01", 0.0, 6.0, "hook", "The gym's mirror wall. He curls a dumbbell in his hoodie next to a big man. In the mirror the big man is the size he is; his own reflection is small, grey and hunched. COMPARED TO ticks up as he glances over. (Opens on the picture.)"),
    ("H1", 6.0, 14.0, "hook", "Night, in bed, the phone: physique after physique flicks past, every one +1 on COMPARED TO. The dark window beside the bed reflects him small. 'Every night, he measured himself against strangers.'"),
    ("S02", 14.0, 23.0, "wound", "His wardrobe mirror. The reflection is small and grey. On the shelf: his old swim medal and a photo of two boys in a pool. The villain rises out of the dark beside the mirror. 'look at you.' 'still so small.'"),
    ("B1", 23.0, 29.0, "stakes", "Outside the gym, Nikhil, goggles on his forehead and a towel round his neck: 'pool's open again. sunday 7, like school?' 'after i bulk.'"),
    ("G1", 29.0, 49.0, "grind", "One locked shot at the mirror wall over four weeks (WEEK 2, 5, 9, 14): heavier dumbbells, he quietly gets bigger, the reflection gets smaller, COMPARED TO climbs. 'he's bigger than you.' 'one more set.' 'not enough. never enough.'"),
    ("G2", 49.0, 56.0, "grind", "A blazing street, 38 degrees on a shop sign. Everyone in T-shirts, fanning themselves; he walks by in the hoodie, sweating. 'Even at 38 degrees, he kept the hoodie on.'"),
    ("G3", 56.0, 63.0, "grind", "Friends lining up for a photo on the phone held out at arm's length. He steps behind the tallest one. 'In every photo, he stood at the back.'"),
    ("R1", 63.0, 82.0, "rock bottom", "Sunday, 7:40 AM. His phone: Nikhil's pool photo, 'missed you again bro'. The wardrobe mirror: the reflection at its smallest, the villain huge. 'you'll never be enough.' He throws a towel over the mirror. The villain is still there. 'He covered the mirror. The voice stayed.'"),
    ("T1", 82.0, 100.0, "turn", "The gym. The big man: 'bro, can you take my pic?' Pumping, holding his breath, finding the light: PHOTO 1 ... 37. 'nah. delete them all.' 'i look tiny.' Then he scrolls a bigger man, and in the mirror his reflection shrinks and greys too. 'The man he envied saw a small man too.' 'Nobody is ever big enough for that mirror.'"),
    ("L1", 100.0, 110.0, "lesson", "The lesson drawn: THEIR PHOTO, one frame (1 second, 37 tries, best light, pumped, edited) against HIS MIRROR, a whole strip of ordinary days (every day, any light, tired, real). 'He had been comparing his every day' 'to someone else's best second.'"),
    ("I1", 110.0, 116.0, "practice", "INSTEAD OF COMPARING: compare with you, a year ago; mute accounts that make you feel small; train for what your body can do."),
    ("F1", 116.0, 130.0, "final fight", "SUNDAY, 7:00 AM, the pool. Nikhil in the water: 'coming in?' He stands at the edge in the hoodie. The villain at full size: 'keep it on.' 'they're all looking.' 'not yet.' Silence: he looks round. Nobody is looking: an uncle floating happily, kids splashing, a lady doing laps. He pulls the hoodie off; the villain breaks; he dives."),
    ("F2", 130.0, 138.0, "final fight", "Underwater: quiet, light, bubbles. He swims and smiles. 'Underwater, there was nothing to compare.'"),
    ("P1", 138.0, 152.0, "payoff", "A race with Nikhil, one length, both laughing; they sit on the edge, feet in the water. In the water his reflection is his real size, warm. COMPARED TO: ME, in gold. 'He stopped racing strangers.' 'He raced his friend instead.'"),
    ("VT", 152.0, 159.0, "viewer", "To the viewer: a phone, a post that makes you feel small, the MUTE button pressed, the post greys out. 'Mute one account that makes you feel small.' 'Then do one thing your body enjoys.'"),
    ("X1", 159.0, 168.0, "mirror", "The opening shot replayed: the gym mirror. A teenager in a hoodie stares at his small grey reflection. He, in a T-shirt now: 'that guy's photo took 37 tries.' '...really?' The kid's reflection grows to his real size."),
    ("TT", 168.0, 177.0, "title", "MIRROR. 'You're measuring your every day against their best second.' 'Look again.'"),
    ("HL", 177.0, 182.0, "helpline", "If the way you see your body is hurting you, talk to someone. India: Tele-MANAS 14416 · findahelpline.com"),
]

CAPS = {
    "C1": (0.4, 5.7), "C2": (9.4, 13.8), "C3": (51.6, 55.8), "C4": (58.8, 62.8), "C5": (77.6, 81.8),
    "C6": (95.2, 99.8), "C7": (96.8, 99.8), "C8": (102.4, 109.8), "C9": (104.6, 109.8),
    "C10": (132.4, 137.6), "C11": (146.4, 151.8), "C12": (148.0, 151.8),
    "V1": (152.4, 155.6), "V2": (155.8, 158.8),
    "T1": (169.6, 176.6), "T2": (172.0, 176.6),
    "H1": (177.4, 181.6), "H2": (178.4, 181.6),
}

CUES = {"V1": 16.4, "V2": 18.6, "V3": 32.0, "V4": 37.0, "V5": 44.0, "V6": 71.6, "V7": 119.0, "V8": 121.0, "V9": 123.2}

BUBBLES = [
    (23.6, 25.8, "nikhil", "pool's open again. sunday 7, like school?"),
    (26.1, 27.6, "him", "after i bulk."),
    (83.4, 85.2, "big", "bro, can you take my pic?"),
    (89.8, 91.4, "big", "nah. delete them all."),
    (91.6, 93.2, "big", "i look tiny."),
    (116.4, 118.2, "nikhil", "coming in?"),
    (160.2, 162.4, "him", "that guy's photo took 37 tries."),
    (162.8, 164.2, "kid", "...really?"),
]

G1_T0, G1_WEEK = 29.0, 5.0
G1_LABELS = ["WEEK 2", "WEEK 5", "WEEK 9", "WEEK 14"]

# COMPARED TO, top-left: every physique he measures himself against
COUNTS = [(0.0, 211), (2.2, 212), (4.4, 213)] + [(6.8 + i * 0.85, 214 + i) for i in range(7)] + \
         [(G1_T0 + 1.0 + i * G1_WEEK, v) for i, v in enumerate((640, 1380, 2710, 4090))] + [(66.0, 4612)]
RELABEL = 145.6       # the payoff: COMPARED TO: ME, in gold

# how big his reflection is drawn (1.0 = his real size)
REFL = [(0.0, 0.64), (14.0, 0.6), (G1_T0, 0.6)] + [(G1_T0 + 1.0 + i * G1_WEEK, v) for i, v in enumerate((0.58, 0.54, 0.49, 0.45))] + \
       [(66.0, 0.4)]

EVENTS = {
    "glance": [2.2, 4.4], "posts": [6.8 + i * 0.85 for i in range(7)], "born": (14.6, 16.2),
    "weeks": [G1_T0 + 1.0 + i * G1_WEEK for i in range(4)], "photo_flash": 60.2, "nikhil_post": 64.4, "towel": 75.0,
    "shots": (86.0, 89.4), "big_scroll": 93.6, "big_shrink": (94.0, 95.6),
    "lesson": 100.4, "card_i": 110.2, "rise": (117.6, 119.0), "silence": (125.0, 126.4), "look_round": (124.6, 126.2),
    "hoodie": 126.4, "crumble": 126.8, "dive": 128.2, "splash": 129.2,
    "race": (139.0, 143.6), "touch": 143.6, "laugh": 144.0, "sit": 147.0,
    "mute": 155.2, "grow_kid": 164.6, "title": 168.4,
}

PHOTOS = 37


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def step_at(table, t):
    v = None
    for tm, x in table:
        if t >= tm:
            v = x
    return v


def count_at(t):
    return step_at(COUNTS, t)


def count_changed(t):
    last = None
    for tm, _ in COUNTS:
        if 0 < tm <= t:
            last = tm
    return last


def refl_at(t):
    """How big his reflection is, eased between steps so it visibly shrinks."""
    prev = REFL[0]
    for tm, v in REFL:
        if t >= tm:
            prev = (tm, v)
    tm, v = prev
    before = REFL[0][1]
    for tm2, v2 in REFL:
        if tm2 < tm:
            before = v2
    k = min(1.0, max(0.0, (t - tm) / 0.8))
    k = k * k * (3 - 2 * k)
    return before + (v - before) * k


def his_scale(t):
    """He really does get stronger during the grind (the progress he can't see)."""
    return 1.0 + 0.06 * min(1.0, max(0.0, (t - G1_T0) / 20.0))
