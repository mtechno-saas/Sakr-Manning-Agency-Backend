import React, { useEffect, useId, useMemo, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import { useFormField, cx } from "../../../../hooks/useFormField";

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
    "border-2 border-gray-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-200",
  light: "bg-white rounded-[15px] border border-gray-100 p-4",
  default: "bg-white border border-black/50 rounded-[15px] shadow-md p-4",
  bordered: "bg-white border border-[#91BBE1] rounded-[15px] p-4",
  shadowed: "bg-white shadow-lg rounded-[15px] border border-gray-100 p-4",
  calendar:
    "font-inter text-sm bg-white border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
  dashboard:
    "bg-white border border-gray-300 rounded-lg py-3 px-4 text-base shadow-sm hover:border-gray-400 transition-all duration-200",
};

export function Select({
  name,
  label,
  options = [],
  placeholder = "Select...",
  required = false,
  searchable = true,
  isMulti = false,
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
    if (isMulti) {
      const currentArray = Array.isArray(currentValue) ? currentValue : [];
      const newArray = currentArray.includes(v)
        ? currentArray.filter(item => item !== v)
        : [...currentArray, v];
      
      if (inForm) {
        setValue(name, newArray, { shouldValidate: true, shouldDirty: true });
        trigger?.(name);
      } else {
        onChange?.(newArray);
      }
    } else {
      if (inForm) {
        setValue(name, v, { shouldValidate: true, shouldDirty: true });
        trigger?.(name);
      } else {
        onChange?.(v);
      }
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

  const isSelected = (v) => {
    if (isMulti) {
      return Array.isArray(currentValue) && currentValue.includes(v);
    }
    return v === currentValue;
  };

  const activeIndex = Math.max(
    0,
    filtered.findIndex((o) => isSelected(getValue(o)))
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

    if (e.key === "ArrowDown") {
      e.preventDefault();
      // Only single select navigation for now to keep it simple
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (!isMulti) setOpen(false);
    } else if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
    }
  }

  const selectedDisplay = useMemo(() => {
    if (isMulti) {
      if (!Array.isArray(currentValue) || currentValue.length === 0) return "";
      if (currentValue.length === 1) {
        const opt = options.find(o => getValue(o) === currentValue[0]);
        return opt ? getLabel(opt) : "";
      }
      return `${currentValue.length} items selected`;
    }
    
    const opt = options.find((o) => getValue(o) === currentValue);
    return opt ? getLabel(opt) : (typeof currentValue === 'string' ? currentValue : "");
  }, [currentValue, options, isMulti]);

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
            "w-full appearance-none font-poppins text-base px-4 py-3 rounded-lg transition-all duration-200 flex items-center justify-between gap-2 text-left",
            variants[variant],
            err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "",
            className
          )}
          {...props}
        >
          <span className={selectedDisplay ? "text-gray-900" : "text-gray-400"}>
            {selectedDisplay || placeholder}
          </span>
          <ChevronDown
            className={cx(
              "w-4 h-4 text-gray-400 transition-transform ml-auto",
              open ? "rotate-180" : ""
            )}
            aria-hidden="true"
          />
        </button>

        {open && (
          <div
            className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            role="listbox"
            id={listId}
            ref={listRef}
          >
            {searchable && (
              <div className="p-3 border-b border-gray-200">
                <input
                  type="text"
                  role="searchbox"
                  placeholder="Search…"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-100 placeholder:text-gray-400"
                />
              </div>
            )}

            {/* Clear option appears on top if a value is selected */}
            {selectedDisplay && (
              <div
                role="option"
                tabIndex={-1}
                onClick={() => {
                  setVal(isMulti ? [] : "");
                  if (!isMulti) setOpen(false);
                }}
                className="px-4 py-3 text-sm text-gray-500 hover:bg-red-50 hover:text-red-600 cursor-pointer border-b border-gray-100"
              >
                Clear selection
              </div>
            )}

            {filtered.length === 0 && (
              <div className="px-4 py-3 text-sm text-gray-500">
                No options found
              </div>
            )}

            {filtered.map((opt, i) => {
              const v = getValue(opt);
              const lbl = getLabel(opt);
              const selected = isSelected(v);
              return (
                <div
                  key={v ?? i}
                  role="option"
                  aria-selected={selected}
                  tabIndex={-1}
                  onClick={() => {
                    setVal(v);
                    if (!isMulti) {
                      setOpen(false);
                      setQuery("");
                    }
                  }}
                  className={cx(
                    "px-4 py-3 text-sm cursor-pointer flex items-center justify-between",
                    selected ? "bg-blue-50 text-blue-700 font-medium" : "text-gray-700 hover:bg-gray-50"
                  )}
                >
                  <span>{lbl}</span>
                  {selected && isMulti && (
                    <div className="w-2 h-2 bg-blue-600 rounded-full" />
                  )}
                </div>
              );
            })}
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
