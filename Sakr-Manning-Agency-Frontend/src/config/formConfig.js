// config/formConfig.js
// Centralized configuration for form components
// Contains all static data, dropdown options, labels, and API endpoints

/**
 * Form Steps Configuration
 * Defines the order, labels, and icons for each form step
 */
export const FORM_STEPS = [
    { id: 0, key: "position_personal", label: "Position & Personal" },
    { id: 1, key: "education", label: "Education" },
    { id: 2, key: "contact", label: "Contact" },
    { id: 3, key: "emergency", label: "Emergency" },
    { id: 4, key: "documents", label: "Documents" },
    { id: 5, key: "certificates", label: "Certificates" },
    { id: 6, key: "health", label: "Health & Marine" },
    { id: 7, key: "courses", label: "Courses" },
    { id: 8, key: "sea_service", label: "Sea Service" },
    { id: 9, key: "references", label: "References" },
    { id: 10, key: "declarations", label: "Declarations" },
    { id: 11, key: "submit", label: "Submit" },
];

/**
 * API Endpoints
 * Centralized reference for all form-related API endpoints
 */
export const API_ENDPOINTS = {
    user: "/users/",
    courses: "/courses/",
    vaccinations: "/vaccinations/",
    licenses: "/my-licenses/",
    languages: "/my-languages/",
    sea_services: "/sea-services/",
};

/**
 * Common Field Labels
 * Consistent labels used across multiple forms
 */
export const FIELD_LABELS = {
    // Document/Certificate fields
    issue_date: "Issue Date",
    expiry_date: "Expiry Date",
    issued_by: "Issued By",
    issued_at: "Issued At",
    country_of_issue: "Country of Issue",
    document_number: "Document Number",
    certificate_number: "Certificate Number",

    // Personal fields
    full_name: "Full Name",
    date_of_birth: "Date of Birth",
    nationality: "Nationality",
    gender: "Gender",

    // Contact fields
    email: "Email",
    mobile: "Mobile",
    address: "Address",
    city: "City",
    country: "Country",

    // Action labels
    save_changes: "Save Changes",
    cancel: "Cancel",
    add: "Add",
    edit: "Edit",
    delete: "Delete",
};

// ============================================================================
// DROPDOWN OPTIONS
// ============================================================================

export const POPULAR_COUNTRIES = [
    "United States",
    "Canada",
    "United Kingdom",
    "Australia",
    "Germany",
    "France",
    "India",
    "China",
    "Japan",
    "Brazil",
    "South Africa",
    "Egypt",
    "United Arab Emirates",
    "Saudi Arabia",
    "Turkey",
    "Italy",
    "Spain",
    "Netherlands",
    "Sweden",
    "Greece",
    "Russia",
    "Philippines",
];

export const POPULAR_NATIONALITIES = [
    "Egyptian",
    "Filipino",
    "Indian",
    "Russian",
    "Ukrainian",
    "Greek",
    "Italian",
    "Spanish",
    "Turkish",
    "Croatian",
    "Polish",
    "Romanian",
    "Chinese",
    "Japanese",
    "South Korean",
    "Indonesian",
    "Vietnamese",
    "Thai",
    "Burmese",
    "American",
    "British",
    "Canadian",
    "German",
    "French",
    "Australian",
    "Brazilian",
    "Mexican",
    "Saudi Arabian",
    "Emirati",
    "Qatari",
    "Kuwaiti",
    "Jordanian",
    "Lebanese",
    "Syrian",
    "Tunisian",
    "Algerian",
    "Moroccan",
    "Libyan",
    "Sudanese",
    "Nigerian",
    "South African",
    "Ethiopian",
    "Ghanaian",
];

/**
 * Course Name Options
 * Marine courses based on STCW regulations
 */
export const COURSE_OPTIONS = [
    { value: "Basic Safety Training", label: "Basic Safety Training" },
    { value: "Advanced Fire Fighting", label: "Advanced Fire Fighting" },
    { value: "GMDSS", label: "GMDSS" },
    { value: "Medical First Aid", label: "Medical First Aid" },
    { value: "Medical Care", label: "Medical Care" },
    { value: "Survival Craft & Rescue Boats", label: "Survival Craft & Rescue Boats" },
    { value: "Bridge Resource Management", label: "Bridge Resource Management" },
    { value: "Engine Room Resource Management", label: "Engine Room Resource Management" },
    { value: "Ship Security Officer", label: "Ship Security Officer" },
    { value: "ECDIS", label: "ECDIS" },
    { value: "Radar Navigation", label: "Radar Navigation" },
    { value: "ARPA", label: "ARPA" },
    { value: "Tanker Familiarization", label: "Tanker Familiarization" },
    { value: "Oil Tanker Cargo Operations", label: "Oil Tanker Cargo Operations" },
    { value: "Chemical Tanker Cargo Operations", label: "Chemical Tanker Cargo Operations" },
    { value: "LNG Tanker Cargo Operations", label: "LNG Tanker Cargo Operations" },
    { value: "Personal Survival Techniques", label: "Personal Survival Techniques" },
    { value: "Proficiency In Personal Survival Techniques", label: "Proficiency In Personal Survival Techniques" },
    { value: "Fire Prevention and Fire Fighting", label: "Fire Prevention and Fire Fighting" },
    { value: "Elementary First Aid", label: "Elementary First Aid" },
    { value: "Medical Care Studies", label: "Medical Care Studies" },
    { value: "Personal Safety and Social Responsibilities", label: "Personal Safety and Social Responsibilities" },
    { value: "Proficiency Of Security Awareness Training Seafarers", label: "Proficiency Of Security Awareness Training Seafarers" },
    { value: "Communications", label: "Communications" },
    { value: "Advanced Communications", label: "Advanced Communications" },
    { value: "ECDIS Advanced Simulator (Management Level)", label: "ECDIS Advanced Simulator (Management Level)" },
    { value: "ECDIS Simulator (Operation Level)", label: "ECDIS Simulator (Operation Level)" },
    { value: "Prevention and Combating of Marine Pollution", label: "Prevention and Combating of Marine Pollution" },
    { value: "Radar & ARPA Simulator and Search & Rescue", label: "Radar & ARPA Simulator and Search & Rescue" },
    { value: "ARPA Simulator and Search", label: "ARPA Simulator and Search" },
    { value: "Marine Radar and Automatic Radar Plotting", label: "Marine Radar and Automatic Radar Plotting" },
    { value: "Navigational Watch keeping", label: "Navigational Watch keeping" },
    { value: "Proficiency for Rating forming part of Navigational watch (II/4)", label: "Proficiency for Rating forming part of Navigational watch (II/4)" },
    { value: "High Voltage Training – Operation of Ship (1000V and More)", label: "High Voltage Training – Operation of Ship (1000V and More)" },
    { value: "Passenger Safety Cargo Safety and Hull Integrity", label: "Passenger Safety Cargo Safety and Hull Integrity" },
    { value: "Crowd Management Training", label: "Crowd Management Training" },
    { value: "Crisis Management and Human Behavior Training", label: "Crisis Management and Human Behavior Training" },
    { value: "Safety Training for Personal Prov. Direct Passengers", label: "Safety Training for Personal Prov. Direct Passengers" },
    { value: "Practical Ability to Prepare Meals (MLC 2006)", label: "Practical Ability to Prepare Meals (MLC 2006)" },
    { value: "Personal Hygiene and Envir. Protection (MLC 2006)", label: "Personal Hygiene and Envir. Protection (MLC 2006)" },
    { value: "Safety and Health in the Provision Meals (MLC 2006)", label: "Safety and Health in the Provision Meals (MLC 2006)" },
    { value: "Food Storage and Inventory Control (MLC 2006)", label: "Food Storage and Inventory Control (MLC 2006)" },
    { value: "Ships Cook Certificate (MLC 2006)", label: "Ships Cook Certificate (MLC 2006)" },
    { value: "Abel Seafarer Deck", label: "Abel Seafarer Deck" },
    { value: "Proficiency for Abel Seafarer Deck (II/5)", label: "Proficiency for Abel Seafarer Deck (II/5)" },
    { value: "Engineering Watch keeping", label: "Engineering Watch keeping" },
    { value: "Proficiency for Rating forming part of a watch in engine room", label: "Proficiency for Rating forming part of a watch in engine room" },
    { value: "Abel Seafarer Engine", label: "Abel Seafarer Engine" },
    { value: "Proficiency for Abel Seafarer Engine (III/5)", label: "Proficiency for Abel Seafarer Engine (III/5)" },
    { value: "Electro Technical Rating", label: "Electro Technical Rating" },
    { value: "Proficiency for Electro Technical Rating (III/7)", label: "Proficiency for Electro Technical Rating (III/7)" },
    { value: "Other", label: "Other" },
];

