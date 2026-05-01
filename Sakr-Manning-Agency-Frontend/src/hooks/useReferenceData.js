// hooks/useReferenceData.js
import { useState, useEffect, useCallback } from "react";
import userService from "../services/Form/userService";

/**
 * Hook to manage reference data (flags, vessel types, certificates, ranks, etc.)
 * Used for dropdown options throughout the form
 */
export const useReferenceData = (options = {}) => {
  const {
    loadOnMount = true,
    cacheKey = "sakr-reference-data-v2",
    cacheExpiry = 24 * 60 * 60 * 1000, // 24 hours
  } = options;

  const [data, setData] = useState({
    flags: [],
    vesselTypes: [],
    certificates: [],
    ranks: [],
    companies: [],
    positions: [],
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastLoaded, setLastLoaded] = useState(null);

  /**
   * Check if cached data is still valid
   */
  const isCacheValid = useCallback(() => {
    const cached = localStorage.getItem(cacheKey);
    if (!cached) return false;

    try {
      const { timestamp } = JSON.parse(cached);
      const age = Date.now() - timestamp;
      return age < cacheExpiry;
    } catch {
      return false;
    }
  }, [cacheKey, cacheExpiry]);

  /**
   * Load data from cache
   */
  const loadFromCache = useCallback(() => {
    try {
      const cached = localStorage.getItem(cacheKey);
      if (!cached) return null;

      const { data: cachedData, timestamp } = JSON.parse(cached);
      setData(cachedData);
      setLastLoaded(new Date(timestamp));
      return cachedData;
    } catch (err) {
      console.warn("Failed to load from cache:", err);
      return null;
    }
  }, [cacheKey]);

  /**
   * Save data to cache
   */
  const saveToCache = useCallback(
    (dataToCache) => {
      try {
        localStorage.setItem(
          cacheKey,
          JSON.stringify({
            data: dataToCache,
            timestamp: Date.now(),
          })
        );
      } catch (err) {
        console.warn("Failed to save to cache:", err);
      }
    },
    [cacheKey]
  );

  /**
   * Load all reference data from backend
   */
  const loadReferenceData = useCallback(
    async (forceRefresh = false) => {
      // Check cache first
      if (!forceRefresh && isCacheValid()) {
        const cachedData = loadFromCache();
        if (cachedData) {
          return { success: true, data: cachedData };
        }
      }

      setIsLoading(true);
      setError(null);

      try {
        const result = await userService.loadAllReferenceData();

        if (result.success) {
          setData(result.data);
          setLastLoaded(new Date());
          saveToCache(result.data);

          return { success: true, data: result.data };
        }

        throw new Error("Failed to load reference data");
      } catch (err) {
        const errorMessage = err.message || "Failed to load reference data";
        setError(errorMessage);
        console.error("Reference data error:", err);

        return {
          success: false,
          message: errorMessage,
        };
      } finally {
        setIsLoading(false);
      }
    },
    [isCacheValid, loadFromCache, saveToCache]
  );

  /**
   * Load specific reference type
   */
  const loadSpecificType = useCallback(async (type) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await userService.getReferenceData(type);

      if (result.success) {
        setData((prev) => ({
          ...prev,
          [type]: result.data,
        }));

        return { success: true, data: result.data };
      }

      throw new Error(`Failed to load ${type}`);
    } catch (err) {
      const errorMessage = err.message || `Failed to load ${type}`;
      setError(errorMessage);

      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Refresh data (force reload)
   */
  const refresh = useCallback(async () => {
    return await loadReferenceData(true);
  }, [loadReferenceData]);

  /**
   * Clear cache
   */
  const clearCache = useCallback(() => {
    localStorage.removeItem(cacheKey);
    setData({
      flags: [],
      vesselTypes: [],
      certificates: [],
      ranks: [],
      companies: [],
      positions: [],
    });
    setLastLoaded(null);
  }, [cacheKey]);

  /**
   * Get options for a specific type (formatted for select dropdowns)
   */
  const getOptions = useCallback(
    (type, labelKey = "name", valueKey = "id") => {
      const items = data[type] || [];
      return items.map((item) => ({
        label: item[labelKey],
        value: item[valueKey],
        ...item, // Include full object for additional data
      }));
    },
    [data]
  );

  /**
   * Find item by ID
   */
  const findById = useCallback(
    (type, id) => {
      const items = data[type] || [];
      return items.find((item) => item.id === id);
    },
    [data]
  );

  /**
   * Load on mount if enabled
   */
  // useEffect(() => {
  //   if (loadOnMount) {
  //     loadReferenceData();
  //   }
  // }, [loadOnMount, loadReferenceData]);

  useEffect(() => {
    let isMounted = true; // ✅ Cleanup flag

    if (loadOnMount) {
      loadReferenceData().then(() => {
        if (isMounted) {
          // Only update state if component still mounted
          setLastLoaded(new Date());
        }
      });
    }

    return () => {
      isMounted = false;
    }; // ✅ Prevent memory leak
  }, [loadOnMount, loadReferenceData]);

  return {
    // Data
    data,
    isLoading,
    error,
    lastLoaded,

    // Getters
    flags: data.flags,
    vesselTypes: data.vesselTypes,
    certificates: data.certificates,
    ranks: data.ranks,
    companies: data.companies,
    positions: data.positions,

    // Actions
    loadReferenceData,
    loadSpecificType,
    refresh,
    clearCache,
    getOptions,
    findById,
  };
};

export default useReferenceData;
