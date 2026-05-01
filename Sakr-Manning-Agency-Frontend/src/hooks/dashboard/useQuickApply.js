// hooks/useQuickApply.js
import { useState } from 'react';
import { cvSubmissionsApi } from '../../services/Dashboard/cvSubmissionsApi';

export const useQuickApply = () => {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [error, setError] = useState(null);

    /**
     * Submit a quick apply application
     * @param {Object} data - Form data containing full_name, email, phone_number, position, job_position, job_position_details, file
     * @param {Array} ranks - Array of rank objects to map position ID to name
     * @returns {Promise<{success: boolean, data?: any, error?: string}>}
     */
    const submitApplication = async (data, ranks = []) => {
        setIsSubmitting(true);
        setError(null);

        try {
            // Create FormData object
            const formData = new FormData();

            // Required fields according to API documentation
            formData.append("title", "CV Application");

            if (data.file && data.file[0]) {
                formData.append("file", data.file[0]);
            } else {
                throw new Error("CV file is required");
            }

            // User information (required for new applicants)
            if (!data.full_name || !data.email) {
                throw new Error("Name and email are required");
            }

            formData.append("name", data.full_name);
            formData.append("email", data.email);

            if (data.phone_number) {
                formData.append("phone_number", data.phone_number);
            }

            // Position - convert ID to name if ranks provided
            if (data.position) {
                const selectedRank = ranks.find(r => r.id === parseInt(data.position));
                formData.append("position", selectedRank?.name || data.position);
            }

            // Job Position (Vacancy)
            if (data.job_position) {
                formData.append("job_position", data.job_position);
            }

            if (data.job_position_details) {
                formData.append("job_position_details", JSON.stringify(data.job_position_details));
            }

            // Submit to API
            const result = await cvSubmissionsApi.createDocument(formData);

            setIsSubmitted(true);
            setIsSubmitting(false);

            return {
                success: true,
                data: result
            };

        } catch (err) {
            const errorMessage = err.message || "Failed to submit application. Please try again.";
            setError(errorMessage);
            setIsSubmitting(false);

            return {
                success: false,
                error: errorMessage
            };
        }
    };

    /**
     * Reset the hook state
     */
    const reset = () => {
        setIsSubmitting(false);
        setIsSubmitted(false);
        setError(null);
    };

    /**
     * Clear error message
     */
    const clearError = () => {
        setError(null);
    };

    return {
        submitApplication,
        isSubmitting,
        isSubmitted,
        error,
        reset,
        clearError
    };
};