/**
 * COC (Certificate of Competency) Options
 */
export const COC_OPTIONS = [
    { value: "Master", label: "Master" },
    { value: "Chief Mate", label: "Chief Mate" },
    { value: "2nd Officer", label: "2nd Officer" },
    { value: "3rd Officer", label: "3rd Officer" },
    { value: "Marine Chief Eng.", label: "Marine Chief Eng." },
    { value: "2nd Marine Eng.", label: "2nd Marine Eng." },
    { value: "3rd Marine Eng.", label: "3rd Marine Eng." },
    { value: "Electro-Technical Officer", label: "Electro-Technical Officer" },
    { value: "Gmdss General Operator", label: "GMDSS General Operator" },
];

/**
 * Vaccination/Health Record Options
 * Types of health certificates and vaccinations
 */
export const VACCINATION_OPTIONS = [
    { value: "Quarantine Letter", label: "Quarantine Letter" },
    { value: "Rubella Immunity", label: "Rubella Immunity" },
    { value: "Tessera Sanitaria", label: "Tessera Sanitaria" },
    { value: "Tuberculosis Laboratory Screen", label: "Tuberculosis Laboratory Screen" },
    { value: "Typhoid Vaccination", label: "Typhoid Vaccination" },
    { value: "Varicella Immunization", label: "Varicella Immunization" },
    { value: "Yellow Fever Immunization", label: "Yellow Fever Immunization" },
    { value: "Chickenpox Immunity Screening", label: "Chickenpox Immunity Screening" },
    { value: "Color Vision Certificate", label: "Color Vision Certificate" },
    { value: "Covid-Sars Vaccination", label: "COVID-SARS Vaccination" },
    { value: "Covid Form", label: "COVID Form" },
    { value: "Foodhandler Exams", label: "Foodhandler Exams" },
    { value: "Health Questionnaire", label: "Health Questionnaire" },
    { value: "Hepatitis A Immunization", label: "Hepatitis A Immunization" },
    { value: "Hepatitis B Immunization", label: "Hepatitis B Immunization" },
    { value: "Italian Medical Pre-Embark Examination", label: "Italian Medical Pre-Embark Examination" },
    { value: "Measles Immunity", label: "Measles Immunity" },
    { value: "Medical Certificate For Seafarers", label: "Medical Certificate For Seafarers" },
    { value: "Mmr Booster 2", label: "MMR Booster 2" },
    { value: "Mmr Vaccination / Immunization", label: "MMR Vaccination / Immunization" },
    { value: "Mumps Immunity", label: "Mumps Immunity" },
    { value: "Pertussis Immunization", label: "Pertussis Immunization" },
];

/**
 * License/Certificate Options
 * Professional maritime licenses based on STCW regulations
 */
