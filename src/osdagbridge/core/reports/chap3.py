# =============================================================================
# Chapter 3: Loads and Load Combinations
# Extracted from report_generator.py — DO NOT add business logic here.
#
# Live-load section (this revision)
#   * Vehicle table  : Vehicle | Total Load (kN) | Impact Factor |
#                      Braking Load -> Considered? | Value (kN) | Eccentricity (m)
#                      one row per vehicle selected in the Loading tab
#   * Braking summary: Parameter | Value | Unit | Reference
#   * Centrifugal    : per vehicle, with radius / speed / force / eccentricity
#   * Footway        : Parameter | Value | Unit | Reference
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from osdagbridge.core.reports.table_utils import longtable_raw, HEADER_FILL, note_rows

def _na(v):
    """Show N/A instead of an empty cell."""
    return v if str(v).strip() not in ("", "---", "kN") else "N/A"


_VSP = "\n\\vspace{1em}\n"
_KV_SPEC = r"|L{5.4cm}|L{9.0cm}|"
_G = 9.81                       # kN per tonne-force (same value chap3 used for braking)
_DASH = "---"


def _kv_table(caption, rows):
    """Two-column Parameter/Value longtable (header repeats on every page)."""
    body = "\n".join(f"{label} & {value} \\\\[6pt]\n\\hline" for label, value in rows)
    return longtable_raw(caption=caption, col_spec=_KV_SPEC,
                         headers=["Parameter", "Value"], body=body)


# -----------------------------------------------------------------------------
# Small helpers for the live-load tables
# -----------------------------------------------------------------------------
def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _fmt(v, nd=2):
    return f"{v:.{nd}f}" if v is not None else "N/A"


def _find_input(input_dict, *needles, exclude=()):
    """First numeric input whose key contains every needle (case-insensitive)."""
    for k, v in input_dict.items():
        ks = str(k).lower()
        if all(n in ks for n in needles) and not any(x in ks for x in exclude):
            f = _num(v)
            if f is not None:
                return f
    return None


def _to_kN(total, expected_tonnes):
    """The IRC6 vehicle functions return loads in the backend's own unit `t`
    (tonne, kN, N, ... depending on keyfile). Check that the sum is the known IRC
    train load in one of those units, then report it in kN."""
    if total is None or not expected_tonnes:
        return None
    ratio = total / expected_tonnes
    # value of "1 tonne" in the backend unit: t, kN (9.81 / 9.80665), N, kg
    for unit in (1.0, 9.81, 9.80665, 1000.0, 9810.0, 9806.65):
        if abs(ratio - unit) <= 0.02 * unit:
            return expected_tonnes * _G
    return None


def _vehicle_total_kN(irc, key):
    """Total vehicle load in kN, taken from the IRC6 backend functions."""
    try:
        if key == "A":
            return _to_kN(sum(irc.cl_204_1_ClassA_vehicle()["wheel_loads"]), 55.4)
        if key == "70R_W":
            return _to_kN(sum(irc.cl_204_1_Class70R_vehicle_wheel()["wheel_loads"]), 100.0)
        if key == "70R_T":
            d = irc.cl_204_1_Class70R_vehicle_track()
            length = d["x"][1] - d["x"][0]
            return _to_kN(d["wheel_loads_udl"] * length * len(d["z"]), 70.0)
        if key == "SV":
            return _num(irc.cl_204_5_1_special_vehicle()["total_load_kN"])
        if key == "FATIGUE":
            return _to_kN(sum(irc.cl_204_6_fatigue_load()["wheel_loads"]), 40.0)
    except Exception:
        return None
    # No backend function exists yet for these IRC 6 Cl. 204.1 vehicles:
    # IRC 6 Cl. 204.1 train loads (tonnes) -> kN. Replace by backend values when added.
    CODE_T = {"AA_W": 40.0, "AA_T": 70.0, "70R_B": 40.0}
    if key in CODE_T:
        return CODE_T[key] * _G
    return None


