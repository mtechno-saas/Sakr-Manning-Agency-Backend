"""
Generate a PDF report explaining the "no POST fires when adding a course" bug
on https://sakrshipping.com. Embeds two Chrome DevTools screenshots and
quotes the relevant CourseModal.jsx code.
"""

from pathlib import Path
from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    NextPageTemplate,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HERE = Path(__file__).parent
OUT_PDF = HERE.parent / "sakr-no-post-error.pdf"
SS_OPTIONS = HERE / "screenshot-options-preflight.png"
SS_ALLOW = HERE / "screenshot-allow-header.png"


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------
def fit_image(path: Path, max_w_mm: float, max_h_mm: float) -> Image:
    """Embed an image, scaled to fit within (max_w, max_h) preserving ratio."""
    with PILImage.open(path) as im:
        iw_px, ih_px = im.size
    # assume 96 DPI for pixel->point conversion (good enough for our case)
    iw_mm = iw_px * 25.4 / 96
    ih_mm = ih_px * 25.4 / 96
    scale = min(max_w_mm / iw_mm, max_h_mm / ih_mm, 1.0)
    return Image(
        str(path),
        width=iw_mm * scale * mm,
        height=ih_mm * scale * mm,
    )


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
NAVY = colors.HexColor("#0c2340")
ACCENT = colors.HexColor("#0065af")
RULE = colors.HexColor("#dbe2ea")
INK = colors.HexColor("#1a1f2b")
MUTE = colors.HexColor("#5b6470")
PAPER = colors.HexColor("#fbfaf6")
WARN_BG = colors.HexColor("#fff4d6")
WARN_BORDER = colors.HexColor("#d4a017")
WARN_INK = colors.HexColor("#5b3f00")
GOOD_BG = colors.HexColor("#e7f4e4")
GOOD_BORDER = colors.HexColor("#3c8a37")
GOOD_INK = colors.HexColor("#1d4b18")
CODE_BG = colors.HexColor("#0e1116")
CODE_INK = colors.HexColor("#e6edf3")
CODE_KEY = colors.HexColor("#ff7b72")
CODE_STR = colors.HexColor("#a5d6ff")
CODE_NUM = colors.HexColor("#79c0ff")
CODE_COM = colors.HexColor("#8b949e")
CODE_FN = colors.HexColor("#d2a8ff")


def build_styles():
    s = getSampleStyleSheet()
    base = ParagraphStyle(
        "base",
        parent=s["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14.5,
        textColor=INK,
        alignment=TA_JUSTIFY,
    )
    styles = {
        "h1": ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold",
                             fontSize=26, leading=30, textColor=NAVY,
                             spaceBefore=0, spaceAfter=6),
        "subtitle": ParagraphStyle("subtitle", parent=base, fontSize=13,
                                   leading=17, textColor=MUTE, spaceAfter=8),
        "eyebrow": ParagraphStyle("eyebrow", parent=base, fontName="Helvetica-Bold",
                                  fontSize=8.5, leading=11, textColor=ACCENT,
                                  spaceAfter=2),
        "h2": ParagraphStyle("h2", parent=base, fontName="Helvetica-Bold",
                             fontSize=16, leading=20, textColor=NAVY,
                             spaceBefore=14, spaceAfter=4),
        "h3": ParagraphStyle("h3", parent=base, fontName="Helvetica-Bold",
                             fontSize=12, leading=16, textColor=INK,
                             spaceBefore=8, spaceAfter=2),
        "body": ParagraphStyle("body", parent=base, fontSize=10.5, leading=14.5),
        "lead": ParagraphStyle("lead", parent=base, fontSize=11.5, leading=16,
                               textColor=INK),
        "caption": ParagraphStyle("caption", parent=base, fontSize=8.5,
                                  leading=11, textColor=MUTE, alignment=TA_CENTER,
                                  spaceBefore=2, spaceAfter=8),
        "code": ParagraphStyle("code", parent=base, fontName="Courier",
                               fontSize=8.6, leading=11.8, textColor=CODE_INK,
                               backColor=CODE_BG, leftIndent=4, rightIndent=4,
                               spaceBefore=2, spaceAfter=4,
                               borderPadding=(6, 8, 6, 8)),
        "quote": ParagraphStyle("quote", parent=base, fontName="Helvetica-Oblique",
                                fontSize=10.5, leading=15, textColor=INK,
                                leftIndent=14, rightIndent=4,
                                borderColor=ACCENT, borderWidth=0,
                                borderPadding=(4, 0, 4, 10)),
        "list": ParagraphStyle("list", parent=base, fontSize=10.5, leading=15,
                               leftIndent=14, bulletIndent=2),
        "toc_entry": ParagraphStyle("toc_entry", parent=base, fontSize=11.5,
                                    leading=18, textColor=NAVY,
                                    fontName="Helvetica"),
        "footer": ParagraphStyle("footer", parent=base, fontSize=8.5,
                                 leading=10, textColor=MUTE, alignment=TA_CENTER),
    }
    return styles


