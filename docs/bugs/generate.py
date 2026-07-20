"""
Bugs Documentation Generator
============================

Generates docs/bugs/bugs.pdf from the BUGS list below.

How to add a new bug:
1. Append a new entry to the BUGS list in this file
2. Each entry is a dict with the fields documented below
3. Drop the screenshot into docs/bugs/screenshots/ and reference it by filename
4. Run:  python docs/bugs/generate.py

The script is self-contained — no external services, no internet, no node.

Bug entry schema (all fields optional except id/title/endpoint):
{
    "id": "BUG-001",
    "title": "Short title",
    "endpoint": "/api/companies/2/",
    "section": "Companies / Detail",
    "severity": "Critical | High | Medium | Low",
    "status": "Open | In Progress | Fixed | Won't Fix | Duplicate",
    "date": "2026-07-20",
    "reporter": "Mahmoud",
    "screenshot": "BUG-001.png",     # file in docs/bugs/screenshots/
    "description": "What's happening",
    "steps": ["Step 1", "Step 2", "..."],
    "expected": "What should happen",
    "actual": "What actually happens",
    "root_cause": "Backend / Frontend / Data / Config",
    "fix": "What was done to fix it (empty if Open)",
    "notes": "Anything else",
}
"""

import os
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, KeepTogether,
    Table, TableStyle, NextPageTemplate, PageTemplate, Frame,
)
from reportlab.pdfgen import canvas

# ---------------------------------------------------------------------------
# Bug data — append new bugs here
# ---------------------------------------------------------------------------

BUGS = [
    # Example placeholder — replace or add below
    # {
    #     "id": "BUG-001",
    #     "title": "PUT /api/companies/2/ returns 400 when only one field is sent",
    #     "endpoint": "/api/companies/{id}/",
    #     "section": "Companies / Detail",
    #     "severity": "High",
    #     "status": "Open",
    #     "date": "2026-07-14",
    #     "reporter": "Mahmoud",
    #     "screenshot": None,
    #     "description": (
    #         "The Edit Company form sends a partial payload via PUT. The backend "
    #         "rejects with 400 because PUT requires all required fields "
    #         "(company_name, contact_email) on full-replace semantics."
    #     ),
    #     "steps": [
    #         "Open the Edit Company modal for company id 2",
    #         "Change only the Address field",
    #         "Click Save Changes",
    #         "Open browser DevTools → Network tab",
    #     ],
    #     "expected": "PATCH-style update succeeds, only the changed field is saved",
    #     "actual": "PUT 400 Bad Request, no field values updated",
    #     "root_cause": "Frontend — src/services/Dashboard/companiesApi.js:108 uses api.put() for partial updates. PUT semantics require all required fields.",
    #     "fix": "",
    #     "notes": "Switch api.put → api.patch in the updateCompany method. PATCH accepts partial payloads natively.",
    # },
]

# ---------------------------------------------------------------------------
# Section ordering — endpoints are grouped by Django app, then by URL
# ---------------------------------------------------------------------------

