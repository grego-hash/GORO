"""Master seed runner — deletes DB, re-creates tables, seeds ALL manufacturers.

Only manufacturers with pricebook pricing are loaded.
Shell-only seed modules are commented out and can be re-enabled
when their pricebooks are extracted.

Run:  python tools/seed_all.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))          # for seed_helpers

from core.hw_configurator_db import get_connection, init_db

# ── Priced manufacturer seed modules ─────────────────────────────────

# Schlage Pricebook (L-Series + ND + 12 additional series)
import seed_schlage_l_series
import seed_schlage_nd
import seed_schlage_alx
import seed_schlage_b250
import seed_schlage_b500
import seed_schlage_b600
import seed_schlage_cl
import seed_schlage_cs210
import seed_schlage_hl
import seed_schlage_lm9200
import seed_schlage_pc
import seed_schlage_pm
import seed_schlage_pt
import seed_schlage_s
import seed_schlage_cylinders

# Von Duprin Pricebook
import seed_vonduprin_pricebook

# LCN Pricebook (7 series)
import seed_lcn_1000
import seed_lcn_4000
import seed_lcn_concealed
import seed_lcn_fire_safety
import seed_lcn_high_security
import seed_lcn_auto_operators
import seed_lcn_actuators

# Hager Pricebook (hinges, closers, exit devices)
import seed_hager_hinges
import seed_hager_closers
import seed_hager_exit

# Ives Pricebook
import seed_ives_pricebook

# Zero International Pricebook
import seed_zero_pricebook

# NGP (National Guard Products) Pricebook
import seed_ngp_pricebook

# Trimco Pricebook
import seed_trimco_pricebook

# ── Shell-only modules (no pricing yet — re-enable after pricebook extraction) ──
# import seed_corbin_russwin
# import seed_sargent
# import seed_yale
# import seed_best
# import seed_exit_devices
# import seed_closers
# import seed_accessories
# import seed_electric_access
# import seed_narrow_stile
# import seed_closers_extended
# import seed_pulls_protection
# import seed_hinges_extended
# import seed_seals
# import seed_dormakaba
# import seed_detex
# import seed_hager_select
# import seed_access_controls
# import seed_institutional
# import seed_value_hardware
# import seed_dorma
# import seed_falcon
# import seed_arrow
# import seed_high_security
# import seed_trine_bommer_roton
# import seed_stanley_gdc
# import seed_additional_allegion
# import seed_accurate_omnia
# import seed_dh_hinges
# import seed_dormakaba_locks
# import seed_yale_electronic
# import seed_hager_tell
# import seed_hager_expanded
# import seed_lockey
# import seed_emtek_baldwin
# import seed_pemko_reese_natguard
# import seed_assa_allegion_misc


def main():
    db_path = Path(__file__).resolve().parent.parent / "data" / "hw_configurator.db"
    if db_path.exists():
        db_path.unlink()
    init_db()
    conn = get_connection()
    try:
        # ── Schlage ──
        seed_schlage_l_series.seed_families(conn)
        seed_schlage_nd.seed(conn)
        seed_schlage_alx.seed(conn)
        seed_schlage_b250.seed(conn)
        seed_schlage_b500.seed(conn)
        seed_schlage_b600.seed(conn)
        seed_schlage_cl.seed(conn)
        seed_schlage_cs210.seed(conn)
        seed_schlage_hl.seed(conn)
        seed_schlage_lm9200.seed(conn)
        seed_schlage_pc.seed(conn)
        seed_schlage_pm.seed(conn)
        seed_schlage_pt.seed(conn)
        seed_schlage_s.seed(conn)
        seed_schlage_cylinders.seed(conn)

        # ── Von Duprin ──
        seed_vonduprin_pricebook.seed(conn)

        # ── LCN ──
        seed_lcn_1000.seed(conn)
        seed_lcn_4000.seed(conn)
        seed_lcn_concealed.seed(conn)
        seed_lcn_fire_safety.seed(conn)
        seed_lcn_high_security.seed(conn)
        seed_lcn_auto_operators.seed(conn)
        seed_lcn_actuators.seed(conn)

        # ── Hager ──
        seed_hager_hinges.seed(conn)
        seed_hager_closers.seed(conn)
        seed_hager_exit.seed(conn)

        # ── Ives ──
        seed_ives_pricebook.seed(conn)

        # ── Zero International ──
        seed_zero_pricebook.seed(conn)

        # ── NGP ──
        seed_ngp_pricebook.seed(conn)

        # ── Trimco ──
        seed_trimco_pricebook.seed(conn)

        conn.commit()
        print("\nAll seed data loaded successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
