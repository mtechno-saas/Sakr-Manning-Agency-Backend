/**
 * utils/formMapper.js - SIMPLIFIED VERSION
 *
 * Strategy: Send EVERYTHING in one PATCH /api/users/{id}/ request
 * - Flat fields (name, email, etc.)
 * - CRUD arrays (documents, certificates, health, courses, seaServices and workExperiences)
 *
 * Backend will handle storing arrays appropriately
 */

import { format, isValid, parseISO } from "date-fns";
import { parsePhoneNumber } from "libphonenumber-js";

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

const toApiDate = (dateStr) => {
  if (!dateStr) return null;
  try {
    const date =
      typeof dateStr === "string" ? parseISO(dateStr) : new Date(dateStr);
    return isValid(date) ? format(date, "yyyy-MM-dd") : null;
  } catch {
    return null;
  }
};

const fromApiDate = (dateStr) => {
  if (!dateStr) return null;
  try {
    return parseISO(dateStr);
  } catch {
    return null;
  }
};

/**
 * Check if ID is temporary (client-generated)
 */
const isTemporaryId = (id) => {
  if (!id) return true;
  const idStr = String(id);
  return (
    idStr.startsWith("temp-") ||
    idStr.startsWith("doc-") ||
    idStr.startsWith("cert-") ||
    idStr.startsWith("health-") ||
    idStr.startsWith("course-") ||
    idStr.startsWith("sea-") ||
    idStr.startsWith("work-") ||
    idStr.startsWith("lang-") ||
    idStr.startsWith("lic-") ||
    idStr.startsWith("vac-") ||
    idStr.startsWith("nok-")
  );
};

const cleanId = (id) => {
  return isTemporaryId(id) ? null : id;
};

const parseName = (fullName) => {
  if (!fullName) return { first: "", middle: "", last: "" };
  const parts = fullName.trim().split(/\s+/);

  if (parts.length === 1) {
    return { first: parts[0], middle: "", last: "" };
  } else if (parts.length === 2) {
    return { first: parts[0], middle: "", last: parts[1] };
  } else {
    return {
      first: parts[0],
      middle: parts.slice(1, -1).join(" "),
      last: parts[parts.length - 1],
    };
  }
};

const calculateAge = (dateOfBirth) => {
  if (!dateOfBirth) return null;

  try {
    const birthDate = new Date(dateOfBirth);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }

    return age;
  } catch {
    return null;
  }
};

const extractPassportNo = (documents) => {
  if (!Array.isArray(documents)) return null;

  const passport = documents.find(
    (doc) => doc.document_type === "passport" || doc.type === "passport"
  );

  return passport?.document_number || passport?.documentNo || passport?.number || null;
};

// ============================================================================
// FRONTEND → BACKEND MAPPING (Single Payload)
// ============================================================================

/**
 * ✅ SIMPLIFIED: Map everything to a single user payload
 * Backend user model accepts nested arrays directly
 */
