import React, { useState } from "react";
import { useFormField, cx } from "../../../../hooks/useFormField";
/**
 * BaseInput - Flexible text input component with form integration.
 *
 * Props:
 *  - name: field name (required for RHF integration)
 *  - label: optional label text
 *  - type: input type (default = "text")
 *  - placeholder: input placeholder
 *  - value: controlled value (if not using react-hook-form)
 *  - onChange: change handler (if not using react-hook-form)
 *  - required: mark field required (adds * to label)
 *  - error: error message (overrides form context)
 *  - icon: optional icon element to render inside the input
 *  - className: custom classes
 *  - ...props: forwarded to <input>
 *
 * Variants (via Tailwind classNames can be added from parent)
 */

const variants = {
  // default:
  //   "border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400",
  default:
    "w-full bg-white shadow-md rounded-[15px] border border-black/50 p-4",
  light:
    "bg-blue-50 border border-blue-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100",
  half: "w-full md:w-1/2 bg-white shadow-md rounded-[15px] border border-black/50 p-4",
  full: "w-full bg-white shadow-md rounded-[15px] border border-black/50 p-4",
  outlined: "w-full bg-white border border-gray-300 rounded-[15px] p-4",
  shadowed: "w-full bg-white shadow-lg rounded-[15px] p-4",
  calendar:
    "font-inter text-sm bg-white border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
  dashboard:
    "w-full bg-white border border-gray-300 rounded-lg py-3 px-4 text-base shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400 transition-all duration-200",
};

