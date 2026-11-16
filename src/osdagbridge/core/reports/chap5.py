
from __future__ import annotations
from typing import TYPE_CHECKING
from osdagbridge.core.reports.charts import ur_overview_tex

from osdagbridge.core.utils.common import (
    KEY_DD_AS_BOT,
    KEY_DD_AS_LONG,
    KEY_DD_AS_MIN,
    KEY_DD_AS_REQ_BOT,
    KEY_DD_AS_REQ_TOP,
    KEY_DD_AS_TOP,
    KEY_DD_COVER_OK,
    KEY_DD_DIA_BOT,
    KEY_DD_D_BOT,
    KEY_DD_FY,
    KEY_DD_GAMMA_DL,
    KEY_DD_GAMMA_LL,
    KEY_DD_HAS_OVERHANG,
    KEY_DD_IMPACT_FACTOR,
    KEY_DD_MIN_COVER,
    KEY_DD_MU_BOT,
    KEY_DD_MU_OH,
    KEY_DD_MU_TOP,
    KEY_DD_M_BARRIER,
    KEY_DD_M_DL,
    KEY_DD_M_DL_OH,
    KEY_DD_M_LL,
    KEY_DD_M_LL_OH,
    KEY_DD_M_ULS_HOG,
    KEY_DD_M_ULS_OH,
    KEY_DD_M_ULS_SAG,
    KEY_DD_PUNCH_C1,
    KEY_DD_PUNCH_C2,
    KEY_DD_PUNCH_OK,
    KEY_DD_PUNCH_U1,
    KEY_DD_PUNCH_VED,
    KEY_DD_PUNCH_VED_KN,
    KEY_DD_SHEAR_OK,
    KEY_DD_SHEAR_VED,
    KEY_DD_SHEAR_VRDC,
    KEY_DD_SPACING_MAX,
    KEY_DD_SPAN,
    KEY_DD_SPC_BOT,
    KEY_DD_TYRE_LENGTH,
    KEY_DD_TYRE_WIDTH,
    KEY_DD_VEHICLE,
    KEY_DD_VRD_C_MPA,
    KEY_DD_WDL,
    KEY_DD_WHEEL_LOAD,
    KEY_DD_WK_BOT,
    KEY_DD_WK_LIMIT,
    KEY_DD_WK_OH,
    KEY_DD_WK_TOP,
    KEY_DECK_CONCRETE_GRADE_BASIC,
    KEY_DESIGN_MODE,
    KEY_DS_BOTTOM_CLEAR_COVER,
    KEY_DS_REINF_MATERIAL,
    KEY_DS_STUD_DIAMETER,
    KEY_DS_TOP_CLEAR_COVER,
    KEY_MATERIAL_DECK_FCK,
    KEY_MATERIAL_DECK_FCTM,
    KEY_MP_ED_TYPE,
    KEY_SD_BOTTOM_FLANGE_THICKNESS,
    KEY_SD_BOTTOM_FLANGE_WIDTH,
    KEY_SD_BS_FCD,
    KEY_SD_BS_FCDW_LC,
    KEY_SD_BS_FCDW_WB,
    KEY_SD_BS_FPSD,
    KEY_SD_BS_R,
    KEY_SD_CLASS_FLANGE,
    KEY_SD_CLASS_WEB,
    KEY_SD_COMPOSITE_IZ,
    KEY_SD_DEFL_LIVE,
    KEY_SD_DEFL_TOTAL,
    KEY_SD_EFFECTIVE_SLAB_WIDTH,
    KEY_SD_FLANGE_CLASS_LIMIT,
    KEY_SD_FLANGE_SLENDERNESS,
    KEY_SD_HIGH_SHEAR,
    KEY_SD_IS_FQ,
    KEY_SD_IS_FQD,
    KEY_SD_IS_IYS_MIN,
    KEY_SD_IS_IYS_PROV,
    KEY_SD_LTB_CHI,
    KEY_SD_LTB_LAMBDA,
    KEY_SD_LTB_MB,
    KEY_SD_LTB_MCR,
    KEY_SD_MDV,
    KEY_SD_MD_CAPACITY,
    KEY_SD_MN_AXIAL,
    KEY_SD_MN_MOMENT,
    KEY_SD_MN_RATIO,
    KEY_SD_MU_APPLIED,
    KEY_SD_PANEL_CD,
    KEY_SD_PNA_DEPTH,
    KEY_SD_SC_D_LIMIT,
    KEY_SD_SC_EDGE_DIST,
    KEY_SD_SC_Qr_kN,
    KEY_SD_SC_Qu_kN,
    KEY_SD_SC_REQ_EDGE_DIST,
    KEY_SD_SC_SL1,
    KEY_SD_SC_SL2,
    KEY_SD_SC_SR,
    KEY_SD_SECTION_CLASS,
    KEY_SD_SECTION_PROP_AREA,
    KEY_SD_SECTION_PROP_IZ,
    KEY_SD_SECTION_PROP_ZUZ,
    KEY_SD_SECTION_PROP_ZZ,
    KEY_SD_SHEAR_AV,
    KEY_SD_SHEAR_KV,
    KEY_SD_SHEAR_LAMBDA_W,
    KEY_SD_SHEAR_TAU_B,
    KEY_SD_SHEAR_VCR,
    KEY_SD_SHEAR_VU,
    KEY_SD_STIFF_END_COUNT,
    KEY_SD_STIFF_END_THICK,
    KEY_SD_STIFF_INT_SPACING,
    KEY_SD_STIFF_INT_THICK,
    KEY_SD_STIFF_LONG,
    KEY_SD_STIFF_METHOD,
    KEY_SD_STRESS_STEEL,
    KEY_SD_STRESS_STEEL_ALLOWABLE,
    KEY_SD_TOP_FLANGE_THICKNESS,
    KEY_SD_TOP_FLANGE_WIDTH,
    KEY_SD_TOTAL_DEPTH,
    KEY_SD_TS_VL,
    KEY_SD_TS_VRD,
    KEY_SD_ULS_PER_GIRDER,
    KEY_SD_WEB_CLASS_LIMIT,
    KEY_SD_WEB_SLENDERNESS,
    KEY_SD_WEB_THICKNESS,
    KEY_SPAN,
    KEY_TS_DECK_OVERHANG,
    KEY_TS_DECK_THICKNESS,
    KEY_TS_NO_OF_GIRDERS,
    KEY_UTIL_FLEXURE,
    KEY_UTIL_INTERACTION,
    KEY_UTIL_LTB,
    KEY_UTIL_SHEAR
)

from osdagbridge.core.reports.report_utils import _tex, _render_value, get_girder_entries
from osdagbridge.core.reports.table_utils import girder_longtable, longtable_raw

if TYPE_CHECKING:
    pass


_VSP = "\n\\vspace{1em}\n"


