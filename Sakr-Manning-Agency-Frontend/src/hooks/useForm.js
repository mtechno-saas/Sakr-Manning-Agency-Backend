// hooks/useForm.js
import { useState, useCallback, useMemo } from "react";
import { validateForm } from "../utils/validation";

export const useForm = (initialValues, validationRules = {}, options = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    validateOnChange = true,
    validateOnBlur = true,
    resetOnSubmit = false,
  } = options;

  // Handle input changes
  const handleChange = useCallback(
    (name) => (event) => {
      const value = event.target.value;

      setValues((prev) => ({
        ...prev,
        [name]: value,
      }));

      // Clear error for this field when user starts typing
      if (errors[name] && validateOnChange) {
        setErrors((prev) => ({
          ...prev,
          [name]: "",
        }));
      }

      // Validate on change if enabled
      if (validateOnChange && validationRules[name]) {
        const error = validationRules[name](value);
        setErrors((prev) => ({
          ...prev,
          [name]: error,
        }));
      }
    },
    [errors, validateOnChange, validationRules]
  );

  // Handle input blur
  const handleBlur = useCallback(
    (name) => () => {
      setTouched((prev) => ({
        ...prev,
        [name]: true,
      }));

      // Validate on blur if enabled
      if (validateOnBlur && validationRules[name]) {
        const error = validationRules[name](values[name]);
        setErrors((prev) => ({
          ...prev,
          [name]: error,
        }));
      }
    },
    [validateOnBlur, validationRules, values]
  );

  // Set field value programmatically
  const setFieldValue = useCallback(
    (name, value) => {
      setValues((prev) => ({
        ...prev,
        [name]: value,
      }));

      // Clear error when setting value
      if (errors[name]) {
        setErrors((prev) => ({
          ...prev,
          [name]: "",
        }));
      }
    },
    [errors]
  );

  // Set field error programmatically
  const setFieldError = useCallback((name, error) => {
    setErrors((prev) => ({
      ...prev,
      [name]: error,
    }));
  }, []);

  // Set multiple errors at once
  const setFormErrors = useCallback((newErrors) => {
    setErrors(newErrors);
  }, []);

  // Reset form to initial values
  const resetForm = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, [initialValues]);

  // Validate entire form
  const validateAll = useCallback(() => {
    const validation = validateForm(values, validationRules);
    setErrors(validation.errors);

    // Mark all fields as touched
    const allTouched = Object.keys(validationRules).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    setTouched(allTouched);

    return validation.isValid;
  }, [values, validationRules]);

  // Handle form submission - FIXED VERSION
  const handleSubmit = useCallback(
    (onSubmit) => async (event) => {
      // Prevent default form submission behavior
      if (event && event.preventDefault) {
        event.preventDefault();
        event.stopPropagation();
      }

      setIsSubmitting(true);

      try {
        const isValid = validateAll();

        if (isValid) {
          await onSubmit(values);
          if (resetOnSubmit) {
            resetForm();
          }
        }
      } catch (error) {
        // Handle submission errors
        console.error("Form submission error:", error);
        // Don't rethrow - let the parent handle errors through callbacks
      } finally {
        setIsSubmitting(false);
      }
    },
    [values, validateAll, resetOnSubmit, resetForm]
  );

  // Get field props for easy spreading
  const getFieldProps = useCallback(
    (name) => ({
      name,
      value: values[name] || "",
      onChange: handleChange(name),
      onBlur: handleBlur(name),
      error: touched[name] && errors[name] ? errors[name] : "",
    }),
    [values, handleChange, handleBlur, touched, errors]
  );

  // Computed values
  const isValid = useMemo(() => {
    return Object.keys(validationRules).every((key) => !errors[key]);
  }, [errors, validationRules]);

  const isDirty = useMemo(() => {
    return Object.keys(values).some(
      (key) => values[key] !== initialValues[key]
    );
  }, [values, initialValues]);

  const hasErrors = useMemo(() => {
    return Object.values(errors).some((error) => error !== "");
  }, [errors]);

  const touchedFields = useMemo(() => {
    return Object.keys(touched).filter((key) => touched[key]);
  }, [touched]);

  return {
    // Values and state
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    isDirty,
    hasErrors,
    touchedFields,

    // Handlers
    handleChange,
    handleBlur,
    handleSubmit,
    setFieldValue,
    setFieldError,
    setFormErrors,
    resetForm,
    validateAll,
    getFieldProps,

    // Utilities
    setValues,
    setIsSubmitting,
  };
};
