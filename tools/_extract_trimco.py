"""Extract Trimco pricebook into structured CSVs using pdfplumber word coordinates.

Outputs:
  data/trimco_boxed_items.csv   – model, description, finish, price
  data/trimco_ap_items.csv      – family, size, finish, price
  data/trimco_specialty_items.csv – model, description, finish, price
"""
import pdfplumber, csv, re, os
from collections import defaultdict

PDF = r"C:\Users\grego\OneDrive - Stockham Construction, Inc\Desktop\PRICEBOOK\Trimco_List_Price_26_CAN.pdf"
DATA = os.path.join(os.path.dirname(__file__), "..", "data")

# ── helpers ──────────────────────────────────────────────────────────

PRICE_RE = re.compile(r"^\d{1,6}\.\d{2}$")
COMMA_PRICE_RE = re.compile(r"^(\d{1,3},\d{3}\.\d{2})$")

def is_price(s):
    s2 = s.replace(",", "")
    if PRICE_RE.match(s2):
        return float(s2)
    return None

def rows_from_words(words, y_tol=4):
    """Group words into rows by y-position."""
    rows = defaultdict(list)
    for w in words:
        y_key = round(w["top"] / y_tol) * y_tol
        rows[y_key].append(w)
    return {y: sorted(ws, key=lambda w: w["x0"]) for y, ws in sorted(rows.items())}


def find_header_rows(row_dict, header_markers):
    """Return list of (y, [word_dicts]) for rows containing header markers."""
    results = []
    for y, ws in row_dict.items():
        texts = {w["text"] for w in ws}
        if any(m in texts for m in header_markers):
            results.append((y, ws))
    return results


def build_col_map(header_words, known_finishes):
    """Build {finish_name: x_center} from header words that match known finish names."""
    col = {}
    for w in header_words:
        t = w["text"]
        if t in known_finishes:
            col[t] = (w["x0"] + w["x1"]) / 2
        elif t == "605/":
            col["605"] = (w["x0"] + w["x1"]) / 2
        elif t == "605/606":
            col["605"] = (w["x0"] + w["x1"]) / 2
        elif t == "611/612":
            col["611"] = (w["x0"] + w["x1"]) / 2
        elif t == "625/626":
            col["625"] = (w["x0"] + w["x1"]) / 2
        elif t == "622/613E":
            col["622"] = (w["x0"] + w["x1"]) / 2
    return col


def nearest_col(x, col_map, tolerance=20):
    """Map an x-position to the nearest column name."""
    best, best_d = None, tolerance
    for name, cx in col_map.items():
        d = abs(x - cx)
        if d < best_d:
            best, best_d = name, d
    return best


# ── BOXED PRICES (pages 45-78) ──────────────────────────────────────

BOXED_FINISHES = {"613", "613E", "622", "625", "626", "628", "629", "630",
                  "710", "Special", "Finishes"}
# 710 appears on a separate line above at the headers; center x ≈ 525
# "Special Finishes" label spans x ≈ 549

BOXED_COLS_FIXED = {
    "605":  250, "613": 282, "613E": 310, "622": 342, "625": 372,
    "626":  404, "628": 435, "629":  465, "630": 495, "710CU": 525,
    "SPECIAL": 553,
}

