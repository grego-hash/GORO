"""Seed Emtek and Baldwin architectural/decorative hardware."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_emtek(conn)
    _seed_baldwin(conn)
    print("  Emtek + Baldwin seeded.")


# ═════════════════════════════════════════════════════════════════════
# Emtek – Architectural Levers and Deadbolts
# ═════════════════════════════════════════════════════════════════════

def _seed_emtek(conn):
    # ── Emtek Lever Set ──
    f = fid(conn, "Emtek", "Lever Set",
            "Architectural Lockset",
            "{function} {lever} {rosette} {finish}",
            "Emtek {function} {lever} on {rosette} Rosette {finish}")

    slot(conn, f, 1, "function", "Function",       1)
    slot(conn, f, 2, "lever",    "Lever Style",    1)
    slot(conn, f, 3, "rosette",  "Rosette / Plate",1)
    slot(conn, f, 4, "finish",   "Finish",         1)

    options(conn, f, "function", [
        ("Passage", "Passage"),
        ("Privacy", "Privacy"),
        ("Entry",   "Keyed Entry"),
        ("Dummy",   "Dummy / Inactive"),
    ])

    options(conn, f, "lever", [
        ("Helios",  "Helios Lever"),
        ("Hercules","Hercules Lever"),
        ("Luzern",  "Luzern Lever"),
        ("Milano",  "Milano Lever"),
        ("Argos",   "Argos Lever"),
        ("Cortina", "Cortina Lever"),
    ])

    options(conn, f, "rosette", [
        ("Disk",  "Disk Rosette"),
        ("Rectangular","Rectangular Rosette"),
        ("CFD",   "Cimarron Faceted Diamond"),
        ("Neos",  "Neos Rosette"),
        ("Plate", "Sideplate (Full Length)"),
    ])

    finishes = [
        ("US26","US26 - Polished Chrome"),
        ("US26D","US26D - Satin Chrome"),
        ("US19","US19 - Flat Black"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US15","US15 - Satin Nickel"),
        ("US3","US3 - Polished Brass"),
        ("US4","US4 - Satin Brass"),
    ]
    options(conn, f, "finish", finishes)

    # ── Emtek Deadbolt ──
    f2 = fid(conn, "Emtek", "Deadbolt",
             "Deadbolt",
             "{type} Deadbolt {finish}",
             "Emtek {type} Deadbolt {finish}")

    slot(conn, f2, 1, "type",   "Type",   1)
    slot(conn, f2, 2, "finish", "Finish", 1)

    options(conn, f2, "type", [
        ("Single","Single Cylinder"),
        ("Double","Double Cylinder"),
        ("Patio", "Patio Deadbolt (one-sided)"),
    ])

    options(conn, f2, "finish", finishes)


# ═════════════════════════════════════════════════════════════════════
# Baldwin – Estate Series (Premium Architectural)
# ═════════════════════════════════════════════════════════════════════

def _seed_baldwin(conn):
    # ── Baldwin Estate Lever Set ──
    f = fid(conn, "Baldwin", "Estate Lever Set",
            "Architectural Lockset",
            "Estate {function} {lever} {rosette} {finish}",
            "Baldwin Estate {function} {lever} {rosette} {finish}")

    slot(conn, f, 1, "function", "Function",        1)
    slot(conn, f, 2, "lever",    "Lever Style",     1)
    slot(conn, f, 3, "rosette",  "Rosette / Plate", 1)
    slot(conn, f, 4, "finish",   "Finish",          1)

    options(conn, f, "function", [
        ("Passage", "Passage"),
        ("Privacy", "Privacy"),
        ("Entry",   "Keyed Entry"),
        ("Dummy",   "Dummy / Inactive"),
    ])

    options(conn, f, "lever", [
        ("5485V", "Federal Lever"),
        ("5162",  "Hollywood Hills Lever"),
        ("5164",  "Soho Lever"),
        ("5485",  "Square Lever"),
        ("5108",  "Capital Lever"),
    ])

    options(conn, f, "rosette", [
        ("BR.CRK","Traditional Rose (BR.CRK)"),
        ("BR.TAR","Taper Rose (BR.TAR)"),
        ("BR.SCR","Square Corner Rose (BR.SCR)"),
        ("SideP", "Sideplate (Full Length)"),
    ])

    options(conn, f, "finish", [
        ("056","056 - Lifetime Satin Nickel"),
        ("003","003 - Lifetime Polished Brass"),
        ("102","102 - Oil Rubbed Bronze"),
        ("150","150 - Satin Nickel"),
        ("190","190 - Satin Black"),
        ("264","264 - Matte Brass/Black"),
    ])

    # ── Baldwin Estate Deadbolt ──
    f2 = fid(conn, "Baldwin", "Estate Deadbolt",
             "Deadbolt",
             "Estate {type} Deadbolt {finish}",
             "Baldwin Estate {type} Deadbolt {finish}")

    slot(conn, f2, 1, "type",   "Type",   1)
    slot(conn, f2, 2, "finish", "Finish", 1)

    options(conn, f2, "type", [
        ("Single","Single Cylinder"),
        ("Double","Double Cylinder"),
        ("Patio", "One-Sided (Patio)"),
    ])

    options(conn, f2, "finish", [
        ("056","056 - Lifetime Satin Nickel"),
        ("003","003 - Lifetime Polished Brass"),
        ("102","102 - Oil Rubbed Bronze"),
        ("150","150 - Satin Nickel"),
        ("190","190 - Satin Black"),
    ])
