# osdagbridge/core/reports/table_utils.py
"""LaTeX longtable helpers for the report.

girder_longtable : one banner per girder/panel/section, any number of blocks.
longtable_raw    : for tables whose body rows are already written as LaTeX.

Both give: caption once, header repeated on every page ("Table X.Y (continued)"),
a note under the table, and no stranded banner at the bottom of a page.
"""

# ---- look & feel (later: move to styles.py) --------------------------------
HEADER_FILL = r"osdagGreen!30"
BANNER_FILL = r"osdagGreen!15"
BLOCK_GAP = "10pt"      # vertical gap between two girder blocks
# \* = never break between a banner and its first row. NOTE: do NOT put a
# \hline/\cline/\hrule after it: \hline lets longtable break there (banner
# stranded) and a bare \hrule overshoots the table when \LTleft=\fill.
BANNER_END = r"\\*"
ROW_GAP = "6pt"         # extra height at the end of each row


def _head_row(headers):
    cells = " & ".join(rf"\textbf{{{h}}}" for h in headers)
    return rf"\rowcolor{{{HEADER_FILL}}} {cells} \\ \hline"


def _shell_open(caption, col_spec, headers, n):
    """\\begin{longtable} + first head + repeated head. Caption appears once."""
    out = [rf"\begin{{longtable}}{{{col_spec}}}",
           rf"\caption{{{caption}}} \\",
           r"\hline"]
    if headers:
        head = _head_row(headers)
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
    if not note:
        return []
    return [r"\par\smallskip\noindent{\footnotesize\textit{Note: " + note + r"}}\par"]


def girder_longtable(caption, col_spec, headers, blocks,
                     banner="Girder {name}", note=None, label=None,
                     row_gap=ROW_GAP, block_gap=BLOCK_GAP):
    """
    blocks : [(name, rows), ...]  rows = list of lists of cell strings.
             Works for any number of girders / panels / locations.
    """
    n = len(headers)
    out = _shell_open(caption + (rf"\label{{{label}}}" if label else ""),
                      col_spec, headers, n)

    for b, (name, rows) in enumerate(blocks):
        if b > 0:
            # visible gap between blocks (closes the box, opens a new one)
            out.append(rf"\noalign{{\vskip {block_gap}}}")
            out.append(r"\hline")
        title = banner.format(name=name)
        # \\* : no page break between banner and first row
        out.append(rf"\multicolumn{{{n}}}{{|l|}}{{\cellcolor{{{BANNER_FILL}}}\textbf{{{title}}}}} " + BANNER_END)
        for i, row in enumerate(rows):
            star = "*" if (i == 0 and len(rows) > 1) else ""
            out.append(" & ".join(row) + rf" \\{star}[{row_gap}] \hline")

    out.append(r"\end{longtable}")
    out += _note(note)
    return "\n".join(out)


def longtable_raw(caption, col_spec, headers=None, body="", note=None,
                  n_cols=None, label=None):
    """body : rows already in LaTeX, each ending with \\\\ and \\hline."""
    n = len(headers) if headers else n_cols
    if n is None:
        raise ValueError("longtable_raw needs headers or n_cols")
    out = _shell_open(caption + (rf"\label{{{label}}}" if label else ""),
                      col_spec, headers, n)
    out.append(body)
    out.append(r"\end{longtable}")
    out += _note(note)
    return "\n".join(out)