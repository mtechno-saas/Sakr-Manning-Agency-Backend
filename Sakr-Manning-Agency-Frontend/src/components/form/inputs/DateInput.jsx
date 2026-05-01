import React, { useState, useRef, useEffect, useCallback } from "react";
import { useFormField, cx } from "../../../hooks/useFormField";

// ============================================================================
// SHARED
// ============================================================================

const variants = {
  default:
    "font-poppins bg-white border-2 border-gray-300 rounded-xl shadow-md hover:border-gray-400 hover:shadow-lg focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  calendar:
    "bg-white border-2 border-gray-300 rounded-xl shadow-md hover:border-gray-400 font-inter focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  outlined:
    "bg-white border-2 border-gray-300 rounded-xl hover:border-gray-300 font-inter focus-within:border-gray-500 focus-within:ring-2 focus-within:ring-gray-100 transition-all duration-200",
  shadowed:
    "font-poppins bg-white border-2 border-gray-300 rounded-xl shadow-lg hover:shadow-xl focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  light:
    "font-inter bg-gray-50 border-2 border-gray-200 rounded-xl hover:border-gray-300 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  dashboard:
    "font-inter bg-white border-2 border-gray-300 rounded-lg shadow-sm hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  modal:
    "font-poppins bg-gray-50 border border-gray-200 rounded-lg hover:border-gray-300 focus-within:border-[#0065AF] focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
};

// ============================================================================
// CONVERSION HELPERS
// ============================================================================

/**
 * Convert YYYY-MM-DD (backend) → DD/MM/YYYY (display)
 */
function isoToDisplay(iso) {
  if (!iso) return "";
  const parts = iso.split("-");
  if (parts.length !== 3) return "";
  const [y, m, d] = parts;
  return `${d}-${m}-${y}`;
}

/**
 * Convert DD/MM/YYYY (display) → YYYY-MM-DD (backend)
 */
function displayToIso(display) {
  if (!display) return "";
  const parts = display.split("-");
  if (parts.length !== 3 || parts[2].length !== 4) return "";
  const [d, m, y] = parts;
  return `${y}-${m}-${d}`;
}

/**
 * Format raw digits typed by the user into DD/MM/YYYY as they type.
 */
function autoFormatDigits(raw) {
  const digits = raw.replace(/\D/g, "").slice(0, 8);
  const d = digits.slice(0, 2);
  const m = digits.slice(2, 4);
  const y = digits.slice(4, 8);
  return [d, m, y].filter(Boolean).join("-");
}

/**
 * Validate a DD/MM/YYYY string represents a real calendar date.
 */
function isCompleteAndValid(display) {
  if (!display || display.length !== 10) return false;
  const parts = display.split("-");
  if (parts.length !== 3) return false;
  const [d, m, y] = parts.map(Number);
  if (!y || y < 1800 || y > 2100) return false;
  if (!m || m < 1 || m > 12) return false;
  if (!d || d < 1 || d > 31) return false;
  const date = new Date(y, m - 1, d);
  return (
    date.getFullYear() === y &&
    date.getMonth() === m - 1 &&
    date.getDate() === d
  );
}

/**
 * Try to parse a pasted string into YYYY-MM-DD.
 * Supports: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, YYYY-MM-DD, YYYY/MM/DD, ISO 8601.
 */
function parsePastedDate(text) {
  const t = text.trim();

  // ISO 8601 with time (e.g. "2025-01-15T00:00:00Z")
  if (/^\d{4}-\d{2}-\d{2}T/.test(t)) {
    const iso = t.slice(0, 10);
    const [y, m, d] = iso.split("-").map(Number);
    const date = new Date(y, m - 1, d);
    if (date.getFullYear() === y && date.getMonth() === m - 1 && date.getDate() === d) {
      return iso;
    }
  }

  // YYYY-MM-DD or YYYY/MM/DD
  const ymdMatch = t.match(/^(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})$/);
  if (ymdMatch) {
    const [, y, m, d] = ymdMatch;
    const iso = `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`;
    const date = new Date(+y, +m - 1, +d);
    if (date.getFullYear() === +y && date.getMonth() === +m - 1 && date.getDate() === +d) {
      return iso;
    }
  }

  // DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
  const dmyMatch = t.match(/^(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})$/);
  if (dmyMatch) {
    const [, d, m, y] = dmyMatch;
    const iso = `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`;
    const date = new Date(+y, +m - 1, +d);
    if (date.getFullYear() === +y && date.getMonth() === +m - 1 && date.getDate() === +d) {
      return iso;
    }
  }

  return null;
}