def ch5_design_checks(checks_data, bridge, fig_paths=None) -> str:
    """Chapter 5 — Design Checks.

    Parameters
    ----------
    checks_data : dict
        Raw checks payload (currently unused; data is sourced from bridge).
    bridge : ReportDataBridge
        Provides input_dict, output_dict, and helper methods.
    """
    girder_entries = get_girder_entries(bridge.input_dict)
    if not girder_entries:
        n = int(bridge.input_dict.get(KEY_TS_NO_OF_GIRDERS, 1))
        girder_entries = [(f"Girder {i}", f"M1") for i in range(1, n + 1)]
    n_girders = len(girder_entries)

    od = bridge.output_dict

    # Deck slab design report values (Tables 5.17(a)-(g)), keyed to
    # common.KEY_DD_*. Populated by deckdesign.design_deck_slab(); empty
    # dict when deck design has not been run. Look up with deck_rpt.get(KEY_...).
    deck_rpt = od.get("deck_report_values", {}) or {}

    # -------------------------------------------------------------------------
    # Table 5.1 — per-girder section properties
    # -------------------------------------------------------------------------
    _T51_SPEC = [
        (r"Depth, D (mm)",                               KEY_SD_TOTAL_DEPTH),
        (r"Top Flange Width, $b_f$ (mm)",                KEY_SD_TOP_FLANGE_WIDTH),
        (r"Bottom Flange Width, $b_f$ (mm)",             KEY_SD_BOTTOM_FLANGE_WIDTH),
        (r"Top Flange Thickness, $t_f$ (mm)",            KEY_SD_TOP_FLANGE_THICKNESS),
        (r"Bottom Flange Thickness, $t_f$ (mm)",         KEY_SD_BOTTOM_FLANGE_THICKNESS),
        (r"Web Thickness, $t_w$ (mm)",                   KEY_SD_WEB_THICKNESS),
        (r"Gross Area, A (cm$^2$)",                      KEY_SD_SECTION_PROP_AREA),
        (r"Moment of Inertia, $I_z$ (cm$^4$)",           KEY_SD_SECTION_PROP_IZ),
        (r"Elastic Section Modulus, $Z_{ez}$ (cm$^3$)",  KEY_SD_SECTION_PROP_ZZ),
        (r"Plastic Section Modulus, $Z_{pz}$ (cm$^3$)",  KEY_SD_SECTION_PROP_ZUZ),
        (r"Effective Slab Width, $b_{eff}$ (mm)",        KEY_SD_EFFECTIVE_SLAB_WIDTH),
        (r"Transformed Composite $I_z$ (cm$^4$)",        KEY_SD_COMPOSITE_IZ),
        (r"Depth to Plastic Neutral Axis (mm)",          KEY_SD_PNA_DEPTH),
    ]
    t51_blocks = [
        (lbl, [[txt, _render_value(od, key)] for txt, key in _T51_SPEC])
        for lbl, _ in girder_entries
    ]
    t51_table = girder_longtable(
        caption=r"Girder Section Properties (Final Optimized / User-selected)",
        col_spec=r"|L{9cm}|C{5cm}|",
        headers=["Property", "Value"],
        blocks=t51_blocks,
    )

    # -------------------------------------------------------------------------
    # Table 5.2 — section classification
    # -------------------------------------------------------------------------
    t52_blocks = []
    for lbl, _ in girder_entries:
        t52_blocks.append((lbl, [
            ["Top Flange", _render_value(od, KEY_SD_FLANGE_SLENDERNESS),
             _render_value(od, KEY_SD_FLANGE_CLASS_LIMIT), _render_value(od, KEY_SD_CLASS_FLANGE)],
            ["Web", _render_value(od, KEY_SD_WEB_SLENDERNESS),
             _render_value(od, KEY_SD_WEB_CLASS_LIMIT), _render_value(od, KEY_SD_CLASS_WEB)],
            ["Overall Section", "---", "---", _render_value(od, KEY_SD_SECTION_CLASS)],
        ]))
    t52_table = girder_longtable(
        caption="Girder Section Classification",
        col_spec=r"|L{3.5cm}|C{3.8cm}|C{3.2cm}|C{3.4cm}|",
        headers=["Element", "Slenderness Ratio", "Class Limit", "Classification"],
        blocks=t52_blocks,
        note="IS 800:2007 Table 2",
    )

    # -------------------------------------------------------------------------
    # Table 5.3 — moment capacity
    # Flexure UR is stored as a percent (cat_urs x 100); show as a ratio (/100,
    # 2 dp) and PASS when <= 1.0.
    # -------------------------------------------------------------------------
    try:
        _flex_ur = float(od.get(KEY_UTIL_FLEXURE)) / 100.0
        _flex_ur_str = f"{_flex_ur:.2f}"
        _flex_status = "PASS" if _flex_ur <= 1.0 else r"\textcolor{red}{FAIL}"
    except (TypeError, ValueError):
        _flex_ur_str = ""
        _flex_status = "---"
    t53_blocks = []
    for lbl, _ in girder_entries:
        t53_blocks.append((lbl, [
            [r"Applied Moment, $M_u$", "Governing LC (ULS)",
             _render_value(od, KEY_SD_MU_APPLIED, " kN-m"), "---"],
            [r"Design Moment Capacity, $M_d$", "IRC 22 Cl. 603.3.1",
             _render_value(od, KEY_SD_MD_CAPACITY, " kN-m"), "---"],
            [r"Utilization Ratio, $M_u / M_d$", r"$M_u / M_d$", _flex_ur_str, _flex_status],
        ]))
    _PFVS_SPEC = r"|L{5.2cm}|C{3.4cm}|C{3.4cm}|C{1.9cm}|"
    t53_table = girder_longtable(
        caption="Moment Capacity Check",
        col_spec=_PFVS_SPEC,
        headers=["Parameter", "Formula", "Value", "Status"],
        blocks=t53_blocks,
        note="IRC 22 Cl. 603.3.1, IS 800 Cl. 8.2.1",
    )

    # -------------------------------------------------------------------------
    # Table 5.4 — shear capacity
    # Shear UR is stored as a percent (cat_urs x 100); show as a ratio.
    # -------------------------------------------------------------------------
    try:
        _shear_ur = float(od.get(KEY_UTIL_SHEAR)) / 100.0
        _shear_ur_str = f"{_shear_ur:.2f}"
        _shear_status = "PASS" if _shear_ur <= 1.0 else r"\textcolor{red}{FAIL}"
    except (TypeError, ValueError):
        _shear_ur_str = ""
        _shear_status = "---"
    t54_blocks = []
    for lbl, _ in girder_entries:
        t54_blocks.append((lbl, [
            [r"Applied Shear, $V_u$", "Governing LC (ULS)", _render_value(od, KEY_SD_SHEAR_VU, " kN"), "---"],
            [r"Shear Area, $A_v$", r"$d_w \times t_w$", _render_value(od, KEY_SD_SHEAR_AV, " mm$^2$"), "---"],
            ["Panel Aspect Ratio, c/d", "---", _render_value(od, KEY_SD_PANEL_CD), "---"],
            [r"Shear Buckling Coefficient, $k_v$", "IS 800 Cl. 8.4.2.2", _render_value(od, KEY_SD_SHEAR_KV), "---"],
            [r"Web Slenderness, $\lambda_w$", r"$\sqrt{f_{yw}/(\sqrt{3}\,\tau_{cr})}$",
             _render_value(od, KEY_SD_SHEAR_LAMBDA_W), "---"],
            [r"Design Shear Stress, $\tau_b$", "IRC 22 Cl. 603.3.3.2",
             _render_value(od, KEY_SD_SHEAR_TAU_B, " MPa"), "---"],
            [r"Shear Buckling Resistance, $V_{cr}$", r"$A_v \times \tau_b$",
             _render_value(od, KEY_SD_SHEAR_VCR, " kN"), "---"],
            [r"Utilization Ratio, $V_u / V_d$", r"$V_u / V_d$", _shear_ur_str, _shear_status],
        ]))
    t54_table = girder_longtable(
        caption="Shear Capacity Check",
        col_spec=_PFVS_SPEC,
        headers=["Parameter", "Formula", "Value", "Status"],
        blocks=t54_blocks,
        note="IS 800 Cl. 8.4, IRC 22 Cl. 603.3.3.2",
    )

    # -------------------------------------------------------------------------
    # Table 5.5 — interaction checks
    # Interaction DCRs use the engine bands: PASS <0.90, WARN <1.00, FAIL >=1.00.
    # -------------------------------------------------------------------------
    def _interaction_status(ratio):
        if ratio < 0.90:
            return "PASS"
        elif ratio < 1.00:
            return "WARN"
        return r"\textcolor{red}{FAIL}"
    try:
        _mv_ur = float(od.get(KEY_UTIL_INTERACTION)) / 100.0
        _mv_ur_str = f"{_mv_ur:.2f}"
        _mv_status = _interaction_status(_mv_ur)
    except (TypeError, ValueError):
        _mv_ur_str = ""
        _mv_status = "---"
    # M-N interaction: None -> no axial load -> N/A.
    _mn_r  = od.get(KEY_SD_MN_RATIO)
    _mn_ax = od.get(KEY_SD_MN_AXIAL)
    _mn_mo = od.get(KEY_SD_MN_MOMENT)
    if _mn_r is None or _mn_ax is None or _mn_mo is None:
        _mn_cond = _mn_val = _mn_status = "N/A"
    else:
        _mn_cond   = f"{_mn_ax:.2f} + {_mn_mo:.2f} = {_mn_r:.3f}"
        _mn_val    = f"{_mn_r:.3f}"
        _mn_status = _interaction_status(_mn_r)
    t55_blocks = []
    for lbl, _ in girder_entries:
        t55_blocks.append((lbl, [
            ["High Shear Condition?", r"$V_u > 0.6\,V_d$", _render_value(od, KEY_SD_HIGH_SHEAR), "---"],
            [r"Reduced Moment Capacity, $M_{dv}$", "IRC 22 Cl. 603.3.3.3",
             _render_value(od, KEY_SD_MDV, " kN-m"), "---"],
            [r"Interaction Check: $M_u \leq M_{dv}$", "---", _mv_ur_str, _mv_status],
            [r"Interaction Check: $N_u/N_{Rd} + M_u/M_{dv} \leq 1.0$", _mn_cond, _mn_val, _mn_status],
        ]))
    t55_table = girder_longtable(
        caption="Interaction Checks (M-V and M-N)",
        col_spec=r"|L{4.8cm}|C{3.8cm}|C{3.4cm}|C{1.9cm}|",
        headers=["Check", "Condition", "Value", "Status"],
        blocks=t55_blocks,
        note="IRC 22 Cl. 603.3.3.3",
    )

    # -------------------------------------------------------------------------
    # Table 5.6 — LTB (construction stage)
    # -------------------------------------------------------------------------
    try:
        _ltb_ur = float(od.get(KEY_UTIL_LTB)) / 100.0
        _ltb_ur_str = f"{_ltb_ur:.2f}"
        _ltb_status = _interaction_status(_ltb_ur)
    except (TypeError, ValueError):
        _ltb_ur_str = ""
        _ltb_status = "---"
    t56_blocks = []
    for lbl, _ in girder_entries:
        t56_blocks.append((lbl, [
            [r"Elastic Critical Moment, $M_{cr}$", "IRC 22 Cl. 603.3.3.1",
             _render_value(od, KEY_SD_LTB_MCR, " kN-m"), "---"],
            [r"Non-dim. Slenderness, $\bar{\lambda}_{LT}$", r"$\sqrt{M_p / M_{cr}}$",
             _render_value(od, KEY_SD_LTB_LAMBDA), "---"],
            [r"LTB Reduction Factor, $\chi_{LT}$", "IS 800 Cl. 8.2.2", _render_value(od, KEY_SD_LTB_CHI), "---"],
            [r"LTB Resistance, $M_b$", r"$\chi_{LT}\,M_p / \gamma_{m0}$",
             _render_value(od, KEY_SD_LTB_MB, " kN-m"), "---"],
            [r"$M_u \leq M_b$", r"$M_u / M_b$", _ltb_ur_str, _ltb_status],
        ]))
    t56_table = girder_longtable(
        caption="Lateral Torsional Buckling Check -- Construction Stage",
        col_spec=_PFVS_SPEC,
        headers=["Parameter", "Formula", "Value", "Status"],
        blocks=t56_blocks,
        note="IRC 22 Cl. 603.3.3.1, IS 800 Cl. 8.2.2",
    )

    # -------------------------------------------------------------------------
    # Table 5.7 — stiffener design summary
    # -------------------------------------------------------------------------
    _T57_SPEC = [
        ("Shear Buckling Design Method",           KEY_SD_STIFF_METHOD),
        ("Intermediate Stiffener Thickness (mm)",  KEY_SD_STIFF_INT_THICK),
        ("Intermediate Stiffener Spacing (mm)",    KEY_SD_STIFF_INT_SPACING),
        ("End Panel Stiffener Thickness (mm)",     KEY_SD_STIFF_END_THICK),
        ("No. of End Panel Stiffeners",            KEY_SD_STIFF_END_COUNT),
        ("Longitudinal Stiffeners",                KEY_SD_STIFF_LONG),
    ]
    t57_blocks = [
        (lbl, [[txt, _render_value(od, key)] for txt, key in _T57_SPEC])
        for lbl, _ in girder_entries
    ]
    t57_table = girder_longtable(
        caption="Stiffener Design Summary",
        col_spec=r"|L{9cm}|C{5cm}|",
        headers=["Parameter", "Value"],
        blocks=t57_blocks,
    )

    # -------------------------------------------------------------------------
    # Intermediate stiffener checks (IS 800 Cl. 8.7.1.2)
    # Status: PASS when Provided >= Required.
    # -------------------------------------------------------------------------
    def _ge_status(provided, required):
        try:
            return "PASS" if float(provided) >= float(required) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"
    _iys_status = _ge_status(od.get(KEY_SD_IS_IYS_PROV), od.get(KEY_SD_IS_IYS_MIN))
    _fqd_status = _ge_status(od.get(KEY_SD_IS_FQD), od.get(KEY_SD_IS_FQ))
    t58_blocks = []
    for lbl, _ in girder_entries:
        t58_blocks.append((lbl, [
            [r"Min. Moment of Inertia, $I_s$",
             _render_value(od, KEY_SD_IS_IYS_MIN, " mm$^4$"),
             _render_value(od, KEY_SD_IS_IYS_PROV, " mm$^4$"), _iys_status],
            [r"Buckling Resistance, $F_{qd} \geq F_q$",
             _render_value(od, KEY_SD_IS_FQ, " kN"),
             _render_value(od, KEY_SD_IS_FQD, " kN"), _fqd_status],
        ]))

    # (Intermediate Stiffener Checks) is a verification table — it only
    # has data when the user supplied stiffener sizes (Design Type = Custom). In
    # Optimized mode the stiffeners are auto-sized (nothing to verify), so the
    # whole table is omitted from the report.
    _is_custom = str(bridge.input_dict.get(KEY_DESIGN_MODE, "Optimized")).strip().lower() in {"custom", "customized"}
    _CHECK_SPEC = r"|L{5.2cm}|C{3.3cm}|C{3.5cm}|C{1.9cm}|"
    if _is_custom:
        t58_block = _VSP + girder_longtable(
            caption="Intermediate Stiffener Checks",
            col_spec=_CHECK_SPEC,
            headers=["Check", "Required", "Provided", "Status"],
            blocks=t58_blocks,
            note="IS 800 Cl. 8.7.1.2",
        )
    else:
        t58_block = ""

    # -------------------------------------------------------------------------
    # End panel (bearing) stiffener checks (IS 800 Cl.8.7.3).
    # End panel == bearing stiffener for this bridge. Each resistance vs reaction R.
    # Resistances are 0 in guidance-only mode -> N/A.
    # -------------------------------------------------------------------------
    _bs_r = od.get(KEY_SD_BS_R)
    def _bs_check(resist_key):
        prov = od.get(resist_key)
        if prov is None or float(prov) <= 0.0 or _bs_r is None:
            return ("N/A", "N/A", "N/A")
        req_s  = f"{_bs_r} kN"
        prov_s = f"{prov} kN"
        status = "PASS" if float(prov) >= float(_bs_r) else r"\textcolor{red}{FAIL}"
        return (req_s, prov_s, status)
    _wb_req, _wb_prov, _wb_st = _bs_check(KEY_SD_BS_FCDW_WB)
    _lc_req, _lc_prov, _lc_st = _bs_check(KEY_SD_BS_FCDW_LC)
    _ps_req, _ps_prov, _ps_st = _bs_check(KEY_SD_BS_FPSD)
    _cb_req, _cb_prov, _cb_st = _bs_check(KEY_SD_BS_FCD)
    t59_blocks = []
    for lbl, _ in girder_entries:
        t59_blocks.append((lbl, [
            ["Web Buckling Resistance",    _wb_req, _wb_prov, _wb_st],
            ["Local Crushing Resistance",  _lc_req, _lc_prov, _lc_st],
            ["Bearing Capacity",           _ps_req, _ps_prov, _ps_st],
            ["Column Buckling Resistance", _cb_req, _cb_prov, _cb_st],
        ]))
    t59_table = girder_longtable(
        caption="End Panel Stiffener Checks",
        col_spec=_CHECK_SPEC,
        headers=["Check", "Required", "Provided", "Status"],
        blocks=t59_blocks,
        note="IS 800 Cl. 8.4.2.2",
    )

    # -------------------------------------------------------------------------
    # Serviceability — deflection checks (IRC 22 Cl. 604.3.2)
    # -------------------------------------------------------------------------
    def _defl_status(actual, allowable):
        """PASS / red FAIL for deflection; '---' when values are missing."""
        try:
            return "PASS" if float(actual) <= float(allowable) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"

    def _dfmt(v, nd=2):
        """Format a numeric value to nd decimal places; empty string when None."""
        try:
            return f"{float(v):.{nd}f}"
        except (TypeError, ValueError):
            return ""

    # Mirror generate_results_values_builder.resolve_deflection_live/total_load
    # exactly so the report shows the same numbers as the Generate Results dialog.
    try:
        _span_m = float(bridge.input_dict.get(KEY_SPAN))
        _allow_live_mm  = _span_m * 1000.0 / 800.0
        _allow_total_mm = _span_m * 1000.0 / 600.0
    except (TypeError, ValueError):
        _allow_live_mm = _allow_total_mm = None
    _allow_live_str  = (f"L/800 = {_allow_live_mm:.1f} mm")  if _allow_live_mm  is not None else ""
    _allow_total_str = (f"L/600 = {_allow_total_mm:.1f} mm") if _allow_total_mm is not None else ""

    t510_blocks = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        _live_mm  = od.get(f"{KEY_SD_DEFL_LIVE}.G{_gi}")
        _total_mm = od.get(f"{KEY_SD_DEFL_TOTAL}.G{_gi}")
        t510_blocks.append((lbl, [
            [r"Live Load Deflection, $\delta_{LL}$ (mm)", _allow_live_str,
             _dfmt(_live_mm, nd=3), _defl_status(_live_mm, _allow_live_mm)],
            [r"Total Load Deflection, $\delta_{total}$ (mm)", _allow_total_str,
             _dfmt(_total_mm, nd=3), _defl_status(_total_mm, _allow_total_mm)],
        ]))
    t510_table = girder_longtable(
        caption="Serviceability -- Deflection Checks",
        col_spec=r"|L{5.4cm}|C{3.4cm}|C{3.2cm}|C{1.9cm}|",
        headers=["Check", "Allowable", "Actual", "Status"],
        blocks=t510_blocks,
        note="IRC 22 Cl. 604.3.2",
    )

    # -------------------------------------------------------------------------
    # SLS steel stress limitation (IRC 22 Cl. 604.3.1) — one row per girder
    # -------------------------------------------------------------------------
    def _mpa(v):
        s = _dfmt(v, nd=2)
        return (s + " MPa") if s else ""

    def _stress_status(actual, allow):
        try:
            return "PASS" if float(actual) <= float(allow) else r"\textcolor{red}{FAIL}"
        except (TypeError, ValueError):
            return "---"

    _dr_511        = od.get("design_results", {}) or {}
    _steel_sigma   = _dr_511.get(KEY_SD_STRESS_STEEL)
    _steel_allow   = _dr_511.get(KEY_SD_STRESS_STEEL_ALLOWABLE)
    _steel_sig_str = _mpa(_steel_sigma)
    _steel_alw_str = _mpa(_steel_allow)
    _steel_status  = _stress_status(_steel_sigma, _steel_allow)

    t511_rows = []
    for lbl, _ in girder_entries:
        t511_rows.append(
            r"\makecell{" + lbl + r"""} & Structural Steel ($0.9\,f_y$) & """
            + _steel_alw_str + r""" & """
            + _steel_sig_str + r""" & """
            + _steel_status + r""" \\[6pt]
\hline"""
        )
    t511_table = longtable_raw(
        caption="Serviceability -- Maximum Stress Limitation",
        col_spec=r"|C{1.8cm}|L{3.4cm}|C{3.0cm}|C{3.0cm}|C{1.8cm}|",
        headers=["Girder", "Element", "Allowable Stress", "Actual Stress", "Status"],
        body="\n".join(t511_rows),
    )

    # -------------------------------------------------------------------------
    # Fatigue assessment (IRC 22 Cl. 605) — one row per girder
    # -------------------------------------------------------------------------
    _fat_cat = ((od.get("design_results", {}) or {})
                .get(KEY_SD_ULS_PER_GIRDER, {}) or {}).get("fatigue", {}) or {}

    def _fat_status(s):
        if s is None or str(s).strip() == "":
            return "---"
        return r"\textcolor{red}{" + str(s) + "}" if "FAIL" in str(s).upper() else str(s)

    t512_rows = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        _g = _fat_cat.get(f"G{_gi}", {}) or {}
        t512_rows.append(
            r"\makecell{" + lbl + r"""} & """
            + _mpa(_g.get("demand")) + r""" & """
            + _mpa(_g.get("capacity")) + r""" & """
            + _dfmt(_g.get("ur"), nd=2) + r""" & """
            + _fat_status(_g.get("status")) + r""" \\[6pt]
\hline"""
        )
    t512_table = longtable_raw(
        caption="Serviceability -- Fatigue Assessment",
        col_spec=r"|C{2.0cm}|C{3.2cm}|C{3.4cm}|C{2.8cm}|C{1.9cm}|",
        headers=["Girder", r"Stress Range, $\Delta\sigma$ (MPa)", r"Fatigue Limit, $f_{fd}$ (MPa)",
                 "Utilization Ratio", "Status"],
        body="\n".join(t512_rows),
        note=(r"IRC 22 Cl. 605 --- governing of normal and shear fatigue (worst by DCR). "
              r"Capacity reduction factor $\mu_r$ applied where plate thickness > 25 mm."),
    )

    # -------------------------------------------------------------------------
    # Girder design summary (controlling check per girder)
    # -------------------------------------------------------------------------
    _pg_summary = (od.get("design_results", {}) or {}).get("per_girder", {}) or {}

    def _with_unit(value, unit):
        s = _dfmt(value, nd=2)
        if not s:
            return ""
        return (s + " " + unit) if unit and str(unit) not in ("-", "–") else s

    g_summary_rows = []
    for _gi, (lbl, _) in enumerate(girder_entries, start=1):
        g_data = _pg_summary.get(f"G{_gi}", {}) or {}
        checks = g_data.get("checks") or []
        if not checks:
            g_summary_rows.append(lbl + r""" &  &  &  &  &  &  \\[6pt]
\hline""")
            continue

        ctrl = max(checks, key=lambda c: c.get("dcr") or 0.0)

        # Worst real load case for the controlling check id (skip Envelope pseudo-LCs)
        ctrl_lc, best_dcr = None, None
        for lc_name, lc_data in (g_data.get("per_lc") or {}).items():
            if str(lc_name).lower().startswith("envelope"):
                continue
            for chk in lc_data.get("checks") or []:
                if chk.get("id") == ctrl.get("check_id"):
                    d = chk.get("dcr") or 0.0
                    if best_dcr is None or d > best_dcr:
                        best_dcr, ctrl_lc = d, lc_name
        if ctrl_lc is None:
            ctrl_lc = (g_data.get("demand") or {}).get("governing_combination") or ""

        g_summary_rows.append(
            lbl + r""" & """ + _tex(str(ctrl_lc)) + r""" & """ + _tex(str(ctrl.get("name", "")))
            + r""" & """ + _with_unit(ctrl.get("demand"),   ctrl.get("demand_unit"))
            + r""" & """ + _with_unit(ctrl.get("capacity"), ctrl.get("capacity_unit"))
            + r""" & """ + _dfmt(ctrl.get("dcr"), nd=3)
            + r""" & """ + _fat_status(ctrl.get("status")) + r""" \\[6pt]
\hline"""
        )
    g_summary_table = longtable_raw(
        caption="Girder Design Summary (DCR / Utilization Ratio)",
        col_spec=r"|C{1.3cm}|>{\centering\arraybackslash}p{3.0cm}|C{2.0cm}|C{1.8cm}|C{1.8cm}|C{1.3cm}|C{1.3cm}|",
        headers=["Girder", "Controlling LC / Combination", "Controlling Check", "Demand",
                 "Capacity", "UR", "Status"],
        body="\n".join(g_summary_rows),
        note=(r"UR = Demand / Capacity. A value $\leq 1.0$ indicates a passing check. The controlling "
              r"check is the criterion with the highest UR for each girder, with the real load "
              r"case/combination that drives it."),
    )

    # -------------------------------------------------------------------------
    # Shear connector capacity (bridge-level)
    # Qu (Cl.606.3.1, Eq.6.1) and Qr (Cl.606.3.2, Table 8) are single per-stud
    # values for the bridge, stored flat inside output_dict["design_results"].
    # -------------------------------------------------------------------------
    _dr_sc = od.get("design_results", {}) or {}

    def _kn(v):
        s = _dfmt(v, nd=2)
        return (s + " kN") if s else ""

    t514_content = (
        r"Design Resistance, $Q_u$ & \footnotesize\makecell{$Q_u=\min(Q_{u,s},\,Q_{u,c})$\\[3pt]$Q_{u,s}=\dfrac{0.8\,f_u\,(\pi d^2/4)}{\gamma_v}$\\[3pt]$Q_{u,c}=\dfrac{0.29\,\alpha\,d^2\sqrt{f_{ck}\,E_{cm}}}{\gamma_v}$} & "
        + _kn(_dr_sc.get(KEY_SD_SC_Qu_kN)) + r""" & IRC 22 Cl. 606.3.1 (Eq. 6.1) \\[6pt]
\hline
Fatigue Shear Resistance, $Q_r$ & IRC 22 Table 8 ($\phi d$, $N_{sc}$) & """
        + _kn(_dr_sc.get(KEY_SD_SC_Qr_kN)) + r""" & IRC 22 Cl. 606.3.2 (Table 8) \\[6pt]
\hline"""
    )
    t514_table = longtable_raw(
        caption="Shear Connector Capacity",
        col_spec=r"|L{3.4cm}|C{5.2cm}|C{2.4cm}|L{2.8cm}|",
        headers=["Parameter", "Formula", "Value", "Reference"],
        body=t514_content,
    )

    # -------------------------------------------------------------------------
    # Shear connector spacing (bridge-level)
    # -------------------------------------------------------------------------
    def _mm(v):
        s = _dfmt(v, nd=1)
        return (s + " mm") if s else ""

    _sc_prov     = _dr_sc.get("stud_spacing_provided_mm")
    _sc_prov_str = _mm(_sc_prov)

    def _sp_row(crit, req):
        return (crit + r" & " + _mm(req) + r" & " + _sc_prov_str + r" & "
                + _defl_status(_sc_prov, req) + r" \\[6pt]")

    t515_content = (
        _sp_row("ULS Shear (SL1)",            _dr_sc.get(KEY_SD_SC_SL1)) + "\n\\hline\n"
        + _sp_row("Full Composite (SL2)",       _dr_sc.get(KEY_SD_SC_SL2)) + "\n\\hline\n"
        + _sp_row("SLS Fatigue (SR)",           _dr_sc.get(KEY_SD_SC_SR)) + "\n\\hline\n"
        + _sp_row("Max Spacing Limit (IRC 22)", _dr_sc.get("stud_spacing_max_mm")) + "\n\\hline"
    )
    t515_table = longtable_raw(
        caption="Shear Connector Spacing",
        col_spec=r"|L{3.2cm}|C{3.9cm}|C{3.9cm}|C{2.0cm}|",
        headers=["Criterion", "Governing Spacing", "Actual Spacing Provided", "Status"],
        body=t515_content,
        note=r"IRC 22 Cl. 606.4, 606.9. Governing spacing $= \min(S_{L1}, S_{L2}, S_R)$.",
    )

    # -------------------------------------------------------------------------
    # Transverse shear & detailing checks (bridge-level)
    # -------------------------------------------------------------------------
    def _cm2m(v):
        s = _dfmt(v, nd=2)
        return (s + r" cm$^2$/m") if s else ""

    def _knm(v):
        s = _dfmt(v, nd=2)
        return (s + " kN/m") if s else ""

    _ts_vl  = _dr_sc.get(KEY_SD_TS_VL)
    _ts_vrd = _dr_sc.get(KEY_SD_TS_VRD)
    if _ts_vl is not None and _ts_vrd is not None:
        try:
            _ts_vl_f = float(_ts_vl)
            _ts_vrd_f = float(_ts_vrd)
            if _ts_vrd_f > 0.0:
                _ts_ur_str = f"{_ts_vl_f / _ts_vrd_f:.2f}"
            else:
                _ts_ur_str = "---"
        except (TypeError, ValueError):
            _ts_ur_str = "---"
    else:
        _ts_ur_str = "---"
    _ts_ok = _dr_sc.get("transverse_shear_ok")
    _ts_status = (r"\textcolor{red}{FAIL}" if _ts_ok is False else "PASS") if _ts_ok is not None else "---"

    _ast_req  = _dr_sc.get("Ast_required_cm2_per_m")
    # Provided transverse steel = the deck's main (bottom + top) bars (see deck design).
    _dd_516 = od.get("deck_design_results", {}) or {}
    try:
        _ast_prov = (float(_dd_516.get("rebar_bottom_area") or 0)
                     + float(_dd_516.get("rebar_top_area") or 0)) / 100.0
    except (TypeError, ValueError):
        _ast_prov = None
    _stud_d   = bridge.input_dict.get(KEY_DS_STUD_DIAMETER)
    _d_lim    = _dr_sc.get(KEY_SD_SC_D_LIMIT)
    _edge     = _dr_sc.get(KEY_SD_SC_EDGE_DIST)
    _edge_req = _dr_sc.get(KEY_SD_SC_REQ_EDGE_DIST)

    def _row516(check, value, status):
        return check + r" & " + value + r" & " + status + r" \\[6pt]"

    t516_content = (
        _row516(r"\textnormal{Longitudinal Shear per unit length, $V_L$}", _knm(_ts_vl), "---") + "\n\\hline\n"
        + _row516(r"\textnormal{Transverse Shear Capacity of Slab, $V_{Rd}$}", _knm(_ts_vrd), "---") + "\n\\hline\n"
        + _row516(r"\textnormal{Transverse Shear Check}", r"$V_L/V_{Rd}$ = " + _ts_ur_str, _ts_status) + "\n\\hline\n"
        + _row516(r"\textnormal{Min. Transverse Reinforcement, $A_{st,min}$}",
                  r"Required " + _cm2m(_ast_req) + r", Provided " + _cm2m(_ast_prov),
                  _defl_status(_ast_req, _ast_prov)) + "\n\\hline\n"
        + _row516(r"\textnormal{Stud Diameter $\leq 2\,t_f$}",
                  r"$d$ = " + _mm(_stud_d) + r" $\leq 2t_f$ = " + _mm(_d_lim),
                  _defl_status(_stud_d, _d_lim)) + "\n\\hline\n"
        + _row516(r"\textnormal{Stud Edge Distance}",
                  r"Provided " + _mm(_edge) + r" (req. $\geq$ " + _mm(_edge_req) + r")",
                  _defl_status(_edge_req, _edge)) + "\n\\hline"
    )
    t516_table = longtable_raw(
        caption="Transverse Shear and Detailing Checks",
        col_spec=r"|L{5.0cm}|L{6.4cm}|C{2.0cm}|",
        headers=["Check", "Value", "Status"],
        body=t516_content,
        note="IRC 22 Cl. 606.6, 606.10.",
    )

    # -------------------------------------------------------------------------
    # Cross bracing tables — one banner per panel (girder pair)
    # -------------------------------------------------------------------------
    pairs = bridge.get_cb_pairs()

    # (a) connection + section properties
    cb_forces_blocks = []
    if not pairs:
        cb_forces_blocks.append(("Between Girders", [["Diagonal", "", "", "", ""]]))
    else:
        for pair in pairs:
            pair_id = pair.replace("-", "")
            rows = []
            for member, label in [("diagonal", "Diagonal"),
                                  ("chord", "Top / Bottom chord")]:
                force_str, ftype = bridge.get_cb_governing_force(pair, member)
                conn_type = bridge.get_cb_connection(pair, member, ftype)
                section  = bridge.get_cb_section(pair, member, ftype)

                # Fetch properties from output_dict
                if member == "diagonal":
                    pfx = f"transverse_member_design.cb.section_properties.bracing.{pair_id}"
                else:
                    pfx = f"transverse_member_design.cb.section_properties.bottom_chord.{pair_id}"
                    if od.get(f"{pfx}.A") is None:
                        pfx = f"transverse_member_design.cb.section_properties.top_chord.{pair_id}"

                area_cm2 = od.get(f"{pfx}.A")
                rv_cm = od.get(f"{pfx}.rv")

                # Convert Area: cm2 -> mm2 ; rv: cm -> mm
                area_str = f"{float(area_cm2) * 100:.1f}" if area_cm2 is not None else ""
                rmin_str = f"{float(rv_cm) * 10:.1f}" if rv_cm is not None else ""
                rows.append([label, conn_type, section, area_str, rmin_str])
            cb_forces_blocks.append((_tex(pair), rows))

    # (b) slenderness
    def get_status_str(slnd_str, limit):
        try:
            v = float(slnd_str)
            return r"\textcolor{black}{PASS}" if v <= limit else r"\textcolor{red}{FAIL}"
        except (ValueError, TypeError):
            return ""
    cb_slender_blocks = []
    if not pairs:
        cb_slender_blocks.append(("Between Girders", [["Diagonal", "C", "", "", "---"]]))
    else:
        top_chord_enabled = od.get("member_properties.cross_bracing_details.top_chord", True)
        bottom_chord_enabled = od.get("member_properties.cross_bracing_details.bottom_chord", True)
        for pair in pairs:
            kl_diag = bridge.get_cb_effective_length("diagonal")
            slnd_diag = bridge.get_cb_slenderness(pair, "diagonal")
            status_diag = get_status_str(slnd_diag, 250)

            kl_tc = bridge.get_cb_effective_length("chord")
            slnd_tc = bridge.get_cb_slenderness(pair, "chord")
            status_tc = get_status_str(slnd_tc, 250)

            kl_bc = bridge.get_cb_effective_length("chord")
            slnd_bc = bridge.get_cb_slenderness(pair, "chord")
            status_bc = get_status_str(slnd_bc, 400)

            rows = [["Diagonal", "C", kl_diag, slnd_diag, f"250 --- {status_diag}"]]
            if top_chord_enabled:
                rows.append(["Top chord", "C", kl_tc, slnd_tc, f"250 --- {status_tc}"])
            if bottom_chord_enabled:
                rows.append(["Bottom chord", "T", kl_bc, slnd_bc, f"400 --- {status_bc}"])
            cb_slender_blocks.append((_tex(pair), rows))

    # (c) capacity summary
    cb_capacity_blocks = []
    for pair in pairs:
        rows = []
        for member, label in [("diagonal", "Diagonal"), ("chord", "Chord")]:
            force_str, ftype = bridge.get_cb_governing_force(pair, member)
            section  = bridge.get_cb_section(pair, member, ftype)
            gov_lc   = bridge.get_cb_gov_lc(pair, member, ftype)
            capacity = bridge.get_cb_capacity(pair, member, ftype)
            ur       = bridge.get_cb_efficiency(pair, member, ftype)
            status   = bridge.get_cb_status(pair, member, ftype)
            rows.append([label, section, gov_lc, force_str, capacity, ur, status])
        cb_capacity_blocks.append((_tex(pair), rows))

    _CB_PROPS_SPEC = r"|L{2.8cm}|L{2.4cm}|C{3.0cm}|C{2.6cm}|C{2.6cm}|"
    _CB_SLEN_SPEC  = r"|L{2.8cm}|L{2.0cm}|C{3.0cm}|C{2.4cm}|C{3.2cm}|"
    _CB_CAP_SPEC   = r"|L{2.1cm}|C{2.3cm}|C{2.9cm}|C{1.7cm}|C{1.7cm}|C{1.2cm}|C{1.5cm}|"
    _CB_PROPS_HDR  = ["Member", "Connection", "Section", r"$A_g$ (mm²)", r"$r_{min}$ (mm)"]
    _CB_SLEN_HDR   = ["Member", "Nature", r"Eff.\ Length $KL$ (mm)", r"$KL/r$", "Limit / Status"]
    _CB_CAP_HDR    = ["Member", "Section", "Governing LC", "Demand (kN)", "Capacity (kN)", "UR", "Status"]
    _CB_NOTE_PROPS = r"$A_g$ = gross cross-sectional area; $r_{min}$ = minimum radius of gyration."
    _CB_NOTE_SLEN  = r" 3. Limit = 250 for compression members, 400 for tension members. $K = 1.0$ for members with both ends pinned."
    _CB_NOTE_CAP   = "Designed per IS 800 Cl. 7 (compression) and Cl. 6 (tension). OsdagBridge cross-bracing module used."

    cb_props_table = girder_longtable(
        caption=r"Cross Bracing --- Connection and Section Properties",
        col_spec=_CB_PROPS_SPEC, headers=_CB_PROPS_HDR, blocks=cb_forces_blocks,
        banner="Panel {name}", note=_CB_NOTE_PROPS)
    cb_slen_table = girder_longtable(
        caption=r"Cross Bracing --- Slenderness Ratio Check (IS~800 Cl.~3.8 )",
        col_spec=_CB_SLEN_SPEC, headers=_CB_SLEN_HDR, blocks=cb_slender_blocks,
        banner="Panel {name}", note=_CB_NOTE_SLEN)
    cb_cap_table = girder_longtable(
        caption=r"Cross Bracing Design --- Capacity Summary",
        col_spec=_CB_CAP_SPEC, headers=_CB_CAP_HDR, blocks=cb_capacity_blocks,
        banner="Panel {name}", note=_CB_NOTE_CAP)

    # NOTE: the End Diaphragm tables currently reuse the cross-bracing data
    # (same as before the refactor). Replace the blocks below when real
    # end-diaphragm data helpers exist.
    ed_props_table = girder_longtable(
        caption=r"End Diaphragm --- Connection and Section Properties",
        col_spec=_CB_PROPS_SPEC, headers=_CB_PROPS_HDR, blocks=cb_forces_blocks,
        banner="Panel {name}", note=_CB_NOTE_PROPS)
    ed_slen_table = girder_longtable(
        caption=r"End Diaphragm --- Slenderness Ratio Check (IS~800 Cl.~3.8 )",
        col_spec=_CB_SLEN_SPEC, headers=_CB_SLEN_HDR, blocks=cb_slender_blocks,
        banner="Panel {name}", note=_CB_NOTE_SLEN)
    ed_cap_table = girder_longtable(
        caption=r"End Diaphragm Design --- Capacity Summary",
        col_spec=_CB_CAP_SPEC, headers=_CB_CAP_HDR, blocks=cb_capacity_blocks,
        banner="Panel {name}", note=_CB_NOTE_CAP)

    # -------------------------------------------------------------------------
    # Deck slab design value helpers (Tables 5.17 a/b/c/e/g)
    # Read from deck_rpt = output_dict["deck_report_values"] (common.KEY_DD_*).
    # -------------------------------------------------------------------------
    _dk_has = bool(deck_rpt)
    _dk_oh = bool(deck_rpt.get(KEY_DD_HAS_OVERHANG))
    _DKPH = r"\placeholder{---}"

    def _dkv(key, default=0.0):
        """Raw float for status comparisons (0.0 if missing/non-numeric)."""
        v = deck_rpt.get(key)
        if v is None or v == "":
            return default
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    def _dkf(key, nd=2, scale=1.0):
        """Formatted display string; placeholder when deck design not run."""
        if not _dk_has:
            return _DKPH
        v = deck_rpt.get(key)
        if v is None or v == "":
            return _DKPH
        try:
            return f"{float(v) * scale:.{nd}f}"
        except (TypeError, ValueError):
            return str(v)

    def _dks(ok):
        """PASS/FAIL status; '---' when deck design not run."""
        return ("PASS" if ok else "FAIL") if _dk_has else "---"

    def _dkoh(key, nd=2, scale=1.0, unit=""):
        """Overhang value; 'N/A' when there is no overhang."""
        if not _dk_has:
            return _DKPH
        if not _dk_oh:
            return "N/A"
        return _dkf(key, nd=nd, scale=scale) + unit

    # Governing crack width = max(bottom, top[, overhang]) vs the limit.
    _dk_wks = [_dkv(KEY_DD_WK_BOT), _dkv(KEY_DD_WK_TOP)]
    if _dk_oh:
        _dk_wks.append(_dkv(KEY_DD_WK_OH))
    _dk_gov_wk = max(_dk_wks)
    _dk_gov_wk_str = (f"{_dk_gov_wk:.4f}" if _dk_has else _DKPH)
    _dk_crack_ok = _dk_has and _dk_gov_wk <= _dkv(KEY_DD_WK_LIMIT)

    # -------------------------------------------------------------------------
    # Overall Design Check Summary (all rows)
    #  (1) Girder DCR-engine checks (design_results["per_girder"])
    #  (2) Deck slab (deck_report_values)
    #  (3) Cross bracing / end diaphragm (get_cb_* helpers)
    # -------------------------------------------------------------------------
    _pg_522 = (od.get("design_results", {}) or {}).get("per_girder", {}) or {}
    _dd_522 = od.get("deck_design_results", {}) or {}

    def _vu_522(v, unit):
        s = _dfmt(v, nd=2)
        if not s:
            return ""
        u = (unit or "").strip()
        return (s + " " + u) if u else s

    def _ur_522(v):
        try:
            f = float(v)
        except (TypeError, ValueError):
            return ""
        s = f"{f:.2f}"
        return (r"\textcolor{red}{" + s + "}") if f > 1.0 else s

    def _lc_short(lc):
        # Show the full combination expression as-is.
        return _tex(str(lc).strip())

    def _gov_lc_in_522(g, check_ids):
        gd = _pg_522.get(g) or {}
        best = None
        for _lc, _ld in (gd.get("per_lc") or {}).items():
            if str(_lc).lower().startswith("envelope"):
                continue
            for _chk in (_ld.get("checks") or []):
                if _chk.get("id") in check_ids:
                    _d = _chk.get("dcr") or 0.0
                    if best is None or _d > best[0]:
                        best = (_d, _lc)
        return _lc_short(best[1]) if best else "---"

    def _dcr_row(check_ids, fallback_unit=""):
        # Prefer per_girder["checks"] (carries units); worst girder by DCR.
        best = None  # (dcr, demand, capacity, dunit, cunit, g)
        for g, gd in _pg_522.items():
            if str(g).startswith("EB"):
                continue
            for chk in (gd.get("checks") or []):
                if chk.get("check_id") in check_ids:
                    d = chk.get("dcr") or 0.0
                    if best is None or d > best[0]:
                        best = (d, chk.get("demand"), chk.get("capacity"),
                                chk.get("demand_unit") or "", chk.get("capacity_unit") or "", g)
        if best is not None:
            d, dem, cap, du, cu, g = best
            return (_gov_lc_in_522(g, check_ids),
                    _vu_522(dem, du) or "---", _vu_522(cap, cu) or "---", _ur_522(d) or "---")
        # Fallback: per_lc (no units) for SLS-conditional checks (e.g. deflection).
        best = None  # (dcr, demand, capacity, lc)
        for g, gd in _pg_522.items():
            if str(g).startswith("EB"):
                continue
            for _lc, _ld in (gd.get("per_lc") or {}).items():
                if str(_lc).lower().startswith("envelope"):
                    continue
                for chk in (_ld.get("checks") or []):
                    if chk.get("id") in check_ids:
                        d = chk.get("dcr") or 0.0
                        if best is None or d > best[0]:
                            best = (d, chk.get("demand"), chk.get("capacity"), _lc)
        if best is None:
            return ("---", "---", "---", "---")
        d, dem, cap, _lc = best
        return (_lc_short(_lc),
                _vu_522(dem, fallback_unit) or "---", _vu_522(cap, fallback_unit) or "---",
                _ur_522(d) or "---")

    # (3) Cross bracing — worst pair/member by UR for the given force type.
    _cb_pairs_522 = bridge.get_cb_pairs()

    def _cb_row(force_type):
        best = None  # (ur, pair, member, capacity_str)
        for pair in _cb_pairs_522:
            for member in ("diagonal", "chord"):
                cap = bridge.get_cb_capacity(pair, member, force_type)
                eff = bridge.get_cb_efficiency(pair, member, force_type)
                try:
                    ur = float(eff)
                except (TypeError, ValueError):
                    continue
                if best is None or ur > best[0]:
                    best = (ur, pair, member, cap)
        if best is None:
            return ("---", "---", "---", "---")
        ur, pair, member, cap = best
        gov = bridge.get_cb_gov_lc(pair, member, force_type) or "---"
        dem = f"{float(cap) * ur:.2f} kN" if cap else "---"
        cap_s = (cap + " kN") if cap else "---"
        return (gov, dem, cap_s, _ur_522(ur))

    def _cb_slender_row():
        best = None  # (ratio, slend, limit)
        for pair in _cb_pairs_522:
            for member in ("diagonal", "chord"):
                s = bridge.get_cb_slenderness(pair, member)
                try:
                    sf = float(s)
                except (TypeError, ValueError):
                    continue
                lim = 400.0 if member == "chord" else 250.0
                ratio = sf / lim
                if best is None or ratio > best[0]:
                    best = (ratio, sf, lim)
        if best is None:
            return ("---", "---", "---", "---")
        ratio, sf, lim = best
        return ("---", f"{sf:.1f}", f"{lim:.0f}", _ur_522(ratio))

    def _row522(label, cells):
        c = [x if x else "---" for x in cells]
        return label + r" & " + r" & ".join(c) + r" \\[6pt]" + "\n\\hline"

    # Deck rows: Demand/Capacity from deck_report_values; UR = Demand/Capacity.
    # The deck is designed for the IRC:6 Basic ULS combination.
    _deck_combo = (
        r"Basic ULS: " + _tex(f"{_dkv(KEY_DD_GAMMA_DL):g}DL + {_dkv(KEY_DD_GAMMA_LL):g}LL")
    ) if _dk_has else "---"

    def _deck_row(dem_key, cap_key, unit, is_oh=False):
        if not _dk_has:
            return ("---", "---", "---", "---")
        if is_oh and not _dk_oh:
            return (_deck_combo, "N/A", "N/A", "N/A")
        dem = _dkv(dem_key)
        cap = _dkv(cap_key)
        ur = (dem / cap) if cap > 0 else None
        return (_deck_combo, f"{dem:.2f} {unit}", f"{cap:.2f} {unit}", _ur_522(ur))

    def _row522_msg(label, msg):
        # Single message spanning the 4 data columns.
        return label + r" & \multicolumn{4}{c|}{" + msg + r"} \\[6pt]" + "\n\\hline"

    # End diaphragm: when configured as Cross Bracing it is designed as bracing
    # members -> mirror the cross-bracing axial rows. For Rolled / Welded beam end
    # diaphragms the moment/shear design is not implemented yet -> show a message.
    _ed_type = ""
    for _k, _v in bridge.input_dict.items():
        if str(_k).startswith(KEY_MP_ED_TYPE) and _v:
            _ed_type = str(_v)
            break
    _ed_is_cb = "brac" in _ed_type.strip().lower()
    if _ed_is_cb:
        _ed_moment_row = _row522(r"End Diaphragm --- Moment", _cb_row("compression"))
        _ed_shear_row  = _row522(r"End Diaphragm --- Shear",  _cb_row("tension"))
    else:
        _ed_msg = r"Rolled / Welded section --- design to be added"
        _ed_moment_row = _row522_msg(r"End Diaphragm --- Moment", _ed_msg)
        _ed_shear_row  = _row522_msg(r"End Diaphragm --- Shear",  _ed_msg)

    # Crack width (slab): governing crack width vs limit (frequent SLS combination).
    def _gov_sls_frequent():
        best = None  # (dcr, lc)
        for _g, _gd in _pg_522.items():
            if str(_g).startswith("EB"):
                continue
            for _lc, _ld in (_gd.get("per_lc") or {}).items():
                if "frequent" not in str(_lc).lower():
                    continue
                _d = _ld.get("max_dcr") or 0.0
                if best is None or _d > best[0]:
                    best = (_d, _lc)
        return _tex(str(best[1]).strip()) if best else "Frequent SLS"

    _wk_lim = _dkv(KEY_DD_WK_LIMIT)
    _crack_cells = (
        (_gov_sls_frequent() if _dk_has else "---"),
        (f"{_dk_gov_wk:.3f} mm" if _dk_has else "---"),
        (f"{_wk_lim:.3f} mm" if _dk_has else "---"),
        (_ur_522(_dk_gov_wk / _wk_lim) if (_dk_has and _wk_lim > 0) else "---"),
    )

    _t522 = [
        _row522(r"Girder --- Moment",             _dcr_row({1})),
        _row522(r"Girder --- Shear",              _dcr_row({2})),
        _row522(r"Girder --- LTB (constr.)",      _dcr_row({5})),
        _row522(r"Girder --- Deflection",         _dcr_row({13, 14}, fallback_unit="mm")),
        _row522(r"Girder --- Stress",             _dcr_row({11}, fallback_unit="MPa")),
        _row522(r"Girder --- Fatigue",            _dcr_row({8, 9}, fallback_unit="MPa")),
        _row522(r"Transverse Shear (slab)",       _dcr_row({16})),
        _row522(r"Crack Width (slab)",            _crack_cells),
        _row522(r"Deck --- Flexure (sagging)",    _deck_row(KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT, "kN-m/m")),
        _row522(r"Deck --- Flexure (hogging)",    _deck_row(KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP, "kN-m/m")),
        _row522(r"Deck --- Cantilever Overhang",  _deck_row(KEY_DD_M_ULS_OH, KEY_DD_MU_OH, "kN-m/m", is_oh=True)),
        _row522(r"Deck --- Punching Shear",       _deck_row(KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA, "MPa")),
        _row522(r"Deck --- One-Way Shear",        _deck_row(KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC, "kN/m")),
        _row522(r"Cross Bracing --- Compression", _cb_row("compression")),
        _row522(r"Cross Bracing --- Tension",     _cb_row("tension")),
        _row522(r"Cross Bracing --- Slenderness", _cb_slender_row()),
        _ed_moment_row,
        _ed_shear_row,
    ]
    t522_table = longtable_raw(
        caption="Overall Design Check Summary --- All Members",
        col_spec=r"|C{3.4cm}|L{4.5cm}|C{2.3cm}|C{2.3cm}|C{1.6cm}|",
        headers=["Member / Check", "Governing Load Combo", "Demand", "Capacity", "UR"],
        body="\n".join(_t522),
        note=(r"UR = Demand / Capacity. All values $\leq 1.0$ indicate passing checks. The governing "
              r"check for each component is highlighted in the individual design check sections above."),
    )

    # -------------------------------------------------------------------------
    # Deck slab tables
    # -------------------------------------------------------------------------
    deck_load_body = (
        r"""\textnormal{Effective Span of Deck Slab, $l_{eff}$} & """ + _dkf(KEY_DD_SPAN, nd=0, scale=1000.0) + r""" mm (girder spacing, c/c) \\[6pt]
\hline
\textnormal{Deck Thickness, $t_s$} & """ + _render_value(bridge.input_dict, KEY_TS_DECK_THICKNESS) + r""" mm \\[6pt]
\hline
\textnormal{Clear Cover (IRC 112 Cl. 15.2)} & Top """ + _render_value(bridge.input_dict, KEY_DS_TOP_CLEAR_COVER) + r""" / Bottom """ + _render_value(bridge.input_dict, KEY_DS_BOTTOM_CLEAR_COVER) + r""" mm \\[6pt]
\hline
\textnormal{Concrete Grade (IRC 112 Cl. 6.4)} & """ + _render_value(bridge.input_dict, KEY_DECK_CONCRETE_GRADE_BASIC) + r""" ($f_{ck}$ = """ + _render_value(bridge.input_dict, KEY_MATERIAL_DECK_FCK) + r""" MPa, $f_{ctm}$ = """ + _render_value(bridge.input_dict, KEY_MATERIAL_DECK_FCTM) + r""" MPa) \\[6pt]
\hline
\textnormal{Reinforcement Grade (IRC 112 Cl. 6.2)} & """ + _render_value(bridge.input_dict, KEY_DS_REINF_MATERIAL) + r""" ($f_y$ = """ + _dkf(KEY_DD_FY, nd=0) + r""" MPa) \\[6pt]
\hline
\textnormal{Dead Load per Unit Area, $w_{DL}$} & """ + _dkf(KEY_DD_WDL, nd=2) + r""" kN/m² (slab self-weight) \\[6pt]
\hline
\textnormal{IRC 6 Wheel Load (Class A / 70R)} & """ + _dkf(KEY_DD_WHEEL_LOAD, nd=1) + r""" kN \\[6pt]
\hline
\textnormal{Tyre Contact Width (IRC 6 Annex~A)} & """ + _dkf(KEY_DD_TYRE_WIDTH, nd=0, scale=1000.0) + r""" mm (transverse) \\[6pt]
\hline
\textnormal{Impact Factor (IRC 6 Cl. 208.2)} & """ + _dkf(KEY_DD_IMPACT_FACTOR, nd=3) + r""" \\[6pt]
\hline
\textnormal{Governing Live Load Case} & """ + _dkf(KEY_DD_VEHICLE) + r""" \\[6pt]
\hline"""
    )
    deck_load_table = longtable_raw(
        caption=r"Deck Slab --- Loading and Geometry",
        col_spec=r"|L{5.5cm}|p{8.6cm}|",
        headers=None, n_cols=2,
        body=deck_load_body,
    )

    # Flexure (interior panel): banners = location, rows = parameters
    deck_flex_blocks = [
        (r"At Midspan (Sagging)", [
            [r"Transverse BM (DL), $M_{T,DL}$", r"$w_{DL}\,l_{eff}^2/10$",
             _dkf(KEY_DD_M_DL, nd=2) + r" kN-m/m", "---"],
            [r"Transverse BM (LL), $M_{T,LL}$", "Effective width (IRC 112 B3.1)",
             _dkf(KEY_DD_M_LL, nd=2) + r" kN-m/m", "---"],
            [r"Total Design BM, $M_{u,sag}$",
             _dkf(KEY_DD_GAMMA_DL, nd=2) + r" DL + " + _dkf(KEY_DD_GAMMA_LL, nd=2) + r" LL",
             _dkf(KEY_DD_M_ULS_SAG, nd=2) + r" kN-m/m", "---"],
            [r"Effective depth, $d$", r"$t_s - c_{nom} - \phi/2$",
             _dkf(KEY_DD_D_BOT, nd=1) + r" mm", "---"],
            [r"Moment Capacity, $M_{Rd}$", "IRC 112 Cl. 12.2",
             _dkf(KEY_DD_MU_BOT, nd=2) + r" kN-m/m",
             _dks(_dkv(KEY_DD_MU_BOT) >= _dkv(KEY_DD_M_ULS_SAG))],
        ]),
        (r"At Support (Hogging)", [
            [r"Total Design BM, $M_{u,hog}$",
             _dkf(KEY_DD_GAMMA_DL, nd=2) + r" DL + " + _dkf(KEY_DD_GAMMA_LL, nd=2) + r" LL (at support)",
             _dkf(KEY_DD_M_ULS_HOG, nd=2) + r" kN-m/m", "---"],
            [r"Required Top Steel, $A_{st,top}$", r"$M_u / (0.87\,f_y\,d)$",
             _dkf(KEY_DD_AS_REQ_TOP, nd=0) + r" mm²/m", "---"],
            [r"Moment Capacity, $M_{Rd}$", "IRC 112 Cl. 12.2",
             _dkf(KEY_DD_MU_TOP, nd=2) + r" kN-m/m",
             _dks(_dkv(KEY_DD_MU_TOP) >= _dkv(KEY_DD_M_ULS_HOG))],
        ]),
    ]
    deck_flex_table = girder_longtable(
        caption=r"Deck Slab --- Flexure Check: Interior Panel (Pigeaud's Method)",
        col_spec=r"|L{4.4cm}|C{3.8cm}|C{3.7cm}|C{2.0cm}|",
        headers=["Parameter", "Formula / Reference", "Value", "Status"],
        blocks=deck_flex_blocks,
        banner="{name}",
        note=(r"IRC 112 Cl. 12.2. Distribution (longitudinal) reinforcement designed for 20\% of "
              r"main steel moment (IRC 21 Cl. 305.18)."),
    )

    deck_oh_body = (
        r"""Overhang Length, $l_{oh}$ & --- & """ + _render_value(bridge.input_dict, KEY_TS_DECK_OVERHANG, " m") + r""" & --- \\[6pt]
\hline
Crash Barrier Load Moment & IRC 6 Cl. 206.4 & """ + _dkoh(KEY_DD_M_BARRIER, nd=2, unit=" kN-m/m") + r""" & --- \\[6pt]
\hline
Dead Load Moment & $w_{DL}\,l_{oh}^2/2$ + railing & """ + _dkoh(KEY_DD_M_DL_OH, nd=2, unit=" kN-m/m") + r""" & --- \\[6pt]
\hline
Live Load Moment (eccentric wheel) & Wheel load $\times$ arm & """ + _dkoh(KEY_DD_M_LL_OH, nd=2, unit=" kN-m/m") + r""" & --- \\[6pt]
\hline
Total Hogging Moment, $M_{u,oh}$ & """ + _dkf(KEY_DD_GAMMA_DL, nd=2) + r""" DL + """ + _dkf(KEY_DD_GAMMA_LL, nd=2) + r""" (LL + CB) & """ + _dkoh(KEY_DD_M_ULS_OH, nd=2, unit=" kN-m/m") + r""" & --- \\[6pt]
\hline
Moment Capacity (top steel), $M_{Rd,oh}$ & IRC 112 Cl. 12.2 & """ + _dkoh(KEY_DD_MU_OH, nd=2, unit=" kN-m/m") + r""" & """ + (_dks(_dkv(KEY_DD_MU_OH) >= _dkv(KEY_DD_M_ULS_OH)) if _dk_oh else ("N/A" if _dk_has else "---")) + r""" \\[6pt]
\hline"""
    )
    deck_oh_table = longtable_raw(
        caption=r"Deck Slab --- Cantilever Overhang Flexure Check",
        col_spec=r"|L{4.8cm}|C{3.2cm}|C{3.9cm}|C{1.9cm}|",
        headers=["Parameter", "Formula", "Value", "Status"],
        body=deck_oh_body,
        note=r"IRC 6 Cl. 206.4 crash barrier loads applied at kerb face; IRC 112 Cl. 12.2 flexure.",
    )

    deck_punch_body = (
        r"""Design Wheel Load (ULS), $V_{Ed}$ & $\gamma_Q\,(1+IF)\,P_w$ & """ + _dkf(KEY_DD_PUNCH_VED_KN, nd=1) + r""" kN & --- \\[6pt]
\hline
Tyre Contact Area & $a \times b$ (IRC 6 Annex~A) & """ + _dkf(KEY_DD_TYRE_WIDTH, nd=0, scale=1000.0) + r""" $\times$ """ + _dkf(KEY_DD_TYRE_LENGTH, nd=0) + r""" mm & --- \\[6pt]
\hline
Loaded Area at mid-depth, $b_0$ & $c_1 \times c_2$ (incl.\ WC dispersion) & """ + _dkf(KEY_DD_PUNCH_C1, nd=0) + r""" $\times$ """ + _dkf(KEY_DD_PUNCH_C2, nd=0) + r""" mm & --- \\[6pt]
\hline
Control Perimeter, $u_1$ & $2(c_1+c_2) + 4\pi d$ & """ + _dkf(KEY_DD_PUNCH_U1, nd=0) + r""" mm & --- \\[6pt]
\hline
Punching Shear Stress, $v_{Ed}$ & $V_{Ed} / (u_1\,d)$ & """ + _dkf(KEY_DD_PUNCH_VED, nd=3) + r""" MPa & --- \\[6pt]
\hline
Punching Resistance, $v_{Rd,c}$ & IRC 112 Eq.\ 10.1 & """ + _dkf(KEY_DD_VRD_C_MPA, nd=3) + r""" MPa & --- \\[6pt]
\hline
Punching Shear Check & $v_{Ed} \leq v_{Rd,c}$ & """ + (f"{_dkv(KEY_DD_PUNCH_VED) / _dkv(KEY_DD_VRD_C_MPA):.2f}" if (_dk_has and _dkv(KEY_DD_VRD_C_MPA) > 0) else _DKPH) + r""" & """ + _dks(bool(deck_rpt.get(KEY_DD_PUNCH_OK))) + r""" \\[6pt]
\hline"""
    )
    deck_punch_table = longtable_raw(
        caption=r"Deck Slab --- Punching Shear Check (IRC~112 Cl.~10.4.6)",
        col_spec=r"|L{4.8cm}|C{3.2cm}|C{3.9cm}|C{1.9cm}|",
        headers=["Parameter", "Formula / Reference", "Value", "Status"],
        body=deck_punch_body,
        note=r"Punching shear reinforcement not typically required for deck slabs with $d \geq 200$ mm and adequate longitudinal reinforcement.",
    )

    deck_crack_body = (
        r"""\textnormal{Min. Reinforcement for Crack Control, $A_{s,min}$} & """ + _dkf(KEY_DD_AS_MIN, nd=0) + r""" mm²/m [IRC 112 Cl. 16.5.1] \\[6pt]
\hline
\textnormal{Provided Reinforcement (bottom)} & $\phi$""" + _dkf(KEY_DD_DIA_BOT, nd=0) + r""" @ """ + _dkf(KEY_DD_SPC_BOT, nd=0) + r""" mm c/c (""" + _dkf(KEY_DD_AS_BOT, nd=0) + r""" mm²/m) \\[6pt]
\hline
\textnormal{Max. Permissible Crack Width} & """ + _dkf(KEY_DD_WK_LIMIT, nd=2) + r""" mm \\[6pt]
\hline
\textnormal{Calculated Crack Width, $w_k$ (governing)} & """ + _dk_gov_wk_str + r""" mm \\[6pt]
\hline
\textnormal{Crack Width Check} & """ + _dks(_dk_crack_ok) + r""" \\[6pt]
\hline"""
    )
    deck_crack_table = longtable_raw(
        caption=r"Crack Width Check (Deck Slab)",
        col_spec=r"|L{6.5cm}|L{7.5cm}|",
        headers=["Parameter", "Value / Reference"],
        body=deck_crack_body,
    )

    deck_shear_body = (
        r"""Design Shear per unit width, $V_{Ed}$ & $\gamma_{DL} V_{DL} + \gamma_{LL}(1{+}IF)V_{LL}$ & """ + _dkf(KEY_DD_SHEAR_VED, nd=2) + r""" kN/m & --- \\[6pt]
\hline
Effective depth, $d$ & $t_s - c_{nom} - \phi/2$ & """ + _dkf(KEY_DD_D_BOT, nd=1) + r""" mm & --- \\[6pt]
\hline
Size factor, $k$ & $1 + \sqrt{200/d} \leq 2.0$ & """ + (f"{min(1.0 + (200.0 / _dkv(KEY_DD_D_BOT)) ** 0.5, 2.0):.3f}" if (_dk_has and _dkv(KEY_DD_D_BOT) > 0) else _DKPH) + r""" & --- \\[6pt]
\hline
Long.\ reinforcement ratio, $\rho_l$ & $A_{sl}/(b_w\,d) \leq 0.02$ & """ + (f"{min(_dkv(KEY_DD_AS_BOT) / (1000.0 * _dkv(KEY_DD_D_BOT)), 0.02):.4f}" if (_dk_has and _dkv(KEY_DD_D_BOT) > 0) else _DKPH) + r""" & --- \\[6pt]
\hline
Shear resistance (no stirrups), $V_{Rd,c}$ & $v_{Rd,c}\,b_w\,d$ (Cl.\ 10.3.2) & """ + _dkf(KEY_DD_SHEAR_VRDC, nd=2) + r""" kN/m & --- \\[6pt]
\hline
One-Way Shear Check & $V_{Ed} \leq V_{Rd,c}$ & """ + (f"{_dkv(KEY_DD_SHEAR_VED) / _dkv(KEY_DD_SHEAR_VRDC):.2f}" if (_dk_has and _dkv(KEY_DD_SHEAR_VRDC) > 0) else _DKPH) + r""" & """ + _dks(bool(deck_rpt.get(KEY_DD_SHEAR_OK))) + r""" \\[6pt]
\hline"""
    )
    deck_shear_table = longtable_raw(
        caption=r"One-Way (Beam) Shear Check (Deck Slab)",
        col_spec=r"|L{4.8cm}|C{3.2cm}|C{3.9cm}|C{1.9cm}|",
        headers=["Parameter", "Formula / Reference", "Value", "Status"],
        body=deck_shear_body,
        note=r"IRC 112 Cl. 10.3.2. Shear reinforcement not provided in deck slabs; capacity relies on concrete and main reinforcement.",
    )

    deck_detail_body = (
        r"""\multicolumn{4}{|l|}{\textbf{Main Reinforcement --- Bottom (Transverse)}} \\[6pt]
\hline
Required Area, $A_{st,req}$ (mm²/m) & """ + _dkf(KEY_DD_AS_REQ_BOT, nd=0) + r""" mm²/m & """ + _dkf(KEY_DD_AS_BOT, nd=0) + r""" mm²/m & """ + _dks(_dkv(KEY_DD_AS_BOT) >= _dkv(KEY_DD_AS_REQ_BOT)) + r""" \\[6pt]
\hline
Bar Diameter $\times$ Spacing & $\phi \geq 10$ mm (IRC 112) & $\phi$""" + _dkf(KEY_DD_DIA_BOT, nd=0) + r""" @ """ + _dkf(KEY_DD_SPC_BOT, nd=0) + r""" mm c/c & --- \\[6pt]
\hline
Min.\ Reinforcement $A_{s,min}$ (IRC 112 Cl. 16.3.1) & """ + _dkf(KEY_DD_AS_MIN, nd=0) + r""" mm²/m & """ + _dkf(KEY_DD_AS_BOT, nd=0) + r""" mm²/m & """ + _dks(_dkv(KEY_DD_AS_BOT) >= _dkv(KEY_DD_AS_MIN)) + r""" \\[6pt]
\hline
Max.\ Bar Spacing (IRC 112 Cl. 16.3.2) & """ + _dkf(KEY_DD_SPACING_MAX, nd=0) + r""" mm & """ + _dkf(KEY_DD_SPC_BOT, nd=0) + r""" mm & """ + _dks(0.0 < _dkv(KEY_DD_SPC_BOT) <= _dkv(KEY_DD_SPACING_MAX)) + r""" \\[6pt]
\hline
\multicolumn{4}{|l|}{\textbf{Distribution Reinforcement --- Longitudinal}} \\[6pt]
\hline
Required Area, $A_{st,dist}$ (mm²/m) & $\geq 20\%$ of main steel & """ + _dkf(KEY_DD_AS_LONG, nd=0) + r""" mm²/m & """ + _dks(_dkv(KEY_DD_AS_LONG) >= max(0.20 * _dkv(KEY_DD_AS_BOT), _dkv(KEY_DD_AS_MIN))) + r""" \\[6pt]
\hline
\multicolumn{4}{|l|}{\textbf{Top Reinforcement (Support / Cantilever Overhang)}} \\[6pt]
\hline
Required Area, $A_{st,top}$ (mm²/m) & """ + _dkf(KEY_DD_AS_REQ_TOP, nd=0) + r""" mm²/m & """ + _dkf(KEY_DD_AS_TOP, nd=0) + r""" mm²/m & """ + _dks(_dkv(KEY_DD_AS_TOP) >= _dkv(KEY_DD_AS_REQ_TOP)) + r""" \\[6pt]
\hline
\multicolumn{4}{|l|}{\textbf{Cover and Detailing}} \\[6pt]
\hline
Clear Cover (IRC 112 Cl. 15.2) & $\geq$ """ + _dkf(KEY_DD_MIN_COVER, nd=0) + r""" mm (Table 14.2) & Top """ + _render_value(bridge.input_dict, KEY_DS_TOP_CLEAR_COVER) + r""" / Bottom """ + _render_value(bridge.input_dict, KEY_DS_BOTTOM_CLEAR_COVER) + r""" mm & """ + _dks(bool(deck_rpt.get(KEY_DD_COVER_OK))) + r""" \\[6pt]
\hline"""
    )
    deck_detail_table = longtable_raw(
        caption=r"Reinforcement Detailing Summary (Deck Slab)",
        col_spec=r"|L{5.0cm}|C{3.5cm}|C{3.5cm}|C{1.9cm}|",
        headers=["Parameter", "Required / Limit", "Provided", "Status"],
        body=deck_detail_body,
        note=r"IRC 112 Cl. 16.3, IS 456 Cl. 26.5. All reinforcement provisions satisfy strength and detailing requirements.",
    )

    # -------------------------------------------------------------------------
    # Assemble chapter
    # -------------------------------------------------------------------------
    parts = [r"""
\chapter{Design Checks}

This section presents all structural design checks performed by OsdagBridge. For each member, the demand from the governing load combination, the code-based capacity, and the utilization ratio are tabulated. All checks reference IS 800:2007 and IRC 22:2014 unless stated otherwise.

\section{Plate Girder Design}
\label{sec:plate-girder}
"""]

    for tbl in (t51_table, t52_table, t53_table, t54_table, t55_table, t56_table, t57_table):
        parts.append(_VSP + tbl)
    parts.append(t58_block)
    for tbl in (t59_table, t510_table, t511_table, t512_table, g_summary_table, t514_table):
        parts.append(_VSP + tbl)

    # The two lines below were in the original template just before the spacing
    # table; they are kept so later tables keep their original alignment.
    parts.append("\n" + r"\setlength\LTleft{0pt}" + "\n" + r"\setlength\LTright{\fill}" + "\n")
    parts.append(t515_table)
    parts.append(_VSP + t516_table)

    parts.append(r"""
% ===========================
\section{Deck Slab Design}
\label{sec:deck-design}
% ===========================

The reinforced concrete deck slab is designed per IRC~112:2011 (flexure, shear, crack width) and IRC~22:2014 (composite construction). Wheel loads are distributed using Pigeaud's method. The deck is checked for flexure in the transverse and longitudinal directions, punching shear, one-way (beam) shear, crack width, and reinforcement detailing.
""")
    for tbl in (deck_load_table, deck_flex_table, deck_oh_table, deck_punch_table):
        parts.append(_VSP + tbl)
    parts.append(_VSP + r"\clearpage" + "\n" + deck_crack_table)
    for tbl in (deck_shear_table, deck_detail_table):
        parts.append(_VSP + tbl)

    parts.append(r"""
% ===========================
\section{Cross Bracing Design}
\label{sec:cross-bracing}
% ===========================

Cross bracing between adjacent plate girders provides lateral stability during construction, resists transverse loads (wind, seismic, braking) in service, and prevents lateral torsional buckling of the girders. Members are designed per IS~800:2007 Cl.~7 (compression) and Cl.~6 (tension). Forces are derived from the grillage model under the governing load combination  (DL + LL + WL).

\vspace{1em}

\vspace{0.4em}
\noindent
\setlength{\tabcolsep}{4pt}
\setlength\LTleft{0pt}
\setlength\LTright{\fill}
""")
    for tbl in (cb_props_table, cb_slen_table, cb_cap_table):
        parts.append(_VSP + tbl)

    parts.append(r"""
% ===========================
\section{End Diaphragm Design}
\label{sec:end-diaphragm}
% ===========================

End diaphragms at the supports transfer transverse loads to the bearings, restrain the bottom flanges against lateral displacement, and maintain the girder cross-section geometry during construction and in service. They are designed per IS~800:2007 and IRC~24:2010 Cl.~507.

\vspace{1em}

\vspace{0.4em}
\noindent
\setlength{\tabcolsep}{4pt}
\setlength{\LTleft}{0pt}
\setlength{\LTright}{\fill}
""")
    for tbl in (ed_props_table, ed_slen_table, ed_cap_table):
        parts.append(_VSP + tbl)

    parts.append(r"""
% ===========================
\section{Overall Design Check Summary}
\label{sec:overall-summary}
% ===========================
""")
    parts.append(_VSP + t522_table + "\n")
    parts.append(ur_overview_tex(od, (fig_paths or {}).get("ur_heatmap")))
    return "\n".join(parts)
    return "\n".join(parts)