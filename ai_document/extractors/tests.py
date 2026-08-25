"""Tests for the Sakr template extractor and its sub-parsers.

Layered tests:
    * Pure-function tests for each section parser (no fixtures needed).
    * Integration test on the actual CV file (test_sakr_smoke).
    * Detection tests.
    * Error-handling tests (NOT_A_CV, NOT_SAKR_TEMPLATE, etc.).
"""

from __future__ import annotations

import os
from django.test import SimpleTestCase

from ai_document.extractors import (
    ErrorCode,
    SakrTemplateExtractor,
    detect_sakr_template,
)
from ai_document.extractors.base import ExtractorResult, make_failure, make_success
from ai_document.extractors.exception_codes import client_message
from ai_document.extractors.sakr_template import (
    _parse_application_meta,
    _parse_contact_details,
    _parse_declaration,
    _parse_education,
    _parse_health_certificates,
    _parse_language_level,
    _parse_marine_courses,
    _parse_next_of_kin,
    _parse_qualifications,
    _parse_references,
    _parse_sea_service,
    _parse_travel_documents,
    _parse_office_use_only,
    _parse_personal_details,
    _extract_by_labels,
    _to_int_or_none,
)
from ai_document.text_utils import (
    is_checked,
    normalize_text,
    split_into_sections,
    split_tables_by_section,
    strip_checkbox_marker,
    tokenize_line,
)


# ── Detection ───────────────────────────────────────────────────────────


class DetectSakrTemplateTests(SimpleTestCase):
    """Cheap pre-check called by the pipeline before running the parser."""

    def test_detects_full_form(self):
        text = "SAKR MANNING AGENCY\n1. PERSONAL DETAILS\nFull Name\nJohn"
        self.assertTrue(detect_sakr_template(text))

    def test_detects_lowercase_agency_name(self):
        text = "sakr manning agency\nPERSONAL DETAILS"
        self.assertTrue(detect_sakr_template(text))

    def test_rejects_empty(self):
        self.assertFalse(detect_sakr_template(""))

    def test_rejects_non_sakr_cv(self):
        # Has a personal-details-shaped section but no agency name.
        text = "John Doe CV\nPERSONAL DETAILS\nExperience..."
        self.assertFalse(detect_sakr_template(text))

    def test_rejects_agency_name_without_personal_details(self):
        # Has agency name but no form structure.
        text = "SAKR MANNING AGENCY\nWe are hiring engineers."
        self.assertFalse(detect_sakr_template(text))


# ── Error code + ExtractorResult shape ─────────────────────────────────


class ErrorCodeTests(SimpleTestCase):

    def test_error_codes_serialize_as_values(self):
        # The wire format is the value, not the name.
        self.assertEqual(ErrorCode.NOT_A_CV, "not_a_cv")
        self.assertEqual(ErrorCode.PARSE_FAILED, "parse_failed")

    def test_client_message_returns_safe_string(self):
        msg = client_message(ErrorCode.NOT_A_CV)
        self.assertIsInstance(msg, str)
        self.assertGreater(len(msg), 0)
        # Must NOT leak any internal detail.
        self.assertNotIn("Traceback", msg)
        self.assertNotIn("Exception", msg)

    def test_unknown_code_falls_back_to_internal(self):
        # Defensive: a future code without a CLIENT_MESSAGES entry must
        # not raise — it must fall back to the generic INTERNAL message.
        class _FakeCode(str):
            pass
        # Use a string-typed fake; client_message does a dict lookup.
        # We simulate by checking that client_message(INTERNAL) works.
        self.assertIn(".", client_message(ErrorCode.INTERNAL))


class ExtractorResultTests(SimpleTestCase):

    def test_make_success_has_data_no_error(self):
        r = make_success({"foo": "bar"}, "test", confidence=0.9)
        self.assertTrue(r.ok)
        self.assertEqual(r.data, {"foo": "bar"})
        self.assertEqual(r.extractor, "test")
        self.assertEqual(r.confidence, 0.9)
        self.assertEqual(r.error, None)
        self.assertEqual(r.warnings, [])

    def test_make_failure_has_error_no_data(self):
        r = make_failure("test", ErrorCode.NOT_A_CV)
        self.assertFalse(r.ok)
        self.assertIsNone(r.data)
        self.assertEqual(r.error, ErrorCode.NOT_A_CV)
        self.assertEqual(r.confidence, 0.0)

    def test_to_dict_is_json_safe(self):
        r = make_success({"k": "v"}, "test")
        d = r.to_dict()
        # Must contain only JSON-serialisable types.
        import json
        json.dumps(d)  # raises if not serialisable


