"""NO.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 160.0

# (id, start, end, beat, what happens)
SCENES = [
    ("S01", 0.0, 3.0, "hook", "Black. 'He never said no.'"),
    ("H1", 3.0, 5.6, "hook", "Office. Boss: 'can you stay late?' 'sure!' First red string drops onto his wrist. SAID YES 1."),
    ("H2", 5.6, 8.2, "hook", "His front door. Neighbour holds out a dog: 'just for the weekend?' 'of course!' 2."),
    ("H3", 8.2, 10.8, "hook", "Café table. 'you'll plan the trip, right?' 'yeah!' 3."),
    ("H4", 10.8, 13.4, "hook", "Shop queue. A man cuts in: 'you don't mind, right?' 'no no, go ahead!' 4."),
    ("H5", 13.4, 15.6, "hook", "Street. Dan with boxes: 'help me move?' 'yes!' 5."),
    ("H6", 15.6, 17.6, "hook", "Four snap close-ups of his smile: 'sure!' 'happy to!' 'of course!' 'anything!' 6-9."),
    ("S02", 17.6, 27.0, "wound", "Home at night, nine strings trailing up. Calendar: SAT = ME. Easel. He reaches for the brush; the strings yank his arm back. Tilt up: the villain holds them all. 'they'll stop liking you.'"),
    ("S03", 27.0, 31.6, "stakes", "Phone: 'free saturday? need a favour'. 'say yes.' Forced smile: 'yes!' 10. ME crossed out, 'Dan'."),
    ("S04", 31.6, 34.6, "stakes", "Black. 'There was always next Saturday.'"),
    ("G1", 34.6, 37.6, "grind", "WEEK 1. Carrying Dan's boxes, pulled along by the strings. 14."),
    ("G2", 37.6, 41.2, "grind", "WEEK 2. Office on a Saturday. Ana (scarf): 'how do you do it all?' He lies: 'i love it!' 22."),
    ("G3", 41.2, 44.2, "grind", "WEEK 3. Three dogs pulling three ways in the rain. 'they need you.' 31."),
    ("G4", 44.2, 47.8, "grind", "WEEK 5. The party he organised; everyone dances, he serves. 'Everyone loved him.' 48."),
    ("G5", 47.8, 51.2, "grind", "WEEK 6. Home late, the easel under a sheet, the calendar full of names. 'He was there for everyone.' 60."),
    ("G6", 51.2, 54.8, "grind", "WEEK 8. Phone: favours stacking up. 'don't be difficult.' 61-77."),
    ("G7", 54.8, 58.2, "grind", "WEEK 9. 1:40 am fixing a friend's laptop. 'Everyone except himself.' 95."),
    ("G8", 58.2, 64.0, "grind", "WEEK 11. Walking home in the rain inside a cage of strings. 'you owe them.' 112."),
    ("R1", 64.0, 70.0, "rock bottom", "Home, 11 pm. The strings tangle, he trips into the easel: it crashes, the paint spills."),
    ("R2", 70.0, 78.0, "rock bottom", "On the floor. 'can you do sunday too?' Villain leans down: 'they only like you for this.' 'sure.' 113. Caption."),
    ("T1", 78.0, 83.0, "turn", "He tugs the string on his wrist. It's slack. He follows it with his eyes to the window."),
    ("T2", 83.0, 90.0, "turn", "The string runs across the rooftops: Dan asleep on his sofa, the end lying loose on the floor. The office: it lies on an empty chair. 'Nobody was holding the strings.'"),
    ("T3", 90.0, 97.0, "turn", "He looks up: every string ends in the villain's fists. It flinches. 'Only his fear was.' Calendar of other people's names: 'Every yes to them was a no to him.'"),
    ("F1", 97.0, 108.0, "final fight", "Saturday morning. Easel up, brush in hand. Knock: 'hey! quick favour?' Phone: 'can you come in today?' Villain at full size hauls him toward the door."),
    ("F2", 108.0, 114.0, "final fight", "He plants his feet, eyes closed, against the pull. 'say yes.' Near-silence, heartbeat."),
    ("F3", 114.0, 117.4, "final fight", "'no.' The strings snap one by one, the villain cracks and bursts. SAID NO 1 in gold."),
    ("F4", 117.4, 121.0, "final fight", "Door: 'oh! no worries. another time?' Phone: 'ok! monday then.' He breathes out."),
    ("P1", 121.0, 129.0, "payoff", "He paints. The first colour in the film: a gold sunrise. 'Nobody left.'"),
    ("P2", 129.0, 136.0, "payoff", "Evening. Dan at the door with pizza: 'brought dinner. can i see?' They sit and look at it, laughing."),
    ("P3", 136.0, 140.0, "payoff", "Calendar: he writes ME in gold on Saturday."),
    ("X1", 140.0, 149.4, "mirror", "Monday, office. Ana has a string. Boss: 'can you stay late?' He: 'you can say no.' Ana: 'not tonight, sorry.' Boss: 'sure, no problem.' Her string falls."),
    ("TT", 149.4, 160.0, "title", "NO. 'Every yes to them was a no to you.' 'Say it.'"),
]

# captions: id -> (start, end)
CAPS = {
    "C1": (0.4, 2.9), "C2": (18.6, 21.8), "C3": (31.9, 34.4), "C4": (44.6, 47.5), "C5": (48.1, 51.0),
    "C6": (55.1, 58.0), "C7": (74.6, 77.8), "C8": (84.6, 88.6), "C9": (90.8, 93.4), "C10": (93.8, 96.8),
    "C11": (125.0, 128.4), "T1": (151.6, 159.6), "T2": (154.0, 159.6),
}

# villain whispers: id -> start second (lengths come from build/line_lengths.json)
CUES = {
    "V1": 25.2, "V2": 28.2, "V3": 41.7, "V4": 52.1, "V5": 61.0, "V6": 72.0,
    "V7": 103.8, "V8": 105.9, "V9": 107.8, "V10": 110.4,
}

# speech bubbles (silent): (start, end, who, text)
BUBBLES = [
    (3.25, 5.5, "boss", "can you stay late?"), (4.15, 5.5, "him", "sure!"),
    (5.85, 8.1, "neighbour", "just for the weekend?"), (6.75, 8.1, "him", "of course!"),
    (8.45, 10.7, "friend", "you'll plan the trip, right?"), (9.35, 10.7, "him", "yeah!"),
    (11.05, 13.3, "stranger", "you don't mind, right?"), (11.95, 13.3, "him", "no no, go ahead!"),
    (13.6, 15.5, "dan", "help me move?"), (14.35, 15.5, "him", "yes!"),
    (27.3, 31.4, "phone", "free saturday? need a favour"), (29.5, 31.4, "him", "yes!"),
    (38.1, 40.4, "ana", "how do you do it all?"), (39.3, 41.1, "him", "i love it!"),
    (70.7, 74.6, "phone", "can you do sunday too?"), (73.4, 75.6, "him", "sure."),
    (100.8, 103.6, "door", "hey! quick favour?"), (101.9, 104.4, "phone", "can you come in today?"),
    (114.0, 117.2, "him_big", "no."),
    (117.8, 120.7, "door", "oh! no worries. another time?"), (119.2, 120.9, "phone", "ok! monday then."),
    (130.0, 132.8, "dan", "brought dinner. can i see?"),
    (140.6, 142.9, "boss", "can you stay late?"), (143.0, 145.0, "him", "you can say no."),
    (145.2, 147.3, "ana", "not tonight, sorry."), (146.7, 148.8, "boss", "sure, no problem."),
]

# the SAID YES counter: (time it changes, new value)
YES = [(4.3, 1), (6.9, 2), (9.5, 3), (12.1, 4), (14.5, 5), (15.75, 6), (16.25, 7), (16.75, 8), (17.25, 9),
       (29.7, 10), (35.0, 14), (38.0, 22), (41.5, 31), (44.5, 48), (48.1, 60)] + \
      [(51.5 + k * 0.13, 61 + k) for k in range(17)] + [(55.1, 95), (58.5, 112), (73.6, 113)]

# picture events the sound must hit on the exact frame
EVENTS = {
    "yank": 23.0, "eyes_open": 24.4, "phone_buzz": 27.0, "strike": 30.4,
    "trip": 66.0, "crash": 66.3, "spill": 66.6, "sunday_buzz": 70.4,
    "tug": 79.6, "flinch": 91.4, "knock": 100.6, "work_buzz": 101.8,
    "eyes_closed": 109.5, "silence": (112.2, 114.0), "eyes_open2": 113.4, "no": 114.0,
    "snaps": [114.05 + k * 0.24 for k in range(10)], "burst": 115.0, "said_no": 114.2,
    "knock2": 129.3, "gold_me": 136.6, "ana_snap": 147.4, "title": 150.0,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def yes_at(t):
    v = 0
    for tm, val in YES:
        if t >= tm:
            v = val
    return v


def yes_changed(t):
    """Time of the most recent change, for the HUD pop."""
    last = None
    for tm, _ in YES:
        if t >= tm:
            last = tm
    return last
