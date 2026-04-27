// services/Form/nextOfKinService.js
// CRUD operations for Next of Kin / Additional Emergency Contacts
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";

/**
 * Next of Kin CRUD operations
 * Endpoint: /api/users/next-of-kin/
 */
export const nextOfKinService = {
    /**
     * Get all next-of-kin records for a user
     * GET /api/users/next-of-kin/?user={userId}
     */
    getNextOfKin: async (userId) => {
        try {
            const response = await api.get(`/users/next-of-kin/`, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data.results || response.data || [],
            };
        } catch (error) {
            console.error("Failed to load next-of-kin:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: [],
            };
        }
    },

    /**
     * Create a new next-of-kin record
     * POST /api/users/next-of-kin/
     */
    createNextOfKin: async (userId, data) => {
        try {
            const payload = {
                user: userId,
                full_name: data.full_name,
                relationship: data.relationship,
                address_country: data.address_country,
                phone: data.phone,
                phone2: data.phone2,
                email: data.email,
            };

            // Remove undefined values
            Object.keys(payload).forEach((key) => {
                if (payload[key] === undefined) {
                    delete payload[key];
                }
            });

            const response = await api.post(`/users/next-of-kin/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Emergency contact created successfully",
            };
        } catch (error) {
            console.error("Failed to create next-of-kin:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create emergency contact",
            };
        }
    },

    /**
     * Update a next-of-kin record
     * PATCH /api/users/next-of-kin/{id}/?user={userId}
     */
    updateNextOfKin: async (id, data, userId) => {
        try {
            const payload = {
                user: userId || data.user,
                full_name: data.full_name,
                relationship: data.relationship,
                address_country: data.address_country,
                phone: data.phone,
                phone2: data.phone2,
                email: data.email,
            };

            // Remove undefined values
            Object.keys(payload).forEach((key) => {
                if (payload[key] === undefined) {
                    delete payload[key];
                }
            });

            const response = await api.patch(`/users/next-of-kin/${id}/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Emergency contact updated successfully",
            };
        } catch (error) {
            console.error("Failed to update next-of-kin:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update emergency contact",
            };
        }
    },

    /**
     * Delete a next-of-kin record
     * DELETE /api/users/next-of-kin/{id}/?user={userId}
     */
    deleteNextOfKin: async (id, userId) => {
        try {
            await api.delete(`/users/next-of-kin/${id}/`, {
                params: { user: userId },
            });
            return {
                success: true,
                message: "Emergency contact deleted successfully",
            };
        } catch (error) {
            console.error("Failed to delete next-of-kin:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to delete emergency contact",
            };
        }
    },

    /**
     * Map frontend next-of-kin data to backend format
     */
    mapToBackend: (data) => ({
        full_name: data.full_name,
        relationship: data.relationship,
        address_country: data.address_country,
        phone: data.phone,
        phone2: data.phone2,
        email: data.email,
    }),

    /**
     * Map backend next-of-kin data to frontend format
     */
    mapToFrontend: (data) => ({
        id: data.id,
        user: data.user,
        full_name: data.full_name,
        relationship: data.relationship,
        address_country: data.address_country,
        phone: data.phone,
        phone2: data.phone2,
        email: data.email,
    }),
};

export default nextOfKinService;
