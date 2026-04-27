// ================================
// Common validation patterns
// ================================
const VALIDATION_PATTERNS = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^[\\+]?[1-9][\d]{0,15}$/,
  passport: /^[A-Z0-9]{6,12}$/,
  seamanBook: /^[A-Z0-9]{8,15}$/,
  certificateNumber: /^[A-Z0-9\-\\/]{5,20}$/,
  vesselName: /^[A-Za-z0-9\s\-\\.]{2,50}$/,
  imoNumber: /^IMO\s?\d{7}$/,
  tonnage: /^\d+(\.\d{1,2})?$/,
};

// ================================
// Position & Personal Form Rules
// ================================
export const POSITION_PERSONAL_RULES = {
  application_for_position: {
    required: "Position is required",
    minLength: { value: 2, message: "Position must be at least 2 characters" },
    maxLength: {
      value: 100,
      message: "Position must not exceed 100 characters",
    },
  },

  last_update_date: { required: "Last update date is required" },

  expected_salary: {
    required: "Expected salary and Currency are required",
    minLength: { value: 3, message: "Please provide more details" },
  },

  profile_photo: {
    validate: {
      fileSize: (file) =>
        file && file.size > 5 * 1024 * 1024
          ? "Photo size must be less than 5MB"
          : true,
      fileType: (file) =>
        file && !file.type.startsWith("image/")
          ? "Only image files are allowed"
          : true,
    },
  },

  full_name: {
    required: "Full name is required",
    minLength: { value: 2, message: "Name must be at least 2 characters" },
    maxLength: { value: 100, message: "Name must not exceed 100 characters" },
    pattern: {
      value: /^[A-Za-z\s\-\\.']+$/,
      message:
        "Name can only contain letters, spaces, hyphens, dots, and apostrophes",
    },
  },

  date_of_birth: {
    required: "Date of birth is required",
    validate: {
      validAge: (value) => {
        if (!value) return true;
        const birthDate = new Date(value);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        if (
          monthDiff < 0 ||
          (monthDiff === 0 && today.getDate() < birthDate.getDate())
        ) {
          age--;
        }
        if (age < 18) return "Must be at least 18 years old";
        if (age > 70) return "Age cannot exceed 70 years";
        return true;
      },
      notFuture: (value) =>
        value && new Date(value) > new Date()
          ? "Birth date cannot be in the future"
          : true,
    },
  },

  marital_status: { required: "Marital status is required" },

  weight: {
    required: "Weight is required",
    min: { value: 40, message: "Weight must be at least 40 kg" },
    max: { value: 200, message: "Weight cannot exceed 200 kg" },
  },

  height: {
    required: "Height is required",
    min: { value: 150, message: "Height must be at least 150 cm" },
    max: { value: 220, message: "Height cannot exceed 220 cm" },
  },

  nationality: {
    required: "Nationality is required",
  },

  place_of_birth: {
    required: "Place of birth is required",
  },

  nearest_port: {
    required: "Nearest airport is required",
  },

  overall_size: {
    required: "Overall size is required",
  },
};

// ================================
// Contact Form Rules
// ================================
export const CONTACT_RULES = {
  home_address: {
    required: "Home address is required",
    minLength: {
      value: 10,
      message: "Please provide full address details",
    },
  },

  email: {
    required: "Email is required",
    pattern: {
      value: VALIDATION_PATTERNS.email,
      message: "Please enter a valid email address",
    },
  },

  mobile: {
    required: "Mobile number is required",
    pattern: {
      value: VALIDATION_PATTERNS.phone,
      message: "Please enter a valid mobile number",
    },
  },
};

// ================================
// Emergency Form Rules
// ================================
export const EMERGENCY_RULES = {
  kin_full_name: {
    required: "Next of kin name is required",
    minLength: { value: 2, message: "Name must be at least 2 characters" },
    pattern: {
      value: /^[A-Za-z\s\-\\.']+$/,
      message: "Name can only contain letters",
    },
  },

  kin_relationship: {
    required: "Relationship is required",
  },

  kin_address: {
    required: "Address is required",
  },

  kin_phone: {
    required: "Phone number is required",
    pattern: {
      value: VALIDATION_PATTERNS.phone,
      message: "Please enter a valid phone number",
    },
  },

  kin_email: {
    required: "Email is required",
    pattern: {
      value: VALIDATION_PATTERNS.email,
      message: "Please enter a valid email address",
    },
  },
};

// ================================
// Education Form Rules
// ================================
export const EDUCATION_RULES = {
  education_school: {
    required: "School name is required",
  },

  marine_issued_date: {
    required: "Date is required",
  },

  marine_result: {
    required: "Result is required",
    min: { value: 0, message: "Result must be 0-100" },
    max: { value: 100, message: "Result must be 0-100" },
  },

  marine_issued_by: {
    required: "Issuing authority is required",
  },

  marine_issued_at: {
    required: "Place of issue is required",
  },
};

// ================================
// Courses Form Rules
// ================================
export const COURSE_RULES = {
  course_name: {
    required: "Course name is required",
  },
  course_number: {
    required: "Course number is required",
    pattern: {
      value: /^[A-Za-z0-9\-\\]+$/,
      message: "Only letters, numbers, dashes and slashes are allowed",
    },
  },
  issue_date: {
    required: "Issued date is required",
  },
  expiry_date: {
    required: "Expiry date is required",
    validate: (value, formValues) => {
      if (formValues.issue_date && value < formValues.issue_date) {
        return "Expiry date cannot be earlier than issued date";
      }
      return true;
    },
  },
  issued_by: {
    required: "Issuing authority is required",
    minLength: {
      value: 2,
      message: "Must be at least 2 characters long",
    },
  },
};

// ================================
// Certificates Form Rules
// ================================

export const CERTIFICATE_RULES = {
  certificate_name: {
    required: "Certificate name is required",
    minLength: {
      value: 3,
      message: "Certificate name must be at least 3 characters long",
    },
  },
  certificate_number: {
    required: "Certificate number is required",
    pattern: {
      value: /^[A-Za-z0-9\-\\]+$/,
      message: "Only letters, numbers, dashes and slashes are allowed",
    },
  },
  issue_date: {
    required: "Issued date is required",
  },
  expiry_date: {
    required: "Expiry date is required",
    validate: (value, formValues) => {
      if (formValues.issue_date && value < formValues.issue_date) {
        return "Expiry date cannot be earlier than issued date";
      }
      return true;
    },
  },
  issued_by: {
    required: "Issuing authority is required",
    minLength: {
      value: 2,
      message: "Must be at least 2 characters long",
    },
  },
  issued_at: {
    required: "Issued location is required",
    minLength: {
      value: 2,
      message: "Must be at least 2 characters long",
    },
  },
};

// ================================
// Health Form Rules
// ================================

export const HEALTH_RULES = {
  name: {
    required: "Vaccination name is required",
    minLength: {
      value: 2,
      message: "Vaccination name must be at least 2 characters",
    },
    maxLength: {
      value: 100,
      message: "Vaccination name must not exceed 100 characters",
    },
  },
  number: {
    maxLength: { value: 50, message: "Number must not exceed 50 characters" },
  },
  issue_date: { required: "Issued date is required" },
  expiry_date: {
    required: "Expiry date is required",
    validate: (value, formValues) => {
      if (formValues.issue_date && value < formValues.issue_date) {
        return "Expiry date cannot be earlier than issued date";
      }
      if (new Date(value) <= new Date()) {
        return "Health record has expired";
      }
      return true;
    },
  },
  issued_by: {
    maxLength: {
      value: 100,
      message: "Issuer must not exceed 100 characters",
    },
  },
  issued_at: {
    maxLength: {
      value: 100,
      message: "Issued at must not exceed 100 characters",
    },
  },
  disease: {
    maxLength: {
      value: 100,
      message: "Disease name must not exceed 100 characters",
    },
  },
  first_date: {},
  last_date: {},
  remarks: {
    maxLength: {
      value: 200,
      message: "Remarks must not exceed 200 characters",
    },
  },
};

// ================================
// Sea Services & Work Experience Form Rules
// ================================

export const SEA_SERVICE_RULES = {
  company_name: { required: "Company name is required" },
  rank: { required: "Rank is required" },
  vessel_name_imo: {
    required: "Vessel name is required",
    maxLength: {
      value: 50,
      message: "Vessel name must not exceed 50 characters",
    },
    pattern: {
      value: /^[A-Za-z0-9\s\-\\.]+$/,
      message: "Invalid vessel name format",
    },
  },
  signed_on: { required: "Sign-on date is required" },
  signed_off: {
    required: "Sign-off date is required",
    validate: (value, formValues) => {
      if (formValues.signed_on && value <= formValues.signed_on) {
        return "Sign-off date must be after sign-on date";
      }
      return true;
    },
  },
};

// ================================
// Documents Form Rules
// ================================
export const DOCUMENT_RULES = {
  document_type: {
    required: "Document type is required",
  },
  document_number: {
    required: "Document number is required",
    minLength: {
      value: 5,
      message: "Document number must be at least 5 characters",
    },
    maxLength: {
      value: 20,
      message: "Document number must not exceed 20 characters",
    },
    validate: {
      passportFormat: (value, formValues) => {
        if (
          formValues?.document_type === "passport" &&
          !VALIDATION_PATTERNS.passport.test(value)
        ) {
          return "Invalid passport number format";
        }
        if (
          formValues?.document_type === "seaman_book" &&
          !VALIDATION_PATTERNS.seamanBook.test(value)
        ) {
          return "Invalid seaman book number format";
        }
        return true;
      },
    },
  },
  issue_date: {
    required: "Issued date is required",
    validate: {
      notFuture: (value) =>
        value && new Date(value) > new Date()
          ? "Issued date cannot be in the future"
          : true,
    },
  },
  expiry_date: {
    required: "Expiry date is required",
    validate: {
      afterIssued: (value, formValues) => {
        if (!value || !formValues?.issue_date) return true;
        return new Date(value) > new Date(formValues.issue_date)
          ? true
          : "Expiry date must be after issued date";
      },
      notPast: (value) =>
        value && new Date(value) <= new Date()
          ? "Document has already expired"
          : true,
    },
  },
  issuing_authority: {
    required: "Issuing authority is required",
    maxLength: {
      value: 100,
      message: "Authority must not exceed 100 characters",
    },
  },
};

// ================================
// Step field mapping
// ================================
export const STEP_FIELDS = {
  0: {
    name: "Position & Personal Information",
    fields: [
      "application_for_position",
      "available_date",
      "expected_salary",
      "full_name",
      "date_of_birth",
      "marital_status",
      "weight",
      "height",
      "nationality",
      "overall_size",
      "place_of_birth",
      "nearest_port",
    ],
  },
  1: {
    name: "Education Details",
    fields: [
      "education_school",
    ],
  },
  2: {
    name: "Contact Information",
    fields: ["home_address", "email", "mobile"],
  },
  3: {
    name: "Emergency Contact",
    fields: [
      "kin_full_name",
      "kin_relationship",
      "kin_address",
      "kin_phone",
      "kin_email",
    ],
  },
  4: {
    name: "Travel Documents",
    fields: ["documents"],
  },
  5: {
    name: "Professional Certificates",
    fields: ["licenses"],
  },
  6: {
    name: "Health & Vaccination",
    fields: ["health"],
  },
  7: {
    name: "Marine Courses",
    fields: ["courses"],
  },
  8: {
    name: "Sea Service & Experience",
    fields: ["sea_services"],
  },
  9: {
    name: "References",
    fields: ["references"],
  },
  10: {
    name: "Declaration",
    fields: ["declaration"],
  },
};

// ================================
// Dynamic Array Rules
// ================================
export const DYNAMIC_ARRAY_RULES = {
  documents: {
    validate: {
      hasItems: (value) =>
        !Array.isArray(value) || value.length === 0
          ? "At least one travel document is required"
          : true,
      validItems: (value) => {
        if (!Array.isArray(value)) return true;
        for (let i = 0; i < value.length; i++) {
          const doc = value[i];
          if (!doc.document_type) return `Document ${i + 1}: Type is required`;
          if (!doc.document_number) return `Document ${i + 1}: Number is required`;
          if (!doc.expiry_date)
            return `Document ${i + 1}: Expiry date is required`;
          const expiryDate = new Date(doc.expiry_date);
          if (expiryDate <= new Date())
            return `Document ${i + 1}: Document has expired`;
          if (
            doc.document_type === "passport" &&
            !VALIDATION_PATTERNS.passport.test(doc.document_number)
          ) {
            return `Document ${i + 1}: Invalid passport number format`;
          }
        }
        return true;
      },
    },
  },

  certificates: {
    validate: {
      hasItems: (value) =>
        !Array.isArray(value) || value.length === 0
          ? "At least one professional certificate is required"
          : true,
      validItems: (value) => {
        if (!Array.isArray(value)) return true;
        for (let i = 0; i < value.length; i++) {
          const cert = value[i];
          if (!cert.certificate_name)
            return `Certificate ${i + 1}: Name is required`;
          if (!cert.expiry_date)
            return `Certificate ${i + 1}: Expiry date is required`;
          const expiryDate = new Date(cert.expiry_date);
          if (expiryDate <= new Date())
            return `Certificate ${i + 1}: Certificate has expired`;
        }
        return true;
      },
    },
  },

  courses: {
    validate: {
      hasItems: (value) =>
        !Array.isArray(value) || value.length === 0
          ? "At least one course is required"
          : true,
      validItems: (value) => {
        if (!Array.isArray(value)) return true;
        for (let i = 0; i < value.length; i++) {
          const c = value[i];
          if (!c.course_name) return `Course ${i + 1}: Name is required`;
          if (!c.expiry_date) return `Course ${i + 1}: Expiry date is required`;
          const expiryDate = new Date(c.expiry_date);
          if (expiryDate <= new Date())
            return `Course ${i + 1}: Course has expired`;
        }
        return true;
      },
    },
  },

  health: {
    validate: {
      hasItems: (value) =>
        !Array.isArray(value) || value.length === 0
          ? "At least one health record is required"
          : true,
      validItems: (value) => {
        if (!Array.isArray(value)) return true;
        for (let i = 0; i < value.length; i++) {
          const h = value[i];
          if (!h.name)
            return `Health Record ${i + 1}: Vaccination name is required`;
          if (!h.expiry_date)
            return `Health Record ${i + 1}: Expiry date is required`;
          const expiryDate = new Date(h.expiry_date);
          if (expiryDate <= new Date())
            return `Health Record ${i + 1}: Record has expired`;
        }
        return true;
      },
    },
  },

  sea_services: {
    validate: {
      hasItems: (value) =>
        !Array.isArray(value) || value.length === 0
          ? "At least one sea service record is required"
          : true,
      validItems: (value) => {
        if (!Array.isArray(value)) return true;
        for (let i = 0; i < value.length; i++) {
          const s = value[i];
          if (!s.company_name)
            return `Sea Service ${i + 1}: Company name is required`;
          if (!s.rank) return `Sea Service ${i + 1}: Rank is required`;
          if (!s.vessel_name)
            return `Sea Service ${i + 1}: Vessel name is required`;
          if (!s.signed_on)
            return `Sea Service ${i + 1}: Sign-on date is required`;
          if (!s.signed_off)
            return `Sea Service ${i + 1}: Sign-off date is required`;
          const signedOver = new Date(s.signed_on);
          const signedOff = new Date(s.signed_off);
          if (signedOff <= signedOver)
            return `Sea Service ${i + 1
              }: Sign-off date must be after sign-on date`;
        }
        return true;
      },
    },
  },
};
