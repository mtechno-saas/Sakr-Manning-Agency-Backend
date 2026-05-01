// config/formConfigs.js
// Centralized form field configurations for all pages

/**
 * CV Management Form Fields
 */
export const cvFormFields = [
  {
    name: "name",
    label: "Full Name",
    type: "text",
    placeholder: "Enter full name",
    required: true,
    validation: ["required", { type: "minLength", value: 2 }],
  },
  {
    name: "position",
    label: "Position",
    type: "text",
    placeholder: "e.g., Chief Engineer",
    required: true,
    validation: ["required"],
  },
  {
    name: "experience",
    label: "Experience",
    type: "text",
    placeholder: "e.g., 15 years",
    required: true,
    validation: ["required"],
  },
  {
    name: "submitted",
    label: "Submitted Date",
    type: "date",
    required: true,
    validation: ["required", "date"],
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "Under Review", label: "Under Review" },
      { value: "Approved", label: "Approved" },
      { value: "Pending", label: "Pending" },
      { value: "Interviewed", label: "Interviewed" },
    ],
  },
];

/**
 * Company Management Form Fields
 */
export const companyFormFields = [
  {
    name: "name",
    label: "Company Name",
    type: "text",
    placeholder: "Enter company name",
    required: true,
    validation: ["required", { type: "minLength", value: 2 }],
  },
  {
    name: "type",
    label: "Company Type",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "Shipping", label: "Shipping" },
      { value: "Cruise", label: "Cruise" },
      { value: "Cargo", label: "Cargo" },
      { value: "Offshore", label: "Offshore" },
    ],
  },
  {
    name: "openPositions",
    label: "Open Positions",
    type: "number",
    placeholder: "0",
    required: true,
    validation: ["required", "positiveNumber"],
  },
  {
    name: "email",
    label: "Contact Email",
    type: "email",
    placeholder: "contact@company.com",
    required: true,
    validation: ["required", "email"],
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "Active", label: "Active" },
      { value: "INACTIVE", label: "Inactive" },
    ],
  },
];

/**
 * Ship Management Form Fields
 */
export const shipFormFields = [
  {
    name: "name",
    label: "Ship Name",
    type: "text",
    placeholder: "e.g., M/V Ocean Explorer",
    required: true,
    validation: ["required"],
  },
  {
    name: "imoNumber",
    label: "IMO Number",
    type: "text",
    placeholder: "IMO1234567",
    required: true,
    validation: ["required", "imoNumber"],
  },
  {
    name: "flag",
    label: "Flag",
    type: "text",
    placeholder: "e.g., Panama",
    required: true,
    validation: ["required"],
  },
  {
    name: "type",
    label: "Ship Type",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "Container Ship", label: "Container Ship" },
      { value: "Cruise Ship", label: "Cruise Ship" },
      { value: "Bulk Carrier", label: "Bulk Carrier" },
      { value: "Tanker", label: "Tanker" },
    ],
  },
  {
    name: "company",
    label: "Company",
    type: "text",
    placeholder: "Company name",
    required: true,
    validation: ["required"],
    helpText: "Enter the company that owns this ship",
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "Active", label: "Active" },
      { value: "INACTIVE", label: "Inactive" },
    ],
  },
];

/**
 * User Management Form Fields
 */
export const userFormFields = [
  {
    name: "name",
    label: "Full Name",
    type: "text",
    placeholder: "Enter full name",
    required: true,
    validation: ["required", { type: "minLength", value: 2 }],
  },
  {
    name: "email",
    label: "Email Address",
    type: "email",
    placeholder: "user@example.com",
    required: true,
    validation: ["required", "email"],
  },
  {
    name: "role",
    label: "Role",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "Admin", label: "Admin" },
      { value: "HR Manager", label: "HR Manager" },
      { value: "Recruiter", label: "Recruiter" },
    ],
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "Active", label: "Active" },
      { value: "Inactive", label: "Inactive" },
    ],
  },
];

/**
 * Documents Management Form Fields
 */

