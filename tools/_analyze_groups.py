"""Analyze boxed item model numbers for family grouping."""
import csv, re
from collections import defaultdict

with open("data/trimco_boxed_items.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Get unique model + description pairs
models = {}
for r in rows:
    m = r["model"]
    d = r["description"]
    if m not in models or (d and not models[m]):
        models[m] = d

# Group by prefix pattern
groups = defaultdict(list)
for m, d in sorted(models.items()):
    # Determine group
    if m.startswith("BP"):
        groups["Back Plates"].append((m, d))
    elif m.startswith("MasterCraft") or m.startswith("STANLEY") or m.startswith("PIERCE") or m.startswith("LAVA"):
        groups["Mastercraft Bronze"].append((m, d))
    elif re.match(r"^(242|248)\b", m):
        groups["Flush Pulls (Small)"].append((m, d))
    elif re.match(r"^24[34]", m):
        groups["Cane Bolts"].append((m, d))
    elif re.match(r"^5[012]\d$", m):
        groups["ADA Signs & Accessories"].append((m, d))
    elif re.match(r"^6\d{2}", m):
        groups["Door Knockers & Catches"].append((m, d))
    elif re.match(r"^1001", m):
        groups["Push Plates"].append((m, d))
    elif re.match(r"^100[3-9]|^101\d", m):
        groups["Pull Plates & Sets"].append((m, d))
    elif re.match(r"^10(6[4-9]|[78]\d)", m):
        groups["Flush Pulls (Recessed)"].append((m, d))
    elif re.match(r"^110[2-9]|^111[0-1]", m):
        groups["Door Pulls (Standard)"].append((m, d))
    elif re.match(r"^111[5-9]|^112\d|^113\d|^114\d|^115\d", m):
        groups["Pulls & Hospital Pulls"].append((m, d))
    elif re.match(r"^119\d", m):
        groups["Offset & Specialty Pulls"].append((m, d))
    elif re.match(r"^120\d|^121[0-3]", m):
        groups["Door Stops & Holders"].append((m, d))
    elif re.match(r"^121[4-9]|^12[23]\d", m):
        groups["Roller Stops & Wall Bumpers"].append((m, d))
    elif re.match(r"^12[3-5]\d", m):
        groups["Floor Stops & Roller Latches"].append((m, d))
    elif re.match(r"^12[6-9]\d|^128\d", m):
        groups["Push/Pull Latches & Bars"].append((m, d))
    elif re.match(r"^3[89]\d", m):
        groups["Coordinators & Strikes"].append((m, d))
    elif re.match(r"^4[0-9]\d{2}", m):
        groups["Push/Pull Combos & Bolts"].append((m, d))
    elif re.match(r"^5\d{3}", m):
        groups["Flush Bolts & Surface Bolts"].append((m, d))
    elif m.startswith("K"):
        groups["Edge Guards"].append((m, d))
    elif "FOCAL" in m.upper() or m.startswith("EML"):
        groups["fOCAL Series"].append((m, d))
    elif "T-PRINT" in m.upper() or "TPRINT" in m.upper():
        groups["T-Print Series"].append((m, d))
    else:
        groups["UNMATCHED"].append((m, d))

for gname in sorted(groups.keys()):
    items = groups[gname]
    print(f"\n{gname} ({len(items)} models):")
    for m, d in items[:8]:
        print(f"  {m:20s} {d}")
    if len(items) > 8:
        print(f"  ... +{len(items)-8} more")
