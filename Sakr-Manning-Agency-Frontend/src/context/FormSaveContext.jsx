import { useState, useCallback, createContext, useContext } from "react";
import { userService } from "../services/Form/userService";

const FormSaveContext = createContext(null);

/**
 * FormSaveProvider - Provides save functionality and navigation to the form.
 *
 * NOTE: All field-name translation (frontend ↔ backend) is handled by formMapper.js.
 * This context passes data straight through to userService without re-mapping.
 */
export function FormSaveProvider({ children, userId, currentStep, onStepChange }) {
    const [isSaving, setIsSaving] = useState(false);
    const [lastSavedData, setLastSavedData] = useState(null);

    /**
     * Navigate to a specific step
     */
    const goToStep = useCallback((stepIndex) => {
        if (onStepChange && typeof stepIndex === 'number') {
            onStepChange(stepIndex);
        }
    }, [onStepChange]);

    /**
     * Save form data for the current step
     * @param {Object} formData - Complete form data from react-hook-form
     * @returns {Promise<{success: boolean, data?: any, message?: string}>}
     */
    const saveFormData = useCallback(async (formData) => {
        if (!userId) {
            console.error("No userId provided to FormSaveProvider");
            return { success: false, message: "User ID is missing" };
        }

        setIsSaving(true);

        try {
            // Pass data directly — formMapper.js handles all translation
            const result = await userService.saveStepData(
                userId,
                currentStep,
                formData,
                lastSavedData
            );

            if (result.success) {
                setLastSavedData(result.data);
                return {
                    success: true,
                    data: result.data,
                    message: result.message,
                    syncErrors: result.syncErrors || [],
                };
            }

            return result;
        } catch (error) {
            console.error("Save error in FormSaveProvider:", error);
            return {
                success: false,
                message: "An unexpected error occurred while saving",
            };
        } finally {
            setIsSaving(false);
        }
    }, [userId, currentStep, lastSavedData]);

    /**
     * Save complete form (for final submission)
     */
    const saveCompleteForm = useCallback(async (formData) => {
        if (!userId) {
            return { success: false, message: "User ID is missing" };
        }

        setIsSaving(true);

        try {
            const result = await userService.saveCompleteForm(userId, formData);

            if (result.success) {
                setLastSavedData(result.data);
                return {
                    success: true,
                    data: result.data,
                    message: result.message,
                    syncErrors: result.syncErrors || [],
                };
            }

            return result;
        } catch (error) {
            console.error("Complete save error:", error);
            return { success: false, message: "Failed to save form" };
        } finally {
            setIsSaving(false);
        }
    }, [userId]);

    /**
     * Load existing form data
     */
    const loadFormData = useCallback(async () => {
        if (!userId) {
            return { success: false, message: "User ID is missing" };
        }

        try {
            const result = await userService.loadFullUserProfile(userId);

            if (result.success) {
                setLastSavedData(result.data);
                return {
                    success: true,
                    data: result.data,
                    message: result.message,
                };
            }

            return result;
        } catch (error) {
            console.error("Load error:", error);
            return { success: false, message: "Failed to load form data" };
        }
    }, [userId]);

    const value = {
        saveFormData,
        saveCompleteForm,
        loadFormData,
        goToStep,
        isSaving,
        lastSavedData,
        setLastSavedData,
    };

    return (
        <FormSaveContext.Provider value={value}>
            {children}
        </FormSaveContext.Provider>
    );
}

/**
 * Hook to use form save functionality
 */
export function useFormSave() {
    const context = useContext(FormSaveContext);
    if (!context) {
        throw new Error("useFormSave must be used within a FormSaveProvider");
    }
    return context;
}

export default FormSaveContext;