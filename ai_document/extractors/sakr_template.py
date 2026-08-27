"""Deterministic parser for the Sakr Manning Agency Seafarer Employment
Application form (revision 1.3, May 2022).

The form is a fixed template with 12 numbered sections plus a meta block
at the top. This module is the *only* code that needs to know the form's
internal structure.

Public surface:

    result = SakrTemplateExtractor().extract(text, tables)

The ``text`` argument is the raw string returned by
:class:`ai_document.document_processor.DocumentProcessor` (or any equivalent
text extractor). The ``tables`` argument is the list of 2-D lists
returned by the same processor (used for tabular sections where column
alignment matters).

The returned ``ExtractorResult`` has the same shape used by every other
extractor in this package, so the view layer is strategy-agnostic.

Why deterministic and not LLM:
    * The form layout is fixed. A label-driven cell walker is more reliable
      than an LLM at this job.
    * No rate limits, no token cost, no 500s on quota exhaustion.
    * Each section parser is a pure function — unit-testable in isolation.

How the parser works:
    * Line-oriented sections (1, 2, 3, 6, 11, 12) — parsed from ``text``,
      with cells joined by ``" | "``. We walk the cells and dispatch on
      known labels.
    * Tabular sections (4, 5, 7, 8, 9, 10) — parsed from ``tables``,
      because the text version drops empty cells and loses column
      alignment. We use the table's first cell to detect section
      boundaries, then map data rows by cell index to the known column
      spec.
"""

from __future__ import annotations

import re
from typing import Any

from ..text_utils import (
    is_checked,
    normalize_text,
    split_into_sections,
    split_tables_by_section,
    strip_checkbox_marker,
)
from .base import ExtractorResult, make_failure, make_success
from .exception_codes import ErrorCode


# ── Detection ───────────────────────────────────────────────────────────

_SAKR_AGENCY_RE = re.compile(r"\bSAKR\s+MANNING\s+AGENCY\b", re.IGNORECASE)
_SAKR_PERSONAL_RE = re.compile(r"\bPERSONAL\s+DETAILS\b", re.IGNORECASE)


def detect_sakr_template(text: str) -> bool:
    """Return True if the text looks like a Sakr Seafarer Application form."""
    if not text:
        return False
    return bool(_SAKR_AGENCY_RE.search(text) and _SAKR_PERSONAL_RE.search(text))


# ── Cell-stream walker (line-oriented) ─────────────────────────────────
#
# Walk a flat cell stream and pull out values for known labels. The cell
# that matches a known label gets paired with the next cell as its value.
# Checkbox groups (Marital Status, English, German) collect multiple
# cells as options until the next known label.

