// hooks/dashboard/useFinance.js
import { useState, useCallback } from "react";
import { financeApi } from "../../services/Dashboard/financeApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { usePermissions } from "./usePermissions";

/**
 * Custom hook for managing finance records
 */

export const useFinance = () => {
  const [records, setRecords] = useState([]);
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
  const { canEdit, canDelete, canCreate, canManageFinance } = usePermissions();

  /**
   * Fetch finance records with optional filters
   */
  const fetchRecords = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);

      try {
        const response = await financeApi.getFinanceRecords(filters);

        setRecords(response.records || []);
        setPagination({
          count: response.count || 0,
          next: response.next || null,
          previous: response.previous || null,
          currentPage: filters.page || 1,
        });

        return { success: true, data: response.records };
      } catch (err) {
        const errorMessage = err.message || "Failed to load finance records";
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
   * Get single finance record by ID
   */
  const getRecordById = useCallback(
    async (recordId) => {
      try {
        const record = await financeApi.getFinanceRecordById(recordId);
        return { success: true, data: record };
      } catch (err) {
        const errorMessage = err.message || "Failed to load finance record";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [notify]
  );

  /**
   * Create new finance record
   */
  const createRecord = useCallback(
    async (recordData) => {
      if (!canCreate && !canManageFinance) {
        notify.error("You do not have permission to create finance records");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const newRecord = await financeApi.createFinanceRecord(recordData);

        setRecords((prev) => [newRecord, ...prev]);
        setPagination((prev) => ({ ...prev, count: prev.count + 1 }));

        return { success: true, data: newRecord };
      } catch (err) {
        const errorMessage = err.message || "Failed to create finance record";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canCreate, canManageFinance, notify]
  );

  /**
   * Update existing finance record
   */
  const updateRecord = useCallback(
    async (recordId, recordData) => {
      if (!canEdit && !canManageFinance) {
        notify.error("You do not have permission to update finance records");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const updatedRecord = await financeApi.updateFinanceRecord(
          recordId,
          recordData
        );

        setRecords((prev) =>
          prev.map((record) =>
            record.id === recordId ? updatedRecord : record
          )
        );

        return { success: true, data: updatedRecord };
      } catch (err) {
        const errorMessage = err.message || "Failed to update finance record";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canEdit, canManageFinance, notify]
  );

  /**
   * Delete finance record
   */
  const deleteRecord = useCallback(
    async (recordId) => {
      if (!canDelete && !canManageFinance) {
        notify.error("You do not have permission to delete finance records");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        await financeApi.deleteFinanceRecord(recordId);

        setRecords((prev) => prev.filter((record) => record.id !== recordId));
        setPagination((prev) => ({ ...prev, count: prev.count - 1 }));

        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to delete finance record";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canDelete, canManageFinance, notify]
  );

  /**
   * Calculate finance (server-side)
   * Used before saving to get accurate calculation
   */
  const calculateFinance = useCallback(
    async (data) => {
      try {
        const calculation = await financeApi.calculateFinance(data);
        return { success: true, data: calculation };
      } catch (err) {
        const errorMessage = err.message || "Failed to calculate finance";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [notify]
  );

  /**
   * Client-side calculation preview (instant feedback)
   */
  const calculatePreview = useCallback((startDate, endDate, dailyRate) => {
    return financeApi.calculateClientSide(startDate, endDate, dailyRate);
  }, []);

  /**
   * Get finance statistics
   */
  const fetchStats = useCallback(async () => {
    try {
      const stats = await financeApi.getFinanceStats();
      return { success: true, data: stats };
    } catch (err) {
      console.warn("Failed to load finance stats:", err);
      return {
        success: false,
        data: {
          total_records: 0,
          total_money: "0.00",
          average_daily_rate: "0.00",
          this_month_total: "0.00",
        },
      };
    }
  }, []);

  /**
   * Export finance records to CSV
   */
  const exportRecords = useCallback(
    async (filters = {}) => {
      try {
        const blob = await financeApi.exportFinanceRecords(filters);

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `finance_records_${new Date().toISOString().split("T")[0]
          }.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to export finance records";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [notify]
  );

  /**
   * Refresh records (reload with current filters)
   */
  const refreshRecords = useCallback(async () => {
    await fetchRecords({ page: pagination.currentPage });
  }, [fetchRecords, pagination.currentPage]);

  return {
    // State
    records,
    loading,
    error,
    pagination,

    // Permissions
    canCreate: canCreate || canManageFinance,
    canEdit: canEdit || canManageFinance,
    canDelete: canDelete || canManageFinance,

    // Methods
    fetchRecords,
    getRecordById,
    createRecord,
    updateRecord,
    deleteRecord,
    calculateFinance,
    calculatePreview,
    fetchStats,
    exportRecords,
    refreshRecords,
  };
};

export default useFinance;
