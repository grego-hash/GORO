"""Seed LCN 4000 Series door closer pricing.

Source: LCN Price Book 16, effective February 27, 2026.
Families: 4000T, 4010, 4010T, 4020, 4020T, 4030, 4030T,
          4040XP, 4040XPT, 4050A, 4050AT, 4110, 4110T
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
    _seed_4000t(conn)
    _seed_4010(conn)
    _seed_4010t(conn)
    _seed_4020(conn)
    _seed_4020t(conn)
    _seed_4030(conn)
    _seed_4030t(conn)
    _seed_4040xp(conn)
    _seed_4040xpt(conn)
    _seed_4050a(conn)
    _seed_4050at(conn)
    _seed_4110(conn)
    _seed_4110t(conn)
    print("  LCN 4000 Series (13 families) seeded.")


# ═══════════════════════════════════════════════════════════════
# 4000T (4003T/4004T) — 3 tiers, single config
# ═══════════════════════════════════════════════════════════════
def _seed_4000t(conn):
    f = fid(conn, "LCN", "4000T Series Closer", "Door Closer",
            "4003T/4004T {finish_tier} {finish}",
            "LCN 4003T/4004T {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 654.00, 779.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("STD", "Standard (4003T or 4004T)"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [("STD", 904.00)], price_type="base")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4010 (4011/4016) — 3 tiers, CYLDEL/CYLTEL
# ═══════════════════════════════════════════════════════════════
def _seed_4010(conn):
    f = fid(conn, "LCN", "4010 Series Closer", "Door Closer",
            "4011 {config} {finish_tier} {finish}",
            "LCN 4011 {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 659.00, 785.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    slot(conn, f, 5, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("REGARM", "REGARM - Regular Arm (4011/4016)"),
        ("H",      "H - Hold Open (4011/4016)"),
        ("FL",     "FL - Flush Arm (4011 only, Powder Coat only)"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLDEL", "Delayed Action (+$71, 4011 only)"),
        ("CYLTEL", "Telephone Booth (+$71)"),
    ])
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("REGARM", 791.00), ("H", 877.00), ("FL", 1030.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLDEL", 71.00), ("CYLTEL", 71.00),
    ], price_type="adder")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")
    # FL only available in Powder Coat
    rule(conn, f, "conflict", "config", "FL", "finish_tier", "PLATED",
         "Flush arm N/A in Plated")
    rule(conn, f, "conflict", "config", "FL", "finish_tier", "PLATED_PREM",
         "Flush arm N/A in Plated Premium")


# ═══════════════════════════════════════════════════════════════
# 4010T — 3 tiers, track closer with DE option
# ═══════════════════════════════════════════════════════════════
def _seed_4010t(conn):
    f = fid(conn, "LCN", "4010T Series Closer", "Door Closer",
            "4011T {config} {finish_tier} {finish}",
            "LCN 4011T {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 654.00, 779.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("STDTRK",    "STDTRK - Standard Track"),
        ("H",         "H - Hold Open Track"),
        ("BUMP",      "BUMP - Bumper Track"),
        ("HBMP",      "HBMP - Hold Open Bumper Track"),
        ("DE-STDTRK", "DE + STDTRK - Double Egress Standard"),
        ("DE-H",      "DE + H - Double Egress Hold Open"),
        ("DE-BUMP",   "DE + BUMP - Double Egress Bumper"),
        ("DE-HBMP",   "DE + HBMP - Double Egress Hold Open Bumper"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("STDTRK", 904.00), ("H", 944.00), ("BUMP", 912.00), ("HBMP", 960.00),
        ("DE-STDTRK", 958.00), ("DE-H", 998.00),
        ("DE-BUMP", 966.00), ("DE-HBMP", 1014.00),
    ], price_type="base")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4020 (4021/4026) — 3 tiers, CYLDEL/CYLTEL
# ═══════════════════════════════════════════════════════════════
def _seed_4020(conn):
    f = fid(conn, "LCN", "4020 Series Closer", "Door Closer",
            "4021 {config} {finish_tier} {finish}",
            "LCN 4021 {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 659.00, 785.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    slot(conn, f, 5, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("REGARM", "REGARM - Regular Arm (4021/4026)"),
        ("LONG",   "LONG - Long Arm (4021/4026)"),
        ("H",      "H - Hold Open (4021/4026)"),
        ("FL",     "FL - Flush Arm (4021 only, Powder Coat only)"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLDEL", "Delayed Action (+$71, 4021 only)"),
        ("CYLTEL", "Telephone Booth (+$71)"),
    ])
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("REGARM", 791.00), ("LONG", 798.00), ("H", 877.00), ("FL", 1030.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLDEL", 71.00), ("CYLTEL", 71.00),
    ], price_type="adder")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")
    rule(conn, f, "conflict", "config", "FL", "finish_tier", "PLATED",
         "Flush arm N/A in Plated")
    rule(conn, f, "conflict", "config", "FL", "finish_tier", "PLATED_PREM",
         "Flush arm N/A in Plated Premium")


# ═══════════════════════════════════════════════════════════════
# 4020T — 3 tiers, track closer (no DE)
# ═══════════════════════════════════════════════════════════════
def _seed_4020t(conn):
    f = fid(conn, "LCN", "4020T Series Closer", "Door Closer",
            "4021T {config} {finish_tier} {finish}",
            "LCN 4021T {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 654.00, 779.00)
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
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("STDTRK", 904.00), ("H", 944.00), ("BUMP", 912.00), ("HBMP", 960.00),
    ], price_type="base")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4030 (4031) — 3 tiers, double lever arm
# ═══════════════════════════════════════════════════════════════
def _seed_4030(conn):
    f = fid(conn, "LCN", "4030 Series Closer", "Door Closer",
            "4031 {config} {finish_tier} {finish}",
            "LCN 4031 {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 633.00, 759.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM", "REGARM - Regular Arm"),
        ("RWPA",   "RWPA - Regular Arm w/ PA Shoe"),
        ("RW62A",  "RW62A - Regular Arm w/ 62A Shoe"),
        ("LD",     "LD - Light Duty Arm"),
        ("LDPA",   "LDPA - Light Duty w/ PA Shoe"),
        ("LD62A",  "LD62A - Light Duty w/ 62A Shoe"),
        ("LONG",   "LONG - Long Arm"),
        ("H",      "H - Hold Open"),
        ("HWPA",   "HWPA - Hold Open Arm w/ PA Shoe"),
        ("HLONG",  "HLONG - Hold Open Long Arm"),
        ("EDA",    "EDA - Extra Duty Arm"),
        ("HEDA",   "HEDA - Hold Open Extra Duty Arm"),
        ("CUSH",   "CUSH - Cushion Arm"),
        ("HCUSH",  "HCUSH - Hold Open Cushion Arm"),
        ("SCUSH",  "SCUSH - Spring Cushion Arm"),
        ("SHCUSH", "SHCUSH - Spring Hold Open Cushion Arm"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("REGARM", 736.00), ("RWPA", 736.00), ("RW62A", 776.00),
        ("LD", 696.00), ("LDPA", 719.00), ("LD62A", 743.00),
        ("LONG", 743.00), ("H", 822.00), ("HWPA", 840.00),
        ("HLONG", 840.00), ("EDA", 800.00), ("HEDA", 864.00),
        ("CUSH", 847.00), ("HCUSH", 959.00), ("SCUSH", 967.00),
        ("SHCUSH", 1049.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 4030T (4031T) — 3 tiers, track closer
# ═══════════════════════════════════════════════════════════════
def _seed_4030t(conn):
    f = fid(conn, "LCN", "4030T Series Closer", "Door Closer",
            "4031T {config} {finish_tier} {finish}",
            "LCN 4031T {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 628.00, 753.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("STDTRK", "STDTRK - Standard Track"),
        ("H",      "H - Hold Open Track"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("STDTRK", 849.00), ("H", 889.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 4040XP — 3 tiers, full arm range, CYLDEL, cover
# ═══════════════════════════════════════════════════════════════
def _seed_4040xp(conn):
    f = fid(conn, "LCN", "4040XP Series Closer", "Door Closer",
            "4040XP {config} {finish_tier} {finish}",
            "LCN 4040XP {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 659.00, 785.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    slot(conn, f, 5, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("REGARM",  "REGARM - Regular Arm"),
        ("RWPA",    "RWPA - Regular Arm w/ PA Shoe"),
        ("LONG",    "LONG - Long Arm"),
        ("XLONG",   "XLONG - Extra Long Arm"),
        ("RW62A",   "RW62A - Regular Arm w/ 62A Shoe"),
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
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLDEL", "Delayed Action (+$71)"),
    ])
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("REGARM", 838.00), ("RWPA", 838.00), ("LONG", 845.00),
        ("XLONG", 902.00), ("RW62A", 878.00), ("H", 924.00),
        ("HWPA", 942.00), ("HLONG", 942.00), ("EDA", 902.00),
        ("EDAW62G", 909.00), ("HEDA", 966.00), ("HEDA62G", 982.00),
        ("CUSH", 949.00), ("HCUSH", 1061.00), ("SCUSH", 1069.00),
        ("SHCUSH", 1151.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLDEL", 71.00),
    ], price_type="adder")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4040XPT — 3 tiers, track closer with DE configs
# ═══════════════════════════════════════════════════════════════
def _seed_4040xpt(conn):
    f = fid(conn, "LCN", "4040XPT Series Closer", "Door Closer",
            "4040XPT {config} {finish_tier} {finish}",
            "LCN 4040XPT {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 654.00, 779.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("STDTRK",    "STDTRK - Standard Track"),
        ("H",         "H - Hold Open Track"),
        ("BUMP",      "BUMP - Bumper Track"),
        ("HBMP",      "HBMP - Hold Open Bumper Track"),
        ("DE-STDTRK", "DE + STDTRK - Double Egress Standard"),
        ("DE-H",      "DE + H - Double Egress Hold Open"),
        ("DE-BUMP",   "DE + BUMP - Double Egress Bumper"),
        ("DE-HBMP",   "DE + HBMP - Double Egress Hold Open Bumper"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("STDTRK", 951.00), ("H", 991.00), ("BUMP", 959.00), ("HBMP", 1007.00),
        ("DE-STDTRK", 1028.00), ("DE-H", 1068.00),
        ("DE-BUMP", 1036.00), ("DE-HBMP", 1084.00),
    ], price_type="base")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4050A — Powder Coat only, cast aluminum
# ═══════════════════════════════════════════════════════════════
def _seed_4050a(conn):
    f = fid(conn, "LCN", "4050A Series Closer", "Door Closer",
            "4050A {config} {finish}", "LCN 4050A {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "cylinder", "Cylinder", 0)
    options(conn, f, "config", [
        ("RWPA",    "RWPA - Regular Arm w/ PA Shoe"),
        ("LONG",    "LONG - Long Arm"),
        ("RW62A",   "RW62A - Regular Arm w/ 62A Shoe"),
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
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLDEL", "Delayed Action (+$71)"),
    ])
    price_bulk(conn, f, "config", [
        ("RWPA", 707.00), ("LONG", 716.00), ("RW62A", 747.00),
        ("HWPA", 812.00), ("HLONG", 812.00), ("EDA", 770.00),
        ("EDAW62G", 778.00), ("HEDA", 833.00), ("HEDA62G", 848.00),
        ("CUSH", 818.00), ("HCUSH", 929.00), ("SCUSH", 937.00),
        ("SHCUSH", 1018.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLDEL", 71.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4050AT — Powder Coat only, track closer with DE configs
# ═══════════════════════════════════════════════════════════════
def _seed_4050at(conn):
    f = fid(conn, "LCN", "4050AT Series Closer", "Door Closer",
            "4050AT {config} {finish}", "LCN 4050AT {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("STDTRK",    "STDTRK - Standard Track"),
        ("H",         "H - Hold Open Track"),
        ("BUMP",      "BUMP - Bumper Track"),
        ("HBMP",      "HBMP - Hold Open Bumper Track"),
        ("DE-STDTRK", "DE + STDTRK - Double Egress Standard"),
        ("DE-H",      "DE + H - Double Egress Hold Open"),
        ("DE-BUMP",   "DE + BUMP - Double Egress Bumper"),
        ("DE-HBMP",   "DE + HBMP - Double Egress Hold Open Bumper"),
    ])
    options(conn, f, "finish", PC)
    price_bulk(conn, f, "config", [
        ("STDTRK", 818.00), ("H", 857.00), ("BUMP", 825.00), ("HBMP", 873.00),
        ("DE-STDTRK", 876.00), ("DE-H", 915.00),
        ("DE-BUMP", 883.00), ("DE-HBMP", 931.00),
    ], price_type="base")


# ═══════════════════════════════════════════════════════════════
# 4110 (4111/4116) — 3 tiers, adjustable spring
# ═══════════════════════════════════════════════════════════════
def _seed_4110(conn):
    f = fid(conn, "LCN", "4110 Series Closer", "Door Closer",
            "4111 {config} {finish_tier} {finish}",
            "LCN 4111 {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 657.00, 784.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "cylinder", "Cylinder", 0)
    slot(conn, f, 5, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("RW62A",   "RW62A - Regular Arm w/ 62A Shoe"),
        ("EDA",     "EDA - Extra Duty Arm"),
        ("EDAW62G", "EDAW62G - Extra Duty Arm w/ 62G Shoe"),
        ("HEDA",    "HEDA - Hold Open Extra Duty Arm"),
        ("HEDA62G", "HEDA62G - Hold Open Extra Duty w/ 62G Shoe"),
        ("FL62",    "FL/62 - Flush Arm (4111 only, Powder Coat only)"),
        ("CUSH",    "CUSH - Cushion Arm"),
        ("HCUSH",   "HCUSH - Hold Open Cushion Arm (4111 only)"),
        ("SCUSH",   "SCUSH - Spring Cushion Arm"),
        ("SHCUSH",  "SHCUSH - Spring Hold Open Cushion (4111 only)"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "cylinder", [
        ("STD", "Standard Cylinder"),
        ("CYLDEL", "Delayed Action (+$71, 4111 only)"),
    ])
    options(conn, f, "cover", [
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("RW62A", 790.00), ("EDA", 814.00), ("EDAW62G", 821.00),
        ("HEDA", 878.00), ("HEDA62G", 894.00), ("FL62", 989.00),
        ("CUSH", 861.00), ("HCUSH", 973.00), ("SCUSH", 981.00),
        ("SHCUSH", 1063.00),
    ], price_type="base")
    price_bulk(conn, f, "cylinder", [
        ("STD", 0.00), ("CYLDEL", 71.00),
    ], price_type="adder")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")
    rule(conn, f, "conflict", "config", "FL62", "finish_tier", "PLATED",
         "Flush arm N/A in Plated")
    rule(conn, f, "conflict", "config", "FL62", "finish_tier", "PLATED_PREM",
         "Flush arm N/A in Plated Premium")


# ═══════════════════════════════════════════════════════════════
# 4110T — 3 tiers, track closer
# ═══════════════════════════════════════════════════════════════
def _seed_4110t(conn):
    f = fid(conn, "LCN", "4110T Series Closer", "Door Closer",
            "4111T {config} {finish_tier} {finish}",
            "LCN 4111T {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 654.00, 779.00)
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
        ("NONE", "No Cover"), ("MC", "Metal Cover (+$26)"),
    ])
    price_bulk(conn, f, "config", [
        ("STDTRK", 863.00), ("H", 903.00), ("BUMP", 871.00), ("HBMP", 919.00),
    ], price_type="base")
    price_bulk(conn, f, "cover", [
        ("NONE", 0.00), ("MC", 26.00),
    ], price_type="adder")
