// src/services/Dashboard/jobOrdersApi.js
import api from "../Auth/api";

/**
 * Job Orders API Service
 * Replaces the previous Vacancies API
 */
export const jobOrdersApi = {
    // ─── JOB ORDERS (HEADERS) ───────────────────────────────────────────────

    /**
     * Get list of job orders with filters
     */
    getJobOrders: async (params = {}) => {
        const response = await api.get("/companies/job-orders/", { params });
        return response.data;
    },

    /**
     * Get single job order detail (includes nested positions)
     */
    getJobOrderById: async (id) => {
        const response = await api.get(`/companies/job-orders/${id}/`);
        return response.data;
    },

    /**
     * Create a new job order
     */
    createJobOrder: async (data) => {
        const response = await api.post("/companies/job-orders/", data);
        return response.data;
    },

    /**
     * Update an existing job order
     */
    updateJobOrder: async (id, data) => {
        const response = await api.patch(`/companies/job-orders/${id}/`, data);
        return response.data;
    },

    /**
     * Delete a job order
     */
    deleteJobOrder: async (id) => {
        await api.delete(`/companies/job-orders/${id}/`);
        return true;
    },

    // ─── JOB ORDER POSITIONS ────────────────────────────────────────────────

    /**
     * Get list of all positions (optionally filtered by job_order)
     */
    getJobPositions: async (params = {}) => {
        const response = await api.get("/companies/job-positions/", { params });
        return response.data;
    },

    /**
     * Add a position to a job order
     */
    createJobPosition: async (data) => {
        const response = await api.post("/companies/job-positions/", data);
        return response.data;
    },

    /**
     * Update a job position
     */
    updateJobPosition: async (id, data) => {
        const response = await api.patch(`/companies/job-positions/${id}/`, data);
        return response.data;
    },

    /**
     * Delete a job position
     */
    deleteJobPosition: async (id) => {
        await api.delete(`/companies/job-positions/${id}/`);
        return true;
    }
};

export default jobOrdersApi;