export const mapFormToBackend = (formData) => {
  if (!formData) return {};

  const nameParts = parseName(formData.full_name);

  // Combine phone number
  let phone_number = formData.mobile || formData.phone_number;
  try {
    if (formData.mobile && formData.mobile_code) {
      const parsed = parsePhoneNumber(formData.mobile, formData.mobile_code);
      if (parsed) {
        phone_number = parsed.number;
      }
    }
  } catch (error) {
    console.warn("Failed to parse phone number for backend:", error);
  }

  // Combine Next of Kin phone
  let next_of_kin_phone = formData.kin_phone;
  try {
    if (formData.kin_phone && formData.kin_phone_code) {
      const parsed = parsePhoneNumber(formData.kin_phone, formData.kin_phone_code);
      if (parsed) {
        next_of_kin_phone = parsed.number;
      }
    }
  } catch (error) {
    console.warn("Failed to parse kin phone number for backend:", error);
  }

  // Build complete payload with ALL data
  const payload = {
    // ===== BASIC INFO =====
    // first_name: formData.full_name || nameParts.first,
    first_name: formData.full_name,
    middle_name: nameParts.middle,
    last_name: nameParts.last,
    email: formData.email,
    phone_number: phone_number,
    profile_image: formData.profile_photo,

    // ===== FILE ATTACHMENTS =====
    marlins_test_attachment: formData.marlins_test_attachment,
    ces_test_attachment: formData.ces_test_attachment,

    // ===== PERSONAL =====
    date_of_birth: toApiDate(formData.date_of_birth),
    Place_Of_Birth: formData.place_of_birth,
    nationality: formData.nationality,
    passport_no: formData.passport_no || extractPassportNo(formData.documents),
    age: calculateAge(formData.date_of_birth),
    marital_status: formData.marital_status?.toUpperCase(),

    // ===== PHYSICAL =====
    Weight_Kg: formData.weight ? parseFloat(formData.weight) : null,
    Height_Cm: formData.height ? parseFloat(formData.height) : null,
    overall_size: formData.overall_size,
    shirt_size: formData.shirt_size,
    trouser_size: formData.trouser_size,
    shoes_size: formData.shoes_size,

    // ===== CONTACT =====
    address: formData.home_address || formData.address,

    // ===== NEXT OF KIN =====
    next_of_kin_full_name: formData.kin_full_name,
    next_of_kin_relationship: formData.kin_relationship,
    next_of_kin_phone: next_of_kin_phone,
    next_of_kin_email: formData.kin_email,
    next_of_kin_address_country: formData.kin_address,

    // ===== EDUCATION =====
    english_language_level: formData.english_level,
    other_language: formData.other_language,
    other_language_level: formData.other_language_level,
    college_or_school: formData.education_school,

    // ===== MARINE TEST =====
    marlins_test_issued_date: toApiDate(formData.marine_issued_date),
    marlins_test_result: formData.marine_result,
    marlins_test_issued_by: formData.marine_issued_by,
    marlins_test_issued_at: formData.marine_issued_at,

    // ===== POSITION =====
    application_for_position: formData.application_for_position,
    other_position: formData.other_position,
    last_update_date: toApiDate(formData.last_update_date),
    salary: [formData.expected_salary, formData.expected_salary_currency].filter(Boolean).join(' '),
    register_code: formData.register_code,
    register_date: toApiDate(formData.register_date),
    available_date: toApiDate(formData.available_date),
    Nearest_Port: formData.nearest_port,

    // ===== ARRAYS (using snake_case input arrays) =====
    vaccinations: Array.isArray(formData.health) ? formData.health : [],
    courses: Array.isArray(formData.courses) ? formData.courses : [],
    work_experience: Array.isArray(formData.work_experiences) ? formData.work_experiences : [],
    sea_services: Array.isArray(formData.sea_services) ? formData.sea_services.map(s => ({
      ...s,
      signed_on: toApiDate(s.signed_on),
      signed_off: toApiDate(s.signed_off),
    })) : [],
    documents: Array.isArray(formData.documents) ? formData.documents : [],
    certificates: Array.isArray(formData.certificates) ? formData.certificates : [],
    licenses: Array.isArray(formData.licenses) ? formData.licenses : [],
    languages: Array.isArray(formData.languages) ? formData.languages : [],
    references: Array.isArray(formData.references) ? formData.references : [],
    declaration: formData.declaration || null,
    next_of_kin: Array.isArray(formData.next_of_kin) ? formData.next_of_kin : [],

    // ===== NEW BACKEND FIELDS (Assuming these exist in backend) =====
    smoker: formData.smoker ?? false,
    blood_type: formData.blood_type || "",
    country: formData.country,
    city: formData.city,
    schengen_visa_status: formData.schengen_visa_status || "",
    us_visa_status: formData.us_visa_status || "",
    user_status: formData.user_status || "ON_SITE",
    tel_number: formData.tel_number,

    // Passports & Seaman Books (extra fields if not in documents array)
    passport_issue_date: toApiDate(formData.passport_issue_date),
    passport_expiry_date: toApiDate(formData.passport_expiry_date),
    passport_issued_by: formData.passport_issued_by,
    passport_place_of_issue: formData.passport_place_of_issue,

    seaman_book_no: formData.seaman_book_no,
    seaman_book_issue_date: toApiDate(formData.seaman_book_issue_date),
    seaman_book_expiry_date: toApiDate(formData.seaman_book_expiry_date),
    seaman_book_issued_by: formData.seaman_book_issued_by,
    seaman_book_place_of_issue: formData.seaman_book_place_of_issue,

    // ===== COC (Certificate of Competency) =====
    coc_certificate_name: formData.coc_certificate_name,
    coc_certificate_number: formData.coc_certificate_number,
    coc_issue_date: toApiDate(formData.coc_issue_date),
    coc_expiry_date: toApiDate(formData.coc_expiry_date),
    coc_issued_at: formData.coc_issued_at,
    coc_issued_by: formData.coc_issued_by,

    // ===== GOC (General Operator Certificate) =====
    goc_certificate_number: formData.goc_certificate_number,
    goc_issue_date: toApiDate(formData.goc_issue_date),
    goc_expiry_date: toApiDate(formData.goc_expiry_date),
    goc_issued_at: formData.goc_issued_at,
    goc_issued_by: formData.goc_issued_by,

    // ===== CES TEST =====
    ces_test_result: formData.ces_test_result,
    ces_test_issued_date: toApiDate(formData.ces_test_issued_date),
    ces_test_issued_by: formData.ces_test_issued_by,
    ces_test_issued_at: formData.ces_test_issued_at,

    // ===== YELLOW FEVER =====
    yellow_fever_number: formData.yellow_fever_number,
    yellow_fever_issue_date: toApiDate(formData.yellow_fever_issue_date),
    yellow_fever_expiry_date: toApiDate(formData.yellow_fever_expiry_date),

    // ===== CHOLERA =====
    cholera_number: formData.cholera_number,
    cholera_issue_date: toApiDate(formData.cholera_issue_date),
    cholera_expiry_date: toApiDate(formData.cholera_expiry_date),

    // ===== COVID =====
    covid_vaccine_name: formData.covid_vaccine_name,
    covid_first_dose: toApiDate(formData.covid_first_dose),
    covid_second_dose: toApiDate(formData.covid_second_dose),
    covid_other_doses_or_remarks: formData.covid_other_doses_or_remarks,

    // ===== INTERNATIONAL MEDICAL =====
    international_medical_number: formData.international_medical_number,
    international_medical_issue_date: toApiDate(formData.international_medical_issue_date),
    international_medical_expiry_date: toApiDate(formData.international_medical_expiry_date),

    // ===== HEALTH CERTIFICATE =====
    health_number: formData.health_number,
    health_issue_date: toApiDate(formData.health_issue_date),
    health_expiry_date: toApiDate(formData.health_expiry_date),
    health_issued_by: formData.health_issued_by,
    health_issued_at: formData.health_issued_at,
    health_flag_state: formData.health_flag_state,
  };

  // Clean up only undefined/null values
  // Keep empty strings (backend may need them for clearing fields)
  // Keep empty arrays (collection sync needs them to detect "delete all items")
  Object.keys(payload).forEach((key) => {
    if (payload[key] === undefined || payload[key] === null) {
      delete payload[key];
    }
  });

  return payload;
};

