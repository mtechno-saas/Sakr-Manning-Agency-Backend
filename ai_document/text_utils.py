"""Text utilities for the Sakr form parser.

Pure helpers used by :mod:`ai_document.extractors.sakr_template`.

The Sakr "Seafarer Employment Application" form (revision 1.3, May 2022) is
laid out in Word as a single big table. After
:class:`ai_document.document_processor.DocumentProcessor` extracts text and
tables, the result is:

    * ``text`` — a string where each non-empty line is either a single
      cell value OR several cells joined by ``" | "`` (the cell separator
      used by the processor for the row's visible cells).
    * ``tables`` — a list of 2-D lists, one per actual ``<table>`` element
      in the document. The big form table has ~22 columns; the
      qualifications / references / etc. cells are placed at fixed
      column indices (e.g. cell[0] = Certificate Name, cell[14] = Issued
      By, cell[20] = Issued At). Empty cells are preserved as ``""``.

So the *line shape* in the text is one of:

    * ``"Label"``                       (label, value on next line)
    * ``"Label | Value"``               (label and value on same line)
    * ``"Label | Value | Label2 | Value2"``  (multiple pairs on one line)
    * ``"Fluent | Good ✓ | Average | Poor"`` (checkbox group line)
    * ``""``                            (blank)

The section parsers in :mod:`ai_document.extractors.sakr_template` use
``text`` for line-oriented sections (1, 2, 3, 6, 11, 12) and ``tables``
for tabular sections (4, 5, 7, 8, 9, 10).
"""

from __future__ import annotations

import re
import unicodedata


# All "checked" markers we have seen in real Sakr-form output.
CHECK_MARKERS: tuple[str, ...] = ("✓", "☑", "☒", "✔", "✗", "[X]", "[x]")

_WS_RE = re.compile(r"[\t\u00A0\u2003\u2009]+")


