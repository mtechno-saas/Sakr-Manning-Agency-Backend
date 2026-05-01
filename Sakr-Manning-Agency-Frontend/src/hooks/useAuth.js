// hooks/useAuth.js
import { useState, useCallback, useEffect } from "react";
import authService from "../services/Auth/authServices";
import config from "../services/Auth/config";

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          // Try to get user from storage first
          const storedUser = authService.getStoredUser();
          if (storedUser) {
            setUser(storedUser);

            // Optionally refresh user data from API in background
            try {
              const currentUser = await authService.getCurrentUser();
              setUser(currentUser);
            } catch (err) {
              console.warn("Could not refresh user data:", err);
              // Keep using stored user
            }
          }
        }
      } catch (err) {
        console.error("Auth initialization error:", err);
      } finally {
        setIsInitialized(true);
      }
    };

    initializeAuth();
  }, []);

  // Auto-clear error after timeout
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Clear error manually
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Login function
   */
  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.login(credentials);
      // console.log("the use Auth response : ", result);
      // const userRole = await authService.getUserRole();
      // console.log("the use Auth response : ", userRole);
      if (result.success && result.user) {
        // result.user.role = userRole;
        setUser(result.user);
        sessionStorage.setItem("last_login", Date.now().toString());
        return {
          success: true,
          message: result.message,
          user: result.user,
          requiresAdminRedirect: result.user.role?.toLowerCase() === "admin",
        };
      }

      throw new Error(result.message || "Login failed");
    } catch (err) {
      const errorMessage = err.message || "Login failed";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Signup function
   */
  const signup = useCallback(async (userData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.register(userData);

      if (result.success) {
        // If email verification is required, don't auto-login
        if (config.FEATURES.EMAIL_VERIFICATION) {
          return {
            success: true,
            requiresVerification: true,
            message: result.message,
          };
        }

        // If no verification needed, auto-login
        const loginResult = await authService.login({
          email: userData.email,
          password: userData.password,
        });

        if (loginResult.success) {
          setUser(loginResult.user);
        }

        return {
          success: true,
          requiresVerification: false,
          message: result.message,
        };
      }

      throw new Error(result.message || "Signup failed");
    } catch (err) {
      const errorMessage = err.message || "Signup failed";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Logout function
   */
  const logout = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      await authService.logout();
      setUser(null);
      return { success: true };
    } catch (err) {
      const errorMessage = err.message || "Logout failed";
      setError(errorMessage);
      // Still clear user state even if API call fails
      setUser(null);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Get current user profile
   */
  const getProfile = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const currentUser = await authService.getCurrentUser();
      const userRole = await authService.getUserRole();
      currentUser.role = userRole;
      setUser(currentUser);
      return {
        success: true,
        user: currentUser,
      };
    } catch (err) {
      const errorMessage = err.message || "Failed to fetch profile";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Update user profile
   */
  const updateProfile = useCallback(async (userId, profileData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.updateProfile(userId, profileData);

      if (result.success) {
        setUser(result.user);
        return {
          success: true,
          user: result.user,
          message: result.message,
        };
      }

      throw new Error(result.message || "Update failed");
    } catch (err) {
      const errorMessage = err.message || "Update failed";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Refresh token
   */
  const refreshToken = useCallback(async () => {
    try {
      await authService.refreshToken();
      return { success: true };
    } catch (err) {
      console.error("Token refresh failed:", err);
      setUser(null);
      return {
        success: false,
        message: "Session expired",
      };
    }
  }, []);

  // ========================================
  // OPTIONAL: Email Verification Methods
  // ========================================

  const sendVerificationCode = useCallback(async (email) => {
    if (!config.FEATURES.EMAIL_VERIFICATION) {
      console.warn("Email verification not enabled");
      return {
        success: false,
        message: "Email verification not supported",
      };
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.sendVerificationCode(email);
      return {
        success: true,
        message: result.message,
      };
    } catch (err) {
      const errorMessage = err.message || "Failed to send code";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const verifyCode = useCallback(async (code, email) => {
    if (!config.FEATURES.EMAIL_VERIFICATION) {
      console.warn("Email verification not enabled");
      return {
        success: false,
        message: "Email verification not supported",
      };
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.verifyCode(code, email);

      if (result.success) {
        // After verification, login the user
        const loginResult = await authService.login({ email, password: null });
        if (loginResult.success) {
          setUser(loginResult.user);
        }

        return {
          success: true,
          message: result.message,
        };
      }

      throw new Error(result.message || "Verification failed");
    } catch (err) {
      const errorMessage = err.message || "Verification failed";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resendCode = useCallback(
    async (email) => {
      return await sendVerificationCode(email);
    },
    [sendVerificationCode]
  );

  // ========================================
  // OPTIONAL: Google Authentication
  // ========================================

  const googleAuth = useCallback(async (googleData) => {
    if (!config.FEATURES.GOOGLE_AUTH) {
      console.warn("Google auth not enabled");
      return {
        success: false,
        message: "Google authentication not supported",
      };
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.googleAuth(googleData);

      if (result.success && result.user) {
        setUser(result.user);
        return {
          success: true,
          message: result.message,
        };
      }

      throw new Error(result.message || "Google authentication failed");
    } catch (err) {
      const errorMessage = err.message || "Google authentication failed";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ========================================
  // OPTIONAL: Password Reset Methods
  // ========================================

  const forgotPassword = useCallback(async (email) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.forgotPassword(email);
      return {
        success: true,
        message: result.message,
      };
    } catch (err) {
      const errorMessage = err.message || "Failed to send reset email";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const resetPassword = useCallback(async (token, newPassword) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.resetPassword(token, newPassword);
      return {
        success: true,
        message: result.message,
      };
    } catch (err) {
      const errorMessage = err.message || "Password reset failed";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    // State
    user,
    isLoading,
    error,
    isInitialized,
    isAuthenticated: !!user,

    // Core Actions
    login,
    signup,
    logout,
    getProfile,
    updateProfile,
    refreshToken,
    clearError,

    // Optional: Email Verification
    sendVerificationCode,
    verifyCode,
    resendCode,

    // Optional: Google Auth
    googleAuth,

    // Optional: Password Reset
    forgotPassword,
    resetPassword,
  };
};
