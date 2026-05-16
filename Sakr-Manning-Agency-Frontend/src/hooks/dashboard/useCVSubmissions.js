// hooks/dashboard/useCVSubmissions.js
import { useState, useCallback } from "react";
import { cvSubmissionsApi } from "../../services/Dashboard/cvSubmissionsApi";
import useNotification from "../../components/dashboard/hooks/useNotification";

/**
 * Custom hook for managing CV submissions in the dashboard
 * Data source: CVSubmission model (Section 4)
 *
 * Statuses: Pending, Under Review, Interviewed, Shortlisted, Approved, Hired, Rejected
 */
export const useCVSubmissions = () => {
  const [submissions, setSubmissions] = useState([]);
  const [stats, setStats] = useState(null);
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

  /**
   * Fetch CV submissions with optional filters
   */
  const fetchSubmissions = useCallback(
    async (filters = {}) => {
      setLoading(true);
      setError(null);
      try {
        const queryFilters = { page_size: 50, ...filters };
        const response = await cvSubmissionsApi.getSubmissions(queryFilters);

        // Handle paginated or flat response
        if (response.results) {
          setSubmissions(response.results);
          setPagination({
            count: response.count || 0,
            next: response.next || null,
            previous: response.previous || null,
            currentPage: queryFilters.page || 1,
            pageSize: queryFilters.page_size || 50,
          });
          return { success: true, data: response.results };
        }

        // Flat array fallback
        const docs = Array.isArray(response) ? response : [];
        setSubmissions(docs);
        setPagination((prev) => ({ ...prev, count: docs.length }));
        return { success: true, data: docs };
      } catch (err) {
        const errorMessage = err.message || "Failed to load CV submissions";
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
   * Alias for fetchSubmissions to support existing components
   */
  const fetchDocuments = useCallback((filters) => fetchSubmissions(filters), [fetchSubmissions]);

  /**
   * Update submission status (Pipeline Move)
   */
  const updateStatus = useCallback(async (id, status) => {
    setLoading(true);
    try {
      const response = await cvSubmissionsApi.updateSubmissionStatus(id, status);
      
      // Update local state to reflect change immediately
      setSubmissions(prev => prev.map(s => s.id === id ? { ...s, status: response.status || status } : s));
      
      return { success: true, data: response };
    } catch (err) {
      const errorMessage = err.message || "Failed to update status";
      notify.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, [notify]);

  /**
   * Create a new CV submission (Admin/HR path)
   */
  const createSubmission = useCallback(async (data) => {
    setLoading(true);
    try {
      const response = await cvSubmissionsApi.createSubmission(data);
      await fetchSubmissions({ page: 1 });
      return { success: true, data: response };
    } catch (err) {
       notify.error(err.message || "Failed to create application");
       return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, [fetchSubmissions, notify]);
  
  // Wait, I need a proper createSubmission in the API service.
  // I'll update the hook to call the API once I've updated the API service too.
  
  /**
   * Update an existing CV submission details
   */
  const updateSubmission = useCallback(async (id, data) => {
    setLoading(true);
    try {
      const result = await cvSubmissionsApi.updateSubmission(id, data);
      setSubmissions(prev => prev.map(s => s.id === id ? { ...s, ...result } : s));
      return { success: true, data: result };
    } catch (err) {
      notify.error(err.message || "Failed to update application");
      return { success: false, error: err.message };
    } finally {
       setLoading(false);
    }
  }, [notify]);

  /**
   * Delete a CV submission
   */
  const deleteSubmission = useCallback(async (id) => {
    setLoading(true);
    try {
      await cvSubmissionsApi.deleteSubmission(id);
      setSubmissions(prev => prev.filter(s => s.id !== id));
      setPagination(prev => ({ ...prev, count: Math.max(0, prev.count - 1) }));
      return { success: true };
    } catch (err) {
      notify.error(err.message || "Failed to delete application");
      return { success: false, error: err.message };
    } finally {
      setLoading(false);
    }
  }, [notify]);

  /**
   * Fetch a single submission by ID (full rich payload)
   */
  const getSubmissionById = useCallback(async (id) => {
    setLoading(true);
    try {
      const data = await cvSubmissionsApi.getSubmissionById(id);
      return { success: true, data };
    } catch (err) {
      const msg = err.message || "Failed to load submission details";
      notify.error(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, [notify]);

  const fetchCVStats = useCallback(async () => {
    try {
      const data = await cvSubmissionsApi.getCVSubmissionStats();
      setStats(data);
      return { success: true, data };
    } catch (err) {
      console.warn("Failed to load CV submission stats:", err);
      return {
        success: false,
        data: { total: 0, pending: 0, under_review: 0, approved: 0 },
      };
    }
  }, []);

  const getLocalCounts = useCallback(() => {
    const total = submissions.length;
    const countsByStatus = submissions.reduce((acc, s) => {
        acc[s.status] = (acc[s.status] || 0) + 1;
        return acc;
    }, {});
    return { total, ...countsByStatus };
  }, [submissions]);

  return {
    submissions,
    stats,
    loading,
    error,
    pagination,
    fetchSubmissions,
    fetchDocuments,
    getSubmissionById,
    updateStatus,
    createSubmission,
    updateSubmission,
    deleteSubmission,
    fetchCVStats,
    getLocalCounts,
  };
};

export default useCVSubmissions;
