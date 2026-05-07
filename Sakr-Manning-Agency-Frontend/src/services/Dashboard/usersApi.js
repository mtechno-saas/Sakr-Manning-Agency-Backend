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

// export const usersApi = {
//   /**
//    * Get all users with optional filters
//    * @param {Object} filters - { status, nationality, role, page, page_size }
//    * @returns {Promise<Object>} { results: [], count, next, previous }
//    */
//   getUsers: async (filters = {}) => {
//     try {
//       const params = new URLSearchParams();

//       // Add filters to query params
//       if (filters.status) params.append("status", filters.status);
//       if (filters.nationality)
//         params.append("nationality", filters.nationality);
//       if (filters.role) params.append("role", filters.role);
//       if (filters.page) params.append("page", filters.page);
//       if (filters.page_size) params.append("page_size", filters.page_size);

//       const queryString = params.toString();
//       const endpoint = queryString
//         ? `/users/users/?${queryString}`
//         : "/users/users/";

//       const response = await api.get(endpoint);

//       // Handle both paginated and non-paginated responses
//       if (response.data.results) {
//         return {
//           users: response.data.results,
//           count: response.data.count,
//           next: response.data.next,
//           previous: response.data.previous,
//         };
//       }

//       // Non-paginated response
//       return {
//         users: Array.isArray(response.data) ? response.data : [],
//         count: Array.isArray(response.data) ? response.data.length : 0,
//       };
//     } catch (error) {
//       console.error("Failed to fetch users:", error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Get user by ID with full details
//    * @param {number} userId
//    * @returns {Promise<Object>} User object with nested data
//    */
//   getUserById: async (userId) => {
//     try {
//       const response = await api.get(`/users/users/${userId}/`);
//       return response.data;
//     } catch (error) {
//       console.error(`Failed to fetch user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Create new user
//    * @param {Object} userData - User data object
//    * @returns {Promise<Object>} Created user object
//    */
//   createUser: async (userData) => {
//     try {
//       const response = await api.post("/users/users/", userData);
//       return response.data;
//     } catch (error) {
//       console.error("Failed to create user:", error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Update user
//    * @param {number} userId
//    * @param {Object} userData - Partial user data to update
//    * @returns {Promise<Object>} Updated user object
//    */
//   updateUser: async (userId, userData) => {
//     try {
//       const response = await api.patch(`/users/users/${userId}/`, userData);
//       return response.data;
//     } catch (error) {
//       console.error(`Failed to update user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Delete user
//    * @param {number} userId
//    * @returns {Promise<void>}
//    */
//   deleteUser: async (userId) => {
//     try {
//       await api.delete(`/users/users/${userId}/`);
//     } catch (error) {
//       console.error(`Failed to delete user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Get user statistics
//    * @returns {Promise<Object>} Statistics object
//    */
//   getUserStats: async () => {
//     try {
//       const response = await api.get("/users/users/stats/");
//       return response.data;
//     } catch (error) {
//       console.error("Failed to fetch user stats:", error);
//       // Return empty stats instead of throwing
//       return {
//         total_users: 0,
//         active_users: 0,
//         under_review: 0,
//         approved: 0,
//         pending: 0,
//       };
//     }
//   },

//   /**
//    * Get user certificates
//    * @param {number} userId
//    * @returns {Promise<Array>} Array of certificates
//    */
//   getUserCertificates: async (userId) => {
//     try {
//       const response = await api.get(`/users/users/${userId}/certificates/`);
//       return response.data;
//     } catch (error) {
//       console.error(`Failed to fetch certificates for user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Add certificate to user
//    * @param {number} userId
//    * @param {number} certificateId
//    * @returns {Promise<Object>}
//    */
//   addCertificateToUser: async (userId, certificateId) => {
//     try {
//       const response = await api.post(
//         `/users/users/${userId}/certificates/add/`,
//         { certificate_id: certificateId }
//       );
//       return response.data;
//     } catch (error) {
//       console.error(`Failed to add certificate to user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Remove certificate from user
//    * @param {number} userId
//    * @param {number} certificateId
//    * @returns {Promise<void>}
//    */
//   removeCertificateFromUser: async (userId, certificateId) => {
//     try {
//       await api.delete(
//         `/users/users/${userId}/certificates/${certificateId}/remove/`
//       );
//     } catch (error) {
//       console.error(`Failed to remove certificate from user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Get user ranks
//    * @param {number} userId
//    * @returns {Promise<Array>} Array of ranks with assigned codes
//    */
//   getUserRanks: async (userId) => {
//     try {
//       const response = await api.get(`/users/users/${userId}/ranks/`);
//       return response.data;
//     } catch (error) {
//       console.error(`Failed to fetch ranks for user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Add rank to user
//    * @param {number} userId
//    * @param {number} rankId
//    * @returns {Promise<Object>}
//    */
//   addRankToUser: async (userId, rankId) => {
//     try {
//       const response = await api.post(`/users/users/${userId}/ranks/add/`, {
//         rank_id: rankId,
//       });
//       return response.data;
//     } catch (error) {
//       console.error(`Failed to add rank to user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Assign rank to user (alternative endpoint)
//    * @param {number} userId
//    * @param {number} rankId
//    * @returns {Promise<Object>}
//    */
//   assignRankToUser: async (userId, rankId) => {
//     try {
//       const response = await api.post(
//         `/users/users/${userId}/assign-rank/${rankId}/`
//       );
//       return response.data;
//     } catch (error) {
//       console.error(`Failed to assign rank to user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Remove rank from user
//    * @param {number} userId
//    * @param {number} rankId
//    * @returns {Promise<void>}
//    */
//   removeRankFromUser: async (userId, rankId) => {
//     try {
//       await api.delete(`/users/users/${userId}/ranks/${rankId}/remove/`);
//     } catch (error) {
//       console.error(`Failed to remove rank from user ${userId}:`, error);
//       throw new Error(handleApiError(error));
//     }
//   },

