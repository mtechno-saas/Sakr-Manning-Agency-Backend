// services/Form/documentService.js
// CRUD operations for Personal Documents (separate endpoint)
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";

/**
 * Personal Documents CRUD operations
 * Endpoint: /api/users/personal-documents/
 */
export const documentService = {
    /**
     * Get all documents for a user
     * GET /api/users/personal-documents/?user={userId}
     */
    getDocuments: async (userId) => {
        try {
            const response = await api.get(`/users/personal-documents/`, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data.results || response.data || [],
            };
        } catch (error) {
            console.error("Failed to load documents:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: [],
            };
        }
    },

    /**
     * Create a new document record
     * POST /api/users/personal-documents/
     */
    createDocument: async (userId, data) => {
        try {
            const formData = new FormData();
            formData.append("user", userId);

            // Map frontend fields to backend fields
            if (data.document_type || data.type) formData.append("document_type", data.document_type || data.type);
            if (data.document_number || data.number) formData.append("document_number", data.document_number || data.number);
            if (data.issue_date) formData.append("issue_date", data.issue_date);
            if (data.expiry_date) formData.append("expiry_date", data.expiry_date);
            if (data.issuing_country) formData.append("issuing_country", data.issuing_country);
            if (data.issued_by) formData.append("issued_by", data.issued_by);
            if (data.place_of_issue) formData.append("place_of_issue", data.place_of_issue);

            // Handle file upload
            if (data.file instanceof File) {
                formData.append("file", data.file);
                formData.append("document_file", data.file);
            } else if (data.document_file instanceof File) {
                formData.append("file", data.document_file);
                formData.append("document_file", data.document_file);
            }

            const response = await api.post(`/users/personal-documents/`, formData, {
                params: { user: userId },
                headers: { "Content-Type": "multipart/form-data" },
            });
            return {
                success: true,
                data: response.data,
                message: "Document created successfully",
            };
        } catch (error) {
            console.error("Failed to create document:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create document",
            };
        }
    },

    /**
     * Update a document record
     * PATCH /api/users/personal-documents/{id}/?user={userId}
     */
    updateDocument: async (id, data, userId) => {
        try {
            const formData = new FormData();

            // Ensure user ID is present
            formData.append("user", userId);

            if (data.document_type || data.type) formData.append("document_type", data.document_type || data.type);
            if (data.document_number || data.number) formData.append("document_number", data.document_number || data.number);
            if (data.issue_date) formData.append("issue_date", data.issue_date);
            if (data.expiry_date) formData.append("expiry_date", data.expiry_date);
            if (data.issuing_country) formData.append("issuing_country", data.issuing_country);
            if (data.issued_by) formData.append("issued_by", data.issued_by);
            if (data.place_of_issue) formData.append("place_of_issue", data.place_of_issue);

            // Handle file upload
            if (data.file instanceof File) {
                formData.append("file", data.file);
                formData.append("document_file", data.file);
            } else if (data.document_file instanceof File) {
                formData.append("file", data.document_file);
                formData.append("document_file", data.document_file);
            }

            const response = await api.patch(`/users/personal-documents/${id}/`, formData, {
                params: { user: userId },
                headers: { "Content-Type": "multipart/form-data" },
            });
            return {
                success: true,
                data: response.data,
                message: "Document updated successfully",
            };
        } catch (error) {
            console.error("Failed to update document:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update document",
            };
        }
    },

    /**
     * Delete a document record
     * DELETE /api/users/personal-documents/{id}/?user={userId}
     */
    deleteDocument: async (id, userId) => {
        try {
            await api.delete(`/users/personal-documents/${id}/`, {
                params: { user: userId },
            });
            return {
                success: true,
                message: "Document deleted successfully",
            };
        } catch (error) {
            console.error("Failed to delete document:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to delete document",
            };
        }
    },
};

export default documentService;
