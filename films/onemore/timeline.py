"""ONE MORE MATCH.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 165.0

SCENES = [
    ("S01", 0.0, 6.0, "hook", "11:02 PM, his desk, headset on, the monitor: VICTORY. The rank badge ticks SILVER III to SILVER II. 'It was always one more match.' (Opens on the picture.)"),
    ("H1", 6.0, 12.0, "hook", "The monitor close: PLAY AGAIN? He clicks. The clock jumps 11:40, 12:25, 1:10. TONIGHT: 2, 3, 4 MATCHES."),
    ("H2", 12.0, 19.0, "hook", "Mum at the door: 'beta, dinner's getting cold.' 'five minutes!' He doesn't turn. 'Five minutes always meant one more match.'"),
    ("S02", 19.0, 28.0, "wound", "1:40 AM. The villain rises out of the monitor's glow. 'one more match.' 'you're so close.'"),
    ("B1", 28.0, 34.0, "stakes", "Dev: 'final on saturday, 10am. we need our keeper' 'i'll be there.' 'practice tmrw 6pm'"),
    ("G1", 34.0, 54.0, "grind", "One locked shot, four nights (MON 1:12, TUE 2:40, WED 3:30, THU 4:05). The rank climbs to GOLD, then PLATINUM; the keeper gloves on the shelf go grey; missed practice texts. 'just till gold.' 'you'll lose your streak.'"),
    ("G2", 54.0, 61.0, "grind", "The pitch at dusk, practice. An empty goal. Dev: 'where's our keeper?' 'He was never AFK in the game.'"),
    ("G3", 61.0, 68.0, "grind", "6:05 AM, still playing. Dad passes the door in his work clothes: 'up already?' '...yeah.' 'He was AFK everywhere else.'"),
    ("R1", 68.0, 84.0, "rock bottom", "FRI 3:52 AM: PROMO MATCH, win 1 to reach DIAMOND. 'promo game. don't quit now.' VICTORY. DIAMOND! He jumps up, alone. Then SAT 11:48: 9 missed calls, Dev: 'we lost 2-1. no keeper.' 'He made Diamond the night they lost the final.'"),
    ("T1", 84.0, 94.0, "turn", "The monitor: SEASON 4 ENDS IN 3 DAYS. ALL RANKS WILL RESET. The diamond badge cracks and falls to UNRANKED. 'The rank reset every season.' 'The days he traded for it didn't.'"),
    ("L1", 94.0, 104.0, "lesson", "The lesson drawn: left, a staircase of badges he climbs that drops back to the bottom every season; right, a row of days that go grey one by one and stay grey."),
    ("I1", 104.0, 110.0, "practice", "INSTEAD OF ONE MORE: pick the number before you log in, log off on a win or a loss, plan one real thing for tomorrow."),
    ("F1", 110.0, 124.0, "final fight", "SEASON 5. A sticky note on the monitor: 2 MATCHES. Match 2: DEFEAT. The villain at full size: 'one more match.' 'you can't end on a loss.' 'one more.' PLAY AGAIN? glows. Silence. He clicks LOG OFF. The villain breaks; the screen goes dark."),
    ("F2", 124.0, 129.0, "final fight", "He sets the keeper gloves by the door. The phone: 6:30 PRACTICE."),
    ("P1", 129.0, 140.0, "payoff", "SATURDAY. The pitch in the morning sun, a real match. A shot; he leaps and catches it. Dev: 'SAVE!' The counter is relabelled REAL MATCHES 1, in gold. 'He still played some nights.' 'He just picked the number first.'"),
    ("VT", 140.0, 147.0, "viewer", "To the viewer: a sticky note, TONIGHT: __ MATCHES. 'Before you log in tonight, pick a number.' 'When you reach it, log off. Win or lose.'"),
    ("X1", 147.0, 156.0, "mirror", "The opening shot replayed: 11:02 PM, VICTORY, PLAY AGAIN? He clicks LOG OFF, takes off the headset and stretches."),
    ("TT", 156.0, 165.0, "title", "ONE MORE MATCH. 'The rank resets every season. The days don't.' 'Log off.'"),
]

CAPS = {
    "C1": (0.4, 5.7), "C2": (15.4, 18.8), "C3": (57.4, 60.8), "C4": (64.4, 67.8), "C5": (80.4, 83.8),
    "C6": (87.6, 93.8), "C7": (89.8, 93.8), "C8": (95.0, 103.8), "C9": (98.0, 103.8),
    "C10": (135.8, 139.8), "C11": (137.2, 139.8),
    "V1": (140.4, 143.6), "V2": (143.8, 146.8),
    "T1": (157.6, 164.6), "T2": (160.0, 164.6),
}

CUES = {"V1": 21.6, "V2": 24.2, "V3": 37.0, "V4": 46.6, "V5": 50.6, "V6": 69.0, "V7": 114.0, "V8": 116.0, "V9": 118.6}

BUBBLES = [
    (13.0, 14.8, "mum", "beta, dinner's getting cold."),
    (15.0, 16.2, "him", "five minutes!"),
    (55.0, 56.8, "dev", "where's our keeper?"),
    (62.0, 63.2, "dad", "up already?"),
    (63.4, 64.4, "him", "...yeah."),
    (132.6, 134.2, "dev", "SAVE!"),
]

# the locked shot: four nights
G1_T0, G1_NIGHT = 34.0, 5.0
G1_DAYS = ["MON", "TUE", "WED", "THU"]
G1_CLOCKS = ["1:12", "2:40", "3:30", "4:05"]

# the rank, as the badge shows it: (time, tier)
RANKS = [(0.0, "SILVER III"), (3.0, "SILVER II"), (8.4, "SILVER I"), (G1_T0 + 2.8, "GOLD III"), (G1_T0 + 7.8, "GOLD I"),
         (G1_T0 + 12.8, "PLATINUM III"), (G1_T0 + 17.8, "PLATINUM I"), (72.4, "DIAMOND"), (90.0, "UNRANKED")]
# matches tonight: (time, n). A new night starts back at 1.
TONIGHT = [(0.0, 1), (7.0, 2), (8.4, 3), (9.8, 4), (G1_T0, 6), (G1_T0 + 5, 7), (G1_T0 + 10, 8), (G1_T0 + 15, 9),
           (68.0, 11), (110.0, 1), (111.0, 2)]
RELABEL = 133.0  # REAL MATCHES 1, in gold

EVENTS = {
    "victory0": 1.4, "badge0": 3.0, "clicks": [7.0, 8.4, 9.8], "knock": 12.4, "born": (19.8, 21.4),
    "dev_text": 28.4, "his_text": 30.0, "dev_text2": 31.6,
    "promo_win": 72.0, "jump": 72.6, "phone": 76.0, "missed": 76.4, "dev_lost": 77.4,
    "season": 84.6, "crack": 88.0, "reset": 90.0, "lesson": 94.4, "card": 104.2,
    "defeat": 111.0, "rise": (112.4, 114.0), "silence": (119.8, 121.0), "logoff": 121.0, "crumble": 121.2,
    "gloves": 125.0, "alarm": 126.6, "shot": 130.4, "catch": 131.6, "whistle": 129.4,
    "x_victory": 148.0, "x_logoff": 151.2, "title": 156.4,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def _last(seq, t, default):
    v = default
    for tm, x in seq:
        if t >= tm:
            v = x
    return v


def rank_at(t):
    return _last(RANKS, t, "SILVER III")


def tonight_at(t):
    return _last(TONIGHT, t, 1)


def hud_changed(t):
    last = None
    for tm, _ in RANKS + TONIGHT:
        if 0 < tm <= t:
            last = tm if last is None else max(last, tm)
    return last
