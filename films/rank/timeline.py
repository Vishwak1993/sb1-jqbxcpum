"""RANK.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 182.0

SCENES = [
    ("S01", 0.0, 6.0, "hook", "2:14 AM, his desk under a lamp, books stacked. The laptop: MOCK TEST 14 · AIR 48,210. The number rises over his head in red. 'He was seventeen. He was a number.' (Opens on the picture.)"),
    ("H1", 6.0, 14.0, "hook", "Dinner. Dad: 'rohan got AIR 312.' Mum: 'he studies 16 hours, beta.' Both look at the red number over his head. 'At home, everyone saw the number.'"),
    ("S02", 14.0, 23.0, "wound", "Back at the desk, night. The villain rises out of the lamp's glow. 'you are your rank.' 'they're ashamed of you.'"),
    ("B1", 23.0, 29.0, "stakes", "Pihu at his door with a paper kite: 'bhaiya, kites on sankranti? you promised.' 'after JEE.' The kite he made her hangs on the shelf."),
    ("G1", 29.0, 49.0, "grind", "One locked shot, four mock tests (MOCK 15 to 18): the rank gets worse, the clock later (1:30, 2:40, 3:30, 4:10), the number over his head bigger. 'study more.' 'sleep is for toppers.' 'rohan wouldn't stop.'"),
    ("G2", 49.0, 56.0, "grind", "Through his window: Pihu and Dad flying a kite in the lane. He pulls the curtain shut. 'He stopped looking up from the book.'"),
    ("G3", 56.0, 63.0, "grind", "The bathroom mirror at dawn: where his face should be, the reflection shows only the red number. 'He couldn't remember who he was without it.'"),
    ("R1", 63.0, 82.0, "rock bottom", "MOCK 19, the exam hall. The clock ticks, his hands shake, the number grows over him, the words on the paper swim. The pencil drops. TIME'S UP. AIR 74,000. 'you're going to fail them.' 'The harder he held on, the less he could see.'"),
    ("T1", 82.0, 100.0, "turn", "Night, the front step. Dad sits beside him. 'i'm sorry. i'm not rohan.' Dad unfolds an old card: '1996. rank 41,286.' 'i didn't get in either.' 'i was scared for you. not of your rank.' A faint grey number shows over Dad's head and fades; his own number shrinks and goes grey. 'His dad had carried a number too.' 'He had put it down years ago.'"),
    ("L1", 100.0, 110.0, "lesson", "The lesson drawn: a long line of a life, AGE 17 to 80. The rank shrinks into a single dot on it marked JEE. 'One exam. One day.' 'He had made it his whole life.'"),
    ("I1", 110.0, 116.0, "practice", "INSTEAD OF MORE HOURS: sleep 7 hours, even before a test; learn from one mistake, not the rank; tell someone when it's too much."),
    ("F1", 116.0, 130.0, "final fight", "JAN 21, 11:40 PM, the night before JEE Main. The villain at full size: 'one more chapter.' 'you're not ready.' 'don't you dare sleep.' Silence. He closes the book and switches off the lamp; the villain breaks in the dark."),
    ("F2", 130.0, 138.0, "final fight", "The exam hall in morning light. He breathes in, out (a breathing ring), no number over his head, and begins to write."),
    ("P1", 138.0, 152.0, "payoff", "SANKRANTI. The park, a blue sky full of kites. His phone: JEE MAIN AIR 21,480. He smiles, pockets it, and flies the kite with Pihu. 'It wasn't Rohan's rank.' 'It was his own. And so was his life.'"),
    ("VT", 152.0, 159.0, "viewer", "To the viewer: a lamp switching off. 'If you're preparing for an exam, sleep tonight.' 'And tell one person how you really feel.'"),
    ("X1", 159.0, 168.0, "mirror", "The colony gate. A neighbour: 'what rank did your son get?' Dad: 'ask me how he is.' The red number over the neighbour's own son fades."),
    ("TT", 168.0, 177.0, "title", "RANK. 'A rank measures one exam. Not you.' 'Breathe. Then begin.'"),
    ("HL", 177.0, 182.0, "helpline", "Exam stress feeling like too much? India: Tele-MANAS 14416 · findahelpline.com"),
]

CAPS = {
    "C1": (0.4, 5.7), "C2": (10.4, 13.8), "C3": (52.2, 55.8), "C4": (59.0, 62.8), "C5": (77.6, 81.8),
    "C6": (95.4, 99.8), "C7": (97.2, 99.8), "C8": (102.4, 109.8), "C9": (104.8, 109.8),
    "C10": (146.4, 151.8), "C11": (148.0, 151.8),
    "V1": (152.4, 155.6), "V2": (155.8, 158.8),
    "T1": (169.6, 176.6), "T2": (172.0, 176.6),
    "H1": (177.4, 181.6), "H2": (178.4, 181.6),
}

CUES = {"V1": 16.4, "V2": 18.6, "V3": 32.0, "V4": 37.0, "V5": 44.0, "V6": 72.0, "V7": 119.0, "V8": 121.2, "V9": 123.2}

BUBBLES = [
    (6.6, 8.2, "dad", "rohan got AIR 312."),
    (8.4, 10.2, "mum", "he studies 16 hours, beta."),
    (23.6, 25.6, "pihu", "bhaiya, kites on sankranti? you promised."),
    (25.9, 27.2, "him", "after JEE."),
    (84.6, 86.6, "him", "i'm sorry. i'm not rohan."),
    (87.6, 89.6, "dad", "1996. rank 41,286."),
    (90.0, 91.8, "dad", "i didn't get in either."),
    (92.2, 94.8, "dad", "i was scared for you. not of your rank."),
    (160.0, 161.8, "uncle", "what rank did your son get?"),
    (162.4, 164.0, "dad", "ask me how he is."),
]

G1_T0, G1_TEST = 29.0, 5.0
G1_LABELS = ["MOCK 15", "MOCK 16", "MOCK 17", "MOCK 18"]
G1_CLOCKS = ["1:30", "2:40", "3:30", "4:10"]

# the rank, as the HUD and the number over his head show it
AIRS = [(0.0, None), (3.0, 48210), (G1_T0 + 2.2, 51300), (G1_T0 + 7.2, 46900), (G1_T0 + 12.2, 58700), (G1_T0 + 17.2, 62400),
        (75.6, 74000)]
RELABEL = 141.6       # the result in the park: JEE MAIN AIR 21,480, in gold
FINAL_AIR = 21480

EVENTS = {
    "result": 3.0, "born": (14.6, 16.2), "g1_results": [G1_T0 + 2.2 + i * G1_TEST for i in range(4)],
    "curtain": 51.2, "pencil": 74.6, "times_up": 75.4, "dad_sits": 83.0, "card": 87.4, "dad_num": (88.0, 94.0),
    "shrink": (92.4, 95.0), "lesson": 100.4, "card_i": 110.2, "rise": (117.6, 119.0), "silence": (125.0, 126.4),
    "book": 126.4, "lamp": 127.2, "crumble": 127.4, "breath": 130.6, "write": 135.6,
    "buzz": 140.4, "pocket": 143.4, "kite": 144.0, "laugh": 148.0, "lamp_vt": 156.0, "fade_kid": 164.6, "title": 168.4,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def air_at(t):
    v = None
    for tm, x in AIRS:
        if t >= tm:
            v = x
    return v


def air_changed(t):
    last = None
    for tm, _ in AIRS:
        if 0 < tm <= t:
            last = tm
    return last


def weight(t):
    """How big the number over his head is drawn, 0..1 (it grows with every test and shrinks at the turn)."""
    k = 0.35
    for i, tm in enumerate(EVENTS["g1_results"]):
        if t >= tm:
            k = 0.45 + 0.1 * i
    if t >= EVENTS["times_up"]:
        k = 1.0
    s0, s1 = EVENTS["shrink"]
    if t >= s0:
        k *= 1 - 0.85 * min(1.0, (t - s0) / (s1 - s0))
    return k
