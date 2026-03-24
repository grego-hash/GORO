"""
Extract all pricing data from Zero International Price Book #13 (Feb 2026).
Produces: data/zero_pricebook_data.json

Table format types found:
  A  6-col: Part No | Description | Each | Per Foot | Per Meter | Stocked
  B  5-col: Part No | Description | Per Foot | Per Meter | Stocked
  C  5-col: Part No | Description | Size | List price each | Stocked   (door bottoms, multi-row)
  D  5-col: Part No | Description | Length (Ft) | Price each | Stocked  (weatherstrip, multi-row)
  E  4-col: Part No | Description | Each | Stocked
  F  Various parts/accessories formats (skip)
"""
import pdfplumber, json, re, sys, os

sys.stdout.reconfigure(encoding="utf-8")

PDF = r"C:\Users\grego\OneDrive - Stockham Construction, Inc\Desktop\PRICEBOOK\Zero_Price_Book_Feb2026_110962.pdf"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "zero_pricebook_data.json")

SKIP_NAV = {"", "THRESHOLDS", "SDLOHSERHT",
            "AUTOMATIC\nDOOR\nBOTTOMS", "SMOTTOB\nROOD\nCITAMOTUA"}

# ── helpers ──────────────────────────────────────────────────────────

def clean_price(val):
    """Extract numeric price from '$12.50', '$12�50', etc. Returns float or None."""
    if not val or val.strip() in ("-", "", "–"):
        return None
    s = val.strip().replace("$", "").replace(",", "").replace("\xa0", "")
    # Fix OCR mis-read mid-dot (U+2022) or other chars as decimal
    s = re.sub(r"[·•�]", ".", s)
    # Remove trailing non-numeric (e.g. "/pack", "/lb.")
    m = re.match(r"([\d]+\.[\d]+)", s)
    if m:
        return float(m.group(1))
    m2 = re.match(r"([\d]+)", s)
    if m2:
        return float(m2.group(1))
    return None


def clean_text(val):
    if not val:
        return ""
    return val.replace("\n", " ").strip()


# ── Section → page ranges & format mappings ──────────────────────────

# Each entry: (section_name, start_page, end_page, format_type)
# format_type: "6col", "5col_perft", "5col_size", "5col_length", "4col_each"
SECTIONS = [
    # ─ Thresholds ─
    ("Thresholds",                          8,  9,  "6col"),
    ("Half Thresholds",                    10, 11,  "5col_perft"),
    ("Carpet Divider Thresholds",          11, 12,  "5col_perft"),
    ("Offset & Rabbeted Thresholds",       12, 13,  "5col_perft"),
    ("Interlocking Bronze Threshold Systems", 13, 14, "5col_perft"),
    ("Thermal Break Thresholds",           14, 15,  "5col_perft"),
    ("Adjustable Thresholds",              15, 17,  "5col_perft"),
    ("Ramps",                              17, 18,  "5col_perft"),
    ("Specialized Threshold Solutions",    18, 18,  "mixed"),
    # ─ Automatic Door Bottoms ─
    ("Heavy Duty Door Bottoms",            19, 21,  "5col_size"),
    ("Regular Duty Door Bottoms",          22, 23,  "5col_size"),
    ("Light Duty Door Bottoms",            23, 23,  "5col_size"),
    ("Sliding & Pocket Door Bottoms",      23, 23,  "5col_size"),
    ("ADA Compliant Door Bottoms",         24, 25,  "5col_size"),
    # ─ Perimeter Seals ─
    ("Perimeter Seal Accessories",         26, 26,  "5col_perft"),
    ("Door Sweeps",                        26, 29,  "6col"),
    ("Door Shoes",                         29, 31,  "6col"),
    ("Adjustable Sealing Systems",         31, 31,  "5col_perft"),
    ("Head & Jamb Gasketing",              32, 36,  "6col"),
    ("Intumescent Seals",                  36, 36,  "5col_perft"),
    ("Meeting Stiles",                     36, 39,  "5col_perft"),
    ("Astragals",                          39, 39,  "5col_perft"),
    # ─ Misc ─
    ("Door Closer Mounting Brackets",      40, 40,  "4col_each"),
    # ─ Weatherstripping ─
    ("Kerf Frame Weatherstripping",        41, 42,  "5col_length"),
    ("Self-Adhesive Weatherstripping",     43, 48,  "5col_mixed"),
    ("Pile Brush Seals",                   48, 49,  "5col_perft"),
    ("Cushion-Spring Seals",               49, 49,  "5col_perft"),
    ("Jamb Seals for Windows",             49, 49,  "5col_perft"),
    ("PSA Weatherstripping for Glass",     49, 49,  "5col_perft"),
    ("Glass Edge Protection",              49, 50,  "5col_perft"),
    # ─ Solutions & Specialty ─
    ("Sound Control Systems",              51, 51,  "5col_perft"),
    ("Cam Lift Hinges",                    51, 51,  "4col_each"),
    ("Flood Barrier Shields",              51, 51,  "5col_perft"),
    ("Finger Guards",                      51, 52,  "5col_perft"),
    # ─ Parts (replacement rubber only) ─
    ("Replacement Rubber",                 56, 56,  "4col_perft"),
]

