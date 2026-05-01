// services/Form/seaServiceService.js
// CRUD operations for Sea Services (separate endpoint)
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";

/**
 * Sea Service CRUD operations
 * Endpoint: /api/users/sea-services/
 */
export const seaServiceService = {
    /**
     * Get all sea services for a user
     * GET /api/users/sea-services/?user={userId}
     */
    getSeaServices: async (userId) => {
        try {
            const response = await api.get(`/users/sea-services/`, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data.results || response.data || [],
            };
        } catch (error) {
            console.error("Failed to load sea services:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: [],
            };
        }
    },

    /**
     * Create a new sea service record
     * POST /api/users/sea-services/
     */
    createSeaService: async (userId, data) => {
        try {
            const payload = {
                user: userId,
                company_name: data.company_name,
                rank: data.rank,
                vessel_name: data.vessel_name,
                imo_number: data.imo_number,
                vessel_name_imo: data.vessel_name_imo,
                flag: data.flag,
                signed_on: data.signed_on,
                signed_off: data.signed_off,
                period: data.period,
                vessel_type: data.vessel_type,
                dwt: data.dwt,
                grt: data.grt,
                dwt_grt: data.dwt_grt,
                engine_type: data.engine_type,
                bh: data.bh,
                kw: data.kw,
                engine_type_bh_kw: data.engine_type_bh_kw,
                reason_for_sign_off: data.reason_for_sign_off,
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

                const response = await api.post(`/users/sea-services/`, formData, {
                    params: { user: userId },
                    headers: { "Content-Type": "multipart/form-data" },
                });
                return {
                    success: true,
                    data: response.data,
                    message: "Sea service record created successfully",
                };
            }

            const response = await api.post(`/users/sea-services/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Sea service record created successfully",
            };
        } catch (error) {
            console.error("Failed to create sea service:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create sea service record",
            };
        }
    },

    /**
     * Update a sea service record
     * PATCH /api/users/sea-services/{id}/?user={userId}
     */
    updateSeaService: async (id, data, userId) => {
        try {
            const payload = {
                user: userId || data.user,
                company_name: data.company_name,
                rank: data.rank,
                vessel_name: data.vessel_name,
                imo_number: data.imo_number,
                vessel_name_imo: data.vessel_name_imo,
                flag: data.flag,
                signed_on: data.signed_on,
                signed_off: data.signed_off,
                period: data.period,
                vessel_type: data.vessel_type,
                dwt: data.dwt,
                grt: data.grt,
                dwt_grt: data.dwt_grt,
                engine_type: data.engine_type,
                bh: data.bh,
                kw: data.kw,
                engine_type_bh_kw: data.engine_type_bh_kw,
                reason_for_sign_off: data.reason_for_sign_off,
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

                const response = await api.patch(`/users/sea-services/${id}/`, formData, {
                    params: { user: userId },
                    headers: { "Content-Type": "multipart/form-data" },
                });
                return {
                    success: true,
                    data: response.data,
                    message: "Sea service record updated successfully",
                };
            }

            const response = await api.patch(`/users/sea-services/${id}/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Sea service record updated successfully",
            };
        } catch (error) {
            console.error("Failed to update sea service:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update sea service record",
            };
        }
    },

    /**
     * Delete a sea service record
     * DELETE /api/users/sea-services/{id}/?user={userId}
     */
    deleteSeaService: async (id, userId) => {
        try {
            await api.delete(`/users/sea-services/${id}/`, {
                params: { user: userId },
            });
            return {
                success: true,
                message: "Sea service record deleted successfully",
            };
        } catch (error) {
            console.error("Failed to delete sea service:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to delete sea service record",
            };
        }
    },

    /**
     * Map frontend sea service data to backend format
     */
    mapToBackend: (data) => ({
        company_name: data.company_name,
        rank: data.rank,
        vessel_name: data.vessel_name,
        imo_number: data.imo_number,
        vessel_name_imo: data.vessel_name_imo,
        flag: data.flag,
        signed_on: data.signed_on,
        signed_off: data.signed_off,
        period: data.period,
        vessel_type: data.vessel_type,
        dwt: data.dwt,
        grt: data.grt,
        dwt_grt: data.dwt_grt,
        engine_type: data.engine_type,
        bh: data.bh,
        kw: data.kw,
        engine_type_bh_kw: data.engine_type_bh_kw,
        reason_for_sign_off: data.reason_for_sign_off,
    }),

    /**
     * Map backend sea service data to frontend format (snake_case preserved)
     */
    mapToFrontend: (data) => ({
        id: data.id,
        user: data.user,
        company_name: data.company_name,
        rank: data.rank,
        vessel_name: data.vessel_name,
        imo_number: data.imo_number,
        vessel_name_imo: data.vessel_name_imo,
        flag: data.flag,
        signed_on: data.signed_on,
        signed_off: data.signed_off,
        period: data.period,
        vessel_type: data.vessel_type,
        dwt: data.dwt,
        grt: data.grt,
        dwt_grt: data.dwt_grt,
        engine_type: data.engine_type,
        bh: data.bh,
        kw: data.kw,
        engine_type_bh_kw: data.engine_type_bh_kw,
        reason_for_sign_off: data.reason_for_sign_off,
    }),
};

export default seaServiceService;