export const LICENSE_OPTIONS = [
    { value: "Master (Reg. II/2 Par. 1-2)", label: "Master (Reg. II/2 Par. 1-2)" },
    { value: "Master (Reg. II/2 Par. 1-2) Endorsement", label: "Master (Reg. II/2 Par. 1-2) Endorsement" },
    { value: "Master <3,000 GRT (Reg. II/2 Par. 3-4)", label: "Master <3,000 GRT (Reg. II/2 Par. 3-4)" },
    { value: "Master <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement", label: "Master <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement" },
    { value: "Master <500 GRT (Reg. II/3 Par. 5-6)", label: "Master <500 GRT (Reg. II/3 Par. 5-6)" },
    { value: "Master <500 GRT (Reg. II/3 Par. 5-6) Endorsement", label: "Master <500 GRT (Reg. II/3 Par. 5-6) Endorsement" },
    { value: "Yachtmaster Coastal", label: "Yachtmaster Coastal" },
    { value: "Chief Officer (Reg. II/2 Par. 1-2)", label: "Chief Officer (Reg. II/2 Par. 1-2)" },
    { value: "Chief Officer (Reg. II/2 Par. 1-2) Endorsement", label: "Chief Officer (Reg. II/2 Par. 1-2) Endorsement" },
    { value: "Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4)", label: "Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4)" },
    { value: "Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement", label: "Chief Officer <3,000 GRT (Reg. II/2 Par. 3-4) Endorsement" },
    { value: "Navigational Watch Officer (Reg. II/1)", label: "Navigational Watch Officer (Reg. II/1)" },
    { value: "Navigational Watch Officer (Reg. II/1) Endorsement", label: "Navigational Watch Officer (Reg. II/1) Endorsement" },
    { value: "Navigational Watch Officer <500 GRT (II/3 Par. 3-4)", label: "Navigational Watch Officer <500 GRT (II/3 Par. 3-4)" },
    { value: "Chief Engineer (Reg. III/2)", label: "Chief Engineer (Reg. III/2)" },
    { value: "Chief Engineer (Reg. III/2) Endorsement", label: "Chief Engineer (Reg. III/2) Endorsement" },
    { value: "Chief Engineer – Steam (Reg. III/2)", label: "Chief Engineer – Steam (Reg. III/2)" },
    { value: "Chief Engineer – Steam (Reg. III/2) Endorsement", label: "Chief Engineer – Steam (Reg. III/2) Endorsement" },
    { value: "Chief Engineer <3,000 KW (Reg. III/3)", label: "Chief Engineer <3,000 KW (Reg. III/3)" },
    { value: "2nd Engineer (Reg. III/2)", label: "2nd Engineer (Reg. III/2)" },
    { value: "2nd Engineer (Reg. III/2) Endorsement", label: "2nd Engineer (Reg. III/2) Endorsement" },
    { value: "2nd Engineer – Steam (Reg. III/3)", label: "2nd Engineer – Steam (Reg. III/3)" },
    { value: "2nd Engineer – Steam (Reg. III/3) Endorsement", label: "2nd Engineer – Steam (Reg. III/3) Endorsement" },
    { value: "2nd Engineer <3,000 KW (Reg. III/3)", label: "2nd Engineer <3,000 KW (Reg. III/3)" },
    { value: "Engineering Watch Officer (Reg. III/1)", label: "Engineering Watch Officer (Reg. III/1)" },
    { value: "Engineering Watch Officer (Reg. III/1) Endorsement", label: "Engineering Watch Officer (Reg. III/1) Endorsement" },
    { value: "Electro Technical Officer (Reg. III/6)", label: "Electro Technical Officer (Reg. III/6)" },
    { value: "Electro Technical Officer (Reg. III/6) Endorsement", label: "Electro Technical Officer (Reg. III/6) Endorsement" },
    { value: "Electro Technical Rating (Reg. III/7)", label: "Electro Technical Rating (Reg. III/7)" },
    { value: "Able Seaman Deck (Reg. II/5)", label: "Able Seaman Deck (Reg. II/5)" },
    { value: "Able Seaman Deck (Reg. II/5) Endorsement", label: "Able Seaman Deck (Reg. II/5) Endorsement" },
    { value: "Able Seaman Engine (Reg. III/5)", label: "Able Seaman Engine (Reg. III/5)" },
    { value: "Able Seaman Engine (Reg. III/5) Endorsement", label: "Able Seaman Engine (Reg. III/5) Endorsement" },
    { value: "Qualified Steward/Messman Endorsement", label: "Qualified Steward/Messman Endorsement" },
    { value: "GMDSS Radio Operator (Reg. IV/2)", label: "GMDSS Radio Operator (Reg. IV/2)" },
    { value: "GMDSS Radio Operator (Reg. IV/2) Endorsement", label: "GMDSS Radio Operator (Reg. IV/2) Endorsement" },
    { value: "GMDSS Endorsement (Reg. IV/2) Flag CRA", label: "GMDSS Endorsement (Reg. IV/2) Flag CRA" },
    { value: "GMDSS Restricted Operator (ROC) (Reg. IV/2)", label: "GMDSS Restricted Operator (ROC) (Reg. IV/2)" },
    { value: "GMDSS Restricted Operator (ROC) (Reg. IV/2) Endorsement", label: "GMDSS Restricted Operator (ROC) (Reg. IV/2) Endorsement" },
    { value: "GMDSS Restricted Operator (ROC) (Reg. IV/2) CRA", label: "GMDSS Restricted Operator (ROC) (Reg. IV/2) CRA" },
    { value: "Qualified Ship’s Cook (MLC 2006)", label: "Qualified Ship’s Cook (MLC 2006)" },
    { value: "Qualified Ship’s Cook (MLC 2006) Endorsement", label: "Qualified Ship’s Cook (MLC 2006) Endorsement" },
    { value: "Navigational Watch Rating (Reg. II/4)", label: "Navigational Watch Rating (Reg. II/4)" },
    { value: "Navigational Watch Rating (Reg. II/4) Endorsement", label: "Navigational Watch Rating (Reg. II/4) Endorsement" },
    { value: "COC – Certificate of Competency", label: "COC – Certificate of Competency" },
    { value: "COC – Certificate of Competency Endorsement", label: "COC – Certificate of Competency Endorsement" },
    { value: "GOC – General Operator Certificate", label: "GOC – General Operator Certificate" },
    { value: "GOC – General Operator Certificate Endorsement", label: "GOC – General Operator Certificate Endorsement" },
];

/**
 * Document Type Options
 * Types of travel and identification documents
 */