def normalize_text(text: str) -> str:
    """Light-touch cleanup: NFKC unicode, tab/space normalisation, line strip."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = _WS_RE.sub(" ", text)
    lines = [ln.strip() for ln in text.split("\n")]
    return "\n".join(lines).strip()


def is_checked(token: str) -> bool:
    """Return True if ``token`` contains a checkbox marker character."""
    if not token:
        return False
    return any(marker in token for marker in CHECK_MARKERS)


def strip_checkbox_marker(token: str) -> str:
    """Return ``token`` with checkbox markers and surrounding whitespace removed."""
    if not token:
        return ""
    for marker in CHECK_MARKERS:
        token = token.replace(marker, "")
    return token.strip()


# ── Cell tokenisation ───────────────────────────────────────────────────

def tokenize_line(line: str) -> list[str]:
    """Split a single line into cell tokens (drop empty cells)."""
    if not line:
        return []
    out: list[str] = []
    for cell in line.split("|"):
        c = cell.strip()
        if c:
            out.append(c)
    return out


def tokenize_lines(text: str) -> list[list[str]]:
    """Return one list of cell tokens per non-blank line."""
    if not text:
        return []
    normalised = normalize_text(text)
    return [tokenize_line(ln) for ln in normalised.split("\n") if ln.strip()]


# ── Section boundary detection (text) ──────────────────────────────────

_SECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("1_personal_details", re.compile(r"^\s*1\.\s*PERSONAL\s+DETAILS\s*$", re.IGNORECASE)),
    ("2_education",        re.compile(r"^\s*2\.\s*EDUCATION\s*$", re.IGNORECASE)),
    ("3_contact_details",  re.compile(r"^\s*3\.\s*CONTACT\s+DETAILS\s*$", re.IGNORECASE)),
    ("4_travel_documents", re.compile(r"^\s*4\.\s*TRAVEL\s+DOCUMENTS\s*$", re.IGNORECASE)),
    (
        "5_professional_qualification_certificate_of_competency",
        re.compile(r"^\s*5\.\s*PROFESSIONAL\s+QUALIFICATION", re.IGNORECASE),
    ),
    (
        "6_next_of_kin_emergency_contact",
        re.compile(r"^\s*6\.\s*NEXT\s+OF\s+KIN", re.IGNORECASE),
    ),
    (
        "7_health_certificates_and_vaccinations",
        re.compile(r"^\s*7\.\s*HEALTH\s+CERTIFICATES", re.IGNORECASE),
    ),
    ("8_marine_courses",   re.compile(r"^\s*8\.\s*MARINE\s+COURSES\s*$", re.IGNORECASE)),
    (
        "9_complete_sea_service_details",
        re.compile(r"^\s*9\s*[-–.]\s*COMPLETE\s+SEA", re.IGNORECASE),
    ),
    ("10_references",      re.compile(r"^\s*10\.\s*REFERENCES\s*$", re.IGNORECASE)),
    ("11_declaration",     re.compile(r"^\s*11\.\s*DECLARATION", re.IGNORECASE)),
    (
        "12_for_office_use_only",
        re.compile(r"^\s*12\.\s*FOR\s+OFFICE\s+USE\s+ONLY", re.IGNORECASE),
    ),
]

LINE_ORIENTED_SECTIONS = {
    "1_personal_details",
    "2_education",
    "3_contact_details",
    "6_next_of_kin_emergency_contact",
    "11_declaration",
    "12_for_office_use_only",
}
TABULAR_SECTIONS = {
    "4_travel_documents",
    "5_professional_qualification_certificate_of_competency",
    "7_health_certificates_and_vaccinations",
    "8_marine_courses",
    "9_complete_sea_service_details",
    "10_references",
}


def find_section_header(line: str) -> str | None:
    """Return the section key if ``line`` is a section header, else None."""
    for key, pattern in _SECTION_PATTERNS:
        if pattern.match(line):
            return key
    return None


def split_into_sections(
    text: str,
) -> tuple[dict[str, list[str]], dict[str, list[list[str]]]]:
    """Split text into per-section cell streams AND per-section row streams.

    Returns:
        line_sections: dict[section_key] -> flat list of cells (for
            line-oriented parsing).
        tabular_sections: dict[section_key] -> list of rows, where each
            row is a list of cells (for tabular parsing from the text).

    The pre-section-1 header block lives under the special key
    ``"0_application_meta"`` (line-oriented; flat list of cells).

    A stray ``12. For Office Use Only`` header that appears at the top of
    the document (a top-level paragraph in the docx) is NOT treated as a
    section — we only accept section headers that appear at or after the
    position of section 1.
    """
    if not text:
        return {}, {}

    normalised = normalize_text(text)
    lines = normalised.split("\n")

    all_header_idx: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        key = find_section_header(line)
        if key:
            all_header_idx.append((idx, key))

    if not all_header_idx:
        return {}, {}

    section_1_idx = next((i for i, k in all_header_idx if k == "1_personal_details"), None)
    if section_1_idx is None:
        return {}, {}

    header_idx = [(i, k) for i, k in all_header_idx if i >= section_1_idx]
    seen: set[str] = set()
    deduped: list[tuple[int, str]] = []
    for i, k in header_idx:
        if k not in seen:
            seen.add(k)
            deduped.append((i, k))
    header_idx = deduped

    line_sections: dict[str, list[str]] = {}
    tabular_sections: dict[str, list[list[str]]] = {}

    if section_1_idx > 0:
        meta_text = "\n".join(lines[0:section_1_idx])
        meta_cells: list[str] = []
        for ln in meta_text.split("\n"):
            meta_cells.extend(tokenize_line(ln))
        line_sections["0_application_meta"] = meta_cells

    for i, (start, key) in enumerate(header_idx):
        end = header_idx[i + 1][0] if i + 1 < len(header_idx) else len(lines)
        body_lines = lines[start + 1: end]

        if key in LINE_ORIENTED_SECTIONS:
            cells: list[str] = []
            for ln in body_lines:
                cells.extend(tokenize_line(ln))
            line_sections[key] = cells
        else:
            rows: list[list[str]] = []
            for ln in body_lines:
                row_cells = tokenize_line(ln)
                if row_cells:
                    rows.append(row_cells)
            tabular_sections[key] = rows

    return line_sections, tabular_sections


# ── Section boundary detection (tables) ─────────────────────────────────
#
# The big form table (Table 2 in DocumentProcessor output) contains rows
# for sections 1, 2, 3, 4, 5, 6, 7. The headers are at SPECIFIC cell
# indices, not just the first column. For example:
#
#     Row 0  cell[0] = "1. PERSONAL DETAILS"     ← section 1 header
#     Row 1  cell[0] = "Full Name", cell[2] = "MOHAMED..."   ← section 1 data
#     ...
#     Row 6  cell[0] = "2. EDUCATION"           ← section 2 header
#     ...
#     Row 14 cell[0] = "4. TRAVEL DOCUMENTS"     ← section 4 header
#     Row 15 cell[0] = "Type", cell[1] = "Document No.", ...  ← travel docs header
#     Row 16 cell[0] = "Passport", cell[1] = "A27533066", ... ← travel docs data
#     ...
#
# So for tabular sections, we walk the table rows and group them by the
# section that owns each row. Empty cells in the middle of a row ARE
# preserved in the table data — this is critical for correctly aligning
# columns (e.g. a qualifications row that has Name in cell[0] and
# Issued At in cell[20] with 18 empty cells in between).


def _is_section_header_row(row: list[str], section_key: str) -> bool:
    """Return True if the first non-empty cell of ``row`` is the section header for ``section_key``."""
    pattern = dict(_SECTION_PATTERNS)[section_key]
    for cell in row:
        s = (cell or "").strip()
        if s:
            return bool(pattern.match(s))
    return False


def split_tables_by_section(
    tables: list[list[list[str]]],
) -> dict[str, list[list[str]]]:
    """Walk all tables and return per-section row groups.

    For each row in each table, find the first non-empty cell. If that
    cell matches a section header, this row STARTS a new section. The
    row is INCLUDED in the previous section if it was inside one, OR
    starts a new section if the first cell is a header.

    Empty rows are dropped.

    The section's row list contains:
        * The header row (e.g. "Type | Document No. | ...") at index 0.
        * Data rows (e.g. "Passport | A27533066 | ...") at index 1+.

    Returns a dict keyed by section. Sections with no rows are omitted.
    """
    if not tables:
        return {}

    sections: dict[str, list[list[str]]] = {}
    current_section: str | None = None

    for table in tables:
        for row in table:
            if not row:
                continue
            # Find the first non-empty cell.
            first = ""
            for cell in row:
                if (cell or "").strip():
                    first = cell.strip()
                    break

            # If this row is a section header, switch to that section.
            new_section = None
            for key in TABULAR_SECTIONS | LINE_ORIENTED_SECTIONS:
                if find_section_header(first) == key:
                    new_section = key
                    break

            if new_section is not None:
                current_section = new_section
                sections.setdefault(current_section, [])
                # Don't include the section header itself in the section
                # body — it's just a marker row.
                continue

            # Otherwise, if we're inside a section, include the row.
            if current_section is not None:
                # Drop completely empty rows.
                if any((c or "").strip() for c in row):
                    sections[current_section].append(row)

    return sections