SECTIONS = [
    {
        "title": "Companies",
        "subtitle": "/api/companies/*",
        "endpoints": [
            ("/api/companies/", "List & Filter"),
            ("/api/companies/", "Create (POST)"),
            ("/api/companies/{id}/", "Detail (GET)"),
            ("/api/companies/{id}/", "Update (PUT)"),
            ("/api/companies/{id}/", "Partial Update (PATCH)"),
            ("/api/companies/{id}/", "Delete (DELETE)"),
            ("/api/companies/stats/", "Stats"),
            ("/api/companies/job-orders/", "Job Orders CRUD"),
            ("/api/companies/job-positions/", "Job Positions CRUD"),
            ("/api/companies/job-positions/apply/", "Quick Apply"),
        ],
    },
    {
        "title": "Interviews",
        "subtitle": "/api/interviews/*",
        "endpoints": [
            ("/api/interviews/", "List"),
            ("/api/interviews/", "Create (POST)"),
            ("/api/interviews/{id}/", "Detail (GET)"),
            ("/api/interviews/{id}/", "Update (PUT / PATCH)"),
            ("/api/interviews/{id}/", "Delete (DELETE)"),
            ("/api/interviews/status/", "Status counts"),
            ("/api/interviews/reminders/", "Reminders CRUD"),
            ("/api/interviews/reminders/upcoming/", "Upcoming"),
        ],
    },
    {
        "title": "Authentication & Users",
        "subtitle": "/api/users/*, /api/login/*",
        "endpoints": [
            ("/api/login/", "JWT obtain"),
            ("/api/login/refresh/", "JWT refresh"),
            ("/api/users/", "Users CRUD"),
            ("/api/users/declarations/", "Declarations"),
            ("/api/users/certificates/", "Certificates"),
            ("/api/auth/google/", "Google auth"),
            ("/api/verify-email/", "Email verify"),
        ],
    },
    {
        "title": "Other apps",
        "subtitle": "Ships, finance, contracts, etc.",
        "endpoints": [
            ("/api/ships/", "Ships"),
            ("/api/finance/", "Finance"),
            ("/api/contracts-gen/", "Contracts"),
            ("/api/tickets-papers/", "Tickets & papers"),
            ("/api/core/", "Reference data"),
            ("/api/logistics/", "Logistics"),
            ("/api/compliance/", "Compliance"),
            ("/api/licenses/", "Licenses"),
            ("/api/courses/", "Courses"),
            ("/api/vaccinations/", "Vaccinations"),
        ],
    },
]

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

styles = getSampleStyleSheet()

NAVY = colors.HexColor("#0b3b66")
BLUE = colors.HexColor("#0e62a8")
RED = colors.HexColor("#c0392b")
AMBER = colors.HexColor("#d68910")
GREEN = colors.HexColor("#1e8449")
GREY = colors.HexColor("#7f8c8d")
LIGHT = colors.HexColor("#ecf0f1")
DARK = colors.HexColor("#2c3e50")

title_style = ParagraphStyle(
    "TitleBig", parent=styles["Title"],
    fontName="Helvetica-Bold", fontSize=32, textColor=NAVY,
    alignment=TA_CENTER, spaceAfter=4*mm, leading=36,
)
subtitle_style = ParagraphStyle(
    "Subtitle", parent=styles["Normal"],
    fontName="Helvetica", fontSize=14, textColor=GREY,
    alignment=TA_CENTER, spaceAfter=6*mm,
)
section_h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontName="Helvetica-Bold", fontSize=18, textColor=NAVY,
    spaceBefore=4*mm, spaceAfter=2*mm, leading=22,
)
section_h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=13, textColor=BLUE,
    spaceBefore=3*mm, spaceAfter=1*mm, leading=16,
)
body_style = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontName="Helvetica", fontSize=10, textColor=DARK,
    leading=14, alignment=TA_JUSTIFY, spaceAfter=2*mm,
)
bug_id_style = ParagraphStyle(
    "BugID", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=11, textColor=NAVY,
    leading=14,
)
bug_title_style = ParagraphStyle(
    "BugTitle", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=12, textColor=DARK,
    leading=15, spaceAfter=2*mm,
)
label_style = ParagraphStyle(
    "Label", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=9, textColor=GREY,
    leading=12,
)
value_style = ParagraphStyle(
    "Value", parent=styles["Normal"],
    fontName="Helvetica", fontSize=9, textColor=DARK,
    leading=12,
)
toc_style = ParagraphStyle(
    "TOC", parent=styles["Normal"],
    fontName="Helvetica", fontSize=11, textColor=DARK,
    leading=18, leftIndent=4*mm,
)
footer_style = ParagraphStyle(
    "Footer", parent=styles["Normal"],
    fontName="Helvetica", fontSize=8, textColor=GREY,
    alignment=TA_CENTER,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SEVERITY_COLOR = {
    "Critical": colors.HexColor("#7b1a1a"),
    "High": RED,
    "Medium": AMBER,
    "Low": colors.HexColor("#3498db"),
}
STATUS_COLOR = {
    "Open": RED,
    "In Progress": AMBER,
    "Fixed": GREEN,
    "Won't Fix": GREY,
    "Duplicate": colors.HexColor("#8e44ad"),
}


def severity_badge(severity):
    color = SEVERITY_COLOR.get(severity, GREY)
    return Paragraph(
        f'<para backColor="{color.hexval()}" textColor="white" '
        f'align="center"><b> {severity or "—"} </b></para>',
        ParagraphStyle("badge", fontName="Helvetica-Bold", fontSize=9, leading=12, alignment=TA_CENTER),
    )


def status_badge(status):
    color = STATUS_COLOR.get(status, GREY)
    return Paragraph(
        f'<para backColor="{color.hexval()}" textColor="white" '
        f'align="center"><b> {status or "—"} </b></para>',
        ParagraphStyle("badge", fontName="Helvetica-Bold", fontSize=9, leading=12, alignment=TA_CENTER),
    )


def kv_row(label, value):
    if value is None or value == "":
        return None
    p = Table(
        [[Paragraph(label.upper(), label_style), Paragraph(str(value), value_style)]],
        colWidths=[3.2*cm, 13.5*cm],
    )
    p.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
    ]))
    return p


