// components/ProtectedRoute.jsx
import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, isLoading, isInitialized } = useAuth();

  // Show loading while initializing
  if (!isInitialized || isLoading) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!user) {
    return (
      <Navigate
        to="/auth"
        replace
        state={{ intendedPath: window.location.pathname }}
      />
    );
  }

  // Role-based access check
  if (requiredRole) {
    const userRole = user.role?.toLowerCase();
    const hasRequiredRole = Array.isArray(requiredRole)
      ? requiredRole.some((role) => userRole === role.toLowerCase())
      : userRole === requiredRole.toLowerCase();

    if (!hasRequiredRole) {
      // Redirect based on role
      if (userRole === "admin" || userRole === "administrator") {
        return <Navigate to="/dashboard" replace />;
      } else {
        return <Navigate to="/form" replace />;
      }
    }
  }

  return children;
};

export default ProtectedRoute;
