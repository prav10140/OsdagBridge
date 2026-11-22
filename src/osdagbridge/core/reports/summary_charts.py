# osdagbridge/core/reports/summary_charts.py
"""Summary charts for the design report.

  * Section 5.5  - Utilization Ratio (UR = Demand / Capacity) bar charts for
                   Steel Plate Girders, Concrete Deck Slab, Cross Bracing and
                   End Diaphragms, each with a red dashed line at UR = 1.0.
  * Chapter 7    - material quantity charts: structural steel tonnage by
                   component, and concrete volume (m3) vs reinforcement (MT).

Usage (see the three small edits in report_generator.py / chap5.py):

    build_summary_charts(tmp_images, output_dict, inputs, bridge, fig_paths)
    ur_bar_charts_tex(fig_paths)       # LaTeX for Section 5.5
    material_charts_tex(fig_paths)     # LaTeX for Chapter 7

Every chart is drawn with matplotlib (Agg backend, no GUI), saved as a PNG in the
temporary images folder and embedded with \\includegraphics inside a figure.
A chart that has no data is skipped (and logged); the report never fails because
of a chart.
"""
import io
import logging
import math
import os
import re
from collections import OrderedDict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

try:                                      # inside the osdagbridge package
    from . import styles as S
except Exception:                         # standalone testing
    S = None

logger = logging.getLogger(__name__)


# =============================================================================
# Style (reads styles.py when it defines CHART / C, otherwise safe defaults)
# =============================================================================
def _cfg():
    chart = (getattr(S, "CHART", None) or {}) if S else {}
    pal = (getattr(S, "C", None) or {}) if S else {}
    primary = "#" + str(pal.get("primary", "91B014")).lstrip("#")
    return {
        "dpi":        chart.get("dpi", 200),
        "pass":       chart.get("pass_color", primary),
        "warn":       chart.get("warn_color", "#F9A825"),
        "fail":       chart.get("fail_color", "#C62828"),
        "threshold":  chart.get("threshold_color", "red"),
        "steel":      chart.get("steel_color", primary),
        "concrete":   chart.get("concrete_color", "#7F8C8D"),
        "rebar":      chart.get("rebar_color", "#2E5E8C"),
        "near_limit": chart.get("near_limit", 0.90),
    }


def _png(fig, dpi):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return buf.getvalue()


def _f(v):
    try:
        x = float(v)
        return None if (math.isnan(x) or math.isinf(x)) else x
    except (TypeError, ValueError):
        return None


def _natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(s))]


