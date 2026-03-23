"""Seed Hager exit device pricing from Pricebook #18 (Mar 2026).

Families:  4601 RIM (Narrow Stile Rim, Grade 1)
           4601 CVR (Concealed Vertical Rod, Grade 1)
           4601 CLB (Concealed Less Bottom Rod, Grade 1)
           4701 RIM (Standard Duty Rim)
           4701 SVR (Surface Vertical Rod)
"""

from seed_helpers import fid, slot, options, price

# ── Finish lists ───────────────────────────────────
F_4601 = [
    ("US3",   "US3 - Bright Brass"),
    ("US4",   "US4 - Satin Brass"),
    ("US10B", "US10B - Oil Rubbed Bronze"),
    ("US26",  "US26 - Bright Chrome"),
    ("US26D", "US26D - Satin Chrome"),
    ("US32D", "US32D - Satin Stainless"),
    ("BLK",   "BLK - Black"),
]
_4601K = [v for v, _ in F_4601]

F_4701 = [
    ("ALM",   "ALM - Aluminum"),
    ("DBZ",   "DBZ - Dark Bronze"),
    ("US3",   "US3 - Bright Brass"),
    ("US32D", "US32D - Satin Stainless"),
    ("BLK",   "BLK - Black"),
]
_4701K = [v for v, _ in F_4701]


def _exit_device(conn, name, desc, cat, size_opts, finish_opts, pricing_data,
                 finish_keys):
    """Create an exit device family with compound size:finish pricing."""
    f = fid(conn, "Hager", name, cat,
            "{size} {finish}",
            f"Hager {desc} {{size}} {{finish}}")
    slot(conn, f, 1, "size", "Size", 1)
    slot(conn, f, 2, "finish", "Finish", 1)
    options(conn, f, "size", size_opts)
    options(conn, f, "finish", finish_opts)
    for sz_key, prices in pricing_data:
        for fin, amt in zip(finish_keys, prices):
            if amt is not None:
                price(conn, f, "size:finish", f"{sz_key}:{fin}", amt)
    return f


def seed(conn):
    _seed_4601_rim(conn)
    _seed_4601_cvr(conn)
    _seed_4601_clb(conn)
    _seed_4701_rim(conn)
    _seed_4701_svr(conn)
    print("  Hager Exit Devices (5 families) seeded.")


# ═══════════════════════════════════════════════════
#  4601 RIM – Narrow Stile Rim, Grade 1
# ═══════════════════════════════════════════════════
def _seed_4601_rim(conn):
    sizes = [
        ("36-EO",      '36" Exit Only'),
        ("36-EO-FIRE", '36" Exit Only (Fire Rated)'),
        ("48-EO",      '48" Exit Only'),
        ("48-EO-FIRE", '48" Exit Only (Fire Rated)'),
    ]
    #                       US3       US4       US10B     US26      US26D     US32D     BLK
    data = [
        ("36-EO",      [1901.76, 1901.76, 1901.76, 1901.76, 1741.82, 1901.76, 1901.76]),
        ("36-EO-FIRE", [2126.40, 2126.40, 2126.40, 2126.40, 1950.49, 2126.40, 2126.40]),
        ("48-EO",      [1958.49, 1958.49, 1958.49, 1958.49, 1792.75, 1958.49, None]),
        ("48-EO-FIRE", [2187.40, 2187.40, 2187.40, 2187.40, 2010.81, 2187.40, None]),
    ]
    _exit_device(conn,
                 "4601 RIM Exit Device",
                 "4601 RIM Narrow Stile Exit Device Grade 1",
                 "Exit Device",
                 sizes, F_4601, data, _4601K)


# ═══════════════════════════════════════════════════
#  4601 CVR – Concealed Vertical Rod, Grade 1
# ═══════════════════════════════════════════════════
def _seed_4601_cvr(conn):
    sizes = [
        ("36x84", '36" x 84"'),
        ("36x96", '36" x 96"'),
        ("48x84", '48" x 84"'),
        ("48x96", '48" x 96"'),
    ]
    #                   US3       US4       US10B     US26      US26D     US32D     BLK
    data = [
        ("36x84", [2689.96, 2650.02, 2650.02, 2689.96, 2623.38, 2650.02, 2650.02]),
        ("36x96", [2743.23, 2703.29, 2703.29, 2743.23, 2676.65, 2703.29, 2703.29]),
        ("48x84", [2769.87, 2743.23, 2769.87, 2769.87, 2703.29, 2743.23, 2743.23]),
        ("48x96", [2823.13, 2796.50, 2823.13, 2823.13, 2756.54, 2796.50, 2796.50]),
    ]
    _exit_device(conn,
                 "4601 CVR Exit Device",
                 "4601 CVR Concealed Vertical Rod Exit Device Grade 1",
                 "Exit Device",
                 sizes, F_4601, data, _4601K)


