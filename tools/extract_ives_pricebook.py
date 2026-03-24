"""Extract ALL pricing data from the Ives Pricebook #16 (Feb 2026) PDF.

Reads the PDF with pdfplumber, parses every product section,
and writes structured JSON to data/ives_pricebook_data.json.

Run:  python tools/extract_ives_pricebook.py [path_to_pdf]
"""

import json
import re
import sys
from pathlib import Path

import pdfplumber

# ─── Default PDF path ────────────────────────────────────────────────
DEFAULT_PDF = (
    r"C:\Users\grego\OneDrive - Stockham Construction, Inc"
    r"\Desktop\PRICEBOOK\Ives_Price_Book_Feb2026_CAN110060.pdf"
)

# ─── BHMA → US finish display name mapping ───────────────────────────
BHMA_TO_US = {
    "600": "USP - Primed",
    "602": "US2C - Zinc Dichromate",
    "603": "US2G - Zinc Plated",
    "604": "US2C - Zinc Dichromate",
    "605": "US3 - Bright Brass",
    "606": "US4 - Satin Brass",
    "609": "US5 - Antique Brass",
    "610": "US9 - Bright Bronze",
    "612": "US10 - Satin Bronze",
    "613": "US10B - Oil Rubbed Bronze",
    "618": "US14 - Bright Nickel",
    "619": "US15 - Satin Nickel",
    "621": "US15A - Satin Nickel, Blackened",
    "622": "BLK - Black",
    "625": "US26 - Bright Chrome",
    "626": "US26D - Satin Chrome",
    "628": "US28 - Satin Aluminum",
    "629": "US32 - Bright Stainless",
    "630": "US32D - Satin Stainless",
    "632": "US3 - Bright Brass (Steel)",
    "633": "US4 - Satin Brass (Steel)",
    "636": "US7 - French Gray (Steel)",
    "638": "US5 - Antique Brass (Steel)",
    "639": "US10 - Satin Bronze (Steel)",
    "640": "US10B - Oil Rubbed Bronze (Steel)",
    "643E": "643E - Aged Bronze",
    "645": "US14 - Bright Nickel (Steel)",
    "646": "US15 - Satin Nickel (Steel)",
    "647": "US15A - Satin Nickel Blackened (Steel)",
    "651": "US26 - Bright Chrome (Steel)",
    "652": "US26D - Satin Chrome (Steel)",
    "666": "A3 - Bright Brass (Aluminum)",
    "667": "A4 - Satin Brass (Aluminum)",
    "668": "A10 - Satin Bronze (Aluminum)",
    "689": "SP28 - Satin Aluminum (Steel)",
    "691": "SP10 - Satin Bronze (Steel)",
    "695": "SP313 - Dark Bronze (Steel)",
    "703": "A10B - Dark Bronze (Aluminum)",
    "706": "SP4 - Satin Brass (Steel)",
    "710": "313 - Dark Bronze Anodized",
    "711": "315 - Flat Black",
    "716": "643E - Aged Bronze",
}


def parse_price(s):
    """Parse a price string like '$24.00' or '-' into float or None."""
    if not s:
        return None
    s = s.strip().replace(",", "")
    if s in ("-", "", "N/A"):
        return None
    m = re.search(r"\$?([\d.]+)", s)
    return float(m.group(1)) if m else None


def finish_display(bhma):
    """Get display name for a BHMA finish code."""
    return BHMA_TO_US.get(bhma, bhma)


# ─── Table helpers ────────────────────────────────────────────────────

def is_sidebar(table):
    """Return True if table is the sidebar navigation (reversed text)."""
    if not table or len(table) < 2:
        return True
    flat = " ".join(str(c or "") for row in table[:3] for c in row)
    return "STOVIP" in flat or "SEGNIH" in flat or "HINGES" in flat


def get_data_tables(page):
    """Get all non-sidebar tables from a page."""
    tables = page.extract_tables()
    return [t for t in tables if not is_sidebar(t) and len(t) >= 3]


# ═════════════════════════════════════════════════════════════════════
#  Section parsers
# ═════════════════════════════════════════════════════════════════════

