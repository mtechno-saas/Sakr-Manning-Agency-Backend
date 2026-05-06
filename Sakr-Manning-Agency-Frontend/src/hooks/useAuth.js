// hooks/useAuth.js
import { useCallback } from "react";
import authService from "../services/Auth/authServices";
import config from "../services/Auth/config";
import { useAuthContext } from "../context/AuthContext";

export const useAuth = () => {
  const {
    user,
    setUser,
    isLoading,
    setIsLoading,
    error,
    setError,
    isInitialized,
    isAuthenticated,
    logout: contextLogout
  } = useAuthContext();

  /**
   * Clear error manually
   */
  const clearError = useCallback(() => {
    setError(null);
  }, [setError]);

  /**
   * Login function
   */
  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.login(credentials);
      if (result.success && result.user) {
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
  }, [setUser, setError, setIsLoading]);

  /**
   * Signup function
   */
  const signup = useCallback(async (userData) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await authService.register(userData);

      if (result.success) {
        if (config.FEATURES.EMAIL_VERIFICATION) {
          return {
            success: true,
            requiresVerification: true,
            message: result.message,
          };
        }

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
  }, [setUser, setError, setIsLoading]);

  /**
   * Logout function
   */
  const logout = useCallback(async () => {
    await contextLogout();
    return { success: true };
  }, [contextLogout]);

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
  }, [setUser, setError, setIsLoading]);

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
  }, [setUser, setError, setIsLoading]);

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
  }, [setUser]);

  //Verification methods...
  const sendVerificationCode = useCallback(async (email) => {
    if (!config.FEATURES.EMAIL_VERIFICATION) return { success: false, message: "Not supported" };
    setIsLoading(true);
    setError(null);
    try {
      const result = await authService.sendVerificationCode(email);
      return { success: true, message: result.message };
    } catch (err) {
      setError(err.message);
      return { success: false, message: err.message };
    } finally {
      setIsLoading(false);
    }
  }, [setError, setIsLoading]);

  const verifyCode = useCallback(async (code, email) => {
    if (!config.FEATURES.EMAIL_VERIFICATION) return { success: false, message: "Not supported" };
    setIsLoading(true);
    setError(null);
    try {
      const result = await authService.verifyCode(code, email);
      if (result.success) {
        const loginResult = await authService.login({ email, password: null });
        if (loginResult.success) setUser(loginResult.user);
        return { success: true, message: result.message };
      }
      throw new Error(result.message || "Verification failed");
    } catch (err) {
      setError(err.message);
      return { success: false, message: err.message };
    } finally {
      setIsLoading(false);
    }
  }, [setUser, setError, setIsLoading]);

  const resendCode = useCallback(async (email) => {
    return await sendVerificationCode(email);
  }, [sendVerificationCode]);

  return {
    user,
    isLoading,
    error,
    isInitialized,
    isAuthenticated,
    login,
    signup,
    logout,
    getProfile,
    updateProfile,
    refreshToken,
    clearError,
    sendVerificationCode,
    verifyCode,
    resendCode,
  };
};
