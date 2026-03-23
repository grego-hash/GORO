"""Seed LCN Concealed door closer pricing.

Source: LCN Price Book 16, effective February 27, 2026.
Families: 2010, 2030, 3030, 3130, 5010, 5030, 6030
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk

PC = [
    ("622", "622 - MTBLK"),  ("689", "689 - AL"),    ("690", "690 - STAT"),
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


def _tier_setup(conn, f, order, plated, premium):
    slot(conn, f, order, "finish_tier", "Finish Tier", 1)
    options(conn, f, "finish_tier", TIERS)
    price_bulk(conn, f, "finish_tier", [
        ("POWDER_COAT", 0.00), ("PLATED", plated), ("PLATED_PREM", premium),
    ], price_type="adder")
    for v, _ in PL:
        rule(conn, f, "conflict", "finish_tier", "POWDER_COAT", "finish", v,
             "Plated finish N/A for Powder Coat")
    for v, _ in PC:
        rule(conn, f, "conflict", "finish_tier", "PLATED", "finish", v,
             "Powder Coat finish N/A for Plated")
        rule(conn, f, "conflict", "finish_tier", "PLATED_PREM", "finish", v,
             "Powder Coat finish N/A for Plated Premium")


def seed(conn):
    _seed_2010(conn)
    _seed_2030(conn)
    _seed_3030(conn)
    _seed_3130(conn)
    _seed_5010(conn)
    _seed_5030(conn)
    _seed_6030(conn)
    print("  LCN Concealed (7 families) seeded.")


# ═══════════════════════════════════════════════════════════════
# 2010 Series — heavy duty concealed, track
# ═══════════════════════════════════════════════════════════════
def _seed_2010(conn):
    f = fid(conn, "LCN", "2010 Series Concealed Closer", "Concealed Closer",
            "2011 {config} {finish_tier} {finish}",
            "LCN 2011 Concealed {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 817.00, 1058.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("STDTRK", "STDTRK - Standard Track"),
        ("H",      "H - Hold Open Track"),
        ("BUMP",   "BUMP - Bumper Track"),
        ("HBUMP",  "HBUMP - Hold Open Bumper Track"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("STDTRK", 1085.00), ("H", 1125.00),
        ("BUMP", 1093.00), ("HBUMP", 1141.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 2030 Series PACER — concealed, narrow transom
# ═══════════════════════════════════════════════════════════════
def _seed_2030(conn):
    f = fid(conn, "LCN", "2030 Series Concealed Closer", "Concealed Closer",
            "2031 {config} {finish_tier} {finish}",
            "LCN 2031 PACER Concealed {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 815.00, 1057.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("STDTRK", "STDTRK - Standard Track"),
        ("H",      "H - Hold Open Track"),
        ("BUMP",   "BUMP - Bumper Track"),
        ("HBUMP",  "HBUMP - Hold Open Bumper Track"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("STDTRK", 1806.00), ("H", 1846.00),
        ("BUMP", 1814.00), ("HBUMP", 1862.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 3030 Series — concealed in door, double lever arm
# ═══════════════════════════════════════════════════════════════
def _seed_3030(conn):
    f = fid(conn, "LCN", "3030 Series Concealed Closer", "Concealed Closer",
            "3031 {config} {finish_tier} {finish}",
            "LCN 3031 Concealed {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 353.00, 401.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM", "REGARM - Regular Arm"),
        ("H",      "H - Hold Open"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("REGARM", 752.00), ("H", 752.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 3130 Series — concealed in door, single lever track
# ═══════════════════════════════════════════════════════════════
def _seed_3130(conn):
    f = fid(conn, "LCN", "3130 Series Concealed Closer", "Concealed Closer",
            "3131 {config} {finish_tier} {finish}",
            "LCN 3131 Concealed {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 353.00, 401.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("STDTRACK", "STDTRACK - Standard Track"),
        ("H",        "H - Hold Open Track"),
        ("BUMP",     "BUMP - Bumper Track"),
        ("HBUMP",    "HBUMP - Hold Open Bumper Track"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("STDTRACK", 910.00), ("H", 950.00),
        ("BUMP", 918.00), ("HBUMP", 966.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 5010 Series — heavy duty concealed, double lever, CYLDEL
# ═══════════════════════════════════════════════════════════════
def _seed_5010(conn):
    f = fid(conn, "LCN", "5010 Series Concealed Closer", "Concealed Closer",
            "5011 {config} {finish_tier} {finish}",
            "LCN 5011 Concealed {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 818.00, 1058.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [
        ("REGARM", "REGARM - Regular Arm"),
        ("H",      "H - Hold Open"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLDEL", "Delayed Action (+$71, N/A for 5016)"),
    ])
    price_bulk(conn, f, "config", [
        ("REGARM", 1006.00), ("H", 1006.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLDEL", 71.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 5030 Series PACER — concealed, narrow transom, double lever
# ═══════════════════════════════════════════════════════════════
def _seed_5030(conn):
    f = fid(conn, "LCN", "5030 Series Concealed Closer", "Concealed Closer",
            "5031 {config} {finish_tier} {finish}",
            "LCN 5031 PACER Concealed {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 815.00, 1057.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM", "REGARM - Regular Arm"),
        ("H",      "H - Hold Open"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("REGARM", 1687.00), ("H", 1687.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 6030 Series PACER — concealed, double-acting, narrow transom
# ═══════════════════════════════════════════════════════════════
def _seed_6030(conn):
    f = fid(conn, "LCN", "6030 Series Concealed Closer", "Concealed Closer",
            "6031 {config} {finish_tier} {finish}",
            "LCN 6031 PACER Double-Acting {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 818.00, 1058.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("BUMP",  "BUMP - Bumper Track"),
        ("HBUMP", "HBUMP - Hold Open Bumper Track"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("BUMP", 2173.00), ("HBUMP", 2221.00),
    ], price_type="base")
