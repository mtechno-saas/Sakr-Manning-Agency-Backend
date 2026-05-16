// hooks/dashboard/useInterviews.js
import { useState, useCallback } from "react";
import { interviewsApi } from "../../services/Dashboard/interviewsApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { usePermissions } from "./usePermissions";

/**
 * Custom hook for managing interviews
 * Handles fetching, creating, updating, deleting interviews
 * Includes permission checks and notifications
 */
export const useInterviews = () => {
  const [interviews, setInterviews] = useState([]);
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
  const { canEdit, canDelete, canScheduleInterviews } = usePermissions();

  /**
   * Fetch interviews with optional filters
   */
  const fetchInterviews = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);

      try {
        const response = await interviewsApi.getInterviews(filters);
        setInterviews(response.interviews || []);
        setPagination({
          count: response.count || 0,
          next: response.next || null,
          previous: response.previous || null,
          currentPage: filters.page || 1,
        });

        return { success: true, data: response.interviews };
      } catch (err) {
        const errorMessage = err.message || "Failed to load interviews";
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
   * Get single interview by ID
   */
  const getInterviewById = useCallback(
    async (interviewId) => {
      try {
        const interview = await interviewsApi.getInterviewById(interviewId);
        return { success: true, data: interview };
      } catch (err) {
        const errorMessage = err.message || "Failed to load interview";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      }
    },
    [notify]
  );

  /**
   * Create new interview
   */
  const createInterview = useCallback(
    async (interviewData) => {
      if (!canScheduleInterviews) {
        notify.error("You do not have permission to schedule interviews");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const newInterview = await interviewsApi.createInterview(interviewData);

        setInterviews((prev) => [newInterview, ...prev]);
        setPagination((prev) => ({ ...prev, count: prev.count + 1 }));

        return { success: true, data: newInterview };
      } catch (err) {
        const errorMessage = err.message || "Failed to schedule interview";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canScheduleInterviews, notify]
  );

  /**
   * Update existing interview
   */
  const updateInterview = useCallback(
    async (interviewId, interviewData) => {
      if (!canEdit && !canScheduleInterviews) {
        notify.error("You do not have permission to update interviews");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        const updatedInterview = await interviewsApi.updateInterview(
          interviewId,
          interviewData
        );

        setInterviews((prev) =>
          prev.map((interview) =>
            interview.id === interviewId ? updatedInterview : interview
          )
        );

        return { success: true, data: updatedInterview };
      } catch (err) {
        const errorMessage = err.message || "Failed to update interview";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canEdit, canScheduleInterviews, notify]
  );

  /**
   * Delete interview
   */
  const deleteInterview = useCallback(
    async (interviewId) => {
      if (!canDelete && !canScheduleInterviews) {
        notify.error("You do not have permission to delete interviews");
        return { success: false, error: "Permission denied" };
      }

      setLoading(true);

      try {
        await interviewsApi.deleteInterview(interviewId);

        setInterviews((prev) =>
          prev.filter((interview) => interview.id !== interviewId)
        );
        setPagination((prev) => ({ ...prev, count: prev.count - 1 }));

        return { success: true };
      } catch (err) {
        const errorMessage = err.message || "Failed to delete interview";
        notify.error(errorMessage);
        return { success: false, error: errorMessage };
      } finally {
        setLoading(false);
      }
    },
    [canDelete, canScheduleInterviews, notify]
  );

  /**
   * Get interview statistics
   */
  const fetchInterviewStats = useCallback(async () => {
    try {
      const stats = await interviewsApi.getInterviewStats();
      return { success: true, data: stats };
    } catch (err) {
      console.warn("Failed to load interview stats:", err);
      return {
        success: false,
        data: {
          total_interviews: 0,
          scheduled: 0,
          completed: 0,
          cancelled: 0,
          today: 0,
          this_week: 0,
          pending: 0,
        },
      };
    }
  }, []);

  /**
   * Get calendar view
   */
  const fetchInterviewCalendar = useCallback(async (params = {}) => {
    try {
      const calendar = await interviewsApi.getInterviewCalendar(params);
      return { success: true, data: calendar };
    } catch (err) {
      console.warn("Failed to load interview calendar:", err);
      return { success: false, data: [] };
    }
  }, []);

  /**
   * Refresh interviews (reload with current filters)
   */
  const refreshInterviews = useCallback(async () => {
    await fetchInterviews({ page: pagination.currentPage });
  }, [fetchInterviews, pagination.currentPage]);

  return {
    // State
    interviews,
    loading,
    error,
    pagination,

    // Permissions
    canScheduleInterviews,
    canEdit,
    canDelete,

    // Methods
    fetchInterviews,
    getInterviewById,
    createInterview,
    updateInterview,
    deleteInterview,
    fetchInterviewStats,
    fetchInterviewCalendar,
    refreshInterviews,
  };
};

export default useInterviews;
