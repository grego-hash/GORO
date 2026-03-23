"""Seed Von Duprin exit device pricing from Pricebook #16 (Feb 2026).

Replaces the old shell families (IDs 10,11,132) which had zero pricing.

Series covered:
  98/99 Series  —  9 device types (Rim, SVR, CVR-47, CVR-48, SPL-57,
                    Mortise-75, Cable-49, Cable-50, XP-Rim)
  33A/35A Series — 3 device types (Rim, SVR-27A, CVR-47A)
  75 Series      — 3 families (Rim, SVR, CVR)
  78 Series      — 4 families (Rim, SVR, CVR, WDC)

Pricing approach for 98/99 (non-Mortise):
  base  = "function:finish"          → Rim prices (15 EXIT + 13 FIRE funcs × 9 finishes)
  adder = "device_type:finish"       → per-device premium over Rim
  adder = "device_type:fire"         → fire-rating premium per device
  adder = "size"                     → 4' = +$30

Mortise-75 has independent pricing because its function set differs.
33A/35A uses its own families with 8 finish columns.
"""

from seed_helpers import fid, slot, options, price, price_bulk, restrict, rule, conflict_all

# ═══════════════════════════════════════════════════════════════
#  Finish definitions (BHMA → US mapping)
# ═══════════════════════════════════════════════════════════════

FINISHES_9899 = [
    ("626",  "626 (US26D) Satin Chrome"),
    ("628",  "628 (US28) Satin Aluminum"),
    ("630",  "630 (US32D) Satin Stainless Steel"),
    ("710",  "710 (313) Duranodic Dark Bronze"),
    ("612",  "612 (US10) Satin Bronze"),
    ("606",  "606 (US4) Satin Brass"),
    ("605",  "605 (US3) Bright Brass"),
    ("643E", "643E Aged Bronze"),
    ("613",  "613 (US10B) Oil Rubbed Bronze"),
]
_FK9899 = [v for v, _ in FINISHES_9899]  # finish keys

FINISHES_33A = [
    ("626",  "626 (US26D) Satin Chrome"),
    ("628",  "628 (US28) Satin Aluminum"),
    ("710",  "710 (313) Duranodic Dark Bronze"),
    ("606",  "606 (US4) Satin Brass"),
    ("605",  "605 (US3) Bright Brass"),
    ("625",  "625 (US26) Bright Chrome"),
    ("643E", "643E Aged Bronze"),
    ("711",  "711 (315) Flat Black"),
]
_FK33A = [v for v, _ in FINISHES_33A]

# ═══════════════════════════════════════════════════════════════
#  Function / trim definitions
# ═══════════════════════════════════════════════════════════════

EXIT_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("TP",    "TP - Thumbpiece"),
    ("TP-BE", "TP-BE - Thumbpiece Blank Escutcheon"),
    ("K",     "K - Knob Trim"),
    ("K-BE",  "K-BE - Knob Blank Escutcheon"),
    ("K-DT",  "K-DT - Knob Dummy Trim"),
    ("K-NL",  "K-NL - Knob Night Latch"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
    ("L-NL",  "L-NL - Lever Night Latch"),
    ("L-KC",  "L-KC - Lever Key Controlled"),
]

FIRE_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("TP",    "TP - Thumbpiece"),
    ("TP-BE", "TP-BE - Thumbpiece Blank Escutcheon"),
    ("K",     "K - Knob Trim"),
    ("K-BE",  "K-BE - Knob Blank Escutcheon"),
    ("K-NL",  "K-NL - Knob Night Latch"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-NL",  "L-NL - Lever Night Latch"),
    ("L-KC",  "L-KC - Lever Key Controlled"),
]

# Mortise has HL (Hospitality Latch) instead of NL-OP, and no K-DT in fire
MORT_EXIT_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("HL",    "HL - Hospitality Latch"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("TP",    "TP - Thumbpiece"),
    ("TP-BE", "TP-BE - Thumbpiece Blank Escutcheon"),
    ("K",     "K - Knob Trim"),
    ("K-BE",  "K-BE - Knob Blank Escutcheon"),
    ("K-DT",  "K-DT - Knob Dummy Trim"),
    ("K-NL",  "K-NL - Knob Night Latch"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-NL",  "L-NL - Lever Night Latch"),
    ("L-KC",  "L-KC - Lever Key Controlled"),
]

MORT_FIRE_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("HL",    "HL - Hospitality Latch"),
    ("NL",    "NL - Night Latch"),
    ("TP",    "TP - Thumbpiece"),
    ("TP-BE", "TP-BE - Thumbpiece Blank Escutcheon"),
    ("K",     "K - Knob Trim"),
    ("K-BE",  "K-BE - Knob Blank Escutcheon"),
    ("K-NL",  "K-NL - Knob Night Latch"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-KC",  "L-KC - Lever Key Controlled"),
]

# 33A/35A Functions (no TP/TP-BE, K-DT)
F33A_EXIT = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-NL",  "L-NL - Lever Night Latch"),
    ("L-KC",  "L-KC - Lever Key Controlled"),
    ("K",     "K - Knob Trim"),
    ("K-BE",  "K-BE - Knob Blank Escutcheon"),
    ("K-NL",  "K-NL - Knob Night Latch"),
]

F33A_FIRE = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-NL",  "L-NL - Lever Night Latch"),
    ("L-KC",  "L-KC - Lever Key Controlled"),
    ("K",     "K - Knob Trim"),
    ("K-BE",  "K-BE - Knob Blank Escutcheon"),
]

# ═══════════════════════════════════════════════════════════════
#  Device types and other options
# ═══════════════════════════════════════════════════════════════

DEVICE_TYPES_9899 = [
    ("RIM",      "Rim Exit Device (98)"),
    ("SVR-27",   "Surface Vertical Rod (99/9927)"),
    ("CVR-47",   "Concealed Vertical Rod (9947)"),
    ("CVR-48",   "Concealed Vertical Rod Top+Bottom (9948)"),
    ("SPL-57",   "Surface 3-Point Latch (9957)"),
    ("CABLE-49", "Concealed Cable (9949)"),
    ("CABLE-50", "WDC Cable (9950)"),
    ("XP-RIM",   "Explosion Proof Rim (XP98/XP99)"),
]

DEVICE_TYPES_33A = [
    ("RIM",    "Rim Exit Device (33A/35A)"),
    ("SVR-27A", "Surface Vertical Rod (27A)"),
    ("CVR-47A", "Concealed Vertical Rod (47A)"),
]

SIZES = [
    ("3FT", '3\' (36")'),
    ("4FT", '4\' (48")'),
]

FIRE_OPTIONS = [
    ("NONE", "Standard (Non-Fire Rated)"),
    ("F",    "Fire Rated"),
]

LEVERS = [
    ("06",  "06 - Knurled Lever"),
    ("17",  "17 - Standard Lever"),
    ("26",  "26 - Straight Lever"),
    ("15",  "15 - Contoured Lever"),
    ("03",  "03 - Knob"),
    ("BRN", "BRN - Breakaway Lever"),
    ("07",  "07 - Bent Lever"),
    ("13",  "13 - Heavy-Duty Lever"),
]

QEL_OPTIONS = [
    ("NONE",    "Standard (No QEL)"),
    ("QEL",     "QEL - Quiet Electric Latch Retraction"),
    ("HD-QEL",  "HD-QEL - QEL w/ Hex Dogging (Panic Only)"),
    ("QELX",    "QELX - QEL for AX Devices"),
    ("HD-QELX", "HD-QELX - QEL w/ Hex Dogging for AX (Panic Only)"),
    ("SD-QEL",  "SD-QEL - QEL w/ Special Center Case Dogging"),
    ("QEL-L",   "QEL-L - Latch Bolt Only (incl. RX Switch)"),
    ("PN",      "PN - Pneumatic Latch Retraction"),
]

DOGGING_OPTIONS = [
    ("NONE", "Standard Dogging"),
    ("CD",   "CD - Cylinder Dogging"),
    ("CDSI", "CDSI - Cylinder Dogging w/ Indicator"),
    ("CI",   "CI - Cylinder Dogging Indicator"),
    ("DI",   "DI - Dogging Indicator"),
    ("LD",   "LD - Less Dogging"),
    ("HDSI", "HDSI - Hex Dogging w/ Indicator"),
    ("SD",   "SD - Special Center Case Dogging (Panic Only)"),
]

DOGGING_OPTIONS_REDUCED = [
    ("NONE", "Standard Dogging"),
    ("CD",   "CD - Cylinder Dogging"),
    ("LD",   "LD - Less Dogging"),
]

SWITCH_OPTIONS = [
    ("NONE",      "No Switch"),
    ("RX",        "RX - Request to Exit"),
    ("RX-LC",     "RX-LC - Request to Exit Low Current"),
    ("RX-2",      "RX-2 - Request to Exit Double Switch"),
    ("WP-RX",     "WP-RX - Waterproof Request to Exit"),
    ("LX",        "LX - Latch Bolt Monitoring"),
    ("LX-LC",     "LX-LC - Latch Bolt Monitoring Low Current"),
    ("LX-RX",     "LX-RX - RX/LX Combination"),
    ("LX-RX-LC",  "LX-RX-LC - RX/LX Combination Low Current"),
    ("SS",        "SS - Signal Switch"),
]

SWITCH_OPTIONS_BASIC = [
    ("NONE",      "No Switch"),
    ("RX",        "RX - Request to Exit"),
    ("WP-RX",     "WP-RX - Waterproof Request to Exit"),
    ("RX-LC",     "RX-LC - Request to Exit Low Current"),
    ("RX-2",      "RX-2 - Request to Exit Double Switch"),
    ("LX",        "LX - Latch Bolt Monitoring"),
    ("LX-LC",     "LX-LC - Latch Bolt Monitoring Low Current"),
    ("LX-RX",     "LX-RX - RX/LX Combination"),
    ("LX-RX-LC",  "LX-RX-LC - RX/LX Combination Low Current"),
]

