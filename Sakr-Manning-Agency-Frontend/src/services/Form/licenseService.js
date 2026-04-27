// services/Form/licenseService.js
// CRUD operations for Licenses/Certificates (separate endpoint)
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";

/**
 * License CRUD operations
 * Endpoint: /api/my-licenses/
 */
export const licenseService = {
    /**
     * Get all licenses for a user
     * GET /api/my-licenses/?user={userId}
     */
    getLicenses: async (userId) => {
        try {
            const response = await api.get(`/my-licenses/`, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data.results || response.data || [],
            };
        } catch (error) {
            console.error("Failed to load licenses:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: [],
            };
        }
    },

    /**
     * Create a new license record
     * POST /api/my-licenses/
     */
    createLicense: async (userId, data) => {
        try {
            // Handle file upload
            const formData = new FormData();
            formData.append("user", userId);
            formData.append("document_name", data.document_name);
            formData.append("document_number", data.document_number);
            formData.append("country_of_issue", data.country_of_issue);
            formData.append("issue_date", data.issue_date);
            formData.append("expiration_date", data.expiration_date);

            if (data.document_file instanceof File) {
                formData.append("document_file", data.document_file);
            } else if (data.file instanceof File) {
                formData.append("document_file", data.file);
            }

            const response = await api.post(`/my-licenses/`, formData, {
                params: { user: userId },
                headers: { "Content-Type": "multipart/form-data" },
            });
            return {
                success: true,
                data: response.data,
                message: "License record created successfully",
            };
        } catch (error) {
            console.error("Failed to create license:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create license record",
            };
        }
    },

    /**
     * Update a license record
     * PATCH /api/my-licenses/{id}/?user={userId}
     */
    updateLicense: async (id, data, userId) => {
        try {
            const formData = new FormData();

            // Ensure user ID is sent
            if (userId || data.user) {
                formData.append("user", userId || data.user);
            }

            if (data.document_name) {
                formData.append("document_name", data.document_name);
            }
            if (data.document_number) {
                formData.append("document_number", data.document_number);
            }
            if (data.country_of_issue) {
                formData.append("country_of_issue", data.country_of_issue);
            }
            if (data.issue_date) {
                formData.append("issue_date", data.issue_date);
            }
            if (data.expiration_date) {
                formData.append("expiration_date", data.expiration_date);
            }

            if (data.document_file instanceof File) {
                formData.append("document_file", data.document_file);
            } else if (data.file instanceof File) {
                formData.append("document_file", data.file);
            }

            const response = await api.patch(`/my-licenses/${id}/`, formData, {
                params: { user: userId },
                headers: { "Content-Type": "multipart/form-data" },
            });
            return {
                success: true,
                data: response.data,
                message: "License record updated successfully",
            };
        } catch (error) {
            console.error("Failed to update license:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update license record",
            };
        }
    },

    /**
     * Delete a license record
     * DELETE /api/my-licenses/{id}/?user={userId}
     */
    deleteLicense: async (id, userId) => {
        try {
            await api.delete(`/my-licenses/${id}/`, {
                params: { user: userId },
            });
            return {
                success: true,
                message: "License record deleted successfully",
            };
        } catch (error) {
            console.error("Failed to delete license:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to delete license record",
            };
        }
    },

    /**
     * Map backend license data to frontend format (snake_case preserved)
     */
    mapToFrontend: (data) => ({
        id: data.id,
        user: data.user,
        document_name: data.document_name,
        document_number: data.document_number,
        country_of_issue: data.country_of_issue,
        issue_date: data.issue_date,
        expiration_date: data.expiration_date,
        document_file: data.document_file,
        created_at: data.created_at,
        updated_at: data.updated_at,
    }),
};

export default licenseService;