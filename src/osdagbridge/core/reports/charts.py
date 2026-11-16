
"""Charts and traceability helpers for the design report.

All colours come from styles.py (single source of truth).

  build_ur_matrix(output_dict)  -> rows, cols, data   (girders x checks)
  ur_heatmap_png(...)           -> PNG bytes
  ur_overview_tex(...)          -> LaTeX for the "Utilization Overview" section
  design_fingerprint(inputs)    -> short SHA-256 hash of the design inputs
"""
from __future__ import annotations

import hashlib
import io
import json
import textwrap

from . import styles as S
from .table_utils import longtable_raw

# Input keys that change between runs without the design changing.
_VOLATILE = ("date", "time", "timestamp", "path", "file", "folder", "dir")


# --------------------------------------------------------------------------
# Data extraction
# --------------------------------------------------------------------------
def build_ur_matrix(output_dict):
    """Return (rows, cols, data): girders x checks of utilization ratios.

    Reads output_dict["design_results"]["per_girder"][G]["checks"], the same
    DCR-engine data that feeds the "Overall Design Check Summary" table.
    data[i][j] is None where a check does not apply to that girder.
    """
    per_girder = ((output_dict.get("design_results") or {}).get("per_girder")) or {}
    rows = [g for g in per_girder if not str(g).startswith("EB")]
    labels = {}
    for g in rows:
        for chk in (per_girder[g].get("checks") or []):
            cid = chk.get("check_id")
            if cid is not None and chk.get("dcr") is not None:
                labels.setdefault(cid, str(chk.get("name") or f"Check {cid}"))
    try:
        ids = sorted(labels)
    except TypeError:
        ids = sorted(labels, key=str)
    cols = [labels[i] for i in ids]
    data = []
    for g in rows:
        by_id = {c.get("check_id"): c.get("dcr") for c in (per_girder[g].get("checks") or [])}
        data.append([_num(by_id.get(i)) for i in ids])
    return rows, cols, data


def _num(v):
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def headroom_pct(ur):
    """Indicative spare capacity: 1/UR - 1, as a percentage."""
    return (1.0 / ur - 1.0) * 100.0 if ur and ur > 0 else None


def governing(rows, cols, data):
    """(girder, check, ur) of the highest UR, or None."""
    best = None
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            v = data[i][j]
            if v is not None and (best is None or v > best[2]):
                best = (r, c, v)
    return best


# --------------------------------------------------------------------------
# Heatmap
# --------------------------------------------------------------------------
def ur_heatmap_png(rows, cols, data, dpi=None):
    """Girders x checks utilization-ratio heatmap. Returns PNG bytes or None."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    if not rows or not cols:
        return None
    arr = np.array([[np.nan if v is None else v for v in r] for r in data], float)
    if np.all(np.isnan(arr)):
        return None

    warn, fail = S.CHART["warn_from"], S.CHART["fail_from"]
    vmax = max(1.2, float(np.nanmax(arr)))
    bw = S.ACTIVE_THEME == "print_bw"
    cmap = "Greys" if bw else "RdYlGn_r"
    norm = TwoSlopeNorm(vmin=0.0, vcenter=warn, vmax=vmax) if not bw else None

    wrapped = ["\n".join(textwrap.wrap(c, 14)) or c for c in cols]
    fig, ax = plt.subplots(figsize=(max(5.0, 1.15 * len(cols) + 1.8),
                                    max(2.2, 0.62 * len(rows) + 1.6)))
    im = ax.imshow(np.ma.masked_invalid(arr), cmap=cmap, norm=norm,
                   vmin=None if norm else 0.0, vmax=None if norm else vmax, aspect="auto")
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(wrapped, fontsize=8)
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows, fontsize=9)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)

    for i in range(len(rows)):
        for j in range(len(cols)):
            v = arr[i, j]
            if np.isnan(v):
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=7, color="#888888")
            else:
                dark = bw and v > 0.6
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8.5,
                        fontweight="bold" if v > fail else "normal",
                        color="white" if dark else "black")

    i, j = np.unravel_index(np.nanargmax(arr), arr.shape)       # governing cell
    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, lw=2.6, ec="black"))
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("Utilization Ratio", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    if not bw:
        cb.ax.axhline(fail, color=S.CHART["threshold_color"], lw=1.2, ls=S.CHART["threshold_ls"])

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi or S.CHART["dpi"], bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


# --------------------------------------------------------------------------
# LaTeX for the Chapter 5 "Utilization Overview" section
# --------------------------------------------------------------------------
def ur_overview_tex(output_dict, heatmap_path=None, top_n=5):
    rows, cols, data = build_ur_matrix(output_dict)
    gov = governing(rows, cols, data)
    if gov is None:
        return ""
    g, chk, ur = gov
    head = headroom_pct(ur)
    verdict = ("exceeds the limit of 1.0" if ur > 1.0 else
               "is within the limit of 1.0")

    out = [r"""
