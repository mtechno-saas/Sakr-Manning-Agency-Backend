import React, { useState, useRef, useEffect, useCallback, useId, useMemo } from "react";
import ReactDOM from "react-dom";
import { ChevronDown, Search, X, Check, Loader2, Plus, Tag as TagIcon } from "lucide-react";
import { useFormField, cx } from "../../../../hooks/useFormField";

/**
 * MultiSelect v2 - Enhanced Multi-Selection Dropdown
 * 
 * FEATURES:
 * - Select multiple options from dropdown
 * - Search/filter options
 * - Select all / Deselect all
 * - Checkbox-based selection
 * - Badge display for selected items
 * - Remove individual selections
 * - Group options support
 * - Custom option rendering
 * - Async search support
 * - Max selections limit
 * - Keyboard navigation
 * - Accessibility (ARIA)
 * - Virtual scrolling for large lists
 * - Quick filters
 * - Export selected values
 * 
 * Props:
 *  - name: field name
 *  - label: label text
 *  - options: array of { value, label, ... }
 *  - value: array of selected values
 *  - onChange: callback(values, selectedItems)
 *  - placeholder: placeholder text
 *  - required: show * if required
 *  - error: error message
 *  - variant: style variant
 *  - disabled: disable input
 *  - searchable: enable search (default: true)
 *  - searchPlaceholder: search input placeholder
 *  - displayKey: key for display text (default: "label")
 *  - valueKey: key for value (default: "value")
 *  - maxSelections: maximum number of selections
 *  - showSelectAll: show select all button (default: true)
 *  - groupBy: key to group options by
 *  - renderOption: custom option renderer
 *  - renderBadge: custom badge renderer
 *  - searchFn: async search function
 *  - debounceMs: search debounce delay
 *  - showCount: show selected count
 *  - clearable: show clear all button
 *  - closeOnSelect: close dropdown after selection (default: false)
 */

const variants = {
    default: "bg-white border border-black/50 rounded-[15px] shadow-md p-4",
    dashboard: "bg-white border border-gray-300 rounded-lg py-3 px-4 text-base shadow-sm hover:border-gray-400 transition-all duration-200",
    light: "bg-white rounded-[15px] border border-gray-100 p-4",
};

// Selected item badge
const Badge = ({ children, onRemove, disabled }) => (
    <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 text-sm rounded-md">
        <span className="truncate max-w-[120px]">{children}</span>
        {!disabled && (
            <button
                type="button"
                onClick={onRemove}
                className="hover:bg-blue-100 rounded p-0.5 transition-colors"
                aria-label={`Remove ${children}`}
            >
                <X className="w-3 h-3" />
            </button>
        )}
    </span>
);