# =============================================================================
# 1. Data for the UR charts
# =============================================================================
def collect_ur_groups(output_dict, input_dict, bridge):
    """Return OrderedDict{element: {"items": [(label, UR|None)], "message": str}}.

    Same data sources as the Overall Design Check Summary (Table 5.22):
      girders   : design_results["per_girder"][G*]["checks"][*]["dcr"]
      deck slab : deck_report_values  (demand / capacity, crack width / limit)
      bracing   : bridge.get_cb_* helpers
    """
    od = output_dict or {}
    inp = input_dict or {}
    groups = OrderedDict()

    # ---- Steel plate girders: governing UR of each girder -------------------
    items, note = [], ""
    pg = (od.get("design_results", {}) or {}).get("per_girder", {}) or {}
    best_all = None
    n_girders = None                 # results of an earlier run (e.g. G4, G5) must not appear
    try:
        from osdagbridge.core.utils.common import KEY_TS_NO_OF_GIRDERS
        n_girders = int(float(inp.get(KEY_TS_NO_OF_GIRDERS)))
    except Exception:
        pass
    for g in sorted(pg, key=_natural):
        if str(g).startswith("EB"):
            continue
        gm = re.fullmatch(r"G(\d+)", str(g))
        if n_girders and gm and int(gm.group(1)) > n_girders:
            continue
        checks = (pg[g] or {}).get("checks") or []
        scored = [(_f(c.get("dcr")), c) for c in checks]
        scored = [(d, c) for d, c in scored if d is not None]
        if not scored:
            continue
        d, c = max(scored, key=lambda t: t[0])
        items.append((str(g), d))
        if best_all is None or d > best_all[0]:
            best_all = (d, f"{g}: {c.get('name', '')}".strip(": "))
    if not items:     # fall back to the flat category URs (stored as percent)
        try:
            from osdagbridge.core.utils.common import (
                KEY_UTIL_FLEXURE, KEY_UTIL_SHEAR, KEY_UTIL_LTB, KEY_UTIL_INTERACTION)
            for lbl, k in (("Flexure", KEY_UTIL_FLEXURE), ("Shear", KEY_UTIL_SHEAR),
                           ("LTB", KEY_UTIL_LTB), ("M-V", KEY_UTIL_INTERACTION)):
                v = _f(od.get(k))
                if v is not None:
                    items.append((lbl, v / 100.0))
            if items:
                best_all = max(((v, l) for l, v in items), key=lambda t: t[0])
        except Exception:
            pass
    groups["Steel Plate Girders"] = {
        "items": items, "message": "No girder results available",
        "governing": best_all[1] if best_all else ""}

    # ---- Concrete deck slab -------------------------------------------------
    items, gov = [], ""
    try:
        from osdagbridge.core.utils.common import (
            KEY_DD_HAS_OVERHANG, KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT, KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP,
            KEY_DD_M_ULS_OH, KEY_DD_MU_OH, KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA,
            KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC, KEY_DD_WK_BOT, KEY_DD_WK_TOP, KEY_DD_WK_OH,
            KEY_DD_WK_LIMIT)
        dk = od.get("deck_report_values", {}) or {}
        if dk:
            has_oh = bool(dk.get(KEY_DD_HAS_OVERHANG))

            def ratio(dem_k, cap_k):
                dem, cap = _f(dk.get(dem_k)), _f(dk.get(cap_k))
                return (dem / cap) if (dem is not None and cap and cap > 0) else None

            items = [
                ("Sagging\nflexure", ratio(KEY_DD_M_ULS_SAG, KEY_DD_MU_BOT)),
                ("Hogging\nflexure", ratio(KEY_DD_M_ULS_HOG, KEY_DD_MU_TOP)),
            ]
            if has_oh:
                items.append(("Cantilever", ratio(KEY_DD_M_ULS_OH, KEY_DD_MU_OH)))
            items += [
                ("Punching\nshear", ratio(KEY_DD_PUNCH_VED, KEY_DD_VRD_C_MPA)),
                ("One-way\nshear", ratio(KEY_DD_SHEAR_VED, KEY_DD_SHEAR_VRDC)),
            ]
            wks = [_f(dk.get(KEY_DD_WK_BOT)), _f(dk.get(KEY_DD_WK_TOP))]
            if has_oh:
                wks.append(_f(dk.get(KEY_DD_WK_OH)))
            wks = [w for w in wks if w is not None]
            lim = _f(dk.get(KEY_DD_WK_LIMIT))
            items.append(("Crack\nwidth", (max(wks) / lim) if (wks and lim and lim > 0) else None))
            vals = [(v, l.replace("\n", " ")) for l, v in items if v is not None]
            gov = {"Cantilever": "Cantilever overhang"}.get(max(vals)[1], max(vals)[1]) if vals else ""
    except Exception as exc:
        logger.warning("UR chart: deck data not read (%s)", exc)
    groups["Concrete Deck Slab"] = {
        "items": items, "message": "Deck slab design not run", "governing": gov}

    # ---- Cross bracing (and end diaphragm when designed as bracing) --------
    def bracing_items():
        out = []
        try:
            for pair in bridge.get_cb_pairs():
                urs = []
                for member, lim in (("diagonal", 250.0), ("chord", 400.0)):
                    for ft in ("compression", "tension"):
                        u = _f(bridge.get_cb_efficiency(pair, member, ft))
                        if u is not None:
                            urs.append(u)
                    s = _f(bridge.get_cb_slenderness(pair, member))
                    if s is not None:
                        urs.append(s / lim)
                out.append((str(pair), max(urs) if urs else None))
        except Exception as exc:
            logger.warning("UR chart: bracing data not read (%s)", exc)
        return out

    cb_items = bracing_items()
    cb_vals = [(v, l) for l, v in cb_items if v is not None]
    groups["Cross Bracing"] = {
        "items": cb_items, "message": "Cross bracing not designed",
        "governing": ("Panel " + max(cb_vals)[1]) if cb_vals else ""}

    ed_type = ""
    try:
        from osdagbridge.core.utils.common import KEY_MP_ED_TYPE
        for k, v in inp.items():
            if str(k).startswith(KEY_MP_ED_TYPE) and v:
                ed_type = str(v)
                break
    except Exception:
        pass
    if "brac" in ed_type.strip().lower():
        groups["End Diaphragms"] = {
            "items": list(cb_items), "message": "End diaphragm not designed",
            "governing": ("Panel " + max(cb_vals)[1]) if cb_vals else ""}
    else:
        groups["End Diaphragms"] = {
            "items": [], "governing": "",
            "message": "Design not available for the selected\nend-diaphragm type (rolled / welded section)"}
    return groups


