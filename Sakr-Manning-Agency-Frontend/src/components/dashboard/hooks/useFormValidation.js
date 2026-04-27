// hooks/useFormValidation.js
// Custom hook for form validation with real-time feedback

import { useState, useCallback, useMemo } from "react";
import {
  validateField,
  validateForm,
  isFormValid,
} from "../../../utils/newValidation";

/**
 * Custom Hook: useFormValidation
 *
 * Handles form validation with real-time feedback
 * Supports field-level and form-level validation
 *
 * @param {Array} fieldConfigs - Field configurations with validation rules
 * @returns {Object} Validation utilities
 *
 * @example
 * const {
 *   errors,
 *   validateFieldValue,
 *   validateAllFields,
 *   clearError,
 *   clearAllErrors,
 *   hasErrors
 * } = useFormValidation(fields);
 */
const useFormValidation = (fieldConfigs = []) => {
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  // Memoize field configs to prevent unnecessary recalculations
  const memoizedFieldConfigs = useMemo(
    () => fieldConfigs,
    [JSON.stringify(fieldConfigs)]
  );

  /**
   * Validate a single field
   * @param {string} fieldName - Name of field to validate
   * @param {any} value - Field value
   * @param {boolean} markTouched - Whether to mark field as touched
   * @returns {string|null} Error message or null
   */
  const validateFieldValue = useCallback(
    (fieldName, value, markTouched = false) => {
      const field = memoizedFieldConfigs.find((f) => f.name === fieldName);
      if (!field || !field.validation) return null;

      const error = validateField(value, field.validation, field.label);

      setErrors((prev) => ({
        ...prev,
        [fieldName]: error,
      }));

      if (markTouched) {
        setTouched((prev) => ({
          ...prev,
          [fieldName]: true,
        }));
      }

      return error;
    },
    [memoizedFieldConfigs]
  );

  /**
   * Validate all fields in form
   * @param {Object} formData - Current form data
   * @returns {Object} Errors object
   */
  const validateAllFields = useCallback(
    (formData) => {
      const newErrors = validateForm(formData, memoizedFieldConfigs);

      setErrors(newErrors);

      // Mark all fields as touched
      const allTouched = {};
      memoizedFieldConfigs.forEach((field) => {
        allTouched[field.name] = true;
      });
      setTouched(allTouched);

      return newErrors;
    },
    [memoizedFieldConfigs]
  );

  /**
   * Clear error for specific field
   * @param {string} fieldName - Name of field
   */
  const clearError = useCallback((fieldName) => {
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[fieldName];
      return newErrors;
    });
  }, []);

  /**
   * Clear all errors - STABLE REFERENCE
   */
  const clearAllErrors = useCallback(() => {
    setErrors({});
    setTouched({});
  }, []); // ✅ Empty dependency array makes this stable

  /**
   * Mark field as touched
   * @param {string} fieldName - Name of field
   */
  const touchField = useCallback((fieldName) => {
    setTouched((prev) => ({
      ...prev,
      [fieldName]: true,
    }));
  }, []);

  /**
   * Check if field has been touched
   * @param {string} fieldName - Name of field
   * @returns {boolean} True if field has been touched
   */
  const isFieldTouched = useCallback(
    (fieldName) => {
      return touched[fieldName] === true;
    },
    [touched]
  );

  /**
   * Get error for specific field (only if touched)
   * @param {string} fieldName - Name of field
   * @returns {string|null} Error message or null
   */
  const getFieldError = useCallback(
    (fieldName) => {
      if (!touched[fieldName]) return null;
      return errors[fieldName] || null;
    },
    [errors, touched]
  );

  /**
   * Check if form has any errors
   * @returns {boolean} True if form is valid
   */
  const hasErrors = useCallback(() => {
    return !isFormValid(errors);
  }, [errors]);

  /**
   * Get all current errors
   * @returns {Object} Errors object
   */
  const getAllErrors = useCallback(() => {
    return errors;
  }, [errors]);

  return {
    errors,
    touched,
    validateFieldValue,
    validateAllFields,
    clearError,
    clearAllErrors,
    touchField,
    isFieldTouched,
    getFieldError,
    hasErrors,
    getAllErrors,
  };
};

export default useFormValidation;