ELEC_OPTIONS = [
    ("NONE", "No Electric Option"),
    ("E",    "E - Electric Strike/Latch Unlocking"),
    ("ESL",  "ESL - Emergency Secure Lockdown (req. QEL)"),
]

ALK_OPTIONS = [
    ("NONE", "No Exit Alarm"),
    ("ALK",  "ALK - Exit Alarm Kit"),
]

OUTDOOR_OPTIONS = [
    ("NONE",   "Standard (Indoor)"),
    ("OUT",    "OUT - Outdoor Defense"),
]

WEEP_OPTIONS = [
    ("NONE", "No Weep Holes"),
    ("WH",   "WH - Weep Holes (req. Outdoor Defense)"),
]

AM_OPTIONS = [
    ("NONE",     "Standard"),
    ("AM",       "AM - Antimicrobial (Device + Trim)"),
    ("AM-TRIM",  "AM - Antimicrobial (Trim Only)"),
]

AX_OPTIONS = [
    ("NONE", "Standard"),
    ("AX",   "AX - Accessible Device"),
]

DBL_CYL_OPTIONS = [
    ("NONE", "Single Cylinder"),
    ("-2",   "-2 - Double Cylinder"),
    ("-2SI", "-2SI - Double Cylinder w/ Security Indicator"),
]

FER_OPTIONS = [
    ("NONE", "Standard"),
    ("FER",  "FER - Fortified Exit Rim"),
]

QM_OPTIONS = [
    ("NONE", "Standard"),
    ("QM",   "QM - Quiet Mechanical"),
]

DELAY_OPTIONS = [
    ("NONE",     "No Delay"),
    ("0-DELAY",  "0 Second Delay"),
    ("30-DELAY", "30 Second Delay"),
    ("BOCA-15",  "BOCA 15 Second Delay"),
    ("BOCA-30",  "BOCA 30 Second Delay"),
    ("OTHER",    "2-60 Second Delay (Custom)"),
]

CX_OPTIONS = [
    ("NONE", "No Chexit"),
    ("CXA",  "CXA - Chexit Controlled Egress"),
]

# ─── Switch price map ───
SWITCH_PRICES = {
    "RX": 419, "RX-LC": 487, "RX-2": 523, "WP-RX": 608,
    "LX": 419, "LX-LC": 487, "LX-RX": 635, "LX-RX-LC": 764,
    "SS": 861,
}

# ─── Dogging price map ───
DOGGING_PRICES = {
    "CD": 158, "CDSI": 521, "CI": 435, "DI": 408,
    "LD": 0, "HDSI": 374, "SD": 667,
}

# ─── QEL price map ───
QEL_PRICES = {
    "QEL": 1446, "HD-QEL": 1446, "QELX": 1538,
    "HD-QELX": 1538, "SD-QEL": 2113, "QEL-L": 2549, "PN": 2348,
}


def _add_options_9899(conn, f, base_slot=7):
    """Add all device option slots to 98/99 families."""
    s = base_slot
    # Dogging
    slot(conn, f, s, "dogging", "Dogging", 0); s += 1
    options(conn, f, "dogging", DOGGING_OPTIONS)
    for k, v in DOGGING_PRICES.items():
        price(conn, f, "dogging", k, v, "adder")
    # Dogging not available fire-rated
    for k, _ in DOGGING_OPTIONS:
        if k != "NONE" and k != "LD":
            rule(conn, f, "conflict", "dogging", k, "fire", "F",
                 f"{k} dogging not available on fire-rated devices")

    # Switches
    slot(conn, f, s, "switch", "Switch", 0); s += 1
    options(conn, f, "switch", SWITCH_OPTIONS)
    for k, v in SWITCH_PRICES.items():
        price(conn, f, "switch", k, v, "adder")

    # QEL (already-defined options, expanded)
    slot(conn, f, s, "qel", "Electric Latch Retraction", 0); s += 1
    options(conn, f, "qel", QEL_OPTIONS)
    for k, v in QEL_PRICES.items():
        price(conn, f, "qel", k, v, "adder")
    for k in ("HD-QEL", "HD-QELX"):
        rule(conn, f, "conflict", "qel", k, "fire", "F",
             f"{k} (hex dogging) not available on fire-rated devices")

    # Electric unlocking
    slot(conn, f, s, "electric", "Electric Option", 0); s += 1
    options(conn, f, "electric", ELEC_OPTIONS)
    price(conn, f, "electric", "E", 1045, "adder")
    price(conn, f, "electric", "ESL", 673, "adder")

    # Exit alarm
    slot(conn, f, s, "alarm", "Exit Alarm", 0); s += 1
    options(conn, f, "alarm", ALK_OPTIONS)
    price(conn, f, "alarm", "ALK", 1042, "adder")

    # Outdoor defense
    slot(conn, f, s, "outdoor", "Outdoor Defense", 0); s += 1
    options(conn, f, "outdoor", OUTDOOR_OPTIONS)
    price(conn, f, "outdoor", "OUT", 657, "adder")

    # Weep holes
    slot(conn, f, s, "weep", "Weep Holes", 0); s += 1
    options(conn, f, "weep", WEEP_OPTIONS)
    price(conn, f, "weep", "WH", 147, "adder")

    # Antimicrobial
    slot(conn, f, s, "antimicrobial", "Antimicrobial Coating", 0); s += 1
    options(conn, f, "antimicrobial", AM_OPTIONS)
    price(conn, f, "antimicrobial", "AM", 111, "adder")
    price(conn, f, "antimicrobial", "AM-TRIM", 51, "adder")

    # Accessible device
    slot(conn, f, s, "accessible", "Accessible Device", 0); s += 1
    options(conn, f, "accessible", AX_OPTIONS)
    price(conn, f, "accessible", "AX", 102, "adder")

    # Double cylinder
    slot(conn, f, s, "dbl_cylinder", "Double Cylinder", 0); s += 1
    options(conn, f, "dbl_cylinder", DBL_CYL_OPTIONS)
    price(conn, f, "dbl_cylinder", "-2", 544, "adder")
    price(conn, f, "dbl_cylinder", "-2SI", 910, "adder")

    # FER
    slot(conn, f, s, "fer", "Fortified Exit Rim (FER)", 0); s += 1
    options(conn, f, "fer", FER_OPTIONS)
    price(conn, f, "fer", "FER", 602, "adder")

    # Quiet mechanical
    slot(conn, f, s, "quiet_mech", "Quiet Mechanical", 0); s += 1
    options(conn, f, "quiet_mech", QM_OPTIONS)
    price(conn, f, "quiet_mech", "QM", 303, "adder")

    # Delayed egress
    slot(conn, f, s, "delay", "Release Delay", 0); s += 1
    options(conn, f, "delay", DELAY_OPTIONS)
    for d in ("0-DELAY", "30-DELAY", "BOCA-15", "BOCA-30"):
        price(conn, f, "delay", d, 223, "adder")
    price(conn, f, "delay", "OTHER", 302, "adder")

    # Chexit
    slot(conn, f, s, "chexit", "Chexit", 0); s += 1
    options(conn, f, "chexit", CX_OPTIONS)
    price(conn, f, "chexit", "CXA", 3066, "adder")
    return s


def _add_options_simple(conn, f, series, base_slot=6):
    """Add device option slots for single-device families (75/78/22/94-95)."""
    s = base_slot

    # Dogging — 75/78 get CD/LD only; 22 gets LD only; 94/95 none
    if series in ("75", "78"):
        slot(conn, f, s, "dogging", "Dogging", 0); s += 1
        options(conn, f, "dogging", DOGGING_OPTIONS_REDUCED)
        price(conn, f, "dogging", "CD", 158, "adder")
        price(conn, f, "dogging", "LD", 0, "adder")
        rule(conn, f, "conflict", "dogging", "CD", "fire", "F",
             "Cylinder dogging not available on fire-rated devices")
    elif series == "22":
        slot(conn, f, s, "dogging", "Dogging", 0); s += 1
        opts_22_dog = [("NONE", "Standard Dogging"), ("LD", "LD - Less Dogging")]
        options(conn, f, "dogging", opts_22_dog)
        price(conn, f, "dogging", "LD", 0, "adder")

    # Switches — all series get at least RX/LX
    if series in ("75", "78"):
        slot(conn, f, s, "switch", "Switch", 0); s += 1
        sw_opts = [o for o in SWITCH_OPTIONS if o[0] not in
                   ("RX-2", "WP-RX", "LX-LC", "LX-RX-LC")]
        options(conn, f, "switch", sw_opts)
        for k in ("RX", "LX", "RX-LC", "LX-RX", "SS"):
            price(conn, f, "switch", k, SWITCH_PRICES[k], "adder")
    elif series == "22":
        slot(conn, f, s, "switch", "Switch", 0); s += 1
        options(conn, f, "switch", SWITCH_OPTIONS_BASIC)
        for k, v in SWITCH_PRICES.items():
            if k != "SS":
                price(conn, f, "switch", k, v, "adder")
    elif series == "9495":
        slot(conn, f, s, "switch", "Switch", 0); s += 1
        sw_9495 = [("NONE", "No Switch"), ("LX", "LX - Latch Bolt Monitoring"),
                   ("SS", "SS - Signal Switch")]
        options(conn, f, "switch", sw_9495)
        price(conn, f, "switch", "LX", 419, "adder")
        price(conn, f, "switch", "SS", 419, "adder")
    if series != "9495":
        s_prev = s  # track if we added switch
    s_prev = s  # update

    # QEL
    slot(conn, f, s, "qel", "Electric Latch Retraction", 0); s += 1
    options(conn, f, "qel", QEL_OPTIONS)
    for k, v in QEL_PRICES.items():
        price(conn, f, "qel", k, v, "adder")
    for k in ("HD-QEL", "HD-QELX"):
        rule(conn, f, "conflict", "qel", k, "fire", "F",
             f"{k} (hex dogging) not available on fire-rated devices")

    # Electric unlocking — 75/78 only
    if series in ("75", "78"):
        slot(conn, f, s, "electric", "Electric Option", 0); s += 1
        options(conn, f, "electric", ELEC_OPTIONS)
        price(conn, f, "electric", "E", 1045, "adder")
        price(conn, f, "electric", "ESL", 673, "adder")

    # Exit alarm
    if series in ("75", "78"):
        slot(conn, f, s, "alarm", "Exit Alarm", 0); s += 1
        options(conn, f, "alarm", ALK_OPTIONS)
        price(conn, f, "alarm", "ALK", 1042, "adder")
    elif series == "22":
        slot(conn, f, s, "alarm", "Exit Alarm", 0); s += 1
        options(conn, f, "alarm", ALK_OPTIONS)
        price(conn, f, "alarm", "ALK", 925, "adder")

    # Accessible device
    if series in ("75", "78"):
        slot(conn, f, s, "accessible", "Accessible Device", 0); s += 1
        options(conn, f, "accessible", AX_OPTIONS)
        price(conn, f, "accessible", "AX", 102, "adder")
    elif series == "22":
        slot(conn, f, s, "accessible", "Accessible Device", 0); s += 1
        options(conn, f, "accessible", AX_OPTIONS)
        price(conn, f, "accessible", "AX", 38, "adder")
    elif series == "9495":
        slot(conn, f, s, "accessible", "Accessible Device", 0); s += 1
        options(conn, f, "accessible", AX_OPTIONS)
        price(conn, f, "accessible", "AX", 102, "adder")

    # Antimicrobial — 94/95 and 22 (626/630 only)
    if series in ("9495", "22"):
        slot(conn, f, s, "antimicrobial", "Antimicrobial Coating", 0); s += 1
        options(conn, f, "antimicrobial", AM_OPTIONS)
        price(conn, f, "antimicrobial", "AM", 111, "adder")
        price(conn, f, "antimicrobial", "AM-TRIM", 51, "adder")

    return s

