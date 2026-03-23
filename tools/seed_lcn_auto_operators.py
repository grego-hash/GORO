"""Seed LCN Auto Operators pricing.

Source: LCN Price Book 16, effective February 27, 2026 (pp 80-115).
Families: Pneumatic (2610, 4810, 4820, 4840), Control Boxes (7980, 7900),
          Electrohydraulic (4630, 4640, 6440), Senior Swing IQ (2810IQ,
          2850IQ, 2860IQ, 9530IQ, 9540IQ, 9550IQ, 9560IQ, Upgrade Kit),
          Benchmark (9130, 9140, 9150)
"""

from seed_helpers import fid, slot, options, rule, price, price_bulk

# ── Finish lists ─────────────────────────────────────────────────────
# Auto operators omit 622 MTBLK from powder coat options
PC = [
    ("689", "689 - AL"),    ("690", "690 - STAT"),
    ("691", "691 - LTBRZ"), ("693", "693 - GLBLK"),
    ("695", "695 - DKBRZ"), ("696", "696 - BRASS"),
]
PL = [
    ("616", "616 - US11"), ("632", "632 - US3"),  ("633", "633 - US4"),
    ("639", "639 - US10"), ("646", "646 - US15"), ("651", "651 - US26"),
    ("652", "652 - US26D"),
]
TIERS = [
    ("POWDER_COAT", "Powder Coat"),
    ("PLATED",      "Plated (652)"),
    ("PLATED_PREM", "Plated Premium"),
]
ANOD_3 = [("628", "628 - ANCLR"), ("710", "710 - ANDKB"), ("711", "711 - ANBLK")]
ANOD_2 = [("628", "628 - ANCLR"), ("710", "710 - ANDKB")]
PC_2 = [("689", "689 - AL"), ("695", "695 - DKBRZ")]


def _tier_setup(conn, f, order, plated, premium):
    """3-tier finish for pneumatic/electrohydraulic operators."""
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
    # Pneumatic operators
    _seed_2610(conn)
    _seed_4810(conn)
    _seed_4820(conn)
    _seed_4840(conn)
    # Control boxes
    _seed_7980(conn)
    _seed_7900(conn)
    # Electrohydraulic operators
    _seed_4630(conn)
    _seed_4640(conn)
    _seed_6440(conn)
    # Senior Swing IQ
    _seed_2810iq(conn)
    _seed_2850iq(conn)
    _seed_2860iq(conn)
    _seed_9530iq(conn)
    _seed_9540iq(conn)
    _seed_9550iq(conn)
    _seed_9560iq(conn)
    _seed_ssiq_upgrade(conn)
    # Benchmark
    _seed_9130(conn)
    _seed_9140(conn)
    _seed_9150(conn)
    print("  LCN Auto Operators (20 families) seeded.")


