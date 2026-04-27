// services/Form/courseService.js
// CRUD operations for Courses (separate endpoint)
import api from "../Auth/api";
import { handleApiError } from "../Auth/handlers";

/**
 * Course CRUD operations
 * Endpoint: /api/courses/
 */
export const courseService = {
    /**
     * Get all courses for a user
     * GET /api/courses/?user={userId}
     */
    getCourses: async (userId) => {
        try {
            const response = await api.get(`/courses/`, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data.results || response.data || [],
            };
        } catch (error) {
            console.error("Failed to load courses:", error);
            return {
                success: false,
                error: handleApiError(error),
                data: [],
            };
        }
    },

    /**
     * Create a new course record
     * POST /api/courses/
     */
    createCourse: async (userId, data) => {
        try {
            const payload = {
                user: userId,
                course_name: data.course_name,
                course_number: data.course_number,
                issue_date: data.issue_date,
                expiry_date: data.expiry_date,
                issued_by: data.issued_by,
                issued_at: data.issued_at,
                country_of_issue: data.country_of_issue,
                document: data.document,
            };

            // Handle file upload if document is a File object
            // Modals pass the file as data.file, so check both keys
            const fileToUpload = data.document instanceof File ? data.document : (data.file instanceof File ? data.file : null);
            if (fileToUpload) {
                const formData = new FormData();
                payload.document = fileToUpload; // ensure it's in the payload for FormData
                Object.keys(payload).forEach((key) => {
                    if (payload[key] !== undefined && payload[key] !== null) {
                        formData.append(key, payload[key]);
                    }
                });

                const response = await api.post(`/courses/`, formData, {
                    params: { user: userId },
                    headers: { "Content-Type": "multipart/form-data" },
                });
                return {
                    success: true,
                    data: response.data,
                    message: "Course record created successfully",
                };
            }

            const response = await api.post(`/courses/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Course record created successfully",
            };
        } catch (error) {
            console.error("Failed to create course:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to create course record",
            };
        }
    },

    /**
     * Update a course record
     * PATCH /api/courses/{id}/?user={userId}
     */
    updateCourse: async (id, data, userId) => {
        try {
            const payload = {
                user: userId || data.user, // Ensure user ID is sent
                course_name: data.course_name,
                course_number: data.course_number,
                issue_date: data.issue_date,
                expiry_date: data.expiry_date,
                issued_by: data.issued_by,
                issued_at: data.issued_at,
                country_of_issue: data.country_of_issue,
            };

            // Remove undefined values
            Object.keys(payload).forEach((key) => {
                if (payload[key] === undefined) {
                    delete payload[key];
                }
            });

            // Handle file upload if document is a File object
            // Modals pass the file as data.file, so check both keys
            const fileToUpload = data.document instanceof File ? data.document : (data.file instanceof File ? data.file : null);
            if (fileToUpload) {
                const formData = new FormData();
                Object.keys(payload).forEach((key) => {
                    if (payload[key] !== undefined && payload[key] !== null) {
                        formData.append(key, payload[key]);
                    }
                });
                formData.append("document", fileToUpload);

                const response = await api.patch(`/courses/${id}/`, formData, {
                    params: { user: userId },
                    headers: { "Content-Type": "multipart/form-data" },
                });
                return {
                    success: true,
                    data: response.data,
                    message: "Course record updated successfully",
                };
            }

            const response = await api.patch(`/courses/${id}/`, payload, {
                params: { user: userId },
            });
            return {
                success: true,
                data: response.data,
                message: "Course record updated successfully",
            };
        } catch (error) {
            console.error("Failed to update course:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to update course record",
            };
        }
    },

    /**
     * Delete a course record
     * DELETE /api/courses/{id}/?user={userId}
     */
    deleteCourse: async (id, userId) => {
        try {
            await api.delete(`/courses/${id}/`, {
                params: { user: userId },
            });
            return {
                success: true,
                message: "Course record deleted successfully",
            };
        } catch (error) {
            console.error("Failed to delete course:", error);
            return {
                success: false,
                error: handleApiError(error),
                message: "Failed to delete course record",
            };
        }
    },

    /**
     * Map frontend course data to backend format
     */
    mapToBackend: (data) => ({
        course_name: data.course_name,
        course_number: data.course_number,
        issue_date: data.issue_date,
        expiry_date: data.expiry_date,
        issued_by: data.issued_by,
        issued_at: data.issued_at,
        country_of_issue: data.country_of_issue,
        document: data.document,
    }),

    /**
     * Map backend course data to frontend format (snake_case preserved)
     */
    mapToFrontend: (data) => ({
        id: data.id,
        user: data.user,
        course_name: data.course_name,
        course_number: data.course_number,
        issue_date: data.issue_date,
        expiry_date: data.expiry_date,
        issued_by: data.issued_by,
        issued_at: data.issued_at,
        country_of_issue: data.country_of_issue,
        document: data.document,
    }),
};

export default courseService;