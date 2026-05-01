# Form Fields Audit & Backend Mapping Analysis

## Overview
This document provides a comprehensive audit of all input fields in the frontend application (both static inline fields and modal fields) compared against the backend user model.

**Legend:**
- ✅ **Mapped**: Field exists in frontend and is correctly mapped to backend.
- ⚠️ **Partial/Mismatch**: Field exists but has naming or logic discrepancies.
- ❌ **Unutilized**: Backend field exists but has NO corresponding frontend input.
- 🆕 **Frontend Only**: Input exists in frontend but may not be persisted or mapped to a specific backend field.

---

## 1. Position & Personal (Step 0)
**Component:** `PositionPersonalForm.jsx`

| Frontend Label | Frontend Field | Backend Field | Status | Notes |
|---|---|---|---|---|
| Application Position | `application_for_position` | `application_for_position` | ✅ | |
| Other Position | `other_position` | `other_position` | ✅ | |
| Register Code | `register_code` | `register_code` | ✅ | |
| Last Update Date | `last_update_date` | `last_update_date` | ✅ | |
| Register Date | `register_date` | `register_date` | ✅ | |
| Available Date | `available_date` | `available_date` | ✅ | |
| Expected Salary | `expected_salary` | `salary` | ✅ | Mapped via `formMapper` |
| Full Name | `full_name` | `first_name`, `middle_name`, `last_name` | ✅ | Split logic in mapper |
| Nationality | `nationality` | `nationality` | ✅ | |
| Place of Birth | `place_of_birth` | `Place_Of_Birth` | ✅ | Backend uses PascalCase |
| Date of Birth | `date_of_birth` | `date_of_birth` | ✅ | |
| Nearest Airport | `nearest_port` | `Nearest_Port` | ✅ | Backend uses PascalCase |
| Marital Status | `marital_status` | `marital_status` | ✅ | |
| Weight (Kg) | `weight` | `Weight_Kg` | ✅ | Backend uses PascalCase |
| Height (Cm) | `height` | `Height_Cm` | ✅ | Backend uses PascalCase |
| Overall Size | `overall_size` | `overall_size` | ✅ | |
| Shirt Size | `shirt_size` | `shirt_size` | ✅ | |
| Trouser Size | `trouser_size` | `trouser_size` | ✅ | |
| Shoes Size | `shoes_size` | `shoes_size` | ✅ | |
| **Unutilized Backend Fields** | - | `user_status` | ❌ | No input field |
| | - | `profile_image` | ❌ | Handled via separate upload logic? |

---

## 2. Education (Step 1)
**Component:** `EducationForm.jsx`

| Frontend Label | Frontend Field | Backend Field | Status | Notes |
|---|---|---|---|---|
| College / School | `education_school` | `college_or_school` | ✅ | Mapped via `formMapper` |
| English Level | `english_level` | `english_language_level` | ✅ | Mapped via `formMapper` |
| Other Language | `other_language` | `other_language` | ✅ | |
| Other Lang Level | `other_language_level` | `other_language_level` | ✅ | |
| **Marlins Test** | | | | |
| Issued Date | `marine_issued_date` | `marlins_test_issued_date` | ✅ | |
| Result % | `marine_result` | `marlins_test_result` | ✅ | |
| Issued By | `marine_issued_by` | `marlins_test_issued_by` | ✅ | |
| Issued At | `marine_issued_at` | `marlins_test_issued_at` | ✅ | |
| **CES Test** | | | | |
| Result | `ces_test_result` | `ces_test_result` | ✅ | Moved here from Certs step |
| Issued Date | `ces_test_issued_date` | `ces_test_issued_date` | ✅ | |
| Issued By | `ces_test_issued_by` | `ces_test_issued_by` | ✅ | |
| Issued At | `ces_test_issued_at` | `ces_test_issued_at` | ✅ | |

---

## 3. Contact (Step 2)
**Component:** `ContactForm.jsx`

