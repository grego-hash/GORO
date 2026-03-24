"""
Extract all pricing data from NGP (National Guard Products) Price List (Feb 1, 2026).
Produces: data/ngp_pricebook_data.json

84-page catalog with 5 major sections:
  SEALS (pp 4-25)            — Dense model/price text, floor closer tables, replacement gasketing
  LITE KITS & LOUVERS (pp 26-57) — 2D grid tables (height × width → price)
  GLASS (pp 58-67)           — 2D grid tables
  CONTINUOUS HINGES (pp 68-73)   — Model × length tables
  SLIDING DOOR HARDWARE (pp 74-81) — Simple model → price lists
"""
import pdfplumber, json, re, sys, os

sys.stdout.reconfigure(encoding="utf-8")

PDF = r"C:\Users\grego\OneDrive - Stockham Construction, Inc\Desktop\PRICEBOOK\NGP.pdf"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "ngp_pricebook_data.json")

# ── helpers ──────────────────────────────────────────────────────────

UNIT_MAP = {"FT": "per_foot", "EA": "each", "PK": "per_pack",
            "ST": "per_set",  "RL": "per_roll", "PC": "per_piece",
            "BX": "per_box",  "SET": "per_set"}

# Regex to find:  PRICE / UNIT   e.g.  31.75 / FT.  or  15.05 /Set
PRICE_UNIT_RE = re.compile(
    r'(\d{1,7}[\.,]\d{2})\s*/\s*(FT|EA|PK|ST|RL|PC|BX|Set)\.?',
    re.IGNORECASE
)

# Regex for prices without slash: used in some table formats  e.g.  270.55
BARE_PRICE_RE = re.compile(r'(\d{1,7}\.\d{2})')

# Lines to skip completely
SKIP_LINE_RE = re.compile(
    r'FEBRUARY\s+1|PRICE\s+LIST|Phone:\s*800|Fax:\s*800|orders@ngp\.com|ngp\.com'
    r'|^\d+\s+Phone|^Phone|^\*\s|^ΓÇ|^┬|^THGIEH|^W I D T H',
    re.IGNORECASE
)

REVERSED_TEXT = {
    "sdlohserhT", "etalP", "revoC", "stnenopmoC", "ylbmessA", "dlohserhT",
    "srevuoL", "leetS", "LDFA", "revuoL", "rooD", "gnidilS", "erawdraH",
    "segniH", "deraeG", "suounitnoC", "stresnI", "gniteksaG", "tnemecalpeR",
    "sresolC", "roolF", "stiK", "etiL", "ellirG", "ytiruceS", "noilluM",
    "sraB", "eslaF", "htiw", "BT", "ssalG", "derepmeT", "TN", "ETILERIF",
    "DSS", "tiK", "detaR", "enacirruH", "elfiorP", "woL", "MROTS",
    "edalB", "elbatsujdA", "kniL", "elbisuF", "detar", "eriF", "PLSL",
    "etalP", "ecaF", "FREP", "sselniatS",
}


def clean_model(text):
    """Clean model name text."""
    s = text.strip()
    # Remove trailing 'x' used as per-foot indicator
    s = re.sub(r'\s+x\s*$', '', s)
    # Remove leading/trailing junk
    s = re.sub(r'^[\s,;]+|[\s,;]+$', '', s)
    # Collapse whitespace
    s = re.sub(r'\s+', ' ', s)
    return s


def is_junk_model(model):
    """Check if a model string is garbage/non-product."""
    if not model or len(model) < 2:
        return True
    # Must start with a letter or digit
    if not model[0].isalnum():
        return True
    # Skip reversed text fragments
    if model in REVERSED_TEXT:
        return True
    # Skip if it's just text descriptions
    low = model.lower()
    skip_words = ['phone', 'fax', 'orders', 'ngp.com', 'february', 'price list',
                  'finish', 'available', 'optional', 'minimum', 'maximum',
                  'note:', 'example:', 'see page', 'contact', 'email',
                  'when ordering', 'the following', 'required', 'threshold type',
                  'material and', 'door thickness', 'door opening', 'handing',
                  'name of floor', 'abrasive', 'polished', 'item numbers',
                  'freight', 'prepaid', 'multiplier', 'multiply width']
    for w in skip_words:
        if w in low:
            return True
    return False


