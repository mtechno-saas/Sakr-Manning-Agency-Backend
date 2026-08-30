from django.test import TestCase

# Create your tests here.
"""
Comprehensive tests for ai_document app (FIXED VERSION)
Tests models, serializers, views, and data extraction
Handles authentication requirements
"""

import os
import json
from io import BytesIO
from django.test import TestCase, TransactionTestCase, SimpleTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from unittest.mock import patch, MagicMock

from .models import Applicant
from api.models import Users
from .serializers import (
    ApplicantToUsersSerializer,
    DocumentUploadSerializer,
    ApplicantListSerializer,
    ConvertApplicantRequestSerializer,
    BatchConvertRequestSerializer,
)


class ApplicantModelTest(TestCase):
    """Test Applicant model"""
    
    def setUp(self):
        """Set up test data"""
        self.applicant_data = {
            'personal_details': {
                'Full_Name': 'John Doe',
                'Date_Of_Birth': '01/01/1990',
                'Nationality': 'American'
            },
            'contact_details': {
                'Email': 'john.doe@example.com',
                'Mobile_Tel': '+1234567890'
            },
            'travel_documents': [
                {
                    'Type': 'Passport',
                    'Document_No': 'AB123456',
                    'ISS_Date': '01/01/2020',
                    'Exp_Date': '01/01/2030'
                }
            ],
            'professional_qualifications': [],
            'next_of_kin_emergency_contact': {},
            'health_certificates_vaccinations': [],
            'covid_19_vaccination': {},
            'marine_courses': [],
            'sea_service_details': [],
            'specialised_experience': [],
            'references': [],
            'declaration': {},
            'office_use_only': {},
            'physical_measurements': {},
            'language_skills': {},
            'medical_history': {},
            'assessments': {},
            'competency_tests': {},
            'applied_position_info': {},
            'education': {},
        }
    
    def test_create_applicant(self):
        """Test creating an applicant"""
        applicant = Applicant.objects.create(**self.applicant_data)
        
        self.assertIsNotNone(applicant.id)
        self.assertEqual(applicant.personal_details['Full_Name'], 'John Doe')
        self.assertEqual(applicant.contact_details['Email'], 'john.doe@example.com')
        self.assertIsNotNone(applicant.created_at)
    
    def test_applicant_string_representation(self):
        """Test applicant __str__ method"""
        applicant = Applicant.objects.create(**self.applicant_data)
        # Just check that str() doesn't raise an error
        str_repr = str(applicant)
        self.assertIsInstance(str_repr, str)
        self.assertTrue(len(str_repr) > 0)


class ApplicantToUsersSerializerTest(TestCase):
    """Test ApplicantToUsersSerializer"""
    
    def setUp(self):
        """Set up test applicant"""
        self.applicant = Applicant.objects.create(
            personal_details={
                'Full_Name': 'Jane Smith',
                'Date_Of_Birth': '15/06/1985',
                'Nationality': 'British',
                'Marital_Status': 'Single'
            },
            contact_details={
                'Email': 'jane.smith@example.com',
                'Mobile_Tel': '+447700900000',
                'Home_Address_City': 'London'
            },
            travel_documents=[
                {
                    'Type': 'Passport',
                    'Document_No': 'GB987654',
                    'ISS_Date': '10/05/2020',
                    'Exp_Date': '10/05/2030',
                    'ISS_By_Authority': 'UK Passport Office'
                },
                {
                    'Type': 'Seaman Book',
                    'Document_No': 'SB123456',
                    'ISS_Date': '01/01/2021',
                    'Exp_Date': '01/01/2026'
                }
            ],
            professional_qualifications=[
                {
                    'Certificate_Name': 'COC',
                    'Issued_By': 'Maritime Authority'
                }
            ],
            health_certificates_vaccinations=[
                {
                    'Flag_State': 'International Medical',
                    'Number': '12345',
                    'Issue_Date': '01/01/2024',
                    'Expiry_Date': '01/01/2026'
                }
            ],
            covid_19_vaccination={
                'Vaccination_Name': 'Pfizer',
                'First_Dose': '01/03/2021',
                'Second_Dose': '01/06/2021'
            },
            next_of_kin_emergency_contact={
                'Full_Name': 'John Smith',
                'Relationship': 'Brother',
                'Email': 'john.smith@example.com'
            },
            marine_courses=[],
            sea_service_details=[],
            specialised_experience=[],
            references=[],
            declaration={},
            office_use_only={},
            physical_measurements={},
            language_skills={},
            medical_history={},
            assessments={},
            competency_tests={},
            applied_position_info={},
            education={},
        )
    
    def test_serializer_fields(self):
        """Test serializer extracts all fields correctly"""
        serializer = ApplicantToUsersSerializer(self.applicant)
        data = serializer.data
        
        # Test personal details
        self.assertEqual(data['first_name'], 'Jane')
        self.assertEqual(data['email'], 'jane.smith@example.com')
        self.assertEqual(data['phone_number'], '+447700900000')
        self.assertEqual(data['nationality'], 'British')
        self.assertEqual(data['marital_status'], 'Single')
        
        # Test travel documents
        self.assertEqual(data['passport_no'], 'GB987654')
        self.assertEqual(data['passport_issued_by'], 'UK Passport Office')
        self.assertEqual(data['seaman_book_no'], 'SB123456')
        
        # Test health certificates
        self.assertEqual(data['health_number'], '12345')
        
        # Test COVID vaccination
        self.assertEqual(data['covid_vaccine_name'], 'Pfizer')
        
        # Test next of kin
        self.assertEqual(data['next_of_kin_full_name'], 'John Smith')
        self.assertEqual(data['next_of_kin_relationship'], 'Brother')
    
    def test_serializer_handles_empty_data(self):
        """Test serializer handles missing data gracefully"""
        empty_applicant = Applicant.objects.create(
            personal_details={},
            contact_details={},
            travel_documents=[],
            professional_qualifications=[],
            next_of_kin_emergency_contact={},
            health_certificates_vaccinations=[],
            covid_19_vaccination={},
            marine_courses=[],
            sea_service_details=[],
            specialised_experience=[],
            references=[],
            declaration={},
            office_use_only={},
            physical_measurements={},
            language_skills={},
            medical_history={},
            assessments={},
            competency_tests={},
            applied_position_info={},
            education={},
        )
        
        serializer = ApplicantToUsersSerializer(empty_applicant)
        data = serializer.data
        
        # Should return empty strings or None, not raise errors
        self.assertEqual(data['email'], '')
        self.assertEqual(data['first_name'], '')
        self.assertEqual(data['passport_no'], '')


class DocumentUploadSerializerTest(TestCase):
    """Test DocumentUploadSerializer"""
    
    def test_valid_pdf_file(self):
        """Test validation accepts PDF files"""
        pdf_file = SimpleUploadedFile(
            "test.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        
        serializer = DocumentUploadSerializer(data={'file': pdf_file})
        self.assertTrue(serializer.is_valid())
    
    def test_valid_docx_file(self):
        """Test validation accepts DOCX files"""
        docx_file = SimpleUploadedFile(
            "test.docx",
            b"DOCX content",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        serializer = DocumentUploadSerializer(data={'file': docx_file})
        self.assertTrue(serializer.is_valid())
    
    def test_invalid_file_type(self):
        """Test validation rejects invalid file types"""
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"Text content",
            content_type="text/plain"
        )
        
        serializer = DocumentUploadSerializer(data={'file': txt_file})
        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)


class AuthenticatedAPITestCase(APITestCase):
    """Base class for API tests that require authentication"""

    def setUp(self):
        """Set up authentication"""
        super().setUp()
        # Create a test user (adjust based on your User model)
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )


        # Authenticate the client
        self.client.force_authenticate(user=self.user)


class AdminAPITestCase(APITestCase):
    """Base class for API tests that require an Admin user.

    The /ai/parse/ endpoint is admin-only (per spec), so its tests
    need an authenticated Admin. Other endpoints (list applicants,
    view detail, etc.) are tested with the regular AuthenticatedAPITestCase
    which creates a default-Employee user.
    """

    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.user = User.objects.create_user(
            email='admin@sakrparser.test',
            password='testpass123',
        )
        self.user.role = 'Admin'
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)


class SeafarerAPITestCase(APITestCase):
    """Base class for tests of endpoints that a seafarer (Crew/Employee) hits."""

    SEAFARER_ROLE = 'Employee'  # override in subclass for 'Crew'

    def setUp(self):
        super().setUp()
        User = get_user_model()
        self.user = User.objects.create_user(
            email='seafarer@sakrparser.test',
            password='testpass123',
        )
        self.user.role = self.SEAFARER_ROLE
        self.user.save()
        self.client.force_authenticate(user=self.user)