export const DOCUMENT_TYPE_OPTIONS = [
    { value: "Bahamas Seaman's Book", label: "Bahamas Seamans Book" },
    { value: "Belize Seaman's Book", label: "Belize Seamans Book" },
    { value: "Bermuda Seaman's Book", label: "Bermuda Seamans Book" },
    { value: "Eu National Id", label: "EU National ID" },
    { value: "Exit Interview", label: "Exit Interview" },
    { value: "Liberian Seaman's Book", label: "Liberian Seamans Book" },
    { value: "Local Id Card", label: "Local ID Card" },
    { value: "Luxembourg Seaman's Book", label: "Luxembourg Seamans Book" },
    { value: "Palau Seaman's Book", label: "Palau Seamans Book" },
    { value: "Panama Seaman's Book", label: "Panama Seamans Book" },
    { value: "Passport", label: "Passport" },
    { value: "Permesso Soggiorno Permanente", label: "Permesso Soggiorno Permanente" },
    { value: "Permesso Soggiorno Temporaneo", label: "Permesso Soggiorno Temporaneo" },
    { value: "Personal Record Sheet", label: "Personal Record Sheet" },
    { value: "Residence Certificate", label: "Residence Certificate" },
    { value: "Seafarers' Id. Doc. Ilo 185", label: "Seafarers ID DOC ILO 185" },
    { value: "Seaman's Book", label: "Seaman's Book" },
    { value: "Seaman's Book/Card Or Id", label: "Seaman's Book/Card or ID" },
    { value: "U.K. Seaman's Book", label: "U.K. Seaman's Book" },
    { value: "Australian Visa Crew", label: "Australian Visa Crew" },
    { value: "Brazil", label: "Brazil Visa" },
    { value: "China", label: "China Visa" },
    { value: "Cyprus", label: "Cyprus Visa" },
    { value: "Germany Visa D", label: "Germany Visa D" },
    { value: "Italian Visa D", label: "Italian Visa D" },
    { value: "Saudi Arabia", label: "Saudi Arabia Visa" },
    { value: "Schengen Visa", label: "Schengen Visa" },
    { value: "Turkey", label: "Turkey Visa" },
    { value: "UAE", label: "UAE Visa" },
    { value: "US Visa B1/B2", label: "US Visa B1/B2" },
    { value: "US Visa C1/D", label: "US Visa C1/D" },
];

/**
 * Language Options
 * Common languages for maritime professionals
 */
export const LANGUAGE_OPTIONS = [
    { value: "English", label: "English" },
    { value: "Arabic", label: "Arabic" },
    { value: "French", label: "French" },
    { value: "Spanish", label: "Spanish" },
    { value: "German", label: "German" },
    { value: "Russian", label: "Russian" },
    { value: "Chinese", label: "Chinese" },
    { value: "Japanese", label: "Japanese" },
    { value: "Portuguese", label: "Portuguese" },
    { value: "Italian", label: "Italian" },
    { value: "Dutch", label: "Dutch" },
    { value: "Greek", label: "Greek" },
    { value: "Turkish", label: "Turkish" },
    { value: "Filipino", label: "Filipino" },
    { value: "Hindi", label: "Hindi" },
    { value: "Other", label: "Other" },
];

/**
 * CEFR Language Level Options
 * Common European Framework of Reference for Languages
 */
export const CEFR_LEVELS = [
    { value: "A1", label: "A1 - Beginner", description: "Basic user - can understand and use familiar everyday expressions." },
    { value: "A2", label: "A2 - Elementary", description: "Basic user - can communicate in simple and routine tasks." },
    { value: "B1", label: "B1 - Intermediate", description: "Independent user - can deal with most situations while travelling." },
    { value: "B2", label: "B2 - Upper-Intermediate", description: "Independent user - can interact with a degree of fluency and spontaneity." },
    { value: "C1", label: "C1 - Advanced", description: "Proficient user - can express ideas fluently and spontaneously." },
    { value: "C2", label: "C2 - Proficiency", description: "Proficient user - can express themselves spontaneously and precisely." },
];
/*
* Speaking/Writing/Reading Levels
* Elementary
* Intermediate
* Advanced
* Native
*/
export const LANGUAGE_LEVELS = [
    { value: "Elementary", label: "Elementary" },
    { value: "Intermediate", label: "Intermediate" },
    { value: "Advanced", label: "Advanced" },
    { value: "Native", label: "Native" },
];

/**
 * Gender Options
 */
export const GENDER_OPTIONS = [
    { value: "male", label: "Male" },
    { value: "female", label: "Female" },
];

/**
 * Marital Status Options
 */
export const MARITAL_STATUS_OPTIONS = [
    { value: "Single", label: "Single" },
    { value: "Married", label: "Married" },
];

/**
 * Religion Options
 */
export const RELIGION_OPTIONS = [
    { value: "islam", label: "Islam" },
    { value: "christianity", label: "Christianity" },
    { value: "other", label: "Other" },
];

/**
 * Education Level Options
 */
export const EDUCATION_LEVEL_OPTIONS = [
    { value: "high_school", label: "High School" },
    { value: "diploma", label: "Diploma" },
    { value: "bachelor", label: "Bachelor's Degree" },
    { value: "master", label: "Master's Degree" },
    { value: "phd", label: "Ph.D." },
    { value: "other", label: "Other" },
];

/**
 * Relationship Options (for emergency contacts)
 */
export const RELATIONSHIP_OPTIONS = [
    { value: "Father", label: "Father" },
    { value: "Mother", label: "Mother" },
    { value: "Brother", label: "Brother" },
    { value: "Sister", label: "Sister" },
    { value: "Wife", label: "Wife" },
    { value: "Husband", label: "Husband" },
    { value: "Son", label: "Son" },
    { value: "Daughter", label: "Daughter" },
    { value: "Uncle", label: "Uncle" },
    { value: "Aunt", label: "Aunt" },
    { value: "Friend", label: "Friend" },
    { value: "Other", label: "Other" },
];

// ============================================================================
// FIELD SCHEMAS (Default Values)
// ============================================================================

/**
 * Form Field Names
 * Centralized registry of all input names to ensure consistency
 */