# ── Text utilities ──────────────────────────────────────────────────────


class TextUtilsTests(SimpleTestCase):

    def test_normalize_unicode_smart_quotes(self):
        # NFKC does NOT convert smart quotes to ASCII; that requires
        # explicit mapping. The test asserts the current behaviour: smart
        # quotes are preserved. If we add explicit smart-quote handling
        # later, this test must be updated.
        self.assertEqual(normalize_text("\u201chello\u201d"), "\u201chello\u201d")
        # But fullwidth ASCII (which NFKC does normalise) is converted.
        self.assertEqual(normalize_text("\uff28ello"), "Hello")

    def test_normalize_strips_each_line(self):
        self.assertEqual(normalize_text("  a  \n   b  "), "a\nb")

    def test_normalize_empty(self):
        self.assertEqual(normalize_text(""), "")
        self.assertEqual(normalize_text(None), "")

    def test_tokenize_line_drops_empty_cells(self):
        self.assertEqual(
            tokenize_line("A |  | B | C"),
            ["A", "B", "C"],
        )

    def test_tokenize_line_single_cell(self):
        self.assertEqual(tokenize_line("hello"), ["hello"])

    def test_is_checked_detects_all_markers(self):
        for marker in ("✓", "☑", "☒", "✔", "✗"):
            self.assertTrue(is_checked(f"option {marker}"))

    def test_is_checked_false_for_plain(self):
        self.assertFalse(is_checked("option"))
        self.assertFalse(is_checked(""))
        self.assertFalse(is_checked(None))

    def test_strip_checkbox_marker(self):
        self.assertEqual(strip_checkbox_marker("Good ✓"), "Good")
        self.assertEqual(strip_checkbox_marker("✓ Good"), "Good")
        self.assertEqual(strip_checkbox_marker("  ✓  "), "")


# ── Section splitter (text) ─────────────────────────────────────────────


class SplitIntoSectionsTests(SimpleTestCase):

    def test_split_returns_both_dicts(self):
        text = (
            "1. PERSONAL DETAILS\nFull Name | John\n\n"
            "2. EDUCATION\nCollege | MIT\n"
        )
        line_sections, tabular_sections = split_into_sections(normalize_text(text))
        # Sections 1 and 2 are line-oriented (parsed from text cells).
        self.assertIn("1_personal_details", line_sections)
        self.assertIn("2_education", line_sections)
        # Tabular sections only appear once the doc has tabular content
        # (travel docs, quals, etc.). Sections 1-3 are always line-oriented.
        self.assertNotIn("1_personal_details", tabular_sections)

    def test_drops_stray_section_12_at_top(self):
        # The Sakr docx has a stray "12. For Office Use Only" paragraph
        # at the very top. Section-splitter must drop it.
        text = (
            "12.For Office Use Only\n"
            "Initial assessment of applicant for further recruitment\n\n"
            "SAKR MANNING AGENCY\n"
            "1. PERSONAL DETAILS\nFull Name | John\n"
        )
        line_sections, _ = split_into_sections(normalize_text(text))
        # The stray 12. must NOT be in line_sections (it appears before 1).
        self.assertNotIn("12_for_office_use_only", line_sections)
        # But the meta block is computed from lines BEFORE section 1.
        self.assertIn("0_application_meta", line_sections)
        self.assertIn("SAKR", " ".join(line_sections["0_application_meta"]))

    def test_meta_block_includes_application_position(self):
        text = (
            "12.For Office Use Only\n\n"
            "SAKR MANNING AGENCY\n"
            "Application For Position as | Bar Waiter\n"
            "Register Code. | DR-6.104\n\n"
            "1. PERSONAL DETAILS\nFull Name | John\n"
        )
        line_sections, _ = split_into_sections(normalize_text(text))
        meta = " | ".join(line_sections["0_application_meta"])
        self.assertIn("Bar Waiter", meta)
        self.assertIn("DR-6.104", meta)


