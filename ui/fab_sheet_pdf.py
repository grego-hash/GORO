"""Render a single Door Fabrication Sheet to PDF using ReportLab.

Mirrors the in-app FabSheetCanvas layout with a cleaner visual hierarchy:
    - Company logo + title
    - Project summary and door-detail cards
    - 4-column body: Hinges+Lock | Machining Specs | Light/Louver+Other HW | Door # grid
"""

from __future__ import annotations

from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from ui.fab_sheet_builder import FabSheet


# ── Geometry constants ──────────────────────────────────────────────

PAGE_W, PAGE_H = landscape(letter)  # 792 x 612 pts
MARGIN = 30
USABLE_W = PAGE_W - 2 * MARGIN
USABLE_H = PAGE_H - 2 * MARGIN

# Font sizes
F_TITLE = 12
F_SECTION = 9
F_LABEL = 7
F_VALUE = 8

LINE_H = 13  # line height for rows

# PDF colors
C_BG = (0.98, 0.98, 0.99)
C_BORDER = (0.78, 0.8, 0.84)
C_TITLE_BG = (0.92, 0.95, 0.99)
C_TITLE_FG = (0.11, 0.22, 0.37)
C_LABEL = (0.33, 0.36, 0.42)
C_VALUE = (0.08, 0.09, 0.1)

# Column geometry (4 columns)
COL_GAP = 6
NUM_COLS = 4
COL_W = (USABLE_W - COL_GAP * (NUM_COLS - 1)) / NUM_COLS
COL_X = [MARGIN + i * (COL_W + COL_GAP) for i in range(NUM_COLS)]


def _v(overrides: Dict[str, str], key: str, fallback: str = "") -> str:
    return overrides.get(key, fallback)


def _parse_inches(text: str) -> float | None:
    """Parse common architectural dimension formats into inches."""
    s = str(text or "").strip().replace('"', "")
    if not s:
        return None
    try:
        if "'" in s:
            parts = s.split("'", 1)
            feet = float(parts[0].strip() or 0)
            inches = _parse_inches(parts[1].lstrip("-").strip() or "0") or 0.0
            return feet * 12.0 + inches
        if " " in s and "/" in s:
            whole, frac = s.rsplit(" ", 1)
            return float(whole) + float(Fraction(frac))
        if "/" in s:
            return float(Fraction(s))
        if "-" in s:
            left, right = s.split("-", 1)
            if left.strip().replace(".", "", 1).isdigit():
                feet = float(left.strip())
                inches = _parse_inches(right.strip() or "0") or 0.0
                return feet * 12.0 + inches
        return float(s)
    except (ValueError, ZeroDivisionError):
        return None


