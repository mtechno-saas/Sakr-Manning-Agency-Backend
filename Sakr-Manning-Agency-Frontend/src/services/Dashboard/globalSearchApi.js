// services/Dashboard/globalSearchApi.js
// Calls the backend /api/global-search/?q=<term> endpoint

import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";

/**
 * Global Search API Service
 * Searches across all platform sections in a single backend call.
 * Backend endpoint: GET /api/global-search/?q=<term>
 * Minimum query length: 2 characters
 */
export const globalSearchApi = {
  /**
   * Search across all sections
   * @param {string} query  - Search term (min 2 chars)
   * @returns {Promise<Object>} Grouped results: { users, ships, companies, cv_submissions, contracts, ... }
   */
  search: async (query = "") => {
    try {
      if (!query || query.trim().length < 2) {
        return { users: [], ships: [], companies: [], cv_submissions: [], contracts: [] };
      }

      const response = await api.get("/global-search/", {
        params: { q: query.trim() },
      });

      return response.data || {};
    } catch (error) {
      console.error("Global search failed:", error);
      throw new Error(handleApiError(error));
    }
  },
};

export default globalSearchApi;