export const FORM_FIELDS = {
    POSITION: {
        APPLICATION: "application_for_position",
        OTHER: "other_position",
        REGISTER_CODE: "register_code",
        LAST_UPDATE: "last_updated_date",
        REGISTER_DATE: "register_date",
        AVAILABLE_DATE: "available_date",
        EXPECTED_SALARY: "expected_salary",
        EXPECTED_SALARY_CURRENCY: "expected_salary_currency",
    },
    PERSONAL: {
        FULL_NAME: "full_name",
        NATIONALITY: "nationality",
        PLACE_OF_BIRTH: "place_of_birth",
        DATE_OF_BIRTH: "date_of_birth",
        NEAREST_PORT: "nearest_port",
        MARITAL_STATUS: "marital_status",
        WEIGHT: "weight",
        HEIGHT: "height",
        OVERALL_SIZE: "overall_size",
        SHIRT_SIZE: "shirt_size",
        TROUSER_SIZE: "trouser_size",
        SHOES_SIZE: "shoes_size",
        PHOTO: "profile_photo",
        SMOKER: "smoker",
        BLOOD_TYPE: "blood_type",
        SCHENGEN_VISA: "schengen_visa_status",
        US_VISA: "us_visa_status",
        USER_STATUS: "user_status",
    },
    CONTACT: {
        ADDRESS: "home_address",
        EMAIL: "email",
        MOBILE: "mobile",
        MOBILE_CODE: "mobile_code",
        MOBILE_2: "mobile_2",
        MOBILE_2_CODE: "mobile_2_code",
        COUNTRY: "country",
        CITY: "city",
    },
    EMERGENCY: {
        FULL_NAME: "kin_full_name",
        RELATIONSHIP: "kin_relationship",
        ADDRESS: "kin_address",
        PHONE: "kin_phone",
        PHONE_CODE: "kin_phone_code",
        EMAIL: "kin_email",
    },
    NEXT_OF_KIN: {
        FULL_NAME: "full_name",
        RELATIONSHIP: "relationship",
        ADDRESS_COUNTRY: "address_country",
        PHONE: "phone",
        PHONE2: "phone2",
        EMAIL: "email",
    },
    EDUCATION: {
        SCHOOL: "education_school",
        MARINE_ISSUED_DATE: "marine_issued_date",
        MARINE_RESULT: "marine_result",
        MARINE_ISSUED_BY: "marine_issued_by",
        MARINE_ISSUED_AT: "marine_issued_at",
        MARINE_FILE: "marlins_test_file",
    },
    SEA_SERVICE: {
        COMPANY: "company_name",
        RANK: "rank",
        VESSEL_NAME: "vessel_name",
        IMO_NUMBER: "imo_number",
        VESSEL_NAME_IMO: "vessel_name_imo",
        SIGNED_ON: "signed_on",
        SIGNED_OFF: "signed_off",
        FLAG: "flag",
        PERIOD: "period",
        VESSEL_TYPE: "vessel_type",
        DWT: "dwt",
        GWT: "gwt",
        GRT: "grt",
        DWT_GRT: "dwt_grt",
        ENGINE_TYPE: "engine_type",
        ENGINE_TYPE_BH_KW: "engine_type_bh_kw",
        BH: "bh",
        KW: "kw",
        REASON: "reason_for_sign_off",
        FILE: "file",
    },
    WORK_EXPERIENCE: {
        EXPERIENCE: "experience",
    },
    PASSPORT: {
        NUMBER: "passport_no",
        ISSUE_DATE: "passport_issue_date",
        EXPIRY_DATE: "passport_expiry_date",
        ISSUED_BY: "passport_issued_by",
        PLACE_OF_ISSUE: "passport_place_of_issue",
    },
    SEAMAN_BOOK: {
        NUMBER: "seaman_book_no",
        ISSUE_DATE: "seaman_book_issue_date",
        EXPIRY_DATE: "seaman_book_expiry_date",
        ISSUED_BY: "seaman_book_issued_by",
        PLACE_OF_ISSUE: "seaman_book_place_of_issue",
    },
    DOCUMENTS: {
        TYPE: "document_type",
        NUMBER: "document_number",
        ISSUE_DATE: "issue_date",
        EXPIRY_DATE: "expiry_date",
        PLACE_OF_ISSUE: "issuing_country",
        ISSUED_BY: "issued_by",
        PLACE_OF_ISSUE_CITY: "place_of_issue",
        FILE: "file",
    },
    COC: {
        NAME: "coc_certificate_name",
        NUMBER: "coc_certificate_number",
        ISSUE_DATE: "coc_issue_date",
        EXPIRY_DATE: "coc_expiry_date",
        ISSUED_AT: "coc_issued_at",
        ISSUED_BY: "coc_issued_by",
    },
    GOC: {
        NUMBER: "goc_certificate_number",
        ISSUE_DATE: "goc_issue_date",
        EXPIRY_DATE: "goc_expiry_date",
        ISSUED_AT: "goc_issued_at",
        ISSUED_BY: "goc_issued_by",
    },
    CES_TEST: {
        RESULT: "ces_test_result",
        ISSUED_DATE: "ces_test_issued_date",
        ISSUED_BY: "ces_test_issued_by",
        ISSUED_AT: "ces_test_issued_at",
        FILE: "ces_test_file",
    },
    CERTIFICATES: {
        NAME: "certificate_name",
        NUMBER: "certificate_number",
        ISSUE_DATE: "issue_date",
        EXPIRY_DATE: "expiration_date",
        ISSUED_BY: "issued_by",
        ISSUED_AT: "issued_at",
        FILE: "document_file",
    },
    YELLOW_FEVER: {
        NUMBER: "yellow_fever_number",
        ISSUE_DATE: "yellow_fever_issue_date",
        EXPIRY_DATE: "yellow_fever_expiry_date",
    },
    CHOLERA: {
        NUMBER: "cholera_number",
        ISSUE_DATE: "cholera_issue_date",
        EXPIRY_DATE: "cholera_expiry_date",
    },
    COVID: {
        VACCINE_NAME: "covid_vaccine_name",
        FIRST_DOSE: "covid_first_dose",
        SECOND_DOSE: "covid_second_dose",
        OTHER_DOSES_OR_REMARKS: "covid_other_doses_or_remarks",
    },
    INTERNATIONAL_MEDICAL: {
        NUMBER: "international_medical_number",
        ISSUE_DATE: "international_medical_issue_date",
        EXPIRY_DATE: "international_medical_expiry_date",
    },
    HEALTH_CERT: {
        NUMBER: "health_number",
        ISSUE_DATE: "health_issue_date",
        EXPIRY_DATE: "health_expiry_date",
        ISSUED_BY: "health_issued_by",
        ISSUED_AT: "health_issued_at",
        FLAG_STATE: "health_flag_state",
    },
    HEALTH: {
        NAME: "name",
        NUMBER: "number",
        ISSUE_DATE: "issue_date",
        EXPIRY_DATE: "expiry_date",
        ISSUED_BY: "issued_by",
        ISSUED_AT: "issued_at",
        DISEASE: "disease",
        FIRST_DATE: "first_date",
        LAST_DATE: "last_date",
        REMARKS: "remarks",
        FILE: "document",
    },
    COURSES: {
        NAME: "course_name",
        NUMBER: "course_number",
        ISSUE_DATE: "issue_date",
        EXPIRY_DATE: "expiry_date",
        ISSUED_BY: "issued_by",
        ISSUED_AT: "issued_at",
        COUNTRY: "country_of_issue",
        FILE: "document",
    },
    LICENSES: {
        NAME: "document_name",
        NUMBER: "document_number",
        ISSUE_DATE: "issue_date",
        EXPIRY_DATE: "expiration_date",
        COUNTRY: "country_of_issue",
        FILE: "document_file",
    },
    LANGUAGES: {
        LANGUAGE: "language",
        GENERAL: "general_remarks",
        SPEAKING: "speaking_level",
        WRITING: "writing_level",
        READING: "reading_level",
        LEVEL: "cefr_level",
        DESCRIPTION: "cefr_description",
        ATTACHMENT: "attachment",
    },
    REFERENCE: {
        NUMBER: "number",
        NAME: "name",
        COMPANY_NAME: "company_name",
        MANAGEMENT: "management",
        COUNTRY: "country",
        POSITION: "position",
        EMAIL: "email",
        TEL: "tel",
    },
    DECLARATION: {
        ACCIDENT_DETAILS: "accident_details",
        ADDICTION_DETAILS: "addiction_details",
        CONSENT: "consent_given",
        DATE: "declaration_date",
        PLACE: "declaration_place",
        DISEASE_DETAILS: "disease_details",
        HAS_ACCIDENT: "has_accident",
        HAS_ADDICTION: "has_addiction",
        HAS_DISEASE: "has_disease",
        HAS_PSYCHIATRIC: "has_psychiatric_treatment",
        PSYCHIATRIC_DETAILS: "psychiatric_treatment_details",
        SIGNATURE: "signature",
    },
};

