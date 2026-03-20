"""Poppler utility functions for PDF processing."""

import os
import sys
from pathlib import Path


def _has_pdfinfo(bin_dir: Path) -> bool:
    exe_name = "pdfinfo.exe" if os.name == "nt" else "pdfinfo"
    return (bin_dir / exe_name).is_file()


def _find_poppler_bin(base_dir: Path) -> str | None:
    if not base_dir.exists() or not base_dir.is_dir():
        return None

    # Common layouts first
    common_candidates = [
        base_dir / "Library" / "bin",
        base_dir / "bin",
    ]
    for candidate in common_candidates:
        if _has_pdfinfo(candidate):
            return str(candidate)

    # Fallback: search for pdfinfo binary under the directory tree
    exe_name = "pdfinfo.exe" if os.name == "nt" else "pdfinfo"
    for exe_path in base_dir.rglob(exe_name):
        if exe_path.is_file():
            return str(exe_path.parent)

    return None


def get_poppler_path():
    """
    Get the path to Poppler.
    
    Returns:
        str: Path to poppler bin directory, or None if not found.
        
    Poppler location priority:
    1. Bundled with application (PyInstaller bundle)
    2. System PATH
    """
    env_path = os.environ.get("POPPLER_PATH", "").strip()
    if env_path:
        resolved = _find_poppler_bin(Path(env_path))
        if resolved:
            return resolved

    # When bundled with PyInstaller
    if getattr(sys, 'frozen', False):
        app_path = Path(sys._MEIPASS)  # type: ignore  # PyInstaller temp folder
        resolved = _find_poppler_bin(app_path / "poppler")
        if resolved:
            return resolved
    
    # Check relative to GORO.exe if running as executable
    if getattr(sys, 'frozen', False):
        exe_path = Path(sys.executable).parent
        resolved = _find_poppler_bin(exe_path / "poppler")
        if resolved:
            return resolved
    
    # Development environment: check for bundled poppler in tools directory
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    resolved = _find_poppler_bin(project_root / "tools" / "poppler-windows")
    if resolved:
        return resolved
    
    # Fall back to system PATH (user must have installed manually)
    return None


def configure_pdf2image():
    """
    Configure pdf2image to use bundled Poppler.
    
    Call this before importing or using pdf2image.convert_from_path()
    """
    poppler_path = get_poppler_path()
    if poppler_path:
        os.environ['POPPLER_PATH'] = poppler_path


if __name__ == "__main__":
    # Debug: print poppler path
    path = get_poppler_path()
    if path:
        print(f"Poppler found at: {path}")
    else:
        print("Poppler not found. Install it or add it to PATH.")
