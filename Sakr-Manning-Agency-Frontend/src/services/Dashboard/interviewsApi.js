/*
- getInterviews() - List interviews
- getInterviewById(id) - Get interview details
- createInterview(data) - Schedule interview
- updateInterview(id, data) - Update interview
- deleteInterview(id) - Cancel interview
- getInterviewStats() - Statistics
- getInterviewCalendar(month, year) - Calendar view
*/

// services/Dashboard/interviewsApi.js
import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";

/**
 * Interviews API Service
 * Handles all interview-related API calls for the dashboard
 */
export const interviewsApi = {
  /**
   * Get all interviews with optional filters
   * @param {Object} filters - { search, status, date, company, position, page, page_size }
   * @returns {Promise<Object>} { results: [], count, next, previous }
   */
  getInterviews: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      const getVal = (v) => (Array.isArray(v) ? v[0] : v);

      // Add filters to query params — aligned with BE docs
      if (filters.candidate) params.append("candidate", getVal(filters.candidate));
      if (filters.company) params.append("company", getVal(filters.company));
      if (filters.status) params.append("status", getVal(filters.status));
      if (filters.scheduled_date) params.append("scheduled_date", getVal(filters.scheduled_date));
      if (filters.scheduled_date_from) params.append("scheduled_date_from", getVal(filters.scheduled_date_from));
      if (filters.scheduled_date_to) params.append("scheduled_date_to", getVal(filters.scheduled_date_to));
      
      // Fallback for older search/date keys if used
      if (filters.search && !filters.candidate) params.append("candidate", getVal(filters.search));
      if (filters.date && !filters.scheduled_date) params.append("scheduled_date", getVal(filters.date));

      if (filters.page) params.append("page", filters.page);
      if (filters.page_size) params.append("page_size", filters.page_size);

      const queryString = params.toString();
      const endpoint = queryString
        ? `/users/interviews/?${queryString}`
        : "/users/interviews/";

      const response = await api.get(endpoint);

      // Handle both paginated and non-paginated responses
      if (response.data.results) {
        return {
          interviews: response.data.results,
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
        };
      }

      // Non-paginated response
      return {
        interviews: Array.isArray(response.data) ? response.data : [],
        count: Array.isArray(response.data) ? response.data.length : 0,
      };
    } catch (error) {
      console.error("Failed to fetch interviews:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get interview by ID with full details
   * @param {number} interviewId
   * @returns {Promise<Object>} Interview object
   */
  getInterviewById: async (interviewId) => {
    try {
      const response = await api.get(`/users/interviews/${interviewId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch interview ${interviewId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create new interview
   * @param {Object} interviewData - Interview data object
   * @returns {Promise<Object>} Created interview object
   */
  createInterview: async (interviewData) => {
    try {
      const response = await api.post("/users/interviews/", interviewData);
      return response.data;
    } catch (error) {
      console.error("Failed to create interview:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update interview
   * @param {number} interviewId
   * @param {Object} interviewData - Partial interview data to update
   * @returns {Promise<Object>} Updated interview object
   */
  updateInterview: async (interviewId, interviewData) => {
    try {
      const response = await api.patch(
        `/users/interviews/${interviewId}/`,
        interviewData
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to update interview ${interviewId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete interview
   * @param {number} interviewId
   * @returns {Promise<void>}
   */
  deleteInterview: async (interviewId) => {
    try {
      await api.delete(`/users/interviews/${interviewId}/`);
    } catch (error) {
      console.error(`Failed to delete interview ${interviewId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get interview statistics
   * @returns {Promise<Object>} Statistics object
   */
  getInterviewStats: async () => {
    try {
      const response = await api.get("/users/interviews/status/");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch interview stats:", error);
      // Return empty stats instead of throwing
      return {
        total_interviews: 0,
        scheduled: 0,
        completed: 0,
        cancelled: 0,
        today: 0,
        this_week: 0,
        pending: 0,
      };
    }
  },

  /**
   * Get calendar view of interviews
   * @param {Object} params - { month, year }
   * @returns {Promise<Array>} Array of interviews grouped by date
   */
  getInterviewCalendar: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.month) queryParams.append("month", params.month);
      if (params.year) queryParams.append("year", params.year);

      const queryString = queryParams.toString();
      const endpoint = queryString
        ? `/users/interviews/calendar/?${queryString}`
        : "/users/interviews/calendar/";

      const response = await api.get(endpoint);
      return response.data;
    } catch (error) {
      console.error("Failed to fetch interview calendar:", error);
      // Return empty array instead of throwing
      return [];
    }
  },
};

export default interviewsApi;
