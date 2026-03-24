"""Seed Hager commercial hinge pricing from Pricebook #18 (Mar 2026).

Models:  BB1279 (Steel BB5K Std Wt), BB1168 (Steel BB5K Hvy Wt),
         BB1191 (Brass/SS BB5K Std Wt), BB1199 (Brass/SS BB5K Hvy Wt),
         700 (Steel PB 3K Std Wt), AB700 (Steel CB-AF 3K Std Wt),
         ECBB1100 (ECCO Steel BB Std Wt), 1251 (Steel Spring Hinge)
"""

from seed_helpers import fid, slot, options, price

# ── Hinge suffix options (ETW / NRP) ────────────────
ETW_NRP_OPTS = [
    ("ETW", "ETW - Electric Transfer Wire"),
    ("NRP", "NRP - Non-Removable Pin"),
]

# ── Common finish option lists ──────────────────────
STEEL_F = [
    ("LS",    "LS - Lustre Steel"),
    ("H2H",   "H2H - Mech Galvanized"),
    ("USP",   "USP - Prime Coat"),
    ("US3",   "US3 - Bright Brass"),
    ("US4",   "US4 - Satin Brass"),
    ("US10",  "US10 - Satin Bronze"),
    ("US10A", "US10A - Antique Bronze"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US15",  "US15 - Satin Nickel"),
    ("US26",  "US26 - Bright Chrome"),
    ("US26D", "US26D - Satin Chrome"),
    ("L1",    "L1 - Flat Black"),
]
# Keys only (with L1)
_SF12 = [v for v, _ in STEEL_F]
# Keys without L1
_SF11 = _SF12[:11]
# 700 series uses these (no H2H, no US15, no L1)
_700K = ["LS", "USP", "US3", "US4", "US10", "US10A", "US10B", "US26", "US26D"]
_700F = [(k, n) for k, n in STEEL_F if k in _700K]

# BB1191/BB1199 brass/stainless finishes
BRASS_F = [
    ("US3",   "US3 - Bright Brass"),
    ("US10",  "US10 - Satin Bronze"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US26",  "US26 - Bright Chrome"),
    ("US26D", "US26D - Satin Chrome"),
    ("US32",  "US32 - Bright Stainless"),
    ("US32D", "US32D - Satin Stainless"),
]
_BF7 = [v for v, _ in BRASS_F]


def _hinge(conn, name, desc_extra, cat, sizes_opts, finish_opts, pricing_data,
           finish_keys, model_prefix=None):
    """Create a hinge family with compound size:finish pricing."""
    pfx = model_prefix or name.split()[0]
    f = fid(conn, "Hager", name, cat,
            f"{pfx} {{size}} {{finish}}",
            f"Hager {desc_extra} {{size}} {{finish}}")
    slot(conn, f, 1, "size", "Size", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "suffix", "Options", 0)
    options(conn, f, "size", sizes_opts)
    options(conn, f, "finish", finish_opts)
    options(conn, f, "suffix", ETW_NRP_OPTS)
    for sz_key, prices in pricing_data:
        fk = finish_keys
        # some sizes have extra L1 column at end
        if len(prices) > len(fk):
            fk = fk + ["L1"] if "L1" not in fk else fk
        for fin, amt in zip(fk, prices):
            price(conn, f, "size:finish", f"{sz_key}:{fin}", amt)
    return f


# ── Size option lists ───────────────────────────────
SZ_BB1279 = [
    ("3.5x3.5",  '3-1/2" x 3-1/2"'),
    ("4x3.5",    '4" x 3-1/2"'),
    ("4x4",      '4" x 4"'),
    ("4.5x4",    '4-1/2" x 4"'),
    ("4.5x4.5",  '4-1/2" x 4-1/2"'),
    ("5x4",      '5" x 4"'),
    ("5x4.5",    '5" x 4-1/2"'),
    ("5x5",      '5" x 5"'),
    ("6x4.5",    '6" x 4-1/2"'),
    ("6x5",      '6" x 5"'),
    ("6x6",      '6" x 6"'),
]

SZ_BB1168 = [
    ("4.5x4",    '4-1/2" x 4"'),
    ("4.5x4.5",  '4-1/2" x 4-1/2"'),
    ("4.5x5",    '4-1/2" x 5"'),
    ("5x4",      '5" x 4"'),
    ("5x4.5",    '5" x 4-1/2"'),
    ("5x5",      '5" x 5"'),
    ("5x6",      '5" x 6"'),
    ("5x7",      '5" x 7"'),
    ("6x4.5",    '6" x 4-1/2"'),
    ("6x5",      '6" x 5"'),
    ("6x6",      '6" x 6"'),
    ("8x6",      '8" x 6"'),
    ("8x8",      '8" x 8"'),
]

SZ_700 = [
    ("3.5x3.5",  '3-1/2" x 3-1/2"'),
    ("4x4",      '4" x 4"'),
    ("4.5x4",    '4-1/2" x 4"'),
    ("4.5x4.5",  '4-1/2" x 4-1/2"'),
    ("5x4",      '5" x 4"'),
    ("5x4.5",    '5" x 4-1/2"'),
    ("5x5",      '5" x 5"'),
]

SZ_1251 = [
    ("3.5x3.5",  '3-1/2" x 3-1/2"'),
    ("4x4",      '4" x 4"'),
    ("4.5x4",    '4-1/2" x 4"'),
    ("4.5x4.5",  '4-1/2" x 4-1/2"'),
]


# ═══════════════════════════════════════════════════
#  BB1279 – Steel, BB5K, Full Mortise, Std Weight
# ═══════════════════════════════════════════════════
# Finishes per size: LS H2H USP US3 US4 US10 US10A US10B US15 US26 US26D [L1]
BB1279_DATA = [
    # 11 finishes
    ("3.5x3.5", [54.33, 87.98, 54.33, 70.40, 54.33, 54.33, 70.40, 70.40, 70.40, 70.40, 54.84]),
    ("4x3.5",   [64.03, 95.23, 58.48, 84.56, 58.48, 64.03, 84.56, 84.56, 84.56, 84.56, 72.77]),
    # 12 finishes (+L1)
    ("4x4",     [45.28, 68.40, 39.65, 54.77, 39.65, 45.28, 54.77, 54.77, 54.77, 54.77, 46.99, 39.65]),
    ("4.5x4",   [36.09, 54.54, 25.47, 43.62, 36.09, 36.09, 43.62, 43.62, 43.62, 43.62, 24.54, 25.47]),
    ("4.5x4.5", [36.09, 54.54, 25.47, 43.62, 36.09, 36.09, 43.62, 43.62, 43.62, 43.62, 23.76, 36.09]),
    # 11 finishes
    ("5x4",     [70.50, 111.63, 70.50, 89.28, 70.50, 70.50, 89.28, 89.28, 89.28, 89.28, 69.07]),
    ("5x4.5",   [70.50, 111.63, 70.50, 89.28, 70.50, 70.50, 89.28, 89.28, 89.28, 89.28, 69.07]),
    ("5x5",     [70.50, 111.63, 70.50, 89.28, 70.50, 70.50, 89.28, 89.28, 89.28, 89.28, 69.07, 70.50]),
    ("6x4.5",   [167.58, 255.39, 167.58, 225.38, 167.58, 167.58, 225.38, 225.38, 225.38, 225.38, 193.54]),
    ("6x5",     [167.58, 255.39, 167.58, 225.38, 167.58, 167.58, 225.38, 225.38, 225.38, 225.38, 193.54]),
    ("6x6",     [167.58, 255.39, 167.58, 225.38, 167.58, 167.58, 225.38, 225.38, 225.38, 225.38, 193.54]),
]


# ═══════════════════════════════════════════════════
#  BB1168 – Steel, BB5K, Full Mortise, Heavy Weight
# ═══════════════════════════════════════════════════
# Finishes: LS USP US3 US4 US10 US10A US10B US15 US26 US26D [L1]
_1168K = ["LS", "USP", "US3", "US4", "US10", "US10A", "US10B", "US15", "US26", "US26D"]
_1168F = [(k, n) for k, n in STEEL_F if k in _1168K]

BB1168_DATA = [
    ("4.5x4",   [82.48, 82.48, 97.94, 78.36, 82.48, 97.94, 97.94, 97.94, 97.94, 70.56]),
    ("4.5x4.5", [82.48, 82.48, 97.94, 78.36, 82.48, 97.94, 97.94, 97.94, 97.94, 70.56]),
    # 4.5x5 has L1
    ("4.5x5",   [92.38, 92.38, 109.70, 87.76, 92.38, 109.70, 109.70, 109.70, 109.70, 79.03, 82.48]),
    ("5x4",     [106.10, 104.53, 110.50, 88.39, 106.10, 110.50, 110.50, 110.50, 110.50, 90.99]),
    ("5x4.5",   [106.10, 104.53, 110.50, 88.39, 106.10, 110.50, 110.50, 110.50, 110.50, 90.99]),
    ("5x5",     [106.10, 104.53, 110.50, 88.39, 106.10, 110.50, 110.50, 110.50, 110.50, 90.99]),
    ("5x6",     [132.63, 130.67, 138.12, 110.49, 132.63, 138.12, 138.12, 138.12, 138.12, 113.73]),
    ("5x7",     [159.15, 156.80, 165.75, 132.59, 159.15, 165.75, 165.75, 165.75, 165.75, 136.48]),
    ("6x4.5",   [293.68, 284.18, 362.11, 289.70, 293.68, 362.11, 362.11, 362.11, 362.11, 273.19]),
    ("6x5",     [293.68, 284.18, 362.11, 289.70, 293.68, 362.11, 362.11, 362.11, 362.11, 273.19]),
    ("6x6",     [293.68, 284.18, 362.11, 289.70, 293.68, 362.11, 362.11, 362.11, 362.11, 273.19]),
    ("8x6",     [656.22, 656.22, 836.36, None, 678.28, 836.36, 836.36, 836.36, 836.36, 710.55]),
    ("8x8",     [656.22, 656.22, 836.36, None, 678.28, 836.36, 836.36, 836.36, 836.36, 710.55]),
]


# ═══════════════════════════════════════════════════
#  700 – Steel, PB 3K, Full Mortise, Standard Weight
# ═══════════════════════════════════════════════════
# Finishes: LS USP US3 US4 US10 US10A US10B US26 US26D
P700_DATA = [
    ("3.5x3.5", [17.45, 12.98, 25.96, 17.45, 17.45, 25.96, 25.96, 25.96, 21.70]),
    ("4x4",     [20.57, 15.96, 29.43, 20.57, 20.57, 29.43, 29.43, 29.43, 26.52]),
    ("4.5x4",   [19.64, 16.81, 33.61, 19.64, 19.64, 33.61, 33.61, 33.61, 21.35]),
    ("4.5x4.5", [19.64, 16.81, 33.61, 19.64, 19.64, 33.61, 33.61, 33.61, 21.35]),
    ("5x4",     [67.59, 55.61, 91.34, 67.59, 67.59, 91.34, 91.34, 91.34, 62.62]),
    ("5x4.5",   [67.59, 55.61, 91.34, 67.59, 67.59, 91.34, 91.34, 91.34, 62.62]),
    ("5x5",     [53.15, 43.69, 66.11, 43.69, 53.15, 72.01, 72.01, 72.01, 49.25]),
]


# ═══════════════════════════════════════════════════
#  AB700 – Steel, CB-AF 3K, Full Mortise, Std Weight
# ═══════════════════════════════════════════════════
# Finishes: LS USP US3 US4 US10 US10A US10B US26 US26D [L1 for 4.5x4.5+]
AB700_DATA = [
    ("3.5x3.5", [51.99, 45.45, 62.84, 45.45, 51.99, 62.84, 62.84, 62.84, 53.97]),
    ("4x4",     [51.99, 45.45, 62.84, 45.45, 51.99, 62.84, 62.84, 62.84, 53.97]),
    ("4.5x4",   [43.33, 30.56, 52.34, 43.33, 43.33, 52.34, 52.34, 52.34, 29.43]),
    ("4.5x4.5", [43.33, 30.56, 52.34, 43.33, 43.33, 52.34, 52.34, 52.34, 29.43, 45.45]),
    ("5x4",     [84.61, 84.61, 107.09, 84.61, 84.61, 107.09, 107.09, 107.09, 82.76]),
    ("5x4.5",   [84.61, 84.61, 107.09, 84.61, 84.61, 107.09, 107.09, 107.09, 82.76]),
    ("5x5",     [84.61, 84.61, 107.09, 84.61, 84.61, 107.09, 107.09, 107.09, 82.76]),
]


# ═══════════════════════════════════════════════════
#  ECBB1100 – ECCO Steel BB, Full Mortise, Std Wt
# ═══════════════════════════════════════════════════
# Limited sizes and finishes from ECCO section
_EC_SIZES = [
    ("4.5x4",   '4-1/2" x 4"'),
    ("4.5x4.5", '4-1/2" x 4-1/2"'),
]
_EC_FINISHES = [
    ("USP",   "USP - Prime Coat"),
    ("US3",   "US3 - Bright Brass"),
    ("US4",   "US4 - Satin Brass"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US15",  "US15 - Satin Nickel"),
    ("US26",  "US26 - Bright Chrome"),
    ("US26D", "US26D - Satin Chrome"),
    ("L1",    "L1 - Flat Black"),
]
_ECK = [v for v, _ in _EC_FINISHES]
# NRP variant data (the standard ECBB1100 NRP)
ECBB1100_DATA = [
    # 4.5x4: US26D only listed as single price
    ("4.5x4",   [None, None, None, None, None, None, 23.27, None]),
    # 4.5x4.5: USP US3 US4 US10B --  -- US26D L1
    ("4.5x4.5", [22.69, 40.07, 30.10, 40.07, None, 40.07, 22.54, 22.69]),
]


# ═══════════════════════════════════════════════════
#  1251 – Steel Spring Hinge, 1/4" Radius, Std Wt
# ═══════════════════════════════════════════════════
_1251K = ["USP", "US3", "US4", "US10", "US10A", "US10B", "US26D"]
_1251F = [(k, n) for k, n in STEEL_F if k in _1251K]

P1251_DATA = [
    ("3.5x3.5", [53.44, 67.24, 53.44, 53.44, 67.24, 67.24, 61.70]),
    ("4x4",     [68.08, 90.13, 68.08, 68.08, 90.13, 90.13, 80.98]),
    ("4.5x4",   [109.64, 147.44, 132.40, 132.40, 147.44, 147.44, 142.54]),
    ("4.5x4.5", [109.64, 147.44, 132.40, 132.40, 147.44, 147.44, 142.54]),
]


# ═══════════════════════════════════════════════════
#  BB1191 – Brass/SS, BB5K, Full Mortise, Std Weight
# ═══════════════════════════════════════════════════
SZ_BB1191 = [
    ("4x4",      '4" x 4"'),
    ("4.5x4",    '4-1/2" x 4"'),
    ("4.5x4.5",  '4-1/2" x 4-1/2"'),
    ("5x4",      '5" x 4"'),
    ("5x4.5",    '5" x 4-1/2"'),
    ("5x5",      '5" x 5"'),
]
# Finishes: US3 US10 US10B US26 US26D US32 US32D
BB1191_DATA = [
    ("4x4",     [309.11, 251.36, 309.11, 248.18, 288.80, 244.75, 288.80]),
    ("4.5x4",   [309.11, 251.36, 309.11, 248.18, 288.80, 244.75, 288.80]),
    ("4.5x4.5", [309.11, 251.36, 309.11, 248.18, 288.80, 244.75, 288.80]),
    ("5x4",     [434.89, 434.89, 434.89, 434.89, 313.32, 309.10, 313.32]),
    ("5x4.5",   [434.89, 434.89, 434.89, 434.89, 313.32, 309.10, 313.32]),
    ("5x5",     [434.89, 434.89, 434.89, 434.89, 313.32, 309.10, 313.32]),
]


# ═══════════════════════════════════════════════════
#  BB1199 – Brass/SS, BB5K, Full Mortise, Heavy Wt
# ═══════════════════════════════════════════════════
SZ_BB1199 = [
    ("4.5x4",    '4-1/2" x 4"'),
    ("4.5x4.5",  '4-1/2" x 4-1/2"'),
    ("5x4",      '5" x 4"'),
    ("5x4.5",    '5" x 4-1/2"'),
    ("5x5",      '5" x 5"'),
    ("6x4.5",    '6" x 4-1/2"'),
    ("6x5",      '6" x 5"'),
    ("6x6",      '6" x 6"'),
]
BB1199_DATA = [
    ("4.5x4",   [456.51, 421.00, 456.51, 456.51, 370.12, 369.02, 366.09]),
    ("4.5x4.5", [456.51, 421.00, 456.51, 456.51, 370.12, 369.02, 366.09]),
    ("5x4",     [571.70, 527.24, 571.70, 571.70, 463.51, 462.13, 458.47]),
    ("5x4.5",   [571.70, 527.24, 571.70, 571.70, 463.51, 462.13, 458.47]),
    ("5x5",     [571.70, 527.24, 571.70, 571.70, 463.51, 462.13, 458.47]),
    ("6x4.5",   [571.70, 527.24, 571.70, 571.70, 463.51, 462.13, 458.47]),
    ("6x5",     [571.70, 527.24, 571.70, 571.70, 463.51, 462.13, 458.47]),
    ("6x6",     [571.70, 527.24, 571.70, 571.70, 463.51, 462.13, 458.47]),
]


# ═══════════════════════════════════════════════════
def seed(conn):
    _seed_bb1279(conn)
    _seed_bb1168(conn)
    _seed_bb1191(conn)
    _seed_bb1199(conn)
    _seed_700(conn)
    _seed_ab700(conn)
    _seed_ecbb1100(conn)
    _seed_1251(conn)
    print("  Hager Hinges (8 families) seeded.")


def _seed_bb1279(conn):
    _hinge(conn,
           "BB1279 Full Mortise Hinge",
           "BB1279 Steel BB5K Full Mortise Std Wt",
           "Hinge",
           SZ_BB1279, STEEL_F, BB1279_DATA, _SF11)


def _seed_bb1168(conn):
    f = fid(conn, "Hager", "BB1168 Full Mortise Hinge", "Hinge",
            "BB1168 {size} {finish}",
            "Hager BB1168 Steel BB5K Full Mortise Hvy Wt {size} {finish}")
    slot(conn, f, 1, "size", "Size", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "suffix", "Options", 0)
    options(conn, f, "size", SZ_BB1168)
    options(conn, f, "finish", _1168F + [("L1", "L1 - Flat Black")])
    options(conn, f, "suffix", ETW_NRP_OPTS)
    fk = [v for v, _ in _1168F]
    for sz, prices in BB1168_DATA:
        keys = fk if len(prices) == len(fk) else fk + ["L1"]
        for fin, amt in zip(keys, prices):
            if amt is not None:
                price(conn, f, "size:finish", f"{sz}:{fin}", amt)


def _seed_bb1191(conn):
    _hinge(conn,
           "BB1191 Full Mortise Hinge",
           "BB1191 Brass/SS BB5K Full Mortise Std Wt",
           "Hinge",
           SZ_BB1191, BRASS_F, BB1191_DATA, _BF7)


def _seed_bb1199(conn):
    _hinge(conn,
           "BB1199 Full Mortise Hinge",
           "BB1199 Brass/SS BB5K Full Mortise Hvy Wt",
           "Hinge",
           SZ_BB1199, BRASS_F, BB1199_DATA, _BF7)


def _seed_700(conn):
    _hinge(conn,
           "700 Full Mortise Hinge",
           "700 Steel PB 3K Full Mortise Std Wt",
           "Hinge",
           SZ_700, _700F, P700_DATA, _700K)


def _seed_ab700(conn):
    _hinge(conn,
           "AB700 Full Mortise Anchor Hinge",
           "AB700 Steel CB-AF 3K Full Mortise Std Wt",
           "Hinge",
           SZ_700, _700F + [("L1", "L1 - Flat Black")], AB700_DATA, _700K)


def _seed_ecbb1100(conn):
    f = fid(conn, "Hager", "ECBB1100 Full Mortise Hinge", "Hinge",
            "ECBB1100 {size} {finish}",
            "Hager ECBB1100 ECCO Steel BB Full Mortise Std Wt {size} {finish}")
    slot(conn, f, 1, "size", "Size", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "suffix", "Options", 0)
    options(conn, f, "size", _EC_SIZES)
    options(conn, f, "finish", _EC_FINISHES)
    options(conn, f, "suffix", ETW_NRP_OPTS)
    for sz, prices in ECBB1100_DATA:
        for fin, amt in zip(_ECK, prices):
            if amt is not None:
                price(conn, f, "size:finish", f"{sz}:{fin}", amt)


def _seed_1251(conn):
    f = fid(conn, "Hager", "1251 Spring Hinge", "Hinge",
            "1251 {size} {finish}",
            "Hager 1251 Steel Spring Hinge 1/4\" Radius {size} {finish}")
    slot(conn, f, 1, "size", "Size", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "suffix", "Options", 0)
    options(conn, f, "size", SZ_1251)
    options(conn, f, "finish", _1251F)
    options(conn, f, "suffix", ETW_NRP_OPTS)
    for sz, prices in P1251_DATA:
        for fin, amt in zip(_1251K, prices):
            if amt is not None:
                price(conn, f, "size:finish", f"{sz}:{fin}", amt)