//   /**
//    * Update profile image
//    * @param {number} userId
//    * @param {File} imageFile
//    * @returns {Promise<Object>}
//    */
//   updateProfileImage: async (userId, imageFile) => {
//     try {
//       const formData = new FormData();
//       formData.append("profile_image", imageFile);

//       const response = await api.patch(`/users/users/${userId}/`, formData, {
//         headers: {
//           "Content-Type": "multipart/form-data",
//         },
//       });
//       return response.data;
//     } catch (error) {
//       console.error(
//         `Failed to update profile image for user ${userId}:`,
//         error
//       );
//       throw new Error(handleApiError(error));
//     }
//   },
// };

// export default usersApi;

// services/Dashboard/api/certificatesApi.js
/**
 * Certificates API Service
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
      const response = await api.get("/ranks/");
      return Array.isArray(response.data)
        ? response.data
        : response.data.results || [];
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
      // Determine if we have actual filters (not just pagination)
      const hasFilters = filters.search || filters.role || filters.nationality ||
        filters.user_status || filters.marital_status ||
        filters.email || filters.first_name || filters.status ||
        filters.is_blacklisted !== undefined;

      const params = new URLSearchParams();

      // Add filter params (for both endpoints)
      // Array handling: if a filter is an array (from multi-select), we use the first value or join if BE supported. 
      // Since BE uses iexact, we extract the first string if it's an array to avoid comma-joined invalid strings.
      const getVal = (v) => Array.isArray(v) ? v[0] : v;

      if (filters.search) params.append("name", getVal(filters.search));
      if (filters.name) params.append("name", getVal(filters.name));
      if (filters.role) params.append("role", getVal(filters.role));
      if (filters.nationality) params.append("nationality", getVal(filters.nationality));
      if (filters.user_status) params.append("user_status", getVal(filters.user_status));
      if (filters.marital_status) params.append("marital_status", getVal(filters.marital_status));
      if (filters.nearest_port) params.append("nearest_port", getVal(filters.nearest_port));
      if (filters.rank_name) params.append("rank_name", getVal(filters.rank_name));
      if (filters.company) params.append("company", getVal(filters.company));
      if (filters.email) params.append("email", getVal(filters.email));
      if (filters.first_name) params.append("name", getVal(filters.first_name));
      if (filters.status) params.append("status", getVal(filters.status));
      if (filters.is_blacklisted !== undefined && filters.is_blacklisted !== "") params.append("is_blacklisted", filters.is_blacklisted);

      // Only add pagination params for /users/users/ endpoint (not for /filter/)
      // /filter/ returns ALL filtered data, we paginate on frontend
      if (!hasFilters) {
        if (filters.page) params.append("page", filters.page);
        if (filters.page_size) params.append("page_size", filters.page_size);
      }

      const queryString = params.toString();

      // Use /api/filter/ endpoint when filters are present (returns all filtered data)
      // Fall back to /users/users/ for basic pagination (when no filters)
      const baseEndpoint = hasFilters ? "/filter/" : "/users/users/";
      const endpoint = queryString ? `${baseEndpoint}?${queryString}` : baseEndpoint;

      const response = await api.get(endpoint);

      // Handle different response formats:
      // 1. /users/users/ returns { results: [], count, next, previous }
      // 2. /filter/ returns { users: [] }
      if (response.data.results) {
        // Standard paginated response
        return {
          users: response.data.results,
          count: response.data.count,
          next: response.data.next,
          previous: response.data.previous,
        };
      }

      if (response.data.users) {
        // Filter endpoint response format
        return {
          users: response.data.users,
          count: response.data.users.length,
          next: null,
          previous: null,
        };
      }

      // Non-paginated array response fallback
      return {
        users: Array.isArray(response.data) ? response.data : [],
        count: Array.isArray(response.data) ? response.data.length : 0,
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

      console.log(
        "Creating user with:",
        hasFile ? "FormData" : "JSON",
        requestData
      );

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

      console.log("Updating user with:", hasFile ? "FormData" : "JSON");
      console.log("Request data:", requestData);

      // ✅ CRITICAL: Pass data in body (2nd parameter), config in 3rd parameter
      const response = await api.patch(
        `/users/users/${userId}/`,
        requestData,
        config
      );

      console.log("Update response:", response.data);
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
      const response = await api.get("/positions/");
      return Array.isArray(response.data) ? response.data : response.data.results || [];
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
