// services/Dashboard/hooks/useUsers.js
import { useState, useCallback } from "react";
import { usersApi } from "../../services/Dashboard/usersApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { usePermissions } from "./usePermissions";
import { useDashboardData } from "../../components/dashboard/context/DashboardDataContext";

/**
 * Custom hook for managing users in the dashboard
 * Handles fetching, creating, updating, deleting users
 * Includes permission checks and notifications
 */

export const useUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    pageSize: 50,
    totalPages: 1,
  });

  const { notify } = useNotification();
  const { canEdit, canDelete, canCreate } = usePermissions();
  const { fetchUsers: refreshGlobalUsers } = useDashboardData();

  /**
   * Fetch users with optional filters
   * Defaults to 25 records per page for server-side pagination
   */
  const fetchUsers = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);

      try {
        const response = await usersApi.getUsers({
          ...filters,
        });

        // Use a default page size of 50 for pagination calculations if not provided by BE
        const pageSize = 50;
        const count = response.count || 0;
        const totalPages = Math.max(1, Math.ceil(count / pageSize));

        setUsers(response.users || []);
        setPagination({
          count: count,
          next: response.next || null,
          previous: response.previous || null,
          currentPage: filters.page || 1,
          pageSize: pageSize,
          totalPages: totalPages,
        });

        return { success: true, data: response.users };
      } catch (err) {
        const errorMessage = err.message || "Failed to load users";
        setError(errorMessage);
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  /**
   * Get single user by ID
   */
  const getUserById = useCallback(
    async (userId) => {
      try {
        const user = await usersApi.getUserById(userId);
        return { success: true, data: user };
      } catch (err) {
        const errorMessage = err.message || "Failed to load user";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [notify]
  );

  /**
   * Create new user (Admin only)
   */
  const createUser = useCallback(
    async (userData) => {
      if (!canCreate) {
        notify.error("You do not have permission to create users");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const newUser = await usersApi.createUser(userData);

        // Add to local state
        setUsers((prev) => [newUser, ...prev]);
        setPagination((prev) => ({ ...prev, count: prev.count + 1 }));

        // Refresh global context cache
        await refreshGlobalUsers(true);
        return { success: true, data: newUser };
      } catch (err) {
        const errorMessage = err.message || "Failed to create user";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canCreate, notify]
  );

  /**
   * Update existing user (Admin only)
   */
  const updateUser = useCallback(
    async (userId, userData) => {
      if (!canEdit) {
        notify.error("You do not have permission to update users");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const updatedUser = await usersApi.updateUser(userId, userData);

        // Update local state
        setUsers((prev) =>
          prev.map((user) => (user.id === userId ? updatedUser : user))
        );

        // Refresh global context cache
        await refreshGlobalUsers(true);
        return { success: true, data: updatedUser };
      } catch (err) {
        const errorMessage = err.message || "Failed to update user";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canEdit, notify]
  );

  /**
   * Delete user (Admin only)
   */
  const deleteUser = useCallback(
    async (userId) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete users");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        await usersApi.deleteUser(userId);

        // Remove from local state
        setUsers((prev) => prev.filter((user) => user.id !== userId));
        setPagination((prev) => ({ ...prev, count: prev.count - 1 }));

        // Refresh global context cache
        await refreshGlobalUsers(true);
        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to delete user";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canDelete, notify]
  );

  /**
   * Get user statistics
   */
  const fetchUserStats = useCallback(async () => {
    try {
      const stats = await usersApi.getUserStats();
      return { success: true, data: stats };
    } catch (err) {
      console.warn("Failed to load user stats:", err);
      // Don't show error notification for stats
      return {
        success: false,
        data: {
          total_users: 0,
          active_users: 0,
          under_review: 0,
          approved: 0,
          pending: 0,
        },
      };
    }
  }, []);

  /**
   * Get granular seafarer status counts for the Dashboard Overview
   * Derived from the already-loaded users array to avoid extra API calls.
   *
   * Matches backend values:
   *   user_status: "ON_SITE"  | "VACATION" | "MEDICAL VACATION"
   *   is_blacklisted: true
   */
  const getUserStatusCounts = useCallback(() => {
    const total = users.length;
    const onSite = users.filter(
      (u) => u.user_status === "ON_SITE" || u.user_status === "On Site"
    ).length;
    const onVacation = users.filter(
      (u) => u.user_status === "VACATION" || u.user_status === "Vacation"
    ).length;
    const onMedical = users.filter(
      (u) =>
        u.user_status === "MEDICAL VACATION" ||
        u.user_status === "Medical Vacation"
    ).length;
    const blacklisted = users.filter((u) => u.is_blacklisted === true).length;

    // Recent registrations: users created within the last 30 days
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentRegistrations = users.filter((u) => {
      const createdAt = u.created_at ? new Date(u.created_at) : null;
      return createdAt && createdAt >= thirtyDaysAgo;
    }).length;

    return {
      total,
      onSite,
      onVacation,
      onMedical,
      blacklisted,
      recentRegistrations,
    };
  }, [users]);

  /**
   * Refresh users (reload with current filters)
   */
  const refreshUsers = useCallback(async () => {
    await fetchUsers({ page: pagination.currentPage });
  }, [fetchUsers, pagination.currentPage]);

  return {
    // State
    users,
    loading,
    error,
    pagination,

    // Permissions
    canCreate,
    canEdit,
    canDelete,

    // Methods
    fetchUsers,
    getUserById,
    createUser,
    updateUser,
    deleteUser,
    fetchUserStats,
    getUserStatusCounts,
    refreshUsers,
  };
};

export default useUsers;
