"""FINE.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 175.0

SCENES = [
    ("S01", 0.0, 5.5, "hook", "The hallway, morning. A smiling mask on the hook by the door. His real face, tired. The mask snaps onto his face. 'He told everyone he was fine.'"),
    ("H1", 5.5, 9.5, "hook", "The corner shop. 'how are you?' 'fine, thanks!' SAID FINE 1."),
    ("H2", 9.5, 13.5, "hook", "The street, Mum on the phone. 'how are you, love?' 'fine, mum! all good.' 2."),
    ("H3", 13.5, 19.0, "hook", "Five-a-side at dusk. Jo: 'you good, mate?' 'fine!' 3. 'It was easier than the truth.'"),
    ("S02", 19.0, 29.0, "wound", "Night, the hallway. The mask comes off onto the hook: under it, his real face. The villain grows out of the mask's grin. 'say you're fine.' 'nobody wants to hear it.'"),
    ("B1", 29.0, 34.5, "stakes", "Jo: 'halloween at mine, sat 31st. costumes compulsory' 'you alright? you've been quiet' 'all good! can't wait'"),
    ("G1", 34.5, 46.5, "grind", "One locked shot of the hallway, five days: mask off at night, on in the morning. SAID FINE climbs to 167, a strap appears, his face gets worse. 'don't be a burden.'"),
    ("G2", 46.5, 53.5, "grind", "The pitch at night. Jo: 'you sure you're ok?' 'fine! honestly.' Jo jogs off. 'And everyone believed him.'"),
    ("G3", 53.5, 60.5, "grind", "The kitchen at 4:40. A full plate, the mask on the table. 'they have their own problems.' 'He wasn't fine. He hadn't been for months.'"),
    ("R1", 60.5, 69.0, "rock bottom", "OCT 30, night, the hook. He pulls at the mask; it won't come off. 'keep it in.' 'One night, it wouldn't come off.' 'now they'll never know.'"),
    ("T1", 69.0, 77.5, "party", "OCT 31, Jo's door, warm light, costumes. 'where's your costume?' '...this is it.' 'ha! creepy.' 'His was the only mask that wasn't a costume.'"),
    ("T2", 77.5, 84.0, "party", "Midnight. 'MASKS OFF!' Everyone pulls theirs off, laughing. His won't move. He slips out the back."),
    ("T3", 84.0, 109.0, "turn", "The back step. Jo sits down. 'you ok?' 'fine.' 212. Jo stays. 'no. how are you really?' 'Nobody had ever asked twice.' The villain: 'say you're fine.' 'just say fine.' Silence. '...not great, actually.' The mask cracks gold. 'i haven't been for a while.' It falls. 'thanks for telling me.'"),
    ("L1", 109.0, 118.0, "lesson", "The lesson drawn: the mask from the side. The hurt bounces back in; every 'you ok?' bounces off. 'The mask kept the hurt in.' 'And it kept everyone out.'"),
    ("I1", 118.0, 124.0, "practice", "INSTEAD OF 'FINE': pick one person, say one true sentence, let them help."),
    ("F1", 124.0, 135.0, "final fight", "MONDAY, the hallway. Mum calls: 'how are you, love?' The villain holds out a new mask: 'just say fine.' 'honestly, mum? it's been a hard few months.' 'oh, love. i'm here. tell me.'"),
    ("P1", 135.0, 144.0, "payoff", "NOVEMBER. The pitch at golden dusk, no mask. 'how's your week been?' 'rough. better now.' Laughter. 'He still had bad days.' 'Now someone knew about them.'"),
    ("VT", 144.0, 150.5, "viewer", "To the viewer: a mask on black. 'Next time someone asks how you are,' 'tell them one true thing.' It cracks into gold light."),
    ("X1", 150.5, 161.0, "mirror", "The opening hallway: the mask, mended with gold, stays on the hook. The shop: 'how are you?' 'tired, honestly. you?' '...fine.' '...really?' The shopkeeper's mask cracks."),
    ("TT", 161.0, 170.0, "title", "FINE. 'Everyone says they're fine.' 'Ask twice.'"),
    ("HL", 170.0, 175.0, "helpline", "Not fine? You don't have to carry it alone. findahelpline.com"),
]

CAPS = {
    "C1": (0.5, 5.3), "C2": (16.6, 18.8), "C3": (20.2, 23.6), "C4": (50.6, 53.3), "C5": (57.0, 60.3),
    "C6": (63.0, 66.4), "C7": (74.4, 77.4), "C8": (93.6, 97.4), "C9": (110.0, 117.6), "C10": (112.6, 117.6),
    "C11": (138.8, 143.6), "C12": (140.6, 143.6),
    "V1": (144.4, 147.6), "V2": (147.6, 150.3),
    "T1": (162.6, 169.6), "T2": (165.0, 169.6),
    "H1": (170.4, 174.6), "H2": (171.4, 174.6),
}

CUES = {"V1": 24.9, "V2": 26.4, "V3": 40.0, "V4": 54.2, "V5": 61.2, "V6": 66.6,
        "V7": 95.6, "V8": 97.6, "V9": 127.6}

BUBBLES = [
    (5.8, 7.0, "shop", "how are you?"),
    (7.3, 9.0, "him", "fine, thanks!"),
    (9.8, 11.2, "mum", "how are you, love?"),
    (11.5, 13.2, "him", "fine, mum! all good."),
    (13.8, 15.2, "jo", "you good, mate?"),
    (15.5, 16.8, "him", "fine!"),
    (47.0, 48.6, "jo", "you sure you're ok?"),
    (48.9, 50.4, "him", "fine! honestly."),
    (70.4, 72.0, "jo", "where's your costume?"),
    (72.4, 74.0, "him", "...this is it."),
    (74.2, 75.4, "jo", "ha! creepy."),
    (77.9, 79.2, "guest", "MASKS OFF!"),
    (87.0, 88.2, "jo", "you ok?"),
    (88.6, 89.6, "him", "fine."),
    (91.2, 93.4, "jo", "no. how are you really?"),
    (100.8, 102.8, "him", "...not great, actually."),
    (103.0, 105.0, "him", "i haven't been for a while."),
    (105.6, 107.4, "jo", "thanks for telling me."),
    (125.8, 127.4, "mum", "how are you, love?"),
    (130.2, 132.6, "him", "honestly, mum? it's been a hard few months."),
    (132.8, 134.6, "mum", "oh, love. i'm here. tell me."),
    (135.4, 136.8, "jo", "how's your week been?"),
    (137.0, 138.6, "him", "rough. better now."),
    (153.9, 155.0, "shop", "how are you?"),
    (155.3, 157.0, "him", "tired, honestly. you?"),
    (157.3, 158.3, "shop", "...fine."),
    (158.6, 159.8, "him", "...really?"),
]

# the locked shot: five days, each a night (mask off) then a morning (mask on)
G1_T0, G1_DAY = 34.5, 2.4
G1_DATES = ["OCT 6", "OCT 11", "OCT 16", "OCT 21", "OCT 26"]
G1_COUNTS = [31, 66, 98, 133, 167]

FINES = [(7.4, 1), (11.6, 2), (15.6, 3), (32.5, 4)] + \
    [(G1_T0 + i * G1_DAY + 1.6, v) for i, v in enumerate(G1_COUNTS)] + \
    [(49.0, 168), (60.5, 211), (88.7, 212)]
RELABEL = 101.6
TRUES = [(RELABEL, 1), (130.4, 2), (135.0, 9)]

EVENTS = {
    "mask_on": 2.6, "door": 4.2, "mask_off": 19.6, "born": (23.4, 25.0), "jo_text": 29.4, "jo_text2": 30.9, "his_reply": 32.4,
    "jo_off": 50.6, "pull": (61.8, 66.2), "jo_door": 69.6, "point": 72.4, "masks_off": 79.4, "his_pull": (80.0, 81.6),
    "leave": 81.8, "back_door": 85.0, "jo_sits": 86.6, "rise": (94.0, 95.6), "silence": (99.3, 100.8),
    "crack1": 101.2, "crack2": 103.4, "fall": 105.0, "tear": 105.4, "arm": 106.0,
    "inside": 109.4, "outside": 112.4, "card": 118.2, "ring": 124.6, "answer": 125.4, "offer": (127.6, 129.0),
    "drop": 130.6, "laugh": 138.8, "viewer_crack": 147.6, "walk_past": 150.8, "shop_mask": 157.3, "shop_crack": 159.8,
    "title": 161.4,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def fine_count(t):
    v = 0
    for tm, n in FINES:
        if t >= tm:
            v = n
    return v


def true_count(t):
    v = 0
    for tm, n in TRUES:
        if t >= tm:
            v = n
    return v


def count_changed(t):
    """Time of the last change of the shown number (for the pop)."""
    last = None
    for tm, _ in FINES + TRUES:
        if t >= tm:
            last = tm if last is None else max(last, tm)
    return last
