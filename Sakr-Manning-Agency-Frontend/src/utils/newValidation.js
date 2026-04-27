// utils/validation.js
// Comprehensive validation utilities for form fields

/**
 * Validation Rules
 * Each rule returns an error message if validation fails, or null if valid
 */

export const validationRules = {
  required: (value, fieldName = "This field") => {
    if (value === null || value === undefined || value === "") {
      return `${fieldName} is required`;
    }
    if (Array.isArray(value) && value.length === 0) {
      return `${fieldName} must have at least one selection`;
    }
    return null;
  },

  email: (value) => {
    if (!value) return null; // Skip if empty (use required rule separately)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return "Please enter a valid email address";
    }
    return null;
  },

  minLength: (value, min, fieldName = "This field") => {
    if (!value) return null;
    if (String(value).length < min) {
      return `${fieldName} must be at least ${min} characters`;
    }
    return null;
  },

  maxLength: (value, max, fieldName = "This field") => {
    if (!value) return null;
    if (String(value).length > max) {
      return `${fieldName} must not exceed ${max} characters`;
    }
    return null;
  },

  number: (value, fieldName = "This field") => {
    if (!value) return null;
    if (isNaN(Number(value))) {
      return `${fieldName} must be a valid number`;
    }
    return null;
  },

  positiveNumber: (value, fieldName = "This field") => {
    if (!value) return null;
    const num = Number(value);
    if (isNaN(num) || num < 0) {
      return `${fieldName} must be a positive number`;
    }
    return null;
  },

  date: (value, fieldName = "This field") => {
    if (!value) return null;
    const date = new Date(value);
    if (isNaN(date.getTime())) {
      return `${fieldName} must be a valid date`;
    }
    return null;
  },

  dateRange: (startDate, endDate) => {
    if (!startDate || !endDate) return null;
    const start = new Date(startDate);
    const end = new Date(endDate);
    if (start > end) {
      return "End date must be after start date";
    }
    return null;
  },

  imoNumber: (value) => {
    if (!value) return null;
    const imoRegex = /^IMO\d{7}$/;
    if (!imoRegex.test(value)) {
      return "IMO number must be in format IMO1234567";
    }
    return null;
  },

  phone: (value) => {
    if (!value) return null;
    const phoneRegex = /^[\d\s\-\\+\\(\\)]+$/;
    if (!phoneRegex.test(value) || value.length < 10) {
      return "Please enter a valid phone number";
    }
    return null;
  },

  url: (value) => {
    if (!value) return null;
    try {
      new URL(value);
      return null;
    } catch {
      return "Please enter a valid URL";
    }
  },

  custom: (value, validatorFn, errorMessage) => {
    if (!validatorFn(value)) {
      return errorMessage || "Invalid value";
    }
    return null;
  },
};

/**
 * Validate a single field based on its rules
 * @param {any} value - Field value
 * @param {Array} rules - Array of validation rules
 * @param {string} fieldName - Field label for error messages
 * @returns {string|null} Error message or null if valid
 */
export const validateField = (value, rules = [], fieldName = "Field") => {
  if (!rules || rules.length === 0) return null;

  for (const rule of rules) {
    let error = null;

    if (typeof rule === "string") {
      // Simple rule: "required", "email", etc.
      if (validationRules[rule]) {
        error = validationRules[rule](value, fieldName);
      }
    } else if (typeof rule === "object") {
      // Complex rule: { type: "minLength", value: 3 }
      const { type, value: ruleValue, message } = rule;
      if (validationRules[type]) {
        if (type === "minLength" || type === "maxLength") {
          error = validationRules[type](value, ruleValue, fieldName);
        } else if (type === "custom") {
          error = validationRules.custom(value, ruleValue, message);
        } else {
          error = validationRules[type](value, fieldName);
        }
      }
    }

    if (error) return error;
  }

  return null;
};

/**
 * Validate entire form
 * @param {Object} formData - Form data object
 * @param {Object} fieldConfigs - Field configurations with validation rules
 * @returns {Object} Errors object { fieldName: errorMessage }
 */
export const validateForm = (formData, fieldConfigs) => {
  const errors = {};

  fieldConfigs.forEach((field) => {
    if (field.validation && field.validation.length > 0) {
      const error = validateField(
        formData[field.name],
        field.validation,
        field.label
      );
      if (error) {
        errors[field.name] = error;
      }
    }
  });

  return errors;
};

/**
 * Check if form has any errors
 * @param {Object} errors - Errors object
 * @returns {boolean} True if form is valid
 */
export const isFormValid = (errors) => {
  return Object.keys(errors).length === 0;
};

/**
 * Pre-defined validation sets for common use cases
 */
export const validationSets = {
  name: ["required", { type: "minLength", value: 2 }],
  email: ["required", "email"],
  phone: ["phone"],
  required: ["required"],
  positiveNumber: ["required", "positiveNumber"],
  date: ["required", "date"],
  imoNumber: ["required", "imoNumber"],
  url: ["url"],
};

/**
 * Get validation set by name
 * @param {string} setName - Name of validation set
 * @returns {Array} Validation rules
 */
export const getValidationSet = (setName) => {
  return validationSets[setName] || [];
};

export default {
  validationRules,
  validateField,
  validateForm,
  isFormValid,
  validationSets,
  getValidationSet,
};
