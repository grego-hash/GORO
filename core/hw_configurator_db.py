"""Hardware Configurator database layer using SQLite."""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


DB_NAME = "hw_configurator.db"


def get_db_path() -> Path:
    """Return the path to the configurator database."""
    return Path(__file__).resolve().parent.parent / "data" / DB_NAME


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS hw_families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                assembly_pattern TEXT NOT NULL DEFAULT '',
                description_template TEXT NOT NULL DEFAULT '',
                UNIQUE(manufacturer, name)
            );

            CREATE TABLE IF NOT EXISTS hw_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL REFERENCES hw_families(id) ON DELETE CASCADE,
                slot_order INTEGER NOT NULL DEFAULT 0,
                slot_name TEXT NOT NULL,
                slot_label TEXT NOT NULL,
                required INTEGER NOT NULL DEFAULT 1,
                UNIQUE(family_id, slot_name)
            );

            CREATE TABLE IF NOT EXISTS hw_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL REFERENCES hw_families(id) ON DELETE CASCADE,
                slot_name TEXT NOT NULL,
                value TEXT NOT NULL,
                display_name TEXT NOT NULL DEFAULT '',
                sort_order INTEGER NOT NULL DEFAULT 0,
                UNIQUE(family_id, slot_name, value)
            );

            CREATE TABLE IF NOT EXISTS hw_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER NOT NULL REFERENCES hw_families(id) ON DELETE CASCADE,
                rule_type TEXT NOT NULL CHECK(rule_type IN ('require','conflict','restrict')),
                trigger_slot TEXT NOT NULL,
                trigger_value TEXT NOT NULL,
                target_slot TEXT NOT NULL,
                target_value TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT ''
            );

            CREATE INDEX IF NOT EXISTS idx_slots_family
                ON hw_slots(family_id);
            CREATE INDEX IF NOT EXISTS idx_options_family_slot
                ON hw_options(family_id, slot_name);
            CREATE INDEX IF NOT EXISTS idx_rules_family
                ON hw_rules(family_id);
            CREATE INDEX IF NOT EXISTS idx_rules_trigger
                ON hw_rules(family_id, trigger_slot, trigger_value);
        """)
        conn.commit()
    finally:
        conn.close()


# ------------------------------------------------------------------
# Read helpers
# ------------------------------------------------------------------

def get_manufacturers() -> List[str]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT manufacturer FROM hw_families ORDER BY manufacturer"
        ).fetchall()
        return [r["manufacturer"] for r in rows]
    finally:
        conn.close()


def get_families(manufacturer: str) -> List[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, name, category, assembly_pattern, description_template "
            "FROM hw_families WHERE manufacturer = ? ORDER BY name",
            (manufacturer,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_family(family_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, manufacturer, name, category, assembly_pattern, "
            "description_template FROM hw_families WHERE id = ?",
            (family_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_slots(family_id: int) -> List[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, slot_name, slot_label, slot_order, required "
            "FROM hw_slots WHERE family_id = ? ORDER BY slot_order",
            (family_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_all_options(family_id: int, slot_name: str) -> List[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT value, display_name FROM hw_options "
            "WHERE family_id = ? AND slot_name = ? ORDER BY sort_order, display_name",
            (family_id, slot_name),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_valid_options(
    family_id: int, slot_name: str, selections: Dict[str, str]
) -> List[dict]:
    """Return valid options for *slot_name* given the current *selections*.

    Rule logic:
      - restrict : whitelist — only listed target values are allowed.
      - conflict : blacklist — listed target values are removed.
      - require  : force — only the required value(s) remain.
    """
    all_opts = get_all_options(family_id, slot_name)
    if not all_opts:
        return all_opts

    conn = get_connection()
    try:
        rules = conn.execute(
            "SELECT rule_type, trigger_slot, trigger_value, target_value "
            "FROM hw_rules WHERE family_id = ? AND target_slot = ?",
            (family_id, slot_name),
        ).fetchall()

        restricted_values: set = set()
        has_restrict = False
        conflicted_values: set = set()
        required_values: set = set()
        has_require = False

        for rule in rules:
            trigger_slot = rule["trigger_slot"]
            trigger_value = rule["trigger_value"]

            if trigger_slot not in selections:
                continue
            if selections[trigger_slot] != trigger_value:
                continue

            rt = rule["rule_type"]
            tv = rule["target_value"]

            if rt == "restrict":
                has_restrict = True
                restricted_values.add(tv)
            elif rt == "conflict":
                conflicted_values.add(tv)
            elif rt == "require":
                has_require = True
                required_values.add(tv)

        valid = all_opts

        if has_require:
            valid = [o for o in valid if o["value"] in required_values]
        elif has_restrict:
            valid = [o for o in valid if o["value"] in restricted_values]

        if conflicted_values:
            valid = [o for o in valid if o["value"] not in conflicted_values]

        return valid
    finally:
        conn.close()


# ------------------------------------------------------------------
# Assembly helpers
# ------------------------------------------------------------------

def assemble_part_number(family_id: int, selections: Dict[str, str]) -> str:
    family = get_family(family_id)
    if not family:
        return ""
    pattern = family["assembly_pattern"]
    if not pattern:
        slots = get_slots(family_id)
        parts = [selections.get(s["slot_name"], "") for s in slots]
        return "".join(p for p in parts if p)
    result = pattern
    for key, val in selections.items():
        result = result.replace("{" + key + "}", val)
    # Remove unfilled placeholders and collapse extra whitespace
    import re as _re
    result = _re.sub(r"\{[^}]+\}", "", result)
    result = " ".join(result.split())
    return result


def assemble_description(family_id: int, selections: Dict[str, str]) -> str:
    family = get_family(family_id)
    if not family:
        return ""
    template = family["description_template"]
    if not template:
        return assemble_part_number(family_id, selections)
    result = template
    for key, val in selections.items():
        result = result.replace("{" + key + "}", val)
    import re as _re
    result = _re.sub(r"\{[^}]+\}", "", result)
    result = " ".join(result.split())
    return result
