// services/Dashboard/jobOrdersApi.js
// CRUD operations for Job Orders at /api/companies/job-orders/

import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";

/**
 * Job Orders API Service
 * Endpoint: /api/companies/job-orders/
 * Auth: IsAuthenticated
 */
export const jobOrdersApi = {
  /**
   * Get all job orders with optional filters
   * @param {Object} filters - { company, ship, status, page, page_size }
   */
  getJobOrders: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      if (filters.company) params.append("company", filters.company);
      if (filters.ship) params.append("ship", filters.ship);
      if (filters.status) params.append("status", filters.status);
      if (filters.search) params.append("search", filters.search);
      if (filters.page) params.append("page", filters.page);
      if (filters.page_size) params.append("page_size", filters.page_size);

      const qs = params.toString();
      const endpoint = qs
        ? `/companies/job-orders/?${qs}`
        : "/companies/job-orders/";

      const response = await api.get(endpoint);

      if (response.data.results) {
        return {
          jobOrders: response.data.results,
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
        };
      }

      return {
        jobOrders: Array.isArray(response.data) ? response.data : [],
        count: Array.isArray(response.data) ? response.data.length : 0,
      };
    } catch (error) {
      console.error("Failed to fetch job orders:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get a single job order by ID (includes nested positions)
   * @param {number} id
   */
  getJobOrderById: async (id) => {
    try {
      const response = await api.get(`/companies/job-orders/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch job order ${id}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create a job order
   * Required: company, ship, reference_number, request_date, target_joining_date, status
   * @param {Object} data
   */
  createJobOrder: async (data) => {
    try {
      const response = await api.post("/companies/job-orders/", data);
      return response.data;
    } catch (error) {
      console.error("Failed to create job order:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update a job order (PATCH)
   * @param {number} id
   * @param {Object} data - Partial fields to update
   */
  updateJobOrder: async (id, data) => {
    try {
      const response = await api.patch(`/companies/job-orders/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error(`Failed to update job order ${id}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete a job order
   * @param {number} id
   */
  deleteJobOrder: async (id) => {
    try {
      await api.delete(`/companies/job-orders/${id}/`);
    } catch (error) {
      console.error(`Failed to delete job order ${id}:`, error);
      throw new Error(handleApiError(error));
    }
  },
};

export default jobOrdersApi;