/**
 * Course Field Schema
 * Default values for course forms
 */
export const COURSE_FIELD_DEFAULTS = {
    [FORM_FIELDS.COURSES.NAME]: "",
    [FORM_FIELDS.COURSES.NUMBER]: "",
    [FORM_FIELDS.COURSES.ISSUE_DATE]: "",
    [FORM_FIELDS.COURSES.EXPIRY_DATE]: "",
    [FORM_FIELDS.COURSES.ISSUED_BY]: "",
    [FORM_FIELDS.COURSES.ISSUED_AT]: "",
    [FORM_FIELDS.COURSES.COUNTRY]: "",
};

/**
 * Vaccination/Health Field Schema
 * Default values for health record forms
 */
export const HEALTH_FIELD_DEFAULTS = {
    [FORM_FIELDS.HEALTH.NAME]: "",
    [FORM_FIELDS.HEALTH.NUMBER]: "",
    [FORM_FIELDS.HEALTH.ISSUE_DATE]: "",
    [FORM_FIELDS.HEALTH.EXPIRY_DATE]: "",
    [FORM_FIELDS.HEALTH.ISSUED_BY]: "",
    [FORM_FIELDS.HEALTH.ISSUED_AT]: "",
    [FORM_FIELDS.HEALTH.DISEASE]: "",
    [FORM_FIELDS.HEALTH.FIRST_DATE]: "",
    [FORM_FIELDS.HEALTH.LAST_DATE]: "",
    [FORM_FIELDS.HEALTH.REMARKS]: "",
};

/**
 * License Field Schema
 * Default values for license forms
 */
export const LICENSE_FIELD_DEFAULTS = {
    [FORM_FIELDS.LICENSES.NAME]: "",
    [FORM_FIELDS.LICENSES.NUMBER]: "",
    [FORM_FIELDS.LICENSES.COUNTRY]: "",
    [FORM_FIELDS.LICENSES.ISSUE_DATE]: "",
    [FORM_FIELDS.LICENSES.EXPIRY_DATE]: "",
};

/**
 * Document Field Schema
 * Default values for document forms
 */
export const DOCUMENT_FIELD_DEFAULTS = {
    [FORM_FIELDS.DOCUMENTS.TYPE]: "",
    [FORM_FIELDS.DOCUMENTS.NUMBER]: "",
    [FORM_FIELDS.DOCUMENTS.PLACE_OF_ISSUE]: "",
    [FORM_FIELDS.DOCUMENTS.ISSUE_DATE]: "",
    [FORM_FIELDS.DOCUMENTS.EXPIRY_DATE]: "",
};

/**
 * Language Field Schema
 * Default values for language forms
 */
export const LANGUAGE_FIELD_DEFAULTS = {
    [FORM_FIELDS.LANGUAGES.LANGUAGE]: "",
    [FORM_FIELDS.LANGUAGES.GENERAL]: "",
    [FORM_FIELDS.LANGUAGES.SPEAKING]: "",
    [FORM_FIELDS.LANGUAGES.WRITING]: "",
    [FORM_FIELDS.LANGUAGES.READING]: "",
    [FORM_FIELDS.LANGUAGES.LEVEL]: "",
    [FORM_FIELDS.LANGUAGES.DESCRIPTION]: "",
};

/**
 * Sea Service Field Schema
 * Default values for sea service forms
 */
export const SEA_SERVICE_FIELD_DEFAULTS = {
    [FORM_FIELDS.SEA_SERVICE.COMPANY]: "",
    [FORM_FIELDS.SEA_SERVICE.RANK]: "",
    [FORM_FIELDS.SEA_SERVICE.VESSEL_NAME]: "",
    [FORM_FIELDS.SEA_SERVICE.IMO_NUMBER]: "",
    [FORM_FIELDS.SEA_SERVICE.VESSEL_NAME_IMO]: "",
    [FORM_FIELDS.SEA_SERVICE.SIGNED_ON]: "",
    [FORM_FIELDS.SEA_SERVICE.SIGNED_OFF]: "",
    [FORM_FIELDS.SEA_SERVICE.FLAG]: "",
    [FORM_FIELDS.SEA_SERVICE.PERIOD]: "",
    [FORM_FIELDS.SEA_SERVICE.VESSEL_TYPE]: "",
    [FORM_FIELDS.SEA_SERVICE.DWT]: "",
    [FORM_FIELDS.SEA_SERVICE.GRT]: "",
    [FORM_FIELDS.SEA_SERVICE.DWT_GRT]: "",
    [FORM_FIELDS.SEA_SERVICE.ENGINE_TYPE]: "",
    [FORM_FIELDS.SEA_SERVICE.ENGINE_TYPE_BH_KW]: "",
    [FORM_FIELDS.SEA_SERVICE.BH]: "",
    [FORM_FIELDS.SEA_SERVICE.KW]: "",
    [FORM_FIELDS.SEA_SERVICE.REASON]: "",
};

