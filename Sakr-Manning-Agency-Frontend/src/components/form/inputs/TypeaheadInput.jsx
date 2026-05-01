import React, { useState, useEffect, useRef, useCallback, useId, useMemo } from "react";
import { ChevronDown, Search, Loader2, X } from "lucide-react";
import { useFormField, cx } from "../../../hooks/useFormField";

/**
 * TypeaheadInput - Async autocomplete with debounced backend search
 * 
 * Props:
 *  - name: field name (RHF integration)
 *  - label: optional label text
 *  - searchFn: async function(query) => Promise<{value, label}[]>
 *  - displayKey: key for display text (default: "label")
 *  - valueKey: key for value (default: "value")
 *  - placeholder: placeholder text
 *  - required: show * if required
 *  - debounceMs: debounce delay (default: 300)
 *  - minChars: minimum characters to trigger search (default: 2)
 *  - value: controlled value
 *  - onChange: callback(value, selectedItem)
 *  - error: error message
 *  - variant: style variant
 *  - initialOptions: pre-loaded options for initial display
 */

const variants = {
    default: "bg-white border border-black/50 rounded-[15px] shadow-md p-4",
    dashboard: "bg-white border border-gray-300 rounded-lg py-3 px-4 text-base shadow-sm hover:border-gray-400 transition-all duration-200",
    light: "bg-white rounded-[15px] border border-gray-100 p-4",
};

