"""Seed LCN 1000 Series door closer pricing.

Source: LCN Price Book 16, effective February 27, 2026.
Families: 1250, 1260, 1450, 1450T, 1460, 1460T
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk

# ── Shared finish data ──────────────────────────────────────────────
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
    """Add finish_tier slot with pricing and restriction rules."""
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
    _seed_1250(conn)
    _seed_1260(conn)
    _seed_1450(conn)
    _seed_1450t(conn)
    _seed_1460(conn)
    _seed_1460t(conn)
    print("  LCN 1000 Series (6 families) seeded.")


# ═══════════════════════════════════════════════════════════════
# 1250 Series — Powder Coat only
# ═══════════════════════════════════════════════════════════════
def _seed_1250(conn):
    f = fid(conn, "LCN", "1250 Series Closer", "Door Closer",
            "1250 {config} {finish}", "LCN 1250 {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("RWPA",   "RWPA - Regular Arm w/ PA Shoe"),
        ("RW62A",  "RW62A - Regular Arm w/ 62A Shoe"),
        ("LONG",   "LONG - Long Arm"),
        ("HWPA",   "HWPA - Hold Open Arm w/ PA Shoe"),
        ("HLONG",  "HLONG - Hold Open Long Arm"),
        ("EDA",    "EDA - Extra Duty Arm"),
        ("HEDA",   "HEDA - Hold Open Extra Duty Arm"),
        ("CUSH",   "CUSH - Cushion Arm"),
        ("HCUSH",  "HCUSH - Hold Open Cushion Arm"),
        ("SCUSH",  "SCUSH - Spring Cushion Arm"),
        ("SHCUSH", "SHCUSH - Spring Hold Open Cushion Arm"),
    ])
    options(conn, f, "finish", PC)
    price_bulk(conn, f, "config", [
        ("RWPA", 344.00), ("RW62A", 365.00), ("LONG", 335.00),
        ("HWPA", 391.00), ("HLONG", 400.00), ("EDA", 423.00),
        ("HEDA", 479.00), ("CUSH", 479.00), ("HCUSH", 573.00),
        ("SCUSH", 573.00), ("SHCUSH", 671.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 1260 (1261) Series — Powder Coat only
# ═══════════════════════════════════════════════════════════════
def _seed_1260(conn):
    f = fid(conn, "LCN", "1260 Series Closer", "Door Closer",
            "1261 {config} {finish}", "LCN 1261 {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM",  "REGARM - Regular Arm"),
        ("RWPA",    "RWPA - Regular Arm w/ PA Shoe"),
        ("RW62A",   "RW62A - Regular Arm w/ 62A Shoe"),
        ("LONG",    "LONG - Long Arm"),
        ("H",       "H - Hold Open"),
        ("HWPA",    "HWPA - Hold Open Arm w/ PA Shoe"),
        ("HLONG",   "HLONG - Hold Open Long Arm"),
        ("EDA",     "EDA - Extra Duty Arm"),
        ("EDAW62G", "EDAW62G - Extra Duty Arm w/ 62G Shoe"),
        ("HEDA",    "HEDA - Hold Open Extra Duty Arm"),
        ("HEDA62G", "HEDA62G - Hold Open Extra Duty w/ 62G Shoe"),
        ("CUSH",    "CUSH - Cushion Arm"),
        ("HCUSH",   "HCUSH - Hold Open Cushion Arm"),
        ("SCUSH",   "SCUSH - Spring Cushion Arm"),
        ("SHCUSH",  "SHCUSH - Spring Hold Open Cushion Arm"),
    ])
    options(conn, f, "finish", PC)
    price_bulk(conn, f, "config", [
        ("REGARM", 462.00), ("RWPA", 471.00), ("RW62A", 494.00),
        ("LONG", 462.00), ("H", 512.00), ("HWPA", 518.00),
        ("HLONG", 525.00), ("EDA", 552.00), ("EDAW62G", 566.00),
        ("HEDA", 604.00), ("HEDA62G", 622.00), ("CUSH", 604.00),
        ("HCUSH", 702.00), ("SCUSH", 702.00), ("SHCUSH", 798.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 1450 Series — Powder Coat only, CYLDEL / cover options
# ═══════════════════════════════════════════════════════════════
def _seed_1450(conn):
    f = fid(conn, "LCN", "1450 Series Closer", "Door Closer",
            "1450 {config} {finish}", "LCN 1450 {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "cylinder", "Cylinder", 0)
    slot(conn, f, 4, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("RWPA",    "RWPA - Regular Arm w/ PA Shoe"),
        ("RW62A",   "RW62A - Regular Arm w/ 62A Shoe"),
        ("LONG",    "LONG - Long Arm"),
        ("HWPA",    "HWPA - Hold Open Arm w/ PA Shoe"),
        ("HLONG",   "HLONG - Hold Open Long Arm"),
        ("EDA",     "EDA - Extra Duty Arm"),
        ("EDAW62G", "EDAW62G - Extra Duty Arm w/ 62G Shoe"),
        ("HEDA",    "HEDA - Hold Open Extra Duty Arm"),
        ("CUSH",    "CUSH - Cushion Arm"),
        ("HCUSH",   "HCUSH - Hold Open Cushion Arm"),
        ("SCUSH",   "SCUSH - Spring Cushion Arm"),
        ("SHCUSH",  "SHCUSH - Spring Hold Open Cushion Arm"),
    ])
    options(conn, f, "finish", PC)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"), ("CYLDEL", "Delayed Action (+$71)"),
    ])
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("FPC", "Full Plastic Cover (+$18)"),
        ("MC", "Metal Cover (+$40)"),
    ])
    price_bulk(conn, f, "config", [
        ("RWPA", 453.00), ("RW62A", 474.00), ("LONG", 444.00),
        ("HWPA", 500.00), ("HLONG", 509.00), ("EDA", 532.00),
        ("EDAW62G", 549.00), ("HEDA", 588.00), ("CUSH", 588.00),
        ("HCUSH", 682.00), ("SCUSH", 682.00), ("SHCUSH", 780.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLDEL", 71.00),
    ], price_type="adder")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("FPC", 18.00), ("MC", 40.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 1450T Series — Powder Coat only, track closer
# ═══════════════════════════════════════════════════════════════
def _seed_1450t(conn):
    f = fid(conn, "LCN", "1450T Series Closer", "Door Closer",
            "1450T {config} {finish}", "LCN 1450T {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("STDTRK", "STDTRK - Standard Track"),
        ("H",      "H - Hold Open Track"),
        ("BUMP",   "BUMP - Bumper Track"),
        ("HBUMP",  "HBUMP - Hold Open Bumper Track"),
    ])
    options(conn, f, "finish", PC)
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("FPC", "Full Plastic Cover (+$18)"),
        ("MC", "Metal Cover (+$39)"),
    ])
    price_bulk(conn, f, "config", [
        ("STDTRK", 573.00), ("H", 612.00), ("BUMP", 580.00), ("HBUMP", 628.00),
    ], price_type="base")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("FPC", 18.00), ("MC", 39.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 1460 (1461) Series — 3 finish tiers, CYLDEL / cover options
# ═══════════════════════════════════════════════════════════════
def _seed_1460(conn):
    f = fid(conn, "LCN", "1460 Series Closer", "Door Closer",
            "1461 {config} {finish_tier} {finish}",
            "LCN 1461 {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 591.00, 701.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    slot(conn, f, 5, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("REGARM",  "REGARM - Regular Arm"),
        ("RWPA",    "RWPA - Regular Arm w/ PA Shoe"),
        ("RW62A",   "RW62A - Regular Arm w/ 62A Shoe"),
        ("LONG",    "LONG - Long Arm"),
        ("H",       "H - Hold Open"),
        ("HWPA",    "HWPA - Hold Open Arm w/ PA Shoe"),
        ("HLONG",   "HLONG - Hold Open Long Arm"),
        ("HD",      "HD - Heavy Duty"),
        ("HDPA",    "HDPA - Heavy Duty w/ PA Shoe"),
        ("HD62A",   "HD62A - Heavy Duty w/ 62A Shoe"),
        ("HDLONG",  "HDLONG - Heavy Duty Long Arm"),
        ("EDA",     "EDA - Extra Duty Arm"),
        ("EDAW62G", "EDAW62G - Extra Duty Arm w/ 62G Shoe"),
        ("HEDA",    "HEDA - Hold Open Extra Duty Arm"),
        ("HEDA62G", "HEDA62G - Hold Open Extra Duty w/ 62G Shoe"),
        ("CUSH",    "CUSH - Cushion Arm"),
        ("HCUSH",   "HCUSH - Hold Open Cushion Arm"),
        ("SCUSH",   "SCUSH - Spring Cushion Arm"),
        ("SHCUSH",  "SHCUSH - Spring Hold Open Cushion Arm"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"), ("CYLDEL", "Delayed Action (+$71)"),
    ])
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("FPC", "Full Plastic Cover (+$18)"),
        ("DS", "Designer Series Metal Cover (+$48)"),
    ])
    price_bulk(conn, f, "config", [
        ("REGARM", 582.00), ("RWPA", 591.00), ("RW62A", 614.00),
        ("LONG", 582.00), ("H", 632.00), ("HWPA", 638.00),
        ("HLONG", 645.00), ("HD", 638.00), ("HDPA", 645.00),
        ("HD62A", 672.00), ("HDLONG", 645.00), ("EDA", 672.00),
        ("EDAW62G", 686.00), ("HEDA", 724.00), ("HEDA62G", 742.00),
        ("CUSH", 724.00), ("HCUSH", 822.00), ("SCUSH", 822.00),
        ("SHCUSH", 918.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLDEL", 71.00),
    ], price_type="adder")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("FPC", 18.00), ("DS", 48.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 1460T Series — 3 finish tiers, track closer
# ═══════════════════════════════════════════════════════════════
def _seed_1460t(conn):
    f = fid(conn, "LCN", "1460T Series Closer", "Door Closer",
            "1461T {config} {finish_tier} {finish}",
            "LCN 1461T {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 462.00, 589.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("STDTRK", "STDTRK - Standard Track"),
        ("H",      "H - Hold Open Track"),
        ("BUMP",   "BUMP - Bumper Track"),
        ("HBMP",   "HBMP - Hold Open Bumper Track"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("FPC", "Full Plastic Cover (+$18)"),
        ("DS", "Designer Series Metal Cover (+$48)"),
    ])
    price_bulk(conn, f, "config", [
        ("STDTRK", 710.00), ("H", 750.00), ("BUMP", 718.00), ("HBMP", 766.00),
    ], price_type="base")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("FPC", 18.00), ("DS", 48.00),
    ], price_type="adder")