# ── PARSER 1: Dense model/price text ────────────────────────────────

def parse_dense_pages(pdf, pages, category):
    """Extract MODEL PRICE / UNIT entries from dense text pages."""
    items = []
    for pg_num in pages:
        page = pdf.pages[pg_num]
        text = page.extract_text() or ""
        for line in text.split("\n"):
            line = line.strip()
            if not line or SKIP_LINE_RE.search(line):
                continue
            matches = list(PRICE_UNIT_RE.finditer(line))
            if not matches:
                continue
            prev_end = 0
            for m in matches:
                model_text = line[prev_end:m.start()].strip()
                price_str = m.group(1).replace(",", ".")
                unit = UNIT_MAP.get(m.group(2).upper(), "each")
                model_text = clean_model(model_text)
                prev_end = m.end()
                if is_junk_model(model_text):
                    continue
                try:
                    price_val = float(price_str)
                except ValueError:
                    continue
                if price_val <= 0:
                    continue
                items.append({
                    "category": category,
                    "part_no": model_text,
                    "price": price_val,
                    "unit": unit,
                    "page": pg_num,
                })
    return items


# ── PARSER 2: 2D grid tables (height × width → price) ──────────────

def parse_grid_page(pdf, pg_num, product_name, category, table_index=None):
    """Extract height × width → price from a 2D grid table."""
    items = []
    tables = pdf.pages[pg_num].extract_tables()
    if not tables:
        return items

    if table_index is not None:
        tables = [tables[table_index]] if table_index < len(tables) else []

    for table in tables:
        if not table or len(table) < 2:
            continue
        # Find the width header row: first row where most cells are numbers
        width_row = None
        data_start = 0
        for ri, row in enumerate(table):
            # Flatten all cell text, split on whitespace, count numbers
            all_parts = []
            for c in row:
                if c and c.strip():
                    all_parts.extend(c.strip().split())
            nums = sum(1 for p in all_parts if re.match(r'^\d+$', p))
            if nums >= 3:  # at least 3 numeric width values
                width_row = row
                data_start = ri + 1
                break

        if width_row is None:
            continue

        # Extract widths - flatten across cells, handle "12 18" merged in one cell
        widths = []
        for c in width_row[1:]:
            if c and c.strip():
                for p in c.strip().split():
                    if re.match(r'^\d+$', p):
                        widths.append(p)

        if not widths:
            continue

        # Process data rows — handle merged cells (multiple heights per cell, \n separated)
        for row in table[data_start:]:
            if not row or not row[0]:
                continue
            heights_cell = row[0].strip()
            heights = [h.strip() for h in heights_cell.split("\n") if h.strip()]

            # Build price matrix: for each height index, collect all width prices
            # by splitting each column cell on \n (rows) and then on spaces (cols)
            price_matrix = [[] for _ in heights]
            for ci in range(1, len(row)):
                cell = row[ci] if row[ci] else ""
                cell_rows = cell.split("\n")
                for hi in range(len(heights)):
                    if hi < len(cell_rows):
                        vals = cell_rows[hi].strip().split()
                        price_matrix[hi].extend(vals)
                    # else: no values for this height in this cell

            # Each height row's price list should align with widths
            for hi, height in enumerate(heights):
                if not re.match(r'^\d+', height):
                    continue
                for wi, w in enumerate(widths):
                    if wi < len(price_matrix[hi]):
                        price_str = price_matrix[hi][wi]
                    else:
                        continue
                    if not price_str or not re.match(r'^\d+', price_str):
                        continue
                    try:
                        price_val = float(price_str.replace(",", ""))
                    except ValueError:
                        continue
                    if price_val <= 0:
                        continue
                    items.append({
                        "category": category,
                        "part_no": product_name,
                        "width": w,
                        "height": height,
                        "price": price_val,
                        "unit": "each",
                        "page": pg_num,
                    })
    return items


# ── PARSER 3: Continuous hinge model × length table ─────────────────

