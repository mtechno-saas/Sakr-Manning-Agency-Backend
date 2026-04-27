// services/Form/declarationService.js
// CRUD operations for Health Declaration (Single Object)
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";

/**
 * Declaration Service - Health Declaration (Single Object per User)
 * Endpoint: /api/users/declarations/
 * 
 * Note: Unlike other services, this manages a single declaration per user,
 * not a collection of items.
 */
export const declarationService = {
    /**
     * Get user's declaration
     * GET /api/users/declarations/?user={userId}
     * Returns the user's single declaration or null if not exists
     */
    getDeclaration: async (userId) => {
        try {
            const response = await api.get(`/users/declarations/`, {
                params: { user: userId },
            });

            // Backend returns array, but we expect only one declaration per user
            const declarations = response.data.results || response.data || [];

            return {
                success: true,
                data: declarations.length > 0 ? declarations[0] : null,
            };
        } catch (error) {
            console.error("Failed to load declaration:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: null,
            };
        }
    },

    /**
     * Create a new declaration
     * POST /api/users/declarations/
     */
    createDeclaration: async (userId, data) => {
        try {
            const payload = {
                user: userId,
                has_disease: data.has_disease || false,
                disease_details: data.disease_details || "",
                has_accident: data.has_accident || false,
                accident_details: data.accident_details || "",
                has_psychiatric_treatment: data.has_psychiatric_treatment || false,
                psychiatric_treatment_details: data.psychiatric_treatment_details || "",
                has_addiction: data.has_addiction || false,
                addiction_details: data.addiction_details || "",
                consent_given: data.consent_given || false,
                declaration_place: data.declaration_place || "",
                declaration_date: data.declaration_date || "",
                signature: data.signature || "",
            };

            const response = await api.post(`/users/declarations/`, payload);
            return {
                success: true,
                data: response.data,
                message: "Declaration created successfully",
            };
        } catch (error) {
            console.error("Failed to create declaration:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create declaration",
            };
        }
    },

    /**
     * Update existing declaration
     * PATCH /api/users/declarations/{id}/
     */
    updateDeclaration: async (id, data, userId) => {
        try {
            const payload = {
                user: userId || data.user,
                has_disease: data.has_disease,
                disease_details: data.disease_details || "",
                has_accident: data.has_accident,
                accident_details: data.accident_details || "",
                has_psychiatric_treatment: data.has_psychiatric_treatment,
                psychiatric_treatment_details: data.psychiatric_treatment_details || "",
                has_addiction: data.has_addiction,
                addiction_details: data.addiction_details || "",
                consent_given: data.consent_given,
                declaration_place: data.declaration_place || "",
                declaration_date: data.declaration_date || "",
                signature: data.signature || "",
            };

            // Remove undefined values
            Object.keys(payload).forEach((key) => {
                if (payload[key] === undefined) {
                    delete payload[key];
                }
            });

            const response = await api.patch(`/users/declarations/${id}/`, payload);
            return {
                success: true,
                data: response.data,
                message: "Declaration updated successfully",
            };
        } catch (error) {
            console.error("Failed to update declaration:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update declaration",
            };
        }
    },

    /**
     * Save declaration (create or update based on existence)
     * This is a helper method that decides whether to create or update
     */
    saveDeclaration: async (userId, data, existingId = null) => {
        if (existingId) {
            return await declarationService.updateDeclaration(existingId, data, userId);
        } else {
            return await declarationService.createDeclaration(userId, data);
        }
    },
};

export default declarationService;