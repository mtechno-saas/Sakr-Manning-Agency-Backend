import React from "react";
import { useFormField, cx } from "../../../hooks/useFormField";

// const variants = {
//   default:
//     "border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-400",
//   outlined:
//     "border-2 border-gray-400 focus:border-blue-600 focus:ring-2 focus:ring-blue-200",
//   shadowed: "shadow-md border-transparent focus:ring-2 focus:ring-blue-100",
//   light:
//     "bg-blue-50 border border-blue-200 focus:border-blue-400 focus:ring-2 focus:ring-blue-100",
//   calendar:
//     "font-inter text-sm bg-white border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100",
// };

export function Checkbox({
  name,
  label,
  rules,
  required = false,
  checked,
  onChange,
  // variant,
  error: externalError,
  className = "",
  ...props
}) {
  const { inForm, register, error } = useFormField(name);
  const err = inForm ? error : externalError;

  return (
    <label className={cx("flex items-center gap-3 cursor-pointer", className)}>
      <input
        id={name}
        name={name}
        type="checkbox"
        role="checkbox"
        aria-invalid={!!err}
        aria-describedby={err ? `${name}-error` : undefined}
        {...(inForm
          ? register(name, rules)
          : {
              checked: !!checked,
              onChange: (e) => onChange?.(e.target.checked),
            })}
        className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        {...props}
      />
      <span className="text-sm text-gray-700">
        {label} {required && <span className="text-red-500">*</span>}
      </span>

      {err && (
        <span id={`${name}-error`} className="ml-2 text-red-500 text-xs">
          {err}
        </span>
      )}
    </label>
  );
}
