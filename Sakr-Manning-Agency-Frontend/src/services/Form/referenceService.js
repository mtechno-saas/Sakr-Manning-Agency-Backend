// services/Form/referenceService.js
// CRUD operations for Professional References
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";

/**
 * Reference Service - Professional References CRUD
 * Endpoint: /api/users/references/
 */
export const referenceService = {
    /**
     * Get all references for a user
     * GET /api/users/references/?user={userId}
     */
    getReferences: async (userId) => {
        try {
            const response = await api.get(`/users/references/`, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data.results || response.data || [],
            };
        } catch (error) {
            console.error("Failed to load references:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: [],
            };
        }
    },

    /**
     * Create a new reference record
     * POST /api/users/references/
     */
    createReference: async (userId, data) => {
        try {
            const payload = {
                user: userId,
                number: data.number,
                name: data.name,
                company_name: data.company_name,
                management: data.management,
                country: data.country,
                position: data.position,
                email: data.email,
                tel: data.tel,
            };

            // Remove undefined values
            Object.keys(payload).forEach((key) => {
                if (payload[key] === undefined) {
                    delete payload[key];
                }
            });

            const response = await api.post(`/users/references/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Reference created successfully",
            };
        } catch (error) {
            console.error("Failed to create reference:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create reference",
            };
        }
    },

    /**
     * Update a reference record
     * PATCH /api/users/references/{id}/?user={userId}
     */
    updateReference: async (id, data, userId) => {
        try {
            const payload = {
                user: userId || data.user,
                number: data.number,
                name: data.name,
                company_name: data.company_name,
                management: data.management,
                country: data.country,
                position: data.position,
                email: data.email,
                tel: data.tel,
            };

            // Remove undefined values
            Object.keys(payload).forEach((key) => {
                if (payload[key] === undefined) {
                    delete payload[key];
                }
            });

            const response = await api.patch(`/users/references/${id}/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Reference updated successfully",
            };
        } catch (error) {
            console.error("Failed to update reference:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update reference",
            };
        }
    },

    /**
     * Delete a reference record
     * DELETE /api/users/references/{id}/?user={userId}
     */
    deleteReference: async (id, userId) => {
        try {
            await api.delete(`/users/references/${id}/`, {
                params: { user: userId },
            });
            return {
                success: true,
                message: "Reference deleted successfully",
            };
        } catch (error) {
            console.error("Failed to delete reference:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to delete reference",
            };
        }
    },
};

export default referenceService;