export function BaseInput({
  name,
  label,
  type = "text",
  placeholder,
  rules,
  required = false,
  value,
  onChange,
  onBlur,
  error: externalError,
  icon,
  variant = "default",
  className = "",
  ...props
}) {
  const { inForm, register, error } = useFormField(name);
  const err = inForm ? error : externalError;

  return (
    <div className={variant === "full" ? "col-span-2 w-full" : "w-full"}>
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <div className="relative">
        <input
          id={name}
          name={name}
          type={type}
          required={required}
          aria-invalid={!!err}
          aria-describedby={err ? `${name}-error` : undefined}
          {...(inForm
            ? register(name, rules)
            : {
              value: value ?? "",
              onChange: (e) => onChange?.(e.target.value),
              onBlur,
            })}
          placeholder={placeholder}
          className={cx(
            "w-full px-4 py-3 rounded-lg text-xl transition-all duration-200 outline-none",
            variants[variant],
            icon ? "pr-10" : "",
            err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "",
            className
          )}
          {...props}
        />

        {icon && (
          <div
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
            aria-hidden="true"
          >
            {icon}
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

/////////////////////////////////////////////////////////////////////////////////////////

export function SuggestionInput({
  name,
  label,
  placeholder,
  rules,
  required = false,
  value,
  onChange,
  onBlur,
  error: externalError,
  icon,
  variant = "default",
  className = "",
  suggestions = [],
  ...props
}) {
  const { inForm, register, error } = useFormField(name);
  const err = inForm ? error : externalError;
  const [inputValue, setInputValue] = useState(value ?? "");

  const handleChange = (val) => {
    setInputValue(val);
    onChange?.(val);
  };

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
        <input
          id={name}
          name={name}
          required={required}
          aria-invalid={!!err}
          aria-describedby={err ? `${name}-error` : undefined}
          {...(inForm
            ? register(name, {
              ...rules,
              onChange: (e) => handleChange(e.target.value),
            })
            : {
              value: inputValue,
              onChange: (e) => handleChange(e.target.value),
              onBlur,
            })}
          placeholder={placeholder}
          className={cx(
            "w-full px-4 py-3 rounded-lg text-xl transition-all duration-200 outline-none",
            variants[variant],
            icon ? "pr-10" : "",
            err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "",
            className
          )}
          list={`${name}-suggestions`}
          {...props}
        />

        {icon && (
          <div
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
            aria-hidden="true"
          >
            {icon}
          </div>
        )}

        {/* Suggestions via datalist */}
        {suggestions.length > 0 && (
          <datalist id={`${name}-suggestions`}>
            {suggestions.map((s, i) => (
              <option key={i} value={s} />
            ))}
          </datalist>
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

/////////////////////////////////////////////////////////////////////////////////////////
import { X } from 'lucide-react';

// const variants = {
// default:
// "w-full bg-white shadow-md rounded-[15px] border border-black/50 p-4",
// light:
// "bg-blue-50 border border-blue-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100",
// half: "w-full md:w-1/2 bg-white shadow-md rounded-[15px] border border-black/50 p-4",
// full: "w-full bg-white shadow-md rounded-[15px] border border-black/50 p-4",
// outlined: "w-full bg-white border border-gray-300 rounded-[15px] p-4",
// shadowed: "w-full bg-white shadow-lg rounded-[15px] p-4",
// calendar:
// "font-inter text-sm bg-white border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
// dashboard:
// "w-full bg-white border border-gray-300 rounded-lg py-3 px-4 text-base shadow-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400 transition-all duration-200",
// };

export function DBBaseInput({
  name,
  label,
  type = "text",
  placeholder,
  rules,
  required = false,
  value,
  onChange,
  onBlur,
  error: externalError,
  icon,
  leadingIcon,
  trailingIcon,
  variant = "default",
  className = "",
  showClearButton = false,
  showCharacterCount = false,
  maxLength,
  disabled = false,
  readOnly = false,
  ...props
}) {
  const { inForm, register, error } = useFormField(name);
  const err = inForm ? error : externalError;
  const [isFocused, setIsFocused] = useState(false);
  const currentValue = value ?? "";
  const hasValue = currentValue.length > 0;
  const handleClear = () => {
    onChange?.("");
  };
  return (
    <div className={variant === "full" ? "col-span-2 w-full" : "w-full"}>
      {label && (
        <label
          htmlFor={name}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label} {required && <span className="text-red-500">*</span>}
        </label>
      )}
      <div className="relative">
        {/* Leading Icon */}
        {leadingIcon && (
          <div
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
            aria-hidden="true"
          >
            {leadingIcon}
          </div>
        )}

        {/* Input */}
        <input
          id={name}
          name={name}
          type={type}
          required={required}
          disabled={disabled}
          readOnly={readOnly}
          aria-invalid={!!err}
          aria-describedby={err ? `${name}-error` : undefined}
          maxLength={maxLength}
          {...(inForm
            ? register(name, rules)
            : {
              value: currentValue,
              onChange: (e) => onChange?.(e.target.value),
              onBlur,
            })}
          onFocus={() => setIsFocused(true)}
          onBlur={(e) => {
            setIsFocused(false);
            onBlur?.(e);
          }}
          placeholder={placeholder}
          className={cx(
            "w-full px-4 py-3 rounded-lg text-base transition-all duration-200 outline-none",
            variants[variant],
            leadingIcon ? "pl-10" : "",
            (icon || trailingIcon || (showClearButton && hasValue)) ? "pr-10" : "",
            err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "",
            disabled ? "opacity-50 cursor-not-allowed" : "",
            readOnly ? "bg-gray-50 cursor-default" : "",
            className
          )}
          {...props}
        />
        {/* Trailing Icons Container */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
          {/* Clear Button */}
          {showClearButton && hasValue && !disabled && !readOnly && (
            <button
              type="button"
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1"
              aria-label="Clear input"
            >
              <X size={16} />
            </button>
          )}

          {/* Trailing Icon or Default Icon */}
          {(trailingIcon || icon) && (
            <div className="text-gray-400 pointer-events-none" aria-hidden="true">
              {trailingIcon || icon}
            </div>
          )}
        </div>
      </div>

      {/* Character Count */}
      {showCharacterCount && maxLength && (
        <div className="mt-1 text-xs text-gray-500 text-right">
          {currentValue.length} / {maxLength}
        </div>
      )}

      {/* Error Message */}
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