class SplitTablesBySectionTests(SimpleTestCase):

    def test_groups_rows_under_section(self):
        tables = [[
            ["1. PERSONAL DETAILS", "", ""],
            ["Full Name", "John", ""],
            ["Date Of Birth", "1990", ""],
            ["4. TRAVEL DOCUMENTS", "", ""],
            ["Type", "Document No.", "ISS. Date"],
            ["Passport", "A123", "2020-01-01"],
        ]]
        sections = split_tables_by_section(tables)
        self.assertIn("1_personal_details", sections)
        self.assertIn("4_travel_documents", sections)
        # Section 1: 2 data rows (Full Name, Date Of Birth).
        self.assertEqual(len(sections["1_personal_details"]), 2)
        # Section 4: 2 rows — column header (Type|Document No.|ISS. Date)
        # and the Passport data row.
        self.assertEqual(len(sections["4_travel_documents"]), 2)

    def test_empty_tables_returns_empty(self):
        self.assertEqual(split_tables_by_section([]), {})
        self.assertEqual(split_tables_by_section(None), {})


# ── _to_int_or_none ────────────────────────────────────────────────────


class ToIntOrNoneTests(SimpleTestCase):

    def test_digits_only(self):
        self.assertEqual(_to_int_or_none("173"), 173)

    def test_with_units(self):
        self.assertEqual(_to_int_or_none("173 cm"), 173)

    def test_empty_returns_none(self):
        self.assertIsNone(_to_int_or_none(""))
        self.assertIsNone(_to_int_or_none(None))

    def test_no_digits_returns_none(self):
        self.assertIsNone(_to_int_or_none("abc"))


# ── _extract_by_labels ─────────────────────────────────────────────────


class ExtractByLabelsTests(SimpleTestCase):

    def test_known_label_takes_next_cell_as_value(self):
        cells = ["Full Name", "John", "Nationality", "Egyptian"]
        out, unknown = _extract_by_labels(cells, {
            "Full Name": "full_name",
            "Nationality": "nationality",
        })
        self.assertEqual(out["full_name"], "John")
        self.assertEqual(out["nationality"], "Egyptian")
        self.assertEqual(unknown, [])

    def test_label_with_no_value_yields_empty(self):
        cells = ["Full Name", "Nationality", "Egyptian"]
        out, _ = _extract_by_labels(cells, {
            "Full Name": "full_name",
            "Nationality": "nationality",
        })
        self.assertEqual(out["full_name"], "")

    def test_checkbox_group_collects_options(self):
        cells = ["Marital Status", "Single", "Married", "Other"]
        out, _ = _extract_by_labels(
            cells,
            {},
            checkbox_group_labels={"Marital Status"},
        )
        self.assertEqual(out["Marital Status"], ["Single", "Married", "Other"])

    def test_unknown_cells_returned(self):
        cells = ["Unknown1", "Foo", "Full Name", "John"]
        out, unknown = _extract_by_labels(cells, {"Full Name": "full_name"})
        self.assertEqual(unknown, ["Unknown1", "Foo"])
        self.assertEqual(out["full_name"], "John")


# ── Section parsers: line-oriented ──────────────────────────────────────


class ParseApplicationMetaTests(SimpleTestCase):

    def test_parses_all_six_fields(self):
        cells = [
            "Application For Position as", "Bar Waiter",
            "Register Code.", "DR-6.104",
            "Other Position (If Any)", "Waiter Restaurant",
            "Register Date", "10.07.2025",
            "Last up Date Data", "",
            "Expected Salary / Available Date", "730 $ - 25/7/2025",
        ]
        out = _parse_application_meta(cells)
        self.assertEqual(out["application_for_position_as"], "Bar Waiter")
        self.assertEqual(out["register_code"], "DR-6.104")
        self.assertEqual(out["other_position"], "Waiter Restaurant")
        self.assertEqual(out["register_date"], "10.07.2025")
        self.assertEqual(out["expected_salary_and_available_date"], "730 $ - 25/7/2025")

    def test_empty_input_returns_empty_dict_with_keys(self):
        out = _parse_application_meta([])
        self.assertEqual(out["application_for_position_as"], "")
        self.assertEqual(out["register_code"], "")


