// hooks/useDebounce.js
// Generic debounce hook for delayed value updates
// Used for search input and other frequently-changing values

import { useState, useEffect } from "react";

/**
 * Custom Hook: useDebounce
 *
 * Delays updating a value until user stops changing it
 * Prevents excessive function calls during rapid changes (like typing)
 *
 * Common use cases:
 * - Search input: Wait 300ms after user stops typing to filter
 * - Resize handlers: Wait 200ms after window resize stops
 * - Auto-save: Wait 1000ms after user stops typing to save
 *
 * @param {any} value - The value to debounce
 * @param {number} delay - Delay in milliseconds (default: 300)
 * @returns {any} Debounced value
 *
 * @example
 * // Search with debouncing
 * const [searchInput, setSearchInput] = useState("");
 * const debouncedSearch = useDebounce(searchInput, 300);
 *
 * // Filter data when debounced value changes
 * useEffect(() => {
 *   const filtered = data.filter(item =>
 *     item.name.toLowerCase().includes(debouncedSearch.toLowerCase())
 *   );
 *   setFilteredData(filtered);
 * }, [debouncedSearch, data]);
 *
 * return (
 *   <input
 *     value={searchInput}
 *     onChange={(e) => setSearchInput(e.target.value)}
 *     placeholder="Search..."
 *   />
 * );
 */
const useDebounce = (value, delay = 300) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    // Set up timer to update debounced value after delay
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Clear timer if value changes before delay completes
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

export default useDebounce;
