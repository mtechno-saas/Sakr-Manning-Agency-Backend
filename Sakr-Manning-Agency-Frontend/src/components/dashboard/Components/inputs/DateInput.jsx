import React, { useState, useRef, useEffect, useMemo } from "react";
import { Calendar, ChevronDown, Clock, X } from "lucide-react";
import { useFormField, cx } from "../../../../hooks/useFormField";

import {
    formatDate,
    formatDateDisplay,
    getToday,
    getTomorrow,
    addDays,
    addMonths,
    daysBetween,
    isPastDate,
    isFutureDate,
    isToday,
    datePresets,
} from "../../../../utils/dashboard/dateHelpers";

/**
 * DateInput v2 - Enhanced Date Picker
 * 
 * NEW FEATURES:
 * - Quick select buttons (Today, Tomorrow, Next Week, etc.)
 * - Working days calculator
 * - Custom date presets
 * - Better visual feedback
 * - Disabled dates support
 * - Business days calculation
 * - Holiday support
 * - Better mobile support
 * - Clear button
 * - Relative date display ("Today", "Tomorrow", "In 3 days")
 * 
 * Props:
 *  - name: field name
 *  - label: label text
 *  - placeholder: placeholder text
 *  - required: show * if required
 *  - min: minimum date (YYYY-MM-DD)
 *  - max: maximum date (YYYY-MM-DD)
 *  - value: controlled value
 *  - onChange: callback(value)
 *  - error: error message
 *  - variant: style variant
 *  - showCalendarIcon: show calendar icon
 *  - disabled: disable input
 * 
 * NEW PROPS:
 *  - quickSelects: array of preset keys ["today", "tomorrow", "nextWeek", "nextMonth"]
 *  - showWorkingDays: show working days from today
 *  - showRelativeDate: show "Today", "Tomorrow", "In X days"
 *  - disabledDates: array of dates to disable (YYYY-MM-DD)
 *  - disabledDaysOfWeek: array of day numbers to disable (0=Sunday, 6=Saturday)
 *  - holidays: array of holiday dates (YYYY-MM-DD)
 *  - countBusinessDays: count only business days (excludes weekends + holidays)
 *  - showClearButton: show clear button
 *  - customPresets: custom quick select presets { label, getValue: () => date }
 */

const variants = {
    default: "font-poppins bg-white border border-black/50 rounded-[8px] py-3 px-4 shadow-md",
    calendar: "bg-white border border-black/50 rounded-[15px] shadow-md p-4 font-inter",
    bordered: "bg-white border border-[#91BBE1] rounded-[8px] p-2 font-inter",
    shadowed: "font-poppins bg-white border border-gray-300 rounded-[8px] p-2 shadow-lg",
    light: "font-inter bg-gray-50 border border-gray-200 rounded-[8px] p-2 focus:ring-1 focus:ring-blue-300",
    dashboard: "font-inter bg-white border border-gray-300 rounded-lg py-2 px-3 text-sm shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400 transition-all duration-200",
};

// Default quick select presets
const defaultPresets = {
    today: { label: "Today", getValue: () => getToday() },
    tomorrow: { label: "Tomorrow", getValue: () => getTomorrow() },
    nextWeek: { label: "Next Week", getValue: () => addDays(getToday(), 7) },
    next2Weeks: { label: "2 Weeks", getValue: () => addDays(getToday(), 14) },
    nextMonth: { label: "Next Month", getValue: () => addMonths(getToday(), 1) },
    next3Months: { label: "3 Months", getValue: () => addMonths(getToday(), 3) },
    next6Months: { label: "6 Months", getValue: () => addMonths(getToday(), 6) },
    nextYear: { label: "Next Year", getValue: () => addMonths(getToday(), 12) },
};

