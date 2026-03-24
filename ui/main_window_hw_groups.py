import csv
from pathlib import Path
from typing import Optional

from core.constants import load_company_accent_color, accent_text_color
from core.optional_services import canvas, inch, letter, simpleSplit


def build_hw_groups_data_from_csv(
    hw_groups_csv: Path,
    hw_csv: Optional[Path] = None,
) -> dict[str, list[dict[str, str]]]:
    """Read Hardware_Groups.csv and return group_name -> part rows with qty and metadata."""
    groups_data: dict = {}
    try:
        with open(hw_groups_csv, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = list(reader.fieldnames or [])

            def _find_col(candidates):
                for candidate in candidates:
                    for h in headers:
                        if (h or "").strip().lower() == candidate.lower():
                            return h
                return None

            group_col = _find_col(["hardware group"])
            part_col = _find_col(["hardware part", "part name", "part"])
            part_id_col = _find_col(["part id"])
            qty_col = _find_col(["count", "qty", "quantity"])

            if not group_col:
                return groups_data

            part_id_lookup: dict = {}
            part_name_lookup: dict = {}
            if hw_csv and Path(hw_csv).exists():
                try:
                    with open(hw_csv, "r", newline="", encoding="utf-8-sig") as hf:
                        hw_reader = csv.DictReader(hf)
                        hw_headers = list(hw_reader.fieldnames or [])

                        def _find_hw_col(candidates):
                            for candidate in candidates:
                                for h in hw_headers:
                                    if (h or "").strip().lower() == candidate.lower():
                                        return h
                            return None

                        hw_part_col = _find_hw_col(["hardware part", "part name"])
                        hw_id_col = _find_hw_col(["part id"])
                        hw_mfr_col = _find_hw_col(["mfr", "manufacturer"])
                        hw_finish_col = _find_hw_col(["finish"])
                        hw_category_col = _find_hw_col(["category"])

                        for hrow in hw_reader:
                            pname = (hrow.get(hw_part_col) or "").strip() if hw_part_col else ""
                            pid = (hrow.get(hw_id_col) or "").strip() if hw_id_col else ""
                            mfr = (hrow.get(hw_mfr_col) or "").strip() if hw_mfr_col else ""
                            finish = (hrow.get(hw_finish_col) or "").strip() if hw_finish_col else ""
                            category = (hrow.get(hw_category_col) or "").strip() if hw_category_col else ""
                            details = {
                                "part_name": pname,
                                "mfr": mfr,
                                "finish": finish,
                                "category": category,
                            }
                            if pid:
                                part_id_lookup[pid] = details
                            if pname:
                                part_name_lookup[pname.lower()] = details
                except Exception:
                    pass

            for row in reader:
                group_name = (row.get(group_col) or "").strip()
                if not group_name:
                    continue
                part_name = (row.get(part_col) or "").strip() if part_col else ""
                qty = (row.get(qty_col) or "").strip() if qty_col else ""
                mfr = ""
                finish = ""
                category = ""

                pid = (row.get(part_id_col) or "").strip() if part_id_col else ""
                if pid and pid in part_id_lookup:
                    details = part_id_lookup[pid]
                    part_name = part_name or details.get("part_name", "")
                    mfr = details.get("mfr", "")
                    finish = details.get("finish", "")
                    category = details.get("category", "")

                if part_name and part_name.lower() in part_name_lookup:
                    details = part_name_lookup[part_name.lower()]
                    if not mfr:
                        mfr = details.get("mfr", "")
                    if not finish:
                        finish = details.get("finish", "")
                    if not category:
                        category = details.get("category", "")

                if not part_name:
                    continue
                if group_name not in groups_data:
                    groups_data[group_name] = []
                groups_data[group_name].append(
                    {
                        "part_name": part_name,
                        "qty": qty,
                        "mfr": mfr,
                        "finish": finish,
                        "category": category,
                    }
                )
    except Exception:
        pass
    return groups_data


def write_hardware_groups_pdf(
    file_path: str,
    groups_data: dict[str, list[dict[str, str]]],
    accent_color: Optional[str] = None,
    data_root=None,
) -> None:
    """Render hardware groups to a two-column letter-size PDF with pagination."""
    if accent_color is None:
        accent_color = load_company_accent_color(data_root)
    fg_color = accent_text_color(accent_color)

    page_width, page_height = letter
    margin = 0.75 * inch
    content_width = page_width - 2 * margin
    col_gap = 0.3 * inch
    col_width = (content_width - col_gap) / 2
    bottom_margin = 0.75 * inch

    group_title_h = 14
    bullet_h = 11
    group_gap = 10

    c = canvas.Canvas(file_path, pagesize=letter)

    def _hex_to_rgb(hex_str: str):
        h = hex_str.lstrip("#")
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        return int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0

    def _entry_lines(entry: dict) -> list[str]:
        part_name = entry.get("part_name", "")
        qty = entry.get("qty", "")
        mfr = entry.get("mfr", "")
        finish = entry.get("finish", "")
        category = entry.get("category", "")

        first_line = f"- {part_name} x {qty}" if qty else f"- {part_name}"
        meta_parts = []
        if mfr:
            meta_parts.append(f"MFR: {mfr}")
        if finish:
            meta_parts.append(f"Finish: {finish}")
        if category:
            meta_parts.append(f"Category: {category}")
        if meta_parts:
            first_line = f"{first_line} | " + " | ".join(meta_parts)

        return simpleSplit(first_line, "Helvetica", 8.5, col_width - 10)

    def _group_height(parts: list) -> float:
        lines_count = 0
        for entry in parts:
            lines_count += max(1, len(_entry_lines(entry)))
        return group_title_h + lines_count * bullet_h + group_gap

    def _draw_header() -> float:
        """Draw page header banner and return the starting Y position for content."""
        y = page_height - margin
        bar_height = 24
        bg_r, bg_g, bg_b = _hex_to_rgb(accent_color)
        fg_r, fg_g, fg_b = _hex_to_rgb(fg_color)
        c.setFillColorRGB(bg_r, bg_g, bg_b)
        c.rect(margin, y - bar_height + 4, content_width, bar_height, stroke=0, fill=1)
        c.setFillColorRGB(fg_r, fg_g, fg_b)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(page_width / 2, y - bar_height + 11, "Hardware Groups")
        c.setFillColorRGB(0, 0, 0)
        y -= bar_height + 8
        return y

    # -- Flow groups into two columns per page with page breaks --
    group_names = list(groups_data.keys())
    col_x_left = margin
    col_x_right = margin + col_width + col_gap

    content_start_y = _draw_header()
    cur_col = 0  # 0 = left, 1 = right
    cur_y = content_start_y

    for group_name in group_names:
        parts = groups_data[group_name]
        gh = _group_height(parts)

        # If this group won't fit in the current column, advance
        if cur_y - gh < bottom_margin:
            if cur_col == 0:
                # Move to right column on same page
                cur_col = 1
                cur_y = content_start_y
                # Re-check fit in right column
                if cur_y - gh < bottom_margin:
                    # Won't fit in right column either — start new page
                    c.showPage()
                    content_start_y = _draw_header()
                    cur_col = 0
                    cur_y = content_start_y
            else:
                # Right column full — start new page
                c.showPage()
                content_start_y = _draw_header()
                cur_col = 0
                cur_y = content_start_y

        col_x = col_x_left if cur_col == 0 else col_x_right

        # Draw group title
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(col_x, cur_y, group_name)
        cur_y -= group_title_h

        # Draw entries, handling page breaks mid-group
        c.setFont("Helvetica", 8.5)
        for entry in parts:
            for line in _entry_lines(entry):
                if cur_y < bottom_margin:
                    if cur_col == 0:
                        cur_col = 1
                        cur_y = content_start_y
                    else:
                        c.showPage()
                        content_start_y = _draw_header()
                        cur_col = 0
                        cur_y = content_start_y
                    col_x = col_x_left if cur_col == 0 else col_x_right
                    # Re-draw group continuation label
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(col_x, cur_y, f"{group_name} (cont.)")
                    cur_y -= group_title_h
                    c.setFont("Helvetica", 8.5)
                c.drawString(col_x + 10, cur_y, line)
                cur_y -= bullet_h
        cur_y -= group_gap

    c.save()