export const documentFormFields = [
  {
    name: "name",
    label: "Full Name",
    type: "text",
    placeholder: "Enter full name",
    required: true,
    validation: ["required"],
  },
  {
    name: "position",
    label: "Position",
    type: "text",
    placeholder: "e.g., Navigation Officer",
    required: true,
    validation: ["required"],
  },
  {
    name: "duration",
    label: "Contract Duration",
    type: "text",
    placeholder: "e.g., 12 months",
    required: false,
  },
  {
    name: "generated",
    label: "Generated Date",
    type: "date",
    required: false,
  },
  {
    name: "signed",
    label: "Signed Date",
    type: "date",
    required: false,
  },
  {
    name: "expires",
    label: "Expiry Date",
    type: "date",
    required: false,
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "signed", label: "Signed" },
      { value: "pending", label: "Pending Signature" },
      { value: "draft", label: "Draft" },
      { value: "expired", label: "Expired" },
      { value: "expiringSoon", label: "Expiring Soon" },
      { value: "notice", label: "Notice Period" },
    ],
  },
];

/**
 * Interview Management Form Fields
 */
export const interviewFormFields = [
  {
    name: "candidateName",
    label: "Candidate Name",
    type: "text",
    placeholder: "Enter candidate name",
    required: true,
    validation: ["required"],
  },
  {
    name: "position",
    label: "Position",
    type: "text",
    placeholder: "e.g., Chief Engineer",
    required: true,
    validation: ["required"],
  },
  {
    name: "company",
    label: "Company",
    type: "text",
    placeholder: "Company name",
    required: true,
    validation: ["required"],
  },
  {
    name: "date",
    label: "Interview Date",
    type: "date",
    required: true,
    validation: ["required", "date"],
  },
  {
    name: "time",
    label: "Interview Time",
    type: "time",
    required: true,
    validation: ["required"],
  },
  {
    name: "type",
    label: "Interview Type",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "video", label: "Video Call" },
      { value: "phone", label: "Phone Call" },
      { value: "in-person", label: "In-Person" },
    ],
  },
  {
    name: "status",
    label: "Status",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "scheduled", label: "Scheduled" },
      { value: "confirmed", label: "Confirmed" },
      { value: "pending", label: "Pending" },
      { value: "completed", label: "Completed" },
      { value: "cancelled", label: "Cancelled" },
    ],
  },
  {
    name: "notes",
    label: "Notes",
    type: "textarea",
    placeholder: "Add any additional notes...",
    required: false,
    rows: 4,
  },
];

/**
 * Finance Management Form Fields
 */
export const financeFormFields = [
  {
    name: "user",
    label: "User",
    type: "text",
    placeholder: "Enter user name",
    required: true,
    validation: ["required"],
  },
  {
    name: "company",
    label: "Company",
    type: "select",
    required: true,
    validation: ["required"],
    options: [
      { value: "Ocean Maritime Ltd", label: "Ocean Maritime Ltd" },
      { value: "Blue Sea Cruises", label: "Blue Sea Cruises" },
      { value: "Global Cargo Corp", label: "Global Cargo Corp" },
      { value: "Maritime Solutions", label: "Maritime Solutions" },
    ],
  },
  {
    name: "startDate",
    label: "Start Date",
    type: "date",
    required: true,
    validation: ["required", "date"],
  },
  {
    name: "endDate",
    label: "End Date",
    type: "date",
    required: false,
    validation: ["date"],
  },
];

/**
 * Get form fields by entity type
 * @param {string} entity - Entity type ('cv', 'company', 'ship', 'user', 'interview')
 * @returns {Array} Field configurations
 */
export const getFormFields = (entity) => {
  const fieldsMap = {
    cv: cvFormFields,
    company: companyFormFields,
    ship: shipFormFields,
    user: userFormFields,
    interview: interviewFormFields,
    document: documentFormFields,
    finance: financeFormFields,
  };

  return fieldsMap[entity] || [];
};

export default {
  cvFormFields,
  companyFormFields,
  shipFormFields,
  userFormFields,
  interviewFormFields,
  documentFormFields,
  financeFormFields,
  getFormFields,
};
