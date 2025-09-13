# from django.shortcuts import render

# # Create your views here.
# # doc_parser/views.py
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser
# from .models import ParsedDocument
# from .serializers import ParsedDocumentSerializer
# from .ai_parser_service import extract_document_features

# class DocumentUploadViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint for uploading seafarer application forms for AI parsing.
#     """
#     queryset = ParsedDocument.objects.all()
#     serializer_class = ParsedDocumentSerializer
#     parser_classes = [MultiPartParser, FormParser]

#     def create(self, request, *args, **kwargs):
#         # Standard file upload handling
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         # Save the initial model instance to get a file path
#         instance = serializer.save()
#         instance.status = 'PROCESSING'
#         instance.save()

#         try:
#             # --- AI Processing Step ---
#             # 1. Extract data from the uploaded document using the AI service
#             extracted_yaml = extract_document_features(instance.source_file.path)
#             if not extracted_yaml:
#                 instance.status = 'FAILED'
#                 instance.save()
#                 return Response(
#                     {"error": "Could not extract data from the document."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )


#             # 3. Save the result and update the status
#             instance.extracted_data_yaml = extracted_yaml
#             instance.status = 'COMPLETED'
#             instance.save()

#             # Return the successful response with the extracted data
#             headers = self.get_success_headers(serializer.data)
#             return Response(
#                 self.get_serializer(instance).data,
#                 status=status.HTTP_201_CREATED,
#                 headers=headers
#             )