def _two_row_header_longtable(caption, col_spec, note=None):
    """Vehicle table shell with the two-row 'Braking Load' group header.
    The header repeats on every page (\\endfirsthead / \\endhead); the note is printed
    under the caption so it can never end up alone on another page."""
    hf = r"\rowcolor{" + HEADER_FILL + r"}"
    h1 = (hf + r" \small\textbf{Vehicle} & \small\textbf{Total Load} & \small\textbf{Impact} & "
          r"\multicolumn{3}{c|}{\small\textbf{Braking Load}} \\ \cline{4-6}")
    h2 = (hf + r" & \small\textbf{(kN)} & \small\textbf{Factor} & \small\textbf{Considered?} & "
          r"\small\textbf{Value (kN)} & \small\textbf{Eccentricity (m)} \\ \hline")
    cont = (r"\multicolumn{6}{l}{\small\textit{\tablename~\thetable\ (continued)}} \\")
    return (r"\begin{longtable}{" + col_spec + "}\n"
            r"\caption{" + caption + r"} \\" + "\n"
            + "\n".join(note_rows(col_spec, 6, note)) + ("\n" if note else "")
            + "\\hline\n" + h1 + "\n" + h2 + "\n"
            r"\endfirsthead" + "\n" + cont + "\n\\hline\n" + h1 + "\n" + h2 + "\n"
            r"\endhead" + "\n")