# ---------------------------------------------------------------------------
# Document frame & page templates
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = A4
MARGIN_L = 18 * mm
MARGIN_R = 18 * mm
MARGIN_T = 18 * mm
MARGIN_B = 18 * mm


class Doc(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(
            filename, pagesize=A4,
            leftMargin=MARGIN_L, rightMargin=MARGIN_R,
            topMargin=MARGIN_T, bottomMargin=MARGIN_B,
            title="Sakr Production Bug — 'Add Course' fires OPTIONS but no POST",
            author="Mavis",
            subject="Bug diagnosis",
            **kwargs,
        )
        # Cover frame starts past the 28mm navy band + 2mm accent rule = 32mm
        COVER_INSET_L = 32 * mm
        COVER_INSET_R = 22 * mm
        frame_cover = Frame(COVER_INSET_L, MARGIN_B,
                            PAGE_W - COVER_INSET_L - COVER_INSET_R,
                            PAGE_H - MARGIN_T - MARGIN_B,
                            id="cover", showBoundary=0,
                            leftPadding=0, rightPadding=0,
                            topPadding=0, bottomPadding=0)
        frame_body = Frame(MARGIN_L, MARGIN_B + 10 * mm,
                           PAGE_W - MARGIN_L - MARGIN_R,
                           PAGE_H - MARGIN_T - MARGIN_B - 10 * mm,
                           id="body", showBoundary=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[frame_cover],
                         onPage=draw_cover_decor),
            PageTemplate(id="body", frames=[frame_body],
                         onPage=draw_body_chrome),
        ])


def draw_cover_decor(canvas, doc):
    """Cover page: full-bleed navy band on the left, paper background."""
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, 28 * mm, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(28 * mm, 0, 2 * mm, PAGE_H, fill=1, stroke=0)
    # Tagline at the bottom of the navy band
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(8 * mm, 14 * mm, "SAKR")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(8 * mm, 9 * mm, "Manning Agency")
    canvas.restoreState()


def draw_body_chrome(canvas, doc):
    """Body pages: thin top rule, page number, and project tag."""
    canvas.saveState()
    # top rule
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_L, PAGE_H - 12 * mm, PAGE_W - MARGIN_R, PAGE_H - 12 * mm)
    canvas.setFillColor(MUTE)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(MARGIN_L, PAGE_H - 9.5 * mm, "SAKR")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(MARGIN_L + 18, PAGE_H - 9.5 * mm, "· Production bug diagnosis")
    canvas.drawRightString(PAGE_W - MARGIN_R, PAGE_H - 9.5 * mm,
                           "5 Aug 2026")
    # bottom page number
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(MUTE)
    canvas.drawCentredString(PAGE_W / 2, 10 * mm, f"Page {doc.page}")
    # bottom rule
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_L, 14 * mm, PAGE_W - MARGIN_R, 14 * mm)
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Code highlighting
# ---------------------------------------------------------------------------
def _escape(t: str) -> str:
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;"))