def _extract_by_labels(
    cells: list[str],
    label_to_key: dict[str, str],
    *,
    checkbox_group_labels: set[str] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    if checkbox_group_labels is None:
        checkbox_group_labels = set()

    result: dict[str, Any] = {key: "" for key in label_to_key.values()}
    unknown: list[str] = []
    i = 0
    n = len(cells)
    while i < n:
        cell = cells[i].strip()
        clean = strip_checkbox_marker(cell).strip()
        if not clean:
            i += 1
            continue

        if clean in label_to_key:
            target_key = label_to_key[clean]
            if i + 1 < n:
                value_cell = cells[i + 1].strip()
                next_clean = strip_checkbox_marker(value_cell).strip()
                if next_clean in label_to_key or next_clean in checkbox_group_labels:
                    result[target_key] = ""
                    i += 1
                else:
                    result[target_key] = value_cell
                    i += 2
            else:
                i += 1
        elif clean in checkbox_group_labels:
            options: list[str] = []
            j = i + 1
            while j < n:
                next_cell = cells[j].strip()
                next_clean = strip_checkbox_marker(next_cell).strip()
                if not next_clean:
                    j += 1
                    continue
                if next_clean in label_to_key or next_clean in checkbox_group_labels:
                    break
                options.append(next_cell)
                j += 1
            result[clean] = options
            i = j
        else:
            unknown.append(cell)
            i += 1

    return result, unknown


def _to_int_or_none(raw: str) -> int | None:
    digits = re.sub(r"\D", "", raw or "")
    return int(digits) if digits else None


# ── Line-oriented section parsers ──────────────────────────────────────


# Regex: any prefix, optional whitespace, "-" or en-dash, optional
# whitespace, any suffix. The prefix is non-greedy so the FIRST "-" wins
# (which is what the form uses). This handles every shape we've seen:
#
#   "730 $ - 25/7/2025"   -> ("730 $",     "25/7/2025")
#   " - 01/03/2025"       -> ("",          "01/03/2025")  (empty salary)
#   "500 - 15/8/2025"     -> ("500",       "15/8/2025")
#   "500 – 15/8/2025"     -> ("500",       "15/8/2025")  (en-dash variant)
#   "1200 USD"            -> ("1200 USD",  "")            (no separator)
#   ""                    -> ("",          "")
_SALARY_DATE_RE = re.compile(r"^(.*?)\s*[-–]\s*(.*)$", re.UNICODE)


def _split_salary_and_date(raw: str) -> tuple[str, str]:
    """Split a combined ``"<salary> - <date>"`` value into two parts.

    The Sakr form puts expected salary and available date on the same
    line, separated by ``" - "`` (space-hyphen-space) — e.g.
    ``"730 $ - 25/7/2025"``. The split is intentionally permissive:

    * The separator may be a hyphen ``-`` or an en-dash ``–``.
    * Whitespace around the separator is optional.
    * If the separator is missing, the entire value is treated as the
      salary (with date empty). This handles the common case where the
      applicant fills in only the salary.
    * An empty input yields ``("", "")``.

    Returns ``(expected_salary, available_date)``.
    """
    if not raw:
        return "", ""
    match = _SALARY_DATE_RE.match(raw.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return raw.strip(), ""


def _parse_application_meta(cells: list[str]) -> dict[str, str]:
    label_to_key = {
        "Application For Position as": "application_for_position_as",
        "Application for position as": "application_for_position_as",
        "Register Code.":             "register_code",
        "Register Code":              "register_code",
        "Other Position (If Any)":    "other_position",
        "Other Position":             "other_position",
        "Register Date":              "register_date",
        "Last up Date Data":          "last_update_data",
        "Last Update Data":           "last_update_data",
        # NOTE: the raw value goes into _expected_salary_and_available_date
        # and we split it into the two fields below. We keep the
        # intermediate key for clarity (and so the splitter is easy to
        # unit-test against a real CV).
        "Expected Salary / Available Date": "_expected_salary_and_available_date",
        "Expected Salary/Available Date":  "_expected_salary_and_available_date",
    }
    out, _ = _extract_by_labels(cells, label_to_key)

    combined = (out.pop("_expected_salary_and_available_date", "") or "").strip()
    salary, available_date = _split_salary_and_date(combined)

    out["expected_salary"] = salary
    out["available_date"] = available_date
    # Keep the combined value as well so callers that want the original
    # raw text don't lose it. (The Applicant model's `applied_position_info`
    # JSONField can store either form.)
    out["expected_salary_and_available_date"] = combined
    return out


def _parse_personal_details(cells: list[str]) -> dict[str, Any]:
    label_to_key = {
        "Full Name":      "full_name",
        "Date Of Birth":  "date_of_birth",
        "Nationality":    "nationality",
        "Height (Cm)":    "height_cm",
        "Weight (Kg)":    "weight_kg",
        "Place Of Birth": "place_of_birth",
        "Overall Size":   "overall_size",
        "Shirt Size":     "shirt_size",
        "Nearest Port":   "nearest_port",
        "Trouser Size":   "trouser_size",
        "Shoes Size":     "shoes_size",
    }
    out, _ = _extract_by_labels(cells, label_to_key, checkbox_group_labels={"Marital Status"})

    marital_options = out.pop("Marital Status", [])  # type: ignore[arg-type]
    is_single = is_married = False
    for opt in marital_options or []:
        opt_clean = strip_checkbox_marker(opt).strip().lower()
        if "single" in opt_clean and is_checked(opt):
            is_single = True
        elif "married" in opt_clean and is_checked(opt):
            is_married = True
    out["marital_status"] = {"single": is_single, "married": is_married}

    out["height_cm"] = _to_int_or_none(str(out.get("height_cm") or ""))
    out["weight_kg"] = _to_int_or_none(str(out.get("weight_kg") or ""))
    return out


def _parse_education(cells: list[str]) -> dict[str, Any]:
    """Section 2: Education.

    The Marline Test block has a quirk: it has 4 SUB-LABELS (Issued Date,
    Result %, Issued By (Authority), Issued At) on the same line as
    "Marline Test" itself. So when we walk the cells with
    ``_extract_by_labels``, the "Issued Date" cell is treated as a
    sibling label and gets paired with the next cell as its value.

    To handle this cleanly, we treat the Marline Test block specially:
    after the "Marline Test" cell, the next 4 non-empty cells are
    SUB-LABELS, not values. The actual values for these sub-fields would
    appear on a SUBSEQUENT line in the document, but in the current
    Sakr form layout they don't (the Marline Test is left blank in most
    CVs). So we set all 4 sub-fields to empty.

    College / School is also special: it's a label that may have an
    actual value on the next cell.
    """
    college_school = ""
    for idx, cell in enumerate(cells):
        if strip_checkbox_marker(cell).strip().lower() in ("college / school", "college/school"):
            if idx + 1 < len(cells):
                next_clean = strip_checkbox_marker(cells[idx + 1]).strip()
                if next_clean and next_clean.lower() not in (
                    "marline test", "english language", "german language",
                ):
                    college_school = cells[idx + 1].strip()
            break

    # English / German checkboxes.
    english_options: list[str] = []
    german_options: list[str] = []
    for idx, cell in enumerate(cells):
        clean = strip_checkbox_marker(cell).strip().lower()
        if clean == "english language":
            for j in range(idx + 1, len(cells)):
                next_clean = strip_checkbox_marker(cells[j]).strip().lower()
                if next_clean in ("german language", "marline test", "college / school", "college/school"):
                    break
                english_options.append(cells[j].strip())
            break
    for idx, cell in enumerate(cells):
        clean = strip_checkbox_marker(cell).strip().lower()
        if clean == "german language":
            for j in range(idx + 1, len(cells)):
                next_clean = strip_checkbox_marker(cells[j]).strip().lower()
                if next_clean in ("english language", "marline test", "college / school", "college/school"):
                    break
                german_options.append(cells[j].strip())
            break

    return {
        "college_school": college_school,
        # All Marline Test sub-fields are empty in the current Sakr form
        # layout (the line is just labels). If a future variant has
        # values, they'll be on the next line and the parser will need
        # to be updated.
        "marline_test": {
            "issued_date":         "",
            "result_percentage":   "",
            "issued_by_authority": "",
            "issued_at":           "",
        },
        "english_language": _parse_language_level(english_options),
        "german_language":  _parse_language_level(german_options),
    }


def _parse_language_level(options: list[str]) -> dict[str, bool]:
    levels = {"fluent": False, "good": False, "average": False, "poor": False}
    for opt in options or []:
        opt_clean = strip_checkbox_marker(opt).strip().lower()
        if not opt_clean:
            continue
        if is_checked(opt):
            for level in levels:
                if level in opt_clean:
                    levels[level] = True
                    break
    return levels


def _parse_contact_details(cells: list[str]) -> dict[str, str]:
    label_to_key = {
        "Home Address / City": "home_address_city",
        "Home Address/City":   "home_address_city",
        "E-Mail":              "e_mail",
        "E-mail":              "e_mail",
        "Email":               "e_mail",
        "Mobile / Tel":        "mobile_tel",
        "Mobile/Tel":          "mobile_tel",
    }
    out, _ = _extract_by_labels(cells, label_to_key)
    return out


def _parse_next_of_kin(cells: list[str]) -> dict[str, str]:
    label_to_key = {
        "Full Name":         "full_name",
        "Relationship":      "relationship",
        "Address / Country": "address_country",
        "Tel. No./ Mobile":  "tel_no_mobile",
        "Tel. No. / Mobile": "tel_no_mobile",
        "Email":             "email",
        "E-Mail":            "email",
    }
    out, _ = _extract_by_labels(cells, label_to_key)
    return out


def _parse_declaration(cells: list[str]) -> dict[str, str]:
    signature = ""
    for cell in cells:
        m = re.search(r"_\(([^)]+)\)_", cell)
        if m:
            signature = m.group(1).strip()
    return {
        "place": "",
        "date": "",
        "signature": signature,
    }


def _parse_office_use_only(_cells: list[str]) -> dict[str, str]:
    return {
        "initial_assessment": "",
        "comments": "",
        "responsible_person": "",
    }


# ── Tabular section parsers ─────────────────────────────────────────────
#
# Tabular sections use the ``tables`` argument (NOT text), because the
# text version drops empty cells and loses column alignment. The big
# form table (Table 2) has columns at fixed indices:
#
#     Travel docs:  cell[0] = Type, cell[1] = Document No, cell[2] = ISS. Date, ...
#     Quals:        cell[0] = Certificate Name, cell[3] = Number, cell[4] = Issue Date,
#                   cell[9] = Expiry Date, cell[14] = Issued By, cell[20] = Issued At
#     Health certs: cell[0] = Type, cell[1] = Number, cell[2] = Issue Date, cell[3] = Expiry Date,
#                   cell[4] = Issued By, cell[5] = Issued At
#     Marine:       cell[0] = Course Name, cell[1] = Number, cell[2] = Issue Date, ...
#     Sea service:  cell[0] = Company Name, cell[1] = Rank, ...
#     References:   cell[0] = No, cell[1] = Company, cell[2] = Position, cell[3] = Name, cell[4] = Tel, cell[5] = Email
#
# We match columns by NAME (the header cell text), so a future revision
# of the form that reorders columns is still handled correctly. The
# name match is by exact case-insensitive equality against the first
# non-empty cell of the column header row.

def _parse_table(
    rows: list[list[str]],
    columns: list[tuple[str, tuple[str, ...]]],
    *,
    known_section_starts: tuple[str, ...] = (),
) -> list[dict[str, str]]:
    """Convert rows into a list of dicts keyed by ``columns``.

    The first row whose cells collectively contain at least one alias
    for EVERY column is the header. Subsequent rows are mapped; rows
    are included only if at least one mapped value is non-empty.

    Rows whose FIRST cell starts with one of ``known_section_starts``
    end the data block.
    """
    if not rows:
        return []

    header_idx = None
    for i, row in enumerate(rows):
        # Cells in the row, normalised: lowercased, checkbox stripped.
        cells_norm = [strip_checkbox_marker(c).strip().lower() for c in row]
        # The row is a header iff every column has at least one alias
        # appearing in some cell. We test columns (not the cartesian
        # product of columns × aliases) so a column with 3 aliases where
        # only 1 matches still counts.
        all_columns_matched = True
        for _key, aliases in columns:
            column_matched = any(
                alias.lower() in cell
                for cell in cells_norm
                if cell
                for alias in aliases
            )
            if not column_matched:
                all_columns_matched = False
                break
        if all_columns_matched:
            header_idx = i
            break

    if header_idx is None:
        return []

    header_cells = [strip_checkbox_marker(c).strip().lower() for c in rows[header_idx]]

    # Build a mapping: column key -> the cell index whose value matches
    # the column's aliases. We pick the FIRST matching cell.
    key_to_idx: dict[str, int] = {}
    for key, aliases in columns:
        for alias in aliases:
            alias_lc = alias.lower()
            for idx, cell in enumerate(header_cells):
                if cell == alias_lc or (cell and alias_lc in cell):
                    key_to_idx[key] = idx
                    break
            if key in key_to_idx:
                break

    if not key_to_idx:
        return []

    out: list[dict[str, str]] = []
    for row in rows[header_idx + 1:]:
        first_cell = strip_checkbox_marker(row[0]).strip() if row else ""
        if known_section_starts and any(
            ks.lower() in first_cell.lower() for ks in known_section_starts
        ):
            break
        record: dict[str, str] = {}
        for key, idx in key_to_idx.items():
            if idx < len(row):
                record[key] = strip_checkbox_marker(row[idx]).strip()
        if any(v for v in record.values()):
            out.append(record)
    return out


_TRAVEL_DOC_COLUMNS = [
    ("type",                ("Type",)),
    ("document_no",         ("Document No.", "Document No")),
    ("iss_date",            ("ISS. Date", "ISS Date", "Issue Date")),
    ("exp_date",            ("Exp. Date", "Exp Date", "Expiry Date")),
    ("iss_by_authority",    ("ISS. By (Authority)", "Iss. By (Authority)", "Issued By")),
    ("place_of_issue",      ("Place of Issue", "Issued At")),
]

_QUALIFICATION_COLUMNS = [
    ("certificate_name",    ("Certificate Name",)),
    ("number",              ("Number",)),
    ("issue_date",          ("Issue Date", "Issued Date")),
    ("expiry_date",         ("Expiry Date", "Exp. Date", "Exp Date")),
    ("issued_by",           ("Issued By",)),
    ("issued_at",           ("Issued At",)),
]

_HEALTH_CERT_COLUMNS = [
    ("certificate_type",    ("Flag State", "Certificate Type", "Type")),
    ("number",              ("Number",)),
    ("issue_date",          ("Issue Date", "Issued Date")),
    ("expiry_date",         ("Expiry Date", "Exp. Date", "Exp Date")),
    ("issued_by",           ("Issued By",)),
    ("issued_at",           ("Issued At",)),
]

_MARINE_COURSE_COLUMNS = [
    ("course_name",         ("Course Name",)),
    ("number",              ("Number",)),
    ("issue_date",          ("Issue Date", "Issued Date")),
    ("expiry_date",         ("Expiry Date", "Exp. Date", "Exp Date")),
    ("issued_by_at",        ("Issued By / At", "Issued By/At", "Issued By", "Issued At")),
]

_SEA_SERVICE_COLUMNS = [
    ("company_name",        ("Company Name",)),
    ("rank",                ("Rank",)),
    ("vessel_name_imo",     ("Vessel Name/IMO Number", "Vessel Name")),
    ("flag",                ("Flag",)),
    ("signed_on",           ("Signed On",)),
    ("signed_off",          ("Signed Off",)),
    ("period",              ("Period",)),
    ("vessel_type",         ("Vessel Type",)),
    ("dwt_grt",             ("D.W.T./ G.R.T", "D.W.T./G.R.T")),
    ("engine_type",         ("Engine Type",)),
    ("bh_kw",               ("BH/ KW", "BH/KW")),
    ("reason_for_sign_off", ("Reason for Sign off", "Reason for Sign-off")),
]

_REFERENCES_COLUMNS = [
    ("no",                              ("No", "#", "No.")),
    ("company_management_country",      ("Company / Management / Country", "Company")),
    ("position",                        ("Position",)),
    ("name",                            ("Name",)),
    ("tel",                             ("TEL", "Tel")),
    ("email",                           ("EMAIL", "Email", "E-Mail")),
]


def _parse_travel_documents(rows: list[list[str]]) -> list[dict[str, str]]:
    return _parse_table(rows, _TRAVEL_DOC_COLUMNS)


def _parse_qualifications(rows: list[list[str]]) -> list[dict[str, str]]:
    return _parse_table(rows, _QUALIFICATION_COLUMNS)


def _parse_health_certificates(rows: list[list[str]]) -> dict[str, Any]:
    certs = _parse_table(rows, _HEALTH_CERT_COLUMNS, known_section_starts=("Covid-19", "Covid"))

    # Covid-19 sub-block: section 7 contains a sub-table whose first
    # column is "Covid-19" and whose remaining columns are the four
    # vaccination fields. The sub-table has either:
    #   (a) one sub-header row (Covid-19 | Vaccination Name | First Dose
    #       | Second Dose | Other) followed by one data row, OR
    #   (b) just one data row (Covid-19 | <name> | <date1> | <date2> |
    #       <remarks>) with no sub-header.
    #
    # Because the form is one big 22-column table, these cells sit at
    # fixed column indices (e.g. Vaccination Name is at cell[2], First
    # Dose at cell[5], etc.), NOT at cells[1] and cells[2]. So we detect
    # the sub-header by content ("Vaccination Name" appears in some
    # cell), then build a column-index map from the sub-header row and
    # apply it to the data row.
    covid: dict[str, str] = {}
    for i, row in enumerate(rows):
        cells_lower = [strip_checkbox_marker(c).strip().lower() for c in row]
        # Look for the sub-header row: contains "vaccination name".
        if "vaccination name" in " ".join(c for c in cells_lower if c):
            sub_header_idx = {name: idx for idx, name in enumerate(cells_lower) if name}
            if i + 1 < len(rows):
                data_row = [strip_checkbox_marker(c).strip() for c in rows[i + 1]]
                covid = {
                    "vaccination_name":       data_row[sub_header_idx["vaccination name"]] if "vaccination name" in sub_header_idx else "",
                    "first_dose":             data_row[sub_header_idx["first dose"]]       if "first dose" in sub_header_idx else "",
                    "second_dose":            data_row[sub_header_idx["second dose"]]      if "second dose" in sub_header_idx else "",
                    "other_doses_or_remarks": data_row[sub_header_idx["(other does or remarks)"]] if "(other does or remarks)" in sub_header_idx
                                            else (data_row[sub_header_idx["other doses or remarks"]] if "other doses or remarks" in sub_header_idx else ""),
                }
            break
        # Look for a one-row data block: a row starting with "Covid-19"
        # whose other cells look like data (dates, vaccine names).
        first_cell = strip_checkbox_marker(row[0]).strip() if row else ""
        if first_cell.lower().startswith("covid"):
            # No sub-header. Try to identify the data row by content.
            # Vaccine names: 2-4 words; dates: contain "/" or "-".
            non_empty = [(idx, strip_checkbox_marker(c).strip()) for idx, c in enumerate(row) if (c or "").strip() and idx > 0]
            if len(non_empty) >= 4:
                covid = {
                    "vaccination_name":       non_empty[0][1],
                    "first_dose":             non_empty[1][1],
                    "second_dose":            non_empty[2][1],
                    "other_doses_or_remarks": non_empty[3][1] if len(non_empty) > 3 else "",
                }
            break

    return {
        "certificates": certs,
        "covid_19": covid,
    }


def _parse_marine_courses(rows: list[list[str]]) -> list[dict[str, str]]:
    return _parse_table(rows, _MARINE_COURSE_COLUMNS)


def _parse_sea_service(rows: list[list[str]]) -> dict[str, Any]:
    records = _parse_table(rows, _SEA_SERVICE_COLUMNS, known_section_starts=("10. References", "REFERENCES"))
    return {
        "service_records": records,
        "total_records": len(records),
    }


def _parse_references(rows: list[list[str]]) -> list[dict[str, str]]:
    return _parse_table(rows, _REFERENCES_COLUMNS, known_section_starts=("11. DECLARATION", "DECLARATION"))


# ── Top-level extractor ────────────────────────────────────────────────


class SakrTemplateExtractor:
    """Deterministic parser for the Sakr Seafarer Employment Application.

    Usage::

        result = SakrTemplateExtractor().extract(text, tables)
        if result.ok:
            Applicant.objects.create(**result.data)
        else:
            ...handle result.error...
    """

    EXTRACTOR_NAME = "sakr_template"

    def extract(
        self,
        text: str,
        tables: list[list[list[str]]] | None = None,
    ) -> ExtractorResult:
        text = text or ""
        tables = tables or []

        if not detect_sakr_template(text):
            return make_failure(
                extractor=self.EXTRACTOR_NAME,
                error=ErrorCode.NOT_SAKR_TEMPLATE,
            )

        try:
            normalised = normalize_text(text)
            line_sections, _text_tabular = split_into_sections(normalised)
            table_sections = split_tables_by_section(tables)
        except Exception as exc:  # pragma: no cover
            return make_failure(
                extractor=self.EXTRACTOR_NAME,
                error=ErrorCode.PARSE_FAILED,
                warnings=[f"section split failed: {exc!r}"],
            )

        if "1_personal_details" not in line_sections:
            return make_failure(
                extractor=self.EXTRACTOR_NAME,
                error=ErrorCode.NOT_SAKR_TEMPLATE,
                warnings=["1. PERSONAL DETAILS section not found"],
            )

        warnings: list[str] = []
        try:
            data: dict[str, Any] = {
                "0_application_meta": _parse_application_meta(
                    line_sections.get("0_application_meta", []),
                ),
                "1_personal_details": _parse_personal_details(
                    line_sections.get("1_personal_details", []),
                ),
                "2_education": _parse_education(line_sections.get("2_education", [])),
                "3_contact_details": _parse_contact_details(
                    line_sections.get("3_contact_details", []),
                ),
                "4_travel_documents": _parse_travel_documents(
                    table_sections.get("4_travel_documents", []),
                ),
                "5_professional_qualification_certificate_of_competency": _parse_qualifications(
                    table_sections.get("5_professional_qualification_certificate_of_competency", []),
                ),
                "6_next_of_kin_emergency_contact": _parse_next_of_kin(
                    line_sections.get("6_next_of_kin_emergency_contact", []),
                ),
                "7_health_certificates_and_vaccinations": _parse_health_certificates(
                    table_sections.get("7_health_certificates_and_vaccinations", []),
                ),
                "8_marine_courses": _parse_marine_courses(
                    table_sections.get("8_marine_courses", []),
                ),
                "9_complete_sea_service_details": _parse_sea_service(
                    table_sections.get("9_complete_sea_service_details", []),
                ),
                "10_references": _parse_references(
                    table_sections.get("10_references", []),
                ),
                "11_declaration": _parse_declaration(
                    line_sections.get("11_declaration", []),
                ),
                "12_for_office_use_only": _parse_office_use_only(
                    line_sections.get("12_for_office_use_only", []),
                ),
            }
        except Exception as exc:  # pragma: no cover
            return make_failure(
                extractor=self.EXTRACTOR_NAME,
                error=ErrorCode.PARSE_FAILED,
                warnings=[f"section parse failed: {exc!r}"],
            )

        full_name = (data.get("1_personal_details") or {}).get("full_name") or ""
        if not full_name.strip():
            warnings.append("Full Name was empty after parsing")
            return make_failure(
                extractor=self.EXTRACTOR_NAME,
                error=ErrorCode.PARSE_FAILED,
                warnings=warnings,
            )

        return make_success(
            data=data,
            extractor=self.EXTRACTOR_NAME,
            confidence=0.95,
            warnings=warnings,
        )