// ============================================================================
// DateInput — Calendar-based (native <input type="date">)
// Stores YYYY-MM-DD, displays DD/MM/YYYY via overlay.
// ============================================================================

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
  variant = "default",
  className = "",
  showCalendarIcon = false,
  ...props
}) {
  const { inForm, register, error, setValue, value: formValue } =
    useFormField(name);
  const err = inForm ? error : externalError;
  const inputRef = useRef(null);
  const [isFocused, setIsFocused] = useState(false);

  const currentValue = inForm ? formValue || "" : value || "";

  const validationRules = { ...rules };
  if (required && !validationRules.required) {
    validationRules.required = "This field is required";
  }

  const handleFocus = () => {
    setIsFocused(true);
    inputRef.current?.showPicker?.();
  };

  const handleBlur = (e) => {
    setIsFocused(false);
    onBlur?.(e);
  };

  const handleChange = (e) => {
    const newValue = e.target.value;
    if (inForm) {
      setValue?.(name, newValue);
    } else {
      onChange?.(newValue);
    }
  };

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <div className={cx("relative", variants[variant])}>
        {/* Placeholder overlay — shown when empty & not focused */}
        {!currentValue && !isFocused && (
          <div
            className="absolute inset-0 flex items-center px-4 pointer-events-none z-10"
            onClick={() => inputRef.current?.focus()}
          >
            <span className="text-gray-400 text-base select-none">{placeholder}</span>
          </div>
        )}

        {/* Native date input — text is always transparent, overlay shows formatted value */}
        <input
          ref={inputRef}
          id={name}
          name={name}
          type="date"
          min={min}
          max={max}
          required={required}
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
            "w-full relative px-4 py-3.5 rounded-xl bg-transparent outline-none transition-all duration-200",
            "min-h-[48px]",
            "text-transparent", // always transparent — overlay handles display
            showCalendarIcon ? "pr-11" : "",
            className
          )}
          style={{ colorScheme: "light", caretColor: "transparent" }}
          {...props}
        />

        {/* Calendar icon */}
        {showCalendarIcon && (
          <div
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
            aria-hidden="true"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* ── Formatted value overlay ── */}
        {currentValue && !isFocused && (
          <div className="absolute inset-0 flex items-center px-4 pointer-events-none bg-transparent z-10">
            <span className="text-gray-900 text-base">{isoToDisplay(currentValue)}</span>
          </div>
        )}
      </div>

      {err && (
        <p id={`${name}-error`} className="mt-2 text-sm text-red-600 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 bg-red-600 rounded-full flex-shrink-0" />
          {err}
        </p>
      )}
    </div>
  );
}

// ============================================================================
// TextDateInput — Text-based date entry
// User types DD/MM/YYYY, stored as YYYY-MM-DD for backend.
// Supports copy & paste of dates in multiple formats.
// ============================================================================

