// context/SearchContext.jsx (UPDATED)
// Global context for managing search state across the application

import React, { createContext, useState, useCallback } from "react";

const SearchContext = createContext(null);

/**
 * SearchProvider Component (UPDATED)
 *
 * Wraps the dashboard to provide search functionality globally
 * Features:
 * - Centralized search state
 * - Persistent search across pages ✅ NEW
 * - Search results storage ✅ NEW
 * - Debounce-ready (value can be debounced in useTableFilters)
 *
 * Usage:
 * <SearchProvider>
 *   <DashboardContent />
 * </SearchProvider>
 */
export const SearchProvider = ({ children }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  // Stable callback to prevent unnecessary re-renders
  const updateSearchQuery = useCallback((value) => {
    setSearchQuery(value);
  }, []);

  // ✅ NEW: Update search results
  const updateSearchResults = useCallback((results) => {
    setSearchResults(results);
  }, []);

  // ✅ NEW: Clear search
  const clearSearch = useCallback(() => {
    setSearchQuery("");
    setSearchResults(null);
    setIsSearching(false);
  }, []);

  // ✅ NEW: Set searching state
  const updateSearching = useCallback((searching) => {
    setIsSearching(searching);
  }, []);

  const value = {
    searchQuery,
    setSearchQuery: updateSearchQuery,
    searchResults,
    setSearchResults: updateSearchResults,
    isSearching,
    setIsSearching: updateSearching,
    clearSearch,
  };

  return (
    <SearchContext.Provider value={value}>{children}</SearchContext.Provider>
  );
};

export default SearchContext;
