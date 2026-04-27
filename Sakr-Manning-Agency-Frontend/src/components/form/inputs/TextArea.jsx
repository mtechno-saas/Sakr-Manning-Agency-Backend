import React from "react";
import { useFormField, cx } from "../../../hooks/useFormField";

/**
 * TextArea - Multi-line input field.
 *
 * Props:
 *  - name: field name (RHF integration)
 *  - label: optional label
 *  - placeholder: placeholder text
 *  - rows: default = 4
 *  - rules: RHF validation rules
 *  - required: show * in label
 *  - value: controlled value (if not using RHF)
 *  - onChange: callback(value)
 *  - onBlur: blur handler
 *  - error: error message
 *  - variant: "default" | "outlined" | "shadowed" | "light" | "calendar"
 *  - className: custom classes
 *
 * Features:
 *  - Resizable (vertical only)
 *  - Accessible error handling
 *  - RHF-aware or standalone
 */

const variants = {
  default:
    "w-full bg-white border border-black/50 rounded-[15px] shadow-md p-4",
  outlined: "w-full bg-white border border-gray-300 rounded-[15px] p-4",
  shadowed: "w-full bg-white shadow-lg rounded-[15px] p-4",
  light:
    "bg-blue-50 border border-blue-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100",
  calendar:
    "font-inter text-sm bg-white border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
  dashboard:
    "w-full bg-white border border-gray-300 rounded-lg p-3 text-base focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400 transition-all duration-200",
  modal:
    "w-full bg-gray-50 border border-gray-200 rounded-lg p-4 transition-all duration-200 hover:border-gray-300 focus:border-[#0065AF] focus:ring-2 focus:ring-blue-100",
};

export function TextArea({
  name,
  label,
  placeholder,
  rows = 4,
  rules,
  required = false,
  value,
  onChange,
  onBlur,
  error: externalError,
  variant = "default",
  className = "",
  ...props
}) {
  const { inForm, register, error } = useFormField(name);
  const err = inForm ? error : externalError;

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

      <textarea
        id={name}
        rows={rows}
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
          "resize-none font-poppins px-4 py-3 rounded-lg text-sm transition-all duration-200 resize-vertical",
          variants[variant],
          err ? "border-red-400 focus:ring-red-100 focus:border-red-500" : "",
          className
        )}
        {...props}
      />

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
