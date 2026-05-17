// services/Dashboard/hooks/usePermissions.js
import { useMemo } from "react";
import { useAuth } from "../useAuth";

/**
 * Custom hook for role-based permissions
 *
 * Rules:
 * - Admin: Full CRUD access
 * - HR Manager & Recruiter: Read-only access
 * - Employee: No dashboard access (handled by ProtectedRoute)
 */

export const usePermissions = () => {
  const { user } = useAuth();

  const permissions = useMemo(() => {
    const userRole = user?.role?.toLowerCase();
    // const userRole = "admin";
    const isAdmin = userRole === "admin" || userRole === "administrator";
    const isHR =
      userRole === "hr" ||
      userRole === "hr_manager" ||
      userRole === "hr manager";
    const isRecruiter = userRole === "recruiter";

    return {
      // User info
      userRole,
      isAdmin,
      isHR,
      isRecruiter,

      // Read permissions (all dashboard users can view)
      canView: true,

      // Write permissions (Admin only)
      canCreate: isAdmin,
      canEdit: isAdmin,
      canUpdate: isAdmin,
      canDelete: isAdmin,

      // Special permissions
      canChangeRoles: isAdmin, // Only admin can change user roles
      canViewFinance: isAdmin || isHR,
      canManageFinance: isAdmin,
      canManageContracts: isAdmin || isHR,
      canScheduleInterviews: isAdmin || isHR || isRecruiter,
      canManageShips: isAdmin,
      canManageCompanies: isAdmin,

      // Helper function to check if action is allowed
      checkPermission: (action) => {
        switch (action) {
          case "create":
          case "edit":
          case "update":
          case "delete":
            return isAdmin;
          case "view":
            return true;
          default:
            return false;
        }
      },
    };
  }, [user?.role]); // if any errors put the user in the dependency array

  return permissions;
};

export default usePermissions;
