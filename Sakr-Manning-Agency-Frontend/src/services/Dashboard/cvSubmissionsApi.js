// services/Dashboard/cvSubmissionsApi.js
import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";
import config from "../Auth/config.js";

export const cvSubmissionsApi = {
    // =========================================================================
    // SECTION 2: CV DOCUMENTS (Public Uploads / Seafarer Profile Generation)
    // Endpoint: /api/documents/
    // =========================================================================

    /**
     * Create Document / Quick Apply (Public Access)
     * Maps to Section 2 (Documents) in backend
     * @param {FormData} formData - Contains file, name, email, phone_number, position, title
     */
    createDocument: async (formData) => {
        try {
            const response = await api.post(config.ENDPOINTS.DOCUMENTS, formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            return response.data;
        } catch (error) {
            console.error("Failed to submit document:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Get all Documents (Section 2)
     * @param {Object} filters - { page, search, status }
     */
    getDocuments: async (filters = {}) => {
        try {
            const params = new URLSearchParams();
            if (filters.page) params.append("page", filters.page);
            if (filters.search) params.append("search", filters.search);
            if (filters.status) params.append("status", filters.status);

            const queryString = params.toString();
            const endpoint = queryString
                ? `${config.ENDPOINTS.DOCUMENTS}?${queryString}`
                : config.ENDPOINTS.DOCUMENTS;

            const response = await api.get(endpoint);
            return response.data;
        } catch (error) {
            console.error("Failed to fetch documents:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Set document status (Section 2 - Admin/HR/Recruiter only)
     * Approved ("Active") triggers user ID generation.
     * @param {number} id - Document ID
     * @param {string} status - "Pending", "Active", "Blacklist"
     */
    setDocumentStatus: async (id, status) => {
        try {
            const response = await api.post(config.ENDPOINTS.DOCUMENT_SET_STATUS(id), {
                status
            });
            return response.data;
        } catch (error) {
            console.error("Failed to set document status:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Update an existing CV document (Section 2)
     */
    updateDocument: async (id, data) => {
        try {
            const isFormData = data instanceof FormData;
            const response = await api.patch(config.ENDPOINTS.DOCUMENT_DETAIL(id), data, {
                headers: isFormData ? { "Content-Type": "multipart/form-data" } : {},
            });
            return response.data;
        } catch (error) {
            console.error("Failed to update document:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Delete a CV document (Section 2)
     */
    deleteDocument: async (id) => {
        try {
            await api.delete(config.ENDPOINTS.DOCUMENT_DETAIL(id));
        } catch (error) {
            console.error("Failed to delete document:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Download CV Document file
     */
    downloadDocument: async (id) => {
        try {
            const response = await api.get(config.ENDPOINTS.DOCUMENT_DOWNLOAD(id), {
                responseType: 'blob'
            });
            return response.data;
        } catch (error) {
            console.error("Failed to download document:", error);
            throw new Error(handleApiError(error));
        }
    },


    // =========================================================================
    // SECTION 4: CV SUBMISSIONS (Recruitment Pipeline)
    // Endpoint: /cv-submissions/
    // =========================================================================

    /**
     * Get all CV Submissions (Section 4 Pipeline)
     */
    getSubmissions: async (filters = {}) => {
        try {
            const params = new URLSearchParams();
            if (filters.page) params.append("page", filters.page);
            if (filters.search) params.append("search", filters.search);
            if (filters.status) params.append("status", filters.status);
            if (filters.user) params.append("user", filters.user);
            if (filters.position) params.append("position", filters.position);
            if (filters.submitted_date_from) params.append("submitted_date_from", filters.submitted_date_from);
            if (filters.submitted_date_to) params.append("submitted_date_to", filters.submitted_date_to);

            const queryString = params.toString();
            const endpoint = queryString
                ? `${config.ENDPOINTS.CV_SUBMISSIONS}?${queryString}`
                : config.ENDPOINTS.CV_SUBMISSIONS;

            const response = await api.get(endpoint);
            return response.data;
        } catch (error) {
            console.error("Failed to fetch CV submissions:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Update CV Submission status (Section 4)
     * Move candidate through pipeline.
     */
    updateSubmissionStatus: async (id, status) => {
        try {
            const response = await api.patch(config.ENDPOINTS.CV_SUBMISSION_UPDATE_STATUS(id), {
                status
            });
            return response.data;
        } catch (error) {
            console.error(`Failed to update status for submission ${id}:`, error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Create a new CV submission (Section 4)
     */
    createSubmission: async (data) => {
        try {
            const isFormData = data instanceof FormData;
            const response = await api.post(config.ENDPOINTS.CV_SUBMISSIONS, data, {
                headers: isFormData ? { "Content-Type": "multipart/form-data" } : {},
            });
            return response.data;
        } catch (error) {
            console.error("Failed to create submission:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Update/PATCH a submission detail (Section 4)
     */
    updateSubmission: async (id, data) => {
        try {
            const isFormData = data instanceof FormData;
            const response = await api.patch(config.ENDPOINTS.CV_SUBMISSION_DETAIL(id), data, {
                headers: isFormData ? { "Content-Type": "multipart/form-data" } : {},
            });
            return response.data;
        } catch (error) {
            console.error("Failed to update submission:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Delete a CV submission (Section 4)
     */
    deleteSubmission: async (id) => {
        try {
            await api.delete(config.ENDPOINTS.CV_SUBMISSION_DETAIL(id));
        } catch (error) {
            console.error("Failed to delete submission:", error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Get a single CV Submission by ID (Section 4 — rich detail view)
     * Returns full payload including job_position_details, user_documents, certificates, coded_rank
     */
    getSubmissionById: async (id) => {
        try {
            const response = await api.get(config.ENDPOINTS.CV_SUBMISSION_DETAIL(id));
            return response.data;
        } catch (error) {
            console.error(`Failed to fetch submission ${id}:`, error);
            throw new Error(handleApiError(error));
        }
    },

    /**
     * Get submission statistics (Section 4 counts)
     */
    getCVSubmissionStats: async () => {
        try {
            const response = await api.get(config.ENDPOINTS.CV_SUBMISSION_STATS);
            return response.data;
        } catch (error) {
            console.error("Failed to fetch CV submission stats:", error);
            return {
                total: 0,
                pending: 0,
                under_review: 0,
                interviewed: 0,
                approved: 0,
                rejected: 0,
                hired: 0
            };
        }
    },
};