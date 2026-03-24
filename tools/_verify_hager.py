"""Verify Hager hinge fixes - part number, description, ETW/NRP."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from core.hw_configurator_db import (
    get_valid_options, assemble_part_number, assemble_description,
    get_list_price
)
import sqlite3

db = pathlib.Path(__file__).resolve().parent.parent / "data" / "hw_configurator.db"
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row

# Get BB1199 family id
row = conn.execute(
    "SELECT id, assembly_pattern, description_template FROM hw_families "
    "WHERE manufacturer='Hager' AND name='BB1199 Full Mortise Hinge'"
).fetchone()
fid = row["id"]
print(f"BB1199 family_id = {fid}")
print(f"  assembly_pattern:    {row['assembly_pattern']}")
print(f"  description_template: {row['description_template']}")
conn.close()

# Test part number assembly
sels = {"size": "4.5x4.5", "finish": "US10B"}
pn = assemble_part_number(fid, sels)
desc = assemble_description(fid, sels)
price = get_list_price(fid, sels)
print(f"\nWith selections: {sels}")
print(f"  Part Number:  {pn}")
print(f"  Description:  {desc}")
print(f"  List Price:   ${price}")

# Test with ETW suffix
sels2 = {"size": "4.5x4.5", "finish": "US10B", "suffix": "ETW"}
pn2 = assemble_part_number(fid, sels2)
desc2 = assemble_description(fid, sels2)
print(f"\nWith selections: {sels2}")
print(f"  Part Number:  {pn2}")
print(f"  Description:  {desc2}")

# Test with NRP suffix
sels3 = {"size": "4.5x4.5", "finish": "US10B", "suffix": "NRP"}
pn3 = assemble_part_number(fid, sels3)
desc3 = assemble_description(fid, sels3)
print(f"\nWith selections: {sels3}")
print(f"  Part Number:  {pn3}")
print(f"  Description:  {desc3}")

# Check ETW/NRP options exist
print("\nSuffix options:")
opts = get_valid_options(fid, "suffix", {})
for o in opts:
    print(f"  {o['value']:5s} {o['display_name']}")

# Verify all families got the prefix
print("\nAll Hager hinge assembly patterns:")
conn2 = sqlite3.connect(str(db))
conn2.row_factory = sqlite3.Row
for r in conn2.execute(
    "SELECT name, assembly_pattern FROM hw_families WHERE manufacturer='Hager' ORDER BY name"
):
    print(f"  {r['name']:40s} pattern: {r['assembly_pattern']}")
conn2.close()
