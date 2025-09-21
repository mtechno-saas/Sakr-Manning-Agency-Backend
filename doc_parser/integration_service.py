# doc_parser/integration_service.py
"""
Service to integrate extracted document data with the main Users model.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from django.db import transaction
from django.contrib.auth import get_user_model

from api.models import Users, Certificate, Rank, UserRank, Reference, SeaService
from .models import ParsedDocument, ExtractedFeature

logger = logging.getLogger(__name__)


class DocumentUserIntegrationService:
    """
    Service to create or update Users from extracted document data.
    """
    
    def __init__(self):
        self.field_mapping = self._get_field_mapping()
    
    def _get_field_mapping(self) -> Dict[str, str]:
        """
        Map extracted feature fields to Users model fields.
        """
        return {
            # Personal Information
            'personal_information.full_name': 'first_name',  # Will need parsing
            'personal_information.date_of_birth': 'date_of_birth',
            'personal_information.nationality': 'nationality',
            'personal_information.place_of_birth': 'Place_Of_Birth',
            'personal_information.height': 'Height_Cm',
            'personal_information.weight': 'Weight_Kg',
            'personal_information.marital_status': 'marital_status',
            
            # Contact Information
            'contact_information.email': 'email',
            'contact_information.phone_number': 'phone_number',
            'contact_information.address': 'address',
            
            # Travel Documents
            'travel_documents.passport_number': 'passport_no',
            'travel_documents.passport_issue_date': 'passport_issue_date',
            'travel_documents.passport_expiry_date': 'passport_expiry_date',
            'travel_documents.seaman_book_number': 'seaman_book_no',
            'travel_documents.seaman_book_issue_date': 'seaman_book_issue_date',
            'travel_documents.seaman_book_expiry_date': 'seaman_book_expiry_date',
            
            # Medical Information
            'medical_information.medical_certificate_number': 'health_number',
            'medical_information.medical_issue_date': 'health_issue_date',
            'medical_information.medical_expiry_date': 'health_expiry_date',
            'medical_information.yellow_fever_vaccination': 'yellow_fever_issue_date',
            
            # Next of Kin
            'next_of_kin.full_name': 'next_of_kin_full_name',
            'next_of_kin.relationship': 'next_of_kin_relationship',
            'next_of_kin.phone_number': 'next_of_kin_phone',
            'next_of_kin.address': 'next_of_kin_address_country',
            'next_of_kin.email': 'next_of_kin_email',
        }
    
    def create_or_update_user_from_document(
        self, 
        document_id: int, 
        update_existing: bool = False
    ) -> Tuple[Optional[Users], Dict[str, Any]]:
        """
        Create or update a User from extracted document data.
        
        Args:
            document_id: ID of the ParsedDocument
            update_existing: Whether to update existing user if email matches
            
        Returns:
            Tuple of (created/updated User instance, result metadata)
        """
        try:
            document = ParsedDocument.objects.get(id=document_id)
            
            if document.status != 'COMPLETED':
                return None, {
                    'success': False,
                    'error': f'Document processing not completed. Status: {document.status}'
                }
            
            extracted_data = document.extracted_features
            if not extracted_data:
                return None, {
                    'success': False,
                    'error': 'No extracted data found in document'
                }
            
            # Prepare user data
            user_data = self._prepare_user_data(extracted_data)
            
            if not user_data.get('email'):
                return None, {
                    'success': False,
                    'error': 'No email found in extracted data. Cannot create user without email.'
                }
            
            # Check if user exists
            existing_user = None
            try:
                existing_user = Users.objects.get(email=user_data['email'])
                if not update_existing:
                    return None, {
                        'success': False,
                        'error': f'User with email {user_data["email"]} already exists. Set update_existing=True to update.'
                    }
            except Users.DoesNotExist:
                pass
            
            # Create or update user
            with transaction.atomic():
                if existing_user:
                    user = self._update_user(existing_user, user_data, extracted_data)
                    action = 'updated'
                else:
                    user = self._create_user(user_data, extracted_data)
                    action = 'created'
                
                # Link document to user
                document.associated_user = user
                document.save()
                
                # Create integration log
                self._log_integration(document, user, action, extracted_data)
            
            return user, {
                'success': True,
                'action': action,
                'user_id': user.id,
                'user_email': user.email,
                'fields_mapped': len([k for k, v in user_data.items() if v]),
                'certificates_created': self._count_certificates_created(extracted_data),
                'sea_services_created': self._count_sea_services_created(extracted_data)
            }
            
        except ParsedDocument.DoesNotExist:
            return None, {
                'success': False,
                'error': f'Document with ID {document_id} not found'
            }
        except Exception as e:
            logger.error(f"Error integrating document {document_id}: {str(e)}", exc_info=True)
            return None, {
                'success': False,
                'error': f'Integration failed: {str(e)}'
            }
    
    def _prepare_user_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare user data by mapping extracted fields to Users model fields.
        """
        user_data = {}
        
        # Map basic fields
        for source_field, target_field in self.field_mapping.items():
            category, field_name = source_field.split('.', 1)
            
            if category in extracted_data and isinstance(extracted_data[category], dict):
                value = extracted_data[category].get(field_name)
                
                if value and str(value).strip() and str(value) != 'Not Available':
                    # Clean and format the value
                    cleaned_value = self._clean_field_value(value, target_field)
                    if cleaned_value:
                        user_data[target_field] = cleaned_value
        
        # Handle special cases
        self._handle_special_mappings(user_data, extracted_data)
        
        return user_data
    
    def _handle_special_mappings(self, user_data: Dict[str, Any], extracted_data: Dict[str, Any]) -> None:
        """
        Handle special field mappings that require custom logic.
        """
        # Parse full name into first_name, middle_name, last_name
        personal_info = extracted_data.get('personal_information', {})
        full_name = personal_info.get('full_name', '')
        
        if full_name and full_name != 'Not Available':
            name_parts = full_name.strip().split()
            if len(name_parts) >= 1:
                user_data['first_name'] = name_parts[0]
            if len(name_parts) >= 2:
                user_data['last_name'] = name_parts[-1]
            if len(name_parts) >= 3:
                user_data['middle_name'] = ' '.join(name_parts[1:-1])
        
        # Generate username if not provided
        if not user_data.get('username') and user_data.get('email'):
            base_username = user_data['email'].split('@')[0]
            username = base_username
            counter = 1
            
            while Users.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            user_data['username'] = username
        
        # Set default status
        user_data['user_status'] = 'AVAILABLE'
        user_data['is_active'] = True
    
    def _clean_field_value(self, value: Any, target_field: str) -> Any:
        """
        Clean and format field values based on target field type.
        """
        if not value or str(value).strip() in ['Not Available', 'N/A', '', 'null', 'None']:
            return None
        
        value_str = str(value).strip()
        
        # Date fields
        if target_field.endswith('_date') or target_field == 'date_of_birth':
            return self._parse_date(value_str)
        
        # Numeric fields
        elif target_field in ['Height_Cm', 'Weight_Kg', 'age']:
            try:
                # Extract numbers from strings like "175 cm" or "75 kg"
                import re
                numbers = re.findall(r'\d+', value_str)
                if numbers:
                    return int(numbers[0])
            except:
                pass
            return None
        
        # Email fields
        elif target_field.endswith('email'):
            if '@' in value_str:
                return value_str.lower()
            return None
        
        # Phone fields
        elif 'phone' in target_field:
            # Clean phone number format
            import re
            phone_clean = re.sub(r'[^\d+]', '', value_str)
            if len(phone_clean) >= 7:
                return phone_clean
            return None
        
        return value_str
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string into YYYY-MM-DD format.
        """
        if not date_str:
            return None
        
        from datetime import datetime
        date_formats = [
            '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y',
            '%d.%m.%Y', '%Y.%m.%d', '%B %d, %Y', '%d %B %Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def _create_user(self, user_data: Dict[str, Any], extracted_data: Dict[str, Any]) -> Users:
        """
        Create a new user with extracted data.
        """
        # Set default password
        user_data['password'] = 'extracted_user_2024'
        
        user = Users.objects.create_user(**user_data)
        
        # Add certificates and qualifications
        self._add_certificates_to_user(user, extracted_data)
        
        # Add sea service records
        self._add_sea_services_to_user(user, extracted_data)
        
        # Add references if available
        self._add_references_to_user(user, extracted_data)
        
        logger.info(f"Created new user from document: {user.email}")
        return user
    
    def _update_user(self, user: Users, user_data: Dict[str, Any], extracted_data: Dict[str, Any]) -> Users:
        """
        Update existing user with extracted data.
        """
        # Remove password from update data
        user_data.pop('password', None)
        
        # Update user fields
        for field, value in user_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        user.save()
        
        # Update relationships
        self._add_certificates_to_user(user, extracted_data)
        self._add_sea_services_to_user(user, extracted_data)
        self._add_references_to_user(user, extracted_data)
        
        logger.info(f"Updated existing user from document: {user.email}")
        return user
    
    def _add_certificates_to_user(self, user: Users, extracted_data: Dict[str, Any]) -> None:
        """
        Add certificates based on extracted training data.
        """
        training_data = extracted_data.get('stcw_training', {})
        qualifications_data = extracted_data.get('qualifications', {})
        
        # Common STCW certificates mapping
        certificate_mapping = {
            'personal_survival_techniques': 'PST - Personal Survival Techniques',
            'fire_prevention_fighting': 'FPFF - Fire Prevention and Fire Fighting',
            'elementary_first_aid': 'EFA - Elementary First Aid',
            'personal_safety_social_responsibilities': 'PSSR - Personal Safety and Social Responsibilities',
            'security_awareness': 'SA - Security Awareness',
            'proficiency_survival_craft': 'PSC - Proficiency in Survival Craft',
            'passenger_safety': 'PS - Passenger Safety',
            'crowd_management': 'CM - Crowd Management',
            'crisis_management': 'CRM - Crisis Management',
        }
        
        certificates_to_add = []
        
        # Process STCW training
        for field_name, cert_name in certificate_mapping.items():
            if training_data.get(field_name):
                cert, created = Certificate.objects.get_or_create(
                    code=field_name.upper(),
                    defaults={'name': cert_name}
                )
                certificates_to_add.append(cert)
        
        # Process qualifications
        coc_data = qualifications_data.get('certificate_of_competency')
        if coc_data and coc_data != 'Not Available':
            cert, created = Certificate.objects.get_or_create(
                code='COC',
                defaults={'name': f'Certificate of Competency - {coc_data}'}
            )
            certificates_to_add.append(cert)
        
        # Add certificates to user
        if certificates_to_add:
            user.certificates.add(*certificates_to_add)
    
    def _add_sea_services_to_user(self, user: Users, extracted_data: Dict[str, Any]) -> None:
        """
        Add sea service records from extracted data.
        """
        sea_service_data = extracted_data.get('sea_service', {})
        
        if not sea_service_data:
            return
        
        # Check if we have enough data for a sea service record
        vessel_name = sea_service_data.get('last_vessel_name', '').strip()
        company_name = sea_service_data.get('last_company', '').strip()
        rank = sea_service_data.get('last_rank', '').strip()
        
        if vessel_name and vessel_name != 'Not Available':
            SeaService.objects.create(
                user=user,
                vessel_name_imo=vessel_name,
                company_name=company_name or 'Not Specified',
                rank=rank or 'Not Specified',
                signed_on=None,  # Would need more specific date extraction
                signed_off=None,
                total_experience_months=self._extract_experience_months(sea_service_data)
            )
    
    def _add_references_to_user(self, user: Users, extracted_data: Dict[str, Any]) -> None:
        """
        Add references from extracted data.
        """
        # This would depend on having reference data in the extracted features
        # For now, we'll skip this unless specific reference data is available
        pass
    
    def _extract_experience_months(self, sea_service_data: Dict[str, Any]) -> Optional[int]:
        """
        Extract total experience in months from sea service data.
        """
        experience_str = sea_service_data.get('total_experience_years', '')
        if not experience_str or experience_str == 'Not Available':
            return None
        
        try:
            import re
            # Look for numbers in the experience string
            numbers = re.findall(r'\d+', str(experience_str))
            if numbers:
                years = int(numbers[0])
                return years * 12  # Convert to months
        except:
            pass
        
        return None
    
    def _count_certificates_created(self, extracted_data: Dict[str, Any]) -> int:
        """Count how many certificates would be created."""
        training_data = extracted_data.get('stcw_training', {})
        qualifications_data = extracted_data.get('qualifications', {})
        
        count = 0
        for value in training_data.values():
            if value and str(value) != 'Not Available':
                count += 1
        
        if qualifications_data.get('certificate_of_competency', '') != 'Not Available':
            count += 1
        
        return count
    
    def _count_sea_services_created(self, extracted_data: Dict[str, Any]) -> int:
        """Count how many sea service records would be created."""
        sea_service_data = extracted_data.get('sea_service', {})
        vessel_name = sea_service_data.get('last_vessel_name', '').strip()
        
        return 1 if vessel_name and vessel_name != 'Not Available' else 0
    
    def _log_integration(self, document: ParsedDocument, user: Users, action: str, extracted_data: Dict[str, Any]) -> None:
        """
        Log the integration process for audit purposes.
        """
        from .models import ExtractionLog
        
        ExtractionLog.objects.create(
            document=document,
            level='INFO',
            message=f'Successfully {action} user {user.email} from extracted document data',
            details={
                'user_id': user.id,
                'action': action,
                'fields_processed': len(extracted_data),
                'integration_timestamp': datetime.now().isoformat()
            },
            extraction_step='user_integration'
        )


# Convenience function
def integrate_document_with_user(document_id: int, update_existing: bool = False) -> Tuple[Optional[Users], Dict[str, Any]]:
    """
    Convenience function to integrate a document with a user.
    """
    service = DocumentUserIntegrationService()
    return service.create_or_update_user_from_document(document_id, update_existing)