def parse_architectural_hinges(pdf, pages):
    """Parse Architectural Hinges (pages 8-30).
    Format: MODEL/DESC, SIZE, STEEL-BHMA, STEEL-LIST, _, _, BRASS-BHMA, BRASS-LIST, _, _, US-REF, BOX, CASE
    """
    items = []
    for pg_num in pages:
        for table in get_data_tables(pdf.pages[pg_num]):
            current_model = None
            current_desc = ""
            current_size = None
            for row in table[2:]:  # skip header rows
                col0 = (row[0] or "").strip()
                col1 = (row[1] or "").strip() if len(row) > 1 else ""

                # New model block
                if col0 and not col0.startswith("$"):
                    lines = col0.split("\n")
                    current_model = lines[0].strip()
                    current_desc = " ".join(l.strip() for l in lines[1:4])

                # Size
                if col1:
                    current_size = col1.split("\n")[0].strip()

                if not current_model or not current_size:
                    continue

                # Steel-based finish
                steel_bhma = (row[2] or "").strip() if len(row) > 2 else ""
                steel_price = parse_price(row[3] if len(row) > 3 else "")
                if steel_bhma and steel_price is not None:
                    items.append({
                        "category": "Architectural Hinges",
                        "model": current_model,
                        "description": current_desc,
                        "size": current_size,
                        "substrate": "Steel",
                        "bhma": steel_bhma,
                        "price": steel_price,
                    })

                # Brass/Stainless finish
                brass_bhma = (row[6] or "").strip() if len(row) > 6 else ""
                brass_price = parse_price(row[7] if len(row) > 7 else "")
                if brass_bhma and brass_price is not None and brass_bhma != "-":
                    items.append({
                        "category": "Architectural Hinges",
                        "model": current_model,
                        "description": current_desc,
                        "size": current_size,
                        "substrate": "Brass/Stainless",
                        "bhma": brass_bhma,
                        "price": brass_price,
                    })

    return items


def parse_continuous_geared(pdf, pages):
    """Parse Continuous Geared Hinges (pages 35-41).
    Format: MODEL NUMBER, DESCRIPTION, FINISH, LENGTH, ALUMINUM BHMA, LIST, _, _
    """
    items = []
    for pg_num in pages:
        for table in get_data_tables(pdf.pages[pg_num]):
            hdr = str(table[0][0] or "")
            if "MODEL" not in hdr.upper() and "LEDOM" not in hdr:
                continue
            current_model = None
            current_desc = ""
            for row in table[2:]:
                col0 = (row[0] or "").strip()
                col1 = (row[1] or "").strip() if len(row) > 1 else ""
                col2 = (row[2] or "").strip() if len(row) > 2 else ""
                col3 = (row[3] or "").strip() if len(row) > 3 else ""

                if col0 and not col0.startswith("$"):
                    lines = col0.split("\n")
                    current_model = lines[0].strip()
                    current_desc = " ".join(l.strip() for l in lines[1:3])

                if not current_model:
                    continue

                # Format: FINISH, LENGTH, BHMA, LIST
                finish_us = col2
                length = col3

                bhma = (row[4] or "").strip() if len(row) > 4 else ""
                price_str = row[5] if len(row) > 5 else ""
                price_val = parse_price(price_str)

                if bhma and price_val is not None:
                    items.append({
                        "category": "Continuous Geared Hinges",
                        "model": current_model,
                        "description": current_desc,
                        "finish": finish_us,
                        "length": length,
                        "bhma": bhma,
                        "price": price_val,
                    })
    return items


