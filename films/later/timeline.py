"""LATER.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 180.0

SCENES = [
    ("S01", 0.0, 3.0, "hook", "Black. 'His dad called every Sunday.'"),
    ("H1", 3.0, 6.5, "hook", "SUN 10:00. His desk. The phone lights up: DAD. He declines."),
    ("H2", 6.5, 9.0, "hook", "The jar on his shelf: one marble lifts out and falls. SUNDAYS LEFT 780 -> 779."),
    ("H3", 9.0, 11.0, "hook", "Next Sunday, the gym. DAD. Decline. 778."),
    ("H4", 11.0, 13.0, "hook", "Next Sunday, the sofa, a game on. DAD. Decline. 777."),
    ("H5", 13.0, 15.0, "hook", "Next Sunday, brunch with friends. DAD. Decline. 776."),
    ("M1", 15.0, 24.0, "hook", "Night. He looks at the jar. The sum appears: Dad is 71. Maybe 15 more years. 15 x 52 = 780 Sundays. 'It sounded like a lot.'"),
    ("H6", 24.0, 30.5, "wound", "Sunday. DAD calling. His thumb hovers. The villain rises out of the laptop's glow: 'later.' Decline. Clink. 775."),
    ("S04", 30.5, 33.5, "wound", "Black. 'He thought there was plenty of time.'"),
    ("D1", 33.5, 40.0, "stakes", "Dad's kitchen. Two plates on the table, the phone to his ear. It rings out. He puts the second plate back."),
    ("D2", 40.0, 46.0, "stakes", "Phone: Dad: 'no worries son! next week then :)' Him: 'next week for sure!' 'he understands.'"),
    ("G1", 46.0, 49.5, "grind", "YEAR 1. Office. Maya at the next desk declines MUM too. 760."),
    ("G2", 49.5, 53.0, "grind", "The jar at night, marbles falling one after another. 'you're busy.' 725."),
    ("G3", 53.0, 56.5, "grind", "YEAR 2. A party. Phone face down: missed call, Dad. 690."),
    ("G4", 56.5, 60.0, "grind", "Autumn through his window, laptop on a Sunday. 'Next week became next month.' 650."),
    ("G5", 60.0, 63.5, "grind", "YEAR 3. Dad: 'merry christmas son. proud of you.' Him: 'thx dad u too'. 'next month.' 620."),
    ("G6", 63.5, 67.0, "grind", "YEAR 4. A new flat, boxes. The jar, lower. 'Next month became next year.' 570."),
    ("G7", 67.0, 70.5, "grind", "YEAR 5. Dad eats alone, one plate, the dog old and grey. 530."),
    ("G8", 70.5, 76.0, "grind", "YEAR 6. His desk, Sunday 10:00. Nothing rings."),
    ("R1", 76.0, 82.0, "rock bottom", "10:01. Dad: 'i'll stop calling on sundays. i know you're busy. love you son.'"),
    ("R2", 82.0, 92.0, "rock bottom", "On the floor below the shelf. 'see? he doesn't mind.' The marbles keep falling. 470."),
    ("T1", 92.0, 100.0, "turn", "He takes the jar down and cups his hands over it. They slip through his fingers anyway. 'He couldn't stop them falling.'"),
    ("T2", 100.0, 106.0, "turn", "One marble in his palm. Inside it, a memory: fishing with Dad. 'He could only choose what they were for.'"),
    ("T3", 106.0, 112.0, "turn", "An empty jar. He writes on its label: WITH DAD."),
    ("F1", 112.0, 124.0, "final fight", "Sunday, 9:50. URGENT email. 'brunch? 11?' The villain at full size: 'later.' 'you're too busy.' 'it'll be awkward now.' 'he stopped calling for a reason.'"),
    ("F2", 124.0, 130.0, "final fight", "His hand on the laptop. 'later.' Eyes closed. Near-silence, heartbeat."),
    ("F3", 130.0, 133.0, "final fight", "He slams the laptop shut. The villain cracks and bursts. He grabs his coat."),
    ("F4", 133.0, 142.0, "final fight", "Morning street, walking fast. Dad's door. A knock. Silence. The door opens."),
    ("P1", 142.0, 150.0, "payoff", "Dad: 'son?' The dog jumps. 'come in, come in!'"),
    ("P2", 150.0, 157.0, "payoff", "The kitchen turns warm. Dad takes the second plate back out. They cook, laughing."),
    ("P3", 157.0, 163.0, "payoff", "His shelf that night: this Sunday's marble falls gold, into the WITH DAD jar. 'This one counted.'"),
    ("X1", 163.0, 171.0, "mirror", "Monday. Maya's phone: MUM calling. Her thumb on decline. He sets a marble on her desk. She answers: 'hi mum!'"),
    ("TT", 171.0, 180.0, "title", "LATER. 'You have fewer Sundays than you think.' 'Go now.'"),
]

CAPS = {
    "C1": (0.4, 2.9), "C2": (21.6, 24.0), "C3": (30.8, 33.4), "C4": (56.8, 59.8), "C5": (63.8, 66.8),
    "C6": (87.6, 91.6), "C7": (95.0, 98.4), "C8": (101.0, 105.6), "C9": (159.8, 162.8),
    "T1": (173.0, 179.6), "T2": (175.4, 179.6),
}

CUES = {
    "V1": 26.2, "V2": 44.6, "V3": 50.4, "V4": 61.8, "V5": 84.4,
    "V6": 116.4, "V7": 118.2, "V8": 120.2, "V9": 122.4, "V10": 126.4,
}

BUBBLES = [
    (141.0, 143.6, "dad", "son?"), (144.2, 147.0, "dad", "come in, come in!"),
    (153.0, 155.6, "dad", "still burn the eggs?"), (154.6, 156.8, "him", "every time."),
    (167.6, 170.6, "maya", "hi mum!"),
]

# SUNDAYS LEFT counter: (time it changes, new value)
LEFT = [(6.8, 780), (7.7, 779), (10.0, 778), (12.0, 777), (14.0, 776), (28.4, 775), (47.0, 760)] + \
       [(50.0 + k * 0.1, 759 - k) for k in range(35)] + \
       [(54.0, 690), (57.4, 650), (61.0, 620), (64.4, 570), (68.0, 530), (71.0, 472)] + \
       [(85.0 + k * 1.2, 471 - k) for k in range(5)] + [(96.4, 465), (98.0, 464), (112.4, 463), (159.0, 462)]

EVENTS = {
    "ring1": 3.4, "decline1": 4.6, "drop1": 7.0,
    "ring6": 24.4, "decline6": 27.8, "drop6": 28.1,
    "dad_ring": 34.2, "plate_back": 37.6,
    "silent_ten": 71.0, "dad_text": 78.4,
    "slip": [96.0, 97.6], "write": 108.0,
    "email": 113.4, "brunch": 115.0, "eyes_closed": 127.4, "silence": (128.2, 130.0), "eyes_open": 129.4,
    "slam": 130.0, "burst": 131.0, "coat": 131.8,
    "knock": 138.6, "door_open": 140.6, "dog_jump": 142.6, "plate_out": 151.4, "gold_drop": 159.0,
    "maya_ring": 163.6, "marble_set": 165.4, "maya_answer": 167.4, "title": 172.0,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def left_at(t):
    v = None
    for tm, val in LEFT:
        if t >= tm:
            v = val
    return v


def left_changed(t):
    last = None
    for tm, _ in LEFT:
        if t >= tm:
            last = tm
    return last
