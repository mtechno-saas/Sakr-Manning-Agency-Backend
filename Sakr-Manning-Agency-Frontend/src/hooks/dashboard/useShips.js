// services/Dashboard/hooks/useShips.js
import { useState, useCallback } from "react";
import { shipsApi } from "../../services/Dashboard/shipsApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { usePermissions } from "./usePermissions";
import { useDashboardData } from "../../components/dashboard/context/DashboardDataContext";

/**
 * Custom hook for managing ships
 */

export const useShips = () => {
  const [ships, setShips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    pageSize: 50,
  });

  const { notify } = useNotification();
  const { canEdit, canDelete, canCreate } = usePermissions();
  const { fetchShips: refreshGlobalShips } = useDashboardData();

  /**
   * Fetch ships with optional filters
   */
  const fetchShips = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);

      try {
        const response = await shipsApi.getShips(filters);

        setShips(response.ships || []);
        setPagination({
          count: response.count || 0,
          next: response.next || null,
          previous: response.previous || null,
          currentPage: filters.page || 1,
        });

        return { success: true, data: response.ships };
      } catch (err) {
        const errorMessage = err.message || "Failed to load ships";
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
   * Get single ship by ID
   */
  const getShipById = useCallback(
    async (shipId) => {
      try {
        const ship = await shipsApi.getShipById(shipId);
        return { success: true, data: ship };
      } catch (err) {
        const errorMessage = err.message || "Failed to load ship";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [notify]
  );

  /**
   * Create new ship (Admin only)
   */
  const createShip = useCallback(
    async (shipData) => {
      if (!canCreate) {
        notify.error("You do not have permission to create ships");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const newShip = await shipsApi.createShip(shipData);

        setShips((prev) => [newShip, ...prev]);
        setPagination((prev) => ({ ...prev, count: prev.count + 1 }));

        // Refresh global context cache
        await refreshGlobalShips(true);
        return { success: true, data: newShip };
      } catch (err) {
        const errorMessage = err.message || "Failed to create ship";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canCreate, notify]
  );

  /**
   * Update existing ship (Admin only)
   */
  const updateShip = useCallback(
    async (shipId, shipData) => {
      if (!canEdit) {
        notify.error("You do not have permission to update ships");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const updatedShip = await shipsApi.updateShip(shipId, shipData);

        setShips((prev) =>
          prev.map((ship) => (ship.id === shipId ? updatedShip : ship))
        );

        // Refresh global context cache
        await refreshGlobalShips(true);
        return { success: true, data: updatedShip };
      } catch (err) {
        const errorMessage = err.message || "Failed to update ship";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canEdit, notify]
  );

  /**
   * Delete ship (Admin only)
   */
  const deleteShip = useCallback(
    async (shipId) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete ships");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        await shipsApi.deleteShip(shipId);

        setShips((prev) => prev.filter((ship) => ship.id !== shipId));
        setPagination((prev) => ({ ...prev, count: prev.count - 1 }));

        // Refresh global context cache
        await refreshGlobalShips(true);
        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to delete ship";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canDelete, notify]
  );

  /**
   * Assign user to ship
   */
  const assignUser = useCallback(
    async (shipId, userId) => {
      if (!canEdit) {
        notify.error("You do not have permission to assign crew");
        return { success: false, error: "Permission denied" };
      }

      try {
        await shipsApi.assignUserToShip(shipId, userId);
        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to assign user";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [canEdit, notify]
  );

  /**
   * Remove user from ship
   */
  const unassignUser = useCallback(
    async (shipId, userId) => {
      if (!canEdit) {
        notify.error("You do not have permission to remove crew");
        return { success: false, error: "Permission denied" };
      }

      try {
        await shipsApi.unassignUserFromShip(shipId, userId);
        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to remove user";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [canEdit, notify]
  );

  /**
   * Refresh ships
   */
  const refreshShips = useCallback(async () => {
    await fetchShips({ page: pagination.currentPage });
  }, [fetchShips, pagination.currentPage]);

  return {
    // State
    ships,
    loading,
    error,
    pagination,

    // Permissions
    canCreate,
    canEdit,
    canDelete,

    // Methods
    fetchShips,
    getShipById,
    createShip,
    updateShip,
    deleteShip,
    assignUser,
    unassignUser,
    refreshShips,
  };
};

export default useShips;
