"""Seed LCN High Security closer pricing.

Source: LCN Price Book 16, effective February 27, 2026.
Families: 2210, 4210, 4210T, 4510, 4510T
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
    _seed_2210(conn)
    _seed_4210(conn)
    _seed_4210t(conn)
    _seed_4510(conn)
    _seed_4510t(conn)
    print("  LCN High Security (5 families) seeded.")


# ═══════════════════════════════════════════════════════════════
# 2210 Series — concealed high security
# ═══════════════════════════════════════════════════════════════
def _seed_2210(conn):
    f = fid(conn, "LCN", "2210 Series High Security Closer", "High Security Closer",
            "2213 {config} {finish_tier} {finish}",
            "LCN 2213 High Security Concealed {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 817.00, 1057.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [
        ("STD", "Standard (2213/2214/2215)"),
        ("DPS", "DPS - Door Position Switch"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLAVB", "Advanced Variable Back Check (+$39)"),
    ])
    price_bulk(conn, f, "config", [
        ("STD", 1509.00), ("DPS", 1685.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLAVB", 39.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4210 (4211/4216) — surface high security, parallel arm
# ═══════════════════════════════════════════════════════════════
def _seed_4210(conn):
    f = fid(conn, "LCN", "4210 Series High Security Closer", "High Security Closer",
            "4211 {config} {finish_tier} {finish}",
            "LCN 4211 High Security {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 633.00, 759.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [
        ("EDA",   "EDA - Extra Duty Arm"),
        ("CUSH",  "CUSH - Cushion Arm"),
        ("HCUSH", "HCUSH - Hold Open Cushion Arm"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLAVB", "Advanced Variable Back Check (+$39)"),
        ("CYLDEL", "Delayed Action (+$71, 4211 only)"),
    ])
    price_bulk(conn, f, "config", [
        ("EDA", 914.00), ("CUSH", 961.00), ("HCUSH", 1073.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLAVB", 39.00), ("CYLDEL", 71.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4210T — surface high security, track
# ═══════════════════════════════════════════════════════════════
def _seed_4210t(conn):
    f = fid(conn, "LCN", "4210T Series High Security Closer", "High Security Closer",
            "4211T {finish_tier} {finish}",
            "LCN 4211T High Security Track {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 633.00, 759.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [("STD", "Standard (4211T/4213T/4214T)")])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLAVB", "Advanced Variable Back Check (+$39)"),
        ("CYLDEL", "Delayed Action (+$71, 4211T only)"),
    ])
    price_bulk(conn, f, "config", [("STD", 1090.00)], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLAVB", 39.00), ("CYLDEL", 71.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4510 (4511/4516) — surface high security, double lever
# ═══════════════════════════════════════════════════════════════
def _seed_4510(conn):
    f = fid(conn, "LCN", "4510 Series High Security Closer", "High Security Closer",
            "4511 {finish_tier} {finish}",
            "LCN 4511 High Security {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 631.00, 759.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [("STD", "Standard EDA (4511/4516)")])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLAVB", "Advanced Variable Back Check (+$39)"),
        ("CYLDEL", "Delayed Action (+$71, 4511 only)"),
    ])
    price_bulk(conn, f, "config", [("STD", 914.00)], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLAVB", 39.00), ("CYLDEL", 71.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4510T — surface high security, track
# ═══════════════════════════════════════════════════════════════
def _seed_4510t(conn):
    f = fid(conn, "LCN", "4510T Series High Security Closer", "High Security Closer",
            "4511T {finish_tier} {finish}",
            "LCN 4511T High Security Track {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 633.00, 759.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [("STD", "Standard (4511T/4513T/4514T)")])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLAVB", "Advanced Variable Back Check (+$39)"),
    ])
    price_bulk(conn, f, "config", [("STD", 1090.00)], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLAVB", 39.00),
    ], price_type="adder")
