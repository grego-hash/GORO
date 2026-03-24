"""Verify Trimco extraction data quality."""
import csv, os
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def show(path, label, key_col="model"):
    print(f"\n{'='*60}")
    print(f"  {label}: {path}")
    print(f"{'='*60}")
    with open(os.path.join(DATA, path), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"  Total rows: {len(rows)}")

    # Unique keys
    if key_col in rows[0]:
        keys = set(r[key_col] for r in rows)
        print(f"  Unique {key_col}s: {len(keys)}")

    # Finish distribution
    finishes = Counter(r["finish"] for r in rows)
    print(f"  Finishes: {dict(finishes)}")

    # Price stats
    prices = [float(r["price"]) for r in rows]
    print(f"  Price range: ${min(prices):.2f} - ${max(prices):,.2f}")

    # Sample rows
    print(f"\n  First 10 rows:")
    for r in rows[:10]:
        print(f"    {r}")
    print(f"\n  Last 5 rows:")
    for r in rows[-5:]:
        print(f"    {r}")

    return rows

boxed = show("trimco_boxed_items.csv", "BOXED PRICES")
ap = show("trimco_ap_items.csv", "AP SERIES", "family")
spec = show("trimco_specialty_items.csv", "SPECIALTY ITEMS")

# Check some known values from page 49 (verified visually)
print(f"\n{'='*60}")
print(f"  SPOT CHECKS")
print(f"{'='*60}")
# Page 49: 1001-4x20 Push Plate 4" x 20" => 605=79.30, 613=79.30, 613E=71.70, 622=71.70
for r in boxed:
    if r["model"] == "1001-4x20":
        print(f"  1001-4x20 / {r['finish']} = ${r['price']}")
        
# Page 26: AP411 12" => 605=530.40
for r in ap:
    if r["family"] == "AP411" and r["size"] == '12"':
        print(f"  AP411 12\" / {r['finish']} = ${r['price']}")
