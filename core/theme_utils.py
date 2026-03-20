import json
from typing import Optional

from PyQt6.QtCore import QSettings


def load_custom_theme(settings: QSettings) -> Optional[dict]:
    raw = settings.value("custom_themes", "")
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return None
        name = settings.value("custom_theme_name", "")
        if not name or name not in data:
            return None
        theme = data[name]
        return theme if isinstance(theme, dict) else None
    except Exception:
        return None


def get_home_theme_colors(theme: str, settings: QSettings) -> dict:
    if theme == "Light":
        return {
            "window_bg": "#F0F0F0",
            "panel_bg": "#FFFFFF",
            "text_primary": "#000000",
            "text_secondary": "#666666",
            "accent": "#0078D4",
            "accent_hover": "#005A9E",
            "button_text": "#FFFFFF",
            "splitter": "#CCCCCC",
            "splitter_hover": "#888888",
            "hover_bg": "#E5E5E5",
        }

    if theme == "Custom":
        custom = load_custom_theme(settings)
        if custom:
            return {
                "window_bg": custom.get("window_bg", "#1E1E1E"),
                "panel_bg": custom.get("panel_bg", "#252526"),
                "text_primary": custom.get("text_primary", "#CCCCCC"),
                "text_secondary": custom.get("text_secondary", "#858585"),
                "accent": custom.get("accent", "#007ACC"),
                "accent_hover": custom.get("accent_hover", custom.get("accent", "#007ACC")),
                "button_text": custom.get("button_text", "#FFFFFF"),
                "splitter": custom.get("splitter", "#3E3E42"),
                "splitter_hover": custom.get("splitter_hover", "#6A6A6F"),
                "hover_bg": custom.get("hover_bg", "#2D2D30"),
                "opacity": custom.get("opacity", 100),
            }

    return {
        "window_bg": "#1E1E1E",
        "panel_bg": "#252526",
        "text_primary": "#CCCCCC",
        "text_secondary": "#858585",
        "accent": "#007ACC",
        "accent_hover": "#005A9E",
        "button_text": "#FFFFFF",
        "splitter": "#3E3E42",
        "splitter_hover": "#6A6A6F",
        "hover_bg": "#2D2D30",
    }


def get_palette_colors(theme: str, settings: QSettings) -> dict:
    if theme == "Light":
        return {
            "window_bg": "#F0F0F0",
            "text_primary": "#000000",
            "base": "#FFFFFF",
            "alt_base": "#E9E9E9",
            "tooltip_base": "#FFFFDC",
            "tooltip_text": "#000000",
            "button": "#F0F0F0",
            "button_text": "#000000",
            "bright_text": "#FF0000",
            "link": "#0064C8",
            "highlight": "#0078D7",
            "highlight_text": "#FFFFFF",
        }

    if theme == "Custom":
        custom = load_custom_theme(settings) or {}

        window_bg = custom.get("window_bg", "#1E1E1E")
        text_primary = custom.get("text_primary", "#CCCCCC")
        panel_bg = custom.get("panel_bg", "#252526")
        accent = custom.get("accent", "#007ACC")

        return {
            "window_bg": window_bg,
            "text_primary": text_primary,
            "base": panel_bg,
            "alt_base": panel_bg,
            "tooltip_base": panel_bg,
            "tooltip_text": text_primary,
            "button": panel_bg,
            "button_text": text_primary,
            "bright_text": "#FFFFFF",
            "link": accent,
            "highlight": accent,
            "highlight_text": custom.get("button_text", "#FFFFFF"),
        }

    return {
        "window_bg": "#1E1E1E",
        "text_primary": "#CCCCCC",
        "base": "#1E1E1E",
        "alt_base": "#2D2D30",
        "tooltip_base": "#252526",
        "tooltip_text": "#CCCCCC",
        "button": "#3E3E42",
        "button_text": "#CCCCCC",
        "bright_text": "#FFFFFF",
        "link": "#007ACC",
        "highlight": "#007ACC",
        "highlight_text": "#FFFFFF",
    }

