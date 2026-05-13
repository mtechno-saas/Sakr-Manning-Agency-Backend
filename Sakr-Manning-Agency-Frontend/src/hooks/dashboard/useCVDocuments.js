// hooks/dashboard/useCVDocuments.js
// Lightweight hook for the CVs tab — wraps cvSubmissionsApi
import { useState, useCallback } from "react";
import { cvSubmissionsApi } from "../../services/Dashboard/cvSubmissionsApi";
import useNotification from "../../components/dashboard/hooks/useNotification";

export const useCVDocuments = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    pageSize: 50,
  });

  const { notify } = useNotification();

  /**
   * Fetch CV documents with optional filters
   * @param {Object} filters - { page, search, status }
   */
  const fetchDocuments = useCallback(
    async (filters = {}) => {
      setLoading(true);
      try {
        const response = await cvSubmissionsApi.getDocuments(filters);

        // Handle both paginated { results, count } and flat array responses
        const docs = response.results || (Array.isArray(response) ? response : []);
        const count = response.count ?? docs.length;

        setDocuments(docs);
        setPagination((prev) => ({
          ...prev,
          count,
          next: response.next || null,
          previous: response.previous || null,
          currentPage: filters.page || 1,
        }));

        return { success: true, data: docs };
      } catch (err) {
        const msg = err.message || "Failed to load CV documents";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  /**
   * Change document status (Pending → Active → Blacklist)
   */
  const setDocumentStatus = useCallback(
    async (id, status) => {
      try {
        const updated = await cvSubmissionsApi.setDocumentStatus(id, status);
        // Update in-place
        setDocuments((prev) =>
          prev.map((d) => (d.id === id ? { ...d, ...updated } : d))
        );
        return { success: true, data: updated };
      } catch (err) {
        const msg = err.message || "Failed to update status";
        notify.error(msg);
        return { success: false, error: msg };
      }
    },
    [notify]
  );

  /**
   * Download a CV file
   */
  const downloadDocument = useCallback(
    async (id, filename) => {
      try {
        const blob = await cvSubmissionsApi.downloadDocument(id);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename || `CV_${id}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        notify.error("Failed to download CV");
        console.error(err);
      }
    },
    [notify]
  );

  /**
   * Create a new CV document (Admin/HR/Recruiter only)
   * @param {FormData} formData - name, email, phone_number, position, status, file
   */
  const createDocument = useCallback(
    async (formData) => {
      setLoading(true);
      try {
        const result = await cvSubmissionsApi.createDocument(formData);
        // Refresh documents to include new entry
        await fetchDocuments({ page: 1 });
        return { success: true, data: result };
      } catch (err) {
        const msg = err.message || "Failed to create CV";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [fetchDocuments, notify]
  );

  /**
   * Update an existing CV document (Admin/HR/Recruiter only)
   * @param {number} id - Document ID
   * @param {FormData|Object} data - Changed fields
   */
  const updateDocument = useCallback(
    async (id, data) => {
      setLoading(true);
      try {
        const updated = await cvSubmissionsApi.updateDocument(id, data);
        // Update in-place
        setDocuments((prev) =>
          prev.map((d) => (d.id === id ? { ...d, ...updated } : d))
        );
        return { success: true, data: updated };
      } catch (err) {
        const msg = err.message || "Failed to update CV";
        notify.error(msg);
        return { success: false, error: msg };
      } finally {
        setLoading(false);
      }
    },
    [notify]
  );

  /**
   * Delete a CV document
   */
  const deleteDocument = useCallback(
    async (id) => {
      try {
        await cvSubmissionsApi.deleteDocument(id);
        setDocuments((prev) => prev.filter((d) => d.id !== id));
        setPagination((prev) => ({ ...prev, count: prev.count - 1 }));
        return { success: true };
      } catch (err) {
        const msg = err.message || "Failed to delete CV";
        notify.error(msg);
        return { success: false, error: msg };
      }
    },
    [notify]
  );

  return {
    documents,
    loading,
    pagination,
    fetchDocuments,
    setDocumentStatus,
    downloadDocument,
    createDocument,
    updateDocument,
    deleteDocument,
  };
};

export default useCVDocuments;