def extract_boxed_pages(pdf):
    """Extract boxed-prices data from pages 45-78 (0-indexed 44-77)."""
    items = []
    for pi in range(44, 78):
        page = pdf.pages[pi]
        words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
        row_map = rows_from_words(words)

        # Find header y so we skip header + preamble rows
        header_y = None
        for y, ws in row_map.items():
            texts = {w["text"] for w in ws}
            if "TRIMCO" in texts and "DESCRIPTION" in texts:
                header_y = y
                break
        if header_y is None:
            continue

        current_model = None
        current_desc = None

        for y in sorted(row_map.keys()):
            if y <= header_y:
                continue
            ws = row_map[y]
            texts = [w["text"] for w in ws]
            text_line = " ".join(texts)

            # Skip Notes, Options, page numbers, section headers
            if text_line.startswith("Note(s):") or text_line.startswith("Options:"):
                continue
            if text_line.startswith("PRICE LIST") or text_line.startswith("BOXED PRICES"):
                continue

            # Collect prices from this row
            prices = []
            non_price_words = []
            for w in ws:
                p = is_price(w["text"])
                if p is not None and w["x0"] > 200:  # prices are to the right
                    col = nearest_col((w["x0"] + w["x1"]) / 2, BOXED_COLS_FIXED, 18)
                    if col:
                        prices.append((col, p))
                elif w["x0"] < 230:
                    non_price_words.append(w)

            # Determine if this is a new model row or a continuation
            if non_price_words:
                first_x = non_price_words[0]["x0"]
                first_text = non_price_words[0]["text"]

                # Model numbers typically start at x ≈ 82-100
                # and match patterns like: 242, 243T, 1001-4x20, BP1, BP-S1, etc.
                is_model = (
                    first_x < 120
                    and re.match(r"^[A-Z0-9]", first_text)
                    and (prices or re.match(r"^\d", first_text) or
                         re.match(r"^[A-Z]{1,4}[\-]?[A-Z]?\d", first_text) or
                         re.match(r"^[A-Z]{2,}\d", first_text))
                )

                if is_model and prices:
                    # This is a model row with prices
                    # Separate model from description
                    model_token = first_text
                    desc_tokens = [w["text"] for w in non_price_words[1:]]
                    current_model = model_token
                    current_desc = " ".join(desc_tokens)
                    for col, price in prices:
                        items.append((current_model, current_desc, col, price))
                elif is_model and not prices:
                    # Model row but prices might be on a separate continuation line
                    model_token = first_text
                    desc_tokens = [w["text"] for w in non_price_words[1:]]
                    current_model = model_token
                    current_desc = " ".join(desc_tokens)
                elif not is_model and prices and current_model:
                    # Continuation with prices but looks like a sub-line
                    # The "prices only" line might have a price orphaned on its own line
                    for col, price in prices:
                        items.append((current_model, current_desc, col, price))
            elif prices and current_model:
                # Pure price row (orphan prices)
                for col, price in prices:
                    items.append((current_model, current_desc, col, price))

        if items:
            page_count = sum(1 for m, d, c, p in items if True)

    # Also handle page 44 (Mastercraft Bronze) separately
    page44_items = extract_page44(pdf)
    items = page44_items + items

    return items


def extract_page44(pdf):
    """Page 44: Mastercraft Bronze with columns DB, SB, SNB, 612, 613, Special."""
    page = pdf.pages[43]
    words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
    row_map = rows_from_words(words)

    # Columns from header: DB@290, SB@322, SNB@351, 612@384, 613@415, Special@535
    cols = {"DB": 290, "SB": 322, "SNB": 351, "612": 384, "613": 415, "SPECIAL": 535}

    header_y = None
    for y, ws in row_map.items():
        texts = {w["text"] for w in ws}
        if "TRIMCO" in texts and "DESCRIPTION" in texts:
            header_y = y
            break
    if header_y is None:
        return []

    items = []
    current_model = None
    current_desc = None

    for y in sorted(row_map.keys()):
        if y <= header_y:
            continue
        ws = row_map[y]
        prices = []
        non_price_words = []
        for w in ws:
            p = is_price(w["text"])
            if p is not None and w["x0"] > 250:
                col = nearest_col((w["x0"] + w["x1"]) / 2, cols, 25)
                if col:
                    prices.append((col, p))
            elif w["x0"] < 250:
                non_price_words.append(w)

        text_line = " ".join(w["text"] for w in non_price_words)
        if text_line.startswith("Note(s)") or text_line.startswith("Formerly"):
            continue
        if "Quote" in text_line:
            continue
        if text_line.startswith("PRICE LIST") or text_line.startswith("BOXED"):
            continue

        if non_price_words and prices:
            model_name = text_line.strip()
            current_model = model_name
            current_desc = ""
            for col, price in prices:
                items.append((current_model, current_desc, col, price))
        elif prices and current_model:
            for col, price in prices:
                items.append((current_model, current_desc, col, price))

    return items