/**
 * Certificate Field Schema
 * Default values for certificate forms
 */
export const CERTIFICATE_FIELD_DEFAULTS = {
    [FORM_FIELDS.CERTIFICATES.NAME]: "",
    [FORM_FIELDS.CERTIFICATES.NUMBER]: "",
    [FORM_FIELDS.CERTIFICATES.ISSUE_DATE]: "",
    [FORM_FIELDS.CERTIFICATES.EXPIRY_DATE]: "",
    [FORM_FIELDS.CERTIFICATES.ISSUED_BY]: "",
    [FORM_FIELDS.CERTIFICATES.ISSUED_AT]: "",
};

/**
 * Declaration Field Schema
 * Default values for declaration form
 */
export const DECLARATION_FIELD_DEFAULTS = {
    [FORM_FIELDS.DECLARATION.HAS_DISEASE]: false,
    [FORM_FIELDS.DECLARATION.DISEASE_DETAILS]: "",
    [FORM_FIELDS.DECLARATION.HAS_ACCIDENT]: false,
    [FORM_FIELDS.DECLARATION.ACCIDENT_DETAILS]: "",
    [FORM_FIELDS.DECLARATION.HAS_PSYCHIATRIC]: false,
    [FORM_FIELDS.DECLARATION.PSYCHIATRIC_DETAILS]: "",
    [FORM_FIELDS.DECLARATION.HAS_ADDICTION]: false,
    [FORM_FIELDS.DECLARATION.ADDICTION_DETAILS]: "",
    [FORM_FIELDS.DECLARATION.CONSENT]: false,
    [FORM_FIELDS.DECLARATION.PLACE]: "",
    [FORM_FIELDS.DECLARATION.DATE]: "",
    [FORM_FIELDS.DECLARATION.SIGNATURE]: "",
};

/**
 * Reference Field Schema
 * Default values for reference forms
 */
export const REFERENCE_FIELD_DEFAULTS = {
    [FORM_FIELDS.REFERENCE.NUMBER]: "",
    [FORM_FIELDS.REFERENCE.NAME]: "",
    [FORM_FIELDS.REFERENCE.COMPANY_NAME]: "",
    [FORM_FIELDS.REFERENCE.MANAGEMENT]: "",
    [FORM_FIELDS.REFERENCE.COUNTRY]: "",
    [FORM_FIELDS.REFERENCE.POSITION]: "",
    [FORM_FIELDS.REFERENCE.EMAIL]: "",
    [FORM_FIELDS.REFERENCE.TEL]: "",
};

/**
 * Work Experience Field Schema
 * Default values for work experience forms
 */
export const WORK_EXPERIENCE_FIELD_DEFAULTS = {
    [FORM_FIELDS.WORK_EXPERIENCE.EXPERIENCE]: "",
};

/**
 * Next of Kin Field Schema
 * Default values for additional emergency contact forms
 */
export const NEXT_OF_KIN_FIELD_DEFAULTS = {
    [FORM_FIELDS.NEXT_OF_KIN.FULL_NAME]: "",
    [FORM_FIELDS.NEXT_OF_KIN.RELATIONSHIP]: "",
    [FORM_FIELDS.NEXT_OF_KIN.ADDRESS_COUNTRY]: "",
    [FORM_FIELDS.NEXT_OF_KIN.PHONE]: "",
    [FORM_FIELDS.NEXT_OF_KIN.PHONE2]: "",
    [FORM_FIELDS.NEXT_OF_KIN.EMAIL]: "",
};



// ============================================================================
// BACKEND FIELD MAPPING (Single Source of Truth)
// ============================================================================

/**
 * Backend Field Names
 * Maps to exact backend API field names (preserves mixed naming conventions)
 * Use this for all form-to-API transformations
 */
