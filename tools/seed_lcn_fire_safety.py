"""Seed LCN Fire / Life Safety closer and holder pricing.

Source: LCN Price Book 16, effective February 27, 2026.
Families: 3130SE, 4040SE, 4040SEH, 2310ME, 4310ME, 4410ME,
          4310HSA, 4410HSA, SEM7800
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk

# ── Finishes (Fire/Life Safety series omit 622-MTBLK) ───────────
PC_FIRE = [
    ("689", "689 - AL"),    ("690", "690 - STAT"),
    ("691", "691 - LTBRZ"),  ("693", "693 - GLBLK"), ("695", "695 - DKBRZ"),
    ("696", "696 - BRASS"),
]
PL = [
    ("616", "616 - US11"),  ("632", "632 - US3"),  ("633", "633 - US4"),
    ("639", "639 - US10"),  ("646", "646 - US15"), ("651", "651 - US26"),
    ("652", "652 - US26D"),
]
TIERS = [
    ("POWDER_COAT", "Powder Coat"),
    ("PLATED",      "Plated (incl. Metal Cover)"),
    ("PLATED_PREM", "Plated Premium"),
]


def _tier_setup(conn, f, order, plated, premium, pc=None):
    pc_list = pc or PC_FIRE
    slot(conn, f, order, "finish_tier", "Finish Tier", 1)
    options(conn, f, "finish_tier", TIERS)
    price_bulk(conn, f, "finish_tier", [
        ("POWDER_COAT", 0.00), ("PLATED", plated), ("PLATED_PREM", premium),
    ], price_type="adder")
    for v, _ in PL:
        rule(conn, f, "conflict", "finish_tier", "POWDER_COAT", "finish", v,
             "Plated finish N/A for Powder Coat")
    for v, _ in pc_list:
        rule(conn, f, "conflict", "finish_tier", "PLATED", "finish", v,
             "Powder Coat finish N/A for Plated")
        rule(conn, f, "conflict", "finish_tier", "PLATED_PREM", "finish", v,
             "Powder Coat finish N/A for Plated Premium")


def seed(conn):
    _seed_3130se(conn)
    _seed_4040se(conn)
    _seed_4040seh(conn)
    _seed_2310me(conn)
    _seed_4310me(conn)
    _seed_4410me(conn)
    _seed_4310hsa(conn)
    _seed_4410hsa(conn)
    _seed_sem7800(conn)
    print("  LCN Fire/Life Safety (9 families) seeded.")


# ═══════════════════════════════════════════════════════════════
# 3130SE SENTRONIC — concealed closer/holder
# ═══════════════════════════════════════════════════════════════
def _seed_3130se(conn):
    f = fid(conn, "LCN", "3130SE Series Closer/Holder", "Fire/Life Safety Closer",
            "3133SE {config} {finish_tier} {finish}",
            "LCN 3133SE SENTRONIC {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 350.00, 397.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "voltage", "Voltage", 1)
    options(conn, f, "config", [
        ("STDTRK", "STDTRK - Standard Track"),
        ("LONG",   "LONG - Long Track"),
    ])
    options(conn, f, "finish", PC_FIRE + PL)
    options(conn, f, "voltage", [
        ("24V",  "24 Volt"), ("120V", "120 Volt"),
    ])
    price_bulk(conn, f, "config", [
        ("STDTRK", 1465.00), ("LONG", 1478.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 4040SE SENTRONIC — surface closer/holder
# ═══════════════════════════════════════════════════════════════
def _seed_4040se(conn):
    f = fid(conn, "LCN", "4040SE Series Closer/Holder", "Fire/Life Safety Closer",
            "4040SE {config} {finish_tier} {finish}",
            "LCN 4040SE SENTRONIC {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 655.00, 779.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "voltage", "Voltage", 1)
    slot(conn, f, 5, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("STDTRKARM-STDTRK", "Std Track Arm + Std Track"),
        ("STDTRKARM-LONG",   "Std Track Arm + Long Track"),
        ("DE-STDTRK",        "Double Egress + Std Track"),
    ])
    options(conn, f, "finish", PC_FIRE + PL)
    options(conn, f, "voltage", [
        ("24V", "24 Volt"), ("120V", "120 Volt"),
    ])
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("STDTRKARM-STDTRK", 1480.00),
        ("STDTRKARM-LONG", 1480.00),
        ("DE-STDTRK", 1556.00),
    ], price_type="base")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4040SEH SENTRONIC — holder only (requires separate closer)
# ═══════════════════════════════════════════════════════════════
def _seed_4040seh(conn):
    f = fid(conn, "LCN", "4040SEH Series Holder", "Fire/Life Safety Closer",
            "4040SEH {finish_tier} {finish}",
            "LCN 4040SEH SENTRONIC Holder {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 349.00, 395.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "voltage", "Voltage", 1)
    options(conn, f, "config", [("STD", "Standard")])
    options(conn, f, "finish", PC_FIRE + PL)
    options(conn, f, "voltage", [
        ("24V", "24 Volt"), ("120V", "120 Volt"),
    ])
    price_bulk(conn, f, "config", [("STD", 938.00)], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 2310ME SENTRONIC — concealed electrically controlled
# ═══════════════════════════════════════════════════════════════
def _seed_2310me(conn):
    f = fid(conn, "LCN", "2310ME Series Closer/Holder", "Fire/Life Safety Closer",
            "2314ME {finish_tier} {finish}",
            "LCN 2314ME SENTRONIC {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 584.00, 727.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "voltage", "Voltage", 1)
    slot(conn, f, 5, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [("STD", "Standard (2314ME)")])
    options(conn, f, "finish", PC_FIRE + PL)
    options(conn, f, "voltage", [
        ("24V", "24 Volt"), ("120V", "120 Volt"),
    ])
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLB80", "Bypass Hold Open to 80° (+$71)"),
        ("CYLB140", "Bypass Hold Open to 140° (+$134)"),
    ])
    price_bulk(conn, f, "config", [("STD", 2027.00)], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLB80", 71.00), ("CYLB140", 134.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4310ME SENTRONIC — surface electrically controlled, SF/DE arm
# ═══════════════════════════════════════════════════════════════
def _seed_4310me(conn):
    f = fid(conn, "LCN", "4310ME Series Closer/Holder", "Fire/Life Safety Closer",
            "4314ME {config} {finish_tier} {finish}",
            "LCN 4314ME SENTRONIC {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 626.00, 1034.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "voltage", "Voltage", 1)
    slot(conn, f, 5, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [
        ("SF", "SF - Swing Free Arm (default)"),
        ("DE", "DE - Double Egress Arm (+$78)"),
    ])
    options(conn, f, "finish", PC_FIRE + PL)
    options(conn, f, "voltage", [
        ("24V", "24 Volt"), ("120V", "120 Volt"),
    ])
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLB80", "Bypass Hold Open to 80° (+$134)"),
        ("CYLB140", "Bypass Hold Open to 140° (+$134)"),
    ])
    price_bulk(conn, f, "config", [
        ("SF", 2075.00), ("DE", 2153.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLB80", 134.00), ("CYLB140", 134.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4410ME SENTRONIC — surface double lever, electrically controlled
# ═══════════════════════════════════════════════════════════════
def _seed_4410me(conn):
    f = fid(conn, "LCN", "4410ME Series Closer/Holder", "Fire/Life Safety Closer",
            "4414ME {config} {finish_tier} {finish}",
            "LCN 4414ME SENTRONIC {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 631.00, 1040.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "voltage", "Voltage", 1)
    slot(conn, f, 5, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [
        ("REGARM", "REGARM - Regular Arm"),
        ("LONG",   "LONG - Long Arm"),
    ])
    options(conn, f, "finish", PC_FIRE + PL)
    options(conn, f, "voltage", [
        ("24V", "24 Volt"), ("120V", "120 Volt"),
    ])
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLB80", "Bypass Hold Open to 80° (+$134)"),
        ("CYLB140", "Bypass Hold Open to 140° (+$134)"),
    ])
    price_bulk(conn, f, "config", [
        ("REGARM", 1961.00), ("LONG", 1969.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLB80", 134.00), ("CYLB140", 134.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4310HSA SENTRONIC — high traffic scanner, track arm
# ═══════════════════════════════════════════════════════════════
def _seed_4310hsa(conn):
    f = fid(conn, "LCN", "4310HSA Series Closer/Holder", "Fire/Life Safety Closer",
            "4311HSA {config} {finish_tier} {finish}",
            "LCN 4311HSA SENTRONIC {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 626.00, 1034.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("STDTRKARM", "Standard Track Arm"),
        ("DE",        "DE - Double Egress Arm (+$78)"),
    ])
    options(conn, f, "finish", PC_FIRE + PL)
    price_bulk(conn, f, "config", [
        ("STDTRKARM", 2208.00), ("DE", 2286.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 4410HSA SENTRONIC — high traffic scanner, double lever
# ═══════════════════════════════════════════════════════════════
def _seed_4410hsa(conn):
    f = fid(conn, "LCN", "4410HSA Series Closer/Holder", "Fire/Life Safety Closer",
            "4412HSA {config} {finish_tier} {finish}",
            "LCN 4412HSA SENTRONIC {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 631.00, 1040.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM", "REGARM - Regular Arm"),
        ("LONG",   "LONG - Long Arm"),
    ])
    options(conn, f, "finish", PC_FIRE + PL)
    price_bulk(conn, f, "config", [
        ("REGARM", 2094.00), ("LONG", 2101.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# SEM7800 Series — electromagnetic door holding magnets
# ═══════════════════════════════════════════════════════════════
def _seed_sem7800(conn):
    f = fid(conn, "LCN", "SEM7800 Series Magnet", "Fire/Life Safety Closer",
            "SEM{config} {finish}",
            "LCN SEM{config} Door Holding Magnet {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("7820", "SEM7820 - Floor Mount"),
        ("7830", "SEM7830 - Recessed Wall Mount"),
        ("7840", "SEM7840 - Surface Wall Mount"),
        ("7850", "SEM7850 - Bracket Mount"),
    ])
    options(conn, f, "finish", [
        ("689", "689 - AL"), ("695", "695 - DKBRZ"),
    ])
    price_bulk(conn, f, "config", [
        ("7820", 1160.00), ("7830", 656.00),
        ("7840", 656.00), ("7850", 656.00),
    ], price_type="base")