def _format_arch(inches_value: float) -> str:
    inches_value = max(0.0, float(inches_value))
    feet = int(inches_value // 12.0)
    rem = round(inches_value - (feet * 12.0), 3)
    if abs(rem - round(rem)) < 0.01:
        rem_text = str(int(round(rem)))
    else:
        rem_text = f"{rem:.2f}".rstrip("0").rstrip(".")
    return f"{feet}'-{rem_text}\""


def _draw_arrowhead(c: Canvas, px: float, py: float, dx: float, dy: float, size: float = 4.0) -> None:
    vec_len = (dx * dx + dy * dy) ** 0.5
    if vec_len <= 0.0001:
        return
    ux = dx / vec_len
    uy = dy / vec_len
    perp_x = -uy
    perp_y = ux
    back_x = px - (ux * size)
    back_y = py - (uy * size)
    wing = size * 0.65
    c.line(px, py, back_x + (perp_x * wing), back_y + (perp_y * wing))
    c.line(px, py, back_x - (perp_x * wing), back_y - (perp_y * wing))


def _draw_h_dim(c: Canvas, x1: float, x2: float, y_geom: float, y_dim: float, label: str) -> None:
    ext_gap = 2.0
    dir_sign = 1.0 if y_dim >= y_geom else -1.0
    y_start = y_geom + (dir_sign * ext_gap)
    c.setLineWidth(0.8)
    c.setDash(2, 2)
    c.line(x1, y_start, x1, y_dim)
    c.line(x2, y_start, x2, y_dim)
    c.line(x1, y_dim, x2, y_dim)
    c.setDash()
    _draw_arrowhead(c, x1, y_dim, 1.0, 0.0, 3.5)
    _draw_arrowhead(c, x2, y_dim, -1.0, 0.0, 3.5)
    c.setFont("Helvetica", 6.5)
    c.setFillColorRGB(1, 1, 1)
    label_w = c.stringWidth(label, "Helvetica", 6.5) + 4
    c.rect(((x1 + x2) / 2.0) - (label_w / 2.0), y_dim + 1.5, label_w, 8, stroke=0, fill=1)
    c.setFillColorRGB(*C_VALUE)
    c.drawCentredString((x1 + x2) / 2.0, y_dim + 2.5, label)


def _draw_v_dim(c: Canvas, x_dim: float, y1: float, y2: float, label: str) -> None:
    bottom = min(y1, y2)
    top = max(y1, y2)
    c.setLineWidth(0.8)
    c.setDash(2, 2)
    c.line(x_dim, bottom, x_dim, top)
    c.setDash()
    _draw_arrowhead(c, x_dim, bottom, 0.0, 1.0, 3.5)
    _draw_arrowhead(c, x_dim, top, 0.0, -1.0, 3.5)
    c.saveState()
    c.setFillColorRGB(1, 1, 1)
    c.translate(x_dim + 6, (bottom + top) / 2.0)
    c.rotate(90)
    tw = c.stringWidth(label, "Helvetica", 6.5) + 4
    c.rect(-(tw / 2.0), -2.0, tw, 8, stroke=0, fill=1)
    c.setFillColorRGB(*C_VALUE)
    c.setFont("Helvetica", 6.5)
    c.drawCentredString(0, 0, label)
    c.restoreState()


def _draw_door_elevation(
    c: Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    sheet: FabSheet,
    ov: Dict[str, str],
    points_per_real_inch: float | None = None,
) -> None:
    """Draw a compact door elevation with basic dimension lines."""
    first = sheet.first()
    if not first:
        return

    # Use prefit values as the primary geometry source for this drawing.
    prefit_w_txt = _v(ov, "prep_leaf_w")
    prefit_h_txt = _v(ov, "prep_leaf_h")
    inactive_prefit_w_txt = _v(ov, "inactive_leaf_w")

    frame_w = _parse_inches(_v(ov, "frame_opening_w", first.width))
    active_w = _parse_inches(prefit_w_txt) or _parse_inches(first.active_width) or frame_w or 36.0
    inactive_w = _parse_inches(inactive_prefit_w_txt) or _parse_inches(first.inactive_width) or 0.0
    frame_h = _parse_inches(prefit_h_txt) or _parse_inches(_v(ov, "frame_opening_h", first.height)) or _parse_inches(first.height) or 84.0

    is_pair = inactive_w > 0.0
    total_w = active_w + inactive_w if is_pair else active_w
    if total_w <= 0:
        total_w = 36.0

    lite_w = _parse_inches(_v(ov, "lite_width", "")) or 0.0
    lite_h = _parse_inches(_v(ov, "lite_height", "")) or 0.0
    lock_stile = _parse_inches(_v(ov, "lite_lockstile", "")) or 0.0
    top_rail = _parse_inches(_v(ov, "lite_top_rail", "")) or 0.0

    pad = 8.0
    draw_w_max = max(10.0, w - (2.0 * pad) - 42.0)
    draw_h_max = max(10.0, h - (2.0 * pad) - 20.0)
    if points_per_real_inch and points_per_real_inch > 0:
        # Match Door Elevations PDF scale: 1/4" = 1'-0" (1.5 pt per real inch).
        draw_w = total_w * points_per_real_inch
        draw_h = frame_h * points_per_real_inch
    else:
        scale = min(draw_w_max / total_w, draw_h_max / frame_h)
        draw_w = total_w * scale
        draw_h = frame_h * scale
    draw_x = x + pad + ((draw_w_max - draw_w) / 2.0)
    draw_y = y + pad + 10.0

    if points_per_real_inch and points_per_real_inch > 0:
        c.setFont("Helvetica-Oblique", 6)
        c.setFillColorRGB(*C_LABEL)
        c.drawRightString(x + w - 8, y + h - 10, 'Scale: 1/4" = 1\'-0"')

    c.setStrokeColorRGB(*C_VALUE)
    c.setLineWidth(1.1)
    c.rect(draw_x, draw_y, draw_w, draw_h)

    split_x = None
    if is_pair:
        split_ratio = max(0.15, min(0.85, active_w / total_w))
        split_x = draw_x + (draw_w * split_ratio)
        c.setLineWidth(0.9)
        c.line(split_x, draw_y, split_x, draw_y + draw_h)

    if lite_w > 0 and lite_h > 0 and active_w > 0:
        leaf_left = draw_x
        leaf_right = split_x if split_x is not None else (draw_x + draw_w)
        leaf_w_in = active_w
        leaf_w_pts = leaf_right - leaf_left
        x_scale = leaf_w_pts / max(leaf_w_in, 1.0)
        y_scale = draw_h / max(frame_h, 1.0)
        lite_w_pts = min(lite_w * x_scale, max(2.0, leaf_w_pts - 4.0))
        lite_h_pts = min(lite_h * y_scale, max(2.0, draw_h - 4.0))
        lite_x = leaf_right - (lock_stile * x_scale) - lite_w_pts
        lite_y = (draw_y + draw_h) - (top_rail * y_scale) - lite_h_pts
        lite_x = max(leaf_left + 1.0, min(leaf_right - lite_w_pts - 1.0, lite_x))
        lite_y = max(draw_y + 1.0, min(draw_y + draw_h - lite_h_pts - 1.0, lite_y))

        c.setLineWidth(0.8)
        c.rect(lite_x, lite_y, lite_w_pts, lite_h_pts)

        c.setLineWidth(0.7)
        c.setDash(2, 2)
        cx = lite_x + (lite_w_pts / 2.0)
        cy = lite_y + (lite_h_pts / 2.0)
        c.line(cx, lite_y + 2.0, cx, lite_y + lite_h_pts - 2.0)
        c.setDash()
        _draw_arrowhead(c, cx, lite_y + 2.0, 0.0, -1.0, 2.8)
        _draw_arrowhead(c, cx, lite_y + lite_h_pts - 2.0, 0.0, 1.0, 2.8)
        c.saveState()
        c.setFont("Helvetica", 6)
        c.translate(cx + 4, cy)
        c.rotate(90)
        c.drawCentredString(0, 0, _format_arch(lite_h))
        c.restoreState()

        dim_y = max(draw_y + 2.0, lite_y - 6.0)
        ext_gap = 1.5
        c.setDash(2, 2)
        c.line(lite_x, lite_y - ext_gap, lite_x, dim_y)
        c.line(lite_x + lite_w_pts, lite_y - ext_gap, lite_x + lite_w_pts, dim_y)
        c.line(lite_x, dim_y, lite_x + lite_w_pts, dim_y)
        c.setDash()
        _draw_arrowhead(c, lite_x, dim_y, 1.0, 0.0, 2.8)
        _draw_arrowhead(c, lite_x + lite_w_pts, dim_y, -1.0, 0.0, 2.8)
        c.setFont("Helvetica", 6)
        lw_label = _format_arch(lite_w)
        lw_w = c.stringWidth(lw_label, "Helvetica", 6) + 3
        c.setFillColorRGB(1, 1, 1)
        c.rect(cx - (lw_w / 2.0), dim_y - 5.5, lw_w, 7, stroke=0, fill=1)
        c.setFillColorRGB(*C_VALUE)
        c.drawCentredString(cx, dim_y - 4.0, lw_label)

    # Pair drawing convention: total opening width at top, each leaf at bottom.
    top_total_label = _format_arch(total_w)
    if is_pair:
        _draw_h_dim(c, draw_x, draw_x + draw_w, draw_y + draw_h, draw_y + draw_h + 12.0, top_total_label)
        active_lbl = prefit_w_txt.strip() or _format_arch(active_w)
        inactive_lbl = inactive_prefit_w_txt.strip() or _format_arch(inactive_w)
        _draw_h_dim(c, draw_x, split_x, draw_y, draw_y - 10.0, active_lbl)
        _draw_h_dim(c, split_x, draw_x + draw_w, draw_y, draw_y - 10.0, inactive_lbl)
    else:
        active_lbl = prefit_w_txt.strip() or _format_arch(active_w)
        _draw_h_dim(c, draw_x, draw_x + draw_w, draw_y, draw_y - 10.0, active_lbl)

    # Height always shown from prefit height when available.
    h_lbl = prefit_h_txt.strip() or _format_arch(frame_h)
    _draw_v_dim(c, draw_x + draw_w + 12.0, draw_y, draw_y + draw_h, h_lbl)

    # Hinge locations: dimensioned from top of door to hinge centerlines.
    y_scale = draw_h / max(frame_h, 1.0)
    hinge_vals: list[tuple[float, str]] = []
    for key in ("hinge_d1", "hinge_d2", "hinge_d3", "hinge_d4"):
        raw = _v(ov, key, "").strip()
        parsed = _parse_inches(raw)
        if raw and parsed and parsed > 0:
            hinge_vals.append((parsed, raw))

    hinge_vals.sort(key=lambda x: x[0])
    for i, (hinge_in, hinge_lbl) in enumerate(hinge_vals):
        center_y = (draw_y + draw_h) - (hinge_in * y_scale)
        if center_y < draw_y + 2.0 or center_y > draw_y + draw_h - 2.0:
            continue

        # Hinge center marker at the hinge stile.
        c.setLineWidth(0.9)
        c.line(draw_x, center_y, draw_x + 4.0, center_y)

        # Stagger dimension lines to keep labels legible.
        dim_x = draw_x - 16.0 - (i * 10.0)
        c.setLineWidth(0.7)
        c.setDash(2, 2)
        ext_gap = 1.8
        c.line(draw_x - ext_gap, draw_y + draw_h, dim_x, draw_y + draw_h)
        c.line(draw_x - ext_gap, center_y, dim_x, center_y)
        c.line(dim_x, center_y, dim_x, draw_y + draw_h)
        c.setDash()
        _draw_arrowhead(c, dim_x, draw_y + draw_h, 0.0, -1.0, 2.8)
        _draw_arrowhead(c, dim_x, center_y, 0.0, 1.0, 2.8)

        c.saveState()
        c.setFillColorRGB(1, 1, 1)
        c.translate(dim_x - 4.0, (center_y + draw_y + draw_h) / 2.0)
        c.rotate(90)
        tw = c.stringWidth(hinge_lbl, "Helvetica", 6.0) + 4
        c.rect(-(tw / 2.0), -2.0, tw, 7.0, stroke=0, fill=1)
        c.setFillColorRGB(*C_VALUE)
        c.setFont("Helvetica", 6.0)
        c.drawCentredString(0, 0, hinge_lbl)
        c.restoreState()


def _draw_elevation_section(
    c: Canvas,
    x: float,
    top_y: float,
    bottom_y: float,
    w: float,
    sheet: FabSheet,
    ov: Dict[str, str],
) -> None:
    """Draw lower-right elevation panel with fixed 1/4" scale."""
    if top_y - bottom_y < 64:
        return

    c.setFont("Helvetica-Bold", F_SECTION)
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(*C_TITLE_BG)
    c.rect(x, top_y - LINE_H, w, LINE_H, fill=1)
    c.setFillColorRGB(*C_TITLE_FG)
    c.drawString(x + 4, top_y - LINE_H + 3, "DOOR ELEVATION")

    content_top = top_y - LINE_H - 4
    content_bottom = bottom_y + 4
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, bottom_y, w, top_y - bottom_y)
    _draw_door_elevation(
        c,
        x + 4,
        content_bottom,
        w - 8,
        max(20.0, content_top - content_bottom),
        sheet,
        ov,
        points_per_real_inch=72.0 / 48.0,
    )