# ═══════════════════════════════════════════════════════════════
#  98/99 Rim BASE PRICES — "function:finish" compound
#  (3' device, non-fire)
# ═══════════════════════════════════════════════════════════════
# Columns: 626, 628, 630, 710, 612, 606, 605, 643E, 613

RIM_PRICES = {
    # EXIT HARDWARE
    "EO":    [2284, 2057, 2349, 2184, 2349, 2427, 2709, 3337, 2722],
    "DT":    [2701, 2474, 2766, 2619, 2784, 2762, 3162, 3772, 3157],
    "NL":    [2725, 2498, 2790, 2643, 2808, 2786, 3186, 3796, 3181],
    "NL-OP": [2499, 2272, 2564, 2399, 2564, 2624, 2924, 3552, 2937],
    "TP":    [2880, 2653, 2945, 2796, 2945, 2923, 3350, 3949, 3334],
    "TP-BE": [2880, 2653, 2945, 2796, 2945, 2923, 3350, 3949, 3334],
    "K":     [3015, 2788, 3080, 2915, 3178, 3042, 3593, 4068, 3453],
    "K-BE":  [3015, 2788, 3080, 2915, 3178, 3042, 3593, 4068, 3453],
    "K-DT":  [2999, 2772, 3064, 2899, 3162, 3026, 3577, 4052, 3437],
    "K-NL":  [2999, 2772, 3064, 2899, 3162, 3026, 3577, 4052, 3437],
    "L":     [3235, 3008, 3300, 3135, 3384, 3330, 3786, 4288, 3708],
    "L-BE":  [3235, 3008, 3300, 3135, 3384, 3330, 3786, 4288, 3708],
    "L-DT":  [3043, 2816, 3108, 2943, 3192, 3138, 3594, 4096, 3516],
    "L-NL":  [3043, 2816, 3108, 2943, 3192, 3138, 3594, 4096, 3516],
    "L-KC":  [3235, 3008, 3300, 3135, 3384, 3330, 3786, 4288, 3708],
}

# ═══════════════════════════════════════════════════════════════
#  Device type adders — "device_type:finish" compound
#  (verified constant across all functions)
# ═══════════════════════════════════════════════════════════════
# Columns: 626, 628, 630, 710, 612, 606, 605, 643E, 613

DEVICE_ADDERS = {
    # RIM has no adder (it IS the base)
    "SVR-27":   [1037, 902, 1199, 1053, 1099, 1158, 1123, 1035, 1367],
    "CVR-47":   [1194, 1045, 1223, 1196, 1173, 1231, 1174, 1178, 1445],
    "CVR-48":   [1713, 1564, 1742, 1715, 1692, 1750, 1693, 1697, 1964],
    "SPL-57":   [2190, 2055, 2352, 2206, 2252, 2311, 2276, 2188, 2520],
    "CABLE-49": [1189, 1040, 1218, 1191, 1168, 1226, 1169, 1173, 1440],
    "CABLE-50": [1417, 1274, 1441, 1412, 1385, 1433, 1428, 1368, 1685],
    "XP-RIM":   [184, 184, 184, 184, 184, 184, 184, 184, 184],
}

# ═══════════════════════════════════════════════════════════════
#  Fire adders — "device_type:fire" compound
#  (verified constant across functions and finishes)
# ═══════════════════════════════════════════════════════════════

FIRE_ADDERS = {
    "RIM":      329,
    "SVR-27":   486,
    "CVR-47":   540,
    "CVR-48":   541,
    "SPL-57":   302,
    "CABLE-49": 343,
    "CABLE-50": 476,
    "XP-RIM":   311,
}

# ═══════════════════════════════════════════════════════════════
#  98/99 Mortise (75) — independent pricing
#  Different function set (HL instead of NL-OP, etc.)
# ═══════════════════════════════════════════════════════════════
# Columns: 626, 628, 630, 710, 612, 606, 605, 643E, 613

MORT_PRICES = {
    # EXIT HARDWARE (14 functions)
    "EO":    [3216, 2958, 3312, 3080, 3324, 3324, 3693, 4213, 3557],
    "HL":    [3550, 3292, 3646, 3427, 3671, 3671, 4040, 4547, 3904],
    "DT":    [3633, 3375, 3729, 3515, 3759, 3659, 4146, 4648, 3992],
    "NL":    [3657, 3399, 3753, 3539, 3783, 3683, 4170, 4672, 4016],
    "TP":    [3812, 3554, 3908, 3692, 3920, 3820, 4334, 4825, 4169],
    "TP-BE": [3812, 3554, 3908, 3692, 3920, 3820, 4334, 4825, 4169],
    "K":     [3947, 3689, 4043, 3827, 4055, 3955, 4469, 4944, 4288],
    "K-BE":  [3947, 3689, 4043, 3827, 4055, 3955, 4469, 4944, 4288],
    "K-DT":  [3931, 3673, 4027, 3811, 4039, 3939, 4453, 4928, 4272],
    "K-NL":  [3931, 3673, 4027, 3811, 4039, 3939, 4453, 4928, 4272],
    "L":     [4167, 3909, 4263, 4047, 4275, 4175, 4689, 5164, 4508],
    "L-BE":  [4167, 3909, 4263, 4047, 4275, 4175, 4689, 5164, 4508],
    "L-NL":  [3975, 3717, 4071, 3855, 4083, 3983, 4497, 4972, 4316],
    "L-KC":  [3975, 3717, 4071, 3855, 4083, 3983, 4497, 4972, 4316],
    # FIRE EXIT HARDWARE (12 functions)
    "EO-F":    [3565, 3307, 3661, 3429, 3673, 3673, 4042, 4562, 3906],
    "DT-F":    [3982, 3724, 4078, 3864, 4108, 4008, 4495, 4997, 4341],
    "HL-F":    [3899, 3641, 3995, 3776, 4020, 4020, 4389, 4896, 4253],
    "NL-F":    [4006, 3748, 4102, 3888, 4132, 4032, 4519, 5021, 4365],
    "TP-F":    [4161, 3903, 4257, 4041, 4269, 4169, 4683, 5174, 4518],
    "TP-BE-F": [4161, 3903, 4257, 4041, 4269, 4169, 4683, 5174, 4518],
    "K-F":     [4296, 4038, 4392, 4176, 4404, 4304, 4818, 5293, 4637],
    "K-BE-F":  [4296, 4038, 4392, 4176, 4404, 4304, 4818, 5293, 4637],
    "K-NL-F":  [4280, 4022, 4376, 4160, 4388, 4288, 4802, 5277, 4621],
    "L-F":     [4516, 4258, 4612, 4396, 4624, 4524, 5038, 5513, 4857],
    "L-BE-F":  [4516, 4258, 4612, 4396, 4624, 4524, 5038, 5513, 4857],
    "L-KC-F":  [4324, 4066, 4420, 4204, 4432, 4332, 4846, 5321, 4665],
}

# ═══════════════════════════════════════════════════════════════
#  33A/35A Rim BASE PRICES
# ═══════════════════════════════════════════════════════════════
# Columns: 626, 628, 710, 606, 605, 625, 643E, 711