export function TextDateInput({
  name,
  label,
  placeholder = "DD-MM-YYYY",
  rules = {},
  required = false,
  value,
  onChange,
  onBlur,
  error: externalError,
  variant = "default",
  className = "",
  ...props
}) {
  const { inForm, register, error, setValue, value: formValue } =
    useFormField(name);
  const displayErr = inForm ? error : externalError;
  const inputRef = useRef(null);

  // The ISO (YYYY-MM-DD) value from form or prop
  const isoValue = inForm ? formValue || "" : value || "";

  const [displayValue, setDisplayValue] = useState(() => isoToDisplay(isoValue));
  const [isFocused, setIsFocused] = useState(false);
  const [localError, setLocalError] = useState("");

  // Keep display in sync when the form value changes externally (e.g. reset, load from API)
  useEffect(() => {
    if (!isFocused) {
      setDisplayValue(isoToDisplay(isoValue));
    }
  }, [isoValue, isFocused]);

  const validationRules = { ...rules };
  if (required && !validationRules.required) {
    validationRules.required = "This field is required";
  }
  // Add a validate rule so RHF also catches invalid dates
  if (!validationRules.validate) {
    validationRules.validate = (val) => {
      if (!val) return true; // empty is handled by "required"
      const display = isoToDisplay(val);
      return isCompleteAndValid(display) || "Please enter a valid date (DD-MM-YYYY)";
    };
  }

  // Register with RHF (hidden registration for validation) — the actual value is
  // controlled via setValue, but we need register so validation rules are applied.
  const rhfProps = inForm ? register(name, validationRules) : {};

  /** Push YYYY-MM-DD value to form or external onChange */
  const commitValue = useCallback(
    (iso) => {
      if (inForm) {
        setValue?.(name, iso, { shouldValidate: true });
      } else {
        onChange?.(iso);
      }
    },
    [inForm, setValue, name, onChange]
  );

  // ── Handlers ──────────────────────────────────────────────────────

  const handleChange = (e) => {
    const formatted = autoFormatDigits(e.target.value);
    setDisplayValue(formatted);

    if (isCompleteAndValid(formatted)) {
      setLocalError("");
      commitValue(displayToIso(formatted));
    } else if (!formatted) {
      setLocalError("");
      commitValue("");
    }
    // Don't commit partial values — wait for blur
  };

  const handlePaste = (e) => {
    const pasted = e.clipboardData?.getData("text");
    if (!pasted) return;

    const iso = parsePastedDate(pasted);
    if (iso) {
      e.preventDefault();
      setDisplayValue(isoToDisplay(iso));
      commitValue(iso);
    }
    // If not parseable, let the default paste happen and handleChange will auto-format
  };

  const handleFocus = () => {
    setIsFocused(true);
    setLocalError("");
  };

  const handleBlur = (e) => {
    setIsFocused(false);

    if (displayValue && !isCompleteAndValid(displayValue)) {
      // Show error for invalid dates instead of silently clearing
      setLocalError("Please enter a valid date (DD-MM-YYYY)");
      setDisplayValue("");
      commitValue("");
    } else if (displayValue && isCompleteAndValid(displayValue)) {
      setLocalError("");
      commitValue(displayToIso(displayValue));
    }

    onBlur?.(e);
  };

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <div className={cx("relative", variants[variant])}>
        {/* Placeholder — only when empty & not focused */}
        {!displayValue && !isFocused && (
          <div className="absolute inset-0 flex items-center px-4 pointer-events-none z-10">
            <span className="text-gray-400 text-base select-none">{placeholder}</span>
          </div>
        )}

        {/* Text input */}
        <input
          ref={inputRef}
          id={name}
          name={name}
          type="text"
          inputMode="numeric"
          autoComplete="off"
          aria-invalid={!!(displayErr || localError)}
          aria-describedby={(displayErr || localError) ? `${name}-error` : undefined}
          value={displayValue}
          onChange={handleChange}
          onPaste={handlePaste}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder=""
          className={cx(
            "w-full relative px-4 py-3.5 rounded-xl bg-transparent outline-none transition-all duration-200",
            "min-h-[48px]",
            "text-gray-900 text-base",
            className
          )}
          {...props}
        />
      </div>

      {(displayErr || localError) && (
        <p id={`${name}-error`} className="mt-2 text-sm text-red-600 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 bg-red-600 rounded-full flex-shrink-0" />
          {displayErr || localError}
        </p>
      )}
    </div>
  );
}