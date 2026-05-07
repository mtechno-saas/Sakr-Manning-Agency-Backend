/*
- getFinanceRecords() - List records
- createFinanceRecord(data) - Create record
- updateFinanceRecord(id, data) - Update record
- deleteFinanceRecord(id) - Delete record
- calculateFinance(data) - Preview calculation
- getFinanceStats() - Statistics
- exportFinanceRecords() - Export data
*/

// services/Dashboard/financeApi.js
import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";

/**
 * Finance API Service
 * Handles all finance-related API calls for the dashboard
 */

export const financeApi = {
  /**
   * Get all finance records with optional filters
   * @param {Object} filters - { search, user, company, start_date, end_date, page, page_size }
   * @returns {Promise<Object>} { results: [], count, next, previous }
   */
  getFinanceRecords: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      const getVal = (v) => (Array.isArray(v) ? v[0] : v);

      // Add filters to query params — aligned with BE docs
      if (filters.user) params.append("user", getVal(filters.user));
      if (filters.company) params.append("company", getVal(filters.company));
      if (filters.status) params.append("status", getVal(filters.status));
      if (filters.record_type) params.append("record_type", getVal(filters.record_type));
      if (filters.start_date_from) params.append("start_date_from", getVal(filters.start_date_from));
      if (filters.start_date_to) params.append("start_date_to", getVal(filters.start_date_to));
      
      // Fallback for older keys if still in UI
      if (filters.start_date && !filters.start_date_from) params.append("start_date_from", getVal(filters.start_date));
      if (filters.end_date && !filters.start_date_to) params.append("start_date_to", getVal(filters.end_date));

      if (filters.page) params.append("page", filters.page);
      if (filters.page_size) params.append("page_size", filters.page_size);

      const queryString = params.toString();
      const endpoint = queryString
        ? `/finance/finance-records/?${queryString}`
        : "/finance/finance-records/";

      const response = await api.get(endpoint);

      // Handle both paginated and non-paginated responses
      if (response.data.results) {
        return {
          records: response.data.results,
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
        };
      }

      // Non-paginated response
      return {
        records: Array.isArray(response.data) ? response.data : [],
        count: Array.isArray(response.data) ? response.data.length : 0,
      };
    } catch (error) {
      console.error("Failed to fetch finance records:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get finance record by ID
   * @param {number} recordId
   * @returns {Promise<Object>} Finance record object
   */
  getFinanceRecordById: async (recordId) => {
    try {
      const response = await api.get(`/finance/finance-records/${recordId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch finance record ${recordId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create new finance record
   * @param {Object} recordData - Finance record data
   * @returns {Promise<Object>} Created record object
   */
  createFinanceRecord: async (recordData) => {
    try {
      const response = await api.post("/finance/finance-records/", recordData);
      return response.data;
    } catch (error) {
      console.error("Failed to create finance record:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update existing finance record
   * @param {number} recordId
   * @param {Object} recordData - Partial record data to update
   * @returns {Promise<Object>} Updated record object
   */
  updateFinanceRecord: async (recordId, recordData) => {
    try {
      const response = await api.patch(
        `/finance/finance-records/${recordId}/`,
        recordData
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to update finance record ${recordId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete finance record
   * @param {number} recordId
   * @returns {Promise<void>}
   */
  deleteFinanceRecord: async (recordId) => {
    try {
      await api.delete(`/finance/finance-records/${recordId}/`);
    } catch (error) {
      console.error(`Failed to delete finance record ${recordId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Calculate finance (client-side preview, server-side confirmation)
   * @param {Object} data - { user, company, start_date, end_date }
   * @returns {Promise<Object>} { total_days, daily_rate, total_money }
   */
  calculateFinance: async (data) => {
    try {
      const response = await api.post(
        "/finance/finance-records/calculate/",
        data
      );
      return response.data;
    } catch (error) {
      console.error("Failed to calculate finance:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get finance statistics
   * @returns {Promise<Object>} Statistics object
   */
  getFinanceStats: async () => {
    try {
      const response = await api.get("/finance/finance-records/status/");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch finance stats:", error);
      // Return empty stats instead of throwing
      return {
        total_records: 0,
        total_money: "0.00",
        average_daily_rate: "0.00",
        this_month_total: "0.00",
      };
    }
  },

  /**
   * Export finance records to CSV (optional)
   * @param {Object} filters - Same filters as getFinanceRecords
   * @returns {Promise<Blob>} CSV file blob
   */
  exportFinanceRecords: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      if (filters.user) params.append("user", filters.user);
      if (filters.company) params.append("company", filters.company);
      if (filters.start_date) params.append("start_date", filters.start_date);
      if (filters.end_date) params.append("end_date", filters.end_date);

      const queryString = params.toString();
      const endpoint = queryString
        ? `/finance/finance-records/export/?${queryString}`
        : "/finance/finance-records/export/";

      const response = await api.get(endpoint, {
        responseType: "blob",
      });

      return response.data;
    } catch (error) {
      console.error("Failed to export finance records:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Client-side calculation helper (for preview before API call)
   * @param {string} startDate - YYYY-MM-DD
   * @param {string} endDate - YYYY-MM-DD
   * @param {number} dailyRate - Daily rate amount
   * @returns {Object} { totalDays, totalMoney }
   */
  calculateClientSide: (startDate, endDate, dailyRate = 150) => {
    if (!startDate || !endDate) {
      return { totalDays: 0, totalMoney: 0 };
    }

    const start = new Date(startDate);
    const end = new Date(endDate);

    // Calculate days difference (inclusive)
    const diffTime = Math.abs(end - start);
    const totalDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    const totalMoney = totalDays * dailyRate;

    return {
      totalDays,
      totalMoney: totalMoney.toFixed(2),
    };
  },
};

export default financeApi;
