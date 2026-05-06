import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import authService from "../services/Auth/authServices";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const storedUser = authService.getStoredUser();
          if (storedUser) {
            setUser(storedUser);
            // Refresh in background
            try {
              const currentUser = await authService.getCurrentUser();
              setUser(currentUser);
            } catch (err) {
              console.warn("Could not refresh user data:", err);
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

  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await authService.login(credentials);
      if (result.success && result.user) {
        setUser(result.user);
        return result;
      }
      throw new Error(result.message || "Login failed");
    } catch (err) {
      setError(err.message);
      return { success: false, message: err.message };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const value = {
    user,
    isLoading,
    error,
    isInitialized,
    isAuthenticated: !!user,
    login,
    logout,
    setUser,
    setError,
    setIsLoading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within an AuthProvider");
  }
  return context;
};