# Section header keywords for matching tables to sections
SECTION_KEYWORDS = {
    "Thresholds":                          ["THRESHOLDS"],
    "Half Thresholds":                     ["HALF THRESHOLDS"],
    "Carpet Divider Thresholds":           ["CARPET DIVIDER"],
    "Offset & Rabbeted Thresholds":        ["OFFSET", "RABBETED"],
    "Interlocking Bronze Threshold Systems": ["INTERLOCKING"],
    "Thermal Break Thresholds":            ["THERMAL BREAK"],
    "Adjustable Thresholds":               ["ADJUSTABLE THRESHOLDS"],
    "Ramps":                               ["RAMPS"],
    "Specialized Threshold Solutions":     ["SPECIALIZED THRESHOLD"],
    "Heavy Duty Door Bottoms":             ["HEAVY DUTY"],
    "Regular Duty Door Bottoms":           ["REGULAR DUTY"],
    "Light Duty Door Bottoms":             ["LIGHT DUTY"],
    "Sliding & Pocket Door Bottoms":       ["SLIDING", "POCKET"],
    "ADA Compliant Door Bottoms":          ["ADA COMPLIANT"],
    "Perimeter Seal Accessories":          ["SPECIALIZED PERIMETER"],
    "Door Sweeps":                         ["DOOR SWEEPS"],
    "Door Shoes":                          ["DOOR SHOES"],
    "Adjustable Sealing Systems":          ["ADJUSTABLE SEALING"],
    "Head & Jamb Gasketing":               ["HEAD & JAMB GASKETING", "HEAD &\nJAMB"],
    "Intumescent Seals":                   ["INTUMESCENT"],
    "Meeting Stiles":                      ["MEETING STILES"],
    "Astragals":                           ["ASTRAGAL"],
    "Door Closer Mounting Brackets":       ["CLOSER MOUNTING"],
    "Kerf Frame Weatherstripping":         ["KERF FRAME"],
    "Self-Adhesive Weatherstripping":      ["SELF-ADHESIVE"],
    "Pile Brush Seals":                    ["PILE", "BRUSH"],
    "Cushion-Spring Seals":                ["CUSHION-SPRING", "CUSHION"],
    "Jamb Seals for Windows":              ["JAMB SEALS", "DOUBLE-HUNG"],
    "PSA Weatherstripping for Glass":      ["PSA WEATHERSTRIPPING", "GLASS DOORS"],
    "Glass Edge Protection":               ["GLASS EDGE", "POLY PILE"],
    "Sound Control Systems":               ["SOUND CONTROL"],
    "Cam Lift Hinges":                     ["CAM LIFT"],
    "Flood Barrier Shields":               ["FLOOD BARRIER"],
    "Finger Guards":                       ["FINGER GUARD", "BIOWALL"],
    "Replacement Rubber":                  ["REPLACEMENT RUBBER"],
}


def table_matches_section(table_header, section_name):
    """Check if a table header matches a section by keywords."""
    if not table_header:
        return False
    h = table_header.upper()
    keywords = SECTION_KEYWORDS.get(section_name, [])
    return any(kw.upper() in h for kw in keywords)


# ── Parsers ──────────────────────────────────────────────────────────

def parse_6col(tables, section_name):
    """6-col: Part No | Description | Each | Per Foot | Per Meter | Stocked
       Price in 'Each' or 'Per Foot' (whichever has a value)."""
    items = []
    for t in tables:
        if not t or len(t) < 3:
            continue
        if len(t[0]) != 6:
            continue
        if not table_matches_section(t[0][0], section_name):
            continue
        for row in t[2:]:  # skip header + sub-header rows
            part_no = clean_text(row[0])
            desc = clean_text(row[1])
            if not part_no:
                continue
            price_each = clean_price(row[2])
            price_perft = clean_price(row[3])
            price = price_each or price_perft
            unit = "each" if price_each else "per_foot"
            if price is None:
                continue
            items.append({
                "category": section_name,
                "part_no": part_no,
                "description": desc,
                "price": price,
                "unit": unit,
            })
    return items