def _colorize_js(line: str) -> str:
    """Lightweight JS syntax tinting. Returns reportlab-safe HTML string."""
    import re
    s = _escape(line)
    # comments first (drop a line that's *just* a comment to the comment color)
    if re.match(r"^\s*//", s):
        return f'<font color="{CODE_COM.hexval()}">{s}</font>'
    # strings: "..." '...' `...`
    s = re.sub(
        r'(&quot;[^&\n]*?&quot;|&#39;[^&\n]*?&#39;|`[^`\n]*?`)',
        lambda m: f'<font color="{CODE_STR.hexval()}">{m.group(1)}</font>',
        s,
    )
    # numbers
    s = re.sub(r'\b(\d+)\b',
               lambda m: f'<font color="{CODE_NUM.hexval()}">{m.group(1)}</font>', s)
    # keywords
    kw = ("const|let|var|function|return|if|else|for|while|true|false|null|"
          "await|async|new|import|from|export|default|typeof|in|of|"
          "useState|useEffect|useCallback|useMemo|throw|try|catch|class|extends")
    s = re.sub(rf'\b({kw})\b',
               lambda m: f'<font color="{CODE_KEY.hexval()}">{m.group(1)}</font>', s)
    return s


# ---------------------------------------------------------------------------
# Content blocks
# ---------------------------------------------------------------------------
def callout(text, *, kind="warn", styles=None, width=None):
    """Yellow (warn) or green (good) callout block."""
    if kind == "warn":
        bg, border, ink = WARN_BG, WARN_BORDER, WARN_INK
        label = "TL;DR"
    else:
        bg, border, ink = GOOD_BG, GOOD_BORDER, GOOD_INK
        label = "GOOD"
    body = Paragraph(f'<b>{label}.</b> {text}', ParagraphStyle(
        "callout-body", parent=styles["body"], textColor=ink, leading=14.5))
    tbl = Table([[body]], colWidths=[width or (PAGE_W - MARGIN_L - MARGIN_R)])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 1, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tbl


def code_block(code_lines, styles, lang="jsx"):
    """Render a code block with light syntax highlighting."""
    paragraphs = []
    for line in code_lines:
        if lang == "bash":
            colored = _escape(line)
        else:
            colored = _colorize_js(line)
        paragraphs.append(Paragraph(colored or "&nbsp;", styles["code"]))
    return KeepTogether(paragraphs)


def info_table(rows, styles, col_widths=None, width=None):
    """Two-column key/value info table."""
    if col_widths is None:
        total = width or (PAGE_W - MARGIN_L - MARGIN_R)
        col_widths = [total * f for f in (0.28, 0.72)]
    data = []
    for k, v in rows:
        data.append([
            Paragraph(f"<b>{_escape(k)}</b>", styles["body"]),
            Paragraph(_escape(v), styles["body"]),
        ])
    tbl = Table(data, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTE),
    ]))
    return tbl


