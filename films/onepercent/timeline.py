"""1%.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 176.0

SCENES = [
    ("S01", 0.0, 3.0, "hook", "Black. 'He never stopped.'"),
    ("H1", 3.0, 6.0, "hook", "Mon 6:00. The alarm. He springs out of bed. BATTERY 100%."),
    ("H2", 6.0, 8.6, "hook", "His desk: INBOX 48. Typing fast. 88%."),
    ("H3", 8.6, 11.2, "hook", "A meeting: two people talking at him at once. 76%."),
    ("H4", 11.2, 13.8, "hook", "Lunch at his desk, a call on his shoulder. 64%."),
    ("H5", 13.8, 17.0, "hook", "Night. The laptop glow; the villain is born from it: 'push through.' 41%."),
    ("H6", 17.0, 24.0, "hook", "He plugs his phone in to charge: 100%. He is at 41%. 'He charged his phone every night.'"),
    ("H7", 24.0, 27.0, "hook", "Black. 'Never himself.'"),
    ("B1", 27.0, 36.0, "stakes", "His little brother Theo at the door with a paper star: 'my play! friday!' 'wouldn't miss it.'"),
    ("G1", 36.0, 39.5, "grind", "WEEK 1. The alarm: he wakes at 80%. Coffee cups: 1, 2, 3."),
    ("G2", 39.5, 43.0, "grind", "WEEK 2. The train, laptop on his knees, eyes closing. 'everyone else is working.' 66%."),
    ("G3", 43.0, 46.5, "grind", "WEEK 3. The office at night, the last one there, the cleaner passing. 'you'll fall behind.' 52%."),
    ("G4", 46.5, 50.0, "grind", "WEEK 4. Phone: Theo: 'rehearsal went great!!' Read. 44%."),
    ("G5", 50.0, 53.5, "grind", "WEEK 5. He lies on the sofa; his foot jiggles; he grabs the laptop. 'rest is for the lazy.' 33%."),
    ("G6", 53.5, 57.0, "grind", "WEEK 6. The bathroom mirror: grey, bags under his eyes. 'He thought tired meant trying.' 21%."),
    ("G7", 57.0, 61.0, "grind", "FRIDAY 18:30. Theo: 'it starts at 7!' He types 'on my way' and keeps working. 9%."),
    ("R1", 61.0, 68.0, "rock bottom", "19:40. Asleep on the keyboard. The mug tips and spills. 1%, red, blinking."),
    ("R2", 68.0, 76.0, "rock bottom", "21:15. Phone: Theo: 'you weren't there' 'its ok'. 'you'll make the next one.' 'He ran out before he got there.'"),
    ("T1", 76.0, 84.0, "turn", "His phone: 'Battery low. Plug in to charge.' He looks at the charger, at the laptop on its cable, then at himself. 'He plugged in everything he owned.' 'Except himself.'"),
    ("T2", 84.0, 93.0, "turn", "The lesson drawn: a battery. In: SLEEP, A WALK, PEOPLE, DOING NOTHING. Out: WORK, WORRY, ONE MORE HOUR. 'Rest wasn't the opposite of work.' 'It was what work ran on.'"),
    ("T3", 93.0, 99.0, "turn", "He sleeps. The moon crosses the window; the battery climbs 1 to 30."),
    ("C1", 99.0, 102.0, "practice", "A walk in the park, warm light. 45%."),
    ("C2", 102.0, 105.0, "practice", "Lunch away from his desk, laughing with a colleague. 58%."),
    ("C3", 105.0, 108.0, "practice", "Phone in the drawer, a book on the sofa. 70%."),
    ("F1", 108.0, 119.0, "final fight", "Thursday night, a big deadline. Emails flood in, the villain at full size. 72 to 50%."),
    ("F2", 119.0, 124.0, "final fight", "His hand on the laptop. 'push through.' Eyes closed. Near-silence, heartbeat."),
    ("F3", 124.0, 127.0, "final fight", "He shuts the laptop and switches off the lamp. Click. Dark. The villain, made of screen light, dissolves."),
    ("V1", 127.0, 138.0, "viewer", "To the viewer: 'Your turn.' 'Drop your shoulders.' A breathing ring grows and shrinks. 'Breathe out.'"),
    ("P1", 138.0, 145.0, "payoff", "Saturday morning, sunlight. He wakes at 100%, in gold."),
    ("P2", 145.0, 154.0, "payoff", "The school hall. Theo on stage as a star sees him in the front row and waves. He waves back."),
    ("X1", 154.0, 163.0, "mirror", "Night. Theo at his homework, yawning, a tiny battery at 12%, a red whisper. He closes the book, switches off the lamp. Theo smiles."),
    ("TT", 163.0, 172.5, "title", "1%. 'You charge everything except yourself.' 'Rest.'"),
    ("ST", 172.5, 176.0, "stinger", "Black. Monday 6:00. 'push through.'"),
]

CAPS = {
    "C1": (0.4, 2.9), "C2": (18.0, 23.8), "C3": (24.3, 26.9), "C4": (54.0, 56.9), "C5": (72.4, 75.8),
    "C6": (79.0, 83.8), "C7": (81.6, 83.8), "C8": (87.4, 92.8), "C9": (89.6, 92.8),
    "V1": (127.6, 130.4), "V2": (130.4, 133.4), "V3": (133.6, 137.6),
    "T1": (164.6, 172.2), "T2": (167.0, 172.2),
}

CUES = {
    "V1": 15.0, "V2": 40.4, "V3": 44.0, "V4": 51.2, "V5": 70.6,
    "V6": 111.0, "V7": 112.6, "V8": 114.6, "V9": 116.4, "V10": 121.0, "V11": 174.0,
}

BUBBLES = [
    (28.6, 32.2, "theo", "my play! friday!"), (32.0, 35.6, "him", "wouldn't miss it."),
    (9.0, 11.0, "m1", "need this by noon"), (9.4, 11.0, "m2", "and this!"),
    (11.6, 13.6, "him", "yep, on it"),
    (102.8, 104.8, "colleague", "you look different!"),
    (148.2, 151.0, "theo", "you came!"),
]

# his BATTERY: (time, value, how it gets there: "step" or "ramp" from the previous key)
BAT = [(3.4, 100, "step"), (6.6, 88, "step"), (9.2, 76, "step"), (11.8, 64, "step"), (14.4, 52, "step"), (16.2, 41, "step"),
       (37.0, 80, "step"), (38.6, 76, "step"), (41.0, 66, "step"), (44.6, 52, "step"), (47.8, 44, "step"), (52.0, 33, "step"),
       (55.0, 21, "step"), (58.6, 9, "step"), (63.0, 1, "ramp"),
       (95.0, 1, "step"), (98.4, 30, "ramp"), (100.0, 45, "step"), (103.0, 58, "step"), (106.0, 70, "step"),
       (108.4, 72, "step"), (112.0, 64, "step"), (114.0, 58, "step"), (116.0, 54, "step"), (118.0, 50, "step"), (138.8, 50, "step"),
       (140.6, 100, "ramp")]

EVENTS = {
    "alarm1": 3.4, "spring": 4.0, "plug": 19.4, "villain_born": (14.2, 16.0),
    "door_knock": 27.4, "alarm2": 36.4, "spill": 64.6, "low_beep": [63.4, 65.4, 67.4],
    "theo_text1": 69.0, "theo_text2": 71.2, "lowbat_popup": 77.0,
    "email_flood": (108.6, 112.0), "eyes_closed": 121.6, "silence": (122.4, 124.0), "eyes_open": 123.6,
    "shut": 124.0, "lamp_off": 124.5, "breath": (130.6, 137.4),
    "wake": 139.0, "wave": 149.6, "theo_lamp": 160.0, "title": 164.0, "alarm3": 173.2,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def bat_at(t):
    v, pt = None, None
    for tm, val, mode in BAT:
        if mode == "ramp" and pt is not None and pt <= t < tm:
            return v + (val - v) * (t - pt) / (tm - pt)
        if t >= tm:
            v, pt = val, tm
        else:
            break
    return v


def bat_changed(t):
    last = None
    for tm, _, mode in BAT:
        if t >= tm and mode == "step":
            last = tm
    return last
