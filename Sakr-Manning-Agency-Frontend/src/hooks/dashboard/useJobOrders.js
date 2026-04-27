// src/hooks/dashboard/useJobOrders.js
import { useState, useCallback } from "react";
import { jobOrdersApi } from "../../services/Dashboard/jobOrdersApi";
import useNotification from "../../components/dashboard/hooks/useNotification";
import { usePermissions } from "./usePermissions";

/**
 * Custom hook for managing Job Orders and Positions
 */
export const useJobOrders = () => {
    const [jobOrders, setJobOrders] = useState([]);
    const [loading, setLoading] = useState(false);
    const [pagination, setPagination] = useState({
        count: 0,
        next: null,
        previous: null,
        currentPage: 1
    });
    const { notify } = useNotification();
    const { canEdit, canDelete, canCreate } = usePermissions();

    // ─── JOB ORDERS ─────────────────────────────────────────────────────────

    const fetchJobOrders = useCallback(async (filters = {}) => {
        setLoading(true);
        try {
            const data = await jobOrdersApi.getJobOrders(filters);
            
            // Handle both raw array and paginated response { results, count, ... }
            const list = Array.isArray(data) ? data : (data.results || data.job_orders || []);
            
            setJobOrders(list);
            
            if (!Array.isArray(data)) {
                setPagination({
                    count: data.count || list.length,
                    next: data.next || null,
                    previous: data.previous || null,
                    currentPage: filters.page || 1
                });
            } else {
                setPagination(prev => ({ ...prev, count: data.length, currentPage: filters.page || 1 }));
            }
            
            return { success: true, data: list };
        } catch (err) {
            const msg = err.message || "Failed to load job orders";
            notify.error(msg);
            return { success: false, error: msg };
        } finally {
            setLoading(false);
        }
    }, [notify]);

    const createJobOrder = useCallback(async (data) => {
        if (!canCreate) {
            notify.error("Permission denied");
            return { success: false };
        }
        setLoading(true);
        try {
            const newOrder = await jobOrdersApi.createJobOrder(data);
            setJobOrders(prev => [newOrder, ...prev]);
            notify.success("Job order created");
            return { success: true, data: newOrder };
        } catch (err) {
            notify.error(err.message || "Failed to create job order");
            return { success: false };
        } finally {
            setLoading(false);
        }
    }, [canCreate, notify]);

    const deleteJobOrder = useCallback(async (id) => {
        if (!canDelete) return { success: false };
        try {
            await jobOrdersApi.deleteJobOrder(id);
            setJobOrders(prev => prev.filter(o => o.id !== id));
            notify.success("Job order deleted");
            return { success: true };
        } catch (err) {
            notify.error(err.message || "Failed to delete job order");
            return { success: false };
        }
    }, [canDelete, notify]);

    // ─── POSITIONS ──────────────────────────────────────────────────────────

    const addPositionToOrder = useCallback(async (data) => {
        try {
            const newPos = await jobOrdersApi.createJobPosition(data);
            // Refresh the specific job order in local state
            setJobOrders(prev => prev.map(o => 
                o.id === data.job_order 
                ? { ...o, positions: [...(o.positions || []), newPos] }
                : o
            ));
            notify.success("Position added");
            return { success: true, data: newPos };
        } catch (err) {
            notify.error(err.message || "Failed to add position");
            return { success: false };
        }
    }, [notify]);

    const removePosition = useCallback(async (posId, orderId) => {
        try {
            await jobOrdersApi.deleteJobPosition(posId);
            setJobOrders(prev => prev.map(o => 
                o.id === orderId 
                ? { ...o, positions: (o.positions || []).filter(p => p.id !== posId) }
                : o
            ));
            notify.success("Position removed");
            return { success: true };
        } catch (err) {
            notify.error(err.message || "Failed to remove position");
            return { success: false };
        }
    }, [notify]);

    return {
        jobOrders,
        loading,
        pagination,
        canCreate,
        canEdit,
        canDelete,
        fetchJobOrders,
        createJobOrder,
        deleteJobOrder,
        addPositionToOrder,
        removePosition
    };
};

export default useJobOrders;