| Frontend Label | Frontend Field | Backend Field | Status | Notes |
|---|---|---|---|---|
| Address | `address` | `address` (also `home_address`) | ✅ | Mapper handles both |
| Email | `email` | `email` | ✅ | |
| Mobile | `mobile` | `phone_number` | ✅ | Combined with code in mapper |
| **Unutilized Backend Fields** | - | `tel_number` | ❌ | No input (only mobile used) |
| | - | `city` | ❌ | No specific city input |
| | - | `country` | ❌ | No specific country input |

---

## 4. Emergency (Step 3)
**Component:** `EmergencyForm.jsx`

| Frontend Label | Frontend Field | Backend Field | Status | Notes |
|---|---|---|---|---|
| Full Name | `kin_full_name` | `next_of_kin_full_name` | ✅ | |
| Relationship | `kin_relationship` | `next_of_kin_relationship` | ✅ | |
| Address/Country | `kin_address` | `next_of_kin_address_country` | ✅ | |
| Phone | `kin_phone` | `next_of_kin_phone` | ✅ | |
| Email | `kin_email` | `next_of_kin_email` | ✅ | |

---

## 5. Documents (Step 4)
**Component:** `DocumentsForm.jsx` & `DocumentModal.jsx`

### Static Fields (New)
| Frontend Label | Frontend Field | Backend Field | Status | Notes |
|---|---|---|---|---|
| **Passport** | | | | |
| Number | `passport_no` | `passport_no` | ✅ | Added recently |
| Issue Date | `passport_issue_date` | `passport_issue_date` | ✅ | Added recently |
| Expiry Date | `passport_expiry_date` | `passport_expiry_date` | ✅ | Added recently |
| Issued By | `passport_issued_by` | `passport_issued_by` | ✅ | Added recently |
| Place of Issue | `passport_place_of_issue` | `passport_place_of_issue` | ✅ | Added recently |
| **Seaman Book** | | | | |
| Number | `seaman_book_no` | `seaman_book_no` | ✅ | Added recently |
| Issue Date | `seaman_book_issue_date` | `seaman_book_issue_date` | ✅ | Added recently |
| Expiry Date | `seaman_book_expiry_date` | `seaman_book_expiry_date` | ✅ | Added recently |
| Issued By | `seaman_book_issued_by` | `seaman_book_issued_by` | ✅ | Added recently |
| Place of Issue | `seaman_book_place_of_issue` | `seaman_book_place_of_issue` | ✅ | Added recently |

### Modal Fields (Collection: `documents`)
| Label | Field | Backend Field | Status |
|---|---|---|---|
| Document Type | `document_type` | `document_type` | ✅ |
| Document No. | `document_number` | `document_number` | ✅ |
| Issue Date | `issue_date` | `issue_date` | ✅ |
| Expiry Date | `expiry_date` | `expiry_date` | ✅ |
| Issued By | `issuing_authority` | `issuing_authority` | ✅ |

---

## 6. Certificates (Step 5)
**Component:** `CertificatesForm.jsx` & `LicenseModal.jsx`

### Static Fields (New)
| Frontend Label | Frontend Field | Backend Field | Status | Notes |
|---|---|---|---|---|
| **COC** | | | | |
| Cert Name | `coc_certificate_name` | `coc_certificate_name` | ✅ | Added recently |
| Cert Number | `coc_certificate_number` | `coc_certificate_number` | ✅ | Added recently |
| Issue Date | `coc_issue_date` | `coc_issue_date` | ✅ | Added recently |
| Expiry Date | `coc_expiry_date` | `coc_expiry_date` | ✅ | Added recently |
| Issued At | `coc_issued_at` | `coc_issued_at` | ✅ | Added recently |
| Issued By | `coc_issued_by` | `coc_issued_by` | ✅ | Added recently |
| **GOC** | | | | |
| Cert Number | `goc_certificate_number` | `goc_certificate_number` | ✅ | Added recently |
| Issue Date | `goc_issue_date` | `goc_issue_date` | ✅ | Added recently |
| Expiry Date | `goc_expiry_date` | `goc_expiry_date` | ✅ | Added recently |
| Issued At | `goc_issued_at` | `goc_issued_at` | ✅ | Added recently |
| Issued By | `goc_issued_by` | `goc_issued_by` | ✅ | Added recently |