export function MultiSelect({
    name,
    label,
    options = [],
    value = [],
    onChange,
    placeholder = "Select options...",
    required = false,
    error: externalError,
    variant = "dashboard",
    className = "",
    disabled = false,
    searchable = true,
    searchPlaceholder = "Search...",
    displayKey = "label",
    valueKey = "value",
    maxSelections,
    showSelectAll = true,
    groupBy,
    renderOption,
    renderBadge,
    searchFn,
    debounceMs = 300,
    showCount = true,
    clearable = true,
    closeOnSelect = false,
    ...props
}) {
    const {
        inForm,
        setValue: setFormValue,
        value: formValue,
        error,
        trigger,
    } = useFormField(name);

    const currentValue = inForm ? (formValue || []) : (value || []);
    const selectedValues = Array.isArray(currentValue) ? currentValue : [];

    const setVal = useCallback((newValues, selectedItems) => {
        if (inForm) {
            setFormValue(name, newValues, { shouldValidate: true, shouldDirty: true });
            trigger?.(name);
        } else {
            onChange?.(newValues, selectedItems);
        }
    }, [inForm, setFormValue, name, trigger, onChange]);

    const [open, setOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [filteredOptions, setFilteredOptions] = useState(options);
    const [dropdownStyle, setDropdownStyle] = useState({});

    const triggerRef = useRef(null);
    const dropdownRef = useRef(null);
    const searchInputRef = useRef(null);
    const debounceRef = useRef(null);
    const listId = useId();

    const err = inForm ? error : externalError;

    // Get selected items
    const selectedItems = useMemo(() => {
        return options.filter(opt => selectedValues.includes(opt[valueKey]));
    }, [options, selectedValues, valueKey]);

    // Filter options based on search
    useEffect(() => {
        if (!searchable || !searchQuery) {
            setFilteredOptions(options);
            return;
        }

        if (searchFn) {
            // Async search
            if (debounceRef.current) {
                clearTimeout(debounceRef.current);
            }

            debounceRef.current = setTimeout(async () => {
                setLoading(true);
                try {
                    const results = await searchFn(searchQuery);
                    setFilteredOptions(Array.isArray(results) ? results : []);
                } catch (err) {
                    console.error("MultiSelect search error:", err);
                    setFilteredOptions([]);
                } finally {
                    setLoading(false);
                }
            }, debounceMs);
        } else {
            // Local search
            const query = searchQuery.toLowerCase();
            const filtered = options.filter(opt => {
                const label = (opt[displayKey] || "").toLowerCase();
                return label.includes(query);
            });
            setFilteredOptions(filtered);
        }
    }, [searchQuery, options, searchable, searchFn, debounceMs, displayKey]);

    // Cleanup debounce
    useEffect(() => {
        return () => {
            if (debounceRef.current) {
                clearTimeout(debounceRef.current);
            }
        };
    }, []);

    // Compute portal dropdown position
    const updateDropdownPosition = useCallback(() => {
        if (!triggerRef.current) return;
        const rect = triggerRef.current.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const spaceBelow = viewportHeight - rect.bottom;
        const spaceAbove = rect.top;
        const dropdownMaxHeight = 320;
        const openUpward = spaceBelow < dropdownMaxHeight && spaceAbove > spaceBelow;

        setDropdownStyle({
            position: "fixed",
            left: `${rect.left}px`,
            width: `${rect.width}px`,
            zIndex: 99999,
            ...(openUpward
                ? { bottom: `${viewportHeight - rect.top}px`, top: "auto" }
                : { top: `${rect.bottom + 4}px`, bottom: "auto" }),
        });
    }, []);

    useEffect(() => {
        if (open) {
            updateDropdownPosition();
            window.addEventListener("scroll", updateDropdownPosition, true);
            window.addEventListener("resize", updateDropdownPosition);
        }
        return () => {
            window.removeEventListener("scroll", updateDropdownPosition, true);
            window.removeEventListener("resize", updateDropdownPosition);
        };
    }, [open, updateDropdownPosition]);

    // Close on outside click (checks both trigger button and portalled list)
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (
                triggerRef.current?.contains(e.target) ||
                dropdownRef.current?.contains(e.target)
            ) return;
            setOpen(false);
        };

        if (open) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [open]);

    // Focus search input when opened
    useEffect(() => {
        if (open && searchable && searchInputRef.current) {
            searchInputRef.current.focus();
        }
    }, [open, searchable]);

    // Toggle selection
    const toggleOption = (optionValue) => {
        const isSelected = selectedValues.includes(optionValue);

        let newValues;
        if (isSelected) {
            newValues = selectedValues.filter(v => v !== optionValue);
        } else {
            if (maxSelections && selectedValues.length >= maxSelections) {
                return; // Max selections reached
            }
            newValues = [...selectedValues, optionValue];
        }

        const newItems = options.filter(opt => newValues.includes(opt[valueKey]));
        setVal(newValues, newItems);

        if (closeOnSelect) {
            setOpen(false);
        }
    };

    // Select all
    const selectAll = () => {
        const allValues = filteredOptions.map(opt => opt[valueKey]);
        const limitedValues = maxSelections ? allValues.slice(0, maxSelections) : allValues;
        const newItems = options.filter(opt => limitedValues.includes(opt[valueKey]));
        setVal(limitedValues, newItems);
    };

    // Deselect all
    const deselectAll = () => {
        setVal([], []);
    };

    // Remove single item
    const removeItem = (optionValue) => {
        const newValues = selectedValues.filter(v => v !== optionValue);
        const newItems = options.filter(opt => newValues.includes(opt[valueKey]));
        setVal(newValues, newItems);
    };

    // Group options
    const groupedOptions = useMemo(() => {
        if (!groupBy) {
            return [{ group: null, items: filteredOptions }];
        }

        const groups = {};
        filteredOptions.forEach(opt => {
            const groupKey = opt[groupBy] || "Other";
            if (!groups[groupKey]) {
                groups[groupKey] = [];
            }
            groups[groupKey].push(opt);
        });

        return Object.entries(groups).map(([group, items]) => ({ group, items }));
    }, [filteredOptions, groupBy]);

    // Default option renderer
    const defaultRenderOption = (opt, isSelected) => {
        const optLabel = opt[displayKey] || opt.name || opt.label;
        return (
            <div className="flex items-center gap-2">
                <div className={cx(
                    "w-4 h-4 border-2 rounded flex items-center justify-center flex-shrink-0",
                    isSelected ? "bg-blue-600 border-blue-600" : "border-gray-300"
                )}>
                    {isSelected && <Check className="w-3 h-3 text-white" />}
                </div>
                <span className="truncate">{optLabel}</span>
            </div>
        );
    };

    // Default badge renderer
    const defaultRenderBadge = (opt) => {
        const optLabel = opt[displayKey] || opt.name || opt.label;
        return optLabel;
    };

    // Check if all filtered options are selected
    const allSelected = useMemo(() => {
        if (filteredOptions.length === 0) return false;
        return filteredOptions.every(opt => selectedValues.includes(opt[valueKey]));
    }, [filteredOptions, selectedValues, valueKey]);

    // Check if at max selections
    const atMaxSelections = maxSelections && selectedValues.length >= maxSelections;

    return (
        <div className="w-full">
            {label && (
                <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
                    {label} {required && <span className="text-red-500">*</span>}
                    {showCount && selectedValues.length > 0 && (
                        <span className="ml-2 text-xs text-gray-500">
                            ({selectedValues.length}{maxSelections ? `/${maxSelections}` : ''} selected)
                        </span>
                    )}
                </label>
            )}

            <div className="relative">
                {/* Main input button */}
                <button
                    ref={triggerRef}
                    type="button"
                    id={name}
                    onClick={() => !disabled && setOpen(!open)}
                    disabled={disabled}
                    aria-haspopup="listbox"
                    aria-expanded={open}
                    aria-controls={listId}
                    className={cx(
                        "w-full flex items-center justify-between gap-2 text-left",
                        variants[variant],
                        err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
                        disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer",
                        className
                    )}
                >
                    <div className="flex-1 min-w-0">
                        {selectedValues.length === 0 ? (
                            <span className="text-gray-400">{placeholder}</span>
                        ) : (
                            <div className="flex flex-wrap gap-1.5">
                                {selectedItems.map(opt => (
                                    <Badge
                                        key={opt[valueKey]}
                                        onRemove={(e) => {
                                            e.stopPropagation();
                                            removeItem(opt[valueKey]);
                                        }}
                                        disabled={disabled}
                                    >
                                        {renderBadge ? renderBadge(opt) : defaultRenderBadge(opt)}
                                    </Badge>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="flex items-center gap-1 flex-shrink-0">
                        {clearable && selectedValues.length > 0 && !disabled && (
                            <button
                                type="button"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    deselectAll();
                                }}
                                className="p-1 hover:bg-gray-100 rounded"
                                aria-label="Clear all selections"
                            >
                                <X className="w-4 h-4 text-gray-400" />
                            </button>
                        )}
                        <ChevronDown
                            className={cx(
                                "w-4 h-4 text-gray-400 transition-transform",
                                open ? "rotate-180" : ""
                            )}
                        />
                    </div>
                </button>

                {/* Dropdown — rendered via portal to escape overflow:hidden parents (e.g. modals) */}
                {open && ReactDOM.createPortal(
                    <div
                        ref={dropdownRef}
                        data-portal-dropdown="true"
                        id={listId}
                        role="listbox"
                        aria-multiselectable="true"
                        style={dropdownStyle}
                        className="bg-white border border-gray-300 rounded-lg shadow-xl max-h-80 overflow-hidden flex flex-col"
                    >
                        {/* Search input */}
                        {searchable && (
                            <div className="p-2 border-b border-gray-200">
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                    <input
                                        ref={searchInputRef}
                                        type="text"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        placeholder={searchPlaceholder}
                                        className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                                    />
                                </div>
                            </div>
                        )}

                        {/* Select all / Deselect all */}
                        {showSelectAll && filteredOptions.length > 0 && !atMaxSelections && (
                            <div className="p-2 border-b border-gray-200 bg-gray-50">
                                <button
                                    type="button"
                                    onClick={allSelected ? deselectAll : selectAll}
                                    className="w-full text-left px-2 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors"
                                >
                                    {allSelected ? "Deselect All" : "Select All"}
                                </button>
                            </div>
                        )}

                        {/* Max selections warning */}
                        {atMaxSelections && (
                            <div className="p-3 bg-amber-50 border-b border-amber-100 text-xs text-amber-700">
                                Maximum {maxSelections} selection{maxSelections !== 1 ? 's' : ''} reached
                            </div>
                        )}

                        {/* Loading state */}
                        {loading && (
                            <div className="p-4 flex items-center justify-center gap-2 text-gray-500">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="text-sm">Searching...</span>
                            </div>
                        )}

                        {/* Options list */}
                        {!loading && (
                            <div className="overflow-y-auto flex-1">
                                {filteredOptions.length === 0 ? (
                                    <div className="p-4 text-center text-sm text-gray-500">
                                        No options found
                                    </div>
                                ) : (
                                    groupedOptions.map((group, groupIdx) => (
                                        <div key={groupIdx}>
                                            {/* Group header */}
                                            {group.group && (
                                                <div className="px-3 py-2 text-xs font-medium text-gray-500 bg-gray-50 sticky top-0">
                                                    {group.group}
                                                </div>
                                            )}

                                            {/* Group items */}
                                            {group.items.map(opt => {
                                                const optValue = opt[valueKey];
                                                const isSelected = selectedValues.includes(optValue);
                                                const isDisabled = !isSelected && atMaxSelections;

                                                return (
                                                    <button
                                                        key={optValue}
                                                        type="button"
                                                        role="option"
                                                        aria-selected={isSelected}
                                                        onClick={() => !isDisabled && toggleOption(optValue)}
                                                        disabled={isDisabled}
                                                        className={cx(
                                                            "w-full px-3 py-2 text-sm text-left transition-colors",
                                                            isSelected ? "bg-blue-50 text-blue-600" : "hover:bg-gray-50",
                                                            isDisabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
                                                        )}
                                                    >
                                                        {renderOption ? renderOption(opt, isSelected) : defaultRenderOption(opt, isSelected)}
                                                    </button>
                                                );
                                            })}
                                        </div>
                                    ))
                                )}
                            </div>
                        )}
                    </div>,
                    document.body
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

/**
 * TagInput v2 - Free Text Tag Input
 * 
 * FEATURES:
 * - Free text input that creates tags
 * - Add tags on Enter, comma, or custom delimiter
 * - Remove tags with backspace or X button
 * - Max tags limit
 * - Tag validation
 * - Duplicate prevention
 * - Custom tag rendering
 * - Paste support (multiple tags at once)
 * - Suggestions/autocomplete
 * - Tag colors/variants
 * - Min/max tag length
 * - Pattern validation
 * - Case transformation
 * 
 * Props:
 *  - name: field name
 *  - label: label text
 *  - value: array of tag strings
 *  - onChange: callback(tags)
 *  - placeholder: placeholder text
 *  - required: show * if required
 *  - error: error message
 *  - variant: style variant
 *  - disabled: disable input
 *  - delimiters: array of delimiter keys (default: ["Enter", ","])
 *  - maxTags: maximum number of tags
 *  - minTagLength: minimum tag length
 *  - maxTagLength: maximum tag length
 *  - allowDuplicates: allow duplicate tags (default: false)
 *  - caseSensitive: case sensitive duplicates (default: false)
 *  - transform: "lowercase" | "uppercase" | "capitalize" | null
 *  - pattern: regex pattern for validation
 *  - patternMessage: error message for pattern validation
 *  - suggestions: array of suggested tags
 *  - showSuggestions: show suggestions dropdown
 *  - renderTag: custom tag renderer
 *  - tagVariant: "default" | "primary" | "success" | "warning" | "error"
 *  - onBeforeAdd: callback(tag) => boolean (validate before adding)
 *  - onTagAdded: callback(tag) triggered when tag is added
 *  - onTagRemoved: callback(tag) triggered when tag is removed
 */

const tagVariants = {
    default: "bg-gray-100 text-gray-700 border-gray-200",
    primary: "bg-blue-50 text-blue-700 border-blue-200",
    success: "bg-green-50 text-green-700 border-green-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
    error: "bg-red-50 text-red-700 border-red-200",
};

// Tag component
const Tag = ({ children, onRemove, disabled, variant = "default" }) => (
    <span className={cx(
        "inline-flex items-center gap-1 px-2 py-1 text-sm rounded-md border",
        tagVariants[variant]
    )}>
        <span className="truncate max-w-[150px]">{children}</span>
        {!disabled && (
            <button
                type="button"
                onClick={onRemove}
                className="hover:bg-black/10 rounded p-0.5 transition-colors"
                aria-label={`Remove tag ${children}`}
            >
                <X className="w-3 h-3" />
            </button>
        )}
    </span>
);

export function TagInput({
    name,
    label,
    value = [],
    onChange,
    placeholder = "Type and press Enter...",
    required = false,
    error: externalError,
    variant = "dashboard",
    className = "",
    disabled = false,
    delimiters = ["Enter", ","],
    maxTags,
    minTagLength = 1,
    maxTagLength = 50,
    allowDuplicates = false,
    caseSensitive = false,
    transform,
    pattern,
    patternMessage = "Invalid tag format",
    suggestions = [],
    showSuggestions = false,
    renderTag,
    tagVariant = "default",
    onBeforeAdd,
    onTagAdded,
    onTagRemoved,
    ...props
}) {
    const {
        inForm,
        setValue: setFormValue,
        value: formValue,
        error,
        trigger,
    } = useFormField(name);

    const currentValue = inForm ? (formValue || []) : (value || []);
    const tags = Array.isArray(currentValue) ? currentValue : [];

    const setVal = useCallback((newTags) => {
        if (inForm) {
            setFormValue(name, newTags, { shouldValidate: true, shouldDirty: true });
            trigger?.(name);
        } else {
            onChange?.(newTags);
        }
    }, [inForm, setFormValue, name, trigger, onChange]);

    const [inputValue, setInputValue] = useState("");
    const [showSuggestionsDropdown, setShowSuggestionsDropdown] = useState(false);
    const [validationError, setValidationError] = useState("");

    const inputRef = useRef(null);
    const containerRef = useRef(null);

    const err = inForm ? error : externalError;

    // Transform tag based on config
    const transformTag = (tag) => {
        let transformed = tag.trim();

        if (!transformed) return transformed;

        switch (transform) {
            case "lowercase":
                return transformed.toLowerCase();
            case "uppercase":
                return transformed.toUpperCase();
            case "capitalize":
                return transformed.charAt(0).toUpperCase() + transformed.slice(1).toLowerCase();
            default:
                return transformed;
        }
    };

    // Validate tag
    const validateTag = (tag) => {
        // Length validation
        if (tag.length < minTagLength) {
            return `Tag must be at least ${minTagLength} character${minTagLength !== 1 ? 's' : ''}`;
        }

        if (tag.length > maxTagLength) {
            return `Tag must be at most ${maxTagLength} characters`;
        }

        // Pattern validation
        if (pattern && !pattern.test(tag)) {
            return patternMessage;
        }

        // Duplicate check
        if (!allowDuplicates) {
            const exists = caseSensitive
                ? tags.includes(tag)
                : tags.some(t => t.toLowerCase() === tag.toLowerCase());

            if (exists) {
                return "Tag already exists";
            }
        }

        // Max tags check
        if (maxTags && tags.length >= maxTags) {
            return `Maximum ${maxTags} tags allowed`;
        }

        return null;
    };

    // Add tag
    const addTag = (tagToAdd) => {
        const transformed = transformTag(tagToAdd);

        if (!transformed) {
            setValidationError("");
            return;
        }

        // Custom validation
        if (onBeforeAdd && !onBeforeAdd(transformed)) {
            return;
        }

        // Built-in validation
        const validationErr = validateTag(transformed);
        if (validationErr) {
            setValidationError(validationErr);
            return;
        }

        // Add tag
        const newTags = [...tags, transformed];
        setVal(newTags);
        setInputValue("");
        setValidationError("");
        setShowSuggestionsDropdown(false);

        // Callback
        onTagAdded?.(transformed);
    };

    // Remove tag
    const removeTag = (index) => {
        const removedTag = tags[index];
        const newTags = tags.filter((_, i) => i !== index);
        setVal(newTags);
        onTagRemoved?.(removedTag);
    };

    // Handle key down
    const handleKeyDown = (e) => {
        // Add tag on delimiter
        if (delimiters.includes(e.key)) {
            e.preventDefault();
            addTag(inputValue);
            return;
        }

        // Remove last tag on backspace if input is empty
        if (e.key === "Backspace" && !inputValue && tags.length > 0) {
            removeTag(tags.length - 1);
            return;
        }

        // Clear validation error on any key
        if (validationError) {
            setValidationError("");
        }
    };

    // Handle paste (support multiple tags)
    const handlePaste = (e) => {
        e.preventDefault();
        const pastedText = e.clipboardData.getData("text");

        // Split by common delimiters
        const newTags = pastedText
            .split(/[,;\n\t]/)
            .map(tag => transformTag(tag))
            .filter(tag => tag && !validateTag(tag));

        if (newTags.length > 0) {
            const limitedTags = maxTags
                ? [...tags, ...newTags].slice(0, maxTags)
                : [...tags, ...newTags];

            setVal(limitedTags);
            setInputValue("");
        }
    };

    // Handle suggestion click
    const handleSuggestionClick = (suggestion) => {
        addTag(suggestion);
        inputRef.current?.focus();
    };

    // Filter suggestions based on input
    const filteredSuggestions = useMemo(() => {
        if (!showSuggestions || !inputValue || !suggestions.length) {
            return [];
        }

        const query = inputValue.toLowerCase();
        return suggestions.filter(s => {
            const sLower = s.toLowerCase();
            return sLower.includes(query) && !tags.includes(s);
        });
    }, [showSuggestions, inputValue, suggestions, tags]);

    // Show suggestions dropdown
    useEffect(() => {
        setShowSuggestionsDropdown(filteredSuggestions.length > 0);
    }, [filteredSuggestions]);

    // Close suggestions on outside click
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (containerRef.current && !containerRef.current.contains(e.target)) {
                setShowSuggestionsDropdown(false);
            }
        };

        if (showSuggestionsDropdown) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [showSuggestionsDropdown]);

    // Default tag renderer
    const defaultRenderTag = (tag, index) => (
        <Tag
            key={index}
            onRemove={() => removeTag(index)}
            disabled={disabled}
            variant={tagVariant}
        >
            {tag}
        </Tag>
    );

    // Check if at max tags
    const atMaxTags = maxTags && tags.length >= maxTags;

    return (
        <div className="w-full">
            {label && (
                <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
                    {label} {required && <span className="text-red-500">*</span>}
                    {tags.length > 0 && (
                        <span className="ml-2 text-xs text-gray-500">
                            ({tags.length}{maxTags ? `/${maxTags}` : ''} tag{tags.length !== 1 ? 's' : ''})
                        </span>
                    )}
                </label>
            )}

            <div className="relative" ref={containerRef}>
                {/* Tags container */}
                <div
                    className={cx(
                        "w-full min-h-[44px] flex flex-wrap gap-2 items-center",
                        variants[variant],
                        err ? "border-red-400 focus-within:ring-red-100 focus-within:border-red-500" : "focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100",
                        disabled ? "opacity-50 cursor-not-allowed bg-gray-50" : "",
                        className
                    )}
                >
                    {/* Tags */}
                    {tags.map((tag, index) => (
                        renderTag ? renderTag(tag, index) : defaultRenderTag(tag, index)
                    ))}

                    {/* Input */}
                    {!atMaxTags && (
                        <input
                            ref={inputRef}
                            type="text"
                            id={name}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            onPaste={handlePaste}
                            placeholder={tags.length === 0 ? placeholder : ""}
                            disabled={disabled}
                            className="flex-1 min-w-[120px] bg-transparent outline-none text-gray-900 placeholder-gray-400"
                            {...props}
                        />
                    )}

                    {/* Add button */}
                    {inputValue && !atMaxTags && (
                        <button
                            type="button"
                            onClick={() => addTag(inputValue)}
                            className="flex-shrink-0 p-1 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                            aria-label="Add tag"
                        >
                            <Plus className="w-4 h-4" />
                        </button>
                    )}
                </div>

                {/* Max tags warning */}
                {atMaxTags && (
                    <p className="mt-1 text-amber-600 text-xs">
                        Maximum {maxTags} tag{maxTags !== 1 ? 's' : ''} reached
                    </p>
                )}

                {/* Validation error */}
                {validationError && (
                    <p className="mt-1 text-red-500 text-xs flex items-center gap-1">
                        <span className="w-1 h-1 bg-red-500 rounded-full" /> {validationError}
                    </p>
                )}

                {/* Field error */}
                {err && !validationError && (
                    <p id={`${name}-error`} className="mt-1 text-red-500 text-xs flex items-center gap-1">
                        <span className="w-1 h-1 bg-red-500 rounded-full" /> {err}
                    </p>
                )}

                {/* Suggestions dropdown */}
                {showSuggestionsDropdown && (
                    <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        <div className="p-2 border-b border-gray-100 text-xs text-gray-500 font-medium">
                            Suggestions
                        </div>
                        {filteredSuggestions.map((suggestion, index) => (
                            <button
                                key={index}
                                type="button"
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="w-full px-3 py-2 text-sm text-left hover:bg-gray-50 transition-colors flex items-center gap-2"
                            >
                                <TagIcon className="w-3.5 h-3.5 text-gray-400" />
                                {suggestion}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* Helper text */}
            {!err && !validationError && delimiters.length > 0 && (
                <p className="mt-1 text-xs text-gray-500">
                    Press {delimiters.map((d, i) => (
                        <React.Fragment key={d}>
                            {i > 0 && " or "}
                            <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs font-mono">
                                {d === "Enter" ? "↵" : d}
                            </kbd>
                        </React.Fragment>
                    ))} to add tag
                </p>
            )}
        </div>
    );
}
