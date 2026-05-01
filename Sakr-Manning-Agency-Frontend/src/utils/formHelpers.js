// utils/formHelpers.js
// Helper functions for form operations

/**
 * Initialize form data from field configs
 * @param {Array} fields - Field configuration array
 * @param {Object} initialData - Optional initial data
 * @returns {Object} Form data object
 */
export const initializeFormData = (fields, initialData = {}) => {
  const formData = {};

  fields.forEach((field) => {
    if (initialData && initialData[field.name] !== undefined) {
      formData[field.name] = initialData[field.name];
    } else if (field.defaultValue !== undefined) {
      formData[field.name] = field.defaultValue;
    } else {
      // Set default based on field type
      switch (field.type) {
        case "checkbox":
          formData[field.name] = false;
          break;
        case "multi-select":
          formData[field.name] = [];
          break;
        case "number":
          formData[field.name] = "";
          break;
        default:
          formData[field.name] = "";
      }
    }
  });

  return formData;
};

/**
 * Deep clone object (for form data)
 * @param {Object} obj - Object to clone
 * @returns {Object} Cloned object
 */
export const deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Check if form data has changed
 * @param {Object} original - Original data
 * @param {Object} current - Current data
 * @returns {boolean} True if data has changed
 */
export const hasFormChanged = (original, current) => {
  return JSON.stringify(original) !== JSON.stringify(current);
};

/**
 * Get changed fields
 * @param {Object} original - Original data
 * @param {Object} current - Current data
 * @returns {Object} Object with only changed fields
 */
export const getChangedFields = (original, current) => {
  const changes = {};

  Object.keys(current).forEach((key) => {
    if (JSON.stringify(original[key]) !== JSON.stringify(current[key])) {
      changes[key] = current[key];
    }
  });

  return changes;
};

/**
 * Format form data for API submission
 * @param {Object} formData - Raw form data
 * @param {Array} fields - Field configurations
 * @returns {Object} Formatted data
 */
export const formatFormData = (formData, fields) => {
  const formatted = { ...formData };

  fields.forEach((field) => {
    const value = formatted[field.name];

    // Apply field-specific formatting
    if (field.format) {
      formatted[field.name] = field.format(value);
    } else {
      // Default formatting based on type
      switch (field.type) {
        case "number":
          formatted[field.name] = value ? Number(value) : null;
          break;
        case "date":
          formatted[field.name] = value ? new Date(value).toISOString() : null;
          break;
        case "checkbox":
          formatted[field.name] = Boolean(value);
          break;
        default:
          // Trim strings
          if (typeof value === "string") {
            formatted[field.name] = value.trim();
          }
      }
    }
  });

  return formatted;
};

/**
 * Generate unique ID
 * @returns {number} Timestamp-based ID
 */
export const generateId = () => {
  return Date.now() + Math.floor(Math.random() * 1000);
};

/**
 * Sanitize HTML to prevent XSS
 * @param {string} html - Raw HTML string
 * @returns {string} Sanitized string
 */
export const sanitizeHtml = (html) => {
  const temp = document.createElement("div");
  temp.textContent = html;
  return temp.innerHTML;
};

/**
 * Format date for input field
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date (YYYY-MM-DD)
 */
export const formatDateForInput = (date) => {
  if (!date) return "";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "";

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
};

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date (Jan 15, 2024)
 */
export const formatDateForDisplay = (date) => {
  if (!date) return "";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "";

  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

/**
 * Debounce function for search/input delays
 * @param {Function} func - Function to debounce
 * @param {number} delay - Delay in milliseconds
 * @returns {Function} Debounced function
 */
export const debounce = (func, delay = 300) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

/**
 * Capitalize first letter
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export const capitalize = (str) => {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Convert camelCase to Title Case
 * @param {string} str - camelCase string
 * @returns {string} Title Case string
 */
export const camelToTitle = (str) => {
  if (!str) return "";
  return str
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (s) => s.toUpperCase())
    .trim();
};

/**
 * Merge default options with user options
 * @param {Object} defaults - Default options
 * @param {Object} options - User options
 * @returns {Object} Merged options
 */
export const mergeOptions = (defaults, options) => {
  return { ...defaults, ...options };
};

export default {
  initializeFormData,
  deepClone,
  hasFormChanged,
  getChangedFields,
  formatFormData,
  generateId,
  sanitizeHtml,
  formatDateForInput,
  formatDateForDisplay,
  debounce,
  capitalize,
  camelToTitle,
  mergeOptions,
};
