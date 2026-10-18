"""RAIN.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 163.0

SCENES = [
    ("S01", 0.0, 4.5, "hook", "The bus stop, morning. A small grey cloud rains on him and nobody else. 'He complained about everything.'"),
    ("H1", 4.5, 9.0, "hook", "The bus board: DELAYED. 'always late!' The words float up and the cloud grows."),
    ("H2", 9.0, 13.5, "hook", "The office coffee machine: 'cold. again.' The cloud grows; a colleague steps out of the drips."),
    ("H3", 13.5, 19.0, "hook", "Lunch with Nia and Ben: 'my boss is the WORST.' The rain falls on their food. 'It always felt better to say it.'"),
    ("S02", 19.0, 27.0, "wound", "Night, his flat. The cloud fills the ceiling; the villain rises out of it: 'it's not fair.' 'why is it always you?'"),
    ("B1", 27.0, 33.0, "stakes", "Nia: 'rough week. could really use friday x'. He answers: 'same. mine was HELL'."),
    ("G1", 33.0, 39.0, "grind", "MONDAY. The platform: CANCELLED. 'cancelled AGAIN?!' A stranger opens an umbrella."),
    ("G2", 39.0, 47.0, "grind", "FRIDAY. Dinner at Nia's. He talks all night: 'and THEN...' The friends open umbrellas at the table; Nia looks down. 'tell them how bad it is.'"),
    ("G3", 47.0, 53.0, "grind", "Walking home in the downpour. 'They stopped asking how his day was.'"),
    ("G4", 53.0, 59.0, "grind", "His flat, the cloud filling the room. 'nobody has it worse.' 'He thought he was just being honest.'"),
    ("R1", 59.0, 68.0, "rock bottom", "NEXT FRIDAY. Outside Nia's window: the dinner, warm, without him. 'see? they don't care.'"),
    ("T1", 68.0, 82.0, "turn", "Nia comes out with the bin. 'you didn't invite me.' 'mum's in hospital.' 'three weeks now.' Under the porch light, a small cloud over her too. '...you never said.' 'you never asked.'"),
    ("T2", 82.0, 94.0, "turn", "The lesson drawn: his words rise into his cloud and it rains on everyone near; hers go out to other people. 'Saying it never let the rain out.' 'It fed the cloud.'"),
    ("T3", 94.0, 104.0, "practice", "INSTEAD: catch it, name one thing that's fine, ask them first. The bus late again: he looks up instead. The cold coffee: a shrug. CLOUDY."),
    ("F1", 104.0, 116.0, "final fight", "Friday dinner. 'how was your week?' The worst week yet; the cloud swells, the villain rises: 'tell them.' 'it's not fair.' 'you deserve to.' 'say it.'"),
    ("F2", 116.0, 119.0, "final fight", "Near-silence. He turns to Nia: 'how's your mum?'"),
    ("F3", 119.0, 125.0, "final fight", "The villain crumbles, the cloud breaks, sun through the window. CLEAR, in gold. 'better. thanks for asking.'"),
    ("P1", 125.0, 135.0, "payoff", "The dinner, warm. 'and your week?' 'the train died. I walked home in socks.' Laughter. 'The bad days still came.' 'He just stopped feeding them.'"),
    ("VT", 135.0, 144.0, "viewer", "To the viewer: a small cloud. 'Count your complaints today.' 'Trade one for a question.' It breaks into light."),
    ("X1", 144.0, 153.0, "mirror", "The opening bus stop, morning. A stranger with a little cloud: 'always late!' Him: 'nice sky though.' The stranger looks up."),
    ("TT", 153.0, 163.0, "title", "RAIN. 'Everyone you meet is standing in their own rain.' 'Ask them first.'"),
]

CAPS = {
    "C1": (0.5, 4.3), "C2": (16.6, 18.8), "C3": (47.6, 52.8), "C4": (56.0, 58.8),
    "C5": (86.0, 93.8), "C6": (88.4, 93.8), "C7": (130.0, 134.8), "C8": (132.0, 134.8),
    "V1": (135.6, 139.4), "V2": (139.8, 143.6),
    "T1": (154.6, 162.6), "T2": (157.0, 162.6),
}

CUES = {"V1": 21.2, "V2": 23.6, "V3": 45.0, "V4": 54.2, "V5": 62.6,
        "V6": 107.0, "V7": 109.0, "V8": 111.0, "V9": 113.2}

BUBBLES = [
    (5.6, 7.2, "him", "always late!"),
    (9.8, 11.4, "him", "cold. again."),
    (14.2, 16.0, "him", "my boss is the WORST."),
    (34.2, 36.0, "him", "cancelled AGAIN?!"),
    (39.6, 41.4, "him", "and THEN..."),
    (42.6, 44.4, "him", "...and my BOSS..."),
    (69.2, 70.4, "nia", "oh. hey."),
    (70.8, 72.6, "him", "you didn't invite me."),
    (73.0, 74.8, "nia", "mum's in hospital."),
    (75.0, 76.6, "nia", "three weeks now."),
    (77.0, 78.6, "him", "...you never said."),
    (79.0, 81.6, "nia", "you never asked."),
    (104.8, 106.6, "ben", "how was your week?"),
    (116.9, 118.9, "him", "how's your mum?"),
    (120.4, 122.8, "nia", "better. thanks for asking."),
    (125.6, 127.0, "ben", "and your week?"),
    (127.4, 129.8, "him", "the train died. I walked home in socks."),
    (146.0, 147.6, "stranger", "always late!"),
    (148.4, 150.2, "him", "nice sky though."),
]

FEEDS = [7.4, 11.6, 16.2, 31.0, 36.2, 41.6, 44.6, 72.8]
SHRINKS = [99.2, 101.6]
SWELL = (106.8, 113.6)
CLEAR_T = 119.4

EVENTS = {
    "born": (19.6, 21.0), "nia_text": 27.6, "his_reply": 30.0, "umbrella": 36.4, "umbrellas": 42.0,
    "door": 68.6, "nia_cloud": 73.0, "thought": 82.4, "true": 85.4, "card": 94.2, "look_up": 99.2, "shrug": 101.6,
    "rise": 107.0, "silence": (115.4, 116.9), "turn_to_nia": 116.4, "crumble": 119.4, "sun": 119.6,
    "laugh": 130.0, "viewer_break": 141.2, "stranger_up": 150.6, "title": 154.0,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def _prog(t, a, b):
    return 0.0 if t <= a else 1.0 if t >= b else (t - a) / (b - a)


def _ease(x):
    return x * x * (3 - 2 * x)


def cloud_k(t):
    """Size of his cloud, 0..1."""
    k = 0.5
    for tm in FEEDS:
        k += 0.1 * _ease(_prog(t, tm, tm + 0.6))
    k = min(k, 1.0)
    for tm in SHRINKS:
        k -= 0.3 * _ease(_prog(t, tm, tm + 0.8))
    k += 0.5 * _ease(_prog(t, *SWELL)) * (1 - _prog(t, CLEAR_T, CLEAR_T + 0.6))
    k *= 1 - _ease(_prog(t, CLEAR_T, CLEAR_T + 1.2))
    return max(0.0, min(1.0, k))


def forecast(t):
    k = cloud_k(t)
    if t >= CLEAR_T + 0.6:
        return "CLEAR"
    if k > 0.85:
        return "STORM"
    if k > 0.45:
        return "RAIN"
    return "CLOUDY"


def forecast_changed(t):
    last = None
    for tm in FEEDS + SHRINKS + [CLEAR_T + 0.6]:
        if t >= tm:
            last = max(last or 0, tm)
    return last