# =============================================================================
# 2. Drawing the UR charts
# =============================================================================
def _bar_color(v, cfg):
    if v > 1.0:
        return cfg["fail"]
    if v >= cfg["near_limit"]:
        return cfg["warn"]
    return cfg["pass"]


def _legend(fig, cfg, anchor_y=-0.02, ax=None):
    handles = [
        Line2D([0], [0], color=cfg["threshold"], ls="--", lw=1.8, label="UR = 1.0 limit"),
        Patch(facecolor=cfg["pass"], edgecolor="black", label=f"Pass (UR $\\leq$ {cfg['near_limit']:.1f})"),
        Patch(facecolor=cfg["warn"], edgecolor="black", label=f"Near limit ({cfg['near_limit']:.1f}-1.0)"),
        Patch(facecolor=cfg["fail"], edgecolor="black", label="Fail (UR > 1.0)"),
    ]
    if ax is not None:      # anchored under the axes (clears multi-line tick labels)
        ax.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=8,
                  bbox_to_anchor=(0.5, anchor_y))
    else:
        fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=8,
                   bbox_to_anchor=(0.5, anchor_y))


def _draw_bars(ax, title, items, cfg, ymax, message=""):
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_ylim(0, ymax)
    ax.set_ylabel("Utilization Ratio (UR)", fontsize=9)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    have = [(l, v) for l, v in items if v is not None]
    if not have:
        ax.set_xticks([])
        ax.text(0.5, 0.5, message or "No data", transform=ax.transAxes, ha="center", va="center",
                fontsize=9, color="gray", style="italic")
    else:
        for i, (lbl, v) in enumerate(items):
            if v is None:
                ax.text(i, 0.02 * ymax, "n/a", ha="center", va="bottom", fontsize=8, color="gray")
                continue
            ax.bar(i, v, width=0.62, color=_bar_color(v, cfg), edgecolor="black", linewidth=0.6, zorder=2)
            ax.text(i, v + 0.015 * ymax, f"{v:.2f}", ha="center", va="bottom", fontsize=8, zorder=5,
                    bbox=dict(facecolor="white", edgecolor="none", pad=1.2, alpha=0.85))
        ax.set_xticks(range(len(items)))
        ax.set_xticklabels([l for l, _ in items], fontsize=(7 if len(items) > 4 else 8))
    ax.axhline(1.0, color=cfg["threshold"], linestyle="--", linewidth=1.7, zorder=3)


def _shared_ymax(groups):
    vals = [v for g in groups.values() for _, v in g["items"] if v is not None]
    return max(1.25, 1.18 * max(vals)) if vals else 1.25


def _overview_items(groups):
    """Bar items (label, governing UR) for the overview chart + max label lines."""
    import textwrap
    items, max_lines = [], 2
    for name, g in groups.items():
        vals = [v for _, v in g["items"] if v is not None]
        label = "\n".join(textwrap.wrap(name, 14))
        if vals and g.get("governing"):
            label += "\n" + "\n".join(textwrap.wrap("(" + g["governing"] + ")", 17))
        elif not vals:
            label += "\n(not designed)"
        max_lines = max(max_lines, label.count("\n") + 1)
        items.append((label, max(vals) if vals else None))
    return items, max_lines