def bug_card(bug, screenshot_dir):
    """Build a single bug card as a KeepTogether flowable."""
    elements = []

    # Header row: BUG-ID — Title — Severity badge — Status badge
    sev = severity_badge(bug.get("severity"))
    sts = status_badge(bug.get("status"))
    header = Table(
        [[
            Paragraph(f'<font color="#0b3b66"><b>{bug.get("id", "BUG-?")}</b></font>', bug_id_style),
            Paragraph(bug.get("title", "(no title)"), bug_title_style),
            sev, sts,
        ]],
        colWidths=[2.2*cm, 9.6*cm, 2.5*cm, 2.5*cm],
    )
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, NAVY),
    ]))
    elements.append(header)
    elements.append(Spacer(1, 2*mm))

    # Metadata table
    meta_rows = [
        kv_row("Endpoint", bug.get("endpoint")),
        kv_row("Section", bug.get("section")),
        kv_row("Date", bug.get("date")),
        kv_row("Reporter", bug.get("reporter")),
    ]
    for row in meta_rows:
        if row:
            elements.append(row)
    elements.append(Spacer(1, 1*mm))

    # Description
    if bug.get("description"):
        elements.append(Paragraph("<b>Description</b>", section_h2))
        elements.append(Paragraph(bug["description"], body_style))

    # Steps
    if bug.get("steps"):
        elements.append(Paragraph("<b>Steps to Reproduce</b>", section_h2))
        for i, step in enumerate(bug["steps"], 1):
            elements.append(Paragraph(f"{i}. {step}", body_style))

    # Expected / Actual
    if bug.get("expected") or bug.get("actual"):
        ea = Table(
            [[
                Paragraph("<b>Expected</b>", section_h2),
                Paragraph("<b>Actual</b>", section_h2),
            ],
            [Paragraph(bug.get("expected", "—"), body_style),
             Paragraph(bug.get("actual", "—"), body_style)]],
            colWidths=[8.3*cm, 8.4*cm],
        )
        ea.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.5, GREY),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, GREY),
            ("BACKGROUND", (0, 0), (-0, -1), colors.HexColor("#eafaf1")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fdedec")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(ea)
        elements.append(Spacer(1, 2*mm))

    # Screenshot
    if bug.get("screenshot"):
        img_path = Path(screenshot_dir) / bug["screenshot"]
        if img_path.exists():
            try:
                img = Image(str(img_path), width=15*cm, height=8*cm, kind="proportional")
                img.hAlign = "CENTER"
                elements.append(Paragraph("<b>Screenshot</b>", section_h2))
                elements.append(img)
                elements.append(Paragraph(
                    f'<para align="center"><font size="8" color="#7f8c8d"><i>{bug["screenshot"]}</i></font></para>',
                    body_style,
                ))
            except Exception as e:
                elements.append(Paragraph(
                    f'<i>(screenshot present but failed to render: {e})</i>',
                    body_style,
                ))
        else:
            elements.append(Paragraph(
                f'<i>(screenshot file not found: {img_path})</i>',
                body_style,
            ))
        elements.append(Spacer(1, 2*mm))

    # Root cause
    if bug.get("root_cause"):
        elements.append(Paragraph(f"<b>Root Cause</b> — {bug['root_cause']}", body_style))

    # Fix
    if bug.get("fix"):
        elements.append(Paragraph("<b>Fix Applied</b>", section_h2))
        elements.append(Paragraph(bug["fix"], body_style))

    # Notes
    if bug.get("notes"):
        elements.append(Paragraph("<b>Notes</b>", section_h2))
        elements.append(Paragraph(bug["notes"], body_style))

    return KeepTogether(elements)


def section_summary_table(endpoints_with_bugs):
    """A summary table per section: endpoint | # bugs | open | fixed."""
    header = ["Endpoint", "Description", "Bugs", "Open", "Fixed"]
    data = [header]
    for ep, desc, bugs in endpoints_with_bugs:
        opens = sum(1 for b in bugs if b.get("status") in ("Open", "In Progress"))
        fixeds = sum(1 for b in bugs if b.get("status") == "Fixed")
        data.append([ep, desc, str(len(bugs)), str(opens), str(fixeds)])

    t = Table(data, colWidths=[5.5*cm, 5.5*cm, 1.8*cm, 1.8*cm, 1.8*cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# ---------------------------------------------------------------------------
# Page templates — header/footer
# ---------------------------------------------------------------------------

def header_footer(canvas_obj, doc):
    canvas_obj.saveState()
    width, height = A4
    # Header line
    canvas_obj.setStrokeColor(NAVY)
    canvas_obj.setLineWidth(1.2)
    canvas_obj.line(2*cm, height - 1.5*cm, width - 2*cm, height - 1.5*cm)
    canvas_obj.setFont("Helvetica-Bold", 9)
    canvas_obj.setFillColor(NAVY)
    canvas_obj.drawString(2*cm, height - 1.2*cm, "Sakr Manning Agency — Bug Tracker")
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GREY)
    canvas_obj.drawRightString(width - 2*cm, height - 1.2*cm, "Confidential — Internal use only")
    # Footer
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(2*cm, 1.5*cm, width - 2*cm, 1.5*cm)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GREY)
    canvas_obj.drawString(2*cm, 1.1*cm, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    canvas_obj.drawRightString(width - 2*cm, 1.1*cm, f"Page {doc.page}")
    canvas_obj.restoreState()


def cover_decoration(canvas_obj, doc):
    """Decorative cover page — no header/footer."""
    canvas_obj.saveState()
    width, height = A4
    # Top color band
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, height - 8*cm, width, 8*cm, fill=1, stroke=0)
    # Accent stripe
    canvas_obj.setFillColor(BLUE)
    canvas_obj.rect(0, height - 8.6*cm, width, 0.6*cm, fill=1, stroke=0)
    # Title text on band
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont("Helvetica-Bold", 28)
    canvas_obj.drawCentredString(width / 2, height - 4*cm, "Bug Tracker")
    canvas_obj.setFont("Helvetica", 14)
    canvas_obj.drawCentredString(width / 2, height - 5*cm, "Sakr Manning Agency — Frontend & Backend")
    # Bottom strip
    canvas_obj.setFillColor(NAVY)
    canvas_obj.rect(0, 0, width, 1.5*cm, fill=1, stroke=0)
    canvas_obj.setFillColor(colors.white)
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawCentredString(
        width / 2, 0.6*cm,
        f"Generated {datetime.now().strftime('%Y-%m-%d')}  •  Source: docs/bugs/generate.py",
    )
    canvas_obj.restoreState()


# ---------------------------------------------------------------------------
# Build the document
# ---------------------------------------------------------------------------

def build():
    here = Path(__file__).parent
    out_path = here / "bugs.pdf"
    screenshot_dir = here / "screenshots"

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2*cm,
        title="Sakr Bug Tracker",
        author="Mavis",
    )

    story = []

    # ---- Cover page ----
    cover_spacer = Spacer(1, 9*cm)
    story.append(cover_spacer)
    story.append(Paragraph("Bug Tracker", title_style))
    story.append(Paragraph("Sakr Manning Agency — Frontend & Backend", subtitle_style))

    # Stats box on cover
    total = len(BUGS)
    by_status = {}
    by_severity = {}
    for b in BUGS:
        s = b.get("status", "Open")
        v = b.get("severity", "—")
        by_status[s] = by_status.get(s, 0) + 1
        by_severity[v] = by_severity.get(v, 0) + 1

    cover_stats = [
        ["Total bugs", str(total)],
        ["Open", str(by_status.get("Open", 0))],
        ["In Progress", str(by_status.get("In Progress", 0))],
        ["Fixed", str(by_status.get("Fixed", 0))],
        ["Critical", str(by_severity.get("Critical", 0))],
        ["High", str(by_severity.get("High", 0))],
    ]
    cover_tbl = Table(cover_stats, colWidths=[6*cm, 4*cm], rowHeights=[10*mm]*6)
    cover_tbl.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, GREY),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
    ]))
    story.append(Spacer(1, 2*cm))
    story.append(cover_tbl)
    story.append(PageBreak())

    # ---- Table of Contents ----
    story.append(Paragraph("Table of Contents", section_h1))
    story.append(Spacer(1, 4*mm))
    toc_entries = []
    for i, sec in enumerate(SECTIONS, 1):
        n_bugs = sum(1 for b in BUGS if any(ep == b.get("endpoint") for ep, _ in sec["endpoints"]))
        toc_entries.append(Paragraph(
            f'<b>{i}. {sec["title"]}</b> &nbsp;&nbsp;<font color="#7f8c8d">({sec["subtitle"]} — {n_bugs} bug{"s" if n_bugs != 1 else ""})</font>',
            toc_style,
        ))
    for e in toc_entries:
        story.append(e)
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        f'<i>Last updated {datetime.now().strftime("%Y-%m-%d %H:%M")}. '
        f'Regenerate with: <b>python docs/bugs/generate.py</b></i>',
        ParagraphStyle("note", parent=body_style, textColor=GREY, fontSize=9),
    ))
    story.append(PageBreak())

    # ---- Sections ----
    for sec in SECTIONS:
        story.append(Paragraph(sec["title"], section_h1))
        story.append(Paragraph(f'<font color="#7f8c8d"><i>{sec["subtitle"]}</i></font>', body_style))
        story.append(Spacer(1, 3*mm))

        # Summary table
        rows = []
        for ep, desc in sec["endpoints"]:
            bugs_here = [b for b in BUGS if b.get("endpoint") == ep]
            rows.append((ep, desc, bugs_here))
        story.append(section_summary_table(rows))
        story.append(Spacer(1, 4*mm))

        # Bug cards
        any_bugs = False
        for ep, desc, bugs_here in rows:
            if not bugs_here:
                continue
            any_bugs = True
            story.append(Paragraph(desc, section_h2))
            for bug in bugs_here:
                story.append(bug_card(bug, screenshot_dir))
                story.append(Spacer(1, 6*mm))

        if not any_bugs:
            story.append(Paragraph(
                '<i>No bugs recorded for this section yet. '
                'Append entries to the BUGS list in generate.py and re-run.</i>',
                body_style,
            ))

        story.append(PageBreak())

    # ---- Build with templates ----
    page_template = PageTemplate(
        id="cover", frames=[Frame(2*cm, 2*cm, A4[0] - 4*cm, A4[1] - 4*cm, id="cover")],
        onPage=cover_decoration,
    )
    body_template = PageTemplate(
        id="body", frames=[Frame(2*cm, 2.2*cm, A4[0] - 4*cm, A4[1] - 4.2*cm, id="body")],
        onPage=header_footer,
    )
    doc.addPageTemplates([page_template, body_template])

    doc.build(story)
    print(f"OK -> {out_path}  ({out_path.stat().st_size:,} bytes, {len(BUGS)} bug{'s' if len(BUGS) != 1 else ''})")


if __name__ == "__main__":
    build()
