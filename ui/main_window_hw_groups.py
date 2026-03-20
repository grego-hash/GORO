import csv
from pathlib import Path
from typing import Optional

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
) -> None:
    """Render hardware groups to a two-column letter-size PDF."""
    page_width, page_height = letter
    margin = 0.75 * inch
    content_width = page_width - 2 * margin
    col_gap = 0.3 * inch
    col_width = (content_width - col_gap) / 2

    c = canvas.Canvas(file_path, pagesize=letter)

    y = page_height - margin
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(page_width / 2, y, "Hardware Groups")
    y -= 6
    c.setLineWidth(0.5)
    c.line(margin, y - 2, page_width - margin, y - 2)
    y -= 16

    group_title_h = 14
    bullet_h = 11
    group_gap = 10

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

    group_names = list(groups_data.keys())
    total_h = sum(_group_height(groups_data[g]) for g in group_names)
    half_h = total_h / 2.0
    left_groups: list = []
    right_groups: list = []
    running = 0.0
    for g in group_names:
        if running < half_h:
            left_groups.append(g)
        else:
            right_groups.append(g)
        running += _group_height(groups_data[g])

    def _draw_column(col_x: float, groups: list, start_y: float) -> None:
        cur_y = start_y
        for group_name in groups:
            parts = groups_data[group_name]
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(0, 0, 0)
            c.drawString(col_x, cur_y, group_name)
            cur_y -= group_title_h
            c.setFont("Helvetica", 8.5)
            for entry in parts:
                for line in _entry_lines(entry):
                    c.drawString(col_x + 10, cur_y, line)
                    cur_y -= bullet_h
            cur_y -= group_gap

    _draw_column(margin, left_groups, y)
    _draw_column(margin + col_width + col_gap, right_groups, y)
    c.save()

