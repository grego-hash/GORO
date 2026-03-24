"""Verify Hager exit device patterns and Ives hinge TW/NRP options."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from core.hw_configurator_db import (
    get_valid_options, assemble_part_number, assemble_description
)
import sqlite3

db = pathlib.Path(__file__).resolve().parent.parent / "data" / "hw_configurator.db"
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row

# ── Hager Exit Devices ──
print("=== Hager Exit Device Assembly Patterns ===")
for r in conn.execute(
    "SELECT name, assembly_pattern FROM hw_families "
    "WHERE manufacturer='Hager' AND category='Exit Device' ORDER BY name"
):
    print(f"  {r['name']:35s} pattern: {r['assembly_pattern']}")

# Test a 4601 RIM part number
fid_row = conn.execute(
    "SELECT id FROM hw_families WHERE manufacturer='Hager' AND name='4601 RIM Exit Device'"
).fetchone()
if fid_row:
    fid = fid_row[0]
    sels = {"size": "36EO", "finish": "US26D"}
    pn = assemble_part_number(fid, sels)
    desc = assemble_description(fid, sels)
    print(f"\n  4601 RIM test: {pn}")
    print(f"  Description:   {desc}")

# ── Ives Hinges ──
print("\n=== Ives Hinge TW/NRP Options ===")
for name in ["Architectural Hinges", "Continuous Geared Hinges", "Pin & Barrel Continuous Hinges"]:
    row = conn.execute(
        "SELECT id FROM hw_families WHERE manufacturer='Ives' AND name=?", (name,)
    ).fetchone()
    if row:
        opts = get_valid_options(row[0], "suffix", {})
        print(f"  {name}: suffix options = {[(o['value'], o['display_name']) for o in opts]}")

# Test Ives hinge with TW
arch_row = conn.execute(
    "SELECT id FROM hw_families WHERE manufacturer='Ives' AND name='Architectural Hinges'"
).fetchone()
if arch_row:
    sels = {"model": "5BB1", "size": '4.5" x 4.5"', "finish": "613", "suffix": "TW"}
    pn = assemble_part_number(arch_row[0], sels)
    desc = assemble_description(arch_row[0], sels)
    print(f"\n  Ives arch hinge test: {pn}")
    print(f"  Description:          {desc}")

conn.close()
