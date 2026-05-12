import React, { useEffect, useId, useMemo, useRef, useState } from "react";
import ReactDOM from "react-dom";
import { ChevronDown, Loader2 } from "lucide-react";
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
    "bg-white border border-gray-300 rounded-lg py-2 px-3 text-sm shadow-sm hover:border-gray-400 transition-all duration-200",
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
  isLoading = false,
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
      // If v is an array, it's a direct reset or set (e.g. from Clear selection)
      if (Array.isArray(v)) {
        if (inForm) {
          setValue(name, v, { shouldValidate: true, shouldDirty: true });
          trigger?.(name);
        } else {
          onChange?.(v);
        }
        return;
      }

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
  const [dropdownStyle, setDropdownStyle] = useState({});
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

  // Compute portal dropdown position
  const updateDropdownPosition = () => {
    if (!buttonRef.current) return;
    const rect = buttonRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const spaceBelow = viewportHeight - rect.bottom;
    const spaceAbove = rect.top;
    const dropdownMaxHeight = 240;
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
  };

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
  }, [open]);

  // Close on outside click (checks both trigger and portalled list)
  useEffect(() => {
    function onDocClick(e) {
      if (
        buttonRef.current?.contains(e.target) ||
        listRef.current?.contains(e.target)
      ) return;
      setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  function onKeyDown(e) {
    if (isLoading) return;
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
          onClick={() => !isLoading && setOpen((o) => !o)}
          onKeyDown={onKeyDown}
          disabled={isLoading || props.disabled}
          className={cx(
            "w-full appearance-none font-poppins text-sm px-3 py-2 rounded-lg transition-all duration-200 flex items-center justify-between gap-2 text-left",
            variants[variant],
            err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "",
            className
          )}
          {...props}
        >
          <span className={selectedDisplay ? "text-gray-900" : "text-gray-400"}>
            {isLoading ? "Loading..." : (selectedDisplay || placeholder)}
          </span>
          {isLoading ? (
            <Loader2 className="w-4 h-4 text-gray-400 animate-spin ml-auto" aria-hidden="true" />
          ) : (
            <ChevronDown
              className={cx(
                "w-4 h-4 text-gray-400 transition-transform ml-auto",
                open ? "rotate-180" : ""
              )}
              aria-hidden="true"
            />
          )}
        </button>

        {open && ReactDOM.createPortal(
          <div
            data-portal-dropdown="true"
            style={dropdownStyle}
            className="bg-white border border-gray-300 rounded-lg shadow-xl max-h-60 overflow-y-auto"
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
                className="px-3 py-2 text-xs text-gray-500 hover:bg-red-50 hover:text-red-600 cursor-pointer border-b border-gray-100"
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
                    "px-3 py-2 text-xs cursor-pointer flex items-center justify-between",
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
          </div>,
          document.body
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
