"""ALONE: the one place where every time lives. Picture and sound both read this file."""

DURATION = 158.0

# (id, start, end, beat, what happens)
SCENES = [
    ("S01", 0.0, 5.0, "hook", "Phone close-up: Friends 214. 'He had 214 friends.'"),
    ("S02", 5.0, 14.0, "wound", "Birthday table, one candle, phone. HUD: NEW MESSAGES 0. 'It was his birthday.'"),
    ("S03", 14.0, 22.0, "wound", "Villain rises out of the phone's glow. 'nobody remembered.' 'they never do.' He blows out the candle."),
    ("S04", 22.0, 31.0, "stakes", "Mum calls. He lies: 'yeah. we went out. it was great.'"),
    ("S05", 31.0, 34.0, "stakes", "Black. 'He didn't want to bother anyone.'"),
    ("M1", 34.0, 37.5, "grind", "DAY 3. Bus stop, phone in hand. 0."),
    ("M2", 37.5, 41.0, "grind", "DAY 9. Office desk, glances at phone. 'they're busy.'"),
    ("M3", 41.0, 45.0, "grind", "DAY 15. Bed, 2:14 am, face lit. 'He checked it 96 times a day.'"),
    ("M4", 45.0, 49.0, "grind", "DAY 21. Phone: friends' photo without him. 'they have new friends.'"),
    ("M5", 49.0, 54.0, "grind", "DAY 22. Chat with Sam, 3 years ago. Types 'hey', deletes it. 'it's been too long.'"),
    ("M6", 54.0, 58.0, "grind", "DAY 30. Dinner for one. 'It always said the same thing.'"),
    ("M7", 58.0, 64.0, "grind", "DAY 41. At the window in the rain."),
    ("R1", 64.0, 67.0, "rock bottom", "Buzz. HUD jumps to 1. He grabs it."),
    ("R2", 67.0, 69.0, "rock bottom", "Phone: 'Storage almost full.'"),
    ("R3", 69.0, 76.0, "rock bottom", "HUD back to 0 in red. 'see? nobody.' Phone face down, head on table."),
    ("T1", 76.0, 81.0, "turn", "He walks to the window and looks across the street."),
    ("T2", 81.0, 96.0, "turn", "Pull out: every window, someone alone with a phone showing 0. 'Everyone was waiting.' 'For someone else to go first.'"),
    ("F1", 96.0, 110.0, "final fight", "He opens the chat. Villain at full size: 'it's weird now.' 'they'll ignore you.' 'you'll look desperate.' 'don't.'"),
    ("F2", 110.0, 115.2, "final fight", "Phone: he types 'hey. i miss you.' Thumb over send. Near-silence, heartbeat."),
    ("F3", 115.2, 118.0, "final fight", "SEND. Gold cracks through the villain; it bursts."),
    ("F4", 118.0, 124.0, "final fight", "Calm. Delivered. He breathes out."),
    ("P1", 124.0, 130.0, "payoff", "Read. Typing... 'i thought you forgot about me.' HUD 1 in gold. 'coffee saturday?'"),
    ("P2", 130.0, 134.0, "payoff", "His first smile. 'He wasn't the only one.'"),
    ("P3", 134.0, 140.0, "payoff", "Café, daylight, two friends laughing."),
    ("X1", 140.0, 145.0, "mirror", "Walking home. One window still blue. He stops, takes out his phone."),
    ("X2", 145.0, 148.0, "mirror", "That window: their phone turns gold. 1."),
    ("TT", 148.0, 158.0, "title", "ALONE. 'Everyone is waiting for someone else.' 'Go first.'"),
]

# spoken lines: id -> start second (lengths come from build/line_lengths.json)
CUES = {
    "N1": 0.7, "N2": 6.3,
    "V1": 16.4, "V2": 18.8,
    "MOM": 23.5, "HIM": 26.9, "N3": 29.1,
    "N4": 31.5,
    "V3": 38.7, "N5": 41.6, "V4": 46.2, "V5": 51.9, "N6": 54.7,
    "V6": 70.0,
    "N7": 88.2, "N8": 91.6,
    "V7": 101.8, "V8": 104.2, "V9": 106.5, "V10": 108.9,
    "N9": 131.0,
    "N10": 150.6, "N11": 153.6,
}

# picture events the sound must hit on the exact frame
EVENTS = {
    "hud_in": 6.0, "first_tap": 9.6, "candle_out": 20.9, "mum_buzz": 22.3, "pickup": 23.2,
    "storage_buzz": 64.6, "hud_red": 69.1, "face_down": 72.2,
    "send": 115.2, "silence": (113.2, 115.2), "read": 125.0, "typing": (125.6, 127.0),
    "reply1": 127.0, "reply2": 128.8, "mirror_tap": 144.0, "mirror_gold": 145.6,
    "title": 148.5,
}

TYPED = "hey. i miss you."
TYPE_T0, TYPE_T1 = 110.5, 113.0


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]