# ═══════════════════════════════════════════════════
#  4601 CLB – Concealed Less Bottom Rod, Grade 1
#  (Same pricing as CVR)
# ═══════════════════════════════════════════════════
def _seed_4601_clb(conn):
    sizes = [
        ("36x84", '36" x 84"'),
        ("36x96", '36" x 96"'),
        ("48x84", '48" x 84"'),
        ("48x96", '48" x 96"'),
    ]
    data = [
        ("36x84", [2689.96, 2650.02, 2650.02, 2689.96, 2623.38, 2650.02, 2650.02]),
        ("36x96", [2743.23, 2703.29, 2703.29, 2743.23, 2676.65, 2703.29, 2703.29]),
        ("48x84", [2769.87, 2743.23, 2769.87, 2769.87, 2703.29, 2743.23, 2743.23]),
        ("48x96", [2823.13, 2796.50, 2823.13, 2823.13, 2756.54, 2796.50, 2796.50]),
    ]
    _exit_device(conn,
                 "4601 CLB Exit Device",
                 "4601 CLB Concealed Less Bottom Rod Exit Device Grade 1",
                 "Exit Device",
                 sizes, F_4601, data, _4601K)


# ═══════════════════════════════════════════════════
#  4701 RIM – Standard Duty Rim
# ═══════════════════════════════════════════════════
def _seed_4701_rim(conn):
    sizes = [
        ("36-EO",      '36" Exit Only'),
        ("36-EO-FIRE", '36" Exit Only (Fire Rated)'),
        ("48-EO",      '48" Exit Only'),
        ("48-EO-FIRE", '48" Exit Only (Fire Rated)'),
    ]
    #                       ALM      DBZ      US3      US32D    BLK
    data = [
        ("36-EO",      [415.88,  415.88,  700.86,  700.86,  415.88]),
        ("36-EO-FIRE", [571.42,  571.42,  860.79,  860.79,  571.42]),
        ("48-EO",      [468.21,  468.21,  753.19,  753.19,  468.21]),
        ("48-EO-FIRE", [625.95,  625.95,  910.92,  910.92,  625.95]),
    ]
    _exit_device(conn,
                 "4701 RIM Exit Device",
                 "4701 RIM Standard Duty Exit Device",
                 "Exit Device",
                 sizes, F_4701, data, _4701K)


# ═══════════════════════════════════════════════════
#  4701 SVR – Surface Vertical Rod
# ═══════════════════════════════════════════════════
def _seed_4701_svr(conn):
    sizes = [
        ("36x84",      '36" x 84"'),
        ("36x84-FIRE", '36" x 84" (Fire Rated)'),
        ("36x96",      '36" x 96"'),
        ("36x96-FIRE", '36" x 96" (Fire Rated)'),
        ("48x84",      '48" x 84"'),
        ("48x84-FIRE", '48" x 84" (Fire Rated)'),
        ("48x96",      '48" x 96"'),
        ("48x96-FIRE", '48" x 96" (Fire Rated)'),
    ]
    #                        ALM       DBZ       US3       US32D     BLK
    data = [
        ("36x84",      [ 676.09,  676.09,  962.59,  962.59,  676.09]),
        ("36x84-FIRE", [ 934.23,  934.23, 1221.34, 1221.34,  934.23]),
        ("36x96",      [ 729.95,  729.95, 1012.67, 1012.67,  729.95]),
        ("36x96-FIRE", [ 988.03,  988.03, 1273.74, 1273.74,  988.03]),
        ("48x84",      [ 753.19,  753.19, 1019.26, 1019.26,  753.19]),
        ("48x84-FIRE", [1012.67, 1012.67, 1297.64, 1297.64, 1012.67]),
        ("48x96",      [ 779.36,  779.36, 1066.53, 1066.53,  779.36]),
        ("48x96-FIRE", [1039.57, 1039.57, 1326.73, 1326.73, 1039.57]),
    ]
    _exit_device(conn,
                 "4701 SVR Exit Device",
                 "4701 SVR Surface Vertical Rod Exit Device",
                 "Exit Device",
                 sizes, F_4701, data, _4701K)
