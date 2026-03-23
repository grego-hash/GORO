"""Master seed runner — deletes DB, re-creates tables, seeds ALL manufacturers.

Run:  python tools/seed_all.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))          # for seed_helpers

from core.hw_configurator_db import get_connection, init_db

# Individual seed modules
import seed_schlage_l_series
import seed_schlage_nd
import seed_corbin_russwin
import seed_sargent
import seed_yale
import seed_best
import seed_von_duprin
import seed_exit_devices
import seed_closers
import seed_accessories
import seed_electric_access
import seed_narrow_stile
import seed_closers_extended
import seed_pulls_protection
import seed_hinges_extended
import seed_seals
import seed_dormakaba
import seed_detex
import seed_hager_select
import seed_access_controls
import seed_institutional
import seed_value_hardware
import seed_dorma

# Batch 4
import seed_falcon
import seed_arrow
import seed_high_security
import seed_trine_bommer_roton
import seed_stanley_gdc
import seed_additional_allegion
import seed_accurate_omnia

# Batch 5
import seed_dh_hinges
import seed_dormakaba_locks
import seed_yale_electronic
import seed_hager_tell
import seed_hager_expanded
import seed_lockey
import seed_emtek_baldwin
import seed_pemko_reese_natguard
import seed_assa_allegion_misc

# Schlage Pricebook series (Batch 6)
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

# LCN Pricebook series (Batch 7)
import seed_lcn_1000
import seed_lcn_4000
import seed_lcn_concealed
import seed_lcn_fire_safety
import seed_lcn_high_security
import seed_lcn_auto_operators
import seed_lcn_actuators


def main():
    db_path = Path(__file__).resolve().parent.parent / "data" / "hw_configurator.db"
    if db_path.exists():
        db_path.unlink()
    init_db()
    conn = get_connection()
    try:
        # Schlage L-Series (existing — uses its own internal helpers)
        seed_schlage_l_series.seed_families(conn)

        # New product lines (use shared seed_helpers)
        seed_schlage_nd.seed(conn)
        seed_corbin_russwin.seed(conn)
        seed_sargent.seed(conn)
        seed_yale.seed(conn)
        seed_best.seed(conn)
        seed_von_duprin.seed(conn)
        seed_exit_devices.seed(conn)
        seed_closers.seed(conn)
        seed_accessories.seed(conn)
        seed_electric_access.seed(conn)
        seed_narrow_stile.seed(conn)
        seed_closers_extended.seed(conn)
        seed_pulls_protection.seed(conn)
        seed_hinges_extended.seed(conn)
        seed_seals.seed(conn)
        seed_dormakaba.seed(conn)
        seed_detex.seed(conn)
        seed_hager_select.seed(conn)
        seed_access_controls.seed(conn)
        seed_institutional.seed(conn)
        seed_value_hardware.seed(conn)
        seed_dorma.seed(conn)

        # Batch 4
        seed_falcon.seed(conn)
        seed_arrow.seed(conn)
        seed_high_security.seed(conn)
        seed_trine_bommer_roton.seed(conn)
        seed_stanley_gdc.seed(conn)
        seed_additional_allegion.seed(conn)
        seed_accurate_omnia.seed(conn)

        # Batch 5
        seed_dh_hinges.seed(conn)
        seed_dormakaba_locks.seed(conn)
        seed_yale_electronic.seed(conn)
        seed_hager_tell.seed(conn)
        seed_hager_expanded.seed(conn)
        seed_lockey.seed(conn)
        seed_emtek_baldwin.seed(conn)
        seed_pemko_reese_natguard.seed(conn)
        seed_assa_allegion_misc.seed(conn)

        # Schlage Pricebook series (Batch 6)
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

        # LCN Pricebook series (Batch 7)
        seed_lcn_1000.seed(conn)
        seed_lcn_4000.seed(conn)
        seed_lcn_concealed.seed(conn)
        seed_lcn_fire_safety.seed(conn)
        seed_lcn_high_security.seed(conn)
        seed_lcn_auto_operators.seed(conn)
        seed_lcn_actuators.seed(conn)

        conn.commit()
        print("\nAll seed data loaded successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
