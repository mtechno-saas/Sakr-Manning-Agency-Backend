import React, { useState } from "react";
import { useFormField, cx } from "../../../hooks/useFormField";

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
  default:
    "w-full bg-white shadow-md rounded-xl border border-gray-300 transition-all duration-200 hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100",
  light:
    "bg-blue-50 border border-blue-200 rounded-xl transition-all duration-200 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100",
  half: "w-full md:w-1/2 bg-white shadow-md rounded-xl border border-gray-300 transition-all duration-200 hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100",
  full: "w-full bg-white shadow-md rounded-xl border border-gray-300 transition-all duration-200 hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100",
  outlined: "w-full bg-white border-2 border-gray-300 rounded-xl transition-all duration-200 hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100",
  shadowed: "w-full bg-white shadow-lg rounded-xl border border-gray-200 transition-all duration-200 hover:shadow-xl focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100",
  calendar:
    "font-inter text-sm bg-white border border-gray-300 rounded-xl transition-all duration-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100",
  dashboard:
    "w-full bg-white border border-gray-300 rounded-lg shadow-sm transition-all duration-200 hover:border-gray-400 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-100",
  modal:
    "w-full bg-gray-50 border border-gray-200 rounded-lg transition-all duration-200 hover:border-gray-300 focus-within:border-[#0065AF] focus-within:ring-2 focus-within:ring-blue-100",
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

      <div className={cx("relative", variants[variant])}>
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
            "w-full px-4 py-3.5 text-base rounded-xl bg-transparent transition-all duration-200 outline-none",
            "placeholder:text-gray-400",
            "sm:text-base md:text-base lg:text-base",
            icon ? "pr-11" : "",
            err ? "text-red-900" : "text-gray-900",
            className
          )}
          {...props}
        />

        {icon && (
          <div
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
            aria-hidden="true"
          >
            {icon}
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

      <div className={cx("relative", variants[variant])}>
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
            "w-full px-4 py-3.5 text-base rounded-xl bg-transparent transition-all duration-200 outline-none",
            "placeholder:text-gray-400",
            "sm:text-base md:text-base lg:text-base",
            icon ? "pr-11" : "",
            err ? "text-red-900" : "text-gray-900",
            className
          )}
          list={`${name}-suggestions`}
          {...props}
        />

        {icon && (
          <div
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
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
          className="mt-2 text-sm text-red-600 flex items-center gap-1.5"
        >
          <span className="w-1.5 h-1.5 bg-red-600 rounded-full flex-shrink-0" />
          {err}
        </p>
      )}
    </div>
  );
}

/////////////////////////////////////////////////////////////////////////////////////////
import { X } from 'lucide-react';

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

      <div className={cx("relative", variants[variant])}>
        {/* Leading Icon */}
        {leadingIcon && (
          <div
            className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
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
            "w-full px-4 py-3.5 text-base rounded-xl bg-transparent transition-all duration-200 outline-none",
            "placeholder:text-gray-400",
            "sm:text-base md:text-base lg:text-base",
            leadingIcon ? "pl-11" : "",
            (icon || trailingIcon || (showClearButton && hasValue)) ? "pr-20" : "",
            err ? "text-red-900" : "text-gray-900",
            disabled ? "opacity-50 cursor-not-allowed" : "",
            readOnly ? "cursor-default" : "",
            className
          )}
          {...props}
        />

        {/* Trailing Icons Container */}
        <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
          {/* Clear Button */}
          {showClearButton && hasValue && !disabled && !readOnly && (
            <button
              type="button"
              onClick={handleClear}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded hover:bg-gray-100"
              aria-label="Clear input"
            >
              <X size={18} />
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
        <div className="mt-1.5 text-xs text-gray-500 text-right">
          {currentValue.length} / {maxLength}
        </div>
      )}

      {/* Error Message */}
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