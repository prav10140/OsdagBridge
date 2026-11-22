# osdagbridge/core/reports/layout_theme.py
"""Figure layout rules for the whole report (one place, applied to every chapter).

  * apply_figure_theme(tex) : limits the height of every report image, so two
        figures fit on one page instead of one figure per half-empty page.
  * FIGURE_CAPTION_SETUP    : LaTeX for the preamble - figure names and notes are
        written BELOW the figure and CENTRED.

Neither needs a change in executive_summary.py / chap4.py / chap6.py.
The only values are in FIGURE (override them in styles.py as  FIGURE = dict(...)).
"""
import re

try:
    from . import styles as S
except Exception:                     # standalone testing
    S = None

FIGURE = {"max_height": r"0.27\textheight",        # tall enough to read, small enough to pair up
          "heatmap_max_height": r"0.37\textheight"}  # Utilization heatmap (Section 5.6)
FIGURE.update((getattr(S, "FIGURE", None) or {}) if S else {})

# Figure captions: bold label, centred, below the picture. Tables keep their caption
# ABOVE the table (set separately in the preamble).
FIGURE_CAPTION_SETUP = (
    "\\captionsetup[figure]{labelfont=bf,justification=centering,singlelinecheck=true,"
    "position=bottom,skip=6pt}\n"
    "\\captionsetup[subfigure]{justification=centering,singlelinecheck=true}\n"
)

# images that are NOT limited: charts (sized by their own code), QR code, logos
_SKIP_PREFIX = ("ur_bar", "mat_", "fingerprint", "qr")      # ur_heatmap is handled separately

_INCLUDE = re.compile(r"\\includegraphics(?:\[(?P<opts>[^\]]*)\])?\{(?P<path>[^}]*)\}")


def apply_figure_theme(tex, max_height=None):
    """Add height=<max> and keepaspectratio to each report image (images/ folder)."""
    cap = max_height or FIGURE["max_height"]

    def fix(m):
        path = m.group("path").replace("\\", "/")
        if "/images/" not in path and not path.startswith("images/"):
            return m.group(0)                          # logos etc. (assets/ folder)
        name = path.rsplit("/", 1)[-1].lower()
        if name.startswith(_SKIP_PREFIX):
            return m.group(0)
        opts = (m.group("opts") or "").strip()
        if "height=" in opts:
            return m.group(0)                          # already sized explicitly
        limit = FIGURE["heatmap_max_height"] if name.startswith("ur_heatmap") else cap
        parts = [p for p in (opts.split(",") if opts else []) if p.strip()]
        if not any(p.strip().startswith("width=") for p in parts):
            parts.append(r"width=\linewidth")
        parts.append("height=" + limit)
        if "keepaspectratio" not in [p.strip() for p in parts]:
            parts.append("keepaspectratio")
        return r"\includegraphics[" + ",".join(parts) + "]{" + m.group("path") + "}"

    return _INCLUDE.sub(fix, tex)