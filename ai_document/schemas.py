"""
Pydantic schemas matching the seafarer_application format exactly.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any


# ── Section 1: Personal Details ───────────────────────────────────────────────

class MaritalStatus(BaseModel):
    single: bool = False
    married: bool = False


class PersonalDetails(BaseModel):
    full_name: Optional[str] = ""
    date_of_birth: Optional[str] = ""
    marital_status: MaritalStatus = Field(default_factory=MaritalStatus)
    nationality: Optional[str] = ""
    height_cm: Optional[Any] = None
    weight_kg: Optional[Any] = None
    place_of_birth: Optional[str] = ""
    overall_size: Optional[str] = ""
    shirt_size: Optional[str] = ""
    nearest_port: Optional[str] = ""
    trouser_size: Optional[str] = ""
    shoes_size: Optional[str] = ""


# ── Section 2: Education ──────────────────────────────────────────────────────

class MarlineTest(BaseModel):
    issued_date: Optional[str] = ""
    result_percentage: Optional[str] = ""
    issued_by_authority: Optional[str] = ""
    issued_at: Optional[str] = ""


class LanguageLevel(BaseModel):
    fluent: bool = False
    good: bool = False
    average: bool = False
    poor: bool = False


class Education(BaseModel):
    college_school: Optional[str] = ""
    marline_test: MarlineTest = Field(default_factory=MarlineTest)
    english_language: LanguageLevel = Field(default_factory=LanguageLevel)
    german_language: LanguageLevel = Field(default_factory=LanguageLevel)


# ── Section 3: Contact Details ────────────────────────────────────────────────

class ContactDetails(BaseModel):
    home_address_city: Optional[str] = ""
    e_mail: Optional[str] = ""
    mobile_tel: Optional[str] = ""


# ── Section 4: Travel Documents ───────────────────────────────────────────────

class TravelDocument(BaseModel):
    type: Optional[str] = ""
    document_no: Optional[str] = ""
    iss_date: Optional[str] = ""
    exp_date: Optional[str] = ""
    iss_by_authority: Optional[str] = ""
    place_of_issue: Optional[str] = ""


# ── Section 5: Professional Qualifications ────────────────────────────────────

class ProfessionalQualification(BaseModel):
    certificate_name: Optional[str] = ""
    number: Optional[str] = ""
    issue_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    issued_by: Optional[str] = ""
    issued_at: Optional[str] = ""


# ── Section 6: Next of Kin ────────────────────────────────────────────────────

class NextOfKin(BaseModel):
    full_name: Optional[str] = ""
    address_country: Optional[str] = ""
    tel_no_mobile: Optional[str] = ""
    relationship: Optional[str] = ""
    email: Optional[str] = ""


# ── Section 7: Health Certificates & Vaccinations ────────────────────────────

class HealthCertificate(BaseModel):
    flag_state: Optional[str] = ""
    number: Optional[str] = ""
    issue_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    issued_by: Optional[str] = ""
    issued_at: Optional[str] = ""


class Covid19(BaseModel):
    vaccination_name: Optional[str] = ""
    first_dose: Optional[str] = ""
    second_dose: Optional[str] = ""
    other_does_or_remarks: Optional[str] = ""


class HealthSection(BaseModel):
    certificates: List[HealthCertificate] = []
    covid_19: Covid19 = Field(default_factory=Covid19)


# ── Section 8: Marine Courses ─────────────────────────────────────────────────

class MarineCourse(BaseModel):
    course_name: Optional[str] = ""
    number: Optional[str] = ""
    issue_date: Optional[str] = ""
    expiry_date: Optional[str] = ""
    issued_by_at: Optional[str] = ""


# ── Section 9: Sea Service Details ───────────────────────────────────────────

class ApplicantInfo(BaseModel):
    name: Optional[str] = ""
    rank: Optional[str] = ""
    register_code: Optional[str] = ""


class ServiceRecord(BaseModel):
    company_name: Optional[str] = ""
    rank: Optional[str] = ""
    vessel_name_imo_number: Optional[str] = ""
    flag: Optional[str] = ""
    signed_on: Optional[str] = ""
    signed_off: Optional[str] = ""
    period: Optional[str] = ""
    vessel_type: Optional[str] = ""
    dwt_grt: Optional[str] = ""
    engine_type: Optional[str] = ""
    bh_kw: Optional[str] = ""
    reason_for_sign_off: Optional[str] = ""


class SeaServiceSection(BaseModel):
    applicant_info: ApplicantInfo = Field(default_factory=ApplicantInfo)
    service_records: List[ServiceRecord] = []


# ── Section 10: References ────────────────────────────────────────────────────

class Reference(BaseModel):
    no: Optional[str] = ""
    company_management_country: Optional[str] = ""
    position: Optional[str] = ""
    name: Optional[str] = ""
    tel: Optional[str] = ""
    email: Optional[str] = ""


# ── Section 11: Declaration ───────────────────────────────────────────────────

class DeclarationAnswer(BaseModel):
    answer: Optional[str] = "NO"
    details: Optional[str] = ""


class DeclarationQuestions(BaseModel):
    suffer_disease_unfit_for_sea: DeclarationAnswer = Field(default_factory=DeclarationAnswer)
    addicted_to_alcohol_or_drugs: DeclarationAnswer = Field(default_factory=DeclarationAnswer)
    suffer_accident_disabled: DeclarationAnswer = Field(default_factory=DeclarationAnswer)
    undergo_psychiatric_treatment: DeclarationAnswer = Field(default_factory=DeclarationAnswer)


class Declaration(BaseModel):
    questions: DeclarationQuestions = Field(default_factory=DeclarationQuestions)
    consent_statement: Optional[str] = ""
    place: Optional[str] = ""
    date: Optional[str] = ""
    signature: Optional[str] = ""


# ── Section 12: Office Use Only ───────────────────────────────────────────────

class ResponsiblePerson(BaseModel):
    name_signature: Optional[str] = ""
    date: Optional[str] = ""


class OfficeUseOnly(BaseModel):
    initial_assessment_of_applicant: Optional[str] = ""
    comments: Optional[str] = ""
    responsible_person: ResponsiblePerson = Field(default_factory=ResponsiblePerson)


# ── Root: Seafarer Application ────────────────────────────────────────────────

class SeafarerApplication(BaseModel):
    field_1_personal_details: PersonalDetails = Field(
        default_factory=PersonalDetails,
        alias="1_personal_details"
    )
    field_2_education: Education = Field(
        default_factory=Education,
        alias="2_education"
    )
    field_3_contact_details: ContactDetails = Field(
        default_factory=ContactDetails,
        alias="3_contact_details"
    )
    field_4_travel_documents: List[TravelDocument] = Field(
        default_factory=list,
        alias="4_travel_documents"
    )
    field_5_professional_qualifications: List[ProfessionalQualification] = Field(
        default_factory=list,
        alias="5_professional_qualification_certificate_of_competency"
    )
    field_6_next_of_kin: NextOfKin = Field(
        default_factory=NextOfKin,
        alias="6_next_of_kin_emergency_contact"
    )
    field_7_health: HealthSection = Field(
        default_factory=HealthSection,
        alias="7_health_certificates_and_vaccinations"
    )
    field_8_marine_courses: List[MarineCourse] = Field(
        default_factory=list,
        alias="8_marine_courses"
    )
    field_9_sea_service: SeaServiceSection = Field(
        default_factory=SeaServiceSection,
        alias="9_complete_sea_service_details"
    )
    field_10_references: List[Reference] = Field(
        default_factory=list,
        alias="10_references"
    )
    field_11_declaration: Declaration = Field(
        default_factory=Declaration,
        alias="11_declaration"
    )
    field_12_office_use: OfficeUseOnly = Field(
        default_factory=OfficeUseOnly,
        alias="12_for_office_use_only"
    )

    model_config = {"populate_by_name": True}

    def to_numbered_dict(self) -> dict:
        """Export with the numbered key names (e.g. '1_personal_details')."""
        return {
            "1_personal_details": self.field_1_personal_details.model_dump(),
            "2_education": self.field_2_education.model_dump(),
            "3_contact_details": self.field_3_contact_details.model_dump(),
            "4_travel_documents": [d.model_dump() for d in self.field_4_travel_documents],
            "5_professional_qualification_certificate_of_competency": [
                q.model_dump() for q in self.field_5_professional_qualifications
            ],
            "6_next_of_kin_emergency_contact": self.field_6_next_of_kin.model_dump(),
            "7_health_certificates_and_vaccinations": self.field_7_health.model_dump(),
            "8_marine_courses": [c.model_dump() for c in self.field_8_marine_courses],
            "9_complete_sea_service_details": self.field_9_sea_service.model_dump(),
            "10_references": [r.model_dump() for r in self.field_10_references],
            "11_declaration": self.field_11_declaration.model_dump(),
            "12_for_office_use_only": self.field_12_office_use.model_dump(),
        }