RIM_33A_PRICES = {
    # EXIT HARDWARE (11 functions)
    "EO":    [2811, 2292, 2297, 2375, 2375, 2942, 3519, 2776],
    "DT":    [3379, 2860, 2865, 3171, 2943, 3651, 4087, 3344],
    "NL":    [3819, 3300, 3305, 3611, 3383, 4091, 4527, 3784],
    "NL-OP": [3305, 2786, 2791, 3085, 2836, 3436, 3980, 3270],
    "L":     [3921, 3402, 3442, 3569, 3437, 4178, 4664, 3921],
    "L-BE":  [3921, 3402, 3442, 3569, 3437, 4178, 4664, 3921],
    "L-NL":  [3729, 3210, 3250, 3377, 3245, 3986, 4472, 3729],
    "L-KC":  [3921, 3402, 3442, 3569, 3437, 4178, 4664, 3921],
    "K":     [3947, 3428, 3433, 3589, 3455, 4196, 4655, 3912],
    "K-BE":  [3947, 3428, 3433, 3589, 3455, 4196, 4655, 3912],
    "K-NL":  [3755, 3236, 3241, 3397, 3263, 4004, 4463, 3720],
    # FIRE EXIT HARDWARE (10 functions)
    "EO-F":    [2854, 2335, 2340, 2418, 2418, 2985, 3562, 2819],
    "DT-F":    [3422, 2903, 2908, 3214, 2986, 3694, 4130, 3387],
    "NL-F":    [3862, 3343, 3348, 3654, 3426, 4134, 4570, 3827],
    "NL-OP-F": [3348, 2829, 2834, 3128, 2879, 3479, 4023, 3313],
    "L-F":     [3964, 3445, 3485, 3612, 3480, 4221, 4707, 3964],
    "L-BE-F":  [3964, 3445, 3485, 3612, 3480, 4221, 4707, 3964],
    "L-NL-F":  [3772, 3253, 3293, 3420, 3288, 4029, 4515, 3772],
    "L-KC-F":  [3964, 3445, 3485, 3612, 3480, 4221, 4707, 3964],
    "K-F":     [3990, 3471, 3476, 3632, 3498, 4239, 4698, 3955],
    "K-BE-F":  [3990, 3471, 3476, 3632, 3498, 4239, 4698, 3955],
}

# 33A/35A device adders (relative to 33A Rim)
# Columns: 626, 628, 710, 606, 605, 625, 643E, 711
DEVICE_ADDERS_33A = {
    "SVR-27A":  [1179, 1092, 1154, 1156, 1152, 1192, 1339, 1427],
    "CVR-47A":  [1172, 1085, 1147, 1149, 1145, 1185, 1332, 1420],
}

# 33A/35A fire adders per device type
FIRE_ADDERS_33A = {
    "RIM":     43,
    "SVR-27A": 42,
    "CVR-47A": 221,
}

# ═══════════════════════════════════════════════════════════════
#  75 Series — Finish definitions (10 finishes, 9 price columns)
#  Columns: 626, 628, 710, 612, 606, 619/643E, 605, 625, 711
# ═══════════════════════════════════════════════════════════════

FINISHES_75 = [
    ("626",  "626 (US26D) Satin Chrome"),
    ("628",  "628 (US28) Satin Aluminum"),
    ("710",  "710 (313) Dark Bronze"),
    ("612",  "612 (US10) Satin Bronze"),
    ("606",  "606 (US4) Satin Brass"),
    ("619",  "619 (US15) Satin Nickel"),
    ("643E", "643E Aged Bronze"),
    ("605",  "605 (US3) Bright Brass"),
    ("625",  "625 (US26) Bright Chrome"),
    ("711",  "711 (315) Flat Black"),
]
_FK75 = [v for v, _ in FINISHES_75]

# ═══════════════════════════════════════════════════════════════
#  78 Series — Finish definitions (11 finishes, 9 price columns)
#  Columns: 626, 628, 630, 710, 612, 606, 605/619/643E, 625, 711
# ═══════════════════════════════════════════════════════════════

FINISHES_78 = [
    ("626",  "626 (US26D) Satin Chrome"),
    ("628",  "628 (US28) Satin Aluminum"),
    ("630",  "630 (US32D) Satin Stainless Steel"),
    ("710",  "710 (313) Dark Bronze"),
    ("612",  "612 (US10) Satin Bronze"),
    ("606",  "606 (US4) Satin Brass"),
    ("605",  "605 (US3) Bright Brass"),
    ("619",  "619 (US15) Satin Nickel"),
    ("643E", "643E Aged Bronze"),
    ("625",  "625 (US26) Bright Chrome"),
    ("711",  "711 (315) Flat Black"),
]
_FK78 = [v for v, _ in FINISHES_78]

# ═══════════════════════════════════════════════════════════════
#  75 / 78 Function definitions
# ═══════════════════════════════════════════════════════════════

R75_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
]

S75_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
    ("TL",    "TL - Thumbpiece Lever"),
    ("TL-BE", "TL-BE - Thumbpiece Lever Blank Escutcheon"),
]

R78_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
    ("L-NL",  "L-NL - Lever Night Latch"),
]

S78_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
    ("L-NL",  "L-NL - Lever Night Latch"),
    ("TL",    "TL - Thumbpiece Lever"),
    ("TL-BE", "TL-BE - Thumbpiece Lever Blank Escutcheon"),
]

# ═══════════════════════════════════════════════════════════════
#  75 Series Prices — "function:finish" (3' non-fire)
# ═══════════════════════════════════════════════════════════════

RIM_75_PRICES = {
    "EO":    [2464, 2021, 2075, 2289, 2311, 2757, 2757, 2666, 2569, 2797],
    "DT":    [3032, 2589, 2643, 3085, 2879, 3466, 3466, 3375, 3278, 3365],
    "NL":    [3472, 3029, 3083, 3525, 3319, 3906, 3906, 3815, 3718, 3805],
    "NL-OP": [2958, 2515, 2569, 2999, 2772, 3251, 3251, 3160, 3063, 3258],
    "L":     [3574, 3131, 3220, 3483, 3373, 3993, 3993, 3902, 3805, 3942],
    "L-BE":  [3501, 3058, 3147, 3410, 3300, 3920, 3920, 3829, 3732, 3869],
    "L-DT":  [3488, 3045, 3134, 3397, 3287, 3907, 3907, 3816, 3719, 3856],
}
FIRE_ADDER_75_RIM = 178

SVR_75_PRICES = {
    "EO":    [3381, 2829, 2930, 3209, 3235, 3565, 3565, 3617, 3505, 3738],
    "DT":    [3949, 3397, 3498, 4005, 3803, 4274, 4274, 4326, 4214, 4306],
    "NL":    [4389, 3837, 3938, 4445, 4243, 4714, 4714, 4766, 4654, 4746],
    "NL-OP": [3875, 3323, 3424, 3919, 3696, 4059, 4059, 4111, 3999, 4199],
    "L":     [4491, 3939, 4075, 4403, 4297, 4801, 4801, 4853, 4741, 4883],
    "L-BE":  [4418, 3866, 4002, 4330, 4224, 4728, 4728, 4780, 4668, 4810],
    "L-DT":  [4405, 3853, 3989, 4317, 4211, 4715, 4715, 4767, 4655, 4797],
    "TL":    [5151, 4599, 4700, 5299, 4839, 5568, 5568, 5620, 5508, 5508],
    "TL-BE": [5085, 4533, 4634, 5233, 4773, 5502, 5502, 5554, 5442, 5442],
}
FIRE_ADDER_75_SVR = 167

CVR_75_PRICES = {
    "EO":    [3447, 2883, 2989, 3283, 3309, 3619, 3619, 3695, 3577, 3800],
    "DT":    [4015, 3451, 3557, 4079, 3877, 4328, 4328, 4404, 4286, 4368],
    "NL":    [4455, 3891, 3997, 4519, 4317, 4768, 4768, 4844, 4726, 4808],
    "NL-OP": [3941, 3377, 3483, 3993, 3770, 4113, 4113, 4189, 4071, 4261],
    "L":     [4557, 3993, 4134, 4477, 4371, 4855, 4855, 4931, 4813, 4945],
    "L-BE":  [4484, 3920, 4061, 4404, 4298, 4782, 4782, 4858, 4740, 4872],
    "L-DT":  [4471, 3907, 4048, 4391, 4285, 4769, 4769, 4845, 4727, 4859],
    "TL":    [5217, 4653, 4759, 5373, 4913, 5622, 5622, 5698, 5580, 5570],
    "TL-BE": [5151, 4587, 4693, 5307, 4847, 5556, 5556, 5632, 5514, 5504],
}
FIRE_ADDER_75_CVR = 256

# ═══════════════════════════════════════════════════════════════
#  78 Series Prices — "function:finish" (3' non-fire)
# ═══════════════════════════════════════════════════════════════

RIM_78_PRICES = {
    "EO":    [1963, 1703, 2012, 1806, 2028, 2083, 2312, 2312, 2312, 2205, 2479],
    "DT":    [2372, 2112, 2421, 2234, 2456, 2412, 2757, 2757, 2757, 2650, 2907],
    "NL":    [2394, 2134, 2443, 2256, 2478, 2434, 2779, 2779, 2779, 2672, 2929],
    "NL-OP": [2178, 1918, 2227, 2021, 2243, 2280, 2527, 2527, 2527, 2420, 2694],
    "L":     [2728, 2468, 2777, 2547, 2793, 2783, 3144, 3144, 3144, 3037, 3244],
    "L-BE":  [2728, 2468, 2777, 2547, 2793, 2783, 3144, 3144, 3144, 3037, 3244],
    "L-DT":  [2579, 2319, 2628, 2398, 2644, 2634, 3024, 3024, 3024, 2917, 3095],
    "L-NL":  [2579, 2319, 2628, 2398, 2644, 2634, 3024, 3024, 3024, 2917, 3095],
}
FIRE_ADDER_78_RIM = 324

SVR_78_PRICES = {
    "EO":    [2852, 2459, 2996, 2656, 2967, 3057, 3250, 3250, 3250, 3153, 3368],
    "DT":    [3261, 2868, 3405, 3084, 3395, 3386, 3695, 3695, 3695, 3598, 3796],
    "NL":    [3283, 2890, 3427, 3106, 3417, 3408, 3717, 3717, 3717, 3620, 3818],
    "NL-OP": [3067, 2674, 3211, 2871, 3182, 3254, 3465, 3465, 3465, 3368, 3583],
    "L":     [3617, 3224, 3761, 3397, 3732, 3757, 4082, 4082, 4082, 3985, 4133],
    "L-BE":  [3617, 3224, 3761, 3397, 3732, 3757, 4082, 4082, 4082, 3985, 4133],
    "L-DT":  [3468, 3075, 3612, 3248, 3583, 3608, 3962, 3962, 3962, 3865, 3984],
    "L-NL":  [3468, 3075, 3612, 3248, 3583, 3608, 3962, 3962, 3962, 3865, 3984],
    "TL":    [4463, 4070, 4607, 4286, 4689, 4422, 4989, 4989, 4989, 4892, 4998],
    "TL-BE": [4397, 4004, 4541, 4220, 4623, 4356, 4923, 4923, 4923, 4826, 4932],
}
FIRE_ADDER_78_SVR = 388

