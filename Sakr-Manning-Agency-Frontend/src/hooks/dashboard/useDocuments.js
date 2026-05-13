// hooks/dashboard/useDocuments.js - REFINED VERSION
import { useState, useCallback, useEffect } from "react";
import { documentsApi } from "../../services/Dashboard/documentsApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { usePermissions } from "./usePermissions";

/**
 * Custom hook for managing contracts/documents
 * Handles fetching, creating, updating, deleting contracts
 * Includes permission checks, notifications, and enriched data
 */

export const useDocuments = () => {
  const [contracts, setContracts] = useState([]);
  const [backendStats, setBackendStats] = useState(null);
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
  const { canManageContracts, canView } = usePermissions();

  /**
   * Fetch contracts with optional filters - returns ENRICHED contracts
   */
  const fetchContracts = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);

      try {
        const response = await documentsApi.getEnrichedContracts(filters);

        setContracts(response.contracts || []);
        setPagination({
          count: response.count || 0,
          next: response.next || null,
          previous: response.previous || null,
          currentPage: filters.page || 1,
        });

        return { success: true, data: response.contracts };
      } catch (err) {
        const errorMessage = err.message || "Failed to load contracts";
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
   * Fetch contract statistics from backend
   */
  const fetchContractStats = useCallback(async () => {
    try {
      const stats = await documentsApi.getContractStats();
      setBackendStats(stats);
      return { success: true, data: stats };
    } catch (err) {
      console.warn("Failed to load contract stats:", err);
      return {
        success: false,
        data: {
          signed_contracts: 0,
          pending_signature: 0,
          drafts: 0,
          critical: 0,
          warning: 1,
          notice: 0,
        },
      };
    }
  }, []);

  /**
   * Calculate LOCAL statistics from enriched contracts
   * This matches the UI design categories exactly
   */
  const getLocalStats = useCallback(() => {
    const stats = {
      total: contracts.length,
      signed: 0,
      pending: 0,
      draft: 0,
      expired: 0,
      cancelled: 0,
      critical: 0, // ≤7 days
      warning: 0, // ≤30 days
      notice: 0, // ≤60 days
      active: 0, // >60 days
    };

    contracts.forEach((contract) => {
      // Count by status
      const status = contract.status;
      if (status === "Signed") stats.signed++;
      else if (status === "Pending Signature") stats.pending++;
      else if (status === "Draft") stats.draft++;
      else if (status === "Expired") stats.expired++;
      else if (status === "Cancelled") stats.cancelled++;
      else if (status === "Active") stats.active++;

      // Count by expiry category (for signed contracts only)
      if (status === "Signed" && contract.expiryCategory) {
        if (contract.expiryCategory === "critical") stats.critical++;
        else if (contract.expiryCategory === "warning") stats.warning++;
        else if (contract.expiryCategory === "notice") stats.notice++;
        else if (contract.expiryCategory === "active") stats.active++;
      }
    });

    return stats;
  }, [contracts]);

  /**
   * Get single contract by ID
   */
  const getContractById = useCallback(
    async (contractId) => {
      try {
        const contract = await documentsApi.getContractById(contractId);

        // Enrich the contract
        const enrichedContract = {
          ...contract,
          daysToExpiry: documentsApi.calculateDaysToExpiry(
            contract.sign_off_date
          ),
          expiryCategory: documentsApi.getExpiryCategory(
            documentsApi.calculateDaysToExpiry(contract.sign_off_date)
          ),
          duration: documentsApi.calculateDuration(
            contract.sign_on_date,
            contract.sign_off_date
          ),
        };

        return { success: true, data: enrichedContract };
      } catch (err) {
        const errorMessage = err.message || "Failed to load contract";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [notify]
  );

  /**
   * Create new contract (Admin/HR only)
   */
  const createContract = useCallback(
    async (contractData) => {
      if (!canManageContracts) {
        notify.error("You do not have permission to create contracts");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const newContract = await documentsApi.createContract(contractData);

        // Enrich the new contract
        const enrichedContract = {
          ...newContract,
          daysToExpiry: documentsApi.calculateDaysToExpiry(
            newContract.sign_off_date
          ),
          expiryCategory: documentsApi.getExpiryCategory(
            documentsApi.calculateDaysToExpiry(newContract.sign_off_date)
          ),
          duration: documentsApi.calculateDuration(
            newContract.sign_on_date,
            newContract.sign_off_date
          ),
        };

        setContracts((prev) => [enrichedContract, ...prev]);
        setPagination((prev) => ({ ...prev, count: prev.count + 1 }));

        await fetchContractStats();
        return { success: true, data: enrichedContract };
      } catch (err) {
        const errorMessage = err.message || "Failed to create contract";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canManageContracts, notify]
  );

  /**
   * Update existing contract (Admin/HR only)
   */
  const updateContract = useCallback(
    async (contractId, contractData) => {
      if (!canManageContracts) {
        notify.error("You do not have permission to update contracts");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const updatedContract = await documentsApi.updateContract(
          contractId,
          contractData
        );

        // Enrich the updated contract
        const enrichedContract = {
          ...updatedContract,
          daysToExpiry: documentsApi.calculateDaysToExpiry(
            updatedContract.sign_off_date
          ),
          expiryCategory: documentsApi.getExpiryCategory(
            documentsApi.calculateDaysToExpiry(updatedContract.sign_off_date)
          ),
          duration: documentsApi.calculateDuration(
            updatedContract.sign_on_date,
            updatedContract.sign_off_date
          ),
        };

        setContracts((prev) =>
          prev.map((contract) =>
            contract.id === contractId ? enrichedContract : contract
          )
        );

        await fetchContractStats();
        return { success: true, data: enrichedContract };
      } catch (err) {
        const errorMessage = err.message || "Failed to update contract";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canManageContracts, notify]
  );

  /**
   * Delete contract (Admin/HR only)
   */
  const deleteContract = useCallback(
    async (contractId) => {
      if (!canManageContracts) {
        notify.error("You do not have permission to delete contracts");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        await documentsApi.deleteContract(contractId);

        setContracts((prev) =>
          prev.filter((contract) => contract.id !== contractId)
        );
        setPagination((prev) => ({ ...prev, count: prev.count - 1 }));

        await fetchContractStats();
        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to delete contract";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canManageContracts, notify]
  );

  /**
   * Filter contracts by status
   */
  const filterByStatus = useCallback(
    (status) => {
      if (!status || status === "all") {
        return contracts;
      }
      return contracts.filter((contract) => contract.status === status);
    },
    [contracts]
  );

  /**
   * Filter contracts by expiry category
   */
  const filterByExpiryCategory = useCallback(
    (category) => {
      if (!category || category === "all") {
        return contracts;
      }
      return contracts.filter(
        (contract) => contract.expiryCategory === category
      );
    },
    [contracts]
  );

  /**
   * Get contracts expiring within specified days
   */
  const getExpiringContracts = useCallback(
    (days = 30) => {
      return contracts.filter((contract) => {
        return (
          contract.daysToExpiry !== null &&
          contract.daysToExpiry >= 0 &&
          contract.daysToExpiry <= days &&
          contract.status === "Signed"
        );
      });
    },
    [contracts]
  );

  /**
   * Refresh contracts (reload with current filters)
   */
  const refreshContracts = useCallback(async () => {
    await fetchContracts({ page: pagination.currentPage });
    await fetchContractStats();
  }, [fetchContracts, fetchContractStats, pagination.currentPage]);

  // Auto-fetch stats when contracts change
  useEffect(() => {
    if (contracts.length > 0 && !backendStats) {
      fetchContractStats();
    }
  }, [contracts.length, backendStats, fetchContractStats]);

  return {
    // State
    contracts,
    loading,
    error,
    pagination,
    backendStats,

    // Permissions
    canManageContracts,
    canView,

    // Methods
    fetchContracts,
    getContractById,
    createContract,
    updateContract,
    deleteContract,
    fetchContractStats,
    refreshContracts,

    // Filtering
    filterByStatus,
    filterByExpiryCategory,
    getExpiringContracts,

    // Stats
    getLocalStats,
    backendStats,
    fetchContractStats,
  };
};

export default useDocuments;
