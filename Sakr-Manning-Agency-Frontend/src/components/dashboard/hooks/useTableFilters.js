// hooks/useTableFilters.js
// Custom hook that consolidates all table filtering logic
// Used in CV.jsx, Company.jsx, Users.jsx

import { useState, useMemo } from "react";

/**
 * Custom Hook: useTableFilters
 *
 * Centralizes all filtering logic for data tables across the application
 * Handles: search, select filters, date range filters
 * Manages modal state, filter values, and active filters
 *
 * @param {array} rawData - Original unfiltered data array
 * @param {object} filterConfig - Configuration for how to filter data
 *
 * Filter Config Structure:
 * {
 *   searchFields: ['name', 'position'],              // Fields to search in
 *   selectFilters: [                                 // Select dropdown filters
 *     { key: 'status', type: 'exact' },
 *     { key: 'role', type: 'exact' }
 *   ],
 *   dateFilters: [                                   // Date range filters
 *     { key: 'dateFrom', targetKey: 'submitted', type: 'from' },
 *     { key: 'dateTo', targetKey: 'submitted', type: 'to' }
 *   ]
 * }
 *
 * @returns {object} Hook state and handlers
 */
const useTableFilters = (rawData = [], filterConfig = {}) => {
  // Modal state
  const [showModal, setShowModal] = useState(false);

  // Filter state: UI editing values (in modal)
  const [filters, setFilters] = useState(initializeFilterState(filterConfig));

  // Active filters: applied values (on data)
  const [activeFilters, setActiveFilters] = useState(
    initializeFilterState(filterConfig)
  );

  // Search query state
  const [searchQuery, setSearchQuery] = useState("");

  // Apply filters and close modal
  const handleApplyFilters = () => {
    setActiveFilters({ ...filters });
    setShowModal(false);
  };

  // Reset filters to empty
  const handleResetFilters = () => {
    const emptyFilters = initializeFilterState(filterConfig);
    setFilters(emptyFilters);
    setActiveFilters(emptyFilters);
    setShowModal(false);
  };

  // Compute filtered data based on active filters and search
  const filteredData = useMemo(() => {
    let result = rawData.slice();

    // 1. Apply search filtering
    if (searchQuery && filterConfig.searchFields?.length > 0) {
      const query = searchQuery.toLowerCase();
      result = result.filter((item) =>
        filterConfig.searchFields.some((field) => {
          const value = item[field];
          return value && String(value).toLowerCase().includes(query);
        })
      );
    }

    // 2. Apply select filters
    if (filterConfig.selectFilters?.length > 0) {
      filterConfig.selectFilters.forEach((filterConfig) => {
        const filterValue = activeFilters[filterConfig.key];
        if (filterValue) {
          result = result.filter((item) => {
            const itemValue = item[filterConfig.key];
            if (filterConfig.type === "exact") {
              return itemValue === filterValue;
            }
            if (filterConfig.type === "includes") {
              return String(itemValue).includes(filterValue);
            }
            if (filterConfig.type === "in") {
              return filterValue.some(
                (v) => itemValue.includes(v) || v.includes(itemValue)
              );
            }
            return true;
          });
        }
      });
    }

    // 3. Apply date range filters
    if (filterConfig.dateFilters?.length > 0) {
      filterConfig.dateFilters.forEach((dateFilterConfig) => {
        const filterValue = activeFilters[dateFilterConfig.key];
        if (filterValue) {
          const filterDate = new Date(filterValue);
          if (!Number.isNaN(filterDate.getTime())) {
            result = result.filter((item) => {
              const itemDate = new Date(item[dateFilterConfig.targetKey]);
              if (Number.isNaN(itemDate.getTime())) return false;

              if (dateFilterConfig.type === "from") {
                return itemDate >= filterDate;
              }
              if (dateFilterConfig.type === "to") {
                return itemDate <= filterDate;
              }
              return true;
            });
          }
        }
      });
    }

    return result;
  }, [rawData, activeFilters, searchQuery, filterConfig]);

  return {
    // Data
    filteredData,

    // Modal control
    showModal,
    setShowModal,

    // Filter state
    filters,
    setFilters,
    activeFilters,
    setActiveFilters,

    // Handlers
    handleApplyFilters,
    handleResetFilters,

    // Search
    searchQuery,
    setSearchQuery,
  };
};

/**
 * Helper: Initialize filter state based on config
 * Creates empty object with all filter keys set to empty string
 */
const initializeFilterState = (filterConfig = {}) => {
  const state = {};

  if (filterConfig.searchFields) {
    state.search = "";
  }

  if (filterConfig.selectFilters?.length > 0) {
    filterConfig.selectFilters.forEach((filter) => {
      state[filter.key] = "";
    });
  }

  if (filterConfig.dateFilters?.length > 0) {
    filterConfig.dateFilters.forEach((filter) => {
      state[filter.key] = "";
    });
  }

  return state;
};

export default useTableFilters;