### Modal Fields (Collection: `licenses` / `certificates`)
| Label | Field | Backend Field | Status |
|---|---|---|---|
| Cert Name | `document_name` | `document_name` | ✅ |
| Number | `document_number` | `document_number` | ✅ |
| Issue Date | `issue_date` | `issue_date` | ✅ |
| Expiry Date | `expiry_date` | `expiry_date` | ✅ |
| Country | `country_of_issue` | `country_of_issue` | ✅ |

---

## 7. Health (Step 6)
**Component:** `HealthForm.jsx` & `HealthModal.jsx`

### Static Fields (New)
| Frontend Label | Frontend Field | Backend Field | Status | Notes |
|---|---|---|---|---|
| **Health Cert** | | | | |
| Number | `health_number` | `health_number` | ✅ | Added recently |
| Issue Date | `health_issue_date` | `health_issue_date` | ✅ | Added recently |
| Expiry Date | `health_expiry_date` | `health_expiry_date` | ✅ | Added recently |
| Issued By | `health_issued_by` | `health_issued_by` | ✅ | Added recently |
| Issued At | `health_issued_at` | `health_issued_at` | ✅ | Added recently |
| Flag State | `health_flag_state` | `health_flag_state` | ✅ | Added recently |
| **Yellow Fever**| | | | |
| Number | `yellow_fever_number` | `yellow_fever_number` | ✅ | Added recently |
| Issue Date | `yellow_fever_issue_date` | `yellow_fever_issue_date` | ✅ | Added recently |
| Expiry Date | `yellow_fever_expiry_date`| `yellow_fever_expiry_date`| ✅ | Added recently |
| **Cholera** | | | | |
| Number | `cholera_number` | `cholera_number` | ✅ | Added recently |
| Issue Date | `cholera_issue_date` | `cholera_issue_date` | ✅ | Added recently |
| Expiry Date | `cholera_expiry_date` | `cholera_expiry_date` | ✅ | Added recently |
| **COVID** | | | | |
| Vaccine Name | `covid_vaccine_name` | `covid_vaccine_name` | ✅ | Added recently |
| First Dose | `covid_first_dose` | `covid_first_dose` | ✅ | Added recently |
| Second Dose | `covid_second_dose` | `covid_second_dose` | ✅ | Added recently |
| Remarks | `covid_other_doses_or_remarks`| `covid_other_doses_or_remarks`| ✅ | Added recently |
| **Int. Medical**| | | | |
| Number | `international_medical_number` | `international_medical_number` | ✅ | Added recently |
| Issue Date | `international_medical_issue_date`| `international_medical_issue_date`| ✅ | Added recently |
| Expiry Date | `international_medical_expiry_date`| `international_medical_expiry_date`| ✅ | Added recently |

### Modal Fields (Collection: `vaccinations` / `health`)
| Label | Field | Backend Field | Status |
|---|---|---|---|
| Vaccination | `name` | `name` | ✅ |
| Number | `number` | `number` | ✅ |
| Issue Date | `issue_date` | `issue_date` | ✅ |
| Expiry Date | `expiry_date` | `expiry_date` | ✅ |
| Issued By | `issued_by` | `issued_by` | ✅ |
| Issued At | `issued_at` | `issued_at` | ✅ |
| Disease | `disease` | `disease` | ✅ |
| First Dose | `first_date` | `first_date` | ✅ |
| Last Dose | `last_date` | `last_date` | ✅ |
| Remarks | `remarks` | `remarks` | ✅ |

---

## 8. Courses (Step 7)
**Component:** `CoursesForm.jsx` & `CourseModal.jsx`