# ═══════════════════════════════════════════════════════════════
# 2610 Series — Pneumatic Concealed Operator
# Adders: PL +$647, PP +$1,062
# ═══════════════════════════════════════════════════════════════
def _seed_2610(conn):
    f = fid(conn, "LCN", "2610 Series Pneumatic Operator", "Auto Operator",
            "2613/2614 {config} {finish_tier} {finish}",
            "LCN 2613/2614 {config} {finish}")
    slot(conn, f, 1, "config", "Cylinder", 1)
    _tier_setup(conn, f, 2, 647.00, 1062.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("CYL", "Standard Cylinder"),
        ("DPS", "Door Position Switch Cylinder"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("CYL", 3724.00), ("DPS", 3903.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 4810 Series — Pneumatic Top Jamb Pull Side
# Adders: PL +$643, PP +$1,059
# ═══════════════════════════════════════════════════════════════
def _seed_4810(conn):
    f = fid(conn, "LCN", "4810 Series Pneumatic Operator", "Auto Operator",
            "4811 {finish_tier} {finish}",
            "LCN 4811 {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 643.00, 1059.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [("STD", "Standard (4811)")])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [("STD", 3655.00)])


# ═══════════════════════════════════════════════════════════════
# 4820 Series — Pneumatic Top Jamb Push Side
# Adders: PL +$645, PP +$1,059
# ═══════════════════════════════════════════════════════════════
def _seed_4820(conn):
    f = fid(conn, "LCN", "4820 Series Pneumatic Operator", "Auto Operator",
            "4822 {config} {finish_tier} {finish}",
            "LCN 4822 {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    _tier_setup(conn, f, 2, 645.00, 1059.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM", "Regular Arm"),
        ("LONG",   "Long Arm"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("REGARM", 3534.00), ("LONG", 3539.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 4840 Series — Pneumatic Door Mounted Push Side
# Adders: PL +$643, PP +$1,059
# ═══════════════════════════════════════════════════════════════
def _seed_4840(conn):
    f = fid(conn, "LCN", "4840 Series Pneumatic Operator", "Auto Operator",
            "4841 {config} {finish_tier} {finish}",
            "LCN 4841 {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    _tier_setup(conn, f, 2, 643.00, 1059.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("EDA",   "EDA Arm"),
        ("CUSH",  "Cushion Arm"),
        ("SCUSH", "Spring Cushion Arm"),
    ])
    options(conn, f, "finish", PC + PL)
    price_bulk(conn, f, "config", [
        ("EDA", 3598.00), ("CUSH", 3647.00), ("SCUSH", 3769.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 7980 Series Control Box — Internal Compressor
# ═══════════════════════════════════════════════════════════════
def _seed_7980(conn):
    f = fid(conn, "LCN", "7980 Series Control Box", "Auto Operator",
            "LCN {config}",
            "LCN {config} Control Box")
    slot(conn, f, 1, "config", "Model", 1)
    options(conn, f, "config", [
        ("7981",    "7981 - Single Door"),
        ("7981ES",  "7981ES - Single Door, ES Relay"),
        ("7982",    "7982 - Double Door"),
        ("7982S",   "7982S - Double Door, Sequential"),
        ("7982ES",  "7982ES - Double Door, ES Relays"),
        ("7982SES", "7982SES - Double Door, Sequential + ES"),
    ])
    price_bulk(conn, f, "config", [
        ("7981", 5291.00),    ("7981ES", 6146.00),
        ("7982", 7491.00),    ("7982S",  8140.00),
        ("7982ES", 8995.00),  ("7982SES", 9566.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 7900 Series Control Box — External Air Source
# ═══════════════════════════════════════════════════════════════
def _seed_7900(conn):
    f = fid(conn, "LCN", "7900 Series Control Box", "Auto Operator",
            "LCN {config}",
            "LCN {config} Control Box")
    slot(conn, f, 1, "config", "Model", 1)
    options(conn, f, "config", [
        ("7901",    "7901 - Single Door"),
        ("7901ES",  "7901ES - Single Door, ES Relay"),
        ("7902",    "7902 - Double Door"),
        ("7902S",   "7902S - Double Door, Sequential"),
        ("7902ES",  "7902ES - Double Door, ES Relays"),
        ("7902SES", "7902SES - Double Door, Sequential + ES"),
        ("7949",    "7949 - Auxiliary Blow-Open"),
        ("7949ES",  "7949ES - Auxiliary Blow-Open, ES Relay"),
    ])
    price_bulk(conn, f, "config", [
        ("7901", 3621.00),    ("7901ES", 4476.00),
        ("7902", 4967.00),    ("7902S",  5617.00),
        ("7902ES", 6513.00),  ("7902SES", 7084.00),
        ("7949", 3013.00),    ("7949ES", 3746.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 4630 Series — Electrohydraulic Pull Side
# Adders: PL +$643, PP +$1,056
# ═══════════════════════════════════════════════════════════════
def _seed_4630(conn):
    f = fid(conn, "LCN", "4630 Series Electrohydraulic Operator", "Auto Operator",
            "4631 {finish_tier} {finish}",
            "LCN 4631 {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    _tier_setup(conn, f, 2, 643.00, 1056.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "screw_pack", "Screw Package", 0)
    options(conn, f, "config", [("STD", "Standard (4631)")])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "screw_pack", [
        ("WMS",  "Wood and Machine Screws (default)"),
        ("TORX", "Torx Machine Screws (+$21)"),
    ])
    price_bulk(conn, f, "config", [("STD", 9495.00)])
    price_bulk(conn, f, "screw_pack", [
        ("WMS", 0.00), ("TORX", 21.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 4640 Series — Electrohydraulic Push Side
# Adders: PL +$645, PP +$1,057
# ═══════════════════════════════════════════════════════════════
def _seed_4640(conn):
    f = fid(conn, "LCN", "4640 Series Electrohydraulic Operator", "Auto Operator",
            "4642 {config} {finish_tier} {finish}",
            "LCN 4642 {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    _tier_setup(conn, f, 2, 645.00, 1057.00)
    slot(conn, f, 3, "finish", "Finish", 1)
    slot(conn, f, 4, "screw_pack", "Screw Package", 0)
    options(conn, f, "config", [
        ("REGARM", "Regular Arm"),
        ("LONG",   "Long Arm"),
    ])
    options(conn, f, "finish", PC + PL)
    options(conn, f, "screw_pack", [
        ("WMS",  "Wood and Machine Screws (default)"),
        ("TORX", "Torx Machine Screws (+$21)"),
    ])
    price_bulk(conn, f, "config", [
        ("REGARM", 9373.00), ("LONG", 9379.00),
    ])
    price_bulk(conn, f, "screw_pack", [
        ("WMS", 0.00), ("TORX", 21.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 6440 Series — Compact Electrohydraulic Operator
# Powder coat only (689 AL / 695 DKBRZ)
# ═══════════════════════════════════════════════════════════════
def _seed_6440(conn):
    f = fid(conn, "LCN", "6440 Series Compact Operator", "Auto Operator",
            "LCN {config} {finish}",
            "LCN {config} {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("6440",       "6440 Module Kit"),
        ("6440-3813W", "6440 + Hardwired Actuator Kit"),
        ("6440-2210",  "6440 + Battery Actuator Kit"),
        ("6440XP",     "6440XP (incl 4040XP + RwPA)"),
    ])
    options(conn, f, "finish", PC_2)
    price_bulk(conn, f, "config", [
        ("6440", 1471.00),       ("6440-3813W", 2863.00),
        ("6440-2210", 2554.00),  ("6440XP", 2303.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 2810IQ Series — Senior Swing Concealed Single Door
# Anodized (628/710/711)
# ═══════════════════════════════════════════════════════════════
def _seed_2810iq(conn):
    f = fid(conn, "LCN", "2810IQ Series Senior Swing", "Auto Operator",
            "2811IQ {config} {finish}",
            "LCN 2811IQ {config} {finish}")
    slot(conn, f, 1, "config", "Arm / Header", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "closer_stop", "Closer Stop", 0)
    options(conn, f, "config", [
        ("ARMCP-HDR",    "Center Pivot, Single Door Header"),
        ("ARMCP-HDR2",   "Center Pivot, Double Door Header"),
        ("ARMOP-HDR",    "Offset Pivot, Single Door Header"),
        ("ARMOP-HDR2",   "Offset Pivot, Double Door Header"),
        ("ARMOP-HDR2MP", "Offset Pivot, Dbl Door Hdr + Manual Prep"),
    ])
    options(conn, f, "finish", ANOD_3)
    options(conn, f, "closer_stop", [
        ("NONE", "None"),
        ("POS",  "Positive Stop (+$42)"),
        ("BKY",  "Breakaway Stop (+$170)"),
    ])
    price_bulk(conn, f, "config", [
        ("ARMCP-HDR", 7897.00),    ("ARMCP-HDR2", 8305.00),
        ("ARMOP-HDR", 8019.00),    ("ARMOP-HDR2", 8427.00),
        ("ARMOP-HDR2MP", 8835.00),
    ])
    price_bulk(conn, f, "closer_stop", [
        ("NONE", 0.00), ("POS", 42.00), ("BKY", 170.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 2850IQ Series — Senior Swing Concealed Double Simultaneous
# ═══════════════════════════════════════════════════════════════
def _seed_2850iq(conn):
    f = fid(conn, "LCN", "2850IQ Series Senior Swing", "Auto Operator",
            "2853IQ {config} {finish}",
            "LCN 2853IQ {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "closer_stop", "Closer Stop", 0)
    options(conn, f, "config", [
        ("ARMCP2", "Center Pivot Arms (Pair)"),
        ("ARMOP2", "Offset Pivot Arms (Pair)"),
    ])
    options(conn, f, "finish", ANOD_3)
    options(conn, f, "closer_stop", [
        ("NONE", "None"),
        ("POS",  "Positive Stop (+$87)"),
        ("BKY",  "Breakaway Stop (+$338)"),
    ])
    price_bulk(conn, f, "config", [
        ("ARMCP2", 12866.00), ("ARMOP2", 13109.00),
    ])
    price_bulk(conn, f, "closer_stop", [
        ("NONE", 0.00), ("POS", 87.00), ("BKY", 338.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 2860IQ Series — Senior Swing Concealed Double Independent
# ═══════════════════════════════════════════════════════════════
def _seed_2860iq(conn):
    f = fid(conn, "LCN", "2860IQ Series Senior Swing", "Auto Operator",
            "2863IQ {config} {finish}",
            "LCN 2863IQ {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "closer_stop", "Closer Stop", 0)
    options(conn, f, "config", [
        ("ARMCP2", "Center Pivot Arms (Pair)"),
        ("ARMOP2", "Offset Pivot Arms (Pair)"),
    ])
    options(conn, f, "finish", ANOD_3)
    options(conn, f, "closer_stop", [
        ("NONE", "None"),
        ("POS",  "Positive Stop (+$70)"),
        ("BKY",  "Breakaway Stop (+$285)"),
    ])
    price_bulk(conn, f, "config", [
        ("ARMCP2", 13542.00), ("ARMOP2", 13785.00),
    ])
    price_bulk(conn, f, "closer_stop", [
        ("NONE", 0.00), ("POS", 70.00), ("BKY", 285.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 9530IQ Series — Senior Swing Surface Pull Side
# ═══════════════════════════════════════════════════════════════
def _seed_9530iq(conn):
    f = fid(conn, "LCN", "9530IQ Series Senior Swing", "Auto Operator",
            "9531IQ {config} {finish}",
            "LCN 9531IQ {config} {finish}")
    slot(conn, f, 1, "config", "Cover / Door Width", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("COV",  "Single Door Cover (33\"-48\")"),
        ("COV2", "Double Door Cover (48 1/8\"-98\")"),
    ])
    options(conn, f, "finish", ANOD_3)
    price_bulk(conn, f, "config", [
        ("COV", 8042.00), ("COV2", 8450.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 9540IQ Series — Senior Swing Surface Push Side
# ═══════════════════════════════════════════════════════════════
def _seed_9540iq(conn):
    f = fid(conn, "LCN", "9540IQ Series Senior Swing", "Auto Operator",
            "9542IQ {config} {finish}",
            "LCN 9542IQ {config} {finish}")
    slot(conn, f, 1, "config", "Arm / Cover", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM-COV",  "Regular Arm, Single Door (33\"-48\")"),
        ("REGARM-COV2", "Regular Arm, Double Door (48 1/8\"-98\")"),
        ("LONG-COV",    "Long Arm, Single Door"),
        ("LONG-COV2",   "Long Arm, Double Door"),
        ("TLS-COV",     "Telescoping Arm, Single Door"),
        ("LNGTLS-COV",  "Long Telescoping Arm, Single Door"),
    ])
    options(conn, f, "finish", ANOD_3)
    price_bulk(conn, f, "config", [
        ("REGARM-COV", 7905.00),  ("REGARM-COV2", 8313.00),
        ("LONG-COV", 7920.00),    ("LONG-COV2", 8328.00),
        ("TLS-COV", 7956.00),     ("LNGTLS-COV", 8026.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 9550IQ Series — Senior Swing Surface Double Simultaneous
# ═══════════════════════════════════════════════════════════════
def _seed_9550iq(conn):
    f = fid(conn, "LCN", "9550IQ Series Senior Swing", "Auto Operator",
            "9553IQ {config} {finish}",
            "LCN 9553IQ {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM2",    "Regular Arms (Pair, Push)"),
        ("LONG2",      "Long Arms (Pair, Push)"),
        ("STDTRKARM2", "Standard Track Arms (Pair, Pull)"),
        ("REGSTDDE",   "Regular + Standard (Double Egress)"),
        ("TLS2",       "Telescoping Arms (Pair, Push)"),
        ("LNGTLS2",    "Long Telescoping Arms (Pair)"),
        ("TLS/STD",    "Telescoping + Standard (Double Egress)"),
    ])
    options(conn, f, "finish", ANOD_3)
    price_bulk(conn, f, "config", [
        ("REGARM2", 12869.00),    ("LONG2", 12899.00),
        ("STDTRKARM2", 13142.00), ("REGSTDDE", 13005.00),
        ("TLS2", 12970.00),       ("LNGTLS2", 13001.00),
        ("TLS/STD", 13056.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 9560IQ Series — Senior Swing Surface Double Independent
# ═══════════════════════════════════════════════════════════════
def _seed_9560iq(conn):
    f = fid(conn, "LCN", "9560IQ Series Senior Swing", "Auto Operator",
            "9563IQ {config} {finish}",
            "LCN 9563IQ {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM2",    "Regular Arms (Pair, Push)"),
        ("LONG2",      "Long Arms (Pair, Push)"),
        ("STDTRKARM2", "Standard Track Arms (Pair, Pull)"),
        ("REGSTDDE",   "Regular + Standard (Double Egress)"),
        ("TLS2",       "Telescoping Arms (Pair, Push)"),
        ("LNGTLS2",    "Long Telescoping Arms (Pair)"),
        ("TLS/STD",    "Telescoping + Standard (Double Egress)"),
    ])
    options(conn, f, "finish", ANOD_3)
    price_bulk(conn, f, "config", [
        ("REGARM2", 13595.00),    ("LONG2", 13625.00),
        ("STDTRKARM2", 13868.00), ("REGSTDDE", 13731.00),
        ("TLS2", 13696.00),       ("LNGTLS2", 13727.00),
        ("TLS/STD", 13717.00),
    ])


# ═══════════════════════════════════════════════════════════════
# SS IQ Upgrade Kit
# ═══════════════════════════════════════════════════════════════
def _seed_ssiq_upgrade(conn):
    f = fid(conn, "LCN", "SS IQ Upgrade Kit", "Auto Operator",
            "LCN SSIQUPGRADE-{config}",
            "LCN Senior Swing IQ Upgrade Kit ({config})")
    slot(conn, f, 1, "config", "Kit Type", 1)
    options(conn, f, "config", [
        ("SD", "Single Door"),
        ("DD", "Double Door"),
    ])
    price_bulk(conn, f, "config", [
        ("SD", 6569.00), ("DD", 10401.00),
    ])


# ═══════════════════════════════════════════════════════════════
# 9130 Series — Benchmark Pull Side
# Anodized (628/710 only)
# ═══════════════════════════════════════════════════════════════
def _seed_9130(conn):
    f = fid(conn, "LCN", "9130 Series Benchmark", "Auto Operator",
            "9131 {finish}",
            "LCN 9131 Benchmark {finish}")
    slot(conn, f, 1, "config", "Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "cover", "Cover", 0)
    options(conn, f, "config", [("STD", "Standard (9131)")])
    options(conn, f, "finish", ANOD_2)
    options(conn, f, "cover", [
        ("MC",  "Standard 27\" Metal Cover (default)"),
        ("FMC", "Full Metal Cover 36\" (+$147)"),
    ])
    price_bulk(conn, f, "config", [("STD", 5714.00)])
    price_bulk(conn, f, "cover", [
        ("MC", 0.00), ("FMC", 147.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 9140 Series — Benchmark Push Side
# ═══════════════════════════════════════════════════════════════
def _seed_9140(conn):
    f = fid(conn, "LCN", "9140 Series Benchmark", "Auto Operator",
            "9142 {config} {finish}",
            "LCN 9142 Benchmark {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    slot(conn, f, 3, "cover", "Cover", 0)
    options(conn, f, "config", [
        ("REGARM", "Regular Arm"),
        ("LONG",   "Long Arm"),
    ])
    options(conn, f, "finish", ANOD_2)
    options(conn, f, "cover", [
        ("MC",  "Standard 27\" Metal Cover (default)"),
        ("FMC", "Full Metal Cover 36\" (+$147)"),
    ])
    price_bulk(conn, f, "config", [
        ("REGARM", 5604.00), ("LONG", 5612.00),
    ])
    price_bulk(conn, f, "cover", [
        ("MC", 0.00), ("FMC", 147.00),
    ], price_type="adder")


# ═══════════════════════════════════════════════════════════════
# 9150 Series — Benchmark Double Door
# ═══════════════════════════════════════════════════════════════
def _seed_9150(conn):
    f = fid(conn, "LCN", "9150 Series Benchmark", "Auto Operator",
            "9153 {config} {finish}",
            "LCN 9153 Benchmark {config} {finish}")
    slot(conn, f, 1, "config", "Arm Type", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "config", [
        ("REGARM2", "Regular Arms (Pair)"),
        ("LONG2",   "Long Arms (Pair)"),
    ])
    options(conn, f, "finish", ANOD_2)
    price_bulk(conn, f, "config", [
        ("REGARM2", 11086.00), ("LONG2", 11101.00),
    ])
