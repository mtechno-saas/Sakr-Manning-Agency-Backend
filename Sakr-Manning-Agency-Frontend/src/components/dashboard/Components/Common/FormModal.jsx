// Components/Common/FormModal.jsx
// Fully reusable, generic form modal for all CRUD operations

import React, { useState, useEffect, useRef } from "react";
import Button from "./Button";
import FormField from "./FormField";
import { getModalStyles } from "../../Styles/componentStyles";
import { getModalTitleStyles } from "../../Styles/cssClasses";
import { getScaledValue } from "../../Styles/globalStyles";
import {
  initializeFormData,
  hasFormChanged,
} from "../../../../utils/formHelpers";
import useFormValidation from "../../hooks/useFormValidation";

/**
 * FormModal Component
 *
 * **Universal CRUD modal for all pages**
 * Supports: Add, Edit, View modes
 * Handles: Validation, form state, submit, cancel
 *
 * @param {boolean} isOpen - Modal visibility
 * @param {string} mode - 'add' | 'edit' | 'view'
 * @param {Function} onClose - Close callback
 * @param {Function} onSubmit - Submit callback with form data
 * @param {string} title - Modal title
 * @param {Array} fields - Field configurations
 * @param {Object} initialData - Initial data for edit mode
 * @param {number} scale - Scale factor
 * @param {boolean} loading - Loading state during submission
 *
 * Fields Configuration Example:
 * [
 *   {
 *     name: "name",
 *     label: "Full Name",
 *     type: "text",
 *     placeholder: "Enter name...",
 *     required: true,
 *     validation: ["required", { type: "minLength", value: 2 }]
 *   }
 * ]
 */
const FormModal = ({
  isOpen,
  mode = "add",
  onClose,
  onSubmit,
  title,
  fields = [],
  initialData = {},
  scale = 1,
  loading = false,
}) => {
  const [formData, setFormData] = useState({});
  const [originalData, setOriginalData] = useState({});
  const [isInitialized, setIsInitialized] = useState(false);
  const firstFieldRef = useRef(null);

  const modalStyles = getModalStyles(scale);
  const titleStyles = getModalTitleStyles(scale);

  // Validation hook - now has stable clearAllErrors
  const {
    // errors,
    validateFieldValue,
    validateAllFields,
    clearAllErrors,
    getFieldError,
    touchField,
  } = useFormValidation(fields);

  // ✅ FIX: Initialize form data only once when modal opens
  useEffect(() => {
    if (isOpen && !isInitialized) {
      const initialized = initializeFormData(fields, initialData);
      setFormData(initialized);
      setOriginalData(initialized);
      clearAllErrors();
      setIsInitialized(true);

      // Focus first field
      if (firstFieldRef.current && mode !== "view") {
        setTimeout(() => firstFieldRef.current?.focus(), 100);
      }
    }

    // Reset when modal closes
    if (!isOpen && isInitialized) {
      setIsInitialized(false);
      setFormData({});
      setOriginalData({});
    }
  }, [isOpen]); // ✅ Only depends on isOpen

  // Handle Escape key
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === "Escape" && !loading) {
        handleClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, loading]);

  // Handle field change
  const handleFieldChange = (fieldName, value) => {
    setFormData((prev) => ({
      ...prev,
      [fieldName]: value,
    }));

    // Validate field on change
    if (mode !== "view") {
      validateFieldValue(fieldName, value);
    }
  };

  // Handle field blur
  const handleFieldBlur = (fieldName) => {
    touchField(fieldName);
    validateFieldValue(fieldName, formData[fieldName], true);
  };

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault();

    if (mode === "view") {
      handleClose();
      return;
    }

    // Validate all fields
    const validationErrors = validateAllFields(formData);

    if (Object.keys(validationErrors).length > 0) {
      // Scroll to first error
      const firstErrorField = Object.keys(validationErrors)[0];
      const errorElement = document.getElementById(firstErrorField);
      if (errorElement) {
        errorElement.scrollIntoView({ behavior: "smooth", block: "center" });
        errorElement.focus();
      }
      return;
    }

    // Submit form
    onSubmit(formData);
  };

  // Handle close
  const handleClose = () => {
    if (loading) return;

    // Warn if unsaved changes
    if (mode === "edit" && hasFormChanged(originalData, formData)) {
      const confirmed = window.confirm(
        "You have unsaved changes. Are you sure you want to close?"
      );
      if (!confirmed) return;
    }

    onClose();
  };

  if (!isOpen) return null;

  const isViewMode = mode === "view";
  // const isEditMode = mode === "edit";
  const isAddMode = mode === "add";

  return (
    <div
      style={modalStyles.overlay}
      role="dialog"
      aria-modal="true"
      aria-labelledby="form-modal-title"
      onClick={handleClose}
    >
      <div
        style={{
          ...modalStyles.panel,
          maxWidth: `${getScaledValue(600, scale)}px`,
          maxHeight: "90vh",
          overflowY: "auto",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Title */}
        <h2 id="form-modal-title" style={titleStyles}>
          {title}
        </h2>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {/* Form Fields */}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: `${getScaledValue(4, scale)}px`,
            }}
          >
            {fields.map((field, index) => (
              <FormField
                key={field.name}
                field={field}
                value={formData[field.name]}
                onChange={handleFieldChange}
                error={getFieldError(field.name)}
                disabled={isViewMode || loading}
                scale={scale}
                ref={index === 0 ? firstFieldRef : null}
                onBlur={() => handleFieldBlur(field.name)}
              />
            ))}
          </div>

          {/* Action Buttons */}
          <div
            style={{
              display: "flex",
              gap: `${getScaledValue(12, scale)}px`,
              justifyContent: "flex-end",
              marginTop: `${getScaledValue(24, scale)}px`,
              paddingTop: `${getScaledValue(16, scale)}px`,
              borderTop: "1px solid #E5E7EB",
            }}
          >
            <Button
              variant="outline"
              onClick={handleClose}
              scale={scale}
              disabled={loading}
              type="button"
            >
              {isViewMode ? "Close" : "Cancel"}
            </Button>

            {!isViewMode && (
              <Button
                variant="primary"
                type="submit"
                scale={scale}
                loading={loading}
              >
                {isAddMode ? "Add" : "Save Changes"}
              </Button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default FormModal;