### Modal Fields (Collection: `courses`)
| Label | Field | Backend Field | Status |
|---|---|---|---|
| Course Name | `course_name` | `course_name` | ✅ |
| Number | `course_number` | `course_number` | ✅ |
| Issue Date | `issue_date` | `issue_date` | ✅ |
| Expiry Date | `expiry_date` | `expiry_date` | ✅ |
| Issued By | `issued_by` | `issued_by` | ✅ |
| Issued At | `issued_at` | `issued_at` | ✅ |
| Country | `country_of_issue` | `country_of_issue` | ✅ |

---

## 9. Sea Service (Step 8)
**Component:** `SeaServiceForm.jsx` & `SeaServiceModal.jsx`

### Modal Fields (Collection: `sea_services`)
| Label | Field | Backend Field | Status |
|---|---|---|---|
| Company | `company_name` | `company_name` | ✅ |
| Rank | `rank` | `rank` | ✅ |
| Vessel/IMO | `vessel_name_imo` | `vessel_name_imo` | ✅ |
| Signed On | `signed_on` | `signed_on` | ✅ |
| Signed Off | `signed_off` | `signed_off` | ✅ |
| Flag | `flag` | `flag` | ✅ |
| Period | `period` | `period` | ✅ |
| Vessel Type | `vessel_type` | `vessel_type` | ✅ |
| DWT/GRT | `dwt_grt` | `dwt_grt` | ✅ |
| Engine Type | `engine_type_bh_kw` | `engine_type_bh_kw` | ✅ |
| Sign Off Reason| `reason_for_sign_off` | `reason_for_sign_off` | ✅ |

---

## 10. References (Step 10)
**Component:** `ReferencesForm.jsx` & `ReferenceModal.jsx`

> **Note:** Reference data maps to `field array` but backend endpoint is likely `/api/references/`. Confirm if this syncs via `userService.js`.

| Label | Field | Backend Field | Status |
|---|---|---|---|
| Number | `number` | `number` | ✅ |
| Company | `company_name` | `company_name` | ✅ |
| Management | `management` | `management` | ✅ |
| Country | `country` | `country` | ✅ |
| Position | `position` | `position` | ✅ |
| Name | `name` | `name` | ✅ |
| Email | `email` | `email` | ✅ |

---

## 11. Declaration (Step 11)
**Component:** `DeclarationForm.jsx`

| Frontend Field | Backend Field | Status | Notes |
|---|---|---|---|
| `has_psychiatric_treatment` | `has_psychiatric_treatment` | ✅ | |
| `psychiatric_treatment_details`| `psychiatric_treatment_details` | ✅ | |
| `has_addiction` | (Derived/Internal) | ⚠️ | Needs verification if backend persists this boolean |
| `addiction_details` | (Derived/Internal) | ⚠️ | |
| `consent_given` | (Derived/Internal) | ⚠️ | Usually strictly frontend validation |
| `declaration_place` | (Derived/Internal) | ⚠️ | |
| `declaration_date` | (Derived/Internal) | ⚠️ | |

---

## Unutilized / Missing Backend Fields

These fields are present in `BACKEND_FIELDS` (or implied by user model) but have **no frontend input**:

1. **User Status**: `user_status`
2. **VISA Status**: `schengen_visa_status`, `us_visa_status`
3. **Smoker**: `smoker`
4. **Blood Type**: `blood_type`
5. **Tel Number**: `tel_number` (Only mobile is used)
6. **City/Country**: `city`, `country` (Addresses are free text)

## Recommendations

1. **Add Missing Fields**: Add inputs for `blood_type`, `smoker`, `schengen_visa_status`, `us_visa_status` in **Step 0 (Personal)**.
2. **Verify References Sync**: Ensure `ReferencesForm` data is actually sent to the backend (check `userService.js` step 10).
3. **Verify Declaration**: Check if `declaration_place`, `declaration_date`, and `signature` need to be persisted to the backend.