def parse_pin_barrel_continuous(pdf, pages):
    """Parse Pin & Barrel Continuous Hinges (page 33).
    Format varies — MODEL, DESCRIPTION, LENGTH, then finish columns.
    """
    items = []
    for pg_num in pages:
        for table in get_data_tables(pdf.pages[pg_num]):
            hdr = str(table[0][0] or "")
            if "MODEL" not in hdr.upper() and "LEDOM" not in hdr:
                continue
            # Try to extract finish column headers
            sub_hdr = table[1] if len(table) > 1 else []
            current_model = None
            current_desc = ""
            for row in table[2:]:
                col0 = (row[0] or "").strip()
                if col0 and not col0.startswith("$") and not col0.startswith("-"):
                    lines = col0.split("\n")
                    current_model = lines[0].strip()
                    current_desc = " ".join(l.strip() for l in lines[1:3])

                if not current_model:
                    continue

                # Length column
                length = (row[2] or "").strip() if len(row) > 2 else ""

                # Price columns start at 3+, mapped to finishes in header
                for ci in range(3, min(len(row), len(table[0]))):
                    finish_hdr = str(table[0][ci] or "").strip()
                    if not finish_hdr or finish_hdr == "N":
                        continue
                    price_val = parse_price(row[ci] if ci < len(row) else "")
                    if price_val is not None:
                        items.append({
                            "category": "Pin & Barrel Continuous Hinges",
                            "model": current_model,
                            "description": current_desc,
                            "length": length if length else "Standard",
                            "bhma": finish_hdr.split("\n")[0].strip(),
                            "price": price_val,
                        })
    return items


def parse_pivots(pdf, pages):
    """Parse Pivots (pages 42-44).
    Wide table with finish columns across the top (reversed text headers).
    """
    items = []
    for pg_num in pages:
        for table in get_data_tables(pdf.pages[pg_num]):
            if len(table) < 4:
                continue
            # Row 2 has US finish names, Row 0-1 have BHMA codes
            # Extract finish mapping from header rows
            finish_map = {}
            for ci in range(3, len(table[0])):
                bhma_raw = str(table[0][ci] or "").strip().replace("\n", "/")
                us_raw = str(table[2][ci] or "").strip() if len(table) > 2 and ci < len(table[2]) else ""
                if bhma_raw and bhma_raw not in ("-", "N", ""):
                    finish_map[ci] = bhma_raw.split("/")[0]

            current_model = None
            current_desc = ""
            for row in table[4:]:
                col0 = (row[0] or "").strip()
                col1 = (row[1] or "").strip() if len(row) > 1 else ""
                col2 = (row[2] or "").strip() if len(row) > 2 else ""

                if col0 and not col0.startswith("$"):
                    lines = col0.split("\n")
                    current_model = lines[0].strip()
                if col1 and not col1.startswith("$"):
                    current_desc = col1.split("\n")[0].strip()

                if not current_model:
                    continue

                lb_rating = col2

                for ci, bhma in finish_map.items():
                    if ci < len(row):
                        price_val = parse_price(row[ci])
                        if price_val is not None:
                            items.append({
                                "category": "Pivots",
                                "model": current_model,
                                "description": current_desc,
                                "lb_rating": lb_rating,
                                "bhma": bhma,
                                "price": price_val,
                            })
    return items


