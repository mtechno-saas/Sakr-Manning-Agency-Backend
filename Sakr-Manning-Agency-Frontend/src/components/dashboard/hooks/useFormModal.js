// hooks/dashboard/useFormModal.js - FINAL PRODUCTION VERSION
/**
 * useFormModal - Reusable Form Modal Logic Hook
 * 
 * This hook centralizes all common form modal operations including:
 * - State management (form data, errors, loading)
 * - Validation
 * - Field change handlers
 * - Save/submit logic
 * - Error handling
 * - Success/error notifications
 * - Dirty state tracking
 * 
 * Benefits:
 * - Eliminates ~200 lines of duplicate code per modal
 * - Consistent behavior across all forms
 * - Single place to fix bugs
 * - Easy to add features to all modals
 * 
 * @module useFormModal
 * @version 1.0.0
 * 
 * @example
 * const {
 *   formData,
 *   errors,
 *   loading,
 *   isEditMode,
 *   handleChange,
 *   handleSave,
 * } = useFormModal({
 *   fieldConfig: COMPANY_FORM_FIELDS,
 *   record: company,
 *   onSave,
 *   onClose,
 *   successMessage: "Company saved successfully",
 * });
 */

import { useState, useEffect, useCallback } from "react";
import {
    getDefaultValues,
    populateFormData,
    validateFormData,
    transformForSave,
} from "../../../utils/dashboard/fieldConfigs";
import useNotification from "./useNotification";

/**
 * Form Modal Hook Configuration
 * @typedef {Object} UseFormModalOptions
 * @property {Array} fieldConfig - Field configuration array
 * @property {Object|null} record - Record to edit (null for create mode)
 * @property {Function} onSave - Save callback function
 * @property {Function} onClose - Close callback function
 * @property {String|Function} successMessage - Success notification message or function(isEdit) => message
 * @property {String} errorMessage - Error notification message (optional)
 * @property {Function} transformBeforeSave - Custom transform function before save (optional)
 * @property {Function} customValidation - Additional validation function (optional)
 */

/**
 * Form Modal Hook Return Value
 * @typedef {Object} UseFormModalReturn
 * @property {Object} formData - Current form state
 * @property {Object} errors - Validation errors
 * @property {Boolean} loading - Submit loading state
 * @property {Boolean} isDirty - Has unsaved changes
 * @property {Boolean} isEditMode - Create vs edit mode
 * @property {Function} handleChange - Single field change handler
 * @property {Function} handleBatchChange - Multiple fields change handler
 * @property {Function} handleSave - Submit handler with validation
 * @property {Function} handleClose - Close handler with dirty check
 * @property {Function} validateForm - Manual validation trigger
 * @property {Function} clearErrors - Clear all errors
 * @property {Function} clearError - Clear specific field error
 * @property {Function} resetForm - Reset to default values
 * @property {Function} getFieldValue - Get specific field value
 * @property {Function} getFieldError - Get specific field error
 * @property {Function} setFormData - Direct form data setter
 * @property {Function} setErrors - Direct errors setter
 */

/**
 * useFormModal Hook
 * @param {UseFormModalOptions} options - Hook configuration
 * @returns {UseFormModalReturn} Form modal state and handlers
 */
