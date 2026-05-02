// components/layout/ProtectedRoute.jsx
import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { tokenStorage } from "../../services/Auth/tokenStorage";

/**
 * ProtectedRoute
 *
 * Two-phase role check:
 *  1. While useAuth initialises (async), fall back to the role stored in
 *     localStorage so the page doesn't flash a redirect on hard-refresh.
 *  2. Once initialised, trust the live `user` object from useAuth (which was
 *     hydrated from the backend on mount).
 *
 * Security note: localStorage role is UI-only. Real enforcement is on the
 * Django backend via JWT permission classes on every API call.
 */
const isAdminRole = (role) => {
  const r = role?.toLowerCase();
  return r === "admin" || r === "administrator";
};

export const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, isLoading, isInitialized } = useAuth();

  // ── Phase 1: auth not yet initialised ────────────────────────────────────
  if (!isInitialized || isLoading) {
    // Quick pre-check using localStorage so admins don't get flashed to /auth
    // on a hard-refresh while the token validation is in flight.
    const storedUser = tokenStorage.getUser();

    if (!storedUser) {
      // No stored session at all — show spinner
      return (
        <div className="min-h-screen w-full flex items-center justify-center bg-white">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4" />
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      );
    }

    if (requiredRole) {
      // If the stored role already fails the check, redirect immediately
      // rather than showing the spinner. Avoids a slow flash for regular users
      // trying to access /dashboard.
      const storedRoleOk = isAdminRole(storedUser.role);
      if (!storedRoleOk) {
        return <Navigate to="/" replace />;
      }
    }

    // Stored session looks valid — show spinner while we finish verifying
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // ── Phase 2: auth initialised — use live user object ─────────────────────
  if (!user) {
    return (
      <Navigate
        to="/auth"
        replace
        state={{ intendedPath: window.location.pathname }}
      />
    );
  }

  if (requiredRole) {
    const hasRole = isAdminRole(user.role);
    if (!hasRole) {
      // Regular user trying to access /dashboard → send home
      return <Navigate to="/" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