#         except Exception as e:
#             # Handle any errors during AI processing
#             instance.status = 'FAILED'
#             instance.save()
#             return Response(
#                 {"error": f"An error occurred during AI processing: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ParsedDocument
from .serializers import ParsedDocumentSerializer
from .ai_parser_service import extract_document_features
from api.models import Users
from api.serializer import UsersSerializer
import yaml
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DocumentUploadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for uploading seafarer application forms for AI parsing.
    """
    queryset = ParsedDocument.objects.all()
    serializer_class = ParsedDocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        # Standard file upload handling
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the initial model instance to get a file path
        instance = serializer.save()
        instance.status = 'PROCESSING'
        instance.save()

        try:
            # --- AI Processing Step ---
            # 1. Extract data from the uploaded document using the AI service
            extracted_yaml = extract_document_features(instance.source_file.path)
            if not extracted_yaml:
                instance.status = 'FAILED'
                instance.save()
                return Response(
                    {"error": "Could not extract data from the document."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Parse the YAML and create a new user
            try:
                # Handle both YAML and JSON responses
                if extracted_yaml.strip().startswith('{') or extracted_yaml.strip().startswith('['):
                    # It's JSON format
                    import json
                    parsed_data = json.loads(extracted_yaml)
                else:
                    # It's YAML format
                    parsed_data = yaml.safe_load(extracted_yaml)
                
                # Handle case where data is wrapped in a "document" key
                if isinstance(parsed_data, dict) and "document" in parsed_data:
                    parsed_data = parsed_data["document"]
                
                # If it's a list, take the first item (or most complete one)
                if isinstance(parsed_data, list) and len(parsed_data) > 0:
                    parsed_data = parsed_data[0]
                
                user = self._create_user_from_yaml(parsed_data)
                
                # Link the created user to the parsed document
                instance.associated_user = user
                
            except Exception as e:
                logger.error(f"Error creating user from extracted data: {str(e)}")
                logger.error(f"Extracted data was: {extracted_yaml}")
                instance.status = 'FAILED'
                instance.save()
                return Response(
                    {"error": f"Could not create user from extracted data: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3. Save the result and update the status
            instance.extracted_data_yaml = extracted_yaml
            instance.status = 'COMPLETED'
            instance.save()

            # Return the successful response with the extracted data and created user info
            response_data = self.get_serializer(instance).data
            response_data['created_user_id'] = user.id if user else None
            response_data['created_user_email'] = user.email if user else None
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                response_data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        except Exception as e:
            # Handle any errors during AI processing
            instance.status = 'FAILED'
            instance.save()
            return Response(
                {"error": f"An error occurred during AI processing: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _create_user_from_yaml(self, yaml_data):
        """
        Create a new Users instance from the parsed YAML data.
        Maps the extracted document fields to the Users model fields.
        """
        if not yaml_data or not isinstance(yaml_data, dict):
            raise ValueError("Invalid YAML data structure")

        # Extract and map the fields
        user_data = {}
        
        # Basic personal information
        full_name = yaml_data.get('full_name', '').strip()
        if full_name:
            name_parts = full_name.split()
            user_data['first_name'] = name_parts[0] if name_parts else ''
            user_data['last_name'] = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        # Date fields with proper parsing
        date_of_birth = self._parse_date(yaml_data.get('date_of_birth'))
        if date_of_birth:
            user_data['date_of_birth'] = date_of_birth
            # Calculate age if date of birth is available
            today = datetime.today().date()
            age = today.year - date_of_birth.year
            if today.month < date_of_birth.month or (today.month == date_of_birth.month and today.day < date_of_birth.day):
                age -= 1
            user_data['age'] = age

        # Contact information
        if yaml_data.get('email'):
            user_data['email'] = yaml_data['email'].strip()
            user_data['username'] = yaml_data['email'].strip()  # Use email as username
        
        if yaml_data.get('phone_number'):
            user_data['phone_number'] = yaml_data['phone_number'].strip()
        
        if yaml_data.get('address'):
            user_data['address'] = yaml_data['address'].strip()
        
        if yaml_data.get('nationality'):
            user_data['nationality'] = yaml_data['nationality'].strip()
        
        if yaml_data.get('place_of_birth'):
            user_data['Place_Of_Birth'] = yaml_data['place_of_birth'].strip()

        # Travel document fields
        if yaml_data.get('passport_number'):
            user_data['passport_no'] = yaml_data['passport_number'].strip()
        
        passport_issue_date = self._parse_date(yaml_data.get('passport_issue_date'))
        if passport_issue_date:
            user_data['passport_issue_date'] = passport_issue_date
            
        passport_expiry_date = self._parse_date(yaml_data.get('passport_expiry_date'))
        if passport_expiry_date:
            user_data['passport_expiry_date'] = passport_expiry_date

        # Seaman book fields
        if yaml_data.get('seaman_book_number'):
            user_data['seaman_book_no'] = yaml_data['seaman_book_number'].strip()
            
        seaman_book_issue_date = self._parse_date(yaml_data.get('seaman_book_issue_date'))
        if seaman_book_issue_date:
            user_data['seaman_book_issue_date'] = seaman_book_issue_date
            
        seaman_book_expiry_date = self._parse_date(yaml_data.get('seaman_book_expiry_date'))
        if seaman_book_expiry_date:
            user_data['seaman_book_expiry_date'] = seaman_book_expiry_date

        # Ensure required fields are present
        if not user_data.get('email'):
            # Generate a temporary email if not provided
            user_data['email'] = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@tempmail.com"
            user_data['username'] = user_data['email']
        
        if not user_data.get('first_name'):
            user_data['first_name'] = 'Unknown'
        
        if not user_data.get('last_name'):
            user_data['last_name'] = 'User'
        
        if not user_data.get('phone_number'):
            user_data['phone_number'] = 'Not provided'

        # Set a default password (you may want to generate a random one and email it)
        user_data['password'] = 'TempPassword123!'

        try:
            # Check if user with this email already exists
            existing_user = Users.objects.filter(email=user_data['email']).first()
            if existing_user:
                logger.warning(f"User with email {user_data['email']} already exists. Skipping creation.")
                return existing_user

            # Create the user using Django's create_user method
            user = Users.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            # Update additional fields
            for field, value in user_data.items():
                if field not in ['username', 'email', 'password', 'first_name', 'last_name'] and hasattr(user, field):
                    setattr(user, field, value)
            
            user.save()
            logger.info(f"Successfully created user: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise e

    def _parse_date(self, date_string):
        """
        Parse date string in various formats and return a date object.
        """
        if not date_string:
            return None
            
        # Try different date formats
        date_formats = [
            '%Y-%m-%d',    # 2023-12-31
            '%d-%m-%Y',    # 31-12-2023
            '%m/%d/%Y',    # 12/31/2023
            '%d/%m/%Y',    # 31/12/2023
            '%Y/%m/%d',    # 2023/12/31
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_string).strip(), fmt).date()
            except ValueError:
                continue
                
        logger.warning(f"Could not parse date: {date_string}")
        return None