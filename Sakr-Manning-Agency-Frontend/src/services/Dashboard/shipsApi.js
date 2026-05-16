/*
- getShips() - List ships
- getShipById(id) - Get ship details
- createShip(data) - Create ship (Admin only)
- updateShip(id, data) - Update ship (Admin only)
- deleteShip(id) - Delete ship (Admin only)
- assignUserToShip(shipId, userId) - Assign crew
- unassignUserFromShip(shipId, userId) - Remove crew
*/

// services/Dashboard/api/shipsApi.js
import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";

/**
 * Ships API Service
 * Handles all ship-related API calls for the dashboard
 */

export const shipsApi = {
  /**
   * Get all ships with optional filters
   * @param {Object} filters - { status, ship_type, flag, company, page, page_size }
   * @returns {Promise<Object>} { results: [], count, next, previous }
   */
  getShips: async (filters = {}) => {
    try {
      const params = new URLSearchParams();

      const getVal = (v) => (Array.isArray(v) ? v[0] : v);

      // Add filters to query params — aligned with BE docs
      if (filters.name) params.append("name", getVal(filters.name));
      if (filters.imo_number) params.append("imo_number", getVal(filters.imo_number));
      if (filters.company) params.append("company", getVal(filters.company));
      if (filters.status) params.append("status", getVal(filters.status));
      if (filters.flag) params.append("flag", getVal(filters.flag));
      if (filters.ship_type) params.append("ship_type", getVal(filters.ship_type));
      if (filters.vessel_type) params.append("ship_type", getVal(filters.vessel_type));

      // Fallback for older search key
      if (filters.search && !filters.name) params.append("name", getVal(filters.search));

      if (filters.page) params.append("page", filters.page);
      if (filters.page_size) params.append("page_size", filters.page_size);

      const queryString = params.toString();
      const endpoint = queryString ? `/ships/?${queryString}` : "/ships/";

      const response = await api.get(endpoint);

      // Handle both paginated and non-paginated responses
      if (response.data.results) {
        return {
          ships: response.data.results,
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
        };
      }

      // Non-paginated response
      return {
        ships: Array.isArray(response.data) ? response.data : [],
        count: Array.isArray(response.data) ? response.data.length : 0,
      };
    } catch (error) {
      console.error("Failed to fetch ships:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get ship by ID with full details
   * @param {number} shipId
   * @returns {Promise<Object>} Ship object
   */
  getShipById: async (shipId) => {
    try {
      const response = await api.get(`/ships/${shipId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch ship ${shipId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create new ship (Admin only)
   * @param {Object} shipData - Ship data object
   * @returns {Promise<Object>} Created ship object
   */
  createShip: async (shipData) => {
    try {
      const response = await api.post("/ships/", shipData);
      return response.data;
    } catch (error) {
      console.error("Failed to create ship:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update ship (Admin only)
   * @param {number} shipId
   * @param {Object} shipData - Partial ship data to update
   * @returns {Promise<Object>} Updated ship object
   */
  updateShip: async (shipId, shipData) => {
    try {
      const response = await api.patch(`/ships/${shipId}/`, shipData);
      return response.data;
    } catch (error) {
      console.error(`Failed to update ship ${shipId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete ship (Admin only)
   * @param {number} shipId
   * @returns {Promise<void>}
   */
  deleteShip: async (shipId) => {
    try {
      await api.delete(`/ships/${shipId}/`);
    } catch (error) {
      console.error(`Failed to delete ship ${shipId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Assign user to ship crew (Admin only)
   * @param {number} shipId
   * @param {number} userId
   * @returns {Promise<Object>}
   */
  assignUserToShip: async (shipId, userId) => {
    try {
      const response = await api.post(`/ships/${shipId}/assign-user/`, {
        user_id: userId,
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to assign user to ship ${shipId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Remove user from ship crew (Admin only)
   * @param {number} shipId
   * @param {number} userId
   * @returns {Promise<Object>}
   */
  /**
   * Remove user from ship crew (Admin only)
   * @param {number} shipId
   * @param {number} userId
   * @returns {Promise<Object>}
   */
  unassignUserFromShip: async (shipId, userId) => {
    try {
      const response = await api.post(`/ships/${shipId}/unassign-user/`, {
        user_id: userId,
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to unassign user from ship ${shipId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get ship crew list
   * @param {number} shipId
   * @returns {Promise<Array>}
   */
  getShipCrew: async (shipId) => {
    try {
      // Use ship detail endpoint as /crew/ does not exist
      const response = await api.get(`/ships/${shipId}/`);
      return response.data.crew || [];
    } catch (error) {
      console.error(`Failed to fetch crew for ship ${shipId}:`, error);
      throw new Error(handleApiError(error));
    }
  },
};
// export default shipsApi;

// services/Dashboard/api/coreApi.js
/**
 * Core API Service
 * Handles flags, vessel types, and rank codes
 */

export const coreApi = {
  /**
   * Ranks (Core)
   */
  getRanks: async () => {
    try {
      const response = await api.get("/core/rank-codes/");
      return Array.isArray(response.data) ? response.data : response.data.results || [];
    } catch (error) {
      console.error("Failed to fetch ranks:", error);
      throw new Error(handleApiError(error));
    }
  },

  createRank: async (rankData) => {
    try {
      const response = await api.post("/core/rank-codes/", rankData);
      return response.data;
    } catch (error) {
      console.error("Failed to create rank:", error);
      throw new Error(handleApiError(error));
    }
  },

  updateRank: async (rankId, rankData) => {
    try {
      const response = await api.patch(`/core/rank-codes/${rankId}/`, rankData);
      return response.data;
    } catch (error) {
      console.error(`Failed to update rank ${rankId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  deleteRank: async (rankId) => {
    try {
      await api.delete(`/core/rank-codes/${rankId}/`);
    } catch (error) {
      console.error(`Failed to delete rank ${rankId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get all flags
   * @returns {Promise<Array>} Array of flags
   */
  getAllFlags: async () => {
    try {
      let allFlags = [];
      let nextPage = "/core/flags/";

      while (nextPage) {
        // Handle full URL if API returns it, otherwise relative
        const response = await api.get(nextPage);

        const data = Array.isArray(response.data) ? response.data : response.data.results || [];
        allFlags = [...allFlags, ...data];

        // Update nextPage
        // Ensure we handle the case where next is a full URL
        nextPage = response.data.next;
      }

      return allFlags;
    } catch (error) {
      console.error("Failed to fetch all flags:", error);
      throw new Error(handleApiError(error));
    }
  },

  getFlags: async (params = {}) => {
    try {
      const response = await api.get("/core/flags/", { params });
      return Array.isArray(response.data)
        ? response.data
        : response.data.results || [];
    } catch (error) {
      console.error("Failed to fetch flags:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get flag by ID
   * @param {number} flagId
   * @returns {Promise<Object>}
   */
  getFlagById: async (flagId) => {
    try {
      const response = await api.get(`/core/flags/${flagId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch flag ${flagId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create flag
   * @param {Object} flagData - { name, icon }
   * @returns {Promise<Object>}
   */
  createFlag: async (flagData) => {
    try {
      const formData = new FormData();
      formData.append("name", flagData.name);
      if (flagData.icon) {
        formData.append("icon", flagData.icon);
      }

      const response = await api.post("/core/flags/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error) {
      console.error("Failed to create flag:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update flag
   * @param {number} flagId
   * @param {Object} flagData
   * @returns {Promise<Object>}
   */
  updateFlag: async (flagId, flagData) => {
    try {
      const formData = new FormData();
      if (flagData.name) formData.append("name", flagData.name);
      if (flagData.icon) formData.append("icon", flagData.icon);

      const response = await api.patch(`/core/flags/${flagId}/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to update flag ${flagId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete flag
   * @param {number} flagId
   * @returns {Promise<void>}
   */
  deleteFlag: async (flagId) => {
    try {
      await api.delete(`/core/flags/${flagId}/`);
    } catch (error) {
      console.error(`Failed to delete flag ${flagId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get all vessel types
   * @returns {Promise<Array>} Array of vessel types
   */
  getVesselTypes: async () => {
    try {
      const response = await api.get("/core/vessel-types/");
      return Array.isArray(response.data)
        ? response.data
        : response.data.results || [];
    } catch (error) {
      console.error("Failed to fetch vessel types:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get vessel type by ID
   * @param {number} vesselTypeId
   * @returns {Promise<Object>}
   */
  getVesselTypeById: async (vesselTypeId) => {
    try {
      const response = await api.get(`/core/vessel-types/${vesselTypeId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch vessel type ${vesselTypeId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create vessel type
   * @param {Object} vesselTypeData - { name }
   * @returns {Promise<Object>}
   */
  createVesselType: async (vesselTypeData) => {
    try {
      const response = await api.post("/core/vessel-types/", vesselTypeData);
      return response.data;
    } catch (error) {
      console.error("Failed to create vessel type:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update vessel type
   * @param {number} vesselTypeId
   * @param {Object} vesselTypeData
   * @returns {Promise<Object>}
   */
  updateVesselType: async (vesselTypeId, vesselTypeData) => {
    try {
      const response = await api.patch(
        `/core/vessel-types/${vesselTypeId}/`,
        vesselTypeData
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to update vessel type ${vesselTypeId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete vessel type
   * @param {number} vesselTypeId
   * @returns {Promise<void>}
   */
  deleteVesselType: async (vesselTypeId) => {
    try {
      await api.delete(`/core/vessel-types/${vesselTypeId}/`);
    } catch (error) {
      console.error(`Failed to delete vessel type ${vesselTypeId}:`, error);
      throw new Error(handleApiError(error));
    }
  },
};

// export default coreApi;