def parse_standard_product(pdf, pages, category):
    """Parse standard product table format used by most sections.
    Key columns: MODEL NUMBER (col with finish), BHMA FINISH, LIST PRICE.
    Handles variants with/without sub-header rows, PUSH/PULL CTC columns, etc.
    """
    items = []
    for pg_num in pages:
        for table in get_data_tables(pdf.pages[pg_num]):
            # Identify column positions from header
            headers = [str(c or "").upper().replace("\n", " ") for c in table[0]]

            # Find key columns
            model_col = None
            model_num_col = None
            bhma_col = None
            price_col = None
            size_col = None
            substrate_col = None
            pull_ctc_col = None
            push_ctc_col = None
            plate_size_col = None

            for i, h in enumerate(headers):
                if "MODEL NUMBER" in h and model_num_col is None:
                    model_num_col = i
                elif h.startswith("MODEL") and model_col is None:
                    model_col = i
                elif "BHMA" in h:
                    bhma_col = i
                elif "LIST PRICE" in h or h == "LIST PRICE":
                    if price_col is None:
                        price_col = i
                elif "SUBSTRATE" in h:
                    substrate_col = i
                elif "PUSH CTC" in h or "PUSH  CTC" in h:
                    push_ctc_col = i
                elif "PULL CTC" in h or "PULL  CTC" in h:
                    pull_ctc_col = i
                elif "PLATE SIZE" in h:
                    plate_size_col = i
                elif "SIZE" in h:
                    size_col = i

            # Fallback: find "LIST" in any header (catches "LIST PRICE", "LIST\nPRICE")
            if price_col is None:
                for i, h in enumerate(headers):
                    if "LIST" in h:
                        price_col = i
                        break

            if price_col is None:
                continue

            # Determine data start row: skip header and optional sub-header
            data_start = 1
            if len(table) > 1:
                sub = table[1]
                sub_text = " ".join(str(s or "") for s in sub).upper()
                # Check for EACH vs PACKAGE sub-header
                for i, s in enumerate(sub or []):
                    if str(s or "").upper().strip() == "EACH":
                        price_col = i
                        break
                # If row 1 looks like a sub-header (contains BHMA, EACH, FINISH, etc.)
                if any(kw in sub_text for kw in ("BHMA", "EACH", "PACKAGE", "FINISH")):
                    data_start = 2

            current_model = None
            current_desc = ""
            current_substrate = None

            for row in table[data_start:]:
                if len(row) <= price_col:
                    continue

                # Get model name from model column
                if model_col is not None and (row[model_col] or "").strip():
                    raw = row[model_col].strip()
                    lines = raw.split("\n")
                    current_model = lines[0].strip()
                    current_desc = " ".join(l.strip() for l in lines[1:3])

                # Get substrate
                if substrate_col is not None and (row[substrate_col] or "").strip():
                    current_substrate = row[substrate_col].strip()

                if not current_model:
                    continue

                # Get model number (includes finish suffix)
                model_number = ""
                if model_num_col is not None:
                    model_number = (row[model_num_col] or "").strip()

                # Get BHMA finish
                bhma = ""
                if bhma_col is not None:
                    bhma = (row[bhma_col] or "").strip()

                # Get price
                price_val = parse_price(row[price_col] if price_col < len(row) else "")

                if price_val is None:
                    continue

                # Get optional extra fields
                extra = {}
                if pull_ctc_col is not None and (row[pull_ctc_col] or "").strip():
                    extra["pull_ctc"] = row[pull_ctc_col].strip()
                if push_ctc_col is not None and (row[push_ctc_col] or "").strip():
                    extra["push_ctc"] = row[push_ctc_col].strip()
                if plate_size_col is not None and (row[plate_size_col] or "").strip():
                    extra["plate_size"] = row[plate_size_col].strip()
                if size_col is not None and (row[size_col] or "").strip():
                    extra["size"] = row[size_col].strip()

                item = {
                    "category": category,
                    "model": current_model,
                    "description": current_desc,
                    "model_number": model_number,
                    "bhma": bhma,
                    "substrate": current_substrate or "",
                    "price": price_val,
                }
                item.update(extra)
                items.append(item)

    return items


def parse_edge_guards(pdf, pages):
    """Parse Edge Guards (pages 95-97).
    Format: MODEL NUMBER, MODEL IMAGE, STYLE, SIZE, then finish price columns.
    """
    items = []
    for pg_num in pages:
        for table in get_data_tables(pdf.pages[pg_num]):
            headers = [str(c or "").strip() for c in table[0]]
            # Find finish columns (they have BHMA codes in header)
            finish_cols = {}
            for i, h in enumerate(headers):
                m = re.search(r"(\d{3})", h)
                if m and i >= 4:
                    finish_cols[i] = m.group(1)

            if not finish_cols:
                continue

            current_model = None
            current_style = None
            for row in table[1:]:
                col0 = (row[0] or "").strip()
                col2 = (row[2] or "").strip() if len(row) > 2 else ""
                col3 = (row[3] or "").strip() if len(row) > 3 else ""

                if col0:
                    current_model = col0
                if col2:
                    current_style = col2

                size = col3
                if not current_model or not size:
                    continue

                for ci, bhma in finish_cols.items():
                    if ci < len(row):
                        price_val = parse_price(row[ci])
                        if price_val is not None:
                            items.append({
                                "category": "Edge Guards",
                                "model": current_model,
                                "style": current_style or "",
                                "size": size,
                                "bhma": bhma,
                                "price": price_val,
                            })
    return items


