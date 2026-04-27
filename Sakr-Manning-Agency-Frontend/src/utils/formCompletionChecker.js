// utils/formCompletionChecker.js
import { STEP_FIELDS } from "./RHFvalidationRules";

/**
 * Check if a form field has a valid value
 */
const hasValidValue = (value) => {
  if (value === null || value === undefined) return false;
  if (typeof value === "string") return value.trim() !== "";
  // For arrays (CRUD collections), check if array has items
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "object" && value !== null) {
    return Object.values(value).some((v) => hasValidValue(v));
  }
  return Boolean(value);
};

/**
 * Check completion status for a specific form step
 */
export const checkStepCompletion = (formData, stepIndex) => {
  const stepConfig = STEP_FIELDS[stepIndex];
  if (!stepConfig) {
    return {
      stepName: "Unknown Step",
      isComplete: false,
      completedFields: 0,
      totalFields: 0,
      missingFields: [],
      completionPercentage: 0,
    };
  }

  const { name: stepName, fields } = stepConfig;
  const missingFields = [];
  let totalFields = 0;
  let completedCount = 0;

  if (fields) {
    fields.forEach((fieldName) => {
      const fieldValue = formData[fieldName];

      // Check if it's a CRUD array field (documents, certificates, etc.)
      if (Array.isArray(fieldValue)) {
        // For CRUD arrays, just check if array has items
        totalFields++;
        if (fieldValue.length > 0) {
          completedCount++;
        } else {
          missingFields.push(fieldName);
        }
      } else {
        // Regular field handling
        totalFields++;
        if (hasValidValue(fieldValue)) {
          completedCount++;
        } else {
          missingFields.push(fieldName);
        }
      }
    });
  }
  const completionPercentage =
    totalFields > 0 ? Math.round((completedCount / totalFields) * 100) : 0;
  const isComplete = completedCount === totalFields;

  return {
    stepName,
    isComplete,
    completedFields: completedCount,
    totalFields,
    missingFields,
    completionPercentage,
  };
};

/**
 * Check completion status for all form steps
 */
export const checkAllStepsCompletion = (formData) => {
  const stepResults = [];
  let totalCompleteSteps = 0;
  let totalSteps = Object.keys(STEP_FIELDS).length;

  Object.keys(STEP_FIELDS).forEach((stepIndex) => {
    const result = checkStepCompletion(formData, parseInt(stepIndex));
    stepResults.push(result);

    if (result.isComplete) {
      totalCompleteSteps++;
    }
  });

  const overallCompletion =
    totalSteps > 0 ? Math.round((totalCompleteSteps / totalSteps) * 100) : 0;
  const isFormComplete = totalCompleteSteps === totalSteps;

  return {
    steps: stepResults,
    totalSteps,
    completedSteps: totalCompleteSteps,
    overallCompletion,
    isFormComplete,
  };
};

/**
 * Get field display names for better UI messages
 */
const FIELD_DISPLAY_NAMES = {
  applicationForPosition: "Application Position",
  available_date: "Available Date",
  application_for_position: "Application Position",
  expectedSalary: "Expected Salary",
  expected_salary: "Expected Salary",
  profilePhoto: "Profile Photo",
  fullName: "Full Name",
  full_name: "Full Name",
  dateOfBirth: "Date of Birth",
  date_of_birth: "Date of Birth",
  maritalStatus: "Marital Status",
  marital_status: "Marital Status",
  weight: "Weight",
  height: "Height",
  nationality: "Nationality",
  overallSize: "Overall Size",
  overall_size: "Overall Size",
  placeOfBirth: "Place of Birth",
  place_of_birth: "Place of Birth",
  nearestPort: "Nearest Port",
  nearest_port: "Nearest Port",
  educationSchool: "School/College",
  education_school: "School/College",
  homeAddress: "Home Address",
  home_address: "Home Address",
  email: "Email Address",
  mobile: "Mobile Number",
  documents: "Travel Documents",
  certificates: "Professional Certificates",
  licenses: "Professional Certificates",
  kinFullName: "Emergency Contact Name",
  kin_full_name: "Emergency Contact Name",
  kinRelationship: "Relationship",
  kin_relationship: "Relationship",
  kinAddress: "Emergency Contact Address",
  kin_address: "Emergency Contact Address",
  kinPhone: "Emergency Contact Phone",
  kin_phone: "Emergency Contact Phone",
  kinEmail: "Emergency Contact Email",
  kin_email: "Emergency Contact Email",
  health: "Health Certificates",
  courses: "Marine Courses",
  seaService: "Sea Service Records",
  sea_services: "Sea Service Records",
  references: "References",
  declaration: "Declaration",
};

/**
 * Get user-friendly field name
 */
export const getFieldDisplayName = (fieldName) => {
  return FIELD_DISPLAY_NAMES[fieldName] || fieldName;
};

/**
 * Format missing fields for display
 */
// export const formatMissingFields = (missingFields) => {
//   return missingFields.map((field) => getFieldDisplayName(field));
// };

export const formatMissingFields = (missingFields) => {
  return missingFields.map((field) => {
    const displayName = getFieldDisplayName(field);
    // ✅ Sanitize to prevent XSS
    return displayName
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  });
};

/**
 * Check if form is ready for submission
 */
export const isFormReadyForSubmission = (formData) => {
  const completion = checkAllStepsCompletion(formData);

  // Define minimum completion requirements
  const CRITICAL_STEPS = [0, 1, 2, 3]; // Position, Education, Contact, Emergency
  const MIN_OVERALL_COMPLETION = 80; // 80% minimum completion

  // Check critical steps completion
  const criticalStepsComplete = CRITICAL_STEPS.every(
    (stepIndex) => completion.steps[stepIndex]?.isComplete
  );

  // Check overall completion percentage
  // add 63% to skip the effect of the CRUD forms (100% * 7 (no. CRUD forms) / 11 (total no. forms))
  const totalCompleteSteps = completion.overallCompletion + 63;
  const meetMinimumCompletion = totalCompleteSteps >= MIN_OVERALL_COMPLETION;

  return {
    // can instead use {criticalStepsComplete} only as indicator but the "Director wants it"
    isReady: criticalStepsComplete && meetMinimumCompletion,
    criticalStepsComplete,
    meetMinimumCompletion,
    completion,
  };
};
