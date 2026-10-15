"""HEAVY.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 166.0

SCENES = [
    ("S01", 0.0, 3.0, "hook", "Black. 'He never forgot anything.'"),
    ("H1", 3.0, 6.6, "hook", "Office. The boss: 'great work, Kai!' Kai takes the credit for their project. A red stone KAI drops into his sack. CARRYING 9 kg."),
    ("H2", 6.6, 9.2, "hook", "Café counter. The wrong drink, 'sorry!'. Stone. 11 kg."),
    ("H3", 9.2, 11.8, "hook", "Street. A car splashes him through a puddle. Stone. 13 kg."),
    ("H4", 11.8, 14.4, "hook", "Phone: Dad: 'still in that job?' Stone DAD. 18 kg."),
    ("H5", 14.4, 17.0, "hook", "Four stones in quick cuts, he staggers. 26 kg."),
    ("S02", 17.0, 26.0, "wound", "Night. The sack by his bed; the stones glow red; the villain rises from the KAI stone's glow: 'never forget.' 'he did that to you.'"),
    ("S03", 26.0, 29.0, "wound", "Black. 'He thought remembering kept him safe.'"),
    ("B1", 29.0, 37.0, "stakes", "Phone: Kai: 'drinks friday? miss you man'. Left on read. 'he doesn't get to.' The group: 'sunrise hike sat! 5am, the old hill'."),
    ("G1", 37.0, 41.0, "grind", "WEEK 1. Walking to work bent under the sack. 'He carried every one of them.' 31 kg."),
    ("G2", 41.0, 45.0, "grind", "WEEK 2. Team lunch, Kai there; he eats alone at his desk. 'Everywhere.' 36 kg."),
    ("G3", 45.0, 49.0, "grind", "WEEK 3. A colleague says hi; he snaps. 'they'll do it again.' 42 kg."),
    ("G4", 49.0, 53.0, "grind", "WEEK 4. The shower: the KAI stone glows through the steam."),
    ("G5", 53.0, 57.0, "grind", "WEEK 5. The sofa: the sack takes the seat; he sits on the floor. 'keep it.' 50 kg."),
    ("G6", 57.0, 61.0, "grind", "WEEK 6. The mirror: bent, grey. 'He thought it made him strong.' 58 kg."),
    ("R1", 61.0, 70.0, "rock bottom", "Saturday 5am, the bottom of the hill. He climbs, the sack drags him back; he slides and sits. The friends at the top, small. 'they're laughing at you.'"),
    ("R2", 70.0, 75.0, "rock bottom", "Close: him on the path, the sack behind him. 'He was the only one still carrying it.'"),
    ("T1", 75.0, 84.0, "turn", "He looks up: Kai at the top, laughing, no sack at all. 'Kai wasn't carrying anything.' 'He'd forgotten it years ago.'"),
    ("T2", 84.0, 93.0, "turn", "The lesson drawn: a seesaw. Kai's side floats; his side is pinned under the stones. 'A grudge doesn't weigh on them.' 'It weighs on you.'"),
    ("T3", 93.0, 102.0, "practice", "On the path he unpacks: the small stones, one by one, set down; they turn grey. 58 to 22 kg."),
    ("F1", 102.0, 114.0, "final fight", "The KAI stone, the heaviest. The villain wraps around the sack and holds it on him: 'never forget.' 'he doesn't deserve it.' 'he'll do it again.' 'don't let him off.'"),
    ("F2", 114.0, 118.0, "final fight", "He lifts it out, eyes closed. Near-silence, heartbeat."),
    ("F3", 118.0, 121.0, "final fight", "He sets it down. It turns grey. The villain crumbles to pebbles. CARRYING 0 kg."),
    ("P1", 121.0, 131.0, "payoff", "He climbs the hill, light. The sun rises: the first gold. Kai: 'you made it!' A high five."),
    ("P2", 131.0, 137.0, "payoff", "The group at the top in the sunrise. 'Letting go wasn't for Kai.' 'It was for him.'"),
    ("VT", 137.0, 146.0, "viewer", "To the viewer: a red stone with a blank label. 'Think of one name.' 'You can put it down.' It sets down and turns grey."),
    ("X1", 146.0, 156.0, "mirror", "Monday, the bus stop. A kid pockets a red pebble after a friend shoves past. He sets his own grey pebble on the bench. The kid looks, and sets his down too."),
    ("TT", 156.0, 166.0, "title", "HEAVY. 'You can't hurt them by carrying it.' 'Put it down.'"),
]

CAPS = {
    "C1": (0.4, 2.9), "C2": (26.3, 28.9), "C3": (37.3, 40.8), "C4": (41.3, 44.6), "C5": (57.3, 60.8),
    "C6": (71.0, 74.8), "C7": (78.4, 83.8), "C8": (80.6, 83.8), "C9": (88.0, 92.8), "C10": (90.2, 92.8),
    "C11": (132.0, 136.8), "C12": (134.0, 136.8),
    "V1": (137.6, 140.8), "V2": (141.0, 145.4),
    "T1": (157.6, 165.6), "T2": (160.0, 165.6),
}

CUES = {
    "V1": 20.6, "V2": 22.8, "V3": 32.6, "V4": 46.6, "V5": 54.6, "V6": 65.6,
    "V7": 104.4, "V8": 106.6, "V9": 108.8, "V10": 111.0,
}

BUBBLES = [
    (3.4, 6.4, "boss", "great work, Kai!"),
    (7.0, 9.0, "barista", "sorry!"),
    (45.4, 47.4, "sue", "morning!"), (46.2, 48.4, "him", "what do you want?"),
    (125.6, 128.6, "kai", "you made it!"),
    (147.8, 149.6, "kid2", "move!"),
]

# stones: (time it drops into the sack, label, kg)
STONES = [(4.6, "KAI", 9), (7.8, "LATTE", 2), (10.4, "SPLASH", 2), (13.0, "DAD", 5),
          (14.6, "BUS", 2), (15.2, "MIA", 2), (15.8, "GROUP CHAT", 2), (16.4, "NEIGHBOUR", 2),
          (33.4, "KAI 2", 5), (39.0, "BOSS", 3), (43.0, "LUNCH", 2), (47.2, "SUE", 3),
          (51.0, "SHOWER", 2), (55.2, "EX", 4), (59.0, "LANDLORD", 3), (60.2, "TRAFFIC", 3)]

# set down on the hill (the small ones, then Kai's)
DROPS = [(94.4, "LATTE"), (95.6, "SPLASH"), (96.8, "BUS"), (97.8, "MIA"), (98.8, "GROUP CHAT"), (99.6, "NEIGHBOUR"),
         (100.4, "TRAFFIC"), (101.2, "LANDLORD"), (101.8, "SHOWER"), (102.0, "LUNCH"), (102.0, "BOSS"),
         (102.0, "SUE"), (102.0, "EX"), (102.0, "DAD")]
KAI_DOWN = 118.0

EVENTS = {
    "credit": 4.6, "splash": 10.0, "dad_text": 12.2, "born": (19.2, 21.0),
    "kai_text": 30.0, "hike_text": 34.6, "snap": 46.2, "slip": 66.4, "look_up": 76.0,
    "eyes_closed": 115.0, "silence": (116.2, 118.0), "eyes_open": 117.6, "kai_down": KAI_DOWN,
    "crumble": 118.4, "sunrise": 122.0, "high_five": 128.6, "viewer_set": 143.0,
    "kid_shove": 147.6, "pebble_set": 150.6, "kid_set": 153.4, "title": 157.0,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def carried(t):
    """Labels in the sack at time t, heaviest first."""
    out = {}
    for tm, lab, kg in STONES:
        if t >= tm:
            out[lab] = kg
    for tm, lab in DROPS:
        if t >= tm and lab in out:
            out.pop(lab)
    if t >= KAI_DOWN:
        out.pop("KAI", None)
        out.pop("KAI 2", None)
    return sorted(out.items(), key=lambda kv: -kv[1])


def kg_at(t):
    return sum(kg for _, kg in carried(t)) + (0 if t < 4.6 else 0)


def kg_changed(t):
    last = None
    for tm, _, _ in STONES:
        if t >= tm:
            last = tm
    for tm, _ in DROPS:
        if t >= tm and (last is None or tm > last):
            last = tm
    if t >= KAI_DOWN:
        last = KAI_DOWN
    return last