def parse_hinge_pages(pdf, pages, category):
    """Parse continuous hinge pricing: model × length columns."""
    items = []
    lengths = ["83", "85", "95", "119"]

    for pg_num in pages:
        text = pdf.pages[pg_num].extract_text() or ""
        for line in text.split("\n"):
            line = line.strip()
            if not line or SKIP_LINE_RE.search(line):
                continue
            # Match lines starting with model (HD or SS prefix) followed by prices
            m = re.match(r'^((?:HD|SS)\S+)\s+(.+)', line)
            if not m:
                continue
            model = m.group(1).strip()
            rest = m.group(2).strip()
            # Extract all numbers from the rest
            prices = re.findall(r'(\d+(?:\.\d+)?)', rest)
            if not prices:
                continue
            # For geared hinges (page 70): cols are 83", 83"bulk, 85", 95", 119"
            # For SS hinges (page 72): cols are 83", 85", 95", 119"
            if pg_num == 70:
                # Geared: first price = 83" standard, skip bulk, then 85", 95", 119"
                price_map = {}
                if len(prices) >= 1:
                    price_map["83"] = float(prices[0])
                # Skip bulk price (index 1, sometimes has "EA." text)
                if len(prices) >= 3:
                    price_map["85"] = float(prices[-3])
                if len(prices) >= 2:
                    price_map["95"] = float(prices[-2])
                if len(prices) >= 1:
                    price_map["119"] = float(prices[-1])
                # Better approach: map based on count
                if len(prices) == 4:
                    # Simple: 83, 85, 95, 119  (no bulk)
                    price_map = {"83": float(prices[0]), "85": float(prices[1]),
                                 "95": float(prices[2]), "119": float(prices[3])}
                elif len(prices) >= 5:
                    # Has bulk: 83std, 83bulk, [text], 85, 95, 119
                    price_map = {"83": float(prices[0]), "85": float(prices[-3]),
                                 "95": float(prices[-2]), "119": float(prices[-1])}
                elif len(prices) == 3:
                    # Missing 83 (probably continuation): 85, 95, 119
                    price_map = {"85": float(prices[0]), "95": float(prices[1]),
                                 "119": float(prices[2])}
                for length, pv in price_map.items():
                    if pv > 0:
                        items.append({
                            "category": category,
                            "part_no": model,
                            "length": length,
                            "price": pv,
                            "unit": "each",
                            "page": pg_num,
                        })
            elif pg_num == 72:
                # SS hinges: 83", 85", 95", 119"
                for i, length in enumerate(lengths):
                    if i < len(prices):
                        try:
                            pv = float(prices[i])
                        except ValueError:
                            continue
                        if pv > 0:
                            items.append({
                                "category": category,
                                "part_no": model,
                                "length": length,
                                "price": pv,
                                "unit": "each",
                                "page": pg_num,
                            })
    return items


# ── PARSER 4: Sliding door hardware ─────────────────────────────────

def parse_sliding_door_pages(pdf, pages, category):
    """Parse sliding door hardware: MODEL ...dots... PRICE /UNIT."""
    items = []
    for pg_num in pages:
        text = pdf.pages[pg_num].extract_text() or ""
        for line in text.split("\n"):
            line = line.strip()
            if not line or SKIP_LINE_RE.search(line):
                continue
            # Clean dot fill: replace runs of 2+ dots (with optional spaces) with double space
            cleaned = re.sub(r'(?:\s*\.){2,}\s*', '  ', line)
            # Find PRICE / UNIT patterns in the cleaned line
            matches = list(PRICE_UNIT_RE.finditer(cleaned))
            if not matches:
                continue
            prev_end = 0
            for m in matches:
                model_text = cleaned[prev_end:m.start()].strip()
                price_str = m.group(1).replace(",", ".")
                unit = UNIT_MAP.get(m.group(2).upper(), "each")
                prev_end = m.end()
                model_text = clean_model(model_text)
                if is_junk_model(model_text):
                    continue
                try:
                    price_val = float(price_str)
                except ValueError:
                    continue
                if price_val <= 0:
                    continue
                items.append({
                    "category": category,
                    "part_no": model_text,
                    "price": price_val,
                    "unit": unit,
                    "page": pg_num,
                })
    return items


# ── PARSER 5: Floor closer thresholds ───────────────────────────────