CVR_78_PRICES = {
    "EO":    [2964, 2556, 3059, 2750, 3036, 3125, 3310, 3310, 3310, 3211, 3473],
    "DT":    [3373, 2965, 3468, 3178, 3464, 3454, 3755, 3755, 3755, 3656, 3901],
    "NL":    [3395, 2987, 3490, 3200, 3486, 3476, 3777, 3777, 3777, 3678, 3923],
    "NL-OP": [3179, 2771, 3274, 2965, 3251, 3322, 3525, 3525, 3525, 3426, 3688],
    "L":     [3729, 3321, 3824, 3491, 3801, 3825, 4142, 4142, 4142, 4043, 4238],
    "L-BE":  [3729, 3321, 3824, 3491, 3801, 3825, 4142, 4142, 4142, 4043, 4238],
    "L-DT":  [3580, 3172, 3675, 3342, 3652, 3676, 4022, 4022, 4022, 3923, 4089],
    "L-NL":  [3580, 3172, 3675, 3342, 3652, 3676, 4022, 4022, 4022, 3923, 4089],
    "TL":    [4575, 4167, 4670, 4380, 4758, 4490, 5049, 5049, 5049, 4950, 5103],
    "TL-BE": [4509, 4101, 4604, 4314, 4692, 4424, 4983, 4983, 4983, 4884, 5037],
}
FIRE_ADDER_78_CVR = 414

WDC_78_PRICES = {
    "EO":    [3327, 2889, 3401, 3117, 3418, 3517, 3760, 3760, 3760, 3651, 3856],
    "DT":    [3736, 3298, 3810, 3545, 3846, 3846, 4205, 4205, 4205, 4096, 4284],
    "NL":    [3758, 3320, 3832, 3567, 3868, 3868, 4227, 4227, 4227, 4118, 4306],
    "NL-OP": [3542, 3104, 3616, 3332, 3633, 3714, 3975, 3975, 3975, 3866, 4071],
    "L":     [4092, 3654, 4166, 3858, 4183, 4217, 4592, 4592, 4592, 4483, 4621],
    "L-BE":  [4092, 3654, 4166, 3858, 4183, 4217, 4592, 4592, 4592, 4483, 4621],
    "L-DT":  [3943, 3505, 4017, 3709, 4034, 4068, 4472, 4472, 4472, 4363, 4472],
    "L-NL":  [3943, 3505, 4017, 3709, 4034, 4068, 4472, 4472, 4472, 4363, 4472],
    "TL":    [5023, 4585, 5097, 4832, 5225, 4967, 5584, 5584, 5584, 5475, 5571],
    "TL-BE": [4957, 4519, 5031, 4766, 5159, 4901, 5518, 5518, 5518, 5409, 5505],
}
FIRE_ADDER_78_WDC = 450


# ═══════════════════════════════════════════════════════════════
#  SEED FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _seed_9899(conn):
    """Seed 98/99 Series (non-Mortise) as one family with adder pricing."""
    f = fid(conn,
            "Von Duprin",
            "98/99 Series Exit Device",
            "Exit Device",
            "{device_type} {function} {finish}",
            "Von Duprin 98/99 {device_type} {function} {finish}")

    all_funcs = EXIT_FUNCS  # superset of exit + fire function codes
    # Combined unique function option list for the slot
    func_options = list(dict(EXIT_FUNCS).items())  # preserves order, dedupes

    slot(conn, f, 1, "device_type",  "Device Type",     1)
    slot(conn, f, 2, "function",     "Function / Trim",  1)
    slot(conn, f, 3, "finish",       "Finish",           1)
    slot(conn, f, 4, "fire",         "Fire Rating",      1)
    slot(conn, f, 5, "size",         "Device Size",      1)
    slot(conn, f, 6, "lever",        "Lever Design",     0)

    options(conn, f, "device_type", DEVICE_TYPES_9899)
    options(conn, f, "function",    EXIT_FUNCS)  # all 15 functions
    options(conn, f, "finish",      FINISHES_9899)
    options(conn, f, "fire",        FIRE_OPTIONS)
    options(conn, f, "size",        SIZES)
    options(conn, f, "lever",       LEVERS)

    # ── Lever only applicable for L-type trims ──
    lever_funcs = {"L", "L-BE", "L-DT", "L-NL", "L-KC"}
    non_lever = [fv for fv, _ in EXIT_FUNCS if fv not in lever_funcs]
    for fv in non_lever:
        for lv, _ in LEVERS:
            rule(conn, f, "conflict", "function", fv, "lever", lv,
                 "Lever only applicable with L-type trims")

    # ── Fire rules: K-DT and L-DT not available fire-rated ──
    for func_code in ("K-DT", "L-DT"):
        rule(conn, f, "conflict", "function", func_code, "fire", "F",
             f"{func_code} not available fire-rated")

    # ── 630 only on 98 (Rim) device ──
    non_rim = [dv for dv, _ in DEVICE_TYPES_9899 if dv not in ("RIM", "XP-RIM")]
    for dv in non_rim:
        rule(conn, f, "conflict", "device_type", dv, "finish", "630",
             "630 (Satin Stainless) only available on Rim device")

    # ── BASE PRICING: function:finish (Rim, 3', non-fire) ──
    for func_key, prices in RIM_PRICES.items():
        for fin, amt in zip(_FK9899, prices):
            price(conn, f, "function:finish", f"{func_key}:{fin}", amt, "base")

    # ── DEVICE ADDERS: device_type:finish ──
    for dev_key, adders in DEVICE_ADDERS.items():
        for fin, amt in zip(_FK9899, adders):
            price(conn, f, "device_type:finish", f"{dev_key}:{fin}", amt, "adder")

    # ── FIRE ADDERS: device_type:fire ──
    for dev_key, amt in FIRE_ADDERS.items():
        price(conn, f, "device_type:fire", f"{dev_key}:F", amt, "adder")

    # ── SIZE ADDER ──
    price(conn, f, "size", "4FT", 30, "adder")

    # ── All device options (dogging, switches, QEL, electric, etc.) ──
    _add_options_9899(conn, f, 7)

    base = len(RIM_PRICES) * len(_FK9899)
    dev = sum(len(a) for a in DEVICE_ADDERS.values())
    fire_cnt = len(FIRE_ADDERS)
    print(f"    98/99 Series: base={base} + device={dev} + fire={fire_cnt} + size=1 + options")
    return f


def _seed_9899_mortise(conn):
    """Seed 98/99 Mortise Lock (75) as a separate family."""
    f = fid(conn,
            "Von Duprin",
            "98/99 Mortise Lock Exit Device (75)",
            "Exit Device",
            "{function} {finish}",
            "Von Duprin 9875/9975 Mortise Lock {function} {finish}")

    # Combined function options (EXIT + FIRE unique)
    all_funcs = list(dict(MORT_EXIT_FUNCS).items())

    slot(conn, f, 1, "function", "Function / Trim",  1)
    slot(conn, f, 2, "finish",   "Finish",            1)
    slot(conn, f, 3, "fire",     "Fire Rating",       1)
    slot(conn, f, 4, "size",     "Device Size",       1)
    slot(conn, f, 5, "lever",    "Lever Design",      0)

    options(conn, f, "function", MORT_EXIT_FUNCS)
    options(conn, f, "finish",   FINISHES_9899)
    options(conn, f, "fire",     FIRE_OPTIONS)
    options(conn, f, "size",     SIZES)
    options(conn, f, "lever",    LEVERS)

    # Lever only for L-type trims
    lever_funcs = {"L", "L-BE", "L-NL", "L-KC"}
    non_lever = [fv for fv, _ in MORT_EXIT_FUNCS if fv not in lever_funcs]
    for fv in non_lever:
        for lv, _ in LEVERS:
            rule(conn, f, "conflict", "function", fv, "lever", lv,
                 "Lever only applicable with L-type trims")

    # K-DT not available fire-rated
    rule(conn, f, "conflict", "function", "K-DT", "fire", "F",
         "K-DT not available fire-rated")
    # L-NL not available fire-rated
    rule(conn, f, "conflict", "function", "L-NL", "fire", "F",
         "L-NL not available fire-rated for Mortise")

    # ── NON-FIRE PRICING: function:finish base ──
    cnt = 0
    for func_key in [fk for fk, _ in MORT_EXIT_FUNCS]:
        if func_key in MORT_PRICES:
            for fin, amt in zip(_FK9899, MORT_PRICES[func_key]):
                price(conn, f, "function:finish", f"{func_key}:{fin}", amt, "base")
                cnt += 1

    # ── FIRE ADDER: constant $349 across all functions and finishes ──
    price(conn, f, "fire", "F", 349, "adder")

    # SIZE ADDER
    price(conn, f, "size", "4FT", 30, "adder")

    # ── All device options ──
    _add_options_9899(conn, f, 6)

    print(f"    98/99 Mortise: base={cnt} + fire=1 + size=1 + options")
    return f


