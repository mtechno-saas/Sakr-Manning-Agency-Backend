// utils/dashboard/fieldConfigs.js - FINAL PRODUCTION VERSION
/**
 * Centralized Field Configurations for All Dashboard Modals
 * 
 * This file contains field definitions for all form modals in the dashboard.
 * Each modal exports its field configuration array which includes:
 * - Field metadata (name, label, type)
 * - Component to render
 * - Validation rules
 * - Default values
 * - Transform functions
 * @module fieldConfigs
 * @version 1.0.0
 */

// ============================================
// FIELD CONFIGURATION STRUCTURE
// ============================================
/**
 * Field Configuration Object Structure:
 * 
 * {
 *   name: string              - Field name (matches formData key)
 *   label: string             - Display label
 *   type: string              - Input type (text, email, number, select, date, typeahead, textarea, checkbox-array, time, url, tel)
 *   component: string         - Component name to use (BaseInput, Select, DateInput, TypeaheadInput, TextArea, CheckboxArray)
 *   required: boolean         - Is field required
 *   placeholder: string       - Placeholder text
 *   options: array            - Options for select/multiselect/checkbox-array
 *   validation: object        - Validation rules
 *   props: object             - Additional props for component
 *   defaultValue: any         - Default value for new records
 *   transformOnSave: function - Transform value before saving
 *   conditionalDisplay: func  - Function to determine if field should display
 *   dependsOn: string         - Field name this field depends on
 * }
 */

// ============================================
// COMPANY FORM FIELDS
// ============================================

export const COMPANY_FORM_FIELDS = [
  {
    name: "company_name",
    label: "Company Name",
    type: "text",
    component: "BaseInput",
    required: true,
    placeholder: "Enter the Company Name",
    gridCols: 9,
    validation: {
      required: "Company name is required",
      minLength: { value: 2, message: "Company name must be at least 2 characters" },
    },
    defaultValue: "",
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Status",
    gridCols: 3,
    options: [
      { value: "Active", label: "Active" },
      { value: "Inactive", label: "Inactive" },
      { value: "Prospect", label: "Prospect" },
    ],
    validation: {
      required: "Status is required",
    },
    defaultValue: "Active",
  },
  {
    name: "company_type",
    label: "Company Type",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Type",
    gridCols: 9,
    options: [
      { value: "Shipping Manning Companies", label: "Shipping Manning Companies" },
      { value: "Cargo Manning Companies", label: "Cargo Manning Companies" },
      { value: "Cruise & Hospitality Manning Companies", label: "Cruise & Hospitality Manning Companies" },
      { value: "Offshore & Oil/Gas Manning Companies", label: "Offshore & Oil/Gas Manning Companies" },
      { value: "Fishing Fleet Manning Companies", label: "Fishing Fleet Manning Companies" },
      { value: "General Crew Manning Companies", label: "General Crew Manning Companies" },
      { value: "Specialized Marine Manning Companies", label: "Specialized Marine Manning Companies" },
      { value: "Temporary / Contract Manning Agencies", label: "Temporary / Contract Manning Agencies" },
      { value: "Full Crew Management Companies", label: "Full Crew Management Companies" },
    ],
    validation: {
      required: "Company type is required",
    },
    defaultValue: "",
  },
  // {
  //   name: "hourly_rate",
  //   label: "Hourly Rate",
  //   type: "number",
  //   component: "BaseInput",
  //   required: true,
  //   placeholder: "0.00",
  //   gridCols: 4,
  //   props: {
  //     step: "0.01",
  //     min: "0",
  //   },
  //   validation: {
  //     required: "Hourly rate is required",
  //     min: { value: 0, message: "Hourly rate cannot be negative" },
  //   },
  //   defaultValue: "",
  //   transformOnSave: (value) => parseFloat(value),
  // },
  {
    name: "company_flag",
    label: "Country Flag",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select country",
    gridCols: 3,
    options: [
      "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia",
      "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium",
      "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil",
      "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada",
      "Cape Verde", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros",
      "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti",
      "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea",
      "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Gambia",
      "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
      "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq",
      "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
      "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
      "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives",
      "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia",
      "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia",
      "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea",
      "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama",
      "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar",
      "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
      "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe",
      "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia",
      "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan",
      "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan",
      "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago",
      "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates",
      "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City",
      "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
    ].map((c) => ({ value: c, label: c })),
    validation: {},
    defaultValue: "",
  },
  {
    name: "contact_email",
    label: "Contact Email",
    type: "email",
    component: "BaseInput",
    required: true,
    placeholder: "info@company.com",
    gridCols: 5,
    validation: {
      required: "Email is required",
      pattern: {
        value: /\S+@\S+\.\S+/,
        message: "Invalid email format",
      },
    },
    defaultValue: "",
  },
  {
    name: "website",
    label: "Website",
    type: "url",
    component: "BaseInput",
    required: false,
    placeholder: "https://www.company.com",
    gridCols: 5,
    validation: {
      pattern: {
        value: /^(https?:\/\/)?[\w.-]+\.[a-z]{2,}(\/.*)*/i,
        message: "Please enter a valid URL",
      },
    },
    defaultValue: "",
  },
  {
    name: "open_positions",
    label: "Open Positions",
    type: "number",
    component: "BaseInput",
    required: false,
    placeholder: "0",
    gridCols: 2,
    props: {
      min: "0",
    },
    validation: {
      min: { value: 0, message: "Cannot be negative" },
    },
    defaultValue: 0,
    transformOnSave: (value) => parseInt(value, 10),
  },
];

