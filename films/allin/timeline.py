"""ALL IN.: the one place where every time lives. Picture and sound both read this file."""

DURATION = 182.0

SCENES = [
    ("S01", 0.0, 6.0, "hook", "His room at night, the match on TV, the phone in his hand: BET ₹500. 'It started with ₹500.' (No black opening: the first frame is the picture.)"),
    ("H1", 6.0, 12.0, "hook", "The app: NEXT BALL: SIX? x3.6. SIX! YOU WON ₹1,800, coins. WINNINGS +₹1,300."),
    ("H2", 12.0, 18.0, "hook", "He jumps up in front of the TV. 'He knew cricket. He thought that was enough.'"),
    ("H3", 18.0, 25.0, "hook", "The next night: BET ₹2,000. LOST. The counter flips: WINNINGS becomes TO GET EVEN ₹700."),
    ("S02", 25.0, 34.0, "wound", "The villain rises out of the phone's glow. 'win it back.' 'you know this game.'"),
    ("B1", 34.0, 40.0, "stakes", "Kabir: 'goa in december!! ₹12k each by the 30th' 'in. got it saved.' 'LETS GO'"),
    ("G1", 40.0, 58.0, "grind", "MATCH 6, MATCH 11, MATCH 19: bigger bets, LOST, LOST, LOST. TO GET EVEN 3,200, 8,900, 15,400. 'you were so close.' 'this one's sure.' 'double it.'"),
    ("G2", 58.0, 65.0, "grind", "Sunday, curtains shut. Kabir: 'cricket today? we're one short' 'can't. busy.' 'He stopped playing cricket. He only watched the odds.'"),
    ("G3", 65.0, 72.0, "grind", "3:52 AM, his face lit by the phone. 'just till you're even.' 'Every loss was a reason to bet again.'"),
    ("R1", 72.0, 94.0, "rock bottom", "The Goa money goes in, ₹12,000 on one ball: LOST. Kabir: 'bro goa money? deadline tonight' 'can you lend me 10k? i'll pay you back friday' 'sent. no rush bro'. LOST again: ₹37,400. 'He bet his best friend's money too.'"),
    ("T1", 94.0, 104.0, "turn", "The app: CONGRATULATIONS! You're now a VIP. MY ACCOUNT: DEPOSITED ₹52,600, WON BACK ₹15,200. 'The app called him a VIP.' 'He was its best customer.'"),
    ("L1", 104.0, 114.0, "lesson", "The lesson drawn: a pitch; he runs for the stumps marked EVEN; every time he gets close they slide away. 'Every bet promised he'd get even.' 'The target moved every time.'"),
    ("F1", 114.0, 130.0, "final fight", "Kabir at the door: 'you've gone quiet. what's going on?' LAST BALL! BET NOW x5. The villain at full size: 'one last bet.' 'win it all back.' Silence. 'i lost it. all of it. your money too.'"),
    ("F2", 130.0, 138.0, "final fight", "'₹37,400.' Kabir: '...okay. we'll fix it. together.' He deletes the app; the villain breaks. The counter is relabelled PAID BACK, in gold."),
    ("I1", 138.0, 144.0, "practice", "INSTEAD OF CHASING: delete the app tonight, tell one person the real number, pay it back slowly."),
    ("P1", 144.0, 153.0, "payoff", "MARCH. Sunday cricket at sunrise. He hits a six; Kabir: 'SIX!' PAID BACK ₹14,000. 'No single ball ever won it back.' 'But every month, the number went down.'"),
    ("VT", 153.0, 160.0, "viewer", "To the viewer: 'If you bet, open the app and add up everything you've put in.' 'Then tell one person the real number.'"),
    ("X1", 160.0, 168.0, "mirror", "The edge of the ground: a stranger on the wall: 'YESSS! ₹1,800!' WINNINGS +₹1,300 over him. 'careful. that's how it started for me.'"),
    ("TT", 168.0, 177.0, "title", "ALL IN. 'You can't win back what the app took.' 'Stop chasing.'"),
    ("HL", 177.0, 182.0, "helpline", "Betting more than you can afford? Talk to someone today."),
]