def _merged_overrides(sheet: FabSheet, field_overrides: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    overrides = dict(field_overrides or {})
    # Auto-populate from prep code database for fields not already overridden.
    try:
        from core.prep_codes import PrepCodeDB
        db = PrepCodeDB.load_default()
        auto = db.resolve_for_fab_sheet(sheet.prep_string)
        for k, v in auto.items():
            if k not in overrides:
                overrides[k] = v
    except Exception:
        pass
    return overrides


# ── Public entry point ──────────────────────────────────────────────

def render_fab_sheet_pdf(
    output_path: str,
    sheet: FabSheet,
    job_name: str = "",
    field_overrides: Optional[Dict[str, str]] = None,
) -> None:
    """Render *sheet* to one or more landscape PDF pages at *output_path*."""
    overrides = _merged_overrides(sheet, field_overrides)
    c = Canvas(output_path, pagesize=landscape(letter))
    start_idx = 0
    page_no = 1
    while True:
        next_idx = _draw_page(c, sheet, job_name, overrides, start_idx, page_no)
        if next_idx >= len(sheet.openings):
            break
        c.showPage()
        start_idx = next_idx
        page_no += 1
    c.save()


def render_fab_sheets_pdf(
    output_path: str,
    sheets: List[FabSheet],
    job_name: str = "",
    overrides_by_index: Optional[Dict[int, Dict[str, str]]] = None,
) -> None:
    """Render multiple sheets into a single multi-page landscape PDF."""
    c = Canvas(output_path, pagesize=landscape(letter))
    all_overrides = overrides_by_index or {}
    first_page = True
    for i, sheet in enumerate(sheets):
        ov = _merged_overrides(sheet, all_overrides.get(i, {}))
        start_idx = 0
        page_no = 1
        while True:
            if not first_page:
                c.showPage()
            next_idx = _draw_page(c, sheet, job_name, ov, start_idx, page_no)
            first_page = False
            if next_idx >= len(sheet.openings):
                break
            start_idx = next_idx
            page_no += 1
    c.save()


# ── Drawing helpers ─────────────────────────────────────────────────

def _draw_page(
    c: Canvas,
    sheet: FabSheet,
    job_name: str,
    ov: Dict[str, str],
    opening_start_idx: int,
    page_no: int,
) -> int:
    first = sheet.first()

    # ── BACKGROUND ──────────────────────────────────────────────────
    c.setFillColorRGB(*C_BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # ── COMPANY LOGO (top-left) ─────────────────────────────────────
    y = PAGE_H - MARGIN
    logo_path = Path.home() / ".goro" / "company_logo.png"
    logo_h = 40
    if logo_path.exists():
        try:
            img = ImageReader(str(logo_path))
            iw, ih = img.getSize()
            max_w, max_h = 150, logo_h
            scale = min(max_w / iw, max_h / ih, 1.0)
            dw, dh = iw * scale, ih * scale
            c.drawImage(img, MARGIN, y - dh, dw, dh, mask="auto")
        except Exception:
            pass

    # ── TITLE ───────────────────────────────────────────────────────
    c.setFillColorRGB(*C_VALUE)
    c.setFont("Helvetica-Bold", F_TITLE)
    c.drawString(MARGIN + 160, y - 14, "DOOR MACHINING SHEET")
    c.setFont("Helvetica", F_LABEL)
    c.setFillColorRGB(*C_LABEL)
    continuation = "" if page_no == 1 else f"  |  CONTINUATION PAGE {page_no}"
    c.drawString(MARGIN + 160, y - 28, f"{sheet.key.label()}  |  {len(sheet.openings)} opening(s){continuation}")

    # Job name / number
    c.setFont("Helvetica-Bold", F_LABEL)
    c.setFillColorRGB(*C_LABEL)
    c.drawString(PAGE_W - MARGIN - 250, y - 8, "JOB NAME:")
    c.setFont("Helvetica", F_VALUE)
    c.setFillColorRGB(*C_VALUE)
    c.drawString(PAGE_W - MARGIN - 190, y - 8, _v(ov, "job_name", job_name))
    c.setFont("Helvetica-Bold", F_LABEL)
    c.setFillColorRGB(*C_LABEL)
    c.drawString(PAGE_W - MARGIN - 250, y - 20, "JOB NUMBER:")
    c.setFont("Helvetica", F_VALUE)
    c.setFillColorRGB(*C_VALUE)
    c.drawString(PAGE_W - MARGIN - 190, y - 20, _v(ov, "job_number"))

    # ── SUMMARY CARDS ──────────────────────────────────────────────
    y -= logo_h + 10
    card_gap = 8
    left_card_w = USABLE_W * 0.62
    right_card_w = USABLE_W - left_card_w - card_gap

    # Compute card height: use two columns for details if > 6 entries
    door_details = first.door_details if first else {}
    detail_line_h = 8
    detail_top_offset = 28  # space for title
    detail_bottom_pad = 8
    detail_items = list(door_details.items())
    num_details = len(detail_items)
    use_two_cols = num_details > 6
    if use_two_cols:
        rows_per_col = (num_details + 1) // 2  # ceil division
    else:
        rows_per_col = num_details
    min_card_h = 76
    needed_details_h = detail_top_offset + rows_per_col * detail_line_h + detail_bottom_pad
    card_h = max(min_card_h, needed_details_h)

    # Project summary card
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(MARGIN, y - card_h, left_card_w, card_h, 5, fill=1, stroke=1)

    c.setFont("Helvetica-Bold", F_LABEL)
    c.setFillColorRGB(*C_LABEL)
    c.drawString(MARGIN + 8, y - 16, "DOOR TYPE")
    c.drawString(MARGIN + 170, y - 16, "FRAME OPENING")
    c.drawString(MARGIN + 340, y - 16, "PREFIT LEAF")
    c.drawString(MARGIN + 470, y - 16, "FIRE")
    c.drawString(MARGIN + 530, y - 16, "STC")
    c.drawString(MARGIN + 580, y - 16, "ELEV")

    fw = _v(ov, "frame_opening_w", first.width if first else "")
    fh = _v(ov, "frame_opening_h", first.height if first else "")
    c.setFont("Helvetica", F_VALUE)
    c.setFillColorRGB(*C_VALUE)
    c.drawString(MARGIN + 8, y - 30, sheet.door_type)
    c.drawString(MARGIN + 170, y - 30, f"{fw} x {fh}")
    c.drawString(MARGIN + 340, y - 30, f"{_v(ov, 'prep_leaf_w')} x {_v(ov, 'prep_leaf_h')}")
    c.drawString(MARGIN + 470, y - 30, _v(ov, "fire_rating", first.rating_fire if first else ""))
    c.drawString(MARGIN + 530, y - 30, _v(ov, "stc_rating", first.stc if first else ""))
    c.drawString(MARGIN + 580, y - 30, first.elevation if first else "")

    inact_w = _v(ov, "inactive_leaf_w")
    inact_h = _v(ov, "inactive_leaf_h")
    if inact_w or inact_h:
        c.setFont("Helvetica-Bold", F_LABEL)
        c.setFillColorRGB(*C_LABEL)
        c.drawString(MARGIN + 8, y - 50, "INACTIVE PREFIT")
        c.setFont("Helvetica", F_VALUE)
        c.setFillColorRGB(*C_VALUE)
        c.drawString(MARGIN + 98, y - 50, f"{inact_w} x {inact_h}")

    if first and first.inactive_elevation:
        c.setFont("Helvetica-Bold", F_LABEL)
        c.setFillColorRGB(*C_LABEL)
        c.drawString(MARGIN + 470, y - 50, "INACTIVE ELEV")
        c.setFont("Helvetica", F_VALUE)
        c.setFillColorRGB(*C_VALUE)
        c.drawString(MARGIN + 548, y - 50, first.inactive_elevation)

    # Door details card
    details_x = MARGIN + left_card_w + card_gap
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(details_x, y - card_h, right_card_w, card_h, 5, fill=1, stroke=1)

    c.setFont("Helvetica-Bold", F_LABEL)
    c.setFillColorRGB(*C_LABEL)
    c.drawString(details_x + 8, y - 16, "DOOR TAB DETAILS")
    c.setFont("Helvetica", 6.5)
    c.setFillColorRGB(*C_VALUE)
    dy = y - 28
    if use_two_cols:
        col2_x = details_x + right_card_w * 0.5
        for i, (label_text, val) in enumerate(detail_items):
            if i < rows_per_col:
                c.drawString(details_x + 8, dy - i * detail_line_h, f"{label_text}: {val}")
            else:
                c.drawString(col2_x, dy - (i - rows_per_col) * detail_line_h, f"{label_text}: {val}")
    else:
        for label_text, val in detail_items:
            c.drawString(details_x + 8, dy, f"{label_text}: {val}")
            dy -= detail_line_h

    # Horizontal separator
    y -= card_h + 10
    c.setStrokeColorRGB(*C_BORDER)
    c.line(MARGIN, y, PAGE_W - MARGIN, y)
    y -= 6

    body_top = y

    # ── COLUMN 1: Hinges + Lock + Light/Louver ─────────────────────
    y = body_top
    y = _draw_section(c, "HINGES", COL_X[0], y, COL_W, [
        ("Type", _v(ov, "hinge_type")),
        ("Template No.", _v(ov, "hinge_template")),
        ("Size", _v(ov, "hinge_size")),
        ("Hinge Backset", _v(ov, "hinge_backset")),
        ("Spec", _v(ov, "hinge_manufacturer")),
        ("Hinge 1", _v(ov, "hinge_d1")),
        ("Hinge 2", _v(ov, "hinge_d2")),
        ("Hinge 3", _v(ov, "hinge_d3")),
        ("Hinge 4", _v(ov, "hinge_d4")),
        ("WIRE CHASE", _v(ov, "wire_chase") or "No"),
    ])
    y -= 6
    y = _draw_section(c, "LOCK", COL_X[0], y, COL_W, [
        ("Type", _v(ov, "lock_type")),
        ("Lockstyle", _v(ov, "lock_lockstyle")),
        ("Description", _v(ov, "lock_description")),
        ("Template No.", _v(ov, "lock_template")),
        ("Top to Center of Lock", _v(ov, "lock_center")),
        ("Lock Backset", _v(ov, "lock_backset")),
        ("Top to Center of Strike", _v(ov, "lock_strike_center")),
    ])
    y -= 6
    y = _draw_section(c, "LIGHT OR LOUVER", COL_X[0], y, COL_W, [
        ("KIT", _v(ov, "lite_kit")),
        ("GLASS THICKNESS", _v(ov, "lite_glass_thickness")),
        ("Size W", _v(ov, "lite_width")),
        ("Size H", _v(ov, "lite_height")),
        ("LOCKSTILE", _v(ov, "lite_lockstile")),
        ("TOP RAIL", _v(ov, "lite_top_rail")),
        ("BOTTOM RAIL", _v(ov, "lite_bottom_rail")),
        ("FACTORY GLAZE", _v(ov, "lite_factory_glaze")),
    ])

    # ── COLUMN 2: Machining Specs ───────────────────────────────────
    y = body_top
    _y_mach = _draw_section(c, "MACHINING SPECS", COL_X[1], y, COL_W, [
        ("STRIKE - TEMP.", _v(ov, "mach_strike_temp")),
        ("STRIKE TEMPLATE", _v(ov, "mach_strike_temp_tmpl")),
        ("FLUSHBOLT", _v(ov, "mach_flushbolt")),
        ("FLUSHBOLT TEMPLATE", _v(ov, "mach_flushbolt_tmpl")),
        ("OVERHEAD STOP", _v(ov, "mach_overhead_stop")),
        ("OH STOP TEMPLATE", _v(ov, "mach_overhead_stop_tmpl")),
        ("DOOR BOTTOM", _v(ov, "mach_door_bottom")),
        ("DB TEMPLATE", _v(ov, "mach_door_bottom_tmpl")),
    ])
    _draw_section(c, "NOTES / OTHER HARDWARE", COL_X[1], _y_mach - 4, COL_W, [
        ("1", _v(ov, "other_hw")),
        ("2", _v(ov, "other_hw_2")),
        ("3", _v(ov, "other_hw_3")),
    ])

    # ── TOP-RIGHT: Openings list (multi-column) ─────────────────────
    openings_top = body_top
    openings_bottom = body_top - 150
    next_idx = _draw_openings_panel(
        c,
        sheet,
        opening_start_idx,
        COL_X[2],
        openings_top,
        openings_bottom,
        (COL_W * 2.0) + COL_GAP,
    )

    # ── LOWER-RIGHT: Door Elevation panel (large, to-scale) ────────
    elev_top = openings_bottom - 8
    elev_bottom = MARGIN + 12
    _draw_elevation_section(
        c,
        COL_X[2],
        elev_top,
        elev_bottom,
        (COL_W * 2.0) + COL_GAP,
        sheet,
        ov,
    )

    # ── Footer ──────────────────────────────────────────────────────
    c.setFillColorRGB(*C_LABEL)
    c.setFont("Helvetica", 6)
    today = datetime.now().strftime("%m/%d/%Y")
    c.drawString(MARGIN, MARGIN - 10, f"Generated by GORO  |  {today}  |  {sheet.key.label()}")
    if next_idx < len(sheet.openings):
        c.drawRightString(
            PAGE_W - MARGIN,
            MARGIN - 10,
            f"Showing {opening_start_idx + 1}-{next_idx} of {len(sheet.openings)} openings  |  Continue on next page",
        )
    else:
        c.drawRightString(PAGE_W - MARGIN, MARGIN - 10, f"Total doors: {len(sheet.openings)}")

    return next_idx


def _wrap_text(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    """Split *text* into lines that fit within *max_width*."""
    from reportlab.lib.utils import simpleSplit
    return simpleSplit(text, font_name, font_size, max_width)


def _draw_section(
    c: Canvas,
    title: str,
    x: float,
    y: float,
    w: float,
    rows: list[tuple[str, str]],
) -> float:
    """Draw a titled section box; returns y after the section."""
    # Title bar
    c.setFont("Helvetica-Bold", F_SECTION)
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(*C_TITLE_BG)
    c.rect(x, y - LINE_H, w, LINE_H, fill=1)
    c.setFillColorRGB(*C_TITLE_FG)
    c.drawString(x + 4, y - LINE_H + 3, title)
    y -= LINE_H

    # Rows – wrap long values across multiple lines
    font_name = "Helvetica"
    c.setFont(font_name, F_LABEL)
    val_x = x + w * 0.48
    val_max_w = w * 0.52 - 8  # available width for value text
    total_lines = 0
    for label, value in rows:
        y -= LINE_H
        total_lines += 1
        c.setFillColorRGB(*C_LABEL)
        c.drawString(x + 4, y + 3, f"{label}:")
        c.setFillColorRGB(*C_VALUE)
        val_str = str(value)
        wrapped = _wrap_text(val_str, font_name, F_LABEL, val_max_w)
        if not wrapped:
            wrapped = [""]
        c.drawString(val_x, y + 3, wrapped[0])
        # Underline first line
        c.setStrokeColorRGB(0.88, 0.89, 0.92)
        c.line(val_x, y, x + w - 4, y)
        # Draw continuation lines
        for extra_line in wrapped[1:]:
            y -= LINE_H
            total_lines += 1
            c.setFillColorRGB(*C_VALUE)
            c.drawString(val_x, y + 3, extra_line)
            c.setStrokeColorRGB(0.88, 0.89, 0.92)
            c.line(val_x, y, x + w - 4, y)

    # Border
    section_h = (total_lines + 1) * LINE_H
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, y, w, section_h)

    return y


def _draw_door_number_grid(
    c: Canvas,
    sheet: FabSheet,
    x: float,
    y: float,
    w: float,
) -> float:
    """Draw the door-number grid with opening and handing columns."""
    # Title bar
    c.setFont("Helvetica-Bold", F_SECTION)
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(*C_TITLE_BG)
    c.rect(x, y - LINE_H, w, LINE_H, fill=1)
    c.setFillColorRGB(*C_TITLE_FG)
    c.drawString(x + 4, y - LINE_H + 3, "DOOR NO.")
    y -= LINE_H

    # Total
    y -= LINE_H
    c.setFont("Helvetica-Bold", F_LABEL)
    c.setFillColorRGB(*C_TITLE_FG)
    c.drawString(x + 4, y + 3, f"TOTAL DOORS THIS PAGE: {len(sheet.openings)}")

    # Column headers
    y -= LINE_H
    c.setFont("Helvetica-Bold", F_LABEL)
    c.setFillColorRGB(*C_LABEL)
    col_num_w = 18
    col_open_x = x + col_num_w
    col_hand_x = x + w * 0.65
    c.drawString(x + 4, y + 3, "#")
    c.drawString(col_open_x, y + 3, "OPENING")
    c.drawString(col_hand_x, y + 3, "HANDING")
    c.setStrokeColorRGB(*C_BORDER)
    c.line(x, y, x + w, y)

    display_rows = min(len(sheet.openings), 15)

    c.setFont("Helvetica", F_VALUE)
    for i in range(display_rows):
        o = sheet.openings[i]
        y -= LINE_H
        c.setFillColorRGB(*C_LABEL)
        c.drawString(x + 4, y + 3, str(i + 1))
        c.setFillColorRGB(*C_VALUE)
        c.drawString(col_open_x, y + 3, o.opening_number)
        c.drawString(col_hand_x, y + 3, o.handing)
        # Row line
        c.setStrokeColorRGB(0.9, 0.91, 0.94)
        c.line(x, y, x + w, y)

    # Border around entire grid
    grid_h = (display_rows + 3) * LINE_H
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, y, w, grid_h)

    return y


def _draw_openings_panel(
    c: Canvas,
    sheet: FabSheet,
    start_idx: int,
    x: float,
    top_y: float,
    bottom_y: float,
    w: float,
) -> int:
    """Draw a large multi-column openings list and return next opening index."""
    if start_idx >= len(sheet.openings):
        return start_idx

    c.setFont("Helvetica-Bold", F_SECTION)
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(*C_TITLE_BG)
    c.rect(x, top_y - LINE_H, w, LINE_H, fill=1)
    c.setFillColorRGB(*C_TITLE_FG)
    c.drawString(x + 4, top_y - LINE_H + 3, "OPENINGS")

    body_top = top_y - LINE_H
    body_h = max(50.0, body_top - bottom_y)
    c.setStrokeColorRGB(*C_BORDER)
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, bottom_y, w, body_h)

    # Handing summary across the whole sheet.
    handing_counts: Dict[str, int] = {}
    for o in sheet.openings:
        hand = str(o.handing or "").strip().upper() or "(BLANK)"
        handing_counts[hand] = handing_counts.get(hand, 0) + 1
    summary_parts = [f"{k}: {v}" for k, v in sorted(handing_counts.items())]
    summary_text = "  |  ".join(summary_parts) if summary_parts else "No handing values"
    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColorRGB(*C_TITLE_FG)
    c.drawString(x + 4, body_top - 9, f"COUNT BY HANDING: {summary_text}")

    col_gap = 8.0
    col_count = max(2, min(4, int((w + col_gap) // 120.0)))
    col_w = (w - ((col_count - 1) * col_gap)) / col_count

    row_h = 10.0
    header_h = row_h
    top_pad = 16.0
    bot_pad = 4.0
    rows_per_col = int((body_h - top_pad - bot_pad - header_h) // row_h)
    rows_per_col = max(4, rows_per_col)

    c.setFont("Helvetica-Bold", 6.5)
    c.setFillColorRGB(*C_LABEL)
    for col in range(col_count):
        cx = x + (col * (col_w + col_gap))
        hy = body_top - top_pad - header_h + 2
        c.drawString(cx + 2, hy, "#")
        c.drawString(cx + 14, hy, "OPENING")
        c.drawString(cx + col_w * 0.68, hy, "HANDING")
        c.setStrokeColorRGB(0.88, 0.89, 0.92)
        c.line(cx, body_top - top_pad - header_h, cx + col_w, body_top - top_pad - header_h)

    current = start_idx
    c.setFont("Helvetica", 6.5)
    for col in range(col_count):
        cx = x + (col * (col_w + col_gap))
        for r in range(rows_per_col):
            if current >= len(sheet.openings):
                break
            o = sheet.openings[current]
            y = body_top - top_pad - header_h - ((r + 1) * row_h) + 2
            c.setFillColorRGB(*C_LABEL)
            c.drawString(cx + 2, y, str(current + 1))
            c.setFillColorRGB(*C_VALUE)
            c.drawString(cx + 14, y, str(o.opening_number or ""))
            c.drawString(cx + col_w * 0.68, y, str(o.handing or ""))
            c.setStrokeColorRGB(0.93, 0.94, 0.96)
            c.line(cx, y - 1.5, cx + col_w, y - 1.5)
            current += 1

    shown = max(0, current - start_idx)
    c.setFont("Helvetica", 6)
    c.setFillColorRGB(*C_LABEL)
    c.drawRightString(x + w - 4, bottom_y + 2, f"Showing {shown} openings on this page")
    return current