# ── AP SERIES (pages 21-43) ─────────────────────────────────────────

AP_FINISHES = {"605/606", "605", "609", "611/612", "611", "612E", "613", "613E",
               "622", "625/626", "625", "628", "629", "316P", "630", "316S",
               "710", "313", "335", "712", "Special", "Finishes"}

def extract_ap_pages(pdf):
    """Extract AP series data from pages 21-43 using midpoint-based family assignment."""
    all_items = []

    for pi in range(20, 43):
        page = pdf.pages[pi]
        words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
        row_map = rows_from_words(words)

        # Find ALL header rows on this page
        headers = []
        for y, ws in row_map.items():
            texts = {w["text"] for w in ws}
            if "Family" in texts and ("Size" in texts or "OA" in texts):
                cols = build_col_map(ws, AP_FINISHES)
                for y2 in [y - 8, y - 16]:
                    if y2 in row_map:
                        for w2 in row_map[y2]:
                            if w2["text"] == "710":
                                cols["710"] = (w2["x0"] + w2["x1"]) / 2
                            if w2["text"] == "Special":
                                cols["SPECIAL"] = (w2["x0"] + w2["x1"]) / 2
                headers.append((y, cols))

        if not headers:
            continue
        headers.sort()

        for h_idx, (header_y, col_map) in enumerate(headers):
            next_header_y = headers[h_idx + 1][0] if h_idx + 1 < len(headers) else 9999

            # Collect ALL rows: data rows AND family-label rows
            data_rows = []   # (y, size, prices_dict)
            family_events = []  # (y, family_name)

            for y in sorted(row_map.keys()):
                if y <= header_y or y >= next_header_y:
                    continue
                ws = row_map[y]
                text_line = " ".join(w["text"] for w in ws)
                if "Note(s)" in text_line or "PRICE LIST" in text_line:
                    continue
                if "AP SERIES" in text_line or "AP400" in text_line or "AP300" in text_line:
                    continue
                if "Mounting" in text_line and "Types" in text_line:
                    continue

                prices = {}
                non_price = []
                for w in ws:
                    p = is_price(w["text"])
                    if p is not None and w["x0"] > 140:
                        col = nearest_col((w["x0"] + w["x1"]) / 2, col_map, 18)
                        if col:
                            prices[col] = p
                    else:
                        non_price.append(w)

                # Check for family name
                for w in non_price:
                    m = re.match(r"^(AP[C]?\d{2,3})", w["text"])
                    if m:
                        family_events.append((y, m.group(1)))
                        break

                # Find size
                size = None
                for w in non_price:
                    if re.match(r'^\d{1,3}"$', w["text"]):
                        size = w["text"]
                        break

                if size and prices:
                    data_rows.append((y, size, prices))

            if not data_rows or not family_events:
                continue

            # Assign each data row to nearest family using midpoint boundaries
            family_events.sort()
            for dy, size, prices in data_rows:
                # Find nearest family event
                best_fam = None
                best_dist = 9999
                for fy, fname in family_events:
                    dist = abs(dy - fy)
                    if dist < best_dist:
                        best_dist = dist
                        best_fam = fname
                if best_fam:
                    for col, price in prices.items():
                        all_items.append((best_fam, size, col, price))

    return all_items


# ── SPECIALTY ITEMS (pages 16-20) ───────────────────────────────────

