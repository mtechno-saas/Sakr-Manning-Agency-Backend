/*
// Handles all user-related API calls
- getUsers() - List all users with pagination/filters
- getUserById(id) - Get detailed user info
- createUser(userData) - Create new user (Add Manual CV)
- updateUser(id, userData) - Update existing user
- deleteUser(id) - Delete user (Admin only)
- updateUserRole(id, role) - Change user role (Admin only)
- getUserCertificates(id) - Get user certificates
- getUserRanks(id) - Get user ranks
*/

// services/Dashboard/api/usersApi.js
import api from "../Auth/api.js";
import { handleApiError } from "../Auth/handlers.js";

/**
 * Users API Service
 * Handles all user-related API calls for the dashboard
 */

export const certificatesApi = {
  /**
   * Get all certificates
   * @returns {Promise<Array>} Array of certificates
   */
  getCertificates: async () => {
    try {
      const response = await api.get("/users/certificates/");
      return Array.isArray(response.data)
        ? response.data
        : response.data.results || [];
    } catch (error) {
      console.error("Failed to fetch certificates:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get certificate by ID
   * @param {number} certificateId
   * @returns {Promise<Object>}
   */
  getCertificateById: async (certificateId) => {
    try {
      const response = await api.get(`/certificates/${certificateId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch certificate ${certificateId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create certificate (Admin only)
   * @param {Object} certificateData - { code, name }
   * @returns {Promise<Object>}
   */
  createCertificate: async (certificateData) => {
    try {
      const response = await api.post("/certificates/", certificateData);
      return response.data;
    } catch (error) {
      console.error("Failed to create certificate:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update certificate (Admin only)
   * @param {number} certificateId
   * @param {Object} certificateData
   * @returns {Promise<Object>}
   */
  updateCertificate: async (certificateId, certificateData) => {
    try {
      const response = await api.patch(
        `/certificates/${certificateId}/`,
        certificateData
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to update certificate ${certificateId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete certificate (Admin only)
   * @param {number} certificateId
   * @returns {Promise<void>}
   */
  deleteCertificate: async (certificateId) => {
    try {
      await api.delete(`/certificates/${certificateId}/`);
    } catch (error) {
      console.error(`Failed to delete certificate ${certificateId}:`, error);
      throw new Error(handleApiError(error));
    }
  },
};

// export default certificatesApi;

// services/Dashboard/api/ranksApi.js
/**
 * Ranks API Service
 */

export const ranksApi = {
  /**
   * Get all ranks
   * @returns {Promise<Array>} Array of ranks
   */
  getRanks: async () => {
    try {
      let allRanks = [];
      let nextUrl = "/ranks/";

      while (nextUrl) {
        // Handle absolute URLs returned by the backend in the 'next' field
        const endpoint = nextUrl.startsWith('http') 
          ? new URL(nextUrl).pathname + new URL(nextUrl).search
          : nextUrl;

        // Ensure we don't duplicate /api/ if it's already in the path and api instance adds it
        const finalEndpoint = endpoint.replace('/api/', '/');

        const response = await api.get(finalEndpoint);

        if (Array.isArray(response.data)) {
          allRanks = [...allRanks, ...response.data];
          break;
        } else if (response.data.results) {
          allRanks = [...allRanks, ...response.data.results];
          nextUrl = response.data.next;
        } else {
          break;
        }
      }
      return allRanks;
    } catch (error) {
      console.error("Failed to fetch ranks:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get rank by ID
   * @param {number} rankId
   * @returns {Promise<Object>}
   */
  getRankById: async (rankId) => {
    try {
      const response = await api.get(`/ranks/${rankId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch rank ${rankId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create rank (Admin only)
   * @param {Object} rankData - { code, name }
   * @returns {Promise<Object>}
   */
  createRank: async (rankData) => {
    try {
      const response = await api.post("/ranks/", rankData);
      return response.data;
    } catch (error) {
      console.error("Failed to create rank:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update rank (Admin only)
   * @param {number} rankId
   * @param {Object} rankData
   * @returns {Promise<Object>}
   */
  updateRank: async (rankId, rankData) => {
    try {
      const response = await api.patch(`/ranks/${rankId}/`, rankData);
      return response.data;
    } catch (error) {
      console.error(`Failed to update rank ${rankId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete rank (Admin only)
   * @param {number} rankId
   * @returns {Promise<void>}
   */
  deleteRank: async (rankId) => {
    try {
      await api.delete(`/ranks/${rankId}/`);
    } catch (error) {
      console.error(`Failed to delete rank ${rankId}:`, error);
      throw new Error(handleApiError(error));
    }
  },
};

// export default ranksApi;

/**
 * Users API Service
 * Handles all user-related API calls for the dashboard
 */

export const usersApi = {
  /**
   * Get all users with optional filters
   * Uses /api/filter/ endpoint when filters are provided for proper filtering
   * Falls back to /users/users/ for basic pagination without filters
   * 
   * @param {Object} filters - Filter parameters
   * @param {string} filters.search - General search across fields
   * @param {string} filters.role - Filter by role (admin, hr_manager, recruiter, employee)
   * @param {string} filters.nationality - Filter by nationality
   * @param {string} filters.user_status - Filter by status (VECATION, ON_SITE, MEDICAL VECATION)
   * @param {string} filters.marital_status - Filter by marital status (SINGLE, MARRIED)
   * @param {string} filters.email - Filter by email
   * @param {string} filters.first_name - Filter by first name
   * @param {number} filters.page - Page number for pagination
   * @param {number} filters.page_size - Items per page (default 25)
   * @returns {Promise<Object>} { users: [], count, next, previous }
   */
  getUsers: async (filters = {}) => {
    try {
      // Keys that are NOT filters (used for pagination/control)
      const nonFilterKeys = ["page", "page_size", "ordering"];

      // Determine if we have actual filters
      const hasFilters = Object.keys(filters).some(key =>
        !nonFilterKeys.includes(key) &&
        filters[key] !== undefined &&
        filters[key] !== null &&
        filters[key] !== "" &&
        filters[key] !== false
      );

      const params = new URLSearchParams();

      // Mapping for specific keys if they differ between UI and BE
      const keyMap = {
        name: "name",
        search: "name",
        first_name: "name",
      };

      // Helper to handle value extraction (especially for arrays)
      const appendParam = (key, value) => {
        if (value === undefined || value === null || value === "" || value === false) return;

        const beKey = keyMap[key] || key;

        if (Array.isArray(value)) {
          // Some BE endpoints expect multiple params with same key
          value.forEach(v => params.append(beKey, v));
        } else {
          params.append(beKey, value);
        }
      };

      // Append all filters
      Object.entries(filters).forEach(([key, value]) => {
        if (!nonFilterKeys.includes(key)) {
          appendParam(key, value);
        }
      });

      // Add pagination params
      if (filters.page) params.append("page", filters.page);

      const queryString = params.toString();
      // Always use the standard users list endpoint as requested
      const baseEndpoint = "/users/users/";
      const endpoint = queryString ? `${baseEndpoint}?${queryString}` : baseEndpoint;

      const response = await api.get(endpoint);

      // Standardize the response parsing
      if (response.data.results) {
        return {
          users: response.data.results,
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
        };
      }

      // Fallback for non-paginated or alternative formats
      const users = response.data.users || (Array.isArray(response.data) ? response.data : []);
      return {
        users: users,
        count: response.data.count || users.length,
        next: response.data.next || null,
        previous: response.data.previous || null,
      };
    } catch (error) {
      console.error("Failed to fetch users:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Search users for TypeaheadInput (optimized for autocomplete)
   * @param {Object} params - { search, role, limit }
   * @returns {Promise<Array>} Array of { value, label, ...userData }
   */
  searchUsers: async (params = {}) => {
    try {
      const queryParams = new URLSearchParams();

      if (params.search) queryParams.append("name", params.search);
      if (params.role) queryParams.append("role", params.role);
      queryParams.append("page_size", params.limit || 20);

      const endpoint = `/users/users/?${queryParams.toString()}`;
      const response = await api.get(endpoint);

      const users = response.data.results || response.data || [];

      // Transform to TypeaheadInput format
      return users.map(user => ({
        value: user.id,
        label: `${user.first_name || ''} ${user.middle_name || ''} ${user.last_name || ''}`.trim() || user.email,
        id: user.id,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        profile_image: user.profile_image,
      }));
    } catch (error) {
      console.error("Failed to search users:", error);
      return [];
    }
  },

  /**
   * Get user by ID with full details
   * @param {number} userId
   * @returns {Promise<Object>} User object with nested data
   */
  getUserById: async (userId) => {
    try {
      const response = await api.get(`/users/users/${userId}/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Create new user
   * @param {Object} userData - User data object (can include profile_image as File)
   * @returns {Promise<Object>} Created user object
   */
  createUser: async (userData) => {
    try {
      // Check if we have a file (profile_image)
      const hasFile = userData.profile_image instanceof File;

      let requestData;
      let config = {};

      if (hasFile) {
        // Use FormData for file uploads
        requestData = new FormData();

        // Add all fields to FormData
        Object.keys(userData).forEach((key) => {
          const value = userData[key];

          if (value === null || value === undefined) {
            return; // Skip null/undefined values
          }

          // Handle arrays (rank_ids, certificate_ids)
          if (Array.isArray(value)) {
            value.forEach((item) => {
              requestData.append(key, item);
            });
          } else if (value instanceof File) {
            // Handle file
            requestData.append(key, value);
          } else {
            // Handle other values
            requestData.append(key, value);
          }
        });

        config = {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        };
      } else {
        // Use JSON for regular data (NO FILES)
        requestData = { ...userData };

        // Remove null/undefined values
        Object.keys(requestData).forEach((key) => {
          if (requestData[key] === null || requestData[key] === undefined) {
            delete requestData[key];
          }
        });

        config = {
          headers: {
            "Content-Type": "application/json",
          },
        };
      }

      const response = await api.post("/users/users/", requestData, config);
      return response.data;
    } catch (error) {
      console.error("Failed to create user:", error);
      console.error("Error response:", error.response?.data);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update user
   * @param {number} userId
   * @param {Object} userData - Partial user data to update (can include profile_image as File)
   * @returns {Promise<Object>} Updated user object
   */
  updateUser: async (userId, userData) => {
    try {
      // Check if we have a file (profile_image)
      const hasFile = userData.profile_image instanceof File;

      let requestData;
      let config = {};

      if (hasFile) {
        // Use FormData for file uploads
        requestData = new FormData();

        // Add all fields to FormData
        Object.keys(userData).forEach((key) => {
          const value = userData[key];

          if (value === null || value === undefined) {
            return; // Skip null/undefined values
          }

          // Handle arrays (rank_ids, certificate_ids)
          if (Array.isArray(value)) {
            value.forEach((item) => {
              requestData.append(key, item);
            });
          } else if (value instanceof File) {
            // Handle file
            requestData.append(key, value);
          } else {
            // Handle other values
            requestData.append(key, value);
          }
        });

        config = {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        };
      } else {
        // ✅ CRITICAL: Use JSON for regular data (NO FILES)
        requestData = { ...userData };

        // Remove null/undefined values
        Object.keys(requestData).forEach((key) => {
          if (requestData[key] === null || requestData[key] === undefined) {
            delete requestData[key];
          }
        });

        // ✅ CRITICAL: Explicitly set Content-Type to JSON
        config = {
          headers: {
            "Content-Type": "application/json",
          },
        };
      }
      // ✅ CRITICAL: Pass data in body (2nd parameter), config in 3rd parameter
      const response = await api.patch(
        `/users/users/${userId}/`,
        requestData,
        config
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to update user ${userId}:`, error);
      console.error("Error response:", error.response?.data);
      console.error("Error config:", error.config);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Delete user
   * @param {number} userId
   * @returns {Promise<void>}
   */
  deleteUser: async (userId) => {
    try {
      await api.delete(`/users/users/${userId}/`);
    } catch (error) {
      console.error(`Failed to delete user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get user statistics
   * @returns {Promise<Object>} Statistics object
   */
  getUserStats: async () => {
    try {
      const response = await api.get("/users/users/stats/");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch user stats:", error);
      // Return empty stats instead of throwing
      return {
        total_users: 0,
        active_users: 0,
        under_review: 0,
        approved: 0,
        pending: 0,
      };
    }
  },

  /**
   * Get user certificates
   * @param {number} userId
   * @returns {Promise<Array>} Array of certificates
   */
  getUserCertificates: async (userId) => {
    try {
      const response = await api.get(`/users/users/${userId}/certificates/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch certificates for user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Add certificate to user
   * @param {number} userId
   * @param {number} certificateId
   * @returns {Promise<Object>}
   */
  addCertificateToUser: async (userId, certificateId) => {
    try {
      const response = await api.post(
        `/users/users/${userId}/certificates/add/`,
        { certificate_id: certificateId },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to add certificate to user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Remove certificate from user
   * @param {number} userId
   * @param {number} certificateId
   * @returns {Promise<void>}
   */
  removeCertificateFromUser: async (userId, certificateId) => {
    try {
      await api.delete(
        `/users/users/${userId}/certificates/${certificateId}/remove/`
      );
    } catch (error) {
      console.error(`Failed to remove certificate from user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get user ranks
   * @param {number} userId
   * @returns {Promise<Array>} Array of ranks with assigned codes
   */
  getUserRanks: async (userId) => {
    try {
      const response = await api.get(`/users/users/${userId}/ranks/`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch ranks for user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Add rank to user
   * @param {number} userId
   * @param {number} rankId
   * @returns {Promise<Object>}
   */
  addRankToUser: async (userId, rankId) => {
    try {
      const response = await api.post(
        `/users/users/${userId}/ranks/add/`,
        { rank_id: rankId },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to add rank to user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Assign rank to user (alternative endpoint)
   * @param {number} userId
   * @param {number} rankId
   * @returns {Promise<Object>}
   */
  assignRankToUser: async (userId, rankId) => {
    try {
      const response = await api.post(
        `/users/users/${userId}/assign-rank/${rankId}/`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to assign rank to user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Remove rank from user
   * @param {number} userId
   * @param {number} rankId
   * @returns {Promise<void>}
   */
  removeRankFromUser: async (userId, rankId) => {
    try {
      await api.delete(`/users/users/${userId}/ranks/${rankId}/remove/`);
    } catch (error) {
      console.error(`Failed to remove rank from user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get all available positions from the positions dropdown
   * GET /api/positions/
   * @returns {Promise<Array>} Array of { value, label } position objects
   */
  getPositions: async () => {
    try {
      let allPositions = [];
      let nextUrl = "/positions/";

      while (nextUrl) {
        // Handle absolute URLs returned by the backend in the 'next' field
        const endpoint = nextUrl.startsWith('http') 
          ? new URL(nextUrl).pathname + new URL(nextUrl).search
          : nextUrl;

        // Ensure we don't duplicate /api/ if it's already in the path and api instance adds it
        const finalEndpoint = endpoint.replace('/api/', '/');

        const response = await api.get(finalEndpoint);

        if (Array.isArray(response.data)) {
          allPositions = [...allPositions, ...response.data];
          break;
        } else if (response.data.results) {
          allPositions = [...allPositions, ...response.data.results];
          nextUrl = response.data.next;
        } else {
          break;
        }
      }
      return allPositions;
    } catch (error) {
      console.error("Failed to fetch positions:", error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Assign a coded rank to a user by position name
   * POST /api/users/{userId}/assign-by-position/
   * @param {number} userId
   * @param {string} position - Position value from GET /api/positions/ (e.g. "2nd. Engineer")
   * @returns {Promise<Object>} { message, rank_created_in_db, user_rank: { id, assigned_code, rank_code, rank_name, rank } }
   */
  assignByPosition: async (userId, position) => {
    try {
      const response = await api.post(
        `/users/users/${userId}/assign-by-position/`,
        { position },
        { headers: { "Content-Type": "application/json" } }
      );
      return response.data;
    } catch (error) {
      console.error(`Failed to assign rank by position for user ${userId}:`, error);
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Update profile image
   * @param {number} userId
   * @param {File} imageFile
   * @returns {Promise<Object>}
   */
  updateProfileImage: async (userId, imageFile) => {
    try {
      const formData = new FormData();
      formData.append("profile_image", imageFile);

      const response = await api.patch(`/users/users/${userId}/`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error) {
      console.error(
        `Failed to update profile image for user ${userId}:`,
        error
      );
      throw new Error(handleApiError(error));
    }
  },
};

export default usersApi;
