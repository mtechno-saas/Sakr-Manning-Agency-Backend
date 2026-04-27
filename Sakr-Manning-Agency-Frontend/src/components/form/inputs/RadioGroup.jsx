import React from "react";
import { useFormField, cx } from "../../../hooks/useFormField";

/**
 * RadioGroup - Custom radio button group.
 *
 * Props:
 *  - name: field name (RHF integration)
 *  - label: optional label text
 *  - options: [{ label, value }]
 *  - value: controlled value
 *  - onChange: callback(value)
 *  - error: error message
 *  - variant: style variant for radios
 *  - className: custom classes
 *
 * Features:
 *  - Keyboard accessible
 *  - Integrates with react-hook-form
 *  - Customizable variants
 */

const variants = {
  default:
    "border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400",
  outlined:
    "border-2 border-gray-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-200",
  shadowed: "shadow-md border-transparent focus:ring-2 focus:ring-blue-100",
  light:
    "bg-blue-50 border border-blue-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100",
  calendar:
    "font-inter text-sm bg-white border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
};

export function RadioGroup({
  name,
  label,
  options = [],
  rules,
  required = false,
  inline = true,
  value,
  onChange,
  error: externalError,
  variant = "default",
  className = "",
  ...props
}) {
  const { inForm, register, error, setValue } = useFormField(name);
  const err = inForm ? error : externalError;

  const handleClear = () => {
    if (inForm) {
      setValue(name, "", { shouldValidate: true, shouldDirty: true });
    } else {
      onChange?.("");
    }
  };

  return (
    <div className={`w-full ${variants[variant]}`}>
      {label && (
        <span className="block text-base font-medium text-gray-700 mb-3">
          {label} {required && <span className="text-red-500">*</span>}
        </span>
      )}

      <div
        role="radiogroup"
        aria-invalid={!!err}
        aria-describedby={err ? `${name}-error` : undefined}
        className={cx(
          inline
            ? "flex gap-4 flex-wrap items-center"
            : "grid gap-3",
          className
        )}
      >
        {options.map((opt, i) => {
          const v = typeof opt === "string" ? opt : opt.value;
          const lbl = typeof opt === "string" ? opt : opt.label;
          const isChecked = inForm
            ? register(name, rules).value === v
            : value === v;

          return (
            <label
              key={v ?? i}
              className={cx(
                "flex items-center gap-3 cursor-pointer group transition-all duration-200",
                "px-4 py-3 rounded-lg border-2 min-h-[48px]",
                "hover:bg-blue-50 hover:border-blue-300",
                isChecked
                  ? "bg-blue-50 border-blue-500"
                  : "bg-white border-gray-300"
              )}
            >
              <input
                type="radio"
                value={v}
                name={name}
                {...(inForm
                  ? register(name, rules)
                  : {
                    checked: value === v,
                    onChange: (e) => onChange?.(e.target.value),
                  })}
                className={cx(
                  "h-5 w-5 text-blue-600 cursor-pointer transition-all duration-200",
                  "focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                )}
                {...props}
              />
              <span className={cx(
                "text-base transition-colors duration-200",
                isChecked ? "text-gray-900 font-medium" : "text-gray-700"
              )}>
                {lbl}
              </span>
            </label>
          );
        })}
      </div>

      {/* Clear option styled as a button */}
      {(inForm ? register(name, rules).value : value) && (
        <button
          type="button"
          onClick={handleClear}
          className="mt-3 flex items-center gap-2 text-sm text-gray-500 hover:text-red-600 transition-colors duration-200 underline decoration-dotted underline-offset-2"
        >
          Clear selection
        </button>
      )}

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