export const useFormModal = ({
    fieldConfig,
    record = null,
    onSave,
    onClose,
    successMessage,
    errorMessage,
    transformBeforeSave,
    customValidation,
}) => {
    const { notify } = useNotification();
    const isEditMode = !!record;

    // ============================================
    // STATE
    // ============================================

    /**
     * Form data state
     * Initialized from record if editing, or defaults if creating
     */
    const [formData, setFormData] = useState(() => {
        return record ? populateFormData(record, fieldConfig) : getDefaultValues(fieldConfig);
    });

    /**
     * Validation errors state
     * Object with field names as keys and error messages as values
     */
    const [errors, setErrors] = useState({});

    /**
     * Loading state for save operation
     */
    const [loading, setLoading] = useState(false);

    /**
     * Dirty state - tracks if form has unsaved changes
     */
    const [isDirty, setIsDirty] = useState(false);

    // ============================================
    // EFFECTS
    // ============================================

    /**
     * Reset form when record changes
     * Useful when modal is reused for different records
     */
    useEffect(() => {
        if (record) {
            setFormData(populateFormData(record, fieldConfig));
        } else {
            setFormData(getDefaultValues(fieldConfig));
        }
        setErrors({});
        setIsDirty(false);
        // NOTE: intentionally omitting `fieldConfig` from deps.
        // fieldConfig (enrichedFieldConfig) rebuilds every time options load,
        // which would reset the form mid-edit. We only want to reset when
        // the record itself changes (different modal open / close).
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [record]);

    // ============================================
    // HANDLERS
    // ============================================

    /**
     * Handle single field change
     * @param {string} fieldName - Name of field to change
     * @param {any} value - New value
     */
    const handleChange = useCallback((fieldName, value) => {
        setFormData((prev) => ({ ...prev, [fieldName]: value }));
        setIsDirty(true);

        // Clear error for this field
        setErrors((prev) => {
            if (prev[fieldName]) {
                const newErrors = { ...prev };
                delete newErrors[fieldName];
                return newErrors;
            }
            return prev;
        });
    }, []);

    /**
     * Handle multiple field changes at once
     * Useful for TypeaheadInputs that need to update both ID and display name
     * 
     * @param {Object} updates - Object with field names as keys and values
     * 
     * @example
     * handleBatchChange({
     *   user: 123,
     *   user_name: "John Doe",
     *   user_email: "john@example.com"
     * });
     */
    const handleBatchChange = useCallback((updates) => {
        setFormData((prev) => ({ ...prev, ...updates }));
        setIsDirty(true);

        // Clear errors for updated fields
        setErrors((prev) => {
            const newErrors = { ...prev };
            Object.keys(updates).forEach((key) => {
                delete newErrors[key];
            });
            return newErrors;
        });
    }, []);

    /**
     * Validate form
     * Runs both config-based validation and custom validation if provided
     * 
     * @returns {boolean} True if form is valid, false otherwise
     */
    const validateForm = useCallback(() => {
        // Run config-based validation
        let newErrors = validateFormData(formData, fieldConfig);

        // Run custom validation if provided
        if (customValidation) {
            const customErrors = customValidation(formData);
            newErrors = { ...newErrors, ...customErrors };
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    }, [formData, fieldConfig, customValidation]);

    /**
     * Handle save
     * Validates, transforms, and submits form data
     * 
     * @returns {Promise<boolean>} True if save succeeded, false otherwise
     */
    const handleSave = useCallback(async () => {
        // Validate form
        if (!validateForm()) {
            notify.error("Please fix the errors in the form");
            return false;
        }

        setLoading(true);

        try {
            // Transform data for save
            let dataToSave = transformForSave(formData, fieldConfig);

            // Apply custom transformation if provided
            if (transformBeforeSave) {
                dataToSave = transformBeforeSave(dataToSave);
            }

            // Call save callback
            await onSave(dataToSave);

            // Show success notification
            if (successMessage) {
                const message = typeof successMessage === "function"
                    ? successMessage(isEditMode)
                    : successMessage;
                notify.success(message);
            }

            // Close modal
            onClose();

            return true;
        } catch (error) {
            console.error("Failed to save:", error);

            // Show error notification
            const errMsg = error.message || errorMessage || "Failed to save. Please try again.";
            notify.error(errMsg);

            return false;
        } finally {
            setLoading(false);
        }
    }, [
        formData,
        fieldConfig,
        validateForm,
        transformBeforeSave,
        onSave,
        onClose,
        successMessage,
        errorMessage,
        isEditMode,
        notify,
    ]);

    /**
     * Handle close with dirty check
     * Shows confirmation if form has unsaved changes
     */
    const handleClose = useCallback(() => {
        if (isDirty) {
            const confirmed = window.confirm(
                "You have unsaved changes. Are you sure you want to close?"
            );
            if (!confirmed) return;
        }
        onClose();
    }, [isDirty, onClose]);

    // ============================================
    // UTILITY FUNCTIONS
    // ============================================

    /**
     * Clear all errors
     */
    const clearErrors = useCallback(() => {
        setErrors({});
    }, []);

    /**
     * Clear specific field error
     * @param {string} fieldName - Name of field to clear error for
     */
    const clearError = useCallback((fieldName) => {
        setErrors((prev) => {
            const newErrors = { ...prev };
            delete newErrors[fieldName];
            return newErrors;
        });
    }, []);

    /**
     * Reset form to default values
     * Useful for "Clear" or "Reset" buttons
     */
    const resetForm = useCallback(() => {
        setFormData(getDefaultValues(fieldConfig));
        setErrors({});
        setIsDirty(false);
    }, [fieldConfig]);

    /**
     * Get field value
     * @param {string} fieldName - Name of field
     * @returns {any} Field value
     */
    const getFieldValue = useCallback(
        (fieldName) => {
            return formData[fieldName];
        },
        [formData]
    );

    /**
     * Get field error
     * @param {string} fieldName - Name of field
     * @returns {string|null} Error message or null
     */
    const getFieldError = useCallback(
        (fieldName) => {
            return errors[fieldName] || null;
        },
        [errors]
    );

    /**
     * Check if field has error
     * @param {string} fieldName - Name of field
     * @returns {boolean} True if field has error
     */
    const hasFieldError = useCallback(
        (fieldName) => {
            return !!errors[fieldName];
        },
        [errors]
    );

    /**
     * Set field value
     * Alternative to handleChange for programmatic updates
     * @param {string} fieldName - Name of field
     * @param {any} value - New value
     */
    const setFieldValue = useCallback(
        (fieldName, value) => {
            handleChange(fieldName, value);
        },
        [handleChange]
    );

    /**
     * Set field error
     * Useful for setting server-side validation errors
     * @param {string} fieldName - Name of field
     * @param {string} errorMessage - Error message
     */
    const setFieldError = useCallback((fieldName, errorMessage) => {
        setErrors((prev) => ({
            ...prev,
            [fieldName]: errorMessage,
        }));
    }, []);

    /**
     * Check if form is valid
     * @returns {boolean} True if form has no errors
     */
    const isValid = useCallback(() => {
        return Object.keys(errors).length === 0;
    }, [errors]);

    /**
     * Check if form has any value
     * @returns {boolean} True if any field has a value
     */
    const hasAnyValue = useCallback(() => {
        return Object.values(formData).some((value) => {
            if (Array.isArray(value)) return value.length > 0;
            if (typeof value === "boolean") return true;
            return !!value;
        });
    }, [formData]);

    // ============================================
    // RETURN
    // ============================================

    return {
        // State
        formData,
        errors,
        loading,
        isDirty,
        isEditMode,

        // Primary Handlers
        handleChange,
        handleBatchChange,
        handleSave,
        handleClose,
        validateForm,

        // Error Management
        clearErrors,
        clearError,
        setFieldError,
        hasFieldError,

        // Field Access
        getFieldValue,
        getFieldError,
        setFieldValue,

        // Form Management
        resetForm,
        setFormData,
        setErrors,

        // Status Checks
        isValid,
        hasAnyValue,
    };
};

export default useFormModal;