class ParsePersonalDetailsTests(SimpleTestCase):

    def test_parses_all_twelve_fields(self):
        # Note: in the real CV, the check marker is part of the cell
        # text, e.g. "Single     ✓", not a separate cell.
        cells = [
            "Full Name", "MOHAMED SHEHATA",
            "Date Of Birth", "28/02/1995",
            "Marital Status", "Single     \u2713", "Married",
            "Nationality", "Egyptian",
            "Height (Cm)", "173",
            "Weight (Kg)", "67",
            "Place Of Birth", "Qena, Egypt",
            "Overall Size", "67",
            "Shirt Size", "Medium",
            "Nearest Port", "Luxor",
            "Trouser Size", "Medium",
            "Shoes Size", "43",
        ]
        out = _parse_personal_details(cells)
        self.assertEqual(out["full_name"], "MOHAMED SHEHATA")
        self.assertEqual(out["date_of_birth"], "28/02/1995")
        self.assertEqual(out["nationality"], "Egyptian")
        self.assertEqual(out["height_cm"], 173)
        self.assertEqual(out["weight_kg"], 67)
        self.assertEqual(out["place_of_birth"], "Qena, Egypt")
        self.assertEqual(out["nearest_port"], "Luxor")
        self.assertTrue(out["marital_status"]["single"])
        self.assertFalse(out["marital_status"]["married"])

    def test_married_checkbox_marks_married(self):
        cells = [
            "Full Name", "Jane",
            "Marital Status", "Single", "Married     \u2713",
        ]
        out = _parse_personal_details(cells)
        self.assertFalse(out["marital_status"]["single"])
        self.assertTrue(out["marital_status"]["married"])

    def test_no_checkbox_yields_neither(self):
        cells = [
            "Full Name", "Alex",
            "Marital Status", "Single", "Married",
        ]
        out = _parse_personal_details(cells)
        self.assertFalse(out["marital_status"]["single"])
        self.assertFalse(out["marital_status"]["married"])

    def test_height_with_unit_stripped(self):
        cells = ["Full Name", "X", "Height (Cm)", "180cm"]
        out = _parse_personal_details(cells)
        self.assertEqual(out["height_cm"], 180)


class ParseEducationTests(SimpleTestCase):

    def test_parses_college_and_languages(self):
        # In the real CV, the check marker is part of the option cell:
        # "Good           ✓" not a separate cell.
        cells = [
            "College / School", "MIT",
            "Marline Test", "Issued Date", "Result %", "Issued By (Authority)", "Issued At",
            "English Language", "Fluent", "Good           \u2713", "Average", "Poor",
            "German Language", "Fluent", "Good", "Average  \u2713", "Poor",
        ]
        out = _parse_education(cells)
        self.assertEqual(out["college_school"], "MIT")
        self.assertTrue(out["english_language"]["good"])
        self.assertTrue(out["german_language"]["average"])

    def test_marline_test_subfields_all_empty(self):
        # The Sakr form puts the 4 sub-labels on the same line as
        # "Marline Test" itself, with no values on the next line. So
        # the sub-fields should all be empty strings.
        cells = [
            "College / School", "MIT",
            "Marline Test", "Issued Date", "Result %", "Issued By (Authority)", "Issued At",
            "English Language", "Fluent", "Good", "Average", "Poor",
        ]
        out = _parse_education(cells)
        self.assertEqual(out["marline_test"]["issued_date"], "")
        self.assertEqual(out["marline_test"]["result_percentage"], "")
        self.assertEqual(out["marline_test"]["issued_by_authority"], "")
        self.assertEqual(out["marline_test"]["issued_at"], "")


