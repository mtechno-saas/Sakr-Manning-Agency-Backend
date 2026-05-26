from rest_framework import serializers
from .models import (
    Users, Rank, UserRank, Contract, Reference, SeaService, Certificate,
    UserLanguage, PersonalDocument, Declaration, NextOfKin
)
from courses.models import Course
from vaccinations.models import Vaccination
from licenses.models import UserLicense
from api.serializers import FlexibleDateField, FlexibleFileField
from datetime import datetime

class SeafarerApplicationSerializer(serializers.ModelSerializer):
    # Define these as fields that can be read and written
    document_info = serializers.JSONField(required=False)
    application_header = serializers.JSONField(required=False)
    personal_details = serializers.JSONField(required=False)
    education = serializers.JSONField(required=False)
    contact_details = serializers.JSONField(required=False)
    travel_documents = serializers.JSONField(required=False)
    professional_qualification = serializers.JSONField(required=False)
    next_of_kin = serializers.JSONField(required=False)
    health_certificates = serializers.JSONField(required=False)
    marine_courses = serializers.JSONField(required=False)
    sea_service_details = serializers.JSONField(required=False)
    references = serializers.JSONField(required=False)
    declaration = serializers.JSONField(required=False)
    for_office_use_only = serializers.JSONField(required=False)

    class Meta:
        model = Users
        fields = [
            'id', 'email', 'first_name', 'middle_name', # Core fields
            'document_info', 'application_header', 'personal_details', 
            'education', 'contact_details', 'travel_documents', 
            'professional_qualification', 'next_of_kin', 'health_certificates', 
            'marine_courses', 'sea_service_details', 'references', 
            'declaration', 'for_office_use_only'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
        }

    def to_representation(self, instance):
        """Custom representation to match the EXACT JSON format requested."""
        data = super().to_representation(instance)
        
        # Build the final structure
        result = {}
        
        if not self.context.get('exclude_headers', False):
            result["document_info"] = self.get_document_info(instance)
            result["application_header"] = self.get_application_header(instance)
            
        result.update({
            "1_personal_details": self.get_personal_details(instance),
            "2_education": self.get_education(instance),
            "3_contact_details": self.get_contact_details(instance),
            "4_travel_documents": self.get_travel_documents(instance),
            "5_professional_qualification_certificate_of_competency": self.get_professional_qualification(instance),
            "6_next_of_kin_emergency_contact": self.get_next_of_kin(instance),
            "7_health_certificates_and_vaccinations": self.get_health_certificates(instance),
            "8_marine_courses": self.get_marine_courses(instance),
            "9_complete_sea_service_details": self.get_sea_service_details(instance),
            "10_references": self.get_references(instance),
            "11_declaration": self.get_declaration(instance),
            "12_for_office_use_only": self.get_for_office_use_only(instance)
        })
        return result

    def _parse_date(self, date_str):
        if not date_str:
            return None
        from datetime import date
        if isinstance(date_str, (datetime, date)):
            return date_str if isinstance(date_str, date) else date_str.date()
        for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y'):
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except ValueError:
                continue
        return None

    def update(self, instance, validated_data):
        # 1. Personal Details & Application Header
        personal = validated_data.get('personal_details', {})
        header = validated_data.get('application_header', {})
        
        if personal:
            full_name = personal.get('full_name', '')
            if full_name:
                parts = full_name.split(' ', 1)
                instance.first_name = parts[0]
                instance.middle_name = parts[1] if len(parts) > 1 else ''
            
            instance.date_of_birth = self._parse_date(personal.get('date_of_birth'))
            status = personal.get('marital_status', {})
            if status.get('married'):
                instance.marital_status = 'MARRIED'
            elif status.get('single'):
                instance.marital_status = 'SINGLE'
                
            instance.nationality = personal.get('nationality', instance.nationality)
            instance.Height_Cm = personal.get('height_cm', instance.Height_Cm)
            instance.Weight_Kg = personal.get('weight_kg', instance.Weight_Kg)
            instance.Place_Of_Birth = personal.get('place_of_birth', instance.Place_Of_Birth)
            instance.overall_size = personal.get('overall_size', instance.overall_size)
            instance.shirt_size = personal.get('shirt_size', instance.shirt_size)
            instance.Nearest_Port = personal.get('nearest_port', instance.Nearest_Port)
            instance.trouser_size = personal.get('trouser_size', instance.trouser_size)
            instance.shoes_size = personal.get('shoes_size', instance.shoes_size)

        if header:
            instance.application_for_position = header.get('application_for_position_as', instance.application_for_position)
            instance.register_code = header.get('register_code', instance.register_code)
            instance.other_position = header.get('other_position_if_any', instance.other_position)
            instance.register_date = self._parse_date(header.get('register_date'))
            
            if 'expected_salary' in header:
                instance.salary = header.get('expected_salary')
            
            if 'available_date' in header:
                instance.available_date = self._parse_date(header.get('available_date'))
            elif 'expected_salary_available_date' in header:
                instance.available_date = self._parse_date(header.get('expected_salary_available_date'))

        # 2. Education
        edu = validated_data.get('education', {})
        if edu:
            instance.college_or_school = edu.get('college_school', instance.college_or_school)
            marlins = edu.get('marline_test', {})
            if marlins:
                instance.marlins_test_issued_date = self._parse_date(marlins.get('issued_date'))
                instance.marlins_test_result = marlins.get('result_percentage', instance.marlins_test_result)
                instance.marlins_test_issued_by = marlins.get('issued_by_authority', instance.marlins_test_issued_by)
                instance.marlins_test_issued_at = marlins.get('issued_at', instance.marlins_test_issued_at)
            
            # Languages
            eng = edu.get('english_language', {})
            if eng:
                for k, v in eng.items():
                    if v: instance.english_language_level = k
            
            ger = edu.get('german_language', {})
            if ger:
                instance.other_language = "German"
                for k, v in ger.items():
                    if v: instance.other_language_level = k

        # 3. Contact Details
        contact = validated_data.get('contact_details', {})
        if contact:
            addr_city = contact.get('home_address_city', '')
            if ',' in addr_city:
                parts = addr_city.split(',', 1)
                instance.address = parts[0].strip()
                instance.city = parts[1].strip()
            else:
                instance.address = addr_city
            
            instance.email = contact.get('e_mail', instance.email)
            instance.phone_number = contact.get('mobile_tel', instance.phone_number)

        # 4. Travel Documents
        travel = validated_data.get('travel_documents', [])
        for t in travel:
            t_type = t.get('type', '')
            if not t_type:
                continue
            t_type_lower = t_type.lower()
            if 'passport' in t_type_lower:
                instance.passport_no = t.get('document_no', instance.passport_no)
                instance.passport_issue_date = self._parse_date(t.get('iss_date'))
                instance.passport_expiry_date = self._parse_date(t.get('exp_date'))
                instance.passport_issued_by = t.get('iss_by_authority', instance.passport_issued_by)
                instance.passport_place_of_issue = t.get('place_of_issue', instance.passport_place_of_issue)
            elif 'seaman book' in t_type_lower and 'other' not in t_type_lower:
                instance.seaman_book_no = t.get('document_no', instance.seaman_book_no)
                instance.seaman_book_issue_date = self._parse_date(t.get('iss_date'))
                instance.seaman_book_expiry_date = self._parse_date(t.get('exp_date'))
                instance.seaman_book_issued_by = t.get('iss_by_authority', instance.seaman_book_issued_by)
                instance.seaman_book_place_of_issue = t.get('place_of_issue', instance.seaman_book_place_of_issue)
            elif 'other seaman book' in t_type_lower:
                instance.other_seaman_book_no = t.get('document_no', instance.other_seaman_book_no)
                instance.other_seaman_book_issue_date = self._parse_date(t.get('iss_date'))
                instance.other_seaman_book_expiry_date = self._parse_date(t.get('exp_date'))
                instance.other_seaman_book_issued_by = t.get('iss_by_authority', instance.other_seaman_book_issued_by)
                instance.other_seaman_book_place_of_issue = t.get('place_of_issue', instance.other_seaman_book_place_of_issue)
            else:
                # Find matching choice in PersonalDocument choices to use its exact model choice capitalization
                matching_choice = None
                for choice_val, _ in PersonalDocument.DOCUMENT_TYPE_CHOICES:
                    if choice_val.lower() == t_type.lower():
                        matching_choice = choice_val
                        break
                
                if matching_choice:
                    PersonalDocument.objects.update_or_create(
                        user=instance,
                        document_type=matching_choice,
                        defaults={
                            'document_number': t.get('document_no'),
                            'issue_date': self._parse_date(t.get('iss_date')),
                            'expiry_date': self._parse_date(t.get('exp_date')),
                            'issued_by': t.get('iss_by_authority'),
                            'place_of_issue': t.get('place_of_issue'),
                            'issuing_country': t.get('issuing_country', '')
                        }
                    )

        # 5. Professional Qualification
        prof = validated_data.get('professional_qualification', [])
        for p in prof:
            p_name = p.get('certificate_name', '').lower()
            if 'coc' in p_name:
                instance.coc_certificate_number = p.get('number', instance.coc_certificate_number)
                instance.coc_issue_date = self._parse_date(p.get('issue_date'))
                instance.coc_expiry_date = self._parse_date(p.get('expiry_date'))
                instance.coc_issued_by = p.get('issued_by', instance.coc_issued_by)
                instance.coc_issued_at = p.get('issued_at', instance.coc_issued_at)
            elif 'goc' in p_name:
                instance.goc_certificate_number = p.get('number', instance.goc_certificate_number)
                instance.goc_issue_date = self._parse_date(p.get('issue_date'))
                instance.goc_expiry_date = self._parse_date(p.get('expiry_date'))
                instance.goc_issued_by = p.get('issued_by', instance.goc_issued_by)
                instance.goc_issued_at = p.get('issued_at', instance.goc_issued_at)

        # 6. Next of Kin
        nok_data = validated_data.get('next_of_kin', {})
        if nok_data:
            instance.next_of_kin_full_name = nok_data.get('full_name', instance.next_of_kin_full_name)
            instance.next_of_kin_address_country = nok_data.get('address_country', instance.next_of_kin_address_country)
            instance.next_of_kin_phone = nok_data.get('tel_no_mobile', instance.next_of_kin_phone)
            instance.next_of_kin_relationship = nok_data.get('relationship', instance.next_of_kin_relationship)
            instance.next_of_kin_email = nok_data.get('email', instance.next_of_kin_email)

        # 7. Health Certificates
        health = validated_data.get('health_certificates', {})
        if health:
            certs = health.get('certificates', [])
            # Use delete and recreate pattern to sync with frontend list
            instance.vaccinations.all().delete()
            
            for c in certs:
                f_state = c.get('flag_state', '')
                if not f_state: continue
                
                fs_lower = f_state.lower()
                # Sync to legacy fields on User model if keyword matches
                if 'international' in fs_lower or 'medical' in fs_lower:
                    instance.international_medical_number = c.get('number', instance.international_medical_number)
                    instance.international_medical_issue_date = self._parse_date(c.get('issue_date'))
                    instance.international_medical_expiry_date = self._parse_date(c.get('expiry_date'))
                    instance.health_issued_by = c.get('issued_by', instance.health_issued_by)
                    instance.health_issued_at = c.get('issued_at', instance.health_issued_at)
                elif 'yellow fever' in fs_lower:
                    instance.yellow_fever_number = c.get('number', instance.yellow_fever_number)
                    instance.yellow_fever_issue_date = self._parse_date(c.get('issue_date'))
                    instance.yellow_fever_expiry_date = self._parse_date(c.get('expiry_date'))
                elif 'cholera' in fs_lower:
                    instance.cholera_number = c.get('number', instance.cholera_number)
                    instance.cholera_issue_date = self._parse_date(c.get('issue_date'))
                    instance.cholera_expiry_date = self._parse_date(c.get('expiry_date'))
                
                # Save to Vaccination model
                Vaccination.objects.create(
                    user=instance,
                    name=f_state,
                    number=c.get('number', ''),
                    issue_date=self._parse_date(c.get('issue_date')),
                    expiry_date=self._parse_date(c.get('expiry_date')),
                    issued_by=c.get('issued_by', ''),
                    issued_at=c.get('issued_at', ''),
                    first_date=self._parse_date(c.get('first_dose')),
                    last_date=self._parse_date(c.get('last_dose')),
                    remarks=c.get('remarks', '')
                )
            
            covid = health.get('covid_19', {})
            if covid:
                instance.covid_vaccine_name = covid.get('vaccination_name', instance.covid_vaccine_name)
                instance.covid_first_dose = self._parse_date(covid.get('first_dose'))
                instance.covid_second_dose = self._parse_date(covid.get('second_dose'))
                instance.covid_other_doses_or_remarks = covid.get('other_does_or_remarks', instance.covid_other_doses_or_remarks)

        # Save main instance
        instance.save()

        # Handle Related models (Delete and Recreate pattern)
        # 8. Marine Courses
        courses_data = validated_data.get('marine_courses', [])
        if courses_data:
            instance.courses.all().delete()
            for c in courses_data:
                Course.objects.create(
                    user=instance,
                    course_name=c.get('course_name', ''),
                    course_number=c.get('number', ''),
                    issue_date=self._parse_date(c.get('issue_date')),
                    expiry_date=self._parse_date(c.get('expiry_date')),
                    issued_by=c.get('issued_by', ''),
                    issued_at=c.get('issued_at', '')
                )

        # 9. Sea Service
        sea_service_data = validated_data.get('sea_service_details', {})
        if sea_service_data:
            records = sea_service_data.get('service_records', [])
            if records:
                instance.sea_services.all().delete()
                for r in records:
                    SeaService.objects.create(
                        user=instance,
                        company_name=r.get('company_name', ''),
                        rank=r.get('rank', ''),
                        vessel_name=r.get('vessel_name_imo_number', '').split('/')[0].strip() if '/' in r.get('vessel_name_imo_number', '') else r.get('vessel_name_imo_number', ''),
                        imo_number=r.get('vessel_name_imo_number', '').split('/')[1].strip() if '/' in r.get('vessel_name_imo_number', '') else '',
                        flag=r.get('flag', ''),
                        signed_on=self._parse_date(r.get('signed_on')),
                        signed_off=self._parse_date(r.get('signed_off')),
                        period=r.get('period', ''),
                        vessel_type=r.get('vessel_type', ''),
                        dwt=r.get('dwt_grt', '').split('/')[0].strip() if '/' in r.get('dwt_grt', '') else r.get('dwt_grt', ''),
                        grt=r.get('dwt_grt', '').split('/')[1].strip() if '/' in r.get('dwt_grt', '') else '',
                        engine_type=r.get('engine_type', ''),
                        bh=r.get('bh_kw', '').split('/')[0].strip() if '/' in r.get('bh_kw', '') else r.get('bh_kw', ''),
                        kw=r.get('bh_kw', '').split('/')[1].strip() if '/' in r.get('bh_kw', '') else '',
                        reason_for_sign_off=r.get('reason_for_sign_off', '')
                    )

        # 10. References
        refs_data = validated_data.get('references', [])
        if refs_data:
            instance.references.all().delete()
            for r in refs_data:
                Reference.objects.create(
                    user=instance,
                    company_name=r.get('company_management_country', ''),
                    position=r.get('position', ''),
                    name=r.get('name', ''),
                    tel=r.get('tel', ''),
                    email=r.get('email', '')
                )

        # 11. Declaration
        decl = validated_data.get('declaration', {})
        if decl:
            qs = decl.get('questions', {})
            suffer_disease = qs.get('suffer_disease_unfit_for_sea', {})
            addicted = qs.get('addicted_to_alcohol_or_drugs', {})
            accident = qs.get('suffer_accident_disabled', {})
            psychiatric = qs.get('undergo_psychiatric_treatment', {})

            disease_ans = suffer_disease.get('answer', 'NO') == 'YES'
            disease_det = suffer_disease.get('details', '')
            addicted_ans = addicted.get('answer', 'NO') == 'YES'
            addicted_det = addicted.get('details', '')
            accident_ans = accident.get('answer', 'NO') == 'YES'
            accident_det = accident.get('details', '')
            psychiatric_ans = psychiatric.get('answer', 'NO') == 'YES'
            psychiatric_det = psychiatric.get('details', '')

            place = decl.get('place', '')
            date_val = self._parse_date(decl.get('date'))

            # Update User instance directly
            instance.disease_history = disease_det if disease_ans else ''
            instance.addiction_history = addicted_det if addicted_ans else ''
            instance.accident_history = accident_det if accident_ans else ''
            instance.psychiatric_treatment_history = psychiatric_det if psychiatric_ans else ''
            instance.declaration_place = place
            instance.declaration_date = date_val

            # Also create/update a Declaration model record to ensure database integrity
            from api.models import Declaration
            Declaration.objects.update_or_create(
                user=instance,
                defaults={
                    'has_disease': disease_ans,
                    'disease_details': disease_det,
                    'has_accident': accident_ans,
                    'accident_details': accident_det,
                    'has_psychiatric_treatment': psychiatric_ans,
                    'psychiatric_treatment_details': psychiatric_det,
                    'has_addiction': addicted_ans,
                    'addiction_details': addicted_det,
                    'consent_given': True,
                    'declaration_place': place,
                    'declaration_date': date_val
                }
            )

        # 12. Office Use
        office = validated_data.get('for_office_use_only', {})
        if office:
            instance.initial_assessment_comments = office.get('comments', instance.initial_assessment_comments)
            resp = office.get('responsible_person', {})
            if resp:
                instance.responsible_person_name = resp.get('name_signature', instance.responsible_person_name)
                instance.assessment_date = self._parse_date(resp.get('date'))

        instance.save()
        return instance

    def create(self, validated_data):
        # Generate a unique email if not provided
        if 'email' not in validated_data:
            import random
            import string
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            validated_data['email'] = f"temp_{random_str}@example.com"
        
        if 'first_name' not in validated_data:
            validated_data['first_name'] = "New Seafarer"

        instance = Users.objects.create(
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            middle_name=validated_data.get('middle_name', ''),
            role='Employee'
        )
        return self.update(instance, validated_data)

    def get_document_info(self, obj):
        return {
            "agency_name": "SAKR MANNING AGENCY",
            "description": "FOR RECRUITING EGYPTIAN LABOR ABROAD",
            "manual_name": "Crewing Management Manual",
            "form_name": "Seafarer Employment Application",
            "revision": "13",
            "page": "4"
        }

    def get_application_header(self, obj):
        return {
            "issue_date": obj.register_date if obj.register_date else "",
            "revision_date": obj.updated_at.strftime("%Y-%m-%d") if obj.updated_at else "",
            "application_for_position_as": obj.application_for_position if obj.application_for_position else "",
            "register_code": obj.register_code if obj.register_code else "",
            "other_position_if_any": obj.other_position if obj.other_position else "",
            "register_date": obj.register_date if obj.register_date else "",
            "last_update_data": obj.last_updated_date.strftime("%Y-%m-%d %H:%M") if obj.last_updated_date else "",
            "expected_salary": obj.salary if obj.salary else "",
            "available_date": obj.available_date if obj.available_date else ""
        }

    def get_personal_details(self, obj):
        return {
            "full_name": f"{obj.first_name} {obj.middle_name}".strip(),
            "date_of_birth": obj.date_of_birth if obj.date_of_birth else "",
            "marital_status": {
                "single": obj.marital_status.upper() == "SINGLE" if obj.marital_status else False,
                "married": obj.marital_status.upper() == "MARRIED" if obj.marital_status else False
            },
            "nationality": obj.nationality if obj.nationality else "",
            "height_cm": obj.Height_Cm if obj.Height_Cm else "",
            "weight_kg": obj.Weight_Kg if obj.Weight_Kg else "",
            "place_of_birth": obj.Place_Of_Birth if obj.Place_Of_Birth else "",
            "overall_size": obj.overall_size if obj.overall_size else "",
            "shirt_size": obj.shirt_size if obj.shirt_size else "",
            "nearest_port": obj.Nearest_Port if obj.Nearest_Port else "",
            "trouser_size": obj.trouser_size if obj.trouser_size else "",
            "shoes_size": obj.shoes_size if obj.shoes_size else ""
        }

    def get_education(self, obj):
        # Language breakdown helper
        def get_lang_breakdown(lang_name, level_field):
            level = (getattr(obj, level_field, "") or "").lower()
            return {
                "fluent": "fluent" in level or "native" in level,
                "good": "good" in level or "advanced" in level,
                "average": "average" in level or "intermediate" in level,
                "poor": "poor" in level or "elementary" in level
            }

        german_level = ""
        if obj.other_language and "german" in obj.other_language.lower():
            german_level = obj.other_language_level or ""

        return {
            "college_school": obj.college_or_school if obj.college_or_school else "",
            "marline_test": {
                "issued_date": obj.marlins_test_issued_date if obj.marlins_test_issued_date else "",
                "result_percentage": obj.marlins_test_result if obj.marlins_test_result else "",
                "issued_by_authority": obj.marlins_test_issued_by if obj.marlins_test_issued_by else "",
                "issued_at": obj.marlins_test_issued_at if obj.marlins_test_issued_at else ""
            },
            "english_language": get_lang_breakdown("English", "english_language_level"),
            "german_language": {
                "fluent": "fluent" in german_level.lower() or "native" in german_level.lower(),
                "good": "good" in german_level.lower() or "advanced" in german_level.lower(),
                "average": "average" in german_level.lower() or "intermediate" in german_level.lower(),
                "poor": "poor" in german_level.lower() or "elementary" in german_level.lower()
            }
        }

    def get_contact_details(self, obj):
        return {
            "home_address_city": f"{obj.address}, {obj.city}" if obj.address and obj.city else (obj.address or obj.city or ""),
            "e_mail": obj.email,
            "mobile_tel": obj.phone_number
        }

    def get_travel_documents(self, obj):
        docs = []
        if obj.passport_no:
            docs.append({
                "type": "Passport",
                "document_no": obj.passport_no,
                "iss_date": obj.passport_issue_date if obj.passport_issue_date else "",
                "exp_date": obj.passport_expiry_date if obj.passport_expiry_date else "",
                "iss_by_authority": obj.passport_issued_by if obj.passport_issued_by else "",
                "place_of_issue": obj.passport_place_of_issue if obj.passport_place_of_issue else "",
                "file_url": obj.passport_attachment.url if obj.passport_attachment else None
            })
        else:
            docs.append({"type": "Passport", "document_no": "", "iss_date": "", "exp_date": "", "iss_by_authority": "", "place_of_issue": "", "file_url": None})

        if obj.seaman_book_no:
            docs.append({
                "type": "Seaman Book",
                "document_no": obj.seaman_book_no,
                "iss_date": obj.seaman_book_issue_date if obj.seaman_book_issue_date else "",
                "exp_date": obj.seaman_book_expiry_date if obj.seaman_book_expiry_date else "",
                "iss_by_authority": obj.seaman_book_issued_by if obj.seaman_book_issued_by else "",
                "place_of_issue": obj.seaman_book_place_of_issue if obj.seaman_book_place_of_issue else "",
                "file_url": obj.seaman_book_attachment.url if obj.seaman_book_attachment else None
            })
        else:
            docs.append({"type": "Seaman Book", "document_no": "", "iss_date": "", "exp_date": "", "iss_by_authority": "", "place_of_issue": "", "file_url": None})

        if obj.other_seaman_book_no:
            docs.append({
                "type": "Other Seaman Book",
                "document_no": obj.other_seaman_book_no,
                "iss_date": obj.other_seaman_book_issue_date if obj.other_seaman_book_issue_date else "",
                "exp_date": obj.other_seaman_book_expiry_date if obj.other_seaman_book_expiry_date else "",
                "iss_by_authority": obj.other_seaman_book_issued_by if obj.other_seaman_book_issued_by else "",
                "place_of_issue": obj.other_seaman_book_place_of_issue if obj.other_seaman_book_place_of_issue else "",
                "file_url": obj.other_seaman_book_attachment.url if obj.other_seaman_book_attachment else None
            })
        else:
            docs.append({"type": "Other Seaman Book", "document_no": "", "iss_date": "", "exp_date": "", "iss_by_authority": "", "place_of_issue": "", "file_url": None})
            
        # Append PersonalDocument records (Visas, IDs, etc.)
        for pd in obj.personal_documents.all():
            docs.append({
                "id": pd.id,
                "type": pd.document_type,
                "document_no": pd.document_number if pd.document_number else "",
                "iss_date": pd.issue_date if pd.issue_date else "",
                "exp_date": pd.expiry_date if pd.expiry_date else "",
                "iss_by_authority": pd.issued_by if pd.issued_by else "",
                "place_of_issue": pd.place_of_issue if pd.place_of_issue else "",
                "issuing_country": pd.issuing_country if pd.issuing_country else "",
                "file_url": pd.file.url if pd.file else None
            })
            
        return docs

    def get_professional_qualification(self, obj):
        return [
            {
                "certificate_name": f"COC ({obj.coc_certificate_name or 'Rank'})",
                "number": obj.coc_certificate_number if obj.coc_certificate_number else "",
                "issue_date": obj.coc_issue_date if obj.coc_issue_date else "",
                "expiry_date": obj.coc_expiry_date if obj.coc_expiry_date else "",
                "issued_by": obj.coc_issued_by if obj.coc_issued_by else "",
                "issued_at": obj.coc_issued_at if obj.coc_issued_at else ""
            },
            {
                "certificate_name": "GOC",
                "number": obj.goc_certificate_number if obj.goc_certificate_number else "",
                "issue_date": obj.goc_issue_date if obj.goc_issue_date else "",
                "expiry_date": obj.goc_expiry_date if obj.goc_expiry_date else "",
                "issued_by": obj.goc_issued_by if obj.goc_issued_by else "",
                "issued_at": obj.goc_issued_at if obj.goc_issued_at else ""
            }
        ]

    def get_next_of_kin(self, obj):
        # Fallback logic for Next of Kin
        full_name = obj.next_of_kin_full_name
        rel = obj.next_of_kin_relationship
        addr = obj.next_of_kin_address_country
        phone = obj.next_of_kin_phone
        email = obj.next_of_kin_email

        # Try related model if Users fields are empty
        if not full_name:
            nok = obj.next_of_kins.first()
            if nok:
                full_name = nok.full_name
                rel = nok.relationship
                addr = nok.address_country
                phone = nok.phone
                email = nok.email

        return {
            "full_name": full_name or "",
            "address_country": addr or "",
            "tel_no_mobile": phone or "",
            "relationship": rel or "",
            "email": email or ""
        }

    def get_health_certificates(self, obj):
        vaccs = obj.vaccinations.all()
        certs = []
        for v in vaccs:
            certs.append({
                "flag_state": v.name,
                "number": v.number or "",
                "issue_date": v.issue_date or "",
                "expiry_date": v.expiry_date or "",
                "issued_by": v.issued_by or "",
                "issued_at": v.issued_at or "",
                "first_dose": v.first_date or "",
                "last_dose": v.last_date or "",
                "remarks": v.remarks or ""
            })

        return {
            "certificates": certs,
            "covid_19": {
                "vaccination_name": obj.covid_vaccine_name or "",
                "first_dose": obj.covid_first_dose or "",
                "second_dose": obj.covid_second_dose or "",
                "other_does_or_remarks": obj.covid_other_doses_or_remarks or ""
            }
        }

    def get_marine_courses(self, obj):
        courses = obj.courses.all()
        result = []
        for c in courses:
            result.append({
                "course_name": c.course_name,
                "number": c.course_number,
                "issue_date": c.issue_date if c.issue_date else "",
                "expiry_date": c.expiry_date if c.expiry_date else "",
                "issued_by": c.issued_by or "",
                "issued_at": c.issued_at or ""
            })
        return result

    def get_sea_service_details(self, obj):
        from core.models import Flag, VesselType
        from api.models import Rank

        services = obj.sea_services.all()
        records = []
        for s in services:
            # Resolve rank_name
            rank_name = ""
            if s.rank:
                if s.rank.isdigit():
                    rank_obj = Rank.objects.filter(id=int(s.rank)).first()
                    rank_name = rank_obj.name if rank_obj else s.rank
                else:
                    rank_name = s.rank

            # Resolve flag_name
            flag_name = ""
            if s.flag:
                if s.flag.isdigit():
                    flag_obj = Flag.objects.filter(id=int(s.flag)).first()
                    flag_name = flag_obj.name if flag_obj else s.flag
                else:
                    flag_name = s.flag

            # Resolve vessel_type_name
            vessel_type_name = ""
            if s.vessel_type:
                if s.vessel_type.isdigit():
                    vt_obj = VesselType.objects.filter(id=int(s.vessel_type)).first()
                    vessel_type_name = vt_obj.name if vt_obj else s.vessel_type
                else:
                    vessel_type_name = s.vessel_type

            records.append({
                "company_name": s.company_name,
                "rank": rank_name,
                "rank_name": rank_name,
                "vessel_name_imo_number": f"{s.vessel_name} / {s.imo_number}".strip(" / "),
                "flag": flag_name,
                "flag_name": flag_name,
                "signed_on": s.signed_on if s.signed_on else "",
                "signed_off": s.signed_off if s.signed_off else "",
                "period": s.period,
                "vessel_type": vessel_type_name,
                "vessel_type_name": vessel_type_name,
                "dwt_grt": f"{s.dwt} / {s.grt}".strip(" / "),
                "engine_type": s.engine_type,
                "bh_kw": f"{s.bh} / {s.kw}".strip(" / "),
                "reason_for_sign_off": s.reason_for_sign_off
            })
        return {
            "applicant_info": {
                "name": f"{obj.first_name} {obj.middle_name}".strip(),
                "rank": obj.application_for_position if obj.application_for_position else "",
                "register_code": obj.register_code if obj.register_code else ""
            },
            "service_records": records
        }

    def get_references(self, obj):
        refs = obj.references.all()
        result = []
        for i, r in enumerate(refs):
            result.append({
                "no": str(i+1),
                "company_management_country": r.company_name,
                "position": r.position,
                "name": r.name,
                "tel": r.tel,
                "email": r.email
            })
        return result

    def get_declaration(self, obj):
        # Fallback fields on User model:
        disease_ans = True if obj.disease_history else False
        disease_det = obj.disease_history or ""
        addicted_ans = True if obj.addiction_history else False
        addicted_det = obj.addiction_history or ""
        accident_ans = True if obj.accident_history else False
        accident_det = obj.accident_history or ""
        psychiatric_ans = True if obj.psychiatric_treatment_history else False
        psychiatric_det = obj.psychiatric_treatment_history or ""
        place = obj.declaration_place or ""
        date = obj.declaration_date

        # Check if the user has a linked Declaration model record (take the latest one)
        latest_decl = obj.declarations.order_by('-created_at').first()
        if latest_decl:
            disease_ans = latest_decl.has_disease
            disease_det = latest_decl.disease_details or ""
            addicted_ans = latest_decl.has_addiction
            addicted_det = latest_decl.addiction_details or ""
            accident_ans = latest_decl.has_accident
            accident_det = latest_decl.accident_details or ""
            psychiatric_ans = latest_decl.has_psychiatric_treatment
            psychiatric_det = latest_decl.psychiatric_treatment_details or ""
            place = latest_decl.declaration_place or ""
            date = latest_decl.declaration_date

        import datetime
        date_str = ""
        if date:
            if isinstance(date, (datetime.date, datetime.datetime)):
                date_str = date.strftime('%Y-%m-%d')
            else:
                date_str = str(date)

        return {
            "questions": {
                "suffer_disease_unfit_for_sea": {"answer": "YES" if disease_ans else "NO", "details": disease_det},
                "addicted_to_alcohol_or_drugs": {"answer": "YES" if addicted_ans else "NO", "details": addicted_det},
                "suffer_accident_disabled": {"answer": "YES" if accident_ans else "NO", "details": accident_det},
                "undergo_psychiatric_treatment": {"answer": "YES" if psychiatric_ans else "NO", "details": psychiatric_det}
            },
            "consent_statement": "I hereby declare that the above facts and information are true and accurate...",
            "place": place,
            "date": date_str,
            "signature": ""
        }

    def get_for_office_use_only(self, obj):
        return {
            "initial_assessment_of_applicant": "",
            "comments": obj.initial_assessment_comments if obj.initial_assessment_comments else "",
            "responsible_person": {
                "name_signature": obj.responsible_person_name if obj.responsible_person_name else "",
                "date": obj.assessment_date if obj.assessment_date else ""
            }
        }