def ur_overview_bar_png(groups):
    """One bar per primary element = its governing (highest) UR."""
    cfg = _cfg()
    items, max_lines = _overview_items(groups)
    if not any(v is not None for _, v in items):
        return None
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    _draw_bars(ax, "Governing Utilization Ratio of Each Primary Element", items, cfg,
               _shared_ymax(groups), "No data")
    _legend(fig, cfg, anchor_y=-(0.075 * max_lines + 0.05), ax=ax)
    return _png(fig, cfg["dpi"])


def ur_group_bars_png(groups):
    """2 x 2 panels: UR of every girder / deck check / bracing panel."""
    cfg = _cfg()
    if not any(v is not None for g in groups.values() for _, v in g["items"]):
        return None
    ymax = _shared_ymax(groups)
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 7.2))
    for ax, (name, g) in zip(axes.flat, groups.items()):
        _draw_bars(ax, name, g["items"], cfg, ymax, g.get("message", ""))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _legend(fig, cfg, anchor_y=0.0)
    return _png(fig, cfg["dpi"])


def ur_combined_png(groups):
    """ONE figure: governing UR per element on top, 2 x 2 detail panels below.
    A single figure can never be split across two pages, so the whole summary
    appears together on one page."""
    cfg = _cfg()
    items, _ = _overview_items(groups)
    if not any(v is not None for _, v in items):
        return None
    ymax = _shared_ymax(groups)
    fig = plt.figure(figsize=(7.4, 8.6))
    gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1, 1], hspace=0.78, wspace=0.28,
                          left=0.09, right=0.98, top=0.96, bottom=0.075)
    ax0 = fig.add_subplot(gs[0, :])
    _draw_bars(ax0, "Governing Utilization Ratio of Each Primary Element", items, cfg, ymax)
    for slot, (name, g) in zip(((1, 0), (1, 1), (2, 0), (2, 1)), groups.items()):
        _draw_bars(fig.add_subplot(gs[slot]), name, g["items"], cfg, ymax, g.get("message", ""))
    _legend(fig, cfg, anchor_y=0.0)
    return _png(fig, cfg["dpi"])


# =============================================================================
# 3. Material quantities (Chapter 7)
# =============================================================================
# Keys written by boq_generator.calculate_material_quantities (values are strings,
# "N.A." when a quantity could not be computed). Several keys are SUMMED (cross bracing =
# top chord + bottom chord + diagonals). End diaphragms have no quantity in the BOQ yet:
# add e.g. "end_diaphragm_wt_total" to boq_generator and list it here, and the bar appears.
MATERIAL_KEYS = {
    "girders":        ["steel_girders_wt_total"],
    "cross_bracing":  ["bracing_top_wt_total", "bracing_bot_wt_total", "bracing_diag_wt_total"],
    "end_diaphragms": ["end_diaphragm_wt_total"],
    "concrete_m3":    ["concrete_deck_vol_total"],
    "rebar_mt":       ["rebar_deck_wt_total"],
}
_SUM_GROUPS = {"cross_bracing"}          # these add up every key that has a number


def collect_quantities(inputs):
    """Return {name: value}: steel / reinforcement in MT, concrete in m3 (None = not available)."""
    inputs = inputs or {}
    out = {}
    for name, keys in MATERIAL_KEYS.items():
        vals = [_f(inputs.get(k)) for k in keys]
        vals = [v for v in vals if v is not None]
        if not vals:
            out[name] = None
        elif name in _SUM_GROUPS:
            out[name] = sum(vals)
        else:
            out[name] = vals[0]
    return out