def extract_specialty_pages(pdf):
    """Extract specialty items from pages 16-20."""
    items = []

    # --- Page 16: UHF210 Ultimate Slide Lock ---
    # Cols: 630, 622/613E  (710CU on separate line above)
    page = pdf.pages[15]
    words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
    row_map = rows_from_words(words)
    # Find header with "630" and column positions
    col16 = {}
    for y, ws in row_map.items():
        for w in ws:
            if w["text"] == "630":
                col16["630"] = (w["x0"] + w["x1"]) / 2
            if w["text"] == "622/613E":
                col16["622"] = (w["x0"] + w["x1"]) / 2
            if w["text"] == "710CU":
                col16["710CU"] = (w["x0"] + w["x1"]) / 2
    for y in sorted(row_map.keys()):
        ws = row_map[y]
        prices = {}
        model = None
        for w in ws:
            p = is_price(w["text"])
            if p is not None:
                col = nearest_col((w["x0"] + w["x1"]) / 2, col16, 30)
                if col:
                    prices[col] = p
            elif re.match(r"^UHF\d", w["text"]):
                model = w["text"]
        if model and prices:
            for col, price in prices.items():
                items.append((model, "Ultimate Slide Lock", col, price))

    # --- Page 17: LDH100 Lockdown Hardware ---
    # Cols: 605/606, 690, 625, 626, Powder, Special
    page = pdf.pages[16]
    words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
    row_map = rows_from_words(words)
    col17 = {}
    for y, ws in row_map.items():
        for w in ws:
            if w["text"] == "605/606":
                col17["605"] = (w["x0"] + w["x1"]) / 2
            if w["text"] == "690":
                col17["690"] = (w["x0"] + w["x1"]) / 2
            if w["text"] == "625":
                col17["625"] = (w["x0"] + w["x1"]) / 2
            if w["text"] == "626":
                col17["626"] = (w["x0"] + w["x1"]) / 2
    for y in sorted(row_map.keys()):
        ws = row_map[y]
        prices = {}
        model = None
        desc_parts = []
        for w in ws:
            p = is_price(w["text"])
            if p is not None and w["x0"] > 200:
                col = nearest_col((w["x0"] + w["x1"]) / 2, col17, 30)
                if col:
                    prices[col] = p
            elif re.match(r"^LDH\d", w["text"]):
                model = w["text"]
            elif w["x0"] > 100 and w["x0"] < 280:
                desc_parts.append(w["text"])
        if model and prices:
            desc = " ".join(desc_parts)
            for col, price in prices.items():
                items.append((model, desc, col, price))

    # --- Page 18: 9-Series Mortise Locks ---
    page = pdf.pages[17]
    words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
    row_map = rows_from_words(words)
    # Find header columns
    col18 = {}
    for y, ws in row_map.items():
        texts = {w["text"] for w in ws}
        if "TRIMCO" in texts or "605/606" in texts:
            for w in ws:
                if w["text"] == "605/606":
                    col18["605"] = (w["x0"] + w["x1"]) / 2
                elif w["text"] == "613":
                    col18["613"] = (w["x0"] + w["x1"]) / 2
                elif w["text"] == "622":
                    col18["622"] = (w["x0"] + w["x1"]) / 2
                elif w["text"] == "625":
                    col18["625"] = (w["x0"] + w["x1"]) / 2
                elif w["text"] == "626":
                    col18["626"] = (w["x0"] + w["x1"]) / 2
                elif w["text"] == "628":
                    col18["628"] = (w["x0"] + w["x1"]) / 2
                elif w["text"] == "630":
                    col18["630"] = (w["x0"] + w["x1"]) / 2
                elif w["text"] == "Special":
                    col18["SPECIAL"] = (w["x0"] + w["x1"]) / 2
    for y in sorted(row_map.keys()):
        ws = row_map[y]
        prices = {}
        model = None
        desc_parts = []
        for w in ws:
            p = is_price(w["text"])
            if p is not None and w["x0"] > 200:
                col = nearest_col((w["x0"] + w["x1"]) / 2, col18, 25)
                if col:
                    prices[col] = p
            elif re.match(r"^9\d{3}", w["text"]):
                model = w["text"]
            elif model and w["x0"] > 80 and w["x0"] < 200 and not re.match(r"^\d", w["text"]):
                desc_parts.append(w["text"])
        if model and prices:
            desc = " ".join(desc_parts)
            for col, price in prices.items():
                items.append((model, desc, col, price))

    # --- Page 19: UFP Ultimate Foot Pulls ---
    # Cols: 316S, 622, 710CU
    page = pdf.pages[18]
    words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
    row_map = rows_from_words(words)
    col19 = {}
    for y, ws in row_map.items():
        for w in ws:
            if w["text"] == "316S":
                col19["316S"] = (w["x0"] + w["x1"]) / 2
            if w["text"] == "622":
                col19["622"] = (w["x0"] + w["x1"]) / 2
            if w["text"] == "710CU":
                col19["710CU"] = (w["x0"] + w["x1"]) / 2
    for y in sorted(row_map.keys()):
        ws = row_map[y]
        prices = {}
        model = None
        for w in ws:
            p = is_price(w["text"])
            if p is not None:
                col = nearest_col((w["x0"] + w["x1"]) / 2, col19, 30)
                if col:
                    prices[col] = p
            elif w["text"] == "UFP":
                model = "UFP"
        if model and prices:
            for col, price in prices.items():
                items.append((model, "Ultimate Foot Pull", col, price))

    # --- Page 20: UCT Ultimate Counter Tops ---
    # Complex size x duty format. Extract with cork/tape and without.
    page = pdf.pages[19]
    text = page.extract_text() or ""
    lines = text.split("\n")
    section = None
    for line in lines:
        if "WITH CORK" in line:
            section = "Cork"
        elif "NO TAPE" in line:
            section = "NoTape"
        elif section:
            m = re.match(r"(?:Square|Rectangular)?\s*(\d+x\d+)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2}|-)", line)
            if not m:
                m = re.match(r"\s*(\d+x\d+)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2}|-)", line)
            if m:
                size, std, heavy = m.group(1), m.group(2), m.group(3)
                std_p = float(std.replace(",", ""))
                desc_tag = f"UCT1 {size} {section}"
                items.append((f"UCT1-{size}", f"Std Duty ({section})", "630", std_p))
                if heavy != "-":
                    heavy_p = float(heavy.replace(",", ""))
                    items.append((f"UCT1-{size}-HD", f"Heavy Duty ({section})", "630", heavy_p))

    return items


