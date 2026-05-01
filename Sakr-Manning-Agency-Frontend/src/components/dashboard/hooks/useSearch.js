// hooks/useSearch.js
// Custom hook to get/set search query from SearchContext
// Provides centralized search state across all pages

import { useContext } from "react";
import SearchContext from "../context/SearchContext";

/**
 * Custom Hook: useSearch
 *
 * Accesses the global search context
 * Provides search query and setter function
 *
 * @returns {object} { searchQuery, setSearchQuery }
 *
 * @example
 * const { searchQuery, setSearchQuery } = useSearch();
 *
 * // Use in component
 * <input
 *   value={searchQuery}
 *   onChange={(e) => setSearchQuery(e.target.value)}
 *   placeholder="Search..."
 * />
 */
const useSearch = () => {
  const context = useContext(SearchContext);

  if (!context) {
    throw new Error(
      "useSearch must be used within SearchProvider. " +
        "Make sure DashboardApp is wrapped with SearchProvider."
    );
  }

  return context;
};

export default useSearch;