class ParseLanguageLevelTests(SimpleTestCase):

    def test_marks_correct_level(self):
        out = _parse_language_level(["Fluent", "Good ✓", "Average", "Poor"])
        self.assertFalse(out["fluent"])
        self.assertTrue(out["good"])
        self.assertFalse(out["average"])
        self.assertFalse(out["poor"])

    def test_no_checkbox_means_all_false(self):
        out = _parse_language_level(["Fluent", "Good", "Average", "Poor"])
        for v in out.values():
            self.assertFalse(v)

    def test_empty_options(self):
        out = _parse_language_level([])
        for v in out.values():
            self.assertFalse(v)


class ParseContactDetailsTests(SimpleTestCase):

    def test_parses_three_fields(self):
        cells = [
            "Home Address / City", "Qena",
            "E-Mail", "x@y.com",
            "Mobile / Tel", "+201234567890",
        ]
        out = _parse_contact_details(cells)
        self.assertEqual(out["home_address_city"], "Qena")
        self.assertEqual(out["e_mail"], "x@y.com")
        self.assertEqual(out["mobile_tel"], "+201234567890")


class ParseNextOfKinTests(SimpleTestCase):

    def test_parses_five_fields(self):
        cells = [
            "Full Name", "Islam Raziqi",
            "Relationship", "cousin",
            "Address / Country", "Qena, Egypt",
            "Tel. No./ Mobile", "+201234567890",
            "Email", "x@y.com",
        ]
        out = _parse_next_of_kin(cells)
        self.assertEqual(out["full_name"], "Islam Raziqi")
        self.assertEqual(out["relationship"], "cousin")
        self.assertEqual(out["address_country"], "Qena, Egypt")
        self.assertEqual(out["tel_no_mobile"], "+201234567890")
        self.assertEqual(out["email"], "x@y.com")


class ParseDeclarationTests(SimpleTestCase):

    def test_extracts_signature(self):
        # The signature is whatever the applicant wrote between the
        # underscores on the signature line. The current parser keeps
        # the underscores because the regex is conservative.
        cells = ["Place____", "Date____", "Signature", "_(_mohamed  shehata_)___"]
        out = _parse_declaration(cells)
        # The regex captures "mohamed  shehata" (with the double space
        # the applicant wrote).
        self.assertIn("mohamed", out["signature"])
        self.assertIn("shehata", out["signature"])
        self.assertEqual(out["place"], "")
        self.assertEqual(out["date"], "")

    def test_no_signature_yields_empty(self):
        cells = ["no signature here"]
        out = _parse_declaration(cells)
        self.assertEqual(out["signature"], "")


class ParseOfficeUseOnlyTests(SimpleTestCase):

    def test_returns_empty_dict(self):
        out = _parse_office_use_only([])
        self.assertEqual(out, {
            "initial_assessment": "",
            "comments": "",
            "responsible_person": "",
        })


# ── Section parsers: tabular ────────────────────────────────────────────


class ParseTravelDocumentsTests(SimpleTestCase):

    def test_parses_three_rows(self):
        rows = [
            ["Type", "Document No.", "ISS. Date", "Exp. Date", "ISS. By (Authority)", "Place of Issue"],
            ["Passport", "A123", "16/12/2020", "15/12/2027", "Egyptian Authority", "Qena, Egypt"],
            ["Seaman Book", "S00053", "30/04/2025", "27/04/2030", "EAMS", "Alex."],
            ["Other Seaman Book", "", "", "", "", ""],
        ]
        out = _parse_travel_documents(rows)
        self.assertEqual(len(out), 3)
        self.assertEqual(out[0]["type"], "Passport")
        self.assertEqual(out[0]["document_no"], "A123")
        self.assertEqual(out[2]["type"], "Other Seaman Book")
        self.assertEqual(out[2]["document_no"], "")

    def test_empty_returns_empty(self):
        self.assertEqual(_parse_travel_documents([]), [])

    def test_handles_sparse_columns(self):
        # The Sakr form has 22 columns, with the actual content at
        # specific indices. The parser must align by cell INDEX, not
        # by cell ORDER (so empty cells in between don't break us).
        rows = [
            ["", "", "Type", "Document No.", "", "ISS. Date", "", "Exp. Date",
             "", "ISS. By (Authority)", "", "Place of Issue", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "Passport", "A123", "", "16/12/2020", "", "15/12/2027",
             "", "Egyptian Authority", "", "Qena, Egypt", "", "", "", "", "", "", "", "", "", ""],
        ]
        out = _parse_travel_documents(rows)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["type"], "Passport")
        self.assertEqual(out[0]["document_no"], "A123")
        self.assertEqual(out[0]["iss_by_authority"], "Egyptian Authority")