export function TypeaheadInput({
    name,
    label,
    searchFn,
    displayKey = "label",
    valueKey = "value",
    placeholder = "Type to search...",
    required = false,
    debounceMs = 300,
    minChars = 2,
    value,
    onChange,
    error: externalError,
    variant = "dashboard",
    className = "",
    initialOptions = [],
    disabled = false,
    ...props
}) {
    const {
        inForm,
        setValue: setFormValue,
        value: formValue,
        error,
        trigger,
    } = useFormField(name);

    const currentValue = inForm ? formValue : value;

    const setVal = (v, item) => {
        if (inForm) {
            setFormValue(name, v, { shouldValidate: true, shouldDirty: true });
            trigger?.(name);
        } else {
            onChange?.(v, item);
        }
    };

    const [open, setOpen] = useState(false);
    const [query, setQuery] = useState("");
    const [options, setOptions] = useState(initialOptions);
    const [loading, setLoading] = useState(false);
    const [selectedItem, setSelectedItem] = useState(null);
    const [highlightedIndex, setHighlightedIndex] = useState(-1);

    const inputRef = useRef(null);
    const listRef = useRef(null);
    const debounceRef = useRef(null);
    const cache = useRef({});
    const listId = useId();

    const err = inForm ? error : externalError;

    // Find selected item from current value
    useEffect(() => {
        if (currentValue && initialOptions.length > 0) {
            const found = initialOptions.find(opt => opt[valueKey] === currentValue);
            if (found) {
                setSelectedItem(found);
            }
        }
    }, [currentValue, initialOptions, valueKey]);

    // Debounced search
    const performSearch = useCallback(async (searchQuery) => {
        if (!searchFn) return;

        if (searchQuery.length < minChars) {
            setOptions(initialOptions);
            return;
        }

        // Check cache
        if (cache.current[searchQuery]) {
            setOptions(cache.current[searchQuery]);
            return;
        }

        setLoading(true);
        try {
            const results = await searchFn(searchQuery);
            const normalized = Array.isArray(results) ? results : (results?.results || results?.data || []);
            cache.current[searchQuery] = normalized;
            setOptions(normalized);
        } catch (err) {
            console.error("Typeahead search error:", err);
            setOptions([]);
        } finally {
            setLoading(false);
        }
    }, [searchFn, minChars, initialOptions]);

    // Handle query change with debounce
    const handleQueryChange = (e) => {
        const newQuery = e.target.value;
        setQuery(newQuery);
        setHighlightedIndex(-1);

        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }

        debounceRef.current = setTimeout(() => {
            performSearch(newQuery);
        }, debounceMs);
    };

    // Cleanup debounce on unmount
    useEffect(() => {
        return () => {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current);
            }
        };
    }, []);

    // Close dropdown on outside click
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (inputRef.current && !inputRef.current.parentElement.contains(e.target)) {
                setOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    // Keyboard navigation
    const handleKeyDown = (e) => {
        if (!open && (e.key === "ArrowDown" || e.key === "Enter")) {
            e.preventDefault();
            setOpen(true);
            if (initialOptions.length > 0) {
                setOptions(initialOptions);
            }
            return;
        }

        if (!open) return;

        switch (e.key) {
            case "ArrowDown":
                e.preventDefault();
                setHighlightedIndex(prev => Math.min(prev + 1, options.length - 1));
                break;
            case "ArrowUp":
                e.preventDefault();
                setHighlightedIndex(prev => Math.max(prev - 1, 0));
                break;
            case "Enter":
                e.preventDefault();
                if (highlightedIndex >= 0 && options[highlightedIndex]) {
                    selectOption(options[highlightedIndex]);
                }
                break;
            case "Escape":
                e.preventDefault();
                setOpen(false);
                break;
            default:
                break;
        }
    };

    // Select an option
    const selectOption = (opt) => {
        setSelectedItem(opt);
        setVal(opt[valueKey], opt);
        setQuery("");
        setOpen(false);
        setHighlightedIndex(-1);
    };

    // Clear selection
    const clearSelection = () => {
        setSelectedItem(null);
        setVal("", null);
        setQuery("");
        inputRef.current?.focus();
    };

    // Display text for selected item
    const displayText = useMemo(() => {
        if (selectedItem) {
            return selectedItem[displayKey] || selectedItem.name || selectedItem.label || "";
        }
        return "";
    }, [selectedItem, displayKey]);

    return (
        <div className="w-full">
            {label && (
                <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
                    {label} {required && <span className="text-red-500">*</span>}
                </label>
            )}

            <div className="relative">
                {/* Input container */}
                <div
                    className={cx(
                        "w-full flex items-center gap-2 cursor-text",
                        variants[variant],
                        err ? "border-red-400 focus-within:ring-red-100 focus-within:border-red-500" : "",
                        disabled ? "opacity-50 cursor-not-allowed" : "",
                        className
                    )}
                    onClick={() => !disabled && inputRef.current?.focus()}
                >
                    <Search className="w-4 h-4 text-gray-400 flex-shrink-0" />

                    {selectedItem && !open ? (
                        // Show selected value
                        <div className="flex-1 flex items-center justify-between">
                            <span className="text-gray-900 truncate">{displayText}</span>
                            {!disabled && (
                                <button
                                    type="button"
                                    onClick={(e) => { e.stopPropagation(); clearSelection(); }}
                                    className="p-1 hover:bg-gray-100 rounded"
                                >
                                    <X className="w-4 h-4 text-gray-400" />
                                </button>
                            )}
                        </div>
                    ) : (
                        // Show search input
                        <input
                            ref={inputRef}
                            type="text"
                            id={name}
                            role="combobox"
                            aria-controls={listId}
                            aria-expanded={open}
                            aria-haspopup="listbox"
                            aria-invalid={!!err}
                            disabled={disabled}
                            value={query}
                            onChange={handleQueryChange}
                            onFocus={() => {
                                setOpen(true);
                                if (options.length === 0 && initialOptions.length > 0) {
                                    setOptions(initialOptions);
                                }
                            }}
                            onKeyDown={handleKeyDown}
                            placeholder={selectedItem ? displayText : placeholder}
                            className="flex-1 bg-transparent outline-none text-gray-900 placeholder-gray-400"
                            {...props}
                        />
                    )}

                    {loading ? (
                        <Loader2 className="w-4 h-4 text-gray-400 animate-spin flex-shrink-0" />
                    ) : (
                        <ChevronDown
                            className={cx(
                                "w-4 h-4 text-gray-400 transition-transform flex-shrink-0",
                                open ? "rotate-180" : ""
                            )}
                        />
                    )}
                </div>

                {/* Dropdown */}
                {open && (
                    <div
                        id={listId}
                        ref={listRef}
                        role="listbox"
                        className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
                    >
                        {loading && (
                            <div className="px-4 py-3 text-sm text-gray-500 flex items-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Searching...
                            </div>
                        )}

                        {!loading && query.length > 0 && query.length < minChars && (
                            <div className="px-4 py-3 text-sm text-gray-500">
                                Type at least {minChars} characters to search
                            </div>
                        )}

                        {!loading && options.length === 0 && query.length >= minChars && (
                            <div className="px-4 py-3 text-sm text-gray-500">
                                No results found
                            </div>
                        )}

                        {!loading && options.map((opt, idx) => {
                            const optValue = opt[valueKey];
                            const optLabel = opt[displayKey] || opt.name || opt.label || optValue;
                            const isSelected = currentValue === optValue;
                            const isHighlighted = idx === highlightedIndex;

                            return (
                                <div
                                    key={optValue ?? idx}
                                    role="option"
                                    aria-selected={isSelected}
                                    onClick={() => selectOption(opt)}
                                    className={cx(
                                        "px-4 py-3 text-sm cursor-pointer transition-colors",
                                        isSelected ? "bg-blue-50 text-blue-600" : "",
                                        isHighlighted ? "bg-gray-100" : "hover:bg-gray-50"
                                    )}
                                >
                                    {optLabel}
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {err && (
                <p id={`${name}-error`} className="mt-1 text-red-500 text-xs flex items-center gap-1">
                    <span className="w-1 h-1 bg-red-500 rounded-full" /> {err}
                </p>
            )}
        </div>
    );
}

export default TypeaheadInput;
