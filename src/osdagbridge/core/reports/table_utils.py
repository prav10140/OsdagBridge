# osdagbridge/core/reports/table_utils.py
"""LaTeX longtable helpers for the report.

girder_longtable : one shaded Girder / Panel column (or banner) per block.
longtable_raw    : for tables whose body rows are already written as LaTeX.
apply_table_theme: whole-document pass: gray table theme + column-style
                   Parameter/Value tables.

Colours: every table shade is GRAY. The values come from styles.py
(TABLE_HEADER_HEX / TABLE_LABEL_HEX) when defined, otherwise the defaults below.
The green of the report is kept for the header/footer rules and the title page only.
"""

try:                                   # inside the osdagbridge package
    from . import styles as S
except ImportError:                    # standalone testing
    import styles as S

import re

# ---- look & feel -----------------------------------------------------------
GRAY_HDR_HEX = getattr(S, "TABLE_HEADER_HEX", "D9D9D9")     # header rows
GRAY_LABEL_HEX = getattr(S, "TABLE_LABEL_HEX", "EDEDED")    # label column / banners

# LaTeX colour definitions: put COLOR_DEFS in the preamble (report_generator.preamble)
COLOR_DEFS = ("\\definecolor{osdagGrayHdr}{HTML}{" + GRAY_HDR_HEX + "}\n"
              "\\definecolor{osdagGray}{HTML}{" + GRAY_LABEL_HEX + "}\n")

HEADER_FILL = "osdagGrayHdr"
BANNER_FILL = "osdagGray"
LABEL_FILL = BANNER_FILL            # shading of Girder / label columns
BLOCK_GAP = S.TABLE["block_gap"]    # vertical gap between two girder blocks
# \* = never break between a banner and its first row. NOTE: do NOT put a
# \hline/\cline/\hrule after it: \hline lets longtable break there (banner
# stranded) and a bare \hrule overshoots the table when \LTleft=\fill.
BANNER_END = r"\\*"
ROW_GAP = S.TABLE["row_gap"]        # extra height at the end of each row
GIRDER_COL_CM = 1.5                 # width of the Girder column

# 2-column tables with these headers are drawn "column style": the first column is
# shaded and bold, and there is no shaded header row (like the title-page table).
_KV_HEADERS = (("parameter", "value"), ("property", "value"))


def _is_kv(headers):
    return bool(headers) and len(headers) == 2 and \
        tuple(str(h).strip().lower() for h in headers) in _KV_HEADERS


def _head_row(headers, fill=True):
    cells = " & ".join(rf"\textbf{{{h}}}" for h in headers)
    rc = rf"\rowcolor{{{HEADER_FILL}}} " if fill else ""
    return rf"{rc}{cells} \\ \hline"


def _shell_open(caption, col_spec, headers, n, fill=True, note=None):
    """\\begin{longtable} + caption + note + first head + repeated head. Caption appears once."""
    out = [rf"\begin{{longtable}}{{{col_spec}}}",
           rf"\caption{{{caption}}} \\"]
    out += note_rows(col_spec, n, note)
    out.append(r"\hline")
    if headers:
        head = _head_row(headers, fill)
        out += [head, r"\endfirsthead",
                rf"\multicolumn{{{n}}}{{l}}"
                rf"{{\small\textit{{\tablename~\thetable\ (continued)}}}} \\",
                r"\hline", head, r"\endhead"]
    else:
        out += [r"\endfirsthead",
                rf"\multicolumn{{{n}}}{{l}}"
                rf"{{\small\textit{{\tablename~\thetable\ (continued)}}}} \\",
                r"\hline", r"\endhead"]
    return out


def _note(note):
    """Plain paragraph note (only used where a table has no \\endlastfoot)."""
    if not note:
        return []
    return [r"\par\smallskip\noindent{\footnotesize\textit{Note: " + note + r"}}\par"]


