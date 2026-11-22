from osdagbridge.core.utils.common import (
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DS_REINF_MATERIAL,
)
from osdagbridge.core.reports.report_utils import _tex
from osdagbridge.core.reports.summary_charts import material_charts_tex
from osdagbridge.core.reports.table_utils import longtable_raw

_ROWS = [
    ("1",    "Structural Steel (IS 2062) for Girders", "steel_girders"),
    ("2(a)", "Cross Bracing - Top Chord",              "bracing_top"),
    ("2(b)", "Cross Bracing - Bottom Chord",           "bracing_bot"),
    ("2(c)", "Cross Bracing - Diagonal Chord",         "bracing_diag"),
    ("3",    "Concrete ({concrete}) for Deck Slab",    "concrete_deck"),
    ("4",    "Reinforcement Steel ({rebar})",          "rebar_deck"),
    ("5",    "Shear Stud Connectors",                  "shear_studs"),
    ("6",    "Crash Barrier",                          "crash_barrier"),
]
_FIELDS = ("vol_formula", "qty", "vol_total", "wt_single", "wt_total")

_NOTE = (
    r"Weights use 2.5 t/m$^3$ for concrete and 7.85 t/m$^3$ for steel. Reinforcement is "
    r"estimated at 120 kg per m$^3$ of deck concrete; it is not computed from the detailed bar "
    r"layout. End-diaphragm quantities are not included in this version. "
    r"N.A. = not available."
)


def ch7_quantities(input_dict, fig_paths=None):
    concrete = _tex(str(input_dict.get(KEY_DECK_CONCRETE_GRADE_BASIC) or "").strip()) or "M40"
    rebar = _tex(str(input_dict.get(KEY_DS_REINF_MATERIAL) or "").strip()) or "Fe 500"

    rows = []
    for sn, label, prefix in _ROWS:
        cells = [str(input_dict.get(f"{prefix}_{f}", "N.A.")) for f in _FIELDS]
        desc = label.format(concrete=concrete, rebar=rebar)
        rows.append(f"{sn} & {desc} & " + " & ".join(cells) + r" \\" + "\n" + r"\hline")

    table = longtable_raw(
        caption="Bill of Materials (Steel, Concrete, and Reinforcement Quantities)",
        col_spec=r"|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|",
        headers=[
            "S.N.", "Item Description", "Volume", "Quantity",
            "Total Volume", "Weight (MT)", "Total Weight (MT)",
        ],
        body="\n".join(rows),
        note=_NOTE,
    )

    charts = material_charts_tex(fig_paths)

    return (
        r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

\begingroup
\setlength{\tabcolsep}{3.5pt}
"""
        + table
        + r"""
\endgroup
"""
        + charts
    )