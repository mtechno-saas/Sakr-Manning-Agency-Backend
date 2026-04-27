import React, { useState, useEffect, useRef, useCallback, useId, useMemo } from "react";
import { ChevronDown, Search, Loader2, X, Plus, AlertCircle, RefreshCw } from "lucide-react";
import { useFormField, cx } from "../../../../hooks/useFormField";

/**
 * TypeaheadInput v2 - Enhanced Async Autocomplete
 * 
 * NEW FEATURES:
 * - Recent selections cache (localStorage)
 * - Rich option rendering (avatars, descriptions, metadata)
 * - Custom empty states
 * - Skeleton loaders
 * - Section headers / grouped options
 * - "Create new" action button
 * - Multi-column display
 * - Custom option templates
 * - Async initial value loading
 * - Enhanced accessibility
 * - Error states with retry
 * - Infinite scroll support
 * 
 * BACKWARD COMPATIBLE - All existing props still work!
 * 
 * Props:
 *  - name: field name (RHF integration)
 *  - label: optional label text
 *  - searchFn: async function(query) => Promise<Array>
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
 *  - initialOptions: pre-loaded options
 *  - disabled: disable input
 * 
 * NEW PROPS:
 *  - enableRecentSelections: enable recent selections cache (default: true)
 *  - recentSelectionsKey: localStorage key for caching (default: name)
 *  - maxRecentSelections: max items to cache (default: 5)
 *  - renderOption: custom option renderer (option, isSelected, isHighlighted) => ReactNode
 *  - renderSelectedValue: custom selected value renderer (option) => ReactNode
 *  - showAvatar: show avatar in options (default: false)
 *  - avatarKey: key for avatar URL (default: "profile_image")
 *  - descriptionKey: key for description text (default: "description")
 *  - metadataKeys: array of keys to show as metadata (e.g., ["email", "role"])
 *  - emptyStateMessage: custom empty state message
 *  - emptyStateIcon: custom empty state icon component
 *  - createNewLabel: label for "Create new" button
 *  - onCreateNew: callback when "Create new" is clicked
 *  - groupBy: key to group options by (creates section headers)
 *  - loadInitialValue: async function(value) => Promise<option> (fetch item by ID)
 *  - onError: callback when search fails
 *  - enableInfiniteScroll: enable infinite scroll (default: false)
 *  - onLoadMore: callback() => Promise<Array> (load more results)
 *  - showSkeleton: show skeleton loaders while loading (default: true)
 */

const variants = {
    default: "bg-white border border-black/50 rounded-[15px] shadow-md p-4",
    dashboard: "bg-white border border-gray-300 rounded-lg py-3 px-4 text-base shadow-sm hover:border-gray-400 transition-all duration-200",
    light: "bg-white rounded-[15px] border border-gray-100 p-4",
};

// Skeleton loader for options
const OptionSkeleton = () => (
    <div className="px-4 py-3 animate-pulse">
        <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
            <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
        </div>
    </div>
);

// Default empty state
const DefaultEmptyState = ({ message, icon: Icon }) => (
    <div className="px-4 py-8 text-center text-gray-500">
        {Icon && <Icon className="w-12 h-12 mx-auto mb-3 text-gray-300" />}
        <p className="text-sm">{message || "No results found"}</p>
    </div>
);

// Recent selections manager
class RecentSelectionsManager {
    constructor(key, maxItems = 5) {
        this.key = `typeahead_recent_${key}`;
        this.maxItems = maxItems;
    }