def steel_tonnage_png(q):
    cfg = _cfg()
    names = [("Girders", "girders"), ("Cross\nBracing", "cross_bracing"), ("End\nDiaphragms", "end_diaphragms")]
    data = [(l, q.get(k)) for l, k in names]
    have = [v for _, v in data if v is not None]
    if not have:
        return None
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    vmax = max(have) or 1.0
    shades = [cfg["steel"], "#B9CF6A", "#D9E6A8"]
    for i, (lbl, v) in enumerate(data):
        if v is None:                       # no quantity in the BOQ for this component
            ax.bar(i, vmax * 0.06, width=0.6, color="white", edgecolor="gray", hatch="///",
                   linewidth=0.8, zorder=2)
            ax.text(i, vmax * 0.09, "n/a\n(not in BOQ)", ha="center", va="bottom", fontsize=8,
                    color="gray", style="italic")
            continue
        ax.bar(i, v, width=0.6, color=shades[i % 3], edgecolor="black", linewidth=0.6, zorder=2)
        ax.text(i, v + 0.015 * vmax, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(range(len(data)))
    ax.set_xticklabels([l for l, _ in data], fontsize=9)
    ax.set_ylabel("Structural steel (MT)", fontsize=9)
    ax.set_ylim(0, vmax * 1.25)
    ax.grid(axis="y", alpha=0.3, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.set_title("Structural Steel Tonnage by Component  (total %.2f MT)" % sum(have),
                 fontsize=10, fontweight="bold")
    return _png(fig, cfg["dpi"])


def concrete_vs_rebar_png(q):
    """Two side-by-side panels (own axis and unit each), so the bars are never
    read against each other: concrete volume in m3 and reinforcement weight in MT."""
    cfg = _cfg()
    conc, reb = q.get("concrete_m3"), q.get("rebar_mt")
    if conc is None and reb is None:
        return None
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 4.2))
    for ax, val, col, ylab, fmt, name in (
            (a1, conc, cfg["concrete"], "Concrete volume (m$^3$)", "{:.2f} m$^3$", "Deck concrete"),
            (a2, reb, cfg["rebar"], "Reinforcement weight (MT)", "{:.3f} MT", "Reinforcement steel")):
        ax.set_ylabel(ylab, fontsize=9)
        ax.set_xticks([0])
        ax.set_xticklabels([name], fontsize=9)
        ax.set_xlim(-0.8, 0.8)
        ax.grid(axis="y", alpha=0.3, zorder=0)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        if val is None:
            ax.set_ylim(0, 1)
            ax.text(0, 0.5, "n/a", ha="center", va="center", color="gray", fontsize=10)
            continue
        ax.bar(0, val, width=0.5, color=col, edgecolor="black", linewidth=0.6, zorder=2)
        ax.set_ylim(0, val * 1.25)
        ax.text(0, val * 1.02, fmt.format(val), ha="center", va="bottom", fontsize=10, fontweight="bold")
    title = "Concrete Volume vs Reinforcement Steel Weight"
    if conc and reb:
        title += "\n(reinforcement intensity %.0f kg/m$^3$)" % (reb * 1000.0 / conc)
    fig.suptitle(title, fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    return _png(fig, cfg["dpi"])


# =============================================================================
# 4. One call from generate_report(): draw, save, register
# =============================================================================
def _save(tmp_images, name, data, fig_paths):
    if not data:
        return False
    path = os.path.join(tmp_images, name + ".png")
    with open(path, "wb") as fh:
        fh.write(data)
    fig_paths[name] = path.replace("\\", "/")
    return True


def build_material_charts(tmp_images, inputs, fig_paths):
    """Material quantity charts (Chapter 7). Call this right BEFORE material_charts_tex(),
    after the BOQ quantities have been merged into `inputs` - then it never depends on
    where build_summary_charts() happens to run."""
    os.makedirs(tmp_images, exist_ok=True)
    try:
        q = collect_quantities(inputs)
        logger.info("Material chart quantities found: %s", {k: v for k, v in q.items() if v is not None})
        missing = [k for k, v in q.items() if v is None]
        if missing:
            logger.info("Material chart: no quantity for %s (keys %s)", missing,
                        {k: MATERIAL_KEYS[k] for k in missing})
        _save(tmp_images, "mat_steel", steel_tonnage_png(q), fig_paths)
        _save(tmp_images, "mat_conc_rebar", concrete_vs_rebar_png(q), fig_paths)
    except Exception as exc:
        logger.warning("Material charts skipped: %s", exc)
    return fig_paths


def build_summary_charts(tmp_images, output_dict, inputs, bridge, fig_paths):
    """Create every summary chart. Failures are logged, never raised."""
    os.makedirs(tmp_images, exist_ok=True)
    try:
        groups = collect_ur_groups(output_dict, inputs, bridge)
        _save(tmp_images, "ur_bar_combined", ur_combined_png(groups), fig_paths)
        _save(tmp_images, "ur_bar_overview", ur_overview_bar_png(groups), fig_paths)
        _save(tmp_images, "ur_bar_groups", ur_group_bars_png(groups), fig_paths)
    except Exception as exc:
        logger.warning("UR bar charts skipped: %s", exc)
    build_material_charts(tmp_images, inputs, fig_paths)
    return fig_paths


# =============================================================================
# 5. LaTeX for the figures
# =============================================================================
def _figure(path, caption, label, width=r"0.92\textwidth"):
    return (r"\begin{figure}[H]" "\n" r"\centering" "\n"
            r"\includegraphics[width=" + width + r"]{" + path + "}\n"
            r"\caption{" + caption + "}\n"
            r"\label{" + label + "}\n"
            r"\end{figure}" "\n")


def ur_bar_charts_tex(fig_paths):
    """LaTeX placed at the end of Section 5.5 (Overall Design Check Summary).

    The heading, the sentence and the single combined figure form one block:
    \\needspace starts a new page when the block would not fit, so the heading is
    never separated from the chart and nothing is left half-empty between figures."""
    fp = fig_paths or {}
    intro = ("The charts below show the utilization ratio (UR = Demand / Capacity) of every primary "
             "element. The red dashed line marks UR\\,=\\,1.0: bars below it pass and bars above it fail.")
    head = ("\n" r"\needspace{22cm}" "\n"
            r"\subsection{Utilization Ratio Charts}" "\n"
            r"\label{sec:ur-charts}" "\n\n" + intro + "\n\n")
    if fp.get("ur_bar_combined"):
        return head + _figure(
            fp["ur_bar_combined"],
            "Utilization ratios of the primary elements: governing UR of each element (top), and the "
            "UR of the steel plate girders, concrete deck slab, cross bracing and end diaphragms (below).",
            "fig:ur-charts", r"0.97\textwidth")
    if fp.get("ur_bar_overview") or fp.get("ur_bar_groups"):       # fallback: separate figures
        out = [head]
        if fp.get("ur_bar_overview"):
            out.append(_figure(fp["ur_bar_overview"], "Governing utilization ratio of each primary element.",
                               "fig:ur-overview", r"0.8\textwidth"))
        if fp.get("ur_bar_groups"):
            out.append(_figure(fp["ur_bar_groups"], "Utilization ratios of the primary elements.",
                               "fig:ur-groups", r"\textwidth"))
        return "\n".join(out)
    return ""


def material_charts_tex(fig_paths):
    """LaTeX placed at the end of Chapter 7 (Material Take-off & Quantity Summary)."""
    fp = fig_paths or {}
    if not (fp.get("mat_steel") or fp.get("mat_conc_rebar")):
        return ""
    out = ["\n" r"\section{Material Quantity Charts}" "\n"
           r"\label{sec:material-charts}" "\n\n"
           "The charts summarise the quantities of the material take-off above.\n\n"]
    if fp.get("mat_steel"):
        out.append(_figure(fp["mat_steel"],
                           "Structural steel tonnage (MT) for girders, cross bracing and end diaphragms.",
                           "fig:mat-steel", r"0.75\textwidth"))
    if fp.get("mat_conc_rebar"):
        out.append(_figure(fp["mat_conc_rebar"],
                           "Concrete volume (m$^3$) against reinforcement steel weight (MT).",
                           "fig:mat-conc-rebar", r"0.75\textwidth"))
    return "\n".join(out)