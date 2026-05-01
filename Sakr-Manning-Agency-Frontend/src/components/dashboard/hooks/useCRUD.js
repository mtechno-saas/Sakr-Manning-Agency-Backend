// hooks/useCRUD.js
// Reusable hook for CRUD operations with optimistic updates

import { useState, useCallback } from "react";
import { generateId } from "../../../utils/formHelpers";

/**
 * Custom Hook: useCRUD
 *
 * Provides complete CRUD operations for any data type
 * Handles optimistic updates and state management
 *
 * @param {Array} initialData - Initial data array
 * @param {Function} onDataChange - Callback when data changes (for parent updates)
 * @returns {Object} CRUD operations and state
 *
 * @example
 * const {
 *   data,
 *   loading,
 *   error,
 *   createItem,
 *   updateItem,
 *   deleteItem,
 *   getItem,
 *   refreshData
 * } = useCRUD(cvData, (newData) => setCvData(newData));
 */
const useCRUD = (initialData = [], onDataChange = null) => {
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Update data and notify parent
   */
  const updateData = useCallback(
    (newData) => {
      setData(newData);
      if (onDataChange) {
        onDataChange(newData);
      }
    },
    [onDataChange]
  );

  /**
   * Create new item
   * @param {Object} newItem - New item data
   * @param {Function} callback - Success callback
   * @returns {Promise<Object>} Created item
   */
  const createItem = useCallback(
    async (newItem, callback = null) => {
      setLoading(true);
      setError(null);

      try {
        // Generate ID if not provided
        const itemWithId = {
          ...newItem,
          id: newItem.id || generateId(),
        };

        // Simulate API delay
        await new Promise((resolve) => setTimeout(resolve, 300));

        // Optimistic update
        const newData = [itemWithId, ...data];
        updateData(newData);

        if (callback) {
          callback(itemWithId);
        }

        return itemWithId;
      } catch (err) {
        setError(err.message || "Failed to create item");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [data, updateData]
  );

  /**
   * Update existing item
   * @param {number|string} id - Item ID
   * @param {Object} updates - Updated data
   * @param {Function} callback - Success callback
   * @returns {Promise<Object>} Updated item
   */
  const updateItem = useCallback(
    async (id, updates, callback = null) => {
      setLoading(true);
      setError(null);

      try {
        // Simulate API delay
        await new Promise((resolve) => setTimeout(resolve, 300));

        // Find and update item
        const itemIndex = data.findIndex((item) => item.id === id);
        if (itemIndex === -1) {
          throw new Error("Item not found");
        }

        const updatedItem = {
          ...data[itemIndex],
          ...updates,
        };

        // Optimistic update
        const newData = [...data];
        newData[itemIndex] = updatedItem;
        updateData(newData);

        if (callback) {
          callback(updatedItem);
        }

        return updatedItem;
      } catch (err) {
        setError(err.message || "Failed to update item");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [data, updateData]
  );

  /**
   * Delete item
   * @param {number|string} id - Item ID
   * @param {Function} callback - Success callback
   * @returns {Promise<boolean>} Success status
   */
  const deleteItem = useCallback(
    async (id, callback = null) => {
      setLoading(true);
      setError(null);

      try {
        // Simulate API delay
        await new Promise((resolve) => setTimeout(resolve, 300));

        // Optimistic update
        const newData = data.filter((item) => item.id !== id);
        updateData(newData);

        if (callback) {
          callback(id);
        }

        return true;
      } catch (err) {
        setError(err.message || "Failed to delete item");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [data, updateData]
  );

  /**
   * Bulk delete items
   * @param {Array} ids - Array of item IDs
   * @param {Function} callback - Success callback
   * @returns {Promise<boolean>} Success status
   */
  const bulkDelete = useCallback(
    async (ids, callback = null) => {
      setLoading(true);
      setError(null);

      try {
        // Simulate API delay
        await new Promise((resolve) => setTimeout(resolve, 500));

        // Optimistic update
        const newData = data.filter((item) => !ids.includes(item.id));
        updateData(newData);

        if (callback) {
          callback(ids);
        }

        return true;
      } catch (err) {
        setError(err.message || "Failed to delete items");
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [data, updateData]
  );

  /**
   * Get single item by ID
   * @param {number|string} id - Item ID
   * @returns {Object|null} Item or null if not found
   */
  const getItem = useCallback(
    (id) => {
      return data.find((item) => item.id === id) || null;
    },
    [data]
  );

  /**
   * Get multiple items by IDs
   * @param {Array} ids - Array of item IDs
   * @returns {Array} Array of items
   */
  const getItems = useCallback(
    (ids) => {
      return data.filter((item) => ids.includes(item.id));
    },
    [data]
  );

  /**
   * Refresh data from source
   * @param {Array} newData - Fresh data
   */
  const refreshData = useCallback(
    (newData) => {
      updateData(newData);
    },
    [updateData]
  );

  /**
   * Clear all data
   */
  const clearData = useCallback(() => {
    updateData([]);
  }, [updateData]);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    data,
    loading,
    error,
    createItem,
    updateItem,
    deleteItem,
    bulkDelete,
    getItem,
    getItems,
    refreshData,
    clearData,
    clearError,
  };
};

export default useCRUD;
