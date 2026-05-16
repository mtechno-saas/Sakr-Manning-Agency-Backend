// hooks/dashboard/useVacancies.js
import { useState, useCallback } from "react";
import { vacanciesApi } from "../../services/Dashboard/vacanciesApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { usePermissions } from "./usePermissions";

/**
 * Custom hook for managing vacancies
 *
 * Permission model (mirrors the company table):
 *   - All authenticated users  → read (GET list / detail)
 *   - Admin only               → create, update, delete
 */
export const useVacancies = () => {
  const [vacancies, setVacancies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
  });

  const { notify } = useNotification();
  const { canEdit, canDelete, canCreate } = usePermissions();

  // ─── READ ──────────────────────────────────────────────────────────────────

  /**
   * Fetch vacancies with optional filters
   * @param {Object} filters - { status, company, rank, search, page, page_size }
   */
  const fetchVacancies = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);

      try {
        const queryFilters = { page_size: 50, ...filters };
        const response = await vacanciesApi.getVacancies(queryFilters);

        setVacancies(response.vacancies || []);
        setPagination({
          count:       response.count    || 0,
          next:        response.next     || null,
          previous:    response.previous || null,
          currentPage: queryFilters.page || 1,
          pageSize:    queryFilters.page_size || 50,
        });

        return { success: true, data: response.vacancies };
      } catch (err) {
        const msg = err.message || "Failed to load vacancies";
        setError(msg);
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  /**
   * Get single vacancy by ID
   */
  const getVacancyById = useCallback(
    async (vacancyId) => {
      try {
        const vacancy = await vacanciesApi.getVacancyById(vacancyId);
        return { success: true, data: vacancy };
      } catch (err) {
        const msg = err.message || "Failed to load vacancy";
        notify.error(msg);
        return { success: false, error: msg };
      }
    },
    [notify]
  );

  // ─── CREATE ────────────────────────────────────────────────────────────────

  /**
   * Create a new vacancy (Admin only)
   */
  const createVacancy = useCallback(
    async (vacancyData) => {
      if (!canCreate) {
        notify.error("You do not have permission to create vacancies");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const newVacancy = await vacanciesApi.createVacancy(vacancyData);

        setVacancies((prev) => [newVacancy, ...prev]);
        setPagination((prev) => ({ ...prev, count: prev.count + 1 }));

        return { success: true, data: newVacancy };
      } catch (err) {
        const msg = err.message || "Failed to create vacancy";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [canCreate, notify]
  );

  // ─── UPDATE ────────────────────────────────────────────────────────────────

  /**
   * Update an existing vacancy (Admin only)
   */
  const updateVacancy = useCallback(
    async (vacancyId, vacancyData) => {
      if (!canEdit) {
        notify.error("You do not have permission to update vacancies");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const updated = await vacanciesApi.updateVacancy(vacancyId, vacancyData);

        setVacancies((prev) =>
          prev.map((v) => (v.id === vacancyId ? updated : v))
        );

        return { success: true, data: updated };
      } catch (err) {
        const msg = err.message || "Failed to update vacancy";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [canEdit, notify]
  );

  // ─── DELETE ────────────────────────────────────────────────────────────────

  /**
   * Delete a vacancy (Admin only)
   */
  const deleteVacancy = useCallback(
    async (vacancyId) => {
      if (!canDelete) {
        notify.error("You do not have permission to delete vacancies");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        await vacanciesApi.deleteVacancy(vacancyId);

        setVacancies((prev) => prev.filter((v) => v.id !== vacancyId));
        setPagination((prev) => ({ ...prev, count: prev.count - 1 }));

        return { success: true };
      } catch (err) {
        const msg = err.message || "Failed to delete vacancy";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [canDelete, notify]
  );

  // ─── STATS ─────────────────────────────────────────────────────────────────

  /**
   * Fetch vacancy statistics (safe – never throws)
   */
  const fetchVacancyStats = useCallback(async () => {
    try {
      const stats = await vacanciesApi.getVacancyStats();
      return { success: true, data: stats };
    } catch (err) {
      console.warn("Failed to load vacancy stats:", err);
      return {
        success: false,
        data: {
          total_vacancies:  0,
          open_vacancies:   0,
          closed_vacancies: 0,
        },
      };
    }
  }, []);

  // ─── REFRESH ───────────────────────────────────────────────────────────────

  const refreshVacancies = useCallback(async () => {
    await fetchVacancies({ page: pagination.currentPage });
  }, [fetchVacancies, pagination.currentPage]);

  // ─── RETURN ────────────────────────────────────────────────────────────────

  return {
    // State
    vacancies,
    loading,
    error,
    pagination,

    // Permissions (expose so UI can conditionally render admin controls)
    canCreate,
    canEdit,
    canDelete,

    // Methods
    fetchVacancies,
    getVacancyById,
    createVacancy,
    updateVacancy,
    deleteVacancy,
    fetchVacancyStats,
    refreshVacancies,
  };
};

export default useVacancies;
