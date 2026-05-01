// services/authServices.js
import api from "./api";
import { tokenStorage } from "./tokenStorage";
import config from "./config";
import {
  getUserIdFromToken,
  formatUserData,
  isAuthenticated as checkAuth,
} from "./helpers";
import { handleApiError } from "./handlers";

export const authService = {
  /**
   * Register new user
   * Backend: POST /api/register/
   * Body: { email, password, first_name }
   */
  register: async (userData) => {
    try {
      const response = await api.post(config.ENDPOINTS.REGISTER, {
        email: userData.email,
        password: userData.password,
        first_name: userData.first_name || userData.name,
      });

      return {
        success: true,
        data: response.data,
        message: "Registration successful",
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Login user
   * Backend: POST /api/login/
   * Body: { email, password }
   * Returns: { access, refresh }
   */
  login: async (credentials) => {
    try {
      const response = await api.post(config.ENDPOINTS.LOGIN, {
        email: credentials.email,
        password: credentials.password,
      });

      const { access, refresh } = response.data;

      // Store tokens
      tokenStorage.setAccessToken(access);
      tokenStorage.setRefreshToken(refresh);

      // Get user ID from token
      const userId = getUserIdFromToken(access);

      // Fetch user profile
      let user = null;
      if (userId) {
        try {
          const userResponse = await api.get(
            config.ENDPOINTS.USER_DETAIL(userId)
          );
          user = formatUserData(userResponse.data);
          tokenStorage.setUser(user);
        } catch (error) {
          console.warn("Could not fetch user profile:", error);
          // Create minimal user object from token
          user = { id: userId, email: credentials.email };
          tokenStorage.setUser(user);
        }
      }

      return {
        success: true,
        user,
        tokens: { access, refresh },
        message: "Login successful",
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Refresh access token
   * Backend: POST /api/login/refresh/
   * Body: { refresh }
   * Returns: { access }
   */
  refreshToken: async () => {
    try {
      const refreshToken = tokenStorage.getRefreshToken();

      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      const response = await api.post(config.ENDPOINTS.LOGIN_REFRESH, {
        refresh: refreshToken,
      });

      const { access } = response.data;
      tokenStorage.setAccessToken(access);

      return {
        success: true,
        access,
      };
    } catch (error) {
      // Clear tokens on refresh failure
      tokenStorage.clearAll();
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Get current user profile
   * Backend: GET /api/users/<id>/
   */
  getCurrentUser: async () => {
    try {
      // Try to get user from storage first
      let user = tokenStorage.getUser();
      if (user?.id) {
        // Refresh user data from API
        const response = await api.get(config.ENDPOINTS.USER_DETAIL(user.id));
        const role = await api.get(config.ENDPOINTS.USER_ME);
        user.role = role;
        user = formatUserData(response.data);
        tokenStorage.setUser(user);
        return user;
      }

      // Fallback: decode token to get user ID
      const token = tokenStorage.getAccessToken();
      if (!token) {
        throw new Error("No access token");
      }

      const userId = getUserIdFromToken(token);
      if (!userId) {
        throw new Error("Invalid token");
      }

      const response = await api.get(config.ENDPOINTS.USER_DETAIL(userId));
      user = formatUserData(response.data);
      tokenStorage.setUser(user);

      return user;
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  getUserRole: async () => {
    try {
      const user = await api.get(config.ENDPOINTS.USER_ME);
      return user.data.role;
    } catch (error) {
      console.log("an error occurs while getting user role: ", error);
      throw new Error(handleApiError(error));
    }
  },
  /**
   * Update user profile
   * Backend: PATCH /api/users/<id>/
   */
  updateProfile: async (userId, profileData) => {
    try {
      const response = await api.patch(
        config.ENDPOINTS.USER_DETAIL(userId),
        profileData
      );

      const user = formatUserData(response.data);
      tokenStorage.setUser(user);

      return {
        success: true,
        user,
        message: "Profile updated successfully",
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Logout user
   * Backend: POST /api/logout/ (optional)
   */
  logout: async () => {
    try {
      // Try to call backend logout endpoint if it exists
      // if (config.ENDPOINTS.LOGOUT) {
      //   try {
      //     await api.post(config.ENDPOINTS.LOGOUT);
      //   } catch (error) {
      //     console.warn("Backend logout failed:", error);
      //     // Continue with local logout
      //   }
      // }

      // Clear local storage
      tokenStorage.clearAll();

      return {
        success: true,
        message: "Logged out successfully",
      };
    } catch (error) {
      console.log("an error occurs : ", error);
      // Always clear local storage even if API call fails
      tokenStorage.clearAll();
      return {
        success: true,
        message: "Logged out successfully",
      };
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    const accessToken = tokenStorage.getAccessToken();
    const refreshToken = tokenStorage.getRefreshToken();
    return checkAuth(accessToken, refreshToken);
  },

  /**
   * Get stored user data
   */
  getStoredUser: () => {
    return tokenStorage.getUser();
  },

  // ========================================
  // OPTIONAL: Email Verification Methods
  // Only enable if backend supports these endpoints
  // ========================================

  /**
   * Send verification code (if backend supports)
   * Backend: POST /auth/send-verification/
   */
  sendVerificationCode: async (email) => {
    if (!config.FEATURES.EMAIL_VERIFICATION) {
      console.warn("Email verification not enabled in backend");
      return {
        success: false,
        message: "Email verification not supported",
      };
    }

    try {
      const response = await api.post(config.ENDPOINTS.SEND_VERIFICATION, {
        email,
      });
      return {
        success: true,
        data: response.data,
        message: "Verification code sent",
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Verify code (if backend supports)
   * Backend: POST /auth/verify-code/
   */
  verifyCode: async (code, email) => {
    if (!config.FEATURES.EMAIL_VERIFICATION) {
      console.warn("Email verification not enabled in backend");
      return {
        success: false,
        message: "Email verification not supported",
      };
    }

    try {
      const response = await api.post(config.ENDPOINTS.VERIFY_CODE, {
        code,
        email,
      });
      return {
        success: true,
        data: response.data,
        message: "Verification successful",
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Resend verification code
   */
  resendCode: async (email) => {
    return await authService.sendVerificationCode(email);
  },

  // ========================================
  // OPTIONAL: Password Reset Methods
  // Only enable if backend supports these endpoints
  // ========================================

  /**
   * Forgot password (if backend supports)
   */
  forgotPassword: async (email) => {
    try {
      const response = await api.post(config.ENDPOINTS.FORGOT_PASSWORD, {
        email,
      });
      return {
        success: true,
        data: response.data,
        message: "Password reset email sent",
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  /**
   * Reset password (if backend supports)
   */
  resetPassword: async (token, newPassword) => {
    try {
      const response = await api.post(config.ENDPOINTS.RESET_PASSWORD, {
        token,
        new_password: newPassword,
      });
      return {
        success: true,
        data: response.data,
        message: "Password reset successful",
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },

  // ========================================
  // OPTIONAL: Google Authentication
  // Only enable if backend supports Google OAuth
  // ========================================

  /**
   * Google authentication
   * 
   * To enable:
   * 1. Set GOOGLE_AUTH: true in config.FEATURES
   * 2. Set VITE_GOOGLE_CLIENT_ID in .env
   * 3. Backend needs endpoint: POST /auth/google/
   *    - Request: { credential: "google_id_token" }
   *    - Response: { access, refresh } (same as /login)
   * 
   * @param {Object} googleData - Google OAuth response data
   * @param {string} googleData.credential - Google ID token
   */
  googleAuth: async (googleData) => {
    if (!config.FEATURES.GOOGLE_AUTH) {
      console.warn("Google auth not enabled. Set FEATURES.GOOGLE_AUTH = true in config.js");
      return {
        success: false,
        message: "Google authentication is not yet enabled. Please use email and password to log in.",
      };
    }

    try {
      const response = await api.post(config.GOOGLE.ENDPOINT, {
        credential: googleData.credential,
      });

      const { access, refresh } = response.data;

      // Store tokens (same flow as regular login)
      tokenStorage.setAccessToken(access);
      tokenStorage.setRefreshToken(refresh);

      // Get user ID from token and fetch profile
      const userId = getUserIdFromToken(access);
      let user = null;

      if (userId) {
        try {
          const userResponse = await api.get(
            config.ENDPOINTS.USER_DETAIL(userId)
          );
          user = formatUserData(userResponse.data);
          tokenStorage.setUser(user);
        } catch (error) {
          console.warn("Could not fetch user profile:", error);
          // Create minimal user object
          user = { id: userId };
          tokenStorage.setUser(user);
        }
      }

      return {
        success: true,
        user,
        tokens: { access, refresh },
        message: "Google authentication successful",
      };
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  },
};

export default authService;
