// src/components/common/Input.jsx
/*
 * Enhanced Input component with more features and validation
 * Props:
 *  - type: input type (text, email, password, etc.)
 *  - placeholder: placeholder text
 *  - value: controlled value
 *  - onChange: change handler
 *  - label: optional label text
 *  - helperText: helper text below input
 *  - error: error message (optional)
 *  - success: success message (optional)
 *  - disabled: disable input
 *  - required: mark as required
 *  - icon: icon element
 *  - iconPosition: "left" | "right"
 *  - size: "sm" | "md" | "lg"
 *  - variant: "default" | "outlined" | "filled"
 *  - maxLength: maximum character length
 *  - showCharCount: show character counter
 *  - className: additional classes
 */

export default function Input({
  type = "text",
  placeholder,
  value,
  onChange,
  label,
  helperText,
  error,
  success,
  disabled = false,
  required = false,
  icon,
  iconPosition = "left",
  size = "md",
  variant = "default",
  maxLength,
  showCharCount = false,
  className = "",
  ...rest
}) {
  const sizeClasses = {
    sm: "px-3 py-2 text-sm rounded-lg",
    md: "px-4 py-3 text-base rounded-xl",
    lg: "px-5 py-4 text-lg rounded-xl",
  };

  const variantClasses = {
    default:
      "border border-[#B6B6B642] bg-white focus:ring-2 focus:ring-[#0065AF] focus:border-[#0065AF]",
    outlined:
      "border-2 border-[#B6B6B642] bg-transparent focus:ring-2 focus:ring-[#0065AF] focus:border-[#0065AF]",
    filled:
      "border-0 bg-[#F5F5F5] focus:ring-2 focus:ring-[#0065AF] focus:bg-white",
    contact:
      "border border-[#1976D2] rounded-[22px] px-6 py-5 bg-transparent outline-none placeholder-black/50",
    form: "border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
  };

  const stateClasses = error
    ? "border-red-500 focus:ring-red-500 focus:border-red-500"
    : success
    ? "border-green-500 focus:ring-green-500 focus:border-green-500"
    : variantClasses[variant];

  const disabledClasses = disabled
    ? "opacity-50 cursor-not-allowed bg-gray-50"
    : "";

  const inputClasses = `w-full transition-all duration-200 focus:outline-none text-[#000000C4] placeholder-[#000000C4]/50 ${
    sizeClasses[size]
  } ${stateClasses} ${disabledClasses} ${
    icon ? (iconPosition === "left" ? "pl-10" : "pr-10") : ""
  } ${className}`;

  const characterCount = value ? value.length : 0;
  const isOverLimit = maxLength && characterCount > maxLength;

  return (
    <div className="w-full flex flex-col gap-2">
      {label && (
        <label className="text-sm font-medium text-[#000000C4] flex items-center gap-1">
          {label}
          {required && <span className="text-red-500">*</span>}
        </label>
      )}

      <div className="relative">
        {icon && iconPosition === "left" && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#000000C4]/50">
            {icon}
          </div>
        )}

        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          required={required}
          maxLength={maxLength}
          className={inputClasses}
          {...rest}
        />

        {icon && iconPosition === "right" && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#000000C4]/50">
            {icon}
          </div>
        )}
      </div>

      <div className="flex justify-between items-start">
        <div className="flex-1">
          {error && (
            <p className="text-sm text-red-500 flex items-center gap-1">
              {error}
            </p>
          )}
          {success && !error && (
            <p className="text-sm text-green-500 flex items-center gap-1">
              {success}
            </p>
          )}
          {helperText && !error && !success && (
            <p className="text-sm text-[#000000C4]/70">{helperText}</p>
          )}
        </div>

        {(showCharCount || maxLength) && (
          <p
            className={`text-xs flex-shrink-0 ml-2 ${
              isOverLimit ? "text-red-500" : "text-[#000000C4]/50"
            }`}
          >
            {characterCount}
            {maxLength && `/${maxLength}`}
          </p>
        )}
      </div>
    </div>
  );
}
