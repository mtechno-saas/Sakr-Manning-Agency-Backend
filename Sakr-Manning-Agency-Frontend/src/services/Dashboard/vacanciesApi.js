/*
- getVacancies(filters)       - List all vacancies
- getVacancyById(id)          - Get vacancy details
- createVacancy(data)         - Create vacancy (Admin only)
- updateVacancy(id, data)     - Update vacancy (Admin only)
- deleteVacancy(id)           - Delete vacancy (Admin only)
- getVacancyStats()           - Get statistics
*/

// services/Dashboard/vacanciesApi.js
import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";

/**
 * Vacancies API Service
 * Handles all vacancy-related API calls for the dashboard.
 *
 * Endpoints:
 *   GET    /companies/vacancies/         → list
 *   POST   /companies/vacancies/         → create  (Admin only)
 *   GET    /companies/vacancies/{id}/    → retrieve
 *   PATCH  /companies/vacancies/{id}/    → update   (Admin only)
 *   DELETE /companies/vacancies/{id}/    → destroy  (Admin only)
 */
export const vacanciesApi = {
  /**
   * Get all vacancies with optional filters
   * @param {Object} filters - { status, company, rank, search, page, page_size }
   * @returns {Promise<Object>} { vacancies: [], count, next, previous }
   */
  getVacancies: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      if (filters.status)    params.append("status",    filters.status);
      if (filters.company)   params.append("company",   filters.company);
      if (filters.rank)      params.append("rank",      filters.rank);
      if (filters.search)    params.append("search",    filters.search);
      if (filters.page)      params.append("page",      filters.page);
      if (filters.page_size) params.append("page_size", filters.page_size);

      const queryString = params.toString();
      const endpoint = queryString
        ? `/companies/vacancies/?${queryString}`
        : "/companies/vacancies/";

      const response = await api.get(endpoint);

      // Handle paginated response
      if (response.data.results) {
        return {
          vacancies: response.data.results,
          count:     response.data.count,
          next:      response.data.next,
          previous:  response.data.previous,
        };
      }

      // Non-paginated fallback
      return {
        vacancies: Array.isArray(response.data) ? response.data : [],
        count:     Array.isArray(response.data) ? response.data.length : 0,
      };
    } catch (error) {
      console.error("Failed to fetch vacancies:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get a single vacancy by ID
   * @param {number} vacancyId
   * @returns {Promise<Object>} Vacancy object
   */
  getVacancyById: async (vacancyId) => {
    try {
      const response = await api.get(`/companies/vacancies/${vacancyId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch vacancy ${vacancyId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create a new vacancy (Admin only)
   * @param {Object} vacancyData - Vacancy fields
   * @returns {Promise<Object>} Created vacancy object
   */
  createVacancy: async (vacancyData) => {
    try {
      const response = await api.post("/companies/vacancies/", vacancyData);
      return response.data;
    } catch (error) {
      console.error("Failed to create vacancy:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update a vacancy (Admin only) — uses PATCH for partial updates
   * @param {number} vacancyId
   * @param {Object} vacancyData - Partial fields to update
   * @returns {Promise<Object>} Updated vacancy object
   */
  updateVacancy: async (vacancyId, vacancyData) => {
    try {
      const response = await api.patch(
        `/companies/vacancies/${vacancyId}/`,
        vacancyData
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to update vacancy ${vacancyId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete a vacancy (Admin only)
   * @param {number} vacancyId
   * @returns {Promise<void>}
   */
  deleteVacancy: async (vacancyId) => {
    try {
      await api.delete(`/companies/vacancies/${vacancyId}/`);
    } catch (error) {
      console.error(`Failed to delete vacancy ${vacancyId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get vacancy statistics
   * @returns {Promise<Object>} Stats object
   */
  getVacancyStats: async () => {
    try {
      const response = await api.get("/companies/vacancies/stats/");
      const data = response.data || {};

      return {
        total_vacancies:  data.total_vacancies  || 0,
        open_vacancies:   data.open_vacancies   || data.by_status?.Open   || 0,
        closed_vacancies: data.closed_vacancies || data.by_status?.Closed || 0,
        by_status:        data.by_status        || {},
        by_company:       data.by_company       || {},
        recent_vacancies: data.recent_vacancies || [],
      };
    } catch (error) {
      console.error("Failed to fetch vacancy stats:", error);
      // Return safe defaults so callers never crash
      return {
        total_vacancies:  0,
        open_vacancies:   0,
        closed_vacancies: 0,
        by_status:        {},
        by_company:       {},
        recent_vacancies: [],
      };
    }
  },

  /**
   * Search vacancies (for typeahead / autocomplete inputs)
   * @param {Object} params - { search, limit }
   * @returns {Promise<Array>} Array of { value, label, ...vacancyData }
   */
  searchVacancies: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams();
      if (params.search) queryParams.append("search", params.search);
      queryParams.append("page_size", params.limit || 20);

      const endpoint = `/companies/vacancies/?${queryParams.toString()}`;
      const response = await api.get(endpoint);

      const vacancies = response.data.results || response.data || [];

      return vacancies.map((vacancy) => ({
        value:   vacancy.id,
        label:   vacancy.title || vacancy.position || `Vacancy #${vacancy.id}`,
        id:      vacancy.id,
        company: vacancy.company,
        status:  vacancy.status,
      }));
    } catch (error) {
      console.error("Failed to search vacancies:", error);
      return [];
    }
  },
};

export default vacanciesApi;