def _seed_33a_35a(conn):
    """Seed 33A/35A Series."""
    f = fid(conn,
            "Von Duprin",
            "33A/35A Series Exit Device",
            "Exit Device",
            "{device_type} {function} {finish}",
            "Von Duprin 33A/35A {device_type} {function} {finish}")

    slot(conn, f, 1, "device_type", "Device Type",     1)
    slot(conn, f, 2, "function",    "Function / Trim",  1)
    slot(conn, f, 3, "finish",      "Finish",           1)
    slot(conn, f, 4, "fire",        "Fire Rating",      1)
    slot(conn, f, 5, "size",        "Device Size",      1)
    slot(conn, f, 6, "lever",       "Lever Design",     0)

    options(conn, f, "device_type", DEVICE_TYPES_33A)
    options(conn, f, "function",    F33A_EXIT)
    options(conn, f, "finish",      FINISHES_33A)
    options(conn, f, "fire",        FIRE_OPTIONS)
    options(conn, f, "size",        SIZES)
    options(conn, f, "lever",       LEVERS)

    # Lever only for L-type trims
    lever_funcs = {"L", "L-BE", "L-NL", "L-KC"}
    non_lever = [fv for fv, _ in F33A_EXIT if fv not in lever_funcs]
    for fv in non_lever:
        for lv, _ in LEVERS:
            rule(conn, f, "conflict", "function", fv, "lever", lv,
                 "Lever only applicable with L-type trims")

    # K-NL not available fire-rated for 33A
    rule(conn, f, "conflict", "function", "K-NL", "fire", "F",
         "K-NL not available fire-rated for 33A/35A")

    # ── BASE PRICING: function:finish (Rim, non-fire) ──
    cnt = 0
    for func_key in [fk for fk, _ in F33A_EXIT]:
        if func_key in RIM_33A_PRICES:
            for fin, amt in zip(_FK33A, RIM_33A_PRICES[func_key]):
                price(conn, f, "function:finish", f"{func_key}:{fin}", amt, "base")
                cnt += 1

    # ── DEVICE ADDERS: device_type:finish ──
    dev_cnt = 0
    for dev_key, adders in DEVICE_ADDERS_33A.items():
        for fin, amt in zip(_FK33A, adders):
            price(conn, f, "device_type:finish", f"{dev_key}:{fin}", amt, "adder")
            dev_cnt += 1

    # ── FIRE ADDERS: device_type:fire ──
    for dev_key, amt in FIRE_ADDERS_33A.items():
        price(conn, f, "device_type:fire", f"{dev_key}:F", amt, "adder")

    # SIZE ADDER
    price(conn, f, "size", "4FT", 30, "adder")

    # ── All device options ──
    _add_options_9899(conn, f, 7)

    fire_cnt = len(FIRE_ADDERS_33A)
    print(f"    33A/35A Series: base={cnt} + device={dev_cnt} + fire={fire_cnt} + size=1 + options")
    return f


def _seed_simple_family(conn, name, funcs, finishes, finish_keys,
                        prices, fire_adder, exit_only=("L-DT",),
                        size_adder=30, series=None):
    """Seed a single-device-type exit device family (75/78 patterns)."""
    f = fid(conn, "Von Duprin", name, "Exit Device",
            "{function} {finish}",
            f"Von Duprin {name} {{function}} {{finish}}")

    slot(conn, f, 1, "function", "Function / Trim", 1)
    slot(conn, f, 2, "finish",   "Finish",          1)
    slot(conn, f, 3, "fire",     "Fire Rating",     1)
    slot(conn, f, 4, "size",     "Device Size",     1)
    slot(conn, f, 5, "lever",    "Lever Design",    0)

    options(conn, f, "function", funcs)
    options(conn, f, "finish",   finishes)
    options(conn, f, "fire",     FIRE_OPTIONS)
    options(conn, f, "size",     SIZES)
    options(conn, f, "lever",    LEVERS)

    # Lever only for L-type trims
    lever_funcs = {fv for fv, _ in funcs if fv.startswith("L")}
    non_lever = [fv for fv, _ in funcs if fv not in lever_funcs]
    for fv in non_lever:
        for lv, _ in LEVERS:
            rule(conn, f, "conflict", "function", fv, "lever", lv,
                 "Lever only applicable with L-type trims")

    # Exit-only functions not available fire-rated
    func_keys = {fv for fv, _ in funcs}
    for fc in exit_only:
        if fc in func_keys:
            rule(conn, f, "conflict", "function", fc, "fire", "F",
                 f"{fc} not available fire-rated")

    # Base pricing: function:finish
    cnt = 0
    for func_key, row in prices.items():
        for fin, amt in zip(finish_keys, row):
            price(conn, f, "function:finish", f"{func_key}:{fin}", amt, "base")
            cnt += 1

    # Fire adder (int=constant, dict=per-finish, None=skip)
    fire_cnt = 0
    if isinstance(fire_adder, dict):
        for fin, amt in fire_adder.items():
            price(conn, f, "fire:finish", f"F:{fin}", amt, "adder")
            fire_cnt += 1
    elif fire_adder is not None:
        price(conn, f, "fire", "F", fire_adder, "adder")
        fire_cnt = 1

    # Size adder
    price(conn, f, "size", "4FT", size_adder, "adder")

    # Device options (optional, series-dependent)
    if series:
        _add_options_simple(conn, f, series, base_slot=6)

    total = cnt + fire_cnt + 1
    print(f"    {name}: {total} pricing rows ({cnt} base + {fire_cnt} fire + 1 size" +
          (f" + options" if series else "") + ")")
    return f


def _seed_75(conn):
    """Seed 75 Series (Rim, SVR, CVR) as separate families."""
    _seed_simple_family(conn, "75 Series Rim Exit Device",
                        R75_FUNCS, FINISHES_75, _FK75,
                        RIM_75_PRICES, FIRE_ADDER_75_RIM, series="75")
    _seed_simple_family(conn, "75 Series Surface Vertical Rod (SVR)",
                        S75_FUNCS, FINISHES_75, _FK75,
                        SVR_75_PRICES, FIRE_ADDER_75_SVR, series="75")
    _seed_simple_family(conn, "75 Series Concealed Vertical Rod (CVR)",
                        S75_FUNCS, FINISHES_75, _FK75,
                        CVR_75_PRICES, FIRE_ADDER_75_CVR, series="75")


def _seed_78(conn):
    """Seed 78 Series (Rim, SVR, CVR, WDC) as separate families."""
    _seed_simple_family(conn, "78 Series Rim Exit Device",
                        R78_FUNCS, FINISHES_78, _FK78,
                        RIM_78_PRICES, FIRE_ADDER_78_RIM, series="78")
    _seed_simple_family(conn, "78 Series Surface Vertical Rod (SVR)",
                        S78_FUNCS, FINISHES_78, _FK78,
                        SVR_78_PRICES, FIRE_ADDER_78_SVR, series="78")
    _seed_simple_family(conn, "78 Series Concealed Vertical Rod (CVR)",
                        S78_FUNCS, FINISHES_78, _FK78,
                        CVR_78_PRICES, FIRE_ADDER_78_CVR, series="78")
    _seed_simple_family(conn, "78 Series Wire/Door Cord (WDC)",
                        S78_FUNCS, FINISHES_78, _FK78,
                        WDC_78_PRICES, FIRE_ADDER_78_WDC, series="78")


# ═══════════════════════════════════════════════════════════════
#  22 Series — Budget Grade 2 Panic Hardware
#  3 price columns → 4 finish options (689/695 share column)
#  Finish column order (pdfplumber): 689/695, 526, 622
# ═══════════════════════════════════════════════════════════════

FINISHES_22 = [
    ("689", "689 Aluminum"),
    ("695", "695 Aluminum"),
    ("526", "526"),
    ("622", "622"),
]
_FK22 = [v for v, _ in FINISHES_22]

F22 = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("K",     "K - Key Lock (Incl. Cylinder)"),
    ("K-BE",  "K-BE - Key Blank Escutcheon"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("TP",    "TP - Thumbpiece"),
    ("TP-BE", "TP-BE - Thumbpiece Blank Escutcheon"),
]

def _exp22(r):
    """Expand 3-col (689/695, 526, 622) → 4 keys (689, 695, 526, 622)."""
    return [r[0], r[0], r[1], r[2]]

# Prices from pdfplumber (3 cols: 689/695, 526, 622)
RIM_22_PRICES = {k: _exp22(v) for k, v in {
    "EO":    [736, 962, 814],    "DT":    [820, 1071, 905],
    "NL":    [832, 1088, 920],   "NL-OP": [951, 1177, 1029],
    "K":     [1115, 1456, 1231], "K-BE":  [1115, 1456, 1231],
    "L":     [1108, 1448, 1223], "L-BE":  [1108, 1448, 1223],
    "TP":    [1105, 1443, 1220], "TP-BE": [1105, 1443, 1220],
}.items()}
FIRE_22_RIM = {"689": 192, "695": 192, "526": 250, "622": 211}

SVR_22_PRICES = {k: _exp22(v) for k, v in {
    "EO":    [1267, 1493, 1345], "DT":    [1351, 1602, 1436],
    "NL":    [1363, 1619, 1451], "NL-OP": [1482, 1708, 1560],
    "K":     [1646, 1987, 1762], "K-BE":  [1646, 1987, 1762],
    "L":     [1639, 1979, 1754], "L-BE":  [1639, 1979, 1754],
    "TP":    [1636, 1974, 1751], "TP-BE": [1636, 1974, 1751],
}.items()}
FIRE_22_SVR = {"689": 391, "695": 391, "526": 449, "622": 410}


def _seed_22(conn):
    """Seed 22 Series (Rim, SVR) — per-finish fire adders."""
    _seed_simple_family(conn, "22 Series Rim Exit Device",
                        F22, FINISHES_22, _FK22,
                        RIM_22_PRICES, FIRE_22_RIM, exit_only=(), series="22")
    _seed_simple_family(conn, "22 Series Surface Vertical Rod (SVR)",
                        F22, FINISHES_22, _FK22,
                        SVR_22_PRICES, FIRE_22_SVR, exit_only=(), series="22")


