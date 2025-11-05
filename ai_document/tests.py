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
from django.test import TestCase, TransactionTestCase
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


# Run tests with: python manage.py test ai_document.tests