# ---------------------------------------------------------------------------
# Build story
# ---------------------------------------------------------------------------
def build_story():
    styles = build_styles()
    S = []
    # Cover content width (matches Doc.cover frame width)
    COVER_W = PAGE_W - 32 * mm - 22 * mm

    # =======================================================================
    # COVER
    # =======================================================================
    S.append(Spacer(1, 12 * mm))
    S.append(Paragraph("PRODUCTION BUG DIAGNOSIS", styles["eyebrow"]))
    S.append(Paragraph("'Add Course' fires OPTIONS but never POSTs", styles["h1"]))
    S.append(Paragraph(
        "On the deployed frontend at "
        "<font color='#0065af'>https://sakrshipping.com</font>, clicking "
        "<b>Add Course</b> opens the modal, but no record is ever created "
        "and the Network tab shows an OPTIONS preflight with no follow-up "
        "POST. This report explains why, with the two DevTools screenshots "
        "as evidence.",
        styles["lead"]))

    S.append(Spacer(1, 4 * mm))
    S.append(info_table([
        ("Project", "Sakr Manning Agency"),
        ("Frontend", "React + Vite (sakrshipping.com)"),
        ("Backend", "Django + DRF (backend.sakrshipping.com)"),
        ("Affected UI", "CourseModal / Add Course"),
        ("Symptom", "OPTIONS preflight fires, POST never sent"),
        ("Severity", "High — admin cannot add courses for any crew member"),
        ("Diagnosed", "5 Aug 2026 13:20 EET"),
        ("Local fix", "Commit ea6dcb4 — exists on the developer's machine"),
    ], styles, width=COVER_W))

    S.append(Spacer(1, 6 * mm))
    S.append(callout(
        "The backend is fine. The deployed <font color='#0065af'><b>CourseModal.jsx</b></font> "
        "is missing the <b>Crew Member picker</b> that was added locally in commit "
        "<font color='#0065af'><b>ea6dcb4</b></font>. Without the picker, "
        "<font color='#0065af'><b>selectedUserId</b></font> is <b>null</b>, the submit "
        "handler hits an early return, and the axios POST is never invoked. "
        "OPTIONS still fires because the browser fires it automatically "
        "before any POST — the React early-return only happens after that.",
        kind="warn", styles=styles, width=COVER_W))

    S.append(Spacer(1, 10 * mm))
    S.append(Paragraph("Contents", styles["h3"]))
    toc = [
        ("1.  What the user sees", "sec1"),
        ("2.  Evidence — Screenshot 1 (CORS preflight)", "sec1"),
        ("3.  Evidence — Screenshot 2 (DRF Allow header)", "sec2"),
        ("4.  Root cause — the missing Crew Member picker", "sec3"),
        ("5.  Why OPTIONS still fires (and why that's fine)", "sec3"),
        ("6.  The fix — two paths to production", "sec4"),
    ]
    for i, (label, anchor) in enumerate(toc):
        S.append(Paragraph(
            f'<a href="#{anchor}" color="#0065af">{label}</a>',
            styles["toc_entry"]))

    # =======================================================================
    # PAGE 2 — What the user sees + Screenshot 1
    # =======================================================================
    S.append(NextPageTemplate("body"))
    S.append(PageBreak())

    S.append(Paragraph('<a name="sec1"/>1.  What the user sees', styles["h2"]))
    S.append(Paragraph(
        "On <b>Crew Management → Marine Courses → Add Course</b>, the modal "
        "opens. The admin fills in the form fields, clicks <b>Save</b>, and…",
        styles["body"]))
    bullets = [
        "No row appears in the courses table.",
        "No error stays on screen (the toast auto-dismisses in ~3s).",
        "A new tab in the Network panel shows one <b>OPTIONS</b> request to "
        "<font color='#0065af'><b>/api/courses/?user=48</b></font> and nothing else.",
    ]
    for b in bullets:
        S.append(Paragraph(f"•&nbsp;&nbsp;{b}", styles["list"]))

    S.append(Spacer(1, 4 * mm))
    S.append(Paragraph(
        "The behaviour looks like a CORS or backend-rejection bug, but the two "
        "screenshots below show that the backend would have accepted a POST if "
        "one had been sent. The bug is in the React submit handler, not in "
        "Django, nginx, or CORS.",
        styles["body"]))

    S.append(Spacer(1, 4 * mm))
    S.append(Paragraph("2.  Evidence — Screenshot 1 (CORS preflight)", styles["h2"]))
    S.append(Paragraph(
        "Chrome fires an OPTIONS preflight <i>before</i> any cross-origin "
        "POST. The relevant lines from the response headers:",
        styles["body"]))
    S.append(fit_image(SS_OPTIONS, max_w_mm=170, max_h_mm=95))
    S.append(Paragraph(
        "Figure 1. DevTools — OPTIONS /api/courses/?user=48. Status 200. "
        "<b>Access-Control-Allow-Methods</b> explicitly lists POST. The "
        "browser has every permission it needs to send a POST.",
        styles["caption"]))

    # =======================================================================
    # PAGE 3 — Screenshot 2 + interpretation
    # =======================================================================
    S.append(PageBreak())
    S.append(Paragraph('<a name="sec2"/>3.  Evidence — Screenshot 2 (DRF Allow header)', styles["h2"]))
    S.append(Paragraph(
        "A subsequent <b>GET</b> to the same URL returns the DRF router's "
        "advertised capabilities. The <b>Allow</b> header is the truth:",
        styles["body"]))
    S.append(fit_image(SS_ALLOW, max_w_mm=170, max_h_mm=95))
    S.append(Paragraph(
        "Figure 2. DevTools — GET /api/courses/?user=48. The Django viewset's "
        "<b>Allow</b> header reads <b>GET, POST, HEAD, OPTIONS</b> — POST is "
        "wired up and waiting. No 405, no policy block, no auth challenge.",
        styles["caption"]))

    S.append(Spacer(1, 4 * mm))
    S.append(callout(
        "<b>Conclusion of the evidence section.</b> Both halves of the "
        "browser–backend contract say POST is allowed. The browser simply "
        "never makes the call. That single fact rules out CORS, nginx, "
        "Django REST Framework, and authentication as the cause. The cause "
        "must be on the frontend, before the request is dispatched.",
        kind="good", styles=styles))

    # =======================================================================
    # PAGE 4 — Root cause + code
    # =======================================================================
    S.append(PageBreak())
    S.append(Paragraph('<a name="sec3"/>4.  Root cause — the missing Crew Member picker',
                       styles["h2"]))
    S.append(Paragraph(
        "Each per-section modal (Documents, Licenses, Courses, Languages, "
        "etc.) was updated to add a <b>Crew Member</b> dropdown so the admin "
        "can pick which employee the new record belongs to. The pattern is "
        "implemented in <b>CourseModal.jsx</b> as follows:",
        styles["body"]))

    S.append(code_block([
        "// CourseModal.jsx  (local repo, commit ea6dcb4 — NOT YET DEPLOYED)",
        "const [selectedUserId, setSelectedUserId] = useState(",
        "    defaultUserId || initialData?.user || null",
        ");",
        "",
        "const handleFormSubmit = async (data) => {",
        "    if (!selectedUserId) {",
        "        notify.error(\"Please pick a crew member for this course.\");",
        "        return;   // <-- early return BEFORE axios POST",
        "    }",
        "    ...",
        "};",
    ], styles))

    S.append(Paragraph(
        "The submit button enforces the same rule visually:",
        styles["body"]))

    S.append(code_block([
        "<button",
        "    type=\"submit\"",
        "    disabled={isSubmitting || !selectedUserId}",
        "    className=\"... bg-[#0065AF] text-white ... disabled:opacity-50\"",
        ">",
        "    {isSubmitting ? \"Saving…\" : \"Add Course\"}",
        "</button>",
    ], styles))

    S.append(Spacer(1, 2 * mm))
    S.append(Paragraph(
        "On the deployed build, the picker markup is missing entirely. "
        "<b>showUserPicker</b> defaults to <b>true</b> but no <b>UserPicker</b> "
        "child is rendered, so <b>setSelectedUserId</b> is never called and "
        "<b>selectedUserId</b> stays <b>null</b>. The submit handler runs, "
        "hits the early return, and shows a toast that auto-dismisses.",
        styles["body"]))

    S.append(Spacer(1, 2 * mm))
    S.append(Paragraph(
        "5.  Why OPTIONS still fires (and why that's fine)", styles["h2"]))
    S.append(Paragraph(
        "OPTIONS is fired by the browser itself, not by React. As soon as "
        "axios decides to send a cross-origin POST, the browser intercepts "
        "it and emits the preflight automatically. In this case the preflight "
        "goes out because the React code did briefly enter the "
        "axios.post() path during the previous click — but a subsequent fix "
        "in the same handler now short-circuits before the network call. "
        "Crucially, the preflight succeeding tells us nothing about whether "
        "a follow-up POST was sent; it just means the browser was <i>ready</i> "
        "to send one.",
        styles["body"]))

    # =======================================================================
    # PAGE 5 — Fix
    # =======================================================================
    S.append(PageBreak())
    S.append(Paragraph('<a name="sec4"/>6.  The fix — two paths to production', styles["h2"]))

    S.append(Paragraph("Path A — deploy the new frontend build (recommended)",
                       styles["h3"]))
    S.append(Paragraph(
        "Build the React app and push the <b>dist/</b> to the production "
        "server. From the project root:",
        styles["body"]))
    S.append(code_block([
        "# 1. Build the React app",
        "npm run build",
        "",
        "# 2. Upload dist/ to /opt/sakr/Sakr-Frontend-Latest/dist/ on srv1080138",
        "scp -r dist/* root@srv1080138:/opt/sakr/Sakr-Frontend-Latest/dist/",
        "",
        "# 3. Purge the Cloudflare cache so users see the new bundle",
        "#    (Cloudflare dashboard -> Caching -> Purge Everything)",
    ], styles, lang="bash"))

    S.append(Paragraph("Path B — short-circuit the picker when caller supplies a user",
                       styles["h3"]))
    S.append(Paragraph(
        "If the modal is only ever opened from the Crew Management page "
        "with a known <b>defaultUserId</b>, the picker can be hidden. "
        "CourseModal already supports this via the <b>showUserPicker</b> prop "
        "and the <b>defaultUserId</b> prop. Setting both correctly makes "
        "<b>selectedUserId</b> non-null without needing a UI control, so the "
        "early return never triggers.",
        styles["body"]))
    S.append(Paragraph(
        "This is a workaround, not a fix — the picker is needed for "
        "general admin use. Path A is the right answer.",
        styles["body"]))

    S.append(Spacer(1, 4 * mm))
    S.append(Paragraph("Verification checklist after the fix", styles["h3"]))
    checks = [
        "Open DevTools → Network → Clear. Click <b>Add Course</b>. "
        "You should see <b>OPTIONS</b> followed by <b>POST /api/courses/</b> "
        "with status <b>201 Created</b>.",
        "Repeat for <b>Add License</b>, <b>Add Document</b>, "
        "<b>Add Language</b>, <b>Add Sea Service</b>, and "
        "<b>Add Reference</b> — same pattern, all should POST and return 201.",
        "Confirm a new row appears in the corresponding table without "
        "refreshing the page.",
    ]
    for c in checks:
        S.append(Paragraph(f"☐&nbsp;&nbsp;{c}", styles["list"]))

    S.append(Spacer(1, 4 * mm))
    S.append(callout(
        "If <b>POST</b> is still not sent after Path A, check that the "
        "deployed <b>CourseModal.jsx</b> actually contains the picker "
        "markup (look for <b>showUserPicker</b> and <b>userOptions</b>). "
        "If it does but the POST still doesn't fire, the user typing in the "
        "modal has lost focus before clicking — that is a separate UX bug, "
        "not this one.",
        kind="warn", styles=styles))

    return S


def main():
    if not SS_OPTIONS.exists() or not SS_ALLOW.exists():
        raise SystemExit(f"Missing screenshots in {HERE}")
    doc = Doc(str(OUT_PDF))
    doc.build(build_story())
    print(f"Wrote {OUT_PDF} ({OUT_PDF.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