# ═══════════════════════════════════════════════════════════════
#  94/95 INPACT Series — 7 price columns → 8 finish options
#  Finish col order: 626, 628, 710, 612, 606, 605/625, 711
#  "3' AND 4' DEVICE PRICING SHOWN" → size adder = $0
# ═══════════════════════════════════════════════════════════════

FINISHES_9495 = [
    ("626",  "626 (US26D) Satin Chrome"),
    ("628",  "628 (US28) Satin Aluminum"),
    ("710",  "710 (313) Dark Bronze"),
    ("612",  "612 (US10) Satin Bronze"),
    ("606",  "606 (US4) Satin Brass"),
    ("605",  "605 (US3) Bright Brass"),
    ("625",  "625 (US26) Bright Chrome"),
    ("711",  "711 (315) Flat Black"),
]
_FK9495 = [v for v, _ in FINISHES_9495]

def _exp9495(r):
    """Expand 7-col → 8 keys (605/625 share col 5)."""
    return r[:5] + [r[5], r[5]] + [r[6]]

CVR47_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
    ("TL",    "TL - Thumbpiece Lever"),
    ("TL-BE", "TL-BE - Thumbpiece Lever Blank Escutcheon"),
]

CVR47_9495_PRICES = {k: _exp9495(v) for k, v in {
    "EO":    [2808, 2647, 2711, 2839, 2966, 3197, 3684],
    "DT":    [3710, 3549, 3613, 3751, 3679, 4125, 4612],
    "L":     [3917, 3756, 3854, 4031, 4027, 4431, 4793],
    "L-BE":  [3917, 3756, 3854, 4031, 4027, 4431, 4793],
    "L-DT":  [4044, 3883, 3981, 4158, 4154, 4558, 4920],
    "TL":    [4912, 4751, 4815, 5045, 4715, 5419, 5814],
    "TL-BE": [4846, 4685, 4749, 4979, 4649, 5353, 5748],
}.items()}

CVR48_9495_PRICES = {k: _exp9495(v) for k, v in {
    "EO":    [3213, 3052, 3116, 3244, 3371, 3602, 4089],
    "DT":    [4115, 3954, 4018, 4156, 4084, 4530, 5017],
    "L":     [4322, 4161, 4259, 4436, 4432, 4836, 5198],
    "L-BE":  [4322, 4161, 4259, 4436, 4432, 4836, 5198],
    "L-DT":  [4449, 4288, 4386, 4563, 4559, 4963, 5325],
    "TL":    [5317, 5156, 5220, 5450, 5120, 5824, 6219],
    "TL-BE": [5251, 5090, 5154, 5384, 5054, 5758, 6153],
}.items()}

MORT_9495_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
]

MORT_9495_PRICES = {k: _exp9495(v) for k, v in {
    "EO":    [3411, 3250, 3349, 3477, 3604, 3835, 4322],
    "DT":    [4313, 4152, 4251, 4389, 4317, 4763, 5250],
    "NL":    [4313, 4152, 4251, 4389, 4317, 4763, 5250],
    "L":     [4520, 4359, 4492, 4669, 4665, 5069, 5431],
    "L-BE":  [4520, 4359, 4492, 4669, 4665, 5069, 5431],
    "L-DT":  [4647, 4486, 4619, 4796, 4792, 5196, 5558],
}.items()}


def _seed_9495(conn):
    """Seed 94/95 INPACT Series (CVR47, CVR48, Mort)."""
    _seed_simple_family(conn, "94/95 Series Concealed Vertical Rod (CVR47)",
                        CVR47_FUNCS, FINISHES_9495, _FK9495,
                        CVR47_9495_PRICES, 466, size_adder=0, series="9495")
    _seed_simple_family(conn, "94/95 Series Concealed Vertical Rod (CVR48)",
                        CVR47_FUNCS, FINISHES_9495, _FK9495,
                        CVR48_9495_PRICES, 469, size_adder=0, series="9495")
    _seed_simple_family(conn, "94/95 Series Mortise Lock (Mort)",
                        MORT_9495_FUNCS, FINISHES_9495, _FK9495,
                        MORT_9495_PRICES, 496, size_adder=0, series="9495")


# ═══════════════════════════════════════════════════════════════
#  55 Series — 6 price columns → 9 finish options
#  Finish col order: 626, 613, 612, 606, 605/625/643E, 622/693
# ═══════════════════════════════════════════════════════════════

FINISHES_55 = [
    ("626",  "626 (US26D) Satin Chrome"),
    ("613",  "613 (US13) Oil Rubbed Bronze"),
    ("612",  "612 (US10) Satin Bronze"),
    ("606",  "606 (US4) Satin Brass"),
    ("605",  "605 (US3) Bright Brass"),
    ("625",  "625 (US26) Bright Chrome"),
    ("643E", "643E Aged Bronze"),
    ("622",  "622 Flat Black"),
    ("693",  "693 Painted Dark Bronze"),
]
_FK55 = [v for v, _ in FINISHES_55]

def _exp55(r):
    """Expand 6-col → 9 keys (605/625/643E share col 4, 622/693 share col 5)."""
    return r[:4] + [r[4]] * 3 + [r[5]] * 2

RIM_55_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
]

RIM_55_PRICES = {k: _exp55(v) for k, v in {
    "EO":    [4508, 4477, 4225, 4043, 4877, 4877],
    "DT":    [5410, 5379, 5137, 4756, 5805, 5805],
    "NL":    [5625, 5594, 5352, 4953, 6020, 6020],
    "NL-OP": [4723, 4692, 4440, 4240, 5092, 5092],
    "L":     [5961, 5914, 5678, 5322, 6452, 6314],
    "L-BE":  [5902, 5855, 5619, 5263, 6393, 6255],
}.items()}

CVR_55_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("NL-OP", "NL-OP - Night Latch Optional Pull"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("TL",    "TL - Thumbpiece Lever"),
    ("TL-BE", "TL-BE - Thumbpiece Lever Blank Escutcheon"),
]

CVR_55_PRICES = {k: _exp55(v) for k, v in {
    "EO":    [5545, 5879, 5431, 5273, 6160, 6160],
    "DT":    [6447, 6781, 6343, 5986, 7088, 7088],
    "NL":    [6741, 7075, 6636, 6278, 7381, 7381],
    "NL-OP": [6135, 6469, 6021, 5771, 6750, 6750],
    "L":     [6963, 7281, 6849, 6517, 7700, 7562],
    "L-BE":  [6908, 7226, 6794, 6462, 7645, 7507],
    "TL":    [7649, 7983, 7637, 7022, 8382, 8290],
    "TL-BE": [7583, 7917, 7571, 6956, 8316, 8224],
}.items()}

# 55 CVR fire adders: EO/DT=$532, L/L-BE=$316, TL/TL-BE=per-finish
CVR_55_FIRE = {
    "EO": 532, "DT": 532, "L": 316, "L-BE": 316,
}
# TL/TL-BE fire adders per finish (6 cols → 9 keys via _exp55)
_TL_55_FIRE_RAW = [248, 248, 238, 295, 288, 222]  # per col
CVR_55_TL_FIRE = dict(zip(_FK55, _exp55(_TL_55_FIRE_RAW)))

WDC_55_PRICES = {k: _exp55(v) for k, v in {
    "EO":    [6258, 6527, 5665, 5494, 6625, 6625],
    "DT":    [7160, 7429, 6577, 6207, 7553, 7553],
    "NL":    [7454, 7723, 6870, 6499, 7846, 7846],
    "NL-OP": [6848, 7117, 6255, 5992, 7215, 7215],
    "L":     [7761, 8014, 7168, 6823, 8250, 8112],
    "L-BE":  [7706, 7959, 7113, 6768, 8195, 8057],
    "TL":    [8447, 8716, 7956, 7328, 8932, 8840],
    "TL-BE": [8381, 8650, 7890, 7262, 8866, 8774],
}.items()}

MORT_55_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
]

MORT_55_PRICES = {k: _exp55(v) for k, v in {
    "EO":    [4282, 4995, 4050, 3914, 4959, 4959],
    "DT":    [5184, 5897, 4962, 4627, 5887, 5887],
    "NL":    [5184, 5897, 4962, 4627, 5887, 5887],
    "L":     [5711, 6408, 5479, 5169, 6510, 6372],
    "L-BE":  [5645, 6342, 5413, 5103, 6444, 6306],
    "L-DT":  [5624, 6321, 5392, 5082, 6423, 6285],
}.items()}


def _seed_55_cvr(conn):
    """Seed 55 CVR with per-function fire adders."""
    f = fid(conn, "Von Duprin",
            "55 Series Concealed Vertical Rod (CVR)", "Exit Device",
            "{function} {finish}",
            "Von Duprin 55 Series CVR {function} {finish}")
    slot(conn, f, 1, "function", "Function / Trim", 1)
    slot(conn, f, 2, "finish",   "Finish",          1)
    slot(conn, f, 3, "fire",     "Fire Rating",     1)
    slot(conn, f, 4, "size",     "Device Size",     1)
    slot(conn, f, 5, "lever",    "Lever Design",    0)
    options(conn, f, "function", CVR_55_FUNCS)
    options(conn, f, "finish",   FINISHES_55)
    options(conn, f, "fire",     FIRE_OPTIONS)
    options(conn, f, "size",     SIZES)
    options(conn, f, "lever",    LEVERS)
    lever_funcs = {fv for fv, _ in CVR_55_FUNCS if fv.startswith("L")}
    for fv, _ in CVR_55_FUNCS:
        if fv not in lever_funcs:
            for lv, _ in LEVERS:
                rule(conn, f, "conflict", "function", fv, "lever", lv,
                     "Lever only applicable with L-type trims")
    # NL/NL-OP not available fire-rated (no fire rows in pricebook)
    for fc in ("NL", "NL-OP"):
        rule(conn, f, "conflict", "function", fc, "fire", "F",
             f"{fc} not available fire-rated")
    # Base pricing
    cnt = 0
    for func_key, row in CVR_55_PRICES.items():
        for fin, amt in zip(_FK55, row):
            price(conn, f, "function:finish", f"{func_key}:{fin}", amt, "base")
            cnt += 1
    # Per-function fire adders
    fire_cnt = 0
    for func_key, amt in CVR_55_FIRE.items():
        price(conn, f, "fire:function", f"F:{func_key}", amt, "adder")
        fire_cnt += 1
    # TL/TL-BE per-finish fire adders
    for func_key in ("TL", "TL-BE"):
        for fin, amt in CVR_55_TL_FIRE.items():
            price(conn, f, "fire:function:finish",
                  f"F:{func_key}:{fin}", amt, "adder")
            fire_cnt += 1
    price(conn, f, "size", "4FT", 30, "adder")
    total = cnt + fire_cnt + 1
    print(f"    55 CVR: {total} pricing rows ({cnt} base + {fire_cnt} fire + 1 size)")


