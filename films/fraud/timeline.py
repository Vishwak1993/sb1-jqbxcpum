"""FRAUD.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 168.0

SCENES = [
    ("S01", 0.0, 3.5, "hook", "The phone: 'Congratulations! You got the job.' 'He got the job.'"),
    ("H1", 3.5, 7.5, "hook", "His room, morning: he jumps for joy, then freezes. 'He was sure it was a mistake.'"),
    ("H2", 7.5, 14.0, "hook", "First day, the lobby mirror. He pins on his badge; in the mirror it flickers red: FRAUD. The villain rises from its glow: 'they'll find out.' REVIEW IN 90 DAYS."),
    ("H3", 14.0, 19.0, "hook", "The office. The boss: 'we're lucky to have you!' 'you got lucky.' He covers the badge with his hand."),
    ("H4", 19.0, 24.0, "hook", "A meeting. A lightbulb on his notepad. He opens his mouth: 'don't. they'll see.' He closes it."),
    ("H5", 24.0, 30.0, "hook", "11:40 PM at his desk, over-preparing. 'everyone else knows what they're doing.' 'Every day, he waited to be found out.'"),
    ("G1", 30.0, 36.0, "grind", "WEEK 3. 'any questions?' 'no, all good!' Then, hiding his screen: 'what is a pivot table'. 'don't ask. they'll know.'"),
    ("G2", 36.0, 42.0, "grind", "WEEK 5. The boss: 'great report!' He shrugs it off. 'Every compliment was a mistake they hadn't noticed yet.'"),
    ("G3", 42.0, 48.0, "grind", "WEEK 8. 1:12 AM, a red #REF! on his screen. 'this is it.' He fixes it in secret."),
    ("G4", 48.0, 56.0, "grind", "WEEK 10. Mira presents his idea, the same lightbulb. Applause. 'it was a stupid idea anyway.' 'He hadn't said a word in ten weeks.'"),
    ("G5", 56.0, 64.0, "grind", "WEEK 12, at home: he types a resignation letter. 'He would leave before they found out.' REVIEW IN 1 DAY."),
    ("R1", 64.0, 72.0, "rock bottom", "Review day. The lobby, the envelope in his hand, into the lift with the others."),
    ("T1", 72.0, 84.0, "turn", "The lift lights flicker: every badge flickers FRAUD. 'Every badge in the lift said the same thing.' 'Nobody had told anyone.'"),
    ("T2", 84.0, 96.0, "turn", "The lesson drawn: WHAT HE THOUGHT (every eye on him) and WHAT WAS TRUE (every eye on itself). 'Nobody was watching him.' 'They were all watching themselves.'"),
    ("F1", 96.0, 110.0, "final fight", "The review. 'so. ninety days.' The villain: 'they know.' 'give them the letter.' 'get out first.' He puts the envelope down. 'can I be honest?' 'I've felt like a fraud since day one.'"),
    ("F2", 110.0, 116.0, "final fight", "Near-silence. The boss: 'me too.' 'eleven years now.' Her badge flickers FRAUD. The villain crumbles."),
    ("F3", 116.0, 122.0, "final fight", "She slides the envelope back. He tears it up. REVIEW: PASSED, in gold."),
    ("P1", 122.0, 134.0, "payoff", "The meeting again: 'I had an idea.' Then: 'what's a pivot table?' Mira: 'honestly? I still google it.'"),
    ("P2", 134.0, 140.0, "payoff", "Evening, the office window gold. 'He still felt it some days.' 'He went anyway.'"),
    ("VT", 140.0, 149.0, "viewer", "To the viewer: a badge. 'Think of the room where you feel like a fraud.' 'Everyone in it feels it too.' FRAUD fades."),
    ("X1", 149.0, 158.0, "mirror", "The opening shot again: the lobby mirror. FRAUD flickers faintly. He smiles at it and walks to the lift."),
    ("TT", 158.0, 168.0, "title", "FRAUD. 'Everyone in the room thinks they're the only one.' 'Go anyway.'"),
]

CAPS = {
    "C1": (0.5, 3.4), "C2": (5.2, 7.4), "C3": (26.6, 29.8), "C4": (38.4, 41.8), "C5": (53.0, 55.8), "C6": (59.0, 63.6),
    "C7": (78.9, 83.8), "C8": (80.6, 83.8), "C9": (90.0, 95.8), "C10": (92.0, 95.8), "C11": (134.4, 139.8), "C12": (136.6, 139.8),
    "V1": (140.6, 144.4), "V2": (144.8, 148.6),
    "T1": (159.6, 167.6), "T2": (162.0, 167.6),
}

CUES = {
    "V1": 11.8, "V2": 16.6, "V3": 21.0, "V4": 24.8, "V5": 34.2, "V6": 44.0, "V7": 51.4,
    "V8": 99.2, "V9": 101.2, "V10": 103.4,
}

BUBBLES = [
    (14.4, 16.4, "boss", "we're lucky to have you!"),
    (30.4, 32.2, "colleague", "any questions?"),
    (31.8, 33.4, "him", "no, all good!"),
    (36.4, 38.2, "boss", "great report!"),
    (96.6, 98.6, "boss", "so. ninety days."),
    (106.0, 107.8, "him", "can I be honest?"),
    (107.8, 110.4, "him", "I've felt like a fraud since day one."),
    (111.6, 113.2, "boss", "me too."),
    (113.2, 115.8, "boss", "eleven years now."),
    (123.4, 125.4, "him", "I had an idea."),
    (127.6, 129.6, "him", "what's a pivot table?"),
    (129.8, 132.6, "mira", "honestly? I still google it."),
]

# REVIEW IN n DAYS: (time it changes, text)
REVIEW = [(9.6, "90 DAYS"), (24.0, "88 DAYS"), (30.0, "72 DAYS"), (36.0, "58 DAYS"), (42.0, "37 DAYS"), (48.0, "20 DAYS"),
          (56.0, "1 DAY"), (64.0, "TODAY"), (119.0, "PASSED")]

EVENTS = {
    "email": 0.6, "jump": 4.0, "freeze": 5.0, "pin": 8.4, "flicker": 9.6, "born": (10.2, 11.6),
    "cover": 17.2, "open_mouth": 20.6, "close_mouth": 21.6, "search": 33.6, "error": 43.4, "fixed": 46.4,
    "applause": 50.2, "letter": 57.0, "lift_in": 68.4, "lift_flicker": 74.4, "lift_back": 78.6,
    "thought": 84.4, "true": 88.4, "rise": 97.4, "envelope_up": 104.0, "envelope_down": 105.6,
    "silence": (110.0, 111.6), "boss_badge": 112.4, "crumble": 113.8, "slide": 116.8, "tear": 118.4, "passed": 119.0,
    "hand_up": 123.0, "laugh": 132.0, "badge_fade": 145.6, "mirror_flicker": 151.4, "walk": 153.4, "title": 159.0,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def review_at(t):
    out = None
    for tm, txt in REVIEW:
        if t >= tm:
            out = txt
    return out


def review_changed(t):
    last = None
    for tm, _ in REVIEW:
        if t >= tm:
            last = tm
    return last