# ── DOOR PROTECTION PLATES (page 79) ─────────────────────────────────

# Column positions for the metal protection plate header on page 79
PROT_COLS = {
    "605": 225, "606": 255, "613": 286, "613E": 315,
    "622": 348, "628": 379, "629": 409, "630": 440,
    "710": 471, "SPECIAL": 497,
}

# Model patterns for protection plates
PROT_MODEL_RE = re.compile(r"^K[AMOSH0E]\d{3}$|^K6000$")

PLATE_TYPES = {
    "KA": "Armor Plate",
    "KM": "Mop Plate",
    "K0": "Kick Plate",
    "KS": "Stretcher Plate",
    "KH": "Handicap Kick Plate",
    "KE": "Self-Illuminated Exit Sign",
}

# Plastic plate columns (completely different header)
PLASTIC_COLS_ORDERED = [
    "Black", "Nubia Brown", "Clear Plastic", "Khaki Brown",
    "Beige", "Grey", "Dove Grey", "Frosty White",
]


def extract_protection_plates(pdf):
    """Extract door protection plate data from page 79 (0-indexed 78).

    Returns list of (model, plate_type, material, finish, price).
    Pricing is per 100 square inches.
    """
    page = pdf.pages[78]
    words = page.extract_words(keep_blank_chars=False, x_tolerance=3, y_tolerance=3)
    row_map = rows_from_words(words)

    items = []
    current_model = None
    current_material = None
    current_plate_type = None

    # Find the metal header row (y≈188)
    metal_header_y = None
    plastic_header_y = None
    for y, ws in row_map.items():
        texts = {w["text"] for w in ws}
        if "Family" in texts and "Material" in texts and "605" in texts:
            metal_header_y = y
        if "Family" in texts and "Material" in texts and "Black" in texts:
            plastic_header_y = y

    if metal_header_y is None:
        return items

    # Process metal plates (between metal header and plastic header)
    end_y = plastic_header_y if plastic_header_y else 9999

    for y in sorted(row_map.keys()):
        if y <= metal_header_y or y >= end_y:
            continue
        ws = row_map[y]

        # Look for model (e.g. KA050 at x≈160)
        model_word = None
        material_word = None
        for w in ws:
            if PROT_MODEL_RE.match(w["text"]) and 140 < w["x0"] < 180:
                model_word = w
            elif re.match(r'^\.\d{3}"$', w["text"]) and 180 < w["x0"] < 210:
                material_word = w

        if model_word:
            current_model = model_word["text"]
            pfx = current_model[:2]
            current_plate_type = PLATE_TYPES.get(pfx, "Protection Plate")
        if material_word:
            current_material = material_word["text"]

        if not current_model:
            continue

        # Collect numeric prices from this row
        for w in ws:
            p = is_price(w["text"])
            if p is not None and w["x0"] > 200:
                col = nearest_col((w["x0"] + w["x1"]) / 2, PROT_COLS, 18)
                if col:
                    items.append((current_model, current_plate_type,
                                  current_material or "", col, p))

    # Process plastic plates (K6000)
    if plastic_header_y:
        # K6000 column x-positions from header
        plastic_col_x = {}
        for y, ws in row_map.items():
            if abs(y - plastic_header_y) > 8:
                continue
            # Build column positions from header words
            for w in ws:
                t = w["text"]
                if t == "Black":
                    plastic_col_x["Black"] = (w["x0"] + w["x1"]) / 2
                elif t == "Beige":
                    plastic_col_x["Beige"] = (w["x0"] + w["x1"]) / 2
                elif t == "Grey" and w["x0"] < 400:
                    plastic_col_x["Grey"] = (w["x0"] + w["x1"]) / 2

        if not plastic_col_x:
            # Use fixed positions from analysis
            plastic_col_x = {
                "Black": 230, "Nubia Brown": 260, "Clear Plastic": 290,
                "Khaki Brown": 320, "Beige": 350, "Grey": 380,
                "Dove Grey": 412, "Frosty White": 444,
            }

        for y in sorted(row_map.keys()):
            if y <= plastic_header_y:
                continue
            ws = row_map[y]
            has_k6000 = any(w["text"] == "K6000" for w in ws)
            if not has_k6000:
                continue

            # Collect prices in order
            prices = []
            for w in sorted(ws, key=lambda w: w["x0"]):
                p = is_price(w["text"])
                if p is not None:
                    prices.append(p)

            # Map prices to colors in order
            for i, p in enumerate(prices):
                if i < len(PLASTIC_COLS_ORDERED):
                    items.append(("K6000", "Plastic Kick Plate", '1/8"',
                                  PLASTIC_COLS_ORDERED[i], p))

    return items