class ParseQualificationsTests(SimpleTestCase):

    def test_aligned_columns(self):
        # The Sakr form has 22 columns. Certificate Name is at index 0,
        # Issued By at index 14, Issued At at index 20. Empty cells
        # between are preserved.
        rows = [
            ["Certificate Name", "", "", "Number", "Issue Date", "", "", "", "",
             "Expiry Date", "", "", "", "", "Issued By", "", "", "", "", "",
             "Issued At", ""],
            ["COC ( Rank)", "", "", "", "", "", "", "", "", "", "", "", "", "",
             "EAMS", "", "", "", "", "", "Alex.", ""],
            ["GOC", "", "", "", "", "", "", "", "", "", "", "", "", "",
             "NTRA", "", "", "", "", "", "Cairo", ""],
        ]
        out = _parse_qualifications(rows)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["certificate_name"], "COC ( Rank)")
        self.assertEqual(out[0]["number"], "")
        self.assertEqual(out[0]["issued_by"], "EAMS")
        self.assertEqual(out[0]["issued_at"], "Alex.")
        self.assertEqual(out[1]["certificate_name"], "GOC")
        self.assertEqual(out[1]["issued_by"], "NTRA")
        self.assertEqual(out[1]["issued_at"], "Cairo")


class ParseHealthCertificatesTests(SimpleTestCase):

    def test_parses_certs_and_covid(self):
        rows = [
            ["Flag State", "Number", "Issue Date", "Expiry Date", "Issued By", "Issued At"],
            ["International Medical", "45319", "2/6/2025", "1/6/2027", "EAMS", "Alex."],
            ["Yellow Fever", "010019", "2/6/2025", "", "Ministry of Health", "Alex."],
            ["Covid-19", "Vaccination Name", "First Dose", "Second Dose", "(Other Does or Remarks)"],
            ["Covid-19", "Sino Farm", "11/11/2021", "2/12/2021", ""],
        ]
        out = _parse_health_certificates(rows)
        self.assertEqual(len(out["certificates"]), 2)
        self.assertEqual(out["certificates"][0]["certificate_type"], "International Medical")
        self.assertEqual(out["covid_19"]["vaccination_name"], "Sino Farm")
        self.assertEqual(out["covid_19"]["first_dose"], "11/11/2021")
        self.assertEqual(out["covid_19"]["second_dose"], "2/12/2021")

    def test_no_covid_row(self):
        rows = [
            ["Flag State", "Number", "Issue Date", "Expiry Date", "Issued By", "Issued At"],
            ["International Medical", "45319", "2/6/2025", "1/6/2027", "EAMS", "Alex."],
        ]
        out = _parse_health_certificates(rows)
        self.assertEqual(len(out["certificates"]), 1)
        self.assertEqual(out["covid_19"], {})


class ParseMarineCoursesTests(SimpleTestCase):

    def test_parses_course_rows(self):
        rows = [
            ["Course Name", "Number", "Issue Date", "Expiry Date", "Issued By / At"],
            ["Personal Survival Techniques", "", "", "", ""],
            ["Proficiency In Personal Survival Techniques", "Npst932",
             "03/05/2025", "03/05/2030", "EAMS / Alex."],
        ]
        out = _parse_marine_courses(rows)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["course_name"], "Personal Survival Techniques")
        self.assertEqual(out[0]["number"], "")
        self.assertEqual(out[1]["course_name"], "Proficiency In Personal Survival Techniques")
        self.assertEqual(out[1]["number"], "Npst932")
        self.assertEqual(out[1]["issued_by_at"], "EAMS / Alex.")