def _table_width(col_spec, n):
    """LaTeX length equal to the table width (column widths + padding + rules)."""
    widths = [float(x) for x in re.findall(r"\{(\d+(?:\.\d+)?)cm\}", col_spec)]
    if len(widths) != n:                       # l / c / r columns: width unknown
        return r"\linewidth"
    return (r"\dimexpr " + f"{sum(widths):.2f}" + r"cm+" + str(2 * n) + r"\tabcolsep+"
            + str(n + 1) + r"\arrayrulewidth\relax")


def note_rows(col_spec, n, note):
    """Lines that print `note` directly under the table caption, as part of the table.
    (A note placed after the table, or in \\endlastfoot, can be pushed onto a page of its
    own together with a repeated header. Under the caption it always stays with the table.)"""
    if not note:
        return []
    w = _table_width(col_spec, n)
    return [r"\multicolumn{" + str(n) + r"}{@{}l@{}}{\parbox[t]{" + w + r"}{\footnotesize\textit{Note: "
            + note + r"}}} \\[3pt]"]


def _scale_widths(col_spec, take_cm):
    """Shrink every {X cm} width in col_spec so a new column of `take_cm` fits."""
    nums = [float(x) for x in re.findall(r"\{(\d+(?:\.\d+)?)cm\}", col_spec)]
    total = sum(nums)
    if total <= take_cm + 1:
        return col_spec
    k = (total - take_cm) / total
    return re.sub(r"\{(\d+(?:\.\d+)?)cm\}",
                  lambda m: "{%.2fcm}" % (float(m.group(1)) * k), col_spec)


def _girder_colspec(width_cm=GIRDER_COL_CM):
    return (r">{\columncolor{" + LABEL_FILL + r"}\centering\arraybackslash\bfseries}"
            r"p{" + f"{width_cm:.2f}" + "cm}")


def _shade_first_column(col_spec, bold=False):
    """Shade the first column of an existing column spec."""
    pre = r">{\columncolor{" + LABEL_FILL + r"}" + (r"\bfseries" if bold else "") + "}"
    return re.sub(r"^\{?\|", lambda m: m.group(0) + pre, col_spec, count=1)


def girder_longtable(caption, col_spec, headers, blocks,
                     banner="Girder {name}", note=None, label=None,
                     row_gap=ROW_GAP, block_gap=BLOCK_GAP, layout=None):
    """
    blocks : [(name, rows), ...]  rows = list of lists of cell strings.
             Works for any number of girders / panels / locations.

    layout : "column" -> a shaded first column (Girder / Panel) on every row
             "banner" -> one full-width banner row above each block
             None     -> "column" when banner is "Girder {name}" or "Panel {name}",
                         otherwise "banner" (e.g. banner="{name}" for locations).
    """
    if layout is None:
        layout = "column" if banner in ("Girder {name}", "Panel {name}") else "banner"
    if layout == "column":
        return _column_longtable(caption, col_spec, headers, blocks,
                                 first_title=banner.replace("{name}", "").strip() or "Girder",
                                 note=note, label=label, row_gap=row_gap, block_gap=block_gap)
    n = len(headers)
    out = _shell_open(caption + (rf"\label{{{label}}}" if label else ""),
                      col_spec, headers, n, note=note)

    for b, (name, rows) in enumerate(blocks):
        if b > 0:
            out.append(rf"\noalign{{\vskip {block_gap}}}")
            out.append(r"\hline")
        title = banner.format(name=name)
        out.append(rf"\multicolumn{{{n}}}{{|l|}}{{\cellcolor{{{BANNER_FILL}}}\textbf{{{title}}}}} " + BANNER_END)
        for i, row in enumerate(rows):
            star = "*" if (i == 0 and len(rows) > 1) else ""
            out.append(" & ".join(row) + rf" \\{star}[{row_gap}] \hline")

    out.append(r"\end{longtable}")
    return "\n".join(out)


def _split_cols(col_spec):
    """Split '|L{5cm}|C{3cm}|' into ['L{5cm}', 'C{3cm}'] (rules removed)."""
    return re.findall(r"[A-Za-z]\{[^}]*\}|[lcr]", col_spec.replace("|", " "))