def parse_floor_closer_pages(pdf, pages, category):
    """Parse thresholds for floor closers: Type Threshold Materials Sizes Prices."""
    items = []
    sizes = ["36", "48", "72", "96"]

    for pg_num in pages:
        text = pdf.pages[pg_num].extract_text() or ""
        for line in text.split("\n"):
            line = line.strip()
            if not line or SKIP_LINE_RE.search(line):
                continue
            # Match: Type# Model Material Finish? price price price price
            # Example: 1 427E 1/2" x 7" Alum. 270.55 299.45 538.70 597.75
            prices = BARE_PRICE_RE.findall(line)
            if len(prices) < 2:
                continue
            # Check if line starts with a type number (1-9)
            m = re.match(r'^(\d)\s+(\S+)\s+(.+)', line)
            if not m:
                continue
            type_num = m.group(1)
            model = m.group(2)
            rest = m.group(3)
            # Extract all prices from the rest
            all_prices = [float(p) for p in BARE_PRICE_RE.findall(rest)]
            if len(all_prices) < 2:
                continue
            # Map prices to sizes
            for i, sz in enumerate(sizes):
                if i < len(all_prices):
                    pv = all_prices[i]
                    if pv > 0:
                        items.append({
                            "category": category,
                            "part_no": f"Type {type_num} - {model}",
                            "size": f'{sz}"',
                            "price": pv,
                            "unit": "each",
                            "page": pg_num,
                        })
    return items


# ── PARSER 6: Door edges & astragals ────────────────────────────────

def parse_door_edges(pdf, pg_num, category):
    """Parse door edges & astragals height × type pricing table."""
    items = []
    text = pdf.pages[pg_num].extract_text() or ""
    lines = text.split("\n")

    # Find the pricing sections
    in_section = None
    for line in lines:
        line = line.strip()
        # Detect section headers
        if "Door Edges" in line and "Astragals" in line and "Stainless" not in line:
            in_section = "Steel"
            continue
        if "Stainless Steel" in line and "#4" in line:
            in_section = "Stainless"
            continue

        if not in_section:
            continue

        # Match: height  price  price  price  price
        # Example: 6'8" 127 178 145 209
        m = re.match(r"(\d+'?\d*\"?)\s+([\d\s-]+)$", line)
        if not m:
            continue
        height = m.group(1)
        vals = m.group(2).split()
        # Columns: Door Edge Ea, Door Edge Set, Astragal Ea, Astragal Set
        col_names = [
            (f"Door Edge {'SS ' if in_section == 'Stainless' else ''}Ea", 0),
            (f"Door Edge {'SS ' if in_section == 'Stainless' else ''}Set", 1),
            (f"Astragal {'SS ' if in_section == 'Stainless' else ''}Ea", 2),
            (f"Astragal {'SS ' if in_section == 'Stainless' else ''}Set", 3),
        ]
        for label, idx in col_names:
            if idx < len(vals) and vals[idx] != "-":
                try:
                    pv = float(vals[idx])
                except ValueError:
                    continue
                if pv > 0:
                    items.append({
                        "category": category,
                        "part_no": label,
                        "size": height,
                        "price": pv,
                        "unit": "each",
                        "page": pg_num,
                    })
    return items


# ── PARSER 7: Replacement gasketing inserts ─────────────────────────

def parse_replacement_gasketing(pdf, pages, category):
    """Parse replacement gasketing: groups of model numbers sharing a price."""
    items = []
    for pg_num in pages:
        text = pdf.pages[pg_num].extract_text() or ""
        for line in text.split("\n"):
            line = line.strip()
            if not line or SKIP_LINE_RE.search(line):
                continue
            # Find lines with price at end: "model1, model2, model3 PRICE"
            # Or "model1 PRICE / FT." format
            matches = list(PRICE_UNIT_RE.finditer(line))
            if matches:
                prev_end = 0
                for m in matches:
                    model_text = clean_model(line[prev_end:m.start()])
                    price_str = m.group(1).replace(",", ".")
                    unit = UNIT_MAP.get(m.group(2).upper(), "each")
                    prev_end = m.end()
                    if is_junk_model(model_text):
                        continue
                    try:
                        price_val = float(price_str)
                    except ValueError:
                        continue
                    if price_val > 0:
                        items.append({
                            "category": category,
                            "part_no": model_text,
                            "price": price_val,
                            "unit": unit,
                            "page": pg_num,
                        })
    return items


# ── PARSER 8: Hinge electric options & replacement parts ────────────

