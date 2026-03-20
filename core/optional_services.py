"""Optional runtime services and dependency bootstrap for GORO."""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from core.utils import get_system


# Windows recycle bin function using native API (avoids WMI issues)
def send_to_recycle_bin(path):
    """Send file or folder to Windows recycle bin using shell API."""
    import ctypes
    from ctypes import Structure, c_uint, c_void_p, c_wchar_p, windll

    class SHFILEOPSTRUCT(Structure):
        _fields_ = [
            ("hwnd", c_void_p),
            ("wFunc", c_uint),
            ("pFrom", c_wchar_p),
            ("pTo", c_wchar_p),
            ("fFlags", c_uint),
            ("fAnyOperationsAborted", c_uint),
            ("hNameMappings", c_void_p),
            ("lpszProgressTitle", c_wchar_p),
        ]

    FO_DELETE = 0x0003
    FOF_ALLOWUNDO = 0x0040
    FOF_NOCONFIRMATION = 0x0010
    FOF_SILENT = 0x0004

    p_from = str(path) + "\0"

    fileop = SHFILEOPSTRUCT()
    fileop.hwnd = None
    fileop.wFunc = FO_DELETE
    fileop.pFrom = p_from
    fileop.pTo = None
    fileop.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
    fileop.fAnyOperationsAborted = 0
    fileop.hNameMappings = None
    fileop.lpszProgressTitle = None

    result = windll.shell32.SHFileOperationW(ctypes.byref(fileop))
    if result != 0:
        raise Exception(f"SHFileOperation failed with code {result}")


send2trash = send_to_recycle_bin
HAS_SEND2TRASH = True


try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except Exception:
    pdfplumber = None
    HAS_PDFPLUMBER = False

try:
    from pdf2image import convert_from_path
    import pytesseract
    from PIL import Image, ImageDraw

    HAS_OCR = True
except Exception:
    convert_from_path = None
    pytesseract = None
    Image = None
    ImageDraw = None
    HAS_OCR = False

try:
    from reportlab.lib import colors
    from reportlab.lib import pagesizes, units
    from reportlab.lib.utils import ImageReader, simpleSplit
    from reportlab.pdfgen import canvas

    letter = pagesizes.letter
    inch = units.inch

    HAS_REPORTLAB = True
except Exception:
    colors = None
    letter = None
    inch = None
    ImageReader = None
    simpleSplit = None
    canvas = None
    HAS_REPORTLAB = False

try:
    from PyPDF2 import PdfMerger

    HAS_PYPDF2 = True
except Exception:
    try:
        from pypdf import PdfMerger

        HAS_PYPDF2 = True
    except Exception:
        try:
            from pypdf import PdfWriter as _PdfWriter

            class PdfMerger:
                def __init__(self):
                    self._writer = _PdfWriter()

                def append(self, file_path):
                    self._writer.append(file_path)

                def write(self, output_path):
                    with open(output_path, "wb") as out_file:
                        self._writer.write(out_file)

                def close(self):
                    return None

            HAS_PYPDF2 = True
        except Exception:
            PdfMerger = None
            HAS_PYPDF2 = False


def get_bundled_tesseract_root() -> Optional[Path]:
    candidates: List[Path] = []

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.extend([
            exe_dir / "tesseract-ocr",
            exe_dir / "tesseract",
        ])

    project_root = Path(__file__).resolve().parent.parent
    candidates.extend([
        project_root / "tools" / "tesseract-ocr",
        project_root / "tools" / "tesseract",
    ])

    for candidate in candidates:
        if (candidate / "tesseract.exe").is_file():
            return candidate

    return None


def resolve_tesseract_path(settings=None) -> Optional[str]:
    candidates: List[str] = []

    try:
        if settings is not None:
            configured_path = settings.value("tesseract_path", "", type=str)
            if configured_path:
                candidates.append(configured_path.strip())
    except Exception:
        pass

    bundled_root = get_bundled_tesseract_root()
    if bundled_root is not None:
        candidates.append(str(bundled_root / "tesseract.exe"))

    env_goro = os.environ.get("GORO_TESSERACT_PATH", "").strip()
    if env_goro:
        candidates.append(env_goro)

    env_tesseract_cmd = os.environ.get("TESSERACT_CMD", "").strip()
    if env_tesseract_cmd:
        candidates.append(env_tesseract_cmd)

    path_tesseract = shutil.which("tesseract")
    if path_tesseract:
        candidates.append(path_tesseract)

    if get_system() == "Windows":
        candidates.extend(
            [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
        )

    for candidate in candidates:
        if not candidate:
            continue

        expanded = os.path.expandvars(os.path.expanduser(candidate.strip().strip('"')))
        if not expanded:
            continue

        if os.path.isabs(expanded) and os.path.isfile(expanded):
            return expanded

        resolved = shutil.which(expanded)
        if resolved:
            return resolved

        rel_path = Path(expanded)
        if rel_path.is_file():
            return str(rel_path.resolve())

    return None


def configure_tesseract(settings=None) -> bool:
    if not HAS_OCR or pytesseract is None:
        return False

    try:
        tesseract_path = resolve_tesseract_path(settings)
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

            tesseract_root = Path(tesseract_path).resolve().parent
            tessdata_dir = tesseract_root / "tessdata"
            if tessdata_dir.is_dir():
                os.environ["TESSDATA_PREFIX"] = str(tesseract_root)

            return True
    except Exception:
        pass

    return False