def _vu_table(caption, rows, note=None):
    """Parameter | Value | Unit | Reference table (unit has its own column)."""
    body = "\n".join(f"{p} & {v} & {u} & {r} \\\\[6pt]\n\\hline" for p, v, u, r in rows)
    return longtable_raw(caption=caption, col_spec=r"|L{4.6cm}|C{3.0cm}|C{2.0cm}|L{3.4cm}|",
                         headers=["Parameter", "Value", "Unit", "Reference"], body=body, note=note)


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017
    span = input_dict.get(KEY_SPAN)
    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)

    # --- Impact factor (1 + IM) from the IRC6 backend ---------------------------
    def _impact_for(kind, tracked=False):
        try:
            span_m = float(span)
            if kind == "A":
                return f"{1.0 + IRC6_2017.cl_208_2_impact_factor(span_m):.3f}"
            if kind == "AA":
                try:    # patched backend: cl_208_3_impact_factor(span, tracked=...)
                    return f"{1.0 + IRC6_2017.cl_208_3_impact_factor(span_m, tracked=tracked):.3f}"
                except TypeError:   # old backend (reads a global; cannot tell wheeled from tracked)
                    return f"{1.0 + IRC6_2017.cl_208_3_impact_factor(span_m):.3f}"
        except Exception:
            pass
        return "N/A"

    # --- Braking: eccentricity (height above roadway) ---------------------------
    try:
        brake_height = float(IRC6_2017.cl_211_3_braking_force_location()["height_m"])
    except Exception:
        brake_height = None

    # (UI flag key, display name, impact class, total-load key, braking considered?, tracked?)
    _VEH_SPEC = [
        (KEY_LL_IRC_CLASS_A,       "Class A",              "A",  "A",       True,  False),
        (KEY_LL_IRC_70R_WHEELED,   "Class 70R (Wheeled)",  "AA", "70R_W",   True,  False),
        (KEY_LL_IRC_70R_TRACKED,   "Class 70R (Tracked)",  "AA", "70R_T",   True,  True),
        (KEY_LL_IRC_AA_WHEELED,    "Class AA (Wheeled)",   "AA", "AA_W",    True,  False),
        (KEY_LL_IRC_AA_TRACKED,    "Class AA (Tracked)",   "AA", "AA_T",    True,  True),
        (KEY_LL_IRC_CLASS_SV,      "Class SV",             None, "SV",      False, False),
        (KEY_LL_IRC_70R_BOGIE,     "Class 70R (Bogie)",    "AA", "70R_B",   True,  False),
        (KEY_LL_IRC_CLASS_FATIGUE, "Class Fatigue",        None, "FATIGUE", False, False),
    ]

    veh_rows = []      # for the vehicle table
    cf_vehicles = []   # (name, total_kN) for the centrifugal table
    for _key, _name, _kind, _tkey, _brake, _trk in _VEH_SPEC:
        if not input_dict.get(_key):
            continue
        total = _vehicle_total_kN(IRC6_2017, _tkey)
        if _brake and total is not None:
            b_val, b_ecc = _fmt(0.20 * total, 1), (_fmt(brake_height, 2) if brake_height is not None else "N/A")
        elif _brake:
            b_val, b_ecc = "N/A", (_fmt(brake_height, 2) if brake_height is not None else "N/A")
        else:
            b_val, b_ecc = _DASH, _DASH
        veh_rows.append([_name, _fmt(total, 1), _impact_for(_kind, _trk) if _kind else "N/A",
                         "Yes" if _brake else "No", b_val, b_ecc])
        if _brake:
            cf_vehicles.append((_name, total))

    for _c in (custom if isinstance(custom, list) else []):
        if isinstance(_c, dict) and _c.get("name"):
            _cn = _tex(str(_c["name"]))
            _tot = None
            for _k in ("total_load", "total_load_kN", "total", "weight", "load"):
                _tot = _num(_c.get(_k))
                if _tot is not None:
                    break
            veh_rows.append([_cn, _fmt(_tot, 1), "N/A", "N/A", "N/A", "N/A"])
        elif isinstance(_c, str) and _c:
            veh_rows.append([_tex(_c), "N/A", "N/A", "N/A", "N/A", "N/A"])

    if not veh_rows:
        veh_rows.append(["None selected"] + [_DASH] * 5)

    veh_body = "\n".join(
        " & ".join(r) + (r" \\" if idx == len(veh_rows) - 1 else r" \\[4pt]") + "\n" + r"\hline"
        for idx, r in enumerate(veh_rows)
    )
    _span_txt = f"{float(span):g} m" if _num(span) is not None else "the design span"
    veh_note = (r"Vehicles are those selected in the Loading tab. Impact factor $= 1+IM$ at span "
                + _span_txt + r" (IRC 6 Cl. 208.2 for Class A; Cl. 208.3 for Class 70R / AA). "
                r"Braking value $= 20\,\%$ of the vehicle's total load (IRC 6 Cl. 211.2), acting at the "
                r"eccentricity shown above the roadway (Cl. 211.3). Class SV and fatigue vehicles carry "
                r"no braking load.")
    _veh_spec = r"|L{3.0cm}|C{2.2cm}|C{1.8cm}|C{2.5cm}|C{1.9cm}|C{2.6cm}|"
    veh_table = (
        r"\begingroup\setlength{\tabcolsep}{4pt}" + "\n"   # 6 columns: tighter padding than the default
        + _two_row_header_longtable("Live Loads (LL) --- Vehicle Loading", _veh_spec, veh_note)
        + veh_body + "\n" + r"\end{longtable}" + "\n" + r"\endgroup")

    # --- Braking summary (bridge level) -----------------------------------------
    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    if lanes in (None, "", 0, "0"):
        _cw = _find_input(input_dict, "carriageway", exclude=("type", "median"))
        if _cw and _cw > 0:
            try:
                lanes = IRC6_2017.table_6(_cw)      # design lanes from carriageway width
            except Exception:
                pass
    braking_kN = None
    if lanes not in (None, ""):
        try:
            raw = float(IRC6_2017.cl_211_2_braking_force(int(lanes)))
            # cl_211_2_braking_force returns Newtons; convert N -> kN
            braking_kN = raw / 1000.0 if raw > 5000.0 else raw
        except Exception:
            braking_kN = None
    brake = _vu_table("Live Loads (LL) --- Braking Force", [
        ("Number of design lanes", _tex(str(lanes)) if lanes not in (None, "") else "N/A", _DASH, "IRC 6 Table 6"),
        ("Total braking force", _fmt(braking_kN, 2), "kN", "IRC 6 Cl. 211.2"),
        ("Point of application (above roadway)", _fmt(brake_height, 2), "m", "IRC 6 Cl. 211.3"),
    ])

    # --- Centrifugal force (IRC 6 Cl. 212): C = W v^2 / (127 R) -----------------
    radius = _find_input(input_dict, "radius")
    speed = _find_input(input_dict, "speed", exclude=("wind",))
    if radius and radius > 0 and speed and speed > 0:
        cf_rows = []
        for _name, _tot in cf_vehicles:
            c_kN = (_tot * speed ** 2 / (127.0 * radius)) if _tot is not None else None
            cf_rows.append((_name, _fmt(radius, 1), _fmt(speed, 1), _fmt(c_kN, 1),
                            _fmt(brake_height, 2) if brake_height is not None else "N/A"))
        if not cf_rows:
            cf_rows.append(("None selected", _DASH, _DASH, _DASH, _DASH))
        cf_body = "\n".join(" & ".join(r) + r" \\[6pt]" + "\n" + r"\hline" for r in cf_rows)
        cf_table = longtable_raw(
            caption="Live Loads (LL) --- Centrifugal Force",
            col_spec=r"|L{3.6cm}|C{2.2cm}|C{2.4cm}|C{2.6cm}|C{2.4cm}|",
            headers=["Vehicle", "Radius, R (m)", "Speed, V (km/h)", "Force, C (kN)", "Eccentricity (m)"],
            body=cf_body,
            note=r"$C = W\,V^2 / (127\,R)$ (IRC 6 Cl. 212.2), applied 1.2 m above the roadway. "
                 r"Applies to curved alignments only.")
    else:
        cf_table = _vu_table("Live Loads (LL) --- Centrifugal Force", [
            ("Radius of curvature, R", "N/A", "m", "IRC 6 Cl. 212"),
            ("Centrifugal force, C", "Not applicable", "kN", "IRC 6 Cl. 212.2"),
        ], note="Centrifugal force acts on curved alignments only. No radius of curvature was "
                "found in the design inputs, so the alignment is treated as straight.")

    # --- Footway loading --------------------------------------------------------
    fp_mode  = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    fp_ref = "Loading tab"
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        try:
            fp_num = float(IRC6_2017.cl_206_1_footway_load())
            fp_ref = "IRC 6 Cl. 206.1"
        except Exception:
            fp_num = None
    else:
        fp_num = _num(fp_value)
    footway = _vu_table("Live Loads (LL) --- Footway Loading", [
        ("Footway pressure mode", _tex(str(fp_mode)) if str(fp_mode).strip() else "N/A", _DASH, "Loading tab"),
        ("Footway live load intensity", _fmt(fp_num, 3), r"kN/m\textsuperscript{2}", fp_ref),
    ])

    # Vz / Pz — prefer stored computed values; fall back to IRC6 Table 12
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb  = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h   = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass
    vz_str = f"{float(vz_val):.2f} m/s" if vz_val not in (None, "") else "N/A"
    pz_str = f"{float(pz_val):.2f} N/m²" if pz_val not in (None, "") else "N/A"

    # Table 3.5 — Seismic: prefer stored computed values; fall back to IRC6 cl_218_5_1
    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral    = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah          = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av          = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z    = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st   = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp   = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res  = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral    = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah          = _res.get("Ah")
            if not sl_av:
                sl_av          = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    def _sl(v, unit=""):
        return f"{float(v):.4f}{unit}" if v not in (None, "") else "N/A"

    # Table 3.6 — Temperature: compute effective bridge temp range from shade temps
    tl_temp_min = tl_temp_max = tl_rise = tl_fall = "N/A"
    try:
        _tmax = input_dict.get(KEY_TL_HIGHEST_MAX_TEMP) or input_dict.get('shade_temp_max')
        _tmin = input_dict.get(KEY_TL_LOWEST_MIN_TEMP)  or input_dict.get('shade_temp_min')
        if _tmax and _tmin:
            _res    = IRC6_2017.cl_215_2_effective_bridge_temperature(
                          float(_tmax), float(_tmin), 'metallic', False)
            _bt_min = _res.get('T_min', 0)
            _bt_max = _res.get('T_max', 0)
            _mean   = (_bt_max + _bt_min) / 2.0
            tl_temp_min = f"{_bt_min:.2f}"
            tl_temp_max = f"{_bt_max:.2f}"
            tl_rise     = f"{_bt_max - _mean:.2f}"
            tl_fall     = f"{_mean - _bt_min:.2f}"
    except Exception:
        pass

    # --- Table 3.7: Load Combinations (dynamically generated from IRC 6) ---
    _LOAD_LABEL_MAP = {
        'dead_load':         'DL',
        'surfacing':         'SIDL',
        'live_load':         'LL',
        'wind_load':         'WL',
        'thermal_load':      'TL',
        'vehicle_collision': 'VC',
        'barge_impact':      'BI',
        'floating_bodies':   'FB',
        'seismic':           'EQ',
    }

    def _fmt_factors(factors):
        """Format a factors dict into a compact load-case string for the table."""
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):  # permanent load with adding/relieving
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue  # skip N/A factors
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"ULS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(
            f"SLS-{i:02d}" + r" & " + cases + r" \\[6pt]" + "\n"
            + r"\hline"
        )

    lc_rows_str = "\n".join(lc_rows)

    dead = _kv_table("Dead Load --- Self Weight", [
        ("Steel Self-Weight Applied", _render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, r" kN/m\textsuperscript{3}")),
        ("Concrete Deck Weight",      _render_value(input_dict, KEY_MATERIAL_DECK_DENSITY,   r" kN/m\textsuperscript{3}")),
        ("Self-Weight Factor",        _render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)),
    ])
    surf = _kv_table("Dead Load for Surfacing (DW)", [
        ("Wearing Course Load", _render_value(input_dict, KEY_WC_MATERIAL) + r" x " + _render_value(input_dict, KEY_WC_THICKNESS)),
        ("Additional SIDL (Crash Barrier)", _render_value(input_dict, KEY_CB_LOAD) + " kN/m per barrier"),
        ("Railing Load", _render_value(input_dict, KEY_RL_LOAD_VALUE) + r" kN/m\sdstar{}"),
    ])
    wind = _kv_table(r"Wind Load (WL) --- per IRC 6", [
        ("Basic Wind Speed, Vb", _render_value(input_dict, "wind_speed", " m/s") + " [from Project Location]"),
        ("Terrain Type", _render_value(input_dict, KEY_WL_TERRAIN_TYPE)),
        ("Average Exposed Height, H (m)", _render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, " m")),
        ("Hourly Mean Wind Speed, Vz", vz_str),
        ("Hourly Wind Pressure, Pz", pz_str.replace("N/m²", r"N/m\textsuperscript{2}")),
        ("Transverse Wind Force", _na(_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, " kN"))),
        ("Longitudinal Wind Force", _na(_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, " kN"))),
        ("Vertical Wind Force", _na(_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, " kN"))),
    ])
    quake = _kv_table(r"Earthquake Load (EL) --- per IRC 6", [
        ("Seismic Zone", _render_value(input_dict, "seismic_zone") + " [from Project Location]"),
        ("Zone Factor, Z", _render_value(input_dict, KEY_SL_ZONE_FACTOR)),
        ("Importance Factor, I", _render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)),
        ("Type of Soil", _render_value(input_dict, KEY_SL_SOIL_TYPE)),
        ("Sa/g", _render_value(input_dict, KEY_SL_SPECTRAL_COEFF)),
        ("Horizontal Seismic Coefficient, Ah", _render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)),
        ("Vertical Seismic Coefficient, Av", _render_value(input_dict, KEY_SL_VERTICAL_COEFF)),
    ])
    temp = _kv_table(r"Temperature Load (TL) --- per IRC 6", [
        ("Maximum Shade Temperature", _render_value(input_dict, "shade_temp_max") + r" $^\circ$C"),
        ("Minimum Shade Temperature", _render_value(input_dict, "shade_temp_min") + r" $^\circ$C"),
        ("Effective Bridge Temp. Range",
         _render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN) + " to " + _render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX) + r" $^\circ$C"),
        ("Temperature Rise / Fall for Design",
         "+" + _render_value(input_dict, KEY_TL_TEMP_RISE) + r" $^\circ$C / \textminus{}" + _render_value(input_dict, KEY_TL_TEMP_FALL) + r" $^\circ$C"),
    ])
    combos = longtable_raw(
        caption="Load Combinations",
        col_spec=r"|C{3.0cm}|L{11.4cm}|",
        headers=["Combination ID", "Load Cases"],
        body=lc_rows_str,
        note="All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.",
    )

    intro = r"""
\chapter{Loads and Load Combinations}

This section summarizes all loads applied to the bridge and the load combinations considered for analysis and design.
"""
    return intro + "".join(
        _VSP + t for t in (dead, surf, veh_table, brake, cf_table, footway, wind, quake, temp, combos)
    ) + "\n"