# ── MAIN ─────────────────────────────────────────────────────────────

def main():
    print("Opening PDF...")
    with pdfplumber.open(PDF) as pdf:
        print("\n--- Boxed Prices (pages 44-78) ---")
        boxed = extract_boxed_pages(pdf)
        print(f"  {len(boxed)} entries, {len(set(r[0] for r in boxed))} models")

        print("\n--- AP Series (pages 21-43) ---")
        ap = extract_ap_pages(pdf)
        print(f"  {len(ap)} entries, {len(set(r[0] for r in ap))} families")

        print("\n--- Specialty Items (pages 16-20) ---")
        spec = extract_specialty_pages(pdf)
        print(f"  {len(spec)} entries, {len(set(r[0] for r in spec))} models")

        print("\n--- Door Protection Plates (page 79) ---")
        prot = extract_protection_plates(pdf)
        print(f"  {len(prot)} entries, {len(set(r[0] for r in prot))} models")

    # Write CSVs
    with open(os.path.join(DATA, "trimco_boxed_items.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "description", "finish", "price"])
        for row in boxed:
            w.writerow(row)

    with open(os.path.join(DATA, "trimco_ap_items.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["family", "size", "finish", "price"])
        for row in ap:
            w.writerow(row)

    with open(os.path.join(DATA, "trimco_specialty_items.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "description", "finish", "price"])
        for row in spec:
            w.writerow(row)

    with open(os.path.join(DATA, "trimco_protection_plates.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "plate_type", "material", "finish", "price"])
        for row in prot:
            w.writerow(row)

    total = len(boxed) + len(ap) + len(spec) + len(prot)
    print(f"\nTotal: {total} pricing entries written")


if __name__ == "__main__":
    main()