// Calculate business days (excluding weekends and holidays)
const calculateBusinessDays = (startDate, endDate, holidays = []) => {
    if (!startDate || !endDate) return 0;

    const start = new Date(startDate);
    const end = new Date(endDate);
    let count = 0;

    const holidaySet = new Set(holidays);

    for (let date = new Date(start); date <= end; date.setDate(date.getDate() + 1)) {
        const dayOfWeek = date.getDay();
        const dateStr = formatDate(date);

        // Skip weekends (Saturday = 6, Sunday = 0)
        if (dayOfWeek === 0 || dayOfWeek === 6) continue;

        // Skip holidays
        if (holidaySet.has(dateStr)) continue;

        count++;
    }

    return count;
};

// Get relative date display
const getRelativeDisplay = (dateStr) => {
    if (!dateStr) return null;

    if (isToday(dateStr)) return "Today";

    const tomorrow = getTomorrow();
    if (dateStr === tomorrow) return "Tomorrow";

    const yesterday = addDays(getToday(), -1);
    if (dateStr === yesterday) return "Yesterday";

    const days = daysBetween(getToday(), dateStr);

    if (days > 0 && days <= 7) return `In ${days} day${days > 1 ? 's' : ''}`;
    if (days < 0 && days >= -7) return `${Math.abs(days)} day${Math.abs(days) > 1 ? 's' : ''} ago`;

    return null;
};

