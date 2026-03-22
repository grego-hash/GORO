"""Seed Accurate Lock & Hardware mortise locks, Omnia architectural mortise locks."""

from seed_helpers import fid, slot, options, restrict, rule, conflict_all


def seed(conn):
    _seed_accurate(conn)
    _seed_omnia(conn)
    print("  Accurate Lock + Omnia seeded.")


# ═════════════════════════════════════════════════════════════════════
# Accurate Lock & Hardware – Mortise Locks
# ═════════════════════════════════════════════════════════════════════

def _seed_accurate(conn):
    # ── Accurate 9100 Series Mortise Lock ──
    f = fid(conn, "Accurate Lock", "9100 Mortise Lock",
            "Mortise Lock",
            "9100 {function} {lever} {rose} {finish}",
            "Accurate 9100 Mortise {function} {lever} {rose} {finish}")

    slot(conn, f, 1, "function", "Function",       1)
    slot(conn, f, 2, "lever",    "Lever/Knob",     1)
    slot(conn, f, 3, "rose",     "Rose / Trim",    1)
    slot(conn, f, 4, "finish",   "Finish",         1)

    options(conn, f, "function", [
        ("9105",  "9105 - Passage"),
        ("9115",  "9115 - Entry"),
        ("9122",  "9122 - Classroom"),
        ("9125",  "9125 - Storeroom"),
        ("9134",  "9134 - Privacy / Bathroom"),
        ("9145",  "9145 - Dormitory / Exit"),
        ("9178",  "9178 - Hotel/Motel"),
    ])

    options(conn, f, "lever", [
        ("L1",  "L1 - Standard Lever"),
        ("L2",  "L2 - Rounded Lever"),
        ("L3",  "L3 - Contemporary Lever"),
        ("ADA", "ADA - ADA Compliant Lever"),
    ])

    options(conn, f, "rose", [
        ("R1","R1 - Round Rose"),
        ("R2","R2 - Square Rose"),
        ("ESC","Escutcheon Plate"),
    ])

    options(conn, f, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US3",  "US3 - Polished Brass"),
        ("US4",  "US4 - Satin Brass"),
    ])

    # Privacy - no cylinder
    restrict(conn, f, "function", "9134", "lever", ["L1","L2","L3","ADA"],
             "Privacy allows all levers")

    # ── Accurate 2000 Series Pocket Door Lock ──
    f2 = fid(conn, "Accurate Lock", "2000 Pocket Door Lock",
             "Pocket Door Lock",
             "2{function} {finish}",
             "Accurate Lock 2{function} Pocket Door Lock {finish}")

    slot(conn, f2, 1, "function", "Function", 1)
    slot(conn, f2, 2, "finish",   "Finish",   1)

    options(conn, f2, "function", [
        ("002","2002 - Privacy (Pocket)"),
        ("001","2001 - Passage (Pocket)"),
        ("014","2014 - Entry (Pocket, Keyed)"),
    ])

    options(conn, f2, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US3",  "US3 - Polished Brass"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US14", "US14 - Polished Nickel"),
    ])


# ═════════════════════════════════════════════════════════════════════
# Omnia – Architectural Mortise Locks
# ═════════════════════════════════════════════════════════════════════

def _seed_omnia(conn):
    # ── Omnia 7000 Series ──
    f = fid(conn, "Omnia", "7000 Mortise Lock",
            "Mortise Lock",
            "7000 {function} {lever} {finish}",
            "Omnia 7000 Series {function} {lever} {finish}")

    slot(conn, f, 1, "function", "Function",      1)
    slot(conn, f, 2, "lever",    "Lever Style",   1)
    slot(conn, f, 3, "finish",   "Finish",        1)

    options(conn, f, "function", [
        ("Passage",    "Passage"),
        ("Privacy",    "Privacy (Thumbturn)"),
        ("Entry",      "Keyed Entry"),
        ("Classroom",  "Classroom"),
        ("Storeroom",  "Storeroom"),
        ("Dummy",      "Dummy Trim"),
    ])

    options(conn, f, "lever", [
        ("ACE","ACE - Contemporary"),
        ("ARC","ARC - Arched"),
        ("SQR","SQR - Square / Modern"),
        ("TRD","TRD - Traditional"),
    ])

    options(conn, f, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US14", "US14 - Polished Nickel"),
        ("US3",  "US3 - Polished Brass"),
        ("US15A","US15A - Antique Nickel"),
    ])

    # ── Omnia 3900 Pocket Door ──
    f2 = fid(conn, "Omnia", "3900 Pocket Door Lock",
             "Pocket Door Lock",
             "3900 {function} {finish}",
             "Omnia 3900 Pocket Door {function} {finish}")

    slot(conn, f2, 1, "function", "Function", 1)
    slot(conn, f2, 2, "finish",   "Finish",   1)

    options(conn, f2, "function", [
        ("Pass",  "Passage"),
        ("Priv",  "Privacy"),
        ("Entry", "Entry (Keyed)"),
    ])

    options(conn, f2, "finish", [
        ("US26D","US26D - Satin Chrome"),
        ("US32D","US32D - Satin Stainless"),
        ("US10B","US10B - Oil Rubbed Bronze"),
        ("US14", "US14 - Polished Nickel"),
        ("US3",  "US3 - Polished Brass"),
    ])