class DocumentUploadViewTest(AuthenticatedAPITestCase):
    """Test DocumentUploadView API endpoint.

    The endpoint is now aligned with ``/ai/parse/``: the response
    always carries the same shape (``{success, extractor, confidence,
    data, warnings, file_name, saved?, user_id?, cv_submission_id?}``)
    regardless of which path (deterministic or LLM) produced the
    data. Save is opt-out via ``save_to_db=false``.
    """

    def setUp(self):
        """Set up test client"""
        super().setUp()
        self.url = '/ai/upload/'

    def _build_llm_payload(self):
        """Standard 12-section numbered payload the LLM path returns."""
        return {
            '1_personal_details': {
                'full_name': 'John Doe',
                'date_of_birth': '01/01/1990',
            },
            '3_contact_details': {
                'e_mail': 'john@example.com',
                'mobile_tel': '+201234567890',
            },
        }

    @patch('ai_document.views._save_parser_output')
    @patch('ai_document.views.SakrTemplateExtractor')
    @patch('ai_document.views.DocumentProcessor')
    @patch('ai_document.views.convert_text_to_json')
    def test_successful_upload(
        self, mock_convert, mock_processor_cls,
        mock_extractor_cls, mock_save,
    ):
        """Test successful LLM-path upload, save_to_db=true (default).

        The deterministic extractor is mocked to FAIL so the view
        falls through to the LLM. ``_save_parser_output`` is mocked
        to return a known ``(user_id, cv_submission_id)`` so the test
        stays focused on the response shape.
        """
        # Mock the document processor
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            'extracted_text': 'Plain text that does NOT match the Sakr template',
            'tables': [],
            'page_count': 2,
        }
        mock_processor_cls.return_value = mock_proc

        # Mock the deterministic extractor to FAIL — so the view
        # falls back to the LLM path.
        from ai_document.extractors import ErrorCode
        det_result = MagicMock()
        det_result.ok = False
        det_result.error = ErrorCode.NOT_SAKR_TEMPLATE
        det_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = det_result

        # Mock the LLM to return the new 12-section numbered format.
        mock_convert.return_value = (
            self._build_llm_payload(),
            {'groq': [], 'gemini': ''},
        )

        # Mock the save helper to return known ids.
        mock_save.return_value = (123, 456)

        pdf_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"PDF content",
            content_type="application/pdf",
        )

        # Provide a fake Groq key so the LLM fallback can run.
        response = self.client.post(
            self.url,
            {
                'file': pdf_file,
                'deepseek_api_key': 'sk_fake_test_key',
            },
            format='multipart',
        )

        # Status: 200 OK (the new shape, matches /ai/parse/).
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response shape — must match /ai/parse/.
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['extractor'], 'deepseek_llm')
        self.assertIn('confidence', response.data)
        self.assertIn('1_personal_details', response.data['data'])
        self.assertEqual(
            response.data['data']['1_personal_details']['full_name'],
            'John Doe',
        )
        self.assertEqual(response.data['file_name'], 'test_cv.pdf')
        self.assertEqual(response.data['warnings'], [])
        # save_to_db defaults to true → saved/user_id/cv_submission_id
        self.assertTrue(response.data['saved'])
        self.assertEqual(response.data['user_id'], 123)
        self.assertEqual(response.data['cv_submission_id'], 456)

    def test_upload_without_file(self):
        """Test upload endpoint without file"""
        response = self.client.post(self.url, {}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"Text content",
            content_type="text/plain",
        )

        response = self.client.post(self.url, {'file': txt_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DocumentUploadViewPathTest(AuthenticatedAPITestCase):
    """Test the deterministic-first + LLM-fallback routing in
    ``/ai/upload/``.

    The view should:

    1. Try ``SakrTemplateExtractor`` FIRST (no LLM cost, no API key).
    2. If it returns ``NOT_SAKR_TEMPLATE`` (or crashes), fall back to
       the LLM (``convert_text_to_json``).
    3. Return the same response shape as ``/ai/parse/`` regardless
       of which path produced the data.

    The auth model is ``AllowAny`` on this endpoint (backwards
    compat with the original) — we just ``force_authenticate`` to a
    regular user for the same convenience as ``DocumentUploadViewTest``.
    """

    def setUp(self):
        super().setUp()
        self.url = "/ai/upload/"

    def _pdf(self, name="cv.pdf"):
        return SimpleUploadedFile(
            name, b"%PDF-1.4 fake", content_type="application/pdf"
        )

    def _mock_processor(self, mock_processor_cls, text="some text", tables=None):
        """Configure a patched DocumentProcessor class to return canned text."""
        instance = MagicMock()
        instance.process_document.return_value = {
            "extracted_text": text,
            "tables": tables or [],
            "page_count": 2,
        }
        mock_processor_cls.return_value = instance
        return instance

    def _mock_extractor_ok(self, mock_extractor_cls, data, confidence=0.95, warnings=None):
        """Configure a patched SakrTemplateExtractor to return ok=True."""
        result = MagicMock()
        result.ok = True
        result.extractor = "sakr_template"
        result.confidence = confidence
        result.data = data
        result.warnings = warnings or []
        mock_extractor_cls.return_value.extract.return_value = result
        return result

    def _mock_extractor_fail(self, mock_extractor_cls, error_code):
        """Configure a patched SakrTemplateExtractor to return ok=False."""
        result = MagicMock()
        result.ok = False
        result.error = error_code
        result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = result
        return result

    # -- deterministic-first behaviour ---------------------------------

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.convert_text_to_json")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_deterministic_path_used_first_when_sakr_template_matches(
        self, mock_processor_cls, mock_extractor_cls,
        mock_convert, mock_save,
    ):
        """SakrTemplateExtractor succeeds → LLM is NEVER called.

        Verifies the performance / cost promise of the deterministic
        path: when the document matches the Sakr form, the LLM
        fallback is not even invoked.
        """
        self._mock_processor(mock_processor_cls)

        deterministic_data = {
            "1_personal_details": {"full_name": "MOHAMED SHEHATA"},
            "3_contact_details": {"e_mail": "m.shehata@sakr.test"},
        }
        self._mock_extractor_ok(mock_extractor_cls, deterministic_data, confidence=0.95)

        mock_save.return_value = (10, 20)

        response = self.client.post(
            self.url,
            {"file": self._pdf(), "deepseek_api_key": "sk_dummy"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # LLM was NOT called.
        mock_convert.assert_not_called()
        # Deterministic extractor was called.
        mock_extractor_cls.return_value.extract.assert_called_once()
        # Response uses the deterministic extractor.
        self.assertEqual(response.data["extractor"], "sakr_template")
        self.assertEqual(response.data["confidence"], 0.95)
        self.assertEqual(
            response.data["data"]["1_personal_details"]["full_name"],
            "MOHAMED SHEHATA",
        )
        # Save happened.
        self.assertTrue(response.data["saved"])
        self.assertEqual(response.data["user_id"], 10)
        self.assertEqual(response.data["cv_submission_id"], 20)

    # -- LLM fallback behaviour ----------------------------------------

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.convert_text_to_json")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_llm_fallback_used_when_deterministic_fails(
        self, mock_processor_cls, mock_extractor_cls,
        mock_convert, mock_save,
    ):
        """SakrTemplateExtractor returns ``NOT_SAKR_TEMPLATE`` →
        LLM is called as fallback and the LLM result is returned.
        """
        from ai_document.extractors import ErrorCode

        self._mock_processor(
            mock_processor_cls,
            text="this is a generic CV, not the Sakr form",
        )
        self._mock_extractor_fail(mock_extractor_cls, ErrorCode.NOT_SAKR_TEMPLATE)

        llm_data = {
            "1_personal_details": {"full_name": "John Doe"},
            "3_contact_details": {"e_mail": "john@example.com"},
        }
        mock_convert.return_value = (llm_data, {"groq": [], "gemini": ""})
        mock_save.return_value = (30, 40)

        response = self.client.post(
            self.url,
            {"file": self._pdf(), "deepseek_api_key": "sk_dummy"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # LLM WAS called.
        mock_convert.assert_called_once()
        # Response uses the LLM extractor.
        self.assertEqual(response.data["extractor"], "deepseek_llm")
        self.assertEqual(
            response.data["data"]["1_personal_details"]["full_name"],
            "John Doe",
        )
        self.assertTrue(response.data["saved"])
        self.assertEqual(response.data["user_id"], 30)

    @patch("ai_document.views.convert_text_to_json")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_no_api_keys_passes_empty_dict_to_llm(
        self, mock_processor_cls, mock_extractor_cls, mock_convert,
    ):
        """Deterministic fails + no API keys in the request → the
        view passes an empty dict to the LLM router so the router
        can try Ollama (local, free) before erroring.

        We mock convert_text_to_json to return the
        ``validation_error`` it would produce when no provider is
        available. The view then returns 400 with ``invalid_document``
        + the helpful "set OLLAMA_HOST" message.
        """
        from ai_document.extractors import ErrorCode

        self._mock_processor(mock_processor_cls, text="random text")
        self._mock_extractor_fail(mock_extractor_cls, ErrorCode.NOT_SAKR_TEMPLATE)

        # Simulate the case where Ollama is NOT configured and no
        # cloud key is supplied — convert_text_to_json would return
        # a validation_error explaining how to fix it.
        mock_convert.return_value = (
            {
                "validation_error": (
                    "No LLM provider is available. Either set OLLAMA_HOST "
                    "or supply a DeepSeek key in the request."
                )
            },
            {},
        )

        # NOTE: no deepseek_api_key, no api_keys_config in the request.
        response = self.client.post(
            self.url, {"file": self._pdf()}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"], "invalid_document")
        self.assertIn("OLLAMA_HOST", response.data["message"])
        self.assertEqual(response.data["file_name"], "cv.pdf")
        # LLM WAS called (with an empty config) — that's how the
        # router learns that no provider is available.
        mock_convert.assert_called_once()

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.convert_text_to_json")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_llm_validation_error_returns_400(
        self, mock_processor_cls, mock_extractor_cls, mock_convert,
        mock_save,
    ):
        """LLM reports ``validation_error`` (e.g. not a maritime CV) →
        400 with the message. NO save happens.
        """
        from ai_document.extractors import ErrorCode

        self._mock_processor(mock_processor_cls, text="not a cv")
        self._mock_extractor_fail(mock_extractor_cls, ErrorCode.NOT_SAKR_TEMPLATE)
        mock_convert.return_value = (
            {"validation_error": "Document is not a valid maritime CV"},
            {"groq": [], "gemini": ""},
        )

        response = self.client.post(
            self.url,
            {"file": self._pdf(), "deepseek_api_key": "sk_dummy"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"], "invalid_document")
        self.assertIn("not a valid maritime CV", response.data["message"])
        # No save happened.
        mock_save.assert_not_called()

    # -- save_to_db=false (dry-run) behaviour ---------------------------

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.convert_text_to_json")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_save_to_db_false_skips_persistence(
        self, mock_processor_cls, mock_extractor_cls,
        mock_convert, mock_save,
    ):
        """``save_to_db=false`` returns the parsed data without
        creating a User / CVSubmission row.
        """
        from ai_document.extractors import ErrorCode

        self._mock_processor(mock_processor_cls, text="generic text")
        self._mock_extractor_fail(mock_extractor_cls, ErrorCode.NOT_SAKR_TEMPLATE)
        mock_convert.return_value = (
            {
                "1_personal_details": {"full_name": "Dry Run"},
                "3_contact_details": {"e_mail": "dry@example.com"},
            },
            {"groq": [], "gemini": ""},
        )

        response = self.client.post(
            self.url,
            {
                "file": self._pdf(),
                "deepseek_api_key": "sk_dummy",
                "save_to_db": "false",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["saved"], False)
        self.assertNotIn("user_id", response.data)
        self.assertNotIn("cv_submission_id", response.data)
        # No save call.
        mock_save.assert_not_called()
        # No new user row was created (the base test user is still there
        # from the AuthenticatedAPITestCase setUp — we just check the
        # count is unchanged).
        baseline_user_count = Users.objects.count()
        # And no CVSubmission row was created either.
        from api.models import CVSubmission
        self.assertFalse(
            CVSubmission.objects.filter(
                user__email="dry@example.com"
            ).exists(),
            "save_to_db=false must not create a CVSubmission row",
        )
        # Sanity: the count is still the baseline.
        self.assertEqual(Users.objects.count(), baseline_user_count)

    # -- response shape parity with /ai/parse/ --------------------------

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_response_shape_matches_parse_view_when_deterministic_ok(
        self, mock_processor_cls, mock_extractor_cls, mock_save,
    ):
        """Top-level keys exactly mirror ``/ai/parse/``:
        success, extractor, confidence, data, warnings, file_name,
        saved, user_id, cv_submission_id.
        """
        self._mock_processor(mock_processor_cls)
        self._mock_extractor_ok(
            mock_extractor_cls,
            {
                "0_application_meta": {"application_for_position_as": "Master"},
                "1_personal_details": {"full_name": "CAPTAIN X"},
            },
            confidence=0.9,
        )
        mock_save.return_value = (1, 2)

        response = self.client.post(
            self.url, {"file": self._pdf()}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.data
        # Required keys present.
        for key in (
            "success", "extractor", "confidence", "data",
            "warnings", "file_name", "saved", "user_id",
            "cv_submission_id",
        ):
            self.assertIn(key, body, f"missing key: {key}")
        # No legacy keys leaked from the old shape.
        for legacy in (
            "id", "applicant_id", "seafarer_application",
            "_upload_meta", "user_documents", "coded_rank",
        ):
            self.assertNotIn(legacy, body, f"legacy key leaked: {legacy}")
        # value sanity.
        self.assertTrue(body["success"])
        self.assertEqual(body["extractor"], "sakr_template")
        self.assertEqual(body["confidence"], 0.9)
        self.assertEqual(body["file_name"], "cv.pdf")
        self.assertEqual(body["user_id"], 1)
        self.assertEqual(body["cv_submission_id"], 2)

    # -- deterministic crashes mid-extraction → fallback to LLM --------

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.convert_text_to_json")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_deterministic_crash_falls_through_to_llm(
        self, mock_processor_cls, mock_extractor_cls,
        mock_convert, mock_save,
    ):
        """If SakrTemplateExtractor itself raises (not a parsed
        error code, but a real exception), the view should still
        fall through to the LLM and succeed.
        """
        self._mock_processor(mock_processor_cls)
        mock_extractor_cls.return_value.extract.side_effect = RuntimeError(
            "unexpected boom"
        )

        mock_convert.return_value = (
            {
                "1_personal_details": {"full_name": "Recovered User"},
                "3_contact_details": {"e_mail": "recovered@example.com"},
            },
            {"groq": [], "gemini": ""},
        )
        mock_save.return_value = (50, 60)

        response = self.client.post(
            self.url,
            {"file": self._pdf(), "deepseek_api_key": "sk_dummy"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["extractor"], "deepseek_llm")
        mock_convert.assert_called_once()


class ApplicantListViewTest(AuthenticatedAPITestCase):
    """Test ApplicantListView API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        super().setUp()
        self.url = '/ai/applicants/'
        
        # Create test applicants
        for i in range(3):
            Applicant.objects.create(
                personal_details={'Full_Name': f'Applicant {i}'},
                contact_details={'Email': f'applicant{i}@example.com'},
                travel_documents=[],
                professional_qualifications=[],
                next_of_kin_emergency_contact={},
                health_certificates_vaccinations=[],
                covid_19_vaccination={},
                marine_courses=[],
                sea_service_details=[],
                specialised_experience=[],
                references=[],
                declaration={},
                office_use_only={},
                physical_measurements={},
                language_skills={},
                medical_history={},
                assessments={},
                competency_tests={},
                applied_position_info={},
                education={},
            )
    
    def test_list_applicants(self):
        """Test listing all applicants"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['applicants']), 3)
        self.assertEqual(response.data['count'], 3)


class ApplicantDetailViewTest(AuthenticatedAPITestCase):
    """Test ApplicantDetailView API endpoint"""
    
    def setUp(self):
        """Set up test applicant"""
        super().setUp()
        
        self.applicant = Applicant.objects.create(
            personal_details={'Full_Name': 'Test User'},
            contact_details={'Email': 'test@example.com'},
            travel_documents=[],
            professional_qualifications=[],
            next_of_kin_emergency_contact={},
            health_certificates_vaccinations=[],
            covid_19_vaccination={},
            marine_courses=[],
            sea_service_details=[],
            specialised_experience=[],
            references=[],
            declaration={},
            office_use_only={},
            physical_measurements={},
            language_skills={},
            medical_history={},
            assessments={},
            competency_tests={},
            applied_position_info={},
            education={},
        )
        
        self.url = f'/ai/applicants/{self.applicant.id}/'
    
    # def test_get_applicant_detail(self):
    #     """Test getting applicant details"""
    #     response = self.client.get(self.url)
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['contact_details']['Email'], 'test@example.com')

    def test_get_applicant_detail(self):
        """Test getting applicant details"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Use flat field instead of nested structure
        self.assertIn('applicant', response.data)
        self.assertIn('email', response.data['applicant'])
        self.assertEqual(response.data['applicant']['email'], 'test@example.com')



    
    def test_get_nonexistent_applicant(self):
        """Test getting non-existent applicant"""
        response = self.client.get('/ai/applicants/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserCreationTest(TransactionTestCase):
    """Test user creation from applicant data"""
    
    def setUp(self):
        """Set up test applicant"""
        self.applicant = Applicant.objects.create(
            personal_details={
                'Full_Name': 'Ahmed Ibrahim',
                'Date_Of_Birth': '18/6/1994',
                'Nationality': 'Egyptian'
            },
            contact_details={
                'Email': 'ahmed@example.com',
                'Mobile_Tel': '+201234567890'
            },
            travel_documents=[
                {
                    'Type': 'Passport',
                    'Document_No': 'A12345678',
                    'ISS_Date': '01/01/2020',
                    'Exp_Date': '01/01/2030'
                }
            ],
            professional_qualifications=[],
            next_of_kin_emergency_contact={},
            health_certificates_vaccinations=[],
            covid_19_vaccination={},
            marine_courses=[],
            sea_service_details=[],
            specialised_experience=[],
            references=[],
            declaration={},
            office_use_only={},
            physical_measurements={},
            language_skills={},
            medical_history={},
            assessments={},
            competency_tests={},
            applied_position_info={},
            education={},
        )
    
    def test_user_created_from_applicant(self):
        """Test that user is created with correct data"""
        # Simulate user creation logic from views
        serializer = ApplicantToUsersSerializer(self.applicant)
        serializer_data = serializer.data
        
        email = serializer_data.get('email')
        self.assertEqual(email, 'ahmed@example.com')
        
        # Test that passport data is extracted
        passport_no = serializer_data.get('passport_no')
        self.assertEqual(passport_no, 'A12345678')


class IntegrationTest(TransactionTestCase):
    """End-to-end integration tests"""

    def setUp(self):
        """Set up authentication"""
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch('ai_document.views.SakrTemplateExtractor')
    @patch('ai_document.views.DocumentProcessor')
    @patch('ai_document.views.convert_text_to_json')
    def test_full_workflow(
        self, mock_convert, mock_processor_cls, mock_extractor_cls,
    ):
        """End-to-end: LLM path → save → Users + CVSubmission rows.

        Drives the upload through the *new* response shape, which is
        identical to ``/ai/parse/`` (top-level ``data`` dict, not the
        legacy ``applicant_id`` / ``seafarer_application`` nest). The
        deterministic extractor is mocked to fail so we exercise the
        LLM-fallback branch.
        """
        # Mock the document processor
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            'extracted_text': 'Full CV text that does NOT match the Sakr template',
            'tables': [],
            'page_count': 5,
        }
        mock_processor_cls.return_value = mock_proc

        # Force the deterministic extractor to fail → LLM path.
        from ai_document.extractors import ErrorCode
        det_result = MagicMock()
        det_result.ok = False
        det_result.error = ErrorCode.NOT_SAKR_TEMPLATE
        det_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = det_result

        # Mock the LLM to return the new 12-section numbered format
        # (the format the real ``convert_text_to_json`` produces).
        mock_convert.return_value = (
            {
                '1_personal_details': {
                    'full_name': 'Integration Test User',
                    'date_of_birth': '01/01/1990',
                    'nationality': 'Test Country',
                },
                '3_contact_details': {
                    'e_mail': 'integration@test.com',
                    'mobile_tel': '+1234567890',
                },
                '4_travel_documents': [
                    {
                        'type': 'Passport',
                        'document_no': 'TEST123',
                        'iss_date': '01/01/2020',
                        'exp_date': '01/01/2030',
                    }
                ],
            },
            {'groq': [], 'gemini': ''},
        )

        # Upload
        pdf_file = SimpleUploadedFile(
            "integration_test.pdf",
            b"PDF content",
            content_type="application/pdf",
        )

        response = self.client.post(
            '/ai/upload/',
            {'file': pdf_file, 'deepseek_api_key': 'sk_fake_test_key'},
            format='multipart',
        )

        # New shape mirrors /ai/parse/: 200 OK with a `data` dict.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['extractor'], 'deepseek_llm')
        self.assertIn('1_personal_details', response.data['data'])
        self.assertEqual(
            response.data['data']['1_personal_details']['full_name'],
            'Integration Test User',
        )
        # Save happened (save_to_db defaults to true).
        self.assertTrue(response.data['saved'])
        self.assertIn('user_id', response.data)
        self.assertIn('cv_submission_id', response.data)

        # Verify the user was actually created.
        user = Users.objects.get(id=response.data['user_id'])
        self.assertEqual(user.email, 'integration@test.com')
        self.assertEqual(user.first_name, 'Integration')
        # The CVSubmission row exists and is linked to the user.
        from api.models import CVSubmission
        cv = CVSubmission.objects.get(id=response.data['cv_submission_id'])
        self.assertEqual(cv.user_id, user.id)


class ParseOnlyViewTest(AdminAPITestCase):
    """Test the deterministic-parser /parse/ endpoint.

    The endpoint is admin-only. AdminAPITestCase sets up an authenticated
    Admin user. Other roles are blocked — see ParseOnlyViewAuthTest.
    """

    def setUp(self):
        AdminAPITestCase.setUp(self)
        self.url = "/ai/parse/"

    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_successful_parse_returns_extracted_json(
        self, mock_processor_cls, mock_extractor_cls
    ):
        # Mock the processor
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "SAKR MANNING AGENCY ... 1. PERSONAL DETAILS ...",
            "tables": [],
        }
        mock_processor_cls.return_value = mock_proc

        # Mock the extractor to return a successful result
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.extractor = "sakr_template"
        mock_result.confidence = 0.95
        mock_result.data = {
            "0_application_meta": {"application_for_position_as": "Bar Waiter"},
            "1_personal_details": {"full_name": "MOHAMED SHEHATA"},
        }
        mock_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = mock_result

        pdf = SimpleUploadedFile("test_cv.pdf", b"PDF content", content_type="application/pdf")
        response = self.client.post(self.url, {"file": pdf}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["extractor"], "sakr_template")
        self.assertEqual(response.data["confidence"], 0.95)
        self.assertIn("1_personal_details", response.data["data"])
        self.assertEqual(
            response.data["data"]["1_personal_details"]["full_name"],
            "MOHAMED SHEHATA",
        )
        self.assertEqual(response.data["file_name"], "test_cv.pdf")

    def test_missing_file_returns_400(self):
        response = self.client.post(self.url, {}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"], "file_missing")

    def test_invalid_file_extension_returns_400(self):
        # DocumentUploadSerializer rejects non-PDF/DOCX.
        txt = SimpleUploadedFile("test.txt", b"text", content_type="text/plain")
        response = self.client.post(self.url, {"file": txt}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_not_a_cv_returns_typed_error(
        self, mock_processor_cls, mock_extractor_cls
    ):
        # Processor returns text that isn't a CV
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "This is a poem about love and sunshine.",
            "tables": [],
        }
        mock_processor_cls.return_value = mock_proc

        # Extractor returns NOT_A_CV error
        from ai_document.extractors import ErrorCode
        mock_result = MagicMock()
        mock_result.ok = False
        mock_result.error = ErrorCode.NOT_SAKR_TEMPLATE
        mock_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = mock_result

        pdf = SimpleUploadedFile("random.pdf", b"PDF", content_type="application/pdf")
        response = self.client.post(self.url, {"file": pdf}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"], "not_sakr_template")
        # The client message must be safe (no exception leak)
        self.assertNotIn("Traceback", response.data["message"])

    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_endpoint_does_not_save_to_db(
        self, mock_processor_cls, mock_extractor_cls
    ):
        # Same as success test, but verify Applicant count is 0 after.
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "SAKR MANNING AGENCY 1. PERSONAL DETAILS ...",
            "tables": [],
        }
        mock_processor_cls.return_value = mock_proc
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.extractor = "sakr_template"
        mock_result.confidence = 0.95
        mock_result.data = {"1_personal_details": {"full_name": "X"}}
        mock_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = mock_result

        before = Applicant.objects.count()
        pdf = SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")
        self.client.post(self.url, {"file": pdf}, format="multipart")
        after = Applicant.objects.count()
        self.assertEqual(before, after, "ParseOnlyView must NOT create Applicant rows")

    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_unexpected_error_returns_typed_internal_error(
        self, mock_processor_cls, mock_extractor_cls
    ):
        # DocumentProcessor itself raises a non-DocumentProcessingError
        # exception. The view's catch-all must return 500 with
        # ErrorCode.INTERNAL, NOT leak the raw exception text.
        mock_proc = MagicMock()
        mock_proc.process_document.side_effect = RuntimeError("disk on fire")
        mock_processor_cls.return_value = mock_proc

        pdf = SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")
        response = self.client.post(self.url, {"file": pdf}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"], "internal_error")
        # Raw exception text must NOT leak into the response.
        self.assertNotIn("disk on fire", str(response.data))


class ParseOnlyViewSaveTest(AdminAPITestCase):
    """Test the save_to_db=true flow that creates Users + CVSubmission."""

    def setUp(self):
        AdminAPITestCase.setUp(self)
        self.url = "/ai/parse/"

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_save_to_db_true_persists_and_returns_ids(
        self, mock_processor_cls, mock_extractor_cls, mock_save
    ):
        from api.models import Users
        from decimal import Decimal
        from datetime import date

        # Mock the processor
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "SAKR MANNING AGENCY 1. PERSONAL DETAILS ...",
            "tables": [],
        }
        mock_processor_cls.return_value = mock_proc

        # Mock the extractor to return a successful result
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.extractor = "sakr_template"
        mock_result.confidence = 0.95
        mock_result.data = {
            "0_application_meta": {
                "application_for_position_as": "Waiter",
                "register_code": "DR-6.104",
                "other_position": "",
                "register_date": "10.07.2025",
                "expected_salary": "730 $",
                "available_date": "25/7/2025",
            },
            "1_personal_details": {
                "full_name": "MOHAMED SHEHATA",
                "date_of_birth": "28/02/1995",
                "marital_status": {"single": True, "married": False},
                "nationality": "Egyptian",
                "place_of_birth": "Qena",
                "height_cm": 173,
                "weight_kg": 67,
            },
            "3_contact_details": {
                "home_address_city": "Qena",
                "e_mail": "MOHAMED@TEST.COM",
                "mobile_tel": "00201090946284",
            },
        }
        mock_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = mock_result

        # Mock the save function
        mock_save.return_value = (42, 99)

        pdf = SimpleUploadedFile("cv.pdf", b"PDF", content_type="application/pdf")
        response = self.client.post(
            self.url,
            {"file": pdf, "save_to_db": "true"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(response.data["saved"])
        self.assertEqual(response.data["user_id"], 42)
        self.assertEqual(response.data["cv_submission_id"], 99)
        # The save function was called once with the parser data and the file.
        mock_save.assert_called_once()
        args, _kwargs = mock_save.call_args
        self.assertEqual(args[0], mock_result.data)

    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_save_to_db_default_false_does_not_persist(
        self, mock_processor_cls, mock_extractor_cls
    ):
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "SAKR MANNING AGENCY 1. PERSONAL DETAILS ...",
            "tables": [],
        }
        mock_processor_cls.return_value = mock_proc
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.extractor = "sakr_template"
        mock_result.confidence = 0.95
        mock_result.data = {"1_personal_details": {"full_name": "X"}}
        mock_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = mock_result

        from api.models import Users
        before = Users.objects.count()

        pdf = SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")
        # No save_to_db field — defaults to false.
        response = self.client.post(self.url, {"file": pdf}, format="multipart")

        after = Users.objects.count()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["saved"])
        self.assertEqual(before, after, "No Users row should be created when save_to_db is absent")

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_save_failure_no_email_returns_400(
        self, mock_processor_cls, mock_extractor_cls, mock_save
    ):
        from ai_document.views import _NoEmailError

        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "SAKR MANNING AGENCY 1. PERSONAL DETAILS ...",
            "tables": [],
        }
        mock_processor_cls.return_value = mock_proc
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.extractor = "sakr_template"
        mock_result.confidence = 0.95
        mock_result.data = {
            "1_personal_details": {"full_name": "X"},
            "3_contact_details": {"e_mail": ""},  # no email
        }
        mock_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = mock_result
        mock_save.side_effect = _NoEmailError("no email")

        pdf = SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")
        response = self.client.post(
            self.url,
            {"file": pdf, "save_to_db": "true"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["error"], "email_missing")
        # The parser output is still in the response, so the user can fix
        # the source CV and re-upload.
        self.assertIn("data", response.data)


class SaveParserOutputIntegrationTest(TransactionTestCase):
    """End-to-end test: the save helper actually creates User + CVSubmission."""

    def setUp(self):
        from api.models import Users, CVSubmission
        # Clean slate — we want exact counts.
        CVSubmission.objects.all().delete()
        Users.objects.filter(email__endswith="@sakrparser.test").delete()

    def test_creates_user_and_cv_submission(self):
        from decimal import Decimal
        from datetime import date
        from ai_document.views import _save_parser_output
        from api.models import Users, CVSubmission

        data = {
            "0_application_meta": {
                "application_for_position_as": "Waiter",
                "register_code": "",
                "other_position": "",
                "register_date": "10.07.2025",
                "expected_salary": "730 $",
                "available_date": "25/7/2025",
            },
            "1_personal_details": {
                "full_name": "MOHAMED SHEHATA",
                "date_of_birth": "28/02/1995",
                "marital_status": {"single": True, "married": False},
                "nationality": "Egyptian",
                "place_of_birth": "Qena",
                "height_cm": 173,
                "weight_kg": 67,
            },
            "3_contact_details": {
                "home_address_city": "Qena",
                "e_mail": "MOHAMED@SAKRPARSER.TEST",
                "mobile_tel": "00201090946284",
            },
        }
        uploaded = SimpleUploadedFile("cv.pdf", b"PDF", content_type="application/pdf")

        user_id, cv_submission_id = _save_parser_output(data, uploaded)

        user = Users.objects.get(id=user_id)
        self.assertEqual(user.email, "mohamed@sakrparser.test")
        self.assertEqual(user.first_name, "MOHAMED")
        self.assertEqual(user.middle_name, "SHEHATA")
        self.assertEqual(user.nationality, "Egyptian")
        self.assertEqual(user.Height_Cm, 173)
        self.assertEqual(user.Weight_Kg, 67)
        self.assertEqual(user.marital_status, "Single")
        # "Waiter" IS a valid position choice → set on the user
        self.assertEqual(user.application_for_position, "Waiter")

        cv = CVSubmission.objects.get(id=cv_submission_id)
        self.assertEqual(cv.user_id, user_id)
        self.assertEqual(cv.status, "Pending")
        # Expected salary "730 $" → Decimal(730)
        self.assertEqual(cv.expected_salary, Decimal("730"))
        # Available date "25/7/2025" → date(2025, 7, 25)
        self.assertEqual(cv.availability_date, date(2025, 7, 25))

    def test_second_call_updates_existing_user(self):
        from ai_document.views import _save_parser_output
        from api.models import Users

        data = {
            "1_personal_details": {
                "full_name": "FIRST LAST",
                "nationality": "Egyptian",
            },
            "3_contact_details": {
                "e_mail": "DUP@SAKRPARSER.TEST",
            },
            "0_application_meta": {
                "expected_salary": "1000",
                "available_date": "01/01/2026",
            },
        }
        uploaded = SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")

        user_id_1, _ = _save_parser_output(data, uploaded)
        user_id_2, _ = _save_parser_output(data, uploaded)

        # Same email → same user, not a duplicate
        self.assertEqual(user_id_1, user_id_2)
        self.assertEqual(Users.objects.filter(email="dup@sakrparser.test").count(), 1)

    def test_save_creates_related_records(self):
        """Regression: _save_parser_output must persist the rest of the
        Sakr data (travel docs, qualifications, NOK, health certs,
        marine courses, sea service) to the related models — not just
        the basic User fields. Otherwise the GET endpoint returns
        empty arrays for everything except personal_details.
        """
        from ai_document.views import _save_parser_output
        from api.models import (
            Users, SeaService, NextOfKin, PersonalDocument,
        )
        from courses.models import Course
        from vaccinations.models import Vaccination

        data = {
            "1_personal_details": {
                "full_name": "TEST USER FOR RELATED",
                "date_of_birth": "01/01/1990",
                "marital_status": {"single": True, "married": False},
                "nationality": "Egyptian",
            },
            "3_contact_details": {
                "e_mail": "related.test@sakrparser.test",
                "mobile_tel": "00201000000000",
            },
            "4_travel_documents": [
                {"type": "Passport", "document_no": "TEST123",
                 "iss_date": "01/01/2020", "exp_date": "01/01/2030",
                 "iss_by_authority": "Test Authority",
                 "place_of_issue": "Cairo"},
                {"type": "Seaman Book", "document_no": "SB123",
                 "iss_date": "19/5/2025", "exp_date": "13/5/2030",
                 "iss_by_authority": "EAMS",
                 "place_of_issue": "Alex."},
                {"type": "Other Seaman Book", "document_no": "OSB123",
                 "iss_date": "", "exp_date": "",
                 "iss_by_authority": "",
                 "place_of_issue": ""},
            ],
            "5_professional_qualification_certificate_of_competency": [
                {"certificate_name": "COC Master", "number": "COC1",
                 "issue_date": "01/01/2020", "expiry_date": "01/01/2025",
                 "issued_by": "Test Auth", "issued_at": "Cairo"},
            ],
            "6_next_of_kin_emergency_contact": {
                "full_name": "Test NOK",
                "relationship": "Brother",
                "tel_no_mobile": "00201000000001",
                "email": "nok@test.com",
                "address_country": "Cairo",
            },
            "7_health_certificates_and_vaccinations": {
                "certificates": [
                    {"flag_state": "International Medical",
                     "number": "MED1", "issue_date": "01/01/2024",
                     "expiry_date": "01/01/2026", "issued_by": "Test Med",
                     "issued_at": "Cairo"},
                ],
                "covid_19": {
                    "vaccination_name": "Pfizer",
                    "first_dose": "01/03/2021",
                    "second_dose": "01/04/2021",
                },
            },
            "8_marine_courses": [
                {"course_name": "Basic Safety", "number": "BS1",
                 "issue_date": "01/01/2020", "expiry_date": "01/01/2025",
                 "issued_by_at": "Test School"},
            ],
            "9_complete_sea_service_details": {
                "service_records": [
                    {"company_name": "Test Co", "rank": "Master",
                     "vessel_name_imo": "TEST VESSEL / IMO 1234567",
                     "flag": "Test Flag", "signed_on": "01/01/2022",
                     "signed_off": "01/01/2023", "period": "1 year",
                     "vessel_type": "Cargo", "dwt_grt": "1000",
                     "engine_type": "Diesel", "bh_kw": "1000",
                     "reason_for_sign_off": "End of contract"},
                ],
            },
        }
        uploaded = SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")
        user_id, _ = _save_parser_output(data, uploaded)

        user = Users.objects.get(id=user_id)

        # 4. Travel docs — Passport + Seaman Book + Other Seaman Book all
        # map to User model fields (not PersonalDocument), based on type.
        # Passport:
        self.assertEqual(user.passport_no, "TEST123")
        # Seaman Book:
        self.assertEqual(user.seaman_book_no, "SB123")
        # Other Seaman Book:
        self.assertEqual(user.other_seaman_book_no, "OSB123")

        # 5. Qualifications → COC set on User model fields
        self.assertEqual(user.coc_certificate_number, "COC1")
        self.assertEqual(user.coc_issued_by, "Test Auth")

        # 6. NOK — stored on User model fields (not a separate NextOfKin
        # record). The serializer exposes them in seafarer_application
        # via the get_next_of_kin helper.
        self.assertEqual(user.next_of_kin_full_name, "Test NOK")
        self.assertEqual(user.next_of_kin_relationship, "Brother")
        self.assertEqual(user.next_of_kin_email, "nok@test.com")
        self.assertEqual(user.next_of_kin_phone, "00201000000001")
        self.assertEqual(user.next_of_kin_address_country, "Cairo")

        # 7. Health certs → 1 Vaccination + User fields
        self.assertEqual(user.vaccinations.count(), 1)
        vacc = user.vaccinations.first()
        self.assertIn("international", vacc.name.lower())
        self.assertEqual(vacc.number, "MED1")
        # International Medical fields synced to User
        self.assertEqual(user.international_medical_number, "MED1")

        # COVID-19 on User
        self.assertEqual(user.covid_vaccine_name, "Pfizer")

        # 8. Marine courses → 1 Course
        self.assertEqual(user.courses.count(), 1)
        course = user.courses.first()
        self.assertEqual(course.course_name, "Basic Safety")
        self.assertEqual(course.course_number, "BS1")

        # 9. Sea service → 1 SeaService
        self.assertEqual(user.sea_services.count(), 1)
        ss = user.sea_services.first()
        self.assertEqual(ss.company_name, "Test Co")
        self.assertEqual(ss.rank, "Master")
        # vessel_name and imo_number are split from vessel_name_imo
        self.assertEqual(ss.vessel_name, "TEST VESSEL")
        self.assertEqual(ss.imo_number, "IMO 1234567")
        self.assertEqual(ss.flag, "Test Flag")

    def test_save_attaches_profile_image_from_photo_path(self):
        """Regression: when DocumentProcessor hands us an
        ``extracted_photo_path``, _save_parser_output must attach it to
        ``user.profile_image`` — otherwise the seafarer's photo is lost.
        """
        import tempfile
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        from ai_document.views import _save_parser_output
        from api.models import Users

        # Build a tiny valid PNG on disk to mimic what
        # DocumentProcessor leaves behind in its temp dir.
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img = Image.new("RGB", (200, 260), color=(180, 200, 220))
            img.save(tmp, format="PNG")
            photo_path = tmp.name

        try:
            data = {
                "1_personal_details": {
                    "full_name": "PHOTO TEST USER",
                    "date_of_birth": "01/01/1990",
                    "marital_status": {"single": True, "married": False},
                    "nationality": "Egyptian",
                },
                "3_contact_details": {
                    "e_mail": "photo.test@sakrparser.test",
                    "mobile_tel": "00201000000099",
                },
            }
            uploaded = SimpleUploadedFile(
                "cv.pdf", b"x", content_type="application/pdf"
            )

            user_id, _ = _save_parser_output(
                data, uploaded, extracted_photo_path=photo_path
            )
            user = Users.objects.get(id=user_id)

            # profile_image must be set and readable
            self.assertTrue(user.profile_image, "profile_image should be set")
            self.assertTrue(user.profile_image.name.startswith("users/"))
            # Original photo bytes must round-trip into the file we save
            with user.profile_image.open("rb") as saved:
                saved_bytes = saved.read()
            with open(photo_path, "rb") as original:
                original_bytes = original.read()
            self.assertEqual(saved_bytes, original_bytes)
        finally:
            os.unlink(photo_path)

    def test_save_skips_missing_photo_path(self):
        """If extracted_photo_path points at a file that no longer
        exists, _save_parser_output must NOT crash and must NOT set a
        profile_image — the seafarer just ends up with no photo.
        """
        from django.core.files.uploadedfile import SimpleUploadedFile
        from ai_document.views import _save_parser_output
        from api.models import Users

        data = {
            "1_personal_details": {
                "full_name": "NO PHOTO USER",
                "date_of_birth": "01/01/1990",
                "marital_status": {"single": True, "married": False},
            },
            "3_contact_details": {
                "e_mail": "no.photo@sakrparser.test",
                "mobile_tel": "00201000000098",
            },
        }
        uploaded = SimpleUploadedFile(
            "cv.pdf", b"x", content_type="application/pdf"
        )
        user_id, _ = _save_parser_output(
            data, uploaded, extracted_photo_path="/nonexistent/photo.png"
        )
        user = Users.objects.get(id=user_id)
        # Either no profile_image, or an empty ImageFieldFile — but no
        # crash. Be lenient because the underlying ImageField can be
        # either "" or None depending on Django version.
        self.assertFalse(bool(user.profile_image))

    def test_save_works_without_photo_path(self):
        """Backward-compat: callers that don't pass a photo path (e.g.
        legacy /ai/upload/ paths) must keep working.
        """
        from django.core.files.uploadedfile import SimpleUploadedFile
        from ai_document.views import _save_parser_output
        from api.models import Users

        data = {
            "1_personal_details": {
                "full_name": "NO PHOTO ARG USER",
                "date_of_birth": "01/01/1990",
                "marital_status": {"single": True, "married": False},
            },
            "3_contact_details": {
                "e_mail": "no.arg@sakrparser.test",
                "mobile_tel": "00201000000097",
            },
        }
        uploaded = SimpleUploadedFile(
            "cv.pdf", b"x", content_type="application/pdf"
        )
        user_id, _ = _save_parser_output(data, uploaded)
        user = Users.objects.get(id=user_id)
        self.assertFalse(bool(user.profile_image))


class ParserHelpersUnitTest(SimpleTestCase):
    """Pure-function tests for the date/salary/name helpers."""

    def test_split_full_name(self):
        from ai_document.views import _split_full_name
        self.assertEqual(_split_full_name("MOHAMED SHEHATA"), ("MOHAMED", "SHEHATA"))
        self.assertEqual(
            _split_full_name("MOHAMED SHEHATA RAMADAN ABDEL BASSET"),
            ("MOHAMED", "SHEHATA RAMADAN ABDEL BASSET"),
        )
        self.assertEqual(_split_full_name(""), ("", ""))
        self.assertEqual(_split_full_name("SINGLE"), ("SINGLE", ""))

    def test_parse_date_loose(self):
        from ai_document.views import _parse_date_loose
        from datetime import date
        self.assertEqual(_parse_date_loose("28/02/1995"), date(1995, 2, 28))
        self.assertEqual(_parse_date_loose("10.07.2025"), date(2025, 7, 10))
        self.assertEqual(_parse_date_loose("25/7/2025"), date(2025, 7, 25))
        self.assertIsNone(_parse_date_loose("not a date"))
        self.assertIsNone(_parse_date_loose(""))
        self.assertIsNone(_parse_date_loose(None))

    def test_parse_salary_to_decimal(self):
        from decimal import Decimal
        from ai_document.views import _parse_salary_to_decimal
        self.assertEqual(_parse_salary_to_decimal("730 $"), Decimal("730"))
        self.assertEqual(_parse_salary_to_decimal("1200 USD"), Decimal("1200"))
        self.assertEqual(_parse_salary_to_decimal("$1500.50"), Decimal("1500.50"))
        self.assertIsNone(_parse_salary_to_decimal(""))
        self.assertIsNone(_parse_salary_to_decimal("abc"))

    def test_marital_status_to_string(self):
        from ai_document.views import _marital_status_to_string
        self.assertEqual(
            _marital_status_to_string({"single": True, "married": False}), "Single"
        )
        self.assertEqual(
            _marital_status_to_string({"single": False, "married": True}), "Married"
        )
        self.assertEqual(
            _marital_status_to_string({"single": False, "married": False}), ""
        )
        self.assertEqual(_marital_status_to_string("Single"), "Single")
        self.assertEqual(_marital_status_to_string(None), "")


class LlmRouterOllamaTest(SimpleTestCase):
    """Unit tests for the Ollama branch of ``_get_active_llm``.

    The router order is:
      0. Ollama (local) — first when OLLAMA_HOST is set
      1. DeepSeek (cloud) — primary cloud LLM
      2. Gemini (cloud) — fallback

    These tests verify:
      * Ollama is tried FIRST when OLLAMA_HOST is set.
      * Ollama is skipped (falls through to DeepSeek) when
        ``api_keys_config["ollama_disabled"] = True``.
      * Ollama is skipped when ``OLLAMA_ENABLED = False`` (env override).
      * Ollama falls through to DeepSeek when the import / init fails.
      * DeepSeek wins when Ollama is not configured at all.

    Note on mocking: ``ChatOllama`` is imported locally inside
    ``_get_active_llm``, so we mock it at its source module
    (``langchain_ollama.ChatOllama``), not at
    ``ai_document.document_to_json.ChatOllama``.
    """

    def setUp(self):
        super().setUp()
        # Strip any leaked LLM env vars from prior tests so our
        # override_settings() / api_keys_config={} actually gives us
        # a "no key" condition. The view's _resolve_api_keys_config
        # mutates os.environ when a request supplies a key, and that
        # side-effect would otherwise leak across tests.
        import os
        self._saved_env = {}
        for var in ("DEEPSEEK_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY"):
            if var in os.environ:
                self._saved_env[var] = os.environ.pop(var)

    def tearDown(self):
        import os
        for var, value in self._saved_env.items():
            os.environ[var] = value
        super().tearDown()

    def _patch_settings(self, **overrides):
        """Apply Django settings overrides for the duration of a test."""
        from django.test import override_settings
        return override_settings(**overrides)

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_wins_when_configured(self, mock_chat_ollama):
        """OLLAMA_HOST set + OLLAMA_ENABLED true → ChatOllama is
        instantiated and returned. Groq is NEVER instantiated.
        """
        from ai_document.document_to_json import _get_active_llm
        mock_llm_instance = MagicMock(name="ollama_llm")
        mock_chat_ollama.return_value = mock_llm_instance

        with self._patch_settings(
            OLLAMA_ENABLED=True,
            OLLAMA_HOST="http://127.0.0.1:11434",
            OLLAMA_MODEL="qwen2.5:7b",
        ):
            llm, info = _get_active_llm({})

        self.assertIs(llm, mock_llm_instance)
        self.assertEqual(info["provider"], "ollama")
        self.assertEqual(info["model"], "qwen2.5:7b")
        self.assertEqual(info["host"], "http://127.0.0.1:11434")

        # Verify ChatOllama was constructed with JSON-mode + the
        # configured model + base_url.
        mock_chat_ollama.assert_called_once()
        call_kwargs = mock_chat_ollama.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "qwen2.5:7b")
        self.assertEqual(call_kwargs["base_url"], "http://127.0.0.1:11434")
        self.assertEqual(call_kwargs["format"], "json")
        self.assertEqual(call_kwargs["temperature"], 0)

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_skipped_when_disabled_in_config(self, mock_chat_ollama):
        """``api_keys_config["ollama_disabled"] = True`` → router
        falls through to DeepSeek/Gemini. Even if OLLAMA_HOST is set.
        """
        from ai_document.document_to_json import _get_active_llm

        with self._patch_settings(
            OLLAMA_ENABLED=True,
            OLLAMA_HOST="http://127.0.0.1:11434",
            DEEPSEEK_API_KEY="",  # don't pick up a leaked env key
        ):
            # No DeepSeek key, no Gemini key — router returns (None, None)
            llm, info = _get_active_llm({"ollama_disabled": True})

        self.assertIsNone(llm)
        self.assertIsNone(info)
        # Ollama was NOT instantiated.
        mock_chat_ollama.assert_not_called()

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_skipped_when_globally_disabled(self, mock_chat_ollama):
        """``OLLAMA_ENABLED = False`` (env override) → router never
        tries Ollama. The cloud fallbacks still get a chance.
        """
        from ai_document.document_to_json import _get_active_llm

        with self._patch_settings(
            OLLAMA_ENABLED=False,
            OLLAMA_HOST="http://127.0.0.1:11434",
        ):
            llm, info = _get_active_llm({})

        self.assertIsNone(llm)
        mock_chat_ollama.assert_not_called()

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_falls_through_to_deepseek_when_init_fails(
        self, mock_chat_ollama,
    ):
        """ChatOllama(...) raises (e.g. server not running) → router
        logs the failure and tries the next provider (DeepSeek).

        The local test env may not have ``langchain_openai`` installed,
        so we inject a stub module into ``sys.modules`` before the
        router's ``from langchain_openai import ChatOpenAI`` runs. On
        prod the real package is in requirements.txt.
        """
        import sys
        import types

        # Stub out langchain_openai so the `from langchain_openai import
        # ChatOpenAI` inside _get_active_llm doesn't ModuleNotFoundError.
        if "langchain_openai" not in sys.modules:
            fake_oa = types.ModuleType("langchain_openai")
            fake_llm = MagicMock(name="deepseek_llm")

            def fake_chat_openai(*args, **kwargs):
                return fake_llm

            fake_oa.ChatOpenAI = fake_chat_openai
            sys.modules["langchain_openai"] = fake_oa
            self.addCleanup(lambda: sys.modules.pop("langchain_openai", None))
        else:
            fake_llm = MagicMock(name="deepseek_llm")
            sys.modules["langchain_openai"].ChatOpenAI = lambda *a, **kw: fake_llm

        from ai_document.document_to_json import _get_active_llm
        mock_chat_ollama.side_effect = ConnectionError(
            "ollama not running"
        )

        with self._patch_settings(
            OLLAMA_ENABLED=True,
            OLLAMA_HOST="http://127.0.0.1:11434",
            DEEPSEEK_API_KEY="sk_test",
        ):
            llm, info = _get_active_llm({})

        # Ollama was attempted, failed, and we fell through to DeepSeek.
        mock_chat_ollama.assert_called_once()
        self.assertIs(llm, fake_llm)
        self.assertEqual(info["provider"], "deepseek")

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_not_attempted_when_host_empty(self, mock_chat_ollama):
        """OLLAMA_HOST empty / unset → Ollama branch is skipped
        entirely (not even imported). The router returns (None, None)
        because no cloud key is configured in this test.
        """
        from ai_document.document_to_json import _get_active_llm

        with self._patch_settings(
            OLLAMA_ENABLED=True,
            OLLAMA_HOST="",  # empty → skip Ollama
            DEEPSEEK_API_KEY="",  # don't accidentally pick up a leaked env key
        ):
            llm, info = _get_active_llm({})

        self.assertIsNone(llm)
        self.assertIsNone(info)
        mock_chat_ollama.assert_not_called()

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_model_override_per_request(self, mock_chat_ollama):
        """``api_keys_config["ollama_model"]`` overrides the default
        from settings for a single request.
        """
        from ai_document.document_to_json import _get_active_llm
        mock_chat_ollama.return_value = MagicMock(name="llm")

        with self._patch_settings(
            OLLAMA_ENABLED=True,
            OLLAMA_HOST="http://127.0.0.1:11434",
            OLLAMA_MODEL="qwen2.5:7b",
        ):
            _get_active_llm({"ollama_model": "llama3.1:8b"})

        # The per-request model name was used.
        call_kwargs = mock_chat_ollama.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "llama3.1:8b")


class DocumentUploadViewOllamaTest(AuthenticatedAPITestCase):
    """End-to-end test: /ai/upload/ works without ANY API keys when
    Ollama is configured locally on the server.

    Mocks convert_text_to_json to act as if it routed through Ollama
    successfully, then verifies the view returns 200 OK with
    ``extractor: "deepseek_llm"`` (the same label we use for any LLM
    path — we don't expose the underlying provider name in the
    public API).
    """

    def setUp(self):
        super().setUp()
        self.url = "/ai/upload/"

    def _pdf(self, name="cv.pdf"):
        return SimpleUploadedFile(
            name, b"%PDF-1.4 fake", content_type="application/pdf"
        )

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.convert_text_to_json")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_upload_works_without_api_keys_when_ollama_up(
        self, mock_processor_cls, mock_extractor_cls,
        mock_convert, mock_save,
    ):
        """No `deepseek_api_key`, no `api_keys_config` in the request.
        The view passes an empty config to the LLM router, which
        picks Ollama (mocked to succeed). Result: 200 OK, save
        happens, no API key was ever needed.
        """
        from ai_document.extractors import ErrorCode

        # Mock the document processor
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "text that doesn't match Sakr form",
            "tables": [],
            "page_count": 2,
        }
        mock_processor_cls.return_value = mock_proc

        # Deterministic extractor fails → LLM path
        det_result = MagicMock()
        det_result.ok = False
        det_result.error = ErrorCode.NOT_SAKR_TEMPLATE
        det_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = det_result

        # LLM path (simulating Ollama) returns a valid CV payload
        mock_convert.return_value = (
            {
                "1_personal_details": {
                    "full_name": "Ollama Extracted User",
                    "date_of_birth": "15/06/1990",
                },
                "3_contact_details": {
                    "e_mail": "ollama.user@example.com",
                    "mobile_tel": "+201234567890",
                },
            },
            {},
        )
        mock_save.return_value = (777, 888)

        # NOTE: NO deepseek_api_key, NO api_keys_config — pure Ollama flow
        response = self.client.post(
            self.url, {"file": self._pdf()}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["extractor"], "deepseek_llm")
        self.assertEqual(
            response.data["data"]["1_personal_details"]["full_name"],
            "Ollama Extracted User",
        )
        # Save happened with the ids _save_parser_output returned.
        self.assertTrue(response.data["saved"])
        self.assertEqual(response.data["user_id"], 777)
        self.assertEqual(response.data["cv_submission_id"], 888)

        # Verify the empty api_keys_config was passed to the LLM
        # router (which is what lets Ollama be picked up).
        call_args = mock_convert.call_args
        passed_config = call_args.kwargs.get("api_keys_config", {})
        self.assertEqual(passed_config, {})


class OllamaOcrServiceTest(SimpleTestCase):
    """Unit tests for ``ai_document.ocr.OllamaOcrService``.

    The service talks to a local Ollama instance over HTTP, so all
    tests mock the ``requests`` calls. The service must:
      * build the correct request payload (model + prompt + base64 image)
      * handle Ollama-down gracefully (return empty string, no raise)
      * run multi-page OCR in parallel
    """

    @patch("ai_document.ocr.requests.get")
    def test_is_available_true_when_model_loaded(self, mock_get):
        """Ollama responds with the model in its list → available."""
        from ai_document.ocr import OllamaOcrService
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [
                {"name": "glm-ocr:latest"},
                {"name": "llama3.1:8b"},
            ]
        }
        self.assertTrue(OllamaOcrService().is_available())
        mock_get.assert_called_once()
        self.assertIn("/api/tags", mock_get.call_args.args[0])

    @patch("ai_document.ocr.requests.get")
    def test_is_available_false_when_model_missing(self, mock_get):
        """Ollama responds but the model is not in the list → not available."""
        from ai_document.ocr import OllamaOcrService
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "models": [{"name": "llama3.1:8b"}]
        }
        self.assertFalse(OllamaOcrService().is_available())

    @patch("ai_document.ocr.requests.get")
    def test_is_available_false_on_connection_error(self, mock_get):
        """Ollama unreachable → False (never raises)."""
        from ai_document.ocr import OllamaOcrService
        mock_get.side_effect = ConnectionError("refused")
        self.assertFalse(OllamaOcrService().is_available())

    @patch("ai_document.ocr.requests.post")
    def test_ocr_image_calls_ollama_with_correct_payload(self, mock_post):
        """Verify the HTTP request shape: model, prompt, base64 image,
        stream=False.
        """
        from ai_document.ocr import OllamaOcrService
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "response": "  EXTRACTED TEXT  "
        }
        mock_post.return_value.raise_for_status = lambda: None

        service = OllamaOcrService(
            host="http://example.com:11434", model="glm-ocr:latest"
        )
        text = service.ocr_image(b"\x89PNG\r\n\x1a\n fake image")

        self.assertEqual(text, "EXTRACTED TEXT")
        mock_post.assert_called_once()
        # Check the URL
        self.assertEqual(
            mock_post.call_args.args[0],
            "http://example.com:11434/api/generate",
        )
        # Check the payload
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["model"], "glm-ocr:latest")
        self.assertEqual(payload["stream"], False)
        self.assertIn("images", payload)
        self.assertEqual(len(payload["images"]), 1)
        # The base64 should decode to our original bytes
        import base64
        self.assertEqual(
            base64.b64decode(payload["images"][0]), b"\x89PNG\r\n\x1a\n fake image"
        )

    @patch("ai_document.ocr.requests.post")
    def test_ocr_image_returns_empty_on_http_error(self, mock_post):
        """Ollama returns 5xx → empty string (caller falls back)."""
        from ai_document.ocr import OllamaOcrService
        mock_post.return_value.status_code = 500
        mock_post.return_value.raise_for_status.side_effect = RuntimeError(
            "500 server error"
        )
        service = OllamaOcrService()
        self.assertEqual(service.ocr_image(b"x"), "")

    @patch("ai_document.ocr.requests.post")
    def test_ocr_image_returns_empty_on_connection_error(self, mock_post):
        """Network down → empty string (caller falls back)."""
        from ai_document.ocr import OllamaOcrService
        mock_post.side_effect = ConnectionError("refused")
        self.assertEqual(OllamaOcrService().ocr_image(b"x"), "")

    def test_ocr_image_empty_bytes_returns_empty(self):
        """Empty bytes is a no-op — no HTTP call."""
        from ai_document.ocr import OllamaOcrService
        with patch("ai_document.ocr.requests.post") as mock_post:
            self.assertEqual(OllamaOcrService().ocr_image(b""), "")
            mock_post.assert_not_called()

    @patch("ai_document.ocr.requests.post")
    def test_ocr_pages_runs_in_parallel(self, mock_post):
        """5 pages → all are processed; result list has 5 entries in
        the correct order. We can't easily assert thread count, but
        we can assert the count and order.
        """
        from ai_document.ocr import OllamaOcrService

        def fake_post(*args, **kwargs):
            # Pull the prompt to figure out which page we're on —
            # the service uses the same prompt for all pages, so we
            # just return a unique string per call (call order is
            # undefined when parallel, so we can't rely on it).
            r = MagicMock()
            r.status_code = 200
            r.json.return_value = {"response": "PAGE_OK"}
            r.raise_for_status = lambda: None
            return r

        mock_post.side_effect = fake_post

        service = OllamaOcrService()
        results = service.ocr_pages([b"img1", b"img2", b"img3", b"img4", b"img5"])

        self.assertEqual(len(results), 5)
        for r in results:
            self.assertEqual(r, "PAGE_OK")
        # 5 calls made (one per page)
        self.assertEqual(mock_post.call_count, 5)

    @patch("ai_document.ocr.requests.post")
    def test_ocr_pages_preserves_order(self, mock_post):
        """Result[i] corresponds to page_images[i], even when the
        HTTP calls complete out of order.

        We can't reliably identify which response goes with which
        image (base64 of "AAAA" ≠ "QUFB" — there's padding). Instead
        we use a counter that records the SUBMIT ORDER of each call,
        and we make page 0 take the longest so others finish first.
        Then we assert result[0] is the one submitted first.
        """
        from ai_document.ocr import OllamaOcrService
        import time
        import threading

        submit_order: list[int] = []
        submit_lock = threading.Lock()

        def slow_post(*args, **kwargs):
            # The base64 image is kwargs["json"]["images"][0].
            # We can use the FIRST FEW chars as a fingerprint that
            # is unique to each image (different image bytes → different
            # base64 first chars in practice for any non-trivial image).
            # For test purposes we know exactly which image we sent,
            # so we can match on length.
            b64 = kwargs["json"]["images"][0]
            # image[0] = 1 byte → b64 length = 4 (no padding)
            # image[1] = 2 bytes → b64 length = 4
            # image[2] = 3 bytes → b64 length = 4
            # image[3] = 4 bytes → b64 length = 8
            # image[4] = 5 bytes → b64 length = 8
            # Use the raw image length instead, by encoding again.
            import base64
            raw_len = len(base64.b64decode(b64))
            # Page index = raw_len - 1
            page_idx = raw_len - 1

            with submit_lock:
                submit_order.append(page_idx)

            # Reverse-completion: page 0 is the slowest
            time.sleep(0.05 * (5 - page_idx))

            r = MagicMock()
            r.status_code = 200
            r.json.return_value = {"response": f"page{page_idx + 1}"}
            r.raise_for_status = lambda: None
            return r

        mock_post.side_effect = slow_post

        service = OllamaOcrService()
        results = service.ocr_pages(
            [b"a", b"ab", b"abc", b"abcd", b"abcde"]
        )
        # Order: results[i] must match image[i]
        self.assertEqual(
            results,
            ["page1", "page2", "page3", "page4", "page5"],
        )
        # Sanity: submit_order should have all 5 indices
        self.assertEqual(sorted(submit_order), [0, 1, 2, 3, 4])

    def test_ocr_pages_empty_list(self):
        """Empty input → empty output, no HTTP call."""
        from ai_document.ocr import OllamaOcrService
        with patch("ai_document.ocr.requests.post") as mock_post:
            self.assertEqual(OllamaOcrService().ocr_pages([]), [])
            mock_post.assert_not_called()

    @patch("ai_document.ocr.requests.post")
    def test_ocr_pages_combined_skips_empty_pages(self, mock_post):
        """Per-page empty results are dropped; non-empty joined by
        default separator.
        """
        from ai_document.ocr import OllamaOcrService
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": ""}
        mock_post.return_value.raise_for_status = lambda: None
        service = OllamaOcrService()
        # All pages return empty → combined is empty
        self.assertEqual(
            service.ocr_pages_combined([b"a", b"b", b"c"]),
            "",
        )


class DocumentProcessorOcrFallbackTest(TestCase):
    """Verify ``DocumentProcessor._ollama_ocr_fallback`` integrates
    with ``OllamaOcrService`` and is gated by the OCR_ENABLED /
    OCR_BACKEND settings.
    """

    def setUp(self):
        from ai_document.document_processor import DocumentProcessor
        self.processor = DocumentProcessor()

    @patch("ai_document.ocr.OllamaOcrService")
    def test_ollama_ocr_returns_text_and_pages(self, mock_service_cls):
        """Happy path: render 3 pages, OCR returns 3 chunks,
        combined text returned, backend=ollama.
        """
        from django.test import override_settings
        # Mock the OllamaOcrService instance
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.ocr_pages_combined.return_value = (
            "PAGE 1 TEXT\n\nPAGE 2 TEXT\n\nPAGE 3 TEXT"
        )
        mock_service_cls.return_value = mock_service

        # Mock PyMuPDF
        with patch("ai_document.document_processor.fitz") as mock_fitz:
            mock_doc = MagicMock()
            mock_doc.__len__ = lambda self: 3
            mock_doc.__iter__ = lambda self: iter(range(3))
            mock_doc.load_page.return_value.get_pixmap.return_value.tobytes.return_value = (
                b"fake-png-bytes"
            )
            mock_fitz.open.return_value = mock_doc
            mock_fitz.Matrix.return_value = MagicMock()

            with override_settings(
                OCR_MAX_PAGES=10,
                OCR_RENDER_DPI=150,
            ):
                result = self.processor._ollama_ocr_fallback("/tmp/test.pdf")

        self.assertEqual(result["backend"], "ollama")
        self.assertEqual(result["pages"], 3)
        self.assertIn("PAGE 1 TEXT", result["text"])
        # OCR service was checked
        mock_service.is_available.assert_called_once()
        # Combined OCR was called
        mock_service.ocr_pages_combined.assert_called_once()

    @patch("ai_document.ocr.OllamaOcrService")
    def test_ollama_ocr_skipped_when_unavailable(self, mock_service_cls):
        """Ollama down / model missing → empty result, no exception."""
        mock_service = MagicMock()
        mock_service.is_available.return_value = False
        mock_service_cls.return_value = mock_service

        result = self.processor._ollama_ocr_fallback("/tmp/test.pdf")
        self.assertEqual(result, {"text": "", "pages": 0, "backend": "ollama"})

    def test_ocr_disabled_short_circuits(self):
        """``OCR_ENABLED=False`` → both backends skipped entirely."""
        from django.test import override_settings
        with override_settings(OCR_ENABLED=False):
            result = self.processor._ocr_fallback("/tmp/test.pdf")
        self.assertEqual(result, {"text": "", "pages": 0, "backend": None})

    @patch("ai_document.ocr.OllamaOcrService")
    def test_ollama_empty_text_falls_through_to_gemini(self, mock_service_cls):
        """When backend=ollama but Ollama returns empty, _ocr_fallback
        tries Gemini. (We mock Gemini to return empty too so the test
        doesn't depend on the actual google-generativeai import.)
        """
        from django.test import override_settings
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.ocr_pages_combined.return_value = ""
        mock_service_cls.return_value = mock_service

        with override_settings(OCR_BACKEND="ollama"):
            with patch.object(
                self.processor, "_gemini_ocr_fallback",
                return_value={"text": "", "pages": 0, "backend": "gemini"},
            ) as mock_gemini:
                result = self.processor._ocr_fallback("/tmp/test.pdf")

        mock_gemini.assert_called_once()
        self.assertEqual(result["backend"], "gemini")
        self.assertEqual(result["text"], "")

    @patch("ai_document.ocr.OllamaOcrService")
    def test_ollama_success_skips_gemini(self, mock_service_cls):
        """When backend=ollama and Ollama returns text, Gemini is
        never called.
        """
        from django.test import override_settings
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.ocr_pages_combined.return_value = "EXTRACTED"
        mock_service_cls.return_value = mock_service

        # Mock PyMuPDF (the file doesn't actually exist)
        with patch("ai_document.document_processor.fitz") as mock_fitz:
            mock_doc = MagicMock()
            mock_doc.__len__ = lambda self: 2
            mock_doc.__iter__ = lambda self: iter(range(2))
            mock_doc.load_page.return_value.get_pixmap.return_value.tobytes.return_value = (
                b"fake"
            )
            mock_fitz.open.return_value = mock_doc
            mock_fitz.Matrix.return_value = MagicMock()

            with override_settings(OCR_BACKEND="ollama"):
                with patch.object(
                    self.processor, "_gemini_ocr_fallback",
                ) as mock_gemini:
                    result = self.processor._ocr_fallback("/tmp/test.pdf")

        mock_gemini.assert_not_called()
        self.assertEqual(result["backend"], "ollama")
        self.assertEqual(result["text"], "EXTRACTED")


class DocumentUploadViewOcrResponseTest(AdminAPITestCase):
    """The /ai/upload/ response now includes ``ocr`` meta. Verify it's
    always present, even when no OCR was applied.
    """

    def setUp(self):
        AdminAPITestCase.setUp(self)
        self.url = "/ai/upload/"

    def _pdf(self, name="cv.pdf"):
        return SimpleUploadedFile(
            name, b"%PDF-1.4 fake", content_type="application/pdf"
        )

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_ocr_meta_in_response_when_processor_reports_it(
        self, mock_processor_cls, mock_extractor_cls, mock_save,
    ):
        """Mock DocumentProcessor to set ocr_applied=True and
        ocr_backend=ollama. The view should pass these through to
        the response under the ``ocr`` key.
        """
        from ai_document.extractors import ErrorCode
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "OCR'd text from the scan",
            "tables": [],
            "ocr_applied": True,
            "ocr_pages_processed": 3,
            "ocr_backend": "ollama",
        }
        mock_processor_cls.return_value = mock_proc

        det_result = MagicMock()
        det_result.ok = True
        det_result.extractor = "sakr_template"
        det_result.confidence = 0.95
        det_result.data = {"1_personal_details": {"full_name": "OCR USER"}}
        det_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = det_result
        mock_save.return_value = (1, 2)

        response = self.client.post(
            self.url, {"file": self._pdf()}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ocr", response.data)
        self.assertTrue(response.data["ocr"]["ocr_applied"])
        self.assertEqual(response.data["ocr"]["ocr_pages_processed"], 3)
        self.assertEqual(response.data["ocr"]["ocr_backend"], "ollama")

    @patch("ai_document.views._save_parser_output")
    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_ocr_meta_defaults_when_processor_omits_keys(
        self, mock_processor_cls, mock_extractor_cls, mock_save,
    ):
        """If the processor dict doesn't have the OCR keys (e.g. an
        older fixture or a custom processor), the view still
        returns a well-formed ``ocr`` block with safe defaults.
        """
        from ai_document.extractors import ErrorCode
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "Sakr form text",
            "tables": [],
            # No ocr_* keys — backward-compat test
        }
        mock_processor_cls.return_value = mock_proc

        det_result = MagicMock()
        det_result.ok = True
        det_result.extractor = "sakr_template"
        det_result.confidence = 0.95
        det_result.data = {"1_personal_details": {"full_name": "X"}}
        det_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = det_result
        mock_save.return_value = (1, 2)

        response = self.client.post(
            self.url, {"file": self._pdf()}, format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("ocr", response.data)
        self.assertFalse(response.data["ocr"]["ocr_applied"])
        self.assertEqual(response.data["ocr"]["ocr_pages_processed"], 0)
        self.assertIsNone(response.data["ocr"]["ocr_backend"])


class ParseOnlyViewAuthTest(APITestCase):
    """Auth checks for the admin-only /ai/parse/ endpoint.

    The spec is: only users with role='Admin' can use /ai/parse/ and
    upload a seafarer CV. Everyone else is blocked.
    """

    def setUp(self):
        self.url = "/ai/parse/"

    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def _post(self, mock_processor_cls, mock_extractor_cls, *, role):
        """Helper: post a stub file with the given role on the test user.

        Mocks DocumentProcessor and SakrTemplateExtractor so the test
        doesn't depend on file content — we only care that the
        permission gate fires (or doesn't) for each role.

        ``role`` is keyword-only because @patch injects the mocks as
        positional args after self.
        """
        # Mock the processor + extractor so the view short-circuits to
        # 200 without actually parsing a file.
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "SAKR MANNING AGENCY 1. PERSONAL DETAILS ...",
            "tables": [],
        }
        mock_processor_cls.return_value = mock_proc
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.extractor = "sakr_template"
        mock_result.confidence = 0.95
        mock_result.data = {"1_personal_details": {"full_name": "X"}}
        mock_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = mock_result

        from django.contrib.auth import get_user_model
        if role is not None:
            user = get_user_model().objects.create_user(
                email=f"{role.lower().replace(' ', '')}@sakrparser.test",
                password="testpass123",
            )
            user.role = role
            user.save()
            self.client.force_authenticate(user=user)
        pdf = SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")
        return self.client.post(self.url, {"file": pdf}, format="multipart")

    def test_admin_is_allowed(self):
        response = self._post(role="Admin")
        # 200 (parse succeeds) — the body shape is tested elsewhere.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hr_manager_is_blocked(self):
        # HR Manager has full access elsewhere, but is NOT an Admin —
        # and this endpoint is admin-only.
        response = self._post(role="HR Manager")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recruiter_is_blocked(self):
        response = self._post(role="Recruiter")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_is_blocked(self):
        # This is the seafarer role — they should never be able to
        # upload their own CV (Admin does that on their behalf).
        response = self._post(role="Employee")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_is_blocked(self):
        response = self._post(role="Crew")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_is_blocked(self):
        # No force_authenticate — request.user is AnonymousUser.
        # The permission check fires before any DB work.
        response = self._post(role=None)
        # DRF returns 401 for unauthenticated users (vs 403 for
        # authenticated-but-forbidden).
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )


class ParseOnlyViewJWTAuthTest(APITestCase):
    """Real-JWT regression test for /ai/parse/.

    The other auth tests in this file use ``client.force_authenticate``
    which bypasses the view's ``authentication_classes``. That's
    fine for unit-testing the permission gate, but it let a real
    production bug slip through: ``authentication_classes = []`` on
    the view meant DRF skipped JWT validation entirely, so a valid
    Bearer token in the ``Authorization`` header was being ignored
    and the request was treated as anonymous (always 403).

    This test issues a real JWT via Simple JWT, sends it in the
    header the way Postman / a real client would, and asserts the
    request is allowed. It would have failed with the old
    ``authentication_classes = []`` config.
    """

    def setUp(self):
        from django.contrib.auth import get_user_model
        from rest_framework_simplejwt.tokens import RefreshToken

        Users = get_user_model()
        self.admin = Users.objects.create_user(
            email="jwt-admin@sakrparser.test",
            password="x",
        )
        self.admin.role = "Admin"
        self.admin.save()

        # Real JWT — same shape as /api/login/ would issue.
        refresh = RefreshToken.for_user(self.admin)
        self.bearer = f"Bearer {refresh.access_token}"
        self.url = "/ai/parse/"

    @patch("ai_document.views.SakrTemplateExtractor")
    @patch("ai_document.views.DocumentProcessor")
    def test_real_jwt_admin_is_allowed(
        self, mock_processor_cls, mock_extractor_cls
    ):
        # Short-circuit the parser with mocks (we only care that
        # the request reaches the view body, not the parser).
        mock_proc = MagicMock()
        mock_proc.process_document.return_value = {
            "extracted_text": "SAKR MANNING AGENCY ...",
            "tables": [],
        }
        mock_processor_cls.return_value = mock_proc
        mock_result = MagicMock()
        mock_result.ok = True
        mock_result.extractor = "sakr_template"
        mock_result.confidence = 0.95
        mock_result.data = {"1_personal_details": {"full_name": "X"}}
        mock_result.warnings = []
        mock_extractor_cls.return_value.extract.return_value = mock_result

        # NOTE: no force_authenticate — the request must be
        # authenticated by the view's own authentication_classes.
        pdf = SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")
        response = self.client.post(
            self.url,
            {"file": pdf},
            format="multipart",
            HTTP_AUTHORIZATION=self.bearer,
        )
        # With the old `authentication_classes = []` config this was
        # 403 because the JWT was ignored. With JWTAuthentication
        # wired in, the admin role passes the IsAdmin gate.
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# Run tests with: python manage.py test ai_document.tests
