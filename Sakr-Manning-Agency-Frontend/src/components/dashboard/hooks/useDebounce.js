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

/*
// hooks/useDebounce.js
import { useState, useEffect } from 'react';
/*

useDebounce - Debounces a value
Delays updating the value until after a specified delay

@param {any} value - Value to debounce
@param {number} delay - Delay in milliseconds (default: 300)
@returns {any} Debounced value

@example
const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebounce(searchTerm, 500);

useEffect(() => {
if (debouncedSearch) {

searchAPI(debouncedSearch);

}
}, [debouncedSearch]);
*/
/*
export function useDebounce(value, delay = 300) {
const [debouncedValue, setDebouncedValue] = useState(value);

useEffect(() => {
const timer = setTimeout(() => {
setDebouncedValue(value);
}, delay);
return () => {
  clearTimeout(timer);
};
}, [value, delay]);
return debouncedValue;
}
*/

/*
useDebouncedCallback - Debounces a callback function
Useful when you want to debounce the execution, not the value

@param {Function} callback - Function to debounce
@param {number} delay - Delay in milliseconds (default: 300)
@returns {Function} Debounced callback

@example
const debouncedSave = useDebouncedCallback((data) => {
saveToAPI(data);
}, 1000);
*/

/* 
export function useDebouncedCallback(callback, delay = 300) {
const [timer, setTimer] = useState(null);

return (...args) => {
if (timer) clearTimeout(timer);
const newTimer = setTimeout(() => {
  callback(...args);
}, delay);

setTimer(newTimer);
};
}
*/
