// services/Form/vaccinationService.js
// CRUD operations for Vaccinations/Health Records (separate endpoint)
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";
import { VACCINATION_OPTIONS } from "../../config/formConfig";

// Re-export for backwards compatibility
export { VACCINATION_OPTIONS };

/**
 * Vaccination CRUD operations
 * Endpoint: /api/vaccinations/
 */
export const vaccinationService = {
    /**
     * Get all vaccinations for a user
     * GET /api/vaccinations/?user={userId}
     */
    getVaccinations: async (userId) => {
        try {
            const response = await api.get(`/vaccinations/`, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data.results || response.data || [],
            };
        } catch (error) {
            console.error("Failed to load vaccinations:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: [],
            };
        }
    },

    /**
     * Create a new vaccination record
     * POST /api/vaccinations/
     */
    createVaccination: async (userId, data) => {
        try {
            const formData = new FormData();
            formData.append("user", userId);
            formData.append("name", data.name);
            formData.append("number", data.number);
            formData.append("issue_date", data.issue_date || data.issueDate);
            formData.append("expiry_date", data.expiry_date || data.expiryDate);
            formData.append("issued_by", data.issued_by || data.issuedBy);
            formData.append("issued_at", data.issued_at || data.issuedAt);

            if (data.disease) formData.append("disease", data.disease);
            if (data.first_date || data.firstDate) {
                formData.append("first_date", data.first_date || data.firstDate);
            }
            if (data.last_date || data.lastDate) {
                formData.append("last_date", data.last_date || data.lastDate);
            }
            if (data.remarks) formData.append("remarks", data.remarks);

            if (data.document instanceof File) {
                formData.append("document", data.document);
            } else if (data.file instanceof File) {
                formData.append("document", data.file);
            }

            const response = await api.post(`/vaccinations/`, formData, {
                params: { user: userId },
                headers: { "Content-Type": "multipart/form-data" },
            });
            return {
                success: true,
                data: response.data,
                message: "Vaccination record created successfully",
            };
        } catch (error) {
            console.error("Failed to create vaccination:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create vaccination record",
            };
        }
    },

    /**
     * Update a vaccination record
     * PATCH /api/vaccinations/{id}/?user={userId}
     */
    updateVaccination: async (id, data, userId) => {
        try {
            const formData = new FormData();

            // Ensure user ID is sent
            if (userId || data.user) {
                formData.append("user", userId || data.user);
            }

            if (data.name) formData.append("name", data.name);
            if (data.number) formData.append("number", data.number);
            if (data.issue_date || data.issueDate) {
                formData.append("issue_date", data.issue_date || data.issueDate);
            }
            if (data.expiry_date || data.expiryDate) {
                formData.append("expiry_date", data.expiry_date || data.expiryDate);
            }
            if (data.issued_by || data.issuedBy) {
                formData.append("issued_by", data.issued_by || data.issuedBy);
            }
            if (data.issued_at || data.issuedAt) {
                formData.append("issued_at", data.issued_at || data.issuedAt);
            }
            if (data.disease) formData.append("disease", data.disease);
            if (data.first_date || data.firstDate) {
                formData.append("first_date", data.first_date || data.firstDate);
            }
            if (data.last_date || data.lastDate) {
                formData.append("last_date", data.last_date || data.lastDate);
            }
            if (data.remarks) formData.append("remarks", data.remarks);

            if (data.document instanceof File) {
                formData.append("document", data.document);
            } else if (data.file instanceof File) {
                formData.append("document", data.file);
            }

            const response = await api.patch(`/vaccinations/${id}/`, formData, {
                params: { user: userId },
                headers: { "Content-Type": "multipart/form-data" },
            });
            return {
                success: true,
                data: response.data,
                message: "Vaccination record updated successfully",
            };
        } catch (error) {
            console.error("Failed to update vaccination:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update vaccination record",
            };
        }
    },

    /**
     * Delete a vaccination record
     * DELETE /api/vaccinations/{id}/?user={userId}
     */
    deleteVaccination: async (id, userId) => {
        try {
            await api.delete(`/vaccinations/${id}/`, {
                params: { user: userId },
            });
            return {
                success: true,
                message: "Vaccination record deleted successfully",
            };
        } catch (error) {
            console.error("Failed to delete vaccination:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to delete vaccination record",
            };
        }
    },

    /**
     * Map backend vaccination data to frontend format (snake_case to match FORM_FIELDS.HEALTH)
     */
    mapToFrontend: (data) => ({
        id: data.id,
        user: data.user,
        name: data.name,
        number: data.number,
        issue_date: data.issue_date,
        expiry_date: data.expiry_date,
        issued_by: data.issued_by,
        issued_at: data.issued_at,
        disease: data.disease,
        first_date: data.first_date,
        last_date: data.last_date,
        remarks: data.remarks,
        document: data.document,
        created_at: data.created_at,
        updated_at: data.updated_at,
    }),
};

export default vaccinationService;