// ============================================
// SHIP FORM FIELDS
// ============================================

export const SHIP_FORM_FIELDS = [
  {
    name: "ship_name",
    label: "Ship Name",
    type: "text",
    component: "BaseInput",
    required: true,
    placeholder: "M/V Ocean Voyager",
    gridCols: 9,
    validation: {
      required: "Ship name is required",
      minLength: { value: 2, message: "Ship name must be at least 2 characters" },
    },
    defaultValue: "",
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select Status",
    gridCols: 3,
    options: [
      { value: "Active", label: "Active" },
      { value: "Under Maintenance", label: "Under Maintenance" },
      { value: "Inactive", label: "Inactive" },
    ],
    validation: {},
    defaultValue: "Active",
  },
  {
    name: "company",
    label: "Company",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Company",
    gridCols: 6,
    validation: {
      required: "Company is required",
    },
    // options will be loaded dynamically from context
    options: [],
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "builder",
    label: "Builder",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "Hyundai Heavy Industries",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
  {
    name: "crew",
    label: "Crew Members (Seafarers)",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select Crew Members",
    gridCols: 12,
    props: {
      isMulti: true, // For our Select component to handle multiple
    },
    // options will be loaded dynamically from context (users)
    options: [],
    defaultValue: [],
    transformOnLoad: (val) => {
      // Backend returns list of objects for ManyToMany
      if (Array.isArray(val)) {
        return val.map(v => typeof v === 'object' ? v.id : v);
      }
      return val || [];
    },
    transformOnSave: (val) => {
      // Backend expects list of IDs for ManyToMany during update
      if (Array.isArray(val)) {
        return val.map(v => typeof v === 'object' ? v.id : v);
      }
      return [];
    }
  },
  {
    name: "ship_type",
    label: "Ship Type",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Ship Type",
    gridCols: 4,
    validation: {
      required: "Ship type is required",
    },
    // options will be loaded dynamically
    options: [],
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "flag",
    label: "Flag",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Flag",
    gridCols: 4,
    validation: {
      required: "Flag is required",
    },
    // options will be loaded dynamically from context
    options: [],
    defaultValue: "",
  },
  {
    name: "imo_number",
    label: "IMO Number",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "1234567",
    gridCols: 4,
    validation: {
      pattern: {
        value: /^\d{7}$/,
        message: "IMO number must be exactly 7 digits",
      },
    },
    props: {
      maxLength: 7,
    },
    defaultValue: "",
  },
  {
    name: "mmsi_no",
    label: "MMSI Number",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "622123456",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
  {
    name: "official_no",
    label: "Official Number",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "EG-2024-001",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
  {
    name: "engine_type",
    label: "Engine Type",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "MAN B&W",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
  {
    name: "engine_power_kw",
    label: "Engine Power (kW)",
    type: "number",
    component: "BaseInput",
    required: false,
    placeholder: "12000",
    gridCols: 6,
    props: { min: "0" },
    validation: { min: { value: 0, message: "Cannot be negative" } },
    defaultValue: "",
    transformOnSave: (v) => parseInt(v, 10) || 0,
  },
  {
    name: "gross_tonnage",
    label: "Gross Tonnage",
    type: "number",
    component: "BaseInput",
    required: false,
    placeholder: "50000",
    gridCols: 4,
    validation: {
      min: { value: 0, message: "Cannot be negative" },
    },
    props: {
      min: "0",
    },
    defaultValue: 0,
    transformOnSave: (value) => parseInt(value, 10) || 0,
  },
  {
    name: "year_built",
    label: "Year Built",
    type: "number",
    component: "BaseInput",
    required: false,
    placeholder: "2020",
    gridCols: 4,
    validation: {
      min: { value: 1900, message: "Year must be after 1900" },
      max: { value: new Date().getFullYear(), message: "Year cannot be in the future" },
    },
    props: {
      min: "1900",
      max: new Date().getFullYear(),
    },
    defaultValue: "",
  },
  {
    name: "deadweight",
    label: "Deadweight (DWT)",
    type: "number",
    component: "BaseInput",
    required: false,
    placeholder: "22000",
    gridCols: 4,
    props: { min: "0" },
    validation: { min: { value: 0, message: "Cannot be negative" } },
    defaultValue: "",
    transformOnSave: (v) => parseInt(v, 10) || 0,
  },
  {
    name: "call_sign",
    label: "Call Sign",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "SUAN2",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
  {
    name: "port_of_registry",
    label: "Port of Registry",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "Alexandria",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
];

// ============================================
// USER FORM FIELDS
// ============================================

export const USER_FORM_FIELDS = [
  {
    name: "email",
    label: "Email",
    type: "email",
    component: "BaseInput",
    required: true,
    placeholder: "john.doe@example.com",
    gridCols: 12,
    validation: {
      required: "Email is required",
      pattern: {
        value: /\S+@\S+\.\S+/,
        message: "Invalid email format",
      },
    },
    defaultValue: "",
  },
  {
    name: "first_name",
    label: "First Name",
    type: "text",
    component: "BaseInput",
    required: true,
    placeholder: "John",
    gridCols: 6,
    validation: {
      required: "First name is required",
      minLength: { value: 2, message: "First name must be at least 2 characters" },
    },
    defaultValue: "",
  },
  {
    name: "middle_name",
    label: "Middle Name",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "Robert",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
  {
    name: "phone_number",
    label: "Phone Number",
    type: "tel",
    component: "BaseInput",
    required: true,
    placeholder: "+1234567890",
    gridCols: 6,
    validation: {
      required: "Phone number is required",
    },
    defaultValue: "",
  },
  {
    name: "nationality",
    label: "Nationality",
    type: "text",
    component: "SuggestionInput",
    required: false,
    placeholder: "Egyptian",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
  {
    name: "date_of_birth",
    label: "Date of Birth",
    type: "date",
    component: "DateInput",
    required: false,
    placeholder: "Select date",
    gridCols: 6,
    validation: {},
    defaultValue: "",
  },
  {
    name: "marital_status",
    label: "Marital Status",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select status",
    gridCols: 6,
    options: [
      { value: "SINGLE", label: "Single" },
      { value: "MARRIED", label: "Married" },
    ],
    validation: {},
    defaultValue: "SINGLE",
  },
  {
    name: "user_status",
    label: "Availability Status",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Status",
    gridCols: 12,
    options: [
      { value: "ON_SITE", label: "ON_SITE" },
      { value: "VACATION", label: "VACATION" },
      { value: "MEDICAL VACATION", label: "MEDICAL VACATION" },
    ],
    validation: {
      required: "Status is required",
    },
    defaultValue: "VACATION",
  },

  {
    name: "rank_ids",
    label: "Ranks",
    type: "checkbox-array",
    component: "CheckboxArray",
    required: false,
    gridCols: 12,
    validation: {},
    options: [], // Will be loaded dynamically
    defaultValue: [],
    transformOnLoad: (val, record) => {
      const source = val || record?.ranks || [];
      return Array.isArray(source)
        ? source.map((i) => (i?.rank_name || i?.name || i?.rank?.name || i))
        : [];
    },
  },
];

// ============================================
// INTERVIEW FORM FIELDS
// ============================================

export const INTERVIEW_FORM_FIELDS = [
  {
    name: "candidate",
    label: "Candidate",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Candidate",
    gridCols: 12,
    validation: {
      required: "Candidate is required",
    },
    options: [], // Will be loaded from context
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "company",
    label: "Company",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Company",
    gridCols: 6,
    validation: {
      required: "Company is required",
    },
    options: [], // Will be loaded from context
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "position",
    label: "Position",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select Position (Rank)",
    gridCols: 6,
    validation: {},
    options: [], // Will be loaded from context
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "scheduled_date",
    label: "Interview Date",
    type: "date",
    component: "DateInput",
    required: true,
    placeholder: "Select date",
    gridCols: 6,
    validation: {
      required: "Date is required",
    },
    props: {
      min: new Date().toISOString().split("T")[0],
    },
    defaultValue: "",
    transformOnLoad: (val) => {
      if (!val || typeof val !== "string") return val;
      const separator = val.includes("T") ? "T" : " ";
      return val.split(separator)[0];
    },
  },
  {
    name: "scheduled_time",
    label: "Interview Time",
    type: "time",
    component: "BaseInput",
    required: true,
    placeholder: "Select time",
    gridCols: 6,
    validation: {
      required: "Time is required",
    },
    defaultValue: "",
    transformOnLoad: (val, record) => {
      const dateTime = record?.scheduled_date;

      // 1. Try extracting from combined date-time field first (most reliable)
      if (dateTime && typeof dateTime === "string" && (dateTime.includes("T") || dateTime.includes(" "))) {
        const separator = dateTime.includes("T") ? "T" : " ";
        const parts = dateTime.split(separator);
        if (parts.length >= 2 && parts[1].includes(":")) {
          return parts[1].substring(0, 5);
        }
      }

      // 2. Fallback to direct time field if it looks valid
      if (val && typeof val === "string" && val.includes(":")) {
        return val.substring(0, 5);
      }

      // 3. Fallback to dateTime itself if it's just a time string
      if (dateTime && typeof dateTime === "string" && dateTime.includes(":")) {
        return dateTime.substring(0, 5);
      }

      return "";
    },
  },
  {
    name: "duration_minutes",
    label: "Duration",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select duration",
    gridCols: 6,
    options: [
      { value: 15, label: "15 minutes" },
      { value: 30, label: "30 minutes" },
      { value: 45, label: "45 minutes" },
      { value: 60, label: "1 hour" },
      { value: 90, label: "1.5 hours" },
      { value: 120, label: "2 hours" },
    ],
    validation: {},
    defaultValue: 45,
    transformOnSave: (value) => parseInt(value, 10),
  },
  {
    name: "interview_type",
    label: "Interview Type",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select type",
    gridCols: 6,
    options: [
      { value: "Video", label: "Video Call" },
      { value: "Phone", label: "Phone Call" },
      { value: "In-person", label: "In-Person" },
    ],
    validation: {},
    defaultValue: "Video",
  },
  {
    name: "meeting_link",
    label: "Meeting Link (Optional)",
    type: "url",
    component: "BaseInput",
    required: false,
    placeholder: "https://teams.microsoft.com/meet/...",
    gridCols: 12,
    validation: {
      pattern: {
        value: /^https?:\/\/.+/,
        message: "Please enter a valid URL",
      },
    },
    defaultValue: "",
    conditionalDisplay: (formData) => formData.interview_type === "Video",
  },
  {
    name: "location",
    label: "Location / Office",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "e.g., Cairo Office or Meeting Room 1",
    gridCols: 6,
    defaultValue: "",
  },
  {
    name: "interviewer_name",
    label: "Interviewer Name",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "e.g., Capt. Ali",
    gridCols: 6,
    defaultValue: "",
  },
  {
    name: "interviewer_email",
    label: "Interviewer Email",
    type: "email",
    component: "BaseInput",
    required: false,
    placeholder: "ali@example.com",
    gridCols: 6,
    defaultValue: "",
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select status",
    gridCols: 6,
    options: [
      { value: "Scheduled", label: "Scheduled" },
      { value: "Completed", label: "Completed" },
      { value: "Cancelled", label: "Cancelled" },
      { value: "Rescheduled", label: "Rescheduled" },
    ],
    validation: {},
    defaultValue: "Scheduled",
  },
  {
    name: "notes",
    label: "Notes (Optional)",
    type: "textarea",
    component: "TextArea",
    required: false,
    placeholder: "Additional notes about the interview...",
    gridCols: 12,
    props: {
      minHeight: 80,
    },
    validation: {},
    defaultValue: "",
  },
];

// ============================================
// FINANCE FORM FIELDS
// ============================================

export const FINANCE_FORM_FIELDS = [
  {
    name: "user",
    label: "User",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select User",
    gridCols: 12,
    validation: {
      required: "User is required",
    },
    options: [], // Loaded from context
    defaultValue: "",
  },
  {
    name: "company",
    label: "Company",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Company",
    gridCols: 12,
    validation: {
      required: "Company is required",
    },
    options: [], // Loaded from context
    defaultValue: "",
  },
  {
    name: "start_date",
    label: "Start Date",
    type: "date",
    component: "DateInput",
    required: true,
    placeholder: "Select start date",
    gridCols: 6,
    validation: {
      required: "Start date is required",
    },
    defaultValue: "",
  },
  {
    name: "end_date",
    label: "End Date",
    type: "date",
    component: "DateInput",
    required: true,
    placeholder: "Select end date",
    gridCols: 6,
    validation: {
      required: "End date is required",
      custom: (value, formData) => {
        if (value && formData.start_date && value < formData.start_date) {
          return "End date must be after start date";
        }
        return null;
      },
    },
    defaultValue: "",
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select status",
    gridCols: 12,
    options: [
      { value: "Cancelled", label: "Cancelled" },
      { value: "Overdue", label: "Overdue" },
      { value: "Paid", label: "Paid" },
      { value: "Pending", label: "Pending" },
    ],
    validation: {
      required: "Status is required",
    },
    defaultValue: "",
  },
];

// ============================================
// DOCUMENT FORM FIELDS
// ============================================

export const DOCUMENT_FORM_FIELDS = [
  {
    name: "user",
    label: "User (Seafarer)",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select User",
    gridCols: 12,
    validation: {
      required: "User is required",
    },
    options: [], // Loaded from context
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "company",
    label: "Company",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Company",
    gridCols: 6,
    validation: {
      required: "Company is required",
    },
    options: [], // Loaded from context
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "ship",
    label: "Ship (Optional)",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select Ship (Optional)",
    gridCols: 6,
    validation: {},
    options: [], // Loaded based on company selection
    defaultValue: "",
    dependsOn: "company",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "rank",
    label: "Rank",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Rank",
    gridCols: 6,
    validation: {
      required: "Rank is required",
    },
    options: [], // Will be loaded from context
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "sign_on_date",
    label: "Sign-On Date",
    type: "date",
    component: "DateInput",
    required: true,
    placeholder: "Select sign-on date",
    gridCols: 6,
    validation: {
      required: "Sign-on date is required",
    },
    defaultValue: "",
  },
  {
    name: "sign_off_date",
    label: "Sign-Off Date",
    type: "date",
    component: "DateInput",
    required: true,
    placeholder: "Select sign-off date",
    gridCols: 6,
    validation: {
      required: "Sign-off date is required",
      custom: (value, formData) => {
        if (value && formData.sign_on_date && value <= formData.sign_on_date) {
          return "Sign-off date must be after sign-on date";
        }
        if (value && formData.sign_on_date) {
          const start = new Date(formData.sign_on_date);
          const end = new Date(value);
          const diffDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
          if (diffDays < 30) {
            return "Contract duration should be at least 1 month";
          }
        }
        return null;
      },
    },
    props: {
      minDependsOn: "sign_on_date",
    },
    defaultValue: "",
  },
  {
    name: "salary",
    label: "Salary",
    type: "number",
    component: "BaseInput",
    required: true,
    placeholder: "5500.00",
    gridCols: 4,
    validation: {
      required: "Salary is required",
      min: { value: 0, message: "Salary must be positive" },
    },
    props: {
      step: "0.01",
      min: "0",
    },
    defaultValue: "",
    transformOnSave: (value) => parseFloat(value).toFixed(2),
  },
  {
    name: "currency",
    label: "Currency",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "USD",
    gridCols: 4,
    options: [
      { value: "USD", label: "USD" },
      { value: "EUR", label: "EUR" },
      { value: "GBP", label: "GBP" },
      { value: "EGP", label: "EGP" },
      { value: "AED", label: "AED" },
      { value: "SAR", label: "SAR" },
      { value: "AUD", label: "AUD" },
      { value: "CAD", label: "CAD" },
      { value: "CHF", label: "CHF" },
    ],
    validation: {},
    defaultValue: "USD",
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select status",
    gridCols: 4,
    options: [
      { value: "Pending Signature", label: "Pending Signature" },
      { value: "Signed", label: "Signed" },
      { value: "Draft", label: "Draft" },
      { value: "Expired", label: "Expired" },
      { value: "Cancelled", label: "Cancelled" },
    ],
    validation: {},
    defaultValue: "Pending Signature",
  },
];

// ============================================
// RANK FORM FIELDS
// ============================================

export const RANK_FORM_FIELDS = [
  {
    name: "rank_name",
    label: "Rank Name",
    type: "text",
    component: "BaseInput",
    required: true,
    placeholder: "e.g., Master",
    gridCols: 6,
    validation: {
      required: "Rank name is required",
    },
    defaultValue: "",
  },
  {
    name: "rank_code",
    label: "Rank Code",
    type: "text",
    component: "BaseInput",
    required: true,
    placeholder: "e.g., MST",
    gridCols: 6,
    validation: {
      required: "Rank code is required",
    },
    defaultValue: "",
  },
];

// ============================================
// CV FORM FIELDS (Documents Management - Section 2)
// ============================================

export const CV_FORM_FIELDS = [
  {
    name: "name",
    label: "Full Name",
    type: "text",
    component: "BaseInput",
    required: true,
    placeholder: "e.g., John Doe",
    gridCols: 12,
    validation: {
      required: "Full name is required",
      minLength: { value: 2, message: "Name must be at least 2 characters" },
    },
    defaultValue: "",
  },
  {
    name: "email",
    label: "Email Address",
    type: "email",
    component: "BaseInput",
    required: true,
    placeholder: "john@example.com",
    gridCols: 6,
    validation: {
      required: "Email is required",
      pattern: {
        value: /\S+@\S+\.\S+/,
        message: "Invalid email format",
      },
    },
    defaultValue: "",
  },
  {
    name: "phone_number",
    label: "Phone Number",
    type: "tel",
    component: "BaseInput",
    required: true,
    placeholder: "+1234567890",
    gridCols: 6,
    validation: {
      required: "Phone number is required",
    },
    defaultValue: "",
  },
  {
    name: "position",
    label: "Position / Rank",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Position (Rank)",
    options: [], // Will be loaded dynamically
    gridCols: 6,
    validation: {
      required: "Position is required",
    },
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Status",
    gridCols: 6,
    options: [
      { value: "Pending", label: "Pending" },
      { value: "Active", label: "Active" },
      { value: "Blacklist", label: "Blacklist" },
    ],
    validation: {
      required: "Status is required",
    },
    defaultValue: "Pending",
  },
  {
    name: "file",
    label: "CV File",
    type: "file",
    component: "BaseInput",
    required: true, // Required for creation
    placeholder: "Choose CV file...",
    gridCols: 12,
    props: {
      type: "file",
      accept: ".pdf,.doc,.docx",
    },
    validation: {
      required: "CV file is required",
    },
    defaultValue: null,
  },
];

// ============================================
// CV SUBMISSION FORM FIELDS (Pipeline - Section 4)
// ============================================

export const CV_SUBMISSION_FORM_FIELDS = [
  {
    name: "user",
    label: "Seafarer",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Seafarer",
    gridCols: 12,
    validation: { required: "Seafarer is required" },
    options: [], // Loaded dynamically
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "company",
    label: "Applying to Company",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select Company",
    gridCols: 6,
    validation: {},
    options: [], // Loaded dynamically
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "position",
    label: "Position (Rank)",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select Position",
    gridCols: 6,
    validation: {},
    options: [], // Loaded dynamically
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "status",
    label: "Pipeline Status",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Status",
    gridCols: 4,
    options: [
      { value: "Pending", label: "Pending" },
      { value: "Under Review", label: "Under Review" },
      { value: "Interviewed", label: "Interviewed" },
      { value: "Shortlisted", label: "Shortlisted" },
      { value: "Approved", label: "Approved" },
      { value: "Hired", label: "Hired" },
      { value: "Rejected", label: "Rejected" },
    ],
    validation: { required: "Status is required" },
    defaultValue: "Pending",
  },
  {
    name: "salary",
    label: "Salary / Expectations",
    type: "text",
    component: "BaseInput",
    required: false,
    placeholder: "e.g., 5000 USD",
    gridCols: 4,
    validation: {},
    defaultValue: "",
  },
  {
    name: "experience_years",
    label: "Experience Years",
    type: "number",
    component: "BaseInput",
    required: false,
    placeholder: "0",
    gridCols: 4,
    props: { min: "0" },
    validation: { min: { value: 0, message: "Cannot be negative" } },
    defaultValue: 0,
    transformOnSave: (v) => parseInt(v, 10) || 0,
  },
];

export const JOB_ORDER_FORM_FIELDS = [
  {
    name: "reference_number",
    label: "Reference Number",
    type: "text",
    component: "BaseInput",
    required: true,
    placeholder: "e.g. JO-2024-001",
    gridCols: 12,
    validation: {
      required: "Reference number is required",
    },
    defaultValue: "",
  },
  {
    name: "company",
    label: "Company",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Company",
    gridCols: 6,
    validation: {
      required: "Company is required",
    },
    options: [], // Loaded from context
    defaultValue: "",
  },
  {
    name: "ship",
    label: "Ship (Optional)",
    type: "select",
    component: "Select",
    required: false,
    placeholder: "Select Ship",
    gridCols: 6,
    options: [], // Loaded from context
    defaultValue: "",
  },
  {
    name: "request_date",
    label: "Request Date",
    type: "date",
    component: "DateInput",
    required: true,
    gridCols: 6,
    validation: {
      required: "Request date is required",
    },
    defaultValue: new Date().toISOString().split('T')[0],
  },
  {
    name: "target_joining_date",
    label: "Target Joining Date",
    type: "date",
    component: "DateInput",
    required: true,
    gridCols: 6,
    validation: {
      required: "Joining date is required",
    },
    defaultValue: "",
  },
  {
    name: "vessel_type_override",
    label: "Vessel Type Override (Optional)",
    type: "text",
    component: "BaseInput",
    gridCols: 6,
    placeholder: "Override default vessel type",
    defaultValue: "",
  },
  {
    name: "trading_area",
    label: "Trading Area",
    type: "text",
    component: "BaseInput",
    gridCols: 6,
    placeholder: "e.g. Mediterranean",
    defaultValue: "",
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Status",
    gridCols: 6,
    options: [
      { value: "Pending", label: "Pending" },
      { value: "Open", label: "Open" },
      { value: "Active", label: "Active" },
      { value: "In Progress", label: "In Progress" },
      { value: "Fulfilled", label: "Fulfilled" },
      { value: "Cancelled", label: "Cancelled" },
    ],
    validation: {
      required: "Status is required",
    },
    defaultValue: "Pending",
  },
  {
    name: "notes",
    label: "Notes",
    type: "textarea",
    component: "TextArea",
    gridCols: 12,
    placeholder: "Additional internal notes...",
    defaultValue: "",
  },
];

// ============================================
// JOB POSITION FORM FIELDS
// ============================================

export const JOB_POSITION_FORM_FIELDS = [
  {
    name: "rank",
    label: "Rank",
    type: "select",
    component: "Select",
    required: true,
    placeholder: "Select Rank",
    validation: {
      required: "Rank is required",
    },
    options: [], // Loaded from context
    defaultValue: "",
    transformOnLoad: (val) => (val && typeof val === "object" ? val.id : val),
  },
  {
    name: "quantity",
    label: "Quantity",
    type: "number",
    component: "BaseInput",
    required: true,
    props: { min: "1" },
    defaultValue: 1,
    transformOnSave: (val) => parseInt(val, 10),
  },
  {
    name: "salary_min",
    label: "Salary Min",
    type: "number",
    component: "BaseInput",
    props: { min: "0", step: "0.01" },
    defaultValue: "",
    transformOnSave: (val) => val ? parseFloat(val) : null,
  },
  {
    name: "salary_max",
    label: "Salary Max",
    type: "number",
    component: "BaseInput",
    props: { min: "0", step: "0.01" },
    defaultValue: "",
    transformOnSave: (val) => val ? parseFloat(val) : null,
  },
  {
    name: "currency",
    label: "Currency",
    type: "text",
    component: "BaseInput",
    defaultValue: "USD",
  },
  {
    name: "contract_duration_months",
    label: "Duration (Months)",
    type: "number",
    component: "BaseInput",
    props: { min: "1" },
    defaultValue: 6,
    transformOnSave: (val) => parseInt(val, 10),
  },
  {
    name: "remarks",
    label: "Remarks",
    type: "textarea",
    component: "TextArea",
    placeholder: "Specific requirements for this position...",
    defaultValue: "",
  },
];

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get default form values from field config
 * @param {Array} fieldConfig - Field configuration array
 * @returns {Object} Default values object
 * 
 * @example
 * const defaults = getDefaultValues(COMPANY_FORM_FIELDS);
 * // { company_name: "", status: "Active", ... }
 */
export const getDefaultValues = (fieldConfig) => {
  return fieldConfig.reduce((acc, field) => {
    acc[field.name] = field.defaultValue !== undefined ? field.defaultValue : "";
    return acc;
  }, {});
};

/**
 * Populate form data from existing record
 * @param {Object} record - Existing record
 * @param {Array} fieldConfig - Field configuration array
 * @returns {Object} Populated form data
 * 
 * @example
 * const formData = populateFormData(existingCompany, COMPANY_FORM_FIELDS);
 */
export const populateFormData = (record, fieldConfig) => {
  if (!record) return getDefaultValues(fieldConfig);

  return fieldConfig.reduce((acc, field) => {
    let value = record[field.name];

    // Apply custom transformation if defined
    if (field.transformOnLoad) {
      value = field.transformOnLoad(value, record);
    }

    // Default to field's default value if undefined in record
    acc[field.name] = (value !== undefined && value !== null)
      ? value
      : field.defaultValue;

    return acc;
  }, {});
};

/**
 * Validate form data against field config
 * @param {Object} formData - Form data to validate
 * @param {Array} fieldConfig - Field configuration array
 * @returns {Object} Errors object (empty if no errors)
 * 
 * @example
 * const errors = validateFormData(formData, COMPANY_FORM_FIELDS);
 * if (Object.keys(errors).length === 0) {
 *   // Form is valid
 * }
 */
export const validateFormData = (formData, fieldConfig) => {
  const errors = {};

  fieldConfig.forEach((field) => {
    const value = formData[field.name];
    const validation = field.validation || {};

    // Required validation
    if (validation.required) {
      // Handle arrays
      if (Array.isArray(value)) {
        if (value.length === 0) {
          errors[field.name] = typeof validation.required === "string"
            ? validation.required
            : `${field.label} is required`;
          return;
        }
      }
      // Handle strings/numbers
      else if (!value && value !== 0) {
        errors[field.name] = typeof validation.required === "string"
          ? validation.required
          : `${field.label} is required`;
        return;
      }
    }

    // Skip other validations if empty and not required
    if (!value && value !== 0 && !validation.required) return;

    // Pattern validation (regex)
    if (validation.pattern && !validation.pattern.value.test(value)) {
      errors[field.name] = validation.pattern.message;
      return;
    }

    // Min length validation
    if (validation.minLength && value.length < validation.minLength.value) {
      errors[field.name] = validation.minLength.message;
      return;
    }

    // Max length validation
    if (validation.maxLength && value.length > validation.maxLength.value) {
      errors[field.name] = validation.maxLength.message;
      return;
    }

    // Min value validation (for numbers)
    if (validation.min !== undefined && parseFloat(value) < validation.min.value) {
      errors[field.name] = validation.min.message;
      return;
    }

    // Max value validation (for numbers)
    if (validation.max !== undefined && parseFloat(value) > validation.max.value) {
      errors[field.name] = validation.max.message;
      return;
    }

    // Custom validation function
    if (validation.custom && typeof validation.custom === "function") {
      const customError = validation.custom(value, formData);
      if (customError) {
        errors[field.name] = customError;
      }
    }
  });

  return errors;
};

/**
 * Transform form data for API submission
 * Applies transformOnSave functions defined in field configs
 * 
 * @param {Object} formData - Raw form data
 * @param {Array} fieldConfig - Field configuration array
 * @returns {Object} Transformed data ready for API
 * 
 * @example
 * const apiData = transformForSave(formData, COMPANY_FORM_FIELDS);
 * // Numbers are parsed, dates formatted, etc.
 */
export const transformForSave = (formData, fieldConfig) => {
  return fieldConfig.reduce((acc, field) => {
    let value = formData[field.name];

    // Apply custom transformation if defined
    if (field.transformOnSave && value !== undefined && value !== null && value !== "") {
      value = field.transformOnSave(value);
    }

    acc[field.name] = value;
    return acc;
  }, {});
};

/**
 * Get field configuration by name
 * @param {Array} fieldConfig - Field configuration array
 * @param {string} fieldName - Field name to find
 * @returns {Object|null} Field config or null
 * 
 * @example
 * const emailField = getFieldConfig(COMPANY_FORM_FIELDS, "contact_email");
 */
export const getFieldConfig = (fieldConfig, fieldName) => {
  return fieldConfig.find((field) => field.name === fieldName) || null;
};

/**
 * Get all required field names
 * @param {Array} fieldConfig - Field configuration array
 * @returns {Array} Array of required field names
 * 
 * @example
 * const required = getRequiredFields(COMPANY_FORM_FIELDS);
 * // ["company_name", "company_type", "contact_email", ...]
 */
export const getRequiredFields = (fieldConfig) => {
  return fieldConfig
    .filter((field) => field.required || field.validation?.required)
    .map((field) => field.name);
};

/**
 * Check if field has errors
 * @param {Object} errors - Errors object
 * @param {string} fieldName - Field name
 * @returns {boolean} True if field has error
 */
export const hasFieldError = (errors, fieldName) => {
  return !!(errors && errors[fieldName]);
};

/**
 * Get field error message
 * @param {Object} errors - Errors object
 * @param {string} fieldName - Field name
 * @returns {string|null} Error message or null
 */
export const getFieldError = (errors, fieldName) => {
  return errors && errors[fieldName] ? errors[fieldName] : null;
};