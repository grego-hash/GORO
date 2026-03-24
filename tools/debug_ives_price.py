"""Debug script to test Ives pricing lookup."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.hw_configurator_db import get_valid_options, get_list_price

fid = 119

# Test 1: What sizes show when model=5BB1?
print("=== Sizes available when model=5BB1 ===")
sizes = get_valid_options(fid, "size", {"model": "5BB1"})
for s in sizes:
    print(f"  {s['value']!r}")
print(f"Total: {len(sizes)}")

# Test 2: What finishes show for 5BB1 + 4.5" x 4.5"?
print('\n=== Finishes for model=5BB1, size=4.5" x 4.5" ===')
finishes = get_valid_options(fid, "finish", {"model": "5BB1", "size": '4.5" x 4.5"'})
for f in finishes[:10]:
    print(f"  {f['value']!r:25s}  {f['display_name']}")
print(f"Total: {len(finishes)}")

# Test 3: Full price lookup
print('\n=== Price lookup: 5BB1 / 4.5" x 4.5" / 613_B ===')
p = get_list_price(fid, {"model": "5BB1", "size": '4.5" x 4.5"', "finish": "613_B"})
print(f"Price: {p}")

# Test 4: What sizes show with NO model selected?
print("\n=== Sizes available with no model selected ===")
sizes_all = get_valid_options(fid, "size", {})
print(f"Total: {len(sizes_all)}")
