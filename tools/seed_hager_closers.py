"""Seed Hager door closer pricing from Pricebook #18 (Mar 2026).

Models:  5100 Series (Grade 1, Size 1-6),
         5300 Series (Grade 1, Concealed, Size 1-6)
"""

from seed_helpers import fid, slot, options, price, price_bulk

# ── Common finish options ───────────────────────────
PAINTED = [
    ("ALM", "ALM - Aluminum"),
    ("BRZ", "BRZ - Bronze"),
    ("DBZ", "DBZ - Dark Bronze"),
    ("GOL", "GOL - Gold"),
    ("BLK", "BLK - Black"),
]
_PK = [v for v, _ in PAINTED]


def seed(conn):
    _seed_5100(conn)
    _seed_5300(conn)
    print("  Hager Closers (2 families) seeded.")


# ═══════════════════════════════════════════════════
#  5100 Series – Grade 1, Adjustable Size 1-6
# ═══════════════════════════════════════════════════
def _seed_5100(conn):
    f = fid(conn, "Hager", "5100 Series Closer", "Closer",
            "5100 {config} {finish}",
            "Hager 5100 Series Grade 1 Size 1-6 Closer, {config}, {finish}")
    slot(conn, f, 1, "config", "Arm Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)

    configs = [
        ("STD",       "Standard Arm w/ Plastic Cover"),
        ("HO",        "5107 Hold Open Arm"),
        ("EHD",       "5106 Extra Heavy Duty Arm"),
        ("EHD_HO",    "5108 EHD Hold Open Arm (specify hand)"),
        ("TRK_NHO",   "Track Arm - Non Hold Open"),
        ("TRK_HO",    "Track Arm - Hold Open"),
        ("TRK_DE_NHO","Track Arm - Double Egress NHO"),
        ("TRK_DE_HO", "Track Arm - Double Egress HO"),
        ("PS_STOP",   "5123 Pull Side Stop Arm"),
        ("PS_HO",     "5124 Pull Side HO Stop Arm"),
        ("EHD_STOP",  "5125 EHD Stop Arm"),
        ("EHD_HO_CSH","5954 EHD HO Cushion Stop Arm"),
        ("EHD_CSH",   "5955 EHD Cushion Stop Arm"),
        ("EHD_HO_STP","5961 EHD HO Stop Arm"),
    ]
    options(conn, f, "config", configs)

    finishes = PAINTED + [("US32D", "US32D - Satin Stainless")]
    options(conn, f, "finish", finishes)

    # Pricing data: (config_key, painted_price, us32d_price_or_None)
    cfg_prices = [
        ("STD",        440.71,  722.27),
        ("HO",         493.78,  None),
        ("EHD",        506.19,  None),
        ("EHD_HO",     488.97,  None),
        ("TRK_NHO",    501.78,  None),
        ("TRK_HO",     520.28,  None),
        ("TRK_DE_NHO", 541.83,  None),
        ("TRK_DE_HO",  560.34,  None),
        ("PS_STOP",    501.58,  None),
        ("PS_HO",      528.69,  None),
        ("EHD_STOP",   506.19,  None),
        ("EHD_HO_CSH", 696.38,  None),
        ("EHD_CSH",    632.80,  None),
        ("EHD_HO_STP", 571.25,  None),
    ]
    for cfg, painted, ss in cfg_prices:
        for fin in _PK:
            price(conn, f, "config:finish", f"{cfg}:{fin}", painted)
        if ss is not None:
            price(conn, f, "config:finish", f"{cfg}:US32D", ss)


# ═══════════════════════════════════════════════════
#  5300 Series – Grade 1, Concealed, Size 1-6
# ═══════════════════════════════════════════════════
def _seed_5300(conn):
    f = fid(conn, "Hager", "5300 Series Concealed Closer", "Closer",
            "5300 {config} {finish}",
            "Hager 5300 Series Grade 1 Concealed Size 1-6 Closer, {config}, {finish}")
    slot(conn, f, 1, "config", "Arm Configuration", 1)
    slot(conn, f, 2, "finish", "Finish", 1)

    configs = [
        ("STD",       "Standard Arm w/ Plastic Cover"),
        ("HO",        "5910 Hold Open Arm"),
        ("EHD",       "5911 Extra Heavy Duty Arm"),
        ("EHD_HO",    "5906 EHD Hold Open Stop Arm"),
        ("EHD_STOP",  "5907 EHD Stop Arm"),
        ("EHD_HO_ARM","5912 EHD Hold Open Arm (specify hand)"),
        ("TRK_NHO",   "Track Arm - Non Hold Open"),
        ("TRK_HO",    "Track Arm - Hold Open"),
        ("PS_STOP",   "5926 Pull Side Stop Arm"),
        ("PS_HO",     "5927 Pull Side HO Stop Arm"),
        ("EHD_HO_CSH","5956 EHD HO Cushion Stop Arm"),
        ("EHD_CSH",   "5957 EHD Cushion Stop Arm"),
    ]
    options(conn, f, "config", configs)
    options(conn, f, "finish", PAINTED)

    cfg_prices = [
        ("STD",        264.21),
        ("HO",         316.54),
        ("EHD",        328.67),
        ("EHD_HO",     392.92),
        ("EHD_STOP",   328.67),
        ("EHD_HO_ARM", 310.71),
        ("TRK_NHO",    326.16),
        ("TRK_HO",     342.84),
        ("PS_STOP",    325.35),
        ("PS_HO",      352.46),
        ("EHD_HO_CSH", 516.15),
        ("EHD_CSH",    460.24),
    ]
    for cfg, painted in cfg_prices:
        for fin in _PK:
            price(conn, f, "config:finish", f"{cfg}:{fin}", painted)
