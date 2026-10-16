"""SOLD.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 175.0

SCENES = [
    ("S01", 0.0, 4.0, "hook", "2:07 AM, in bed, his face lit by the phone. 'He bought something every night.'"),
    ("H1", 4.0, 7.0, "hook", "The phone: DESK LAMP $39, the red BUY NOW. His thumb taps. ORDER PLACED. THE SEA jar: $640 to $601."),
    ("H2", 7.0, 12.0, "hook", "The door: a courier hands him a box. He opens it: a little burst of light, he smiles. It fades in two seconds."),
    ("H3", 12.0, 17.0, "hook", "The flat: boxes land on a tower by the window, one by one, each with a sticker: BORED, BAD DAY, SUNDAY, SALE, 2AM. The tower starts to block the light."),
    ("S02", 17.0, 25.0, "wound", "2 AM again. The villain rises from the phone's glow: 'treat yourself.' 'you'll feel better.'"),
    ("B1", 25.0, 33.0, "stakes", "The shelf: a jar labelled THE SEA, the sea postcard on the window behind the boxes. 'He was saving for the sea.' A coin flies from the jar into the phone. 'Every box came out of the jar.'"),
    ("G1", 33.0, 38.0, "grind", "WEEK 1. The bus home after a bad day; he buys. Box: BAD DAY. 'you earned it.' 'Every bad feeling had a fix.'"),
    ("G2", 38.0, 43.0, "grind", "WEEK 2. Sunday on the floor by the bed, bored, scrolling. 'it's on sale.' Box: SUNDAY."),
    ("G3", 43.0, 48.0, "grind", "WEEK 3. His brother: 'call me sometime?' Left. He buys instead. Box: LONELY. 'It lasted until the door.'"),
    ("G4", 48.0, 53.0, "grind", "WEEK 4. The tower covers the window. The room is dark. He squeezes past. 'just this one.' Box: TIRED."),
    ("G5", 53.0, 58.0, "grind", "WEEK 5. The last coin leaves the jar. $0 in red. 'The jar was empty.'"),
    ("R1", 58.0, 68.0, "rock bottom", "He wants to see the postcard. He pulls one box: the tower falls on him. A sale buzz: 'this one will fix it.'"),
    ("R2", 68.0, 74.0, "rock bottom", "Close: sitting in the fallen boxes, nearly all still taped shut. 'He hadn't opened most of them.'"),
    ("T1", 74.0, 84.0, "turn", "He reads the stickers: BORED, BAD DAY, SUNDAY, LONELY, TIRED, 2AM. 'He wasn't buying things.' 'He was buying a feeling.'"),
    ("T2", 84.0, 94.0, "turn", "The lesson drawn: HOW HE FELT. Up at BUY NOW, up at ON ITS WAY, down at the door, lower each time. 'The feeling never came in the box.'"),
    ("T3", 94.0, 104.0, "practice", "He returns the taped boxes one by one; coins fly back into the jar, $0 to $556. The window comes back."),
    ("T4", 104.0, 112.0, "practice", "BORED: a walk at dusk. LONELY: he calls his brother. BAD DAY: he cooks. 'So he gave each feeling what it wanted.'"),
    ("F1", 112.0, 124.0, "final fight", "Friday, 2:07 AM. FLASH SALE ENDS IN 00:00:59, ONLY 1 LEFT. The villain rises from the phone and pushes his thumb to BUY NOW: 'it ends in a minute.' 'only one left.' 'you'll miss it.' 'buy it.' He sets the phone down."),
    ("F2", 124.0, 128.0, "final fight", "The countdown on the nightstand: 3, 2, 1, 0. Near-silence, heartbeat. SALE ENDED. The villain crumbles."),
    ("F3", 128.0, 133.0, "final fight", "Nothing happens. Then: NEW SALE! ENDS IN 23:59:59. He laughs. 'The sale ended.' 'Nothing happened.'"),
    ("P1", 133.0, 141.0, "payoff", "Weeks: coins drop into the jar, the window is clear, morning light. THE SEA $1,200 in gold. He takes the postcard down."),
    ("P2", 141.0, 150.0, "payoff", "The sea at golden hour. He stands in the waves. 'The sea was what he wanted.' 'It never fit in a box.'"),
    ("VT", 150.0, 158.0, "viewer", "To the viewer: YOUR CART (3). 'Open your cart.' 'Leave it there for one day.' BUY NOW turns into TOMORROW."),
    ("X1", 158.0, 165.0, "mirror", "2:07 AM again, the opening shot: a cart on his phone. He turns it face down and sleeps. On the shelf: a seashell and a new jar, THE MOUNTAINS."),
    ("TT", 165.0, 175.0, "title", "SOLD. 'What you want isn't in the cart.' 'Wait one day.'"),
]

CAPS = {
    "C1": (0.4, 3.9), "C2": (25.4, 32.8), "C3": (29.0, 32.8), "C4": (35.6, 37.8), "C5": (45.6, 47.8),
    "C6": (55.0, 57.8), "C7": (69.0, 73.8), "C8": (77.0, 83.8), "C9": (79.4, 83.8), "C10": (89.0, 93.8),
    "C11": (106.0, 111.8), "C12": (129.0, 132.8), "C13": (130.6, 132.8), "C14": (143.0, 149.8), "C15": (145.4, 149.8),
    "V1": (150.6, 153.8), "V2": (154.0, 157.6),
    "T1": (166.6, 174.6), "T2": (169.0, 174.6),
}

CUES = {
    "V1": 20.6, "V2": 22.8, "V3": 34.2, "V4": 39.4, "V5": 49.6, "V6": 63.6,
    "V7": 114.6, "V8": 117.5, "V9": 119.6, "V10": 121.2,
}

BUBBLES = [
    (7.6, 9.0, "courier", "for you!"),
    (33.4, 34.8, "boss", "redo it."),
    (108.4, 110.4, "bro", "hey you!"),
]

# every purchase: (time the coin leaves the jar and the box joins the tower, sticker, price)
BUYS = [(5.4, "CAN'T SLEEP", 39),
        (12.6, "BORED", 45), (13.4, "BAD DAY", 60), (14.2, "SUNDAY", 35), (15.0, "SALE", 29), (15.8, "2AM", 52),
        (36.4, "BAD DAY", 64), (41.4, "SUNDAY", 48), (46.0, "LONELY", 85), (51.0, "TIRED", 70), (55.0, "JUST BECAUSE", 113)]
OPENED = {0, 1}  # the lamp and the BORED box; everything else is still taped shut
START = 640
GOAL = 1200

# returns in T3: (time it leaves through the door, index into BUYS)
RETURNS = [(95.0 + i * 0.95, i + 2) for i in range(9)]
SAVE_T0, SAVE_T1 = 133.4, 138.6   # the jar fills from what's left to GOAL

EVENTS = {
    "tap": 5.4, "doorbell": 7.2, "open": 9.0, "born": (19.0, 20.8), "coin": 30.0,
    "bro_text": 44.0, "pull": 60.6, "collapse": 61.2, "sale_buzz": 63.2,
    "flash": 112.6, "push": 117.0, "set_down": 122.4, "zero": 127.0, "silence": (125.2, 127.0),
    "new_sale": 130.2, "laugh": 130.6, "gold": 138.6, "postcard": 139.4,
    "cart_tomorrow": 155.4, "face_down": 161.4, "title": 166.0,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def jar_at(t):
    """Money in THE SEA jar at time t."""
    v = START - sum(p for tm, _, p in BUYS if t >= tm)
    v += sum(BUYS[i][2] for tm, i in RETURNS if t >= tm)
    if t >= SAVE_T0:
        base = v
        k = min(1.0, (t - SAVE_T0) / (SAVE_T1 - SAVE_T0))
        k = k * k * (3 - 2 * k)
        v = round(base + (GOAL - base) * k)
    return int(v)


def jar_changed(t):
    last = None
    for tm, _, _ in BUYS:
        if t >= tm:
            last = tm
    for tm, _ in RETURNS:
        if t >= tm:
            last = tm
    return last


def tower(t):
    """Indices of the boxes standing in the tower (bought, not yet fallen)."""
    if t >= EVENTS["collapse"]:
        return []
    return [i for i, (tm, _, _) in enumerate(BUYS) if t >= tm]


def fallen(t):
    """Indices of the boxes lying on the floor after the collapse (until returned)."""
    if t < EVENTS["collapse"]:
        return []
    gone = {i for tm, i in RETURNS if t >= tm}
    out = [i for i, (tm, _, _) in enumerate(BUYS) if tm < EVENTS["collapse"] and i not in gone]
    return out
