"""Quick test: verify get_valid_options returns all L Series functions."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from core.hw_configurator_db import get_valid_options, get_family

# Get the L Series family id
import sqlite3
db = pathlib.Path(__file__).resolve().parent.parent / "data" / "hw_configurator.db"
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
fid = conn.execute(
    "SELECT id FROM hw_families WHERE manufacturer='Schlage' AND name='L Series Mortise Lock'"
).fetchone()[0]
print(f"L Series family_id = {fid}")
conn.close()

# Get valid function options with no prior selections
valid = get_valid_options(fid, "function", {})
print(f"\nValid function options (no selections): {len(valid)}")
for o in valid:
    print(f"  {o['value']:15s} {o['display_name']}")

# Verify some expected functions are present
expected = ["L0170", "L9010", "L9025", "L9040", "L9050", "L9060", "L9070", "L9080", "LV9040"]
for fn in expected:
    found = any(o["value"] == fn for o in valid)
    print(f"  {fn}: {'OK' if found else 'MISSING!'}")
