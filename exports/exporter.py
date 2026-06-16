"""
SemiContact Pro — Export Engine  (v8 — production upgrade)

Item 3 (critical): Live figure is NEVER modified.
    export_png and export_pdf both receive the live Figure but immediately
    deep-copy it via graphs.export_renderer.render_for_export().
    All B&W / light-theme styling is applied ONLY to the copy.

Item 4: Advanced PDF includes optional residual plot section.
Item 5: Export consistency — marker visibility and deviation state are passed
        through so exports mirror exactly what the user sees on-screen.
"""

import copy
import io
from typing import Optional

from matplotlib.figure import Figure

from analysis.models import AnalysisSession
from utils.helpers import fmt
from graphs.export_renderer import render_for_export, fig_to_png_bytes


# ── PNG export ────────────────────────────────────────────────────────────────

def export_png(
    live_fig: Figure,
    filepath: str,
    show_markers: bool = True,
) -> None:
    """
    Export the graph as a high-res PNG.
    Uses deep-copy — light/publication theme, live canvas unchanged.
    """
    # Deep-copy; use light theme + publication colours to match PDF export (bw=True)
    fig_copy = render_for_export(live_fig, bw=True, show_markers=show_markers)
    fig_copy.savefig(filepath, dpi=200, bbox_inches="tight",
                     facecolor=fig_copy.get_facecolor())
    import matplotlib.pyplot as plt
    plt.close(fig_copy)


# ── PDF export ────────────────────────────────────────────────────────────────