// ============================================================================
// BACKEND → FRONTEND MAPPING
// ============================================================================

/**
 * ✅ Map backend response to frontend form structure (snake_case)
 */
export const mapBackendToFrontend = (user) => {
  if (!user) return {};

  // Helper to safely parse arrays
  const parseArray = (field, fieldName) => {
    try {
      if (!field) return [];
      if (Array.isArray(field)) return field;
      if (typeof field === "string") return JSON.parse(field);
      return [];
    } catch (e) {
      console.error(`Failed to parse ${fieldName}:`, e);
      return [];
    }
  };

  const getArray = (originalKey, ...alternatives) => {
    let val = user[originalKey];
    if (!val) {
      for (const alt of alternatives) {
        if (user[alt]) {
          val = user[alt];
          break;
        }
      }
    }
    return parseArray(val, originalKey);
  };

  const healthRecords = getArray("health_records", "HealthRecords", "health", "vaccinations");
  const courses = getArray("courses", "Courses");
  const workExperience = getArray("work_experience", "WorkExperience", "workExperiences");
  const seaServices = getArray("sea_services", "SeaServices", "seaServices");
  const documents = getArray("documents", "Documents");
  const certificates = getArray("certificates", "Certificates");
  const licenses = getArray("licenses", "Licenses", "my_licenses");
  const languages = getArray("languages", "Languages", "my_languages");
  const references = getArray("references", "References");
  const nextOfKin = getArray("next_of_kin");

  // Parse Phone Number
  let mobile_code = "";
  let mobile = user.phone_number || "";
  try {
    if (user.phone_number) {
      const parsed = parsePhoneNumber(user.phone_number);
      if (parsed && parsed.country) {
        mobile_code = parsed.country; // e.g. "EG"
        mobile = parsed.nationalNumber;
      }
    }
  } catch (e) { }

  // Parse Kin Phone
  let kin_phone_code = "";
  let kin_phone = user.next_of_kin_phone || "";
  try {
    if (user.next_of_kin_phone) {
      const parsed = parsePhoneNumber(user.next_of_kin_phone);
      if (parsed && parsed.country) {
        kin_phone_code = parsed.country;
        kin_phone = parsed.nationalNumber;
      }
    }
  } catch (e) { }

  return {
    // ===== BASIC INFO =====
    id: user.id,
    // full_name: [user.first_name, user.middle_name, user.last_name]
    //   .filter(Boolean)
    //   .join(" ") 
    full_name: user.first_name,
    first_name: user.first_name,
    middle_name: user.middle_name,
    last_name: user.last_name,
    email: user.email,

    // ===== PERSONAL =====
    date_of_birth: user.date_of_birth,
    place_of_birth: user.Place_Of_Birth, // backend uses Capitalized P?
    nationality: user.nationality,
    passport_no: user.passport_no,
    age: user.age,
    marital_status: user.marital_status?.toLowerCase(),

    // ===== POSITION =====
    application_for_position: user.application_for_position,
    other_position: user.other_position,
    last_update_date: user.last_update_date,
    expected_salary: (() => {
      const parts = (user.salary || '').trim().split(/\s+/);
      return parts[0] || '';
    })(),
    expected_salary_currency: (() => {
      const parts = (user.salary || '').trim().split(/\s+/);
      const curr = (parts[1] || 'USD').toUpperCase();
      return ['USD', 'EUR', 'EGP'].includes(curr) ? curr : 'USD';
    })(),
    nearest_port: user.Nearest_Port,
    register_code: user.register_code,
    register_date: user.register_date,
    available_date: user.available_date,

    // ===== PROFILE IMAGE =====
    profile_photo: user.profile_image,

    // ===== PHYSICAL =====
    weight: user.Weight_Kg || "",
    height: user.Height_Cm || "",
    overall_size: user.overall_size,
    shirt_size: user.shirt_size,
    trouser_size: user.trouser_size,
    shoes_size: user.shoes_size,

    // ===== EDUCATION =====
    education_school: user.college_or_school,
    english_level: user.english_language_level,
    other_language: user.other_language,
    other_language_level: user.other_language_level,

    // ===== MARINE TEST =====
    marine_issued_date: user.marlins_test_issued_date,
    marine_result: user.marlins_test_result,
    marine_issued_by: user.marlins_test_issued_by,
    marine_issued_at: user.marlins_test_issued_at,

    // ===== FILE ATTACHMENTS (URLs from backend) =====
    marlins_test_attachment: user.marlins_test_attachment,
    ces_test_attachment: user.ces_test_attachment,

    // ===== CONTACT =====
    home_address: user.address,
    address: user.address,
    mobile: mobile,
    mobile_code: mobile_code,
    phone_number: mobile,

    // ===== NEXT OF KIN =====
    kin_full_name: user.next_of_kin_full_name,
    kin_relationship: user.next_of_kin_relationship,
    kin_phone: kin_phone,
    kin_phone_code: kin_phone_code,
    kin_email: user.next_of_kin_email,
    kin_address: user.next_of_kin_address_country,

    // ===== ARRAYS (snake_case items) =====
    certificates: certificates.map((d) => ({
      id: d.id || `cert-${Date.now()}-${Math.random()}`,
      certificate_name: d.certificate_name,
      certificate_number: d.certificate_number || d.number,
      issue_date: d.issue_date,
      expiry_date: d.expiry_date,
      issued_by: d.issued_by,
      issued_at: d.issued_at,
    })),

    health: healthRecords.map((h) => ({
      ...h,
      id: h.id || `health-${Date.now()}-${Math.random()}`,
    })),

    courses: courses.map((c) => ({
      id: c.id || `course-${Date.now()}-${Math.random()}`,
      user: c.user,
      course_name: c.course_name,
      course_number: c.course_number,
      issue_date: c.issue_date,
      expiry_date: c.expiry_date,
      issued_by: c.issued_by,
      issued_at: c.issued_at,
      country_of_issue: c.country_of_issue,
      document: c.document,
    })),

    sea_services: seaServices.map((s) => ({
      ...s,
      id: s.id || `sea-${Date.now()}-${Math.random()}`,
    })),

    work_experiences: workExperience.map((w) => ({
      ...w,
      id: w.id || `work-${Date.now()}-${Math.random()}`,
    })),

    documents: documents.map((d) => ({
      ...d,
      id: d.id || `doc-${Date.now()}-${Math.random()}`,
      file: d.document_file || d.file,
    })),

    licenses: licenses.map((l) => ({
      ...l,
      id: l.id || `lic-${Date.now()}-${Math.random()}`,
    })),

    languages: languages.map((l) => ({
      ...l,
      id: l.id || `lang-${Date.now()}-${Math.random()}`,
    })),

    references: references.map((r) => ({
      ...r,
      id: r.id || `ref-${Date.now()}-${Math.random()}`,
    })),

    // ===== PASSPORT DETAILS =====
    passport_issue_date: user.passport_issue_date,
    passport_expiry_date: user.passport_expiry_date,
    passport_issued_by: user.passport_issued_by,
    passport_place_of_issue: user.passport_place_of_issue,

    // ===== SEAMAN BOOK =====
    seaman_book_no: user.seaman_book_no,
    seaman_book_issue_date: user.seaman_book_issue_date,
    seaman_book_expiry_date: user.seaman_book_expiry_date,
    seaman_book_issued_by: user.seaman_book_issued_by,
    seaman_book_place_of_issue: user.seaman_book_place_of_issue,

    // ===== COC (Certificate of Competency) =====
    coc_certificate_name: user.coc_certificate_name,
    coc_certificate_number: user.coc_certificate_number,
    coc_issue_date: user.coc_issue_date,
    coc_expiry_date: user.coc_expiry_date,
    coc_issued_at: user.coc_issued_at,
    coc_issued_by: user.coc_issued_by,

    // ===== GOC (General Operator Certificate) =====
    goc_certificate_number: user.goc_certificate_number,
    goc_issue_date: user.goc_issue_date,
    goc_expiry_date: user.goc_expiry_date,
    goc_issued_at: user.goc_issued_at,
    goc_issued_by: user.goc_issued_by,

    // ===== CES TEST =====
    ces_test_result: user.ces_test_result,
    ces_test_issued_date: user.ces_test_issued_date,
    ces_test_issued_by: user.ces_test_issued_by,
    ces_test_issued_at: user.ces_test_issued_at,

    // ===== YELLOW FEVER =====
    yellow_fever_number: user.yellow_fever_number,
    yellow_fever_issue_date: user.yellow_fever_issue_date,
    yellow_fever_expiry_date: user.yellow_fever_expiry_date,

    // ===== CHOLERA =====
    cholera_number: user.cholera_number,
    cholera_issue_date: user.cholera_issue_date,
    cholera_expiry_date: user.cholera_expiry_date,

    // ===== COVID =====
    covid_vaccine_name: user.covid_vaccine_name,
    covid_first_dose: user.covid_first_dose,
    covid_second_dose: user.covid_second_dose,
    covid_other_doses_or_remarks: user.covid_other_doses_or_remarks,

    // ===== INTERNATIONAL MEDICAL =====
    international_medical_number: user.international_medical_number,
    international_medical_issue_date: user.international_medical_issue_date,
    international_medical_expiry_date: user.international_medical_expiry_date,

    // ===== HEALTH CERTIFICATE =====
    health_number: user.health_number,
    health_issue_date: user.health_issue_date,
    health_expiry_date: user.health_expiry_date,
    health_issued_by: user.health_issued_by,
    health_issued_at: user.health_issued_at,
    health_flag_state: user.health_flag_state,

    // ===== OTHER FIELDS =====
    smoker: user.smoker,
    blood_type: user.blood_type,
    country: user.country,
    city: user.city,
    tel_number: user.tel_number,

    // ===== DECLARATION =====
    declaration: user.declaration || null,

    // ===== NEXT OF KIN (additional contacts) =====
    next_of_kin: nextOfKin.map((n) => ({
      ...n,
      id: n.id || `nok-${Date.now()}-${Math.random()}`,
    })),
  };
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const validateFormData = (formData) => {
  const errors = {};

  if (!formData.full_name?.trim()) {
    errors.full_name = "Full name is required";
  }

  if (!formData.email?.trim()) {
    errors.email = "Email is required";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = "Invalid email format";
  }

  if (!formData.mobile?.trim()) {
    errors.mobile = "Phone number is required";
  }

  if (!formData.nationality?.trim()) {
    errors.nationality = "Nationality is required";
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const calculateFormDiff = (currentData, savedData) => {
  const diff = {};
  Object.keys(currentData).forEach((key) => {
    if (JSON.stringify(currentData[key]) !== JSON.stringify(savedData[key])) {
      diff[key] = currentData[key];
    }
  });
  return diff;
};

export const hasUnsavedChanges = (currentData, savedData) => {
  return JSON.stringify(currentData) !== JSON.stringify(savedData);
};

export default {
  mapFormToBackend,
  mapBackendToFrontend,
  validateFormData,
  calculateFormDiff,
  hasUnsavedChanges,
  toApiDate,
  fromApiDate,
  cleanId,
  isTemporaryId,
};