def parse_hinge_options(pdf, pg_num, category):
    """Parse hinge electric options and replacement parts from page 71."""
    items = []
    text = pdf.pages[pg_num].extract_text() or ""
    for line in text.split("\n"):
        line = line.strip()
        if not line or SKIP_LINE_RE.search(line):
            continue
        matches = list(PRICE_UNIT_RE.finditer(line))
        if matches:
            prev_end = 0
            for m in matches:
                model_text = clean_model(line[prev_end:m.start()])
                price_str = m.group(1).replace(",", ".")
                unit = UNIT_MAP.get(m.group(2).upper(), "each")
                prev_end = m.end()
                if is_junk_model(model_text):
                    continue
                # Only include hinge-related models
                if not any(x in model_text for x in ["HD", "SS", "ETW", "EPT"]):
                    continue
                try:
                    price_val = float(price_str)
                except ValueError:
                    continue
                if price_val > 0:
                    items.append({
                        "category": category,
                        "part_no": model_text,
                        "price": price_val,
                        "unit": unit,
                        "page": pg_num,
                    })
    return items


# ── PARSER 9: Security lite kits (individual products, page 44) ─────

def parse_security_lite_kits(pdf, pg_num, category):
    """Parse L-VGLF security lite kits and round lite kits."""
    items = []
    text = pdf.pages[pg_num].extract_text() or ""
    # Pattern: L-VGLF-XX size $PRICE  or  model size PRICE
    price_re = re.compile(r'(L-(?:VGLF|FRA100|LO)-?\S*)\s+(\S+)\s+\$?(\d+)')
    for line in text.split("\n"):
        line = line.strip()
        m = price_re.search(line)
        if m:
            model = m.group(1)
            size = m.group(2)
            price_val = float(m.group(3))
            full_model = f"{model} {size}"
            if price_val > 0:
                items.append({
                    "category": category,
                    "part_no": full_model,
                    "price": price_val,
                    "unit": "each",
                    "page": pg_num,
                })
    return items


# ── Section definitions ──────────────────────────────────────────────

# Dense text sections: (category_name, [page_numbers])
DENSE_SECTIONS = [
    ("Threshold Fasteners",           [6]),
    ("Threshold Assembly Components", [9]),
    ("Ramps",                         [10]),
    ("Seals & Gasketing",            [11, 12, 13]),
    ("Thresholds",                    [15, 16, 17, 18, 19, 20]),
]

# Grid table sections: (category_name, product_model, page_number)
GRID_SECTIONS = [
    # Lite Kits
    ("Lite Kits - Standard",          "L-FRA100/L-GLF100",        29),
    ("Lite Kits - Pyran F",           "L-FRA100/L-GLF100 Pyran",  30),
    ("Lite Kits - 20T Fire-Rated",    "L-FRA100/L-GLF100 20T",    32),
    ("Lite Kits - 20T Fire-Rated",    "L-FRA100 LO-PRO 20T",      33),
    ("Lite Kits - Variable Thickness", "L-FRA100-SP/L-GLF100-SP", 36),
    ("Lite Kits - Security Grille",   "L-SG100/L-SG100-TB",       37),
    ("Lite Kits - Stainless Steel",   "L-CVFM-SS/L-CVFM-316SS",   38),
    ("Lite Kits - Stainless SP",      "L-CVFM-SS-SP/316SS-SP",    39),
    ("Lite Kits - SG-10 Security",    "SG-10",                     40),
    ("Lite Kits - SSD Sliding Door",  "SSD/SG-10-SSD/LO-PRO-SSD", 41),
    ("Lite Kits - BR-7 Security",     "BR-7",                      42),
    ("Lite Kits - Hurricane",         "STORM-HR/LO-PRO",           43),
    # Louvers
    ("Louvers - Steel AFDL",          "AFDL/L-700",                45),
    ("Louvers - FDLS Inverted",       "FDLS",                      46),
    ("Louvers - SS316",               "L-700-RX-316SS",            47, 0),
    ("Louvers - SS316",               "FDLS-316SS",                 47, 1),
    ("Louvers - Aluminum",            "L-A700-B/BF/C",             48),
    ("Louvers - Adjustable Blade",    "L-1800/L-1900 FLDL",        49),
    ("Louvers - PLSL Security",       "PLSL/PLSL-316SS",           50),
    ("Louvers - L-VRSG-2 Grille",     "L-VRSG-2/L-VRSG-2-TB",     51),
    ("Louvers - L-VRSG-3 Grille",     "L-VRSG-3/L-VRSG-3-TB",     52),
    ("Louvers - FLDL-SG Fire-Rated",  "FLDL-SG1/SG2",             53),
    ("Security Grille Face Plates",   "DSFP/DSFP-PERF",           54),
    ("Security Grille Face Plates",   "DSFP-NB-PERF",             55),
    # Glass
    ("Glass - Pyran F",               "Pyran F",                   60),
    ("Glass - FireLite NT",           "FireLite NT",               61),
    ("Glass - Protect3 Wired",        "Protect3",                  62),
    ("Glass - 20T Tempered",          "20T Tempered",              63),
    ("Glass - Tempered 1/4 in",       "Tempered 1/4\"",            65),
]