\section{Utilization Overview}
\label{sec:ur-overview}

The heatmap below shows the utilization ratio (UR = demand / capacity) of every check for every girder, so that the critical element can be found at a glance. Cells run from green (low UR) through amber (UR $\geq 0.8$, near critical) to red (UR $> 1.0$, failing). Cells marked n/a do not apply to that girder, and the governing cell is outlined in black.
"""]
    if heatmap_path:
        out.append(r"""
\begin{center}
\includegraphics[width=\linewidth,keepaspectratio]{""" + heatmap_path + r"""}
\captionof{figure}{Utilization ratio heatmap (girders $\times$ checks)}
\end{center}
""")
    gtxt = (r"\noindent The governing check is \textbf{" + _esc(chk) + r"} on \textbf{" + _esc(g)
            + r"}, with UR $= " + f"{ur:.2f}" + r"$, which " + verdict + ".")
    if head is not None:
        gtxt += (f" Indicative headroom on this check is {head:.0f}\\%." if head >= 0
                 else f" Indicative capacity shortfall on this check is {-head:.0f}\\%.")
    out.append(gtxt + "\n")

    # top-N table
    flat = [(data[i][j], rows[i], cols[j]) for i in range(len(rows))
            for j in range(len(cols)) if data[i][j] is not None]
    flat.sort(reverse=True)
    body = []
    for v, r, c in flat[:top_n]:
        h = headroom_pct(v)
        ur_s = (r"\textcolor{red}{" + f"{v:.2f}" + "}") if v > 1.0 else f"{v:.2f}"
        body.append(f"{_esc(r)} & {_esc(c)} & {ur_s} & "
                    + (f"{h:+.0f}\\%" if h is not None else "---") + r" \\[6pt]" + "\n\\hline")
    out.append("\n\\vspace{1em}\n" + longtable_raw(
        caption=f"Most Utilised Checks (top {min(top_n, len(flat))})",
        col_spec=r"|C{2.0cm}|L{6.4cm}|C{2.4cm}|C{3.0cm}|",
        headers=["Girder", "Check", "UR", "Headroom"],
        body="\n".join(body),
        note=r"Headroom $= 1/\mathrm{UR} - 1$ is indicative only and assumes capacity scales linearly with load.",
    ))
    return "\n".join(out)


def _esc(s):
    s = str(s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}")):
        s = s.replace(a, b)
    return s


# --------------------------------------------------------------------------
# Design fingerprint (traceability)
# --------------------------------------------------------------------------
def design_fingerprint(inputs):
    """16-hex-char SHA-256 fingerprint of the design inputs.

    Compute it BEFORE quantities are merged into the inputs, so the value only
    changes when the user changes the design.
    """
    clean = {}
    for k, v in (inputs or {}).items():
        ks = str(k).lower()
        if any(t in ks for t in _VOLATILE):
            continue
        if isinstance(v, (str, int, float, bool)) or v is None:
            clean[str(k)] = v
    blob = json.dumps(clean, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16].upper()


def fingerprint_display(fp):
    """ABCD-EF01-2345-6789 for reading from a printed page."""
    return "-".join(fp[i:i + 4] for i in range(0, len(fp), 4))


def qr_png(text, scale=8, border=2):
    """QR code for `text` as PNG bytes, or None if no QR library is installed.

    Uses `segno` (pure Python, no TeX package needed). The report then shows
    only the readable fingerprint if segno is missing.
    """
    try:
        import segno
    except ImportError:
        return None
    buf = io.BytesIO()
    segno.make(text, error="m").save(buf, kind="png", scale=scale, border=border)
    return buf.getvalue()