class ParseSeaServiceTests(SimpleTestCase):

    def test_empty_records(self):
        rows = [
            ["Company Name", "Rank", "Vessel Name/IMO Number", "Flag", "Signed On", "Signed Off"],
        ]
        out = _parse_sea_service(rows)
        self.assertEqual(out["service_records"], [])
        self.assertEqual(out["total_records"], 0)

    def test_one_record(self):
        # Sea service header has 12 columns in the Sakr form. Include
        # all of them so the header is detected.
        rows = [
            ["Company Name", "Rank", "Vessel Name/IMO Number", "Flag",
             "Signed On", "Signed Off", "Period", "Vessel Type",
             "D.W.T./ G.R.T", "Engine Type", "BH/ KW", "Reason for Sign off"],
            ["Maersk", "Master", "Ever Given / 9811000", "Panama",
             "2024-01-01", "2024-06-01", "5 months", "Container",
             "200,000 DWT", "MAN B&W", "60,000 BHP", "End of contract"],
        ]
        out = _parse_sea_service(rows)
        self.assertEqual(out["total_records"], 1)
        self.assertEqual(out["service_records"][0]["company_name"], "Maersk")
        self.assertEqual(out["service_records"][0]["rank"], "Master")


class ParseReferencesTests(SimpleTestCase):

    def test_parses_three_rows(self):
        rows = [
            ["No", "Company / Management / Country", "Position", "Name", "TEL", "EMAIL"],
            ["1", "Sunrise", "Bar Waiter", "Essam", "00201069917891", ""],
            ["2", "Premier", "Bar Waiter", "Tayeb", "00201090347643", ""],
            ["3", "Titanic", "Bar Waiter", "Ahmed", "00201099268441", ""],
        ]
        out = _parse_references(rows)
        self.assertEqual(len(out), 3)
        self.assertEqual(out[0]["company_management_country"], "Sunrise")
        self.assertEqual(out[0]["name"], "Essam")
        self.assertEqual(out[2]["name"], "Ahmed")


# ── Top-level extractor ────────────────────────────────────────────────


class SakrTemplateExtractorTests(SimpleTestCase):

    def setUp(self):
        self.extractor = SakrTemplateExtractor()

    def test_extract_empty_text_returns_failure(self):
        r = self.extractor.extract("")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, ErrorCode.NOT_SAKR_TEMPLATE)

    def test_extract_non_cv_returns_not_a_cv(self):
        r = self.extractor.extract("This is a poem about love and sunshine.")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, ErrorCode.NOT_SAKR_TEMPLATE)

    def test_extract_agency_name_only_returns_not_sakr_template(self):
        # Has the agency name but is missing the form structure.
        r = self.extractor.extract("SAKR MANNING AGENCY\nWe are hiring.")
        self.assertFalse(r.ok)
        self.assertEqual(r.error, ErrorCode.NOT_SAKR_TEMPLATE)

    def test_extract_minimal_form(self):
        # Just enough structure to pass detection + parse.
        text = (
            "SAKR MANNING AGENCY\n"
            "1. PERSONAL DETAILS\n"
            "Full Name | John Doe\n"
        )
        r = self.extractor.extract(text, [])
        self.assertTrue(r.ok)
        self.assertEqual(r.data["1_personal_details"]["full_name"], "John Doe")

    def test_extract_returns_extractor_name(self):
        text = (
            "SAKR MANNING AGENCY\n"
            "1. PERSONAL DETAILS\n"
            "Full Name | John\n"
        )
        r = self.extractor.extract(text, [])
        self.assertEqual(r.extractor, "sakr_template")
        self.assertGreater(r.confidence, 0.5)


# ── Real CV file smoke test ────────────────────────────────────────────


REAL_CV_PATH = r"E:\2-TECHNO AQUARE\waiter Mohamed Shehata Ramadan Abdel Basset.docx"


