// services/Form/languageService.js
// CRUD operations for Languages (separate endpoint)
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";

/**
 * Language CRUD operations
 * Endpoint: /api/users/user-languages/
 */
export const languageService = {
    /**
     * Get all languages for a user
     * GET /api/users/user-languages/?user={userId}
     */
    getLanguages: async (userId) => {
        try {
            const response = await api.get(`/users/user-languages/`, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data.results || response.data || [],
            };
        } catch (error) {
            console.error("Failed to load languages:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: [],
            };
        }
    },

    /**
     * Create a new language record
     * POST /api/users/user-languages/
     */
    createLanguage: async (userId, data) => {
        try {
            const payload = {
                user: userId,
                language: data.language,
                general_remarks: data.general_remarks,
                speaking_level: data.speaking_level,
                writing_level: data.writing_level,
                reading_level: data.reading_level,
                cefr_level: data.cefr_level,
                cefr_description: data.cefr_description,
                attachment: data.attachment,
            };
            // Use FormData if a file is attached
            if (data.file instanceof File) {
                const formData = new FormData();
                Object.keys(payload).forEach((key) => {
                    if (payload[key] !== undefined && payload[key] !== null) {
                        formData.append(key, payload[key]);
                    }
                });
                formData.append("file", data.file);

                const response = await api.post(`/users/user-languages/`, formData, {
                    params: { user: userId },
                    headers: { "Content-Type": "multipart/form-data" },
                });
                return {
                    success: true,
                    data: response.data,
                    message: "Language record created successfully",
                };
            }

            const response = await api.post(`/users/user-languages/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Language record created successfully",
            };
        } catch (error) {
            console.error("Failed to create language:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create language record",
            };
        }
    },

    /**
     * Update a language record
     * PATCH /api/users/user-languages/{id}/?user={userId}
     */
    updateLanguage: async (id, data, userId) => {
        try {
            const payload = {
                user: userId || data.user,
                language: data.language,
                general_remarks: data.general_remarks,
                speaking_level: data.speaking_level,
                writing_level: data.writing_level,
                reading_level: data.reading_level,
                cefr_level: data.cefr_level,
                cefr_description: data.cefr_description,
            };

            // Remove undefined values
            Object.keys(payload).forEach((key) => {
                if (payload[key] === undefined) {
                    delete payload[key];
                }
            });

            // Use FormData if a file is attached
            if (data.file instanceof File) {
                const formData = new FormData();
                Object.keys(payload).forEach((key) => {
                    if (payload[key] !== undefined && payload[key] !== null) {
                        formData.append(key, payload[key]);
                    }
                });
                formData.append("file", data.file);

                const response = await api.patch(`/users/user-languages/${id}/`, formData, {
                    params: { user: userId },
                    headers: { "Content-Type": "multipart/form-data" },
                });
                return {
                    success: true,
                    data: response.data,
                    message: "Language record updated successfully",
                };
            }

            const response = await api.patch(`/users/user-languages/${id}/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Language record updated successfully",
            };
        } catch (error) {
            console.error("Failed to update language:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update language record",
            };
        }
    },

    /**
     * Delete a language record
     * DELETE /api/users/user-languages/{id}/?user={userId}
     */
    deleteLanguage: async (id, userId) => {
        try {
            await api.delete(`/users/user-languages/${id}/`, {
                params: { user: userId },
            });
            return {
                success: true,
                message: "Language record deleted successfully",
            };
        } catch (error) {
            console.error("Failed to delete language:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to delete language record",
            };
        }
    },

    /**
     * Map frontend language data to backend format
     */
    mapToBackend: (data) => ({
        user: data.user,
        language: data.language,
        general_remarks: data.general_remarks,
        speaking_level: data.speaking_level,
        writing_level: data.writing_level,
        reading_level: data.reading_level,
        cefr_level: data.cefr_level,
        cefr_description: data.cefr_description,
    }),

    /**
     * Map backend language data to frontend format (snake_case preserved)
     */
    mapToFrontend: (data) => ({
        id: data.id,
        language: data.language,
        general_remarks: data.general_remarks,
        speaking_level: data.speaking_level,
        writing_level: data.writing_level,
        reading_level: data.reading_level,
        cefr_level: data.cefr_level,
        cefr_description: data.cefr_description,
    }),
};

export default languageService;