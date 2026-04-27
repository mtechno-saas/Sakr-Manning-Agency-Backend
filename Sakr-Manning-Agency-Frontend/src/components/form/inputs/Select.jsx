import React, { useEffect, useId, useMemo, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import { useFormField, cx } from "../../../hooks/useFormField";

/**
 * Select - Accessible dropdown select with search support.
 *
 * Props:
 *  - name: field name (RHF integration)
 *  - label: optional label text
 *  - options: array of { value, label } or string[]
 *  - placeholder: placeholder text
 *  - required: show * if required
 *  - searchable: enable inline search filter
 *  - value: controlled value
 *  - onChange: callback(value)
 *  - error: error message
 *  - variant: "default" | "outlined" | "shadowed" | "light" | "bordered" | "calendar"
 *  - className: custom classes
 *
 * Features:
 *  - Keyboard navigation (ArrowUp, ArrowDown, Enter, Escape)
 *  - Search box inside dropdown
 *  - ARIA roles for accessibility
 */

const variants = {
  outlined:
    "border-2 border-gray-300 hover:border-gray-400 transition-all duration-200",
  code:
    "hover:border-gray-400 transition-all duration-200",
  light:
    "bg-white rounded-xl border-2 border-gray-200 hover:border-gray-300 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  default:
    "bg-white border-2 border-gray-300 rounded-xl shadow-md hover:border-gray-400 hover:shadow-lg focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  bordered:
    "bg-white border-2 border-blue-200 rounded-xl hover:border-blue-300 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  shadowed:
    "bg-white shadow-lg rounded-xl border-2 border-gray-200 hover:shadow-xl focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  calendar:
    "font-inter bg-white border-2 border-gray-300 rounded-xl hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  dashboard:
    "bg-white border-2 border-gray-300 rounded-lg shadow-sm hover:border-gray-400 hover:shadow-md focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
  modal:
    "bg-gray-50 border border-gray-200 rounded-lg hover:border-gray-300 focus-within:border-[#0065AF] focus-within:ring-2 focus-within:ring-blue-100 transition-all duration-200",
};

export function Select({
  name,
  label,
  options = [],
  placeholder = "Select...",
  required = false,
  searchable = true,
  value,
  onChange,
  error: externalError,
  variant = "default",
  className = "",
  ...props
}) {
  const {
    inForm,
    setValue,
    value: formValue,
    error,
    trigger,
  } = useFormField(name);
  const currentValue = inForm ? formValue : value;
  const setVal = (v) => {
    if (inForm) {
      setValue(name, v, { shouldValidate: true, shouldDirty: true });
      trigger?.(name);
    } else {
      onChange?.(v);
    }
  };

  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const buttonRef = useRef(null);
  const listRef = useRef(null);
  const listId = useId();
  const err = inForm ? error : externalError;

  const getLabel = (opt) => (typeof opt === "string" ? opt : opt.label);
  const getValue = (opt) => (typeof opt === "string" ? opt : opt.value);

  const filtered = useMemo(
    () =>
      !searchable || !query
        ? options
        : options.filter((o) =>
          getLabel(o).toLowerCase().includes(query.toLowerCase())
        ),
    [options, query, searchable]
  );

  const activeIndex = Math.max(
    0,
    filtered.findIndex((o) => getValue(o) === currentValue)
  );

  useEffect(() => {
    function onDocClick(e) {
      if (!buttonRef.current) return;
      if (!buttonRef.current.parentElement.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  function onKeyDown(e) {
    if (
      !open &&
      (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ")
    ) {
      e.preventDefault();
      setOpen(true);
      return;
    }
    if (!open) return;

    const max = filtered.length - 1;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      const next = Math.min(activeIndex + 1, max);
      const v = getValue(filtered[next]);
      setVal(v);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      const prev = Math.max(activeIndex - 1, 0);
      const v = getValue(filtered[prev]);
      setVal(v);
    } else if (e.key === "Enter") {
      e.preventDefault();
      setOpen(false);
    } else if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
    }
  }

  const selectedLabel =
    options.find((o) => getValue(o) === currentValue)?.label ??
    options.find((o) => getValue(o) === currentValue) ??
    "";

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

      <div className="relative">
        <button
          ref={buttonRef}
          id={name}
          type="button"
          role="combobox"
          required={required}
          aria-controls={listId}
          aria-expanded={open}
          aria-haspopup="listbox"
          aria-invalid={!!err}
          aria-describedby={err ? `${name}-error` : undefined}
          onClick={() => setOpen((o) => !o)}
          onKeyDown={onKeyDown}
          className={cx(
            "w-full appearance-none font-poppins text-base px-4 py-3.5 rounded-xl transition-all duration-200 flex items-center justify-between gap-3",
            "min-h-[48px]", // Touch-friendly minimum height
            variants[variant],
            err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "",
            className
          )}
          {...props}
        >
          <span className={cx(
            "truncate text-left flex-1",
            selectedLabel ? "text-gray-900" : "text-gray-400"
          )}>
            {selectedLabel || placeholder}
          </span>
          <ChevronDown
            className={cx(
              "w-5 h-5 text-gray-400 transition-transform flex-shrink-0",
              open ? "rotate-180" : ""
            )}
            aria-hidden="true"
          />
        </button>

        {open && (
          <div
            className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-300 rounded-xl shadow-xl max-h-64 overflow-hidden flex flex-col"
            role="listbox"
            id={listId}
            ref={listRef}
          >
            {searchable && (
              <div className="p-3 border-b border-gray-200 flex-shrink-0">
                <input
                  type="text"
                  role="searchbox"
                  placeholder="Search…"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full px-3 py-2.5 border-2 border-gray-300 rounded-lg text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all duration-200"
                />
              </div>
            )}

            <div className="overflow-y-auto flex-1">
              {/* Clear option appears on top if a value is selected */}
              {selectedLabel && (
                <div
                  role="option"
                  tabIndex={-1}
                  onClick={() => {
                    setVal("");
                    setOpen(false);
                  }}
                  className="px-4 py-3 text-sm text-gray-500 hover:bg-red-50 hover:text-red-600 cursor-pointer border-b border-gray-100 transition-colors duration-150 min-h-[44px] flex items-center"
                >
                  Clear selection
                </div>
              )}

              {filtered.length === 0 && (
                <div className="px-4 py-8 text-sm text-gray-500 text-center">
                  No options found
                </div>
              )}

              {filtered.map((opt, i) => {
                const v = getValue(opt);
                const lbl = getLabel(opt);
                const selected = v === currentValue;
                return (
                  <div
                    key={v ?? i}
                    role="option"
                    aria-selected={selected}
                    tabIndex={-1}
                    onClick={() => {
                      setVal(v);
                      setOpen(false);
                      setQuery("");
                    }}
                    className={cx(
                      "px-4 py-3 text-sm cursor-pointer transition-colors duration-150 min-h-[44px] flex items-center",
                      selected
                        ? "bg-blue-50 text-blue-700 font-medium"
                        : "hover:bg-blue-50 text-gray-700"
                    )}
                  >
                    {lbl}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {err && (
        <p
          id={`${name}-error`}
          className="mt-2 text-sm text-red-600 flex items-center gap-1.5"
        >
          <span className="w-1.5 h-1.5 bg-red-600 rounded-full flex-shrink-0" />
          {err}
        </p>
      )}
    </div>
  );
}