CAPS = {
    "C1": (0.3, 5.7), "C2": (13.0, 17.8), "C3": (62.0, 64.8), "C4": (68.0, 71.8), "C5": (90.0, 93.8),
    "C6": (95.6, 99.4), "C7": (99.8, 103.8), "C8": (105.0, 113.6), "C9": (108.0, 113.6),
    "C10": (148.6, 152.8), "C11": (149.6, 152.8),
    "V1": (153.4, 156.8), "V2": (157.0, 159.8),
    "T1": (169.6, 176.6), "T2": (172.0, 176.6),
    "H1": (177.4, 181.6), "H2": (178.4, 181.6),
}

CUES = {"V1": 28.0, "V2": 30.2, "V3": 41.0, "V4": 47.0, "V5": 53.0, "V6": 65.6, "V7": 75.6,
        "V8": 121.0, "V9": 123.0}

BUBBLES = [
    (58.6, 60.4, "kabir_ph", "cricket today? we're one short"),
    (60.8, 62.0, "him", "can't. busy."),
    (116.0, 118.2, "kabir", "you've gone quiet. what's going on?"),
    (126.4, 128.8, "him", "i lost it. all of it. your money too."),
    (130.0, 131.4, "him", "₹37,400."),
    (131.8, 133.8, "kabir", "...okay. we'll fix it. together."),
    (147.0, 148.4, "kabir", "SIX!"),
    (161.0, 162.6, "stranger", "YESSS! ₹1,800!"),
    (164.0, 166.4, "him", "careful. that's how it started for me."),
]

G1_T0, G1_NIGHT = 40.0, 6.0
G1_LABELS = ["MATCH 6", "MATCH 11", "MATCH 19"]
G1_BETS = ["₹1,500", "₹4,000", "₹8,000"]

# the counter: (time, mode, value). mode: "win" (WINNINGS +), "even" (TO GET EVEN), "paid" (PAID BACK)
COUNTS = [(9.0, "win", 1300), (21.6, "even", 700),
          (G1_T0 + 3.8, "even", 3200), (G1_T0 + G1_NIGHT + 3.8, "even", 8900), (G1_T0 + 2 * G1_NIGHT + 3.8, "even", 15400),
          (78.0, "even", 27400), (89.8, "even", 37400), (135.0, "paid", 0), (144.0, "paid", 14000)]
TOTAL_OWED = 37400
RELABEL = 135.0

EVENTS = {
    "bet0": 2.6, "tap0": 3.0, "six": 8.0, "won": 8.4, "jump": 12.4, "bet1": 19.0, "lost1": 21.0,
    "born": (26.0, 27.6), "k_text": 34.4, "his_text": 36.0, "k_text2": 37.6,
    "g1_lost": [G1_T0 + 3.4, G1_T0 + G1_NIGHT + 3.4, G1_T0 + 2 * G1_NIGHT + 3.4],
    "goa": 73.5, "allin": 75.0, "lost_goa": 77.6, "k_msg": 80.4, "his_ask": 82.2, "k_sent": 84.4, "received": 85.2,
    "lost_k": 89.4, "vip": 94.4, "account": 98.2, "lesson": 104.4,
    "knock": 114.4, "kabir_in": 115.0, "last_ball": 118.6, "rise": (119.0, 120.6), "silence": (124.8, 126.4),
    "delete": 134.0, "delete_tap": 134.4, "crumble": 134.6, "card": 138.2, "hit": 146.5,
    "stranger_win": 161.0, "title": 168.4,
}


def scene_at(t):
    for s in SCENES:
        if s[1] <= t < s[2]:
            return s
    return SCENES[-1]


def count_at(t):
    m, v = None, None
    for tm, mode, val in COUNTS:
        if t >= tm:
            m, v = mode, val
    return m, v


def count_changed(t):
    last = None
    for tm, _, _ in COUNTS:
        if t >= tm:
            last = tm
    return last
