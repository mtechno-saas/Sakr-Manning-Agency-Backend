// hooks/dashboard/useJobOrders.js
import { useState, useCallback } from "react";
import { jobOrdersApi } from "../../services/Dashboard/jobOrdersApi";
import useNotification from "../../components/dashboard/hooks/useNotification";

/**
 * Custom hook for managing Job Orders in the dashboard
 * Data source: /api/companies/job-orders/
 *
 * KPIs:
 * - Open Positions: jobOrders with status = "Open"
 */
export const useJobOrders = () => {
  const [jobOrders, setJobOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
  });

  const { notify } = useNotification();

  // ── Fetch ──────────────────────────────────────────────────────────────────
  const fetchJobOrders = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);
      try {
        const response = await jobOrdersApi.getJobOrders(filters);
        setJobOrders(response.jobOrders || []);
        setPagination({
          count: response.count || 0,
          next: response.next || null,
          previous: response.previous || null,
          currentPage: filters.page || 1,
        });
        return { success: true, data: response.jobOrders };
      } catch (err) {
        const msg = err.message || "Failed to load job orders";
        setError(msg);
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  // ── Create ─────────────────────────────────────────────────────────────────
  const createJobOrder = useCallback(
    async (data) => {
      setLoading(true);
      try {
        const created = await jobOrdersApi.createJobOrder(data);
        setJobOrders((prev) => [created, ...prev]);
        notify.success("Job order created successfully");
        return { success: true, data: created };
      } catch (err) {
        const msg = err.message || "Failed to create job order";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  // ── Update ─────────────────────────────────────────────────────────────────
  const updateJobOrder = useCallback(
    async (id, data) => {
      setLoading(true);
      try {
        const updated = await jobOrdersApi.updateJobOrder(id, data);
        setJobOrders((prev) =>
          prev.map((jo) => (jo.id === id ? updated : jo))
        );
        notify.success("Job order updated successfully");
        return { success: true, data: updated };
      } catch (err) {
        const msg = err.message || "Failed to update job order";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  // ── Delete ─────────────────────────────────────────────────────────────────
  const deleteJobOrder = useCallback(
    async (id) => {
      setLoading(true);
      try {
        await jobOrdersApi.deleteJobOrder(id);
        setJobOrders((prev) => prev.filter((jo) => jo.id !== id));
        notify.success("Job order deleted successfully");
        return { success: true };
      } catch (err) {
        const msg = err.message || "Failed to delete job order";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  // ── Refresh ────────────────────────────────────────────────────────────────
  const refreshJobOrders = useCallback(async () => {
    await fetchJobOrders({ page: pagination.currentPage });
  }, [fetchJobOrders, pagination.currentPage]);

  return {
    // State
    jobOrders,
    loading,
    error,
    pagination,

    // Methods
    fetchJobOrders,
    createJobOrder,
    updateJobOrder,
    deleteJobOrder,
    refreshJobOrders,
  };
};

export default useJobOrders;
