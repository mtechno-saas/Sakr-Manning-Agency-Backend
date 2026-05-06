// services/Dashboard/documentsApi.js - REFINED VERSION
import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";
import config from "../Auth/config.js";

/**
 * Documents/Contracts API Service
 * Handles all contract-related API calls for the dashboard
 *
 * API Endpoints from backend:
 * - GET/POST /api/contracts/
 * - GET/PUT/PATCH/DELETE /api/contracts/{id}/
 * - GET /api/contracts/stats/
 */

export const documentsApi = {
  /**
   * Get all contracts with optional filters
   * @param {Object} filters - { status, user, company, ship, rank, page, page_size }
   * @returns {Promise<Object>} { results: [], count, next, previous }
   */
  getContracts: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      const getVal = (v) => Array.isArray(v) ? v[0] : v;

      // Add filters to query params
      if (filters.status) params.append("status", getVal(filters.status));
      if (filters.user) params.append("user", getVal(filters.user));
      if (filters.company) params.append("company", getVal(filters.company));
      if (filters.ship) params.append("ship", getVal(filters.ship));
      if (filters.rank) params.append("rank", getVal(filters.rank));
      if (filters.search) params.append("search", getVal(filters.search));

      // Pagination params
      if (filters.page) params.append("page", filters.page);
      if (filters.page_size) params.append("page_size", filters.page_size);

      const queryString = params.toString();
      const endpoint = queryString
        ? `${config.ENDPOINTS.CONTRACTS}?${queryString}`
        : config.ENDPOINTS.CONTRACTS;

      const response = await api.get(endpoint);

      // Handle both paginated and non-paginated responses
      if (response.data.results) {
        return {
          contracts: response.data.results,
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
        };
      }

      // Non-paginated response
      return {
        contracts: Array.isArray(response.data) ? response.data : [],
        count: Array.isArray(response.data) ? response.data.length : 0,
      };
    } catch (error) {
      console.error("Failed to fetch contracts:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get contract by ID with full details
   * @param {number} contractId
   * @returns {Promise<Object>} Contract object with populated relationships
   */
  getContractById: async (contractId) => {
    try {
      const response = await api.get(config.ENDPOINTS.CONTRACT_DETAIL(contractId));
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch contract ${contractId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create new contract (Admin/HR only)
   * @param {Object} contractData - Contract data object
   * @returns {Promise<Object>} Created contract object
   *
   * Expected data format:
   * {
   *   user: number,          // User ID (required)
   *   ship: number,          // Ship ID (optional)
   *   company: number,       // Company ID (required)
   *   rank: number,          // Rank ID (required)
   *   sign_on_date: "YYYY-MM-DD",  // Required
   *   sign_off_date: "YYYY-MM-DD", // Required
   *   salary: "5500.00",     // Required
   *   currency: "USD",       // Default: USD
   *   status: "Pending Signature" | "Signed" | "Expired" | "Cancelled" | "Draft"
   * }
   */
  createContract: async (contractData) => {
    try {
      const response = await api.post(config.ENDPOINTS.CONTRACTS, contractData);
      return response.data;
    } catch (error) {
      console.error("Failed to create contract:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update contract (Admin/HR only)
   * @param {number} contractId
   * @param {Object} contractData - Partial contract data to update
   * @returns {Promise<Object>} Updated contract object
   */
  updateContract: async (contractId, contractData) => {
    try {
      const response = await api.patch(
        config.ENDPOINTS.CONTRACT_DETAIL(contractId),
        contractData
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to update contract ${contractId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete contract (Admin/HR only)
   * @param {number} contractId
   * @returns {Promise<void>}
   */
  deleteContract: async (contractId) => {
    try {
      await api.delete(config.ENDPOINTS.CONTRACT_DETAIL(contractId));
    } catch (error) {
      console.error(`Failed to delete contract ${contractId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Download contract document
   * @param {number} contractId 
   */
  downloadContract: async (contractId) => {
    try {
      const endpoint = `${config.ENDPOINTS.CONTRACT_DETAIL(contractId)}download/`;
      const response = await api.get(endpoint, { responseType: 'blob' });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Try to extract filename from headers, default if missing
      const contentDisposition = response.headers['content-disposition'];
      let filename = `contract_${contractId}.pdf`;
      if (contentDisposition && contentDisposition.indexOf('filename=') !== -1) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, '');
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      return { success: true };
    } catch (error) {
      console.error(`Failed to download contract ${contractId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get contract statistics from backend
   * @returns {Promise<Object>} Statistics object
   *
   * Returns:
   * {
   *   total_contracts: number,
   *   signed_contracts: number,
   *   pending_signature: number,
   *   expired_contracts: number,
   *   active_contracts: number,
   *   draft_contracts: number,
   *   cancelled_contracts: number
   * }
   */
  getContractStats: async () => {
    try {
      const response = await api.get(config.ENDPOINTS.CONTRACT_STATS);
      return response.data;
    } catch (error) {
      console.error("Failed to fetch contract stats:", error);
      // Return empty stats instead of throwing
      return {
        total_contracts: 0,
        signed_contracts: 0,
        pending_signature: 0,
        expired_contracts: 0,
        active_contracts: 0,
        draft_contracts: 0,
        cancelled_contracts: 0,
      };
    }
  },

  /**
   * Calculate days until contract expiry
   * @param {string} signOffDate - Sign-off date in YYYY-MM-DD format
   * @returns {number} Days remaining (negative if expired)
   */
  calculateDaysToExpiry: (signOffDate) => {
    if (!signOffDate) return null;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const expiryDate = new Date(signOffDate);
    expiryDate.setHours(0, 0, 0, 0);

    const diffTime = expiryDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    return diffDays;
  },

  /**
   * Get expiry status category
   * @param {number} daysToExpiry
   * @returns {string} "critical" | "warning" | "notice" | "active" | "expired"
   */
  getExpiryCategory: (daysToExpiry) => {
    if (daysToExpiry === null) return "unknown";
    if (daysToExpiry < 0) return "expired";
    if (daysToExpiry <= 7) return "critical";
    if (daysToExpiry <= 30) return "warning";
    if (daysToExpiry <= 60) return "notice";
    return "active";
  },

  /**
   * Calculate contract duration in months
   * @param {string} signOnDate
   * @param {string} signOffDate
   * @returns {number} Duration in months
   */
  calculateDuration: (signOnDate, signOffDate) => {
    if (!signOnDate || !signOffDate) return 0;

    const startDate = new Date(signOnDate);
    const endDate = new Date(signOffDate);

    const diffTime = Math.abs(endDate - startDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    const diffMonths = Math.round(diffDays / 30);

    return diffMonths;
  },

  /**
   * Get enriched contracts with calculated fields
   * @param {Object} filters
   * @returns {Promise<Object>}
   */
  getEnrichedContracts: async (filters = {}) => {
    try {
      const response = await documentsApi.getContracts(filters);

      // Enrich each contract with calculated fields
      const enrichedContracts = response.contracts.map((contract) => ({
        ...contract,
        daysToExpiry: documentsApi.calculateDaysToExpiry(
          contract.sign_off_date
        ),
        expiryCategory: documentsApi.getExpiryCategory(
          documentsApi.calculateDaysToExpiry(contract.sign_off_date)
        ),
        duration: documentsApi.calculateDuration(
          contract.sign_on_date,
          contract.sign_off_date
        ),
      }));

      return {
        ...response,
        contracts: enrichedContracts,
      };
    } catch (error) {
      console.error("Failed to fetch enriched contracts:", error);
      throw error;
    }
  },
};

export default documentsApi;
