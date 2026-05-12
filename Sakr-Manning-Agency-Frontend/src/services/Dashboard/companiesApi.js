/*
- getCompanies() - List companies
- getCompanyById(id) - Get company details
- createCompany(data) - Create company (Admin only)
- updateCompany(id, data) - Update company (Admin only)
- deleteCompany(id) - Delete company (Admin only)
- getCompanyStats() - Get statistics
*/

// services/Dashboard/api/companiesApi.js
import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";

/**
 * Companies API Service
 * Handles all company-related API calls for the dashboard
 */
export const companiesApi = {
  /**
   * Get all companies with optional filters
   * @param {Object} filters - { status, company_type, page, page_size }
   * @returns {Promise<Object>} { results: [], count, next, previous }
   */
  getCompanies: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      // Add filters to query params — aligned with BE docs
      const getVal = (v) => (Array.isArray(v) ? v[0] : v);

      if (filters.name) params.append("name", getVal(filters.name));
      if (filters.company_type) params.append("company_type", getVal(filters.company_type));
      if (filters.status) params.append("status", getVal(filters.status));

      // Fallback for older search key
      if (filters.search && !filters.name) params.append("name", getVal(filters.search));

      // Standard pagination params
      if (filters.page) params.append("page", filters.page);
      if (filters.page_size) params.append("page_size", filters.page_size);

      const queryString = params.toString();
      const endpoint = queryString
        ? `/companies/?${queryString}`
        : "/companies/";

      const response = await api.get(endpoint);

      // Handle both paginated and non-paginated responses
      if (response.data.results) {
        return {
          companies: response.data.results,
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
        };
      }

      // Non-paginated response
      return {
        companies: Array.isArray(response.data) ? response.data : [],
        count: Array.isArray(response.data) ? response.data.length : 0,
      };
    } catch (error) {
      console.error("Failed to fetch companies:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get company by ID with full details
   * @param {number} companyId
   * @returns {Promise<Object>} Company object
   */
  getCompanyById: async (companyId) => {
    try {
      const response = await api.get(`/companies/${companyId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch company ${companyId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create new company (Admin only)
   * @param {Object} companyData - Company data object
   * @returns {Promise<Object>} Created company object
   */
  createCompany: async (companyData) => {
    try {
      const response = await api.post("/companies/", companyData);
      return response.data;
    } catch (error) {
      console.error("Failed to create company:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update company (Admin only)
   * @param {number} companyId
   * @param {Object} companyData - Partial company data to update
   * @returns {Promise<Object>} Updated company object
   */
  updateCompany: async (companyId, companyData) => {
    try {
      const response = await api.put(`/companies/${companyId}/`, companyData);
      return response.data;
    } catch (error) {
      console.error(`Failed to update company ${companyId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete company (Admin only)
   * @param {number} companyId
   * @returns {Promise<void>}
   */
  deleteCompany: async (companyId) => {
    try {
      await api.delete(`/companies/${companyId}/`);
    } catch (error) {
      console.error(`Failed to delete company ${companyId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Batch fetch companies by IDs (fixes N+1 query problem)
   * @param {Array<number>} ids - Array of company IDs
   * @returns {Promise<Object>} Map of { id: companyData }
   */
  getCompaniesByIds: async (ids = []) => {
    try {
      if (!ids.length) return {};

      // Deduplicate and filter nulls
      const uniqueIds = [...new Set(ids.filter(Boolean))];

      // Fetch all at once (backend may support ?id__in=1,2,3 or we fetch individually in parallel)
      // For now, use parallel fetch with Promise.all
      const results = await Promise.all(
        uniqueIds.map(async (id) => {
          try {
            const response = await api.get(`/companies/${id}/`);
            return { id, data: response.data };
          } catch {
            return { id, data: null };
          }
        })
      );

      // Convert to map
      const companyMap = {};
      results.forEach(({ id, data }) => {
        if (data) {
          companyMap[id] = data;
        }
      });

      return companyMap;
    } catch (error) {
      console.error("Failed to batch fetch companies:", error);
      return {};
    }
  },

  /**
   * Search companies for TypeaheadInput
   * @param {Object} params - { search, limit }
   * @returns {Promise<Array>} Array of { value, label, ...companyData }
   */
  searchCompanies: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams();

      if (params.search) queryParams.append("search", params.search);
      queryParams.append("page_size", params.limit || 20);

      const endpoint = `/companies/?${queryParams.toString()}`;
      const response = await api.get(endpoint);

      const companies = response.data.results || response.data || [];

      return companies.map(company => ({
        value: company.id,
        label: company.company_name || company.name,
        id: company.id,
        company_name: company.company_name,
        company_type: company.company_type,
      }));
    } catch (error) {
      console.error("Failed to search companies:", error);
      return [];
    }
  },

  /**
   * Get company statistics
   * Response shape (updated backend):
   * {
   *   total_companies, by_status: { Active, Inactive, Prospect },
   *   by_type: { ... }, open_positions: { total, companies_with_openings },
   *   recent_companies: [...]
   * }
   * @returns {Promise<Object>} Statistics object
   */
  getCompanyStats: async () => {
    try {
      const response = await api.get("/companies/stats/");
      const data = response.data || {};

      // Normalize to a flat shape for easy consumption
      return {
        total_companies: data.total_companies || 0,
        active_companies: data.by_status?.Active || 0,
        inactive_companies: data.by_status?.Inactive || 0,
        prospect_companies: data.by_status?.Prospect || 0,
        by_status: data.by_status || {},
        by_type: data.by_type || {},
        total_open_positions: data.open_positions?.total || 0,
        companies_with_openings: data.open_positions?.companies_with_openings || 0,
        recent_companies: data.recent_companies || [],
      };
    } catch (error) {
      console.error("Failed to fetch company stats:", error);
      return {
        total_companies: 0,
        active_companies: 0,
        inactive_companies: 0,
        prospect_companies: 0,
        by_status: {},
        by_type: {},
        total_open_positions: 0,
        companies_with_openings: 0,
        recent_companies: [],
      };
    }
  },
};

export default companiesApi;