def parse_5col_perft(tables, section_name):
    """5-col: Part No | Description | Per Foot | Per Meter | Stocked"""
    items = []
    for t in tables:
        if not t or len(t) < 3:
            continue
        if len(t[0]) != 5:
            continue
        if not table_matches_section(t[0][0], section_name):
            continue
        for row in t[2:]:
            part_no = clean_text(row[0])
            desc = clean_text(row[1])
            if not part_no:
                continue
            price = clean_price(row[2])
            if price is None:
                continue
            items.append({
                "category": section_name,
                "part_no": part_no,
                "description": desc,
                "price": price,
                "unit": "per_foot",
            })
    return items


def parse_5col_size(tables, section_name):
    """5-col door bottoms: Part No | Description | Size | Price each | Stocked
       Multi-row: continuation rows have None in cols 0-1."""
    items = []
    for t in tables:
        if not t or len(t) < 3:
            continue
        if len(t[0]) != 5:
            continue
        if not table_matches_section(t[0][0], section_name):
            continue
        current_part = None
        current_desc = None
        for row in t[2:]:
            pn = clean_text(row[0])
            ds = clean_text(row[1])
            if pn:
                current_part = pn
                current_desc = ds
            size = clean_text(row[2])
            price = clean_price(row[3])
            if not current_part or not size or price is None:
                continue
            items.append({
                "category": section_name,
                "part_no": current_part,
                "description": current_desc,
                "size": size,
                "price": price,
                "unit": "each",
            })
    return items


def parse_5col_length(tables, section_name):
    """5-col weatherstripping: Part No | Description | Length (Ft) | Price each | Stocked
       Multi-row: continuation rows have None in cols 0-1."""
    items = []
    for t in tables:
        if not t or len(t) < 3:
            continue
        if len(t[0]) != 5:
            continue
        if not table_matches_section(t[0][0], section_name):
            continue
        # Find the sub-header row index (row containing "Part number")
        data_start = 2
        if len(t) > 2:
            r2 = clean_text(t[1][0]).lower() if t[1] and t[1][0] else ""
            if "part" not in r2:
                # Might have an extra sub-header (e.g., "Solid neoprene & silicone seals")
                if len(t) > 3:
                    r3 = clean_text(t[2][0]).lower() if t[2] and t[2][0] else ""
                    if "part" in r3:
                        data_start = 3
        current_part = None
        current_desc = None
        for row in t[data_start:]:
            pn = clean_text(row[0])
            ds = clean_text(row[1])
            if pn:
                current_part = pn
                current_desc = ds
            length = clean_text(row[2])
            price = clean_price(row[3])
            if not current_part or not length or price is None:
                continue
            items.append({
                "category": section_name,
                "part_no": current_part,
                "description": current_desc,
                "length": length,
                "price": price,
                "unit": "each",
            })
    return items


def parse_5col_mixed(tables, section_name):
    """Self-adhesive weatherstripping: sometimes length-based, sometimes per-foot.
       Check column headers to decide."""
    items = []
    for t in tables:
        if not t or len(t) < 3:
            continue
        if len(t[0]) != 5:
            continue
        if not table_matches_section(t[0][0], section_name):
            continue
        # Detect format from sub-header row
        # Find the row with "Part number" in it
        header_row_idx = 1
        for i in range(1, min(4, len(t))):
            cell = clean_text(t[i][0]).lower() if t[i] and t[i][0] else ""
            if "part" in cell:
                header_row_idx = i
                break
        header_row = t[header_row_idx]
        col2_header = clean_text(header_row[2]).lower() if header_row[2] else ""

        if "length" in col2_header or "ft" in col2_header:
            # Length-based format
            current_part = None
            current_desc = None
            for row in t[header_row_idx + 1:]:
                pn = clean_text(row[0])
                ds = clean_text(row[1])
                if pn:
                    current_part = pn
                    current_desc = ds
                length = clean_text(row[2])
                price = clean_price(row[3])
                if not current_part or not length or price is None:
                    continue
                items.append({
                    "category": section_name,
                    "part_no": current_part,
                    "description": current_desc,
                    "length": length,
                    "price": price,
                    "unit": "each",
                })
        elif "per foot" in col2_header or "foot" in col2_header:
            # Per-foot format
            for row in t[header_row_idx + 1:]:
                pn = clean_text(row[0])
                ds = clean_text(row[1])
                if not pn:
                    continue
                price = clean_price(row[2])
                if price is None:
                    continue
                items.append({
                    "category": section_name,
                    "part_no": pn,
                    "description": ds,
                    "price": price,
                    "unit": "per_foot",
                })
        else:
            # Default: try length-based
            current_part = None
            current_desc = None
            for row in t[header_row_idx + 1:]:
                pn = clean_text(row[0])
                ds = clean_text(row[1])
                if pn:
                    current_part = pn
                    current_desc = ds
                val2 = clean_text(row[2])
                price = clean_price(row[3])
                if not current_part or not val2 or price is None:
                    continue
                items.append({
                    "category": section_name,
                    "part_no": current_part,
                    "description": current_desc,
                    "length": val2,
                    "price": price,
                    "unit": "each",
                })
    return items