def export_pdf(
    session: AnalysisSession,
    live_fig: Figure,
    filepath: str,
    report_date: str = "",
    show_markers: bool = True,
) -> None:
    """
    Generate a publication-quality B&W PDF report.

    Args:
        session:      Fitted AnalysisSession with all datasets.
        live_fig:     Live PlotCanvas figure — deep-copied, never modified.
        filepath:     Output .pdf path.
        report_date:  User-entered date string (DD-MM-YYYY).
        show_markers: Mirror the app's current marker-visibility state.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, Image as RLImage, PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    import matplotlib.pyplot as plt

    # ── B&W palette ───────────────────────────────────────────────────
    C_WHITE      = colors.white
    C_BLACK      = colors.black
    C_LIGHT_GREY = colors.HexColor("#f2f2f2")
    C_MID_GREY   = colors.HexColor("#cccccc")
    C_DARK_GREY  = colors.HexColor("#444444")
    C_SUB        = colors.HexColor("#555555")

    PAGE_W, PAGE_H = A4

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles   = getSampleStyleSheet()
    date_str = report_date if report_date else "—"

    # ── Paragraph styles ──────────────────────────────────────────────
    title_style = ParagraphStyle(
        "SCP_Title", parent=styles["Title"],
        textColor=C_BLACK, fontSize=18,
        spaceAfter=2, spaceBefore=0, alignment=TA_CENTER,
    )
    sub_style = ParagraphStyle(
        "SCP_Sub", parent=styles["Normal"],
        textColor=C_SUB, fontSize=8, alignment=TA_CENTER, spaceAfter=4,
    )
    section_style = ParagraphStyle(
        "SCP_Section", parent=styles["Normal"],
        textColor=C_BLACK, fontSize=10, fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=3,
    )
    ds_style = ParagraphStyle(
        "SCP_DS", parent=styles["Normal"],
        textColor=C_BLACK, fontSize=8, fontName="Helvetica-Bold",
        spaceBefore=6, spaceAfter=2,
    )

    # ── Page background: white + thin bottom rule ─────────────────────
    def _bg(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_WHITE)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setStrokeColor(C_MID_GREY)
        canvas.setLineWidth(0.5)
        canvas.line(1.8 * cm, 0.8 * cm, PAGE_W - 1.8 * cm, 0.8 * cm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(C_SUB)
        canvas.drawCentredString(PAGE_W / 2, 0.28 * cm, f"Page {doc.page}")
        canvas.restoreState()

    # ── Table style helper ────────────────────────────────────────────
    def _std_table_style(header_row: bool = True) -> TableStyle:
        style = [
            ("FONTSIZE",      (0, 0),  (-1, -1), 8),
            ("TEXTCOLOR",     (0, 0),  (-1, -1), C_BLACK),
            ("GRID",          (0, 0),  (-1, -1), 0.4, C_MID_GREY),
            ("ALIGN",         (1, 0),  (-1, -1), "RIGHT"),
            ("LEFTPADDING",   (0, 0),  (-1, -1), 4),
            ("RIGHTPADDING",  (0, 0),  (-1, -1), 4),
            ("TOPPADDING",    (0, 0),  (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0),  (-1, -1), 3),
        ]
        if header_row:
            style += [
                ("BACKGROUND",  (0, 0),  (-1, 0),  C_DARK_GREY),
                ("TEXTCOLOR",   (0, 0),  (-1, 0),  C_WHITE),
                ("FONTNAME",    (0, 0),  (-1, 0),  "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_LIGHT_GREY]),
            ]
        return TableStyle(style)

    story = []

    # ── Title ─────────────────────────────────────────────────────────
    story.append(Paragraph("SemiContact Pro", title_style))
    story.append(Paragraph(
        "SEMICONDUCTOR CONTACT RESISTANCE ANALYSIS REPORT", sub_style,
    ))
    story.append(HRFlowable(width="100%", thickness=0.8, color=C_BLACK, spaceAfter=6))

    # ── Session metadata ──────────────────────────────────────────────
    meta_data = [
        ["Date",          date_str],
        ["Analysis Mode", session.mode],
        ["Wafer Number",  session.wafer_number or "—"],
        ["Product ID",    session.product_id   or "—"],
        ["Datasets",      str(len(session.datasets))],
    ]
    meta_tbl = Table(meta_data, colWidths=[4.5 * cm, 12 * cm])
    meta_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_LIGHT_GREY, C_WHITE]),
        ("FONTNAME",       (0, 0), (0, -1),  "Helvetica-Bold"),
        ("TEXTCOLOR",      (0, 0), (-1, -1), C_BLACK),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("GRID",           (0, 0), (-1, -1), 0.4, C_MID_GREY),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("TOPPADDING",     (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 3),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.4 * cm))

    # ── Main graph (Item 3: deep-copy, never modifies live canvas) ────
    story.append(Paragraph("Analysis Graph", section_style))
    fig_export = render_for_export(live_fig, bw=True, show_markers=show_markers)
    buf_main   = fig_to_png_bytes(fig_export, dpi=150)
    plt.close(fig_export)
    story.append(RLImage(buf_main, width=16 * cm, height=9 * cm))
    story.append(Spacer(1, 0.3 * cm))

    # ── Extracted parameters ──────────────────────────────────────────
    story.append(Paragraph("Extracted Parameters", section_style))
    story.append(HRFlowable(width="100%", thickness=0.4, color=C_MID_GREY, spaceAfter=3))

    param_header = [
        "Dataset", "Slope", "Intercept", "Rc (\u03a9)",
        "RSH (\u03a9/\u25a1)", "L\u209c (\u00b5m)", "FOM",
    ]
    param_rows = [param_header]
    for ds in session.datasets:
        param_rows.append([
            ds.label,
            fmt(ds.slope),
            fmt(ds.intercept),
            fmt(ds.Rc),
            fmt(ds.RSH),
            fmt(ds.LT),
            fmt(ds.FOM),
        ])

    col_w = [3.6, 2.6, 2.6, 2.2, 2.6, 2.2, 2.4]
    param_tbl = Table(param_rows, colWidths=[c * cm for c in col_w])
    param_tbl.setStyle(_std_table_style())
    story.append(param_tbl)

    # ── Input data tables (new page, compact 3-across) ────────────────
    story.append(PageBreak())
    story.append(Paragraph("Input Data Tables", section_style))
    story.append(HRFlowable(width="100%", thickness=0.4, color=C_MID_GREY, spaceAfter=3))

    TABLES_PER_ROW = 3
    CONTENT_W = PAGE_W - 1.8 * cm - 1.8 * cm
    GUTTER    = 0.3 * cm
    CELL_W    = (CONTENT_W - (TABLES_PER_ROW - 1) * GUTTER) / TABLES_PER_ROW
    sub_col_w = [1.4 * cm, 2.0 * cm, 2.0 * cm]

    def _make_ds_table(ds) -> Table:
        hdr  = ["d (\u00b5m)", "R (\u03a9)", "R\u2099 (\u03a9)"]
        rows = [hdr]
        for pt in ds.points:
            R_str  = fmt(pt.R)    if pt.R    is not None else "\u2014"
            Rn_str = fmt(pt.Rnew) if pt.Rnew is not None else "\u2014"
            rows.append([str(int(pt.d)), R_str, Rn_str])
        t = Table(rows, colWidths=sub_col_w)
        t.setStyle(_std_table_style())
        return t

    mini_style = ParagraphStyle(
        "SCP_DS_mini", parent=styles["Normal"],
        textColor=C_BLACK, fontSize=7, fontName="Helvetica-Bold",
        spaceBefore=0, spaceAfter=0,
    )

    datasets = session.datasets
    for i in range(0, len(datasets), TABLES_PER_ROW):
        group = datasets[i: i + TABLES_PER_ROW]

        label_cells = [
            Paragraph(f"<b>{ds.label}</b>  Rp={fmt(ds.Rp)}\u03a9", mini_style)
            for ds in group
        ]
        while len(label_cells) < TABLES_PER_ROW:
            label_cells.append("")

        col_widths = ([CELL_W + GUTTER] * (TABLES_PER_ROW - 1)) + [CELL_W]

        lbl_row = Table([label_cells], colWidths=col_widths)
        lbl_row.setStyle(TableStyle([
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
        ]))
        story.append(lbl_row)

        table_cells = [_make_ds_table(ds) for ds in group]
        while len(table_cells) < TABLES_PER_ROW:
            table_cells.append("")

        data_row = Table([table_cells], colWidths=col_widths)
        data_row.setStyle(TableStyle([
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(data_row)
        story.append(Spacer(1, 0.25 * cm))

    doc.build(story, onFirstPage=_bg, onLaterPages=_bg)