def parse_long_door_pulls(pdf, pages):
    """Parse Long Door Pulls — Offset (pages 75) and Straight (76-78).
    Format: MODEL, LENGTH, PULL CTC, FINISH (BHMA), LIST PRICE
    """
    items = []
    for pg_num in pages:
        for table in get_data_tables(pdf.pages[pg_num]):
            current_model = None
            current_desc = ""
            for row in table[1:]:
                col0 = (row[0] or "").strip()
                col1 = (row[1] or "").strip() if len(row) > 1 else ""
                col2 = (row[2] or "").strip() if len(row) > 2 else ""
                col3 = (row[3] or "").strip() if len(row) > 3 else ""

                if col0 and not col0.startswith("$"):
                    lines = col0.split("\n")
                    current_model = lines[0].strip()
                    current_desc = " ".join(l.strip() for l in lines[1:3])

                if not current_model:
                    continue

                length = col1
                bhma = col3
                price_val = parse_price(row[4] if len(row) > 4 else "")

                if bhma and price_val is not None:
                    items.append({
                        "category": "Long Door Pulls",
                        "model": current_model,
                        "description": current_desc,
                        "length": length or "",
                        "pull_ctc": col2,
                        "bhma": bhma,
                        "price": price_val,
                    })
    return items


def parse_protection_plates(pdf, pages):
    """Parse Protection Plates (pages 92-94).
    May have different format with size-based addons.
    """
    items = []
    for pg_num in pages:
        for table in get_data_tables(pdf.pages[pg_num]):
            headers = [str(c or "").upper() for c in table[0]]
            # Standard product format or addon format
            if "LIST ADD" in " ".join(headers):
                # Addon/surcharge table — skip for now
                continue
            # Try standard format
            items.extend(
                parse_standard_product(pdf, [pg_num], "Protection Plates")
            )
            break  # avoid double-processing
    return items


# ═════════════════════════════════════════════════════════════════════
#  Main extraction orchestrator
# ═════════════════════════════════════════════════════════════════════