def _seed_55(conn):
    """Seed 55 Series (Rim, CVR, WDC, Mort)."""
    _seed_simple_family(conn, "55 Series Rim Exit Device",
                        RIM_55_FUNCS, FINISHES_55, _FK55,
                        RIM_55_PRICES, None,
                        exit_only=tuple(k for k, _ in RIM_55_FUNCS))
    _seed_55_cvr(conn)
    _seed_simple_family(conn, "55 Series Wire/Door Cord (WDC)",
                        CVR_55_FUNCS, FINISHES_55, _FK55,
                        WDC_55_PRICES, 276, exit_only=())
    _seed_simple_family(conn, "55 Series Mortise Lock (Mort)",
                        MORT_55_FUNCS, FINISHES_55, _FK55,
                        MORT_55_PRICES, 352)


# ═══════════════════════════════════════════════════════════════
#  88 Series — 6 price columns → 10 finish options
#  Finish col order: 626, 613, 612, 606, 605/619/625/643E, 622/693
# ═══════════════════════════════════════════════════════════════

FINISHES_88 = [
    ("626",  "626 (US26D) Satin Chrome"),
    ("613",  "613 (US13) Oil Rubbed Bronze"),
    ("612",  "612 (US10) Satin Bronze"),
    ("606",  "606 (US4) Satin Brass"),
    ("605",  "605 (US3) Bright Brass"),
    ("619",  "619 (US15) Satin Nickel"),
    ("625",  "625 (US26) Bright Chrome"),
    ("643E", "643E Aged Bronze"),
    ("622",  "622 Flat Black"),
    ("693",  "693 Painted Dark Bronze"),
]
_FK88 = [v for v, _ in FINISHES_88]

def _exp88(r):
    """Expand 6-col → 10 keys (605/619/625/643E share col 4, 622/693 col 5)."""
    return r[:4] + [r[4]] * 4 + [r[5]] * 2

SVR_88_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("TP",    "TP - Thumbpiece"),
    ("TP-BE", "TP-BE - Thumbpiece Blank Escutcheon"),
    ("K",     "K - Key Lock"),
    ("K-BE",  "K-BE - Key Blank Escutcheon"),
    ("K-DT",  "K-DT - Key Dummy Trim"),
    ("K-NL",  "K-NL - Key Night Latch"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
    ("TL",    "TL - Thumbpiece Lever"),
    ("TL-BE", "TL-BE - Thumbpiece Lever Blank Escutcheon"),
]

SVR_88_PRICES = {k: _exp88(v) for k, v in {
    "EO":    [3328, 3554, 3188, 3027, 3913, 3913],
    "DT":    [3756, 4011, 3743, 3356, 4468, 4468],
    "NL":    [3803, 4061, 3852, 3480, 4577, 4577],
    "TP":    [3803, 4061, 3852, 3480, 4577, 4577],
    "TP-BE": [3803, 4061, 3852, 3480, 4577, 4577],
    "K":     [3883, 4150, 3896, 3480, 4621, 4621],
    "K-BE":  [3883, 4150, 3896, 3480, 4621, 4621],
    "K-DT":  [3883, 4150, 3896, 3480, 4621, 4621],
    "K-NL":  [3883, 4150, 3896, 3480, 4621, 4621],
    "L":     [4446, 4656, 4306, 3971, 5153, 5015],
    "L-BE":  [4389, 4599, 4249, 3914, 5096, 4958],
    "L-DT":  [4357, 4567, 4217, 3882, 5064, 4926],
    "TL":    [4960, 5215, 5039, 4394, 5764, 5672],
    "TL-BE": [4892, 5147, 4971, 4326, 5696, 5604],
}.items()}

# 88 CVR — fire-only (5 functions, all fire-rated)
CVR_88_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("TL",    "TL - Thumbpiece Lever"),
    ("TL-BE", "TL-BE - Thumbpiece Lever Blank Escutcheon"),
]

CVR_88_PRICES = {k: _exp88(v) for k, v in {
    "EO":    [4129, 4355, 3989, 3828, 4714, 4714],
    "L":     [5331, 5541, 5191, 4856, 6038, 5900],
    "L-BE":  [5276, 5486, 5136, 4801, 5983, 5845],
    "TL":    [5759, 6014, 5838, 5193, 6563, 6471],
    "TL-BE": [5693, 5948, 5772, 5127, 6497, 6405],
}.items()}

MORT_88_FUNCS = [
    ("EO",    "EO - Exit Only"),
    ("DT",    "DT - Dummy Trim"),
    ("NL",    "NL - Night Latch"),
    ("TP",    "TP - Thumbpiece"),
    ("TP-BE", "TP-BE - Thumbpiece Blank Escutcheon"),
    ("K",     "K - Key Lock"),
    ("K-BE",  "K-BE - Key Blank Escutcheon"),
    ("K-DT",  "K-DT - Key Dummy Trim"),
    ("L",     "L - Lever Trim"),
    ("L-BE",  "L-BE - Lever Blank Escutcheon"),
    ("L-DT",  "L-DT - Lever Dummy Trim"),
]

MORT_88_PRICES = {k: _exp88(v) for k, v in {
    "EO":    [3174, 3889, 3272, 3142, 3750, 3750],
    "DT":    [3602, 4346, 3827, 3471, 4305, 4305],
    "NL":    [3631, 4375, 3856, 3500, 4334, 4334],
    "TP":    [3649, 4396, 3936, 3595, 4414, 4414],
    "TP-BE": [3649, 4396, 3936, 3595, 4414, 4414],
    "K":     [3729, 4485, 3980, 3595, 4458, 4458],
    "K-BE":  [3729, 4485, 3980, 3595, 4458, 4458],
    "K-DT":  [3729, 4485, 3980, 3595, 4458, 4458],
    "L":     [4292, 4991, 4390, 4086, 4990, 4852],
    "L-BE":  [4235, 4934, 4333, 4029, 4933, 4795],
    "L-DT":  [4203, 4902, 4301, 3997, 4901, 4763],
}.items()}


def _seed_88_cvr(conn):
    """Seed 88 CVR — fire-only device (no exit-only option)."""
    f = fid(conn, "Von Duprin",
            "88 Series Concealed Vertical Rod (CVR) Fire", "Exit Device",
            "{function} {finish}",
            "Von Duprin 88 CVR Fire {function} {finish}")
    slot(conn, f, 1, "function", "Function / Trim", 1)
    slot(conn, f, 2, "finish",   "Finish",          1)
    slot(conn, f, 3, "size",     "Device Size",     1)
    slot(conn, f, 4, "lever",    "Lever Design",    0)
    options(conn, f, "function", CVR_88_FUNCS)
    options(conn, f, "finish",   FINISHES_88)
    options(conn, f, "size",     SIZES)
    options(conn, f, "lever",    LEVERS)
    lever_funcs = {fv for fv, _ in CVR_88_FUNCS if fv.startswith("L")}
    for fv, _ in CVR_88_FUNCS:
        if fv not in lever_funcs:
            for lv, _ in LEVERS:
                rule(conn, f, "conflict", "function", fv, "lever", lv,
                     "Lever only applicable with L-type trims")
    cnt = 0
    for func_key, row in CVR_88_PRICES.items():
        for fin, amt in zip(_FK88, row):
            price(conn, f, "function:finish", f"{func_key}:{fin}", amt, "base")
            cnt += 1
    price(conn, f, "size", "4FT", 30, "adder")
    total = cnt + 1
    print(f"    88 CVR Fire: {total} pricing rows ({cnt} base + 1 size)")


def _seed_88(conn):
    """Seed 88 Series (SVR, CVR, Mort)."""
    _seed_simple_family(conn, "88 Series Surface Vertical Rod (SVR)",
                        SVR_88_FUNCS, FINISHES_88, _FK88,
                        SVR_88_PRICES, 1172,
                        exit_only=("L-DT", "K-DT"))
    _seed_88_cvr(conn)
    _seed_simple_family(conn, "88 Series Mortise Lock (Mort)",
                        MORT_88_FUNCS, FINISHES_88, _FK88,
                        MORT_88_PRICES, 292,
                        exit_only=("L-DT", "K-DT"))


def seed(conn):
    """Main entry point — delete old shells and seed from pricebook."""
    # Remove old shell families with zero pricing
    for old_id in (10, 11, 132, 133):
        conn.execute("DELETE FROM hw_rules WHERE family_id=?", (old_id,))
        conn.execute("DELETE FROM hw_options WHERE family_id=?", (old_id,))
        conn.execute("DELETE FROM hw_slots WHERE family_id=?", (old_id,))
        conn.execute("DELETE FROM hw_pricing WHERE family_id=?", (old_id,))
        conn.execute("DELETE FROM hw_families WHERE id=?", (old_id,))

    _seed_9899(conn)
    _seed_9899_mortise(conn)
    _seed_33a_35a(conn)
    _seed_75(conn)
    _seed_78(conn)
    _seed_22(conn)
    _seed_9495(conn)
    _seed_55(conn)
    _seed_88(conn)
    print("  Von Duprin pricebook seeded (all series).")
