"""Group boxed items by description for family assignment."""
import csv, re
from collections import defaultdict

with open("data/trimco_boxed_items.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Build model→description map (use best available desc)
models = {}
for r in rows:
    m, d = r["model"], r["description"]
    if m not in models:
        models[m] = d
    elif d and (not models[m] or len(d) > len(models[m])):
        models[m] = d

# Check how many have empty descriptions
empty = sum(1 for d in models.values() if not d)
print(f"Models with empty desc: {empty}/{len(models)}")

# Category assignment by description keywords + model prefix
def categorize(model, desc):
    d = desc.lower()
    m = model
    
    if m.startswith("BP"):
        return "Back Plates"
    if m.startswith("MasterCraft") or m.startswith("STANLEY") or m.startswith("PIERCE") or m.startswith("LAVA"):
        return "Mastercraft Bronze"
    if m.startswith("K"):
        return "Edge Guards"
    
    if "push plate" in d and "pull" not in d:
        return "Push Plates"
    if "pull plate" in d:
        return "Pull Plates"
    if "push" in d and "pull" in d and ("latch" in d or "set" in d):
        return "Push/Pull Latch Sets"
    if "push bar" in d or "push/pull" in d:
        return "Push Bars & Combos"
    if "flush pull" in d or "flush cup" in d or "flush" in d and "pull" in d:
        return "Flush Pulls"
    if "concealed" in d and "pull" in d:
        return "Flush Pulls"
    if "cane bolt" in d:
        return "Cane Bolts"
    if "hospital pull" in d:
        return "Hospital Pulls"
    if "anti-vandal" in d or "tuf-lok" in d:
        return "Anti-Vandal"
    if "ada" in d or "restroom sign" in d:
        return "ADA Signs"
    if "knocker" in d:
        return "Door Knockers"
    if "catch" in d or "ball catch" in d:
        return "Catches & Latches"
    if "roller latch" in d:
        return "Catches & Latches"
    if "latchset" in d or "latchbolt" in d:
        return "Push/Pull Latch Sets"
    if "coordinator" in d:
        return "Coordinators"
    if "flushbolt" in d or "flush bolt" in d:
        return "Flush Bolts"
    if "surface bolt" in d:
        return "Surface Bolts"
    if "strike" in d and "dust" in d:
        return "Dust Proof Strikes"
    if "strike" in d:
        return "Strikes"
    if "wall stop" in d or "wall bumper" in d:
        return "Wall Stops & Bumpers"
    if "floor stop" in d:
        return "Floor Stops & Holders"
    if "door holder" in d or "hold" in d and "open" in d:
        return "Door Holders"
    if "kickdown" in d:
        return "Door Holders"
    if "door stop" in d or "floor stop" in d or "base stop" in d:
        return "Door Stops"
    if "hinge pin" in d:
        return "Door Stops"
    if "roller stop" in d:
        return "Roller Stops"
    if "angle stop" in d:
        return "Roller Stops"
    if "pull" in d and "offset" in d:
        return "Offset Pulls"
    if "grab bar" in d:
        return "Grab Bars & Safety"
    if "pull" in d:
        return "Door Pulls"
    if "astragal" in d or "lock astragal" in d:
        return "Astragals"
    if "edge guard" in d or "finger guard" in d:
        return "Edge Guards"
    if "chain" in d or "swing arm" in d or "security door" in d:
        return "Security Hardware"
    if "anchor" in d or "spacer" in d:
        return "Push/Pull Latch Sets"
    if "emergency" in d or "hold open" in d:
        return "Security Hardware"
    if re.match(r"^509$", m):
        return "ADA Signs"
    if "indicator" in d or "filler" in d:
        return "Miscellaneous"
    
    return "Miscellaneous"

groups = defaultdict(list)
for m, d in sorted(models.items()):
    cat = categorize(m, d)
    groups[cat].append((m, d))

for gname in sorted(groups.keys()):
    items = groups[gname]
    cnt = sum(1 for r in rows if categorize(r["model"], r["description"]) == gname)
    print(f"\n{gname} ({len(items)} models, {cnt} price rows):")
    for m, d in items[:5]:
        print(f"  {m:20s} {d}")
    if len(items) > 5:
        print(f"  ... +{len(items)-5} more")
