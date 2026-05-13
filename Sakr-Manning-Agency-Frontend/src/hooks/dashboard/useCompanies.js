// services/Dashboard/hooks/useCompanies.js
import { useState, useCallback } from "react";
import { companiesApi } from "../../services/Dashboard/companiesApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { usePermissions } from "./usePermissions";
import { useDashboardData } from "../../components/dashboard/context/DashboardDataContext";

/**
 * Custom hook for managing companies
 */

export const useCompanies = () => {
  const [companies, setCompanies] = useState([]);
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
  const { fetchCompanies: refreshGlobalCompanies } = useDashboardData();

  /**
   * Fetch companies with optional filters
   */
  const fetchCompanies = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);

      try {
        const response = await companiesApi.getCompanies(filters);

        setCompanies(response.companies || []);
        setPagination({
          count: response.count || 0,
          next: response.next || null,
          previous: response.previous || null,
          currentPage: filters.page || 1,
        });

        return { success: true, data: response.companies };
      } catch (err) {
        const errorMessage = err.message || "Failed to load companies";
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
   * Get single company by ID
   */
  const getCompanyById = useCallback(
    async (companyId) => {
      try {
        const company = await companiesApi.getCompanyById(companyId);
        return { success: true, data: company };
      } catch (err) {
        const errorMessage = err.message || "Failed to load company";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [notify]
  );

  /**
   * Create new company (Admin only)
   */
  const createCompany = useCallback(
    async (companyData) => {
      if (!canCreate) {
        notify.error("You do not have permission to create companies");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const newCompany = await companiesApi.createCompany(companyData);

        setCompanies((prev) => [newCompany, ...prev]);
        setPagination((prev) => ({ ...prev, count: prev.count + 1 }));

        // Refresh global context cache
        await refreshGlobalCompanies(true);
        return { success: true, data: newCompany };
      } catch (err) {
        const errorMessage = err.message || "Failed to create company";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canCreate, notify]
  );

  /**
   * Update existing company (Admin only)
   */
  const updateCompany = useCallback(
    async (companyId, companyData) => {
      if (!canEdit) {
        notify.error("You do not have permission to update companies");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const updatedCompany = await companiesApi.updateCompany(
          companyId,
          companyData
        );

        setCompanies((prev) =>
          prev.map((company) =>
            company.id === companyId ? updatedCompany : company
          )
        );

        // Refresh global context cache
        await refreshGlobalCompanies(true);
        return { success: true, data: updatedCompany };
      } catch (err) {
        const errorMessage = err.message || "Failed to update company";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canEdit, notify]
  );

  /**
   * Delete company (Admin only)
   */
  const deleteCompany = useCallback(
    async (companyId) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete companies");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        await companiesApi.deleteCompany(companyId);

        setCompanies((prev) =>
          prev.filter((company) => company.id !== companyId)
        );
        setPagination((prev) => ({ ...prev, count: prev.count - 1 }));

        // Refresh global context cache
        await refreshGlobalCompanies(true);
        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to delete company";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canDelete, notify]
  );

  /**
   * Get company statistics
   */
  const fetchCompanyStats = useCallback(async () => {
    try {
      const stats = await companiesApi.getCompanyStats();
      return { success: true, data: stats };
    } catch (err) {
      console.warn("Failed to load company stats:", err);
      return {
        success: false,
        data: {
          total_companies: 0,
          active_companies: 0,
          inactive_companies: 0,
          total_open_positions: 0,
        },
      };
    }
  }, []);

  /**
   * Refresh companies
   */
  const refreshCompanies = useCallback(async () => {
    await fetchCompanies({ page: pagination.currentPage });
  }, [fetchCompanies, pagination.currentPage]);

  return {
    // State
    companies,
    loading,
    error,
    pagination,

    // Permissions
    canCreate,
    canEdit,
    canDelete,

    // Methods
    fetchCompanies,
    getCompanyById,
    createCompany,
    updateCompany,
    deleteCompany,
    fetchCompanyStats,
    refreshCompanies,
  };
};

export default useCompanies;
