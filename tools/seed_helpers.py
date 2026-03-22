"""Shared helper functions for hardware configurator seed scripts."""


def fid(conn, manufacturer, name, category, pattern, template):
    """Insert a family and return its id."""
    conn.execute("""
        INSERT OR IGNORE INTO hw_families
            (manufacturer, name, category, assembly_pattern, description_template)
        VALUES (?, ?, ?, ?, ?)
    """, (manufacturer, name, category, pattern, template))
    return conn.execute(
        "SELECT id FROM hw_families WHERE manufacturer=? AND name=?",
        (manufacturer, name),
    ).fetchone()[0]


def slot(conn, family_id, order, name, label, required):
    conn.execute("""
        INSERT OR IGNORE INTO hw_slots (family_id, slot_order, slot_name, slot_label, required)
        VALUES (?, ?, ?, ?, ?)
    """, (family_id, order, name, label, required))


def options(conn, family_id, slot_name, pairs):
    for i, (val, display) in enumerate(pairs):
        conn.execute("""
            INSERT OR IGNORE INTO hw_options (family_id, slot_name, value, display_name, sort_order)
            VALUES (?, ?, ?, ?, ?)
        """, (family_id, slot_name, val, display, i))


def restrict(conn, family_id, trigger_slot, trigger_val, target_slot, allowed, desc):
    for val in allowed:
        rule(conn, family_id, "restrict", trigger_slot, trigger_val, target_slot, val, desc)


def rule(conn, family_id, rtype, tslot, tval, target_slot, target_val, desc):
    conn.execute("""
        INSERT OR IGNORE INTO hw_rules
            (family_id, rule_type, trigger_slot, trigger_value, target_slot, target_value, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (family_id, rtype, tslot, tval, target_slot, target_val, desc))


def conflict_all(conn, family_id, trigger_slot, trigger_values, target_slot, target_options, desc):
    """Create conflict rules to hide a target slot for a list of trigger values."""
    for tv in trigger_values:
        for opt in target_options:
            rule(conn, family_id, "conflict", trigger_slot, tv, target_slot, opt[0], desc)