    get() {
        try {
            const stored = localStorage.getItem(this.key);
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    }

    add(item) {
        try {
            let recent = this.get();
            // Remove if already exists
            recent = recent.filter(r => r.value !== item.value);
            // Add to front
            recent.unshift(item);
            // Limit to maxItems
            recent = recent.slice(0, this.maxItems);
            localStorage.setItem(this.key, JSON.stringify(recent));
        } catch (err) {
            console.warn("Failed to save recent selection:", err);
        }
    }

    clear() {
        try {
            localStorage.removeItem(this.key);
        } catch (err) {
            console.warn("Failed to clear recent selections:", err);
        }
    }
}

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
    // NEW PROPS
    enableRecentSelections = true,
    recentSelectionsKey,
    maxRecentSelections = 5,
    renderOption,
    renderSelectedValue,
    showAvatar = false,
    avatarKey = "profile_image",
    descriptionKey = "description",
    metadataKeys = [],
    emptyStateMessage,
    emptyStateIcon,
    createNewLabel,
    onCreateNew,
    groupBy,
    loadInitialValue,
    onError,
    enableInfiniteScroll = false,
    onLoadMore,
    showSkeleton = true,
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
    const [searchError, setSearchError] = useState(null);
    const [hasMore, setHasMore] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);

    const inputRef = useRef(null);
    const listRef = useRef(null);
    const debounceRef = useRef(null);
    const cache = useRef({});
    const listId = useId();
    const scrollObserverRef = useRef(null);

    const err = inForm ? error : externalError;

    // Recent selections manager
    const recentManager = useMemo(() => {
        if (!enableRecentSelections) return null;
        return new RecentSelectionsManager(
            recentSelectionsKey || name,
            maxRecentSelections
        );
    }, [enableRecentSelections, recentSelectionsKey, name, maxRecentSelections]);

    // Load initial value if needed
    useEffect(() => {
        if (currentValue && !selectedItem && loadInitialValue) {
            loadInitialValue(currentValue)
                .then(item => {
                    if (item) {
                        setSelectedItem(item);
                    }
                })
                .catch(err => {
                    console.error("Failed to load initial value:", err);
                });
        }
    }, [currentValue, selectedItem, loadInitialValue]);

    // Find selected item from current value
    useEffect(() => {
        if (currentValue && initialOptions.length > 0 && !selectedItem) {
            const found = initialOptions.find(opt => opt[valueKey] === currentValue);
            if (found) {
                setSelectedItem(found);
            }
        }
    }, [currentValue, initialOptions, valueKey, selectedItem]);

    // Debounced search
    const performSearch = useCallback(async (searchQuery) => {
        if (!searchFn) return;

        if (searchQuery.length < minChars) {
            // Show recent selections if available
            if (recentManager && searchQuery.length === 0) {
                const recent = recentManager.get();
                setOptions(recent.length > 0 ? recent : initialOptions);
            } else {
                setOptions(initialOptions);
            }
            return;
        }

        // Check cache
        if (cache.current[searchQuery]) {
            setOptions(cache.current[searchQuery]);
            setSearchError(null);
            return;
        }

        setLoading(true);
        setSearchError(null);

        try {
            const results = await searchFn(searchQuery);
            const normalized = Array.isArray(results) ? results : (results?.results || results?.data || []);
            cache.current[searchQuery] = normalized;
            setOptions(normalized);

            // Check if there are more results
            if (results?.next || results?.hasMore) {
                setHasMore(true);
            } else {
                setHasMore(false);
            }
        } catch (err) {
            console.error("Typeahead search error:", err);
            setSearchError(err.message || "Search failed");
            setOptions([]);
            onError?.(err);
        } finally {
            setLoading(false);
        }
    }, [searchFn, minChars, initialOptions, recentManager, onError]);

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

    // Infinite scroll observer
    useEffect(() => {
        if (!enableInfiniteScroll || !onLoadMore || !listRef.current) return;

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && hasMore && !loadingMore) {
                    handleLoadMore();
                }
            },
            { threshold: 1.0 }
        );

        const sentinel = listRef.current.querySelector('.scroll-sentinel');
        if (sentinel) {
            observer.observe(sentinel);
        }

        scrollObserverRef.current = observer;

        return () => {
            if (scrollObserverRef.current) {
                scrollObserverRef.current.disconnect();
            }
        };
    }, [enableInfiniteScroll, hasMore, loadingMore, onLoadMore]);

    // Load more results
    const handleLoadMore = async () => {
        if (!onLoadMore || loadingMore) return;

        setLoadingMore(true);
        try {
            const moreResults = await onLoadMore();
            const normalized = Array.isArray(moreResults) ? moreResults : (moreResults?.results || moreResults?.data || []);
            setOptions(prev => [...prev, ...normalized]);

            if (moreResults?.next || moreResults?.hasMore) {
                setHasMore(true);
            } else {
                setHasMore(false);
            }
        } catch (err) {
            console.error("Failed to load more:", err);
        } finally {
            setLoadingMore(false);
        }
    };

    // Keyboard navigation
    const handleKeyDown = (e) => {
        if (!open && (e.key === "ArrowDown" || e.key === "Enter")) {
            e.preventDefault();
            setOpen(true);
            if (recentManager && query.length === 0) {
                const recent = recentManager.get();
                setOptions(recent.length > 0 ? recent : initialOptions);
            } else if (initialOptions.length > 0) {
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

    // Scroll highlighted item into view
    useEffect(() => {
        if (highlightedIndex >= 0 && listRef.current) {
            const highlightedElement = listRef.current.querySelector(`[data-option-index="${highlightedIndex}"]`);
            if (highlightedElement) {
                highlightedElement.scrollIntoView({
                    block: "nearest",
                    behavior: "smooth"
                });
            }
        }
    }, [highlightedIndex]);

    // Select an option
    const selectOption = (opt) => {
        setSelectedItem(opt);
        setVal(opt[valueKey], opt);
        setQuery("");
        setOpen(false);
        setHighlightedIndex(-1);

        // Add to recent selections
        if (recentManager) {
            recentManager.add(opt);
        }
    };

    // Clear selection
    const clearSelection = () => {
        setSelectedItem(null);
        setVal("", null);
        setQuery("");
        inputRef.current?.focus();
    };

    // Retry search
    const retrySearch = () => {
        setSearchError(null);
        performSearch(query);
    };

    // Group options by key
    const groupedOptions = useMemo(() => {
        if (!groupBy || options.length === 0) {
            return [{ group: null, items: options }];
        }

        const groups = {};
        options.forEach(opt => {
            const groupKey = opt[groupBy] || "Other";
            if (!groups[groupKey]) {
                groups[groupKey] = [];
            }
            groups[groupKey].push(opt);
        });

        return Object.entries(groups).map(([group, items]) => ({
            group,
            items
        }));
    }, [options, groupBy]);

    // Default option renderer
    const defaultRenderOption = (opt, isSelected, isHighlighted) => {
        const optValue = opt[valueKey];
        const optLabel = opt[displayKey] || opt.name || opt.label || optValue;
        const optDescription = opt[descriptionKey];
        const optAvatar = opt[avatarKey];
        const metadata = metadataKeys.map(key => opt[key]).filter(Boolean);

        return (
            <div className="flex items-center gap-3">
                {showAvatar && optAvatar && (
                    <img
                        src={optAvatar}
                        alt=""
                        className="w-8 h-8 rounded-full object-cover flex-shrink-0"
                    />
                )}
                {showAvatar && !optAvatar && (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                        <span className="text-xs font-medium text-gray-600">
                            {optLabel.charAt(0).toUpperCase()}
                        </span>
                    </div>
                )}
                <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-900 truncate">
                        {optLabel}
                    </div>
                    {optDescription && (
                        <div className="text-xs text-gray-500 truncate">
                            {optDescription}
                        </div>
                    )}
                    {metadata.length > 0 && (
                        <div className="text-xs text-gray-400 truncate">
                            {metadata.join(" • ")}
                        </div>
                    )}
                </div>
            </div>
        );
    };

    // Display text for selected item
    const displayText = useMemo(() => {
        if (selectedItem) {
            return selectedItem[displayKey] || selectedItem.name || selectedItem.label || "";
        }
        return "";
    }, [selectedItem, displayKey]);

    // Check if showing recent selections
    const showingRecent = useMemo(() => {
        if (!recentManager || query.length > 0) return false;
        const recent = recentManager.get();
        return recent.length > 0 && JSON.stringify(recent) === JSON.stringify(options);
    }, [recentManager, query, options]);

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
                        err ? "border-red-400 focus-within:ring-red-100 focus-within:border-red-500" : "focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100",
                        disabled ? "opacity-50 cursor-not-allowed" : "",
                        className
                    )}
                    onClick={() => !disabled && inputRef.current?.focus()}
                >
                    <Search className="w-4 h-4 text-gray-400 flex-shrink-0" />

                    {selectedItem && !open ? (
                        // Show selected value
                        <div className="flex-1 flex items-center justify-between min-w-0">
                            {renderSelectedValue ? (
                                renderSelectedValue(selectedItem)
                            ) : (
                                <span className="text-gray-900 truncate">{displayText}</span>
                            )}
                            {!disabled && (
                                <button
                                    type="button"
                                    onClick={(e) => { e.stopPropagation(); clearSelection(); }}
                                    className="p-1 hover:bg-gray-100 rounded flex-shrink-0"
                                    aria-label="Clear selection"
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
                            aria-activedescendant={highlightedIndex >= 0 ? `${listId}-option-${highlightedIndex}` : undefined}
                            disabled={disabled}
                            value={query}
                            onChange={handleQueryChange}
                            onFocus={() => {
                                setOpen(true);
                                if (options.length === 0) {
                                    if (recentManager && query.length === 0) {
                                        const recent = recentManager.get();
                                        setOptions(recent.length > 0 ? recent : initialOptions);
                                    } else if (initialOptions.length > 0) {
                                        setOptions(initialOptions);
                                    }
                                }
                            }}
                            onKeyDown={handleKeyDown}
                            placeholder={selectedItem ? displayText : placeholder}
                            className="flex-1 bg-transparent outline-none text-gray-900 placeholder-gray-400 min-w-0"
                            autoComplete="off"
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
                        aria-label={label || "Search results"}
                        className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-80 overflow-y-auto"
                    >
                        {/* Loading skeleton */}
                        {loading && showSkeleton && (
                            <>
                                <OptionSkeleton />
                                <OptionSkeleton />
                                <OptionSkeleton />
                            </>
                        )}

                        {/* Loading without skeleton */}
                        {loading && !showSkeleton && (
                            <div className="px-4 py-3 text-sm text-gray-500 flex items-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Searching...
                            </div>
                        )}

                        {/* Minimum characters message */}
                        {!loading && query.length > 0 && query.length < minChars && (
                            <div className="px-4 py-3 text-sm text-gray-500">
                                Type at least {minChars} characters to search
                            </div>
                        )}

                        {/* Error state */}
                        {!loading && searchError && (
                            <div className="px-4 py-6 text-center">
                                <AlertCircle className="w-12 h-12 mx-auto mb-3 text-red-300" />
                                <p className="text-sm text-red-600 mb-3">{searchError}</p>
                                <button
                                    type="button"
                                    onClick={retrySearch}
                                    className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                                >
                                    <RefreshCw className="w-4 h-4" />
                                    Retry
                                </button>
                            </div>
                        )}

                        {/* Empty state */}
                        {!loading && !searchError && options.length === 0 && query.length >= minChars && (
                            <DefaultEmptyState
                                message={emptyStateMessage}
                                icon={emptyStateIcon}
                            />
                        )}

                        {/* Recent selections header */}
                        {!loading && showingRecent && (
                            <div className="px-4 py-2 text-xs font-medium text-gray-500 border-b border-gray-100 sticky top-0 bg-white">
                                Recent Selections
                            </div>
                        )}

                        {/* Options */}
                        {!loading && !searchError && groupedOptions.map((group, groupIdx) => (
                            <div key={groupIdx}>
                                {/* Group header */}
                                {group.group && (
                                    <div className="px-4 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b border-gray-100 sticky top-0">
                                        {group.group}
                                    </div>
                                )}

                                {/* Group items */}
                                {group.items.map((opt, idx) => {
                                    const globalIdx = groupedOptions
                                        .slice(0, groupIdx)
                                        .reduce((sum, g) => sum + g.items.length, 0) + idx;
                                    const optValue = opt[valueKey];
                                    const isSelected = currentValue === optValue;
                                    const isHighlighted = globalIdx === highlightedIndex;

                                    return (
                                        <div
                                            key={optValue ?? globalIdx}
                                            id={`${listId}-option-${globalIdx}`}
                                            role="option"
                                            aria-selected={isSelected}
                                            data-option-index={globalIdx}
                                            onClick={() => selectOption(opt)}
                                            className={cx(
                                                "px-4 py-3 text-sm cursor-pointer transition-colors",
                                                isSelected ? "bg-blue-50 text-blue-600" : "",
                                                isHighlighted ? "bg-gray-100" : "hover:bg-gray-50"
                                            )}
                                        >
                                            {renderOption ? renderOption(opt, isSelected, isHighlighted) : defaultRenderOption(opt, isSelected, isHighlighted)}
                                        </div>
                                    );
                                })}
                            </div>
                        ))}

                        {/* Loading more indicator */}
                        {loadingMore && (
                            <div className="px-4 py-3 text-sm text-gray-500 flex items-center justify-center gap-2 border-t border-gray-100">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Loading more...
                            </div>
                        )}

                        {/* Infinite scroll sentinel */}
                        {enableInfiniteScroll && hasMore && !loadingMore && (
                            <div className="scroll-sentinel h-1" />
                        )}

                        {/* Create new action */}
                        {!loading && onCreateNew && query.length >= minChars && (
                            <button
                                type="button"
                                onClick={() => {
                                    setOpen(false);
                                    onCreateNew(query);
                                }}
                                className="w-full px-4 py-3 text-sm text-blue-600 hover:bg-blue-50 flex items-center gap-2 border-t border-gray-100 transition-colors"
                            >
                                <Plus className="w-4 h-4" />
                                {createNewLabel || `Create "${query}"`}
                            </button>
                        )}
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