"""Verify Trimco compound pricing still works after fix."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from core.hw_configurator_db import get_valid_options
import sqlite3

db = pathlib.Path(__file__).resolve().parent.parent / "data" / "hw_configurator.db"
conn = sqlite3.connect(str(db))
conn.row_factory = sqlite3.Row
fid = conn.execute(
    "SELECT id FROM hw_families WHERE manufacturer='Trimco' AND name='Push Plates'"
).fetchone()[0]
conn.close()

models = get_valid_options(fid, "model", {})
print(f"Trimco Push Plates models: {len(models)}")
for o in models[:5]:
    print(f"  {o['value']}")
print("  ...")

finishes = get_valid_options(fid, "finish", {})
print(f"\nFinishes (no model selected): {len(finishes)}")
for o in finishes:
    print(f"  {o['value']:10s} {o['display_name']}")

# With a model selected, check finish filtering
finishes2 = get_valid_options(fid, "finish", {"model": "1001-4x20"})
print(f"\nFinishes (model=1001-4x20): {len(finishes2)}")
for o in finishes2:
    print(f"  {o['value']:10s} {o['display_name']}")
