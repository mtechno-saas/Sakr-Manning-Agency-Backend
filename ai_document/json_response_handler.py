"""
Robust JSON response handler for Django app dealing with LLM-generated JSON.
Handles malformed JSON from language models and provides fallback parsing strategies.
"""

import json
import re
import logging
from typing import Dict, Any, Optional, Union
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class JSONResponseHandler:
    """
    Handles malformed JSON responses from LLM and provides robust parsing.
    """
    
    @staticmethod
    def clean_llm_json(raw_text: str) -> str:
        """
        Clean malformed JSON from LLM output.
        
        Args:
            raw_text: Raw text output from LLM
            
        Returns:
            Cleaned JSON string
        """
        if hasattr(raw_text, 'content'):
            raw_text = raw_text.content
        else:
            raw_text = str(raw_text)
        
        # Remove markdown code fences
        text = re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE)
        
        # Extract JSON object if embedded in other text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
        
        # Fix common LLM JSON issues
        
        # 1. Remove control characters that cause parsing errors
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # 2. Fix broken array syntax like ["English", "Arabic"]
        def fix_array_syntax(match):
            content = match.group(1)
            # Split by comma and clean each item
            items = []
            for item in content.split(','):
                item = item.strip().strip('"\'')
                if item:
                    items.append(f'"{item}"')
            return f'[{", ".join(items)}]'
        
        text = re.sub(r'\[([^\]]*)\]', fix_array_syntax, text)
        
        # 3. Fix object syntax in arrays
        def fix_object_in_array(match):
            content = match.group(1)
            # If it looks like an object, wrap it properly
            if '{' in content and '}' in content:
                return f'[{content}]'
            return match.group(0)
        
        text = re.sub(r'\[([^[\]]*\{[^}]*\}[^[\]]*)\]', fix_object_in_array, text)
        
        # 4. Ensure all keys are quoted
        text = re.sub(r'(\w+)(?=\s*:)', r'"\1"', text)
        
        # 5. Fix trailing commas
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        
        # 6. Fix multiple commas
        text = re.sub(r',\s*,+', ',', text)
        
        # 7. Fix quotes around values
        text = re.sub(r':\s*"([^"]*)"([^,}\]]*)"', r': "\1\2"', text)
        
        return text
    
    @staticmethod
    def extract_structured_data(raw_text: str) -> Dict[str, Any]:
        """
        Extract structured data using regex patterns as fallback.
        
        Args:
            raw_text: Raw text from LLM
            
        Returns:
            Dictionary with extracted data
        """
        result = {
            "Personal_Details": {},
            "Education": {},
            "Contact_Details": {},
            "Travel_Documents": {},
            "Professional_Qualifications": {},
            "Next_of_Kin_Emergency_Contact": {},
            "Health_Certificates_Vaccinations": {},
            "Covid_19_Vaccination": {},
            "Marine_Courses": {},
            "Sea_Service_Details": {},
            "Specialised_Experience": {},
            "References": {},
            "Declaration": {},
            "Office_Use_Only": {}
        }
        
        # Extract personal details
        name_match = re.search(r'"name":\s*"([^"]*)"', raw_text, re.IGNORECASE)
        if name_match:
            result["Personal_Details"]["name"] = name_match.group(1)
        
        email_match = re.search(r'"email":\s*"([^"]*@[^"]*)"', raw_text, re.IGNORECASE)
        if email_match:
            result["Personal_Details"]["email"] = email_match.group(1)
            result["Contact_Details"]["email"] = email_match.group(1)
        
        phone_match = re.search(r'"phone":\s*"([^"]*)"', raw_text, re.IGNORECASE)
        if phone_match:
            result["Personal_Details"]["phone"] = phone_match.group(1)
            result["Contact_Details"]["phone"] = phone_match.group(1)
        
        # Extract nationality
        nationality_match = re.search(r'"nationality":\s*"([^"]*)"', raw_text, re.IGNORECASE)
        if nationality_match:
            result["Personal_Details"]["nationality"] = nationality_match.group(1)
        
        # Extract birth date
        birth_date_match = re.search(r'"birth_date":\s*"([^"]*)"', raw_text, re.IGNORECASE)
        if birth_date_match:
            result["Personal_Details"]["birth_date"] = birth_date_match.group(1)
        
        # Extract address
        address_match = re.search(r'"address":\s*"([^"]*)"', raw_text, re.IGNORECASE)
        if address_match:
            result["Personal_Details"]["address"] = address_match.group(1)
            result["Contact_Details"]["address"] = address_match.group(1)
        
        return result
    
    @staticmethod
    def parse_llm_response(raw_response: str) -> Dict[str, Any]:
        """
        Parse LLM response with multiple fallback strategies.
        
        Args:
            raw_response: Raw response from LLM
            
        Returns:
            Parsed dictionary or error information
        """
        logger.info("Attempting to parse LLM response")
        
        # Strategy 1: Try direct JSON parsing
        try:
            if isinstance(raw_response, dict):
                return raw_response
            
            result = json.loads(raw_response)
            logger.info("Successfully parsed JSON directly")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parsing failed: {e}")
        
        # Strategy 2: Clean and parse
        try:
            cleaned = JSONResponseHandler.clean_llm_json(raw_response)
            result = json.loads(cleaned)
            logger.info("Successfully parsed cleaned JSON")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Cleaned JSON parsing failed: {e}")
        
        # Strategy 3: Extract structured data manually
        try:
            result = JSONResponseHandler.extract_structured_data(raw_response)
            logger.info("Successfully extracted structured data manually")
            return result
        except Exception as e:
            logger.error(f"Manual extraction failed: {e}")
        
        # Strategy 4: Return minimal structure with error info
        logger.error("All parsing strategies failed")
        return {
            "Personal_Details": {},
            "Education": {},
            "Contact_Details": {},
            "Travel_Documents": {},
            "Professional_Qualifications": {},
            "Next_of_Kin_Emergency_Contact": {},
            "Health_Certificates_Vaccinations": {},
            "Covid_19_Vaccination": {},
            "Marine_Courses": {},
            "Sea_Service_Details": {},
            "Specialised_Experience": {},
            "References": {},
            "Declaration": {},
            "Office_Use_Only": {},
            "parsing_error": "Failed to parse LLM response",
            "raw_output": raw_response[:500] if len(raw_response) > 500 else raw_response
        }
    
    @staticmethod
    def create_success_response(data: Dict[str, Any], message: str = "Success") -> Response:
        """
        Create a standardized success response.
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            DRF Response object
        """
        return Response({
            "success": True,
            "message": message,
            "data": data,
            "timestamp": "2025-09-30T18:41:23Z"  # You can use timezone.now()
        }, status=status.HTTP_200_OK)
    
    @staticmethod
    def create_error_response(error_message: str, error_code: str = "PROCESSING_ERROR", 
                            status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
        """
        Create a standardized error response.
        
        Args:
            error_message: Error description
            error_code: Error code
            status_code: HTTP status code
            
        Returns:
            DRF Response object
        """
        return Response({
            "success": False,
            "error": {
                "code": error_code,
                "message": error_message
            },
            "timestamp": "2025-09-30T18:41:23Z"  # You can use timezone.now()
        }, status=status_code)


class ApplicantDataValidator:
    """
    Validates and normalizes applicant data from parsed JSON.
    """
    
    @staticmethod
    def validate_personal_details(personal_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize personal details.
        
        Args:
            personal_details: Personal details dictionary
            
        Returns:
            Validated personal details
        """
        validated = {}
        
        # Name validation
        name = personal_details.get("name", "").strip()
        if name:
            validated["name"] = name.upper()
        
        # Email validation
        email = personal_details.get("email", "").strip().lower()
        if email and "@" in email:
            validated["email"] = email
        
        # Phone validation
        phone = personal_details.get("phone", "").strip()
        if phone:
            # Remove common prefixes and clean
            phone = re.sub(r'^(\+|00)', '', phone)
            phone = re.sub(r'[^\d+]', '', phone)
            validated["phone"] = phone
        
        # Birth date validation
        birth_date = personal_details.get("birth_date", "").strip()
        if birth_date:
            validated["birth_date"] = birth_date
        
        # Nationality validation
        nationality = personal_details.get("nationality", "").strip()
        if nationality:
            validated["nationality"] = nationality.title()
        
        # Address validation
        address = personal_details.get("address", "").strip()
        if address:
            validated["address"] = address
        
        return validated
    
    @staticmethod
    def validate_contact_details(contact_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize contact details.
        
        Args:
            contact_details: Contact details dictionary
            
        Returns:
            Validated contact details
        """
        validated = {}
        
        # Email validation
        email = contact_details.get("email", "").strip().lower()
        if email and "@" in email:
            validated["email"] = email
        
        # Phone validation
        phone = contact_details.get("phone", "").strip()
        if phone:
            phone = re.sub(r'^(\+|00)', '', phone)
            phone = re.sub(r'[^\d+]', '', phone)
            validated["phone"] = phone
        
        # Address validation
        address = contact_details.get("address", "").strip()
        if address:
            validated["address"] = address
        
        return validated
    
    @staticmethod
    def validate_and_normalize_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize all applicant data.
        
        Args:
            parsed_data: Parsed data from LLM
            
        Returns:
            Validated and normalized data
        """
        validated_data = {}
        
        # Validate personal details
        if "Personal_Details" in parsed_data:
            validated_data["Personal_Details"] = ApplicantDataValidator.validate_personal_details(
                parsed_data["Personal_Details"]
            )
        
        # Validate contact details
        if "Contact_Details" in parsed_data:
            validated_data["Contact_Details"] = ApplicantDataValidator.validate_contact_details(
                parsed_data["Contact_Details"]
            )
        
        # Copy other sections as-is (you can add more validation as needed)
        for key in ["Education", "Travel_Documents", "Professional_Qualifications", 
                   "Next_of_Kin_Emergency_Contact", "Health_Certificates_Vaccinations",
                   "Covid_19_Vaccination", "Marine_Courses", "Sea_Service_Details",
                   "Specialised_Experience", "References", "Declaration", "Office_Use_Only"]:
            if key in parsed_data:
                validated_data[key] = parsed_data[key]
            else:
                validated_data[key] = {}
        
        return validated_data


# Example usage function
def process_document_response(raw_llm_output: str, file_name: str) -> Response:
    """
    Process document and return standardized response.
    
    Args:
        raw_llm_output: Raw output from LLM
        file_name: Name of processed file
        
    Returns:
        Standardized API response
    """
    try:
        # Parse LLM response
        parsed_data = JSONResponseHandler.parse_llm_response(raw_llm_output)
        
        # Validate and normalize data
        validated_data = ApplicantDataValidator.validate_and_normalize_data(parsed_data)
        
        # Create response data
        response_data = {
            "file_name": file_name,
            "applicant_data": validated_data,
            "processing_status": "completed",
            "data_quality": "high" if "parsing_error" not in validated_data else "low"
        }
        
        return JSONResponseHandler.create_success_response(
            response_data, 
            "Document processed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error processing document response: {e}")
        return JSONResponseHandler.create_error_response(
            f"Failed to process document: {str(e)}",
            "DOCUMENT_PROCESSING_ERROR"
        )