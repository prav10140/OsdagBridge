THEMES = {
    "osdag":    {"primary": "91B014", "pass": "2E7D32", "warn": "F9A825", "fail": "C62828"},
    "navy":     {"primary": "1F4E79", "pass": "2E7D32", "warn": "F9A825", "fail": "C62828"},
    # photocopy-safe: greys only (charts should add hatching in this theme)
    "print_bw": {"primary": "000000", "pass": "555555", "warn": "999999", "fail": "000000"},
}
ACTIVE_THEME = "osdag"
C = THEMES[ACTIVE_THEME]

# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------
PAGE = dict(
    paper="a4paper",
    font_pt="12pt",
    margin="1in",
    footskip="36pt",      # room for rule + "* Software default value" note
    headheight="18pt",    # fancyhdr needs 17.5pt with setstretch 1.15 (no warning)
    line_stretch="1.15",
)

# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------
TABLE = dict(
    tabcolsep="6pt",
    arraystretch="1.12",
    rule_width="0.5pt",
    extrarowheight="0.6pt",
    lt_pre="0pt",
    lt_post="6pt",
    header_fill_pct=30,   # column-header row  : osdagGreen!30
    banner_fill_pct=15,   # girder/panel banner: osdagGreen!15
    block_gap="10pt",     # space between two girder blocks
    row_gap="6pt",        # extra height at the end of each row
)

# --------------------------------------------------------------------------
# Header / footer text
# --------------------------------------------------------------------------
HEADER_RULE = dict(color="osdagGreen", height="1pt", after="2pt")
FOOTER_RULE = dict(color="osdagGreen", height="1pt", after="6pt")
FOOTER_LEFT = r"Osdag $|$ FOSSEE $|$ Indian Institute of Technology Bombay"
FOOTER_RIGHT = r"Page \thepage\ of \pageref{LastPage}"
SOFTWARE_DEFAULT_NOTE = r"* Software default value"

# --------------------------------------------------------------------------
# Charts (matplotlib) - used by the chart module
# --------------------------------------------------------------------------
CHART = dict(
    dpi=200,
    figsize=(7, 4),
    threshold_color="#C62828",
    threshold_ls="--",
    pass_color="#" + C["pass"],
    warn_color="#" + C["warn"],
    fail_color="#" + C["fail"],
    warn_from=0.8,        # UR >= 0.8 is "near critical" (amber)
    fail_from=1.0,        # UR >  1.0 fails (red)
)