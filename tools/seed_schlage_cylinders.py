"""Seed Schlage sold-separate cylinder data from CYLINDERS.pdf (Pricebook 16).

Source: Schlage Pricebook 16, Effective February 27, 2026
Pages: CYLINDERS.pdf (32 pages)

Creates families:
  1. Conventional KIL Cylinders (Key-in-Knob/Lever)
  2. Conventional Deadbolt Cylinders
  3. Conventional Mortise Cylinders
  4. Conventional Rim Cylinders
  5. FSIC Cores
  6. FSIC Mortise Cylinders
  7. FSIC Rim Cylinders
  8. SFIC Cores
  9. SFIC Mortise Cylinders
  10. SFIC Rim Cylinders
  11. Competitive KIL Cylinders
  12. Letter/Mailbox Cylinders
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from seed_helpers import fid, slot, options, price, rule

# ── Shared mechanism options ─────────────────────────────────────────
STD_MECHS = [
    ("STD_OPEN",  "Standard (Open Keyway)"),
    ("STD_RESTR", "Standard (Restricted Keyway)"),
    ("PRIMUS",    "Primus / Primus XP / Primus RP"),
    ("UL437",     "Primus UL437 / XP / RP"),
    ("SL",        "Everest SL"),
    ("SL_PXP",    "SL Primus XP"),
    ("SL_UL437",  "SL Primus UL437"),
]


def _seed_table(conn, family_name, category, pattern, template,
                app_slot, app_label, apps, mech_slot, mech_label,
                mechs, pricing_data):
    """Generic seeder: application × mechanism → price.

    apps:         [(value, display), ...]
    mechs:        [(value, display), ...]
    pricing_data: [(app_value, mech_value, amount), ...] — only rows that exist
    """
    f = fid(conn, "Schlage", family_name, category, pattern, template)

    slot(conn, f, 1, app_slot, app_label, 1)
    slot(conn, f, 2, mech_slot, mech_label, 1)

    options(conn, f, app_slot, apps)
    options(conn, f, mech_slot, mechs)

    compound = f"{app_slot}:{mech_slot}"
    n = 0
    for app_val, mech_val, amt in pricing_data:
        price(conn, f, compound, f"{app_val}:{mech_val}", amt, "base")
        n += 1

    return n


# =====================================================================
# 1. CONVENTIONAL KIL CYLINDERS  (Pages 1-5)
# =====================================================================

_KIL_APPS = [
    # A Series
    ("A_ALL",          "A Series - All (except Orbit)"),
    ("A_ORBIT",        "A Series - Orbit (except A73)"),
    ("A_FAC",          "A Series - Faculty Restroom"),
    ("A_FAC_ORBIT",    "A Series - Faculty Restroom (Orbit)"),
    # AD / CO Series
    ("ADCO_CYL",       "AD/CO Series - Cylindrical / Exits ATH or 8AT"),
    ("ADCO_MORT",      "AD/CO Series - Mortise / Exits (non-ATH/8AT)"),
    # AL Series
    ("AL_ALL",         "AL Series - All Functions"),
    ("AL_FAC",         "AL Series - Faculty Restroom"),
    # ALX Series
    ("ALX_ALL",        "ALX Series - All (except Classroom)"),
    ("ALX_CLASS",      "ALX Series - Classroom"),
    # D Series
    ("D_KNOB",         "D Series - Knob"),
    ("D_KNOB_THICK",   "D Series - Knob (2\" to 2-1/4\" door)"),
    ("D_FAC_KNOB",     "D Series - Faculty Restroom (Knob)"),
    ("D_FAC_THICK",    "D Series - Faculty Restroom (2\" to 2-1/4\")"),
    ("D_LEVER",        "D Series - Lever"),
    ("D_FAC_LEVER",    "D Series - Faculty Restroom (Lever)"),
    # H Series
    ("H_ALL",          "H Series - All (except Orbit)"),
    ("H_ORBIT",        "H Series - Orbit (except A73)"),
    ("H_FAC",          "H Series - Faculty Restroom (except Orbit)"),
    ("H_FAC_ORBIT",    "H Series - Faculty Restroom (Orbit)"),
    # ND Series
    ("ND_ALL",         "ND Series - All (except Faculty Restroom)"),
    ("ND_FAC",         "ND Series - Faculty Restroom"),
    # S Series
    ("S_LEVER",        "S Series - Keyed Levers"),
    # S200 Series
    ("S200_LEVER",     "S200 Series - Keyed Levers"),
    ("S200_DB",        "S200 Series - Deadbolts"),
    # Portable Security
    ("CL_DOOR",        "Portable Security - CL Series (Door)"),
    ("CL_DRAWER",      "Portable Security - CL Series (Drawer)"),
    ("KS_PADLOCK",     "Portable Security - KS Series Padlocks"),
    ("KC_CABLE",       "Portable Security - KC Series Cables"),
]

# (app_value, mech_value, amount)
# Standard tier: $103 open / $137 restricted
_KIL_STD = 103.00
_KIL_STD_R = 137.00
_KIL_PRIM = 225.00
_KIL_UL = 294.00
_KIL_SL = 137.00
_KIL_SLPXP = 225.00
_KIL_SLUL = 294.00
_KIL_FAC_O = 152.00
_KIL_FAC_R = 186.00


def _kil_std(app):
    """Standard-price KIL rows ($103/$137/$225/$294/$137/$225/$294)."""
    return [
        (app, "STD_OPEN",  _KIL_STD),
        (app, "STD_RESTR", _KIL_STD_R),
        (app, "PRIMUS",    _KIL_PRIM),
        (app, "UL437",     _KIL_UL),
        (app, "SL",        _KIL_SL),
        (app, "SL_PXP",    _KIL_SLPXP),
        (app, "SL_UL437",  _KIL_SLUL),
    ]


def _kil_fac(app):
    """Faculty restroom KIL rows ($152/$186, no Primus/SL)."""
    return [
        (app, "STD_OPEN",  _KIL_FAC_O),
        (app, "STD_RESTR", _KIL_FAC_R),
    ]


def _kil_pricing():
    rows = []
    # A Series
    rows += _kil_std("A_ALL")
    rows += _kil_std("A_ORBIT")
    rows += _kil_fac("A_FAC")
    rows += _kil_fac("A_FAC_ORBIT")
    # AD/CO Series
    rows += _kil_std("ADCO_CYL")
    rows += _kil_std("ADCO_MORT")
    # AL Series
    rows += _kil_std("AL_ALL")
    rows += _kil_fac("AL_FAC")
    # ALX Series
    rows += _kil_std("ALX_ALL")
    rows += _kil_std("ALX_CLASS")
    # D Series
    rows += _kil_std("D_KNOB")
    rows += _kil_std("D_KNOB_THICK")
    rows += _kil_fac("D_FAC_KNOB")
    rows += _kil_fac("D_FAC_THICK")
    rows += _kil_std("D_LEVER")
    rows += _kil_fac("D_FAC_LEVER")
    # H Series
    rows += _kil_std("H_ALL")
    rows += _kil_std("H_ORBIT")
    rows += _kil_fac("H_FAC")
    rows += _kil_fac("H_FAC_ORBIT")
    # ND Series
    rows += _kil_std("ND_ALL")
    rows += _kil_fac("ND_FAC")
    # S Series — no SL UL437
    rows += [
        ("S_LEVER", "STD_OPEN",  103.00),
        ("S_LEVER", "STD_RESTR", 137.00),
        ("S_LEVER", "PRIMUS",    225.00),
        ("S_LEVER", "UL437",     294.00),
        ("S_LEVER", "SL",        137.00),
        ("S_LEVER", "SL_PXP",    225.00),
    ]
    # S200 Series
    rows += _kil_std("S200_LEVER")
    rows += _kil_std("S200_DB")
    # Portable Security
    rows += _kil_std("CL_DOOR")
    rows += _kil_std("CL_DRAWER")
    # KS/KC — no SL
    for app in ("KS_PADLOCK", "KC_CABLE"):
        rows += [
            (app, "STD_OPEN",  103.00),
            (app, "STD_RESTR", 137.00),
            (app, "PRIMUS",    225.00),
            (app, "UL437",     294.00),
        ]
    return rows


def _seed_kil(conn):
    n = _seed_table(
        conn,
        "Conventional KIL Cylinders",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage {application} Conventional KIL Cylinder - {mechanism}",
        "application", "Lock Series / Function", _KIL_APPS,
        "mechanism", "Cylinder Mechanism", STD_MECHS,
        _kil_pricing(),
    )
    return n


# =====================================================================
# 2. CONVENTIONAL DEADBOLT CYLINDERS  (Pages 6-11)
# =====================================================================

_DB_APPS = [
    # B250
    ("B250_CYL5",       "B250 - Cylinder Only 5-pin (Open keyway only)"),
    ("B250_CYL6",       "B250 - Cylinder Only 6-pin"),
    ("B250_HSG_OUT5",   "B250 - Cyl w/ Housing Outside 5-pin"),
    ("B250_HSG_OUT6",   "B250 - Cyl w/ Housing Outside 6-pin"),
    ("B250_HSG_IN6",    "B250 - Cyl w/ Housing Inside 6-pin"),
    ("B250_HONLY_OUT",  "B250 - Housing Only Outside (Conventional)"),
    ("B250_HONLY_IN",   "B250 - Housing Only Inside (Conventional)"),
    ("B250_HONLY_FSIC", "B250 - Housing Only (FSIC, w/ tailpiece)"),
    # B500 Single
    ("B500_SC_STD",     "B500 - Single Cyl (B560/B563) 1-3/8\" to 1-3/4\""),
    ("B500_SC_THICK",   "B500 - Single Cyl (B560/B563) >1-3/4\" to 2-1/4\""),
    ("B500_SC_B561",    "B500 - Single Cyl (B561) 1-3/8\" to 2-1/4\""),
    # B500 Double
    ("B500_DC_STD",     "B500 - Double Cyl (B562) 1-3/8\" to 1-3/4\""),
    ("B500_DC_THICK",   "B500 - Double Cyl (B562) >1-3/4\" to 2-1/4\""),
    # B600/B700/B800 Single
    ("B600_SC_STD",     "B600 - Single Cyl (B660/B663) 1-3/8\" to 2-1/2\""),
    ("B600_SC_B661_S",  "B600 - Single Cyl (B661/B664) 1-3/8\" to 2\""),
    ("B600_SC_B661_L",  "B600 - Single Cyl (B661/B664) >2\" to 2-1/2\""),
    # B600 Double
    ("B600_DC_STD",     "B600 - Double Cyl (B662) 1-3/8\" to 2\""),
    ("B600_DC_THICK",   "B600 - Double Cyl (B662) >2\" to 2-1/2\""),
    # B600 Housing only
    ("B600_H_OUT",      "B600 - Housing Only Outside (B660/B661/B663)"),
    ("B600_H_OUT_DC",   "B600 - Housing Only Outside (B662)"),
    ("B600_H_IN_DC",    "B600 - Housing Only Inside (B662)"),
    # CS200
    ("CS200_SC",        "CS200 - Single Cylinder 6-pin"),
    # H Series (deadbolt section)
    ("H_CYL_ONLY",      "H Series - Cylinder Only 6-pin"),
    ("H_CYL_HSG",       "H Series - Cyl w/ Housing 6-pin"),
    ("H_HSG_CONV",      "H Series - Housing Only (Conventional)"),
]

_DB_MECHS = STD_MECHS  # same 7 mechanisms


def _db_pricing():
    rows = []
    # B250 Cylinder only 5-pin (open only)
    rows.append(("B250_CYL5", "STD_OPEN", 103.00))
    # B250 Cylinder only 6-pin
    rows += [("B250_CYL6", m, p) for m, p in [
        ("STD_OPEN", 103.00), ("STD_RESTR", 137.00),
        ("PRIMUS", 225.00), ("UL437", 294.00),
        ("SL", 137.00), ("SL_PXP", 225.00), ("SL_UL437", 294.00),
    ]]
    # B250 Cyl w/ Housing Outside 5-pin (open only)
    rows.append(("B250_HSG_OUT5", "STD_OPEN", 103.00))
    # B250 Cyl w/ Housing 6-pin
    for app in ("B250_HSG_OUT6", "B250_HSG_IN6"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 103.00), ("STD_RESTR", 137.00),
            ("PRIMUS", 225.00), ("UL437", 294.00),
        ]]
    # B250 Housing only
    for app, amt in [("B250_HONLY_OUT", 46.20), ("B250_HONLY_IN", 46.20)]:
        rows.append((app, "STD_OPEN", amt))
    rows.append(("B250_HONLY_FSIC", "STD_OPEN", 117.00))
    # B500 Single
    for app in ("B500_SC_STD", "B500_SC_THICK", "B500_SC_B561"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 103.00), ("STD_RESTR", 137.00),
            ("PRIMUS", 225.00), ("UL437", 294.00),
        ]]
    rows += [("B500_SC_STD", "SL", 137.00), ("B500_SC_STD", "SL_PXP", 225.00), ("B500_SC_STD", "SL_UL437", 294.00)]
    rows += [("B500_SC_THICK", "SL", 137.00), ("B500_SC_THICK", "SL_PXP", 225.00)]
    rows += [("B500_SC_B561", "SL", 137.00), ("B500_SC_B561", "SL_PXP", 225.00), ("B500_SC_B561", "SL_UL437", 294.00)]
    # B500 Double
    for app in ("B500_DC_STD", "B500_DC_THICK"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 103.00), ("STD_RESTR", 137.00),
            ("PRIMUS", 225.00), ("UL437", 294.00),
        ]]
    rows += [("B500_DC_STD", "SL", 137.00), ("B500_DC_STD", "SL_PXP", 225.00), ("B500_DC_STD", "SL_UL437", 294.00)]
    rows += [("B500_DC_THICK", "SL", 137.00), ("B500_DC_THICK", "SL_PXP", 225.00)]
    # B600 Single
    for app in ("B600_SC_STD", "B600_SC_B661_S", "B600_SC_B661_L"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 103.00), ("STD_RESTR", 137.00),
            ("PRIMUS", 225.00), ("UL437", 294.00),
            ("SL", 137.00), ("SL_PXP", 225.00), ("SL_UL437", 294.00),
        ]]
    # B600 Double
    for app in ("B600_DC_STD", "B600_DC_THICK"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 103.00), ("STD_RESTR", 137.00),
            ("PRIMUS", 225.00), ("UL437", 294.00),
            ("SL", 137.00), ("SL_PXP", 225.00), ("SL_UL437", 294.00),
        ]]
    # B600 Housing only
    for app in ("B600_H_OUT", "B600_H_OUT_DC"):
        rows.append((app, "STD_OPEN", 101.00))
    rows.append(("B600_H_IN_DC", "STD_OPEN", 103.00))
    # CS200
    rows += [("CS200_SC", "STD_OPEN", 103.00), ("CS200_SC", "STD_RESTR", 137.00),
             ("CS200_SC", "SL", 137.00)]
    # H Series deadbolt
    for app in ("H_CYL_ONLY", "H_CYL_HSG"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 103.00), ("STD_RESTR", 137.00),
            ("PRIMUS", 225.00), ("UL437", 294.00),
        ]]
    rows.append(("H_HSG_CONV", "STD_OPEN", 46.20))
    return rows


def _seed_deadbolt(conn):
    return _seed_table(
        conn,
        "Conventional Deadbolt Cylinders",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage {application} Deadbolt Cylinder - {mechanism}",
        "application", "Lock Series / Configuration", _DB_APPS,
        "mechanism", "Cylinder Mechanism", _DB_MECHS,
        _db_pricing(),
    )


# =====================================================================
# 3. CONVENTIONAL MORTISE CYLINDERS  (Pages 12-14)
# =====================================================================

_MORT_APPS = [
    # L Series (except L9060)
    ("L_LN_CYL",        "L Series - L/N Escutcheon, Cylinder Only"),
    ("L_LN_LM",         "L Series - L/N Esc, LM9280/LM9380/LMV9380"),
    ("L_LN_FAC",        "L Series - L/N Esc, Faculty Restroom"),
    ("L_CONC",          "L Series - Concealed (L-Esc), Cylinder Only"),
    ("L_CONC_FAC",      "L Series - Concealed (L-Esc), Faculty Restroom"),
    ("L_ROSE",          "L Series - Rose Trim w/ Comp Ring & Spring"),
    ("L_ROSE_LM",       "L Series - Rose Trim, LM9280/LM9380/LMV9380"),
    ("L_ROSE_FAC",      "L Series - Rose Trim, Faculty Restroom"),
    # L9060 / Von Duprin
    ("VD_SPRING",       "L9060/Von Duprin - Cyl w/ Comp Spring"),
    ("VD_RING",         "L9060/Von Duprin - Cyl w/ Comp Ring & Spring"),
    ("VD_LOCKOUT",      "L9060/Von Duprin - Lockout Function"),
    ("VD_AR2331",       "L9060/Von Duprin - Adams Rite 2331 (1-1/8\" only)"),
    ("VD_CONC",         "L9060/Von Duprin - Concealed (L-Esc)"),
    # Competitor Mortise
    ("AR_MS4500_CYL",   "Adams Rite MS/4500/4700 - Cylinder Only"),
    ("AR_MS4500_BLOCK", "Adams Rite MS/4500/4700 - w/ 3/8\" Blocking Ring"),
    ("AR_MS4500_LO",    "Adams Rite MS/4500/4700 - Lockout"),
    ("AR_4070",         "Adams Rite 4070 - Cylinder Only"),
    ("CR_MASTER",       "Corbin Russwin Master Ring"),
]


def _mort_pricing():
    rows = []
    # L/N Escutcheon cylinder only
    rows += [("L_LN_CYL", m, p) for m, p in [
        ("STD_OPEN", 122.00), ("STD_RESTR", 156.00),
        ("PRIMUS", 244.00), ("UL437", 313.00),
        ("SL", 156.00), ("SL_PXP", 244.00),
    ]]
    # L/N Esc LM9280 etc.
    rows += [("L_LN_LM", m, p) for m, p in [
        ("STD_OPEN", 122.00), ("STD_RESTR", 156.00),
    ]]
    # L/N Esc Faculty Restroom
    rows += [("L_LN_FAC", m, p) for m, p in [
        ("STD_OPEN", 200.00), ("STD_RESTR", 234.00),
    ]]
    # Concealed (L-Esc)
    rows += [("L_CONC", m, p) for m, p in [
        ("STD_OPEN", 157.00), ("STD_RESTR", 191.00),
        ("PRIMUS", 279.00), ("UL437", 348.00),
    ]]
    # Concealed Faculty Restroom
    rows += [("L_CONC_FAC", m, p) for m, p in [
        ("STD_OPEN", 235.00), ("STD_RESTR", 269.00),
    ]]
    # Rose trim w/ comp ring & spring
    rows += [("L_ROSE", m, p) for m, p in [
        ("STD_OPEN", 130.00), ("STD_RESTR", 164.00),
        ("PRIMUS", 252.00), ("UL437", 321.00),
        ("SL", 164.00), ("SL_PXP", 252.00), ("SL_UL437", 321.00),
    ]]
    # Rose trim LM9280 etc.
    rows += [("L_ROSE_LM", m, p) for m, p in [
        ("STD_OPEN", 130.00), ("STD_RESTR", 164.00),
    ]]
    # Rose trim Faculty Restroom
    rows += [("L_ROSE_FAC", m, p) for m, p in [
        ("STD_OPEN", 208.00), ("STD_RESTR", 242.00),
    ]]
    # L9060 / Von Duprin — cyl w/ comp spring
    rows += [("VD_SPRING", m, p) for m, p in [
        ("STD_OPEN", 126.00), ("STD_RESTR", 160.00),
        ("PRIMUS", 248.00), ("UL437", 317.00),
        ("SL", 160.00), ("SL_PXP", 248.00), ("SL_UL437", 317.00),
    ]]
    # L9060 / VD — cyl w/ comp ring & spring
    rows += [("VD_RING", m, p) for m, p in [
        ("STD_OPEN", 130.00), ("STD_RESTR", 164.00),
        ("PRIMUS", 252.00), ("UL437", 321.00),
        ("SL", 164.00), ("SL_PXP", 252.00), ("SL_UL437", 321.00),
    ]]
    # Lockout
    rows += [("VD_LOCKOUT", m, p) for m, p in [
        ("PRIMUS", 337.00), ("UL437", 406.00),
    ]]
    # Adams Rite 2331 (1-1/8" only)
    rows += [("VD_AR2331", m, p) for m, p in [
        ("STD_OPEN", 137.00), ("STD_RESTR", 171.00),
        ("PRIMUS", 259.00), ("UL437", 328.00),
        ("SL", 171.00), ("SL_PXP", 259.00), ("SL_UL437", 328.00),
    ]]
    # Concealed (L9060 / VD)
    rows += [("VD_CONC", m, p) for m, p in [
        ("STD_OPEN", 157.00), ("STD_RESTR", 191.00),
        ("PRIMUS", 279.00), ("UL437", 348.00),
    ]]
    # Adams Rite MS/4500/4700 — cyl only
    rows += [("AR_MS4500_CYL", m, p) for m, p in [
        ("STD_OPEN", 122.00), ("STD_RESTR", 156.00),
    ]]
    # AR MS/4500 — w/ blocking ring
    rows += [("AR_MS4500_BLOCK", m, p) for m, p in [
        ("STD_OPEN", 130.00), ("STD_RESTR", 164.00),
        ("PRIMUS", 252.00), ("UL437", 321.00),
        ("SL", 164.00), ("SL_PXP", 252.00), ("SL_UL437", 321.00),
    ]]
    # AR lockout
    rows += [("AR_MS4500_LO", m, p) for m, p in [
        ("PRIMUS", 337.00), ("UL437", 406.00),
    ]]
    # Adams Rite 4070
    rows += [("AR_4070", m, p) for m, p in [
        ("STD_OPEN", 122.00), ("STD_RESTR", 156.00),
        ("PRIMUS", 244.00), ("UL437", 313.00),
        ("SL", 156.00), ("SL_PXP", 244.00), ("SL_UL437", 313.00),
    ]]
    # Corbin Russwin Master Ring
    rows += [("CR_MASTER", m, p) for m, p in [
        ("STD_OPEN", 297.00), ("STD_RESTR", 331.00),
        ("PRIMUS", 419.00), ("UL437", 488.00),
    ]]
    return rows


def _seed_mortise(conn):
    return _seed_table(
        conn,
        "Conventional Mortise Cylinders",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage Mortise Cylinder - {application} {mechanism}",
        "application", "Application", _MORT_APPS,
        "mechanism", "Cylinder Mechanism", STD_MECHS,
        _mort_pricing(),
    )


# =====================================================================
# 4. CONVENTIONAL RIM CYLINDERS  (Page 15)
# =====================================================================

_RIM_APPS = [
    ("RIM_HORIZ",      "Rim Cylinder - Horizontal Tailpiece"),
    ("RIM_VERT",       "Rim Cylinder - Vertical Tailpiece"),
    ("RIM_LO_HORIZ",   "Rim Cylinder - Lockout (Horizontal)"),
    ("THUMB_STD",      "Thumbturn - Standard (Horizontal)"),
    ("THUMB_ADA",      "Thumbturn - ADA (Horizontal)"),
]

_RIM_MECHS = STD_MECHS


def _rim_pricing():
    rows = []
    for app in ("RIM_HORIZ", "RIM_VERT"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 122.00), ("STD_RESTR", 156.00),
            ("PRIMUS", 244.00), ("UL437", 313.00),
            ("SL", 156.00), ("SL_PXP", 244.00), ("SL_UL437", 313.00),
        ]]
    # Lockout (Primus only)
    rows += [("RIM_LO_HORIZ", m, p) for m, p in [
        ("PRIMUS", 329.00), ("UL437", 398.00),
    ]]
    # Thumbturns
    for app in ("THUMB_STD", "THUMB_ADA"):
        rows.append((app, "STD_OPEN", 190.00))
    return rows


def _seed_rim(conn):
    return _seed_table(
        conn,
        "Conventional Rim Cylinders",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage Rim Cylinder - {application} {mechanism}",
        "application", "Configuration", _RIM_APPS,
        "mechanism", "Cylinder Mechanism", _RIM_MECHS,
        _rim_pricing(),
    )


# =====================================================================
# 5. FSIC CORES  (Page 16)
# =====================================================================

_FSIC_CORE_APPS = [
    ("FSIC_LOGO",       "FSIC Core - With Logo (23-030 / 20-740)"),
    ("FSIC_NOLOGO",     "FSIC Core - Without Logo (23-031 / 20-741)"),
    ("FSIC_FAC_LOGO",   "FSIC Core - Faculty Restroom, With Logo (30-120)"),
    ("FSIC_FAC_NOLOGO", "FSIC Core - Faculty Restroom, Without Logo (30-121)"),
    # LFIC (Competitive)
    ("LFIC_SAR_COMB",   "LFIC - Sargent Combinated"),
    ("LFIC_SAR_UNCOMB", "LFIC - Sargent Uncombinated"),
    ("LFIC_CR_COMB",    "LFIC - Corbin Russwin Combinated"),
    ("LFIC_CR_UNCOMB",  "LFIC - Corbin Russwin Uncombinated"),
]

_FSIC_MECHS = [
    ("STD_OPEN",  "Standard (Open Keyway)"),
    ("STD_RESTR", "Standard (Restricted Keyway)"),
    ("PRIMUS",    "Primus / Primus XP / Primus RP"),
    ("SL",        "Everest SL"),
    ("SL_PXP",    "SL Primus XP"),
]


def _fsic_core_pricing():
    rows = []
    for app in ("FSIC_LOGO", "FSIC_NOLOGO"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 115.00), ("STD_RESTR", 149.00),
            ("PRIMUS", 237.00),
            ("SL", 149.00), ("SL_PXP", 237.00),
        ]]
    for app in ("FSIC_FAC_LOGO", "FSIC_FAC_NOLOGO"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 193.00), ("STD_RESTR", 227.00),
        ]]
    # LFIC
    for app in ("LFIC_SAR_COMB", "LFIC_CR_COMB"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 115.00), ("STD_RESTR", 149.00),
            ("PRIMUS", 237.00),
        ]]
    for app in ("LFIC_SAR_UNCOMB", "LFIC_CR_UNCOMB"):
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 75.00), ("STD_RESTR", 109.00),
            ("PRIMUS", 197.00),
        ]]
    return rows


def _seed_fsic_cores(conn):
    return _seed_table(
        conn,
        "FSIC Cores",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage FSIC Core - {application} {mechanism}",
        "application", "Core Type", _FSIC_CORE_APPS,
        "mechanism", "Cylinder Mechanism", _FSIC_MECHS,
        _fsic_core_pricing(),
    )


# =====================================================================
# 6. FSIC MORTISE CYLINDERS  (Pages 17-18)
# =====================================================================

_FSIC_MORT_APPS = [
    # L Series (except L9060)
    ("FSIC_L_LN",       "L Series - L/N Esc, Core & Housing (30-008)"),
    ("FSIC_L_LN_FAC",   "L Series - L/N Esc, Faculty Restroom (30-010)"),
    ("FSIC_L_ROSE",     "L Series - Rose Trim w/ Blocking Ring (30-138)"),
    ("FSIC_L_ROSE_FAC", "L Series - Rose Trim, Faculty Restroom (30-140)"),
    ("FSIC_L_HONLY",    "L Series - Housing Only (30-016 / 30-007)"),
    # L9060
    ("FSIC_L9060_LN",   "L9060 - L/N Esc, Core & Housing (30-030)"),
    ("FSIC_L9060_ROSE", "L9060 - Rose Trim (No Std/SL)"),
    ("FSIC_L9060_HONLY","L9060 - Housing Only (30-032)"),
    # LM9280 etc.
    ("FSIC_LM_CORE",    "LM9280/LM9380 - Core & Housing"),
    ("FSIC_LM_HONLY",   "LM9280/LM9380 - Housing Only (26-102)"),
    # Von Duprin
    ("FSIC_VD_CORE",    "Von Duprin - Core & Housing (26-091)"),
    ("FSIC_VD_BLOCK",   "Von Duprin - w/ 3/8\" Blocking Ring (20-061)"),
    ("FSIC_VD_HONLY",   "Von Duprin - Housing Only (20-059 / 26-064)"),
    # Adams Rite MS/4500
    ("FSIC_AR_CORE",    "Adams Rite MS/4500 - Core & Housing (26-098)"),
    ("FSIC_AR_BLOCK",   "Adams Rite MS/4500 - w/ Blocking Rings (20-062)"),
    ("FSIC_AR_HONLY",   "Adams Rite MS/4500 - Housing Only (20-060)"),
    # Adams Rite 4070
    ("FSIC_AR4070",     "Adams Rite 4070 - Core & Housing (20-091)"),
    ("FSIC_AR4070_HONLY","Adams Rite 4070 - Housing Only (20-090)"),
]


def _fsic_mort_pricing():
    rows = []
    # L Series L/N Esc
    rows += [("FSIC_L_LN", m, p) for m, p in [
        ("STD_OPEN", 235.00), ("STD_RESTR", 269.00),
        ("PRIMUS", 357.00),
        ("SL", 269.00), ("SL_PXP", 357.00),
    ]]
    rows += [("FSIC_L_LN_FAC", m, p) for m, p in [
        ("STD_OPEN", 284.00), ("STD_RESTR", 318.00),
    ]]
    # L Series Rose trim
    rows += [("FSIC_L_ROSE", m, p) for m, p in [
        ("STD_OPEN", 242.00), ("STD_RESTR", 276.00),
        ("PRIMUS", 364.00),
        ("SL", 276.00), ("SL_PXP", 364.00),
    ]]
    rows += [("FSIC_L_ROSE_FAC", m, p) for m, p in [
        ("STD_OPEN", 291.00), ("STD_RESTR", 325.00),
    ]]
    rows.append(("FSIC_L_HONLY", "STD_OPEN", 112.00))
    # L9060
    rows += [("FSIC_L9060_LN", m, p) for m, p in [
        ("STD_OPEN", 235.00), ("STD_RESTR", 269.00),
        ("PRIMUS", 357.00),
        ("SL", 269.00), ("SL_PXP", 357.00),
    ]]
    rows += [("FSIC_L9060_ROSE", "PRIMUS", 364.00)]
    rows.append(("FSIC_L9060_HONLY", "STD_OPEN", 112.00))
    # LM9280 etc.
    rows += [("FSIC_LM_CORE", m, p) for m, p in [
        ("STD_OPEN", 235.00), ("STD_RESTR", 269.00),
    ]]
    rows.append(("FSIC_LM_HONLY", "STD_OPEN", 120.00))
    # Von Duprin
    rows += [("FSIC_VD_CORE", m, p) for m, p in [
        ("STD_OPEN", 235.00), ("STD_RESTR", 269.00),
        ("PRIMUS", 357.00),
        ("SL", 269.00), ("SL_PXP", 357.00),
    ]]
    rows += [("FSIC_VD_BLOCK", m, p) for m, p in [
        ("STD_OPEN", 242.00), ("STD_RESTR", 276.00),
        ("PRIMUS", 364.00),
        ("SL", 276.00), ("SL_PXP", 364.00),
    ]]
    rows.append(("FSIC_VD_HONLY", "STD_OPEN", 112.00))
    # Adams Rite MS/4500
    rows += [("FSIC_AR_CORE", m, p) for m, p in [
        ("STD_OPEN", 235.00), ("STD_RESTR", 269.00),
        ("SL", 269.00),
    ]]
    rows += [("FSIC_AR_BLOCK", m, p) for m, p in [
        ("STD_OPEN", 242.00), ("STD_RESTR", 276.00),
        ("PRIMUS", 364.00),
        ("SL", 276.00), ("SL_PXP", 364.00),
    ]]
    rows.append(("FSIC_AR_HONLY", "STD_OPEN", 112.00))
    # Adams Rite 4070
    rows += [("FSIC_AR4070", m, p) for m, p in [
        ("STD_OPEN", 242.00), ("STD_RESTR", 276.00),
        ("PRIMUS", 364.00),
        ("SL", 276.00), ("SL_PXP", 364.00),
    ]]
    rows.append(("FSIC_AR4070_HONLY", "STD_OPEN", 112.00))
    return rows


def _seed_fsic_mortise(conn):
    return _seed_table(
        conn,
        "FSIC Mortise Cylinders",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage FSIC Mortise Cylinder - {application} {mechanism}",
        "application", "Application", _FSIC_MORT_APPS,
        "mechanism", "Cylinder Mechanism", _FSIC_MECHS,
        _fsic_mort_pricing(),
    )


# =====================================================================
# 7. FSIC RIM CYLINDERS  (Page 19)
# =====================================================================

_FSIC_RIM_APPS = [
    ("FSIC_RIM",    "FSIC Rim - Core & Housing (20-057 / 20-757)"),
    ("FSIC_RIM_H",  "FSIC Rim - Housing Only (20-079)"),
]


def _fsic_rim_pricing():
    rows = []
    rows += [("FSIC_RIM", m, p) for m, p in [
        ("STD_OPEN", 227.00), ("STD_RESTR", 261.00),
        ("PRIMUS", 349.00),
        ("SL", 261.00), ("SL_PXP", 349.00),
    ]]
    rows.append(("FSIC_RIM_H", "STD_OPEN", 112.00))
    return rows


def _seed_fsic_rim(conn):
    return _seed_table(
        conn,
        "FSIC Rim Cylinders",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage FSIC Rim Cylinder - {application} {mechanism}",
        "application", "Configuration", _FSIC_RIM_APPS,
        "mechanism", "Cylinder Mechanism", _FSIC_MECHS,
        _fsic_rim_pricing(),
    )


# =====================================================================
# 8. SFIC CORES  (Page 20)
# =====================================================================

_SFIC_APPS = [
    ("SFIC_COMB",    "Everest 29/Everest - Combinated (80-037)"),
    ("SFIC_UNCOMB",  "Everest 29/Everest - Uncombinated (80-036)"),
    ("SFIC_7PIN",    "7-pin Uncombinated, BEST Keyways (80-033)"),
    ("SFIC_6PIN",    "6-pin Uncombinated, BEST Keyways (80-043)"),
]

_SFIC_MECHS = [
    ("STD_RESTR", "Standard (Restricted Keyway)"),
    ("STD_OPEN",  "Standard (Open Keyway)"),
]


def _sfic_core_pricing():
    return [
        ("SFIC_COMB",   "STD_RESTR", 135.00),
        ("SFIC_UNCOMB", "STD_RESTR",  95.00),
        ("SFIC_7PIN",   "STD_RESTR",  64.00),
        ("SFIC_6PIN",   "STD_RESTR",  64.00),
    ]


def _seed_sfic_cores(conn):
    return _seed_table(
        conn,
        "SFIC Cores",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage SFIC Core - {application}",
        "application", "Core Type", _SFIC_APPS,
        "mechanism", "Keyway", _SFIC_MECHS,
        _sfic_core_pricing(),
    )


# =====================================================================
# 9. SFIC MORTISE CYLINDERS  (Page 21)
# =====================================================================

_SFIC_MORT_APPS = [
    ("SFIC_L_LN",     "L Series - L/N Esc (80-308)"),
    ("SFIC_L_ROSE",   "L Series - Rose Trim (80-301)"),
    ("SFIC_L9060",    "L9060 - L/N Esc (80-304)"),
    ("SFIC_LM",       "LM9280/LM9380 (26-106)"),
    ("SFIC_VD",       "Von Duprin - w/ Blocking Ring (80-302)"),
    ("SFIC_AR_MS",    "Adams Rite MS/4500 - w/ Blocking Ring (80-303)"),
    ("SFIC_AR_4070",  "Adams Rite 4070 - w/ Blocking Ring (80-305)"),
]

_SFIC_MORT_MECHS = [
    ("STD_RESTR",    "Standard (Restricted)"),
    ("KEYED",        "Keyed Core"),
    ("DISPOSABLE",   "Disposable / Construction Core"),
]


def _sfic_mort_pricing():
    rows = []
    # All L-Series, LM, and standard apps: $255 restricted, $190 keyed, $120 disp
    for app in ("SFIC_L_LN", "SFIC_L9060", "SFIC_LM", "SFIC_AR_MS"):
        rows += [(app, m, p) for m, p in [
            ("STD_RESTR", 255.00), ("KEYED", 190.00), ("DISPOSABLE", 120.00),
        ]]
    # Rose trim & blocking ring apps: $262, $197, $127
    for app in ("SFIC_L_ROSE", "SFIC_VD", "SFIC_AR_4070"):
        rows += [(app, m, p) for m, p in [
            ("STD_RESTR", 262.00), ("KEYED", 197.00), ("DISPOSABLE", 127.00),
        ]]
    return rows


def _seed_sfic_mortise(conn):
    return _seed_table(
        conn,
        "SFIC Mortise Cylinders",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage SFIC Mortise Cylinder - {application} {mechanism}",
        "application", "Application", _SFIC_MORT_APPS,
        "mechanism", "Core Type", _SFIC_MORT_MECHS,
        _sfic_mort_pricing(),
    )


# =====================================================================
# 10. SFIC RIM CYLINDERS  (Page 22)
# =====================================================================

_SFIC_RIM_APPS = [
    ("SFIC_RIM",    "SFIC Rim - Core & Housing (80-329)"),
    ("SFIC_RIM_H",  "SFIC Rim - Housing Only (80-129)"),
]


def _sfic_rim_pricing():
    return [
        ("SFIC_RIM", "STD_RESTR",  247.00),
        ("SFIC_RIM", "KEYED",      182.00),
        ("SFIC_RIM", "DISPOSABLE", 112.00),
        ("SFIC_RIM_H", "STD_RESTR", 112.00),
    ]


def _seed_sfic_rim(conn):
    f = fid(conn, "Schlage", "SFIC Rim Cylinders", "Cylinder",
            "{application} {mechanism}",
            "Schlage SFIC Rim Cylinder - {application} {mechanism}")

    slot(conn, f, 1, "application", "Configuration", 1)
    slot(conn, f, 2, "mechanism", "Core Type", 1)

    options(conn, f, "application", _SFIC_RIM_APPS)
    mechs = [
        ("STD_RESTR",  "Standard (Restricted)"),
        ("KEYED",      "Keyed Core"),
        ("DISPOSABLE", "Disposable / Construction Core"),
    ]
    options(conn, f, "mechanism", mechs)

    n = 0
    for app, mech, amt in _sfic_rim_pricing():
        price(conn, f, "application:mechanism", f"{app}:{mech}", amt, "base")
        n += 1
    return n


# =====================================================================
# 11. COMPETITIVE KIL CYLINDERS  (Pages 23-24)
# =====================================================================

_COMP_APPS = [
    ("CR_CL3300",      "Corbin Russwin CL3300"),
    ("CR_CL3400",      "Corbin Russwin CL3400 / CL3600"),
    ("CR_CK4200",      "Corbin Russwin CK4200 / UT5200"),
    ("SAR_LEVER",      "Sargent 7L/8L/10L (Levers)"),
    ("SAR_KNOB",       "Sargent 7L/8L/10L (Knobs)"),
    ("SAR_6L",         "Sargent 6L (except B Knob)"),
    ("YALE_LEVER",     "Yale 5300LN/5400LN (Levers)"),
    ("YALE_KNOB",      "Yale 5300LN/5400LN/6200 (Knobs)"),
    ("FAL_B611",       "Falcon B611/T381(IS/W)/W (except 561)"),
    ("FAL_T",          "Falcon T (except 571 and 381 inside)"),
    ("FAL_T571",       "Falcon T571"),
    ("FAL_W561_K",     "Falcon W561 (Knobs)"),
    ("FAL_W561_L",     "Falcon W561 (Levers)"),
    ("FAL_M",          "Falcon M Series"),
    ("FAL_B",          "Falcon B Series (except 611)"),
]


def _comp_pricing():
    rows = []
    # All have standard $103/$137, Primus $225, UL437 $294
    for app, _, in _COMP_APPS:
        rows += [(app, m, p) for m, p in [
            ("STD_OPEN", 103.00), ("STD_RESTR", 137.00),
            ("PRIMUS", 225.00), ("UL437", 294.00),
        ]]
    # SL pricing (from page 24)
    _sl_map = {
        "CR_CL3300":   {"SL": 137.00, "SL_PXP": 225.00},
        "CR_CL3400":   {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "SAR_LEVER":   {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "SAR_KNOB":    {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "SAR_6L":      {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "YALE_LEVER":  {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "YALE_KNOB":   {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "FAL_B611":    {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "FAL_T":       {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "FAL_T571":    {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "FAL_W561_K":  {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
        "FAL_W561_L":  {"SL": 137.00, "SL_PXP": 225.00, "SL_UL437": 294.00},
    }
    for app, sl_data in _sl_map.items():
        for m, p in sl_data.items():
            rows.append((app, m, p))
    return rows


def _seed_competitive(conn):
    return _seed_table(
        conn,
        "Competitive KIL Cylinders",
        "Cylinder",
        "{application} {mechanism}",
        "Schlage Competitive Cylinder - {application} {mechanism}",
        "application", "Brand / Lock Series", _COMP_APPS,
        "mechanism", "Cylinder Mechanism", STD_MECHS,
        _comp_pricing(),
    )


# =====================================================================
# 12. LETTER / MAILBOX CYLINDERS  (Page 24)
# =====================================================================

_MAIL_APPS = [
    ("MAIL_AUTH",     "Auth 466/470/480 Series (20-067)"),
    ("MAIL_BOMMER",   "Bommer Vertical Mailbox (20-001-118)"),
    ("MAIL_FEDCHUTE", "Bommer/Florence/Cutler/Federal Equip (20-069)"),
]


def _mail_pricing():
    return [
        ("MAIL_AUTH",     "STD_OPEN", 150.00),
        ("MAIL_AUTH",     "STD_RESTR", 184.00),
        ("MAIL_BOMMER",   "STD_OPEN", 130.00),
        ("MAIL_BOMMER",   "STD_RESTR", 164.00),
        ("MAIL_FEDCHUTE", "STD_OPEN", 150.00),
        ("MAIL_FEDCHUTE", "STD_RESTR", 184.00),
    ]


def _seed_mailbox(conn):
    f = fid(conn, "Schlage", "Letter/Mailbox Cylinders", "Cylinder",
            "{application} {mechanism}",
            "Schlage Mailbox Cylinder - {application}")

    slot(conn, f, 1, "application", "Mailbox Type", 1)
    slot(conn, f, 2, "mechanism", "Keyway", 1)

    options(conn, f, "application", _MAIL_APPS)
    options(conn, f, "mechanism", [
        ("STD_OPEN", "Classic / Everest (Open)"),
        ("STD_RESTR", "Everest (Restricted)"),
    ])

    n = 0
    for app, mech, amt in _mail_pricing():
        price(conn, f, "application:mechanism", f"{app}:{mech}", amt, "base")
        n += 1
    return n


# =====================================================================
# MAIN SEED ENTRY POINT
# =====================================================================

def seed(conn):
    """Seed all Schlage sold-separate cylinder families."""
    total = 0
    families = 0

    seeders = [
        ("Conventional KIL Cylinders",     _seed_kil),
        ("Conventional Deadbolt Cylinders", _seed_deadbolt),
        ("Conventional Mortise Cylinders",  _seed_mortise),
        ("Conventional Rim Cylinders",      _seed_rim),
        ("FSIC Cores",                      _seed_fsic_cores),
        ("FSIC Mortise Cylinders",          _seed_fsic_mortise),
        ("FSIC Rim Cylinders",              _seed_fsic_rim),
        ("SFIC Cores",                      _seed_sfic_cores),
        ("SFIC Mortise Cylinders",          _seed_sfic_mortise),
        ("SFIC Rim Cylinders",              _seed_sfic_rim),
        ("Competitive KIL Cylinders",       _seed_competitive),
        ("Letter/Mailbox Cylinders",        _seed_mailbox),
    ]

    for name, fn in seeders:
        n = fn(conn)
        print(f"  Schlage {name}: {n} pricing rows")
        total += n
        families += 1

    print(f"  Schlage Cylinders TOTAL: {families} families, {total} pricing rows")
    return total


if __name__ == "__main__":
    import sqlite3
    db = os.path.join(os.path.dirname(__file__), "..", "data", "hw_configurator.db")
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = ON")
    seed(conn)
    conn.commit()
    conn.close()