export function DateInput({
    name,
    label,
    placeholder = "Select a date",
    rules = {},
    required = false,
    min,
    max,
    value,
    onChange,
    onBlur,
    error: externalError,
    variant = "dashboard",
    className = "",
    showCalendarIcon = false,
    disabled = false,
    // NEW PROPS
    quickSelects = [],
    showWorkingDays = false,
    showRelativeDate = false,
    disabledDates = [],
    disabledDaysOfWeek = [],
    holidays = [],
    countBusinessDays = false,
    showClearButton = true,
    customPresets = {},
    ...props
}) {
    const { inForm, register, error, setValue, getValues, watch } = useFormField(name);
    const err = inForm ? error : externalError;
    const inputRef = useRef(null);

    const [isFocused, setIsFocused] = useState(false);
    const [hasValue, setHasValue] = useState(() => {
        if (inForm && typeof getValues === "function") {
            const formValue = getValues(name);
            if (formValue) return true;
            const watchedValue = watch?.(name);
            return !!watchedValue;
        }
        return !!value;
    });

    const currentValue = inForm ? watch?.(name) || "" : value || "";

    useEffect(() => {
        setHasValue(!!currentValue);
    }, [currentValue]);

    // Merge validation rules
    const validationRules = { ...rules };
    if (required && !validationRules.required) {
        validationRules.required = "This field is required";
    }

    const handleFocus = () => {
        setIsFocused(true);
        if (inputRef.current) {
            inputRef.current.showPicker?.();
        }
    };

    const handleBlur = (e) => {
        setIsFocused(false);
        setHasValue(!!e.target.value);
        onBlur?.(e);
    };

    const handleChange = (e) => {
        const newValue = e.target.value;
        setHasValue(!!newValue);

        if (inForm) {
            setValue?.(name, newValue);
        } else {
            onChange?.(newValue);
        }
    };

    const handleQuickSelect = (presetKey) => {
        const preset = customPresets[presetKey] || defaultPresets[presetKey];
        if (!preset) return;

        const dateValue = preset.getValue();
        setHasValue(!!dateValue);

        if (inForm) {
            setValue?.(name, dateValue);
        } else {
            onChange?.(dateValue);
        }

        // Trigger validation if in form
        if (inForm && inputRef.current) {
            inputRef.current.dispatchEvent(new Event("change", { bubbles: true }));
        }
    };

    const handleClear = () => {
        setHasValue(false);
        if (inForm) {
            setValue?.(name, "");
        } else {
            onChange?.("");
        }
    };

    // Check if date is disabled
    const isDateDisabled = (dateStr) => {
        if (!dateStr) return false;

        // Check disabled dates array
        if (disabledDates.includes(dateStr)) return true;

        // Check disabled days of week
        if (disabledDaysOfWeek.length > 0) {
            const date = new Date(dateStr);
            if (disabledDaysOfWeek.includes(date.getDay())) return true;
        }

        return false;
    };

    // Calculate days info
    const daysInfo = useMemo(() => {
        if (!currentValue || (!showWorkingDays && !countBusinessDays)) return null;

        const today = getToday();
        const totalDays = daysBetween(today, currentValue);

        if (totalDays <= 0) return null;

        const businessDays = countBusinessDays
            ? calculateBusinessDays(today, currentValue, holidays)
            : null;

        return { totalDays, businessDays };
    }, [currentValue, showWorkingDays, countBusinessDays, holidays]);

    // Relative date display
    const relativeDisplay = useMemo(() => {
        if (!showRelativeDate || !currentValue) return null;
        return getRelativeDisplay(currentValue);
    }, [showRelativeDate, currentValue]);

    // Combined presets
    const availablePresets = useMemo(() => {
        return quickSelects.map(key => ({
            key,
            ...(customPresets[key] || defaultPresets[key])
        })).filter(p => p.label);
    }, [quickSelects, customPresets]);

    return (
        <div className="w-full">
            {label && (
                <label
                    htmlFor={name}
                    className="block text-sm font-medium text-gray-700 mb-2"
                >
                    {label} {required && <span className="text-red-500">*</span>}
                </label>
            )}

            <div className="space-y-2">
                {/* Quick select buttons */}
                {availablePresets.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                        {availablePresets.map(preset => (
                            <button
                                key={preset.key}
                                type="button"
                                onClick={() => handleQuickSelect(preset.key)}
                                disabled={disabled}
                                className={cx(
                                    "px-2 py-1 text-[10px] font-medium rounded-md transition-colors",
                                    "border border-gray-300 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-600",
                                    disabled && "opacity-50 cursor-not-allowed"
                                )}
                            >
                                {preset.label}
                            </button>
                        ))}
                    </div>
                )}

                {/* Date input container */}
                <div className="relative">
                    {/* Custom placeholder overlay */}
                    {!hasValue && !isFocused && (
                        <div
                            className="absolute inset-0 flex items-center px-4 pointer-events-none z-10"
                            onClick={() => inputRef.current?.focus()}
                        >
                            <span className="text-gray-400 text-sm select-none">
                                {placeholder}
                            </span>
                        </div>
                    )}

                    {/* Actual date input */}
                    <input
                        ref={inputRef}
                        id={name}
                        name={name}
                        type="date"
                        min={min}
                        max={max}
                        required={required}
                        disabled={disabled}
                        aria-invalid={!!err}
                        aria-describedby={err ? `${name}-error` : undefined}
                        {...(inForm
                            ? {
                                ...register(name, validationRules),
                                onChange: (e) => {
                                    register(name, validationRules).onChange(e);
                                    handleChange(e);
                                },
                            }
                            : {
                                value: currentValue,
                                onChange: handleChange,
                                onBlur: handleBlur,
                            })}
                        onFocus={handleFocus}
                        onBlur={handleBlur}
                        className={cx(
                            "w-full relative",
                            variants[variant] ?? variants.default,
                            !hasValue && !isFocused ? "text-transparent" : "text-gray-900",
                            err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "",
                            showCalendarIcon ? "pr-10" : "",
                            showClearButton && hasValue ? "pr-20" : "",
                            disabled && "opacity-50 cursor-not-allowed",
                            className
                        )}
                        style={{
                            colorScheme: "light",
                            ...(!isFocused && {
                                color: "transparent",
                            }),
                            caretColor: isFocused ? "black" : "transparent",
                        }}
                        {...props}
                    />

                    {/* Icons container */}
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                        {/* Clear button */}
                        {showClearButton && hasValue && !disabled && (
                            <button
                                type="button"
                                onClick={handleClear}
                                className="p-1 hover:bg-gray-100 rounded transition-colors"
                                aria-label="Clear date"
                            >
                                <X className="w-4 h-4 text-gray-400" />
                            </button>
                        )}

                        {/* Calendar icon */}
                        {showCalendarIcon && (
                            <div className="text-gray-400 pointer-events-none" aria-hidden="true">
                                <Calendar className="w-4 h-4" />
                            </div>
                        )}
                    </div>

                    {/* Value display with relative date */}
                    {hasValue && !isFocused && currentValue && (
                        <div className="absolute inset-0 flex items-center px-4 pointer-events-none bg-transparent">
                            <div className="flex items-center gap-2">
                                <span className="text-gray-700 text-sm">
                                    {formatDateDisplay(currentValue)}
                                </span>
                                {relativeDisplay && (
                                    <span className="text-xs text-blue-600 font-medium">
                                        ({relativeDisplay})
                                    </span>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* Working days info */}
                {daysInfo && (
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                        <Clock className="w-3.5 h-3.5" />
                        <span>
                            {daysInfo.totalDays} day{daysInfo.totalDays !== 1 ? 's' : ''}
                            {daysInfo.businessDays !== null && (
                                <> ({daysInfo.businessDays} business day{daysInfo.businessDays !== 1 ? 's' : ''})</>
                            )}
                        </span>
                    </div>
                )}
            </div>

            {err && (
                <p
                    id={`${name}-error`}
                    className="mt-1 text-red-500 text-xs flex items-center gap-1"
                >
                    <span className="w-1 h-1 bg-red-500 rounded-full" /> {err}
                </p>
            )}
        </div>
    );
}

/**
 * DateRangeInput v2 - Date Range Picker
 * 
 * FEATURES:
 * - Start and end date selection
 * - Automatic validation (end >= start)
 * - Quick select presets (This Week, This Month, etc.)
 * - Duration display
 * - Business days calculation
 * - Swap dates button
 * - Clear both dates
 * - Min/max range validation
 * 
 * Props:
 *  - nameStart: field name for start date
 *  - nameEnd: field name for end date
 *  - label: label text
 *  - required: show * if required
 *  - minDate: minimum allowed date
 *  - maxDate: maximum allowed date
 *  - minRange: minimum days between dates
 *  - maxRange: maximum days between dates
 *  - valueStart: controlled start value
 *  - valueEnd: controlled end value
 *  - onChangeStart: callback(value)
 *  - onChangeEnd: callback(value)
 *  - errorStart: start date error
 *  - errorEnd: end date error
 *  - variant: style variant
 *  - disabled: disable inputs
 *  - quickSelects: array of preset keys
 *  - showDuration: show duration between dates
 *  - countBusinessDays: count only business days
 *  - holidays: array of holiday dates
 *  - showSwapButton: show button to swap dates
 */

export function DateRangeInput({
    nameStart,
    nameEnd,
    label,
    required = false,
    minDate,
    maxDate,
    minRange,
    maxRange,
    valueStart,
    valueEnd,
    onChangeStart,
    onChangeEnd,
    errorStart: externalErrorStart,
    errorEnd: externalErrorEnd,
    variant = "dashboard",
    className = "",
    disabled = false,
    quickSelects = [],
    showDuration = true,
    countBusinessDays = false,
    holidays = [],
    showSwapButton = false,
    ...props
}) {
    // Form field hooks for both dates
    const {
        inForm: inFormStart,
        setValue: setValueStart,
        watch: watchStart,
        error: errorStart,
    } = useFormField(nameStart);

    const {
        inForm: inFormEnd,
        setValue: setValueEnd,
        watch: watchEnd,
        error: errorEnd,
    } = useFormField(nameEnd);

    const currentStartValue = inFormStart ? watchStart?.(nameStart) || "" : valueStart || "";
    const currentEndValue = inFormEnd ? watchEnd?.(nameEnd) || "" : valueEnd || "";

    const errStart = inFormStart ? errorStart : externalErrorStart;
    const errEnd = inFormEnd ? errorEnd : externalErrorEnd;

    // Quick select presets for ranges
    const rangePresets = {
        thisWeek: {
            label: "This Week",
            getValue: () => {
                const today = new Date();
                const dayOfWeek = today.getDay();
                const start = addDays(formatDate(today), -(dayOfWeek === 0 ? 6 : dayOfWeek - 1));
                const end = addDays(start, 6);
                return { start, end };
            },
        },
        nextWeek: {
            label: "Next Week",
            getValue: () => {
                const today = new Date();
                const dayOfWeek = today.getDay();
                const start = addDays(formatDate(today), 7 - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
                const end = addDays(start, 6);
                return { start, end };
            },
        },
        thisMonth: {
            label: "This Month",
            getValue: () => {
                const today = new Date();
                const start = formatDate(new Date(today.getFullYear(), today.getMonth(), 1));
                const end = formatDate(new Date(today.getFullYear(), today.getMonth() + 1, 0));
                return { start, end };
            },
        },
        nextMonth: {
            label: "Next Month",
            getValue: () => {
                const today = new Date();
                const start = formatDate(new Date(today.getFullYear(), today.getMonth() + 1, 1));
                const end = formatDate(new Date(today.getFullYear(), today.getMonth() + 2, 0));
                return { start, end };
            },
        },
        next30Days: {
            label: "Next 30 Days",
            getValue: () => {
                const start = getToday();
                const end = addDays(start, 30);
                return { start, end };
            },
        },
        next90Days: {
            label: "Next 90 Days",
            getValue: () => {
                const start = getToday();
                const end = addDays(start, 90);
                return { start, end };
            },
        },
    };

    const handleStartChange = (newValue) => {
        if (inFormStart) {
            setValueStart?.(nameStart, newValue);
        } else {
            onChangeStart?.(newValue);
        }

        // Auto-adjust end date if it's before start
        if (newValue && currentEndValue && newValue > currentEndValue) {
            if (inFormEnd) {
                setValueEnd?.(nameEnd, newValue);
            } else {
                onChangeEnd?.(newValue);
            }
        }
    };

    const handleEndChange = (newValue) => {
        if (inFormEnd) {
            setValueEnd?.(nameEnd, newValue);
        } else {
            onChangeEnd?.(newValue);
        }

        // Auto-adjust start date if it's after end
        if (newValue && currentStartValue && newValue < currentStartValue) {
            if (inFormStart) {
                setValueStart?.(nameStart, newValue);
            } else {
                onChangeStart?.(newValue);
            }
        }
    };

    const handleQuickSelect = (presetKey) => {
        const preset = rangePresets[presetKey];
        if (!preset) return;

        const { start, end } = preset.getValue();

        if (inFormStart) {
            setValueStart?.(nameStart, start);
        } else {
            onChangeStart?.(start);
        }

        if (inFormEnd) {
            setValueEnd?.(nameEnd, end);
        } else {
            onChangeEnd?.(end);
        }
    };

    const handleSwap = () => {
        const tempStart = currentStartValue;
        const tempEnd = currentEndValue;

        if (inFormStart) {
            setValueStart?.(nameStart, tempEnd);
        } else {
            onChangeStart?.(tempEnd);
        }

        if (inFormEnd) {
            setValueEnd?.(nameEnd, tempStart);
        } else {
            onChangeEnd?.(tempStart);
        }
    };

    const handleClearBoth = () => {
        if (inFormStart) {
            setValueStart?.(nameStart, "");
        } else {
            onChangeStart?.("");
        }

        if (inFormEnd) {
            setValueEnd?.(nameEnd, "");
        } else {
            onChangeEnd?.("");
        }
    };

    // Calculate duration
    const durationInfo = useMemo(() => {
        if (!currentStartValue || !currentEndValue || !showDuration) return null;

        const totalDays = daysBetween(currentStartValue, currentEndValue);
        if (totalDays < 0) return null;

        const businessDays = countBusinessDays
            ? calculateBusinessDays(currentStartValue, currentEndValue, holidays)
            : null;

        return { totalDays, businessDays };
    }, [currentStartValue, currentEndValue, showDuration, countBusinessDays, holidays]);

    // Available presets
    const availablePresets = useMemo(() => {
        return quickSelects.map(key => ({
            key,
            ...rangePresets[key]
        })).filter(p => p.label);
    }, [quickSelects]);

    // Calculate min/max for end date based on start date and constraints
    const endDateMin = useMemo(() => {
        if (!currentStartValue) return minDate;

        if (minRange) {
            const minEndDate = addDays(currentStartValue, minRange);
            return minDate && minEndDate < minDate ? minDate : minEndDate;
        }

        return currentStartValue > (minDate || "") ? currentStartValue : minDate;
    }, [currentStartValue, minDate, minRange]);

    const endDateMax = useMemo(() => {
        if (!currentStartValue || !maxRange) return maxDate;

        const maxEndDate = addDays(currentStartValue, maxRange);
        return maxDate && maxEndDate > maxDate ? maxDate : maxEndDate;
    }, [currentStartValue, maxDate, maxRange]);

    return (
        <div className="w-full">
            {label && (
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    {label} {required && <span className="text-red-500">*</span>}
                </label>
            )}

            <div className="space-y-3">
                {/* Quick select buttons */}
                {availablePresets.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                        {availablePresets.map(preset => (
                            <button
                                key={preset.key}
                                type="button"
                                onClick={() => handleQuickSelect(preset.key)}
                                disabled={disabled}
                                className={cx(
                                    "px-2 py-1 text-[10px] font-medium rounded-md transition-colors",
                                    "border border-gray-300 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-600",
                                    disabled && "opacity-50 cursor-not-allowed"
                                )}
                            >
                                {preset.label}
                            </button>
                        ))}
                    </div>
                )}

                {/* Date inputs */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {/* Start Date */}
                    <div>
                        <label
                            htmlFor={nameStart}
                            className="block text-xs font-medium text-gray-600 mb-1"
                        >
                            Start Date
                        </label>
                        <DateInput
                            name={nameStart}
                            placeholder="Start date"
                            variant={variant}
                            min={minDate}
                            max={currentEndValue || maxDate}
                            value={currentStartValue}
                            onChange={handleStartChange}
                            error={errStart}
                            disabled={disabled}
                            showCalendarIcon
                            showClearButton={false}
                            className={className}
                        />
                    </div>

                    {/* End Date */}
                    <div>
                        <label
                            htmlFor={nameEnd}
                            className="block text-xs font-medium text-gray-600 mb-1"
                        >
                            End Date
                        </label>
                        <DateInput
                            name={nameEnd}
                            placeholder="End date"
                            variant={variant}
                            min={endDateMin}
                            max={endDateMax}
                            value={currentEndValue}
                            onChange={handleEndChange}
                            error={errEnd}
                            disabled={disabled}
                            showCalendarIcon
                            showClearButton={false}
                            className={className}
                        />
                    </div>
                </div>

                {/* Duration and actions */}
                {(durationInfo || showSwapButton) && (
                    <div className="flex items-center justify-between">
                        {/* Duration display */}
                        {durationInfo && (
                            <div className="flex items-center gap-2 text-xs text-gray-600">
                                <Clock className="w-3.5 h-3.5" />
                                <span>
                                    {durationInfo.totalDays + 1} day{durationInfo.totalDays + 1 !== 1 ? 's' : ''}
                                    {durationInfo.businessDays !== null && (
                                        <> ({durationInfo.businessDays} business day{durationInfo.businessDays !== 1 ? 's' : ''})</>
                                    )}
                                </span>
                            </div>
                        )}

                        {/* Action buttons */}
                        <div className="flex items-center gap-2">
                            {showSwapButton && currentStartValue && currentEndValue && (
                                <button
                                    type="button"
                                    onClick={handleSwap}
                                    disabled={disabled}
                                    className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                                >
                                    ↔ Swap
                                </button>
                            )}
                            {(currentStartValue || currentEndValue) && (
                                <button
                                    type="button"
                                    onClick={handleClearBoth}
                                    disabled={disabled}
                                    className="text-xs text-gray-500 hover:text-gray-700 font-medium"
                                >
                                    Clear All
                                </button>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
