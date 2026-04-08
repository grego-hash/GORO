"""
Generate OCTO logo splash – 1280×720 MP4.

Two interlocking C-shaped lobes forming an infinity/figure-8 symbol,
drawn as a continuous orbit, then 'OCTO' text fades in below.
Matches the actual OCTO logo: round circular C-lobes with the
lower-left → upper-right crossing strand on top.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math
import os

# ── Configuration ─────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 30
BG       = (10, 10, 10)         # #0A0A0A
TEAL     = (14, 123, 142)       # logo teal  (#0E7B8E)

CX, CY   = WIDTH // 2, HEIGHT // 2 - 40
R         = 135                  # lobe radius (px)
D         = 135                  # half-distance between circle centres
STROKE    = 48                   # line width
GAP_DEG   = 35                   # half-gap of each C (degrees)

N_ARC     = 300                  # points per C-arc
N_CROSS   = 80                   # points per crossing curve

TRACE_FR  = 60                   # 2.0 s draw
TEXT_FR   = 12                   # 0.4 s text fade
HOLD_FR   = 30                   # 1.0 s hold
TOTAL_FR  = TRACE_FR + TEXT_FR + HOLD_FR

FONT_SZ   = 66
TRACKING  = 18
TEXT_Y_OFF = 70                  # px below bottom of infinity

OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "splash.mp4",
)

# ── Font ──────────────────────────────────────────────────────

def _font(sz):
    for p in (
        r"C:\Windows\Fonts\ARLRDBD.TTF",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ):
        if os.path.isfile(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

FONT = _font(FONT_SZ)

# ── Geometry helpers ──────────────────────────────────────────

def _pt(cx, cy, r, deg):
    """Screen-space point on circle at angle *deg* (math CCW from east)."""
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy - r * math.sin(a))


def _bezier(p0, p1, p2, p3, n):
    """Cubic Bézier with *n* samples."""
    pts = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0
        u = 1 - t
        x = u**3*p0[0] + 3*u**2*t*p1[0] + 3*u*t**2*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u**2*t*p1[1] + 3*u*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts


# ── Build continuous figure-8 path from two C-arcs + crossings ──

def _build_path():
    """
    Path order (continuous orbit):
      Seg 1 – Right C arc   (CW,  290° of arc)
      Seg 2 – Crossing 1    (under strand, lower-right → upper-left)
      Seg 3 – Left C arc    (CCW, 290° of arc)
      Seg 4 – Crossing 2    (OVER strand, lower-left → upper-right)
    """
    g   = GAP_DEG
    cxl = CX - D
    cxr = CX + D
    arc = 360 - 2 * g           # arc span of each C-shape (degrees)

    sg = math.sin(math.radians(g))
    cg = math.cos(math.radians(g))
    CP = 0.45                    # bezier control-point distance scale

    path = []

    # ── Seg 1: Right C (gap faces LEFT, arc CW from top-left to bottom-left)
    for i in range(N_ARC):
        t = i / (N_ARC - 1)
        angle = (180 - g) - t * arc          # 145° → −145°
        path.append(_pt(cxr, CY, R, angle))

    # ── Seg 2: Crossing 1  (UNDER – from bottom-left of right C → top-right of left C)
    A = path[-1]
    B = _pt(cxl, CY, R, g)
    tan_ab = (-R * sg, -R * cg)              # shared tangent direction (left, up)
    P1 = (A[0] + CP * tan_ab[0], A[1] + CP * tan_ab[1])
    P2 = (B[0] - CP * tan_ab[0], B[1] - CP * tan_ab[1])
    path.extend(_bezier(A, P1, P2, B, N_CROSS))

    # ── Seg 3: Left C (gap faces RIGHT, arc CCW from top-right to bottom-right)
    for i in range(N_ARC):
        t = i / (N_ARC - 1)
        angle = g + t * arc                  # 35° → 325°
        path.append(_pt(cxl, CY, R, angle))

    # ── Seg 4: Crossing 2  (OVER – from bottom-right of left C → top-left of right C)
    c2s = len(path)
    C  = path[-1]
    E  = _pt(cxr, CY, R, 180 - g)
    tan_ce = (R * sg, -R * cg)               # shared tangent direction (right, up)
    P1 = (C[0] + CP * tan_ce[0], C[1] + CP * tan_ce[1])
    P2 = (E[0] - CP * tan_ce[0], E[1] - CP * tan_ce[1])
    path.extend(_bezier(C, P1, P2, E, N_CROSS))
    c2e = len(path)

    return path, c2s, c2e


PATH, C2S, C2E = _build_path()

BG_BGR   = BG[::-1]
TEAL_BGR = TEAL[::-1]

# ── Drawing helpers ───────────────────────────────────────────

def _poly(img, pts, clr=None, th=STROKE):
    if len(pts) < 2:
        return
    clr = clr or TEAL_BGR
    a = np.array([(int(round(x)), int(round(y))) for x, y in pts], np.int32)
    cv2.polylines(img, [a], False, clr, th, cv2.LINE_AA)


def _cap(img, pt, clr=None, r=STROKE // 2):
    clr = clr or TEAL_BGR
    cv2.circle(img, (int(round(pt[0])), int(round(pt[1]))),
               r, clr, -1, cv2.LINE_AA)


def _text(img_bgr, alpha):
    pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    d   = ImageDraw.Draw(pil)
    txt = "OCTO"
    c   = tuple(int(BG[i] + (TEAL[i] - BG[i]) * alpha) for i in range(3))
    ws  = []
    for ch in txt:
        bb = d.textbbox((0, 0), ch, font=FONT)
        ws.append(bb[2] - bb[0])
    tw = sum(ws) + TRACKING * (len(txt) - 1)
    ty = CY + R + TEXT_Y_OFF
    x  = (WIDTH - tw) // 2
    for i, ch in enumerate(txt):
        bb = d.textbbox((0, 0), ch, font=FONT)
        d.text((x - bb[0], ty - bb[1]), ch, font=FONT, fill=c)
        x += ws[i] + TRACKING
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


# ── Frame renderer ────────────────────────────────────────────

def _render(progress, text_alpha):
    img = np.full((HEIGHT, WIDTH, 3), BG_BGR, dtype=np.uint8)
    n   = len(PATH)
    nd  = max(0, min(int(progress * n), n))

    if nd >= 2:
        _poly(img, PATH[:nd])
        _cap(img, PATH[0])
        _cap(img, PATH[nd - 1])

        # Redraw OVER crossing on top once it has been traced
        if nd > C2E:
            PAD = 8
            lo = max(0, C2S - PAD)
            hi = min(n, C2E + PAD)
            _poly(img, PATH[lo:hi])

    if text_alpha > 0:
        img = _text(img, text_alpha)

    return img


# ── Main ──────────────────────────────────────────────────────

def main():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

    w = cv2.VideoWriter(
        OUTPUT, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT),
    )
    if not w.isOpened():
        raise RuntimeError(f"Cannot create {OUTPUT}")

    for f in range(TOTAL_FR):
        if f < TRACE_FR:
            p  = f / max(TRACE_FR - 1, 1)
            ta = 0.0
        elif f < TRACE_FR + TEXT_FR:
            p  = 1.0
            ta = (f - TRACE_FR) / max(TEXT_FR - 1, 1)
        else:
            p  = 1.0
            ta = 1.0

        w.write(_render(p, ta))

    w.release()
    print(f"OK  {TOTAL_FR} frames ({TOTAL_FR / FPS:.1f}s)  →  {OUTPUT}")


if __name__ == "__main__":
    main()
