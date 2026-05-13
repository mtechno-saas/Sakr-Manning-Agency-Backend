// hooks/dashboard/useRanks.js
import { useState, useCallback } from "react";
import { ranksApi } from "../../services/Dashboard/usersApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { useDashboardData } from "../../components/dashboard/context/DashboardDataContext";

/**
 * Hook for managing Rank Codes (Core)
 */
export const useRanks = () => {
  const [ranks, setRanks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { notify } = useNotification();
  const { fetchRanks: refreshGlobalRanks } = useDashboardData();

  const fetchRanks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ranksApi.getRanks();
      setRanks(data);
      return { success: true, data };
    } catch (err) {
      const msg = err.message || "Failed to load ranks";
      setError(msg);
      notify.error(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, [notify]);

  const createRank = useCallback(async (data) => {
    setLoading(true);
    try {
      const created = await ranksApi.createRank(data);
      setRanks((prev) => [...prev, created]);

      // Refresh global context cache
      await refreshGlobalRanks(true);
      return { success: true, data: created };
    } catch (err) {
      const msg = err.message || "Failed to create rank";
      notify.error(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, [notify]);

  const updateRank = useCallback(async (id, data) => {
    setLoading(true);
    try {
      const updated = await ranksApi.updateRank(id, data);
      setRanks((prev) => prev.map((r) => (r.id === id ? updated : r)));

      // Refresh global context cache
      await refreshGlobalRanks(true);
      return { success: true, data: updated };
    } catch (err) {
      const msg = err.message || "Failed to update rank";
      notify.error(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, [notify]);

  const deleteRank = useCallback(async (id) => {
    setLoading(true);
    try {
      await ranksApi.deleteRank(id);
      setRanks((prev) => prev.filter((r) => r.id !== id));

      // Refresh global context cache
      await refreshGlobalRanks(true);
      return { success: true };
    } catch (err) {
      const msg = err.message || "Failed to delete rank";
      notify.error(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, [notify]);

  return {
    ranks,
    loading,
    error,
    fetchRanks,
    createRank,
    updateRank,
    deleteRank,
  };
};

export default useRanks;