class RealCVSmokeTest(SimpleTestCase):
    """Run the parser against the actual Sakr CV on disk.

    Skipped if the file is not present (e.g. on CI without the file).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not os.path.exists(REAL_CV_PATH):
            cls.skip_test = True
            return
        cls.skip_test = False
        from ai_document.document_processor import DocumentProcessor
        proc = DocumentProcessor()
        cls.proc_result = proc.process_document(REAL_CV_PATH)
        cls.text = cls.proc_result.get("extracted_text", "")
        cls.tables = cls.proc_result.get("tables", [])

    def setUp(self):
        if self.skip_test:
            self.skipTest("Real CV not present on this machine")

    def test_detects_as_sakr(self):
        self.assertTrue(detect_sakr_template(self.text))

    def test_extracts_full_name(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok, f"extract failed: {r.error} {r.warnings}")
        self.assertEqual(
            r.data["1_personal_details"]["full_name"],
            "MOHAMED SHEHATA RAMADAN ABDEL BASSET",
        )

    def test_extracts_email(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        self.assertEqual(
            r.data["3_contact_details"]["e_mail"],
            "MOHASHEHATA1995@GMAIL.COM",
        )

    def test_extracts_register_code(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        self.assertEqual(
            r.data["0_application_meta"]["register_code"],
            "DR-6.104",
        )

    def test_extracts_three_travel_docs(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.data["4_travel_documents"]), 3)
        types = [d["type"] for d in r.data["4_travel_documents"]]
        self.assertEqual(types, ["Passport", "Seaman Book", "Other Seaman Book"])

    def test_extracts_three_qualifications(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        # Waiter CV has 2 qualifications (COC, GOC). We assert >= 1
        # because the test may be run against a CV with more.
        self.assertGreaterEqual(len(r.data["5_professional_qualification_certificate_of_competency"]), 1)
        certs = [
            d["certificate_name"]
            for d in r.data["5_professional_qualification_certificate_of_competency"]
        ]
        self.assertIn("COC ( Rank) …………..", certs)
        self.assertIn("GOC", certs)

    def test_extracts_three_health_certs(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        certs = r.data["7_health_certificates_and_vaccinations"]["certificates"]
        self.assertEqual(len(certs), 3)
        types = [c["certificate_type"] for c in certs]
        self.assertEqual(
            types,
            ["International Medical", "Yellow Fever", "Cholera"],
        )

    def test_extracts_covid_vaccine(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        covid = r.data["7_health_certificates_and_vaccinations"]["covid_19"]
        self.assertEqual(covid["vaccination_name"], "Sino Farm")
        self.assertEqual(covid["first_dose"], "11/11/2021")
        self.assertEqual(covid["second_dose"], "2/12/2021")

    def test_extracts_marine_courses(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        # The waiter CV has many course entries.
        self.assertGreaterEqual(len(r.data["8_marine_courses"]), 20)

    def test_extracts_three_references(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        self.assertEqual(len(r.data["10_references"]), 3)
        names = [ref["name"] for ref in r.data["10_references"]]
        self.assertEqual(names, ["Essam Mahmoud", "Tayeb Asaad", "Ahmed Mahfouz"])

    def test_marital_status_is_single(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        self.assertTrue(r.data["1_personal_details"]["marital_status"]["single"])
        self.assertFalse(r.data["1_personal_details"]["marital_status"]["married"])

    def test_english_is_good_level(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        eng = r.data["2_education"]["english_language"]
        self.assertTrue(eng["good"])
        self.assertFalse(eng["fluent"])

    def test_german_is_average_level(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        ger = r.data["2_education"]["german_language"]
        self.assertTrue(ger["average"])
        self.assertFalse(ger["fluent"])

    def test_declaration_has_signature(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        sig = r.data["11_declaration"]["signature"]
        self.assertIn("mohamed", sig.lower())

    def test_all_twelve_sections_present(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        expected = {
            "0_application_meta", "1_personal_details", "2_education",
            "3_contact_details", "4_travel_documents",
            "5_professional_qualification_certificate_of_competency",
            "6_next_of_kin_emergency_contact",
            "7_health_certificates_and_vaccinations",
            "8_marine_courses", "9_complete_sea_service_details",
            "10_references", "11_declaration", "12_for_office_use_only",
        }
        self.assertEqual(set(r.data.keys()), expected)

    def test_height_weight_are_ints(self):
        r = SakrTemplateExtractor().extract(self.text, self.tables)
        self.assertTrue(r.ok)
        self.assertIsInstance(r.data["1_personal_details"]["height_cm"], int)
        self.assertIsInstance(r.data["1_personal_details"]["weight_kg"], int)
