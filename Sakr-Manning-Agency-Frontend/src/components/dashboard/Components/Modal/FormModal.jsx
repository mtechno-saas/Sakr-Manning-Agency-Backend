// components/dashboard/Common/FormModal.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { BaseModal } from './BaseModal';
import { useUnsavedChanges } from '../../hooks/useUnsavedChanges';
import useKeyboardShortcuts from '../../hooks/useKeyboardShortcuts';
import Button from '../../../common/Button';
import useNotification from '../../hooks/useNotification';

/**
@param {boolean} isOpen - Controls modal visibility
@param {function} onClose - Close handler
@param {function} onSave - Save handler (receives formData)
@param {string} title - Modal title
@param {object} initialData - Initial form data
@param {boolean} isEditMode - Whether editing existing data
@param {string} size - Modal size
@param {function} children - Render prop function: ({ formData, errors, handleChange, setErrors })
@param {boolean} showUnsavedWarning - Show warning for unsaved changes
@param {function} validateOnSubmit - Custom validation function
@param {number} scale - Scale factor
*/

export function FormModal({
    isOpen,
    onClose,
    onSave,
    title,
    subtitle,
    initialData = {},
    isEditMode = false,
    size = 'md',
    children,
    showUnsavedWarning = true,
    validateOnSubmit,
    scale = 1,
}) {
    const { notify } = useNotification();
    const [formData, setFormData] = useState(initialData);
    const [errors, setErrors] = useState({});
    const [isDirty, setIsDirty] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Track unsaved changes
    useUnsavedChanges(isDirty && showUnsavedWarning && isOpen);
    // Reset form when modal opens/closes or initialData changes
    useEffect(() => {
        if (isOpen) {
            setFormData(initialData);
            setIsDirty(false);
            setErrors({});
        }
    }, [isOpen, initialData]);
    // Handle field change
    const handleChange = useCallback((field, value) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
        setIsDirty(true);
        // Clear error for this field
        setErrors((prev) => {
            if (prev[field]) {
                const newErrors = { ...prev };
                delete newErrors[field];
                return newErrors;
            }
            return prev;
        });
    }, []);
    // Handle close with unsaved changes check
    const handleClose = useCallback(() => {
        if (isDirty && showUnsavedWarning) {
            const confirmed = window.confirm(
                'You have unsaved changes. Are you sure you want to close?'
            );
            if (!confirmed) return;
        }
        onClose();
    }, [isDirty, showUnsavedWarning, onClose]);
    // Handle form submission
    const handleSubmit = useCallback(async () => {
        // Run validation if provided
        if (validateOnSubmit) {
            const validationErrors = validateOnSubmit(formData);
            if (validationErrors && Object.keys(validationErrors).length > 0) {
                setErrors(validationErrors);
                notify.error('Please fix the errors in the form');
                return;
            }
        }
        setIsSubmitting(true);

        try {
            await onSave(formData);
            setIsDirty(false);
            // Don't close here - let parent handle it via onSave callback
        } catch (error) {
            console.error('Form submission error:', error);
            notify.error(error.message || 'Failed to save. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    }, [formData, onSave, validateOnSubmit, notify]);
    // Keyboard shortcuts for save
    useKeyboardShortcuts(
        {
            'Control+s': (e) => {
                e.preventDefault();
                if (!isSubmitting) handleSubmit();
            },
            'Control+Enter': (e) => {
                e.preventDefault();
                if (!isSubmitting) handleSubmit();
            },
        },
        isOpen
    );
    // Footer with action buttons
    const footer = (
        <div
            style={{
                display: 'flex',
                gap: `${Math.round(12 * scale)}px`,
                justifyContent: 'flex-end',
                alignItems: 'center',
            }}
        >
            {/* Keyboard shortcut hint */}
            <div
                style={{
                    fontSize: `${Math.round(11 * scale)}px`,
                    color: '#9CA3AF',
                    marginRight: 'auto',
                }}
            >
                <kbd
                    style={{
                        padding: `${Math.round(2 * scale)}px ${Math.round(6 * scale)}px`,
                        backgroundColor: '#F3F4F6',
                        borderRadius: `${Math.round(4 * scale)}px`,
                        fontSize: `${Math.round(10 * scale)}px`,
                        fontFamily: 'monospace',
                    }}
                >
                    Esc
                </kbd>{' '}
                to close •{' '}
                <kbd
                    style={{
                        padding: `${Math.round(2 * scale)}px ${Math.round(6 * scale)}px`,
                        backgroundColor: '#F3F4F6',
                        borderRadius: `${Math.round(4 * scale)}px`,
                        fontSize: `${Math.round(10 * scale)}px`,
                        fontFamily: 'monospace',
                    }}
                >
                    Ctrl+Enter
                </kbd>{' '}
                to save
            </div>

            <Button variant="outline" onClick={handleClose} scale={scale} disabled={isSubmitting}>
                Cancel
            </Button>
            <Button
                variant="primary"
                onClick={handleSubmit}
                scale={scale}
                disabled={isSubmitting}
                loading={isSubmitting}
            >
                {isSubmitting ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
            </Button>
        </div>
    );
    return (
        <BaseModal
            isOpen={isOpen}
            onClose={handleClose}
            title={title}
            subtitle={subtitle}
            size={size}
            footer={footer}
            scale={scale}
            closeOnOverlayClick={!isDirty} // Prevent accidental close if dirty
        >
            {typeof children === 'function'
                ? children({ formData, errors, handleChange, setErrors, isDirty, isSubmitting })
                : children}
        </BaseModal>
    );
}
export default FormModal;
