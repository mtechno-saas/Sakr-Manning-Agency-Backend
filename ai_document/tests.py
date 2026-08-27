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
    """Test DocumentUploadView API endpoint"""
    
    def setUp(self):
        """Set up test client"""
        super().setUp()
        self.url = '/ai/upload/'
    
    @patch('ai_document.views.DocumentProcessor')
    @patch('ai_document.views.convert_text_to_json')
    def test_successful_upload(self, mock_convert, mock_processor):
        """Test successful document upload and processing"""
        # Mock document processor
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_document.return_value = {
            'extracted_text': 'Sample CV text with name John Doe',
            'page_count': 2
        }
        mock_processor.return_value = mock_processor_instance
        
        # Mock LLM conversion
        mock_convert.return_value = {
            'Personal_Details': {
                'Full_Name': 'John Doe',
                'Date_Of_Birth': '01/01/1990'
            },
            'Contact_Details': {
                'Email': 'john@example.com'
            },
            'Travel_Documents': [],
            'Professional_Qualifications': [],
            'Next_of_Kin_Emergency_Contact': {},
            'Health_Certificates_Vaccinations': [],
            'Covid_19_Vaccination': {},
            'Marine_Courses': [],
            'Sea_Service_Details': [],
            'Specialised_Experience': [],
            'References': [],
            'Declaration': {},
            'Office_Use_Only': {},
            'Physical_Measurements': {},
            'Language_Skills': {},
            'Medical_History': {},
            'Assessments': {},
            'Competency_Tests': {},
            'Applied_Position_Info': {},
            'Education': {},
        }
        
        # Create test file
        pdf_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        
        # Make request
        response = self.client.post(self.url, {'file': pdf_file}, format='multipart')
        
        # Assertions
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_206_PARTIAL_CONTENT])
        self.assertTrue(response.data['success'])
        self.assertIsNotNone(response.data['applicant_id'])
    
    def test_upload_without_file(self):
        """Test upload endpoint without file"""
        response = self.client.post(self.url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"Text content",
            content_type="text/plain"
        )
        
        response = self.client.post(self.url, {'file': txt_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
    
    @patch('ai_document.views.DocumentProcessor')
    @patch('ai_document.views.convert_text_to_json')
    def test_full_workflow(self, mock_convert, mock_processor):
        """Test complete workflow from upload to user creation"""
        # Mock document processor
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_document.return_value = {
            'extracted_text': 'Full CV text',
            'page_count': 5
        }
        mock_processor.return_value = mock_processor_instance
        
        # Mock LLM conversion with realistic data
        mock_convert.return_value = {
            'Personal_Details': {
                'Full_Name': 'Integration Test User',
                'Date_Of_Birth': '01/01/1990',
                'Nationality': 'Test Country'
            },
            'Contact_Details': {
                'Email': 'integration@test.com',
                'Mobile_Tel': '+1234567890'
            },
            'Travel_Documents': [
                {
                    'Type': 'Passport',
                    'Document_No': 'TEST123',
                    'ISS_Date': '01/01/2020',
                    'Exp_Date': '01/01/2030'
                }
            ],
            'Professional_Qualifications': [],
            'Next_of_Kin_Emergency_Contact': {},
            'Health_Certificates_Vaccinations': [],
            'Covid_19_Vaccination': {},
            'Marine_Courses': [],
            'Sea_Service_Details': [],
            'Specialised_Experience': [],
            'References': [],
            'Declaration': {},
            'Office_Use_Only': {},
            'Physical_Measurements': {},
            'Language_Skills': {},
            'Medical_History': {},
            'Assessments': {},
            'Competency_Tests': {},
            'Applied_Position_Info': {},
            'Education': {},
        }
        
        # Upload document
        pdf_file = SimpleUploadedFile(
            "integration_test.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        
        response = self.client.post('/ai/upload/', {'file': pdf_file}, format='multipart')
        
        # Verify response
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_206_PARTIAL_CONTENT])
        self.assertTrue(response.data['success'])
        
        applicant_id = response.data['applicant_id']
        self.assertIsNotNone(applicant_id)
        
        # Verify applicant was created
        applicant = Applicant.objects.get(id=applicant_id)
        self.assertEqual(
            applicant.personal_details['Full_Name'],
            'Integration Test User'
        )


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