MAX_MERGED_ROWS = 10     # taller blocks flow across pages (name repeated on each row)


def _column_longtable(caption, col_spec, headers, blocks, first_title,
                      note, label, row_gap, block_gap):
    """Longtable with a shaded Girder (or Panel) column showing each name ONCE,
    centred next to all of that girder's rows.

    Each girder is a single unbreakable table row: the name sits in the first
    cell and the girder's rows are a small nested table in the remaining cells.
    Because it is one row, a block can never be split across a page, so the
    merged name can never end up on the wrong page (the old multirow problem).
    """
    scaled = _scale_widths(col_spec, GIRDER_COL_CM + 0.45)
    cols = _split_cols(scaled)
    spec = "|" + _girder_colspec() + scaled.lstrip("{")
    all_headers = [first_title] + list(headers)
    n = len(all_headers)
    nested_spec = "|".join(cols) + "|"
    out = _shell_open(caption + (rf"\label{{{label}}}" if label else ""), spec, all_headers, n, note=note)

    for b, (name, rows) in enumerate(blocks):
        if b > 0:
            out.append(r"\hline")
        if len(rows) > MAX_MERGED_ROWS:                 # too tall for one page
            for i, row in enumerate(rows):
                lab = name if i == 0 else r"\textcolor{black!45}{" + name + "}"
                out.append(lab + " & " + " & ".join(row) + rf" \\[{row_gap}] \hline")
            continue
        inner = (r" \\[" + row_gap + r"] \hline" + "\n").join(" & ".join(r) for r in rows)
        out.append(
            name + " & \\multicolumn{" + str(n - 1) + r"}{@{}l@{}}{\begin{tabular}[c]{" + nested_spec + "}\n"
            + inner + r" \\[" + row_gap + "]" + "\n"
            + r"\end{tabular}} \\ \hline")
    out.append(r"\end{longtable}")
    return "\n".join(out)


def longtable_raw(caption, col_spec, headers=None, body="", note=None,
                  n_cols=None, label=None):
    """body : rows already in LaTeX, each ending with \\\\ and \\hline."""
    n = len(headers) if headers else n_cols
    if n is None:
        raise ValueError("longtable_raw needs headers or n_cols")
    fill = True
    if headers and str(headers[0]).strip().lower() == "girder":
        col_spec = _shade_first_column(col_spec, bold=True)
    elif _is_kv(headers):                       # Parameter | Value -> column style
        col_spec = _shade_first_column(col_spec, bold=True)
        fill = False
    out = _shell_open(caption + (rf"\label{{{label}}}" if label else ""),
                      col_spec, headers, n, fill=fill, note=note)
    out.append(body)
    out.append(r"\end{longtable}")
    return "\n".join(out)


# --------------------------------------------------------------------------
# Whole-report theme pass
# --------------------------------------------------------------------------
_ENV_RE = re.compile(r"\\begin\{(longtable|tabular)\}(.*?)\\end\{\1\}", re.S)
_ROW_AFTER_HLINE = re.compile(r"\\hline[ \t]*\n(?P<row>[^\n]*?)\\\\")
_GREEN_FILL = re.compile(r"\\(rowcolor|columncolor|cellcolor)\{osdagGreen(?:![0-9.]+)?\}")


def _all_bold_or_empty(cells):
    return (len(cells) >= 2 and any(cells)
            and all(c == "" or c.startswith(r"\textbf{") for c in cells))


def _plain(cell):
    return re.sub(r"^\\textbf\{(.*)\}$", r"\1", cell.strip()).strip().lower()

_LT_HEAD_RE = re.compile(
    r"(\\hline[ \t]*\n)(?P<row>[^\n]*?\\\\(?:\[[^\]]*\])?[ \t]*\n?[ \t]*\\hline)"
)