def parse_4col_each(tables, section_name):
    """4-col: Part No | Description | Each/Price | Stocked"""
    items = []
    for t in tables:
        if not t or len(t) < 3:
            continue
        if len(t[0]) != 4:
            continue
        if not table_matches_section(t[0][0], section_name):
            continue
        # Find data start
        data_start = 2
        for i in range(1, min(4, len(t))):
            cell = clean_text(t[i][0]).lower() if t[i] and t[i][0] else ""
            if "part" in cell or "art" in cell:
                data_start = i + 1
                break
        for row in t[data_start:]:
            part_no = clean_text(row[0])
            desc = clean_text(row[1])
            if not part_no:
                continue
            price = clean_price(row[2])
            if price is None:
                continue
            items.append({
                "category": section_name,
                "part_no": part_no,
                "description": desc,
                "price": price,
                "unit": "each",
            })
    return items


def parse_4col_perft(tables, section_name):
    """4-col per-foot: Part No | Description | Per Foot | Per Meter"""
    items = []
    for t in tables:
        if not t or len(t) < 3:
            continue
        if len(t[0]) != 4:
            continue
        if not table_matches_section(t[0][0], section_name):
            continue
        for row in t[2:]:
            part_no = clean_text(row[0])
            desc = clean_text(row[1])
            if not part_no:
                continue
            price = clean_price(row[2])
            if price is None:
                continue
            items.append({
                "category": section_name,
                "part_no": part_no,
                "description": desc,
                "price": price,
                "unit": "per_foot",
            })
    return items


def parse_mixed_threshold(tables, section_name):
    """Page 18 specialized thresholds — has both 4-col and 6-col tables."""
    items = []
    for t in tables:
        if not t or len(t) < 3:
            continue
        if not table_matches_section(t[0][0], section_name):
            continue
        ncols = len(t[0])
        if ncols == 4:
            # /inch x /ft format — complex pricing, skip or parse simply
            for row in t[2:]:
                pn = clean_text(row[0])
                ds = clean_text(row[1])
                price_str = clean_text(row[2])
                if not pn:
                    continue
                price = clean_price(row[2])
                if price is None:
                    continue
                items.append({
                    "category": section_name,
                    "part_no": pn,
                    "description": ds,
                    "price": price,
                    "unit": "special",
                })
        elif ncols == 6:
            for row in t[2:]:
                pn = clean_text(row[0])
                ds = clean_text(row[1])
                if not pn:
                    continue
                price_ft = clean_price(row[3])
                if price_ft is None:
                    continue
                items.append({
                    "category": section_name,
                    "part_no": pn,
                    "description": ds,
                    "price": price_ft,
                    "unit": "per_foot",
                })
    return items


# ── Main extraction ──────────────────────────────────────────────────

FORMAT_PARSERS = {
    "6col":        parse_6col,
    "5col_perft":  parse_5col_perft,
    "5col_size":   parse_5col_size,
    "5col_length": parse_5col_length,
    "5col_mixed":  parse_5col_mixed,
    "4col_each":   parse_4col_each,
    "4col_perft":  parse_4col_perft,
    "mixed":       parse_mixed_threshold,
}


def extract_all():
    pdf = pdfplumber.open(PDF)
    all_items = []

    for section_name, start_pg, end_pg, fmt in SECTIONS:
        parser = FORMAT_PARSERS[fmt]
        section_items = []

        for pg_num in range(start_pg, end_pg + 1):
            page = pdf.pages[pg_num - 1]
            tables = page.extract_tables()
            items = parser(tables, section_name)
            section_items.extend(items)

        count = len(section_items)
        if count > 0:
            print(f"  {section_name}: {count} items")
        else:
            print(f"  {section_name}: 0 items  *** CHECK ***")
        all_items.extend(section_items)

    pdf.close()
    return all_items


if __name__ == "__main__":
    print("Extracting Zero International Pricebook #13 ...\n")
    items = extract_all()

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    # Stats
    cats = {}
    for it in items:
        cats[it["category"]] = cats.get(it["category"], 0) + 1

    print(f"\nTotal items: {len(items)}")
    print(f"Categories: {len(cats)}")
    print(f"Output: {OUT}")