# ── Main extraction ─────────────────────────────────────────────────

def extract_all():
    pdf = pdfplumber.open(PDF)
    all_items = []

    # 1. Dense model/price sections
    print("  --- Dense Model/Price Sections ---")
    for cat, pages in DENSE_SECTIONS:
        items = parse_dense_pages(pdf, pages, cat)
        print(f"  {cat}: {len(items)} items (pages {pages})")
        all_items.extend(items)

    # 2. Floor closer thresholds
    print("\n  --- Floor Closer Thresholds ---")
    items = parse_floor_closer_pages(pdf, [21, 22, 23], "Thresholds for Floor Closers")
    print(f"  Thresholds for Floor Closers: {len(items)} items")
    all_items.extend(items)

    # 3. Replacement gasketing inserts
    print("\n  --- Replacement Parts ---")
    items = parse_replacement_gasketing(pdf, [24, 25], "Replacement Gasketing Inserts")
    print(f"  Replacement Gasketing Inserts: {len(items)} items")
    all_items.extend(items)

    # 4. Grid tables (lite kits, louvers, glass)
    print("\n  --- Grid Tables (Lite Kits, Louvers, Glass) ---")
    grid_cat_counts = {}
    for entry in GRID_SECTIONS:
        cat, product, pg = entry[0], entry[1], entry[2]
        tidx = entry[3] if len(entry) > 3 else None
        items = parse_grid_page(pdf, pg, product, cat, table_index=tidx)
        grid_cat_counts[cat] = grid_cat_counts.get(cat, 0) + len(items)
        all_items.extend(items)
    for cat, count in sorted(grid_cat_counts.items()):
        print(f"  {cat}: {count} items")

    # 5. Security lite kits (page 44)
    items = parse_security_lite_kits(pdf, 44, "Security Lite Kits - L-VGLF")
    print(f"  Security Lite Kits - L-VGLF: {len(items)} items")
    all_items.extend(items)

    # 6. Door edges & astragals
    print("\n  --- Door Edges & Astragals ---")
    items = parse_door_edges(pdf, 56, "Door Edges & Astragals")
    print(f"  Door Edges & Astragals: {len(items)} items")
    all_items.extend(items)

    # 7. Continuous hinges
    print("\n  --- Continuous Hinges ---")
    items = parse_hinge_pages(pdf, [70], "Continuous Geared Hinges")
    print(f"  Continuous Geared Hinges: {len(items)} items")
    all_items.extend(items)

    items = parse_hinge_pages(pdf, [72], "SS Continuous Hinges")
    print(f"  SS Continuous Hinges: {len(items)} items")
    all_items.extend(items)

    items = parse_hinge_options(pdf, 71, "Hinge Electric Options & Parts")
    print(f"  Hinge Electric Options & Parts: {len(items)} items")
    all_items.extend(items)

    # 8. Sliding door hardware
    print("\n  --- Sliding Door Hardware ---")
    items = parse_sliding_door_pages(pdf, [76, 77, 78, 79, 80, 81],
                                     "Sliding Door Hardware")
    print(f"  Sliding Door Hardware: {len(items)} items")
    all_items.extend(items)

    pdf.close()
    return all_items


if __name__ == "__main__":
    print("Extracting NGP (National Guard Products) Price List ...\n")
    items = extract_all()

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    # Stats
    cats = {}
    for it in items:
        cats[it["category"]] = cats.get(it["category"], 0) + 1

    print(f"\nTotal items: {len(items)}")
    print(f"Categories: {len(cats)}")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")
    print(f"\nOutput: {OUT}")