def _add_longtable_heads(block):
    """Insert \\endfirsthead / \\endhead into hand-written longtables that lack them."""
    if r"\endhead" in block or r"\endfirsthead" in block:
        return block
    hm = _LT_HEAD_RE.search(block)
    if not hm:
        return block
    row_line = hm.group("row")
    clean = re.sub(r"\\rowcolor\{[^}]*\}\s*", "", row_line.split(r"\\")[0])
    cells = [c.strip() for c in clean.split("&")]
    if not _all_bold_or_empty(cells):
        return block
    n = len(cells)
    rep = (
        hm.group(1) + row_line + "\n"
        r"\endfirsthead" + "\n"
        rf"\multicolumn{{{n}}}{{l}}{{\small\textit{{\tablename~\thetable\ (continued)}}}} \\" + "\n"
        r"\hline" + "\n"
        + row_line + "\n"
        r"\endhead"
    )
    return block[:hm.start()] + rep + block[hm.end():]


def apply_table_theme(tex):
    """Give every remaining hand-written table the report's gray theme.

    * header row (all bold cells)                  -> gray header fill
    * "Parameter | Value" header                   -> COLUMN style: shaded bold first
                                                      column, no shaded header row
    * key/value table (bold label, plain value)    -> shaded label column
    * header whose first cell is "Girder"/empty    -> shaded first column
    Any green table fill (osdagGreen!NN in \\rowcolor / \\columncolor / \\cellcolor)
    that other modules produced is turned into the matching gray.
    Tables built with the helpers above already carry the theme and are left alone.
    Safe to run once on the finished document.
    """
    header_fill = r"\rowcolor{" + HEADER_FILL + r"} "

    def fix(m):
        block = m.group(0)
        if m.group(1) == "longtable":
            # longtable requires "\\" after \caption{...}; many hand-written tables omit it
            block = re.sub(r"(?m)^(\\caption\{.*\})[ \t]*$(?=\n\\hline)", r"\1 \\\\", block)
        has_row = r"\rowcolor" in block
        has_col = r"\columncolor" in block
        shade_first = False
        kv_style = False
        pieces = []
        first = True
        for rm in _ROW_AFTER_HLINE.finditer(block):
            cells = [c.strip() for c in rm.group("row").split("&")]
            if _all_bold_or_empty(cells):
                if first and len(cells) == 2 and tuple(_plain(c) for c in cells) in _KV_HEADERS:
                    kv_style = True
                if kv_style:
                    if first:
                        shade_first = True
                else:
                    if not has_row:
                        pieces.append((rm.start("row"), header_fill))
                    if first and (_plain(cells[0]) == "" or "girder" in cells[0].lower()):
                        shade_first = True
            elif first and len(cells) >= 2 and cells[0].startswith(r"\textbf{"):
                shade_first = True                  # key / value table
            first = False

        if not has_row and r"\multirow{2}{*}{\makecell{\textbf{Load}" in block:
            block = re.sub(r"(\\hline[ \t]*\n)(\\multirow\{2\}\{\*\}\{\\makecell\{\\textbf\{Load\})",
                           lambda mm: mm.group(1) + header_fill + mm.group(2), block)
            block = re.sub(r"(\\cline\{2-9\}[ \t]*\n\s*\n)(&)",
                           lambda mm: mm.group(1) + header_fill + mm.group(2), block)

        if pieces:
            out, pos = [], 0
            for idx, text in sorted(pieces):
                out.append(block[pos:idx]); out.append(text); pos = idx
            out.append(block[pos:])
            block = "".join(out)

        if shade_first and not has_col:
            bold = r"\bfseries" if kv_style else ""
            block = re.sub(r"(\\begin\{(?:longtable|tabular)\}\{)\|",
                           lambda mm: mm.group(1) + "|" + r">{\columncolor{" + LABEL_FILL + "}" + bold + "}",
                           block, count=1)
        if m.group(1) == "longtable":
            block = _add_longtable_heads(block)
        return block

    tex = _ENV_RE.sub(fix, tex)

    # any green table fill left over (e.g. from charts.py tables) -> gray
    def to_gray(mm):
        return "\\" + mm.group(1) + "{" + (HEADER_FILL if mm.group(1) == "rowcolor" else BANNER_FILL) + "}"
    return _GREEN_FILL.sub(to_gray, tex)