def extract_all(pdf_path):
    """Extract all pricing data from the Ives pricebook."""
    pdf = pdfplumber.open(pdf_path)
    all_items = []

    print("Extracting Architectural Hinges (pages 8-30)...")
    all_items.extend(parse_architectural_hinges(pdf, range(8, 31)))

    print("Extracting Pin & Barrel Continuous Hinges (page 33)...")
    all_items.extend(parse_pin_barrel_continuous(pdf, [33]))

    print("Extracting Continuous Geared Hinges (pages 35-41)...")
    all_items.extend(parse_continuous_geared(pdf, range(35, 42)))

    print("Extracting Pivots (pages 42-44)...")
    all_items.extend(parse_pivots(pdf, range(42, 45)))

    print("Extracting Architectural Pulls (pages 48-67)...")
    all_items.extend(parse_standard_product(pdf, range(48, 68), "Architectural Pulls"))

    print("Extracting Decorative Pulls (pages 68-74)...")
    all_items.extend(parse_standard_product(pdf, range(68, 75), "Decorative Pulls"))

    print("Extracting Long Door Pulls (pages 75-78)...")
    all_items.extend(parse_long_door_pulls(pdf, range(75, 79)))

    print("Extracting Sliding Door Pulls (pages 79-80)...")
    all_items.extend(parse_standard_product(pdf, range(79, 81), "Sliding Door Pulls"))

    print("Extracting Push & Pull Plates (pages 81-91)...")
    all_items.extend(parse_standard_product(pdf, range(81, 92), "Push & Pull Plates"))

    print("Extracting Protection Plates (pages 92-94)...")
    all_items.extend(parse_standard_product(pdf, range(92, 95), "Protection Plates"))

    print("Extracting Edge Guards (pages 94-97)...")
    all_items.extend(parse_edge_guards(pdf, range(94, 98)))

    print("Extracting Vandal Resistant Trim (page 98)...")
    all_items.extend(parse_standard_product(pdf, [98], "Vandal Resistant Trim"))

    print("Extracting Flush Pulls (pages 99-101)...")
    all_items.extend(parse_standard_product(pdf, range(99, 102), "Flush Pulls"))

    print("Extracting Flush Bolts (pages 101-107)...")
    all_items.extend(parse_standard_product(pdf, range(101, 108), "Flush Bolts"))

    print("Extracting Coordinators (pages 108-110)...")
    all_items.extend(parse_standard_product(pdf, range(108, 111), "Coordinators"))

    print("Extracting Surface Bolts (pages 111-115)...")
    all_items.extend(parse_standard_product(pdf, range(111, 116), "Surface Bolts"))

    print("Extracting Door Guards & Dutch Door Bolts (pages 115-116)...")
    all_items.extend(parse_standard_product(pdf, range(115, 117), "Door Guards"))

    print("Extracting Roller Latches (pages 117-119)...")
    all_items.extend(parse_standard_product(pdf, range(117, 120), "Roller Latches"))

    print("Extracting Angle Stops (page 120)...")
    all_items.extend(parse_standard_product(pdf, [120], "Angle Stops"))

    print("Extracting Latches & Catches (pages 121-123)...")
    all_items.extend(parse_standard_product(pdf, range(121, 124), "Latches & Catches"))

    print("Extracting Floor Stops (pages 124-127)...")
    all_items.extend(parse_standard_product(pdf, range(124, 128), "Floor Stops"))

    print("Extracting Floor Stops & Holders (pages 128-129)...")
    all_items.extend(parse_standard_product(pdf, range(128, 130), "Floor Stops & Holders"))

    print("Extracting Wall Stops & Bumpers (pages 130-132)...")
    all_items.extend(parse_standard_product(pdf, range(130, 133), "Wall Stops & Bumpers"))

    print("Extracting Wall Stops & Holders (page 133)...")
    all_items.extend(parse_standard_product(pdf, [133], "Wall Stops & Holders"))

    print("Extracting Door Holders (pages 134-136)...")
    all_items.extend(parse_standard_product(pdf, range(134, 137), "Door Holders"))

    print("Extracting Roller Bumpers & Residential Stops (pages 137-142)...")
    all_items.extend(parse_standard_product(pdf, range(137, 143), "Residential Door Stops"))

    print("Extracting Door Silencers & Crash Stops (page 143)...")
    all_items.extend(parse_standard_product(pdf, [143], "Door Silencers"))

    print("Extracting Lock Guards (pages 143-144)...")
    all_items.extend(parse_standard_product(pdf, range(143, 145), "Lock Guards"))

    print("Extracting Viewers (pages 145-146)...")
    all_items.extend(parse_standard_product(pdf, range(145, 147), "Viewers"))

    print("Extracting Door Knockers & Mail Slots (pages 147-148)...")
    all_items.extend(parse_standard_product(pdf, range(147, 149), "Exterior Hardware"))

    print("Extracting Brackets & Hooks (pages 149-156)...")
    all_items.extend(parse_standard_product(pdf, range(149, 157), "Brackets & Hooks"))

    print("Extracting Window Hardware (pages 157-158)...")
    all_items.extend(parse_standard_product(pdf, range(157, 159), "Window Hardware"))

    print("Extracting Rescue Hardware (page 159)...")
    all_items.extend(parse_standard_product(pdf, [159], "Rescue Hardware"))

    pdf.close()
    return all_items


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PDF
    if not Path(pdf_path).exists():
        print(f"ERROR: PDF not found at {pdf_path}")
        sys.exit(1)

    items = extract_all(pdf_path)

    # Summary
    by_cat = {}
    for item in items:
        cat = item["category"]
        by_cat[cat] = by_cat.get(cat, 0) + 1

    print(f"\n{'='*60}")
    print(f"Total items extracted: {len(items)}")
    print(f"{'='*60}")
    for cat, count in sorted(by_cat.items()):
        print(f"  {cat}: {count}")

    # Write JSON
    out_path = Path(__file__).resolve().parent.parent / "data" / "ives_pricebook_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    print(f"\nData written to {out_path}")


if __name__ == "__main__":
    main()