export const BACKEND_FIELDS = {
    // User flat fields - mixed naming conventions from backend
    USER: {
        // Basic Info
        first_name: "first_name",
        middle_name: "middle_name",
        last_name: "last_name",
        email: "email",
        phone_number: "phone_number",
        profile_image: "profile_image",

        // Personal - Note: Backend uses Title_Case for some fields
        date_of_birth: "date_of_birth",
        Place_Of_Birth: "Place_Of_Birth",
        nationality: "nationality",
        passport_no: "passport_no",
        age: "age",
        marital_status: "marital_status",

        // Physical - Backend uses Title_Case
        Weight_Kg: "Weight_Kg",
        Height_Cm: "Height_Cm",
        overall_size: "overall_size",
        shirt_size: "shirt_size",
        trouser_size: "trouser_size",
        shoes_size: "shoes_size",

        // Contact
        address: "address",
        Nearest_Port: "Nearest_Port",

        // Next of Kin
        next_of_kin_full_name: "next_of_kin_full_name",
        next_of_kin_relationship: "next_of_kin_relationship",
        next_of_kin_phone: "next_of_kin_phone",
        next_of_kin_email: "next_of_kin_email",
        next_of_kin_address_country: "next_of_kin_address_country",

        // Education
        english_language_level: "english_language_level",
        other_language: "other_language",
        other_language_level: "other_language_level",
        college_or_school: "college_or_school",

        // Marine Test
        marlins_test_issued_date: "marlins_test_issued_date",
        marlins_test_result: "marlins_test_result",
        marlins_test_issued_by: "marlins_test_issued_by",
        marlins_test_issued_at: "marlins_test_issued_at",

        // Position
        application_for_position: "application_for_position",
        other_position: "other_position",
        last_update_date: "last_update_date",
        salary: "salary",
        register_code: "register_code",
        register_date: "register_date",
        available_date: "available_date",
    },

    // Personal Documents (API: /api/users/personal-documents/)
    DOCUMENTS: {
        document_type: "document_type",
        document_number: "document_number",
        issue_date: "issue_date",
        expiry_date: "expiry_date",
        issuing_country: "issuing_country",
        issued_by: "issued_by",
        place_of_issue: "place_of_issue",
    },

    // Certificates (nested in user)
    CERTIFICATES: {
        certificate_name: "certificate_name",
        certificate_number: "certificate_number",
        issue_date: "issue_date",
        expiry_date: "expiry_date",
        issued_by: "issued_by",
        issued_at: "issued_at",
    },

    // Vaccinations/Health (API: /api/vaccinations/)
    VACCINATIONS: {
        name: "name",
        number: "number",
        issue_date: "issue_date",
        expiry_date: "expiry_date",
        issued_by: "issued_by",
        issued_at: "issued_at",
        disease: "disease",
        first_date: "first_date",
        last_date: "last_date",
        remarks: "remarks",
    },

    // Courses (API: /api/courses/)
    COURSES: {
        course_name: "course_name",
        course_number: "course_number",
        issue_date: "issue_date",
        expiry_date: "expiry_date",
        issued_by: "issued_by",
        issued_at: "issued_at",
        country_of_issue: "country_of_issue",
    },

    // Sea Services (API: /api/sea-services/)
    SEA_SERVICES: {
        company_name: "company_name",
        rank: "rank",
        vessel_name: "vessel_name",
        imo_number: "imo_number",
        vessel_name_imo: "vessel_name_imo",
        signed_on: "signed_on",
        signed_off: "signed_off",
        flag: "flag",
        period: "period",
        vessel_type: "vessel_type",
        dwt: "dwt",
        grt: "grt",
        dwt_grt: "dwt_grt",
        engine_type: "engine_type",
        engine_type_bh_kw: "engine_type_bh_kw",
        bh: "bh",
        kw: "kw",
        reason_for_sign_off: "reason_for_sign_off",
        file: "file",
    },

    // Licenses (API: /api/my-licenses/)
    LICENSES: {
        document_name: "document_name",
        document_number: "document_number",
        issue_date: "issue_date",
        expiration_date: "expiration_date",
        country_of_issue: "country_of_issue",
    },

    // Languages (API: /api/users/user-languages/)
    LANGUAGES: {
        language: "language",
        general_remarks: "general_remarks",
        speaking_level: "speaking_level",
        writing_level: "writing_level",
        reading_level: "reading_level",
        cefr_level: "cefr_level",
        cefr_description: "cefr_description",
        attachment: "attachment",
    },

    // Declaration (API: /api/users/declarations/)
    DECLARATION: {
        has_disease: "has_disease",
        disease_details: "disease_details",
        has_accident: "has_accident",
        accident_details: "accident_details",
        has_psychiatric_treatment: "has_psychiatric_treatment",
        psychiatric_treatment_details: "psychiatric_treatment_details",
        has_addiction: "has_addiction",
        addiction_details: "addiction_details",
        consent_given: "consent_given",
        declaration_place: "declaration_place",
        declaration_date: "declaration_date",
        signature: "signature",
    },
};

/**
 * Form Array Keys
 * Centralized keys for array fields in form state
 */
export const FORM_ARRAYS = {
    DOCUMENTS: "documents",
    CERTIFICATES: "certificates",
    HEALTH: "health",
    COURSES: "courses",
    SEA_SERVICES: "sea_services",
    WORK_EXPERIENCES: "work_experiences",
    LICENSES: "licenses",
    LANGUAGES: "languages",
};

// ============================================================================
// CONSOLIDATED EXPORTS
// ============================================================================

/**
 * All form options consolidated into a single object
 * for easy import: import { FORM_OPTIONS } from '@/config/formConfig';
 */
/**
 * Blood Type Options
 */
export const BLOOD_TYPE_OPTIONS = [
    { value: "A+", label: "A+" },
    { value: "A-", label: "A-" },
    { value: "B+", label: "B+" },
    { value: "B-", label: "B-" },
    { value: "AB+", label: "AB+" },
    { value: "AB-", label: "AB-" },
    { value: "O+", label: "O+" },
    { value: "O-", label: "O-" },
];

/**
 * Visa Status Options
 */
export const VISA_STATUS_OPTIONS = [
    { value: "Valid", label: "Valid" },
    { value: "Expired", label: "Expired" },
    { value: "None", label: "None" },
];

/**
 * All form options consolidated into a single object
 * for easy import: import { FORM_OPTIONS } from '@/config/formConfig';
 */
export const FORM_OPTIONS = {
    courses: COURSE_OPTIONS,
    vaccinations: VACCINATION_OPTIONS,
    licenses: LICENSE_OPTIONS,
    documents: DOCUMENT_TYPE_OPTIONS,
    languages: LANGUAGE_OPTIONS,
    cefr_levels: CEFR_LEVELS,
    genders: GENDER_OPTIONS,
    marital_statuses: MARITAL_STATUS_OPTIONS,
    religions: RELIGION_OPTIONS,
    education_levels: EDUCATION_LEVEL_OPTIONS,
    relationships: RELATIONSHIP_OPTIONS,
    blood_types: BLOOD_TYPE_OPTIONS,
    visa_statuses: VISA_STATUS_OPTIONS,
};

/**
 * All field defaults consolidated
 */
export const FIELD_DEFAULTS = {
    course: COURSE_FIELD_DEFAULTS,
    health: HEALTH_FIELD_DEFAULTS,
    license: LICENSE_FIELD_DEFAULTS,
    document: DOCUMENT_FIELD_DEFAULTS,
    language: LANGUAGE_FIELD_DEFAULTS,
    sea_service: SEA_SERVICE_FIELD_DEFAULTS,
    certificate: CERTIFICATE_FIELD_DEFAULTS,
    reference: REFERENCE_FIELD_DEFAULTS,
    work_experience: WORK_EXPERIENCE_FIELD_DEFAULTS,
    declaration: DECLARATION_FIELD_DEFAULTS,
};

export default {
    FORM_STEPS,
    API_ENDPOINTS,
    FIELD_LABELS,
    FORM_FIELDS,
    FORM_OPTIONS,
    FIELD_DEFAULTS,
    BACKEND_FIELDS,
    FORM_ARRAYS,
};

